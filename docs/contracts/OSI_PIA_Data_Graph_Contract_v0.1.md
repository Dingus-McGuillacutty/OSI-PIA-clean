# OSI–PIA Data and Graph Contract v0.1

**Status:** Working specification  
**Scope:** Participant-level PIA evidence and its translation into the OSI/PIA Neo4j graph  
**Purpose:** Define one stable interface from normalized source data to graph objects without collapsing evidence into interpretation.

---

## 1. Contract Principle

The data contract and graph contract are two views of the same system.

- The **data contract** defines the records that may enter the system.
- The **graph contract** defines how those records become nodes, relationships, and properties.
- A field should not exist in the import data unless its graph destination or validation purpose is known.
- A graph property or relationship should not be created unless its source field, derivation rule, or analytical status is documented.

The contract preserves this chain:

```text
Source
  ↓ contains
Evidence
  ↓ occurred in
Experience
  ↓ may support
Capability
  ↓ may participate in
State and State Transition analysis
```

PIA measures and preserves evidence. It does not measure the person as a total object.

---

## 2. Core Engineering Rules

Every graph object must answer:

1. **What are you?** — label and type
2. **Who are you?** — stable identifier
3. **Why do you exist?** — provenance or relationship to a source record

Additional rules:

- Stable identifiers are required before import.
- Imports must be rerunnable without duplication.
- Source facts and analytical interpretations must remain separate.
- Raw or near-raw evidence must retain provenance.
- Analytical mappings require confidence and review status.
- Missing data must remain missing; it must not be silently inferred.
- Deletion, correction, and supersession must be traceable.
- Participant-derived data MUST NOT be committed to a tracked repository.

---

## 3. Canonical Objects

### 3.1 Participant

Represents the participant whose evidence is being preserved.

| Field | Type | Required | Graph mapping | Notes |
|---|---|---:|---|---|
| participant_id | string | yes | `(:Participant {participant_id})` | Stable, non-semantic ID; `PIA-9000`–`PIA-9999` are reserved for synthetic fixtures |
| display_name | string | no | Participant property | Use pseudonym or approved display label |
| status | enum | yes | Participant property | `active`, `inactive`, `withdrawn`, `archived` |
| consent_status | enum | yes | Participant property | `pending`, `granted`, `limited`, `withdrawn` |
| created_at | datetime | yes | Participant property | ISO 8601 |
| updated_at | datetime | yes | Participant property | ISO 8601 |

### 3.2 Source

Represents a document, interview, record, or other evidence-bearing origin.

| Field | Type | Required | Graph mapping | Notes |
|---|---|---:|---|---|
| source_id | string | yes | `(:Source {source_id})` | Stable ID |
| participant_id | string | yes | `(Participant)-[:HAS_SOURCE]->(Source)` | Foreign key |
| source_type | enum | yes | Source property | `resume`, `cover_letter`, `interview`, `questionnaire`, `portfolio`, `record`, `other` |
| title | string | no | Source property | Human-readable source title |
| source_date | date | no | Source property | Date represented by source |
| collected_at | datetime | yes | Source property | Acquisition timestamp; a legacy graph may leave it null only when `collected_at_status = unknown` creates an explicit review queue |
| file_reference | string | no | Source property | Non-sensitive repository or local reference |
| confidentiality | enum | yes | Source property | `public`, `internal`, `restricted`, `participant_private` |
| checksum | string | no | Source property | Optional integrity check |

### 3.3 Experience

Represents a bounded context in which evidence occurred: role, project, education period, service period, or comparable episode.

| Field | Type | Required | Graph mapping | Notes |
|---|---|---:|---|---|
| experience_id | string | yes | `(:Experience {experience_id})` | Stable ID |
| participant_id | string | yes | `(Participant)-[:HAS_EXPERIENCE]->(Experience)` | Foreign key |
| experience_type | enum | yes | Experience property | `employment`, `education`, `project`, `service`, `creative_work`, `other` |
| title | string | yes | Experience property | Role or experience title |
| organization_name | string | no | Experience property initially | May later resolve to Organization node |
| start_date | date | no | Experience property | Partial dates permitted by policy |
| end_date | date | no | Experience property | Null means current or unknown; distinguish with `date_status` |
| date_status | enum | yes | Experience property | `known`, `partial`, `current`, `unknown` |
| description | string | no | Experience property | Neutral contextual summary |

