"""Relationship Extraction Evaluation Metrics."""
from typing import List, Dict, Any, Tuple
import json

from pydantic import BaseModel

class RelationshipEvaluationMetrics(BaseModel):
    exact_relationship_precision: float
    exact_relationship_recall: float
    exact_relationship_f1: float
    true_positives: int
    false_positives: int
    false_negatives: int
    evidence_offset_mismatch_count: int
    missing_evidence_count: int
    unknown_endpoint_count: int
    unsupported_relationship_type_count: int
    per_relationship_type_precision: Dict[str, float]
    per_relationship_type_recall: Dict[str, float]
    per_relationship_type_f1: Dict[str, float]

def evaluate_relationships(gold_rels: List[Dict[str, Any]], pred_rels: List[Dict[str, Any]], 
                           gold_entities: List[Dict[str, Any]], pred_entities: List[Dict[str, Any]]) -> RelationshipEvaluationMetrics:
    """Evaluate relationships based on endpoint and type matching."""
    
    # We need a way to map pred_entities to gold_entities to verify endpoints.
    # We will map entities by their exact identity: (label, start, end, text)
    gold_ent_map = {} # candidate_id -> identity
    for g in gold_entities:
        c_id = g.get("candidate_id") or g.get("id")
        identity = (g.get("label", g.get("entity_type")), g.get("start_offset"), g.get("end_offset"), g.get("text", g.get("original_value", "")))
        gold_ent_map[c_id] = identity
        
    pred_ent_map = {} # candidate_id -> identity
    for p in pred_entities:
        c_id = p.get("candidate_id") or p.get("id")
        identity = (p.get("label", p.get("entity_type")), p.get("start_offset"), p.get("end_offset"), p.get("text", p.get("original_value", "")))
        pred_ent_map[c_id] = identity

    # Build relationship identities
    gold_set = set()
    gold_by_type = {}
    for g in gold_rels:
        s_id = g.get("source_candidate_id", g.get("source_entity_id"))
        t_id = g.get("target_candidate_id", g.get("target_entity_id"))
        r_type = g.get("relationship_type", g.get("relation_type"))
        
        s_ident = gold_ent_map.get(s_id)
        t_ident = gold_ent_map.get(t_id)
        
        if s_ident and t_ident:
            item = (s_ident, r_type, t_ident)
            gold_set.add(item)
            if r_type not in gold_by_type:
                gold_by_type[r_type] = set()
            gold_by_type[r_type].add(item)

    pred_set = set()
    pred_by_type = {}
    unknown_endpoint_count = 0
    missing_evidence_count = 0
    
    for p in pred_rels:
        s_id = p.get("source_candidate_id", p.get("source_entity_id"))
        t_id = p.get("target_candidate_id", p.get("target_entity_id"))
        r_type = p.get("relationship_type", p.get("relation_type"))
        
        s_ident = pred_ent_map.get(s_id)
        t_ident = pred_ent_map.get(t_id)
        
        if not p.get("evidence_text"):
            missing_evidence_count += 1
            
        if s_ident and t_ident:
            item = (s_ident, r_type, t_ident)
            pred_set.add(item)
            if r_type not in pred_by_type:
                pred_by_type[r_type] = set()
            pred_by_type[r_type].add(item)
        else:
            unknown_endpoint_count += 1

    # Metrics calculation
    tp = len(gold_set.intersection(pred_set))
    fp = len(pred_set - gold_set)
    fn = len(gold_set - pred_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    per_type_precision = {}
    per_type_recall = {}
    per_type_f1 = {}
    
    all_types = set(gold_by_type.keys()).union(set(pred_by_type.keys()))
    for t in all_types:
        t_gold = gold_by_type.get(t, set())
        t_pred = pred_by_type.get(t, set())
        
        t_tp = len(t_gold.intersection(t_pred))
        t_fp = len(t_pred - t_gold)
        t_fn = len(t_gold - t_pred)
        
        t_p = t_tp / (t_tp + t_fp) if (t_tp + t_fp) > 0 else 0.0
        t_r = t_tp / (t_tp + t_fn) if (t_tp + t_fn) > 0 else 0.0
        t_f1 = 2 * t_p * t_r / (t_p + t_r) if (t_p + t_r) > 0 else 0.0
        
        per_type_precision[t] = t_p
        per_type_recall[t] = t_r
        per_type_f1[t] = t_f1

    # unsupported relationship types
    # from our mapping rules, everything generated should be in the list, but we can compute it if needed
    unsupported_relationship_type_count = 0
    supported_types = {"CALLED", "USED", "OWNS", "VISITED", "TRANSFERRED_TO", "INVOLVED_IN", "MENTIONED_IN", "CONNECTED_TO", "OCCURRED_AT"}
    for p in pred_rels:
        r_type = p.get("relationship_type", p.get("relation_type"))
        if r_type not in supported_types:
            unsupported_relationship_type_count += 1
            
    evidence_offset_mismatch_count = 0 # Future enhancement
            
    return RelationshipEvaluationMetrics(
        exact_relationship_precision=precision,
        exact_relationship_recall=recall,
        exact_relationship_f1=f1,
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        evidence_offset_mismatch_count=evidence_offset_mismatch_count,
        missing_evidence_count=missing_evidence_count,
        unknown_endpoint_count=unknown_endpoint_count,
        unsupported_relationship_type_count=unsupported_relationship_type_count,
        per_relationship_type_precision=per_type_precision,
        per_relationship_type_recall=per_type_recall,
        per_relationship_type_f1=per_type_f1
    )
