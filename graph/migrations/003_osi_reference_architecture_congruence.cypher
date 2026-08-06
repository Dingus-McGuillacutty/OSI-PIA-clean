// OSI Reference architecture congruence v0.2
//
// Target database: osi-reference
// Compatibility: additive except for no destructive domain changes;
//                Neo4j 5+ / Cypher 25
// Recovery: restore the pre-migration backup. Additive labels and properties
//           are marked with alignment_version = '0.2.0' or managed_by =
//           '003_osi_reference_architecture_congruence'.
//
// This migration:
// - makes Department an explicit OrganizationalUnit specialization;
// - makes StaffingEvent an explicit Event specialization;
// - repairs Source -> Collection -> Evidence provenance for directory evidence;
// - adds reviewable metadata to analytical assertion relationships;
// - declares the bounded OSI core projection in the working registry;
// - links the database to the shared OSI/PIA reference architecture profile.
//
// It does not create instances of theoretical constructs such as Trust,
// Predictability, Flow, or OrganizationalHealth. Those constructs are
// registered as planned projections until evidence and derivation contracts
// exist.

CREATE CONSTRAINT osi_architecture_profile_id_unique IF NOT EXISTS
FOR (n:ArchitectureProfile)
REQUIRE n.profile_id IS UNIQUE;

CREATE CONSTRAINT osi_graph_migration_id_unique IF NOT EXISTS
FOR (n:GraphMigration)
REQUIRE n.migration_id IS UNIQUE;

CREATE CONSTRAINT osi_capability_id_unique IF NOT EXISTS
FOR (n:Capability)
REQUIRE n.capability_id IS UNIQUE;

CREATE CONSTRAINT osi_principle_id_unique IF NOT EXISTS
FOR (n:Principle)
REQUIRE n.principle_id IS UNIQUE;

CREATE CONSTRAINT osi_invariant_id_unique IF NOT EXISTS
FOR (n:Invariant)
REQUIRE n.invariant_id IS UNIQUE;

MERGE (migration:GraphMigration {
  migration_id: '003_osi_reference_architecture_congruence'
})
ON CREATE SET
  migration.name = 'OSI Reference architecture congruence',
  migration.version = '0.2.0',
  migration.target_database = 'osi-reference',
  migration.started_at = datetime(),
  migration.managed_by = '003_osi_reference_architecture_congruence'
SET migration.status = 'running'
WITH migration

CALL (migration) {
  MATCH (department:Department)
  SET department:OrganizationalUnit,
      department.organizational_unit_type =
        coalesce(department.organizational_unit_type, 'department'),
      department.alignment_version = '0.2.0',
      department.aligned_by =
        '003_osi_reference_architecture_congruence'
  RETURN count(department) AS organizational_units_aligned
}

CALL (migration) {
  MATCH (staffing_event:StaffingEvent)
  SET staffing_event:Event,
      staffing_event.event_type =
        coalesce(staffing_event.event_type, 'staffing'),
      staffing_event.alignment_version = '0.2.0',
      staffing_event.aligned_by =
        '003_osi_reference_architecture_congruence'
  RETURN count(staffing_event) AS events_aligned
}

CALL (migration) {
  MATCH (source:Source {source_id: 'SRC-DIR-EDGEWOOD-001'})
  MERGE (collection:Collection {
    collection_id: 'COL-DIR-EDGEWOOD-001'
  })
  ON CREATE SET
    collection.name = 'Edgewood institutional directory evidence collection',
    collection.status = 'working',
    collection.collection_type = 'directory_extract',
    collection.method = 'source_file_alignment',
    collection.purpose =
      'Preserve provenance for directory-derived organizational-unit evidence.',
    collection.collected_at_status = 'not_recorded',
    collection.collector = 'legacy_graph_alignment',
    collection.created_at = datetime(),
    collection.created_at_basis = 'migration_backfill',
    collection.managed_by =
      '003_osi_reference_architecture_congruence'
  MERGE (collection)-[from_source:COLLECTED_FROM]->(source)
  ON CREATE SET
    from_source.relationship_semantic_class = 'provenance_fact',
    from_source.provenance_basis =
      'Collection was reconstructed from the Evidence.source_file and Source.source_files correspondence.',
    from_source.created_at = datetime(),
    from_source.created_at_basis = 'migration_backfill'
  WITH collection, source
  MATCH (evidence:Evidence)
  WHERE evidence.source_file IN source.source_files
  MERGE (collection)-[produced:PRODUCED]->(evidence)
  ON CREATE SET
    produced.relationship_semantic_class = 'provenance_fact',
    produced.provenance_basis =
      'Evidence.source_file is listed in Source.source_files.',
    produced.created_at = datetime(),
    produced.created_at_basis = 'migration_backfill'
  RETURN count(evidence) AS evidence_provenance_repaired
}

