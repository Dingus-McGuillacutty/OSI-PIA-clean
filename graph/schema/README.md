# Graph Schema

## Purpose

This directory contains Neo4j schema statements and descriptive catalogues.
The files reflect more than one stage of the graph's development and must not
all be treated as executable, canonical, or assured.

Conceptual definitions reside in [`ontology/`](../../ontology/README.md).
Current participant mappings reside in the
[Data and Graph Contract](../../docs/contracts/OSI_PIA_Data_Graph_Contract_v0.1.md).
Projection status is summarized in the
[Graph Ontology Crosswalk](../../architecture/graph_ontology/graph_Ontology.md).

## Files and maturity

| File | Actual role | Execution status |
|---|---|---|
| `000_constraints.cypher` | Historical pointer documenting why the former `id` constraints were superseded | Non-executable; use migrations |
| `010_INDEXES.cypher` | Historical pointer replacing the former duplicated relationship catalogue | Non-executable; use migrations |
| `020_NODES.cypher` | Congruent OSI/PIA label catalogue, including specialization labels | Descriptive; bare patterns are not executable schema |
| `030_RELATIONSHIPS.cypher` | Congruent relationship catalogue for the participant spine, assessment layer, OSI analysis, and graph governance | Descriptive; relationship definitions and migrations are authoritative |
| `040_assessment.cypher` | Assessment uniqueness constraint and indexes | Executable experimental extension |

File numbering records intended application order only after each file is
promoted to executable schema. It is not currently a claim that the whole
directory can be run as a migration.

Ordered executable changes live in [`graph/migrations/`](../migrations/README.md).
The first migrations add separate working `osi-reference` and `pia-reference`
meta-ontology registries. The v0.2 congruence migrations align the bounded
core projection, property names, relationship meanings, and shared
architecture profile while preserving separate registries and databases.

## Current contracted participant schema

The working v0.1 contract requires stable identities for:

- `Participant.participant_id`;
- `Source.source_id`;
- `Experience.experience_id`;
- `Evidence.evidence_id`;
- `Capability.capability_id`.

It also contracts `HAS_SOURCE`, `HAS_EXPERIENCE`, `CONTAINS`,
`OCCURRED_IN`, and the reviewable `SUPPORTS` assertion. The full properties,
enums, and validation rules remain in the versioned contract.

These identities are created by the generic participant importer and preserved
by the versioned PIA congruence migration. Executable database changes belong
in `graph/migrations/`, not in this descriptive directory.

## Promotion requirements

Before a schema file is described as canonical or included in an automated
migration, it must:

1. map to an approved ontology item and contract;
2. contain valid, idempotent Neo4j Cypher;
3. declare compatibility and application order;
4. include corresponding import and validation behavior;
5. preserve provenance, interpretation, privacy, and consent boundaries;
6. pass Graph Assurance when that capability is available.

## Design principles

- One contracted stable identifier per canonical entity.
- Singular `PascalCase` labels, `UPPER_SNAKE_CASE` relationships, and
  `snake_case` properties.
- Schema files do not define conceptual meaning.
- Catalogue presence does not imply implementation.
- Schema changes are versioned and paired with validation.

## Related implementation

- [Generic participant import](../cypher/imports/import_participant_package_v0.1.cypher)
- [Post-import validation](../cypher/validation/validate_participant_package_v0.1.cypher)
- [Graph Standards](../../architecture/graph_standards/Graph_Standards.md)
