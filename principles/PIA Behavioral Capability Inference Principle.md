---
artifact_id: principle-pia-behavioral-inference-001
domain: pia
layer: principle
authority: working
status: proposed
version: "0.2.0"
owner: pia-ontology
lifecycle_state: formulation
---

# PIA Behavioral Capability Inference Principle

## Governing principle

> Infer capabilities from demonstrated behavior, not merely from labels—but
> never infer personality, quality, or outcomes beyond what the behavior
> supports.

This principle permits PIA to recognize capabilities that are operationally
demonstrated even when a source does not use the capability's preferred name.
It also prevents a job title, credential, self-description, or isolated phrase
from becoming a demonstrated-application conclusion by itself.

## Evidence completeness and educational evidence

Every supplied evidence item must be considered. Consideration does not
require a positive capability mapping, but it does require a reproducible
disposition such as mapped behavioral evidence, mapped educational evidence,
context only, duplicate or dependent source, unusable metadata, contradictory
evidence, or no supported mapping.

Coursework, training, education, and credentials have evidentiary value. Their
titles and supplied bodies may support bounded claims about:

- structured learning engagement;
- topic and method exposure;
- professional preparation;
- credentialed preparation; and
- relevance to a capability or professional domain.

Educational evidence must remain distinguishable from evidence of workplace
application. Course completion alone does not establish proficiency, quality
of performance, successful transfer, use in a particular job, or a fixed
professional identity.

When educational content and a listed experience map to the same capability,
PIA may record a topical alignment. The alignment can improve the completeness
of interpretation, but it must not be represented as proof that the course
caused, preceded, or was applied in that experience unless the evidence states
that connection.

### Credential-definition resolution

A credential title is not a complete definition of the credential. During
intake, PIA must record whether the assessed domain is `source_defined`,
`issuer_verified`, `participant_defined`, `title_only_unknown`, or
`conflicting_definition`. A title-only or conflicting definition must remain
explicit and enter a definition-expansion queue. The intake should request:

- the issuer's domain or body-of-knowledge definition and applicable version;
- the knowledge, tasks, or skills assessed;
- prerequisites or experience requirements;
- the work contexts in which the participant applied the preparation; and
- any artifact, result, or independent source that could support the
  application link.

Issuer material can resolve what a credential covers. It does not prove that
the participant applied the full body of knowledge or performed effectively.
When participant evidence explicitly names both credential completion and its
application in a work context, PIA may record
`explicitly_attributed_in_source`. The educational assertion remains
`knowledge_exposure`; the work evidence separately supports demonstrated or
inferred application.

## Evidence classes

Every behavioral capability assertion must be classified as one of:

1. **Directly demonstrated** — the evidence describes the behavior, work
   product, responsibility, or result with enough specificity to support the
   capability directly.
2. **Strongly inferred** — multiple details or a sufficiently specific
   behavior pattern support the capability even though the capability is not
   named.
3. **Contextually suggested** — the surrounding context makes the capability
   plausible, but the evidence is not yet strong enough for an accepted
   mapping.

A contextual suggestion is a review lead, not a positive finding. It should
remain unmapped unless preserving it as a proposed assertion materially helps
human review.

Educational preparation is an evidence role, not a fourth behavioral
inference class. Its bounded capability mappings remain review-required and
must identify `knowledge_exposure` rather than `demonstrated_application` as
their claim scope.

## Required inference boundary

Every inferred mapping must preserve:

- the behavior that supports the inference;
- the source and evidence chain;
- the inference class;
- mapping confidence and its basis;
- source-independence or duplication limits;
- review status; and
- a **negative boundary** stating what the evidence does not establish.

For example, coordinating a system implementation may support project
leadership and stakeholder coordination. It does not by itself prove formal
people-management authority, organization-wide strategic leadership, or a
particular outcome.

## Capability granularity

Broad labels such as `Teamwork` and `Leadership` are too ambiguous to be
direct evidence-to-capability targets. PIA should map the specific operational
capacity shown by the evidence.

Teamwork-related evidence may support capabilities such as collaborative
execution, cross-functional collaboration, stakeholder coordination, shared
problem-solving, knowledge sharing, feedback integration, role coordination,
handoff management, conflict navigation, or team capability development.

Shared Problem-Solving may be strongly inferred when the same documented
experience contains both:

1. problem-directed behavior, such as analysis, improvement, response,
   design, or resolution; and
2. evidence that the work occurred through an interdependent group,
   department, project, or organization.

The inference is bounded to that experience. It does not establish equal
participation, consensus, shared authority, or that every phase of defining
and resolving the problem was jointly performed. Mere membership in a group,
without problem-directed behavior, is insufficient.

Reflective Learning may be strongly inferred when evidence shows that
professional learning was examined, adapted, translated, or taught for use in
work. Completion alone is insufficient, and the inference must not imply a
formal reflective method when none is described.

Leadership-related evidence may support project, team, operational, technical,
training and development, governance, crisis, informal or peer, change, or
strategic leadership. These are not interchangeable, and one must not be
substituted for another without evidence.

## Ecosystem-aware, participant-centered interpretation

PIA may represent how a participant:

- coordinated with stakeholders;
- enabled users or peers;
- mentored, taught, or transferred knowledge;
- led a project, team, function, implementation, or response;
- translated information between groups;
- improved shared work;
- received or exercised bounded responsibility; or
- operated under constraints involving trust, authority, risk, or urgency.

The surrounding people and institutions provide context. They are not
additional participants to be profiled, and PIA must not infer their traits,
motives, or capabilities beyond what the source establishes.

## Absence, contradiction, and incompleteness

Pattern-level reporting should distinguish:

- evidence present;
- emerging evidence;
- insufficient evidence;
- contradictory or mixed evidence; and
- not yet assessed.

Insufficient evidence means the available evidence does not currently support
the scoped finding. It never means the participant lacks the capability.

## Analytical domains

The working PIA capability profile organizes reportable patterns into:

1. systems and information;
2. project design and execution;
3. analysis and decision support;
4. communication and translation;
5. collaboration and teamwork;
6. leadership and human development;
7. risk, resilience, and stewardship; and
8. learning, adaptation, and professional development.

These domains organize evidence for explanation. They are not participant
scores, personality dimensions, or fixed identity categories.

## Promotion boundary

This is a working, proposed principle. Implementation may use it for
reversible testing and review, but it does not supersede the canonical
[PIA Measurement Doctrine](../governance/PIA_MEASUREMENT_DOCTRINE.md).
Promotion requires documented review, reproducible validation, and explicit
human approval under the repository governance model.
