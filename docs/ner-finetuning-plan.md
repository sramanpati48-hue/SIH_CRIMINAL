# NER Fine-Tuning Plan

*Note: Per core project rules, the system currently exclusively uses synthetic data and does not fine-tune models on real police or PII data.*

This document outlines the proposed strategy for fine-tuning a Named Entity Recognition (NER) model on custom, synthetic investigative reports in future milestones.

## 1. Dataset Generation
- Use `faker` and deterministic templates to generate thousands of synthetic unstructured case reports.
- Annotate the generated dataset with exact character offsets for custom entities (e.g., `PERSON`, `ALIAS`, `VEHICLE`, `MONEY`, `BANK_ACCOUNT`).
- Ensure balanced representation of complex relationships and edge cases (e.g., multiple aliases, overlapping contexts).

## 2. Model Selection
- Choose a lightweight, open-weight transformer model (e.g., a variant of BERT or RoBERTa) optimized for NER tasks.
- The model must run efficiently on local hardware or a managed GCP pipeline, respecting the project's infrastructure constraints.

## 3. Training Pipeline
- Preprocess synthetic annotations into standard token classification format (e.g., BIO tagging).
- Fine-tune the model using Hugging Face `transformers` or a Vertex AI pipeline.
- Evaluate the model against a held-out test set of synthetic reports, tracking Precision, Recall, and F1-score for each entity class.

## 4. Integration
- Implement a new `ExtractorProvider` (e.g., `HuggingFaceExtractor`) to wrap the fine-tuned model inference.
- Utilize the existing `DocumentExtractionService` to orchestrate extraction, preserving the human-in-the-loop review workflow and Neo4j graph sync.

## 5. Future Learned Relationship Models
Currently, relationship extraction is entirely deterministic and relies on strict substring rules (as per Milestone 9). In the future, once the NER model is fine-tuned, a secondary relation extraction (RE) classification model can be trained to replace or augment the rules. 
- The learned model will still require human-in-the-loop review.
- It will predict relation types from the allow-listed set based on context embeddings between two extracted entities.
