# Milestone: PIA Protected Evidence Review and Session Lifecycle

Date: 2026-07-28

Status: Implemented and validated working checkpoint

Authority: Working/proposed; controlled-participant use remains gated

Commit: `369e5a2`

Builds on: [PIA Protected Intake and Credential-Resolution Baseline](MILESTONE_2026-07-28_PIA_PROTECTED_INTAKE_AND_CREDENTIAL_RESOLUTION.md)

## Overview

This checkpoint records the transition from protected document storage and
credential-definition resolution to reviewable evidence intake with durable,
participant-readable session continuity.

It covers the seven development commits after the protected-intake
baseline:

1. governed credential review and lookup routing;
2. protected-intake linkage to credential resolution;
3. protected evidence extraction;
4. explicit image-input limitations;
5. revisable evidence-review controls;
6. authenticated protected-session continuation; and
7. protected-session lifecycle and deletion-integrity hardening.

The checkpoint advances the intake implementation without changing its
`working/proposed` authority or authorizing production participant use.

## What became operationally testable

### Protected evidence extraction

- bounded, non-executing extraction from TXT, CSV, RTF, DOCX, and
  selectable-text PDF documents;
- in-memory decryption and parsing without a temporary plaintext file;
- encrypted extracted-text persistence;
- stable source-artifact, extraction, evidence, and provenance identities;
- exact source locators and parser-version traceability;
- source-checksum and parser-version idempotency;
- explicit routing for unsupported legacy DOC, general ZIP, image, scanned,
  or image-only inputs; and
- an enforced empty capability-assertion output.

Extraction creates review candidates, not capability conclusions.

### Accountable evidence review

- keep, corrected-wording, and exclusion decisions;
- append-only review events preserving earlier decisions;
- visible current disposition before a decision is revised;
- corrected wording that remains source-grounded;
- downstream exclusion until review is complete; and
- restoration of current review state after a deliberate session resume.

### Credential-definition linkage

- protected, minimized credential questions;
- reuse of known public definitions;
- routing of ambiguity, missing version, missing issuer, source gaps, and
  conflicts to governed definition review;
- server-side optional external lookup configuration;
- no participant narrative in public reference queries; and
- no automatic credential-completion, application, or capability claim.

### Protected session continuity

- bounded authenticated listing of resumable sessions;
- saved-work progress showing documents, reviewed evidence, pending evidence,
  and credential checks;
- saved-work sessions separated from empty sessions;
- explicit current-session labeling;
- human-readable creation and update times;
- a warning before creating another session with the same private label; and
- audited restoration of staged documents, evidence state, and credential
  results.

The private label remains a navigation aid, not a unique identity.

### Withdrawal and deletion integrity

- exact removed-session receipts;
- immediate clearing of stale current-session state;
- refreshed session listings after withdrawal or deletion;
- permanent retirement of deleted participant and session identifiers;
- allocation checks against both active sessions and deletion tombstones;
- fail-closed listing and resumption when an active identifier collides with a
  tombstone; and
- an explicit blocking validation finding for deleted-identifier reuse.

Deletion tombstones retain lifecycle proof without retaining participant
content.

## Participant-facing interpretation

The interface now distinguishes four states that were previously easy to
confuse:

| Display state | Meaning |
|---|---|
| Current session | The protected session presently open in the browser workspace |
| Session with saved work | A resumable session containing documents, evidence, or credential work |
| Empty session | A resumable authorization record with no saved evidence work |
| Removed session receipt | The exact session just withdrawn or deleted and no longer available as active work |

Sequential session references are durable audit identifiers. They do not mean
that every earlier session belongs to one continuous participant record.

## Validation evidence

At this checkpoint:

- 119 repository Python tests passed;
- 18 focused protected-intake tests passed;
- the generated participant-interface script passed syntax validation;
- repository governance validation checked 136 registry rows, 65 metadata
  artifacts, 514 repository links, 93 ontology identities, and 291 tracked
  paths; and
- governance validation found zero restricted participant signatures.

These results establish reproducible implementation coherence. They do not
constitute security certification, privacy approval, or production
authorization.

## Version boundary

The checkpoint records:

- PIA Intake Subsystem Framework `0.8.1`;
- PIA Protected Evidence Extraction Profile `0.2.1`;
- protected participant store `0.4.1`;
- protected participant interface `0.4.1`; and
- protected evidence-intake linkage `0.1.0`.

All remain at Formulation and `working/proposed`.

## What remains outside this boundary

- production or unsupervised real-participant intake;
- image or scanned-document OCR;
- automated malware-safe interpretation of image content;
- unreviewed remote or AI processing of private evidence;
- automatic capability inference from extracted text;
- credential-to-participant application findings;
- participant evidence projection into Neo4j;
- automatic participant-report generation from protected intake;
- multi-user or network-exposed deployment;
- completed recovery, privacy, consent, incident-response, and operational
  approval; and
- security or privacy guarantees beyond the validated local controls.

## Next governed checkpoint

The next intake checkpoint should connect accepted evidence to governed
mapping proposals while preserving the separation among:

1. source text;
2. participant-reviewed evidence;
3. public credential meaning;
4. capability interpretation;
5. confidence and uncertainty; and
6. participant-reviewable outputs.

That work must remain downstream of evidence review and upstream of any graph
projection or report claim. The controlled-pilot operational gate remains
open in parallel.
