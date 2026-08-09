# OSI–PIA Import Contract v0.1

**Status:** Working specification  
**Depends on:** `OSI_PIA_Data_Graph_Contract_v0.1.md`, `OSI_PIA_CSV_Contract_v0.1.md`  
**Purpose:** Define how validated canonical records are written to the OSI/PIA Neo4j graph safely, repeatably, and observably.

---

## 1. Contract Principle

An import is a controlled state transition, not a file upload.

The importer must preserve identity, provenance, interpretation boundaries, and graph integrity while producing enough operational evidence to explain exactly what changed.

```text
Canonical package
    ↓ preflight validation
Dry run and import plan
    ↓ approved execution
Transactional graph writes
    ↓ post-import validation
Import report and audit record
```

No graph write may occur before blocking validation passes.

---

## 2. Required Import Modes

The importer must support:

### `validate`

Parse and validate all files without connecting to or writing to Neo4j.

### `dry-run`

Validate the package, inspect target-graph dependencies, and produce an import plan without changing graph state.

### `apply`

Execute the approved import plan and run post-import validation.

### `resume`

Continue a failed multi-stage import only when the importer can prove that completed stages are idempotent and the package has not changed.

A future `rollback` mode may be added, but v0.1 must never imply rollback capability unless it is actually implemented and tested.

---

## 3. Import Unit

The canonical import unit is an immutable package identified by:

```text
package_id
contract_version
participant_id or declared scope
file checksums
created_at
```

The importer should compute a package checksum from the manifest and file checksums.

If a previously applied `package_id` is presented with different contents, the import must stop with a blocking conflict.

---

## 4. Required Preflight Checks

Before graph writes, the importer must confirm:

- supported contract version;
- required files and headers;
- valid UTF-8 and CSV structure;
- required values and types;
- enum validity;
- unique IDs inside the package;
- foreign-key resolution inside the package or target graph;
- participant consistency;
- no evidence without Source provenance;
- valid confidence range;
- graph connectivity and authentication;
- required constraints and indexes;
- package has not already been applied with conflicting content;
- no blocking Validation Contract failures.

Warnings must be reported but may proceed according to explicit policy.

---

## 5. Canonical Import Order

```text
0. Schema constraints and indexes
1. Participant
2. Source
3. Experience
4. Evidence
5. Capability
6. Evidence–Capability mappings
7. Import audit record
8. Post-import validation
```

This order reflects dependency, not conceptual importance.

The importer must fail clearly when a required parent object is absent. It must not silently create placeholder Participant, Source, Experience, Evidence, or Capability nodes.

---

## 6. Idempotency

All graph writes must be rerunnable without creating duplicate canonical objects.

Node identity must use stable-key `MERGE`:

```cypher
MERGE (p:Participant {participant_id: row.participant_id})
```

Relationships with stable mapping identity must be matched using their endpoints and `mapping_id`, or represented through an assertion node if the database/version cannot reliably enforce relationship identity.

An identical package rerun must produce:

- zero duplicate nodes;
- zero duplicate canonical relationships;
- no loss of prior provenance;
- a report distinguishing matched from changed records.

Idempotency does not mean silently overwriting conflicting values.

---

## 7. Update and Conflict Policy

Fields are classified as:

### Identity fields

Immutable after first successful import.

Examples:

- participant_id
- source_id
- experience_id
- evidence_id
- capability_id
- mapping_id

### Mutable descriptive fields

May be updated when the incoming package is authoritative and the change is logged.

Examples:

- display_name
- title
- description
- review_status
- updated_at

### Protected evidence fields

Must not be overwritten without explicit correction or supersession semantics.

Examples:

- evidence_text
- source_id
- source_locator
- fidelity_status

When an existing protected field differs from incoming data, the importer must classify the record as a conflict and stop or quarantine it according to policy. It must not silently choose one value.

---

## 8. Transaction Boundaries

Each import stage must run in bounded transactions.

Recommended behavior:

- small participant packages: one transaction per record type;
- larger packages: deterministic batches with configurable batch size;
- relationship stages only after all required endpoint stages succeed;
- audit record finalized only after post-import validation passes.

A stage failure must report:

- package ID;
- stage;
- batch or row identifier;
- stable record ID;
- error class;
- whether any prior stage committed;
- safe next action.

