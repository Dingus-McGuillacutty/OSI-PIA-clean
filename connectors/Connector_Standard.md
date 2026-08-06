---
artifact_id: standard-connector-001
domain: shared
layer: standard
authority: canonical
status: active
version: "1.1"
owner: connector-maintainers
---

# Connector Standard

## Purpose

This standard governs connector identity, directory structure, manifests,
contracts, provenance, privacy, outputs, and lifecycle.

## Identity and naming

Connector directories use:

```text
connector-{NNN}-{descriptive-name}/
```

The numeric identifier is stable and never reused. The descriptive name may
be clarified through a governed migration without changing `connector_id`.

Examples:

```text
connector-001-linkedin/
connector-002-resume/
connector-003-survey/
connector-004-hris/
```

## Required structure

```text
connector-NNN-name/
├── README.md
├── .gitignore
├── config/
│   ├── connector_manifest.yaml
│   └── field_map.yaml
├── docs/
│   └── data_contract.md
├── src/
└── templates/
```

Tests and fixtures SHOULD be added when a connector is qualified for repeated
use. Private archives and generated participant records MUST NOT be stored in
the connector directory.

## Required manifest fields

```yaml
schema_version: "1.0"
connector_id: connector-001
connector_name: linkedin
display_name: LinkedIn Archive
namespace: pia
domain_scope:
  - pia
contract_id: contract-pia-linkedin-001
contract_version: "1.0"
owner: pia-connectors
status: active
version: "0.1.0"
source_type: linkedin_archive_csv
```

Rules:

- `connector_id` matches the directory number.
- `connector_name` is lowercase `kebab-case`.
- `namespace` identifies the connector's primary semantic output and conforms
  to the [Namespace Standard](../governance/policies/NAMESPACE_STANDARD.md).
- `domain_scope` contains one or more explicit repository domains.
- `contract_id` resolves through the Contract Registry.
- `owner` names a stewardship role.
- `status` is `proposed`, `active`, `deprecated`, `superseded`, or `retired`.
- `version` follows semantic versioning.

Additional privacy, provenance, input, and output fields MAY extend the
manifest without redefining these fields.

## Domain boundary

A connector MAY serve more than one domain, but every domain must be declared.
Cross-domain output requires an explicit contract and mapping.

A connector MUST NOT:

- infer domain scope from whoever happens to run it;
- turn a source assertion into verified fact;
- overwrite source evidence with normalized or analytical values;
- create participant or organizational judgments;
- combine OSI and PIA outputs without an authorized cross-domain contract.

## Provenance and fidelity

Normalized records retain:

- connector ID and version;
- source type and source reference;
- source file and row or equivalent locator;
- deterministic derivation method;
- processing time or import-run identity;
- participant or organizational authorization boundary;
- fidelity and review status where required by contract.

Normalization may change representation but must not conceal that the source
made the original assertion.

## Privacy

Each connector declares a default data classification and public-repository
allow/prohibit rules. Secrets, credentials, private archives, normalized
participant records, and derived assessments are prohibited from the public
repository.

Connectors use minimum necessary observation and should ignore source fields
that are outside their declared purpose.

## Outputs and assurance

Outputs use contracted fields and stable identities. A connector documents:

- accepted input formats;
- normalized outputs;
- field mappings;
- failure and warning behavior;
- idempotency expectations;
- human-review points;
- downstream assurance requirements.

Connector success does not authorize graph import or publication. Outputs
still pass the applicable assurance and consent gates.

## Versioning

- patch: non-breaking corrections or documentation;
- minor: compatible source coverage or output additions;
- major: breaking field, identity, contract, or semantic changes.

Breaking changes require migration guidance and a new contract version.

## Registration and lifecycle

A connector is active only when:

- its numbered directory and manifest agree;
- its contract and owner are registered;
- privacy exclusions are present;
- documentation describes inputs, outputs, and limitations;
- applicable validation passes.

Addition, rename, deprecation, supersession, or retirement updates the
Connector Registry in the same commit.
