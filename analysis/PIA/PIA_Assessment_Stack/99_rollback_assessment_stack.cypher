// DESTRUCTIVE. Removes the Assessment layer only.
// Existing Participant, Source, Experience, Evidence, Capability, Pattern,
// and IdentityHypothesis nodes are not deleted.

MATCH (a:Assessment)
DETACH DELETE a;

DROP INDEX assessment_status IF EXISTS;
DROP INDEX assessment_method_version IF EXISTS;
DROP INDEX assessment_created IF EXISTS;
DROP CONSTRAINT assessment_id_unique IF EXISTS;
