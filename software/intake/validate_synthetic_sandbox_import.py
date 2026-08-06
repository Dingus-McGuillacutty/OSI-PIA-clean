"""Read-only validation of one PIA-Sandbox synthetic import run."""

from __future__ import annotations

import argparse

from software.intake.synthetic_sandbox_import import _password_window
from software.intake.sandbox_projection_preflight import SANDBOX_DATABASE, SANDBOX_URI


QUERY = """
MATCH (e:Evidence)-[r:SUPPORTS {last_import_run: $run_id}]->(c:Capability)
RETURN count(r) AS relationship_count,
       collect(r.mapping_id) AS mapping_ids,
       collect(e.evidence_id) AS evidence_ids,
       collect(c.profile_capability_id) AS capability_ids,
       all(x IN collect(r) WHERE x.synthetic = true
         AND x.review_status = 'accepted'
         AND x.confidence >= 0.0 AND x.confidence <= 1.0) AS properties_valid
"""

CARDINALITY_QUERIES = {
    "evidence_node_count": """
        MATCH (e:Evidence {evidence_id: 'PIA-SYN-EVD-001'})
        RETURN count(e) AS value
    """,
    "capability_node_count": """
        MATCH (c:Capability {profile_capability_id: 'CAP-PIA-HANDOFF-MANAGEMENT'})
        RETURN count(c) AS value
    """,
    "mapping_relationship_count": """
        MATCH ()-[r:SUPPORTS {mapping_id: 'PIA-SYN-MAP-001'}]->()
        RETURN count(r) AS value
    """,
    "expected_path_count": """
        MATCH (:Evidence {evidence_id: 'PIA-SYN-EVD-001'})
              -[:SUPPORTS {mapping_id: 'PIA-SYN-MAP-001'}]->
              (:Capability {profile_capability_id: 'CAP-PIA-HANDOFF-MANAGEMENT'})
        RETURN count(*) AS value
    """,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one synthetic PIA-Sandbox import run.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--windowed-password", action="store_true")
    args = parser.parse_args()
    if not args.run_id.startswith("PIA-SANDBOX-RUN-"):
        parser.error("Run ID is not a PIA sandbox run identifier.")
    password = _password_window() if args.windowed_password else __import__("getpass").getpass.getpass("Local Neo4j password: ")
    from neo4j import GraphDatabase
    with GraphDatabase.driver(SANDBOX_URI, auth=("neo4j", password)) as driver:
        with driver.session(database=SANDBOX_DATABASE) as session:
            result = session.run(QUERY, run_id=args.run_id).single().data()
            cardinality = {
                name: session.run(query).single()["value"]
                for name, query in CARDINALITY_QUERIES.items()
            }
    accepted = (
        result["relationship_count"] == 1
        and result["mapping_ids"] == ["PIA-SYN-MAP-001"]
        and result["evidence_ids"] == ["PIA-SYN-EVD-001"]
        and result["capability_ids"] == ["CAP-PIA-HANDOFF-MANAGEMENT"]
        and result["properties_valid"] is True
        and all(value == 1 for value in cardinality.values())
    )
    print(
        {
            "status": "pass" if accepted else "fail",
            "run_id": args.run_id,
            **result,
            **cardinality,
            "idempotent_structure": all(value == 1 for value in cardinality.values()),
            "graph_write": "not_performed",
        }
    )
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
