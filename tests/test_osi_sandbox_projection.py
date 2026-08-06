from __future__ import annotations

import unittest

from software.importer.osi_sandbox_projection_assurance import (
    OSISandboxProjectionAssurance,
    build_manifest,
)
from software.importer.osi_sandbox_projection_preflight import (
    OSIProjectionPreflightError,
    SANDBOX_DATABASE,
    SANDBOX_URI,
    preflight,
)
from software.importer.osi_synthetic_sandbox_import import SYNTHETIC_RECORDS


class OSISandboxProjectionTests(unittest.TestCase):
    def records(self):
        return [dict(record) for record in SYNTHETIC_RECORDS]

    def test_valid_synthetic_package_passes_without_graph_write(self) -> None:
        records = self.records()
        result = OSISandboxProjectionAssurance().assure(records, build_manifest(records))
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["graph_write"], "not_performed")
        self.assertEqual(result["target_preflight"]["connection"], "not_attempted")

    def test_missing_boundary_is_blocked(self) -> None:
        records = self.records(); records[0]["negative_boundary"] = ""
        result = OSISandboxProjectionAssurance().assure(records, build_manifest(records))
        self.assertEqual(result["status"], "block")
        self.assertIn("negative_boundary", result["findings"][0])

    def test_unaccepted_record_is_blocked(self) -> None:
        records = self.records(); records[0]["review_status"] = "needs_review"
        result = OSISandboxProjectionAssurance().assure(records, build_manifest(records))
        self.assertEqual(result["status"], "block")
        self.assertIn("must be accepted", result["findings"][-1])

    def test_non_synthetic_identity_is_blocked(self) -> None:
        records = self.records(); records[0]["organization_id"] = "ORG-001"
        result = OSISandboxProjectionAssurance().assure(records, build_manifest(records))
        self.assertEqual(result["status"], "block")
        self.assertIn("not synthetic", result["findings"][-1])

    def test_target_cannot_be_reference_database(self) -> None:
        records = self.records(); manifest = build_manifest(records); manifest["target_database"] = "osi-reference"
        result = OSISandboxProjectionAssurance().assure(records, manifest)
        self.assertEqual(result["status"], "block")

    def test_direct_preflight_allows_only_osi_sandbox(self) -> None:
        manifest = build_manifest(self.records())
        result = preflight(manifest, uri=SANDBOX_URI, database=SANDBOX_DATABASE)
        self.assertEqual(result["status"], "passed")
        with self.assertRaises(OSIProjectionPreflightError):
            preflight(manifest, uri=SANDBOX_URI, database="osi-reference")


if __name__ == "__main__":
    unittest.main()
