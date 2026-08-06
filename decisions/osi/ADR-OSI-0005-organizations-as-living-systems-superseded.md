---
artifact_id: adr-osi-0005
domain: osi
layer: decision
authority: historical
status: superseded
version: "1.0"
owner: osi-architecture
---

# ADR-OSI-0005: Organizations as Living Systems

## Status

Superseded by
[ADR-OSI-0001](ADR-OSI-0001-organizations-as-living-cooperative-systems.md).

## Normalization date

2026-07-23

## Context

Static organizational charts and isolated metrics cannot adequately represent how capability, trust, knowledge, relationships, movement, and motivation evolve over time.

## Decision

OSI models organizations as living cooperative systems rather than static hierarchies.

## Alternatives considered

- Model only formal structure and reporting lines.
- Treat organizational measures as independent snapshots.
- Reduce organizational condition to a single composite score.

## Consequences

Future analytics should examine relationships, temporal change, and state transitions rather than isolated records alone. This decision informs organizational health, capability capital, organizational metabolism, trust research, and PIA-informed longitudinal reasoning.

The model requires careful uncertainty handling and must not imply that organizations are literally biological organisms.

## Related records

- [ADR-SHARED-0006](../shared/ADR-SHARED-0006-graph-before-analytics.md)
- [Supporting Architectural Principles](../../docs/principles/architectural_principles.md)

## Supersession rationale

ADR-OSI-0001 contains the earlier and more complete decision, including the
living cooperative human-system boundary and alternatives. This record is
retained as a later implementation-era formulation.
