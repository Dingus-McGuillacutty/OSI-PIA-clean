"""Target gate for a future synthetic-only PIA sandbox import runner.

artifact_id: component-pia-sandbox-projection-preflight-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

from typing import Any

from software.intake.local_private_intake import IntakePreflightError


SANDBOX_DATABASE = "PIA-Sandbox"
SANDBOX_URI = "neo4j://127.0.0.1:7687"


def preflight(manifest: dict[str, Any], *, uri: str, database: str) -> dict[str, str]:
    """Validate only the declared synthetic sandbox target; never connect."""

    if uri != SANDBOX_URI:
        raise IntakePreflightError("Sandbox projection requires the local Neo4j URI.")
    if database != SANDBOX_DATABASE:
        raise IntakePreflightError("Sandbox projection may target PIA-Sandbox only.")
    if manifest.get("target_environment") != "local_sandbox":
        raise IntakePreflightError("Projection manifest is not a local sandbox manifest.")
    if manifest.get("target_database") != SANDBOX_DATABASE:
        raise IntakePreflightError("Manifest target is not PIA-Sandbox.")
    if manifest.get("projection_mode") != "dry_run":
        raise IntakePreflightError("Only dry_run projection is authorized.")
    return {"status": "passed", "uri": uri, "database": database, "connection": "not_attempted"}