### 3.4 Evidence

Represents a source-grounded statement, activity, output, responsibility, event, or outcome.

| Field | Type | Required | Graph mapping | Notes |
|---|---|---:|---|---|
| evidence_id | string | yes | `(:Evidence {evidence_id})` | Stable ID |
| source_id | string | yes | `(Source)-[:CONTAINS]->(Evidence)` | Provenance required |
| experience_id | string | no | `(Evidence)-[:OCCURRED_IN]->(Experience)` | Required when context is known |
| participant_id | string | yes | Validation field | Usually derivable through Source |
| evidence_text | string | yes | Evidence property | Concise, faithful statement |
| evidence_type | enum | yes | Evidence property | `activity`, `responsibility`, `output`, `achievement`, `event`, `condition`, `statement`, `other` |
| source_locator | string | no | Evidence property | Page, section, paragraph, timestamp, or row |
| event_date | date | no | Evidence property | When the evidence occurred, if known |
| extraction_method | enum | yes | Evidence property | `manual`, `assisted`, `automated`, `unknown`; `unknown` is permitted only for explicit legacy review |
| fidelity_status | enum | yes | Evidence property | `verbatim`, `close_paraphrase`, `normalized`, `summarized`, `unknown`; `unknown` is permitted only for explicit legacy review |
| review_status | enum | yes | Evidence property | `unreviewed`, `reviewed`, `participant_confirmed`, `disputed`, `superseded` |
| created_at | datetime | yes | Evidence property | ISO 8601 |

### 3.5 Capability

Represents a defined capacity that evidence may support. Capability is not asserted merely because a participant possesses a title or credential.

| Field | Type | Required | Graph mapping | Notes |
|---|---|---:|---|---|
| capability_id | string | yes | `(:Capability {capability_id})` | Stable canonical ID |
| capability_name | string | yes | Capability property | Canonical label |
| definition | string | yes | Capability property | Operational definition |
| status | enum | yes | Capability property | `proposed`, `working`, `established`, `deprecated` |
| ontology_version | string | yes | Capability property | Schema/ontology version |

### 3.6 Evidence–Capability Mapping

This is an analytical assertion and must remain distinct from Evidence.

| Field | Type | Required | Graph mapping | Notes |
|---|---|---:|---|---|
| mapping_id | string | yes | Relationship identity property | Stable ID |
| evidence_id | string | yes | Start node | Foreign key |
| capability_id | string | yes | End node | Foreign key |
| relationship_type | enum | yes | `[:SUPPORTS]` | v0.1 permits `SUPPORTS` only |
| confidence | number | yes | Relationship property | Range 0.00–1.00 |
| confidence_basis | string | yes | Relationship property | Brief rationale |
| proposed_by | enum/string | yes | Relationship property | `human`, `model`, or reviewer ID |
| review_status | enum | yes | Relationship property | `proposed`, `accepted`, `rejected`, `needs_review` |
| created_at | datetime | yes | Relationship property | ISO 8601 |
| reviewed_at | datetime | no | Relationship property | ISO 8601 |

PIA capability mappings may use the additive
[PIA Capability Evidence Mapping Profile](PIA_Capability_Evidence_Mapping_Profile_v0.2.md).
That profile preserves every v0.1 mapping requirement while adding evidence
role, claim scope, application status, inference level, mapping basis,
negative boundary, contextual scope, and
source-independence limits. Existing v0.1 mappings do not acquire the working
profile merely because the extension exists.

---

### 3.7 Legacy Congruence Rules

