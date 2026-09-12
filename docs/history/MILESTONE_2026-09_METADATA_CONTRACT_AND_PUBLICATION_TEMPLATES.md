---
artifact_id: milestone-metadata-contract-publication-templates-001
title: Metadata Contract and Publication Templates
domain: shared
layer: history
authority: supporting
status: active
version: "1.0.0"
owner: repository-governance
lifecycle_state: validation
---

# Milestone: Metadata Contract and Publication Templates

**Date:** 2026-09-11  
**Status:** Architectural milestone

## Summary

OSI-PIA moved artifact metadata from convention to a governed interface.
Required fields and controlled vocabularies are now defined in a versioned,
machine-readable contract and consumed by the repository governance validator.
This gives human and computational contributors a shared, testable agreement
about how artifacts identify their authority, status, lifecycle, ownership, and
relationships.

Publication creation also gained a proper entry path. Authors now have a
documented guide and reusable templates for both individual articles and
article series. Publication hubs link to those templates, and the publication
registry records the guide as a governed supporting artifact.

## What changed

- Added the [artifact metadata contract](../../data/contracts/osi_pia_artifact_metadata_contract_v0.1.json)
  and its human-readable [contract guide](../contracts/OSI_PIA_Artifact_Metadata_Contract_v0.1.md).
- Updated the repository governance validator to load and enforce the
  contract's controlled vocabularies.
- Added regression coverage confirming that status and lifecycle state remain
  distinct dimensions.
- Corrected and registered recent research and evidence records whose metadata
  had used lifecycle terms as statuses.
- Added an [article template](../publications/templates/ARTICLE_TEMPLATE.md.example),
  an [article-series template](../publications/templates/ARTICLE_SERIES_TEMPLATE.md.example),
  and a [publication template guide](../publications/templates/README.md).
- Linked the authoring path from the publication documentation hubs and
  registered it in the publication registry.

## Development boundary

This milestone improves machine-readable governance, publication consistency,
and authoring usability. It does not promote research into canonical
architecture, make an artifact self-authorizing, or authorize production
processing, automated hiring, or unsupervised participant handling.

Metadata is now an interface for governed interpretation, not a substitute for
human review or stewardship.

## Validation

At milestone capture:

- repository governance validation passed: 191 registry rows, 98 metadata
  artifacts, 768 repository links, 93 ontology IDs, 411 tracked paths, and no
  restricted participant signatures;
- focused governance tests passed;
- publication encoding checks passed for 13 Markdown files; and
- the working tree passed `git diff --check` (with only expected line-ending
  warnings).

The implementation was recorded in commit `b9a2dea`.
