---
artifact_id: registry-adr-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.1"
owner: repository-governance
---

# ADR Registry

## Scope

This registry inventories the normalized, scope-based decision series.

| Artifact ID | Name | Domain | Layer | Authority | Status | Owner | Version | Canonical Location | Depends On |
|---|---|---|---|---|---|---|---|---|---|
| `decision-collection-001` | Architecture Decision Record Collection | `shared` | `decision` | `canonical` | `active` | `repository-governance` | `1.0` | [ADR collection](../../decisions/README.md) | `standard-registry-001` |
| `decision-index-001` | Architecture Decision Record Index | `shared` | `decision` | `canonical` | `active` | `repository-governance` | `1.0` | [ADR Index](../../decisions/ADR_INDEX.md) | `decision-collection-001`<br>`registry-adr-001` |
| `adr-scope-0000` | Architecture Decision Record Template | `shared` | `decision` | `working` | `proposed` | `responsible-role` | `1.0` | [ADR Template](../../decisions/ADR-TEMPLATE.md) | `decision-collection-001`<br>`repo-conventions-001` |
| `adr-shared-0001` | Repository Domain Boundaries | `shared` | `decision` | `canonical` | `active` | `repository-governance` | `1.0` | [ADR-SHARED-0001](../../decisions/shared/ADR-SHARED-0001-repository-domain-boundaries.md) | `repo-architecture-001` |
| `adr-shared-0002` | Shared Epistemology, Distinct Domain Ontologies | `shared` | `decision` | `canonical` | `active` | `ontology-maintainers` | `1.0` | [ADR-SHARED-0002](../../decisions/shared/ADR-SHARED-0002-shared-epistemology-distinct-domain-ontologies.md) | `adr-shared-0001`<br>`ontology-shared-meta-001` |
| `adr-shared-0003` | Assurance Before Ingestion | `shared` | `decision` | `canonical` | `active` | `assurance-maintainers` | `1.0` | [ADR-SHARED-0003](../../decisions/shared/ADR-SHARED-0003-assurance-before-ingestion.md) | `principle-shared-engineering-001` |
| `adr-shared-0004` | Assurance Reports as Canonical Output | `shared` | `decision` | `canonical` | `active` | `assurance-maintainers` | `1.0` | [ADR-SHARED-0004](../../decisions/shared/ADR-SHARED-0004-assurance-report-canonical-output.md) | `adr-shared-0003` |
| `adr-shared-0005` | Ethics as a First-Class Assurance Dimension | `shared` | `decision` | `canonical` | `active` | `assurance-maintainers` | `1.0` | [ADR-SHARED-0005](../../decisions/shared/ADR-SHARED-0005-ethics-first-class-assurance.md) | `adr-shared-0003`<br>`principle-osi-hippocratic-001` |
| `adr-shared-0006` | Graph Before Analytics | `shared` | `decision` | `canonical` | `active` | `graph-maintainers` | `1.0` | [ADR-SHARED-0006](../../decisions/shared/ADR-SHARED-0006-graph-before-analytics.md) | `adr-shared-0003`<br>`contract-shared-data-graph-001` |
| `adr-osi-0001` | Model Organizations as Living Cooperative Systems | `osi` | `decision` | `canonical` | `active` | `osi-architecture` | `1.0` | [ADR-OSI-0001](../../decisions/osi/ADR-OSI-0001-organizations-as-living-cooperative-systems.md) | `principle-osi-foundational-001` |
| `adr-osi-0002` | Predictability as a Precondition of Trust | `osi` | `decision` | `canonical` | `active` | `osi-architecture` | `1.0` | [ADR-OSI-0002](../../decisions/osi/ADR-OSI-0002-predictability-as-precondition-of-trust.md) | `adr-osi-0001` |
| `adr-osi-0003` | Organizational Health as an Emergent Construct | `osi` | `decision` | `canonical` | `active` | `osi-architecture` | `1.0` | [ADR-OSI-0003](../../decisions/osi/ADR-OSI-0003-organizational-health-as-emergent-construct.md) | `adr-osi-0001`<br>`adr-osi-0002` |
| `adr-osi-0004` | Predictability Precedes Trust | `osi` | `decision` | `historical` | `superseded` | `osi-architecture` | `1.0` | [ADR-OSI-0004](../../decisions/osi/ADR-OSI-0004-predictability-precedes-trust-superseded.md) | `adr-osi-0002` |
| `adr-osi-0005` | Organizations as Living Systems | `osi` | `decision` | `historical` | `superseded` | `osi-architecture` | `1.0` | [ADR-OSI-0005](../../decisions/osi/ADR-OSI-0005-organizations-as-living-systems-superseded.md) | `adr-osi-0001` |
| `adr-pia-0001` | PIA Evaluates Evidence, Not People | `pia` | `decision` | `working` | `proposed` | `pia-governance` | `1.0` | [ADR-PIA-0001](../../decisions/pia/ADR-PIA-0001-evidence-not-person-scoring.md) | `adr-shared-0001`<br>`principle-osi-hippocratic-001`<br>`contract-shared-data-graph-001` |
| `adr-imp-0001` | CSV Assurance Engine as Reference Implementation | `implementation` | `decision` | `canonical` | `active` | `assurance-maintainers` | `1.0` | [ADR-IMP-0001](../../decisions/implementation/ADR-IMP-0001-csv-assurance-reference-implementation.md) | `adr-shared-0003`<br>`adr-shared-0004`<br>`contract-shared-csv-001` |
| `adr-imp-0002` | Assurance-Gated Analytical Pipeline | `implementation` | `decision` | `working` | `proposed` | `assurance-maintainers` | `1.0` | [ADR-IMP-0002](../../decisions/implementation/ADR-IMP-0002-assurance-gated-analytical-pipeline.md) | `adr-shared-0003`<br>`adr-shared-0004`<br>`adr-shared-0006` |

## Known normalization work

Normalization is complete. Prior ADR-0007 and docs ADR-0006 remain preserved
as `adr-osi-0004` and `adr-osi-0005`, explicitly superseded by their more
complete authorities. The legacy mapping is recorded in the
[ADR Index](../../decisions/ADR_INDEX.md) and `MIG-001` in the
[Repository Migration Plan](../Repository_Migration_Plan.md).
