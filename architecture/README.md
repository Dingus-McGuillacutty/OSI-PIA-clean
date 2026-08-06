# Architecture Map

This directory contains stable and working architecture records. The folders
are intentionally separated by architectural concern; they are not alternate
copies of the same system.

## Current architecture areas

| Directory | Purpose | Status |
|---|---|---|
| `Architecture/` | OSI domain, repository, and system architecture | Supporting and canonical records |
| `graph_ontology/` | Shared graph architecture, OSI/PIA reference databases, ontology crosswalks, and graph congruence | Canonical graph boundary |
| `graph_standards/` | Graph naming, schema, and implementation standards | Supporting standards |
| `pia-intake/` | PIA intake subsystem, protection, credential, and review architecture | Working/proposed |
| `Import Pipeline/` | Import and projection pipeline architecture | Supporting implementation architecture |

## Related architecture records outside this directory

Some concerns have deliberately separate homes:

- `decisions/` contains ADRs. It is the authoritative decision record; ADRs do
  not belong inside an architecture folder.
- `docs/architecture/` contains shared knowledge-management, assurance, and
  system reference documents.
- `foundation/` contains the OSI and PIA conceptual foundations and
  meta-models.
- `ontology/` contains technology-independent ontology definitions.
- `analysis/` contains analytical outputs, not architecture.
- `graph/` contains executable graph schema, migrations, imports, and
  validation code.
- `software/` contains implementation code, including the PIA intake service
  and participant/reviewer interfaces.

## Intended future vocabulary

As the repository is migrated, architecture concerns may be grouped under
these names:

```text
architecture/
├── domain/       OSI and PIA domain architecture
├── system/       cross-component system architecture
├── components/   component and subsystem architecture
├── graph/        graph and projection architecture
├── analytics/    analytical architecture
├── ui/           interface and participant/reviewer experience architecture
└── intake/       PIA intake architecture
```

This is a target vocabulary, not an authorization to move files immediately.
Existing paths remain valid until a governed migration updates links,
registries, tests, and release manifests together.

## Navigation rule

When a document could fit more than one area, classify it by its primary
architectural responsibility and link to related concerns rather than creating
a duplicate copy. The architecture registry and the linked canonical
documents govern when this map is only descriptive.
