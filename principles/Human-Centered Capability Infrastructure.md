---
artifact_id: principle-shared-human-centered-capability-infrastructure-001
title: Human-Centered Capability Infrastructure
domain: shared
layer: principle
authority: working
status: proposed
version: "0.1.0"
owner: architecture-maintainers
lifecycle_state: formulation
---

# Human-Centered Capability Infrastructure

**Status:** Formal architectural principle proposed for governance review  
**Applies to:** PIA, OSI, interoperability, and participant-facing systems

## Principle

> **PIA should be maximally expressive internally, maximally interoperable
> externally, and maximally understandable and useful to the person whose
> capability it represents.**

The purpose of the system is not merely to create richer records about people.
It is to increase the likelihood that people can **recognize, develop,
communicate, and deploy their capabilities into meaningful opportunity and
contribution**.

Therefore, complexity should be absorbed by the system rather than imposed on
the participant. Ontologies, graphs, taxonomies, standards, credentials, AI
inference, and institutional integrations should function as infrastructure
beneath a human-facing layer that remains understandable, contestable,
portable, and practically useful.

## Associated constraint

> **Capability information should not become sequestered inside the
> institutions or technical systems intended to recognize it.**

This constraint exists because capability can be technically represented,
stored, analyzed, or exchanged without producing meaningful benefit for the
person whose capability is being represented.

The architecture should therefore resist designs in which useful capability
information becomes accessible primarily to institutions, employers,
platforms, or technical intermediaries while remaining opaque, inaccessible,
or unusable to the individual.

## Architectural implications

The system should favor:

- participant access to and comprehension of their own capability record;
- portable outputs that remain useful outside PIA;
- transparent evidence and inference rather than opaque scoring;
- interoperability with established systems without making those systems the
  owner of the person's capability narrative;
- translation of institutional and technical complexity into useful individual
  action;
- explicit provenance so a person can understand why a capability claim exists;
- contestability so participants can question, correct, reject, or supplement
  interpretations;
- evidence structures that distinguish observation from inference;
- feedback loops in which new work, learning, and outcomes return value to the
  individual as well as the organization; and
- outputs that help people gain access to relevant work, learning,
  relationships, tools, and developmental opportunities.

## Relationship to PIA and OSI

PIA and OSI address complementary failures in capability conversion.

### PIA

PIA addresses the individual-side recognition problem:

> **What capability exists, what evidence supports it, and how can it be made
> understandable and portable?**

PIA should help individuals recognize and articulate capability that may be
poorly represented by conventional résumés, credentials, job titles,
educational histories, or existing skills taxonomies.

### OSI

OSI addresses the organizational-side conversion problem:

> **Once capability becomes visible, can the organization recognize, trust,
> deploy, and develop it?**

OSI examines whether organizational conditions convert visible capability into
meaningful work, contribution, development, and mobility.

### Interoperability layer

Open skills, Learning and Employment Records, credentials, taxonomies, and
other standards provide infrastructure for moving capability information
between systems. They should serve the human-centered objective rather than
redefine it.

The intended relationship is:

```text
Human lived evidence
        ↓
PIA capability discovery and interpretation
        ↓
Participant-understandable evidence and outputs
        ↓
Standards-compatible translation and portability
        ↓
Institutional recognition
        ↓
OSI conversion conditions
        ↓
Opportunity / deployment / development
        ↓
New outcomes and evidence
        ↓
Value returned to the individual
```

## Meta-purpose

The project began with a failure of capability recognition at the individual
level. OSI emerged from the complementary observation that even recognized
capability may remain underused when an organization lacks the conditions
necessary to absorb and develop it.

Research into open-skills and LER infrastructure revealed the same structural
risk at another scale: valuable capability information may exist inside
sophisticated institutional systems without reliably becoming meaningful
opportunity for the people those systems are intended to serve.

This leads to a broader project purpose:

> **Capability infrastructure should exist to increase human capability and
> opportunity, not merely to improve institutional records about people.**

The participant is therefore not simply a data source, credential subject,
employee record, or object of assessment. The participant is a primary
beneficiary of the system.

## Design test

A proposed feature, data model, integration, or analytical method should be
tested against the following question:

> **Does this make the person's capability more understandable, portable,
> actionable, or developable for the person themselves, or does it primarily
> add another institutional layer around them?**

Institutional utility is desirable and often necessary. Institutional utility
alone is insufficient.

## Concise form

> **Do not merely make capability machine-readable. Make it human-usable.**

## Authority boundary

This is a working/proposed shared principle. It guides current design and
review, but does not supersede canonical governance, authorize production
processing, or establish a claim about any participant.
