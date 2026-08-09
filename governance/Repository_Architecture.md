---
artifact_id: repo-architecture-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.1"
owner: repository-governance
---

# Repository Architecture

## Purpose

This document governs the structure of the OSI-PIA repository. It defines
domain boundaries, architectural layers, dependency direction, and the
location of authoritative repository metadata.

It does not replace the domain architecture in
[`architecture/`](../architecture/Architecture/Architecture.md), the knowledge
governance framework in
[`docs/architecture/`](../docs/architecture/KNOWLEDGE_MANAGEMENT_GOVERNANCE.md),
or the conceptual ontology in [`ontology/`](../ontology/README.md). It states
how those authorities coexist in one repository.

The proposed [OSI-PIA Governance Model](GOVERNANCE_MODEL.md) consolidates these
boundaries into a constitutional governance layer. Until that proposal is
reviewed and promoted, the current canonical authorities retain their
existing scopes.

## Architectural model

```text
                         Shared governance
                                |
          Shared foundation, epistemology, assurance, and contracts
                                |
                 +--------------+--------------+
                 |                             |
              OSI domain                   PIA domain
                 |                             |
       organizational models          participant evidence models
                 |                             |
                 +--------------+--------------+
                                |
                  explicit cross-domain contracts
                                |
                 implementations and applications
```

OSI and PIA are peer domain implementations of a shared foundation. Neither
domain is a subset, extension, data source, or subordinate component of the
other.

Shared artifacts may constrain or support both domains. A domain artifact may
depend on shared artifacts. A dependency between OSI and PIA must be explicit,
purpose-bound, provenance-preserving, and represented by a contract or
recorded decision.

## Domain model

Every governed artifact declares one domain.

| Domain | Meaning |
|---|---|
| `shared` | Applies across OSI and PIA without assigning either domain authority over the other |
| `osi` | Defines organizational-system concepts, evidence, graph projections, analysis, or outputs |
| `pia` | Defines participant-level evidence, capability, assessment, graph projections, analysis, or outputs |
| `implementation` | Provides technical machinery without defining OSI or PIA domain meaning |
| `test` | Provides fixtures and verification behavior only |

An artifact that serves both OSI and PIA is `shared`; it is not assigned a
combined or ambiguous domain. Domain scope describes architectural authority,
not simply the directory in which a file currently resides.

## Repository layers and ownership

| Location | Architectural responsibility | Content authority |
|---|---|---|
| `governance/` | Ethical, knowledge, repository, and change-control boundaries | Governance rules and repository registries |
| `foundation/` | Durable theoretical system models | Foundational OSI theory |
| `principles/` | Enduring conceptual and engineering propositions | Project principles |
| `ontology/` | Technology-independent concepts and meta-ontology | Conceptual meaning |
| `architecture/` | Stable domain and technical structures | Architectural design and graph projection |
| `docs/contracts/` and `data/contracts/` | Versioned interoperability obligations | Accepted record and behavior contracts |
| `assurance/` and `docs/architecture/assurance/` | Assurance model, findings, and review requirements | Assurance rules and reference descriptions |
| `graph/` | Executable schemas, migrations, imports, validation, and graph guidance | Graph implementation |
| `data/` | Controlled examples, templates, and participant-package structures | Data packages subject to privacy rules |
| `analysis/` | Repeatable analytical and diagnostic artifacts | Domain analysis |
| `connectors/` | Numbered source adapters and their manifests | Connector implementation and contracts |
| `software/` | Reusable platform implementation | Qualified software components |
| `tests/` | Automated regression and integrity verification | Test behavior |
| `active-research/` and `docs/research-standards/` | Exploratory work and validation material | Working research |
| `docs/publications/` | Publication standards and examples | Public-output guidance |
| `decisions/` | Scoped shared, OSI, PIA, and implementation decision records | Decision rationale |

Prior ADR collections have been normalized under `decisions/`. Remaining
compatibility paths and migrations are governed by
[`Repository_Migration_Plan.md`](Repository_Migration_Plan.md).

## Authority order

When two artifacts appear to overlap, resolve authority in this order:

1. Governance constrains all other material.
2. A recorded accepted decision explains why a durable choice was made.
3. Foundation and principles constrain domain meaning.
4. Ontology defines technology-independent concepts.
5. Architecture defines stable structures and projections.
6. Versioned contracts define accepted interfaces and records.
7. Executable schema, migrations, and software implement those definitions.
8. Analysis and publications consume governed outputs.
9. Research may challenge any layer but does not silently supersede it.

The repository registries identify the canonical location, authority, status,
owner, version, and dependencies of governed artifacts. A registry entry does
not promote an artifact or replace its contents.

## Dependency rules

- Governance may constrain every layer.
- Domain ontology depends on shared epistemology and governance.
- Graph implementation depends on ontology, architecture, and contracts.
- Imports depend on contracts, schema, provenance, consent, and assurance.
- Analysis depends on assured data or graph structures.
- Publications depend on traceable analysis and publication governance.
- Software must not create domain meaning that is absent from a governed
  ontology, architecture, contract, or decision.
- Cross-domain use requires an explicit mapping and declared purpose.

Dependencies should point inward toward more stable authority. A lower layer
must not redefine an upstream artifact through implementation convenience.

## Canonical and compatibility locations

Each governed artifact has one canonical location. Compatibility copies,
generated outputs, and historical paths must point to that location and must
not evolve independently.

The prior ADR overlap and root-level Connector 001 copies have been resolved
through governed migrations. Remaining compatibility paths retain their
registered authority and must not evolve into parallel canonical locations.

## Repository governance

The authoritative repository-governance package is:

- this architecture;
- [`Repository_Conventions.md`](Repository_Conventions.md);
- [`Repository_Migration_Plan.md`](Repository_Migration_Plan.md);
- the [governed registries](registries/README.md) under
  `governance/registries/`.

The proposed [`GOVERNANCE_MODEL.md`](GOVERNANCE_MODEL.md) is the candidate
constitutional layer for this package. It becomes authoritative only through
explicit promotion.

Changes that alter domain boundaries, canonical locations, identifier schemes,
or dependency direction require an ADR or an equivalent explicit governance
decision before migration.