CALL (migration) {
  MATCH (collection:Collection)-[relationship:COLLECTED_FROM|PRODUCED]->()
  SET relationship.relationship_semantic_class =
        coalesce(relationship.relationship_semantic_class, 'provenance_fact'),
      relationship.provenance_basis =
        coalesce(
          relationship.provenance_basis,
          'Existing source or collection structure in the reference graph.'
        ),
      relationship.created_at =
        coalesce(relationship.created_at, datetime()),
      relationship.created_at_basis =
        coalesce(
          relationship.created_at_basis,
          'migration_backfill'
        )
  RETURN count(relationship) AS provenance_relationships_aligned
}

CALL (migration) {
  MATCH (start)-[assertion]->(end)
  WHERE type(assertion) IN [
    'SUPPORTED_BY',
    'ASSESSES',
    'BASED_ON',
    'DERIVED_FROM',
    'INFERRED_FROM',
    'INFORMED_BY',
    'VALIDATES',
    'ESTIMATED_FROM',
    'SUPPORTED_BY_INDICATOR'
  ]
  WITH
    assertion,
    type(assertion) AS relationship_type,
    coalesce(
      start.entity_id,
      start.evidence_id,
      start.observation_id,
      start.hypothesis_id,
      start.assessment_id,
      start.prediction_id,
      start.indicator_id,
      start.state_estimate_id,
      start.decision_space_id,
      start.validation_id,
      start.name
    ) AS start_id,
    coalesce(
      end.entity_id,
      end.evidence_id,
      end.observation_id,
      end.hypothesis_id,
      end.assessment_id,
      end.prediction_id,
      end.indicator_id,
      end.state_estimate_id,
      end.decision_space_id,
      end.validation_id,
      end.name
    ) AS end_id
  SET assertion.assertion_id =
        coalesce(
          assertion.assertion_id,
          'assertion:osi-reference:' +
          relationship_type + ':' + start_id + ':' + end_id
        ),
      assertion.relationship_semantic_class = 'analytical_assertion',
      assertion.assertion_basis =
        coalesce(
          assertion.assertion_basis,
          'Legacy relationship preserved from the reference graph; the connected evidence and analytical objects provide its current basis.'
        ),
      assertion.proposed_by =
        coalesce(assertion.proposed_by, 'legacy_graph_alignment'),
      assertion.review_status =
        coalesce(assertion.review_status, 'needs_review'),
      assertion.created_at =
        coalesce(assertion.created_at, datetime()),
      assertion.created_at_basis =
        coalesce(
          assertion.created_at_basis,
          'migration_backfill'
        ),
      assertion.human_review_required =
        coalesce(assertion.human_review_required, true),
      assertion.alignment_version = '0.2.0'
  RETURN count(assertion) AS assertions_aligned
}

MATCH (ontology:Ontology {ontology_id: 'ontology:osi-reference'})
SET ontology.version = '0.2.0',
    ontology.architecture_alignment_state = 'congruence',
    ontology.aligned_at = datetime(),
    ontology.aligned_by =
      '003_osi_reference_architecture_congruence'
MERGE (profile:ArchitectureProfile {
  profile_id: 'architecture-profile:osi-pia-reference:0.2'
})
ON CREATE SET
  profile.name = 'OSI/PIA Reference Graph Architecture',
  profile.version = '0.2.0',
  profile.status = 'working',
  profile.knowledge_lifecycle_state = 'congruence',
  profile.ontology_status = 'working',
  profile.label_convention = 'singular_pascal_case',
  profile.relationship_convention = 'upper_snake_case',
  profile.property_convention = 'snake_case',
  profile.identity_policy =
    'One contracted stable identity for each canonical object.',
  profile.evidence_boundary =
    'Source facts, observations, interpretations, assertions, and decisions remain distinguishable and traceable.',
  profile.uncertainty_policy =
    'Unknown values remain explicit; assertions carry basis, review state, and uncertainty where applicable.',
  profile.human_boundary =
    'The graph supports human diagnosis and review; it does not authorize person scoring or automated punishment.',
  profile.privacy_boundary =
    'Use minimum necessary data, purpose limitation, consent, correction, and reviewed access.',
  profile.source_refs = [
    'architecture/graph_ontology/REFERENCE_GRAPH_CONGRUENCE.md',
    'ontology/META_ONTOLOGY.md',
    'architecture/graph_standards/Graph_Standards.md'
  ],
  profile.managed_by =
    '003_osi_reference_architecture_congruence',
  profile.created_at = datetime()
