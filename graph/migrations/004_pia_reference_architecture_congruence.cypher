// PIA Reference architecture congruence v0.2
//
// Target database: pia-reference
// Compatibility: additive property aliases plus two scoped relationship-type
//                corrections; Neo4j 5+ / Cypher 25
// Recovery: restore the pre-migration backup. The corrected relationships
//           retain migrated_from_relationship_type and all legacy properties,
//           so a reviewed reverse migration can reconstruct USES and the
//           Source -> Experience use of CONTAINS if required.
//
// This migration:
// - backfills canonical v0.1 contract property names without deleting legacy
//   properties;
// - preserves unknown metadata explicitly rather than inventing certainty;
// - makes every Evidence -> Capability SUPPORTS assertion reviewable;
// - corrects Assessment -[:USES]-> Capability to USES_CAPABILITY;
// - corrects Source -[:CONTAINS]-> Experience to DESCRIBES, leaving CONTAINS
//   with the contracted Source -> Evidence meaning;
// - declares the bounded PIA projection in the working registry;
// - links the database to the shared OSI/PIA reference architecture profile.

CREATE CONSTRAINT pia_architecture_profile_id_unique IF NOT EXISTS
FOR (n:ArchitectureProfile)
REQUIRE n.profile_id IS UNIQUE;

CREATE CONSTRAINT pia_graph_migration_id_unique IF NOT EXISTS
FOR (n:GraphMigration)
REQUIRE n.migration_id IS UNIQUE;

CREATE INDEX pia_evidence_review_status IF NOT EXISTS
FOR (n:Evidence)
ON (n.review_status);

CREATE INDEX pia_source_confidentiality IF NOT EXISTS
FOR (n:Source)
ON (n.confidentiality);

MERGE (migration:GraphMigration {
  migration_id: '004_pia_reference_architecture_congruence'
})
ON CREATE SET
  migration.name = 'PIA Reference architecture congruence',
  migration.version = '0.2.0',
  migration.target_database = 'pia-reference',
  migration.started_at = datetime(),
  migration.managed_by =
    '004_pia_reference_architecture_congruence'
SET migration.status = 'running'
WITH migration

CALL (migration) {
  MATCH (participant:Participant)
  SET participant.display_name =
        coalesce(
          participant.display_name,
          participant.label,
          participant.name
        ),
      participant.created_at =
        coalesce(participant.created_at, participant.created),
      participant.updated_at =
        coalesce(
          participant.updated_at,
          participant.updated,
          participant.created_at,
          participant.created
        )
  SET participant.consent_status_basis =
        CASE
          WHEN participant.consent_status IS NULL
          THEN 'legacy_not_recorded'
          ELSE coalesce(
            participant.consent_status_basis,
            'source_record'
          )
        END,
      participant.consent_status =
        coalesce(participant.consent_status, 'pending'),
      participant.contract_alignment_version = '0.2.0',
      participant.aligned_by =
        '004_pia_reference_architecture_congruence'
  RETURN count(participant) AS participants_aligned
}

CALL (migration) {
  MATCH (source:Source)
  SET source.source_type_legacy =
        CASE
          WHEN source.source_type IN [
            'resume',
            'cover_letter',
            'interview',
            'questionnaire',
            'portfolio',
            'record',
            'other'
          ] THEN source.source_type_legacy
          ELSE coalesce(source.source_type_legacy, source.source_type)
        END,
      source.source_type =
        CASE
          WHEN source.source_type IN [
            'resume',
            'cover_letter',
            'interview',
            'questionnaire',
            'portfolio',
            'record',
            'other'
          ] THEN source.source_type
          ELSE 'other'
        END,
      source.title =
        coalesce(
          source.title,
          source.name,
          source.label,
          source.filename
        ),
      source.file_reference =
        coalesce(source.file_reference, source.filename),
      source.collected_at =
        coalesce(
          source.collected_at,
          source.imported,
          source.created
        ),
      source.confidentiality =
        coalesce(source.confidentiality, 'participant_private')
  SET source.collected_at_status =
        CASE
          WHEN source.collected_at IS NULL THEN 'unknown'
          ELSE 'known'
        END,
      source.contract_alignment_version = '0.2.0',
      source.aligned_by =
        '004_pia_reference_architecture_congruence'
  RETURN count(source) AS sources_aligned
}

