"""Comparison of Rules, Anomalies, and Similarities."""

def generate_comparison(rule_alerts: list, anomaly_pred=None, priority_pred=None, similarity_matches=None):
    """Generates an agreement status and explanation based on different model outputs."""
    
    has_rules = len(rule_alerts) > 0
    has_model = False
    model_flags = False
    
    if priority_pred and isinstance(priority_pred, dict) and priority_pred.get("status") == "INSUFFICIENT_DATA":
        priority_pred = None # Invalid

    if priority_pred:
        has_model = True
        if priority_pred.prediction in ["HIGH", "CRITICAL"]:
            model_flags = True
    
    if anomaly_pred:
        has_model = True
        if anomaly_pred.prediction == "ANOMALOUS":
            model_flags = True
            
    has_similarity = similarity_matches and len(similarity_matches) > 0
    
    if has_rules and model_flags:
        status = "RULES_AND_MODEL_AGREE"
        explanation = "Deterministic rule alerts and machine learning models both flag this case for review."
    elif has_rules and not model_flags:
        status = "RULES_ONLY"
        explanation = "Rule-based patterns triggered alerts, but ML models did not find significant structural anomalies."
    elif not has_rules and model_flags:
        status = "MODEL_ONLY"
        explanation = "No specific deterministic rules triggered, but ML models identified structural anomalies requiring review."
    elif not has_rules and not model_flags and has_similarity:
        status = "SIMILARITY_ONLY"
        explanation = "No rules or direct model alerts, but historical similarity matches exist."
    elif not has_rules and not model_flags and not has_model:
        status = "INSUFFICIENT_DATA"
        explanation = "Insufficient data to train ML models and no rule alerts triggered."
    else:
        status = "REQUIRES_REVIEW"
        explanation = "Standard review required."
        
    return {
        "status": status,
        "explanation": explanation
    }
