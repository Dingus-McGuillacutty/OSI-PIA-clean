// OSI/PIA generic participant package importer v0.1
// Preconditions:
// 1. Package has passed software/importer/osi_pia_validate.py.
// 2. CSV files are available to Neo4j under $package_path.
// 3. Run each section in order. MERGE makes the import rerunnable.

:param package_path => 'file:///participant_package/';
:param run_id => 'IMPORT-REPLACE-ME';
:param engine_version => '0.1';
:param contract_version => '0.1';

// -----------------------------------------------------------------------------
// Schema
// -----------------------------------------------------------------------------
CREATE CONSTRAINT participant_id_unique IF NOT EXISTS
FOR (n:Participant) REQUIRE n.participant_id IS UNIQUE;

CREATE CONSTRAINT source_id_unique IF NOT EXISTS
FOR (n:Source) REQUIRE n.source_id IS UNIQUE;

CREATE CONSTRAINT experience_id_unique IF NOT EXISTS
FOR (n:Experience) REQUIRE n.experience_id IS UNIQUE;

CREATE CONSTRAINT evidence_id_unique IF NOT EXISTS
FOR (n:Evidence) REQUIRE n.evidence_id IS UNIQUE;

CREATE CONSTRAINT capability_id_unique IF NOT EXISTS
FOR (n:Capability) REQUIRE n.capability_id IS UNIQUE;

CREATE INDEX evidence_review_status IF NOT EXISTS
FOR (n:Evidence) ON (n.review_status);

CREATE INDEX source_type IF NOT EXISTS
FOR (n:Source) ON (n.source_type);

// -----------------------------------------------------------------------------
// Import audit
// -----------------------------------------------------------------------------
MERGE (run:ImportRun {run_id: $run_id})
ON CREATE SET run.started_at = datetime(),
              run.status = 'running'
SET run.engine_version = $engine_version,
    run.contract_version = $contract_version,
    run.package_path = $package_path;

// -----------------------------------------------------------------------------
// 1. Participant
// -----------------------------------------------------------------------------
LOAD CSV WITH HEADERS FROM $package_path + 'participant.csv' AS row
MERGE (p:Participant {participant_id: trim(row.participant_id)})
ON CREATE SET p.created_at = datetime(row.created_at)
SET p.display_name = CASE WHEN trim(row.display_name) = '' THEN null ELSE row.display_name END,
    p.status = row.status,
    p.consent_status = row.consent_status,
    p.updated_at = datetime(row.updated_at),
    p.contract_version = $contract_version,
    p.last_import_run = $run_id;

// -----------------------------------------------------------------------------
// 2. Source and provenance
// -----------------------------------------------------------------------------
LOAD CSV WITH HEADERS FROM $package_path + 'source.csv' AS row
MATCH (p:Participant {participant_id: trim(row.participant_id)})
MERGE (s:Source {source_id: trim(row.source_id)})
SET s.source_type = row.source_type,
    s.title = CASE WHEN trim(row.title) = '' THEN null ELSE row.title END,
    s.source_date = CASE WHEN trim(row.source_date) = '' THEN null ELSE date(row.source_date) END,
    s.collected_at = datetime(row.collected_at),
    s.file_reference = CASE WHEN trim(row.file_reference) = '' THEN null ELSE row.file_reference END,
    s.confidentiality = row.confidentiality,
    s.checksum = CASE WHEN trim(row.checksum) = '' THEN null ELSE row.checksum END,
    s.contract_version = $contract_version,
    s.last_import_run = $run_id
MERGE (p)-[:HAS_SOURCE]->(s);

// -----------------------------------------------------------------------------
// 3. Experience
// -----------------------------------------------------------------------------
LOAD CSV WITH HEADERS FROM $package_path + 'experience.csv' AS row
MATCH (p:Participant {participant_id: trim(row.participant_id)})
MERGE (x:Experience {experience_id: trim(row.experience_id)})
SET x.experience_type = row.experience_type,
    x.title = row.title,
    x.organization_name = CASE WHEN trim(row.organization_name) = '' THEN null ELSE row.organization_name END,
    x.start_date = CASE WHEN trim(row.start_date) = '' THEN null ELSE date(row.start_date) END,
    x.end_date = CASE WHEN trim(row.end_date) = '' THEN null ELSE date(row.end_date) END,
    x.date_status = row.date_status,
    x.description = CASE WHEN trim(row.description) = '' THEN null ELSE row.description END,
    x.contract_version = $contract_version,
    x.last_import_run = $run_id