CALL (migration) {
  MATCH (experience:Experience)
  SET experience.experience_type_legacy =
        CASE
          WHEN experience.experience_type IN [
            'employment',
            'education',
            'project',
            'service',
            'creative_work',
            'other'
          ] THEN experience.experience_type_legacy
          ELSE coalesce(
            experience.experience_type_legacy,
            experience.experience_type
          )
        END,
      experience.experience_type =
        CASE experience.experience_type
          WHEN 'position' THEN 'employment'
          WHEN 'education' THEN 'education'
          WHEN 'project' THEN 'project'
          WHEN 'employment' THEN 'employment'
          WHEN 'service' THEN 'service'
          WHEN 'creative_work' THEN 'creative_work'
          ELSE 'other'
        END,
      experience.title =
        coalesce(
          experience.title,
          experience.label,
          experience.role
        ),
      experience.organization_name =
        coalesce(
          experience.organization_name,
          experience.organization
        ),
      experience.start_date =
        coalesce(
          experience.start_date,
          experience.started_on
        ),
      experience.end_date =
        coalesce(
          experience.end_date,
          experience.finished_on
        )
  SET experience.date_status =
        coalesce(
          experience.date_status,
          CASE
            WHEN experience.current = true THEN 'current'
            WHEN experience.start_date IS NOT NULL
              AND experience.end_date IS NOT NULL THEN 'known'
            WHEN experience.start_date IS NOT NULL
              OR experience.end_date IS NOT NULL THEN 'partial'
            ELSE 'unknown'
          END
        ),
      experience.date_status_basis =
        coalesce(
          experience.date_status_basis,
          'derived_from_legacy_temporal_fields'
        ),
      experience.contract_alignment_version = '0.2.0',
      experience.aligned_by =
        '004_pia_reference_architecture_congruence'
  RETURN count(experience) AS experiences_aligned
}

CALL (migration) {
  MATCH (evidence:Evidence)
  SET evidence.evidence_type_legacy =
        CASE
          WHEN evidence.evidence_type IN [
            'activity',
            'responsibility',
            'output',
            'achievement',
            'event',
            'condition',
            'statement',
            'other'
          ] THEN evidence.evidence_type_legacy
          ELSE coalesce(
            evidence.evidence_type_legacy,
            evidence.evidence_type
          )
        END,
      evidence.evidence_type =
        CASE evidence.evidence_type
          WHEN 'demonstrated_action' THEN 'activity'
          WHEN 'project_outcome' THEN 'achievement'
          WHEN 'publication' THEN 'output'
          WHEN 'recognition' THEN 'achievement'
          WHEN 'activity' THEN 'activity'
          WHEN 'responsibility' THEN 'responsibility'
          WHEN 'output' THEN 'output'
          WHEN 'achievement' THEN 'achievement'
          WHEN 'event' THEN 'event'
          WHEN 'condition' THEN 'condition'
          WHEN 'other' THEN 'other'
          ELSE 'statement'
        END,
      evidence.evidence_text =
        coalesce(evidence.evidence_text, evidence.text),
      evidence.extraction_method =
        coalesce(evidence.extraction_method, 'unknown'),
      evidence.fidelity_status =
        coalesce(evidence.fidelity_status, 'unknown'),
      evidence.review_status =
        coalesce(
          evidence.review_status,
          CASE evidence.status
            WHEN 'accepted' THEN 'reviewed'
            WHEN 'reviewed' THEN 'reviewed'
            ELSE 'unreviewed'
          END
        ),
      evidence.created_at =
        coalesce(
          evidence.created_at,
          evidence.created,
          datetime()
        )
  SET evidence.created_at_basis =
        coalesce(
          evidence.created_at_basis,
          CASE
            WHEN evidence.created IS NULL
            THEN 'migration_backfill'
            ELSE 'legacy_created_property'
          END
        ),
      evidence.metadata_review_status =
        CASE
          WHEN evidence.extraction_method = 'unknown'
            OR evidence.fidelity_status = 'unknown'
          THEN 'required'
          ELSE coalesce(
            evidence.metadata_review_status,
            'not_required'
          )
        END,
      evidence.contract_alignment_version = '0.2.0',
      evidence.aligned_by =
        '004_pia_reference_architecture_congruence'
  RETURN count(evidence) AS evidence_aligned
}

