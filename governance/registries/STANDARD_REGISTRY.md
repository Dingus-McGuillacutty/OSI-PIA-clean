---
artifact_id: registry-standard-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.3"
owner: repository-governance
---

# Standard Registry

## Scope

This registry indexes cross-cutting conformance standards. Standards define
rules; architecture explains structure, and contracts define versioned
interfaces.

| Artifact ID | Name | Domain | Layer | Authority | Status | Owner | Version | Canonical Location | Depends On |
|---|---|---|---|---|---|---|---|---|---|
| `repo-conventions-001` | Repository Conventions | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.2` | [Repository Conventions](../Repository_Conventions.md) | `repo-architecture-001` |
| `standard-namespace-001` | Namespace Standard | `shared` | `standard` | `canonical` | `active` | `repository-governance` | `1.0` | [Namespace Standard](../policies/NAMESPACE_STANDARD.md) | `repo-conventions-001`<br>`adr-shared-0001`<br>`adr-shared-0002` |
| `standard-clean-release-001` | OSI-PIA Clean Release Standard | `shared` | `standard` | `canonical` | `active` | `repository-governance` | `1.0.0` | [Clean Release Standard](../CLEAN_RELEASE_STANDARD.md) | `governance-model-001`<br>`repo-conventions-001`<br>`software-governance-validator-001` |
| `standard-connector-001` | Connector Standard | `shared` | `standard` | `canonical` | `active` | `connector-maintainers` | `1.1` | [Connector Standard](../../connectors/Connector_Standard.md) | `standard-namespace-001`<br>`adr-shared-0001` |
| `standard-graph-001` | Graph Standards | `shared` | `standard` | `canonical` | `active` | `graph-maintainers` | `unversioned` | [Graph Standards](../../architecture/graph_standards/Graph_Standards.md) | `standard-namespace-001`<br>`ontology-shared-meta-001`<br>`contract-shared-data-graph-001` |
| `standard-component-001` | Component Standard | `implementation` | `standard` | `canonical` | `active` | `software-maintainers` | `unversioned` | [Component Standard](../../docs/architecture/assurance/component_standard.md) | `standard-namespace-001`<br>`architecture-assurance-001` |
| `standard-logic-chain-001` | Logic Chain Standard | `shared` | `standard` | `canonical` | `active` | `assurance-maintainers` | `unversioned` | [Logic Chain Standard](../../docs/architecture/assurance/logic_chain.md) | `principle-shared-engineering-001` |
| `standard-publication-001` | OSI Publication Standard | `shared` | `standard` | `canonical` | `active` | `publication-maintainers` | `0.1` | [Publication Standard](../../docs/publications/standards/OSI_Publication_Standard_v0.1.md) | `principle-osi-hippocratic-001`<br>`standard-logic-chain-001` |
