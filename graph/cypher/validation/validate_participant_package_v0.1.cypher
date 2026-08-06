// OSI/PIA post-import graph validation v0.1
// Set run_id to inspect only objects touched by one import run.
:param run_id => 'IMPORT-REPLACE-ME';

// V-GRAPH-001 Evidence without source provenance — blocking
MATCH (e:Evidence {last_import_run: $run_id})
WHERE NOT (:Source)-[:CONTAINS]->(e)
RETURN 'error' AS severity,
       'V-GRAPH-001' AS code,
       e.evidence_id AS object_id,
       'Evidence has no Source provenance.' AS message;

// V-GRAPH-002 Source without participant — blocking
MATCH (s:Source {last_import_run: $run_id})
WHERE NOT (:Participant)-[:HAS_SOURCE]->(s)
RETURN 'error' AS severity,
       'V-GRAPH-002' AS code,
       s.source_id AS object_id,
       'Source has no Participant parent.' AS message;

// V-GRAPH-003 Experience without participant — blocking
MATCH (x:Experience {last_import_run: $run_id})
WHERE NOT (:Participant)-[:HAS_EXPERIENCE]->(x)
RETURN 'error' AS severity,
       'V-GRAPH-003' AS code,
       x.experience_id AS object_id,
       'Experience has no Participant parent.' AS message;

// V-GRAPH-004 Invalid confidence — blocking
MATCH (:Evidence)-[r:SUPPORTS {last_import_run: $run_id}]->(:Capability)
WHERE r.confidence < 0 OR r.confidence > 1 OR r.confidence IS NULL
RETURN 'error' AS severity,
       'V-GRAPH-004' AS code,
       r.mapping_id AS object_id,
       'SUPPORTS confidence is absent or outside 0.00–1.00.' AS message;

// V-GRAPH-005 Duplicate mapping identity — blocking
MATCH ()-[r:SUPPORTS]->()
WITH r.mapping_id AS object_id, count(*) AS occurrences
WHERE object_id IS NOT NULL AND occurrences > 1
RETURN 'error' AS severity,
       'V-GRAPH-005' AS code,
       object_id,
       'Mapping ID occurs ' + toString(occurrences) + ' times.' AS message;

// V-GRAPH-006 Evidence text conflict — blocking pending review
MATCH (e:Evidence {last_import_run: $run_id, import_text_conflict: true})
RETURN 'error' AS severity,
       'V-GRAPH-006' AS code,
       e.evidence_id AS object_id,
       'Incoming Evidence text conflicted with protected stored text.' AS message;

// V-GRAPH-007 Evidence without Experience — warning
MATCH (e:Evidence {last_import_run: $run_id})
WHERE NOT (e)-[:OCCURRED_IN]->(:Experience)
RETURN 'warning' AS severity,
       'V-GRAPH-007' AS code,
       e.evidence_id AS object_id,
       'Evidence has no Experience context.' AS message;

// V-GRAPH-008 Unreviewed analytical mapping — warning
MATCH (:Evidence)-[r:SUPPORTS {last_import_run: $run_id}]->(:Capability)
WHERE r.review_status IN ['proposed', 'needs_review']
RETURN 'warning' AS severity,
       'V-GRAPH-008' AS code,
       r.mapping_id AS object_id,
       'Analytical mapping has not been accepted or rejected.' AS message;

// V-GRAPH-009 Missing source locator — warning
MATCH (e:Evidence {last_import_run: $run_id})
WHERE e.source_locator IS NULL OR trim(e.source_locator) = ''
RETURN 'warning' AS severity,
       'V-GRAPH-009' AS code,
       e.evidence_id AS object_id,
       'Evidence has no source locator.' AS message;

// Run summary
MATCH (run:ImportRun {run_id: $run_id})
OPTIONAL MATCH (n) WHERE n.last_import_run = $run_id
WITH run, labels(n) AS node_labels, count(n) AS count
RETURN run.run_id AS run_id,
       run.status AS current_status,
       collect({labels: node_labels, count: count}) AS imported_node_counts,
       'Review all preceding error result sets before accepting the run.' AS instruction;

// After the validation suite returns no blocking errors, execute:
// MATCH (run:ImportRun {run_id: $run_id})
// SET run.status = 'accepted', run.validated_at = datetime();