CALL (migration) {
  MATCH (capability:Capability)
  SET capability.capability_name =
        coalesce(
          capability.capability_name,
          capability.name,
          capability.label
        ),
      capability.name =
        coalesce(
          capability.name,
          capability.capability_name,
          capability.label
        ),
      capability.status_legacy =
        CASE
          WHEN capability.status = 'candidate'
          THEN coalesce(capability.status_legacy, capability.status)
          ELSE capability.status_legacy
        END,
      capability.status =
        CASE
          WHEN capability.status = 'candidate' THEN 'working'
          WHEN capability.status IN [
            'proposed',
            'working',
            'established',
            'deprecated'
          ] THEN capability.status
          ELSE 'proposed'
        END,
      capability.ontology_version =
        coalesce(
          capability.ontology_version,
          '0.2.0-working'
        ),
      capability.definition =
        coalesce(
          capability.definition,
          'Working capability concept: ' +
          coalesce(
            capability.capability_name,
            capability.name,
            capability.label
          ) +
          '. Operational criteria require ontology review before promotion.'
        )
  SET capability.definition_status =
        coalesce(
          capability.definition_status,
          'provisional_legacy_alignment'
        ),
      capability.contract_alignment_version = '0.2.0',
      capability.aligned_by =
        '004_pia_reference_architecture_congruence'
  RETURN count(capability) AS capabilities_aligned
}

CALL (migration) {
  MATCH (assessment:Assessment)
  SET assessment.created_at =
        coalesce(
          assessment.created_at,
          assessment.created,
          datetime()
        ),
      assessment.updated_at =
        coalesce(
          assessment.updated_at,
          assessment.updated
        ),
      assessment.contract_alignment_version = '0.2.0',
      assessment.aligned_by =
        '004_pia_reference_architecture_congruence'
  RETURN count(assessment) AS assessments_aligned
}

CALL (migration) {
  MATCH (:Evidence)-[mapping:SUPPORTS]->(:Capability)
  WITH
    mapping,
    startNode(mapping) AS evidence,
    endNode(mapping) AS capability
  SET mapping.mapping_id =
        coalesce(
          mapping.mapping_id,
          'mapping:' + evidence.evidence_id +
          ':' + capability.capability_id
        ),
      mapping.confidence_basis =
        coalesce(
          mapping.confidence_basis,
          'Legacy quantitative mapping preserved during architecture alignment; the original rationale was not recorded and requires review.'
        ),
      mapping.proposed_by =
        coalesce(
          mapping.proposed_by,
          mapping.analyst,
          'legacy_graph_alignment'
        ),
      mapping.review_status =
        coalesce(
          mapping.review_status,
          CASE mapping.status
            WHEN 'accepted' THEN 'accepted'
            WHEN 'reviewed' THEN 'accepted'
            WHEN 'candidate' THEN 'needs_review'
            ELSE 'proposed'
          END
        ),
      mapping.created_at =
        coalesce(
          mapping.created_at,
          mapping.created,
          datetime()
        ),
      mapping.assertion_id =
        coalesce(
          mapping.assertion_id,
          mapping.mapping_id,
          'mapping:' + evidence.evidence_id +
          ':' + capability.capability_id
        ),
      mapping.relationship_semantic_class =
        'analytical_assertion',
      mapping.human_review_required =
        CASE
          WHEN mapping.review_status = 'accepted' THEN false
          ELSE true
        END,
      mapping.created_at_basis =
        coalesce(
          mapping.created_at_basis,
          CASE
            WHEN mapping.created IS NULL
            THEN 'migration_backfill'
            ELSE 'legacy_created_property'
          END
        ),
      mapping.contract_alignment_version = '0.2.0'
  WITH mapping
  SET mapping.assertion_basis =
        coalesce(
          mapping.assertion_basis,
          mapping.confidence_basis
        )
  RETURN count(mapping) AS mappings_aligned
}

