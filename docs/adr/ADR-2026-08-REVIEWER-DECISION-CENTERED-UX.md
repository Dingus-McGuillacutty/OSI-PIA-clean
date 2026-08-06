# ADR — Decision-Centered Reviewer Experience

**Status:** Accepted; first structural implementation complete
**Date:** 2026-08-05

## Decision

The reviewer interface will be organized around professional decisions rather
than internal ontology fields:

1. Open the protected workspace.
2. Add evidence.
3. Review what the source actually says.
4. Decide what accepted evidence may support.
5. Prepare a review summary.

## Reviewer-facing vocabulary

The reviewer should primarily see:

- Accept, Edit, or Reject;
- Strength of support: Tentative, Moderate, Strong, or Directly demonstrated;
- Reviewer rationale;
- What this evidence does not establish;
- Scope or known limits.

Numeric confidence, source-independence metadata, and other provenance fields
remain captured by the system but should not be required as manual ontology
entry unless a governed exception requires them.

## Assurance boundary

This redesign does not remove audit history, provenance, evidence-chain
integrity, reviewer identity, or review-required mapping status. It changes the
presentation and derives internal values from simpler reviewer choices.

Independent challenge remains available when confidence is low, evidence is
conflicted, the capability is consequential, or publication assurance requires
it. It is not mandatory for every ordinary review.

## Implemented structural baseline

The owner/reviewer route now uses a dedicated decision-centered workbench while
retaining the existing protected endpoints and audit records. Its desktop
reference contains:

- a compact six-stage workflow tracker;
- protected workspace and evidence-intake controls;
- a document pane;
- an extracted-statement queue;
- a selected-statement decision pane; and
- a live review summary.

The next implementation pass places capability support directly inside the
selected-statement pane and derives remaining technical mapping fields from the
reviewer's simpler choices.
