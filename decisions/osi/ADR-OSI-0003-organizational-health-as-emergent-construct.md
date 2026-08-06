---
artifact_id: adr-osi-0003
domain: osi
layer: decision
authority: canonical
status: active
version: "1.0"
owner: osi-architecture
---

# ADR-OSI-0003: Treat Organizational Health as an Emergent Construct

## Status

Accepted as a working architectural decision

## Date

2026-07-17

## Context

Common organizational assessments attempt to represent health using
isolated measures such as:

- engagement;
- turnover;
- productivity;
- financial performance;
- satisfaction;
- or trust.

Each of these may provide useful evidence, but none independently
represents organizational health.

## Decision

OSI will model Organizational Health as an emergent construct inferred
from multiple interacting conditions and observed transitions.

The recursive evidence model is:

Observable Indicators  
→ Structural and Relational Properties  
→ Predictability Field Estimate  
→ Trust Field Estimate  
→ Capability and Flow Estimate  
→ State Transition Analysis  
→ Organizational Health Estimate

## Rationale

Health exists at the system level.

It reflects the organization’s ability to:

- mobilize capability;
- maintain workable cooperation;
- process information;
- adapt;
- recover;
- learn;
- and produce sustainable outcomes.

A system may perform well temporarily while remaining unhealthy.

A system may also experience short-term disruption while adapting in
a healthy manner.

## Consequences

- OSI will not rely on one health score without supporting evidence.
- Health assessments must retain underlying indicators.
- State transitions and recovery patterns become central evidence.
- Performance and health must remain analytically distinct.
- Numerical precision must not disguise uncertainty.

## Related records

- [ADR-OSI-0001](ADR-OSI-0001-organizations-as-living-cooperative-systems.md)
- [ADR-OSI-0002](ADR-OSI-0002-predictability-as-precondition-of-trust.md)
