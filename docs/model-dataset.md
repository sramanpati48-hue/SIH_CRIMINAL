# Model Dataset Generation

This document outlines how we construct datasets for machine learning training in SIH 26189.

## Feature Definitions
Each case is flattened into a deterministic feature vector containing:
- **Graph Structure:** e.g., node count, edge count, density, average degree, betweenness centrality metrics.
- **Entity Counts:** e.g., number of people, phones, bank accounts.
- **Relationship Counts:** e.g., call volumes, transactions, cross-case linkages.
- **Temporal Features:** e.g., rapid transaction chain occurrences, event spans.
- **Pattern Features:** e.g., number of triggered rule-based patterns (shared phones, bridges, etc.).

## Target Labels
When running supervised training (Random Forest), labels are defined based on historical `Alert` acceptances or planted anomalies in synthetic data.

## Case-Level Splitting
To prevent data leakage, dataset splitting (Train / Validation / Test) is **strictly performed at the case level**. We never split entities or relationships belonging to the same case across different sets. This ensures the model learns generalizable patterns rather than memorizing a specific case's structure.

## Insufficient-Data Behavior
Because our dataset may initially be small (e.g., ~10 synthetic cases):
- We enforce `MIN_SUPERVISED_CASES=20`.
- If fewer cases with valid labels exist, dataset generation will explicitly report `INSUFFICIENT_DATA`.
- Supervised training is aborted to prevent misleading metrics. The system relies entirely on rules and the unsupervised Isolation Forest baseline until sufficient data is gathered.

## Synthetic-Label Limitations and False-Positive Risks
- Our current labels are entirely synthetic. Real-world criminal networks may behave vastly differently.
- There is a known risk of bias if synthetic data generators over-represent certain innocent patterns (e.g., normal business transactions) as anomalous.
- All model outputs must display a warning regarding synthetic limitations.