SET profile.aligned_at = datetime()
MERGE (ontology)-[:CONFORMS_TO_ARCHITECTURE]->(profile)
MERGE (ontology)-[:APPLIED_MIGRATION]->(migration)
WITH ontology, profile, migration,
     organizational_units_aligned,
     events_aligned,
     evidence_provenance_repaired,
     provenance_relationships_aligned,
     assertions_aligned

CALL (ontology) {
  UNWIND [
    {
      graph_label: 'ArchitectureProfile',
      identity: 'profile_id',
      kind: 'governance_object',
      implementation: 'implemented',
      definition: 'A versioned declaration of the graph conventions and ethical boundaries shared by the OSI and PIA reference databases.',
      distinction: 'Defines projection rules; it does not define domain truth.',
      temporal: 'Versioned and superseded rather than silently rewritten.'
    },
    {
      graph_label: 'GraphMigration',
      identity: 'migration_id',
      kind: 'operational_object',
      implementation: 'implemented',
      definition: 'An auditable record that a versioned graph change was applied.',
      distinction: 'Operational provenance rather than organizational evidence.',
      temporal: 'Records start, completion, and migration version.'
    },
    {
      graph_label: 'Organization',
      identity: 'entity_id',
      kind: 'entity_type',
      implementation: 'implemented',
      definition: 'A coordinated human system formed to pursue one or more purposes.',
      distinction: 'The whole cooperative system rather than one unit, position, or person.',
      temporal: 'Identity persists while attributes and membership change over time.'
    },
    {
      graph_label: 'Person',
      identity: 'entity_id',
      kind: 'entity_type',
      implementation: 'implemented',
      definition: 'A human participant represented within the organizational system.',
      distinction: 'A person is not a score, role, position, or source of unrestricted data.',
      temporal: 'Identity persists; roles and positions are time-bounded.'
    },
    {
      graph_label: 'Role',
      identity: 'role_id',
      kind: 'entity_type',
      implementation: 'planned',
      definition: 'A set of expected functions, responsibilities, authorities, and relationships.',
      distinction: 'Exists independently from a person and from a specific organizational placement.',
      temporal: 'Versioned when expectations or authority change.'
    },
    {
      graph_label: 'Position',
      identity: 'entity_id',
      kind: 'entity_type',
      implementation: 'implemented',
      definition: 'A specific organizational placement through which a role is assigned.',
      distinction: 'A position may be filled or vacant and is not identical to its occupant.',
      temporal: 'Occupancy and organizational placement are time-bounded.'
    },
    {
      graph_label: 'Team',
      identity: 'team_id',
      kind: 'entity_type',
      implementation: 'planned',
      definition: 'A group of people and roles connected through shared work, responsibility, or purpose.',
      distinction: 'A collaborative grouping rather than any formal organizational unit.',
      temporal: 'Membership and purpose may change over time.'
    },
    {
      graph_label: 'OrganizationalUnit',
      identity: 'entity_id',
      kind: 'entity_type',
      implementation: 'implemented',
      definition: 'A formally or informally bounded part of an organization.',
      distinction: 'The general concept specialized by Department and future unit types.',
      temporal: 'Boundary, authority, and membership are time-bounded.'
    },
    {
      graph_label: 'Department',
      identity: 'entity_id',
      kind: 'entity_type',
      implementation: 'implemented',
      definition: 'A formal organizational unit represented as a specialization of OrganizationalUnit.',
      distinction: 'A department is one unit type, not the general unit concept.',
      temporal: 'Names, authority, and placement may change over time.'
    },
    {
      graph_label: 'Capability',
      identity: 'capability_id',
      kind: 'entity_type',
      implementation: 'implemented',
      definition: 'The ability to perform an action, exercise judgment, solve a problem, create an output, or produce useful change.',
      distinction: 'Capability is not equivalent to a credential, title, or observed performance.',
      temporal: 'Definitions are versioned; evidence support is time- and context-bounded.'
    },
    {
      graph_label: 'CapabilityCapital',
      identity: 'capability_capital_id',
      kind: 'construct',
      implementation: 'planned',
      definition: 'The stored human capacity present within an organizational system.',
      distinction: 'Potential capacity rather than capacity successfully expressed.',
      temporal: 'Estimated for a defined scope and time.'
    },
    {
      graph_label: 'EffectiveCapability',
      identity: 'effective_capability_id',
      kind: 'construct',
      implementation: 'planned',
      definition: 'Capability that is successfully expressed, directed, and applied.',
      distinction: 'Observed or inferred utilization rather than latent capability.',
      temporal: 'Assessed for a defined context and period.'
    },
    {
      graph_label: 'Trust',
      identity: 'trust_id',
      kind: 'construct',
      implementation: 'planned',
      definition: 'An emergent relational condition involving expectations of reliability, safety, competence, honesty, and appropriate behavior.',
      distinction: 'A distributed field condition rather than an attitude score.',
      temporal: 'Inferred for a defined scope and time from multiple evidence sources.'
    },
    {
      graph_label: 'Predictability',
      identity: 'predictability_id',
      kind: 'construct',
      implementation: 'planned',
      definition: 'The degree to which participants can form reliable and workable models of the organizational environment.',
      distinction: 'Workable legibility rather than organizational stasis or certainty.',
      temporal: 'Inferred for a defined scope and time.'
    },
    {
      graph_label: 'OrganizationalCapital',
      identity: 'organizational_capital_id',
      kind: 'construct',
      implementation: 'planned',
      definition: 'A resource or capacity present within or available to an organization.',
      distinction: 'Stored capacity rather than its movement or activation.',
      temporal: 'Estimated for a defined scope and time.'
    },
    {
      graph_label: 'OrganizationalEnergy',
      identity: 'organizational_energy_id',
      kind: 'construct',
      implementation: 'planned',
      definition: 'The capacity available to initiate, sustain, or redirect action.',
      distinction: 'Available activation capacity rather than flow or output.',
      temporal: 'Estimated for a defined scope and time.'
    },
    {
      graph_label: 'Flow',
      identity: 'flow_id',
      kind: 'construct',
      implementation: 'planned',
      definition: 'The movement of information, authority, resources, capability, knowledge, attention, or support.',
      distinction: 'Movement through the system rather than the topology through which movement occurs.',
      temporal: 'Measured or inferred across a defined pathway and period.'
    },
    {
      graph_label: 'Topology',
      identity: 'topology_id',
      kind: 'construct',
      implementation: 'planned',
      definition: 'The structural arrangement of entities and relationships within the organization.',
      distinction: 'Structural connectivity rather than distributed field conditions.',
      temporal: 'Versioned or estimated at a defined time.'
    },
    {
      graph_label: 'FieldCondition',
      identity: 'field_condition_id',
      kind: 'construct',
      implementation: 'planned',
      definition: 'A distributed condition that influences behavior and movement across part or all of an organization.',
      distinction: 'A relational system condition rather than an individual trait.',
      temporal: 'Inferred for a defined scope and time.'
    },
    {
      graph_label: 'Source',
      identity: 'source_id',
      kind: 'evidence_object',
      implementation: 'implemented',
      definition: 'An identifiable origin from which evidence is collected.',
      distinction: 'The origin of evidence rather than the evidence or an interpretation.',
      temporal: 'Collection and source dates remain distinct.'
    },
    {
      graph_label: 'Collection',
      identity: 'collection_id',
      kind: 'evidence_object',
      implementation: 'implemented',
      definition: 'A bounded acquisition event or package connecting a Source to produced Evidence.',
      distinction: 'Operational provenance rather than the source or evidence content.',
      temporal: 'Time-bounded by acquisition when known.'
    },
    {
      graph_label: 'Evidence',
      identity: 'evidence_id',
      kind: 'evidence_object',
      implementation: 'implemented',
      definition: 'Information used to support, challenge, or contextualize a claim.',
      distinction: 'Source-grounded material rather than an observation or interpretation.',
      temporal: 'Source time, event time, and record time remain distinguishable.'
    },
    {
      graph_label: 'Observation',
      identity: 'observation_id',
      kind: 'epistemic_object',
      implementation: 'implemented',
      definition: 'A recorded description of something perceived, detected, or reported.',
      distinction: 'A bounded description that remains separate from interpretation.',
      temporal: 'Observed time and recorded time remain distinguishable.'
    },
    {
      graph_label: 'Indicator',
      identity: 'indicator_id',
      kind: 'analytical_object',
      implementation: 'implemented',
      definition: 'An observable measure used as evidence for a broader construct.',
      distinction: 'An observable signal rather than the construct it informs.',
      temporal: 'Value and as-of time are required for interpretation.'
    },
    {
      graph_label: 'Construct',
      identity: 'construct_id',
      kind: 'construct',
      implementation: 'planned',
      definition: 'A theoretical property that may be inferred from multiple indicators.',
      distinction: 'An inferred concept rather than directly observed evidence.',
      temporal: 'Any estimate is scope- and time-bounded.'
    },
    {
      graph_label: 'Assessment',
      identity: 'assessment_id',
      kind: 'analytical_object',
      implementation: 'implemented',
      definition: 'A revisable interpretation of available evidence concerning a bounded entity, relationship, condition, or state.',
      distinction: 'An interpretation rather than source evidence or a human decision.',
      temporal: 'Versioned; later assessments supersede rather than overwrite.'
    },
    {
      graph_label: 'State',
      identity: 'state_id',
      kind: 'construct',
      implementation: 'planned',
      definition: 'The condition of an entity, relationship, or system at a defined time.',
      distinction: 'The modeled condition rather than an estimate or transition.',
      temporal: 'Always defined for a time or interval.'
    },
    {
      graph_label: 'StateEstimate',
      identity: 'state_estimate_id',
      kind: 'analytical_object',
      implementation: 'implemented',
      definition: 'A reviewable estimate of state derived from observations and indicators.',
      distinction: 'An epistemic representation of State rather than State itself.',
      temporal: 'Requires an as-of time, scope, and revision history.'
    },
    {
      graph_label: 'StateTransition',
      identity: 'state_transition_id',
      kind: 'event_type',
      implementation: 'planned',
      definition: 'A change from one State to another.',
      distinction: 'The change process rather than either endpoint state.',
      temporal: 'Requires ordered before and after states or bounded transition time.'
    },
    {
      graph_label: 'Event',
      identity: 'entity_id',
      kind: 'event_type',
      implementation: 'implemented',
      definition: 'An occurrence associated with a time, participants, and possible state changes.',
      distinction: 'An occurrence rather than an assessment or outcome.',
      temporal: 'Event time is distinct from observation and record time.'
    },
    {
      graph_label: 'StaffingEvent',
      identity: 'entity_id',
      kind: 'event_type',
      implementation: 'implemented',
      definition: 'An Event involving a change in staffing or position occupancy.',
      distinction: 'A specialized Event rather than a StateTransition or Position.',
      temporal: 'Occurs at a defined or explicitly unknown time.'
    },
    {
      graph_label: 'Outcome',
      identity: 'outcome_id',
      kind: 'domain_object',
      implementation: 'implemented',
      definition: 'A result produced by organizational activity or state transition.',
      distinction: 'A result rather than the intervention or assessment that preceded it.',
      temporal: 'Observed for a defined period after an action or transition.'
    },
    {
      graph_label: 'OrganizationalHealth',
      identity: 'organizational_health_id',
      kind: 'construct',
      implementation: 'planned',
      definition: 'An emergent condition reflecting the system ability to mobilize capability, maintain workable relationships, adapt, recover, learn, and sustain outcomes.',
      distinction: 'An emergent assessment rather than a direct metric or dashboard score.',
      temporal: 'Assessed for a defined scope and time with explicit uncertainty.'
    },
    {
      graph_label: 'Vacancy',
      identity: 'vacancy_id',
      kind: 'state_type',
      implementation: 'planned',
      definition: 'A State in which an established Position lacks its intended occupant.',
      distinction: 'A position state rather than a person property.',
      temporal: 'Bounded by vacancy start and end or explicit unknown status.'
    },
    {
      graph_label: 'Principle',
      identity: 'principle_id',
      kind: 'governance_object',
      implementation: 'implemented',
      definition: 'A normative commitment that constrains ontology, data, analysis, and use.',
      distinction: 'A governing commitment rather than an empirical claim.',
      temporal: 'Versioned and superseded through governance.'
    },
    {
      graph_label: 'Invariant',
      identity: 'invariant_id',
      kind: 'governance_object',
      implementation: 'implemented',
      definition: 'A condition that an implementation or analytical path must preserve.',
      distinction: 'An enforceable boundary rather than a preferred practice.',
      temporal: 'Versioned and reviewed whenever the architecture changes.'
    }
  ] AS concept_data
  MERGE (concept:Concept {
    concept_id:
      'concept:osi-reference:' + concept_data.graph_label
  })
  SET concept.name = concept_data.graph_label,
      concept.graph_label = concept_data.graph_label,
      concept.stable_identity_property = concept_data.identity,
      concept.item_kind = concept_data.kind,
      concept.scope = 'osi-reference',
      concept.definition = concept_data.definition,
      concept.distinction = concept_data.distinction,
      concept.temporal_semantics = concept_data.temporal,
      concept.evidence_boundary =
        'Instances and assertions must remain traceable to source facts, governed reference definitions, or explicit derivation records.',
      concept.privacy_boundary =
        'Minimum necessary data; no person scoring, covert inference, or automated punitive use.',
      concept.relationship_policy =
        'Use only registered relationship definitions with explicit direction and semantic class.',
      concept.version = '0.2.0',
      concept.steward = 'OSI ontology steward',
      concept.knowledge_lifecycle_state = 'congruence',
      concept.ontology_status = 'working',
      concept.implementation_status = concept_data.implementation,
      concept.definition_status = 'declared',
      concept.source_ref = 'ontology/CORE CONCEPTS.md',
      concept.last_aligned_by =
        '003_osi_reference_architecture_congruence',
      concept.aligned_at = datetime()
  MERGE (ontology)-[:DEFINES_CONCEPT]->(concept)
  RETURN count(concept) AS core_concepts_aligned
}

