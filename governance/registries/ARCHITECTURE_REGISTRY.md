---
artifact_id: registry-architecture-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.10"
owner: repository-governance
---

# Architecture Registry

## Scope

This registry indexes stable repository, knowledge, assurance, domain, and
graph architecture.

| Artifact ID | Name | Domain | Layer | Authority | Status | Owner | Version | Canonical Location | Depends On |
|---|---|---|---|---|---|---|---|---|---|
| `repo-architecture-001` | Repository Architecture | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.1` | [Repository Architecture](../Repository_Architecture.md) | `principle-shared-engineering-001` |
| `governance-model-001` | OSI-PIA Governance Model | `shared` | `governance` | `working` | `proposed` | `repository-governance` | `0.2.0` | [Governance Model](../GOVERNANCE_MODEL.md) | `repo-architecture-001`<br>`repo-conventions-001`<br>`standard-registry-001`<br>`standard-namespace-001`<br>`architecture-knowledge-governance-001`<br>`adr-shared-0001`<br>`adr-shared-0002`<br>`principle-osi-hippocratic-001`<br>`principle-pia-measurement-001` |
| `governance-model-ratification-review-001` | Governance Model Ratification Review | `shared` | `governance` | `supporting` | `active` | `repository-governance` | `0.1.0` | [Ratification Review](../GOVERNANCE_MODEL_RATIFICATION_REVIEW.md) | `governance-model-001`<br>`architecture-knowledge-governance-001`<br>`software-governance-validator-001` |
| `repo-migration-plan-001` | Repository Migration Plan | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.2` | [Repository Migration Plan](../Repository_Migration_Plan.md) | `repo-architecture-001`<br>`repo-conventions-001`<br>`standard-clean-release-001` |
| `architecture-osi-domain-001` | OSI Repository and Domain Architecture | `osi` | `architecture` | `supporting` | `active` | `osi-architecture` | `unversioned` | [OSI Repository Architecture](../../architecture/Architecture/Architecture.md) | `repo-architecture-001`<br>`ontology-osi-meta-model-001` |
| `architecture-osi-constitution-001` | OSI Philosophical Constitution | `osi` | `foundation` | `supporting` | `active` | `osi-architecture` | `0.1` | [OSI Philosophical Constitution](../../foundation/OSI_CONSTITUTION.md) | `principle-osi-foundational-001`<br>`governance-model-001` |
| `architecture-osi-overview-001` | OSI Architecture Overview | `osi` | `architecture` | `supporting` | `active` | `osi-architecture` | `unversioned` | [Architecture Overview](../../architecture/Architecture/Overview.md) | `architecture-osi-domain-001` |
| `architecture-knowledge-lifecycle-001` | Knowledge Lifecycle | `shared` | `architecture` | `canonical` | `active` | `knowledge-governance` | `unversioned` | [Knowledge Lifecycle](../../foundation/KNOWLEDGE_LIFECYCLE.md) | `principle-shared-engineering-001` |
| `architecture-knowledge-governance-001` | Knowledge Management Governance | `shared` | `architecture` | `canonical` | `active` | `knowledge-governance` | `unversioned` | [Knowledge Management Governance](../../docs/architecture/KNOWLEDGE_MANAGEMENT_GOVERNANCE.md) | `architecture-knowledge-lifecycle-001` |
| `architecture-assurance-001` | Assurance Architecture | `shared` | `architecture` | `canonical` | `active` | `assurance-maintainers` | `unversioned` | [Assurance Architecture](../../docs/architecture/Assurance_Architecture.md) | `adr-shared-0003`<br>`adr-shared-0004` |
| `architecture-system-pipeline-001` | OSI System Pipeline | `osi` | `architecture` | `canonical` | `active` | `osi-architecture` | `unversioned` | [OSI System Pipeline](../../docs/architecture/OSI_System_Pipeline.md) | `architecture-assurance-001`<br>`adr-shared-0006` |
| `architecture-import-pipeline-001` | Import Pipeline | `implementation` | `architecture` | `supporting` | `active` | `graph-maintainers` | `unversioned` | [Import Pipeline](../../architecture/Import%20Pipeline/README.md) | `contract-shared-import-001` |
| `architecture-pia-intake-subsystem-001` | PIA Intake Subsystem Framework | `pia` | `architecture` | `working` | `proposed` | `pia-intake` | `0.8.1` | [PIA Intake Subsystem Framework](../../architecture/pia-intake/PIA_Intake_Subsystem_Framework.md) | `principle-pia-measurement-001`<br>`principle-pia-behavioral-inference-001`<br>`ontology-pia-capability-pattern-001`<br>`contract-shared-data-graph-001`<br>`contract-pia-capability-evidence-mapping-002`<br>`contract-shared-import-001`<br>`graph-pia-reference-001`<br>`governance-model-001` |
| `architecture-pia-intake-phase2b-protection-001` | PIA Phase 2B Protection Profile | `pia` | `architecture` | `working` | `proposed` | `pia-intake` | `0.1.0` | [PIA Phase 2B Protection Profile](../../architecture/pia-intake/PIA_Phase_2B_Protection_Profile.md) | `architecture-pia-intake-subsystem-001`<br>`contract-pia-intake-phase1-json-001`<br>`governance-model-001` |
| `architecture-pia-protected-evidence-extraction-001` | PIA Protected Evidence Extraction Profile | `pia` | `architecture` | `working` | `proposed` | `pia-intake` | `0.2.1` | [PIA Protected Evidence Extraction Profile](../../architecture/pia-intake/PIA_Protected_Evidence_Extraction_Profile.md) | `architecture-pia-intake-subsystem-001`<br>`architecture-pia-intake-phase2b-protection-001`<br>`contract-pia-protected-evidence-extraction-001` |
| `architecture-pia-credential-library-001` | PIA Credential Definition Library | `pia` | `architecture` | `working` | `proposed` | `pia-intake` | `0.5.0` | [PIA Credential Definition Library](../../architecture/pia-intake/PIA_Credential_Definition_Library.md) | `architecture-pia-intake-subsystem-001`<br>`principle-pia-behavioral-inference-001`<br>`ontology-pia-capability-pattern-001`<br>`contract-pia-capability-evidence-mapping-002` |
| `architecture-pia-intake-phase3a-review-001` | PIA Phase 3A Credential Review Profile | `pia` | `architecture` | `working` | `proposed` | `pia-intake` | `0.1.0` | [PIA Phase 3A Credential Review Profile](../../architecture/pia-intake/PIA_Phase_3A_Credential_Review_Profile.md) | `architecture-pia-intake-subsystem-001`<br>`architecture-pia-credential-library-001`<br>`contract-pia-credential-catalog-001`<br>`governance-model-001` |
| `architecture-pia-intake-phase3b-lookup-001` | PIA Phase 3B Credential Lookup Profile | `pia` | `architecture` | `working` | `proposed` | `pia-intake` | `0.2.0` | [PIA Phase 3B Credential Lookup Profile](../../architecture/pia-intake/PIA_Phase_3B_Credential_Lookup_Profile.md) | `architecture-pia-intake-subsystem-001`<br>`architecture-pia-credential-library-001`<br>`contract-pia-credential-lookup-001`<br>`contract-pia-credential-catalog-001`<br>`governance-model-001` |
| `architecture-graph-platform-001` | OSI-PIA Graph Architecture | `shared` | `architecture` | `canonical` | `active` | `graph-maintainers` | `1.0` | [Graph Architecture](../../architecture/graph_ontology/Graph_Architecture.md) | `adr-shared-0002`<br>`standard-namespace-001`<br>`architecture-reference-graph-congruence-001` |
| `architecture-graph-crosswalk-001` | OSI-PIA Graph Ontology Crosswalk | `shared` | `architecture` | `canonical` | `active` | `graph-maintainers` | `unversioned` | [Graph Ontology Crosswalk](../../architecture/graph_ontology/graph_Ontology.md) | `ontology-shared-meta-001`<br>`contract-shared-data-graph-001` |
| `architecture-graph-schema-reference-001` | Canonical Graph Schema References | `shared` | `architecture` | `supporting` | `active` | `graph-maintainers` | `unversioned` | [Canonical Schema References](../../architecture/graph_ontology/Canonical_Schema.md) | `architecture-graph-crosswalk-001` |
| `architecture-reference-graph-congruence-001` | OSI-PIA Reference Graph Congruence Profile | `shared` | `architecture` | `canonical` | `active` | `graph-maintainers` | `0.2` | [Reference Graph Congruence](../../architecture/graph_ontology/REFERENCE_GRAPH_CONGRUENCE.md) | `architecture-graph-crosswalk-001`<br>`standard-graph-001` |

## Active drafting notice

`architecture-pia-intake-subsystem-001`,
`architecture-pia-intake-phase2b-protection-001`,
`architecture-pia-protected-evidence-extraction-001`,
`architecture-pia-credential-library-001`,
`architecture-pia-intake-phase3a-review-001`, and
`architecture-pia-intake-phase3b-lookup-001` are in active development and
subject to change. Their governed state is `working` authority, `proposed`
status, and `formulation` lifecycle. Registration makes them discoverable and
traceable; it does not make their candidate contracts, agent roles, records,
vocabularies, or graph projections accepted or implemented.


