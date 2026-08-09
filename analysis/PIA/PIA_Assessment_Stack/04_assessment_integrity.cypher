// PIA Inspector — Assessment integrity checks

// 1. Inventory
MATCH (a:Assessment)
OPTIONAL MATCH (p:Participant)-[:HAS_ASSESSMENT]->(a)
OPTIONAL MATCH (a)-[:EVALUATES]->(pat:Pattern)
OPTIONAL MATCH (a)-[:USES_CAPABILITY]->(cap:Capability)
OPTIONAL MATCH (a)-[:BASED_ON]->(e:Evidence)
OPTIONAL MATCH (a)-[:SUPPORTS_IDENTITY]->(i:IdentityHypothesis)
RETURN a.assessment_id AS assessment_id,
       a.status AS status,
       a.method_version AS method_version,
       a.analyst AS analyst,
       count(DISTINCT p) AS participants,
       count(DISTINCT pat) AS patterns,
       count(DISTINCT cap) AS capabilities,
       count(DISTINCT e) AS evidence,
       count(DISTINCT i) AS identity_hypotheses
ORDER BY assessment_id;

// 2. Missing required properties
MATCH (a:Assessment)
WITH a,
     [x IN [
       CASE WHEN a.assessment_id IS NULL THEN 'assessment_id' END,
       CASE WHEN a.created_at IS NULL THEN 'created_at' END,
       CASE WHEN a.analyst IS NULL OR trim(a.analyst) = '' THEN 'analyst' END,
       CASE WHEN a.method_version IS NULL OR trim(a.method_version) = '' THEN 'method_version' END,
       CASE WHEN a.status IS NULL OR trim(a.status) = '' THEN 'status' END
     ] WHERE x IS NOT NULL] AS missing
WHERE size(missing) > 0
RETURN a.assessment_id AS assessment_id, missing;

// 3. Orphan assessments
MATCH (a:Assessment)
WHERE NOT (:Participant)-[:HAS_ASSESSMENT]->(a)
RETURN a.assessment_id AS orphan_assessment;

// 4. Assessments with no analytical basis
MATCH (a:Assessment)
WHERE NOT (a)-[:EVALUATES|USES_CAPABILITY|BASED_ON]->()
RETURN a.assessment_id AS assessment_without_basis;

// 5. Assessments that support identity but cite no evidence
MATCH (a:Assessment)-[:SUPPORTS_IDENTITY]->(:IdentityHypothesis)
WHERE NOT (a)-[:BASED_ON]->(:Evidence)
RETURN DISTINCT a.assessment_id AS unsupported_identity_assessment;
