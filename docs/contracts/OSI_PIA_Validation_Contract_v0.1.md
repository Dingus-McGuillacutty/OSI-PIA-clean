# OSI–PIA Validation Contract v0.1

**Status:** Working specification  
**Depends on:** `OSI_PIA_Data_Graph_Contract_v0.1.md`, `OSI_PIA_CSV_Contract_v0.1.md`, `OSI_PIA_Import_Contract_v0.1.md`  
**Purpose:** Define the validation rules, severity levels, evidence requirements, and acceptance thresholds for OSI/PIA data packages and graph imports.

---

## 1. Contract Principle

Validation protects meaning, not merely syntax.

A record may be technically parseable and still violate the evidence architecture, provenance requirements, participant boundaries, or graph contract.

Validation therefore occurs at four layers:

```text
1. File and schema validation
2. Record and cross-record validation
3. Pre-import graph validation
4. Post-import graph validation
```

A package is not complete until all required layers pass.

---

## 2. Severity Levels

### Error

A blocking violation. The affected package or stage must not proceed.

Examples:

- missing stable ID;
- duplicate ID;
- unresolved required foreign key;
- invalid enum;
- participant mismatch;
- evidence without Source provenance;
- confidence outside `0.00–1.00`.

### Warning

A non-blocking condition requiring visibility or review.

Examples:

- missing Source locator;
- Evidence without Experience context when context is not required;
- partial or unknown dates;
- mapping remains unreviewed;
- likely duplicate evidence text.

### Notice

Informational output describing a valid but meaningful condition.

Examples:

- zero capability mappings supplied;
- optional file omitted;
- existing graph object matched unchanged;
- current Experience has no end date.

Severity must be determined by rule code, not improvised by each importer implementation.

---

## 3. Validation Result Structure

Every finding must include:

```text
rule_code
severity
stage
file
row_number
record_type
record_id
field
message
expected
actual
suggested_action
```

Sensitive values should be redacted or summarized when included in reports.

Every validation run must also include:

```text
validation_run_id
package_id
contract_version
validator_version
started_at
completed_at
status
error_count
warning_count
notice_count
```

Allowed overall statuses:

- `passed`
- `passed_with_warnings`
- `failed`
- `incomplete`

---

## 4. Rule-Code Convention

```text
OSI-[LAYER]-[OBJECT]-[NUMBER]
```

Examples:

```text
OSI-CSV-HDR-001
OSI-REC-EVD-001
OSI-XREF-SRC-001
OSI-GRAPH-EVD-001
OSI-ETHICS-PRV-001
```

Layer abbreviations:

- `CSV` — file and header structure
- `REC` — single-record validation
- `XREF` — cross-record and foreign-key validation
- `GRAPH` — target or post-import graph validation
- `ETHICS` — privacy, consent, and governance validation

Rule codes are stable interfaces. Their meaning must not change silently.

---

## 5. File and Schema Rules

### `OSI-CSV-FILE-001` — Invalid encoding

**Severity:** Error  
File must be valid UTF-8.

### `OSI-CSV-HDR-001` — Missing required column

**Severity:** Error  
Every required contract column must be present.

### `OSI-CSV-HDR-002` — Unknown column

**Severity:** Error by default  
Unknown fields require a contract revision or explicit compatibility mapping.

### `OSI-CSV-HDR-003` — Duplicate column name

**Severity:** Error

### `OSI-CSV-ROW-001` — Malformed CSV row

**Severity:** Error  
Row has invalid quoting, inconsistent structure, or cannot be parsed.

### `OSI-CSV-FMT-001` — Spreadsheet formula detected

**Severity:** Error  
Canonical CSV data must not execute formulas.

### `OSI-CSV-NULL-001` — Invalid null substitute

**Severity:** Error or Warning by field policy  
Values such as `N/A` or `NULL` must not replace actual nulls unless explicitly allowed.

---

## 6. Common Record Rules

### `OSI-REC-ID-001` — Missing stable ID

**Severity:** Error

