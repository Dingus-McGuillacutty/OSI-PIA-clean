---
artifact_id: governance-model-001
title: OSI-PIA Governance Model
domain: shared
layer: governance
authority: working
status: proposed
version: "0.2.0"
owner: repository-governance
lifecycle_state: congruence
last_reviewed: "2026-07-24"
review_cycle: annual
---

# OSI-PIA Governance Model

## Status and adoption

This document is the proposed constitutional governance model for OSI-PIA.
It consolidates rules already established across repository architecture,
decisions, conventions, registries, namespace governance, knowledge
governance, assurance, and ethical principles.

Version `0.2.0` is working material at Congruence. Its ratification review is
recorded in the
[Governance Model Ratification Review](GOVERNANCE_MODEL_RATIFICATION_REVIEW.md).
It does not supersede an existing canonical authority. Adoption requires an
accepted scoped decision and promotion to `authority: canonical`,
`status: active`.

At Congruence, the model depends on the existing canonical standards and
authorities that supplied its rules. The ratification decision must explicitly
reverse or restate that dependency direction for any standard that will
implement the promoted constitutional model. Until that decision is accepted,
the registered dependencies remain descriptive of the model's derivation and
must not be interpreted as constitutional subordination.

## Purpose

The Governance Model defines how OSI-PIA preserves:

- architectural coherence;
- OSI and PIA domain independence;
- semantic integrity;
- stable identity and canonical authority;
- evidence, provenance, and uncertainty;
- traceable and reversible change;
- human accountability and ethical limits.

When adopted, supporting policies and standards implement this model in
greater detail. They may specialize its rules but must not silently supersede
them.

## Governance objective

Governance exists to make development easier to understand, evaluate, revise,
and extend without allowing architecture or meaning to drift silently.

Governed development is:

- coherent;
- traceable;
- proportionate to risk;
- reversible where practical;
- understandable to humans and machines;
- ethically aligned;
- structurally maintainable;
- explicit about uncertainty and incomplete knowledge.

## Governing rule

> Every promoted artifact has a stable identity, declared domain and scope,
> canonical location, known authority, explicit status, accountable owner,
> and traceable relationship to the rest of the architecture.

Existence in the repository, a database, an analysis, or a deployed system
does not by itself establish promotion or authority.

## Scope

This model applies to persistent project artifacts, including:

- documentation and architectural decisions;
- principles, doctrines, ontology, and epistemology;
- registries, standards, policies, and contracts;
- graph schemas, migrations, imports, and reference-database definitions;
- connectors, configuration, software, tests, and validation;
- data and evidence packages;
- research, analytical models, reports, and publications.

Temporary notes and experiments may use reduced governance, but they must
remain identifiable as working material and must not be presented as
canonical, promoted, or assured.

# Part I â€” Authority framework

## Authority order

The repository's authority order is:

1. governance and human-centered ethical constraints;
2. accepted architectural decisions;
3. foundation and principles;
4. technology-independent ontology;
5. architecture and governed mappings;
6. versioned contracts and standards;
7. executable schema, migrations, connectors, and software;
8. analysis, reports, and publications;
9. research and experiments.

A lower layer implements or tests a higher layer. It must not redefine that
layer through implementation convenience.

## Authority, status, and lifecycle

These dimensions remain separate:

| Dimension | Question | Governed vocabulary |
|---|---|---|
| Authority | How should this artifact be interpreted? | `canonical`, `supporting`, `working`, `historical` |
| Status | Is it currently available and in what operational condition? | `active`, `proposed`, `review-required`, `deprecated`, `superseded`, `retired` |
| Knowledge lifecycle | How mature is the knowledge? | Observation through Stewardship as defined by the Knowledge Lifecycle |

The [Repository Conventions](Repository_Conventions.md) govern metadata and
controlled values. The
[Knowledge Lifecycle](../foundation/KNOWLEDGE_LIFECYCLE.md) governs
knowledge maturity. A status or successful implementation must not be used as
a substitute for authority or justified promotion.

## Canonical authority

Only one active canonical artifact should govern the same scope and version
unless the architecture explicitly defines multiple coexisting authorities.

When apparent authorities overlap:

1. identify their stable artifact IDs and registered scopes;
2. compare meaning rather than filenames;
3. preserve both until authority and migration risk are understood;
4. record the resolution, supersession, or review requirement;
5. update references and registries in the same governed change.

# Part II â€” Domain governance

## Architectural domains

```text
OSI-PIA
â”‚
â”œâ”€â”€ Shared Foundation
â”œâ”€â”€ OSI Domain
â””â”€â”€ PIA Domain
```

### Shared foundation

The shared domain contains meaning and mechanisms legitimately common to both
OSI and PIA, including governance, shared epistemology, provenance, assurance,
lifecycle rules, registries, namespace rules, and approved technical
contracts.

