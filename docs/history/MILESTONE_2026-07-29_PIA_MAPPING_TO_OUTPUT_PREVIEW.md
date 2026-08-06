# Milestone: PIA Mapping-to-Output Preview

Date: 2026-07-29

Status: Implemented and validated working checkpoint

Authority: Working/proposed; controlled-participant use remains gated

Commit: To be assigned at the next intentional commit boundary

Builds on: [PIA Governed Evidence-to-Mapping Handoff](MILESTONE_2026-07-29_PIA_GOVERNED_MAPPING_HANDOFF.md)

## Overview

This checkpoint records the first protected handoff from accepted capability
mappings to a participant-readable draft output and an exact dry-run projection
manifest. It preserves the distinction between a bounded interpretation,
technical evidence detail, output assurance, and graph projection.

## Implemented boundary

- only currently accepted mappings can enter a draft output;
- repeated mappings are grouped into one participant-facing capability pattern;
- the technical companion retains each individual accepted mapping and its
  evidence boundary;
- incomplete, excessively brief, or obvious test-only confidence, scope, or
  boundary fields hold the participant overview for output assurance;
- the hold state provides a safe corrective path through a new, reviewer
  accepted revision rather than altering historical mapping records;
- superseded mappings remain auditable but leave the current output state; and
- the manifest remains `local_sandbox`, `dry_run`, pending approval, and
  explicitly records that no graph write occurred.

## Controlled report-ready test

A fresh synthetic session was used to avoid mixing earlier exploratory mapping
history with the positive output test. Three mappings were created, reviewed
by the distinct local reviewer account, and accepted. The prepared output:

- grouped the three mappings into one bounded `Handoff Management` pattern;
- retained the strongest accepted working confidence of `0.7`;
- displayed the stated interpretation boundary;
- reported three underlying technical-companion mappings; and
- produced a dry-run manifest with output assurance `pass` and no graph write.

This verifies the complete synthetic path:

```text
protected document → reviewed evidence → accepted mapping →
output assurance → participant preview + dry-run manifest
```

## Interpretation and limits

The output is a transient working preview, not an exported report, graph
record, participant score, independent professional assessment, or published
claim. The passed synthetic test does not authorize production participant
processing, graph projection, report publication, or promotion of working
ontology and capability definitions.

## Remaining gates

- formal independent-review and exception governance;
- participant-facing report composition, export, and deletion controls;
- approved dry-run and post-write graph assurance before any sandbox import;
- image and scanned-document support;
- production privacy, consent, recovery, incident-response, and operational
  review; and
- network-exposure and multi-user deployment controls.
