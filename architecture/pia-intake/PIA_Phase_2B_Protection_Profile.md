---
artifact_id: architecture-pia-intake-phase2b-protection-001
domain: pia
layer: architecture
authority: working
status: proposed
version: "0.1.0"
owner: pia-intake
lifecycle_state: formulation
development_state: in_progress_subject_to_change
---

# PIA Phase 2B Protection Profile

## Purpose and authority

This profile defines the implemented protection boundary for the Windows-local
PIA participant-intake candidate. It refines Phase 2 of the
[PIA Intake Subsystem Framework](PIA_Intake_Subsystem_Framework.md).

The implementation is `working/proposed`. It is not a production authorization,
a canonical security standard, or approval for unsupervised participant
processing.

## Protection model

### Storage and keys

- Every participant session receives a random 256-bit data key.
- Session metadata and accepted document bytes use authenticated AES-256-GCM
  encryption with record-specific associated data.
- Session keys are wrapped by a store master key.
- Windows Data Protection API protects the master key for the current Windows
  user. Machine-wide DPAPI scope is not used.
- The store directory is initialized with inherited access removed and access
  limited to the initializing Windows user and `SYSTEM`.
- The original filename, participant label, purpose, scope, withdrawal reason,
  evidence metadata, and detailed audit events are encrypted at rest.
- The public store manifest and deletion tombstones contain control state and
  pseudonymous identifiers, not participant document content.
- The master key authenticates the public store manifest, local account
  registry, and deletion tombstones so unauthorized changes are detectable.

DPAPI normally binds protected material to the same Windows user and computer.
Administrator password reset, profile loss, machine loss, storage failure, or
unmanaged backup behavior can make DPAPI-protected material unavailable.
Initialization therefore requires a separately located recovery bundle
encrypted by an independent recovery passphrase. The recovery bundle is
verified before store initialization completes.

### Authentication and authorization

- Owner and reviewer accounts use local identifiers and scrypt password
  verifiers. Raw passphrases are not stored.
- The owner may create sessions, stage evidence, withdraw authorization,
  delete sessions, execute retention, validate the store, and provision
  reviewers.
- Reviewers may create sessions, stage evidence, review state, and record
  withdrawal. They cannot delete sessions or execute retention.
- Browser sessions are random bearer tokens held only in server memory.
- Browser sessions are bound to the local client address and user-agent
  fingerprint, expire after 20 minutes of inactivity, and have an eight-hour
  maximum lifetime.
- Server restart invalidates every browser session.
- State-changing requests require a same-origin, per-session CSRF token.
- Repeated failed login attempts are locally throttled.

The server binds only to `127.0.0.1`. This profile does not authorize network
exposure, remote accounts, federated identity, or remote administration.

### Malware inspection

Uploaded document bytes are sent directly from process memory to the registered
Windows Antimalware Scan Interface provider before storage. No plaintext scan
file is written.

Only `clean` and `not detected` results are accepted. Administrator-policy
blocks, malware detections, provider risk results, initialization failures, and
scan errors all block storage. A rejected artifact produces an encrypted audit
event without retaining the document.

The implementation follows Microsoft's
[AMSI buffer-scanning contract](https://learn.microsoft.com/en-us/windows/win32/api/amsi/nf-amsi-amsiscanbuffer)
and
[AMSI result boundary](https://learn.microsoft.com/en-us/windows/win32/api/amsi/ne-amsi-amsi_result).

### Withdrawal, deletion, and retention

- Withdrawal immediately changes consent to `withdrawn` and processing state
  to `blocked`.
- No further artifact staging is permitted after withdrawal.
- The owner may combine withdrawal with immediate deletion.
- Deletion records an encrypted audit event, overwrites and removes the wrapped
  session-key file, removes encrypted session metadata and artifacts, and
  leaves a non-content deletion tombstone.
- Finite retention classes are 30, 90, or 365 days.
- Retention can be previewed without change or explicitly executed.
- The protected server can be started with explicit retention enforcement.
- Expired, undeleted sessions fail store validation.

Application deletion cannot erase copies held in external backups, filesystem
snapshots, forensic storage, exported reports, or material previously sent
outside this boundary. Operational approval must define those systems and
their corresponding deletion obligations.

## Data flow

1. An authenticated owner or reviewer records purpose, scope, authorization,
   confidentiality, and finite retention.
2. The subsystem creates a pseudonymous participant and intake-session
   identity plus an encrypted session record.
3. A selected document remains in browser and process memory while AMSI
   inspects its bytes.
4. A blocked or failed scan stops intake without storing the document.
5. An accepted document is encrypted before being written to the participant
   store.
6. The encrypted session record receives checksum, provenance, document type,
   scan result, duplicate disposition, and processing-boundary metadata.
7. An encrypted, hash-chained audit event records the operation.
8. Remote processing and graph projection remain disabled.

## Recovery and validation

Reproducible validation checks:

- DPAPI key availability;
- authenticated decryption of session records and documents;
- stored-content SHA-256 checksums;
- encrypted audit-event sequence and hash-chain continuity;
- store-manifest, account-registry, and deletion-tombstone integrity tags;
- duplicate references;
- consent and processing-state boundaries;
- retention deadlines;
- session storage containment; and
- deletion tombstones.

Before a controlled participant pilot, the operator must complete a recovery
drill using a disposable protected store and a separately stored recovery
bundle. Recovery testing must not expose or overwrite an active participant
store.

## Known limits

- The implementation is currently Windows-local.
- Secrets and decrypted content exist transiently in application memory.
- Local administrators, endpoint compromise, memory inspection, malicious
  browser extensions, and compromised antimalware providers remain outside
  the application's sole control.
- Loopback HTTP is not authorized for network exposure.
- Recovery-bundle custody and off-device backup protection are operational
  responsibilities.
- Link acquisition, OCR, legacy-format conversion, automatic credential
  discovery, graph projection, and participant report generation remain later
  phases. The separately governed protected-evidence profile now adds bounded
  local extraction and review for supported staged files.
- Export, correction, and downstream-output deletion still require governed
  integration with each downstream system.

## Controlled-pilot gate

Real participant intake should begin only after:

1. the owner initializes the store without placing a secret in shell history;
2. the recovery bundle is moved to an approved separate location;
3. owner and reviewer access are tested;
4. AMSI preflight and a synthetic rejected-document case are demonstrated;
5. withdrawal, deletion, and retention are exercised on synthetic sessions;
6. recovery is demonstrated on a disposable store;
7. governance, privacy, and security reviewers record approval and residual
   risks; and
8. the participant consent language matches the implemented purpose, scope,
   retention, correction, withdrawal, and deletion behavior.

Until that gate is recorded, Phase 2B is a working participant-ready candidate,
not an approved production service.
