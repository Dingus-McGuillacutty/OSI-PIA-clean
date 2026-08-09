// Validate PIA capability evidence and pattern profile v0.2.
// Target database: pia-reference

MATCH (ontology:Ontology {ontology_id: 'ontology:pia-reference'})

CALL (ontology) {
  MATCH (ontology)-[:APPLIED_MIGRATION]->(
    migration:GraphMigration {
      migration_id: '005_pia_behavioral_capability_profile'
    }
  )
  WHERE migration.status = 'applied'
    AND migration.version = '0.2.0'
    AND migration.ontology_status = 'working'
    AND migration.knowledge_lifecycle_state = 'formulation'
  RETURN count(migration) AS applied_migration_count
}

CALL () {
  MATCH (pattern:Pattern {
    profile_ontology_version: 'pia-capability-pattern-profile-0.2.0'
  })
  RETURN
    count(pattern) AS pattern_count,
    count(
      CASE
        WHEN pattern.profile_pattern_id IS NULL
          OR pattern.pattern_name IS NULL
          OR pattern.profile_definition IS NULL
          OR pattern.profile_status <> 'working'
          OR pattern.profile_method_version <>
            'pia-capability-evidence-mapping-0.2'
          OR pattern.profile_knowledge_lifecycle_state <> 'formulation'
          OR pattern.profile_participant_review_required <> true
          OR pattern.profile_synthetic <> false
        THEN 1
      END
    ) AS invalid_patterns
}

CALL () {
  MATCH (capability:Capability {
    profile_ontology_version: 'pia-capability-pattern-profile-0.2.0'
  })
  RETURN
    count(capability) AS capability_count,
    count(
      CASE
        WHEN capability.profile_capability_id IS NULL
          OR capability.capability_name IS NULL
          OR capability.profile_definition IS NULL
          OR capability.profile_status <> 'working'
          OR capability.profile_definition_status <>
            'working_behavioral_definition'
          OR capability.inference_profile <>
            'pia-capability-evidence-mapping-0.2'
        THEN 1
      END
    ) AS invalid_capabilities,
    count(
      CASE
        WHEN toLower(capability.capability_name) IN [
          'teamwork',
          'leadership'
        ]
        THEN 1
      END
    ) AS prohibited_generic_capabilities
}

CALL () {
  MATCH (
    capability:Capability {
      profile_ontology_version: 'pia-capability-pattern-profile-0.2.0'
    }
  )-[contribution_rel:CONTRIBUTES_TO {
    grouping_profile: 'pia-capability-pattern-profile-0.2.0'
  }]->(
    pattern:Pattern {
      profile_ontology_version: 'pia-capability-pattern-profile-0.2.0'
    }
  )
  RETURN
    count(contribution_rel) AS contribution_count,
    count(
      CASE
        WHEN contribution_rel.contribution_id IS NULL
          OR contribution_rel.assertion_id IS NULL
          OR contribution_rel.assertion_basis IS NULL
          OR contribution_rel.confidence IS NULL
          OR contribution_rel.confidence < 0.0
          OR contribution_rel.confidence > 1.0
          OR contribution_rel.confidence_basis IS NULL
          OR contribution_rel.proposed_by IS NULL
          OR contribution_rel.review_status IS NULL
          OR NOT contribution_rel.review_status IN [
            'proposed',
            'accepted',
            'rejected',
            'needs_review'
          ]
          OR contribution_rel.human_review_required IS NULL
          OR contribution_rel.relationship_semantic_class <>
            'analytical_assertion'
        THEN 1
      END
    ) AS invalid_contributions
}

CALL () {
  MATCH (
    capability:Capability {
      profile_ontology_version: 'pia-capability-pattern-profile-0.2.0'
    }
  )-[:CONTRIBUTES_TO {
    grouping_profile: 'pia-capability-pattern-profile-0.2.0'
  }]->(
    pattern:Pattern {
      profile_ontology_version: 'pia-capability-pattern-profile-0.2.0'
    }
  )
  WITH
    capability.profile_capability_id AS capability_id,
    pattern.profile_pattern_id AS pattern_id,
    count(*) AS occurrences
  WHERE capability_id IS NULL
    OR pattern_id IS NULL
    OR occurrences > 1
  RETURN count(*) AS duplicate_or_unidentified_contributions
}

