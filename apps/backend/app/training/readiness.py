import os
import json
from typing import List, Dict, Any, Tuple
from collections import defaultdict

from apps.backend.app.training.schemas import ReadinessStatus, SplitStatus, LabelCounts

# Safeguards / defaults, ideally loaded from config
NER_MIN_TRAIN_DOCUMENTS = int(os.getenv("NER_MIN_TRAIN_DOCUMENTS", "30"))
NER_MIN_VALIDATION_DOCUMENTS = int(os.getenv("NER_MIN_VALIDATION_DOCUMENTS", "10"))
NER_MIN_TEST_DOCUMENTS = int(os.getenv("NER_MIN_TEST_DOCUMENTS", "10"))
NER_MIN_EXAMPLES_PER_LABEL = int(os.getenv("NER_MIN_EXAMPLES_PER_LABEL", "5"))
NER_TRAINING_ENABLED = os.getenv("NER_TRAINING_ENABLED", "false").lower() == "true"

REQUIRED_LABELS = {"PERSON", "PHONE", "LOCATION", "ORGANIZATION"}
ALLOW_LISTED_LABELS = {"PERSON", "ALIAS", "PHONE", "VEHICLE", "LOCATION", "ORGANIZATION", "BANK_ACCOUNT", "CASE_ID", "DATE", "MONEY"}

def check_training_readiness(data_dir: str = "data/synthetic/ner") -> ReadinessStatus:
    errors = []
    warnings = []
    
    train_path = os.path.join(data_dir, "train.jsonl")
    val_path = os.path.join(data_dir, "validation.jsonl")
    test_path = os.path.join(data_dir, "test.jsonl")
    
    global_doc_ids = set()
    
    def analyze_split(path: str, min_docs: int) -> Tuple[SplitStatus, set]:
        if not os.path.exists(path):
            return SplitStatus(exists=False, document_count=0, entity_count=0, label_distribution=[]), set()
            
        doc_count = 0
        ent_count = 0
        label_counts = defaultdict(int)
        doc_ids = set()
        
        with open(path, 'r', encoding='utf-8') as f:
            for line_no, line in enumerate(f, 1):
                if not line.strip(): continue
                try:
                    doc = json.loads(line)
                    doc_id = doc.get("id", doc.get("document_id"))
                    if not doc_id:
                        errors.append(f"{path}:{line_no} - Missing document ID")
                        continue
                        
                    if doc_id in doc_ids:
                        errors.append(f"{path}:{line_no} - Duplicate document ID {doc_id} within split")
                    doc_ids.add(doc_id)
                    
                    if doc_id in global_doc_ids:
                        errors.append(f"Document ID {doc_id} appears in multiple splits! Split leakage detected.")
                    global_doc_ids.add(doc_id)
                    
                    doc_count += 1
                    
                    text = doc.get("text", doc.get("content", ""))
                    for ent in doc.get("entities", []):
                        ent_count += 1
                        label = ent.get("label", ent.get("entity_type"))
                        if label not in ALLOW_LISTED_LABELS:
                            errors.append(f"{path} - Unsupported label '{label}' in doc {doc_id}")
                            
                        start = ent.get("start")
                        if start is None:
                            start = ent.get("start_offset")
                        end = ent.get("end")
                        if end is None:
                            end = ent.get("end_offset")
                            
                        if start is None or end is None or start >= end or end > len(text):
                            errors.append(f"{path} - Invalid offsets for entity in doc {doc_id}")
                            
                        # Validate text match
                        ent_text = ent.get("text", ent.get("original_value", ""))
                        if start is not None and end is not None:
                            if text[start:end] != ent_text:
                                errors.append(f"{path} - Offset mismatch in doc {doc_id}. Expected '{ent_text}', found '{text[start:end]}'")
                        
                        label_counts[label] += 1
                        
                except Exception as e:
                    errors.append(f"{path}:{line_no} - JSON parsing or validation error: {str(e)}")
                    
        if doc_count < min_docs:
            errors.append(f"{path} has {doc_count} docs, which is below the minimum {min_docs}")
            
        l_counts = []
        for label, count in label_counts.items():
            is_suff = count >= NER_MIN_EXAMPLES_PER_LABEL
            l_counts.append(LabelCounts(label=label, count=count, is_sufficient=is_suff))
            if not is_suff and label in REQUIRED_LABELS:
                warnings.append(f"{path} - Underrepresented critical label {label} ({count} < {NER_MIN_EXAMPLES_PER_LABEL})")
            
        return SplitStatus(
            exists=True,
            document_count=doc_count,
            entity_count=ent_count,
            label_distribution=l_counts
        ), doc_ids

    train_stat, train_docs = analyze_split(train_path, NER_MIN_TRAIN_DOCUMENTS)
    val_stat, val_docs = analyze_split(val_path, NER_MIN_VALIDATION_DOCUMENTS)
    test_stat, test_docs = analyze_split(test_path, NER_MIN_TEST_DOCUMENTS)
    
    if not train_stat.exists: errors.append(f"Train split not found at {train_path}")
    if not val_stat.exists: errors.append(f"Validation split not found at {val_path}")
    if not test_stat.exists: errors.append(f"Test split not found at {test_path}")
    
    if not NER_TRAINING_ENABLED:
        errors.append("NER_TRAINING_ENABLED is false. Training is disabled.")
        
    status = "NOT_READY"
    if not errors:
        status = "READY_WITH_WARNINGS" if warnings else "READY"

    return ReadinessStatus(
        status=status,
        dataset_version="v1.0-synthetic",
        training_enabled=NER_TRAINING_ENABLED,
        train_split=train_stat,
        validation_split=val_stat,
        test_split=test_stat,
        warnings=warnings,
        errors=errors
    )
