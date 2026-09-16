---
artifact_id: publication-article-temporal-authority-001
title: "Temporal Authority"
domain: shared
layer: publication
authority: supporting
status: active
version: "0.2"
owner: publication-stewardship
series: "Hiring and Capability Recognition"
series_part: 8
permalink: /publications/articles/2026-09-16_temporal-authority.html
---

# Temporal Authority

## The truth of a person's capability is bounded by time and context. Neither gives an organization the authority to turn a past state into a permanent ceiling.

## Publication Note

This article is part of the OSI-PIA public article series. It describes an
active research and development direction. It does not claim that OSI-PIA is a
finished hiring product, validated employment-screening system, legal
compliance tool, or production decision system.

## Article

A record can remain true about the past while becoming wrong as a description
of the present. That distinction sounds obvious until we look at how
institutions actually use information about people. A job title can follow
someone for years after their work has outgrown it. An old performance
evaluation can continue to shape assumptions after the conditions that
produced it have changed. A credential can remain historically valid while
becoming a weak indicator of current skill. A personality assessment can
capture a person at one point in time and then quietly harden into an identity
claim. A résumé can preserve an accurate history while still badly
underrepresenting current capability.

The problem is not simply stale data. The problem is **authority being carried
forward farther in time than the evidence supports**. That is the problem of
temporal authority.

## Historical truth is not current truth

Most information systems are built to preserve records. Fewer are designed to
reason carefully about the authority those records should retain as conditions
change. A project-status document may accurately state that a system is
unfinished. Six months later, the system may be running in production. The old
document has not become false. It remains a valid historical record. What has
changed is its authority to describe the present state. The same logic applies
to human capability. A person may once have required close supervision. They
may once have lacked a skill. They may once have been operating within a
narrow role. They may once have performed poorly under a particular set of
conditions.

Those observations may remain historically valid. They do not automatically
remain valid descriptions of the person now. This gives us three distinct
questions:

1. **Historical validity** — Was the claim reasonably supported when it was recorded?
2. **Temporal transferability** — Under what conditions may that claim legitimately be carried forward?
3. **Current validity** — Is there sufficient evidence to use that claim as a description of the present state?

Conventional records often collapse all three into one. If the record exists,
it is treated as if it still speaks with the same authority. That is a mistake.

## Evidence has a jurisdiction in time

A useful way to think about this is that evidence has a kind of temporal
jurisdiction. Some facts remain authoritative for a very long time. A degree
conferred twenty years ago remains a degree conferred twenty years ago. Other
claims decay much more quickly. A five-year-old evaluation of someone's
technical proficiency may no longer say much about what they can do today. A
statement about a team's morale may become obsolete within weeks. A project
status can change within hours. A timestamp is therefore necessary but
insufficient. Knowing when something was observed does not tell us:

- how rapidly the underlying state can change;
- whether newer evidence supersedes it;
- whether the claim concerns a stable trait, temporary condition, completed event, prediction, or interpretation;
- how much current authority should remain; or
- whether the evidence is appropriate for the decision being made now.

Temporal authority is not a property of the date alone. It is a property of the
relationship among **evidence, claim, context, change, and use**.

## Do not let synthesis erase chronology

This matters even more in AI-mediated systems. Modern AI systems are
exceptionally good at taking many pieces of information and turning them into
a smooth, coherent account. That is useful. It is also dangerous when
chronology disappears inside the synthesis. A system can ingest several
historically accurate observations, combine them into one elegant summary, and
accidentally produce a description that appears current even though the
underlying evidence comes from different states, different contexts, and
different periods of a person's life. The failure mode looks like this:

```text
Historically accurate observations
            ↓
Loss of chronology and context
            ↓
Coherent synthesis
            ↓
Apparent current description
            ↓
Decision or action
```

The answer is not to avoid synthesis. The answer is to preserve the temporal
structure beneath it.

```text
Observation
    ↓
Observed at time t
    ↓
State at time t
    ↓
Subsequent observations
    ↓
Change / continuity / contradiction
    ↓
Current confidence and authority
```

A responsible system should preserve not only what was known, but **when it
was known, what state it described, what has changed since, and how much
authority the old evidence still deserves**.

## A career history is not a capability ceiling

This becomes especially important in employment. Conventional labor systems
often treat occupational history as evidence of occupational destiny. If a
person has held the same kind of role for ten years, the system frequently
treats that history as evidence of what the person is qualified to continue
doing. But:

> **“This person held Role X for ten years”**

is evidence of employment history. It is not automatically evidence that:

> **“Role X represents this person's current maximum capability.”**

