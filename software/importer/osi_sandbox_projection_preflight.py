"""Target gate for a future synthetic-only OSI sandbox import runner.

This module performs declaration checks only; it never connects to Neo4j.
"""

from __future__ import annotations

from typing import Any


SANDBOX_DATABASE = "OSI-Sandbox"
SANDBOX_URI = "neo4j://127.0.0.1:7687"


class OSIProjectionPreflightError(ValueError):
    """Raised when a declared OSI projection target is outside its boundary."""


def preflight(manifest: dict[str, Any], *, uri: str, database: str) -> dict[str, str]:
    """Allow only the declared synthetic OSI sandbox target; never connect."""

    if uri != SANDBOX_URI:
        raise OSIProjectionPreflightError("OSI sandbox projection requires the local Neo4j URI.")
    if database != SANDBOX_DATABASE:
        raise OSIProjectionPreflightError("OSI sandbox projection may target OSI-Sandbox only.")
    if manifest.get("target_environment") != "local_sandbox":
        raise OSIProjectionPreflightError("Projection manifest is not a local sandbox manifest.")
    if manifest.get("target_database") != SANDBOX_DATABASE:
        raise OSIProjectionPreflightError("Manifest target is not OSI-Sandbox.")
    if manifest.get("projection_mode") != "synthetic_only":
        raise OSIProjectionPreflightError("Only synthetic_only projection is authorized.")
    if manifest.get("diagnostic_output") != "not_authorized":
        raise OSIProjectionPreflightError("Sandbox projection must not authorize diagnostic output.")
    return {"status": "passed", "uri": uri, "database": database, "connection": "not_attempted"}
