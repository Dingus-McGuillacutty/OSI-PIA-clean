// Import reviewable PIA capability evidence mappings v0.2.
// Target database: pia-reference
//
// Supply $mappings as a list of maps. This script imports assertions only;
// it does not create Evidence or Capability nodes.
//
// Required map keys:
// mapping_id, evidence_id, profile_capability_id, confidence,
// confidence_basis, proposed_by, review_status, created_at, inference_level,
// evidence_role, claim_scope, application_status, alignment_basis,
// behavioral_basis, negative_boundary, scope_limit, source_independence_note.
// Educational rows additionally require credential_definition_status,
// credential_definition_source, and definition_expansion_required. Resolved
// issuer definitions also require credential_definition_uri and
// credential_domain_scope.
//
// Optional map key: reviewed_at.
//
// Example shape only (not participant data):
// {
//   mapping_id: 'MAP-SYNTHETIC-001',
//   evidence_id: 'SYNTHETIC-EVD-001',
//   profile_capability_id: 'CAP-PIA-STAKEHOLDER-COORDINATION',
//   confidence: 0.84,
//   confidence_basis: 'Specific coordinated behaviors are documented.',
//   proposed_by: 'human',
//   review_status: 'proposed',
//   created_at: '2026-07-25T00:00:00Z',
//   reviewed_at: null,
//   inference_level: 'strongly_inferred',
//   evidence_role: 'behavioral_demonstration',
//   claim_scope: 'demonstrated_application',
//   application_status: 'described_in_source',
//   aligned_experience_ids: 'SYNTHETIC-EXP-001',
//   alignment_basis: 'The evidence is scoped to the listed experience.',
//   course_title: '',
//   behavioral_basis: 'The evidence describes coordinated needs and actions.',
//   negative_boundary: 'Does not prove formal supervisory authority.',
//   scope_limit: 'The documented implementation project.',
//   source_independence_note: 'One source chain; no independent corroboration.'
// }

UNWIND $mappings AS row
WITH row
WHERE row.mapping_id IS NOT NULL
  AND trim(row.mapping_id) <> ''
  AND row.evidence_id IS NOT NULL
  AND trim(row.evidence_id) <> ''
  AND row.profile_capability_id IS NOT NULL
  AND trim(row.profile_capability_id) <> ''
  AND row.confidence IS NOT NULL
  AND toFloat(row.confidence) >= 0.0
  AND toFloat(row.confidence) <= 1.0
  AND row.confidence_basis IS NOT NULL
  AND trim(row.confidence_basis) <> ''
  AND row.proposed_by IS NOT NULL
  AND trim(row.proposed_by) <> ''
  AND row.created_at IS NOT NULL
  AND trim(row.created_at) <> ''
  AND row.review_status IN [
    'proposed',
    'accepted',
    'rejected',
    'needs_review'
  ]
  AND row.inference_level IN [
    'directly_demonstrated',
    'strongly_inferred',
    'contextually_suggested'
  ]
  AND row.evidence_role IN [
    'behavioral_demonstration',
    'educational_preparation'
  ]
  AND row.claim_scope IN [
    'demonstrated_application',
    'knowledge_exposure'
  ]
  AND row.application_status IN [
    'described_in_source',
    'explicitly_attributed_in_source',
    'topically_aligned_not_verified',
    'not_established'
  ]
  AND row.alignment_basis IS NOT NULL
  AND trim(row.alignment_basis) <> ''
  AND row.behavioral_basis IS NOT NULL
  AND trim(row.behavioral_basis) <> ''
  AND row.negative_boundary IS NOT NULL
  AND trim(row.negative_boundary) <> ''
  AND row.scope_limit IS NOT NULL
  AND trim(row.scope_limit) <> ''
  AND row.source_independence_note IS NOT NULL
  AND trim(row.source_independence_note) <> ''
  AND (
    row.inference_level <> 'contextually_suggested'
    OR (
      row.review_status = 'needs_review'
      AND toFloat(row.confidence) <= 0.49
    )
  )
  AND (
    row.inference_level <> 'strongly_inferred'
    OR row.review_status = 'accepted'
    OR toFloat(row.confidence) <= 0.89
  )
  AND (
    row.evidence_role <> 'educational_preparation'
    OR (
      row.inference_level = 'contextually_suggested'
      AND row.review_status = 'needs_review'
      AND toFloat(row.confidence) <= 0.49
      AND row.claim_scope = 'knowledge_exposure'
      AND row.application_status IN [
        'not_established',
        'topically_aligned_not_verified',
        'explicitly_attributed_in_source'
      ]
      AND row.credential_definition_status IN [
        'source_defined',
        'issuer_verified',
        'participant_defined',
        'title_only_unknown',
        'conflicting_definition'
      ]
      AND row.credential_definition_source IS NOT NULL
      AND trim(row.credential_definition_source) <> ''
      AND row.definition_expansion_required IS NOT NULL
      AND (
        NOT row.credential_definition_status IN [
          'title_only_unknown',
          'conflicting_definition'
        ]
        OR row.definition_expansion_required = true
      )
      AND (
        row.application_status <> 'explicitly_attributed_in_source'
        OR (
          row.aligned_experience_ids IS NOT NULL
          AND trim(row.aligned_experience_ids) <> ''
        )
      )
      AND (
        row.credential_definition_status <> 'issuer_verified'
        OR (
          row.credential_definition_uri IS NOT NULL
          AND trim(row.credential_definition_uri) <> ''
          AND row.credential_domain_scope IS NOT NULL
          AND trim(row.credential_domain_scope) <> ''
        )
      )
    )
  )
  AND (
    row.evidence_role <> 'behavioral_demonstration'
    OR row.claim_scope = 'demonstrated_application'
  )
