// Optional: create an IdentityHypothesis and connect it to an Assessment.

:param assessment_id => 'ASM-SYNTHETIC-001';
:param identity_id => 'IDH-SYNTHETIC-001';
:param statement => 'REPLACE_WITH_HYPOTHESIS';
:param status => 'hypothesis';
:param participant_validation => 'pending';

MATCH (a:Assessment {assessment_id: $assessment_id})
MERGE (i:IdentityHypothesis {identity_id: $identity_id})
ON CREATE SET
  i.statement = $statement,
  i.status = $status,
  i.participant_validation = $participant_validation,
  i.created_at = datetime(),
  i.namespace = a.namespace
ON MATCH SET i.updated_at = datetime()
MERGE (a)-[r:SUPPORTS_IDENTITY]->(i)
ON CREATE SET
  r.created_at = datetime(),
  r.status = 'active',
  r.relationship_semantic_class = 'sensitive_analytical_assertion',
  r.review_status = 'needs_review'
RETURN a.assessment_id, i.identity_id, i.statement, i.status;
