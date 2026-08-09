# OSI-PIA Governance

## Purpose

This directory defines the ethical, scientific, knowledge, repository, and
operational boundaries of OSI and PIA.

Governance documents describe what the project may be used for, how knowledge
and implementation are developed, how canonical artifacts are identified, and
what OSI and PIA must not become.

## Repository governance

The proposed [OSI-PIA Governance Model](GOVERNANCE_MODEL.md) consolidates the
repository's constitutional rules for authority, domain independence,
identity, promotion, change, assurance, and human accountability. Version
`0.2.0` has completed its Congruence review but remains working material until
ratified and promoted. The
[Ratification Review](GOVERNANCE_MODEL_RATIFICATION_REVIEW.md) records its
findings, issue dispositions, and Validation evidence.

The repository-governance baseline is:

- [Repository Architecture](Repository_Architecture.md) — domain boundaries,
  architectural layers, dependency direction, and authority;
- [Repository Conventions](Repository_Conventions.md) — identifiers, metadata,
  naming, status, canonical locations, and commit discipline;
- [Namespace Standard](policies/NAMESPACE_STANDARD.md) — consistent domain
  identity across ontology, graph, manifests, contracts, and outputs;
- [Clean Release Standard](CLEAN_RELEASE_STANDARD.md) — separate restricted
  development provenance from a participant-data-free publication lineage;
- [Repository Migration Plan](Repository_Migration_Plan.md) — controlled
  resolution of known path and authority inconsistencies.

The [repository registries](registries/README.md) live under
`governance/registries/`. Registries index canonical artifacts but do not
replace them.

## What belongs here

- the OSI Hippocratic Principle;
- ethical requirements;
- human oversight requirements;
- prohibited uses;
- privacy principles;
- data stewardship requirements;
- scientific integrity standards;
- amendment and review procedures;
- safeguards against misuse;
- repository architecture and conventions;
- canonical artifact registries;
- controlled migration and deprecation rules.

## Governing orientation

OSI and PIA exist to improve human understanding, human cooperation,
organizational health, participant agency, and appropriate human attention.

It must not be designed primarily to:

- control people;
- automate coercion;
- disguise surveillance;
- punish vulnerability;
- suppress dissent;
- or optimize organizational output at the expense of human dignity.

## Relationship to other directories

- `/foundation` explains what OSI is.
- `/principles` contains foundational theoretical claims.
- `/ontology` defines modeled entities and relationships.
- `/research` contains investigations and validation work.
- `/decisions` records major architectural choices.

OSI and PIA are peer domains built on a shared foundation. Cross-domain use
requires an explicit mapping, declared purpose, provenance preservation, and
review proportionate to risk.
