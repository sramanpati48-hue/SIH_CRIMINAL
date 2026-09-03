# Model Card: SIH 26189 Baseline Analysis

## Model Details
- **Architecture:** Isolation Forest (Unsupervised Baseline), Random Forest (Supervised Baseline).
- **Library:** `scikit-learn`
- **Model Versioning:** Timestamp-based semantic tracking alongside checksum validation.

## Intended Use
- **Primary Use:** Providing investigative priority scoring, anomaly highlighting, and structural similarity matching for human-in-the-loop review.
- **Prohibited Use:** Autonomous decision making, predicting criminal likelihood, predicting guilt, or assigning automatic accusations.

## Training Data & Limitations
- **Data Source:** Exclusively synthetic generated cases.
- **Limitations:** Does not represent real-world ground truth. Extreme false-positive rates are expected if applied to real data due to lack of diverse "innocent" baseline behavior in the synthetic generator.
- **Insufficient-Data Handling:** Supervised training aborts if `cases < 20`.

## Features
- Structural metrics (density, betweenness, degrees)
- Volume counts (nodes, edges, specific entity types)
- Temporal patterns (event spans, transaction velocity)

## Evaluation Metrics (When applicable)
- Precision, Recall, F1-Score, False-Positive Rate.
- Metrics are calculated on a strictly case-level isolated test set.

## Bias & Fairness
- Known biases: May flag highly-connected lawful individuals (e.g., lawyers, real estate agents) as anomalous due to structural similarities with central figures in a network.
- **Mitigation:** Human-review requirement for every AI lead.
