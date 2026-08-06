# OSI/PIA Graph

## Purpose

This directory contains shared graph implementation mechanics and the
database-specific migrations, imports, and validators for the separate OSI and
PIA graph projections. The graphs represent participants and organizations as
connected systems rather than isolated records.

Neo4j is the current implementation, but the conceptual model remains
database-independent.

## Authority boundary

The graph implements an approved projection of the ontology; it does not
define conceptual meaning.

- [`ontology/`](../ontology/README.md) defines concepts.
- The shared
  [`Graph Architecture`](../architecture/graph_ontology/Graph_Architecture.md)
  defines database roles, layering, and projection boundaries.
- The
  [`OSI Reference Database`](../architecture/graph_ontology/OSI_Reference_Database.md)
  and
  [`PIA Reference Database`](../architecture/graph_ontology/PIA_Reference_Database.md)
  documents define the two database-specific acceptance boundaries.
- The
  [`Graph Ontology Crosswalk`](../architecture/graph_ontology/graph_Ontology.md)
  records current, experimental, and planned projections.
- [`Graph Standards`](../architecture/graph_standards/Graph_Standards.md)
  define cross-cutting engineering rules.
- [`docs/contracts/`](../docs/contracts/) define versioned data, graph, import,
  and validation behavior.

## Current structure

```text
graph/
├── schema/       schema statements and descriptive catalogues
├── migrations/   ordered, executable graph changes
├── cypher/
│   ├── imports/  generic participant package import
│   └── validation/
├── imports/      local-only mount point; no participant files are tracked
└── data/         graph-oriented dictionaries and data guidance
```

The [`migrations/`](migrations/README.md) directory contains ordered executable
changes. Planned directories such as `queries/`, `diagrams/`, and `seed/`
should be created only when their first governed artifact is ready.

## Current participant projection

The contracted v0.1 graph preserves this evidence chain:

```text
Participant -[HAS_SOURCE]-> Source -[CONTAINS]-> Evidence
    |                                            |
    +-[HAS_EXPERIENCE]-> Experience <-[OCCURRED_IN]-+
                                                 |
                                                 +-[SUPPORTS]-> Capability
```

The exact direction and semantics of the relationships are documented in the
[Graph Ontology Crosswalk](../architecture/graph_ontology/graph_Ontology.md)
and
[Data and Graph Contract](../docs/contracts/OSI_PIA_Data_Graph_Contract_v0.1.md).

## Schema

[`schema/`](schema/README.md) contains both executable Cypher and early
descriptive catalogues. Its README identifies the status of each file so that
catalogue entries are not mistaken for deployed or assured schema.

The first versioned migrations add separate working meta-ontology registries
to `osi-reference` and `pia-reference` without merging their ontologies. The
v0.2 congruence migrations connect both registries to one shared architecture
profile while preserving database-specific concepts, contracts, and maturity.

The
[`OSI/PIA Reference Graph Congruence Profile`](../architecture/graph_ontology/REFERENCE_GRAPH_CONGRUENCE.md)
records canonical labels, relationship semantic classes, compatibility
corrections, evidence boundaries, and the distinction between structural
congruence and remaining review work.

The working
[`PIA Capability and Pattern Profile`](../ontology/PIA_CAPABILITY_PATTERN_PROFILE.md)
adds a proposed behavior-grounded vocabulary for broader experience mapping.
Its eight Patterns organize report output; specific Capabilities remain the
only targets of Evidence-to-Capability assertions.

## Reference databases

`osi-reference` and `pia-reference` are separate governed projections. They
share architecture, engineering, provenance, lifecycle, confidence, and
assurance conventions but retain distinct ontology namespaces and domain
interpretations. No live database state or private record is stored in this
repository.

Database-local `Concept` and `RelationshipDefinition` nodes implement the
bounded projection. The repository
[Ontology Registry](../governance/registries/ONTOLOGY_REGISTRY.md) remains the
canonical identity and status index.

## Import and validation

- [`cypher/imports/import_participant_package_v0.1.cypher`](cypher/imports/import_participant_package_v0.1.cypher)
  is the generic contract-driven participant import script.
- [`cypher/validation/validate_participant_package_v0.1.cypher`](cypher/validation/validate_participant_package_v0.1.cypher)
  performs post-import graph checks.
- [`migrations/005_pia_behavioral_capability_profile.cypher`](migrations/005_pia_behavioral_capability_profile.cypher)
  installs the proposed capability and pattern vocabulary without participant
  records.
- [`cypher/imports/import_capability_evidence_mappings_v0.2.cypher`](cypher/imports/import_capability_evidence_mappings_v0.2.cypher)
  imports bounded behavioral and educational assertions while keeping
  knowledge exposure separate from demonstrated application.
- [`cypher/validation/validate_pia_capability_evidence_profile_v0.2.cypher`](cypher/validation/validate_pia_capability_evidence_profile_v0.2.cypher)
  validates that working profile and any mappings created under it.
- The v0.2 OSI and PIA congruence validators verify the shared architecture
  profile, canonical labels and relationship meanings, assertion metadata,
  provenance, registry completeness, and explicit legacy review queues.
- Participant-specific imports are supplied from private local sources and
  must not be tracked. See the repository [data boundary](../data/README.md);
  local imports must not be treated as the generic contract.

## Objectives

The graph should make it possible to understand:

- relationships;
- organizational topology and flow;
- capability movement and utilization;
- trust and predictability conditions;
- state transitions;
- complete evidence lineage.

## Implementation philosophy

- The ontology drives the graph.
- Evidence remains separate from interpretation.
- Every canonical object has stable identity and provenance.
- Imports are idempotent and auditable.
- Experimental labels and relationships are not described as canonical.
- Private operational datasets and live database files do not belong in Git.

## Long-term vision

The graph should become a navigable, temporally honest representation of
organizational state. It exists to support understanding, diagnosis, repair,
and learning rather than surveillance, static organization charts, or
automated judgment.
