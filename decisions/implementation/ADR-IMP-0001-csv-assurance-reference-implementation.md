---
artifact_id: adr-imp-0001
domain: implementation
layer: decision
authority: canonical
status: active
version: "1.0"
owner: assurance-maintainers
---

# ADR-IMP-0001: CSV Assurance Engine as Reference Implementation

## Status

Accepted

## Normalization date

2026-07-23

## Context

The Assurance Framework requires a concrete implementation to prove its contracts and provide a stable pattern for future engines.

## Decision

CSV Assurance Engine v1.0 is the certified reference implementation of the OSI Assurance Framework.

## Alternatives considered

- Keep the CSV engine as a provisional validator.
- Wait for Graph Assurance before certifying a reference implementation.
- Allow each engine to reinterpret the framework contracts.

## Consequences

Future assurance engines inherit the stable component, Finding, AssuranceResult, and AssuranceReport contracts. Changes to the CSV engine must preserve compatibility or explicitly revise the framework contract.

## Related records

- [ADR-SHARED-0003](../shared/ADR-SHARED-0003-assurance-before-ingestion.md)
- [ADR-SHARED-0004](../shared/ADR-SHARED-0004-assurance-report-canonical-output.md)
