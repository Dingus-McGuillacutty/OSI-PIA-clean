---
artifact_id: research-pia-ler-open-skills-crosswalk-001
title: PIA to Open Skills and Learning and Employment Record Crosswalk
domain: shared
layer: active-research
authority: working
status: proposed
version: "0.1"
owner: research-governance
lifecycle_state: formulation
review_cycle: milestone
last_reviewed: "2026-09-16"
---

# PIA ↔ Open Skills / LER Crosswalk

**Status:** Working architectural crosswalk  
**Purpose:** Establish how PIA's internal capability and evidence model relates
to existing open-skills, credential, and Learning and Employment Record (LER)
infrastructure.

## Scope and core distinction

PIA should not replace established skill, credential, or LER standards. This
crosswalk is a working map of boundaries and possible translation points, not a
claim that every listed standard has been independently reviewed or that every
mapping is already implementable.

PIA's candidate distinctive layer is upstream:

> **PIA reasons from heterogeneous longitudinal evidence toward defensible
> capability inferences. Existing standards can describe, transport, verify,
> and exchange the resulting claims.**

The working architecture is therefore:

```text
Evidence and inference
  → semantic translation
  → standards-based interchange
  → organizational use
```

## Established ecosystem layers

The following are ecosystem families to be verified against their authoritative
specifications before implementation or formal citation. LER is an ecosystem
and concept, not one single schema.

| Layer | Established representation | Primary function |
|---|---|---|
| Skill and competency semantics | Open Skills Network Rich Skill Descriptor (RSD), Credential Engine CTDL-ASN, 1EdTech CASE | Defines named skills or competencies and their relationships |
| Achievement and evidence record | 1EdTech CLR 2.0, Open Badges 3.0 | Represents achievements, criteria, evidence, results, issuer, dates, and alignments |
| Trust and portability | W3C Verifiable Credentials | Provides portable, issuer-signed, machine-verifiable claims |
| Employment-system interchange | HR Open LER-RS | Translates learning and employment records into résumé, hiring, and advancement workflows |

The project bibliography should attach authoritative references for each
standards family before this crosswalk is used to support a formal paper or
implementation decision.

## PIA crosswalk

Mappings below distinguish direct interchange compatibility from PIA-native
interpretive work. `Strong` means a plausible established representation
exists; it does not mean the PIA claim is automatically valid.

| PIA concept | Closest established representation | Working mapping | Important distinction |
|---|---|---|---|
| Person | VC credential subject; CLR subject or profile | Strong | External identity representation is largely solved |
| Capability | RSD or CTDL-ASN competency | Strong for named capability; partial for higher-order inference | PIA may infer capabilities broader than conventional skill labels |
| Capability name | RSD skill name or CTDL-ASN competency label | Strong | Direct mapping candidate |
| Capability statement | RSD skill statement or CTDL-ASN competency text | Strong | Useful standardized export target |
| Capability category or taxonomy | RSD categories; CTDL-ASN frameworks or collections | Strong | PIA may retain a richer internal ontology |
| External alignment | RSD or CTDL alignments; CLR Alignment | Strong | Can map to occupations, skills, standards, credentials, or frameworks |
| Achievement | CLR Achievement | Strong | Reuse established representation |
| Artifact or work sample | CLR Evidence | Very strong | Supports evidence-backed claims |
| Evidence chain | Multiple CLR Evidence objects plus narrative | Strong externally; richer internally in PIA | CLR can carry evidence while PIA preserves detailed graph relationships |
| Evaluation criteria | CLR Criteria | Strong | Describes what must be demonstrated |
| Observed assessment or result | CLR Result or ResultDescription | Strong | Useful for measured or reviewed outcomes |
| Role during activity | CLR subject role | Strong | Important for work-derived evidence |
| Activity time and context | CLR activity dates | Strong | Supports longitudinal records |
| Evaluator or assessor | CLR source or issuer-related structures | Strong | Separates evidence evaluator from credential issuer |
| Credential or certification | Open Badge or CLR credential | Strong | No proprietary PIA representation is required |
| External endorsement | Endorsement credential | Very strong | Possible bridge from PIA inference to institutional validation |
| Verification or provenance | VC proof, status, and schema; CLR issuer or source | Strong for authenticity | Authenticity does not itself prove validity of a PIA inference |
| PIA confidence | No obvious direct equivalent | Weak | Likely remains PIA-native and bounded |
| Raw observation | Evidence can be represented externally | Partial | Better preserved as a distinct PIA layer |
| Higher-order inferred capability | Competency or achievement export | Partial | The inference process itself is not standardized |
| Developmental trajectory | Longitudinal CLR records | Partial | Standards represent events better than inferred capability growth |
| Learning velocity | No obvious standard equivalent | Weak | Candidate PIA construct |
| Environmental conditions | Little or no direct LER analogue | Weak | PIA and OSI domain |
| Conversion factors | Little or no direct LER analogue | Weak | PIA and OSI domain |
| Capability utilization | Little or no direct LER analogue | Weak | OSI domain |
| Organizational capability absorption | No obvious LER analogue | Weak | OSI-specific research area |
| Employment or résumé export | HR Open LER-RS | Strong | Appropriate downstream interface |