### `OSI-REC-ID-002` — Duplicate stable ID in package

**Severity:** Error

### `OSI-REC-ID-003` — Invalid ID format

**Severity:** Warning initially; Error when a canonical pattern is enforced

### `OSI-REC-REQ-001` — Required value missing

**Severity:** Error

### `OSI-REC-ENUM-001` — Invalid enum value

**Severity:** Error

### `OSI-REC-DATE-001` — Invalid date

**Severity:** Error

### `OSI-REC-DATETIME-001` — Invalid datetime

**Severity:** Error

### `OSI-REC-WS-001` — Leading or trailing whitespace normalized

**Severity:** Notice

### `OSI-REC-LEN-001` — Value exceeds configured safe length

**Severity:** Warning or Error according to field policy

---

## 7. Participant Rules

### `OSI-REC-PAR-001` — Invalid participant status

**Severity:** Error

### `OSI-REC-PAR-002` — Invalid consent status

**Severity:** Error

### `OSI-ETHICS-PAR-001` — Import not permitted by consent status

**Severity:** Error  
Records must not be imported beyond the participant's consent scope.

### `OSI-REC-PAR-003` — Updated timestamp precedes created timestamp

**Severity:** Error

---

## 8. Source Rules

### `OSI-XREF-SRC-001` — Source participant not found

**Severity:** Error

### `OSI-REC-SRC-001` — Invalid source type

**Severity:** Error

### `OSI-REC-SRC-002` — Invalid confidentiality value

**Severity:** Error

### `OSI-ETHICS-SRC-001` — Sensitive file reference exposed

**Severity:** Error  
File references must not expose credentials, unrestricted local paths, or direct personal identifiers.

### `OSI-REC-SRC-003` — Checksum format unusual

**Severity:** Warning

---

## 9. Experience Rules

### `OSI-XREF-EXP-001` — Experience participant not found

**Severity:** Error

### `OSI-REC-EXP-001` — Missing title

**Severity:** Error

### `OSI-REC-EXP-002` — Invalid experience type

**Severity:** Error

### `OSI-REC-EXP-003` — End date precedes start date

**Severity:** Error

### `OSI-REC-EXP-004` — Current experience has end date

**Severity:** Warning

### `OSI-REC-EXP-005` — Known date status lacks usable date

**Severity:** Warning or Error according to required analysis

### `OSI-REC-EXP-006` — Partial date represented as invalid full date

**Severity:** Error

---

## 10. Evidence Rules

### `OSI-XREF-EVD-001` — Evidence Source not found

**Severity:** Error

### `OSI-XREF-EVD-002` — Evidence Experience not found

**Severity:** Error when populated

### `OSI-XREF-EVD-003` — Participant mismatch

**Severity:** Error  
Evidence participant must match the participant connected to its Source and Experience.

### `OSI-REC-EVD-001` — Evidence text missing

**Severity:** Error

### `OSI-REC-EVD-002` — Invalid evidence type

**Severity:** Error

### `OSI-REC-EVD-003` — Invalid extraction method

**Severity:** Error

### `OSI-REC-EVD-004` — Invalid fidelity status

**Severity:** Error

### `OSI-REC-EVD-005` — Invalid review status

**Severity:** Error

### `OSI-REC-EVD-006` — Source locator missing

**Severity:** Warning

### `OSI-REC-EVD-007` — Expected Experience context missing

**Severity:** Error when `experience_expected=true`

### `OSI-REC-EVD-008` — Evidence text likely duplicates another item in the same Source

**Severity:** Warning  
Similarity detection may flag records, but must not automatically delete or merge them.

### `OSI-REC-EVD-009` — Analytical language detected in Evidence

**Severity:** Warning requiring review  
Potential capability inference, diagnosis, scoring, recommendation, or prediction appears inside evidence text.

This rule is heuristic and must not overwrite or reject valid source statements without human review.

### `OSI-ETHICS-EVD-001` — Restricted content exceeds permitted handling scope

**Severity:** Error

