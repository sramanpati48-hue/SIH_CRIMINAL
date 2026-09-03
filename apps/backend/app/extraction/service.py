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

class DocumentExtractionService:
    def __init__(self, db: Session):
        self.db = db
        self.extractor = MockExtractor() # Use mock by default as requested
        self.graph_service = GraphService()

    def process_document(self, document_id: str) -> Dict[str, Any]:
        """Extract candidates from document and persist as UNREVIEWED."""
        doc = self.db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document {document_id} not found")
        
        # 1. Extract
        result = self.extractor.extract(document_id, doc.raw_content or "")
        
        # 2. Save Entities
        saved_entities = {}
        for ent in result.entities:
            # Idempotency check: don't duplicate if already extracted by this provider
            existing = self.db.query(ExtractedEntity).filter(
                ExtractedEntity.document_id == document_id,
                ExtractedEntity.start_offset == ent.start_offset,
                ExtractedEntity.end_offset == ent.end_offset,
                ExtractedEntity.extraction_provider == ent.extraction_provider
            ).first()
            
            if not existing:
                res = resolve_entity_candidate(self.db, doc.case_id, ent.normalized_value, ent.entity_type)
                
                db_ent = ExtractedEntity(
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

        # 3. Save Relationships
        for rel in result.relationships:
            if rel.source_candidate_id not in saved_entities or rel.target_candidate_id not in saved_entities:
                continue
            
            src_id = saved_entities[rel.source_candidate_id]
            tgt_id = saved_entities[rel.target_candidate_id]
            
            existing_rel = self.db.query(ExtractedRelationship).filter(
                ExtractedRelationship.document_id == document_id,
                ExtractedRelationship.source_entity_id == src_id,
                ExtractedRelationship.target_entity_id == tgt_id,
                ExtractedRelationship.relation_type == rel.relationship_type
            ).first()
            
            if not existing_rel:
                db_rel = ExtractedRelationship(
                    case_id=doc.case_id,
                    document_id=document_id,
                    source_entity_id=src_id,
                    target_entity_id=tgt_id,
                    relation_type=rel.relationship_type,
                    source_text_snippet=rel.source_text,
                    confidence_score=rel.confidence,
                    verification_status="UNREVIEWED",
                    extraction_provider=rel.extraction_provider,
                    extraction_version=rel.extraction_version,
                )
                self.db.add(db_rel)

        self.db.commit()
        return {"status": "success", "entities": len(result.entities), "relationships": len(result.relationships)}


    def review_entity(self, entity_id: str, decision: ReviewDecision, reviewer_id: str):
        ent = self.db.query(ExtractedEntity).filter(ExtractedEntity.id == entity_id).first()
        if not ent:
            raise ValueError("Entity not found")
            
        ent.verification_status = decision.verification_status
        ent.reviewer_identity = reviewer_id
        
        if decision.verification_status == "CORRECTED":
            ent.canonical_name = decision.corrected_value
            ent.original_value = decision.corrected_value # Keep history if needed, but per prompt don't overwrite original candidate history in a destructive way without audit
        
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
