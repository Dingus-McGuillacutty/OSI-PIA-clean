from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from software.intake.credential_definition_catalog import (
    DEFAULT_CATALOG,
    CredentialDefinitionCatalog,
)
from software.intake.credential_definition_review import (
    CredentialDefinitionReviewService,
    CredentialReviewError,
    CredentialReviewRequest,
)
from software.intake.credential_review_server import (
    CredentialReviewHTTPServer,
    LOCAL_HOST,
)


DEFINITION_ID = "CRED-DEF-ASIS-PSP-2022-001"


class PIACredentialDefinitionReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.catalog_root = Path(self.temporary_directory.name) / "catalog"
        shutil.copytree(DEFAULT_CATALOG, self.catalog_root)
        self.service = CredentialDefinitionReviewService(
            self.catalog_root,
            clock=lambda: datetime(
                2026, 7, 29, 1, 2, 3, tzinfo=timezone.utc
            ),
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    @staticmethod
    def request(**overrides: object) -> CredentialReviewRequest:
        values: dict[str, object] = {
            "credential_definition_id": DEFINITION_ID,
            "reviewer_actor_id": "credential-reviewer-local-001",
            "reviewer_role": "credential_definition_reviewer",
            "decision": "accepted_with_limits",
            "review_basis": (
                "The issuer sources, fingerprints, bounded summaries, and "
                "domain locators were independently inspected."
            ),
            "limitations": (
                "The precise effective start and end dates remain unstated."
            ),
            "review_cycle": "annual",
            "sources_reviewed": True,
            "boundary_reviewed": True,
        }
        values.update(overrides)
        return CredentialReviewRequest(**values)  # type: ignore[arg-type]

    def _catalog_digest(self) -> str:
        digest = hashlib.sha256()
        for path in sorted(self.catalog_root.glob("*.csv")):
            digest.update(path.name.encode("utf-8"))
            digest.update(path.read_bytes())
        return digest.hexdigest()

    def test_queue_exposes_public_definition_package_only(self) -> None:
        queue = self.service.list_review_queue()
        self.assertEqual(len(queue), 1)
        package = queue[0]
        self.assertEqual(
            package["credential_definition"]["credential_definition_id"],
            DEFINITION_ID,
        )
        serialized = json.dumps(package).casefold()
        self.assertNotIn("participant_id", serialized)
        self.assertNotIn("completion_date", serialized)
        self.assertEqual(len(package["sources"]), 2)
        self.assertEqual(len(package["domain_elements"]), 3)

    def test_proposing_actor_cannot_review_own_package(self) -> None:
        with self.assertRaisesRegex(
            CredentialReviewError, "cannot review its own"
        ):
            self.service.preview(
                self.request(
                    reviewer_actor_id="credential-definition-agent-v0.1"
                )
            )

    def test_preview_validates_without_mutating_catalog(self) -> None:
        before = self._catalog_digest()
        result = self.service.preview(self.request())
        after = self._catalog_digest()
        self.assertEqual(before, after)
        self.assertFalse(result["applied"])
        self.assertEqual(result["projected_resolution_status"], "resolved")
        self.assertEqual(len(result["review_record_ids"]), 6)
        self.assertEqual(result["participant_claims_established"], [])

    def test_acceptance_with_limits_requires_stated_limit(self) -> None:
        with self.assertRaisesRegex(CredentialReviewError, "requires"):
            self.service.preview(self.request(limitations=""))

    def test_unbounded_effective_period_cannot_be_fully_accepted(self) -> None:
        with self.assertRaisesRegex(
            CredentialReviewError, "effective boundaries"
        ):
            self.service.preview(
                self.request(decision="accepted", limitations="")
            )

    def test_apply_appends_reviews_closes_queue_and_resolves(self) -> None:
        result = self.service.apply(self.request())
        self.assertTrue(result["applied"])
        catalog = CredentialDefinitionCatalog(self.catalog_root)
        self.assertTrue(catalog.validate()["valid"])
        resolution = catalog.resolve(
            "Physical Security Professional", issuer_hint="ASIS"
        )
        self.assertEqual(resolution["resolution_status"], "resolved")
        self.assertEqual(
            len(catalog.rows["credential_definition_review.csv"]), 6
        )
        queue = catalog.rows["credential_definition_expansion_queue.csv"][0]
        self.assertEqual(queue["processing_state"], "closed")

    def test_revision_request_keeps_definition_out_of_resolved_state(self) -> None:
        result = self.service.apply(
            self.request(
                decision="revision_requested",
                limitations="",
                review_basis=(
                    "The domain structure is useful, but effective-version "
                    "support requires a documented revision."
                ),
            )
        )
        self.assertEqual(
            result["projected_resolution_status"],
            "definition_found_pending_review",
        )
        catalog = CredentialDefinitionCatalog(self.catalog_root)
        self.assertTrue(catalog.validate()["valid"])
        self.assertEqual(
            catalog.rows["credential_definition_expansion_queue.csv"][0][
                "processing_state"
            ],
            "in_progress",
        )

    def test_follow_up_review_supersedes_same_targets_without_erasing_history(
        self,
    ) -> None:
        first = self.service.apply(self.request())
        second = self.service.apply(
            self.request(
                decision="revision_requested",
                limitations="",
                review_basis=(
                    "A later source-change notice requires the accepted "
                    "definition package to return to revision."
                ),
            )
        )
        self.assertTrue(second["applied"])
        self.assertTrue(
            set(first["review_record_ids"]).isdisjoint(
                second["review_record_ids"]
            )
        )
        catalog = CredentialDefinitionCatalog(self.catalog_root)
        self.assertTrue(catalog.validate()["valid"])
        reviews = catalog.rows["credential_definition_review.csv"]
        self.assertEqual(len(reviews), 12)
        self.assertEqual(
            {
                row["supersedes_credential_definition_review_id"]
                for row in reviews[6:]
            },
            set(first["review_record_ids"]),
        )

    def test_catalog_validator_rejects_self_review_record(self) -> None:
        request = self.request()
        self.service.apply(request)
        review_path = self.catalog_root / "credential_definition_review.csv"
        value = review_path.read_text(encoding="utf-8")
        value = value.replace(
            "credential-reviewer-local-001",
            "credential-definition-agent-v0.1",
            1,
        )
        review_path.write_text(value, encoding="utf-8")
        report = CredentialDefinitionCatalog(self.catalog_root).validate()
        self.assertFalse(report["valid"])
        self.assertIn(
            "SELF_REVIEW_PROHIBITED",
            {finding["code"] for finding in report["findings"]},
        )


class PIACredentialReviewHTTPTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.catalog_root = Path(self.temporary_directory.name) / "catalog"
        shutil.copytree(DEFAULT_CATALOG, self.catalog_root)
        service = CredentialDefinitionReviewService(self.catalog_root)
        self.server = CredentialReviewHTTPServer(
            (LOCAL_HOST, 0), service, allow_catalog_writes=False
        )
        self.thread = threading.Thread(
            target=self.server.serve_forever, daemon=True
        )
        self.thread.start()
        self.base_url = (
            f"http://{LOCAL_HOST}:{self.server.server_address[1]}"
        )

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temporary_directory.cleanup()

    def _request(
        self, path: str, *, body: dict[str, object] | None = None
    ) -> tuple[int, dict[str, object]]:
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=data,
            headers={
                "X-PIA-Local-Token": self.server.local_token,
                **(
                    {"Content-Type": "application/json"}
                    if data is not None
                    else {}
                ),
            },
            method="POST" if data is not None else "GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as exc:
            try:
                return exc.code, json.loads(exc.read())
            finally:
                exc.close()

    def test_status_and_queue_are_available_locally(self) -> None:
        status, value = self._request("/api/status")
        self.assertEqual(status, 200)
        self.assertFalse(value["write_enabled"])
        status, queue = self._request("/api/review-queue")
        self.assertEqual(status, 200)
        self.assertEqual(len(queue), 1)

    def test_preview_only_server_refuses_catalog_apply(self) -> None:
        body = {
            **PIACredentialDefinitionReviewTests.request().__dict__,
            "confirm_catalog_change": "APPLY REVIEW",
        }
        status, value = self._request("/api/review/apply", body=body)
        self.assertEqual(status, 403)
        self.assertIn("disabled", str(value["error"]))

    def test_queue_requires_restart_scoped_local_token(self) -> None:
        request = urllib.request.Request(self.base_url + "/api/review-queue")
        with self.assertRaises(urllib.error.HTTPError) as raised:
            urllib.request.urlopen(request, timeout=3)
        self.assertEqual(raised.exception.code, 400)
        raised.exception.close()


if __name__ == "__main__":
    unittest.main()
