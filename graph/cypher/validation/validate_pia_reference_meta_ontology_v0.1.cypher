// Validate the PIA Reference meta-ontology registry v0.1.
// Target database: pia-reference
//
// A passing result has `validation_passed = true` and no unregistered labels
// or relationship types.

MATCH (ontology:Ontology {ontology_id: 'ontology:pia-reference'})

CALL (ontology) {
  MATCH (ontology)-[:HAS_LIFECYCLE_STATE]->(state:LifecycleState)
  RETURN count(state) AS lifecycle_state_count
}

CALL (ontology) {
  MATCH (ontology)-[:HAS_KNOWLEDGE_STATE]->(state:KnowledgeState)
  RETURN count(state) AS knowledge_state_count
}

CALL (ontology) {
  MATCH (ontology)-[:USES_CONFIDENCE_MODEL]->(
    model:ConfidenceModel {
      confidence_model_id:
        'confidence:pia-reference:qualitative-v1'
    }
  )
  RETURN count(model) AS confidence_model_count
}

CALL (ontology) {
  MATCH (ontology)-[:CURRENT_LIFECYCLE_STATE]->(state:LifecycleState)
  RETURN count(state) AS current_lifecycle_state_count
}

CALL (ontology) {
  MATCH (ontology)-[:CURRENT_KNOWLEDGE_STATE]->(state:KnowledgeState)
  RETURN count(state) AS current_knowledge_state_count
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
  WITH ontology, collect(DISTINCT type(relationship)) AS observed_types
  MATCH (ontology)-[:DEFINES_RELATIONSHIP]->
    (definition:RelationshipDefinition)
  WITH
    observed_types,
    collect(DISTINCT definition.graph_relationship_type) AS registered_types
  RETURN [
    relationship_type IN observed_types
    WHERE NOT relationship_type IN registered_types
  ] AS unregistered_relationship_types
}

CALL () {
  SHOW CONSTRAINTS YIELD labelsOrTypes
  UNWIND labelsOrTypes AS graph_label
  RETURN collect(DISTINCT graph_label) AS schema_labels
}

CALL (ontology, schema_labels) {
  MATCH (ontology)-[:DEFINES_CONCEPT]->(concept:Concept)
  WITH
    schema_labels,
    collect(DISTINCT concept.graph_label) AS registered_labels
  RETURN [
    graph_label IN schema_labels
    WHERE NOT graph_label IN registered_labels
  ] AS unregistered_schema_labels
}

CALL () {
  SHOW CONSTRAINTS YIELD name
  WHERE name IN [
    'pia_meta_ontology_id_unique',
    'pia_meta_concept_id_unique',
    'pia_meta_relationship_definition_id_unique',
    'pia_meta_lifecycle_state_id_unique',
    'pia_meta_knowledge_state_id_unique',
    'pia_meta_confidence_model_id_unique'
  ]
  RETURN count(name) AS meta_constraint_count
}

RETURN
  lifecycle_state_count,
  knowledge_state_count,
  confidence_model_count,
  current_lifecycle_state_count,
  current_knowledge_state_count,
  meta_constraint_count,
  unregistered_labels,
  unregistered_schema_labels,
  unregistered_relationship_types,
  lifecycle_state_count = 7
    AND knowledge_state_count = 5
    AND confidence_model_count = 1
    AND current_lifecycle_state_count = 1
    AND current_knowledge_state_count = 1
    AND meta_constraint_count = 6
    AND size(unregistered_labels) = 0
    AND size(unregistered_schema_labels) = 0
    AND size(unregistered_relationship_types) = 0
    AS validation_passed;