`shared` is not a miscellaneous category. Cross-domain use alone does not make
an artifact semantically shared.

### OSI

OSI governs organizational-system concepts, evidence, graph projections,
analysis, software, and outputs.

### PIA

PIA governs participant-controlled evidence, experience, capability, bounded
assessment, graph projections, software, and outputs.

## Domain independence

OSI and PIA are peer domains built on a shared foundation. Neither is:

- a subset or subordinate implementation of the other;
- merely a data source or analytical feature of the other;
- authorized to redefine the other's ontology;
- authorized to erase the other's consent, purpose, or output boundary.

Domain independence remains visible in namespaces, file paths, identifiers,
registries, reference databases, contracts, schemas, outputs, and decisions.

## Cross-domain interaction

OSI and PIA interact only through an explicit governed mapping, contract, or
application boundary that declares:

1. originating and receiving domains;
2. source and target namespaced identities;
3. purpose and prohibited interpretations;
4. semantic mapping type and direction;
5. provenance and consent requirements;
6. assurance and human-review requirements;
7. expected outputs and retention boundary;
8. accountable owner and approving authority.

Similar language, technical co-location, or use in one report does not
establish semantic equivalence.

Cross-domain behavior must not:

- turn PIA evidence into an OSI conclusion without authorization;
- turn OSI conditions into unsupported claims about a participant;
- conflate organizational and personal capability;
- derive identity-level claims from organizational indicators;
- derive organizational conclusions from isolated participant evidence;
- use shared components to make one domain controlling over the other.

# Part III â€” Identity, registries, and namespaces

## Artifact identity

Every governed artifact has one unique, stable `artifact_id`. Identity remains
stable across file renames, directory changes, formatting changes, and
compatible implementation revisions.

Promoted Markdown artifacts carry the metadata required by the Repository
Conventions. Executable artifacts carry equivalent metadata directly or
through an enclosing registered package.

## Registry rule

> Nothing enters the promoted architecture without a registry entry.

The [registry catalog](registries/README.md) is the authoritative inventory of
registries. Type registries identify what exists, where its canonical form
lives, its domain, layer, authority, status, owner, version, and dependencies.
They point to knowledge; they do not duplicate it.

Registry validation confirms:

- artifact IDs are unique;
- canonical locations exist;
- registered metadata matches artifact metadata where present;
- dependencies resolve and prohibited cycles are absent;
- domain, authority, status, and namespace values are valid;
- links resolve;
- canonical artifacts are not silently duplicated.

## Namespace rule

Every governed artifact and semantic object is attributable to one approved
namespace:

```text
shared
osi
pia
implementation
test
```

The [Namespace Standard](policies/NAMESPACE_STANDARD.md) governs
representation in artifact metadata, ontology IDs, graph projections,
manifests, contracts, records, reports, and exports. A shared technical
mechanism does not automatically have shared semantic authority.

# Part IV â€” Ontology and graph governance

## Ontology authority

The [Ontology Registry](registries/ONTOLOGY_REGISTRY.md) is the canonical
inventory of governed concept and relationship identities and status.
Definitions remain in their registered authorities.

A Neo4j label is not automatically an ontology concept. An ontology concept
does not automatically require a Neo4j label.

An ontologically significant change includes:

- adding, removing, merging, or dividing a concept;
- changing a definition, distinction, domain, or knowledge status;
- changing relationship direction or meaning;
- changing interpretation of existing evidence;
- changing a cross-domain mapping.

Such a change requires impact analysis, registry update, architecture and
contract review, migration guidance, validation, and an ADR when it changes a
durable architectural choice.

## Shared ontology restraint

A concept enters `shared:` only when it has equivalent foundational meaning
and valid use in both domains without loss of domain-specific interpretation.
Similar terms with different meanings remain separately namespaced and may be
related through an explicit mapping.

## Graph architecture

`osi-reference` and `pia-reference` are separate domain projections governed
by the [Graph Architecture](../architecture/graph_ontology/Graph_Architecture.md).
They share engineering, provenance, lifecycle, confidence, and assurance
rules while retaining distinct ontology identities, schema responsibilities,
analytical purposes, privacy boundaries, and outputs.

Reference databases implement and validate governed semantic architecture.
They are not unrestricted production stores, substitutes for ontology
documentation, ungoverned experiment spaces, or the sole source of domain
meaning.

## Graph change

A promoted graph change identifies:

- target database and domain;
- affected labels, relationships, properties, constraints, and indexes;
- ontology and contract mappings;
- compatibility and privacy effects;
- migration sequence and recovery;
- reproducible validation results;
- unresolved review queues.

