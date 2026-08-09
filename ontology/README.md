# OSI Ontology

## Purpose

This directory defines the concepts that OSI models and the
relationships between them.

The ontology creates a shared language for:

- research;
- documentation;
- data collection;
- graph database design;
- analysis;
- and software development.

## What belongs here

- entity definitions;
- relationship definitions;
- concept hierarchies;
- state definitions;
- transition definitions;
- naming standards;
- property definitions;
- ontology diagrams;
- ontology change records.

## Ontology rule

A term should not be added merely because it appears in a source
document.

It should be added when OSI needs to represent the concept
consistently across the system.

## Distinction from the glossary

The glossary provides readable explanations.

The ontology provides formal distinctions and relationships.

## Documents

| Document | Role |
|---|---|
| [`CORE CONCEPTS.md`](CORE%20CONCEPTS.md) | Current plain-language definitions of core OSI concepts |
| [`META_ONTOLOGY.md`](META_ONTOLOGY.md) | Working rules for ontology item kinds, status, governance, and technical projection |
| [`PIA_CAPABILITY_PATTERN_PROFILE.md`](PIA_CAPABILITY_PATTERN_PROFILE.md) | Working PIA behavioral capability vocabulary, report-level patterns, mapping boundaries, and finding states |
| [`graph_Ontology.md`](../architecture/graph_ontology/graph_Ontology.md) | Crosswalk from approved concepts and contracts to current and planned graph structures |
| [`ONTOLOGY_REGISTRY.md`](../governance/registries/ONTOLOGY_REGISTRY.md) | Governed inventory of shared, OSI, PIA, and implementation ontology identities and status |

## Authority boundary

The ontology is the authority for conceptual meaning. Data contracts define
accepted records, and the graph implements an approved projection of those
concepts. Neither a CSV field nor a Neo4j label silently creates a new
canonical concept.

The Ontology Registry is authoritative for inventory identity and recorded
status. It points to definition authorities; it does not replace them or make
an implemented graph label canonical.

The OSI theoretical foundation remains in
[`foundation/OSI_META_MODEL.md`](../foundation/OSI_META_MODEL.md). The
foundation explains the system model; this directory defines what the system
must represent consistently.

PIA behavioral interpretation is additionally constrained by the canonical
[PIA Measurement Doctrine](../governance/PIA_MEASUREMENT_DOCTRINE.md) and the
working
[PIA Behavioral Capability Inference Principle](../principles/PIA%20Behavioral%20Capability%20Inference%20Principle.md).