## Where PIA should remain richer

PIA's internal graph should preserve relationships that would be unnecessarily
difficult or inappropriate to force into an interchange standard.

Working internal model:

```text
Person
  ↓
Observation
  ↓
Source
  ↓
Artifact
  ↓
Context
  ↓
Outcome
  ↓
Evidence
  ↓
CapabilityInference
  ↓
Confidence
```

Additional relationships may include:

```text
Evidence → SUPPORTS → CapabilityInference
Evidence → CONTRADICTS → CapabilityInference
CapabilityInference → ALIGNS_WITH → ExternalCompetency
Artifact → PRODUCED_IN → Context
Outcome → RESULTED_FROM → Activity
CapabilityInference → OBSERVED_UNDER → EnvironmentalCondition
```

The standards layer receives the appropriate export, not necessarily the
entire internal reasoning graph.

## Three-layer PIA architecture

### 1. Evidence and inference layer — PIA native

PIA performs or coordinates:

- evidence collection;
- provenance preservation;
- artifact and context linking;
- longitudinal pattern detection;
- capability inference;
- confidence assignment;
- competing-evidence handling;
- developmental trajectory analysis; and
- environmental and contextual interpretation.

This is where the richer graph belongs.

### 2. Semantic translation layer — the socket

The socket converts PIA concepts into established languages. Example paths:

```text
PIA Capability
    ↓
RSD or CTDL-ASN competency

PIA evidence-backed capability claim
    ↓
CLR Achievement + Evidence + Criteria

PIA external validation
    ↓
Open Badge, CLR, or endorsement

PIA career-facing record
    ↓
LER-RS
```

It should also map PIA capabilities to recognized skill taxonomies,
occupational taxonomies, competency frameworks, credentials, job architecture,
and learning pathways. PIA therefore does not require receiving systems to
adopt the complete PIA ontology.

### 3. Trust and interoperability layer — established ecosystem

```text
CLR or Open Badge
       ↓
W3C Verifiable Credential
       ↓
LER, wallet, HR platform, ATS, or talent marketplace
```

Existing infrastructure may handle portability and cryptographic or
institutional verification. PIA must not represent that infrastructure as
validation of an inference it did not independently establish.

## Evidence versus inference

Existing systems are increasingly capable of representing:

> **This person did X and here is the evidence.**

PIA is investigating whether it can defensibly answer:

> **Taken together, what do X, Y, Z, and repeated longitudinal patterns imply
> that this person is capable of doing?**

For example, a conventional skill extractor might return:

```text
Microsoft Access
Neo4j
Cypher
workflow design
documentation
AI
UI design
```

PIA may investigate a bounded higher-order capability such as:

