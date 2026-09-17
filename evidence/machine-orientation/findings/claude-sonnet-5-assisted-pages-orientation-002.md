---
artifact_id: finding-machine-orientation-claude-assisted-pages-002
title: "Claude Sonnet 5 Assisted Pages Orientation"
domain: shared
layer: evidence
authority: working
status: active
lifecycle_state: observation
version: "0.1.0"
owner: research-governance
test_stage: stage-1-assisted-orientation
related_runs:
  - claude-sonnet-5-assisted-pages-orientation-002
  - research-machine-orientation-conformance-001
---

# Claude Sonnet 5 Assisted Pages Orientation

## Record boundary

This record documents a multi-part, user-assisted orientation run against the
public OSI-PIA Pages site and clean repository. It is deliberately scoped as
an improvement over the earlier Claude access termination, while excluding
automatic discovery and autonomous link following from the assessment.

It is not a blind discoverability score, a general Claude capability claim, or
evidence that the site is indexed for all computational environments.

## Test condition

| Field | Result |
|---|---|
| Model | Claude Sonnet 5 |
| Surface | OSI-PIA GitHub Pages site and clean repository |
| Access condition | User supplied or directly opened the public entry content |
| Orientation condition | Assisted reading of the public landing and Start Here path |
| Automatic search discovery | **Excluded** |
| Autonomous link following | **Excluded** |
| Repository mutation | None authorized or observed |
| Real participant material | **No** |
| Exact model-session identifier | Not supplied |

## Observed results

Claude correctly identified:

- OSI as Organizational Systems Intelligence and PIA as Professional Identity
  Architecture;
- the clean, participant-data-free release lineage;
- the peer relationship between OSI and PIA and their governed mappings;
- the evidence, assurance, graph, governance, and publication layers;
- the non-production and non-authorized status of the current implementation;
- the distinction between evidence, interpretation, graph projection, and
  human-accountable output; and
- the public Pages site as a navigable explanation and orientation surface.

It also recognized the practical distinction between the public Pages route and
the repository's deeper canonical artifacts. When its fetcher could not proceed
from a discovered page to additional URLs, it disclosed the limitation instead
of claiming to have read those files.

## Corrected observations

The run included two claims that do not match the current repository state:

1. The report described `START_HERE.md` as having several plain-text dead ends.
   The current file contains linked entries for the orientation path and now
   includes direct links to the public publications, articles, briefs, and
   bibliography.
2. The report described the visible repository history as a single commit.
   The clean repository currently has a multi-commit history. A shallow or
   limited external view may explain that observation, but the test does not
   establish repository history from that view alone.

These are retrieval/view limitations or stale observations, not evidence that
Claude misunderstood the architecture.

## Layered assessment

```text
Source admission after assistance       successful
Project identity recognition             successful
Architecture and governance orientation successful
Current-state checking                   partial; two stale/view claims
Automatic discovery                      excluded
Autonomous link following                excluded
```

The central improvement over the earlier Claude run is that the model was able
to form a grounded project interpretation once the public source was admitted.
The earlier run could not begin orientation at all. This run therefore provides
evidence about assisted source admission and orientation quality, not about
search ranking or independent traversal.

> **External model can traverse from high-level orientation into canonical
> technical architecture and preserve critical authority and ethical boundaries
> when the artifact is directly retrievable.**

In this record, “directly retrievable” is the limiting condition. The statement
does not imply autonomous discovery, unrestricted link following, or authority
to change the source environment.

## What this test supports

- Pages is an effective human-readable and machine-orienting public surface
  once reached.
- Redundant identity, status, and boundary language helps an unfamiliar model
  reconstruct project meaning from limited context.
- A model can preserve uncertainty about inaccessible deeper material while
  still interpreting the material it actually saw.
- Public navigation and repository authority can be separated without merging
  the two roles.
- Stale or shallow views of commit history and link structure must be checked
  against the source repository before being treated as project facts.

## What this test does not support

- It does not show that Claude can discover OSI-PIA through ordinary web search.
- It does not show that Claude can autonomously follow every public link.
- It does not establish that Pages is indexed or retrievable in other model
  environments.
- It does not establish general machine alignment, safety, or conformance.
- It does not authorize repository changes, publication promotion, or any
  participant or organizational decision.

## Replication design

The next comparison should keep the conditions explicit:

| Condition | Discovery | Link following | Orientation score |
|---|---|---|---|
| Blind | Included | Included | Score only after access passes |
| Assisted entry | Excluded | Excluded | Score orientation and uncertainty handling |
| Assisted deep retrieval | Excluded | User-supplied links only | Score file-level interpretation separately |

The assisted result should not be combined with the blind result. They answer
different questions and expose different boundaries in the chain:

```text
public to humans
→ machine-reachable
→ machine-readable
→ machine-understood
→ authorized to act
```

## Related evidence

- [Earlier Claude access finding](claude-access-discoverability-and-admission-001.md)
- [Claude Sonnet 5/high orientation record](../scored-results/claude-sonnet-5-high-run-001.md)
- [Outside Machine Orientation and Conformance Test](../../../active-research/experiments/MACHINE_ORIENTATION_CONFORMANCE_001.md)
