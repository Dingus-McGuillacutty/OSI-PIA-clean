// PIA Assessment Stack — schema migration
// Neo4j 5.x. Safe to run repeatedly.

CREATE CONSTRAINT assessment_id_unique IF NOT EXISTS
FOR (a:Assessment)
REQUIRE a.assessment_id IS UNIQUE;

CREATE INDEX assessment_status IF NOT EXISTS
FOR (a:Assessment)
ON (a.status);

CREATE INDEX assessment_method_version IF NOT EXISTS
FOR (a:Assessment)
ON (a.method_version);

CREATE INDEX assessment_created_at IF NOT EXISTS
FOR (a:Assessment)
ON (a.created_at);