CALL (ontology) {
  UNWIND [
    {
      relationship_type: 'CONFORMS_TO_ARCHITECTURE',
      start_label: 'Ontology',
      end_label: 'ArchitectureProfile',
      semantic_class: 'governance_link',
      cardinality: 'many_to_one_per_version',
      assertion_required: false,
      definition: 'Links an ontology registry to the architecture profile whose rules it follows.'
    },
    {
      relationship_type: 'APPLIED_MIGRATION',
      start_label: 'Ontology',
      end_label: 'GraphMigration',
      semantic_class: 'operational_provenance',
      cardinality: 'one_to_many',
      assertion_required: false,
      definition: 'Records a versioned migration applied to the ontology projection.'
    },
    {
      relationship_type: 'POSITION_AT',
      start_label: 'Position',
      end_label: 'Organization',
      semantic_class: 'structural_fact',
      cardinality: 'many_to_one_at_time',
      assertion_required: false,
      definition: 'Places a Position within an Organization.'
    },
    {
      relationship_type: 'POSITION_IN',
      start_label: 'Position',
      end_label: 'OrganizationalUnit',
      semantic_class: 'structural_fact',
      cardinality: 'many_to_one_at_time',
      assertion_required: false,
      definition: 'Places a Position within an OrganizationalUnit.'
    },
    {
      relationship_type: 'PART_OF',
      start_label: 'OrganizationalUnit',
      end_label: 'Organization',
      semantic_class: 'structural_fact',
      cardinality: 'many_to_one_at_time',
      assertion_required: false,
      definition: 'Places an OrganizationalUnit within an Organization.'
    },
    {
      relationship_type: 'HELD_POSITION',
      start_label: 'Person',
      end_label: 'Position',
      semantic_class: 'temporal_fact',
      cardinality: 'many_to_many_over_time',
      assertion_required: false,
      definition: 'Records that a Person occupied a Position for a bounded period.'
    },
    {
      relationship_type: 'COLLECTED_FROM',
      start_label: 'Collection',
      end_label: 'Source',
      semantic_class: 'provenance_fact',
      cardinality: 'many_to_one',
      assertion_required: false,
      definition: 'Identifies the Source from which a Collection was acquired.'
    },
    {
      relationship_type: 'PRODUCED',
      start_label: 'Collection',
      end_label: 'Evidence',
      semantic_class: 'provenance_fact',
      cardinality: 'one_to_many',
      assertion_required: false,
      definition: 'Connects a Collection to Evidence produced during acquisition or extraction.'
    },
    {
      relationship_type: 'ABOUT',
      start_label: 'EpistemicObject',
      end_label: 'Entity',
      semantic_class: 'scope_reference',
      cardinality: 'many_to_many',
      assertion_required: false,
      definition: 'Identifies the bounded subject of evidence, observation, or analysis.'
    },
    {
      relationship_type: 'SUPPORTED_BY',
      start_label: 'EpistemicObject',
      end_label: 'EvidenceOrEpistemicObject',
      semantic_class: 'analytical_assertion',
      cardinality: 'many_to_many',
      assertion_required: true,
      definition: 'States that a reviewable epistemic object is supported by a lower-level evidentiary object.'
    },
    {
      relationship_type: 'ASSESSES',
      start_label: 'Assessment',
      end_label: 'HypothesisOrConstruct',
      semantic_class: 'analytical_assertion',
      cardinality: 'many_to_many',
      assertion_required: true,
      definition: 'States what bounded hypothesis or construct an Assessment evaluates.'
    },
    {
      relationship_type: 'DERIVED_FROM',
      start_label: 'AnalyticalObject',
      end_label: 'Observation',
      semantic_class: 'analytical_assertion',
      cardinality: 'many_to_many',
      assertion_required: true,
      definition: 'Records the lower-level observations from which an analytical object was derived.'
    },
    {
      relationship_type: 'INFERRED_FROM',
      start_label: 'StateEstimate',
      end_label: 'Indicator',
      semantic_class: 'analytical_assertion',
      cardinality: 'many_to_many',
      assertion_required: true,
      definition: 'Records indicators used to infer a StateEstimate.'
    },
    {
      relationship_type: 'ESTIMATED_FROM',
      start_label: 'StateEstimate',
      end_label: 'Observation',
      semantic_class: 'analytical_assertion',
      cardinality: 'many_to_many',
      assertion_required: true,
      definition: 'Records observations used directly in a StateEstimate.'
    },
    {
      relationship_type: 'SUPPORTED_BY_INDICATOR',
      start_label: 'StateEstimate',
      end_label: 'Indicator',
      semantic_class: 'analytical_assertion',
      cardinality: 'many_to_many',
      assertion_required: true,
      definition: 'Records indicators that support a StateEstimate.'
    },
    {
      relationship_type: 'INFORMED_BY',
      start_label: 'DecisionSpace',
      end_label: 'AnalyticalObject',
      semantic_class: 'analytical_assertion',
      cardinality: 'many_to_many',
      assertion_required: true,
      definition: 'Records analytical objects that informed a bounded DecisionSpace.'
    },
    {
      relationship_type: 'VALIDATES',
      start_label: 'Validation',
      end_label: 'AnalyticalObject',
      semantic_class: 'analytical_assertion',
      cardinality: 'many_to_many',
      assertion_required: true,
      definition: 'Records the analytical object evaluated by a Validation activity.'
    },
    {
      relationship_type: 'AUTHORIZED',
      start_label: 'Decision',
      end_label: 'Intervention',
      semantic_class: 'governance_decision',
      cardinality: 'one_to_many',
      assertion_required: false,
      definition: 'Records that a human-accountable Decision authorized an Intervention.'
    },
    {
      relationship_type: 'PRODUCED_OUTCOME',
      start_label: 'Intervention',
      end_label: 'Outcome',
      semantic_class: 'observed_result',
      cardinality: 'one_to_many',
      assertion_required: false,
      definition: 'Connects an Intervention to a subsequently observed Outcome without asserting sole causation.'
    }
  ] AS relationship_data
  MERGE (definition:RelationshipDefinition {
    relationship_definition_id:
      'relationship-definition:osi-reference:' +
      relationship_data.relationship_type
  })
  SET definition.name = relationship_data.relationship_type,
      definition.graph_relationship_type =
        relationship_data.relationship_type,
      definition.direction = 'outbound',
      definition.canonical_start_label =
        relationship_data.start_label,
      definition.canonical_end_label =
        relationship_data.end_label,
      definition.cardinality =
        relationship_data.cardinality,
      definition.semantic_class =
        relationship_data.semantic_class,
      definition.assertion_metadata_required =
        relationship_data.assertion_required,
      definition.definition =
        relationship_data.definition,
      definition.scope = 'osi-reference',
      definition.version = '0.2.0',
      definition.steward = 'OSI ontology steward',
      definition.knowledge_lifecycle_state = 'congruence',
      definition.ontology_status = 'working',
      definition.implementation_status =
        CASE
          WHEN relationship_data.relationship_type IN [
            'CONFORMS_TO_ARCHITECTURE',
            'APPLIED_MIGRATION',
            'POSITION_AT',
            'POSITION_IN',
            'PART_OF',
            'HELD_POSITION',
            'COLLECTED_FROM',
            'PRODUCED',
            'ABOUT',
            'SUPPORTED_BY',
            'ASSESSES',
            'DERIVED_FROM',
            'INFERRED_FROM',
            'ESTIMATED_FROM',
            'SUPPORTED_BY_INDICATOR',
            'INFORMED_BY',
            'VALIDATES',
            'AUTHORIZED',
            'PRODUCED_OUTCOME'
          ] THEN 'implemented'
          ELSE 'documented'
        END,
      definition.definition_status = 'declared',
      definition.source_ref =
        'architecture/graph_ontology/REFERENCE_GRAPH_CONGRUENCE.md',
      definition.last_aligned_by =
        '003_osi_reference_architecture_congruence',
      definition.aligned_at = datetime()
  MERGE (ontology)-[:DEFINES_RELATIONSHIP]->(definition)
  RETURN count(definition) AS core_relationships_aligned
}

