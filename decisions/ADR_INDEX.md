---
artifact_id: decision-index-001
domain: shared
layer: decision
authority: canonical
status: active
version: "1.0"
owner: repository-governance
---

# ADR Index

## Purpose

This index is the human navigation and migration record for OSI-PIA decisions.
The stable artifact IDs and dependency graph are maintained in the
[ADR Registry](../governance/registries/ADR_REGISTRY.md).

## Canonical decisions and legacy mapping

| Current ADR | Decision | Status | Prior location or ID | Reason for scope |
|---|---|---|---|---|
| [ADR-SHARED-0001](shared/ADR-SHARED-0001-repository-domain-boundaries.md) | Repository Domain Boundaries | Accepted | New | Governs OSI and PIA as peer domains |
| [ADR-SHARED-0002](shared/ADR-SHARED-0002-shared-epistemology-distinct-domain-ontologies.md) | Shared Epistemology, Distinct Domain Ontologies | Accepted | New | Governs cross-domain knowledge architecture |
| [ADR-SHARED-0003](shared/ADR-SHARED-0003-assurance-before-ingestion.md) | Assurance Before Ingestion | Accepted | `docs/adr/ADR-0001` | Applies before OSI or PIA ingestion |
| [ADR-SHARED-0004](shared/ADR-SHARED-0004-assurance-report-canonical-output.md) | Assurance Reports as Canonical Output | Accepted | `docs/adr/ADR-0002` | Defines a shared assurance interface |
| [ADR-SHARED-0005](shared/ADR-SHARED-0005-ethics-first-class-assurance.md) | Ethics as a First-Class Assurance Dimension | Accepted | `docs/adr/ADR-0003` | Constrains both domains and implementations |
| [ADR-SHARED-0006](shared/ADR-SHARED-0006-graph-before-analytics.md) | Graph Before Analytics | Accepted | `docs/adr/ADR-0005` | Establishes shared pipeline ordering |
| [ADR-OSI-0001](osi/ADR-OSI-0001-organizations-as-living-cooperative-systems.md) | Organizations as Living Cooperative Systems | Accepted | `architecture/Architecture/decisions/ADR-0001` | Defines OSI system meaning |
| [ADR-OSI-0002](osi/ADR-OSI-0002-predictability-as-precondition-of-trust.md) | Predictability as a Precondition of Trust | Accepted | `architecture/Architecture/decisions/ADR-0002` | Defines OSI construct relationships |
| [ADR-OSI-0003](osi/ADR-OSI-0003-organizational-health-as-emergent-construct.md) | Organizational Health as an Emergent Construct | Accepted | `architecture/Architecture/decisions/ADR-0003` | Defines OSI analytical meaning |
| [ADR-OSI-0004](osi/ADR-OSI-0004-predictability-precedes-trust-superseded.md) | Predictability Precedes Trust | Superseded by ADR-OSI-0002 | `architecture/Architecture/decisions/ADR-0007` | Preserves the duplicate historical record |
| [ADR-OSI-0005](osi/ADR-OSI-0005-organizations-as-living-systems-superseded.md) | Organizations as Living Systems | Superseded by ADR-OSI-0001 | `docs/adr/ADR-0006` | Preserves the second historical formulation |
| [ADR-PIA-0001](pia/ADR-PIA-0001-evidence-not-person-scoring.md) | PIA Evaluates Evidence, Not People | Proposed | `decisions/ADR-PIA-EVIDENCE-NOT-PERSON-SCORING` | Defines a PIA assessment boundary |
| [ADR-IMP-0001](implementation/ADR-IMP-0001-csv-assurance-reference-implementation.md) | CSV Assurance Engine as Reference Implementation | Accepted | `docs/adr/ADR-0004` | Selects a reference implementation |
| [ADR-IMP-0002](implementation/ADR-IMP-0002-assurance-gated-analytical-pipeline.md) | Assurance-Gated Analytical Pipeline | Proposed | `architecture/Architecture/decisions/ADR-0008` | Proposes implementation gate behavior |

## Normalization outcome

The prior three ADR collections were normalized without discarding records.
Two duplicate decisions remain available as explicitly superseded history.
References use stable scoped IDs, so later path migrations do not require
renumbering.
