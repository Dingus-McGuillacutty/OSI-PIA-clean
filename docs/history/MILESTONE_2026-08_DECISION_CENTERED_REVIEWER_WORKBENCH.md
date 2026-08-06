# Milestone — Decision-Centered Reviewer Workbench

**Status:** Working structural baseline validated in the browser
**Date:** 2026-08-05
**Domain:** PIA protected intake and evidence review

## Accomplishment

The owner/reviewer interface was replaced with a dedicated evidence-review
workbench. The new route is organized around the reviewer's professional
decisions rather than the internal order of repository artifacts or ontology
fields.

## Implemented experience

- A concise header states the reviewer's actual task: review evidence and
  support capabilities.
- Protection controls remain visible without dominating the working surface.
- A compact six-stage tracker communicates workspace, evidence, credential,
  summary, and completion state.
- The primary workspace uses three panes:
  - documents;
  - extracted statements; and
  - the selected statement and its decision controls.
- Accept, Edit, and Reject remain connected to the protected evidence-review
  endpoint and append-only audit history.
- Accepted, edited, rejected, and remaining counts update from the current
  evidence state.
- The layout stacks responsively on narrower windows without turning the stage
  tracker into oversized cards.

## Preserved integrity controls

The redesign did not remove or bypass:

- participant authorization and bounded processing scope;
- encrypted participant storage;
- source and evidence identifiers;
- review-decision history;
- reviewer identity;
- withdrawal and retention controls; or
- the separation between evidence review, capability interpretation, and
  publication.

## Design principle demonstrated

The system should carry architectural complexity beneath the interface. The
reviewer should conduct a careful professional review rather than manually fill
out the ontology.

## Next bounded work

1. Add reviewer notes and explicit limits to the selected-statement pane.
2. Attach capability-support cards directly to accepted evidence.
3. Derive numeric confidence and source-diversity metadata from categorical
   reviewer choices and recorded provenance.
4. Add filtering, pagination, credential-review handoff, and completion-state
   testing.
5. Test conditional independent challenge instead of requiring a second
   reviewer for every ordinary mapping.

## Release references

- Reviewer page replacement source commit: `0f07ea5`
- Responsive tracker source commit: `820cc34`
- Validated clean release: `cda52ed`
