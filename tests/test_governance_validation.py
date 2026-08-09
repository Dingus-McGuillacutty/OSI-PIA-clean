from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = (
    REPOSITORY_ROOT
    / "software"
    / "governance"
    / "validate_repository_governance.py"
)


class GovernanceValidationTests(unittest.TestCase):
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
