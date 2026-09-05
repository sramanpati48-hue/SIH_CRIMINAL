# Extraction Providers

The system is designed with a pluggable architecture for NLP document extraction, allowing for deterministic rules, small ML models, or large language models (LLMs) to be swapped interchangeably.

## `ExtractorProvider` Interface

Any extraction engine must implement the `ExtractorProvider` interface defined in `apps/backend/app/extraction/providers.py`. It requires two asynchronous methods:

- `extract_entities(document_id: str, document_text: str) -> List[ExtractedEntityCandidate]`
- `extract_relationships(document_id: str, document_text: str, entities: List[ExtractedEntityCandidate]) -> List[ExtractedRelationshipCandidate]`

*Note: In Milestone 9, relationship extraction was officially decoupled from the `ExtractorProvider` interface. While providers can still optionally generate relationships via `extract`, the primary application pipeline explicitly runs the deterministic rule engine from `relationship_rules.py` after entity extraction to ensure exact, traceable evidence.*

## Current Implementations

### `MockExtractor`
A regex-based, deterministic extraction provider used for Milestone 8. It simulates NLP behavior using synthetic data patterns. It extracts specific entity types and resolves fallback relationships based on proximity and keywords.

## Future Implementations

In future milestones, we will integrate advanced NLP models (such as fine-tuned BERT models or Gemini API via `gemini-interactions-api`) to handle complex semantic relationships and entity recognition in noisy or unstructured text.