The reference databases contain records created before this contract. A
congruence migration may add canonical aliases and controlled enum mappings,
but it must not delete the original property or manufacture historical
certainty.

- `text` may be copied to `evidence_text`.
- `name` or `label` may be copied to `capability_name`.
- `created` and `updated` may be copied to `created_at` and `updated_at` when
  their semantics match.
- Missing legacy consent is represented as `pending` with
  `consent_status_basis = legacy_not_recorded`; it requires human review and
  is not equivalent to granted consent.
- Non-contract enum values must be retained in a property ending in `_legacy`
  before the canonical value is normalized.
- Missing source collection time remains null with
  `collected_at_status = unknown`.
- Missing extraction method or fidelity is represented as `unknown` with
  `metadata_review_status = required`.
- A migration-time `created_at` backfill must declare
  `created_at_basis = migration_backfill`.
- Provisional generated definitions must declare
  `definition_status = provisional_legacy_alignment` and must be reviewed
  before ontology promotion.

These rules create an explicit review queue. They do not convert legacy data
into assured data.

---

## 4. Canonical Graph Pattern

```text
(:Participant)
  -[:HAS_SOURCE]->(:Source)
  -[:CONTAINS]->(:Evidence)
  -[:OCCURRED_IN]->(:Experience)

(:Participant)
  -[:HAS_EXPERIENCE]->(:Experience)

(:Evidence)
  -[:SUPPORTS {
      mapping_id,
      confidence,
      confidence_basis,
      proposed_by,
      review_status,
      created_at,
      reviewed_at
    }]->(:Capability)
```

The pattern does **not** mean every Evidence item must support a Capability. Unmapped evidence is valid and should remain available for later review.

---

## 5. Identifier Standard

Recommended patterns:

```text
Participant: PIA-9001
Source:      PIA-9001-SRC-001
Experience:  PIA-9001-EXP-001
Evidence:    PIA-9001-EVD-001
Mapping:     PIA-9001-MAP-001
Capability:  CAP-ISSUE-RESOLUTION
```

Rules:

- IDs are immutable after publication/import.
- IDs must not encode sensitive personal information.
- Human-readable names may change; IDs may not.
- Corrected records retain the original ID unless the original record is superseded by a distinct object.

---

## 6. Import Order

```text
1. Participant
2. Source
3. Experience
4. Evidence
5. Capability
6. Evidence–Capability mappings
```

The importer must fail clearly when a required parent object does not exist.

---

## 7. Neo4j Constraints and Indexes

```cypher
CREATE CONSTRAINT participant_id_unique IF NOT EXISTS
FOR (n:Participant) REQUIRE n.participant_id IS UNIQUE;

CREATE CONSTRAINT source_id_unique IF NOT EXISTS
FOR (n:Source) REQUIRE n.source_id IS UNIQUE;

CREATE CONSTRAINT experience_id_unique IF NOT EXISTS
FOR (n:Experience) REQUIRE n.experience_id IS UNIQUE;

CREATE CONSTRAINT evidence_id_unique IF NOT EXISTS
FOR (n:Evidence) REQUIRE n.evidence_id IS UNIQUE;

CREATE CONSTRAINT capability_id_unique IF NOT EXISTS
FOR (n:Capability) REQUIRE n.capability_id IS UNIQUE;

CREATE INDEX evidence_review_status IF NOT EXISTS
FOR (n:Evidence) ON (n.review_status);

CREATE INDEX source_type IF NOT EXISTS
FOR (n:Source) ON (n.source_type);
```

Relationship uniqueness for `mapping_id` must be enforced by importer validation in Neo4j versions that do not support the required relationship constraint.

---

## 8. Import Behavior

All imports should use stable-key `MERGE` operations.

Example:

```cypher
MERGE (p:Participant {participant_id: row.participant_id})
SET p.display_name = row.display_name,
    p.status = row.status,
    p.consent_status = row.consent_status,
    p.updated_at = datetime(row.updated_at)
ON CREATE SET p.created_at = datetime(row.created_at);
```

The importer must:

- validate required fields before graph writes;
- reject duplicate IDs within an input batch;
- report missing foreign keys;
- distinguish warnings from blocking errors;
- produce counts for created, matched, updated, skipped, and rejected records;
- never silently create placeholder parent nodes;
- support a dry-run mode before production import.

---

## 9. Validation Rules

### Blocking validation

- Missing stable ID
- Duplicate stable ID
- Missing required parent record
- Invalid enum value
- Confidence outside 0.00–1.00
- Evidence without Source provenance
- Participant mismatch across related records
- Invalid date or datetime format

### Warning validation

- Evidence lacks Experience context
- Source locator absent
- Capability mapping remains unreviewed
- Partial or unknown dates
- Evidence text duplicates another item within the same Source

### Post-import graph checks

```cypher
// Evidence without source provenance
MATCH (e:Evidence)
WHERE NOT (:Source)-[:CONTAINS]->(e)
RETURN e.evidence_id;

// Evidence referencing no experience where context was expected
MATCH (e:Evidence)
WHERE e.experience_expected = true
  AND NOT (e)-[:OCCURRED_IN]->(:Experience)
RETURN e.evidence_id;

// Capability mappings outside valid confidence range
MATCH (:Evidence)-[r:SUPPORTS]->(:Capability)
WHERE r.confidence < 0 OR r.confidence > 1
RETURN r.mapping_id, r.confidence;

// Duplicate relationship identities
MATCH ()-[r:SUPPORTS]->()
WITH r.mapping_id AS id, count(*) AS c
WHERE id IS NOT NULL AND c > 1
RETURN id, c;
```

---

## 10. Evidence and Interpretation Boundary

The following belongs on Evidence:

- what the source states;
- the source location;
- the context in which the activity occurred;
- how the evidence was extracted and normalized;
- review or participant confirmation status.

The following belongs on analytical relationships or later assessment objects:

- inferred capability;
- confidence in the inference;
- construct scores;
- organizational diagnosis;
- recommendations;
- predictions.

No analytical conclusion may overwrite the underlying Evidence text.

---

## 11. Versioning and Change Control

This contract uses semantic versions.

- **Patch:** clarification or non-breaking documentation correction
- **Minor:** additive fields, enums, or relationships that preserve existing imports
- **Major:** breaking identifier, field, node, or relationship change

Every breaking change requires:

1. a decision record;
2. a migration script;
3. updated validation queries;
4. updated sample data;
5. a changelog entry;
6. a declared compatibility boundary.

Imported nodes should carry `schema_version` when practical.

---

## 12. Privacy and Governance Boundary

The repository may contain:

- schemas;
- synthetic examples;
- pseudonymized samples approved for publication;
- import scripts;
- validation scripts;
- migration history.

The repository should not contain:

- unapproved participant identities;
- private source documents;
- credentials;
- confidential organizational records;
- live Neo4j database files;
- raw exports containing personal information.

Consent withdrawal or correction must be represented operationally; Git
history must not be treated as a lawful or ethical reason to retain
participant-derived data in a tracked repository.

---

## 13. v0.1 Acceptance Test

The contract is considered operational when it can:

1. validate a complete normalized participant dataset;
2. import it twice without creating duplicate nodes or mappings;
3. preserve Source → Evidence provenance;
4. preserve Evidence → Experience context;
5. keep capability mappings separate and reviewable;
6. detect orphaned objects and invalid mappings;
7. produce a repeatable import report;
8. represent at least two contrasting participants without changing the core schema.

---

## 14. Immediate Implementation Sequence

1. Create CSV templates matching this contract.
2. Create Neo4j constraints and indexes.
3. Convert participant-specific Cypher into generic import scripts.
4. Add pre-import and post-import validation.
5. Run two independently generated synthetic participant packages through the
   same pipeline.
6. Record all mismatches as contract findings rather than silently adapting the data.

---

**Working conclusion:** The data and graph contracts should evolve together because each field must have a graph destination and each graph object must have traceable data provenance.
