"""Deterministic mock extraction provider."""
import re
from apps.backend.app.extraction.providers import ExtractorProvider
from apps.backend.app.extraction.schemas import (
    DocumentExtractionResult,
    ExtractedEntityCandidate,
    ExtractedRelationshipCandidate
)
from apps.backend.app.extraction.normalization import normalize_entity_value

class MockExtractor(ExtractorProvider):
    """Deterministic mock extractor for synthetic case reports."""
    
    @property
    def provider_name(self) -> str:
        return "MOCK_EXTRACTOR"

    @property
    def provider_version(self) -> str:
        return "1.0.0"
        
    @property
    def model_version(self) -> str:
        return "1.0.0"

    @property
    def extraction_version(self) -> str:
        return "1.0.0"

    def extract_entities(self, document_id: str, document_text: str) -> list[ExtractedEntityCandidate]:
        entities: list[ExtractedEntityCandidate] = []

        # 1. Phone numbers
        phone_matches = re.finditer(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", document_text)
        for i, match in enumerate(phone_matches):
            val = match.group(0)
            entities.append(ExtractedEntityCandidate(
                candidate_id=f"ent_phone_{i}",
                entity_type="PHONE",
                original_value=val,
                normalized_value=normalize_entity_value("PHONE", val),
                source_document_id=document_id,
                source_text=val,
                start_offset=match.start(),
                end_offset=match.end(),
                confidence=0.95,
                verification_status="UNREVIEWED",
                extraction_provider=self.provider_name,
                extraction_version=self.provider_version,
            ))

        # 2. People
        person_matches = re.finditer(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", document_text)
        for i, match in enumerate(person_matches):
            val = match.group(0)
            if val in ["Case Report", "Synthetic Case"]:
                continue
            entities.append(ExtractedEntityCandidate(
                candidate_id=f"ent_person_{i}",
                entity_type="PERSON",
                original_value=val,
                normalized_value=normalize_entity_value("PERSON", val),
                source_document_id=document_id,
                source_text=val,
                start_offset=match.start(),
                end_offset=match.end(),
                confidence=0.60 if "lowconf" in document_text.lower() and i == 0 else 0.90,
                verification_status="UNREVIEWED",
                extraction_provider=self.provider_name,
                extraction_version=self.provider_version,
            ))

        # 3. Dates
        date_matches = re.finditer(r"\d{4}-\d{2}-\d{2}", document_text)
        for i, match in enumerate(date_matches):
            val = match.group(0)
            entities.append(ExtractedEntityCandidate(
                candidate_id=f"ent_date_{i}",
                entity_type="DATE",
                original_value=val,
                normalized_value=normalize_entity_value("DATE", val),
                source_document_id=document_id,
                source_text=val,
                start_offset=match.start(),
                end_offset=match.end(),
                confidence=0.99,
                verification_status="UNREVIEWED",
                extraction_provider=self.provider_name,
                extraction_version=self.provider_version,
            ))

        # 4. Money
        money_matches = re.finditer(r"\$\d+(?:,\d{3})*(?:\.\d{2})?", document_text)
        for i, match in enumerate(money_matches):
            val = match.group(0)
            entities.append(ExtractedEntityCandidate(
                candidate_id=f"ent_money_{i}",
                entity_type="MONEY",
                original_value=val,
                normalized_value=normalize_entity_value("MONEY", val),
                source_document_id=document_id,
                source_text=val,
                start_offset=match.start(),
                end_offset=match.end(),
                confidence=0.92,
                verification_status="UNREVIEWED",
                extraction_provider=self.provider_name,
                extraction_version=self.provider_version,
            ))

        # 5. Bank Accounts
        bank_matches = re.finditer(r"\b(?:BA\d{3,}|ACC[-_]?\d{4,})\b", document_text)
        for i, match in enumerate(bank_matches):
            val = match.group(0)
            entities.append(ExtractedEntityCandidate(
                candidate_id=f"ent_bank_{i}",
                entity_type="BANK_ACCOUNT",
                original_value=val,
                normalized_value=normalize_entity_value("BANK_ACCOUNT", val),
                source_document_id=document_id,
                source_text=val,
                start_offset=match.start(),
                end_offset=match.end(),
                confidence=0.91,
                verification_status="UNREVIEWED",
                extraction_provider=self.provider_name,
                extraction_version=self.provider_version,
            ))

        # 6. Vehicles
        veh_matches = re.finditer(r"\b[A-Z]{3}-\d{4}\b", document_text)
        for i, match in enumerate(veh_matches):
            val = match.group(0)
            entities.append(ExtractedEntityCandidate(
                candidate_id=f"ent_vehicle_{i}",
                entity_type="VEHICLE",
                original_value=val,
                normalized_value=normalize_entity_value("VEHICLE", val),
                source_document_id=document_id,
                source_text=val,
                start_offset=match.start(),
                end_offset=match.end(),
                confidence=0.88,
                verification_status="UNREVIEWED",
                extraction_provider=self.provider_name,
                extraction_version=self.provider_version,
            ))

        return entities

    def extract_relationships(
        self, document_id: str, document_text: str, entities: list[ExtractedEntityCandidate]
    ) -> list[ExtractedRelationshipCandidate]:
        relationships: list[ExtractedRelationshipCandidate] = []

        person_candidates = [e for e in entities if e.entity_type == "PERSON"]
        phone_candidates = [e for e in entities if e.entity_type == "PHONE"]
        veh_candidates = [e for e in entities if e.entity_type == "VEHICLE"]
        bank_candidates = [e for e in entities if e.entity_type == "BANK_ACCOUNT"]

        # CALLED: First person -> First phone
        if person_candidates and phone_candidates:
            start_off = person_candidates[0].start_offset
            end_off = max(phone_candidates[0].end_offset, start_off + 5)
            snippet = document_text[start_off:end_off] if end_off <= len(document_text) else person_candidates[0].original_value
            if not snippet.strip():
                snippet = f"{person_candidates[0].original_value} called {phone_candidates[0].original_value}"

            relationships.append(ExtractedRelationshipCandidate(
                candidate_id="rel_called_0",
                source_candidate_id=person_candidates[0].candidate_id,
                relationship_type="CALLED",
                target_candidate_id=phone_candidates[0].candidate_id,
                source_document_id=document_id,
                case_id="MOCK_CASE",
                source_text=snippet,
                confidence=0.85,
                verification_status="UNREVIEWED",
                extraction_provider=self.provider_name,
                extraction_version=self.provider_version,
                relationship_rule_version="mock"
            ))

        # OWNS: First person -> First vehicle
        if person_candidates and veh_candidates:
            start_off = person_candidates[0].start_offset
            end_off = max(veh_candidates[0].end_offset, start_off + 5)
            snippet = document_text[start_off:end_off] if end_off <= len(document_text) else person_candidates[0].original_value
            if not snippet.strip():
                snippet = f"{person_candidates[0].original_value} owns {veh_candidates[0].original_value}"

            relationships.append(ExtractedRelationshipCandidate(
                candidate_id="rel_owns_0",
                source_candidate_id=person_candidates[0].candidate_id,
                relationship_type="OWNS",
                target_candidate_id=veh_candidates[0].candidate_id,
                source_document_id=document_id,
                case_id="MOCK_CASE",
                source_text=snippet,
                confidence=0.80,
                verification_status="UNREVIEWED",
                extraction_provider=self.provider_name,
                extraction_version=self.provider_version,
                relationship_rule_version="mock"
            ))

        # TRANSFERRED_TO: First person -> First bank account
        if person_candidates and bank_candidates:
            snippet = f"{person_candidates[0].original_value} transferred to {bank_candidates[0].original_value}"
            relationships.append(ExtractedRelationshipCandidate(
                candidate_id="rel_transfer_0",
                source_candidate_id=person_candidates[0].candidate_id,
                relationship_type="TRANSFERRED_TO",
                target_candidate_id=bank_candidates[0].candidate_id,
                source_document_id=document_id,
                case_id="MOCK_CASE",
                source_text=snippet,
                confidence=0.9,
                verification_status="UNREVIEWED",
                extraction_provider=self.provider_name,
                extraction_version=self.provider_version,
                relationship_rule_version="mock"
            ))

        return relationships

    def extract(self, document_id: str, document_text: str) -> DocumentExtractionResult:
        entities = self.extract_entities(document_id, document_text)
        relationships = self.extract_relationships(document_id, document_text, entities)

        return DocumentExtractionResult(
            document_id=document_id,
            entities=entities,
            relationships=relationships,
            provider=self.provider_name,
            version=self.provider_version,
        )
