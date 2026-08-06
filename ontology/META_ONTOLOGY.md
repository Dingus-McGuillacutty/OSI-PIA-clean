---
artifact_id: ontology-shared-meta-001
domain: shared
layer: ontology
authority: working
status: active
version: "0.2"
owner: ontology-maintainers
---

# OSI-PIA Ontology Meta-Model

**Knowledge state:** Formulation

**Scope:** Rules for defining, governing, and projecting OSI/PIA ontology items

**Implementation status:** Working registry implemented in `osi-reference`;
registry presence does not imply canonical status

## Purpose

This document defines the structure of the OSI/PIA ontology rather than
another set of organizational concepts. It provides a common way to describe
concepts, relationships, properties, states, assertions, and constraints
before they are represented in data contracts or a graph database.

The meta-ontology prevents four different things from being treated as if they
were interchangeable:

1. a theoretical construct in the OSI foundation;
2. a concept that OSI/PIA needs to represent consistently;
3. a record or field defined by a data contract;
4. a label, relationship, property, constraint, or index implemented in Neo4j.

## Authority boundaries

| Layer | Question answered | Canonical location |
|---|---|---|
| Foundation | What system model explains OSI? | `foundation/` |
| Principles | What commitments constrain the model? | `principles/` |
| Ontology | What concepts and relationships must be represented? | `ontology/` |
| Meta-ontology | What kinds of ontology items exist, and how are they governed? | This document |
| Data contracts | What records and fields may enter the system? | `data/contracts/` and `docs/contracts/` |
| Graph ontology crosswalk | How do approved concepts project into the graph? | `architecture/graph_ontology/graph_Ontology.md` |
| Graph implementation | What Neo4j structures and migrations are executable? | `graph/` |
| Analysis | What interpretations may be made from assured graph data? | `analysis/` |

No downstream layer may silently redefine an upstream concept. A graph label
does not make a concept canonical, and a conceptual term does not imply that a
graph label has been implemented.

## Ontology item kinds

Every promoted ontology item should declare one primary kind.

| Kind | Meaning | Example |
|---|---|---|
| Concept | A defined idea needed across the system | Organizational Health |
| Entity type | A thing with stable identity | Participant, Source, Capability |
| Relationship type | A typed connection with defined direction and meaning | HAS_SOURCE, OCCURRED_IN |
| Property definition | A named characteristic with a defined value domain | `consent_status` |
| Event type | An occurrence associated with time and participants | Promotion, disruption |
| State type | A condition at a defined time | Vacancy, review state |
| Transition type | A change between states | Role transition |
| Assertion type | A reviewable interpretation supported by evidence | Evidence supports Capability |
| Constraint | A conceptual rule that valid representations must preserve | Evidence requires Source provenance |

These kinds are semantic categories. They do not prescribe whether an item is
implemented as a node, relationship, property, constraint, or derived view.

## Required declaration

Before an ontology item is treated as canonical, its declaration should make
the following information recoverable:

- stable ontology identifier;
- canonical name and plain-language definition;
- ontology item kind;
- scope and intended use;
- distinction from neighboring concepts;
- lifecycle state and ontology status;
- provenance or decision references;
- allowed or required relationships;
- evidence and interpretation boundary;
- temporal meaning, when relevant;
- privacy, consent, and ethical constraints;
- version and compatibility notes;
- graph or data mappings, if any;
- responsible steward.

Existing documents may be brought into this structure incrementally. This
document does not retroactively claim that every current concept already has a
complete declaration.

## Independent status dimensions

Three status dimensions must remain separate.

### Knowledge lifecycle state

Where the underlying knowledge sits in the governed lifecycle:

```text
Observation -> Exploration -> Formulation -> Congruence
    -> Validation -> Promotion -> Stewardship
```

### Ontology status

Whether the item is proposed, working, canonical, deprecated, or retired as
part of the shared conceptual model.

### Implementation status

Whether the item is unmapped, documented, contracted, implemented, or assured
in a particular technical system.

An ontology item can be canonical but not yet implemented. An implemented
label can also be experimental and therefore not canonical. Domain-specific
record statuses, such as participant consent or assessment review status, are
separate from all three dimensions.

## Representation rules

### Identity

An entity type must define the basis of stable identity before import or graph
projection. Human-readable names must not substitute for stable identifiers.

