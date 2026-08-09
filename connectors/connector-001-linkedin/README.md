---
artifact_id: connector-001
domain: pia
layer: connector
authority: canonical
status: active
version: "0.1.0"
owner: pia-connectors
---

# Connector 001 — LinkedIn Archive

Connector 001 translates a LinkedIn data archive into canonical PIA evidence records
while preserving source provenance.

It conforms to the [Connector Standard](../Connector_Standard.md). Its
manifest is the machine-readable authority for identity and scope.

## Scope

The connector currently supports the structured CSV files found in a LinkedIn archive,
including profile, positions, education, certifications, projects, publications, skills,
honors, learning activity, endorsements, connections, applications, and related metadata.

## Outputs

- Normalized domain tables
- Canonical evidence records
- Neo4j-ready node and relationship CSV files
- A processing report
- A participant summary suitable for human review

## Privacy boundary

The connector code and templates may be committed to Git.

Participant archives and generated participant records must **not** be
committed to a tracked repository. Store them in a private participant
workspace or an encrypted data store.
The included `.gitignore` excludes the expected participant-data paths.

## Usage

Run from this connector directory:

```bash
python src/ingest_linkedin.py \
  --input /path/to/linkedin-archive \
  --output /path/to/participant-001 \
  --participant-id participant-001
```

## Methodological rule

Connector 001 does not treat source assertions as verified truth. It records:

1. the source file,
2. the source row,
3. the normalized claim,
4. the evidence type,
5. provenance and sensitivity,
6. any deterministic derivation applied.

Human validation remains required before high-confidence PIA conclusions are published.

## Canonical assets

- `config/connector_manifest.yaml` — identity, scope, privacy, and provenance
  behavior;
- `config/field_map.yaml` — supported source-to-entity mappings;
- `docs/data_contract.md` — connector-specific record obligations;
- `templates/evidence_records_template.csv` — blank output template;
- `src/ingest_linkedin.py` — current normalization implementation.

No root-level compatibility copy is authoritative.
