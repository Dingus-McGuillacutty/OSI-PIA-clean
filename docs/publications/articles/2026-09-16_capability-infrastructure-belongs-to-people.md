---
artifact_id: publication-article-capability-infrastructure-people-001
title: "Capability Infrastructure Should Belong to the People It Describes"
domain: shared
layer: publication
authority: supporting
status: active
version: "0.2"
owner: publication-stewardship
series: "Hiring and Capability Recognition"
series_part: 9
permalink: /publications/articles/2026-09-16_capability-infrastructure-belongs-to-people.html
---

# Capability Infrastructure Should Belong to the People It Describes

## Systems built to recognize human capability should increase individual agency and opportunity—not bury that capability inside another layer of institutional machinery.

## Publication Note

This article is part of the OSI-PIA public article series. It describes an
active research and development direction. It does not claim that OSI-PIA is a
finished hiring product, validated employment-screening system, legal
compliance tool, or production decision system.

## Article

There is already a substantial technical ecosystem for describing learning,
skills, credentials, work experience, and employment records. There are open
skills frameworks, Learning and Employment Records, verifiable credentials,
digital badges, competency taxonomies, and standards for transporting career
information between systems. That infrastructure matters. PIA did not begin
by asking how to build another credential wallet, taxonomy, or human-resources
data standard.

We began with a more human problem:

> **What can this person actually do, what evidence supports it, and why is so much of that capability invisible to the systems that are supposed to recognize it?**

That starting point remains the governing point of the project.

## We built toward an existing field without knowing it existed

PIA emerged from a practical failure of representation. A conventional record
could contain degrees, credentials, work history, job titles, and résumé
bullets and still fail to explain the capability evidenced by actual work. The
project therefore began reconstructing capability from the ground up while
preserving:

- work history, education, credentials, projects, and artifacts;
- informal learning, outcomes, and surrounding context;
- sources, provenance, confidence, and uncertainty; and
- relationships among evidence, interpretation, and later revision.

We needed to distinguish raw observation from interpretation, explain why a
capability claim existed, and let later evidence strengthen, weaken, or
supersede an earlier conclusion. We also needed outputs that could leave the
system and remain understandable to the person. That led toward graph-based
representation, evidence chains, capability inference, portable outputs, and a
translation layer connecting a richer internal model to institutional systems.

Only later did we look closely at the Open Skills and Learning and Employment
Record ecosystem. The convergence showed that many downstream representation
and interoperability problems already have serious standards work behind them.
PIA does not need to reinvent those structures. The convergence also clarified
the part of the problem PIA had actually been working on.

## Representation is not recognition

Existing infrastructure can represent claims such as:

> This person earned this credential.

> This achievement maps to these skills.

> This record came from this issuer and can be verified.

Those are important capabilities. But they begin after something has already
been made legible. PIA begins earlier:

> **What does the total body of evidence reasonably indicate that this person can do, including capability that no previous institution has formally named, credentialed, rewarded, or noticed?**

A person's strongest capability may not correspond neatly to a prior job title.
It may emerge only when different kinds of evidence are viewed together. A
conventional extractor may list tools and tasks while missing the higher-order
pattern:

> **This person repeatedly learns unfamiliar systems, identifies underlying structure, integrates information across domains, and converts ambiguous problems into usable systems.**

That is a capability-discovery problem, not merely a credential-transport
problem.

## The infrastructure should not become another layer between the person and opportunity

Capability-recognition infrastructure is often encountered through standards
bodies, schools, credential providers, workforce agencies, employers, HR
platforms, research organizations, and technical specifications. All can be
useful. But the person whose capability is represented can still remain several
layers away from the system.

> **Capability information can become increasingly sophisticated while the individual remains unable to understand, use, challenge, carry, or benefit from it.**

That is structurally similar to the failure PIA and OSI are trying to solve. A
capability can exist inside a person but fail to become opportunity because a
system does not recognize or deploy it. Information about capability can also
exist inside institutional systems but fail to become useful to the individual
because it is sequestered behind organizational or technical layers. In both
cases, something valuable exists but the surrounding system fails to convert it
into usable human opportunity.

## The formal architectural principle

