"""Entity Extraction Evaluation Metrics."""
from typing import List, Dict, Any, Tuple
import json

from pydantic import BaseModel

class EntityEvaluationMetrics(BaseModel):
    precision: float
    recall: float
    f1: float
    true_positives: int
    false_positives: int
    false_negatives: int
    per_label_precision: Dict[str, float]
    per_label_recall: Dict[str, float]
    per_label_f1: Dict[str, float]
    offset_mismatch_count: int
    entity_count_difference: int

def evaluate_entities(gold_entities: List[Dict[str, Any]], pred_entities: List[Dict[str, Any]]) -> EntityEvaluationMetrics:
    """Evaluate predicted entities against gold standard (exact span matching)."""
    
    # Pre-process gold
    gold_set = set()
    gold_by_label = {}
    for g in gold_entities:
        label = g.get("label", g.get("entity_type"))
        start = g.get("start_offset")
        end = g.get("end_offset")
        text = g.get("text", g.get("original_value", ""))
        item = (label, start, end, text)
        gold_set.add(item)
        
        if label not in gold_by_label:
            gold_by_label[label] = set()
        gold_by_label[label].add(item)

    # Pre-process preds
    pred_set = set()
    pred_by_label = {}
    for p in pred_entities:
        label = p.get("label", p.get("entity_type"))
        start = p.get("start_offset")
        end = p.get("end_offset")
        text = p.get("text", p.get("original_value", ""))
        item = (label, start, end, text)
        pred_set.add(item)
        
        if label not in pred_by_label:
            pred_by_label[label] = set()
        pred_by_label[label].add(item)
        
    # Global metrics
    tp = len(gold_set.intersection(pred_set))
    fp = len(pred_set - gold_set)
    fn = len(gold_set - pred_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # Per-label metrics
    all_labels = set(gold_by_label.keys()).union(set(pred_by_label.keys()))
    per_label_precision = {}
    per_label_recall = {}
    per_label_f1 = {}
    
    for label in all_labels:
        l_gold = gold_by_label.get(label, set())
        l_pred = pred_by_label.get(label, set())
        
        l_tp = len(l_gold.intersection(l_pred))
        l_fp = len(l_pred - l_gold)
        l_fn = len(l_gold - l_pred)
        
        l_p = l_tp / (l_tp + l_fp) if (l_tp + l_fp) > 0 else 0.0
        l_r = l_tp / (l_tp + l_fn) if (l_tp + l_fn) > 0 else 0.0
        l_f1 = 2 * l_p * l_r / (l_p + l_r) if (l_p + l_r) > 0 else 0.0
        
        per_label_precision[label] = l_p
        per_label_recall[label] = l_r
        per_label_f1[label] = l_f1
        
    # Offset mismatch count (same label, overlapping bounds but not exact match)
    offset_mismatch_count = 0
    # For every fn, is there an fp that overlaps?
    for fn_item in (gold_set - pred_set):
        g_label, g_start, g_end, _ = fn_item
        for fp_item in (pred_set - gold_set):
            p_label, p_start, p_end, _ = fp_item
            if g_label == p_label:
                # check overlap
                if max(g_start, p_start) < min(g_end, p_end):
                    offset_mismatch_count += 1
                    break
                    
    entity_count_difference = len(pred_set) - len(gold_set)
    
    return EntityEvaluationMetrics(
        precision=precision,
        recall=recall,
        f1=f1,
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        per_label_precision=per_label_precision,
        per_label_recall=per_label_recall,
        per_label_f1=per_label_f1,
        offset_mismatch_count=offset_mismatch_count,
        entity_count_difference=entity_count_difference
    )
