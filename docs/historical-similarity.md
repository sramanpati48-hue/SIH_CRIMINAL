# Historical Similarity

SIH 26189 allows investigators to find historically similar cases to accelerate investigations and discover cross-case linkages.

## Approach
We use **Deterministic Weighted Cosine Similarity**. 

### Process:
1. **Vectorization:** Each case is converted into a structured `CaseFeatureVector` (counts, centralities, densities).
2. **Alignment & Missing Values:** Feature names are aligned lexicographically. Missing values are filled deterministically with `0.0`.
3. **Normalization:** Features are scaled (e.g., using `MinMaxScaler`) to ensure node counts don't overpower smaller bounded metrics like graph density.
4. **Weights:** Configurable weights are applied to prioritize structural features (e.g., betweenness) over raw volume features (e.g., total nodes).
5. **Similarity Calculation:** Cosine similarity determines the angle between vectors.
6. **Tie-Breaking:** If two cases share the exact same similarity score, ties are broken deterministically by sorting `case_id`.

## Explainability
When presenting similar cases, the system outputs:
- **Similarity Score:** `[0.0, 1.0]`
- **Matched Features:** Features with identical or highly similar normalized values.
- **Differing Features:** Features that diverge the most.
- **Explanation:** A neutral summary. Example: *"This case has structural similarity to C004 because both contain a rapid transaction chain, repeated-location events, and a bridge candidate. Similarity does not establish that the cases are the same."*