The architecture should therefore be governed by this rule:

> **PIA should be maximally expressive internally, maximally interoperable externally, and maximally understandable and useful to the person whose capability it represents.**

This is an architectural principle, not merely a user-interface preference. A
system may use graphs, ontologies, standards, competency alignments, verifiable
credentials, AI-assisted inference, and institutional integrations. The
complexity should be absorbed by the infrastructure rather than placed on the
individual. A participant should not need to understand CTDL, CLR, RSD, Open
Badges, verifiable credentials, or HR interoperability in order to benefit
from them.

The participant-facing interaction should remain close to:

> Tell us what you have done.

> Show us what exists.

> Let us determine what the evidence supports.

> Here is what we see, why we see it, and what remains uncertain.

> Here is what you can take with you.

## The associated constraint

The principle requires a corresponding constraint:

> **Capability information should not become sequestered inside the institutions or technical systems intended to recognize it.**

Institutions may contribute evidence. Employers may validate work. Schools may
issue credentials. Reviewers may endorse claims. Standards may make records
interoperable. None of those actors should need to own the authoritative
definition of the person.

An employer should be able to say what work it observed, what outcomes occurred,
what the person's role was, and what it is willing to verify. That evidence can
remain valuable after the employment relationship ends, but the employer should
not have unilateral authority to turn its classification into a permanent
identity. The role title belongs to the history; the evidence belongs in the
record; the person should be able to carry both forward.

## Portability requires more governance, not less

Freeing capability information from institutional custody does not mean
weakening standards. A portable capability system should be able to show:

- the underlying evidence and who produced or observed it;
- when it occurred and under what conditions;
- what was inferred and how confident that inference is;
- whether other evidence supports or contradicts it;
- who independently reviewed or endorsed it; and
- whether later evidence changed the interpretation.

That is more rigorous than allowing a job title, manager judgment, résumé
bullet, or opaque score to stand in for the person. The goal is not to make
everyone their own unquestioned authority. It is to prevent any single
institution from becoming the unquestioned authority either.

## Existing standards are infrastructure, not the enemy

The Open Skills and LER ecosystem should be treated as infrastructure to build
upon. Existing work addresses semantic definitions of skills and competencies,
structured achievement records, evidence attachment, digital credentials,
verification, portable records, and machine-readable employment information.

PIA should use those structures where they fit. Its translation or “socket”
layer need not force employers, schools, or platforms to adopt the full internal
PIA ontology. It can translate appropriate portions of a richer capability
model into languages those systems already understand:

```text
Human lived evidence
        ↓
PIA capability discovery and interpretation
        ↓
Participant-understandable evidence and outputs
        ↓
Open Skills / LER translation
        ↓
Existing institutional systems
```

The standards layer carries the signal. PIA helps determine what signal is
worth carrying.

## What the related research shows

Several Burning Glass Institute reports illuminate different points in the same
system:

### Recognition

