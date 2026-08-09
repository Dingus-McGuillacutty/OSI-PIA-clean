"""Read-only validation of one OSI-Sandbox synthetic import run."""

from __future__ import annotations

import argparse
import getpass

from software.importer.osi_sandbox_projection_preflight import SANDBOX_DATABASE, SANDBOX_URI
from software.importer.osi_synthetic_sandbox_import import _password_window


QUERY = """
MATCH (o:Organization)-[:HAS_SOURCE]->(s:Source)-[:CONTAINS_EVIDENCE]->(e:Evidence)
      -[r:SUPPORTS_OBSERVATION {last_import_run: $run_id}]->(obs:ObservationCandidate)
RETURN count(r) AS relationship_count,
       collect(DISTINCT r.observation_id) AS observation_ids,
       collect(DISTINCT e.evidence_id) AS evidence_ids,
       collect(DISTINCT o.organization_id) AS organization_ids,
       all(x IN collect(r) WHERE x.synthetic = true AND x.review_status = 'accepted'
         AND x.confidence >= 0.0 AND x.confidence <= 1.0
         AND x.negative_boundary IS NOT NULL) AS properties_valid
"""

CARDINALITY_QUERIES = {
    "audit_run_count": "MATCH (run:OSIImportRun {run_id: $run_id, synthetic: true, status: 'completed'}) RETURN count(run) AS value",
    "organization_node_count": "MATCH (n:Organization {organization_id: 'OSI-SYN-ORG-001'}) RETURN count(n) AS value",
    "source_node_count": "MATCH (n:Source) WHERE n.source_id IN ['OSI-SYN-SRC-001','OSI-SYN-SRC-002','OSI-SYN-SRC-003'] RETURN count(n) AS value",
    "evidence_node_count": "MATCH (n:Evidence) WHERE n.evidence_id IN ['OSI-SYN-EVD-001','OSI-SYN-EVD-002','OSI-SYN-EVD-003'] RETURN count(n) AS value",
    "observation_node_count": "MATCH (n:ObservationCandidate) WHERE n.observation_id IN ['OSI-SYN-OBS-001','OSI-SYN-OBS-002','OSI-SYN-OBS-003'] RETURN count(n) AS value",
    "observation_relationship_count": "MATCH ()-[r:SUPPORTS_OBSERVATION]->() WHERE r.observation_id IN ['OSI-SYN-OBS-001','OSI-SYN-OBS-002','OSI-SYN-OBS-003'] RETURN count(r) AS value",
    "expected_path_count": "MATCH (:Organization {organization_id: 'OSI-SYN-ORG-001'})-[:HAS_SOURCE]->(:Source)-[:CONTAINS_EVIDENCE]->(:Evidence)-[:SUPPORTS_OBSERVATION]->(:ObservationCandidate) WHERE size(['OSI-SYN-OBS-001','OSI-SYN-OBS-002','OSI-SYN-OBS-003']) = 3 RETURN count(*) AS value",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one synthetic OSI-Sandbox import run.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--windowed-password", action="store_true")
    args = parser.parse_args()
    if not args.run_id.startswith("OSI-SANDBOX-RUN-"):
        parser.error("Run ID is not an OSI sandbox run identifier.")
    password = _password_window() if args.windowed_password else getpass.getpass("Local Neo4j password: ")
    from neo4j import GraphDatabase
    with GraphDatabase.driver(SANDBOX_URI, auth=("neo4j", password)) as driver:
        with driver.session(database=SANDBOX_DATABASE) as session:
            result = session.run(QUERY, run_id=args.run_id).single().data()
            cardinality = {name: session.run(query, run_id=args.run_id).single()["value"] for name, query in CARDINALITY_QUERIES.items()}
    accepted = (
        result["relationship_count"] == 3
        and set(result["observation_ids"]) == {"OSI-SYN-OBS-001", "OSI-SYN-OBS-002", "OSI-SYN-OBS-003"}
        and set(result["evidence_ids"]) == {"OSI-SYN-EVD-001", "OSI-SYN-EVD-002", "OSI-SYN-EVD-003"}
        and result["organization_ids"] == ["OSI-SYN-ORG-001"]
        and result["properties_valid"] is True
        and cardinality["audit_run_count"] == 1
        and cardinality["organization_node_count"] == 1
        and all(cardinality[name] == 3 for name in cardinality if name not in {"audit_run_count", "organization_node_count"})
    )
    idempotent = cardinality["audit_run_count"] == 1 and cardinality["organization_node_count"] == 1 and all(value == 3 for name, value in cardinality.items() if name not in {"audit_run_count", "organization_node_count"})
    print({"status": "pass" if accepted else "fail", "run_id": args.run_id, **result, **cardinality, "idempotent_structure": idempotent, "graph_write": "not_performed"})
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
