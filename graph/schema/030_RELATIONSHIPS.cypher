// OSI/PIA graph relationship catalogue v0.2.
//
// Descriptive only. Relationship direction, semantic class, cardinality, and
// maturity are governed by
// architecture/graph_ontology/REFERENCE_GRAPH_CONGRUENCE.md and the live
// RelationshipDefinition registries.

// ---------------------------------------------------------------------------
// PIA contracted evidence spine
// ---------------------------------------------------------------------------

// (:Participant)-[:HAS_SOURCE]->(:Source)
// (:Participant)-[:HAS_EXPERIENCE]->(:Experience)
// (:Source)-[:CONTAINS]->(:Evidence)
// (:Source)-[:DESCRIBES]->(:Experience)
// (:Evidence)-[:OCCURRED_IN]->(:Experience)
// (:Evidence)-[:SUPPORTS]->(:Capability)

// ---------------------------------------------------------------------------
// PIA experimental assessment layer
// ---------------------------------------------------------------------------

// (:Participant)-[:HAS_ASSESSMENT]->(:Assessment)
// (:Assessment)-[:EVALUATES]->(:Pattern)
// (:Assessment)-[:USES_CAPABILITY]->(:Capability)
// (:Assessment)-[:BASED_ON]->(:Evidence)
// (:Assessment)-[:SUPPORTS_IDENTITY]->(:IdentityHypothesis)
// (:Capability)-[:CONTRIBUTES_TO]->(:Pattern)

// ---------------------------------------------------------------------------
// OSI implemented structural and evidence relationships
// ---------------------------------------------------------------------------

// (:OrganizationalUnit)-[:PART_OF]->(:Organization)
// (:Position)-[:POSITION_IN]->(:OrganizationalUnit)
// (:Position)-[:POSITION_AT]->(:Organization)
// (:Person)-[:HELD_POSITION]->(:Position)
// (:Collection)-[:COLLECTED_FROM]->(:Source)
// (:Collection)-[:PRODUCED]->(:Evidence)
// (:Observation)-[:SUPPORTED_BY]->(:Evidence)
// (:Indicator)-[:DERIVED_FROM]->(:Observation)
// (:StateEstimate)-[:ESTIMATED_FROM]->(:Observation)
// (:StateEstimate)-[:SUPPORTED_BY_INDICATOR]->(:Indicator)

// ---------------------------------------------------------------------------
// OSI reviewable analysis, action, and learning
// ---------------------------------------------------------------------------

// (:Assessment)-[:ASSESSES]->(:Hypothesis)
// (:Prediction)-[:BASED_ON]->(:Assessment)
// (:StateEstimate)-[:INFERRED_FROM]->(:Indicator)
// (:DecisionSpace)-[:INFORMED_BY]->(:AnalyticalObject)
// (:Decision)-[:AUTHORIZED]->(:Intervention)
// (:Intervention)-[:PRODUCED_OUTCOME]->(:Outcome)
// (:Validation)-[:VALIDATES]->(:AnalyticalObject)
// (:PatternMemory)-[:LEARNED_FROM]->(:Validation)

// ---------------------------------------------------------------------------
// Shared graph governance
// ---------------------------------------------------------------------------

// (:Ontology)-[:CONFORMS_TO_ARCHITECTURE]->(:ArchitectureProfile)
// (:Ontology)-[:APPLIED_MIGRATION]->(:GraphMigration)
// (:Ontology)-[:DEFINES_CONCEPT]->(:Concept)
// (:Ontology)-[:DEFINES_RELATIONSHIP]->(:RelationshipDefinition)
