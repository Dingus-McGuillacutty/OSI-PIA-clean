---
artifact_id: adr-shared-0004
domain: shared
layer: decision
authority: canonical
status: active
version: "1.0"
owner: assurance-maintainers
---

# ADR-SHARED-0004: Assurance Reports as Canonical Output

## Status

Accepted

## Normalization date

2026-07-23

## Context

Assurance engines evaluate multiple dimensions and may contain component-specific rules. Downstream consumers need a stable interface that does not depend on internal validation routines.

## Decision

`AssuranceReport` is the canonical public output of every OSI Assurance Engine.

## Alternatives considered

- Expose raw validator output.
- Return only a Boolean acceptance decision.
- Let each component define its own report format.

## Consequences

Consumers receive a versioned, extensible, auditable contract containing component identity, findings, dimension results, evidence, and overall disposition. Components must translate internal behavior into this shared report contract.

## Related records

- [ADR-SHARED-0003](ADR-SHARED-0003-assurance-before-ingestion.md)
- [ADR-IMP-0001](../implementation/ADR-IMP-0001-csv-assurance-reference-implementation.md)
