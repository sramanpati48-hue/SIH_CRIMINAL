# Prediction Targets

This document defines the allowed machine learning prediction targets in SIH 26189.

## Allowed Targets

1. **Structural Similarity:** Cosine similarity distance between case feature vectors.
2. **Anomaly Score:** An isolation-based score representing structural unusualness compared to a synthetic baseline.
3. **Investigative Priority:** A bucket (e.g., `HIGH`, `MEDIUM`, `LOW`) determining human review order based on historical case patterns.
4. **Pattern-Type Suggestion:** Recommended review tags based on feature prevalence.
5. **Lead-Priority Bucket:** A priority assignment for a specific AI-generated lead.

## Prohibited Targets

Under no circumstances will models in this system output:
- Criminal probability
- Guilt prediction
- Criminal classification
- Automatic accusation

## Glossary & Distinctions

- **Extraction Confidence:** NLP pipeline metric denoting how sure the extractor is that an entity exists in text.
- **Relationship Confidence:** Likelihood that a relationship exists between two entities based on the evidence available.
- **Rule-based Pattern Score:** A fixed severity/score triggered by deterministic pattern-matching rules (e.g., `SharedPhoneDetector`).
- **Anomaly Score:** The continuous value produced by an Isolation Forest model measuring deviation from normal baseline features.
- **Historical Similarity Score:** A `[0.0, 1.0]` cosine similarity metric between two historical case graphs.
- **Investigative Priority:** The final, human-readable bucket or tag suggesting where investigators should spend their time.
