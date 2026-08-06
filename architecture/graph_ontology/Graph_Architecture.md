---
artifact_id: architecture-graph-platform-001
domain: shared
layer: architecture
authority: canonical
status: active
version: "1.0"
owner: graph-maintainers
---

# OSI-PIA Graph Architecture

## Purpose

This architecture defines how governed knowledge becomes an executable graph
without allowing database structure to redefine ontology, evidence, or human
judgment. It applies to the separate `osi-reference` and `pia-reference`
Neo4j databases and to future operational projections that conform to the
same rules.

## Architectural position

```text
Ethics, governance, and accepted decisions
                    |
Foundation, principles, and shared epistemology
                    |
        +-----------+-----------+
        |                       |
   OSI ontology             PIA ontology
        |                       |
        +-----------+-----------+
                    |
      shared graph architecture and standards
                    |
        +-----------+-----------+
        |                       |
   osi-reference           pia-reference
        |                       |
  OSI operations,          PIA packages,
 analysis, and views       analysis, and views
        +-----------+-----------+
                    |
       explicit cross-domain mappings only
```

OSI and PIA share epistemic, provenance, lifecycle, assurance, and graph
engineering rules. They do not share one domain ontology or one combined
reference database.

## Authority by layer

| Layer | Responsibility | Canonical authority |
|---|---|---|
| Governance | Ethical boundaries, domains, promotion, and change control | Governance documents and accepted ADRs |
| Ontology | Technology-independent concept and relationship meaning | Ontology sources and [Ontology Registry](../../governance/registries/ONTOLOGY_REGISTRY.md) |
| Architecture | Stable separation, mappings, projection rules, and database roles | This document, database specifications, and congruence profile |
| Contracts | Accepted records, fields, imports, and validation obligations | Versioned data, graph, import, and validation contracts |
| Graph implementation | Constraints, indexes, migrations, imports, and validators | Versioned files under [`graph/`](../../graph/README.md) |
| Live state | Applied data and operational history | Controlled database state and assurance evidence |

A lower layer implements a higher layer. It does not silently promote,
broaden, merge, or redefine it.

## Database topology

### `osi-reference`

The [OSI Reference Database](OSI_Reference_Database.md) is the governed OSI
projection for organizational-system structure, evidence, analysis, state,
change, and the bounded living-system concept inventory.

### `pia-reference`

The [PIA Reference Database](PIA_Reference_Database.md) is the governed PIA
projection for participant-controlled sources, experiences, evidence,
capabilities, and bounded analytical extensions.

### No shared domain database

Shared epistemology is represented by the same governed architecture and by
separately namespaced registry objects in each database. It does not require a
third Neo4j database. Database-local registry nodes are implementation
projections, not a replacement for the repository's canonical Ontology
Registry.

## Reference-database role

A reference database is a governed, executable semantic baseline. It holds:

- a database-scoped `Ontology` root;
- complete declarations for the bounded concept and relationship projection;
- lifecycle, knowledge-state, and confidence vocabularies;
- the applicable `ArchitectureProfile`;
- applied `GraphMigration` records;
- enough governed domain state to exercise the current projection and its
  validators.

A reference database is not:

- the source of conceptual authority;
- permission to treat every observed label as canonical;
- a universal production database;
- a public-data boundary;
- a reason to combine OSI and PIA interpretations;
- a substitute for contracts, consent, provenance, or assurance.

Live database files, credentials, and private records are not committed to the
repository. Any participant or organizational records present in a controlled
database remain subject to their original privacy, consent, correction,
purpose, and retention obligations.

## Shared projection rules

Both databases conform to the
[Reference Graph Congruence Profile](REFERENCE_GRAPH_CONGRUENCE.md):

- singular `PascalCase` labels;
- directional `UPPER_SNAKE_CASE` relationship types;
- `snake_case` properties;
- one stable identity for each canonical object;
- evidence and provenance kept separate from interpretation;
- reviewable metadata on analytical assertions;
- explicit unknowns rather than invented values;
- history for material corrections and supersession;
- minimum-necessary data and human accountability.

