---
artifact_id: publication-article-false-negative-stack-001
title: "The False Negative Stack"
domain: shared
layer: publication
authority: supporting
status: active
version: "0.1"
owner: publication-stewardship
series: "Machine Participation and Human Systems"
series_part: 1
permalink: /publications/articles/2026-09-10_false-negative-stack.html
---

# The False Negative Stack
## When Reasonable Gates Make Real Capability Disappear

In September 2026, I asked Claude Sonnet 5 to inspect a public GitHub repository I maintain: **OSI-PIA-clean**, the development repository for Organizational Systems Intelligence and Professional Identity Architecture.

Repository:

`https://github.com/Dingus-McGuillacutty/OSI-PIA-clean`

The repository was public. I supplied the exact URL. I could open it normally in a browser.

Claude could not read it.

In that test environment, Claude reported that its browsing tools could not fetch the repository because the source had not first appeared through the search pathway available to it. I then supplied the GitHub Pages site for the same project. Claude reported essentially the same problem: without the source first appearing in search, its fetch tool would not proceed.

The repository had not failed a substantive evaluation.

Its contents had never entered the model's context.

**It had failed the recognition pathway.**

That distinction should sound familiar to anyone who has spent time around modern hiring systems.

> **Testing note:** These observations describe specific model-and-tool environments on the dates tested. They do not establish permanent capabilities or limitations of the underlying language models or their vendors.

## The gate may be working exactly as designed

There are good reasons to put defensive boundaries around AI systems that access external sources.

An autonomous or semi-autonomous system should not necessarily be allowed to fetch any location a user provides. Arbitrary external content can contain malicious instructions, hostile redirects, poisoned information, attempts at data exfiltration, or material that creates legal, security, or economic risks.

A cautious system may therefore require several conditions before external information enters its trust domain.

Conceptually, the path may look something like this:

```text
public to humans
→ machine-reachable
→ source-admissible
→ machine-readable
→ machine-understood
```

Each gate may be individually reasonable.

But the experiment exposed the other side of that architecture.

A legitimate resource that cannot satisfy one of the admission mechanisms can disappear before the system ever evaluates what it contains.

The defensive system avoids one class of false positive while creating a false negative.

That does not mean the defense is wrong.

It means **the false-negative cost exists whether or not the system measures it**.

## We already do this to people

Modern hiring systems operate through a similar stack of recognition boundaries.

A person may possess the capability an organization needs. They may have years of evidence showing that they can do the work. They may have solved comparable problems repeatedly.

But that evidence still has to travel through a series of gates.

It must survive résumé conventions.

It must be parsed successfully.

It must use language a screening system recognizes.

It may need particular credentials.

It may need the right title.

It may need to rank highly enough in an automated screen.

It must attract the attention of a recruiter operating under time pressure.

It must make sense to a hiring manager working from familiar categories.

It must fit an interview process designed around assumptions about what a qualified candidate normally looks like.

Any individual gate may have a defensible purpose.

Together they create what we might call a **false negative stack**.

By the end of the process, the organization may confidently report:

> We could not find a qualified candidate.

But the system may have established something much narrower:

> No candidate whose representation successfully traversed our recognition system reached the final decision point.

Those statements are not equivalent.

## The missing evidence does not announce itself

False positives are often visible.

Something unwanted gets through the gate. A bad hire occurs. A malicious source is admitted. A fraud control fails. A security incident happens.

The failure generates an event.

False negatives are harder.

The highly capable applicant never appears in the final pool.

The internal employee who could solve the problem is never considered.

The unusual but relevant experience is never recognized.

The useful document never enters the machine's context.

The employee with transferable expertise never becomes visible to the team looking for that expertise.

Nothing obviously breaks.

The missing capability simply fails to become part of the recorded system state.

That makes false-negative systems unusually difficult to correct.

The organization receives evidence about what passed its gates.

It receives much less information about what the gates prevented it from seeing.

Over time, the system can therefore become increasingly confident in a recognition process whose largest errors are structurally hidden from it.

## The same pattern appeared across AI systems

The Claude test was not the only access failure.

In an earlier blind test, **Kimi K3** could not reach the same public repository and abstained from describing the project.

In a later test, **Gemini Flash-Lite** also failed to access the repository. It disclosed the failure, but then partially filled the information gap by incorrectly guessing that "OSI" referred to Open Systems Interconnection and that the project might be a networking or security toolkit.

Those are meaningfully different responses to the same broad condition.

Kimi preserved uncertainty.

Gemini preserved part of the uncertainty but also introduced speculative completion.

Claude Sonnet 5, in the tested environment, refused to infer project contents after it could not establish a source path.

This is not a ranking of the models.

It is an example of how different computational participants, operating with different model and tool configurations, can behave differently when a legitimate source fails to cross an admission boundary.

## Security has already learned part of this lesson

Good security architecture does not normally treat every unknown object as identical.

There is a difference between malicious, untrusted, unverified, unknown, partially verified, constrained, and trusted.

Those distinctions matter because responsible systems need alternatives to both unrestricted admission and permanent rejection.

They use sandboxing.

They request additional verification.

They escalate unusual cases.

They permit limited access.

They retain uncertainty.

They involve human review.

The goal is not to eliminate gates.

It is to make the gates sufficiently intelligent that they can distinguish **dangerous** from merely **unfamiliar**.

Human capability systems need the same maturity.

An applicant who does not satisfy the preferred recognition path should not automatically become epistemically equivalent to an applicant who has been shown to lack the required capability.

Those are different states.

One means:

> We evaluated the evidence and found it insufficient.

The other may mean:

> Our system did not successfully interpret the evidence.

A system designed around human capability should preserve that distinction.

## When reasonable gates interact

The deeper organizational problem appears when individually reasonable gates interact.

A credential requirement may be defensible.

A résumé parser may be efficient.

An automated ranking system may reduce workload.

A recruiter may need shortcuts.

A manager may prefer familiar backgrounds.

An interview structure may need consistency.

None of those mechanisms alone constitutes the hiring ecosystem.

But stack them together and a capable person may have to survive five, six, or seven independent recognition filters before anyone meaningfully examines what they can actually do.

This is not necessarily the result of malicious intent or incompetent managers.

It can be an emergent property of the system.

The same thing occurs inside organizations.

Capability may exist while remaining blocked by reporting structures, departmental boundaries, access controls, internal job classifications, manager assumptions, information silos, promotion criteria, or metrics that recognize activity without recognizing underlying value.

The organization can then experience a capability shortage while simultaneously employing people who possess the missing capability.

That is not merely a talent problem.

It is a visibility problem created by the architecture of the system.

## The design question is not whether to have gates

Every system has gates.

Security systems need them.

AI systems need them.

Hiring systems need them.

Organizations need ways to establish trust, manage risk, and decide where to allocate limited attention.

The more useful question is:

> **What happens to legitimate people, information, and capability that cannot traverse the preferred trust path?**

A mature recognition system should account for false negatives as deliberately as it accounts for false positives.

It should preserve uncertainty rather than converting lack of recognition into certainty about lack of value.

It should provide alternate paths for verification.

And it should be capable of asking whether its own defensive architecture is hiding the very capability it was built to find.

The AI experiment was small.

But the pattern was not.

The public repository was real.

The location was correct.

The content was available.

The recognition stack simply could not see it.

We should be very careful about building human systems that make the same mistake.