[*Credential Fluency: The Hiring Advantage in the Race for Skills*](https://skillsright.org/wp-content/uploads/2026/03/Credential-Fluency_The-Hiring-Advantage-in-the-Race-for-Skills_OneTen_BGI_Report.pdf)
shows why removing degree requirements alone does little if organizations do
not build the infrastructure needed to recognize, evaluate, and trust
alternative signals. The problem is not only whether a worker possesses a
credential; the organization must be able to interpret it and act on it.

### Mobility

[*Sidetracked: The Hidden Crisis in Mid-Career Mobility*](https://www.burningglassinstitute.org/research/sidetracked)
describes how career stagnation can become structurally embedded even among
experienced professionals, and how recovery may involve redirecting existing
human capital rather than starting over. The problem is not always a lack of
capability; it may be a failure to convert capability into a new trajectory.

### Organizational architecture

[*The Company You Keep: The Outsized Effect of Employer Practices on Pay, Promotion, and Retention*](https://www.burningglassinstitute.org/research/the-company-you-keep)
shows why workers with similar jobs and skills can experience different pay,
promotion, and retention depending on employer practices. Organizations differ
in their ability to convert human capability into development and mobility.

Taken together:

```text
Capability can be overlooked
        ↓
Signals can fail to be recognized
        ↓
Career structures can strand capability
        ↓
Organizations differ in their ability to convert capability into opportunity
```

## PIA and OSI are complementary

PIA asks:

> **What capability does the evidence indicate exists?**

The interoperability layer asks:

> **Can that capability be represented in forms other systems understand?**

OSI asks:

> **Can the receiving organization recognize, trust, deploy, and develop it?**

```text
PIA
What capability exists?
        ↓
Interoperability
Can it be communicated?
        ↓
OSI
Can the organization convert it into opportunity and contribution?
```

Better records alone do not guarantee better outcomes. A portable capability
record can still enter an organization that does not know what to do with it;
an organization may want to develop people but lack reliable information about
what capability is present. The architecture must work from both directions.

## Human-centered does not mean flattering

A system built for individuals must still be rigorous. PIA should preserve
supporting and contradictory evidence, provenance, uncertainty, confidence,
temporal context, limits of inference, external validation, and participant
contestability. The participant should understand why a claim exists. A reviewer
should be able to disagree. Later evidence should be able to change the
conclusion. That is what makes a record trustworthy enough to travel.

## The person is a primary beneficiary, not merely a data source

The individual should not exist merely to populate a better institutional
database. Capability infrastructure should help a real person:

- understand their own capability more accurately;
- identify evidence they did not realize mattered;
- recognize developmental patterns in their history;
- communicate capability that conventional signals miss;
- carry evidence across institutional boundaries;
- identify plausible next opportunities; and
- continue developing rather than becoming trapped inside an old classification.

The person represented by the system should be one of its direct beneficiaries.

## A practical design test

Every major feature should be tested against this question:

> **Does this make the person's capability more understandable, portable, actionable, or developable for the person themselves, or does it primarily add another institutional layer around them?**

Institutional utility is desirable. Institutional utility alone is insufficient.
This test applies to data models, interfaces, assessments, credentials,
AI inference, employer integrations, researcher access, analytics, governance,
and export formats.

## A statement of intent

We are not building a better institutional record *of* a person and calling
that empowerment. We are building infrastructure intended to return greater
understanding and agency **to the person**, while making that understanding
sufficiently rigorous and interoperable that institutions can act on it
responsibly.

The success test remains human:

> **Does better capability information change what a real person can understand, attempt, demonstrate, learn, contribute, or be entrusted to do?**

Capability infrastructure should not merely produce better records about
people. It should help people understand and direct their own development while
helping institutions recognize and use capability more responsibly.

> **Do not merely make capability machine-readable. Make it human-usable.**

---

## Sources

- Burning Glass Institute and OneTen. [*Credential Fluency: The Hiring Advantage in the Race for Skills*](https://skillsright.org/wp-content/uploads/2026/03/Credential-Fluency_The-Hiring-Advantage-in-the-Race-for-Skills_OneTen_BGI_Report.pdf) (2026).
- Burning Glass Institute and NYU School of Professional Studies. [*Sidetracked: The Hidden Crisis in Mid-Career Mobility*](https://www.burningglassinstitute.org/research/sidetracked) (2026).
- Burning Glass Institute and Tullman Family Office. [*The Company You Keep: The Outsized Effect of Employer Practices on Pay, Promotion, and Retention*](https://www.burningglassinstitute.org/research/the-company-you-keep) (2026).
- Open Skills Network. [Rich Skill Descriptor (RSD)](https://www.openskillsnetwork.org/rsd).
- Credential Engine. [Credential Transparency Description Language (CTDL)](https://credentialengine.org/credential-transparency/ctdl/).
- 1EdTech. [Comprehensive Learner Record 2.0](https://www.1edtech.org/standards/clr) and [Open Badges 3.0](https://www.1edtech.org/standards/open-badges).
- W3C. [Verifiable Credentials Data Model 2.0](https://www.w3.org/TR/vc-data-model/).
- HR Open Standards. [Trusted Career Profile](https://www.hropenstandards.org/news/official-release-of-the-trusted-career-profile-tcp) and LER work.
- PIA/OSI internal governance concepts: human-centered capability infrastructure, provenance, contestability, temporal authority, observation vs. interpretation, and participant portability.
