---
artifact_id: graph-pia-reference-001
domain: pia
layer: graph
authority: canonical
status: active
version: "0.2"
owner: graph-maintainers
---

# PIA Reference Database

## Purpose

`pia-reference` is the governed Neo4j projection of participant-controlled
sources, experiences, evidence, capabilities, and bounded analytical
extensions. It preserves the distinction between what a source states, what
evidence supports, and what a revisable assessment proposes.

This specification defines the database role and acceptance boundary. It
inherits the shared [Graph Architecture](Graph_Architecture.md), the
[Reference Graph Congruence Profile](REFERENCE_GRAPH_CONGRUENCE.md), and the
versioned participant data and graph contracts.

## Authority boundary

The database implements:

- shared epistemic, provenance, lifecycle, and assurance governance;
- PIA concepts indexed in the
  [Ontology Registry](../../governance/registries/ONTOLOGY_REGISTRY.md);
- the contracted participant evidence spine;
- experimental analytical objects whose status remains explicit;
- approved constraints, imports, migrations, and validators.

The participant is not reduced to the graph. Absence of evidence is not
absence of capability, an assessment is not a permanent identity, and
database implementation does not promote a working concept.

## Contracted evidence spine

```text
Participant -[:HAS_SOURCE]-> Source -[:CONTAINS]-> Evidence
Participant -[:HAS_EXPERIENCE]-> Experience
Evidence -[:OCCURRED_IN]-> Experience
Evidence -[:SUPPORTS]-> Capability
```

`CONTAINS` is reserved for the provenance relationship from Source to
Evidence. `OCCURRED_IN` remains optional when a source does not establish the
experience context.

`SUPPORTS` is a reviewable analytical assertion, not a source fact. It carries
mapping and assertion identity, numeric confidence bounded from `0.00` to
`1.00`, basis, proposer, review state, time, and the human-review boundary.
Confidence applies to one evidence-to-capability mapping and never to the
participant's worth or potential.

## Bounded analytical extension

```text
Participant -[:HAS_ASSESSMENT]-> Assessment
Assessment -[:EVALUATES]-> Pattern
Assessment -[:USES_CAPABILITY]-> Capability
Assessment -[:BASED_ON]-> Evidence
Assessment -[:SUPPORTS_IDENTITY]-> IdentityHypothesis
```

`Assessment`, `Pattern`, `Observation`, `IdentityHypothesis`, and
`Representation` remain working or experimental unless separately promoted.
An `IdentityHypothesis` is revisable, participant-reviewable, and unsuitable
as a fixed classification.

## Working behavioral capability extension

The
[PIA Capability and Pattern Profile](../../ontology/PIA_CAPABILITY_PATTERN_PROFILE.md)
defines a proposed vocabulary for recognizing specific capabilities across
broader professional, technical, service, educational, and project
experiences.

Under this extension:

- `Teamwork` and `Leadership` are report-level ideas rather than direct
  Capability targets;
- evidence maps to specific behaviors such as stakeholder coordination,
  handoff management, technical leadership, change leadership, or user
  enablement;
- every mapping declares whether it is directly demonstrated, strongly
  inferred, or contextually suggested;
- every mapping states what the evidence does not prove and the context to
  which it is limited; and
- insufficient evidence remains an evidence condition, not a conclusion that
  the participant lacks a capability.

The eight working Pattern nodes organize output across systems, projects,
analysis, communication, collaboration, leadership, risk, and learning. They
are analytical groupings, not scores or fixed identity dimensions.

## Canonical relationship corrections

| Prior representation | Canonical representation | Boundary restored |
|---|---|---|
| `Assessment-[:USES]->Capability` | `Assessment-[:USES_CAPABILITY]->Capability` | Distinguishes analytical reference from generic use |
| `Source-[:CONTAINS]->Experience` | `Source-[:DESCRIBES]->Experience` | Reserves `CONTAINS` for Source-to-Evidence provenance |

Migration retains the prior property map and
`migrated_from_relationship_type` for traceability. The legacy relationship
types are deprecated and must not be recreated by new imports.

## Identity and namespace

The semantic identities use `pia:`. Graph labels remain singular
`PascalCase`; relationship types remain directional `UPPER_SNAKE_CASE`.
Database registry identities such as
`concept:pia-reference:Assessment` identify projected registry nodes and map
to ontology identities such as `pia:assessment`.

Participant, source, experience, evidence, capability, assessment, and mapping
identities remain separate. A display name, job title, source filename, or
assessment label is not a stable participant identity.