> **Designs and implements knowledge systems that transform heterogeneous
> organizational information into structured, usable decision resources.**

The individual named skills can then be aligned to existing taxonomies. The
higher-order inference and its evidence chain remain the candidate PIA
contribution, subject to participant review, evidence limits, and external
validation where appropriate.

## Potential validation and endorsement pathway

One possible trust model is:

```text
PIA-generated capability hypothesis
        ↓
Participant reviews or accepts claim
        ↓
Evidence is attached
        ↓
Independent reviewer evaluates claim
        ↓
External endorsement
        ↓
Standards-compatible portable assertion
```

This avoids requiring PIA to become an accreditation authority. PIA can serve
as the discovery, evidence-construction, and interpretation system while
qualified third parties provide validation or endorsement.

## Relationship to OSI

PIA and OSI sit on opposite sides of the capability transaction:

| Layer | Working question |
|---|---|
| PIA | What capability does the evidence indicate may exist? |
| Socket or LER layer | How can that capability be represented and communicated in forms existing institutions understand? |
| OSI | What happens when that signal enters an organization? |

OSI examines conditions such as recognition, trust, autonomy, information
access, opportunity, sponsorship, role permeability, development, mobility,
and manager incentives. These may affect whether visible capability becomes:

```text
Capability
    ↓
Deployment
    ↓
Contribution
    ↓
Development
    ↓
Greater Capability
```

The OSI question is not whether a portable record guarantees a result. It is
whether the receiving human system can convert a capability signal into useful
work under observable conditions.

## Current boundary of possible PIA contribution

PIA should not currently claim novelty in:

- digital credentials;
- portable skill records;
- skill taxonomies;
- evidence-linked achievements;
- credential verification;
- machine-readable résumés;
- LERs;
- competency frameworks; or
- skills-first hiring itself.

Those areas already have substantial infrastructure and research. The current
candidate research space is narrower:

> **Can heterogeneous longitudinal evidence be used to infer defensible
> higher-order human capabilities and developmental trajectories that
> conventional credentials, occupational histories, and named skills fail to
> represent?**

And then:

> **Can those inferences be translated into established open-skills and LER
> representations in a sufficiently transparent and evidence-backed form that
> external institutions can trust and act upon them?**

## End-to-end working model

```text
Lived, work, and learning evidence
             ↓
       PIA observations
             ↓
   Evidence and provenance graph
             ↓
     Capability inference
             ↓
 Confidence and evidence chain
             ↓
      PIA translation socket
             ↓
   RSD, CTDL, or CASE alignment
             ↓
 CLR or Open Badge representation
             ↓
 W3C Verifiable Credential
             ↓
 LER-RS, ATS, HRIS, wallet, or other receiving system
             ↓
 Organizational recognition
             ↓
    OSI conversion factors
             ↓
      Capability deployment
             ↓
       Observable outcome
             ↓
        New PIA evidence
```

## Working architectural principle

> **PIA should be maximally expressive internally and maximally interoperable
> externally.**

The graph preserves nuance. The socket preserves compatibility. The standards
ecosystem provides portability. OSI examines whether the receiving human system
can actually convert the capability into useful work.

## Review and source backlog

Before this crosswalk is promoted or used to justify implementation, the
research steward should:

1. attach authoritative specifications for RSD, CTDL-ASN, CASE, CLR, Open
   Badges, Verifiable Credentials, and LER-RS to the Project Bibliography;
2. verify version, status, licensing, and interoperability assumptions for
   each standards family;
3. test each proposed export against a concrete evidence chain without
   discarding provenance or uncertainty;
4. document what each external representation supports and does not support;
5. define how participant review, correction, withdrawal, and selective
   disclosure survive translation; and
6. keep OSI's organizational conditions separate from a portable PIA claim.

This crosswalk is a research instrument. It does not authorize production
exports, accreditation, hiring decisions, organizational diagnosis, or
unsupervised machine action.
