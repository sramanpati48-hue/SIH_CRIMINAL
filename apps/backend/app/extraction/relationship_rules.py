"""Deterministic extraction rules for relationships."""
import re
from typing import List, Optional, Tuple, Dict
from apps.backend.app.extraction.schemas import ExtractedEntityCandidate

RELATIONSHIP_RULE_VERSION = "1.0.0"

class RelationshipMatch:
    def __init__(
        self,
        source: ExtractedEntityCandidate,
        target: ExtractedEntityCandidate,
        relation_type: str,
        evidence_text: str,
        start_offset: Optional[int],
        end_offset: Optional[int],
        confidence: float
    ):
        self.source = source
        self.target = target
        self.relation_type = relation_type
        self.evidence_text = evidence_text
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.confidence = confidence

def find_evidence_bounds(text: str, source: ExtractedEntityCandidate, target: ExtractedEntityCandidate, verb_pattern: str) -> Optional[Tuple[int, int, str]]:
    """Helper to find the bounding offsets and exact evidence string."""
    # Ensure source and target are ordered as they appear in the text
    first, second = sorted([source, target], key=lambda x: x.start_offset)
    # The verb must occur between the two entities
    between_text = text[first.end_offset:second.start_offset]
    if re.search(verb_pattern, between_text, re.IGNORECASE):
        start = first.start_offset
        end = second.end_offset
        return start, end, text[start:end]
    return None


def extract_called(text: str, entities: List[ExtractedEntityCandidate]) -> List[RelationshipMatch]:
    matches = []
    people = [e for e in entities if e.entity_type == "PERSON"]
    phones = [e for e in entities if e.entity_type == "PHONE"]
    
    # Person to Person
    for i, p1 in enumerate(people):
        for p2 in people[i+1:]:
            bounds = find_evidence_bounds(text, p1, p2, r'\b(called|contacted.*by phone|spoke with)\b')
            if bounds:
                matches.append(RelationshipMatch(p1, p2, "CALLED", bounds[2], bounds[0], bounds[1], 0.95))
                if "spoke with" in bounds[2].lower():
                    matches.append(RelationshipMatch(p2, p1, "CALLED", bounds[2], bounds[0], bounds[1], 0.95))
                    
    # Person to Phone
    for p in people:
        for ph in phones:
            bounds = find_evidence_bounds(text, p, ph, r'\b(called|contacted.*by phone|spoke with)\b')
            if bounds:
                if p.start_offset < ph.start_offset:
                    matches.append(RelationshipMatch(p, ph, "CALLED", bounds[2], bounds[0], bounds[1], 0.95))
    return matches


def extract_used(text: str, entities: List[ExtractedEntityCandidate]) -> List[RelationshipMatch]:
    matches = []
    people = [e for e in entities if e.entity_type == "PERSON"]
    vehicles_phones = [e for e in entities if e.entity_type in ("VEHICLE", "PHONE")]
    for p in people:
        for v in vehicles_phones:
            bounds = find_evidence_bounds(text, p, v, r'\b(used|travelled in)\b')
            if bounds:
                # Ensure the person comes before the object in the sentence
                if p.start_offset < v.start_offset:
                    matches.append(RelationshipMatch(p, v, "USED", bounds[2], bounds[0], bounds[1], 0.95))
    return matches


def extract_owns(text: str, entities: List[ExtractedEntityCandidate]) -> List[RelationshipMatch]:
    matches = []
    people = [e for e in entities if e.entity_type == "PERSON"]
    assets = [e for e in entities if e.entity_type in ("VEHICLE", "BANK_ACCOUNT")]
    for p in people:
        for a in assets:
            bounds = find_evidence_bounds(text, p, a, r'\b(owns|owned|is the owner of)\b')
            if bounds:
                if p.start_offset < a.start_offset:
                    matches.append(RelationshipMatch(p, a, "OWNS", bounds[2], bounds[0], bounds[1], 0.95))
    return matches


def extract_visited(text: str, entities: List[ExtractedEntityCandidate]) -> List[RelationshipMatch]:
    matches = []
    people = [e for e in entities if e.entity_type == "PERSON"]
    locations = [e for e in entities if e.entity_type == "LOCATION"]
    for p in people:
        for l in locations:
            bounds = find_evidence_bounds(text, p, l, r'\b(visited|was seen at|travelled to)\b')
            if bounds:
                if p.start_offset < l.start_offset:
                    matches.append(RelationshipMatch(p, l, "VISITED", bounds[2], bounds[0], bounds[1], 0.95))
    return matches