CALL (ontology) {
  MATCH (concept:Concept)
  WHERE concept.scope = 'osi-reference'
    AND concept.knowledge_lifecycle_state = 'congruence'
  OPTIONAL MATCH (ontology)-[:DEFINES_RELATIONSHIP]->(
    definition:RelationshipDefinition
  )
  WHERE definition.knowledge_lifecycle_state = 'congruence'
    AND (
      definition.canonical_start_label = concept.graph_label
      OR definition.canonical_end_label = concept.graph_label
      OR concept.graph_label IN
        coalesce(definition.observed_start_labels, [])
      OR concept.graph_label IN
        coalesce(definition.observed_end_labels, [])
    )
  WITH
    concept,
    [
      relationship_type IN collect(
        DISTINCT definition.graph_relationship_type
      )
      WHERE relationship_type IS NOT NULL
    ] AS allowed_relationships
  SET concept.allowed_relationships = allowed_relationships
  RETURN count(concept) AS allowed_relationship_sets_aligned
}

CALL (ontology) {
  MATCH (concept:Concept)
  WHERE concept.scope = 'osi-reference'
    AND concept.definition IS NULL
  SET concept.definition_status = 'inventory_only',
      concept.knowledge_lifecycle_state =
        coalesce(concept.knowledge_lifecycle_state, 'formulation'),
      concept.relationship_policy =
        coalesce(
          concept.relationship_policy,
          'No canonical relationship use until a governed declaration is added.'
        )
  RETURN count(concept) AS inventory_only_concepts
}

