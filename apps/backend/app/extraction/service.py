"""Service orchestrating extraction, human review, and Neo4j sync."""
import uuid
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from apps.backend.app.models.document import Document
from apps.backend.app.models.entity import ExtractedEntity
from apps.backend.app.models.relationship import ExtractedRelationship
from apps.backend.app.models.audit_log import AuditLog
from apps.backend.app.extraction.mock_provider import MockExtractor
from apps.backend.app.extraction.schemas import ReviewDecision
from apps.backend.app.extraction.resolution import resolve_entity_candidate
from apps.backend.app.graph.service import GraphService, GraphServiceUnavailableError

from apps.backend.app.core.config import settings
from apps.backend.app.extraction.local_ner_provider import SpacyNERProvider

class DocumentExtractionService:
    def __init__(self, db: Session):
        self.db = db
        if settings.EXTRACTION_PROVIDER == "SPACY":
            self.extractor = SpacyNERProvider()
        else:
            self.extractor = MockExtractor()
        self.graph_service = GraphService()

    def process_document(self, document_id: str, extract_relationships: bool = False) -> Dict[str, Any]:
        """Extract candidates from document and persist as UNREVIEWED."""
        from apps.backend.app.models.extraction_run import ExtractionRun
        from apps.backend.app.extraction.relationship_service import RelationshipExtractionService
        from apps.backend.app.extraction.schemas import ExtractedEntityCandidate
        import hashlib
        
        doc = self.db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document {document_id} not found")
        
        # 1. Resolve Provider Identity
        provider_name = self.extractor.provider_name
        provider_ver = self.extractor.provider_version
        model_ver = self.extractor.model_version
        extraction_ver = self.extractor.extraction_version
        post_proc_ver = "1.0.0" # Deterministic post-processing version
        rel_rule_ver = "1.0.0" # Relationship rules version
        
        run_identity = f"{document_id}:{provider_name}:{provider_ver}:{model_ver}:{extraction_ver}:{post_proc_ver}:{rel_rule_ver}"
        extraction_run_id = hashlib.sha256(run_identity.encode("utf-8")).hexdigest()
        
        run = self.db.query(ExtractionRun).filter(ExtractionRun.extraction_run_id == extraction_run_id).first()
        if run and run.status == "COMPLETED":
            return {
                "status": "success",
                "extraction_run_id": run.extraction_run_id,
                "entities": run.entity_candidate_count,
                "relationships": run.relationship_candidate_count,
                "warning": "Run already exists (idempotency matched). Returned cached counts."
            }
            
        if not run:
            run = ExtractionRun(
                extraction_run_id=extraction_run_id,
                document_id=document_id,
                case_id=doc.case_id,
                provider=provider_name,
                provider_version=provider_ver,
                model_version=model_ver,
                extraction_version=extraction_ver,
                post_processing_version=post_proc_ver,
                relationship_rule_version=rel_rule_ver,
                status="RUNNING",
                started_at=datetime.now(timezone.utc)
            )
            self.db.add(run)
            self.db.commit()
            
        # Extract
        try:
            result = self.extractor.extract(document_id, doc.raw_content or "")
        except RuntimeError as e:
            if "unavailable" in str(e).lower():
                run.status = "PROVIDER_UNAVAILABLE"
                run.warnings = json.dumps({"reason": str(e)})
                self.db.commit()
                return {"status": "PROVIDER_UNAVAILABLE", "provider": provider_name, "reason": str(e)}
            run.status = "FAILED"
            run.warnings = json.dumps({"error": str(e)})
            self.db.commit()
            return {"status": "FAILED", "error": "Internal extraction failure"}
        except Exception as e:
            run.status = "FAILED"
            run.warnings = json.dumps({"error": str(e)})
            self.db.commit()
            return {"status": "FAILED", "error": "Internal extraction failure"}

        
        # Save Entities
        saved_entities = {}
        for ent in result.entities:
            existing = self.db.query(ExtractedEntity).filter(
                ExtractedEntity.document_id == document_id,
                ExtractedEntity.start_offset == ent.start_offset,
                ExtractedEntity.end_offset == ent.end_offset,
                ExtractedEntity.extraction_provider == ent.extraction_provider
            ).first()
            
            if not existing:
                res = resolve_entity_candidate(self.db, doc.case_id, ent.normalized_value, ent.entity_type)
                
                db_ent = ExtractedEntity(
                    extraction_run_id=extraction_run_id,
                    case_id=doc.case_id,
                    document_id=document_id,
                    entity_type=ent.entity_type,
                    original_value=ent.original_value,
                    canonical_name=ent.normalized_value,
                    source_text=ent.source_text,
                    start_offset=ent.start_offset,
                    end_offset=ent.end_offset,
                    confidence_score=ent.confidence,
                    verification_status="UNREVIEWED",
                    extraction_provider=ent.extraction_provider,
                    extraction_version=ent.extraction_version,
                    attributes=json.dumps({"resolution": res})
                )
                self.db.add(db_ent)
                self.db.flush()
                saved_entities[ent.candidate_id] = db_ent.id
            else:
                saved_entities[ent.candidate_id] = existing.id

        run.entity_candidate_count = len(result.entities)
        
        rel_count = 0
        if extract_relationships:
            # We map the saved_entities IDs to the ExtractedEntityCandidate for relation extraction
            db_entities = self.db.query(ExtractedEntity).filter_by(document_id=document_id).all()
            entities = [
                ExtractedEntityCandidate(
                    candidate_id=e.id, 
                    entity_type=e.entity_type,
                    original_value=e.original_value or "",
                    normalized_value=e.canonical_name,
                    source_document_id=document_id,
                    source_text=e.source_text or "",
                    start_offset=e.start_offset or 0,
                    end_offset=e.end_offset or 0,
                    confidence=float(e.confidence_score) if e.confidence_score else 0.85,
                    verification_status=e.verification_status,
                    extraction_provider=e.extraction_provider or "UNKNOWN",
                    extraction_version=e.extraction_version or "1.0"
                )
                for e in db_entities if e.start_offset is not None and e.end_offset is not None
            ]
            rel_svc = RelationshipExtractionService(self.db, provider_name, extraction_ver, extraction_run_id=extraction_run_id)
            rel_cands = rel_svc.extract_relationships(document_id, doc.case_id, doc.raw_content or "", entities)
            persisted = rel_svc.persist_candidates(rel_cands)
            rel_count = len(persisted)
            
        run.relationship_candidate_count = rel_count
        run.status = "COMPLETED"
        run.completed_at = datetime.now(timezone.utc)
        
        self.db.commit()
        return {
            "status": "success", 
            "extraction_run_id": run.extraction_run_id, 
            "entities": run.entity_candidate_count, 
            "relationships": run.relationship_candidate_count
        }


    def review_entity(self, entity_id: str, decision: ReviewDecision, reviewer_id: str):
        ent = self.db.query(ExtractedEntity).filter(ExtractedEntity.id == entity_id).first()
        if not ent:
            raise ValueError("Entity not found")
            
        ent.verification_status = decision.verification_status
        ent.reviewer_identity = reviewer_id
        
        if decision.verification_status == "CORRECTED":
            ent.canonical_name = decision.corrected_value  # Preserve ent.original_value intact
        
        if decision.rationale:
            ent.review_rationale = decision.rationale
            
        self._audit("ENTITY", "REVIEW_ENTITY", reviewer_id, entity_id, decision.model_dump())
        self.db.commit()


    def review_relationship(self, relationship_id: str, decision: ReviewDecision, reviewer_id: str):
        rel = self.db.query(ExtractedRelationship).filter(ExtractedRelationship.id == relationship_id).first()
        if not rel:
            raise ValueError("Relationship not found")
            
        rel.verification_status = decision.verification_status
        rel.reviewer_identity = reviewer_id
        rel.verified_by = reviewer_id
        
        if decision.verification_status == "CORRECTED" and decision.corrected_value:
            rel.relation_type = decision.corrected_value
            
        if decision.rationale:
            rel.review_rationale = decision.rationale
            
        self._audit("RELATIONSHIP", "REVIEW_RELATIONSHIP", reviewer_id, relationship_id, decision.model_dump())
        self.db.commit()

    def sync_approved_to_graph(self, document_id: str) -> Dict[str, Any]:
        """Push ACCEPTED/CORRECTED entities and relationships to Neo4j."""
        from apps.backend.app.graph.driver import neo4j_manager
        from apps.backend.app.graph.repository import GraphRepository
        
        entities = self.db.query(ExtractedEntity).filter(
            ExtractedEntity.document_id == document_id,
            ExtractedEntity.verification_status.in_(["ACCEPTED", "CORRECTED"]),
            ExtractedEntity.graph_sync_status != "SYNCED"
        ).all()
        
        relationships = self.db.query(ExtractedRelationship).filter(
            ExtractedRelationship.document_id == document_id,
            ExtractedRelationship.verification_status.in_(["ACCEPTED", "CORRECTED"]),
            ExtractedRelationship.graph_sync_status != "SYNCED"
        ).all()
        
        if not neo4j_manager.is_available():
            # Retryable fallback
            for e in entities:
                e.graph_sync_status = "RETRYABLE_FAILURE"
                e.graph_sync_error = "Neo4j Offline"
            for r in relationships:
                r.graph_sync_status = "RETRYABLE_FAILURE"
                r.graph_sync_error = "Neo4j Offline"
            self.db.commit()
            return {"status": "RETRYABLE_FAILURE", "reason": "Neo4j Offline"}
            
        try:
            with neo4j_manager.get_session() as session:
                repo = GraphRepository(session)
                # Sync Entities
                for e in entities:
                    props = {"name": e.canonical_name, "original_value": e.original_value, "source_document": document_id}
                    repo.create_or_merge_entity(e.entity_type.capitalize(), e.id, props, e.case_id, [document_id])
                    e.graph_sync_status = "SYNCED"
                    e.graph_synced_at = datetime.now(timezone.utc)
                    
                # Sync Relationships
                for r in relationships:
                    # Resolve endpoints
                    src = self.db.query(ExtractedEntity).filter(ExtractedEntity.id == r.source_entity_id).first()
                    tgt = self.db.query(ExtractedEntity).filter(ExtractedEntity.id == r.target_entity_id).first()
                    
                    if src.graph_sync_status == "SYNCED" and tgt.graph_sync_status == "SYNCED":
                        props = {"confidence": r.confidence_score, "verified_by": r.verified_by}
                        repo.create_or_merge_relationship(
                            src.entity_type.capitalize(), src.id, 
                            tgt.entity_type.capitalize(), tgt.id, 
                            r.relation_type, r.id, props
                        )
                        r.graph_sync_status = "SYNCED"
                        r.graph_synced_at = datetime.now(timezone.utc)
                    else:
                        r.graph_sync_status = "RETRYABLE_FAILURE"
                        r.graph_sync_error = "Endpoints not synced"
            
            self.db.commit()
            return {"status": "SUCCESS"}
        except Exception as ex:
            for e in entities:
                e.graph_sync_status = "RETRYABLE_FAILURE"
                e.graph_sync_error = str(ex)
            for r in relationships:
                r.graph_sync_status = "RETRYABLE_FAILURE"
                r.graph_sync_error = str(ex)
            self.db.commit()
            return {"status": "RETRYABLE_FAILURE", "reason": str(ex)}

    def _audit(self, target_type: str, action: str, user_id: str, record_id: str, details: dict):
        log = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=record_id,
            new_state=json.dumps(details),
            rationale=details.get("rationale")
        )
        self.db.add(log)
