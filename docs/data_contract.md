# Connector 001 Data Contract

Every normalized record must retain enough information to trace it back to its origin.

## Required provenance

- `participant_id`
- `source_file`
- `source_row`
- `evidence_id`
- `derivation_method`

## Confidence vocabulary

- `source_asserted` — directly stated by the source archive
- `corroborated` — supported by two or more independent records
- `derived_low` — deterministic but weak inference
- `derived_medium` — multiple signals support the inference
- `human_validated` — reviewed and accepted by the participant or analyst

## Sensitivity vocabulary

- `private`
- `restricted`
- `shareable_with_consent`
- `public_source`

Connection details, messages, phone numbers, email addresses, application data, and
advertising-targeting data default to `restricted`.
