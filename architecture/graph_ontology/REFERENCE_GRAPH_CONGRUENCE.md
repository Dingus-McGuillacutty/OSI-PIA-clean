# OSI/PIA Reference Graph Congruence Profile

**Version:** 0.2.0

**Status:** Working architecture at Congruence

**Scope:** `osi-reference` and `pia-reference`

**Database specifications:** [OSI Reference Database](OSI_Reference_Database.md)
and [PIA Reference Database](PIA_Reference_Database.md)

## Purpose

This profile defines the architecture shared by the two reference graphs while
preserving their different purposes:

- PIA preserves participant-controlled evidence and bounded interpretations.
- OSI models organizational structure, field conditions, state, change, and
  repair without reducing people to scores.

The profile aligns ontology declarations, graph labels, relationship meaning,
property names, evidence boundaries, confidence, governance, and validation.
It does not make every registered graph object canonical. Inventory-only and
experimental objects remain explicitly marked.

## Authority

The profile implements, but does not replace, the existing authority order:

1. governance and ethical boundaries;
2. foundation and principles;
3. ontology and meta-ontology;
4. data, import, and validation contracts;
5. graph crosswalk and migrations;
6. analysis and human judgment.

If executable graph behavior differs from a higher layer, the graph is the
component that must be corrected.

## Shared architecture

Both databases implement the following separation:

```text
Source fact and context
        |
        v
Evidence or Observation
        |
        v
Reviewable analytical assertion
        |
        v
Assessment or StateEstimate
        |
        v
Human-accountable decision, learning, or representation
```

The graph must never collapse those stages into one node, relationship, or
score.

### Shared graph conventions

| Concern | Rule |
|---|---|
| Node labels | Singular `PascalCase` |
| Relationships | Directed `UPPER_SNAKE_CASE` |
| Properties | `snake_case` |
| Identity | One contracted stable identity for each canonical object |
| Unknowns | Remain explicit and are not silently inferred |
| Assertions | Carry stable identity, basis, proposer, review state, and time |
| History | Corrections and supersession remain traceable |
| Confidence | Applies to a bounded assertion, never to person worth |
| Human boundary | High-impact interpretation and action remain human-accountable |
| Privacy | Minimum necessary data, consent, correction, purpose limitation, and reviewed access |

Each database contains an `ArchitectureProfile` with
`profile_id = architecture-profile:osi-pia-reference:0.2` and links its
`Ontology` registry through `CONFORMS_TO_ARCHITECTURE`.

## Semantic relationship classes

Every governed relationship definition declares one of these meanings:

| Class | Meaning |
|---|---|
| `provenance_fact` | Source-grounding or acquisition lineage |
| `provenance_context` | Ownership or evidence-package context |
| `structural_fact` | Organizational placement or containment |
| `temporal_fact` | A fact true for a bounded time |
| `context_fact` | Context established by a source or governed record |
| `scope_reference` | The bounded subject of an epistemic object |
| `analytical_basis` | Evidence directly reviewed by an analysis |
| `analytical_reference` | A concept explicitly used by an analysis |
| `analytical_assertion` | A revisable interpretation requiring assertion metadata |
| `sensitive_analytical_assertion` | A high-sensitivity interpretation requiring participant agency |
| `governance_decision` | Human-accountable authorization |
| `observed_result` | An observed result without an unsupported sole-causation claim |
| `operational_provenance` | Import, migration, or validation lineage |

Observed relationships without a governed meaning remain
`working_unclassified` and at Formulation.

## PIA projection

### Contracted evidence spine

```text
Participant -[:HAS_SOURCE]-> Source -[:CONTAINS]-> Evidence
Participant -[:HAS_EXPERIENCE]-> Experience
Evidence -[:OCCURRED_IN]-> Experience
Evidence -[:SUPPORTS]-> Capability
```

`SUPPORTS` is an `analytical_assertion`. It requires:

- `mapping_id` and `assertion_id`;
- numeric `confidence` from `0.00` through `1.00`;
- `confidence_basis` and `assertion_basis`;
- `proposed_by`;
- `review_status`;
- `created_at`;
- explicit human-review status.

The numeric model is registered as
`confidence:pia-reference:evidence-capability-numeric-v1`. It is confidence
in one evidence-to-capability mapping, not a participant score.

### Corrected PIA meanings

