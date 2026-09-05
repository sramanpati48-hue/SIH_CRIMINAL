# NER Training Readiness

## Overview
Before we can run custom fine-tuning of the spaCy NER model, the system rigorously checks the dataset for quality, balance, and constraints. The `scripts/check_ner_training_readiness.py` script validates the `data/synthetic/ner/` files.

## Document-Level Split Separation
- A document must appear in exactly one split (`train.jsonl`, `validation.jsonl`, `test.jsonl`).
- Split leakage (same document ID across multiple files) will halt training preparation.

## Label Coverage
Configurable minimums are applied:
- **NER_MIN_EXAMPLES_PER_LABEL**: Ensure classes like `PERSON`, `LOCATION` are well-represented (default 5 for development, 50 in production).
- **Required Labels**: `PERSON`, `PHONE`, `LOCATION`, `ORGANIZATION`. Missing these entirely causes failures or warnings.

## Safeties
- **NER_TRAINING_ENABLED**: Must explicitly be true to bypass the `NOT_READY` block.
- **Synthetic constraints**: The data must come from the deterministic mock generator; NO real PII is permitted.
