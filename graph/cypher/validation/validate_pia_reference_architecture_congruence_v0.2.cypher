// Validate PIA Reference architecture congruence v0.2.
// Target database: pia-reference

MATCH (ontology:Ontology {ontology_id: 'ontology:pia-reference'})

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
        '004_pia_reference_architecture_congruence'
    }
  )
  WHERE migration.status = 'applied'
  RETURN count(migration) AS applied_migration_count
}

CALL () {
  MATCH (participant:Participant)
  RETURN
    count(participant) AS participant_count,
    count(
      CASE
        WHEN participant.participant_id IS NULL
          OR participant.status IS NULL
          OR participant.consent_status IS NULL
          OR participant.created_at IS NULL
          OR participant.updated_at IS NULL
        THEN 1
      END
    ) AS participants_missing_contract_metadata,
    count(
      CASE
        WHEN participant.consent_status IN [
          'pending',
          'limited'
        ]
        THEN 1
      END
    ) AS participants_requiring_consent_review
}

CALL () {
  MATCH (source:Source)
  RETURN
    count(source) AS source_count,
    count(
      CASE
        WHEN source.source_id IS NULL
          OR source.source_type IS NULL
          OR source.title IS NULL
          OR source.confidentiality IS NULL
          OR (
            source.collected_at IS NULL
            AND source.collected_at_status <> 'unknown'
          )
        THEN 1
      END
    ) AS sources_missing_contract_metadata,
    count(
      CASE
        WHEN source.collected_at_status = 'unknown' THEN 1
      END
    ) AS sources_requiring_collection_time_review
}

CALL () {
  MATCH (experience:Experience)
  RETURN
    count(experience) AS experience_count,
    count(
      CASE
        WHEN experience.experience_id IS NULL
          OR experience.experience_type IS NULL
          OR experience.title IS NULL
          OR experience.date_status IS NULL
        THEN 1
      END
    ) AS experiences_missing_contract_metadata,
    count(
      CASE
        WHEN experience.date_status = 'unknown' THEN 1
      END
    ) AS experiences_requiring_date_review
}

CALL () {
  MATCH (evidence:Evidence)
  RETURN
    count(evidence) AS evidence_count,
    count(
      CASE
        WHEN evidence.evidence_id IS NULL
          OR evidence.evidence_text IS NULL
          OR evidence.evidence_type IS NULL
          OR evidence.extraction_method IS NULL
          OR evidence.fidelity_status IS NULL
          OR evidence.review_status IS NULL
          OR evidence.created_at IS NULL
        THEN 1
      END
    ) AS evidence_missing_contract_metadata,
    count(
      CASE
        WHEN evidence.metadata_review_status = 'required'
        THEN 1
      END
    ) AS evidence_requiring_metadata_review
}

CALL () {
  MATCH (capability:Capability)
  RETURN
    count(capability) AS capability_count,
    count(
      CASE
        WHEN capability.capability_id IS NULL
          OR capability.capability_name IS NULL
          OR capability.definition IS NULL
          OR capability.status IS NULL
          OR capability.ontology_version IS NULL
        THEN 1
      END
    ) AS capabilities_missing_contract_metadata,
    count(
      CASE
        WHEN capability.definition_status =
          'provisional_legacy_alignment'
        THEN 1
      END
    ) AS capabilities_requiring_definition_review
}

CALL () {
  MATCH (source:Source)
  WHERE NOT (:Participant)-[:HAS_SOURCE]->(source)
  RETURN count(source) AS orphan_sources
}

CALL () {
  MATCH (experience:Experience)
  WHERE NOT (:Participant)-[:HAS_EXPERIENCE]->(experience)
  RETURN count(experience) AS orphan_experiences
}

CALL () {
  MATCH (evidence:Evidence)
  WHERE NOT (:Source)-[:CONTAINS]->(evidence)
  RETURN count(evidence) AS evidence_without_source
}

CALL () {
  MATCH (:Evidence)-[mapping:SUPPORTS]->(:Capability)
  RETURN
    count(mapping) AS mapping_count,
    count(
      CASE
        WHEN mapping.mapping_id IS NULL
          OR mapping.confidence IS NULL
          OR mapping.confidence < 0
          OR mapping.confidence > 1
          OR mapping.confidence_basis IS NULL
          OR mapping.proposed_by IS NULL
          OR mapping.review_status IS NULL
          OR mapping.created_at IS NULL
          OR mapping.assertion_id IS NULL
          OR mapping.assertion_basis IS NULL
          OR mapping.relationship_semantic_class <>
            'analytical_assertion'
        THEN 1
      END
    ) AS mappings_missing_assertion_metadata
}