---

## 11. Capability Rules

### `OSI-REC-CAP-001` — Capability definition missing

**Severity:** Error

### `OSI-REC-CAP-002` — Invalid capability status

**Severity:** Error

### `OSI-REC-CAP-003` — Ontology version missing

**Severity:** Error

### `OSI-REC-CAP-004` — Deprecated capability used in new mapping

**Severity:** Warning or Error according to ontology policy

### `OSI-REC-CAP-005` — Duplicate canonical capability name

**Severity:** Warning requiring ontology review

---

## 12. Mapping Rules

### `OSI-XREF-MAP-001` — Evidence endpoint not found

**Severity:** Error

### `OSI-XREF-MAP-002` — Capability endpoint not found

**Severity:** Error

### `OSI-REC-MAP-001` — Invalid relationship type

**Severity:** Error  
Only `SUPPORTS` is permitted in v0.1.

### `OSI-REC-MAP-002` — Confidence outside range

**Severity:** Error  
Confidence must be from `0.00` through `1.00` inclusive.

### `OSI-REC-MAP-003` — Confidence basis missing

**Severity:** Error

### `OSI-REC-MAP-004` — Invalid mapping review status

**Severity:** Error

### `OSI-REC-MAP-005` — Reviewed timestamp absent for accepted or rejected mapping

**Severity:** Warning

### `OSI-REC-MAP-006` — Duplicate Evidence–Capability assertion

**Severity:** Error when mapping identity duplicates; Warning when separate IDs assert the same endpoints and require review

---

## 13. Pre-Import Graph Rules

Before apply mode, validate the target graph.

### `OSI-GRAPH-SCHEMA-001` — Required uniqueness constraint missing

**Severity:** Error

Required node identity constraints:

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
```

### `OSI-GRAPH-PKG-001` — Package ID exists with conflicting checksum

**Severity:** Error

### `OSI-GRAPH-CONFLICT-001` — Protected evidence field conflict

**Severity:** Error

### `OSI-GRAPH-XREF-001` — Required parent absent from package and graph

**Severity:** Error

---

## 14. Post-Import Graph Rules

### `OSI-GRAPH-EVD-001` — Evidence without Source provenance

**Severity:** Error

```cypher
MATCH (e:Evidence)
WHERE NOT (:Source)-[:CONTAINS]->(e)
RETURN e.evidence_id AS record_id;
```

### `OSI-GRAPH-EVD-002` — Evidence has multiple Source owners

**Severity:** Error unless future ontology explicitly permits it

```cypher
MATCH (s:Source)-[:CONTAINS]->(e:Evidence)
WITH e, count(s) AS source_count
WHERE source_count <> 1
RETURN e.evidence_id AS record_id, source_count;
```

### `OSI-GRAPH-EVD-003` — Expected Experience relationship missing

**Severity:** Error

```cypher
MATCH (e:Evidence)
WHERE e.experience_expected = true
  AND NOT (e)-[:OCCURRED_IN]->(:Experience)
RETURN e.evidence_id AS record_id;
```

### `OSI-GRAPH-PAR-001` — Source connected to wrong Participant

**Severity:** Error

```cypher
MATCH (p:Participant)-[:HAS_SOURCE]->(s:Source)
WHERE s.participant_id IS NOT NULL
  AND s.participant_id <> p.participant_id
RETURN s.source_id AS record_id, s.participant_id, p.participant_id;
```

### `OSI-GRAPH-PAR-002` — Experience connected to wrong Participant

**Severity:** Error

```cypher
MATCH (p:Participant)-[:HAS_EXPERIENCE]->(x:Experience)
WHERE x.participant_id IS NOT NULL
  AND x.participant_id <> p.participant_id
