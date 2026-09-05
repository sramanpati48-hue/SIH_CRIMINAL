# Synthetic Named Entity Recognition (NER) & Relationship Evaluation Dataset

## Overview

This directory contains a deterministic, synthetic evaluation dataset designed for benchmarking Named Entity Recognition (NER) and Relationship Extraction (RE) models within the **SIH 26189 Criminal Network Analysis System**.

> [!IMPORTANT]
> **Evaluation-Only Synthetic Dataset:** This dataset is composed exclusively of synthetically generated texts, fictitious names, synthetic identifiers, and simulated law-enforcement narratives. Under no circumstances should real personal identifiers, phone numbers, addresses, or banking details be added. This dataset is designed strictly for offline model evaluation, regression testing, and error analysis.

---

## 1. File Inventory & Splits

The dataset is partitioned at the **document level** to prevent data leakage. Document IDs and scenarios are strictly disjoint across splits:

| File | Document Count | Purpose | Scenario Families |
| :--- | :--- | :--- | :--- |
| `train.jsonl` | 40 | Baseline training & fine-tuning experiments | Wire fraud, physical surveillance, traffic stops, line intercepts, search warrants, negative controls, decoy narratives, malformed OCR scans |
| `validation.jsonl` | 15 | Hyperparameter tuning & threshold selection | Maritime cargo declarations, burner SIM handshakes, banking SAR alerts, fleet vehicle audit negative controls, high-density multi-alias debriefs |
| `test.jsonl` | 20 | Unseen held-out evaluation & error analysis | Triangulated multi-jurisdiction meetings, smurfing/micro-structuring chains, cold-case file linkages, server room access negative controls, adversarial OCR/noisy logs |

---

## 2. File Format

Each file is stored in JSON Lines (`.jsonl`) format. Each line represents a self-contained document with the following schema:

```json
{
  "document_id": "DOC_TR_001",
  "split": "train",
  "scenario_type": "financial_wire_layering",
  "text": "Financial crimes investigator intake memorandum for case CASE-2024-SYN-101. On January 10, 2024, primary subject Marcuz Kowalski (operating under the street alias 'Razor') authorized an electronic funds wire. Acting as a controlling director of Synthetic Holdings Ltd, the subject ordered a transfer of $4,500 from primary escrow account SYN-ACCT-67433 directly to correspondent account BA-SYN-99329. Both the individual and the corporate entity are formally investigated under active proceedings.",
  "entities": [
    {
      "id": "DOC_TR_001_e0",
      "label": "CASE_ID",
      "start": 57,
      "end": 74,
      "text": "CASE-2024-SYN-101"
    },
    {
      "id": "DOC_TR_001_e1",
      "label": "DATE",
      "start": 79,
      "end": 95,
      "text": "January 10, 2024"
    },
    {
      "id": "DOC_TR_001_e2",
      "label": "PERSON",
      "start": 113,
      "end": 128,
      "text": "Marcuz Kowalski"
    },
    {
      "id": "DOC_TR_001_e3",
      "label": "ALIAS",
      "start": 164,
      "end": 169,
      "text": "Razor"
    }
  ],
  "relationships": [
    {
      "id": "DOC_TR_001_r0",
      "type": "OWNS",
      "source_entity_id": "DOC_TR_001_e2",
      "target_entity_id": "DOC_TR_001_e6",
      "text": "Marcuz Kowalski owns SYN-ACCT-67433"
    },
    {
      "id": "DOC_TR_001_r1",
      "type": "TRANSFERRED_TO",
      "source_entity_id": "DOC_TR_001_e6",
      "target_entity_id": "DOC_TR_001_e7",
      "text": "transferred $4,500 from SYN-ACCT-67433 to BA-SYN-99329"
    }
  ]
}
```

### Key Field Definitions
- `document_id` (`str`): Unique, stable identifier across the entire dataset.
- `split` (`str`): `train`, `validation`, or `test`.
- `scenario_type` (`str`): Categorical label describing the narrative template family.
- `text` (`str`): Unstructured synthetic report text.
- `entities` (`list`): List of annotated entity candidate spans:
  - `id` (`str`): Document-scoped unique identifier (e.g. `DOC_TR_001_e0`).
  - `label` (`str`): Allow-listed entity category.
  - `start` (`int`): 0-indexed character start offset (inclusive).
  - `end` (`int`): 0-indexed character end offset (exclusive).
  - `text` (`str`): Exact substring slice matching `text[start:end]`.
- `relationships` (`list`): List of annotated relationships between entities:
  - `id` (`str`): Document-scoped unique identifier (e.g. `DOC_TR_001_r0`).
  - `type` (`str`): Allow-listed relationship category.
  - `source_entity_id` (`str`): Identifier of the source entity in `entities`.
  - `target_entity_id` (`str`): Identifier of the target entity in `entities`.
  - `text` (`str`): Textual context or summary describing the evidence.

---

## 3. Supported Entity Labels

The dataset strictly supports the 10 target entities:

1. **`PERSON`**: Personal names of individuals (e.g., `Marcuz Kowalski`, `Elena Smythe`, `Jonathon Smith`).
2. **`ALIAS`**: Street monikers, operational code names, or aliases (e.g., `Razor`, `Nightowl`, `The Ghost`).
3. **`PHONE`**: Telecommunications numbers, formatted in fictitious ranges (e.g., `+1-555-0142`, `(555) 018-9201`).
4. **`VEHICLE`**: License plates, vehicle identifiers, or transport units (e.g., `SYN-VEH-1049`, `SYN-TRK-8812`).
5. **`LOCATION`**: Physical addresses, facilities, or venues (e.g., `Warehouse 4, 100 Industrial Parkway, Sector 9`).
6. **`ORGANIZATION`**: Corporations, partnerships, shell entities, or financial institutions (e.g., `Synthetic Holdings Ltd`).
7. **`BANK_ACCOUNT`**: Financial accounts, ledgers, or IBAN-like tokens (e.g., `SYN-BA-10042`, `ACC-SYN-4920`).
8. **`CASE_ID`**: Formal investigative case numbers or dossier codes (e.g., `CASE-2024-SYN-101`, `CR-26189-A`).
9. **`DATE`**: Calendar dates in ISO or textual representations (e.g., `2024-05-12`, `January 10, 2024`, `15/03/2024`).
10. **`MONEY`**: Currency quantities with monetary symbols or currency codes (e.g., `$4,500`, `$25,000.00`, `USD 50,000`).

---

## 4. Supported Relationship Labels

Relationships link pairs of annotated entities within the same document:

1. **`CALLED`**: Communication initiated from a `PHONE` or `PERSON` to another `PHONE` or `PERSON`.
2. **`USED`**: An individual utilizing an `ALIAS`, operating a `VEHICLE`, or employing a `PHONE`.
3. **`OWNS`**: A `PERSON` or `ORGANIZATION` possessing a `VEHICLE`, `BANK_ACCOUNT`, or asset.
4. **`VISITED`**: A `PERSON` or `VEHICLE` arriving at, entering, or berthing at a `LOCATION`.
5. **`TRANSFERRED_TO`**: Financial movement between two `BANK_ACCOUNT` entities or persons.
6. **`INVOLVED_IN`**: A `PERSON`, `ORGANIZATION`, or `VEHICLE` tied to an active `CASE_ID`.
7. **`MENTIONED_IN`**: A `PERSON`, `ALIAS`, or `PHONE` cited within an investigative `CASE_ID`.
8. **`CONNECTED_TO`**: Direct personal or institutional association between `PERSON` and `ORGANIZATION`, or between two persons.
9. **`OCCURRED_AT`**: An incident, case, or communication session tied to a physical `LOCATION`.

---

## 5. Split Strategy & Template Leakage Prevention

To ensure robust evaluation and avoid memorization:
1. **Document-Level Partitioning:** Document IDs are disjoint across train, validation, and test.
2. **Template Scenario Disjointness:**
   - **Train** focuses on primary white-collar wire transfers, traffic stops, and wiretap logs.
   - **Validation** introduces maritime shipping declarations, burner handset handshakes, and bank SAR notices.
   - **Test** features multi-jurisdiction syndicate meetings, multi-hop smurfing chains, and cold-case record reviews.
3. **Name & Identifier Diversity:** Person names include international naming conventions and common spelling variations (e.g., `Jonathon` vs `Johnathan`, `Marcuz` vs `Marcus`, `Catharina` vs `Katarina`).

---

## 6. Known Ambiguities & Edge Cases

The dataset includes intentional challenges for model evaluation and error analysis:

1. **Lexical Decoys / Common Nouns as Names:**
   - Words like `General`, `March`, `Bill`, `Chase`, `Hope`, and `Major` appear in natural lower-case or capitalized non-entity contexts (e.g., *"general surveillance was conducted in late March"*). Evaluators should verify that models do not falsely classify these as `PERSON` or `ORGANIZATION`.
2. **Negative Examples (Zero Entities):**
   - Documents such as `DOC_TR_006`, `DOC_VAL_004`, and `DOC_TEST_004` describe routine administrative tasks or environmental audits with **0 entities** and **0 relationships**.
3. **Punctuation & OCR Artifacts:**
   - Scenarios such as `T8` and `S5` feature bracketed identifiers (`Case[CASE-2024-SYN-408]`), semicolons touching accounts (`account SYN-BA-10042;`), and unspaced punctuation to simulate real-world scanned narrative noise.
4. **Anonymous & Unresolved Mentions:**
   - Sentences stating *"an unknown individual called someone"* or *"the vehicle was observed"* contain no named entities and have no annotated relationships, testing model restraint against hallucination.

---

## 7. Synthetic Data Limitations

1. **Distributional Bias:** The text is procedurally generated using deterministic slot-filling and Faker variants. It lacks the colloquial idiosyncrasies, dialects, and grammatical inconsistencies of raw police logs.
2. **Fictitious Formatting Constraints:** Phone numbers are strictly bounded to `555-01xx` for ethical safety; real-world numbers have varied country and area code prefixes.
3. **Evaluation Purpose:** This dataset is constructed for automated regression benchmarking and token classification scoring (`seqeval`). It is not intended for training models intended for production deployment without human verification.

---

## 8. Generation & Reproducibility

The dataset is generated deterministically by running:

```bash
python data/synthetic/ner/generate_ner_data.py
```

Default Seed: `26189`. Running this command reproduces exact character offsets, document texts, and split partitions.
