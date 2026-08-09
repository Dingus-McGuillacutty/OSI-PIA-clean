---
artifact_id: software-pia-local-intake-001
domain: pia
layer: implementation
authority: working
status: proposed
version: "0.9.0"
owner: pia-intake
lifecycle_state: formulation
development_state: in_progress_subject_to_change
---

# PIA Local Intake

## Current capability

This package contains the Phase 2A synthetic sandbox, the Phase 2B protected
participant-intake candidate, and the first participant-free Phase 3
credential-definition resolution and Phase 3A independent-review increments
for the
[PIA Intake Subsystem](../../architecture/pia-intake/PIA_Intake_Subsystem_Framework.md).

Phase 2A provides:

- a localhost-only manual intake page;
- purpose, scope, consent, confidentiality, and retention preflight;
- synthetic intake-session creation;
- local document staging outside the repository;
- SHA-256 content checksums;
- exact-duplicate detection within an intake session;
- provenance and document-type metadata;
- append-only local audit events; and
- reproducible stored-content integrity validation.

Phase 2B adds:

- current-user Windows DPAPI protection for the store master key;
- AES-256-GCM encryption for participant metadata, documents, and detailed
  audit events;
- separately located, passphrase-encrypted recovery bundles;
- local owner and reviewer accounts with bounded roles;
- memory-only, restart-invalidated authenticated browser sessions;
- authenticated, bounded active-session summaries and audited protected-session
  resumption after signing in again;
- permanent retirement of deleted participant and session identifiers, with
  fail-closed collision detection and active-list refresh after withdrawal or
  deletion;
- in-memory Windows AMSI inspection before storage;
- immediate withdrawal blocking;
- owner-controlled session-key erasure and encrypted-file removal;
- executable 30-, 90-, and 365-day retention; and
- encrypted audit-chain and stored-content validation.

Protected evidence extraction adds:

- explicit evidence-extraction authorization scope;
- in-memory decryption and non-executing parsing for TXT, CSV, RTF, DOCX, and
  selectable-text PDF sources;
- manual-preparation routing for legacy DOC and general ZIP files;
- bounded source-grounded Evidence candidates with stable provenance and no
  capability assertions;
- encrypted extracted text, candidate records, and append-only review events;
- keep, correct, exclude, and dispute decisions;
- downstream exclusion until accountable review; and
- extraction ciphertext, checksum, provenance, identity, and review-event
  validation.

Protected capability-mapping handoff adds:

- a separate `capability_mapping` authorization scope;
- encrypted, review-required mapping proposals created only from accepted,
  source-grounded evidence;
- working PIA capability-vocabulary selection without participant data;
- required confidence, behavioral basis, scope limit, source-independence,
  and negative-boundary fields; and
- independent accept, reject, and scope-narrowing review events that preserve
  the original proposal and create a superseding mapping when narrowed; and
- explicit prohibition on mapping acceptance, graph projection, reporting, or
  participant scoring by the proposing workflow.

### Controlled mapping-review workflow

Create a mapping proposal only after evidence has been reviewed and retained
for downstream use. Then use a distinct local reviewer account to select the
proposal from the **Review queue** and record one outcome:

| Decision | Protected result |
|---|---|
| Accept | The bounded proposal becomes an accepted mapping. |
| Reject | The proposal remains in audit history and is excluded from downstream use. |
| Narrow scope | The original is retained as superseded and a separately identified, narrower accepted successor is created. |

The proposer cannot make any of these decisions on their own proposal. A sole
operator may exercise owner and reviewer accounts for synthetic technical
testing, but that result must be recorded as single-operator controlled testing
rather than independent human review. Deletion and retention remain owner-only
actions.