RETURN x.experience_id AS record_id, x.participant_id, p.participant_id;
```

### `OSI-GRAPH-MAP-001` — Mapping confidence outside range

**Severity:** Error

```cypher
MATCH (:Evidence)-[r:SUPPORTS]->(:Capability)
WHERE r.confidence < 0 OR r.confidence > 1
RETURN r.mapping_id AS record_id, r.confidence;
```

### `OSI-GRAPH-MAP-002` — Duplicate mapping identity

**Severity:** Error

```cypher
MATCH ()-[r:SUPPORTS]->()
WITH r.mapping_id AS mapping_id, count(*) AS relationship_count
WHERE mapping_id IS NOT NULL AND relationship_count > 1
RETURN mapping_id AS record_id, relationship_count;
```

### `OSI-GRAPH-ORPHAN-001` — Orphan Source

**Severity:** Error

```cypher
MATCH (s:Source)
WHERE NOT (:Participant)-[:HAS_SOURCE]->(s)
RETURN s.source_id AS record_id;
```

### `OSI-GRAPH-ORPHAN-002` — Orphan Experience

**Severity:** Error

```cypher
MATCH (x:Experience)
WHERE NOT (:Participant)-[:HAS_EXPERIENCE]->(x)
RETURN x.experience_id AS record_id;
```

### `OSI-GRAPH-ORPHAN-003` — Unmapped Evidence

**Severity:** Notice  
Unmapped Evidence is valid and must not be treated as a defect.

```cypher
MATCH (e:Evidence)
WHERE NOT (e)-[:SUPPORTS]->(:Capability)
RETURN e.evidence_id AS record_id;
```

---

## 15. Count Reconciliation

For each record type:

```text
received = created + matched_unchanged + updated + skipped + rejected + conflicted
```

Where categories overlap in an implementation, the report must clearly define the counting model and provide a non-overlapping reconciliation total.

Post-import graph counts must match the approved import plan after accounting for existing matched records.

A count mismatch is an Error until explained.

Rule:

### `OSI-GRAPH-COUNT-001` — Import counts do not reconcile

**Severity:** Error

---

## 16. Privacy and Governance Validation

Validation must occur before data leaves its approved handling boundary.

At minimum, check for:

- unsupported consent scope;
- direct identifiers in public or synthetic datasets;
- confidential file paths;
- credentials or secrets;
- participant-private material in repository-bound packages;
- restricted content in logs or reports.

Automated checks supplement but do not replace human privacy review.

### `OSI-ETHICS-PRV-001` — Protected content targeted for public repository

**Severity:** Error

### `OSI-ETHICS-SEC-001` — Credential or secret detected

**Severity:** Error

---

## 17. Acceptance Thresholds

### Package acceptance

A package may enter dry-run when:

- error count is zero;
- schema and record checks are complete;
- warnings and notices are reported.

### Apply acceptance

A package may enter apply mode when:

- package validation passed;
- target graph preflight passed;
- package checksum is stable;
- consent and confidentiality rules permit the import;
- the operator approved any warnings requiring review.

### Completion acceptance

An import is complete only when:

- all planned stages executed;
- transaction outcomes are known;
- counts reconcile;
- post-import Error count is zero;
- import report is finalized;
- package status is `completed`.

Warnings may produce `completed_with_warnings` in a future status model, but must not be hidden.

---

## 18. Regression Test Set

A conforming validator should include synthetic fixtures for:

1. fully valid participant package;
2. missing required column;
3. duplicate Evidence ID;
4. unresolved Source foreign key;
5. participant mismatch;
6. invalid date;
7. confidence below zero and above one;
8. Evidence without Source;
9. expected Experience missing;
10. repeated identical import;
11. conflicting package checksum;
12. protected Evidence text conflict;
13. privacy violation in file reference;
14. valid unmapped Evidence;
15. mapping requiring review.

Every bug fix to validation should add or update a regression fixture.

---

## 19. Versioning

Validation rules are versioned with the contract family.

- New Warning or Notice rules may be additive in a minor version.
- New Error rules that reject previously valid packages require explicit compatibility review.
- Changed rule meaning requires a new rule code or major version.
- Deprecated rule codes remain documented for historical report interpretation.

The validator version, contract version, and rule-set version must appear in every validation report.
