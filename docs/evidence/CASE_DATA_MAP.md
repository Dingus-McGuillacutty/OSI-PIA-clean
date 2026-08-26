---
artifact_id: evidence-osi-case-data-map-001
title: "OSI Evidence Case-to-Data Map"
domain: osi
layer: evidence
authority: supporting
status: proposed
version: "0.1"
owner: osi-research
lifecycle_state: validation
---

This map answers the visitor question: **“Show me which tested data supports
this case.”** It connects the public case narratives to the participant-free
synthetic package and states where the connection is only partial or has not
yet been instantiated.

The machine-readable version is [case_data_map.csv](case_data_map.csv).

## Case 001 — Capability Blockage

**Mapping status:** Partial alignment

The current proxy is `OSI-SYN-SRC-002` → `OSI-SYN-EVD-002` →
`OSI-SYN-OBS-002`. The fixture records decisions routed through a single
operational role. That is relevant to a blockage hypothesis, but it does not
encode stable capability, workload, utilization decline, or causality.

- [Source fixture](https://github.com/Dingus-McGuillacutty/OSI-PIA-clean/blob/main/data/fixtures/osi-organizational-evidence-synthetic/source.csv)
- [Evidence fixture](https://github.com/Dingus-McGuillacutty/OSI-PIA-clean/blob/main/data/fixtures/osi-organizational-evidence-synthetic/evidence.csv)
- [Observation fixture](https://github.com/Dingus-McGuillacutty/OSI-PIA-clean/blob/main/data/fixtures/osi-organizational-evidence-synthetic/observation_candidate.csv)
- [Assurance tests](https://github.com/Dingus-McGuillacutty/OSI-PIA-clean/blob/main/tests/test_osi_organizational_evidence_assurance.py)
- [Graph path walkthrough](visualizations/LIVE_SANDBOX_GRAPH_TOUR.md#2-capability-blockage)

## Case 002 — False Capability Signal

**Mapping status:** Bounded match

The tested path is `OSI-SYN-SRC-003` → `OSI-SYN-EVD-003` →
`OSI-SYN-OBS-003`. The evidence explicitly records delivery continuity while
the team relies on undocumented role knowledge. This supports the bounded
output-versus-resilience distinction, not a claim about organizational health
or future failure.

- [Source fixture](https://github.com/Dingus-McGuillacutty/OSI-PIA-clean/blob/main/data/fixtures/osi-organizational-evidence-synthetic/source.csv)
- [Evidence fixture](https://github.com/Dingus-McGuillacutty/OSI-PIA-clean/blob/main/data/fixtures/osi-organizational-evidence-synthetic/evidence.csv)
- [Observation fixture](https://github.com/Dingus-McGuillacutty/OSI-PIA-clean/blob/main/data/fixtures/osi-organizational-evidence-synthetic/observation_candidate.csv)
- [Assurance tests](https://github.com/Dingus-McGuillacutty/OSI-PIA-clean/blob/main/tests/test_osi_organizational_evidence_assurance.py)
- [Graph path walkthrough](visualizations/LIVE_SANDBOX_GRAPH_TOUR.md#3-bridge-dependency-bottleneck)

## Case 003 — Misattribution of Failure

**Mapping status:** Not yet instantiated

The current synthetic package has no evidence row encoding conflicting
reporting paths, unclear authority, or individual attribution. The case is
therefore a public research scenario, not a claim that the current sandbox run
has tested. This distinction is intentional and prevents the graph mechanics
from being presented as stronger evidence than they are.

The next data increment should add a dedicated synthetic record and a test that
asserts the case-specific mapping before this case is called demonstrated.

## What the tests prove today

The assurance suite proves the package's file contracts, provenance links,
synthetic-only identities, review gates, confidence bounds, and negative
boundaries. It does not prove that a narrative case is semantically reproduced
by a fixture unless this map says so.
