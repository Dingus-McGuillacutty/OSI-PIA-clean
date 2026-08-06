# OSI Component Development Standard

Version: **Pre-1.0 normative draft**

## Applicability

Assurance, import, graph, analytics, reporting, and future reasoning components.

## Required identity

Every component declares `component_id`, `component_version`, and `contract_version`.

## Required interface

Every component implements Contract, Validation, Congruence, Regression, Performance, Ethics, and Epistemic Integrity tests, and provides or inherits Audit and `assure()`.

## Rule output

Rules shall emit Findings and shall not bypass the Finding gate.

## Epistemic requirements

Components preserve source references, distinguish evidence from interpretation, expose uncertainty, use rule IDs, preserve Logic Chains, expose failures, and avoid silent input mutation.

## Ethics

Unresolved authorization should emit `REVIEW`; explicit prohibition or withdrawn consent should emit `ERROR` and block the affected operation.

## Continuous testing

Minimum coverage: regression, dimension routing, Finding integrity, Logic Chain integrity, and canonical calibration.

## Auditability

Runs must be uniquely identified, timestamped, versioned, serializable, attributable, and inspectable at Finding level.

## Human review

`REQUIRES_HUMAN_REVIEW` is an explicit state, not a silent fallback.
