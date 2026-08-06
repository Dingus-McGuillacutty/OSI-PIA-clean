// OSI Reference meta-ontology registry v0.1
//
// Target database: osi-reference
// Compatibility: additive; Neo4j 5+ / Cypher 25
// Recovery: restore the pre-migration backup, or remove only objects marked
//           managed_by = '001_osi_reference_meta_ontology' through a reviewed
//           recovery migration.
//
// This migration registers the live graph vocabulary. It does not relabel,
// rewrite, or delete existing domain data, and registry presence does not make
// an ontology item canonical.

CREATE CONSTRAINT osi_meta_ontology_id_unique IF NOT EXISTS
FOR (n:Ontology)
REQUIRE n.ontology_id IS UNIQUE;

CREATE CONSTRAINT osi_meta_concept_id_unique IF NOT EXISTS
FOR (n:Concept)
REQUIRE n.concept_id IS UNIQUE;

CREATE CONSTRAINT osi_meta_relationship_definition_id_unique IF NOT EXISTS
FOR (n:RelationshipDefinition)
REQUIRE n.relationship_definition_id IS UNIQUE;

CREATE CONSTRAINT osi_meta_lifecycle_state_id_unique IF NOT EXISTS
FOR (n:LifecycleState)
REQUIRE n.lifecycle_state_id IS UNIQUE;

CREATE CONSTRAINT osi_meta_knowledge_state_id_unique IF NOT EXISTS
FOR (n:KnowledgeState)
REQUIRE n.knowledge_state_id IS UNIQUE;

CREATE CONSTRAINT osi_meta_confidence_model_id_unique IF NOT EXISTS
FOR (n:ConfidenceModel)
REQUIRE n.confidence_model_id IS UNIQUE;

MERGE (ontology:Ontology {ontology_id: 'ontology:osi-reference'})
ON CREATE SET
  ontology.name = 'OSI Reference Ontology',
  ontology.version = '0.1.0',
  ontology.scope = 'osi-reference',
  ontology.knowledge_lifecycle_state = 'formulation',
  ontology.ontology_status = 'working',
  ontology.implementation_status = 'implemented',
  ontology.description =
    'Working registry for the concepts, relationships, lifecycle, knowledge state, and confidence vocabulary observed in the OSI Reference graph.',
  ontology.source_ref = 'ontology/META_ONTOLOGY.md',
  ontology.managed_by = '001_osi_reference_meta_ontology',
  ontology.created_at = datetime()
WITH ontology

CALL (ontology) {
  UNWIND [
    {
      code: 'observation',
      name: 'Observation',
      ordinal: 1,
      description: 'Source-grounded material has been recorded without promoting an interpretation.'
    },
    {
      code: 'exploration',
      name: 'Exploration',
      ordinal: 2,
      description: 'Possible patterns and questions are being explored.'
    },
    {
      code: 'formulation',
      name: 'Formulation',
      ordinal: 3,
      description: 'A reviewable concept, relationship, or model is being stated.'
    },
    {
      code: 'congruence',
      name: 'Congruence',
      ordinal: 4,
      description: 'The formulation is being checked against neighboring concepts and system commitments.'
    },
    {
      code: 'validation',
      name: 'Validation',
      ordinal: 5,
      description: 'Evidence, tests, and counterexamples are being used to evaluate the formulation.'
    },
    {
      code: 'promotion',
      name: 'Promotion',
      ordinal: 6,
      description: 'An accepted formulation is being promoted into governed use.'
    },
    {
      code: 'stewardship',
      name: 'Stewardship',
      ordinal: 7,
      description: 'The promoted item is monitored, maintained, superseded, or retired.'
    }
  ] AS state_data
  MERGE (state:LifecycleState {
    lifecycle_state_id: 'lifecycle:knowledge:' + state_data.code
  })
  ON CREATE SET
    state.name = state_data.name,
    state.code = state_data.code,
    state.ordinal = state_data.ordinal,
    state.description = state_data.description,
    state.dimension = 'knowledge_lifecycle',
    state.managed_by = '001_osi_reference_meta_ontology',
    state.created_at = datetime()
  MERGE (ontology)-[:HAS_LIFECYCLE_STATE]->(state)
  WITH ontology, count(state) AS lifecycle_state_count
  UNWIND [
    ['observation', 'exploration'],
    ['exploration', 'formulation'],
    ['formulation', 'congruence'],
    ['congruence', 'validation'],
    ['validation', 'promotion'],
    ['promotion', 'stewardship']
  ] AS transition
  MATCH (from:LifecycleState {
    lifecycle_state_id: 'lifecycle:knowledge:' + transition[0]
  })
  MATCH (to:LifecycleState {
    lifecycle_state_id: 'lifecycle:knowledge:' + transition[1]
  })
  MERGE (from)-[:MAY_PROGRESS_TO]->(to)
  RETURN lifecycle_state_count, count(*) AS lifecycle_transition_count
}

