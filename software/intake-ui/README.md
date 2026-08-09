---
artifact_id: component-pia-credential-review-ui-001
domain: implementation
layer: component
authority: working
status: proposed
version: "0.7.0"
owner: pia-intake
lifecycle_state: formulation
---

# PIA Participant Review and Document Update

> **Development state: IN PROGRESS — SUBJECT TO CHANGE.**
> This is a working, proposed interface prototype at Formulation. It is not a
> production intake service, participant-data store, accepted review contract,
> or graph-write component.

This prototype demonstrates a low-burden participant checkpoint between
credential-definition work and capability mapping. It is designed for people
with many varied courses, trainings, licenses, or certifications and limited
time for a long intake sequence. It:

- summarizes which credentials are recognized, need a source, or need a quick
  participant answer;
- reduces the immediate review to three bounded choices: applied in work,
  preparation only, or correction needed;
- presents a short supported meaning and negative boundary before the choice;
- advances through a ready queue without making optional detail a prerequisite;
- preserves optional note, source-link, document-selection, skip, and return
  paths; and
- keeps participant context visibly separate from the reusable credential
  definition.

The interface follows a simple visual sequence:

```text
Check the short meaning -> Choose the closest fit -> Continue
```

The progress count measures review completion only. It is not a capability
score, participant ranking, or claim-strength measure.

Version `0.3.0` adds an optional report-to-document handoff. From an example
participant overview, a participant may:

- keep the completed report without requesting any document change;
- choose a LinkedIn profile, résumé, or chronological CV as a target;
- compare current wording with an evidence-bounded suggestion;
- edit, accept, or reject each proposed change independently;
- inspect the report basis for each suggestion; and
- copy or download a separate editable draft.

The handoff does not edit or publish the participant's source document. It does
not add the generated wording to the evidence graph, treat document acceptance
as new proof, or create claims beyond the accepted report. A future durable
implementation should preserve the target identity, source version, report
version, transformation method, per-suggestion decisions, evidence references,
and exported-draft identity in an explicit transformation manifest.

Version `0.4.0` distinguishes the short executive summary from the full
evidence report. The participant may:

- view the full report without changing its composition;
- add or remove the executive summary from the working full-report view;
- see whether the summary is currently included by participant choice;
- navigate the professional narrative, capability/evidence register, and
  interpretation limits behind the overview; and
- continue from the full report to the unchanged document-update options.

Including the executive summary changes report composition only. It does not
change evidence, confidence, graph state, or the accepted interpretation.

Version `0.5.0` adds visible privacy commitments, an optional technical
evidence companion, and participant-directed evidence updates. It:

- links the intake, overview, document editor, and full report to a plain
  language privacy foundation;
- distinguishes current prototype guarantees from safeguards required before
  production participant intake;
- states that prototype choices are session-only, browser-created downloads
  are not uploaded by the interface, participant PII is excluded from the
  tracked repository, and site delivery is encrypted in transit;
- avoids claiming encrypted retained storage until encryption-at-rest,
  access-control, retention, and deletion safeguards are implemented and
  validated;
- lets the participant preview, add, or remove a technical evidence companion;
- shows synthetic per-capability confidence, evidence counts, evidence roles,
  source-group coverage, and bounded conflicts without creating an overall
  participant score; and
- replaces passive `reviewable` language with direct `Update my evidence`
  paths from the report menu, capability register, technical companion, and
  evidence-boundary section.

Technical-companion inclusion is a report-composition choice. It does not
change the underlying evidence, confidence calculation, or graph state.

Version `0.6.0` establishes a participant-first entry sequence and makes the
credential review visually congruent with the report and approved sharing
image. The site now:

- begins with a privacy-first participant page at the site root;
- uses a changeable, session-only participant label instead of requiring a
  name or email;
- lets a participant select multiple initial professional, career,
  credential, learning, and supporting-evidence documents;
- displays selected file names and sizes, supports removal, and requires a
  clear prototype privacy acknowledgement before continuing with files;
- states that the working screen does not upload, analyze, or retain selected
  documents;
- provides a continue-without-documents path;
- moves the quick credential review workspace to `/credentials`; and
- reuses the accepted PIA report palette, typography, assurance language, and
  `og-v5.png` visual across both intake steps.

The current page-to-page transition is demonstrative. Because the prototype
does not upload or persist files, selected documents are not transferred to
the credential-review route. A durable implementation must stage them through
the governed Source Artifact, Intake Session, consent, retention, malware
inspection, and assurance contracts before extraction.

Version `0.7.0` consolidates the participant-reference and initial-document
surfaces into one intake card. It removes the separate static document-category
list and instead:

- accepts documents through file selection or drag and drop;
- presents one document-type selector for every added file;
- supports professional-profile, career-document, credential-or-learning, and
  supporting-evidence classifications;
- shows classification progress alongside selected count and file size;
- permits removal and re-selection without retaining the file; and
- requires every selected document to have a type, plus the prototype privacy
  acknowledgement, before continuing with the document set.

Document type is participant-supplied intake metadata. It organizes the source
for later processing but does not establish evidence meaning, capability,
quality, or acceptance.

The current version uses synthetic credential and participant identifiers.
Typed input, document decisions, generated drafts, and selected file names
remain in memory only and disappear on reload. No document is uploaded,
persisted, committed, published, or projected to a graph.

Durable participant input belongs in a later local-private intake phase using
the contracted Source Artifact, Review Event, and assurance boundaries.
