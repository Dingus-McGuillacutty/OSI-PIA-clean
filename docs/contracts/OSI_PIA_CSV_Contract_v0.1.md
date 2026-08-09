# OSI–PIA CSV Contract v0.1

**Status:** Working specification  
**Depends on:** `OSI_PIA_Data_Graph_Contract_v0.1.md`  
**Purpose:** Define the exact tabular interface used to move normalized PIA records into the import and graph pipeline.

---

## 1. Contract Principle

CSV is a transport layer, not the ontology.

Each CSV file represents one canonical record type from the data and graph contract. Column names, required fields, identifiers, enum values, and foreign keys must remain stable and machine-checkable.

The CSV contract must preserve:

```text
Source material
    ↓ normalization
Canonical CSV records
    ↓ validation
Graph import
    ↓
Traceable Neo4j objects
```

No analytical inference may be inserted into an evidence field merely to make an import easier.

---

## 2. File Set

A complete participant package may contain:

```text
participants.csv
sources.csv
experiences.csv
evidence.csv
capabilities.csv
evidence_capability_mappings.csv
```

`capabilities.csv` may be shared across participant packages when it contains canonical ontology records rather than participant-specific data.

Files containing no records may be omitted unless the importer is configured to require a complete package manifest.

---

## 3. Encoding and Format

All files must use:

- UTF-8 encoding
- comma delimiter
- one header row
- double quotes for fields containing commas, quotes, or line breaks
- doubled internal quotes according to RFC 4180 conventions
- ISO 8601 dates and datetimes
- dot decimal notation
- empty field for null values
- no spreadsheet formulas
- no merged cells, comments, colors, or presentation formatting

Line endings may be LF or CRLF. The importer must normalize either form.

A CSV file must not contain a byte-order mark unless the importer explicitly supports it.

---

## 4. General Column Rules

- Column names use lowercase `snake_case`.
- Required columns must be present even when a particular optional value is empty.
- Unknown columns are blocking errors by default.
- Column order should follow this contract, but validation must identify fields by header name rather than position.
- IDs are case-sensitive immutable strings.
- Leading and trailing whitespace must be trimmed during normalization.
- Empty strings become null for optional fields.
- Empty strings are invalid for required fields.
- Literal strings such as `NULL`, `N/A`, `unknown`, or `none` must not be used as null substitutes unless the field enum explicitly permits `unknown`.

---

## 5. File Schemas

## 5.1 `participants.csv`

Header:

```csv
participant_id,display_name,status,consent_status,created_at,updated_at
```

| Column | Required | Rule |
|---|---:|---|
| participant_id | yes | Pattern recommended: `PIA-[0-9]{3,}` |
| display_name | no | Pseudonym or approved display label |
| status | yes | `active`, `inactive`, `withdrawn`, `archived` |
| consent_status | yes | `pending`, `granted`, `limited`, `withdrawn` |
| created_at | yes | ISO 8601 datetime |
| updated_at | yes | ISO 8601 datetime |

The numeric range `PIA-9000` through `PIA-9999` is reserved for synthetic
fixtures and examples. It must not be assigned to a participant record.

## 5.2 `sources.csv`

Header:

```csv
source_id,participant_id,source_type,title,source_date,collected_at,file_reference,confidentiality,checksum
```

| Column | Required | Rule |
|---|---:|---|
| source_id | yes | Stable unique ID |
| participant_id | yes | Must exist in `participants.csv` or the target graph |
| source_type | yes | `resume`, `cover_letter`, `interview`, `questionnaire`, `portfolio`, `record`, `other` |
| title | no | Human-readable source title |
| source_date | no | ISO 8601 date |
| collected_at | yes | ISO 8601 datetime |
| file_reference | no | Non-sensitive reference only |
| confidentiality | yes | `public`, `internal`, `restricted`, `participant_private` |
| checksum | no | Lowercase hexadecimal preferred |

## 5.3 `experiences.csv`

Header:

```csv
experience_id,participant_id,experience_type,title,organization_name,start_date,end_date,date_status,description
```

| Column | Required | Rule |
|---|---:|---|
| experience_id | yes | Stable unique ID |
| participant_id | yes | Must exist in `participants.csv` or target graph |
| experience_type | yes | `employment`, `education`, `project`, `service`, `creative_work`, `other` |
| title | yes | Neutral role or experience title |
| organization_name | no | Text value until resolved to an Organization node |
| start_date | no | ISO 8601 full date unless partial-date policy is used |
| end_date | no | Empty for current or unknown; interpret using `date_status` |
| date_status | yes | `known`, `partial`, `current`, `unknown` |
| description | no | Neutral contextual summary |

Partial dates must not be represented as invalid dates. Until a dedicated partial-date structure exists, retain the normalized date only when defensible and mark `date_status=partial`.

## 5.4 `evidence.csv`

Header:

```csv
evidence_id,source_id,experience_id,participant_id,evidence_text,evidence_type,source_locator,event_date,extraction_method,fidelity_status,review_status,created_at,experience_expected
```

| Column | Required | Rule |
|---|---:|---|
| evidence_id | yes | Stable unique ID |
| source_id | yes | Must resolve to a Source |
| experience_id | no | Must resolve when populated |
| participant_id | yes | Must match the Source and Experience participant |
| evidence_text | yes | Concise faithful source-grounded statement |
| evidence_type | yes | `activity`, `responsibility`, `output`, `achievement`, `event`, `condition`, `statement`, `other` |
| source_locator | no | Page, section, paragraph, timestamp, or row |
| event_date | no | ISO 8601 date |
| extraction_method | yes | `manual`, `assisted`, `automated` |
| fidelity_status | yes | `verbatim`, `close_paraphrase`, `normalized`, `summarized` |
| review_status | yes | `unreviewed`, `reviewed`, `participant_confirmed`, `disputed`, `superseded` |
| created_at | yes | ISO 8601 datetime |
| experience_expected | yes | Boolean: `true` or `false` |

`evidence_text` must not contain a capability inference, assessment score, recommendation, or diagnosis unless the source itself explicitly states that content and the record is classified as a source statement.

## 5.5 `capabilities.csv`

Header:

```csv
capability_id,capability_name,definition,status,ontology_version
```

| Column | Required | Rule |
|---|---:|---|
| capability_id | yes | Stable canonical ID, recommended `CAP-*` |
| capability_name | yes | Canonical human-readable label |
| definition | yes | Operational definition |
| status | yes | `proposed`, `working`, `established`, `deprecated` |
| ontology_version | yes | Version string |

## 5.6 `evidence_capability_mappings.csv`

Header:

```csv
mapping_id,evidence_id,capability_id,relationship_type,confidence,confidence_basis,proposed_by,review_status,created_at,reviewed_at
```

| Column | Required | Rule |
|---|---:|---|
| mapping_id | yes | Stable unique mapping ID |
| evidence_id | yes | Must resolve to Evidence |
| capability_id | yes | Must resolve to Capability |
| relationship_type | yes | `SUPPORTS` only in v0.1 |
| confidence | yes | Decimal from `0.00` through `1.00` |
| confidence_basis | yes | Brief explicit rationale |
| proposed_by | yes | `human`, `model`, or reviewer identifier |
| review_status | yes | `proposed`, `accepted`, `rejected`, `needs_review` |
| created_at | yes | ISO 8601 datetime |
| reviewed_at | no | ISO 8601 datetime |

---

## 6. Identifier and Foreign-Key Rules

Recommended patterns:

```text
PIA-9001
PIA-9001-SRC-001
PIA-9001-EXP-001
PIA-9001-EVD-001
PIA-9001-MAP-001
CAP-ISSUE-RESOLUTION
```

Validation must confirm:

- uniqueness within each file;
- uniqueness across the target graph where applicable;
- participant consistency across Source, Experience, and Evidence;
- resolvable foreign keys;
- immutable identity during reruns.

The importer must not invent missing parent identifiers or silently create placeholder records.

---

## 7. Package Manifest

A participant package should include `manifest.yaml` when imports become automated.

Recommended fields:

```yaml
contract_version: 0.1.0
package_id: PIA-9001-IMPORT-001
participant_id: PIA-9001
created_at: 2026-07-22T00:00:00Z
created_by: human-or-process-id
files:
  participants: participants.csv
  sources: sources.csv
  experiences: experiences.csv
  evidence: evidence.csv
  mappings: evidence_capability_mappings.csv
```

The manifest does not replace file-level validation.

---

## 8. Privacy and Repository Rules

Public Git repositories may contain:

- schemas;
- templates;
- synthetic examples;
- pseudonymized demonstration data approved for publication.

Public Git repositories must not contain:

- confidential source documents;
- participant-private text;
- direct identifiers;
- credentials;
- unrestricted local file paths;
- unapproved personal data.

`file_reference` must point to a controlled reference, not expose a sensitive location.

---

## 9. Acceptance Criteria

A CSV package conforms to v0.1 when:

1. every file is valid UTF-8 CSV;
2. every supplied file has the exact required header set;
3. all required values are present;
4. all enums, booleans, dates, datetimes, and numbers parse correctly;
5. IDs are unique and immutable;
6. all foreign keys resolve;
7. participant identity is consistent across records;
8. evidence retains Source provenance;
9. analytical mappings remain separate from Evidence;
10. the package passes the Validation Contract before graph writes.

---

## 10. Versioning

This contract follows the version of the parent data and graph contract.

- Patch changes clarify formatting without changing accepted records.
- Minor changes add backward-compatible columns or enum values.
- Major changes alter required columns, identity, or record meaning.

Any breaking CSV change requires updated templates, validators, importer logic, sample data, and migration guidance.
