# Milestone: PIA Protected Intake and Credential-Resolution Baseline

Date: 2026-07-28

Status: Implemented and validated working baseline

Authority: Working/proposed; operational review remains required

Commit: `8171e0b`

## Overview

This milestone marks PIA's transition from participant-facing prototypes and
manually prepared evidence experiments to a governed local intake foundation
with executable protection controls and a participant-free credential
definition layer.

The milestone joins three development increments:

1. Phase 2A local synthetic intake;
2. Phase 2B protected Windows-local participant intake; and
3. the first Phase 3 credential-definition resolution increment.

## What became operationally testable

### Phase 2A — synthetic intake

- purpose, scope, authorization, confidentiality, and retention preflight;
- local synthetic document staging outside Git;
- source and document-type metadata;
- SHA-256 integrity fingerprints;
- exact-duplicate detection;
- append-only audit events; and
- a localhost-only manual intake surface.

### Phase 2B — protected intake candidate

- current-user Windows DPAPI protection for the store master key;
- per-session AES-256-GCM encryption for participant metadata and artifacts;
- separately protected recovery bundles;
- owner and reviewer authentication with bounded roles;
- memory-only browser sessions, CSRF protection, and login throttling;
- in-memory Windows AMSI inspection before encrypted persistence;
- immediate processing blocks after withdrawal;
- session-key erasure, encrypted-file deletion, and integrity-protected
  non-content tombstones;
- executable finite retention policies; and
- encrypted audit-chain, authorization, integrity, and containment validation.

### Phase 3 — credential-definition resolution

- a participant-free public credential catalog contract;
- normalized issuer, credential-family, versioned-definition, public-source,
  domain, review, and expansion-queue records;
- exact title, acronym, alias, issuer, version, and effective-date resolution;
- explicit pending-review, ambiguity, version-unknown, source-needed,
  inaccessible, and conflict outcomes;
- title-collision and supersession safeguards;
- participant-data and private-path exclusion from the public catalog; and
- a review-pending ASIS Physical Security Professional definition candidate
  grounded in issuer-primary source material and content fingerprints.

## Validation evidence

At the milestone boundary:

- 72 repository Python tests passed;
- 16 focused Phase 3 credential-catalog tests passed;
- 6 participant-interface build and rendering tests passed;
- repository governance validation checked 119 registry rows, 58 metadata
  artifacts, 471 repository links, 93 ontology identities, and 262 tracked
  paths;
- governance validation found zero restricted participant signatures; and
- the credential catalog validated with zero errors or warnings.

These results establish reproducible implementation coherence. They do not
constitute security certification or production authorization.

## Why it matters

Before this milestone, PIA could demonstrate participant-facing intake and
report concepts, but durable intake of sensitive evidence remained
intentionally blocked.

After this milestone, PIA has:

```text
Participant-facing intake
        ↓
Purpose and consent boundary
        ↓
Malware-inspected encrypted local storage
        ↓
Executable withdrawal, deletion, and retention

Public credential question
        ↓
Participant-free definition lookup
        ↓
Resolved, review-pending, ambiguous, or source-needed outcome
```

The two paths remain deliberately separate. Public credential meaning cannot
be used as proof that a participant earned, applied, or performed the
credential.

## What this milestone does not authorize

The following remain outside the completed boundary:

- unsupervised or production real-participant intake;
- network exposure of the localhost service;
- unreviewed remote or AI processing of participant evidence;
- automatic document extraction or credential discovery;
- automatic promotion of credential definitions;
- credential-to-capability acceptance;
- participant application findings;
- Neo4j participant projection;
- automatic report generation from protected intake; and
- claims that encryption eliminates endpoint, malware, recovery, or operator
  risk.

The ASIS PSP definition remains `source_defined/pending`, not
`issuer_verified`. An independent credential-definition reviewer must examine
and record its bounded interpretation before it becomes reusable authority.

## Remaining operational gate

Before a controlled participant pilot:

1. initialize a disposable protected store using private passphrases;
2. place the recovery bundle in a separate approved failure boundary;
3. complete and record a recovery drill;
4. confirm BitLocker, Windows update, antimalware, browser, and local-account
   posture;
5. review consent language against actual correction, withdrawal, retention,
   deletion, and output behavior;
6. document residual risks and incident response;
7. record governance, privacy, and security approval; and
8. use the approved protected service on port 8789 rather than the synthetic
   port-8788 intake.

## Next milestone

The next PIA milestone is a controlled Phase 3 review workflow that:

- connects minimized credential-definition questions from protected intake to
  the participant-free expansion process;
- supports independent source and definition review;
- preserves participant/private and public/reference separation;
- adds review-cycle and source-change events; and
- remains upstream of Phase 4 application linkage and participant feedback.

The shared graph lane continues separately toward assured Neo4j import and
graph-level assurance.