Those are different claims. Recent work on mid-career mobility makes the
distinction concrete. The [Burning Glass Institute and NYU School of
Professional Studies report *Sidetracked: The Hidden Crisis in Mid-Career
Mobility*](https://www.burningglassinstitute.org/research/sidetracked)
examined large-scale career histories and describes how prolonged career stall
can become visible before it hardens, including movement into adjacent roles
that reuse existing human capital. That matters because a stalled career can
produce a self-reinforcing record. A narrow role produces a narrow title. The
narrow title limits what employers infer. The limited inference constrains
opportunity.

The constrained opportunity produces less visible evidence of broader
capability. The record then appears to confirm the original assumption. The
history remains true. The inference becomes increasingly misleading. That is a
temporal-authority failure.

## Context matters too

Time is only half the problem. A capability observation is always made under
conditions. A person may perform differently depending on autonomy, trust,
information access, role clarity, supervision, tools, workload, team quality,
incentives, psychological safety, developmental opportunity, organizational
politics, and fit between role demands and actual capability. A past
observation may therefore be bounded by context as well as time. This does not
mean poor outcomes should be dismissed whenever the context was difficult. It
means the observation should be interpreted at the level the evidence
supports. “Performed poorly under these conditions” is a stronger statement
than “is a poor performer.”

“Required close supervision in this role at this point in time” is more
defensible than “requires close supervision.” “Had not yet demonstrated
capability X” is different from “is incapable of X.” These distinctions matter
because institutions routinely transform context-bound observations into
context-free identities. That is not rigor. It is overreach.

## Institutions may record history. They do not own the future.

Organizations need records. Managers need evaluations. Researchers need
longitudinal data. Employers need to make decisions under uncertainty. Temporal
authority is not an argument against institutional judgment. It is an argument
for disciplined judgment. Institutions should be able to say:

> We observed this.  
> We observed it under these conditions.  
> We observed it at this time.  
> This is how we interpreted it.  
> This is how confident we were.

What they should not be able to do without current evidence is quietly turn
that observation into:

> Therefore, this is what this person is.

Or:

> Therefore, this is what this person will remain capable of.

Historical evidence is not an institutional license to impose a permanent
ceiling.

## Why this matters for PIA

PIA is being built around an explicit separation between observation and
inference. That distinction becomes much more powerful when time is included.
A capability record should be able to preserve:

```text
Observation
    ↓
Source
    ↓
Artifact / evidence
    ↓
Context
    ↓
Time
    ↓
Inference
    ↓
Confidence
    ↓
Subsequent evidence
    ↓
Revised or sustained inference
```

The old inference need not be erased. It may remain an important part of the
history. But later evidence should be able to narrow, expand, contradict, or
supersede it. This is especially important for people whose conventional
biographies understate their development. Someone may have learned rapidly.
Their work may have expanded beyond their title. Their ability may have become
visible only after gaining new tools, autonomy, or opportunity. The architecture
should be able to represent that change instead of forcing the present person
into the shape of the oldest surviving record.

## Why this matters for OSI

Organizations change too. An employee once viewed as junior may now be
operating at a much higher level. A team once considered dysfunctional may have
changed leadership. A unit once dependent on external expertise may have
developed strong internal capability. A manager once highly effective may be
operating in a different environment with different results. A skill once
scarce may now be abundant. If OSI is meant to understand organizations as
dynamic systems, then it cannot treat historical states as permanent
properties. It must treat state transitions as first-class evidence. That
requires a basic discipline:

> **Preserve history without mistaking history for the present.**

## Governance consequence

Temporal authority should therefore become an explicit governance rule. Every
consequential capability claim should be able to answer:

- What is the underlying evidence?
- When was it observed?
- Under what conditions?
- What exactly was inferred?
- How stable is that inference expected to be?
- What subsequent evidence exists?
- Has the claim been reaffirmed, weakened, contradicted, or superseded?
- Is the claim still appropriate for the decision being made now?

This is more demanding than simply storing timestamps. It is also more fair.

## The governing principle

The principle can be stated simply:

> **Evidence should retain its history without inheriting unlimited authority over the future.**

And for capability systems specifically:

> **The truth of a person's capability is bounded by time and context. Neither gives an organization the authority to turn a past state into a permanent ceiling.**

A person is not a frozen record. An organization is not a frozen state. A
responsible architecture should know the difference.

---

## Sources

- Burning Glass Institute and NYU School of Professional Studies. [*Sidetracked: The Hidden Crisis in Mid-Career Mobility*](https://www.burningglassinstitute.org/research/sidetracked) (2026).
- PIA/OSI internal governance concepts: observation vs. interpretation, provenance, confidence, state transitions, contestability, and human-centered capability infrastructure.
