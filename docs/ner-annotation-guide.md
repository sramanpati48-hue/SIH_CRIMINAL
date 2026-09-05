# NER & Relationship Annotation Guide

This document outlines the formal annotation guidelines, boundary conventions, and schema constraints for Named Entity Recognition (NER) and Relationship Extraction (RE) within the **SIH 26189 AI-Assisted Criminal Network Analysis System**.

---

## 1. Ethical & Traceability Principles

1. **Synthetic-Data Exclusivity:** Annotations must never contain real-world Personally Identifiable Information (PII), real banking coordinates, or authentic telephone records.
2. **Ground Truth Verification:** Every entity span must be strictly anchored to the original document text via character offsets:
   $$\text{document.text}[\text{start}:\text{end}] == \text{entity.text}$$
3. **No Automatic Accusation:** Annotations denote linguistic mentions and evidentiary leads, not criminal culpability.

---

## 2. Entity Annotation Guidelines

### 2.1 Supported Entity Classes

| Entity Label | Definition | Boundary Inclusion Rules | Negative / Excluded Patterns |
| :--- | :--- | :--- | :--- |
| **`PERSON`** | Names of real or synthetic individuals. | Include first, middle, last names, and generational suffixes (e.g. `Marcus Vance`, `Catharina Van Der Bilt`). Do **not** include professional titles (exclude `Dr.`, `Officer`, `Mr.`). | Generic terms like `the suspect`, `unknown individual`, `courier`, `manager`. |
| **`ALIAS`** | Monikers, code names, or street nicknames used in lieu of legal names. | Span includes the alias text itself without surrounding quotation marks (e.g., annotate `Razor`, not `'Razor'`). | Legal names or honorifics. |
| **`PHONE`** | Telecommunications numbers. | Include international country code and area codes (e.g. `+1-555-0142`, `(555) 018-9201`). | Extension numbers unless part of the primary dial string. |
| **`VEHICLE`** | Specific vehicle registrations, transport unit codes, or plate numbers. | Include the plate/alphanumeric identifier (e.g. `SYN-VEH-1049`, `SYN-TRK-8812`). | Generic descriptions like `a black sedan`, `the truck`. |
| **`LOCATION`** | Physical geographic addresses, facility names, piers, or rooms. | Include street address, suite/room, and city if part of the direct phrase (e.g. `Warehouse 4, 100 Industrial Parkway, Sector 9`). | Broad jurisdictions or countries mentioned in passing unless denoting a specific meeting venue. |
| **`ORGANIZATION`** | Formal corporate entities, financial institutions, shell companies, or agencies. | Include corporate suffixes (e.g. `Synthetic Holdings Ltd`, `First Fictional Credit Union`). | Generic references like `the company`, `the bank`, `headquarters`. |
| **`BANK_ACCOUNT`** | Financial ledger codes, account numbers, or deposit coordinates. | Include alphanumeric account prefix and number (e.g. `SYN-BA-10042`, `ACC-SYN-4920`). | Transaction IDs (e.g. `TX-1001`), check numbers, or routing numbers. |
| **`CASE_ID`** | Formal docket, incident, or case file reference identifiers. | Include the entire case identifier string (e.g. `CASE-2024-SYN-101`, `CR-26189-A`). | Generic mentions like `the case`, `active file`. |
| **`DATE`** | Calendar dates and chronological references. | Include month, day, year spans in ISO or long format (e.g. `2024-05-12`, `January 10, 2024`, `15/03/2024`). | Relative time of day alone (e.g., `at 19:45 hours`), durations (e.g. `20 minutes`). |
| **`MONEY`** | Monetary amounts. | Include currency symbol/code and numeric amount (e.g. `$4,500`, `USD 50,000`, `7,500 dollars`). | Non-monetary counts or percentages. |

---

## 3. Boundary & Formatting Conventions

### 3.1 Punctuation Attachment
- Punctuation marks that are not syntactically part of the token (commas, semicolons, brackets, trailing periods) must **never** be included in the entity span.
  - *Correct:* `CASE-2024-SYN-101` in `Case[CASE-2024-SYN-101];`
  - *Incorrect:* `[CASE-2024-SYN-101];`