## Executable baseline

| Responsibility | Governed artifact |
|---|---|
| Generic package import | [`import_participant_package_v0.1.cypher`](../../graph/cypher/imports/import_participant_package_v0.1.cypher) |
| Package validation | [`validate_participant_package_v0.1.cypher`](../../graph/cypher/validation/validate_participant_package_v0.1.cypher) |
| Meta-ontology registry | [`002_pia_reference_meta_ontology.cypher`](../../graph/migrations/002_pia_reference_meta_ontology.cypher) |
| Architecture alignment | [`004_pia_reference_architecture_congruence.cypher`](../../graph/migrations/004_pia_reference_architecture_congruence.cypher) |
| Capability evidence vocabulary | [`005_pia_behavioral_capability_profile.cypher`](../../graph/migrations/005_pia_behavioral_capability_profile.cypher) |
| Capability evidence import | [`import_capability_evidence_mappings_v0.2.cypher`](../../graph/cypher/imports/import_capability_evidence_mappings_v0.2.cypher) |
| Registry validation | [`validate_pia_reference_meta_ontology_v0.1.cypher`](../../graph/cypher/validation/validate_pia_reference_meta_ontology_v0.1.cypher) |
| Congruence validation | [`validate_pia_reference_architecture_congruence_v0.2.cypher`](../../graph/cypher/validation/validate_pia_reference_architecture_congruence_v0.2.cypher) |
| Capability evidence validation | [`validate_pia_capability_evidence_profile_v0.2.cypher`](../../graph/cypher/validation/validate_pia_capability_evidence_profile_v0.2.cypher) |

The v0.2 migration backfills canonical property aliases, represents unknown
legacy metadata explicitly, completes assertion metadata, corrects two scoped
relationship types, and links the database to the shared architecture
profile. It does not delete legacy properties or silently grant consent.

Migration `005` is an additive working extension. It creates no participant
records and does not promote the vocabulary merely because it is executable.

## Acceptance criteria

The v0.2 validator requires:

- one matching `ArchitectureProfile` and one applied migration record;
- complete contracted metadata on Participant, Source, Experience, Evidence,
  and Capability nodes;
- no orphan Sources, Experiences, or Evidence;
- complete, unique assertion metadata on every Evidence-to-Capability mapping;
- zero legacy `USES` and overloaded Source-to-Experience `CONTAINS`
  relationships;
- implemented `USES_CAPABILITY` and `DESCRIBES` corrections;
- one governed numeric confidence model;
- complete bounded-core registry declarations;
- no observed unregistered labels or relationship types.

Consent, unknown dates, unknown extraction or fidelity metadata, and
provisional definitions remain visible review queues. They do not prevent a
structurally valid migration from reporting its unresolved knowledge.

## Validated snapshot

The following diagnostic snapshot was captured on 2026-07-23 after applying
the v0.2 congruence migration:

| Measure | Observed |
|---|---:|
| Nodes | 376 |
| Relationships | 1,089 |
| `Concept` registry nodes | 18 |
| `RelationshipDefinition` registry nodes | 24 |
| Applied v0.2 migration records | 1 |
| Architecture profiles | 1 |
| Evidence-to-Capability mappings | 374 |
| Mappings missing assertion metadata | 0 |
| `USES_CAPABILITY` relationships | 8 |
| Legacy `USES` relationships | 0 |
| `DESCRIBES` relationships | 72 |
| Overloaded Source-to-Experience `CONTAINS` | 0 |

This is a point-in-time operational observation, not a schema contract or a
committed database fixture. Re-run the validators against the target database
for current assurance.

## Remaining review queues

The same snapshot exposed knowledge that still requires human review:

| Queue | Count |
|---|---:|
| Participant consent status | 2 |
| Source collection time | 8 |
| Experience date completeness | 6 |
| Evidence extraction or fidelity metadata | 191 |
| Provisional capability definitions | 28 |

These counts do not authorize default values or automatic acceptance. The
source record, participant agency, and applicable contract determine how each
queue is resolved.

## Privacy and participant agency

PIA data is private by default unless an explicit contract and participant
authorization establish another boundary. Access, correction, purpose,
retention, and publication controls remain enforceable throughout the
evidence and assessment chain.

The database must not produce a universal participant score, reputation
ranking, intelligence or morality measure, automatic employability decision,
permanent identity classification, or proof that an undocumented capability
is absent. High-impact interpretation remains human-accountable and
participant-reviewable.