CALL (ontology) {
  MATCH (definition:RelationshipDefinition)
  WHERE definition.scope = 'osi-reference'
    AND definition.definition IS NULL
  SET definition.definition_status = 'inventory_only',
      definition.semantic_class =
        coalesce(definition.semantic_class, 'working_unclassified'),
      definition.assertion_metadata_required =
        coalesce(definition.assertion_metadata_required, false)
  RETURN count(definition) AS inventory_only_relationships
}

CALL (ontology) {
  MATCH (observed)
  UNWIND labels(observed) AS graph_label
  WITH ontology, graph_label, count(observed) AS observed_node_count
  MERGE (concept:Concept {
    concept_id: 'concept:osi-reference:' + graph_label
  })
  ON CREATE SET
    concept.name = graph_label,
    concept.graph_label = graph_label,
    concept.item_kind = 'graph_label',
    concept.scope = 'osi-reference',
    concept.knowledge_lifecycle_state = 'formulation',
    concept.ontology_status = 'working',
    concept.implementation_status = 'implemented',
    concept.definition_status = 'inventory_only',
    concept.registration_basis = 'observed_live_graph_label',
    concept.source_ref = 'ontology/META_ONTOLOGY.md',
    concept.managed_by =
      '003_osi_reference_architecture_congruence',
    concept.created_at = datetime()
  SET concept.observed_node_count = observed_node_count
  MERGE (ontology)-[:DEFINES_CONCEPT]->(concept)
  RETURN count(concept) AS observed_concepts_registered
}

