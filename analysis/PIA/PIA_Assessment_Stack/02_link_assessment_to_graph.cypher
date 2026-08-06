// Link an existing Assessment to the analytical objects it uses.
// Run only the sections needed. Replace parameter values first.

:param assessment_id => 'ASM-SYNTHETIC-001'
:param pattern_ids => ['REPLACE_PATTERN_ID'];
:param capability_ids => ['REPLACE_CAPABILITY_ID'];
:param evidence_ids => ['REPLACE_EVIDENCE_ID'];
:param identity_ids => ['REPLACE_IDENTITY_ID'];
:param analyst => 'REPLACE_ANALYST_ID';

// A. Patterns evaluated by the assessment
MATCH (a:Assessment {assessment_id: $assessment_id})
UNWIND $pattern_ids AS pattern_id
MATCH (p:Pattern {pattern_id: pattern_id})
MERGE (a)-[r:EVALUATES]->(p)
ON CREATE SET
  r.created_at = datetime(),
  r.analyst = $analyst,
  r.status = 'active',
  r.relationship_semantic_class = 'analytical_assertion',
  r.review_status = 'needs_review'
RETURN count(r) AS patterns_linked;

// B. Capabilities used in the assessment
MATCH (a:Assessment {assessment_id: $assessment_id})
UNWIND $capability_ids AS capability_id
MATCH (c:Capability {capability_id: capability_id})
MERGE (a)-[r:USES_CAPABILITY]->(c)
ON CREATE SET
  r.created_at = datetime(),
  r.analyst = $analyst,
  r.status = 'active',
  r.relationship_semantic_class = 'analytical_reference'
RETURN count(r) AS capabilities_linked;

// C. Evidence directly reviewed by the assessment
MATCH (a:Assessment {assessment_id: $assessment_id})
UNWIND $evidence_ids AS evidence_id
MATCH (e:Evidence {evidence_id: evidence_id})
MERGE (a)-[r:BASED_ON]->(e)
ON CREATE SET
  r.created_at = datetime(),
  r.analyst = $analyst,
  r.status = 'active',
  r.relationship_semantic_class = 'analytical_basis'
RETURN count(r) AS evidence_linked;

// D. Identity hypotheses supported by the assessment
MATCH (a:Assessment {assessment_id: $assessment_id})
UNWIND $identity_ids AS identity_id
MATCH (i:IdentityHypothesis {identity_id: identity_id})
MERGE (a)-[r:SUPPORTS_IDENTITY]->(i)
ON CREATE SET
  r.created_at = datetime(),
  r.analyst = $analyst,
  r.status = 'active',
  r.relationship_semantic_class = 'sensitive_analytical_assertion',
  r.review_status = 'needs_review'
RETURN count(r) AS identities_linked;
