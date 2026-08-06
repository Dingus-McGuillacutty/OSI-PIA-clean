---
artifact_id: graph-osi-reference-001
domain: osi
layer: graph
authority: canonical
status: active
version: "0.2"
owner: graph-maintainers
---

# OSI Reference Database

## Purpose

`osi-reference` is the governed Neo4j projection of the bounded OSI
organizational-system architecture. It aligns organizational structure,
evidence lineage, analytical assertions, state estimation, decision support,
and the planned living-system concepts without manufacturing observations or
assessments for concepts that lack approved evidence and derivation contracts.

This specification defines the database role and acceptance boundary. It
inherits the shared [Graph Architecture](Graph_Architecture.md) and
[Reference Graph Congruence Profile](REFERENCE_GRAPH_CONGRUENCE.md).

## Authority boundary

The database implements:

- shared epistemic and lifecycle governance;
- the OSI conceptual authorities indexed in the
  [Ontology Registry](../../governance/registries/ONTOLOGY_REGISTRY.md);
- graph mappings recorded in the
  [Graph Ontology Crosswalk](graph_Ontology.md);
- approved constraints, migrations, and validators.

Observed graph state does not define ontology. A label found in the database
is canonical only to the extent established by its registered definition,
status, architecture mapping, contract, and assurance evidence.

## Bounded projection

### Organizational structure

```text
Person -[:HELD_POSITION]-> Position
Position -[:POSITION_AT]-> Organization
Position -[:POSITION_IN]-> OrganizationalUnit
OrganizationalUnit -[:PART_OF]-> Organization
```

`Department` is an additive specialization of `OrganizationalUnit`.
`StaffingEvent` is an additive specialization of `Event`. The general and
specialized concepts remain distinguishable.

### Evidence and analysis

```text
Source <-[:COLLECTED_FROM]- Collection -[:PRODUCED]-> Evidence
Evidence -> Observation
Observation -> Hypothesis / Assessment
Assessment -> Indicator / StateEstimate / Prediction
StateEstimate -> DecisionSpace
DecisionSpace -> human-accountable Decision and Intervention
Intervention -> Outcome
Validation -> PatternMemory
```

The diagram expresses architectural flow, not permission to create every
connection automatically. Analytical relationships retain stable assertion
identity, basis, proposer, review state, and time. Source and collection
provenance remain independently traversable.

### Living-system inventory

| Maturity | Concepts |
|---|---|
| Implemented bounded core | Organization, Person, Position, OrganizationalUnit, Department, Capability, Source, Collection, Evidence, Observation, Indicator, Assessment, StateEstimate, Event, StaffingEvent, Outcome, Principle, Invariant |
| Declared planned projection | Role, Team, CapabilityCapital, EffectiveCapability, Trust, Predictability, OrganizationalCapital, OrganizationalEnergy, Flow, Topology, FieldCondition, Construct, State, StateTransition, OrganizationalHealth, Vacancy |
| Inventory-only analytical objects | DecisionSpace, Decision, Intervention, Validation, PatternMemory and observed legacy extensions pending classification |

Planned registration makes the written architecture visible. It does not
create empirical instances or establish a validated measurement model.

## Identity and namespace

The semantic identities use `osi:`. Graph labels remain singular
`PascalCase`; relationship types remain directional `UPPER_SNAKE_CASE`.
Database registry identities such as
`concept:osi-reference:Organization` identify projected registry nodes and
map to canonical ontology identities such as `osi:organization`.

Stable domain identity properties remain defined by the registered concept,
contract, or schema. Names, titles, and current organizational placement are
not stable identifiers.

## Executable baseline

| Responsibility | Governed artifact |
|---|---|
| Meta-ontology registry | [`001_osi_reference_meta_ontology.cypher`](../../graph/migrations/001_osi_reference_meta_ontology.cypher) |
| Architecture alignment | [`003_osi_reference_architecture_congruence.cypher`](../../graph/migrations/003_osi_reference_architecture_congruence.cypher) |
| Registry validation | [`validate_osi_reference_meta_ontology_v0.1.cypher`](../../graph/cypher/validation/validate_osi_reference_meta_ontology_v0.1.cypher) |
| Congruence validation | [`validate_osi_reference_architecture_congruence_v0.2.cypher`](../../graph/cypher/validation/validate_osi_reference_architecture_congruence_v0.2.cypher) |

Migrations are rerunnable. The v0.2 alignment is additive: it adds
specialization labels, provenance, canonical metadata, registry declarations,
and the shared architecture profile without instantiating theoretical
constructs.

## Acceptance criteria

The v0.2 validator requires:

- one matching `ArchitectureProfile` and one applied migration record;
- every `Department` also labeled `OrganizationalUnit`;
- every `StaffingEvent` also labeled `Event`;
- every Evidence node connected to Collection provenance;
- complete, unique metadata for governed analytical assertions;
- complete bounded-core concept and relationship declarations;
- no observed unregistered labels or relationship types.

A passing result establishes structural congruence with this profile. It does
not validate every legacy assertion, confirm causal interpretation, or
promote planned constructs.

## Validated snapshot

The following diagnostic snapshot was captured on 2026-07-23 after applying
the v0.2 congruence migration:

| Measure | Observed |
|---|---:|
| Nodes | 407 |
| Relationships | 692 |
| `Concept` registry nodes | 81 |
| `RelationshipDefinition` registry nodes | 110 |
| Applied v0.2 migration records | 1 |
| Architecture profiles | 1 |
| `Department` / `OrganizationalUnit` alignment | 17 / 17 |
| `StaffingEvent` / `Event` alignment | 10 / 10 |
| Evidence without Collection provenance | 0 |
| Analytical assertions with complete metadata | 60 / 60 |

This is a point-in-time operational observation, not a schema contract or a
committed database fixture. Re-run the validators against the target database
for current assurance.

## Remaining review queues

Structural alignment is complete for the bounded projection. Semantic work
remains:

- classify inventory-only legacy relationship types;
- review legacy assertion basis and review states;
- approve evidence, indicator, derivation, temporal, and validation contracts
  before instantiating Trust, Predictability, Flow, OrganizationalHealth, or
  related constructs;
- distinguish organizational observation from inference and intervention
  authorization;
- maintain privacy, purpose, access, and correction controls for controlled
  organizational records.

Review queues are knowledge, not errors to hide. Unknown or provisional state
must remain explicit until reviewed.

## Ethical boundary

The database supports human understanding, diagnosis, repair, and learning.
It must not be used as a covert surveillance graph, an automatic worker score,
a sole-cause model of organizational outcomes, or an autonomous decision
system. People remain more than their represented positions, evidence, or
modeled relationships.
