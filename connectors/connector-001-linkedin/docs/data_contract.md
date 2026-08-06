---
artifact_id: contract-pia-linkedin-001
domain: pia
layer: contract
authority: canonical
status: active
version: "1.0"
owner: pia-connectors
---

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

## Authority boundary

The connector records source-grounded claims and deterministic normalization.
It does not verify the source assertion, assign capability, or authorize graph
import. Downstream use remains governed by the shared CSV, validation, import,
and graph contracts.