Cross-database integration uses governed mappings, contracts, or application
services. A third shared graph requires a separate accepted architectural
decision.

# Part V â€” Evidence, connectors, contracts, and data

## Evidence and interpretation

Source facts, Evidence, Observations, analytical assertions, Assessments,
StateEstimates, and human decisions remain distinguishable. Every
interpretive transition preserves source identity, basis, uncertainty,
proposer, review state, time, and applicable consent or privacy boundaries.

Missing evidence remains unknown. It must not be converted into a negative
claim, invented placeholder, or false certainty.

## Connector governance

Connectors use stable sequential identifiers and descriptive directory names,
as defined by the [Connector Standard](../connectors/Connector_Standard.md).
Each connector has one canonical implementation and a manifest declaring its
identity, primary namespace, domain scope, contract, owner, status, version,
source type, privacy boundary, and provenance behavior.

Compatibility copies and examples remain explicitly subordinate to the
canonical connector. Apparent duplicates are compared and their references
reviewed before consolidation or removal.

## Contract governance

Contracts define governed boundaries between producers and consumers. A
contract declares its domain, version, records and fields, semantic
interpretation, validation, provenance, privacy, compatibility, and failure
behavior.

Syntactic validity does not establish semantic validity. Breaking identity,
meaning, or compatibility changes require version review, migration guidance,
and updated consumers and validators.

## Data governance

Data collection and use remain purpose-limited, minimum-necessary,
provenance-preserving, and subject to applicable consent, correction, access,
retention, and deletion requirements.

Private records, credentials, live database files, and generated secrets are
not committed. Synthetic and test data are labeled so they cannot be mistaken
for production evidence.

# Part VI â€” Decisions, change, and migration

## Architectural decisions

ADRs use independent, sequential scopes:

```text
ADR-SHARED-####
ADR-OSI-####
ADR-PIA-####
ADR-IMP-####
```

Shared ADRs govern repository-wide or cross-domain choices. OSI and PIA ADRs
govern their respective domain meaning and projections. Implementation ADRs
govern technical mechanisms and must not override domain decisions.

An ADR records context, decision, scope, status, consequences, dependencies,
supersession, and implementation implications.

## Change classification

| Class | Meaning | Minimum review |
|---|---|---|
| Editorial | Wording or formatting without intended meaning change | Owner review and link checks |
| Corrective | Repairs an error while preserving intended architecture | Owner review and affected validation |
| Additive | Adds a compatible artifact, concept, or capability | Registry and domain-owner review |
| Structural | Changes path, dependency, organization, or authority boundary | Impact analysis and migration review |
| Semantic | Changes meaning, ontology, interpretation, or domain scope | Domain and ontology review; ADR as required |
| Breaking | Invalidates consumers, identities, contracts, or interpretations | Accepted decision, migration, recovery, and full assurance |

Review and evidence increase with consequence, irreversibility, privacy
impact, and semantic reach.

## Migration governance

Migrations are documented, incremental, traceable, and reversible where
practical. A migration states current and target state, affected artifacts,
reason, dependencies, risk, sequence, validation, and recovery.

One commit should represent one coherent architectural change. Large,
mixed-purpose reorganizations are decomposed into reviewable phases.

# Part VII â€” Lifecycle, promotion, and retirement

## Knowledge lifecycle

Knowledge maturity follows the canonical lifecycle:

```text
Observation
  -> Exploration
  -> Formulation
  -> Congruence
  -> Validation
  -> Promotion
  -> Stewardship
```

Operational status remains separate. Implementation can precede promotion,
but it must remain labeled as working or experimental.

## Promotion

An artifact may be promoted when:

- identity, domain, scope, owner, and canonical location are stable;
- a registry entry exists and dependencies resolve;
- applicable decisions are accepted;
- documentation and implementation agree;
- required technical, epistemic, ethical, and congruence checks pass;
- known conflicts and review queues are resolved or explicitly bounded;
- approval is recorded by the accountable authority.

Promotion is a governance action, not merely a commit, merge, deployment, or
successful test.

## Deprecation, supersession, and retirement

Deprecated or superseded artifacts remain traceable. They identify the reason,
replacement, compatibility requirement, and removal or archival path.
Historical provenance is preserved, and two artifacts must not appear
simultaneously canonical for the same scope.

# Part VIII â€” Assurance and human-centered governance

## Governance and assurance

Governance determines what is authoritative, who owns it, how it may change,
and how it relates to the architecture.

Assurance evaluates whether evidence supports claims, implementation matches
declared architecture, and outputs remain within permitted interpretation.
Promotion may require both governance approval and assurance evidence.

Automated validation can detect structural violations. It cannot perform
semantic promotion or replace accountable human judgment.

## Human-centered constraint

