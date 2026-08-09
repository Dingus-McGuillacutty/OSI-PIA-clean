// Validate OSI Reference architecture congruence v0.2.
// Target database: osi-reference

MATCH (ontology:Ontology {ontology_id: 'ontology:osi-reference'})

CALL (ontology) {
  MATCH (ontology)-[:CONFORMS_TO_ARCHITECTURE]->(
    profile:ArchitectureProfile {
      profile_id: 'architecture-profile:osi-pia-reference:0.2'
    }
  )
  WHERE profile.knowledge_lifecycle_state = 'congruence'
    AND profile.ontology_status = 'working'
  RETURN count(profile) AS architecture_profile_count
}

CALL (ontology) {
  MATCH (ontology)-[:APPLIED_MIGRATION]->(
    migration:GraphMigration {
      migration_id:
        '003_osi_reference_architecture_congruence'
    }
  )
  WHERE migration.status = 'applied'
  RETURN count(migration) AS applied_migration_count
}

CALL () {
  MATCH (department:Department)
  RETURN
    count(department) AS department_count,
    count(
      CASE
        WHEN department:OrganizationalUnit THEN 1
      END
    ) AS department_organizational_unit_count
}

CALL () {
  MATCH (staffing_event:StaffingEvent)
  RETURN
    count(staffing_event) AS staffing_event_count,
    count(
      CASE
        WHEN staffing_event:Event THEN 1
      END
    ) AS staffing_event_event_count
}

CALL () {
  MATCH (evidence:Evidence)
  WHERE NOT (:Collection)-[:PRODUCED]->(evidence)
  RETURN count(evidence) AS evidence_without_collection_provenance
}

CALL () {
  MATCH ()-[assertion]->()
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
  RETURN
    count(assertion) AS analytical_assertion_count,
    count(
      CASE
        WHEN assertion.assertion_id IS NULL
          OR assertion.assertion_basis IS NULL
          OR assertion.proposed_by IS NULL
          OR assertion.review_status IS NULL
          OR assertion.created_at IS NULL
          OR assertion.relationship_semantic_class <>
            'analytical_assertion'
        THEN 1
      END
    ) AS analytical_assertions_missing_metadata
}

CALL () {
  MATCH ()-[assertion]->()
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
  WITH assertion.assertion_id AS assertion_id, count(*) AS occurrences
  WHERE assertion_id IS NULL OR occurrences > 1
  RETURN count(*) AS invalid_assertion_identity_groups
}

CALL (ontology) {
  UNWIND [
    'ArchitectureProfile',
    'GraphMigration',
    'Organization',
    'Person',
    'Role',
    'Position',
    'Team',
    'OrganizationalUnit',
    'Department',
    'Capability',
    'CapabilityCapital',
    'EffectiveCapability',
    'Trust',
    'Predictability',
    'OrganizationalCapital',
    'OrganizationalEnergy',
    'Flow',
    'Topology',
    'FieldCondition',
    'Source',
    'Collection',
    'Evidence',
    'Observation',
    'Indicator',
    'Construct',
    'Assessment',
    'State',
    'StateEstimate',
    'StateTransition',
    'Event',
    'StaffingEvent',
    'Outcome',
    'OrganizationalHealth',
    'Vacancy',
    'Principle',
    'Invariant'
  ] AS graph_label
  OPTIONAL MATCH (ontology)-[:DEFINES_CONCEPT]->(
    concept:Concept {graph_label: graph_label}
  )
  WITH graph_label, concept
  WHERE concept IS NULL
    OR concept.definition IS NULL
    OR concept.distinction IS NULL
    OR concept.stable_identity_property IS NULL
    OR concept.temporal_semantics IS NULL
    OR concept.evidence_boundary IS NULL
    OR concept.privacy_boundary IS NULL
    OR concept.relationship_policy IS NULL
    OR concept.allowed_relationships IS NULL
    OR concept.steward IS NULL
    OR concept.version IS NULL
    OR concept.knowledge_lifecycle_state <> 'congruence'
  RETURN collect(graph_label) AS incomplete_core_concepts
}

CALL (ontology) {
  UNWIND [
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
  ] AS relationship_type
  OPTIONAL MATCH (ontology)-[:DEFINES_RELATIONSHIP]->(
    definition:RelationshipDefinition {
      graph_relationship_type: relationship_type
    }
  )
  WITH relationship_type, definition
  WHERE definition IS NULL
    OR definition.definition IS NULL
    OR definition.canonical_start_label IS NULL
    OR definition.canonical_end_label IS NULL
    OR definition.cardinality IS NULL
    OR definition.semantic_class IS NULL
    OR definition.assertion_metadata_required IS NULL
    OR definition.steward IS NULL
    OR definition.version IS NULL
    OR definition.knowledge_lifecycle_state <> 'congruence'
  RETURN collect(relationship_type) AS incomplete_core_relationships
}

CALL (ontology) {
  MATCH (observed)
  UNWIND labels(observed) AS graph_label
  WITH ontology, collect(DISTINCT graph_label) AS observed_labels
  MATCH (ontology)-[:DEFINES_CONCEPT]->(concept:Concept)
  WITH
    observed_labels,
    collect(DISTINCT concept.graph_label) AS registered_labels
  RETURN [
    graph_label IN observed_labels
    WHERE NOT graph_label IN registered_labels
  ] AS unregistered_labels
}

CALL (ontology) {
  MATCH ()-[relationship]->()
  WITH
    ontology,
    collect(DISTINCT type(relationship)) AS observed_types
  MATCH (ontology)-[:DEFINES_RELATIONSHIP]->(
    definition:RelationshipDefinition
  )
  WITH
    observed_types,
    collect(
      DISTINCT definition.graph_relationship_type
    ) AS registered_types
  RETURN [
    relationship_type IN observed_types
    WHERE NOT relationship_type IN registered_types
  ] AS unregistered_relationship_types
}

RETURN
  architecture_profile_count,
  applied_migration_count,
  department_count,
  department_organizational_unit_count,
  staffing_event_count,
  staffing_event_event_count,
  evidence_without_collection_provenance,
  analytical_assertion_count,
  analytical_assertions_missing_metadata,
  invalid_assertion_identity_groups,
  incomplete_core_concepts,
  incomplete_core_relationships,
  unregistered_labels,
  unregistered_relationship_types,
  architecture_profile_count = 1
    AND applied_migration_count = 1
    AND department_count = department_organizational_unit_count
    AND staffing_event_count = staffing_event_event_count
    AND evidence_without_collection_provenance = 0
    AND analytical_assertion_count > 0
    AND analytical_assertions_missing_metadata = 0
    AND invalid_assertion_identity_groups = 0
    AND size(incomplete_core_concepts) = 0
    AND size(incomplete_core_relationships) = 0
    AND size(unregistered_labels) = 0
    AND size(unregistered_relationship_types) = 0
    AS validation_passed;
