---
artifact_id: registry-connector-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.1"
owner: repository-governance
---

# Connector Registry

## Scope

This registry indexes numbered connectors. The connector ID remains stable
when its readable name or physical path changes.

| Artifact ID | Name | Domain | Layer | Authority | Status | Owner | Version | Canonical Location | Depends On |
|---|---|---|---|---|---|---|---|---|---|
| `connector-collection-001` | Connector Collection | `shared` | `connector` | `canonical` | `active` | `connector-maintainers` | `1.1` | [Connectors](../../connectors/README.md) | `standard-connector-001` |
| `connector-001` | LinkedIn Archive Connector | `pia` | `connector` | `canonical` | `active` | `pia-connectors` | `0.1.0` | [connector-001-linkedin](../../connectors/connector-001-linkedin/) | `connector-collection-001`<br>`contract-shared-csv-001`<br>`contract-pia-linkedin-001` |
| `connector-002` | Credential Engine Registry Search Connector | `pia` | `connector` | `working` | `proposed` | `pia-connectors` | `0.1.0` | [connector-002-credential-engine](../../connectors/connector-002-credential-engine/) | `connector-collection-001`<br>`contract-pia-credential-resolution-linkage-001` |

## Compatibility note

The prior root-level manifest, field map, implementation, and template were
byte-identical compatibility copies. They were retired through `MIG-002`; the
numbered connector directory is the sole authority.
