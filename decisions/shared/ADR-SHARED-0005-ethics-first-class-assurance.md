---
artifact_id: adr-shared-0005
domain: shared
layer: decision
authority: canonical
status: active
version: "1.0"
owner: assurance-maintainers
---

# ADR-SHARED-0005: Ethics as a First-Class Assurance Dimension

## Status

Accepted

## Normalization date

2026-07-23

## Context

A dataset can be technically valid while lacking appropriate consent, authorization, or use boundaries. Treating ethics as a side effect of validation would allow technically correct but ethically unsuitable information to proceed.

## Decision

Ethics shall be evaluated independently as a first-class assurance dimension. Technical validity does not imply ethical authorization.

## Alternatives considered

- Encode consent checks as ordinary validation rules.
- Handle ethics only through policy documentation.
- Defer ethical review until analytics or deployment.

## Consequences

Ethical findings become explicit, auditable, and capable of blocking or requiring human review. Components must preserve consent and use-boundary evidence throughout downstream processing.

## Related records

- [ADR-SHARED-0003](ADR-SHARED-0003-assurance-before-ingestion.md)
- [OSI Hippocratic Principle](../../governance/OSI%20Hippocratic%20Principle.md)