CALL (migration) {
  MATCH (assessment:Assessment)-[legacy:USES]->(capability:Capability)
  MERGE (assessment)-[canonical:USES_CAPABILITY]->(capability)
  SET canonical += properties(legacy),
      canonical.created_at =
        coalesce(
          canonical.created_at,
          canonical.created,
          datetime()
        ),
      canonical.relationship_semantic_class =
        'analytical_reference',
      canonical.migrated_from_relationship_type = 'USES',
      canonical.migrated_at = datetime(),
      canonical.alignment_version = '0.2.0'
  DELETE legacy
  RETURN count(canonical) AS uses_capability_relationships_corrected
}

CALL (migration) {
  MATCH (source:Source)-[legacy:CONTAINS]->(experience:Experience)
  MERGE (source)-[canonical:DESCRIBES]->(experience)
  SET canonical += properties(legacy),
      canonical.created_at =
        coalesce(
          canonical.created_at,
          canonical.created,
          datetime()
        ),
      canonical.relationship_semantic_class = 'context_fact',
      canonical.migrated_from_relationship_type = 'CONTAINS',
      canonical.migrated_at = datetime(),
      canonical.alignment_version = '0.2.0'
  DELETE legacy
  RETURN count(canonical) AS source_experience_relationships_corrected
}

CALL (migration) {
  MATCH ()-[relationship:
    HAS_SOURCE|
    HAS_EXPERIENCE|
    CONTAINS|
    OCCURRED_IN|
    HAS_ASSESSMENT|
    EVALUATES|
    USES_CAPABILITY|
    BASED_ON|
    CONTRIBUTES_TO|
    DESCRIBES
  ]->()
  SET relationship.created_at =
        coalesce(
          relationship.created_at,
          relationship.created,
          datetime()
        ),
      relationship.created_at_basis =
        coalesce(
          relationship.created_at_basis,
          CASE
            WHEN relationship.created IS NULL
            THEN 'migration_backfill'
            ELSE 'legacy_created_property'
          END
        ),
      relationship.contract_alignment_version = '0.2.0'
  RETURN count(relationship) AS contextual_relationships_aligned
}

MATCH (ontology:Ontology {ontology_id: 'ontology:pia-reference'})
SET ontology.version = '0.2.0',
    ontology.architecture_alignment_state = 'congruence',
    ontology.aligned_at = datetime(),
    ontology.aligned_by =
      '004_pia_reference_architecture_congruence'
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
    'PIA evaluates evidence supporting bounded conclusions; it does not score the person as a total object.',
  profile.privacy_boundary =
    'Use minimum necessary data, purpose limitation, consent, correction, and reviewed access.',
  profile.source_refs = [
    'architecture/graph_ontology/REFERENCE_GRAPH_CONGRUENCE.md',
    'ontology/META_ONTOLOGY.md',
    'docs/contracts/OSI_PIA_Data_Graph_Contract_v0.1.md',
    'governance/PIA_MEASUREMENT_DOCTRINE.md'
  ],
  profile.managed_by =
    '004_pia_reference_architecture_congruence',
  profile.created_at = datetime()
SET profile.aligned_at = datetime()
MERGE (ontology)-[:CONFORMS_TO_ARCHITECTURE]->(profile)
MERGE (ontology)-[:APPLIED_MIGRATION]->(migration)
WITH ontology, profile, migration,
     participants_aligned,
     sources_aligned,
     experiences_aligned,
     evidence_aligned,
     capabilities_aligned,
     assessments_aligned,
     mappings_aligned,
     uses_capability_relationships_corrected,
     source_experience_relationships_corrected,
     contextual_relationships_aligned

CALL (ontology) {
  MATCH (legacy:ConfidenceModel {
    confidence_model_id:
      'confidence:pia-reference:qualitative-v1'
  })
  SET legacy.implementation_status =
        'documented_not_observed',
      legacy.applicability =
        'Reserved for future qualitative interpretations; not the Evidence-to-Capability mapping model.',
      legacy.last_aligned_by =
        '004_pia_reference_architecture_congruence'
  RETURN count(legacy) AS legacy_confidence_models_retained
}

