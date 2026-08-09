---
artifact_id: adr-shared-0006
domain: shared
layer: decision
authority: canonical
status: active
version: "1.0"
owner: graph-maintainers
---

# ADR-SHARED-0006: Graph Before Analytics

## Status

Accepted

## Normalization date

2026-07-23

## Context

OSI analytics depend on relationships, provenance, movement, and changing organizational conditions. Running analytics directly against raw CSV packages would duplicate import logic and weaken the distinction between source records and the canonical organizational model.

## Decision

Analytics shall operate on assured graph structures rather than directly on raw participant CSV packages.

## Alternatives considered

- Run analytics directly against CSV files.
- Maintain parallel CSV and graph analytical paths.
- Allow each analytical module to choose its own source representation.

## Consequences

The graph becomes the canonical organizational model for analytics. Graph import and Graph Assurance become prerequisites for production analytical capability. This adds an implementation stage but reduces duplicated logic and preserves relationship semantics.

## Related records

- [ADR-SHARED-0003](ADR-SHARED-0003-assurance-before-ingestion.md)
- [ADR-OSI-0001](../osi/ADR-OSI-0001-organizations-as-living-cooperative-systems.md)
