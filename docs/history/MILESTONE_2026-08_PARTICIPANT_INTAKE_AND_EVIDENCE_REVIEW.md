# Milestone — Participant Intake and Evidence Review

**Status:** Implemented and validated locally  
**Layer:** Protected participant intake  
**Date:** 2026-08-04

## Accomplishment

The participant-facing intake workflow now operates as a complete, bounded
local flow from workspace setup through participant-controlled evidence review.
The interface has been separated from reviewer-only mapping, credential
interpretation, and graph-projection controls.

## Working participant flow

1. Create a private, time-limited workspace.
2. Choose a supported document and identify its type.
3. See the selected filename and explicit save readiness before upload.
4. Save the document into the protected workspace.
5. Prepare source-grounded evidence review.
6. Keep or exclude each evidence candidate.
7. Change a decision when the participant reconsiders.
8. View a participant-safe summary of kept evidence.
9. Withdraw authorization and stop further processing.
10. Sign out of the local session.

## Governance and boundary behavior

- Participant-friendly scope labels map to the governed internal
  `evidence_extraction` scope.
- Evidence remains review-gated and source-grounded.
- Participant decisions are recorded through the protected review endpoint.
- Reviewer-only mapping, credential meaning, capability interpretation, and
  graph projection remain outside the participant interface.
- The participant summary does not claim a capability assessment or replace
  reviewer interpretation.
- Withdrawal disables further participant processing for the session.

## Validation

The implementation was checked with:

- Python compilation of the protected intake server;
- repository governance validation;
- repository diff-whitespace validation;
- clean-release generation and publication;
- manual browser testing of login, workspace creation, document upload,
  evidence review, reversible decisions, participant summary, withdrawal, and
  sign-out.

## Known next boundary

The next deliberate integration is the reviewer-side completion of any mapping
or interpretation required for a richer participant report. The current
participant summary intentionally exposes only evidence the participant chose
to keep.

## Release references

- Source implementation commit: `8ee49ad`
- Clean release commit: `acd3158`
