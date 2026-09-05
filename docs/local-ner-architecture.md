# Local NER Architecture

This document defines the architectural integration for the optional local Named Entity Recognition (NER) provider, fulfilling Milestone 9 requirements.

## 1. Abstraction Implementation

The system currently relies on the `ExtractorProvider` interface. We will fully implement the `HuggingFaceExtractor` placeholder defined in `apps/backend/app/extraction/providers.py`.

```python
class HuggingFaceExtractor(ExtractorProvider):
    def __init__(self, model_name: str = "dslim/bert-base-NER"):
        # Lazy imports to ensure core app does not crash if transformers is missing
        try:
            from transformers import pipeline
        except ImportError:
            raise RuntimeError("NER dependencies missing. Install them first.")
        
        self.pipeline = pipeline("ner", model=model_name, aggregation_strategy="simple")
```

## 2. Dependency Management

To prevent the core backend container and local development environment from ballooning in size (due to PyTorch and Transformers), NER capabilities will be strictly isolated.

1. **New File**: `apps/backend/requirements-ner.txt`
   ```text
   transformers>=4.38.0
   torch>=2.2.0 --index-url https://download.pytorch.org/whl/cpu
   ```
2. **Runtime Checks**: The `DocumentExtractionService` or Dependency Injection container will default to `MockExtractor` if `HuggingFaceExtractor` fails to initialize.

## 3. Entity Mapping & Confidence

Open-weight models typically output standard CoNLL-2003 entities (`PER`, `ORG`, `LOC`, `MISC`). 
The `HuggingFaceExtractor` must map these to the system's strict allow-list (`PERSON`, `ORGANIZATION`, `LOCATION`).

- **Confidence Score**: The model's softmax probability for the extracted token span will be mapped directly to the `ExtractedEntityCandidate.confidence` field (0.0 to 1.0).
- **Offsets**: Hugging Face pipelines provide character offsets (`start`, `end`). These map precisely to our `start_offset` and `end_offset`, fulfilling our traceability requirements.

## 4. Relationship Fallback

Since standard NER models do not extract *relationships* between entities, the `HuggingFaceExtractor.extract_relationships` method will initially reuse the deterministic distance-based rules from `MockExtractor`, or return an empty list until a dedicated Relation Extraction (RE) model is introduced.

## 5. Non-Destructive Integration

This architecture guarantees that introducing real ML inference will not break the existing test suites or the determinism of the `MockExtractor`. Tests for `HuggingFaceExtractor` will be skipped dynamically using `@pytest.mark.skipif` if the `transformers` library is not found in the environment.