The importer must not describe a partially committed package as successfully imported.

---

## 9. Canonical Write Semantics

### Participant

- `MERGE` by `participant_id`.
- Set mutable fields according to conflict policy.
- Preserve original `created_at`.
- Update `updated_at` only from valid authoritative input.

### Source

- `MERGE` by `source_id`.
- Require the Participant before creating `HAS_SOURCE`.
- Preserve confidentiality and provenance fields.

### Experience

- `MERGE` by `experience_id`.
- Require the Participant before creating `HAS_EXPERIENCE`.

### Evidence

- `MERGE` by `evidence_id`.
- Require Source provenance before creating Evidence.
- Create `CONTAINS` from Source.
- Create `OCCURRED_IN` only when `experience_id` is supplied and valid.
- Never manufacture an Experience relationship from text inference during import.

### Capability

- `MERGE` by `capability_id`.
- Treat definitions and ontology versions as controlled ontology content.

### Evidence–Capability mapping

- Require existing Evidence and Capability endpoints.
- Preserve confidence, basis, proposer, review state, and timestamps.
- Rejected mappings remain auditable and must not be rewritten as accepted.

---

## 10. Import Audit Object

Every applied package should create or update an import audit record.

Recommended graph pattern:

```text
(:ImportRun {
  import_run_id,
  package_id,
  package_checksum,
  contract_version,
  mode,
  status,
  started_at,
  completed_at,
  importer_version,
  initiated_by
})
```

Optional relationships:

```text
(ImportRun)-[:IMPORTED]->(Participant)
(ImportRun)-[:CREATED]->(GraphObject)
(ImportRun)-[:UPDATED]->(GraphObject)
(ImportRun)-[:REJECTED]->(ImportIssue)
```

At minimum, an external structured import report must preserve the same information if `ImportRun` is not yet implemented in the graph.

---

## 11. Required Import Metrics

For every record type, report:

```text
received
validated
created
matched_unchanged
updated
skipped
warning
rejected
conflicted
```

Also report:

- package checksum;
- contract version;
- importer version;
- start and end timestamps;
- elapsed time;
- validation summary;
- transaction summary;
- post-import validation result.

Counts must reconcile. The report must explain any difference between received and successfully represented records.

---

## 12. Error Classes

### Blocking preflight errors

No graph writes occur.

Examples:

- invalid schema;
- duplicate ID;
- unresolved required foreign key;
- participant mismatch;
- unsupported contract version;
- package checksum conflict.

### Record conflicts

The incoming record disagrees with protected graph state.

The importer must stop the stage or quarantine the record according to configured policy and report the conflict.

### Transaction failures

A Neo4j write failed after execution began.

The importer must report committed stages, failed stage, and safe recovery procedure.

### Post-import validation failures

Writes completed, but graph invariants do not hold.

The package status becomes `validation_failed`, not `completed`.

---

## 13. Logging and Security

Logs must be structured and useful without exposing protected content.

Logs may include:

- stable IDs;
- file names;
- row numbers;
- rule codes;
- counts;
- timestamps;
- technical error messages.

Logs should not include:

- full participant-private evidence text;
- credentials;
- database passwords;
- sensitive local paths;
- unrestricted source content.

Connection secrets must come from environment variables or an approved secret store, never committed configuration.

---

## 14. Acceptance Criteria

An importer conforms to v0.1 when it can demonstrate that:

1. invalid packages produce no graph writes;
2. dry-run produces the same planned object counts as apply;
3. records are imported in dependency order;
4. rerunning an identical package creates no duplicates;
5. missing parent objects are not silently manufactured;
6. protected evidence conflicts are surfaced;
7. analytical mappings remain separate from Evidence;
8. every applied package produces a reconciled import report;
9. post-import validation is run automatically;
10. a failed or partial run is never reported as complete.

---

## 15. Versioning and Implementation Boundary

This document specifies behavior, not a particular implementation language.

A conforming importer may use:

- Cypher `LOAD CSV` for controlled validation work;
- Python with the Neo4j driver;
- another implementation that satisfies the contract.

Manual Cypher may remain useful for testing, but regular participant ingestion should move toward a reusable importer that reads the machine-readable contract and emits structured validation and import reports.
