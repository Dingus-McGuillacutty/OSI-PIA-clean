---
artifact_id: publication-template-guide-001
title: "Publication Template Guide"
domain: shared
layer: publication
authority: supporting
status: active
version: "1.0"
owner: publication-stewardship
---

# Publication Template Guide

These templates provide a consistent starting point for public articles while
leaving authors responsible for evidence, interpretation, uncertainty, and
publication review. They are examples, not automatic authority or permission
to publish.

## Templates

- [General article template](ARTICLE_TEMPLATE.md.example) — a standalone
  public-facing essay.
- [Series article template](ARTICLE_SERIES_TEMPLATE.md.example) — an article
  that belongs to a numbered or named sequence.

## Before publication

1. Copy a template into `docs/publications/articles/`.
2. Replace every placeholder in the front matter and body.
3. Use a unique lowercase `artifact_id` and a stable permalink.
4. Keep `status` within the metadata contract; use `lifecycle_state` for
   developmental meaning.
5. Add the artifact to `PUBLICATION_REGISTRY.md` in the same commit.
6. Add the rendered article to the article index.
7. Run the encoding, link, and governance checks before pushing.

The canonical publication source is Markdown. HTML, PDF, and other formats are
generated or distribution artifacts unless explicitly designated otherwise.
