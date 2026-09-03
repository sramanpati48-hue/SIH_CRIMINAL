# Synthetic Dataset (SIH 26189 Prototype)

This directory contains deterministic, synthetic data for testing the Criminal Network Analysis pipeline. 
**No real personal data is present in these files.** All records are generated using standard seeded faker libraries and contain planted patterns specifically for demonstration and verification of graph analytics.

## Files and Data Dictionary

| File | Primary Key | Required Columns | Description |
| :--- | :--- | :--- | :--- |
| `cases.csv` | `case_id` | `case_id`, `title`, `status`, `opened_at` | Baseline investigation cases. |
| `people.csv` | `person_id` | `person_id`, `name`, `alias`, `dob`, `case_id` | Synthetic identities. |
| `phones.csv` | `phone_id` | `phone_id`, `number`, `owner_person_id`, `case_id` | Synthetic phone subscriptions. |
| `vehicles.csv` | `vehicle_id` | `vehicle_id`, `plate`, `owner_person_id`, `case_id` | Synthetic vehicle registrations. |
| `locations.csv` | `location_id` | `location_id`, `address`, `case_id` | Physical addresses or coordinates. |
| `calls.csv` | N/A | `caller_phone_id`, `receiver_phone_id`, `timestamp`, `duration_seconds`, `case_id` | Synthetic Call Detail Records (CDR). |
| `transactions.csv` | `transaction_id` | `transaction_id`, `source_account`, `target_account`, `amount`, `timestamp`, `case_id` | Synthetic financial transactions. |
| `case_reports.json` | `report_id` | `report_id`, `case_id`, `text` | Synthetic unstructured surveillance and incident reports. |

## Planted Patterns (Manifest)
The generator is seeded to reliably produce these specific graph topologies:

1. **Cross-case connector:** `P001` is associated with three different cases (`C001`, `C002`, `C003`).
2. **Shared phone:** `PH001` is owned/used by both `P002` and `P003`.
3. **Shared vehicle:** `V001` is observed in both `C006` and `C007`.
4. **Repeated location:** `P004`, `P005`, and `P006` are co-located at `LOC002` (embedded in `DOC002` unstructured text).
5. **Rapid transaction chain:** `BA001` -> `BA002` -> `BA003` -> `BA004` within 48 hours in `C001`.
6. **Bridge relationship:** `P010` is explicitly linked to both the `C004` and `C005` clusters.
7. **Legitimate high-connectivity:** `BA050` acts as a central hub for multiple synthetic transactions (representing a legitimate financial institution hub).
