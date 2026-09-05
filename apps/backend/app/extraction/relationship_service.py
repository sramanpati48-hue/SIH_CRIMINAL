"""Service for extracting relationships deterministically."""
import hashlib
from typing import List, Optional, Tuple, Dict, Any

from sqlalchemy.orm import Session
from pydantic import ValidationError

from apps.backend.app.extraction.schemas import (
    ExtractedEntityCandidate,
    ExtractedRelationshipCandidate,
)
from apps.backend.app.models.relationship import ExtractedRelationship
from apps.backend.app.extraction.relationship_rules import run_all_rules, RELATIONSHIP_RULE_VERSION


class RelationshipExtractionService:
    def __init__(self, db: Session, provider: str, extraction_version: str, extraction_run_id: str = None):
        self.db = db
        self.provider = provider
        self.extraction_version = extraction_version
        self.rule_version = RELATIONSHIP_RULE_VERSION
        self.extraction_run_id = extraction_run_id

    def generate_candidate_id(
        self,
        document_id: str,
        source_id: str,
        rel_type: str,
        target_id: str,
        evidence_text: str,
        event_date: Optional[str]
    ) -> str:
        unique_string = f"{document_id}|{source_id}|{rel_type}|{target_id}|{self.rule_version}|{evidence_text}|{event_date}"
        hash_digest = hashlib.sha256(unique_string.encode("utf-8")).hexdigest()[:16]
        return f"rel_{hash_digest}"

    def extract_relationships(
        self,
        document_id: str,
        case_id: str,
        source_text: str,
        entities: List[ExtractedEntityCandidate]
    ) -> List[ExtractedRelationshipCandidate]:
        
        matches = run_all_rules(document_id, source_text, entities)
        
        candidates = []
        for match in matches:
            # Handle ambiguity: if multiple entities match the same offsets
            # For simplicity in this deterministic ruleset, the rules only output specific pairs.
            # Real ambiguity handling would check if another pair matched the exact same bounds.
            
            # Generate ID
            cand_id = self.generate_candidate_id(
                document_id,
                match.source.candidate_id,
                match.relation_type,
                match.target.candidate_id,
                match.evidence_text,
                None
            )
            
            try:
                candidate = ExtractedRelationshipCandidate(
                    candidate_id=cand_id,
                    source_candidate_id=match.source.candidate_id,
                    relationship_type=match.relation_type,
                    target_candidate_id=match.target.candidate_id,
                    source_document_id=document_id,
                    case_id=case_id,
                    source_text=source_text,
                    start_offset=match.start_offset,
                    end_offset=match.end_offset,
                    evidence_text=match.evidence_text,
                    event_date=None,
                    confidence=match.confidence,
                    verification_status="UNREVIEWED",
                    extraction_provider=self.provider,
                    extraction_version=self.extraction_version,
                    relationship_rule_version=self.rule_version,
                    source_record_id=None
                )
                candidates.append(candidate)
            except ValidationError:
                # Log warning or handle
                pass
                
        # Deduplicate
        seen = set()
        final_candidates = []
        for c in candidates:
            if c.candidate_id not in seen:
                seen.add(c.candidate_id)
                final_candidates.append(c)
                
        return final_candidates

    def persist_candidates(self, candidates: List[ExtractedRelationshipCandidate]) -> List[ExtractedRelationship]:
        # Idempotent persistence
        persisted = []
        for cand in candidates:
            # Map candidate_id to actual DB entity IDs. 
            # The schemas.py schema has source_candidate_id but the DB model ExtractedRelationship needs source_entity_id.
            # We need to lookup the actual ExtractedEntity PK by candidate_id.
            from apps.backend.app.models.entity import ExtractedEntity
            
            src_ent = self.db.query(ExtractedEntity).filter_by(document_id=cand.source_document_id, id=cand.source_candidate_id).first()
            if not src_ent:
                # Try finding by candidate_id if candidate_id was stored somewhere. But wait, ExtractedEntity doesn't store candidate_id natively?
                # Actually, ExtractedEntity ID IS the candidate_id in our pipeline when created.
                src_ent = self.db.query(ExtractedEntity).filter_by(id=cand.source_candidate_id).first()
                
            tgt_ent = self.db.query(ExtractedEntity).filter_by(id=cand.target_candidate_id).first()
            
            if not src_ent or not tgt_ent:
                continue

            existing = self.db.query(ExtractedRelationship).filter_by(
                document_id=cand.source_document_id,
                source_entity_id=src_ent.id,
                target_entity_id=tgt_ent.id,
                relation_type=cand.relationship_type,
                relationship_rule_version=cand.relationship_rule_version
            ).first()

            if not existing:
                db_rel = ExtractedRelationship(
                    id=cand.candidate_id,
                    extraction_run_id=self.extraction_run_id,
                    case_id=cand.case_id,
                    document_id=cand.source_document_id,
                    source_entity_id=src_ent.id,
                    target_entity_id=tgt_ent.id,
                    relation_type=cand.relationship_type,
                    source_text_snippet=cand.evidence_text,
                    start_offset=cand.start_offset,
                    end_offset=cand.end_offset,
                    event_timestamp=None,
                    confidence_score=cand.confidence,
                    verification_status=cand.verification_status,
                    extraction_provider=cand.extraction_provider,
                    extraction_version=cand.extraction_version,
                    relationship_rule_version=cand.relationship_rule_version
                )
                self.db.add(db_rel)
                self.db.flush()
                persisted.append(db_rel)
            else:
                persisted.append(existing)
        
        self.db.commit()
        return persisted