CALL (ontology) {
  MATCH (start)-[relationship]->(end)
  UNWIND labels(start) AS start_label
  UNWIND labels(end) AS end_label
  WITH DISTINCT
    ontology,
    type(relationship) AS relationship_type,
    start_label,
    end_label
  ORDER BY relationship_type, start_label, end_label
  WITH
    ontology,
    relationship_type,
    collect(DISTINCT start_label) AS observed_start_labels,
    collect(DISTINCT end_label) AS observed_end_labels
  MERGE (definition:RelationshipDefinition {
    relationship_definition_id:
      'relationship-definition:osi-reference:' +
      relationship_type
  })
  ON CREATE SET
    definition.name = relationship_type,
    definition.graph_relationship_type = relationship_type,
    definition.direction = 'outbound',
    definition.scope = 'osi-reference',
    definition.knowledge_lifecycle_state = 'formulation',
    definition.ontology_status = 'working',
    definition.implementation_status = 'implemented',
    definition.definition_status = 'inventory_only',
    definition.semantic_class = 'working_unclassified',
    definition.registration_basis =
      'observed_live_graph_relationship',
    definition.source_ref = 'ontology/META_ONTOLOGY.md',
    definition.managed_by =
      '003_osi_reference_architecture_congruence',
    definition.created_at = datetime()
  SET definition.observed_start_labels =
        observed_start_labels,
      definition.observed_end_labels =
        observed_end_labels
  MERGE (ontology)-[:DEFINES_RELATIONSHIP]->(definition)
  RETURN count(definition) AS observed_relationships_registered
}

SET migration.status = 'applied',
    migration.completed_at = datetime(),
    migration.summary =
      'Aligned OSI specialization labels, evidence provenance, analytical assertion metadata, core declarations, and the shared architecture profile.'

RETURN
  migration.migration_id AS migration_id,
  migration.status AS status,
  organizational_units_aligned,
  events_aligned,
  evidence_provenance_repaired,
  provenance_relationships_aligned,
  assertions_aligned,
  core_concepts_aligned,
  core_relationships_aligned,
  allowed_relationship_sets_aligned,
  inventory_only_concepts,
  inventory_only_relationships,
  observed_concepts_registered,
  observed_relationships_registered;
