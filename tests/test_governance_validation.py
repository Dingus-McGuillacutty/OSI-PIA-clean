from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
import json


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = (
    REPOSITORY_ROOT
    / "software"
    / "governance"
    / "validate_repository_governance.py"
)


class GovernanceValidationTests(unittest.TestCase):
    def test_metadata_contract_separates_status_and_lifecycle(self) -> None:
        contract_path = (
            REPOSITORY_ROOT
            / "data"
            / "contracts"
            / "osi_pia_artifact_metadata_contract_v0.1.json"
        )
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        vocabularies = contract["controlled_vocabularies"]
        self.assertNotIn("exploratory", vocabularies["statuses"])
        self.assertNotIn("observed", vocabularies["statuses"])
        self.assertIn("exploration", vocabularies["lifecycle_states"])
        self.assertIn("observation", vocabularies["lifecycle_states"])

    def test_repository_governance_invariants(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--root", str(REPOSITORY_ROOT)],
            cwd=REPOSITORY_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"{result.stdout}\n{result.stderr}".strip(),
        )


if __name__ == "__main__":
    unittest.main()
