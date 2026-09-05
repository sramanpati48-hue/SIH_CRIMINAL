# Model Registry

The `ExtractionModel` table safely tracks all custom models (NER fine-tunes).

## Fields tracked
- `model_id`: Internal unique tracking ID.
- `provider`: E.g., `SPACY_CUSTOM`.
- `dataset_version`: Synthetic data version stamp.
- `artifact_storage_key`: Opaque key relative to trusted root (not exposed to user via API).
- `artifact_filename`: Basename of the artifact (not exposed via API).
- `sha256_checksum`: Deterministic SHA-256 of the model directory (not exposed via API).
- `status`: Lifecycle (`TRAINING`, `READY`, `FAILED`).
- `test_metrics`: F1, Precision, Recall stored as JSON payload.

## Provider Loading
To load a registered model, configure `EXTRACTION_PROVIDER=SPACY_CUSTOM` and set `SPACY_CUSTOM_MODEL_ID=your_model_id`. The application will internally resolve the storage key via `load_trusted_spacy_model()`, verify its checksum, and load it securely. If the model is missing or verification fails, it degrades gracefully to `PROVIDER_UNAVAILABLE` rather than silently falling back to `MOCK`.

