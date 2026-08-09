---
artifact_id: registry-contract-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.8"
owner: repository-governance
---

# Contract Registry

## Scope

This registry indexes governed data, import, validation, and connector
contracts, including proposals whose working authority is explicit.
Documentation and machine-readable projections remain distinct artifacts.

| Artifact ID | Name | Domain | Layer | Authority | Status | Owner | Version | Canonical Location | Depends On |
|---|---|---|---|---|---|---|---|---|---|
| `contract-shared-csv-001` | OSI-PIA CSV Contract | `shared` | `contract` | `canonical` | `active` | `assurance-maintainers` | `0.1` | [CSV Contract](../../docs/contracts/OSI_PIA_CSV_Contract_v0.1.md) | `principle-shared-engineering-001` |
| `contract-shared-data-graph-001` | OSI-PIA Data and Graph Contract | `shared` | `contract` | `canonical` | `active` | `graph-maintainers` | `0.1` | [Data and Graph Contract](../../docs/contracts/OSI_PIA_Data_Graph_Contract_v0.1.md) | `contract-shared-csv-001`<br>`ontology-shared-meta-001` |
| `contract-pia-capability-evidence-mapping-002` | PIA Capability Evidence Mapping Profile | `pia` | `contract` | `working` | `proposed` | `pia-ontology` | `0.2` | [Capability evidence mapping profile](../../docs/contracts/PIA_Capability_Evidence_Mapping_Profile_v0.2.md) | `contract-shared-data-graph-001`<br>`ontology-pia-capability-pattern-001` |
| `contract-pia-intake-phase1-001` | PIA Intake Phase 1 Record Contract | `pia` | `contract` | `working` | `proposed` | `pia-intake` | `0.1.0` | [PIA Intake Phase 1 record contract](../../docs/contracts/PIA_Intake_Phase_1_Record_Contract_v0.1.md) | `architecture-pia-intake-subsystem-001`<br>`architecture-pia-credential-library-001`<br>`contract-shared-data-graph-001`<br>`contract-pia-capability-evidence-mapping-002` |
| `contract-pia-intake-phase1-json-001` | PIA Intake Phase 1 Machine-Readable Record Contract | `pia` | `contract` | `supporting` | `proposed` | `pia-intake` | `0.1.0` | [Machine-readable intake contract](../../data/contracts/pia_intake_phase1_contract_v0.1.json) | `contract-pia-intake-phase1-001` |
| `contract-pia-credential-catalog-001` | PIA Credential Definition Catalog Contract | `pia` | `contract` | `working` | `proposed` | `pia-intake` | `0.2.0` | [Credential definition catalog contract](../../docs/contracts/PIA_Credential_Definition_Catalog_Contract_v0.2.md) | `architecture-pia-intake-subsystem-001`<br>`architecture-pia-credential-library-001`<br>`contract-pia-intake-phase1-001` |
| `contract-pia-credential-catalog-json-001` | PIA Credential Definition Catalog Machine-Readable Contract | `pia` | `contract` | `supporting` | `proposed` | `pia-intake` | `0.2.0` | [Machine-readable credential catalog contract](../../data/contracts/pia_credential_definition_catalog_contract_v0.2.json) | `contract-pia-credential-catalog-001` |
| `contract-pia-credential-lookup-001` | PIA Credential Lookup Request Contract | `pia` | `contract` | `working` | `proposed` | `pia-intake` | `0.1.0` | [Credential lookup request contract](../../docs/contracts/PIA_Credential_Lookup_Request_Contract_v0.1.md) | `architecture-pia-intake-subsystem-001`<br>`architecture-pia-credential-library-001`<br>`contract-pia-credential-catalog-001` |
| `contract-pia-credential-lookup-json-001` | PIA Credential Lookup Machine-Readable Contract | `pia` | `contract` | `supporting` | `proposed` | `pia-intake` | `0.1.0` | [Machine-readable credential lookup contract](../../data/contracts/pia_credential_lookup_request_contract_v0.1.json) | `contract-pia-credential-lookup-001` |
| `contract-pia-credential-resolution-linkage-001` | PIA Credential Resolution Linkage Contract | `pia` | `contract` | `working` | `proposed` | `pia-intake` | `0.1.0` | [Credential resolution linkage contract](../../docs/contracts/PIA_Credential_Resolution_Linkage_Contract_v0.1.md) | `architecture-pia-intake-phase2b-protection-001`<br>`architecture-pia-intake-phase3b-lookup-001`<br>`contract-pia-credential-lookup-001` |
| `contract-pia-credential-resolution-linkage-json-001` | PIA Credential Resolution Linkage Machine-Readable Contract | `pia` | `contract` | `supporting` | `proposed` | `pia-intake` | `0.1.0` | [Machine-readable credential resolution linkage contract](../../data/contracts/pia_credential_resolution_linkage_contract_v0.1.json) | `contract-pia-credential-resolution-linkage-001` |
| `contract-pia-protected-evidence-extraction-001` | PIA Protected Evidence Extraction Contract | `pia` | `contract` | `working` | `proposed` | `pia-intake` | `0.1.0` | [Protected evidence extraction contract](../../docs/contracts/PIA_Protected_Evidence_Extraction_Contract_v0.1.md) | `architecture-pia-intake-subsystem-001`<br>`architecture-pia-intake-phase2b-protection-001`<br>`contract-shared-data-graph-001` |
| `contract-pia-protected-evidence-extraction-json-001` | PIA Protected Evidence Extraction Machine-Readable Contract | `pia` | `contract` | `supporting` | `proposed` | `pia-intake` | `0.1.0` | [Machine-readable protected evidence extraction contract](../../data/contracts/pia_protected_evidence_extraction_contract_v0.1.json) | `contract-pia-protected-evidence-extraction-001` |
| `contract-shared-import-001` | OSI-PIA Import Contract | `shared` | `contract` | `canonical` | `active` | `graph-maintainers` | `0.1` | [Import Contract](../../docs/contracts/OSI_PIA_Import_Contract_v0.1.md) | `contract-shared-data-graph-001` |
| `contract-shared-validation-001` | OSI-PIA Validation Contract | `shared` | `contract` | `canonical` | `active` | `assurance-maintainers` | `0.1` | [Validation Contract](../../docs/contracts/OSI_PIA_Validation_Contract_v0.1.md) | `contract-shared-import-001` |
| `contract-osi-organizational-evidence-001` | OSI Organizational Evidence Package Contract | `osi` | `contract` | `working` | `proposed` | `osi-architecture` | `0.1` | [Organizational evidence package contract](../../docs/contracts/OSI_Organizational_Evidence_Package_Contract_v0.1.md) | `architecture-osi-domain-001`<br>`contract-shared-validation-001` |
| `contract-osi-synthetic-sandbox-projection-001` | OSI Synthetic Sandbox Projection Contract | `osi` | `contract` | `working` | `proposed` | `osi-architecture` | `0.1` | [Synthetic sandbox projection contract](../../docs/contracts/OSI_Synthetic_Sandbox_Projection_Contract_v0.1.md) | `contract-osi-organizational-evidence-001`<br>`architecture-graph-platform-001` |
| `contract-shared-data-graph-yaml-001` | Machine-Readable Data and Graph Contract | `shared` | `contract` | `supporting` | `active` | `graph-maintainers` | `0.1.0` | [YAML contract](../../data/contracts/osi_pia_contract_v0.1.yaml) | `contract-shared-data-graph-001` |
| `contract-pia-linkedin-001` | LinkedIn Connector Data Contract | `pia` | `contract` | `canonical` | `active` | `pia-connectors` | `1.0` | [Connector data contract](../../connectors/connector-001-linkedin/docs/data_contract.md) | `contract-shared-csv-001` |
| `contract-data-legacy-001` | Legacy Data Contract Documentation | `shared` | `contract` | `supporting` | `review-required` | `assurance-maintainers` | `unversioned` | [Legacy data contract](../../docs/data_contract.md) | `contract-shared-csv-001`<br>`contract-shared-data-graph-001` |
