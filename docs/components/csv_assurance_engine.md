# CSV Assurance Engine

Status: Certified Reference Implementation  
Version: 1.0

## Purpose

The CSV Assurance Engine evaluates canonical participant packages before graph import. It is the first certified implementation of the OSI Assurance Framework.

## Pipeline position

```text
Participant Package
↓
CSV Assurance Engine
↓
Assurance Report
↓
Graph Import
```

## Canonical package

- `participant.csv`
- `source.csv`
- `experience.csv`
- `evidence.csv`
- `capability.csv`
- `evidence_capability_mapping.csv`

## Assurance dimensions

The engine evaluates Contract, Validation, Congruence, Regression, Performance, Ethics, Epistemic Integrity, and Audit.

## Findings

A Finding records severity, code, message, rule identifier, assurance dimension, evidence, logic chain, source reference, and uncertainty where applicable.

## Assurance results

Each dimension produces an `AssuranceResult` with its disposition, findings, evidence, metrics, and explanatory message.

## Assurance report

`AssuranceReport` is the canonical public output. It records component and contract versions, run identity, dimension results, findings, evidence references, and overall disposition.

## CLI

```bash
python -m software.importer.csv_assurance_engine path/to/package
python -m software.importer.csv_assurance_engine path/to/package --assurance-only
python -m software.importer.csv_assurance_engine path/to/package --report report.json
```

A successful package returns exit code `0`; a failed package returns exit code `2`.

## Compatibility

The engine preserves the legacy validation interface while exposing canonical v1.0 assurance behavior. Future assurance engines should inherit the framework contracts rather than create incompatible report structures.