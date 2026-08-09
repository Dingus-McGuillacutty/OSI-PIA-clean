# OSI Reference Architecture

Version: **Pre-1.0 review draft**  
Implementation baseline: `OSIComponent` and `CSVAssuranceEngine` v0.3

## Purpose

OSI requires software components to expose the basis, limits, and integrity of their operation. The architecture separates component-specific evaluation from standard reporting.

```text
Input → OSI Component → Assurance Rules → Findings → Assurance Results → Assurance Report
```

## Core objects

### OSIComponent
Declares `component_id`, `component_version`, and `contract_version`, and implements the assurance dimensions.

### Finding
A traceable rule result containing severity, code, message, dimension, rule identifier, source, evidence, uncertainty, and Logic Chain.

### AssuranceResult
Represents one assurance dimension for one run.

### AssuranceReport
Represents the complete assurance state of one component run.

## Ordered assurance dimensions

1. Contract
2. Validation
3. Congruence
4. Regression
5. Performance
6. Ethics
7. Epistemic Integrity
8. Audit

## Dispositions

`PASS`, `PASS_WITH_WARNINGS`, `FAIL`, `NOT_APPLICABLE`, `REQUIRES_HUMAN_REVIEW`.

Overall priority: `FAIL`, `REQUIRES_HUMAN_REVIEW`, `PASS_WITH_WARNINGS`, `PASS`, `NOT_APPLICABLE`.

## Failure exposure

Unhandled assurance exceptions become failed dimension results rather than being hidden.

## Continuous integrity

Each component should be tested for regression, dimension routing, Finding integrity, Logic Chain integrity, and calibration against canonical datasets.

Calibration is platform verification, not a ninth runtime dimension.

## Extension model

CSV, graph import, graph assurance, analytics, and future reasoning engines should share this contract while defining their own rules.
