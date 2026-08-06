// Create one Assessment and attach it to an existing Participant.
// Replace the parameter values in Neo4j Browser before running.

:param participant_id => 'PIA-9001';
:param assessment_id => 'ASM-SYNTHETIC-001';
:param analyst => 'REPLACE_ANALYST_ID';
:param method_version => 'PIA-0.1';
:param status => 'draft';
:param confidence => 'pending';
:param summary => 'Synthetic assessment used to exercise the PIA workflow.';
:param notes => '';

MATCH (p:Participant {participant_id: $participant_id})
MERGE (a:Assessment {assessment_id: $assessment_id})
ON CREATE SET
  a.created_at = datetime(),
  a.analyst = $analyst,
  a.method_version = $method_version,
  a.status = $status,
  a.confidence = $confidence,
  a.summary = $summary,
  a.notes = $notes,
  a.namespace = p.namespace
ON MATCH SET
  a.updated_at = datetime()
MERGE (p)-[r:HAS_ASSESSMENT]->(a)
ON CREATE SET
  r.created_at = datetime(),
  r.status = 'active',
  r.relationship_semantic_class = 'analytical_record'
RETURN p.participant_id AS participant_id,
       a.assessment_id AS assessment_id,
       a.status AS status,
       a.method_version AS method_version;
