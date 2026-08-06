// Trace an Assessment through the actual PIA evidence chain.

:param assessment_id => 'ASM-SYNTHETIC-001';

MATCH (participant:Participant)-[:HAS_ASSESSMENT]->(a:Assessment {assessment_id: $assessment_id})
OPTIONAL MATCH (a)-[:SUPPORTS_IDENTITY]->(identity:IdentityHypothesis)
OPTIONAL MATCH (a)-[:EVALUATES]->(pattern:Pattern)
OPTIONAL MATCH (a)-[:USES_CAPABILITY]->(capability:Capability)
OPTIONAL MATCH (a)-[:BASED_ON]->(evidence:Evidence)
OPTIONAL MATCH (source:Source)-[:CONTAINS]->(evidence)
OPTIONAL MATCH (evidence)-[:OCCURRED_IN]->(experience:Experience)
RETURN participant.participant_id AS participant_id,
       a.assessment_id AS assessment_id,
       a.method_version AS method_version,
       a.status AS assessment_status,
       collect(DISTINCT identity{.identity_id, .statement, .status}) AS identities,
       collect(DISTINCT pattern{.pattern_id, .name, .status}) AS patterns,
       collect(DISTINCT capability{.capability_id, .capability_name, .label, .status}) AS capabilities,
       collect(DISTINCT evidence{.evidence_id, .label, .evidence_text, .evidence_type, .review_status}) AS evidence,
       collect(DISTINCT source{.source_id, .title, .name, .source_type}) AS sources,
       collect(DISTINCT experience{.experience_id, .title, .organization_name, .experience_type, .date_status}) AS experiences;
