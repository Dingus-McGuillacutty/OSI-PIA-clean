---
artifact_id: registry-catalog-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.25"
owner: repository-governance
---

# Repository Registries

## Purpose

The registries are the authoritative repository inventory for governed
artifacts. They tell human and machine readers what exists, where the canonical
artifact lives, what authority it carries, who stewards it, and what it
depends on.

Registries do not contain the architecture, ontology, contract, decision,
software, or research they index. Canonical meaning remains in the linked
artifact.

## Governing standard

Every registry conforms to the
[Registry Standard](REGISTRY_STANDARD.md). Registry rows use stable artifact
IDs and one common field order.

## Registry catalog

| Artifact ID | Name | Domain | Layer | Authority | Status | Owner | Version | Canonical Location | Depends On |
|---|---|---|---|---|---|---|---|---|---|
| `registry-catalog-001` | Repository Registry Catalog | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.25` | [Registry Catalog](README.md) | `standard-registry-001` |
| `standard-registry-001` | Registry Standard | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.1` | [Registry Standard](REGISTRY_STANDARD.md) | `repo-conventions-001` |
| `registry-adr-001` | ADR Registry | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.1` | [ADR Registry](ADR_REGISTRY.md) | `standard-registry-001` |
| `registry-architecture-001` | Architecture Registry | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.10` | [Architecture Registry](ARCHITECTURE_REGISTRY.md) | `standard-registry-001` |
| `registry-component-001` | Component Registry | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.26` | [Component Registry](COMPONENT_REGISTRY.md) | `standard-registry-001` |
| `registry-connector-001` | Connector Registry | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.1` | [Connector Registry](CONNECTOR_REGISTRY.md) | `standard-registry-001` |
| `registry-contract-001` | Contract Registry | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.8` | [Contract Registry](CONTRACT_REGISTRY.md) | `standard-registry-001` |
| `registry-graph-001` | Graph Registry | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.4` | [Graph Registry](GRAPH_REGISTRY.md) | `standard-registry-001` |
| `registry-ontology-001` | Ontology Registry | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.2` | [Ontology Registry](ONTOLOGY_REGISTRY.md) | `standard-registry-001` |
| `registry-principle-001` | Principle Registry | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.1` | [Principle Registry](PRINCIPLE_REGISTRY.md) | `standard-registry-001` |
| `registry-publication-001` | Publication Registry | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.6` | [Publication Registry](PUBLICATION_REGISTRY.md) | `standard-registry-001` |
| `registry-research-001` | Research Registry | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.3` | [Research Registry](RESEARCH_REGISTRY.md) | `standard-registry-001` |
| `registry-software-001` | Software Registry | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.8` | [Software Registry](SOFTWARE_REGISTRY.md) | `standard-registry-001` |
| `registry-standard-001` | Standard Registry | `shared` | `governance` | `canonical` | `active` | `repository-governance` | `1.3` | [Standard Registry](STANDARD_REGISTRY.md) | `standard-registry-001` |

The individual scopes are:

- ADR: architectural and governance decisions, including compatibility IDs;
- Architecture: repository, system, knowledge, assurance, and graph design;
- Component: independently testable implementation components;
- Connector: numbered external-source connectors;
- Contract: versioned data, import, validation, and connector obligations;
- Graph: reference graphs, executable graph packages, and validators;
- Ontology: conceptual models, vocabularies, and semantic dictionaries;
- Principle: foundational, engineering, ethical, and domain principles;
- Publication: governed public outputs and examples;
- Research: active methods, studies, and milestones;
- Software: packages, compatibility paths, and workflows;
- Standard: cross-cutting conformance rules.

## Reading order

Start with the Architecture, Principle, Ontology, and Contract registries to
understand intended meaning. Use the Graph, Component, Connector, and Software
registries to find implementations. Use the ADR registry to understand durable
choices and the Research registry to find work that has not necessarily been
promoted.

## Authority boundary

An entry records authority; it does not create it. Promotion, deprecation,
supersession, and retirement remain governed by the
[Knowledge Management Governance](../../docs/architecture/KNOWLEDGE_MANAGEMENT_GOVERNANCE.md)
framework and the
[Repository Conventions](../Repository_Conventions.md).

Unresolved overlap is recorded as `review-required`. Absence from a registry
means only that the inventory is incomplete; it does not by itself invalidate
an artifact.

## Maintenance

Update the appropriate registry in the same commit when a governed artifact is
added, moved, superseded, deprecated, retired, or changes dependencies. Changes
to the common schema belong in `REGISTRY_STANDARD.md`, not in an individual
registry.
