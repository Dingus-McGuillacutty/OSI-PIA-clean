---
artifact_id: registry-graph-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.4"
owner: repository-governance
---

# Graph Registry

## Scope

This registry indexes reproducible reference-graph specifications, executable
migrations, imports, and validators. Live Neo4j database state is not stored in
the registry.

| Artifact ID | Name | Domain | Layer | Authority | Status | Owner | Version | Canonical Location | Depends On |
|---|---|---|---|---|---|---|---|---|---|
| `graph-osi-reference-001` | OSI Reference Database Specification | `osi` | `graph` | `canonical` | `active` | `graph-maintainers` | `0.2` | [OSI Reference Database](../../architecture/graph_ontology/OSI_Reference_Database.md) | `architecture-graph-platform-001`<br>`architecture-reference-graph-congruence-001`<br>`ontology-osi-core-001` |
| `graph-pia-reference-001` | PIA Reference Database Specification | `pia` | `graph` | `canonical` | `active` | `graph-maintainers` | `0.2` | [PIA Reference Database](../../architecture/graph_ontology/PIA_Reference_Database.md) | `architecture-graph-platform-001`<br>`architecture-reference-graph-congruence-001`<br>`contract-shared-data-graph-001` |
| `graph-schema-package-001` | Shared Graph Schema Package | `shared` | `graph` | `canonical` | `active` | `graph-maintainers` | `unversioned` | [Graph schema](../../graph/schema/) | `standard-graph-001`<br>`contract-shared-data-graph-001` |
| `graph-osi-meta-migration-001` | OSI Reference Meta-Ontology Migration | `osi` | `graph` | `canonical` | `active` | `graph-maintainers` | `0.1` | [Migration 001](../../graph/migrations/001_osi_reference_meta_ontology.cypher) | `ontology-shared-meta-001`<br>`graph-osi-reference-001` |
| `graph-pia-meta-migration-001` | PIA Reference Meta-Ontology Migration | `pia` | `graph` | `canonical` | `active` | `graph-maintainers` | `0.1` | [Migration 002](../../graph/migrations/002_pia_reference_meta_ontology.cypher) | `ontology-shared-meta-001`<br>`graph-pia-reference-001` |
| `graph-osi-congruence-migration-001` | OSI Reference Architecture Congruence Migration | `osi` | `graph` | `canonical` | `active` | `graph-maintainers` | `0.2` | [Migration 003](../../graph/migrations/003_osi_reference_architecture_congruence.cypher) | `graph-osi-meta-migration-001`<br>`architecture-reference-graph-congruence-001` |
| `graph-pia-congruence-migration-001` | PIA Reference Architecture Congruence Migration | `pia` | `graph` | `canonical` | `active` | `graph-maintainers` | `0.2` | [Migration 004](../../graph/migrations/004_pia_reference_architecture_congruence.cypher) | `graph-pia-meta-migration-001`<br>`architecture-reference-graph-congruence-001` |
| `graph-pia-behavioral-profile-migration-001` | PIA Capability Evidence Profile Migration | `pia` | `graph` | `working` | `proposed` | `graph-maintainers` | `0.2.0` | [Migration 005](../../graph/migrations/005_pia_behavioral_capability_profile.cypher) | `graph-pia-congruence-migration-001`<br>`ontology-pia-capability-pattern-001` |
| `graph-participant-import-001` | Participant Package Import | `pia` | `graph` | `canonical` | `active` | `graph-maintainers` | `0.1` | [Participant import](../../graph/cypher/imports/import_participant_package_v0.1.cypher) | `contract-shared-import-001` |
| `graph-pia-capability-evidence-import-002` | PIA Capability Evidence Mapping Import | `pia` | `graph` | `working` | `proposed` | `graph-maintainers` | `0.2` | [Capability evidence import](../../graph/cypher/imports/import_capability_evidence_mappings_v0.2.cypher) | `contract-pia-capability-evidence-mapping-002`<br>`graph-pia-behavioral-profile-migration-001` |
| `graph-participant-validation-001` | Participant Package Graph Validation | `pia` | `graph` | `canonical` | `active` | `graph-maintainers` | `0.1` | [Participant validation](../../graph/cypher/validation/validate_participant_package_v0.1.cypher) | `contract-shared-validation-001`<br>`graph-participant-import-001` |
| `graph-osi-congruence-validation-001` | OSI Reference Congruence Validation | `osi` | `graph` | `canonical` | `active` | `graph-maintainers` | `0.2` | [OSI congruence validator](../../graph/cypher/validation/validate_osi_reference_architecture_congruence_v0.2.cypher) | `graph-osi-congruence-migration-001` |
| `graph-osi-synthetic-sandbox-import-001` | OSI Synthetic Sandbox Import | `osi` | `graph` | `working` | `proposed` | `osi-architecture` | `0.1` | [Synthetic sandbox importer](../../software/importer/osi_synthetic_sandbox_import.py) | `contract-osi-synthetic-sandbox-projection-001`<br>`component-osi-synthetic-sandbox-import-001` |
| `graph-osi-synthetic-sandbox-validation-001` | OSI Synthetic Sandbox Import Validation | `osi` | `graph` | `working` | `proposed` | `osi-architecture` | `0.1` | [Synthetic sandbox validator](../../software/importer/validate_osi_synthetic_sandbox_import.py) | `graph-osi-synthetic-sandbox-import-001`<br>`component-osi-synthetic-sandbox-import-validator-001` |
| `graph-pia-congruence-validation-001` | PIA Reference Congruence Validation | `pia` | `graph` | `canonical` | `active` | `graph-maintainers` | `0.2` | [PIA congruence validator](../../graph/cypher/validation/validate_pia_reference_architecture_congruence_v0.2.cypher) | `graph-pia-congruence-migration-001` |
| `graph-pia-capability-evidence-validation-002` | PIA Capability Evidence Profile Validation | `pia` | `graph` | `working` | `proposed` | `graph-maintainers` | `0.2` | [Capability evidence validator](../../graph/cypher/validation/validate_pia_capability_evidence_profile_v0.2.cypher) | `graph-pia-behavioral-profile-migration-001`<br>`contract-pia-capability-evidence-mapping-002` |