MERGE (p)-[:HAS_EXPERIENCE]->(x);

// -----------------------------------------------------------------------------
// 4. Evidence
// Evidence text is protected. Existing text is not silently overwritten.
// A conflict is marked for review instead.
// -----------------------------------------------------------------------------
LOAD CSV WITH HEADERS FROM $package_path + 'evidence.csv' AS row
MATCH (s:Source {source_id: trim(row.source_id)})
MATCH (p:Participant {participant_id: trim(row.participant_id)})
MERGE (e:Evidence {evidence_id: trim(row.evidence_id)})
ON CREATE SET e.evidence_text = row.evidence_text,
              e.created_at = datetime(row.created_at)
SET e.evidence_type = row.evidence_type,
    e.source_locator = CASE WHEN trim(row.source_locator) = '' THEN null ELSE row.source_locator END,
    e.event_date = CASE WHEN trim(row.event_date) = '' THEN null ELSE date(row.event_date) END,
    e.extraction_method = row.extraction_method,
    e.fidelity_status = row.fidelity_status,
    e.review_status = CASE
        WHEN e.evidence_text IS NOT NULL AND e.evidence_text <> row.evidence_text THEN 'disputed'
        ELSE row.review_status
    END,
    e.import_text_conflict = CASE
        WHEN e.evidence_text IS NOT NULL AND e.evidence_text <> row.evidence_text THEN true
        ELSE false
    END,
    e.contract_version = $contract_version,
    e.last_import_run = $run_id
MERGE (s)-[:CONTAINS]->(e)
FOREACH (_ IN CASE WHEN trim(row.experience_id) = '' THEN [] ELSE [1] END |
    MERGE (x:Experience {experience_id: trim(row.experience_id)})
    MERGE (e)-[:OCCURRED_IN]->(x)
);

// -----------------------------------------------------------------------------
// 5. Capability ontology
// -----------------------------------------------------------------------------
LOAD CSV WITH HEADERS FROM $package_path + 'capability.csv' AS row
MERGE (c:Capability {capability_id: trim(row.capability_id)})
SET c.capability_name = row.capability_name,
    c.definition = row.definition,
    c.status = row.status,
    c.ontology_version = row.ontology_version,
    c.contract_version = $contract_version,
    c.last_import_run = $run_id;

// -----------------------------------------------------------------------------
// 6. Evidence-to-capability analytical mappings
// -----------------------------------------------------------------------------
LOAD CSV WITH HEADERS FROM $package_path + 'evidence_capability_mapping.csv' AS row
MATCH (e:Evidence {evidence_id: trim(row.evidence_id)})
MATCH (c:Capability {capability_id: trim(row.capability_id)})
MERGE (e)-[r:SUPPORTS {mapping_id: trim(row.mapping_id)}]->(c)
SET r.confidence = toFloat(row.confidence),
    r.confidence_basis = row.confidence_basis,
    r.proposed_by = row.proposed_by,
    r.review_status = row.review_status,
    r.created_at = datetime(row.created_at),
    r.reviewed_at = CASE WHEN trim(row.reviewed_at) = '' THEN null ELSE datetime(row.reviewed_at) END,
    r.contract_version = $contract_version,
    r.last_import_run = $run_id;

// -----------------------------------------------------------------------------
// Finalize audit. Post-import validation should run before marking accepted.
// -----------------------------------------------------------------------------
MATCH (run:ImportRun {run_id: $run_id})
SET run.graph_write_completed_at = datetime(),
    run.status = 'awaiting_validation';

RETURN $run_id AS run_id,
       'awaiting_validation' AS status;