The [Namespace Standard](../../governance/policies/NAMESPACE_STANDARD.md)
governs the mapping between namespaced ontology identities and graph
representations. The same label in two databases does not establish identical
domain meaning.

## Graph governance objects

| Object | Role | Authority boundary |
|---|---|---|
| `Ontology` | Database-scoped root for the projected registry | Identifies a projection; does not define repository ontology |
| `Concept` | Declares graph label, identity, maturity, and boundaries | Mirrors governed definitions and status |
| `RelationshipDefinition` | Declares direction, endpoints, semantic class, and assertion requirements | Mirrors governed relationship meaning |
| `LifecycleState` | Represents the knowledge lifecycle | Shared vocabulary, separately projected |
| `KnowledgeState` | Represents proposed through retired status | Implementation of governance vocabulary |
| `ConfidenceModel` | Bounds confidence for a specified assertion | Never a score of person worth |
| `ArchitectureProfile` | Identifies shared graph rules and ethical boundaries | Conformance record |
| `GraphMigration` | Records an applied executable change | Operational provenance |

These objects form a database-local registry. The canonical inventory of
ontology identities and status remains
[`governance/registries/ONTOLOGY_REGISTRY.md`](../../governance/registries/ONTOLOGY_REGISTRY.md);
a parallel meta-ontology registry document must not be created.

## Data and interpretation flow

```text
Source and context
        |
        v
Evidence or observation
        |
        v
Reviewable analytical assertion
        |
        v
Assessment or state estimate
        |
        v
Human-accountable decision, representation, or learning
```

Each transition preserves the source identity, derivation or assertion basis,
time, confidence model where applicable, proposer, review state, and the
relevant privacy or consent boundary.

## Cross-domain use

Cross-domain analysis operates through an explicit mapping or contracted
product. It declares source and target ontology identities, purpose,
direction, semantic fit, provenance behavior, assurance, and human review.

It must not:

- copy a PIA assessment into OSI as an organizational fact;
- use OSI conditions to assign a fixed participant identity;
- remove source namespaces from a combined output;
- infer equivalence from identical labels or co-location;
- create automated employment, exclusion, or control decisions.

## Change and promotion

Graph change follows this order:

1. define or identify the governed ontology item;
2. record namespaced identity and status;
3. update the architecture crosswalk and contracts;
4. implement an idempotent migration or import;
5. run technical, provenance, ethical, and congruence validation;
6. expose unresolved knowledge as a review queue;
7. promote only through the knowledge-governance process.

Implementation maturity and ontology status remain distinct. A successful
migration can establish structural congruence without proving a construct or
promoting it to canonical ontology.

## Current executable baseline

The current baseline is version `0.2`:

| Target | Registry migration | Congruence migration | Validator |
|---|---|---|---|
| `osi-reference` | [`001_osi_reference_meta_ontology.cypher`](../../graph/migrations/001_osi_reference_meta_ontology.cypher) | [`003_osi_reference_architecture_congruence.cypher`](../../graph/migrations/003_osi_reference_architecture_congruence.cypher) | [`validate_osi_reference_architecture_congruence_v0.2.cypher`](../../graph/cypher/validation/validate_osi_reference_architecture_congruence_v0.2.cypher) |
| `pia-reference` | [`002_pia_reference_meta_ontology.cypher`](../../graph/migrations/002_pia_reference_meta_ontology.cypher) | [`004_pia_reference_architecture_congruence.cypher`](../../graph/migrations/004_pia_reference_architecture_congruence.cypher) | [`validate_pia_reference_architecture_congruence_v0.2.cypher`](../../graph/cypher/validation/validate_pia_reference_architecture_congruence_v0.2.cypher) |

Database-specific validation results and remaining review queues are recorded
in the two reference-database specifications.
