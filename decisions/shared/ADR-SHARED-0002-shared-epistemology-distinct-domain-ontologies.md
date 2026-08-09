---
artifact_id: adr-shared-0002
domain: shared
layer: decision
authority: canonical
status: active
version: "1.0"
owner: ontology-maintainers
---

# ADR-SHARED-0002: Shared Epistemology, Distinct Domain Ontologies

## Status

Accepted

## Date

2026-07-23

## Context

OSI and PIA both require evidence, provenance, uncertainty, knowledge state,
review, and change over time. They do not, however, model the same domain.
Merging their ontologies would make similarly named concepts appear
interchangeable and could make domain-specific interpretation silently binding
across the project.

The two Neo4j reference databases already demonstrate the value of distinct
domain projections governed by common epistemic rules.

## Decision

OSI and PIA share a governed epistemic and meta-ontological foundation while
retaining distinct conceptual ontologies and reference graph projections.

Shared concepts define how knowledge claims are represented and governed.
OSI concepts define organizational systems. PIA concepts define participant
evidence and bounded assessment.

A shared concept is created only when its meaning is genuinely the same in
both domains. Otherwise, explicit mappings relate distinct OSI and PIA
concepts without merging them.

No third shared Neo4j database is required by this decision.

## Consequences

- Concept identifiers use `shared:`, `osi:`, or `pia:` namespaces.
- `osi-reference` and `pia-reference` remain separate.
- Shared graph architecture may govern both databases without combining their
  nodes or interpretations.
- The ontology registry records authority and domain explicitly.
- Similar labels require an explicit semantic crosswalk before cross-domain
  use.
- Graph implementation cannot promote a concept to canonical ontology status.

## Alternatives considered

### One combined ontology and reference database

Rejected because it obscures authority and increases accidental semantic
coupling.

### Fully independent epistemologies

Rejected because evidence, provenance, uncertainty, and knowledge lifecycle
rules should remain congruent across the platform.

### Shared labels without namespaces

Rejected because name similarity does not establish equivalent meaning.

## Related records

- [ADR-SHARED-0001](ADR-SHARED-0001-repository-domain-boundaries.md)
- [Ontology Meta-Model](../../ontology/META_ONTOLOGY.md)
- [Reference Graph Congruence Profile](../../architecture/graph_ontology/REFERENCE_GRAPH_CONGRUENCE.md)
