---
artifact_id: registry-ontology-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.2"
owner: repository-governance
---

# Ontology Registry

## Scope

This registry indexes technology-independent system models, ontology
vocabularies, and supporting semantic dictionaries. Graph projections are
indexed in the Graph Registry.

| Artifact ID | Name | Domain | Layer | Authority | Status | Owner | Version | Canonical Location | Depends On |
|---|---|---|---|---|---|---|---|---|---|
| `ontology-shared-meta-001` | OSI-PIA Ontology Meta-Model | `shared` | `ontology` | `working` | `active` | `ontology-maintainers` | `0.2` | [Ontology Meta-Model](../../ontology/META_ONTOLOGY.md) | `architecture-knowledge-lifecycle-001`<br>`architecture-knowledge-governance-001` |
| `ontology-osi-meta-model-001` | OSI System Meta-Model | `osi` | `foundation` | `canonical` | `active` | `osi-ontology` | `0.1` | [OSI Meta-Model](../../foundation/OSI_META_MODEL.md) | `principle-osi-foundational-001` |
| `ontology-osi-core-001` | OSI Core Concepts | `osi` | `ontology` | `canonical` | `active` | `osi-ontology` | `0.1` | [OSI Core Concepts](../../ontology/CORE%20CONCEPTS.md) | `ontology-osi-meta-model-001` |
| `ontology-pia-capability-pattern-001` | PIA Capability and Pattern Profile | `pia` | `ontology` | `working` | `proposed` | `pia-ontology` | `0.2.0` | [PIA Capability and Pattern Profile](../../ontology/PIA_CAPABILITY_PATTERN_PROFILE.md) | `principle-pia-behavioral-inference-001`<br>`ontology-shared-meta-001`<br>`contract-shared-data-graph-001` |
| `ontology-graph-property-dictionary-001` | Graph Property Dictionary | `shared` | `ontology` | `supporting` | `active` | `graph-maintainers` | `0.2` | [Property dictionary](../../graph/data/dictionaries/property%20dictionary.md) | `ontology-shared-meta-001`<br>`contract-shared-data-graph-001` |

## Ontology item index

This secondary index records the current bounded knowledge-model inventory.
The registry is authoritative for identity, domain, and status; definitions
remain in the linked authorities.

Authority keys:

| Key | Definition authority |
|---|---|
| `META` | [Ontology Meta-Model](../../ontology/META_ONTOLOGY.md) |
| `LIFECYCLE` | [Knowledge Lifecycle](../../foundation/KNOWLEDGE_LIFECYCLE.md) |
| `CORE` | [OSI Core Concepts](../../ontology/CORE%20CONCEPTS.md) |
| `PROFILE` | [Reference Graph Congruence Profile](../../architecture/graph_ontology/REFERENCE_GRAPH_CONGRUENCE.md) |
| `CONTRACT` | [Data and Graph Contract](../../docs/contracts/OSI_PIA_Data_Graph_Contract_v0.1.md) |
| `PIA_PROFILE` | [PIA Capability and Pattern Profile](../../ontology/PIA_CAPABILITY_PATTERN_PROFILE.md) |
| `ASSESSMENT` | [PIA Assessment Stack](../../analysis/PIA/PIA_Assessment_Stack/README.md) |

The item schema is:

| Field | Meaning |
|---|---|
| Ontology ID | Stable lowercase namespaced identity |
| Name | Human-readable canonical name |
| Domain | `shared`, `osi`, `pia`, or `implementation` |
| Kind | Primary ontology item kind |
| Ontology status | `proposed`, `working`, `canonical`, `deprecated`, or `retired` |
| Implementation | Current reference-graph projection maturity |
| Definition authority | Key identifying the governing definition source |

### Concepts

