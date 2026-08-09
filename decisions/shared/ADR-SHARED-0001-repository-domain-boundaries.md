---
artifact_id: adr-shared-0001
domain: shared
layer: decision
authority: canonical
status: active
version: "1.0"
owner: repository-governance
---

# ADR-SHARED-0001: Repository Domain Boundaries

## Status

Accepted

## Date

2026-07-23

## Context

OSI and PIA share evidence, provenance, assurance, contracts, and
meta-ontological rules, but they answer different questions. Repository paths
and prior descriptions sometimes implied that PIA was merely an input to OSI
or that one domain could silently inherit the other's interpretations.

That ambiguity risks semantic entanglement, inappropriate cross-domain
inference, and outputs whose authority cannot be determined by humans or
software.

## Decision

OSI and PIA are peer domain implementations of a shared foundation.

- `shared` governs cross-domain epistemology, assurance, contracts, and
  repository behavior.
- `osi` governs organizational-system concepts, models, analyses, and outputs.
- `pia` governs participant evidence, capability, assessment, and outputs.
- `implementation` provides technical machinery without creating domain
  meaning.
- `test` provides fixtures and verification behavior only.

Neither OSI nor PIA is a subset, extension, data source, or subordinate
component of the other.

Cross-domain use requires an explicit mapping, declared purpose, preserved
provenance, and assurance review proportionate to consequence.

## Consequences

- Governed artifacts declare exactly one domain.
- ADRs, registries, namespaces, graph projections, and outputs expose domain
  scope.
- Shared artifacts cannot silently impose OSI meaning on PIA or PIA meaning on
  OSI.
- Physical repository normalization may proceed in bounded migrations.
- Cross-domain analytical products remain attributable to explicit contracts
  and human accountability.

## Alternatives considered

### PIA as an OSI submodule

Rejected because participant evidence and assessment have independent
governance and output boundaries.

### OSI and PIA as unrelated repositories

Rejected because both domains rely on a genuinely shared epistemic,
provenance, assurance, and contract foundation.

### Infer domain from paths

Rejected because current paths include compatibility locations and cannot
reliably communicate authority.

## Related records

- [Repository Architecture](../../governance/Repository_Architecture.md)
- [Repository Conventions](../../governance/Repository_Conventions.md)
- [ADR-SHARED-0002](ADR-SHARED-0002-shared-epistemology-distinct-domain-ontologies.md)
