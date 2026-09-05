# NER Evaluation Strategy

Before fine-tuning or deploying any ML models against investigative case reports, we must establish a robust evaluation pipeline. This strategy utilizes exclusively synthetic data.

## 1. Synthetic Dataset Generation

We will create a new CLI tool or script (`apps/backend/scripts/generate_synthetic_ner_data.py`) utilizing the `faker` library.

**Generation Process:**
1. Select a deterministic template: *"Subject [PERSON] was observed near [LOCATION] driving a [VEHICLE]."*
2. Populate slots using `faker.providers`.
3. Record the exact string offsets for the generated entities.
4. Output as JSONL.

Example output:
```json
{
  "text": "Subject Alice Smith was observed near Central Park driving a Toyota Camry.",
  "entities": [
    {"label": "PERSON", "start": 8, "end": 19, "text": "Alice Smith"},
    {"label": "LOCATION", "start": 38, "end": 50, "text": "Central Park"},
    {"label": "VEHICLE", "start": 61, "end": 73, "text": "Toyota Camry"}
  ]
}
```

## 2. Evaluation Execution

An evaluation script (`evaluate_ner.py`) will feed the synthetic text into the `ExtractorProvider` (e.g., `HuggingFaceExtractor`).

The script will compare the extracted `ExtractedEntityCandidate` lists against the ground-truth JSONL entities.

## 3. Metrics Tracking

Using strict exact-match boundaries, the evaluator will calculate:
- **True Positives (TP)**: Model predicted exact boundary and label.
- **False Positives (FP)**: Model predicted an entity that does not exist, or got the boundary/label wrong.
- **False Negatives (FN)**: Model missed an entity present in ground truth.

**Calculations:**
- **Precision** = TP / (TP + FP)
- **Recall** = TP / (TP + FN)
- **F1-Score** = 2 * (Precision * Recall) / (Precision + Recall)

## 4. Evaluation Criteria

The model should achieve a baseline F1-score of **> 0.80** on standard entities (`PERSON`, `LOCATION`, `ORGANIZATION`) on the synthetic validation set before it is considered ready for the `UNREVIEWED` human-in-the-loop pipeline.

Entities that fail to meet this threshold will rely strictly on manual analyst input or rule-based overrides.