CALL (ontology) {
  MATCH (current:LifecycleState {
    lifecycle_state_id: 'lifecycle:knowledge:formulation'
  })
  MERGE (ontology)-[:CURRENT_LIFECYCLE_STATE]->(current)
  RETURN count(current) AS current_lifecycle_state_count
}

CALL (ontology) {
  UNWIND [
    {
      code: 'proposed',
      name: 'Proposed',
      ordinal: 1,
      description: 'Suggested for shared use but not yet accepted.'
    },
    {
      code: 'working',
      name: 'Working',
      ordinal: 2,
      description: 'Actively used for design or evaluation without canonical authority.'
    },
    {
      code: 'canonical',
      name: 'Canonical',
      ordinal: 3,
      description: 'Accepted as the governed shared definition.'
    },
    {
      code: 'deprecated',
      name: 'Deprecated',
      ordinal: 4,
      description: 'Still interpretable but no longer preferred for new use.'
    },
    {
      code: 'retired',
      name: 'Retired',
      ordinal: 5,
      description: 'Removed from active use while retained for history and compatibility.'
    }
  ] AS state_data
  MERGE (state:KnowledgeState {
    knowledge_state_id: 'knowledge-state:ontology:' + state_data.code
  })
  ON CREATE SET
    state.name = state_data.name,
    state.code = state_data.code,
    state.ordinal = state_data.ordinal,
    state.description = state_data.description,
    state.dimension = 'ontology_status',
    state.managed_by = '001_osi_reference_meta_ontology',
    state.created_at = datetime()
  MERGE (ontology)-[:HAS_KNOWLEDGE_STATE]->(state)
  WITH ontology, count(state) AS knowledge_state_count
  UNWIND [
    ['proposed', 'working'],
    ['working', 'canonical'],
    ['canonical', 'deprecated'],
    ['deprecated', 'retired']
  ] AS transition
  MATCH (from:KnowledgeState {
    knowledge_state_id: 'knowledge-state:ontology:' + transition[0]
  })
  MATCH (to:KnowledgeState {
    knowledge_state_id: 'knowledge-state:ontology:' + transition[1]
  })
  MERGE (from)-[:MAY_CHANGE_TO]->(to)
  RETURN knowledge_state_count, count(*) AS knowledge_transition_count
}

CALL (ontology) {
  MATCH (current:KnowledgeState {
    knowledge_state_id: 'knowledge-state:ontology:working'
  })
  MERGE (ontology)-[:CURRENT_KNOWLEDGE_STATE]->(current)
  RETURN count(current) AS current_knowledge_state_count
}