CALL () {
  MATCH (:Evidence)-[mapping:SUPPORTS]->(:Capability)
  WITH mapping.mapping_id AS mapping_id, count(*) AS occurrences
  WHERE mapping_id IS NULL OR occurrences > 1
  RETURN count(*) AS invalid_mapping_identity_groups
}

CALL () {
  MATCH (:Assessment)-[legacy:USES]->(:Capability)
  RETURN count(legacy) AS legacy_uses_relationships
}

CALL () {
  MATCH (:Assessment)-[canonical:USES_CAPABILITY]->(:Capability)
  RETURN count(canonical) AS uses_capability_relationships
}

CALL () {
  MATCH (:Source)-[legacy:CONTAINS]->(:Experience)
  RETURN count(legacy) AS overloaded_contains_relationships
}

CALL () {
  MATCH (:Source)-[canonical:DESCRIBES]->(:Experience)
  RETURN count(canonical) AS source_describes_experience_relationships
}

CALL (ontology) {
  MATCH (definition:RelationshipDefinition {
    relationship_definition_id:
      'relationship-definition:pia-reference:SUPPORTS'
  })-[:USES_CONFIDENCE_MODEL]->(
    model:ConfidenceModel {
      confidence_model_id:
        'confidence:pia-reference:evidence-capability-numeric-v1'
    }
  )
  WHERE model.property_name = 'confidence'
    AND model.minimum = 0.0
    AND model.maximum = 1.0
  RETURN count(model) AS numeric_confidence_model_count
}

CALL (ontology) {
  UNWIND [
    'ArchitectureProfile',
    'GraphMigration',
    'Participant',
    'Source',
    'Experience',
    'Evidence',
    'Capability',
    'Pattern',
    'Assessment',
    'Observation',
    'IdentityHypothesis',
    'Representation'
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
    'HAS_SOURCE',
    'HAS_EXPERIENCE',
    'CONTAINS',
    'DESCRIBES',
    'OCCURRED_IN',
    'SUPPORTS',
    'CONTRIBUTES_TO',
    'HAS_ASSESSMENT',
    'EVALUATES',
    'USES_CAPABILITY',
    'BASED_ON',
    'SUPPORTS_IDENTITY'
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
  participant_count,
  participants_missing_contract_metadata,
  participants_requiring_consent_review,
  source_count,
  sources_missing_contract_metadata,
  sources_requiring_collection_time_review,
  experience_count,
  experiences_missing_contract_metadata,
  experiences_requiring_date_review,
  evidence_count,
  evidence_missing_contract_metadata,
  evidence_requiring_metadata_review,
  capability_count,
  capabilities_missing_contract_metadata,
  capabilities_requiring_definition_review,
  orphan_sources,
  orphan_experiences,
  evidence_without_source,
  mapping_count,
  mappings_missing_assertion_metadata,
  invalid_mapping_identity_groups,
  legacy_uses_relationships,
  uses_capability_relationships,
  overloaded_contains_relationships,
  source_describes_experience_relationships,
  numeric_confidence_model_count,
  incomplete_core_concepts,
  incomplete_core_relationships,
  unregistered_labels,
  unregistered_relationship_types,
  architecture_profile_count = 1
    AND applied_migration_count = 1
    AND participants_missing_contract_metadata = 0
    AND sources_missing_contract_metadata = 0
    AND experiences_missing_contract_metadata = 0
    AND evidence_missing_contract_metadata = 0
    AND capabilities_missing_contract_metadata = 0
    AND orphan_sources = 0
    AND orphan_experiences = 0
    AND evidence_without_source = 0
    AND mapping_count > 0
    AND mappings_missing_assertion_metadata = 0
    AND invalid_mapping_identity_groups = 0
    AND legacy_uses_relationships = 0
    AND uses_capability_relationships > 0
    AND overloaded_contains_relationships = 0
    AND source_describes_experience_relationships > 0
    AND numeric_confidence_model_count = 1
    AND size(incomplete_core_concepts) = 0
    AND size(incomplete_core_relationships) = 0
    AND size(unregistered_labels) = 0
    AND size(unregistered_relationship_types) = 0
    AS validation_passed;
