# Milestone 9 Progress Review

## Completed Work
- **Local NER Provider:** Implemented `SpacyNERProvider` in `local_ner_provider.py`.
- **Label Mapping:** Created `label_mapping.py` to map spaCy entity types to internal `EntityType` values.
- **Post Processing Placeholder:** Created `post_processing.py`.
- **Dependencies:** Created `requirements-ner.txt` containing optional dependencies (`spacy`).
- **Documentation:** Created `local-ner-provider.md` documenting architecture.
- **Tests:** Created `test_local_ner_provider.py` which ensures the missing model case raises `RuntimeError` rather than crashing on initialization.
- **Configuration:** Updated `apps/backend/app/core/config.py` to add the `EXTRACTION_PROVIDER` property.

## Missing Work
- The deterministic NLP post-processing (Prompt 5) is partially implemented (the file `post_processing.py` exists, but lacks robust logic for overlap resolution, determinism, duplicate spans, confidence preservation, etc.).

## Configuration Risks
- **No data loss occurred.** A previous Python script used to modify `config.py` was executed safely because it read the duplicated output of a `replace_file_content` tool call rather than the original file contents. `git diff` confirms all previous configuration fields (`DATABASE_URL`, `NEO4J_URI`, `DEV_REVIEWER_ID`, etc.) remain intact.

## Test Results
- Clean test run confirms `MockExtractor` remains the default, `SpacyNERProvider` correctly triggers optional degradation, and existing application behavior is unchanged. Tests pass flawlessly as SQLite locking issues from dangling processes were resolved.

## Whether Prompt 5 is Already Partially Implemented
- **Yes.** The file `post_processing.py` was created, but it currently only contains placeholder mock logic.

## Exact Next Safe Prompt to Run
```text
# Continue Milestone 9: Harden Deterministic NLP Post-Processing

Project root: <Use the currently open repository root>

The optional local NER provider is implemented. Do not replace MockExtractor. Do not download models. Do not modify unrelated files.

Before coding:
1. Read docs/milestone-9-progress-review.md.
2. Inspect:
   - apps/backend/app/extraction/schemas.py
   - apps/backend/app/extraction/local_ner_provider.py
   - apps/backend/app/extraction/mock_provider.py
   - apps/backend/app/extraction/label_mapping.py
   - apps/backend/app/extraction/post_processing.py
   - apps/backend/app/extraction/service.py
   - existing extraction tests
3. List intended file changes.
4. Preserve all existing tests.

Harden post-processing for these entity types:
- PHONE
- VEHICLE
- BANK_ACCOUNT
- CASE_ID
- DATE
- MONEY
- ALIAS

Requirements:
- Preserve original text.
- Preserve exact start and end offsets.
- Ensure text[start:end] equals the candidate text.
- Use only allow-listed labels.
- Resolve duplicate spans deterministically.
- Resolve overlaps deterministically and document the policy.
- Preserve provider confidence.
- Store post-processing version.
- Generate stable candidate IDs for identical input.
- Do not automatically mark candidates as verified.
- Do not merge entities across cases.
- Do not fabricate dates, amounts, relationships, or evidence.
- Do not create relationship candidates in the post-processing module.
- Keep source-document IDs intact.

Implement pure, unit-testable functions.
Add or update:
- tests/backend/test_post_processing.py

Test:
- phone extraction
- vehicle extraction
- bank-account extraction
- case-ID extraction
- date extraction
- money extraction
- alias extraction
- exact offsets
- duplicate spans
- overlapping spans
- malformed text
- missing values
- unsupported labels
- repeated-input determinism
- provider confidence preservation
- UNREVIEWED default status
- source-document preservation

Run:
- pytest -q tests/backend/
- pytest -m neo4j

Do not run Docker commands.
At the end, report:
- files changed
- post-processing rules
- overlap policy
- tests executed
- test results
- remaining limitations
```
