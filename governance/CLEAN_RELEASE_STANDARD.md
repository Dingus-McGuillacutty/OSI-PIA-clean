---
artifact_id: standard-clean-release-001
title: OSI-PIA Clean Release Standard
domain: shared
layer: standard
authority: canonical
status: active
version: "1.0.0"
owner: repository-governance
last_reviewed: "2026-07-24"
review_cycle: annual
---

# OSI-PIA Clean Release Standard

## Purpose

This standard defines how OSI-PIA preserves its restricted development
lineage while creating a separate release lineage that contains no
participant data or participant-derived development evidence.

It implements the clean-release choice recorded by MIG-010. It does not
authorize publication, change access controls, rewrite the restricted
archive, or configure a release remote.

## Two-lineage boundary

### Restricted development archive

The existing repository is the restricted development lineage. Its historical
objects preserve authentic development provenance, including objects that
formerly held participant material.

The restricted archive:

- is not a publication source;
- retains its original history without destructive rewriting;
- remains subject to private access controls;
- is used only for authorized development, audit, or recovery;
- must never be connected as an object source or alternate history for the
  clean release repository.

### Sanitized release lineage

The release repository begins with a new root commit created from a validated
sanitized tree. It has no parent, graft, replacement reference, shared object
store, alternates file, submodule link to the archive, or remote configured by
the release builder.

The sanitized lineage contains only material appropriate for broader release:

- architecture, governance, ontology, contracts, standards, and decisions;
- generic graph mechanisms and migrations;
- software and synthetic tests;
- explicitly synthetic methodological examples;
- release provenance that identifies the source tree without importing its
  history.

## Prohibited release content

The release tree MUST NOT contain:

- participant source exports, archives, messages, resumes, or contact data;
- normalized or derived participant datasets;
- participant-specific Cypher, graph imports, analytical reports, or database
  snapshots;
- identifiers that reproduce restricted development participant identities;
- examples or tests that are not explicitly synthetic;
- credentials, secrets, live databases, generated runtime state, or private
  connector output;
- Git objects, refs, bundles, patches, alternates, or submodules that expose
  the restricted lineage.

Aggregate counts, property inventories, timestamps, and read statistics
exported from a participant-bearing graph are participant-derived development
evidence and are excluded even when they do not identify a person directly.

## Sanitization rules

Before a release tree is created:

1. participant-derived status reports and live graph exports are removed or
   rewritten as generic architecture;
2. executable examples use the contract-reserved synthetic participant range
   `PIA-9000` through `PIA-9999`;
3. analyst and reviewer values are placeholders;
4. participant-specific publications are removed or rewritten as synthetic
   methodological examples;
5. the governance validator, test suite, compilation, and diff-integrity
   checks pass;
6. the exact staged or committed source tree is recorded by Git tree ID.

## Reproducible build

Use the registered clean-release builder:

```text
python software/governance/create_clean_release.py \
  --source . \
  --source-ref <validated-commit-or-tree> \
  --destination <new-empty-directory>
```

The builder:

1. resolves and archives only the selected tree;
2. creates a new directory with no source `.git` content;
3. writes `CLEAN_RELEASE_PROVENANCE.md`;
4. initializes an independent Git repository;
5. creates one root commit with a non-personal release-process identity;
6. runs governance validation in the new repository;
7. verifies one commit, no parent, no remote, and no Git alternates.

The destination must not already exist. The builder never deletes, rewrites,
or modifies the restricted archive.

## Release gates

A clean repository is ready for remote publication only when:

- its governance validator passes;
- all automated tests and compilation checks pass;
- `git diff --check` passes;
- the worktree is clean;
- `git rev-list --count --all` returns `1`;
- the root commit has no parent;
- no remote or object alternate is configured;
- the tracked tree contains no participant-data signature;
- a human reviews the generated provenance record and publication scope.

Creating the local clean lineage is not permission to publish it. Remote
creation, visibility, and push remain separate user-authorized actions.

## Recovery and verification

If validation fails, discard the incomplete destination and correct the
sanitized source tree. Never repair a release by importing commits or objects
from the restricted archive.

The restricted archive remains the recovery source for development history.
The clean release repository remains the publication source. Their histories
must stay deliberately independent.
