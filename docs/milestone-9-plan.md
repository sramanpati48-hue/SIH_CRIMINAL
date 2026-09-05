# Milestone 9 Plan: Optional Local NER & Synthetic Evaluation

## Objective
Implement an optional local Named Entity Recognition (NER) provider and a synthetic evaluation workflow without breaking the existing deterministic `MockExtractor`.

## 1. Local NER Provider Comparison

To fulfill the NLP requirements, we evaluate two primary frameworks compatible with Python 3.10:

| Feature | spaCy NER | Hugging Face (Transformers) |
| :--- | :--- | :--- |
| **Dependency Footprint** | Lightweight (~50MB for `en_core_web_sm`) | Heavy (~2GB+ with `torch` and weights) |
| **Speed (CPU)** | Extremely Fast | Slow (without optimizations like ONNX) |
| **Custom Entities** | Requires custom spaCy training pipeline | Highly extensible via standard BIO token classification (BERT/RoBERTa) |
| **Strategic Alignment** | Good for baseline, harder for deep custom context | Aligns directly with `docs/ner-finetuning-plan.md` |

### Recommendation
We recommend **Hugging Face Token Classification** (using `transformers` and `torch`). While heavier, it directly aligns with the `ner-finetuning-plan.md` goal of fine-tuning a BERT/RoBERTa variant for custom investigatory entities (e.g., `VEHICLE`, `ALIAS`, `BANK_ACCOUNT`). 

To mitigate the heavy dependency footprint, it will be introduced strictly as an **optional dependency group** (e.g., `[ner]`).

## 2. Optional Dependencies
We will define an optional dependency set (e.g., `requirements-ner.txt` or an `extras_require` block) containing:
- `transformers>=4.38.0`
- `torch>=2.2.0` (CPU-only version recommended for local development)
- `seqeval` (for evaluation metrics)

The core `requirements.txt` will remain lightweight.

## 3. Synthetic Evaluation Dataset
We will expand the existing `faker`-based data generator to emit **annotated** synthetic case reports.
- **Format**: JSONL files containing `"text"` and `"entities": [{"label": "PERSON", "start": 0, "end": 8, "text": "John Doe"}]`.
- **Content**: 100% synthetic police, banking, and phone records. No real PII.
- **Split**: Train (80%), Validation (10%), Test (10%).

## 4. Evaluation Metrics
The evaluation workflow will track standard Token Classification metrics via `seqeval`:
- **Precision**: How many of the extracted entities are correct.
- **Recall**: How many of the true entities were found.
- **F1-Score**: Harmonic mean of Precision and Recall.
Metrics will be tracked globally and per-entity-type (e.g., `F1-PERSON`, `F1-BANK_ACCOUNT`).

## 5. Provider-Failure Behaviour
The new `HuggingFaceExtractor` (which implements `ExtractorProvider`) will:
1. Wrap `transformers` imports in `try/except ImportError`.
2. If dependencies are missing, attempting to instantiate or use the provider will raise a clear `RuntimeError("Optional NER dependencies are not installed. Run 'pip install -r requirements-ner.txt'.")`
3. Fall back gracefully in tests (mocking or skipping NER tests if dependencies are missing) ensuring the CI/CD pipeline does not break.

## 6. Human-Review Safeguards
Adding a real ML model introduces probabilistic errors (false positives/negatives). To safeguard the system:
- All extractions from the NER provider will still strictly enter the database as `UNREVIEWED`.
- The `ExtractionReviewPanel` will continue to mandate explicit human `ACCEPT` or `CORRECT` actions before syncing to Neo4j.
- The `confidence` score from the model's softmax outputs will be stored and displayed to help reviewers triage low-confidence predictions.
