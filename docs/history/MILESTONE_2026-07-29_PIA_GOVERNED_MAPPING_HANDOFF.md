# Milestone: PIA Governed Evidence-to-Mapping Handoff

Date: 2026-07-29

Status: Implemented and validated working checkpoint

Authority: Working/proposed; controlled-participant use remains gated

Commit: To be assigned at the next intentional commit boundary

Builds on: [PIA Protected Evidence Review and Session Lifecycle](MILESTONE_2026-07-28_PIA_PROTECTED_EVIDENCE_AND_SESSION_LIFECYCLE.md)

## Overview

This checkpoint connects accepted, source-grounded participant evidence to
bounded capability-mapping proposals. It preserves the separation between
evidence extraction, evidence review, capability interpretation, graph
projection, and participant reporting.

The mapping workflow is a protected local handoff. It does not write a
participant record to a graph, generate a report claim, create a participant
score, or promote the working capability vocabulary.

## What became operationally testable

### Bounded mapping proposals

- proposals originate only from evidence already reviewed and included for
  downstream use;
- proposals use the working PIA capability vocabulary without storing
  participant data in that vocabulary;
- each proposal preserves source identity and locator, inference level,
  confidence, confidence basis, behavioral basis, scope limit,
  source-independence note, and negative boundary;
- contextual and educational interpretations remain explicitly bounded; and
- protected mapping records remain encrypted at rest inside the local
  participant store.

### Accountable mapping review

- a proposer cannot accept, reject, or narrow their own mapping proposal;
- an authorized distinct account can accept or reject a proposal with a
  recorded reason;
- narrowing preserves the original proposal as superseded and creates a
  separately identified, accepted successor with narrower boundaries;
- unresolved proposals are presented in a reviewer queue for direct
  selection; and
- all mapping decisions append protected audit events rather than overwriting
  earlier interpretation history.

### Local administration usability

- local reviewer provisioning supports masked windowed passphrase entry when
  terminal hidden-input handling is unreliable; and
- the owner and reviewer account roles can be exercised by one operator for
  controlled technical testing without representing that test as independent
  human review.

## Controlled test evidence

The local protected-store test used only synthetic evidence and local account
roles. The following paths were exercised successfully:

| Test path | Verified result |
|---|---|
| Owner-created proposal + reviewer acceptance | Accepted interpretation retained with its stated confidence and boundary |
| Owner-created proposal + reviewer rejection | Proposal retained in audit history and excluded from downstream use |
| Owner-created proposal + reviewer scope narrowing | Original marked superseded; narrowed successor accepted with explicit replacement boundary |
| Store validation after decisions | Encryption, checksums, audit-chain integrity, authorization state, and retention controls passed |

The final validation displayed 7 synthetic sessions, 4 synthetic artifacts,
and 162 protected audit events. Those counts are test-state observations, not
repository data and must not be treated as participant metrics.

## Operating model

For the present single-operator controlled test environment:

1. the local owner account creates or proposes work;
2. the separate local reviewer account performs the mapping decision; and
3. the test record identifies this as one operator exercising two protected
   roles.

This demonstrates technical role separation and auditability. It does not
substitute for independent human review in a consequential participant or
production workflow. Such use remains subject to the controlled-pilot,
privacy, consent, recovery, security, and operational review gates.

## Validation evidence

- 19 focused protected-intake tests passed after the reviewer-provisioning and
  review-queue additions;
- the protected-store validation passed after the acceptance, rejection, and
  narrowing paths; and
- repository changes remain participant-data-free by design.

These results establish implementation coherence, not security certification,
privacy approval, production authorization, or independent-review completion.

## What remains outside this boundary

- production or unsupervised real-participant intake;
- a formally approved independent-review and exception process;
- graph projection of protected participant mappings;
- automated participant-report generation from the protected mapping state;
- image or scanned-document OCR;
- multi-user or network-exposed deployment; and
- promotion of any working ontology, capability, mapping, or intake artifact.

## Next governed checkpoint

The next checkpoint should define the accountable handoff from accepted,
bounded mapping state to a dry-run projection manifest and participant-facing
outputs. It must preserve every source, review, scope, confidence, uncertainty,
and negative-boundary control established here.
