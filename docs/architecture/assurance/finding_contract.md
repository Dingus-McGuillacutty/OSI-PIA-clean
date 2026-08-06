# Finding Contract

Version: **Pre-1.0 normative draft**

## Definition

A Finding is the atomic reasoning record and the required gate between rule evaluation and assurance reporting.

## Fields

| Field | Requirement |
|---|---|
| severity | Required |
| code | Required |
| message | Required |
| dimension | Required |
| rule_id | Required |
| source_reference | Optional |
| file / row / field | Optional source location |
| evidence | Required when no source reference exists |
| logic_chain | Required by epistemic policy |
| confidence | Optional |
| uncertainty | Optional |

## Severity values

`error`, `warning`, `notice`, `review`.

## Mapping

- any error → `FAIL`
- otherwise any review → `REQUIRES_HUMAN_REVIEW`
- otherwise any warning → `PASS_WITH_WARNINGS`
- otherwise → `PASS`

A notice does not independently raise disposition.

## Minimum epistemic requirements

Every Finding shall contain a rule ID, dimension, Logic Chain, and either a source reference or evidence.

## Immutability

Implemented Findings are frozen dataclasses and should be treated as immutable records.

## Naming

Codes use uppercase snake case. Rule IDs use dimension-prefixed dotted names.