| Ontology ID | Name | Domain | Kind | Ontology status | Implementation | Definition authority |
|---|---|---|---|---|---|---|
| `shared:evidence` | Evidence | `shared` | epistemic category | `working` | both reference graphs | `META` |
| `shared:provenance` | Provenance | `shared` | epistemic constraint | `working` | both reference graphs | `META` |
| `shared:confidence` | Confidence | `shared` | assertion metadata | `working` | scoped models in both graphs | `META` |
| `shared:knowledge_lifecycle` | Knowledge Lifecycle | `shared` | lifecycle model | `working` | `LifecycleState` in both graphs | `LIFECYCLE` |
| `shared:knowledge_state` | Knowledge State | `shared` | state model | `working` | `KnowledgeState` in both graphs | `META` |
| `shared:state_transition` | State Transition | `shared` | transition type | `working` | OSI projection; shared semantics | `META` |
| `shared:assertion` | Assertion | `shared` | assertion type | `working` | relationship metadata in both graphs | `META` |
| `shared:observation` | Observation | `shared` | epistemic category | `working` | domain projections in both graphs | `META` |
| `implementation:architecture_profile` | Architecture Profile | `implementation` | governance object | `working` | `ArchitectureProfile` implemented in both graphs | `PROFILE` |
| `implementation:graph_migration` | Graph Migration | `implementation` | operational object | `working` | `GraphMigration` implemented in both graphs | `PROFILE` |
| `osi:organization` | Organization | `osi` | entity type | `working` | `osi-reference:Organization` implemented | `CORE` |
| `osi:person` | Person | `osi` | entity type | `working` | `osi-reference:Person` implemented | `CORE` |
| `osi:role` | Role | `osi` | entity type | `working` | `osi-reference:Role` planned | `CORE` |
| `osi:position` | Position | `osi` | entity type | `working` | `osi-reference:Position` implemented | `CORE` |
| `osi:team` | Team | `osi` | entity type | `working` | `osi-reference:Team` planned | `CORE` |
| `osi:organizational_unit` | Organizational Unit | `osi` | entity type | `working` | `osi-reference:OrganizationalUnit` implemented | `CORE` |
| `osi:department` | Department | `osi` | entity specialization | `working` | `osi-reference:Department` implemented | `PROFILE` |
| `osi:capability` | Capability | `osi` | entity type | `working` | `osi-reference:Capability` implemented | `CORE` |
| `osi:capability_capital` | Capability Capital | `osi` | construct | `working` | `osi-reference:CapabilityCapital` planned | `CORE` |
| `osi:effective_capability` | Effective Capability | `osi` | construct | `working` | `osi-reference:EffectiveCapability` planned | `CORE` |
| `osi:trust` | Trust | `osi` | construct | `working` | `osi-reference:Trust` planned | `CORE` |
| `osi:predictability` | Predictability | `osi` | construct | `working` | `osi-reference:Predictability` planned | `CORE` |
| `osi:organizational_capital` | Organizational Capital | `osi` | construct | `working` | `osi-reference:OrganizationalCapital` planned | `CORE` |
| `osi:organizational_energy` | Organizational Energy | `osi` | construct | `working` | `osi-reference:OrganizationalEnergy` planned | `CORE` |
| `osi:flow` | Flow | `osi` | construct | `working` | `osi-reference:Flow` planned | `CORE` |
| `osi:topology` | Topology | `osi` | construct | `working` | `osi-reference:Topology` planned | `CORE` |
| `osi:field_condition` | Field Condition | `osi` | construct | `working` | `osi-reference:FieldCondition` planned | `CORE` |
| `osi:source` | Source | `osi` | evidence object | `working` | `osi-reference:Source` implemented | `PROFILE` |
| `osi:collection` | Collection | `osi` | evidence object | `working` | `osi-reference:Collection` implemented | `PROFILE` |
| `osi:evidence` | Evidence | `osi` | evidence object | `working` | `osi-reference:Evidence` implemented | `CORE` |
| `osi:observation` | Observation | `osi` | epistemic object | `working` | `osi-reference:Observation` implemented | `CORE` |
| `osi:indicator` | Indicator | `osi` | analytical object | `working` | `osi-reference:Indicator` implemented | `CORE` |
| `osi:construct` | Construct | `osi` | construct | `working` | `osi-reference:Construct` planned | `CORE` |
| `osi:assessment` | Assessment | `osi` | analytical object | `working` | `osi-reference:Assessment` implemented | `CORE` |
| `osi:state` | State | `osi` | construct | `working` | `osi-reference:State` planned | `CORE` |
| `osi:state_estimate` | State Estimate | `osi` | analytical object | `working` | `osi-reference:StateEstimate` implemented | `PROFILE` |
| `osi:state_transition` | State Transition | `osi` | event type | `working` | `osi-reference:StateTransition` planned | `CORE` |
| `osi:event` | Event | `osi` | event type | `working` | `osi-reference:Event` implemented | `CORE` |
| `osi:staffing_event` | Staffing Event | `osi` | event specialization | `working` | `osi-reference:StaffingEvent` implemented | `PROFILE` |
| `osi:outcome` | Outcome | `osi` | domain object | `working` | `osi-reference:Outcome` implemented | `CORE` |
| `osi:organizational_health` | Organizational Health | `osi` | construct | `working` | `osi-reference:OrganizationalHealth` planned | `CORE` |
| `osi:vacancy` | Vacancy | `osi` | state type | `working` | `osi-reference:Vacancy` planned | `CORE` |
| `osi:principle` | Principle | `osi` | governance object | `working` | `osi-reference:Principle` implemented | `PROFILE` |
| `osi:invariant` | Invariant | `osi` | governance object | `working` | `osi-reference:Invariant` implemented | `PROFILE` |
| `osi:decision_space` | Decision Space | `osi` | analytical object | `working` | `osi-reference:DecisionSpace` inventory only | `PROFILE` |
| `osi:decision` | Decision | `osi` | governance event | `working` | `osi-reference:Decision` inventory only | `PROFILE` |
| `osi:intervention` | Intervention | `osi` | action event | `working` | `osi-reference:Intervention` inventory only | `PROFILE` |
| `osi:validation` | Validation | `osi` | assurance activity | `working` | `osi-reference:Validation` inventory only | `PROFILE` |
| `osi:pattern_memory` | Pattern Memory | `osi` | analytical memory | `working` | `osi-reference:PatternMemory` inventory only | `PROFILE` |
| `pia:participant` | Participant | `pia` | entity type | `working` | `pia-reference:Participant` implemented | `CONTRACT` |
| `pia:source` | Source | `pia` | evidence object | `working` | `pia-reference:Source` implemented | `CONTRACT` |
| `pia:experience` | Experience | `pia` | context object | `working` | `pia-reference:Experience` implemented | `CONTRACT` |
| `pia:evidence` | Evidence | `pia` | evidence object | `working` | `pia-reference:Evidence` implemented | `CONTRACT` |
| `pia:capability` | Capability | `pia` | entity type | `working` | `pia-reference:Capability` implemented | `CONTRACT` |
| `pia:pattern` | Pattern | `pia` | analytical object | `working` | `pia-reference:Pattern` experimental | `ASSESSMENT` |
| `pia:capability_evidence_mapping` | Capability Evidence Mapping | `pia` | assertion type | `proposed` | `pia-reference:SUPPORTS` working profile | `PIA_PROFILE` |
| `pia:pattern_finding_state` | Pattern Finding State | `pia` | state type | `proposed` | assessment relationship property planned | `PIA_PROFILE` |
| `pia:assessment` | Assessment | `pia` | analytical object | `working` | `pia-reference:Assessment` experimental | `ASSESSMENT` |
| `pia:observation` | Observation | `pia` | epistemic object | `working` | `pia-reference:Observation` schema only | `ASSESSMENT` |
| `pia:identity_hypothesis` | Identity Hypothesis | `pia` | analytical object | `working` | `pia-reference:IdentityHypothesis` schema only | `ASSESSMENT` |
| `pia:representation` | Representation | `pia` | analytical object | `working` | `pia-reference:Representation` schema only | `ASSESSMENT` |

