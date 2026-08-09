# Assurance Report Contract

Version: **Pre-1.0 normative draft**

## Purpose

The AssuranceReport is the complete serializable record of one OSI component assurance run.

## Fields

- component ID and version
- contract version
- run ID
- UTC timestamp
- input reference
- configuration reference
- ordered results
- overall disposition
- reviewer
- waivers

Each AssuranceResult contains dimension, disposition, message, errors, warnings, metrics, evidence, and findings.

## Required order

contract, validation, congruence, regression, performance, ethics, epistemic_integrity, audit.

## Finalization priority

`FAIL` → `REQUIRES_HUMAN_REVIEW` → `PASS_WITH_WARNINGS` → `PASS` → `NOT_APPLICABLE`.

## Failure containment

Unhandled dimension exceptions become failed AssuranceResults and preserve exception type and message.

## Reviewer and waivers

The framework carries these fields, but full waiver authority is not yet defined. Waivers must never erase Findings.