| Legacy representation | Congruent representation | Treatment |
|---|---|---|
| `Assessment-[:USES]->Capability` | `Assessment-[:USES_CAPABILITY]->Capability` | Relationship type migrated; legacy properties preserved |
| `Source-[:CONTAINS]->Experience` | `Source-[:DESCRIBES]->Experience` | Removes the overloaded meaning of `CONTAINS` |
| `Evidence.text` | `Evidence.evidence_text` | Canonical alias added; legacy property retained |
| `Capability.name` or `label` | `Capability.capability_name` | Canonical alias added |
| `created` / `updated` | `created_at` / `updated_at` | Canonical aliases added where the semantics match |

Legacy enum values are preserved in properties ending in `_legacy` before the
canonical property is normalized.

Unknown extraction method, fidelity, collection time, or experience time is
represented explicitly. It is not converted into false certainty. An
`unknown` value or a corresponding status property is a review queue, not an
assurance claim.

Missing legacy consent is represented as `pending` with
`consent_status_basis = legacy_not_recorded`. Pending consent requires human
review and must never be interpreted as granted consent.

Capability definitions created during legacy alignment are marked
`provisional_legacy_alignment`. They require ontology review before
promotion.

### Experimental PIA layer

`Assessment`, `Pattern`, `Observation`, `IdentityHypothesis`, and
`Representation` remain outside the contracted participant spine.

The canonical assessment relationships are:

```text
Participant -[:HAS_ASSESSMENT]-> Assessment
Assessment -[:EVALUATES]-> Pattern
Assessment -[:USES_CAPABILITY]-> Capability
Assessment -[:BASED_ON]-> Evidence
Assessment -[:SUPPORTS_IDENTITY]-> IdentityHypothesis
```

`IdentityHypothesis` remains a sensitive, participant-reviewable hypothesis.
It must never become a fixed identity classification.

## OSI projection

### Specialization labels

Existing domain data uses additive specialization labels:

```text
Department:OrganizationalUnit
StaffingEvent:Event
```

The specialized labels preserve compatibility while making the core ontology
explicit. `Department` is not treated as the general concept for every
organizational unit, and `StaffingEvent` is not treated as a separate category
from Event.

### Evidence and analysis

The implemented OSI path distinguishes:

```text
Source -> Collection -> Evidence -> Observation
       -> Hypothesis / Assessment
       -> Indicator / StateEstimate / Prediction
       -> DecisionSpace -> Decision -> Intervention -> Outcome
       -> Validation -> PatternMemory
```

Analytical relationships such as `SUPPORTED_BY`, `DERIVED_FROM`,
`INFERRED_FROM`, `ESTIMATED_FROM`, `SUPPORTED_BY_INDICATOR`, `ASSESSES`,
`INFORMED_BY`, and `VALIDATES` carry common assertion metadata. Legacy
assertions are marked `needs_review`; migration does not silently promote
them.

### Living-system core

The registry declares the written OSI core:

- Organization, Person, Role, Position, Team, and OrganizationalUnit;
- Capability, CapabilityCapital, and EffectiveCapability;
- Topology and FieldCondition;
- Predictability, Trust, OrganizationalCapital, OrganizationalEnergy, and
  Flow;
- State, StateEstimate, StateTransition, Event, Outcome, and Vacancy;
- Construct and OrganizationalHealth.

Only concepts supported by current data are instantiated. Predictability,
Trust, Flow, OrganizationalHealth, and related constructs remain planned
projections until their indicator, derivation, temporal, privacy, and
validation contracts are approved. Registration makes the architecture
visible; it does not manufacture an organizational assessment.

## Maturity and promotion

The architecture profile and declared core projection are at Congruence:

- their names and distinctions agree with the written ontology;
- graph direction and semantic classes are explicit;
- legacy label and property drift is mapped;
- evidence and interpretation boundaries are explicit;
- executable migrations and validation exist.

This does not promote the full ontology to canonical or validated status.
Empirical constructs, provisional capability definitions, legacy metadata
gaps, and inventory-only relationship types remain review work.

## Executable implementation

| Target | Migration | Validation |
|---|---|---|
| `osi-reference` | `graph/migrations/003_osi_reference_architecture_congruence.cypher` | `graph/cypher/validation/validate_osi_reference_architecture_congruence_v0.2.cypher` |
| `pia-reference` | `graph/migrations/004_pia_reference_architecture_congruence.cypher` | `graph/cypher/validation/validate_pia_reference_architecture_congruence_v0.2.cypher` |

Both migrations are rerunnable. Validation distinguishes structural
congruence from review queues so missing historical knowledge stays visible.
