# Synthetic Data Strategy

This project uses exclusively synthetic data to build, test, and demonstrate the Criminal Network Analysis System (SIH 26189).

## Policy
1. **No Real Data**: Never use real names, phone numbers, banking data, or PII.
2. **Determinism**: The synthetic data generator uses a fixed seed (`seed=42`) to produce identical results on every run.
3. **Planted Patterns**: The data contains specific patterns designed to test our graph algorithms and UI visualization.

## Generator
Located at `data/synthetic/generate_data.py`. Run via:
```bash
python data/synthetic/generate_data.py
```

## Planted Patterns
1. **Cross-case connector:** Person `P001` bridges Cases 1, 2, and 3.
2. **Shared phone:** Phone `PH001` is shared by `P002` and `P003`.
3. **Shared vehicle:** Vehicle `V001` appears in Cases 6 and 7.
4. **Repeated location:** Several people co-located at `LOC002` (embedded in unstructured text of `DOC002`).
5. **Rapid transaction chain:** Funds move from `BA001` -> `BA002` -> `BA003` -> `BA004` within 48 hours.
6. **Bridge relationship:** Person `P010` acts as a crucial bridge between two distinct clusters (Case 4 and 5).
7. **Legitimate high-connectivity:** `BA050` acts as a highly-connected Bank Hub, demonstrating how the system handles large-degree nodes that aren't inherently suspicious.

## Schema
See `data/synthetic/README.md` for the data dictionary detailing each CSV column and JSON structure.
