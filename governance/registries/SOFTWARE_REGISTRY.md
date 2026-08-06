---
artifact_id: registry-software-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.8"
owner: repository-governance
---

# Software Registry

## Scope

This registry indexes implementation packages, workflows, and compatibility
paths. Independently testable modules are indexed in the Component Registry.

| Artifact ID | Name | Domain | Layer | Authority | Status | Owner | Version | Canonical Location | Depends On |
|---|---|---|---|---|---|---|---|---|---|
| `software-component-framework-001` | Component Framework Package | `implementation` | `software` | `canonical` | `active` | `software-maintainers` | `unversioned` | [Component framework](../../software/framework/) | `standard-component-001` |
| `software-importer-001` | Assurance Importer Package | `implementation` | `software` | `canonical` | `active` | `assurance-maintainers` | `1.0` | [Importer package](../../software/importer/) | `architecture-assurance-001`<br>`contract-shared-validation-001` |
| `software-governance-validator-001` | Repository Governance Validator | `implementation` | `software` | `canonical` | `active` | `repository-governance` | `1.0.0` | [Governance validator](../../software/governance/validate_repository_governance.py) | `repo-conventions-001`<br>`standard-registry-001`<br>`standard-namespace-001`<br>`governance-model-001` |
| `software-clean-release-builder-001` | Clean Release Repository Builder | `implementation` | `software` | `canonical` | `active` | `repository-governance` | `1.0.0` | [Clean release builder](../../software/governance/create_clean_release.py) | `software-governance-validator-001`<br>`standard-clean-release-001`<br>`repo-migration-plan-001` |
| `software-assurance-workflow-001` | Assurance Test Workflow | `test` | `software` | `canonical` | `active` | `assurance-maintainers` | `unversioned` | [GitHub Actions workflow](../../.github/workflows/assurance-tests.yml) | `software-importer-001`<br>`software-governance-validator-001` |
| `software-pia-local-intake-001` | PIA Local Intake Package | `pia` | `implementation` | `working` | `proposed` | `pia-intake` | `0.9.0` | [PIA local intake](../../software/intake/README.md) | `architecture-pia-intake-subsystem-001`<br>`architecture-pia-intake-phase2b-protection-001`<br>`architecture-pia-protected-evidence-extraction-001`<br>`architecture-pia-credential-library-001`<br>`architecture-pia-intake-phase3a-review-001`<br>`architecture-pia-intake-phase3b-lookup-001`<br>`contract-pia-intake-phase1-json-001`<br>`contract-pia-protected-evidence-extraction-json-001`<br>`contract-pia-capability-evidence-mapping-002`<br>`contract-pia-credential-catalog-json-001`<br>`contract-pia-credential-lookup-json-001`<br>`contract-pia-credential-resolution-linkage-json-001`<br>`component-pia-local-private-intake-001`<br>`component-pia-local-private-intake-ui-001`<br>`component-pia-intake-phase2b-security-001`<br>`component-pia-protected-participant-intake-001`<br>`component-pia-intake-phase2b-admin-001`<br>`component-pia-evidence-extraction-001`<br>`component-pia-evidence-intake-linkage-001`<br>`component-pia-capability-mapping-linkage-001`<br>`component-pia-protected-intake-ui-001`<br>`component-pia-credential-definition-catalog-001`<br>`component-pia-credential-definition-review-001`<br>`component-pia-credential-review-workbench-001`<br>`component-pia-credential-lookup-router-001`<br>`component-pia-credential-registry-connector-001`<br>`component-pia-credential-intake-linkage-001`<br>`connector-002` |