def extract_transferred_to(text: str, entities: List[ExtractedEntityCandidate]) -> List[RelationshipMatch]:
    matches = []
    # "PERSON transferred MONEY to PERSON"
    # "PERSON transferred MONEY to BANK_ACCOUNT"
    # "BANK_ACCOUNT transferred MONEY to BANK_ACCOUNT"
    # For now, we will simplify by looking for transferring entities
    actors = [e for e in entities if e.entity_type in ("PERSON", "BANK_ACCOUNT")]
    for i, a1 in enumerate(actors):
        for a2 in actors:
            if a1.candidate_id == a2.candidate_id:
                continue
            bounds = find_evidence_bounds(text, a1, a2, r'\b(transferred.*to|sent.*to)\b')
            if bounds:
                if a1.start_offset < a2.start_offset:
                    matches.append(RelationshipMatch(a1, a2, "TRANSFERRED_TO", bounds[2], bounds[0], bounds[1], 0.85))
    return matches


def extract_involved_in(text: str, entities: List[ExtractedEntityCandidate]) -> List[RelationshipMatch]:
    matches = []
    people = [e for e in entities if e.entity_type == "PERSON"]
    cases = [e for e in entities if e.entity_type == "CASE_ID"]
    for p in people:
        for c in cases:
            bounds = find_evidence_bounds(text, p, c, r'\b(is mentioned in|is linked to|is involved in)\b')
            if bounds:
                matches.append(RelationshipMatch(p, c, "INVOLVED_IN", bounds[2], bounds[0], bounds[1], 0.95))
    return matches


def extract_mentioned_in(document_id: str, text: str, entities: List[ExtractedEntityCandidate]) -> List[RelationshipMatch]:
    # Creates MENTIONED_IN if they are in the text.
    # The requirement: "Connect an entity to a document only when the entity appears in the source text."
    # Since they are extracted entities, they appear in the text.
    # But wait, MENTIONED_IN connects an entity to a document. Since documents aren't extracted entities, 
    # MENTIONED_IN is usually `ExtractedRelationshipCandidate` where target is a Document?
    # But target_candidate_id must point to an entity candidate.
    # If the rule means connecting entity to document, we might need a fake candidate ID for the document?
    # Wait, the prompt says: "Connect an entity to a document only when the entity appears in the source text."
    # But `target_candidate_id` must reference a valid candidate. 
    # Usually, MENTIONED_IN connects PERSON -> CASE_ID or PERSON -> Document? 
    # Actually, MENTIONED_IN might just be skipped for now if it requires pointing to a Document that isn't an entity.
    # Let's just create it if we have a CASE_ID entity.
    matches = []
    # If MENTIONED_IN is person -> document, we need a special way to represent the document.
    return matches


def extract_connected_to(text: str, entities: List[ExtractedEntityCandidate]) -> List[RelationshipMatch]:
    matches = []
    # "Use only when the text explicitly states a connection."
    for i, e1 in enumerate(entities):
        for e2 in entities[i+1:]:
            bounds = find_evidence_bounds(text, e1, e2, r'\b(is connected to|has a connection with)\b')
            if bounds:
                matches.append(RelationshipMatch(e1, e2, "CONNECTED_TO", bounds[2], bounds[0], bounds[1], 0.95))
                matches.append(RelationshipMatch(e2, e1, "CONNECTED_TO", bounds[2], bounds[0], bounds[1], 0.95))
    return matches


def extract_occurred_at(text: str, entities: List[ExtractedEntityCandidate]) -> List[RelationshipMatch]:
    matches = []
    # "Connect an event or relationship to a location only when explicitly associated."
    # We can connect CASE_ID -> LOCATION
    cases = [e for e in entities if e.entity_type == "CASE_ID"]
    locations = [e for e in entities if e.entity_type == "LOCATION"]
    for c in cases:
        for l in locations:
            bounds = find_evidence_bounds(text, c, l, r'\b(occurred at|happened in|took place at)\b')
            if bounds:
                matches.append(RelationshipMatch(c, l, "OCCURRED_AT", bounds[2], bounds[0], bounds[1], 0.95))
    return matches

def run_all_rules(document_id: str, text: str, entities: List[ExtractedEntityCandidate]) -> List[RelationshipMatch]:
    all_matches = []
    all_matches.extend(extract_called(text, entities))
    all_matches.extend(extract_used(text, entities))
    all_matches.extend(extract_owns(text, entities))
    all_matches.extend(extract_visited(text, entities))
    all_matches.extend(extract_transferred_to(text, entities))
    all_matches.extend(extract_involved_in(text, entities))
    all_matches.extend(extract_connected_to(text, entities))
    all_matches.extend(extract_occurred_at(text, entities))
    return all_matches