MATCH (evidence:Evidence {evidence_id: trim(row.evidence_id)})
MATCH (capability:Capability {
  profile_capability_id: trim(row.profile_capability_id)
})
MERGE (evidence)-[mapping:SUPPORTS {
  mapping_id: trim(row.mapping_id)
}]->(capability)
ON CREATE SET mapping.created_at = datetime(row.created_at)
SET
  mapping.assertion_id = trim(row.mapping_id),
  mapping.confidence = toFloat(row.confidence),
  mapping.confidence_basis = row.confidence_basis,
  mapping.assertion_basis = row.behavioral_basis,
  mapping.proposed_by = row.proposed_by,
  mapping.review_status = row.review_status,
  mapping.reviewed_at =
    CASE
      WHEN row.reviewed_at IS NULL OR trim(row.reviewed_at) = ''
      THEN null
      ELSE datetime(row.reviewed_at)
    END,
  mapping.human_review_required = row.review_status <> 'accepted',
  mapping.relationship_semantic_class = 'analytical_assertion',
  mapping.mapping_profile = 'pia-capability-evidence-mapping-0.2',
  mapping.inference_level = row.inference_level,
  mapping.evidence_role = row.evidence_role,
  mapping.claim_scope = row.claim_scope,
  mapping.application_status = row.application_status,
  mapping.aligned_experience_ids =
    coalesce(row.aligned_experience_ids, ''),
  mapping.alignment_basis = row.alignment_basis,
  mapping.course_title = coalesce(row.course_title, ''),
  mapping.credential_definition_status =
    coalesce(row.credential_definition_status, ''),
  mapping.credential_definition_source =
    coalesce(row.credential_definition_source, ''),
  mapping.credential_definition_uri =
    coalesce(row.credential_definition_uri, ''),
  mapping.credential_domain_scope =
    coalesce(row.credential_domain_scope, ''),
  mapping.definition_expansion_required =
    coalesce(row.definition_expansion_required, false),
  mapping.behavioral_basis = row.behavioral_basis,
  mapping.negative_boundary = row.negative_boundary,
  mapping.scope_limit = row.scope_limit,
  mapping.source_independence_note = row.source_independence_note,
  mapping.updated_at = datetime()
RETURN
  count(mapping) AS imported_mapping_count,
  collect(mapping.mapping_id) AS imported_mapping_ids;