CALL (ontology) {
  MERGE (model:ConfidenceModel {
    confidence_model_id:
      'confidence:pia-reference:evidence-capability-numeric-v1'
  })
  ON CREATE SET
    model.name =
      'PIA Evidence-to-Capability Numeric Confidence',
    model.version = '1.0',
    model.property_name = 'confidence',
    model.method = 'bounded_numeric',
    model.minimum = 0.0,
    model.maximum = 1.0,
    model.enforcement_status =
      'validated_not_database_constrained',
    model.description =
      'Bounded confidence for a specific Evidence-to-Capability assertion; it is not a person score.',
    model.scope = 'Evidence-SUPPORTS-Capability',
    model.managed_by =
      '004_pia_reference_architecture_congruence',
    model.created_at = datetime()
  MERGE (ontology)-[:USES_CONFIDENCE_MODEL]->(model)
  RETURN count(model) AS numeric_confidence_models_aligned
}

CALL (ontology) {
  UNWIND [
    {
      graph_label: 'ArchitectureProfile',
      identity: 'profile_id',
      kind: 'governance_object',
      implementation: 'implemented',
      definition: 'A versioned declaration of graph conventions and ethical boundaries shared by the OSI and PIA reference databases.',
      distinction: 'Defines projection rules; it does not define participant or organizational truth.',
      temporal: 'Versioned and superseded rather than silently rewritten.',
      privacy: 'Contains governance metadata rather than participant evidence.'
    },
    {
      graph_label: 'GraphMigration',
      identity: 'migration_id',
      kind: 'operational_object',
      implementation: 'implemented',
      definition: 'An auditable record that a versioned graph change was applied.',
      distinction: 'Operational provenance rather than participant evidence.',
      temporal: 'Records start, completion, and migration version.',
      privacy: 'Must not contain unnecessary participant data.'
    },
    {
      graph_label: 'Participant',
      identity: 'participant_id',
      kind: 'entity_type',
      implementation: 'implemented',
      definition: 'The person whose bounded evidence package is represented for self-understanding and review.',
      distinction: 'A participant is not an assessment, capability total, reputation score, or employability score.',
      temporal: 'Consent, participation status, and corrections are time-bounded.',
      privacy: 'Sensitive person context; consent, correction, purpose limitation, and minimum necessary use are required.'
    },
    {
      graph_label: 'Source',
      identity: 'source_id',
      kind: 'evidence_object',
      implementation: 'implemented',
      definition: 'A document, interview, record, or other evidence-bearing origin.',
      distinction: 'The origin of evidence rather than the evidence or an interpretation.',
      temporal: 'Source date and collection date remain distinguishable; unknown collection time remains explicit.',
      privacy: 'Confidentiality and participant ownership must be explicit.'
    },
    {
      graph_label: 'Experience',
      identity: 'experience_id',
      kind: 'context_object',
      implementation: 'implemented',
      definition: 'A bounded role, project, education, service, creative, or comparable context in which evidence occurred.',
      distinction: 'Context for evidence rather than evidence of capability by itself.',
      temporal: 'Start, end, current, partial, and unknown date status remain distinguishable.',
      privacy: 'Only context necessary to interpret participant evidence should be represented.'
    },
    {
      graph_label: 'Evidence',
      identity: 'evidence_id',
      kind: 'evidence_object',
      implementation: 'implemented',
      definition: 'A source-grounded statement, activity, output, responsibility, event, condition, or outcome.',
      distinction: 'Preserved evidence rather than a capability assertion or assessment.',
      temporal: 'Event time, source time, and graph record time remain distinguishable.',
      privacy: 'Must retain Source provenance, review state, and participant correction rights.'
    },
    {
      graph_label: 'Capability',
      identity: 'capability_id',
      kind: 'entity_type',
      implementation: 'implemented',
      definition: 'A defined capacity that evidence may support within a bounded context.',
      distinction: 'A capability concept is not a total judgment of a person and is not established by title or credential alone.',
      temporal: 'Definitions are versioned; evidence mappings are contextual and revisable.',
      privacy: 'Must not be aggregated into an opaque person score.'
    },
    {
      graph_label: 'Pattern',
      identity: 'pattern_id',
      kind: 'analytical_object',
      implementation: 'experimental',
      definition: 'A reviewable analytical pattern that groups related capability evidence without overwriting it.',
      distinction: 'A pattern is an interpretation, not source evidence or identity.',
      temporal: 'Versioned with its method and supporting assessments.',
      privacy: 'Requires bounded use and human review.'
    },
    {
      graph_label: 'Assessment',
      identity: 'assessment_id',
      kind: 'analytical_object',
      implementation: 'experimental',
      definition: 'A versioned analyst interpretation based on inspectable Evidence, Capability, and Pattern objects.',
      distinction: 'A revisable interpretation rather than participant identity or source fact.',
      temporal: 'Later method versions create new assessments or explicit supersession.',
      privacy: 'Requires accountable analyst identity, review state, and participant correction pathways.'
    },
    {
      graph_label: 'Observation',
      identity: 'observation_id',
      kind: 'epistemic_object',
      implementation: 'schema_only',
      definition: 'A recorded description directly supported by source-grounded material.',
      distinction: 'A bounded description that remains separate from interpretation.',
      temporal: 'Observed time and recorded time remain distinguishable.',
      privacy: 'Must remain within participant consent and purpose boundaries.'
    },
    {
      graph_label: 'IdentityHypothesis',
      identity: 'identity_id',
      kind: 'analytical_object',
      implementation: 'schema_only',
      definition: 'A participant-reviewable hypothesis about a bounded identity pattern supported by assessments.',
      distinction: 'A revisable hypothesis, never a fixed identity classification or person score.',
      temporal: 'Versioned, reviewable, and supersedable.',
      privacy: 'High-sensitivity interpretation requiring participant agency and explicit review.'
    },
    {
      graph_label: 'Representation',
      identity: 'representation_id',
      kind: 'analytical_object',
      implementation: 'schema_only',
      definition: 'A bounded presentation of evidence or analysis for a declared audience and purpose.',
      distinction: 'A presentation layer rather than the underlying evidence or ontology.',
      temporal: 'Versioned for audience, purpose, and source state.',
      privacy: 'Must not disclose evidence beyond consent and purpose.'
    }
  ] AS concept_data
  MERGE (concept:Concept {
    concept_id:
      'concept:pia-reference:' + concept_data.graph_label
  })
  SET concept.name = concept_data.graph_label,
      concept.graph_label = concept_data.graph_label,
      concept.stable_identity_property = concept_data.identity,
      concept.item_kind = concept_data.kind,
      concept.scope = 'pia-reference',
      concept.definition = concept_data.definition,
      concept.distinction = concept_data.distinction,
      concept.temporal_semantics = concept_data.temporal,
      concept.evidence_boundary =
        'Evidence remains source-grounded; interpretations remain separate, reviewable, and reversible.',
      concept.privacy_boundary = concept_data.privacy,
      concept.relationship_policy =
        'Use only registered relationship definitions with explicit direction and semantic class.',
      concept.version = '0.2.0',
      concept.steward = 'PIA ontology steward',
      concept.knowledge_lifecycle_state = 'congruence',
      concept.ontology_status = 'working',
      concept.implementation_status = concept_data.implementation,
      concept.definition_status = 'declared',
      concept.source_ref =
        CASE
          WHEN concept_data.graph_label IN [
            'Participant',
            'Source',
            'Experience',
            'Evidence',
            'Capability'
          ]
          THEN 'docs/contracts/OSI_PIA_Data_Graph_Contract_v0.1.md'
          ELSE 'architecture/graph_ontology/REFERENCE_GRAPH_CONGRUENCE.md'
        END,
      concept.last_aligned_by =
        '004_pia_reference_architecture_congruence',
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
      relationship_type: 'HAS_SOURCE',
      start_label: 'Participant',
      end_label: 'Source',
      semantic_class: 'provenance_context',
      cardinality: 'one_to_many',
      assertion_required: false,
      definition: 'Connects a Participant evidence package to one of its Sources.'
    },
    {
      relationship_type: 'HAS_EXPERIENCE',
      start_label: 'Participant',
      end_label: 'Experience',
      semantic_class: 'context_fact',
      cardinality: 'one_to_many',
      assertion_required: false,
      definition: 'Connects a Participant to a represented Experience context.'
    },
    {
      relationship_type: 'CONTAINS',
      start_label: 'Source',
      end_label: 'Evidence',
      semantic_class: 'provenance_fact',
      cardinality: 'one_to_many',
      assertion_required: false,
      definition: 'Grounds Evidence in the Source that contains it.'
    },
    {
      relationship_type: 'DESCRIBES',
      start_label: 'Source',
      end_label: 'Experience',
      semantic_class: 'context_fact',
      cardinality: 'many_to_many',
      assertion_required: false,
      definition: 'Records that a Source describes an Experience context without claiming that it contains the Experience.'
    },
    {
      relationship_type: 'OCCURRED_IN',
      start_label: 'Evidence',
      end_label: 'Experience',
      semantic_class: 'context_fact',
      cardinality: 'many_to_one_when_known',
      assertion_required: false,
      definition: 'Places Evidence in an Experience context when the Source establishes that context.'
    },
    {
      relationship_type: 'SUPPORTS',
      start_label: 'Evidence',
      end_label: 'Capability',
      semantic_class: 'analytical_assertion',
      cardinality: 'many_to_many',
      assertion_required: true,
      definition: 'States that Evidence may support a Capability subject to bounded confidence and review.'
    },
    {
      relationship_type: 'CONTRIBUTES_TO',
      start_label: 'Capability',
      end_label: 'Pattern',
      semantic_class: 'analytical_assertion',
      cardinality: 'many_to_many',
      assertion_required: true,
      definition: 'States that a Capability contributes to a reviewable analytical Pattern.'
    },
    {
      relationship_type: 'HAS_ASSESSMENT',
      start_label: 'Participant',
      end_label: 'Assessment',
      semantic_class: 'analytical_record',
      cardinality: 'one_to_many',
      assertion_required: false,
      definition: 'Associates a Participant with a versioned Assessment record without making the Assessment part of participant identity.'
    },
    {
      relationship_type: 'EVALUATES',
      start_label: 'Assessment',
      end_label: 'Pattern',
      semantic_class: 'analytical_assertion',
      cardinality: 'many_to_many',
      assertion_required: true,
      definition: 'Records a Pattern evaluated by an Assessment.'
    },
    {
      relationship_type: 'USES_CAPABILITY',
      start_label: 'Assessment',
      end_label: 'Capability',
      semantic_class: 'analytical_reference',
      cardinality: 'many_to_many',
      assertion_required: false,
      definition: 'Records a Capability concept explicitly used by an Assessment.'
    },
    {
      relationship_type: 'BASED_ON',
      start_label: 'Assessment',
      end_label: 'Evidence',
      semantic_class: 'analytical_basis',
      cardinality: 'many_to_many',
      assertion_required: false,
      definition: 'Records Evidence directly reviewed as the basis of an Assessment.'
    },
    {
      relationship_type: 'SUPPORTS_IDENTITY',
      start_label: 'Assessment',
      end_label: 'IdentityHypothesis',
      semantic_class: 'sensitive_analytical_assertion',
      cardinality: 'many_to_many',
      assertion_required: true,
      definition: 'States that an Assessment may support a participant-reviewable IdentityHypothesis.'
    }
  ] AS relationship_data
  MERGE (definition:RelationshipDefinition {
    relationship_definition_id:
      'relationship-definition:pia-reference:' +
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
      definition.scope = 'pia-reference',
      definition.version = '0.2.0',
      definition.steward = 'PIA ontology steward',
      definition.knowledge_lifecycle_state = 'congruence',
      definition.ontology_status = 'working',
      definition.implementation_status =
        CASE
          WHEN relationship_data.relationship_type =
            'SUPPORTS_IDENTITY'
          THEN 'schema_only'
          ELSE 'implemented'
        END,
      definition.definition_status = 'declared',
      definition.source_ref =
        'architecture/graph_ontology/REFERENCE_GRAPH_CONGRUENCE.md',
      definition.last_aligned_by =
        '004_pia_reference_architecture_congruence',
      definition.aligned_at = datetime()
  MERGE (ontology)-[:DEFINES_RELATIONSHIP]->(definition)
  RETURN count(definition) AS core_relationships_aligned
}

CALL (ontology) {
  MATCH (deprecated:RelationshipDefinition {
    relationship_definition_id:
      'relationship-definition:pia-reference:USES'
  })
  SET deprecated.ontology_status = 'deprecated',
      deprecated.implementation_status = 'migrated',
      deprecated.definition_status = 'declared',
      deprecated.definition =
        'Legacy ambiguous relationship formerly used between Assessment and Capability.',
      deprecated.replaced_by = 'USES_CAPABILITY',
      deprecated.last_aligned_by =
        '004_pia_reference_architecture_congruence'
  RETURN count(deprecated) AS deprecated_relationships_marked
}

CALL (ontology) {
  MATCH (supports:RelationshipDefinition {
    relationship_definition_id:
      'relationship-definition:pia-reference:SUPPORTS'
  })
  MATCH (model:ConfidenceModel {
    confidence_model_id:
      'confidence:pia-reference:evidence-capability-numeric-v1'
  })
  MERGE (supports)-[:USES_CONFIDENCE_MODEL]->(model)
  RETURN count(model) AS supports_confidence_models_linked
}

CALL (ontology) {
  MATCH (concept:Concept)
  WHERE concept.scope = 'pia-reference'
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
  WHERE concept.scope = 'pia-reference'
    AND concept.definition IS NULL
  SET concept.definition_status = 'inventory_only',
      concept.relationship_policy =
        coalesce(
          concept.relationship_policy,
          'No canonical relationship use until a governed declaration is added.'
        )
  RETURN count(concept) AS inventory_only_concepts
}

CALL (ontology) {
  MATCH (definition:RelationshipDefinition)
  WHERE definition.scope = 'pia-reference'
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
    concept_id: 'concept:pia-reference:' + graph_label
  })
  ON CREATE SET
    concept.name = graph_label,
    concept.graph_label = graph_label,
    concept.item_kind = 'graph_label',
    concept.scope = 'pia-reference',
    concept.knowledge_lifecycle_state = 'formulation',
    concept.ontology_status = 'working',
    concept.implementation_status = 'implemented',
    concept.definition_status = 'inventory_only',
    concept.registration_basis = 'observed_live_graph_label',
    concept.source_ref = 'ontology/META_ONTOLOGY.md',
    concept.managed_by =
      '004_pia_reference_architecture_congruence',
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
      'relationship-definition:pia-reference:' +
      relationship_type
  })
  ON CREATE SET
    definition.name = relationship_type,
    definition.graph_relationship_type = relationship_type,
    definition.direction = 'outbound',
    definition.scope = 'pia-reference',
    definition.knowledge_lifecycle_state = 'formulation',
    definition.ontology_status = 'working',
    definition.implementation_status = 'implemented',
    definition.definition_status = 'inventory_only',
    definition.semantic_class = 'working_unclassified',
    definition.registration_basis =
      'observed_live_graph_relationship',
    definition.source_ref = 'ontology/META_ONTOLOGY.md',
    definition.managed_by =
      '004_pia_reference_architecture_congruence',
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
      'Aligned PIA contract property names, explicit unknowns, assertion metadata, relationship meanings, core declarations, confidence model, and the shared architecture profile.'

RETURN
  migration.migration_id AS migration_id,
  migration.status AS status,
  participants_aligned,
  sources_aligned,
  experiences_aligned,
  evidence_aligned,
  capabilities_aligned,
  assessments_aligned,
  mappings_aligned,
  uses_capability_relationships_corrected,
  source_experience_relationships_corrected,
  contextual_relationships_aligned,
  legacy_confidence_models_retained,
  numeric_confidence_models_aligned,
  core_concepts_aligned,
  core_relationships_aligned,
  deprecated_relationships_marked,
  supports_confidence_models_linked,
  allowed_relationship_sets_aligned,
  inventory_only_concepts,
  inventory_only_relationships,
  observed_concepts_registered,
  observed_relationships_registered;