CALL (ontology) {
  MERGE (model:ConfidenceModel {
    confidence_model_id: 'confidence:osi-reference:qualitative-v1'
  })
  ON CREATE SET
    model.name = 'OSI Reference Qualitative Confidence',
    model.version = '1.0',
    model.property_name = 'confidence_level',
    model.method = 'qualitative_ordinal',
    model.allowed_levels = ['very_low', 'low', 'moderate', 'high'],
    model.observed_scoped_values = [
      'moderate_high_within_test_fixture',
      'high_within_test_fixture'
    ],
    model.enforcement_status = 'documented_not_enforced',
    model.description =
      'Documents the qualitative confidence vocabulary already present in the OSI Reference graph without converting confidence into a person score.',
    model.managed_by = '001_osi_reference_meta_ontology',
    model.created_at = datetime()
  MERGE (ontology)-[:USES_CONFIDENCE_MODEL]->(model)
  RETURN count(model) AS confidence_model_count
}

CALL (ontology) {
  MERGE (concept:Concept {
    concept_id: 'concept:osi-reference:Concept'
  })
  ON CREATE SET
    concept.name = 'Concept',
    concept.graph_label = 'Concept',
    concept.item_kind = 'concept',
    concept.scope = 'osi-reference',
    concept.knowledge_lifecycle_state = 'formulation',
    concept.ontology_status = 'working',
    concept.implementation_status = 'implemented',
    concept.registration_basis = 'meta_ontology_bootstrap',
    concept.source_ref = 'ontology/META_ONTOLOGY.md',
    concept.managed_by = '001_osi_reference_meta_ontology',
    concept.created_at = datetime()
  MERGE (ontology)-[:DEFINES_CONCEPT]->(concept)
  RETURN count(concept) AS concept_bootstrap_count
}

CALL (ontology) {
  MERGE (definition:RelationshipDefinition {
    relationship_definition_id:
      'relationship-definition:osi-reference:DEFINES_RELATIONSHIP'
  })
  ON CREATE SET
    definition.name = 'DEFINES_RELATIONSHIP',
    definition.graph_relationship_type = 'DEFINES_RELATIONSHIP',
    definition.direction = 'outbound',
    definition.scope = 'osi-reference',
    definition.knowledge_lifecycle_state = 'formulation',
    definition.ontology_status = 'working',
    definition.implementation_status = 'implemented',
    definition.registration_basis = 'meta_ontology_bootstrap',
    definition.source_ref = 'ontology/META_ONTOLOGY.md',
    definition.managed_by = '001_osi_reference_meta_ontology',
    definition.created_at = datetime()
  MERGE (ontology)-[:DEFINES_RELATIONSHIP]->(definition)
  RETURN count(definition) AS relationship_bootstrap_count
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
    concept.registration_basis = 'observed_live_graph_label',
    concept.observed_node_count_at_registration = observed_node_count,
    concept.source_ref = 'ontology/META_ONTOLOGY.md',
    concept.managed_by = '001_osi_reference_meta_ontology',
    concept.created_at = datetime()
  MERGE (ontology)-[:DEFINES_CONCEPT]->(concept)
  RETURN count(concept) AS registered_concept_count
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
      'relationship-definition:osi-reference:' + relationship_type
  })
  ON CREATE SET
    definition.name = relationship_type,
    definition.graph_relationship_type = relationship_type,
    definition.direction = 'outbound',
    definition.scope = 'osi-reference',
    definition.knowledge_lifecycle_state = 'formulation',
    definition.ontology_status = 'working',
    definition.implementation_status = 'implemented',
    definition.registration_basis = 'observed_live_graph_relationship',
    definition.source_ref = 'ontology/META_ONTOLOGY.md',
    definition.managed_by = '001_osi_reference_meta_ontology',
    definition.created_at = datetime()
  SET
    definition.observed_start_labels = observed_start_labels,
    definition.observed_end_labels = observed_end_labels
  MERGE (ontology)-[:DEFINES_RELATIONSHIP]->(definition)
  RETURN count(definition) AS registered_relationship_count
}

RETURN
  ontology.ontology_id AS ontology_id,
  lifecycle_state_count,
  lifecycle_transition_count,
  current_lifecycle_state_count,
  knowledge_state_count,
  knowledge_transition_count,
  current_knowledge_state_count,
  confidence_model_count,
  registered_concept_count,
  registered_relationship_count;
