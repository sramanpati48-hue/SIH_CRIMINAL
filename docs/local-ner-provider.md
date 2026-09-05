# Local NER Provider Architecture

## Overview
The SIH 26189 Criminal Network Analysis System supports an optional local Named Entity Recognition (NER) provider using spaCy. This allows for offline extraction of entities from text. 

To maintain the system's lightweight default profile, the local NER provider is an **optional dependency** and is not installed by default. If the provider is unavailable or missing, the system gracefully falls back to the `MockExtractor` or explicitly raises an unavailability error when configured but missing the required libraries.

## Requirements
To use the local NER provider, you must install the optional requirements:
```bash
# From the backend directory
pip install -r requirements-ner.txt

# Download the spaCy model (e.g., small English model)
python -m spacy download en_core_web_sm
```

## Configuration
Update your `.env` file to select the spaCy provider:
```env
# Use the baseline spacy model (en_core_web_sm)
EXTRACTION_PROVIDER=SPACY_BASELINE

# OR: Use a custom fine-tuned model from the registry
EXTRACTION_PROVIDER=SPACY_CUSTOM
SPACY_CUSTOM_MODEL_ID=your_model_id
```
If `EXTRACTION_PROVIDER` is set to `MOCK` or omitted, the system defaults to the `MockExtractor`.

## Design Constraints Met
- **Application Startup:** The provider wraps external imports in `try...except` and initializes without auto-downloading models. Startup will not fail or hang if the model is missing.
- **Graceful Degradation:** Missing model files will produce a clear warning in the logs, and API requests attempting to extract using this unavailable provider will fail gracefully (RuntimeError indicating unavailability).
- **MockExtractor Preservation:** The default `MockExtractor` continues to operate identically and doesn't require any additional packages.
- **Provider Output Compatibility:** Output matches the strict `ExtractedEntityCandidate` and `DocumentExtractionResult` Pydantic schemas, preserving character boundaries, text, and applying label normalizations.
