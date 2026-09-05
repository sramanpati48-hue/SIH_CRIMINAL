# Custom NER Model Evaluation

## Strictly Held-out Data
Models are evaluated only against `data/synthetic/ner/test.jsonl`. This ensures separation of the train/validation splits from the evaluation metrics.

## Methodology
- **Entity Matching**: Exact offset mapping between predicted bounds and gold synthetic bounds.
- **Relationship Topology**: Source to target match based on entity linkage.

## Limitations
Because this pipeline relies exclusively on synthetically generated mock text, the resulting trained model should NEVER be assumed to perform with high accuracy on real-world unstructured intelligence data. Synthetic models are for pipeline demonstration, explainability UI testing, and CI/CD validation. 
No claims of guilt should ever be driven by this model's outputs.