CALL () {
  MATCH (:Evidence)-[mapping:SUPPORTS {
    mapping_profile: 'pia-capability-evidence-mapping-0.2'
  }]->(:Capability)
  RETURN
    count(mapping) AS behavioral_mapping_count,
    count(
      CASE
        WHEN mapping.mapping_id IS NULL
          OR mapping.assertion_id IS NULL
          OR mapping.confidence IS NULL
          OR mapping.confidence < 0.0
          OR mapping.confidence > 1.0
          OR mapping.confidence_basis IS NULL
          OR mapping.assertion_basis IS NULL
          OR mapping.proposed_by IS NULL
          OR mapping.review_status IS NULL
          OR NOT mapping.review_status IN [
            'proposed',
            'accepted',
            'rejected',
            'needs_review'
          ]
          OR mapping.inference_level IS NULL
          OR NOT mapping.inference_level IN [
            'directly_demonstrated',
            'strongly_inferred',
            'contextually_suggested'
          ]
          OR mapping.evidence_role IS NULL
          OR NOT mapping.evidence_role IN [
            'behavioral_demonstration',
            'educational_preparation'
          ]
          OR mapping.claim_scope IS NULL
          OR NOT mapping.claim_scope IN [
            'demonstrated_application',
            'knowledge_exposure'
          ]
          OR mapping.application_status IS NULL
          OR NOT mapping.application_status IN [
            'described_in_source',
            'explicitly_attributed_in_source',
            'topically_aligned_not_verified',
            'not_established'
          ]
          OR mapping.alignment_basis IS NULL
          OR trim(mapping.alignment_basis) = ''
          OR mapping.behavioral_basis IS NULL
          OR trim(mapping.behavioral_basis) = ''
          OR mapping.negative_boundary IS NULL
          OR trim(mapping.negative_boundary) = ''
          OR mapping.scope_limit IS NULL
          OR trim(mapping.scope_limit) = ''
          OR mapping.source_independence_note IS NULL
          OR trim(mapping.source_independence_note) = ''
          OR mapping.created_at IS NULL
          OR mapping.human_review_required IS NULL
          OR mapping.relationship_semantic_class <>
            'analytical_assertion'
        THEN 1
      END
    ) AS invalid_behavioral_mappings,
    count(
      CASE
        WHEN mapping.inference_level = 'contextually_suggested'
          AND (
            mapping.review_status <> 'needs_review'
            OR mapping.confidence > 0.49
          )
        THEN 1
      END
    ) AS invalid_contextual_suggestions,
    count(
      CASE
        WHEN mapping.evidence_role = 'educational_preparation'
          AND (
            mapping.inference_level <> 'contextually_suggested'
            OR mapping.review_status <> 'needs_review'
            OR mapping.confidence > 0.49
            OR mapping.claim_scope <> 'knowledge_exposure'
            OR NOT mapping.application_status IN [
              'not_established',
              'topically_aligned_not_verified',
              'explicitly_attributed_in_source'
            ]
            OR NOT mapping.credential_definition_status IN [
              'source_defined',
              'issuer_verified',
              'participant_defined',
              'title_only_unknown',
              'conflicting_definition'
            ]
            OR mapping.credential_definition_source IS NULL
            OR trim(mapping.credential_definition_source) = ''
            OR mapping.definition_expansion_required IS NULL
            OR (
              mapping.credential_definition_status IN [
                'title_only_unknown',
                'conflicting_definition'
              ]
              AND mapping.definition_expansion_required <> true
            )
            OR (
              mapping.application_status = 'explicitly_attributed_in_source'
              AND (
                mapping.aligned_experience_ids IS NULL
                OR trim(mapping.aligned_experience_ids) = ''
              )
            )
            OR (
              mapping.credential_definition_status = 'issuer_verified'
              AND (
                mapping.credential_definition_uri IS NULL
                OR trim(mapping.credential_definition_uri) = ''
                OR mapping.credential_domain_scope IS NULL
                OR trim(mapping.credential_domain_scope) = ''
              )
            )
          )
        THEN 1
      END
    ) AS invalid_educational_mappings,
    count(
      CASE
        WHEN mapping.evidence_role = 'behavioral_demonstration'
          AND mapping.claim_scope <> 'demonstrated_application'
        THEN 1
      END
    ) AS invalid_behavioral_claim_scopes,
    count(
      CASE
        WHEN mapping.inference_level = 'strongly_inferred'
          AND mapping.review_status <> 'accepted'
          AND mapping.confidence > 0.89
        THEN 1
      END
    ) AS overconfident_unaccepted_inferences
}

CALL () {
  MATCH (:Evidence)-[mapping:SUPPORTS {
    mapping_profile: 'pia-capability-evidence-mapping-0.2'
  }]->(:Capability)
  WITH mapping.mapping_id AS mapping_id, count(*) AS occurrences
  WHERE mapping_id IS NULL OR occurrences > 1
  RETURN count(*) AS invalid_behavioral_mapping_identity_groups
}

CALL () {
  MATCH (:Assessment)-[evaluation:EVALUATES]->(:Pattern)
  WHERE evaluation.mapping_profile =
    'pia-capability-evidence-mapping-0.2'
  RETURN
    count(evaluation) AS profile_evaluation_count,
    count(
      CASE
        WHEN evaluation.finding_state IS NULL
          OR NOT evaluation.finding_state IN [
          'evidence_present',
          'emerging_evidence',
          'insufficient_evidence',
          'mixed_or_contradictory_evidence',
          'not_yet_assessed'
        ]
        THEN 1
      END
    ) AS invalid_finding_states
}

RETURN
  applied_migration_count,
  pattern_count,
  invalid_patterns,
  capability_count,
  invalid_capabilities,
  prohibited_generic_capabilities,
  contribution_count,
  invalid_contributions,
  duplicate_or_unidentified_contributions,
  behavioral_mapping_count,
  invalid_behavioral_mappings,
  invalid_contextual_suggestions,
  invalid_educational_mappings,
  invalid_behavioral_claim_scopes,
  overconfident_unaccepted_inferences,
  invalid_behavioral_mapping_identity_groups,
  profile_evaluation_count,
  invalid_finding_states,
  applied_migration_count = 1
    AND pattern_count = 8
    AND invalid_patterns = 0
    AND capability_count = 52
    AND invalid_capabilities = 0
    AND prohibited_generic_capabilities = 0
    AND contribution_count = 59
    AND invalid_contributions = 0
    AND duplicate_or_unidentified_contributions = 0
    AND invalid_behavioral_mappings = 0
    AND invalid_contextual_suggestions = 0
    AND invalid_educational_mappings = 0
    AND invalid_behavioral_claim_scopes = 0
    AND overconfident_unaccepted_inferences = 0
    AND invalid_behavioral_mapping_identity_groups = 0
    AND invalid_finding_states = 0
    AS validation_passed;
