---
artifact_id: adr-osi-0002
domain: osi
layer: decision
authority: canonical
status: active
version: "1.0"
owner: osi-architecture
---

# ADR-OSI-0002: Model Predictability as a Precondition of Trust

## Status

Accepted as a working architectural decision

## Date

2026-07-17

## Context

Earlier OSI discussions treated trust as a primary organizational
condition.

Further development showed that trust often emerges from repeated
experience of whether an environment is understandable, reliable,
explainable, and workable.

Legibility and consistency were initially considered separate
constructs.

They are now treated as major components of Predictability.

## Decision

OSI will model the Predictability Field as a foundational condition
that contributes to the emergence and maintenance of the Trust Field.

The working relationship is:

Predictability Field  
→ Trust Field  
→ Organizational Flow  
→ Capability Utilization  
→ Organizational Outcomes

## Rationale

People are better able to participate, cooperate, and take appropriate
risk when they can form reliable mental models of:

- decisions;
- authority;
- rules;
- expectations;
- consequences;
- and organizational responses.

Dynamic organizations can remain predictable when change is legible,
explained, and consistently managed.

Predictability therefore does not mean sameness or rigidity.

## Consequences

- Predictability becomes a core OSI construct.
- Legibility and consistency are modeled within Predictability.
- Trust is treated as emergent rather than entirely primary.
- Indicators of decision clarity and rule reliability become important.
- Organizational uncertainty must be distinguished from organizational
  dynamism.

## Open questions

- Which indicators best estimate Predictability Field strength?
- How quickly can trust recover after predictability is restored?
- Can localized predictability support trust within a globally
  unpredictable organization?

## Supersedes

- [ADR-OSI-0004](ADR-OSI-0004-predictability-precedes-trust-superseded.md)

## Related records

- [ADR-OSI-0001](ADR-OSI-0001-organizations-as-living-cooperative-systems.md)
- [Foundational OSI Principles](../../principles/Foundational%20Principles.md)
