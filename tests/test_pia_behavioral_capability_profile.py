from __future__ import annotations

import re
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_PROFILE = (
    REPOSITORY_ROOT / "ontology" / "PIA_CAPABILITY_PATTERN_PROFILE.md"
)
MIGRATION = (
    REPOSITORY_ROOT
    / "graph"
    / "migrations"
    / "005_pia_behavioral_capability_profile.cypher"
)
IMPORTER = (
    REPOSITORY_ROOT
    / "graph"
    / "cypher"
    / "imports"
    / "import_capability_evidence_mappings_v0.2.cypher"
)
VALIDATOR = (
    REPOSITORY_ROOT
    / "graph"
    / "cypher"
    / "validation"
    / "validate_pia_capability_evidence_profile_v0.2.cypher"
)


def markdown_ids(text: str, prefix: str) -> set[str]:
    return set(re.findall(rf"^\|\s*`({prefix}[A-Z0-9-]+)`\s*\|", text, re.MULTILINE))


def migration_ids(text: str, prefix: str) -> set[str]:
    return set(re.findall(rf"\bid:\s*'({prefix}[A-Z0-9-]+)'", text))


class PIABehavioralCapabilityProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = ONTOLOGY_PROFILE.read_text(encoding="utf-8")
        cls.migration = MIGRATION.read_text(encoding="utf-8")
        cls.importer = IMPORTER.read_text(encoding="utf-8")
        cls.validator = VALIDATOR.read_text(encoding="utf-8")

    def test_documented_vocabulary_matches_executable_migration(self) -> None:
        documented_capabilities = markdown_ids(self.profile, "CAP-PIA-")
        migrated_capabilities = migration_ids(self.migration, "CAP-PIA-")
        documented_patterns = markdown_ids(self.profile, "PAT-PIA-")
        migrated_patterns = migration_ids(self.migration, "PAT-PIA-")

        self.assertEqual(len(documented_capabilities), 52)
        self.assertEqual(documented_capabilities, migrated_capabilities)
        self.assertEqual(len(documented_patterns), 8)
        self.assertEqual(documented_patterns, migrated_patterns)

    def test_generic_teamwork_and_leadership_are_not_capabilities(self) -> None:
        capability_rows = re.findall(
            r"^\|\s*`CAP-PIA-[^`]+`\s*\|\s*([^|]+)\|",
            self.profile,
            re.MULTILINE,
        )
        normalized_names = {name.strip().lower() for name in capability_rows}
        self.assertNotIn("teamwork", normalized_names)
        self.assertNotIn("leadership", normalized_names)
        self.assertIn("Collaboration and Teamwork", self.profile)
        self.assertIn("Leadership and Human Development", self.profile)

    def test_importer_requires_behavioral_boundaries(self) -> None:
        for required_property in (
            "mapping_profile",
            "inference_level",
            "evidence_role",
            "claim_scope",
            "application_status",
            "alignment_basis",
            "credential_definition_status",
            "credential_definition_source",
            "credential_definition_uri",
            "credential_domain_scope",
            "definition_expansion_required",
            "behavioral_basis",
            "negative_boundary",
            "scope_limit",
            "source_independence_note",
        ):
            self.assertIn(required_property, self.importer)

        self.assertIn("contextually_suggested", self.importer)
        self.assertIn("row.review_status = 'needs_review'", self.importer)
        self.assertIn("toFloat(row.confidence) <= 0.49", self.importer)
        self.assertIn("toFloat(row.confidence) <= 0.89", self.importer)
        self.assertIn("educational_preparation", self.importer)
        self.assertIn("knowledge_exposure", self.importer)
        self.assertIn("explicitly_attributed_in_source", self.importer)
        self.assertIn("title_only_unknown", self.importer)
        self.assertIn("issuer_verified", self.importer)
        self.assertIn("definition_expansion_required = true", self.importer)

    def test_profile_documents_bounded_group_context_inference(self) -> None:
        for required_fragment in (
            "problem-directed and interdependent",
            "interdependent group",
            "group membership alone",
            "equal contribution",
            "shared authority",
            "definition-expansion queue",
        ):
            self.assertIn(required_fragment, self.profile)

    def test_live_validator_checks_profile_counts_and_inference_bounds(self) -> None:
        for required_fragment in (
            "pattern_count = 8",
            "capability_count = 52",
            "contribution_count = 59",
            "invalid_behavioral_mappings = 0",
            "invalid_contextual_suggestions = 0",
            "invalid_educational_mappings = 0",
            "invalid_behavioral_claim_scopes = 0",
            "overconfident_unaccepted_inferences = 0",
            "invalid_behavioral_mapping_identity_groups = 0",
        ):
            self.assertIn(required_fragment, self.validator)
        self.assertIn("credential_definition_status", self.validator)
        self.assertIn("explicitly_attributed_in_source", self.validator)


if __name__ == "__main__":
    unittest.main()
