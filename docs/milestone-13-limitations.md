# Milestone 13 Limitations

While Evidence-Backed HTML Report Generation has been successfully implemented, the prototype carries several known limitations relevant to production deployment.

## 1. Output Format
- The system currently only exports HTML. PDF generation is intentionally deferred. While HTML is portable and highly accessible for browser inspection and printing, a future milestone must implement secure server-side PDF rendering (e.g., via headless Chromium or `WeasyPrint`) if tamper-evident offline documents are required.

## 2. No Report Signing / Hashing
- Downloaded reports do not currently carry a digital signature (e.g., GPG or a cryptographic hash embedded on a ledger). As a result, if a user tampers with the HTML file locally, the backend cannot inherently prove it was modified.

## 3. Ephemeral Generation
- Reports are generated on demand in memory and immediately discarded by the server. While this ensures data privacy and reduces persistent attack surfaces, it also means there is no historical "snapshot" of a report retrieved later if the underlying case data is subsequently altered.

## 4. Synthetic Data Context
- All evidence excerpts, cases, and relationships are entirely synthetic for the SIH prototype.

## 5. UI Loading Experience
- If generating a massive report for a case hitting the upper limits (500 entities, 500 relationships), the on-demand generation might take noticeable CPU time on the backend. No asynchronous background worker (e.g., Celery) is used for export in this prototype.