### 3.2 Whitespace & Contractions
- Spans must not include leading or trailing whitespace.
- If a token has an internal apostrophe (e.g., `O'Connor`), the apostrophe is part of the `PERSON` span.

### 3.3 Quotation Marks in Aliases
- When an alias is introduced with quotes (e.g. `alias 'Nightowl'`), annotate only the enclosed name: `Nightowl`.

---

## 4. Relationship Annotation Guidelines

Relationships connect two existing annotated entities within the same document:

| Relationship | Permissible Source Types | Permissible Target Types | Semantics & Example |
| :--- | :--- | :--- | :--- |
| **`CALLED`** | `PHONE`, `PERSON` | `PHONE`, `PERSON` | A telecom transmission from source to target. (*Phone A called Phone B*) |
| **`USED`** | `PERSON` | `ALIAS`, `PHONE`, `VEHICLE` | An individual operating, possessing, or adopting a resource. (*Marcus used alias Razor*) |
| **`OWNS`** | `PERSON`, `ORGANIZATION` | `VEHICLE`, `BANK_ACCOUNT`, `PHONE` | Legal or operational ownership of an asset. (*Synthetic Holdings Ltd owns SYN-BA-10042*) |
| **`VISITED`** | `PERSON`, `VEHICLE` | `LOCATION` | Physical arrival, berthing, or presence at a venue. (*Marcus arrived at Warehouse 4*) |
| **`TRANSFERRED_TO`**| `BANK_ACCOUNT`, `PERSON` | `BANK_ACCOUNT`, `PERSON` | Movement of funds between financial nodes. (*Account A transferred to Account B*) |
| **`INVOLVED_IN`** | `PERSON`, `ORGANIZATION`, `VEHICLE` | `CASE_ID` | Formal subject or asset named in an investigation. (*Elena involved in CASE-2024-SYN-101*) |
| **`MENTIONED_IN`** | `PERSON`, `ALIAS`, `PHONE`, `ORGANIZATION` | `CASE_ID` | Secondary citation or cross-reference in a dossier. (*Phone mentioned in CASE-2024-SYN-101*) |
| **`CONNECTED_TO`** | `PERSON`, `ORGANIZATION` | `PERSON`, `ORGANIZATION` | Known institutional, corporate, or personal relationship. (*Marcus connected to Elena*) |
| **`OCCURRED_AT`** | `CASE_ID`, `PHONE` | `LOCATION` | Event or operational action linked to a venue. (*Case incident occurred at Pier 42*) |

---

## 5. Ambiguity & Decoy Disambiguation Rules

To prepare models for messy, real-world narrative text, annotators must adhere to strict disambiguation rules:

1. **Capitalized Common Nouns (Decoys):**
   - In law enforcement text, words like *General*, *March*, *Bill*, *Major*, and *Chase* frequently appear.
   - *Example:* *"During late March, officers gave chase."* -> **Do not annotate** as `DATE` or `PERSON`.
2. **Organization vs. Location:**
   - If a commercial facility name also denotes the physical address where an action took place:
     - Annotate as `ORGANIZATION` if referring to legal responsibility or charter (*"Apex Logistics chartered the vessel"*).
     - Annotate as `LOCATION` if referring strictly to physical coordinates (*"met at Terminal 2 Cargo Bay, East Port Facility"*).
3. **Negative / Unresolved Pronouns:**
   - Pronouns (*"he arrived"*, *"she called"*) are **never** annotated as `PERSON` unless part of a resolved co-reference link (which is not part of this baseline token classification task).

---

## 6. Error Analysis & Metrics Protocol

During model evaluation using `seqeval`:
- **Strict Match:** Both boundary offsets (`start`, `end`) and the entity `label` must match ground truth exactly.
- **Partial Span Overlap:** Marked as both a **False Positive** (for the predicted incorrect boundary) and a **False Negative** (for the missed exact boundary).
- **Evaluation Splits:** All test evaluations must run strictly against `test.jsonl`, without consulting `train.jsonl` or `validation.jsonl`.