### Relationships

Relationship IDs identify semantic definitions. The corresponding graph type
remains uppercase and directional.

| Ontology ID | Graph type | Domain | Direction | Ontology status | Implementation | Definition authority |
|---|---|---|---|---|---|---|
| `shared:conforms_to_architecture` | `CONFORMS_TO_ARCHITECTURE` | `shared` | Ontology â†’ ArchitectureProfile | `working` | both graphs | `PROFILE` |
| `shared:applied_migration` | `APPLIED_MIGRATION` | `shared` | Ontology â†’ GraphMigration | `working` | both graphs | `PROFILE` |
| `osi:position_at` | `POSITION_AT` | `osi` | Position â†’ Organization | `working` | implemented | `PROFILE` |
| `osi:position_in` | `POSITION_IN` | `osi` | Position â†’ OrganizationalUnit | `working` | implemented | `PROFILE` |
| `osi:part_of` | `PART_OF` | `osi` | OrganizationalUnit â†’ Organization | `working` | implemented | `PROFILE` |
| `osi:held_position` | `HELD_POSITION` | `osi` | Person â†’ Position | `working` | implemented | `PROFILE` |
| `osi:collected_from` | `COLLECTED_FROM` | `osi` | Collection â†’ Source | `working` | implemented | `PROFILE` |
| `osi:produced` | `PRODUCED` | `osi` | Collection â†’ Evidence | `working` | implemented | `PROFILE` |
| `osi:about` | `ABOUT` | `osi` | EpistemicObject â†’ Entity | `working` | implemented | `PROFILE` |
| `osi:supported_by` | `SUPPORTED_BY` | `osi` | EpistemicObject â†’ EvidenceOrEpistemicObject | `working` | implemented | `PROFILE` |
| `osi:assesses` | `ASSESSES` | `osi` | Assessment â†’ HypothesisOrConstruct | `working` | implemented | `PROFILE` |
| `osi:derived_from` | `DERIVED_FROM` | `osi` | AnalyticalObject â†’ Observation | `working` | implemented | `PROFILE` |
| `osi:inferred_from` | `INFERRED_FROM` | `osi` | StateEstimate â†’ Indicator | `working` | implemented | `PROFILE` |
| `osi:estimated_from` | `ESTIMATED_FROM` | `osi` | StateEstimate â†’ Observation | `working` | implemented | `PROFILE` |
| `osi:supported_by_indicator` | `SUPPORTED_BY_INDICATOR` | `osi` | StateEstimate â†’ Indicator | `working` | implemented | `PROFILE` |
| `osi:informed_by` | `INFORMED_BY` | `osi` | DecisionSpace â†’ AnalyticalObject | `working` | implemented | `PROFILE` |
| `osi:validates` | `VALIDATES` | `osi` | Validation â†’ AnalyticalObject | `working` | implemented | `PROFILE` |
| `osi:authorized` | `AUTHORIZED` | `osi` | Decision â†’ Intervention | `working` | implemented | `PROFILE` |
| `osi:produced_outcome` | `PRODUCED_OUTCOME` | `osi` | Intervention â†’ Outcome | `working` | implemented | `PROFILE` |
| `pia:has_source` | `HAS_SOURCE` | `pia` | Participant â†’ Source | `working` | implemented | `CONTRACT` |
| `pia:has_experience` | `HAS_EXPERIENCE` | `pia` | Participant â†’ Experience | `working` | implemented | `CONTRACT` |
| `pia:contains` | `CONTAINS` | `pia` | Source â†’ Evidence | `working` | implemented | `CONTRACT` |
| `pia:describes` | `DESCRIBES` | `pia` | Source â†’ Experience | `working` | implemented | `PROFILE` |
| `pia:occurred_in` | `OCCURRED_IN` | `pia` | Evidence â†’ Experience | `working` | implemented | `CONTRACT` |
| `pia:supports` | `SUPPORTS` | `pia` | Evidence â†’ Capability | `working` | implemented | `CONTRACT` |
| `pia:contributes_to` | `CONTRIBUTES_TO` | `pia` | Capability â†’ Pattern | `working` | implemented | `ASSESSMENT` |
| `pia:has_assessment` | `HAS_ASSESSMENT` | `pia` | Participant â†’ Assessment | `working` | implemented | `ASSESSMENT` |
| `pia:evaluates` | `EVALUATES` | `pia` | Assessment â†’ Pattern | `working` | implemented | `ASSESSMENT` |
| `pia:uses_capability` | `USES_CAPABILITY` | `pia` | Assessment â†’ Capability | `working` | implemented | `ASSESSMENT` |
| `pia:based_on` | `BASED_ON` | `pia` | Assessment â†’ Evidence | `working` | implemented | `ASSESSMENT` |
| `pia:supports_identity` | `SUPPORTS_IDENTITY` | `pia` | Assessment â†’ IdentityHypothesis | `working` | schema only | `ASSESSMENT` |
| `pia:uses` | `USES` | `pia` | Assessment â†’ Capability | `deprecated` | migrated to `USES_CAPABILITY` | `PROFILE` |

## Boundary and promotion

`shared:` identifies genuinely common epistemic meaning. Domain concepts such
as `osi:evidence` and `pia:evidence` specialize that shared category without
becoming interchangeable records.

PIA meaning remains distributed across its measurement governance, contracts,
assessment architecture, graph profile, and the working capability and
pattern profile. This registry supplies stable identity and status; no single
implementation artifact silently becomes the complete PIA ontology.

All listed concepts remain `working` unless explicitly shown otherwise.
Implementation does not promote ontology status. Promotion requires the
declaration, congruence, validation, and stewardship evidence defined by the
Ontology Meta-Model.