After testing, use **Validate store** or the command in
[Validation and retention](#validation-and-retention) to confirm encryption,
checksums, authorization, audit-chain integrity, and retention controls.

### Draft output handoff

The protected intake page can prepare a transient **Working capability
overview** from accepted mappings only. It includes the accepted interpretation,
confidence, evidence basis, and stated boundary. The accompanying manifest is
an exact `local_sandbox` `dry_run` for `PIA-Sandbox`; it has pending assurance
and approval status and performs no graph write. It is not a published report,
participant score, or participant graph projection.

### Sandbox projection assurance

The same draft output produces an offline, participant-minimized package of
accepted `Evidence-[:SUPPORTS]->Capability` assertions. Assurance verifies the
exact manifest selection and count, valid confidence, `PIA-Sandbox` target,
and `dry_run` mode. This component has no Neo4j connection and cannot write a
graph. A later, separately governed stage must provide a synthetic-only import
runner and post-import validation before any sandbox write is considered. The
current synthetic-only runner and read-only validator now provide that bounded
test stage; they do not authorize participant projection.

The current preflight accepts only `neo4j://127.0.0.1:7687` and the
`PIA-Sandbox` database declaration. It intentionally does not open a Neo4j
connection; connecting, importing, and post-import validation are the next
separately governed synthetic-only step.

The synthetic importer is a separate opt-in command. Without `--apply-synthetic`
it prints the exact run declaration and writes nothing. The apply flag uses a
local password prompt and writes only the embedded synthetic test row to
`PIA-Sandbox`; it cannot accept participant material.

Before authentication, the importer validates the embedded package namespace,
confidence range, required fields, and mapping-ID uniqueness. The
`--exercise-invalid-package` option deliberately tests an invalid confidence
and must report that authentication was not attempted and no graph write was
performed. The read-only post-import validator also counts the exact evidence
node, capability node, mapping relationship, and expected path. Each count
must remain one after a repeated import.

This is a backward-compatible addition to the protected store's `0.2.0`
storage schema. New evidence collections and extraction directories are
created only when needed. Existing sessions remain readable, but extraction
is blocked unless their recorded processing scope already includes
`evidence_extraction`.

Phase 3 currently adds:

- a participant-free public credential-definition catalog;
- normalized issuer, family, definition, source, domain, review, and
  expansion-queue records;
- public-source SHA-256 fingerprints without retaining full source copies;
- title, acronym, alias, issuer, version, and effective-date resolution;
- explicit pending-review, ambiguity, version-unknown, source-needed,
  inaccessible, and conflict outcomes;
- reproducible privacy, integrity, supersession, collision, and review
  validation; and
- one review-pending ASIS PSP definition candidate from issuer-primary
  materials.

Phase 3A adds:

- explicit proposal and reviewer actor identities;
- enforceable separation between proposing and reviewing actors;
- a participant-free definition-package view containing the bounded
  definition, public source integrity metadata, domains, and negative limits;
- preview-first accept, accept-with-limits, revision, rejection, and dispute
  paths;
- staged full-catalog validation before any write;
- append-only target-level review events and annual review metadata;
- explicit write enablement, confirmation, single-writer locking, rollback,
  and installed-state revalidation; and
- a localhost review workbench on port 8790.

Phase 3B adds:

- a strict participant-free lookup request contract;
- rejection of unknown, participant, session, evidence, certificate-number,
  completion-date, note, document, contact, and private-path fields;
- deterministic request fingerprints without participant identity;
- catalog-first reuse before participant clarification or external research;
- governed routing for resolved, pending-review, version-unknown, ambiguous,
  source-needed, inaccessible, and conflicting definitions;
- targeted clarification only for issuer or version distinctions; and
- an optional server-side Credential Engine CTDL Search API connector;
- allowlisted endpoints, environment-held API keys, bounded primary-source
  searches, normalized candidate fingerprints, and fail-closed errors;
- a protected-store minimization bridge with encrypted private relationship
  and clarification history;
- authenticated intake endpoints and a low-burden credential check interface;
- withdrawal, deletion, retention, and scope enforcement for private linkage;
  and
- no participant claims or automatic definition acceptance.

## Safety boundary

The synthetic server on port 8788 remains synthetic-only. The protected server
on port 8789 requires a separately initialized participant store and owner
authentication.

The Phase 2B implementation is a working participant-ready candidate, not an
approved production service. Complete the controlled-pilot gate in the
[Phase 2B Protection Profile](../../architecture/pia-intake/PIA_Phase_2B_Protection_Profile.md)
before using real participant material.

The participant intake modes do not:

- transmit content to a remote service;
- accept PNG, JPG/JPEG, HEIC, TIFF, screenshots, or scanned/image-only PDFs;
- use OCR or execute legacy DOC conversion or general ZIP expansion;
- automatically discover credential titles from extracted evidence;
- infer capabilities during extraction;
- write to Neo4j;
- produce graph projections; or
- place staged documents in the Git repository.

The Phase 3 catalog resolves public reference meaning only. It cannot establish
that a participant earned, currently holds, applied, or performed a credential.

## Run the Phase 2A synthetic page

From the repository root, choose an absolute sandbox folder outside this
repository:

```powershell
python -m software.intake.local_intake_server `
  --storage-root C:\private\pia-phase2-synthetic
```

Then open:

```text
http://127.0.0.1:8788/
```

The server binds only to the local loopback interface. The page labels its
synthetic-only boundary and creates no remote or graph connection.

## Validate and query the Phase 3 credential catalog

Validate the participant-free catalog:

```powershell
python -m software.intake.credential_definition_catalog validate
```

Query the current PSP candidate:

```powershell
python -m software.intake.credential_definition_catalog resolve `
  --title "PSP" `
  --issuer "ASIS"
```

The current result is `definition_found_pending_review`. That is expected:
issuer material has been captured and structured, but an independent
credential-definition reviewer has not yet granted reusable
`issuer_verified` status.

## Route a Phase 3B.1 credential lookup

Check the accepted local catalog before any external research:

```powershell
python -m software.intake.credential_lookup_router `
  --title "PSP" `
  --issuer "ASIS"
```

The current seed returns `manual_definition_review` because its PSP candidate
is intentionally still pending Phase 3A review. After an accountable limited
acceptance, the same lookup returns `resolved` without repeating public
credential research.

An unknown credential returns `external_registry_lookup`. The protected intake
can optionally execute the bounded Phase 3B.2 public-registry lookup; the
standalone Phase 3B.1 router never performs network access.

## Run the Phase 3A review workbench

Start in the default preview-only mode:

```powershell
python -m software.intake.credential_review_server
```

Then open:

```text
http://127.0.0.1:8790/
```

Preview mode can inspect a definition and validate a projected decision, but
it cannot change the catalog.

After an accountable reviewer has checked the public sources and the preview,
restart with explicit catalog-write authority:

```powershell
python -m software.intake.credential_review_server `
  --allow-catalog-writes
```

The workbench still requires an explicit confirmation before applying the
review. The current ASIS PSP candidate has incomplete effective-date
boundaries, so unqualified acceptance is blocked. It may be accepted with
explicit limits or returned for revision. Do not enter participant names,
records, credential numbers, completion dates, private paths, or participant
notes in this workbench.

## Initialize Phase 2B

Install the tested cryptography and PDF-text dependencies into the intended
Python environment, then initialize from a private terminal. Passphrases are
prompted without being placed in the command history:

```powershell
python -m pip install -r software\intake\requirements-phase2b.txt
```

Then initialize the protected store:

```powershell
python -m software.intake.phase2b_admin initialize `
  --storage-root C:\private\pia-participant-store `
  --recovery-bundle D:\offline\pia-recovery.json `
  --windowed-passphrases
```

The participant store and recovery bundle must be outside this repository and
must not share the same storage-failure boundary.
`--windowed-passphrases` uses local masked entry windows and is useful when a
terminal does not handle Python's hidden passphrase prompt correctly. It does
not place passphrases in command history or files.

Start the protected server:

```powershell
python -m software.intake.protected_intake_server `
  --storage-root C:\private\pia-participant-store
```

This default mode supports local catalog checks, encrypted linkage, and
targeted clarification without external network access. New sessions whose
scope includes evidence extraction can also extract and review supported
staged documents. Existing sessions without that explicit scope remain
blocked from extraction.

To enable Credential Engine lookup for local catalog misses, first obtain an
approved Credential Engine Search API account and place the key in the current
terminal session:

```powershell
$credentialEngineKey = Read-Host "Credential Engine API key" -AsSecureString
$env:PIA_CREDENTIAL_ENGINE_API_KEY = `
  [System.Net.NetworkCredential]::new("", $credentialEngineKey).Password
Remove-Variable credentialEngineKey
python -m software.intake.protected_intake_server `
  --storage-root C:\private\pia-participant-store `
  --enable-external-credential-lookup
```

Use `--credential-engine-environment sandbox` for an approved sandbox key.
The key stays server-side and is not returned to the browser, persisted in the
participant session, or written to Git.

Then open:

```text
http://127.0.0.1:8789/
```

After a page reload or server restart, sign in again and choose **Review saved
sessions**. The page initially reveals only a bounded summary containing the
private session label, state, human-readable timestamps, and
document/evidence/credential progress. Sessions containing saved work appear
first; empty sessions are visibly labeled and separated in a collapsed group.
The open browser session is marked **Current session**. Choosing **Continue
this saved work** records an encrypted audit event and restores the
staged-document list, current evidence-review decisions, and
credential-resolution results. Authentication remains memory-only; protected
intake sessions remain encrypted and resumable until withdrawal, deletion, or
retention expiry.

Before a new session is created with a private label already used by an open
session, the interface shows the existing session list and requires a second,
explicit choice to create a separate session. This guard reduces accidental
duplicate sessions without treating the private label as a unique participant
identifier.

Deleted session identifiers are permanently retired. New-session allocation
checks both active encrypted sessions and deletion tombstones, and store
validation reports an explicit blocking error if an active directory ever
collides with a deleted identifier. After withdrawal or deletion, the current
workspace and cached active-session list are cleared and refreshed, and the
interface names the exact session removed.

Provision a reviewer from the local terminal:

```powershell
python -m software.intake.phase2b_admin add-reviewer `
  --storage-root C:\private\pia-participant-store `
  --account-id reviewer-001 `
  --windowed-passphrases
```

`--windowed-passphrases` keeps the local owner verification and new reviewer
passphrase entry out of terminal input. Use it when the terminal does not
reliably handle hidden passphrases.

## Validation and retention

Validate the protected store:

```powershell
python -m software.intake.phase2b_admin validate `
  --storage-root C:\private\pia-participant-store
```

Preview expired-session retention:

```powershell
python -m software.intake.phase2b_admin retention `
  --storage-root C:\private\pia-participant-store
```

Add `--apply` only after reviewing the preview. Applying retention erases
expired session keys and removes their encrypted participant files.

The Phase 2A `LocalIntakeStore.validate()` method recomputes synthetic stored
checksums and checks session authorization, retention, synthetic identity,
duplicate references, and storage-root containment.

The Phase 2B `ProtectedParticipantIntakeStore.validate()` method authenticates
encrypted records, verifies content checksums and the encrypted audit chain,
checks consent and retention boundaries, and detects escaped storage
references. Automated tests use temporary synthetic bytes and never add
participant-derived fixtures to the repository.