### Direction and meaning

A relationship type must define its start type, end type, direction, meaning,
cardinality expectations when known, and whether it records a source fact or
an interpretation.

### Assertions

Interpretive links must remain reviewable. When a relationship expresses an
assertion, it should preserve the basis, proposer, confidence or uncertainty,
review status, and relevant timestamps. The current Evidence-to-Capability
`SUPPORTS` mapping is an assertion, not a direct fact about a person.

When a capability assertion is inferred from behavior rather than stated
explicitly, it must also preserve the behavioral basis, inference level,
contextual scope, source-independence limits, and a negative boundary naming
what the evidence does not establish. A title, credential, or self-label is
context rather than sufficient behavioral evidence. Failure to establish a
valid mapping remains insufficient evidence for the scoped claim; it is not
evidence that a person lacks the capability.

### Evidence boundary

Source, observation, evidence, indicator, construct, assessment,
interpretation, and possible action must remain distinguishable. No projection
may overwrite source-grounded evidence with an analytical conclusion.

### Time

State, transition, and event items must define how time is represented,
including unknown or partial time. A current value must not erase prior state
when history is analytically or ethically significant.

### Provenance

Every implemented object must be traceable to an accepted source record,
derivation rule, ontology declaration, or operational event. Missing
provenance must remain visible rather than being filled by inference.

### Human boundary

Ontology and graph structures must support system diagnosis and participant
understanding without enabling covert surveillance, person scoring, automated
punishment, or decontextualized claims.

## Projection path

An ontology addition should move through explicit mappings:

```text
Foundation or research formulation
    -> ontology declaration
    -> data and graph contract
    -> graph ontology crosswalk
    -> executable schema or migration
    -> import and validation behavior
    -> assurance evidence
```

Each arrow is a governed mapping, not an equivalence. A concept may stop at
any layer until evidence, design, and implementation are ready.

## Change control

An additive ontology change should include:

1. a declaration containing the required metadata;
2. a comparison with existing concepts to prevent synonyms or duplication;
3. updated crosswalks and contracts where implementation is intended;
4. validation and migration work before an implementation claim;
5. a changelog entry when the change becomes canonical or operational.

A breaking change to identity, meaning, relationship direction, evidence
semantics, or interpretation boundaries requires an ADR, compatibility
statement, migration plan, and explicit supersession path.

## Current application

The first application of this meta-model is the participant evidence graph
documented in
[`architecture/graph_ontology/graph_Ontology.md`](../architecture/graph_ontology/graph_Ontology.md).
That crosswalk distinguishes the contracted participant graph, experimental
assessment extensions, operational import objects, and the broader conceptual
OSI model.

The additive
[`001_osi_reference_meta_ontology.cypher`](../graph/migrations/001_osi_reference_meta_ontology.cypher)
migration implements a working registry in the `osi-reference` database. It
adds `Ontology`, `Concept`, `RelationshipDefinition`, `LifecycleState`,
`KnowledgeState`, and `ConfidenceModel` structures, then registers the graph
labels and relationship types observed when the migration is applied. The
registry records implementation; it does not promote those observed objects
to canonical ontology status.

The parallel
[`002_pia_reference_meta_ontology.cypher`](../graph/migrations/002_pia_reference_meta_ontology.cypher)
migration applies the same governance vocabulary to a separately namespaced
registry in `pia-reference`. OSI and PIA therefore share lifecycle, status,
assertion-governance, and architecture semantics while preserving distinct
concept and relationship catalogs. Confidence models are scoped to their
assertion type: OSI currently uses qualitative analytical confidence, while
the contracted PIA Evidence-to-Capability assertion uses bounded numeric
confidence.

The
[`OSI/PIA Reference Graph Congruence Profile`](../architecture/graph_ontology/REFERENCE_GRAPH_CONGRUENCE.md)
and migrations `003` and `004` complete declarations for the bounded core,
add an `ArchitectureProfile`, classify governed relationships, and preserve
legacy gaps as explicit review queues. Core projection declarations may be at
Congruence while the broader registry and this meta-model remain at
Formulation.

## Promotion note

This document is intentionally marked as Formulation. Its working registry may
be used for discovery and governance, but the metadata vocabulary should pass
congruence and governance review before becoming a machine-enforced ontology
contract.
