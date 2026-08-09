# CSV Assurance Engine Specification

Version: **0.3 implementation specification**

## Purpose

Evaluates canonical OSI/PIA participant CSV packages before graph import while preserving validator compatibility.

## Inputs

- `participant.csv`
- `source.csv`
- `experience.csv`
- `evidence.csv`
- `capability.csv`
- `evidence_capability_mapping.csv`

Contract version: `0.1`.

## Outputs

- standard `AssuranceReport`
- legacy compatibility report
- JSON
- automation-friendly exit status

## Gates

### Contract
Required files, readable CSVs, and required columns.

### Validation
Required values, enums, ID patterns, uniqueness, ISO dates, and confidence range.

### Congruence
Participant, source, experience, evidence, and capability relationships.

### Regression
Checks parity between blocking Findings and legacy acceptance. Drift emits `ACCEPTANCE_DRIFT` under `regression.acceptance_parity`.

### Performance
Records rows and elapsed time.

### Ethics
`granted` passes; `pending` and `limited` require review; `withdrawn` fails and blocks import.

### Epistemic Integrity
Checks experience context, source locator, and required Finding traceability.

### Audit
Records component and contract versions plus Finding counts by dimension and severity.

## Compatibility

Reference module: `software/importer/csv_assurance_engine.py`  
Compatibility module: `software/importer/osi_pia_validate.py`

Legacy acceptance remains: no `ERROR` Findings.

## Non-goals

The engine does not import Neo4j data, validate graph state, perform analytics, resolve limited-consent scope, or replace human review.