OSI-PIA exists to improve understanding, participant agency, cooperation,
development, coordination, organizational health, and repair. It must not be
optimized for coercive control.

Governed work must avoid:

- unsupported person scoring or universal ranking;
- deterministic identity classification;
- hidden or purpose-expanded surveillance;
- claims exceeding available evidence;
- automated consequential decisions without accountable human review;
- treating system output as unquestionable authority;
- optimizing organizational output at the expense of human dignity.

The [OSI Hippocratic Principle](OSI%20Hippocratic%20Principle.md) and
[PIA Measurement Doctrine](PIA_MEASUREMENT_DOCTRINE.md) govern the
domain-specific ethical boundaries.

# Part IX â€” Stewardship and accountability

## Roles

Roles are stewardship responsibilities and need not correspond one-to-one
with named people.

| Role | Responsibility |
|---|---|
| Repository governance | Maintains this model, repository architecture, conventions, registries, and change protocol |
| OSI domain steward | Reviews OSI meaning, boundaries, mappings, and outputs |
| PIA domain steward | Reviews PIA meaning, participant agency, mappings, and outputs |
| Ontology steward | Maintains concept identity, definition authority, status, and semantic impact review |
| Graph maintainer | Maintains graph architecture, migrations, validators, and database conformance |
| Contract or component owner | Maintains versioned interface, implementation, compatibility, and tests |
| Assurance maintainer | Defines checks and preserves assurance evidence without claiming promotion authority |
| Human reviewer | Makes accountable decisions where consent, ethics, semantics, or consequence require judgment |

No role may approve a change outside its authority merely because it can
implement or deploy it.

### Knowledge-governance role mapping

The canonical roles in
[Knowledge Management Governance](../docs/architecture/KNOWLEDGE_MANAGEMENT_GOVERNANCE.md)
map to this model as follows:

| Canonical role | Governance-model specialization |
|---|---|
| Contributor | Any role proposing evidence, analysis, implementation, or amendment |
| Reviewer | Human reviewer and the affected domain, ontology, graph, contract, component, or assurance steward |
| Maintainer | Repository governance and the applicable domain or implementation maintainer |
| Promotion Authority | The authority named by the applicable transition rule; for this model, an accepted scoped shared ADR |
| Steward | Repository governance after promotion, with affected domain stewards retaining their bounded authority |

Implementation access, repository maintenance, or test ownership does not by
itself confer Promotion Authority. A person may hold more than one role, but
the decision record must state which role supplied each review or approval.

## Exceptions

A temporary exception records:

- stable exception identity;
- rule and scope affected;
- justification and risk;
- owner and approving authority;
- compensating controls;
- review or expiry date;
- remediation or retirement plan.

Exceptions must not silently redefine architecture. They cannot waive human
dignity, applicable consent, provenance integrity, or legal obligations.

Each exception is a governed artifact with an `exception-` artifact ID and
the metadata required by Repository Conventions. It must be linked from the
affected artifact's primary registry row or migration record. There are no
active exceptions at this review. Before the first exception is accepted, the
ratification authority must designate its durable registry home; absence of
that registry cannot be used to hide or imply an exception.

## Compliance

Governance compliance is evaluated through:

- registry and metadata validation;
- link and dependency checks;
- contract and schema validation;
- migration and regression tests;
- congruence and epistemic review;
- privacy, consent, and ethical review;
- recorded human approval where automation is insufficient.

Failures remain visible as errors, review requirements, or governed
exceptions. They are not converted into silent defaults.

# Part X â€” Review and amendment

## Review

This model is reviewed:

- before initial promotion;
- when domain boundaries or authority order change;
- when a new registry, namespace, reference database, or artifact class is
  introduced;
- after a material governance failure;
- at major architectural milestones;
- at least annually while active.

Review confirms that the model remains internally consistent, enforceable,
aligned with ethical commitments, and congruent with repository practice.
The front matter records `last_reviewed` and `review_cycle`; while active, the
default cycle is annual from the last completed review.

## Amendment

A material amendment requires:

1. a proposed versioned change;
2. impact analysis across domains and registries;
3. review by affected stewards;
4. an ADR when the change alters a durable architectural choice;
5. updated standards, mappings, migrations, and validation as applicable;
6. an explicit promotion decision.

Historical versions remain traceable through Git and registry history.

## Adoption criteria

Promotion of this proposal to the canonical Governance Model requires:

- confirmation that its authority order does not conflict with accepted
  decisions or ethical principles;
- agreement on stewardship and amendment authority;
- registry, dependency, metadata, and link validation;
- review of OSI and PIA independence and cross-domain protections;
- review of promotion, exception, and human-accountability rules;
- an accepted governance decision or equivalent recorded approval.

Until then, canonical repository authorities continue to govern their current
scopes.


