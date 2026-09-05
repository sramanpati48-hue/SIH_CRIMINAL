# spaCy Custom NER Pipeline

## Prerequisites
1. Ensure synthetic data is generated.
2. Ensure data passes `check_ner_training_readiness.py`.
3. Convert data via `prepare_spacy_ner_data.py`.

## Training
To train the model, you must enable training in configuration and invoke the CLI explicitly:

1. Set `NER_TRAINING_ENABLED=true` in `.env`
2. Run the training script:
```bash
python scripts/train_spacy_ner.py --data-dir data/training/spacy
```
Training does NOT happen during FastApi application startup, nor can it be triggered via API.

## Registration
The best model artifact (`model-best`) is securely promoted to the `MODEL_ARTIFACT_ROOT`, assigned a `model_id`, checksummed for integrity, and registered in the `ExtractionModel` registry table (status `READY`). Absolute paths are never stored. The frontend reads from this table to display the model registry.
