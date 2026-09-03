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

    def extract(self, document_id: str, document_text: str) -> DocumentExtractionResult:
        entities = []
        relationships = []
        
        # Very simple deterministic rules based on regex for the mock data
        # Phone: (123) 456-7890 or 123-456-7890
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
                extraction_version=self.provider_version
            ))

        # Person: Looking for capitalized words like John Doe
        person_matches = re.finditer(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", document_text)
        for i, match in enumerate(person_matches):
            val = match.group(0)
            # Filter out some false positives manually if needed
            if val in ["Case Report", "Synthetic Case"]: continue
            entities.append(ExtractedEntityCandidate(
                candidate_id=f"ent_person_{i}",
                entity_type="PERSON",
                original_value=val,
                normalized_value=normalize_entity_value("PERSON", val),
                source_document_id=document_id,
                source_text=val,
                start_offset=match.start(),
                end_offset=match.end(),
                # Inject a low confidence example for review
                confidence=0.60 if "lowconf" in document_text.lower() and i == 0 else 0.90,
                verification_status="UNREVIEWED",
                extraction_provider=self.provider_name,
                extraction_version=self.provider_version
            ))

        # Date: YYYY-MM-DD
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
                extraction_version=self.provider_version
            ))

        # Connect the first person to the first phone as CALLED
        person_candidates = [e for e in entities if e.entity_type == "PERSON"]
        phone_candidates = [e for e in entities if e.entity_type == "PHONE"]
        
        if person_candidates and phone_candidates:
            rel_source_text = f"{person_candidates[0].original_value} called {phone_candidates[0].original_value}"
            # find if that text exists, else just mock the offset from person
            start_off = person_candidates[0].start_offset
            end_off = phone_candidates[0].end_offset if phone_candidates[0].end_offset > start_off else start_off + 10
            
            relationships.append(ExtractedRelationshipCandidate(
                candidate_id="rel_1",
                source_candidate_id=person_candidates[0].candidate_id,
                relationship_type="CALLED",
                target_candidate_id=phone_candidates[0].candidate_id,
                source_document_id=document_id,
                source_text=document_text[start_off:end_off] if end_off > start_off else person_candidates[0].original_value,
                confidence=0.85,
                verification_status="UNREVIEWED",
                extraction_provider=self.provider_name,
                extraction_version=self.provider_version
            ))

        return DocumentExtractionResult(
            document_id=document_id,
            entities=entities,
            relationships=relationships,
            provider=self.provider_name,
            version=self.provider_version
        )
