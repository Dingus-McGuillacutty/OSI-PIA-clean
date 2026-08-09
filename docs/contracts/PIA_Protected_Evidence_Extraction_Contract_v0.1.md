---
artifact_id: contract-pia-protected-evidence-extraction-001
domain: pia
layer: contract
authority: working
status: proposed
version: "0.1.0"
owner: pia-intake
lifecycle_state: formulation
development_state: in_progress_subject_to_change
---

# PIA Protected Evidence Extraction Contract v0.1

## Purpose

This contract converts an authorized, malware-inspected source artifact into
faithful evidence candidates that a participant or accountable reviewer can
keep, correct, exclude, or dispute.

Extraction answers:

> What reviewable statements are present in this source, and exactly where did
> each statement come from?

It does not answer:

> What is the participant capable of, how confident should PIA be, or what
> professional identity does the evidence establish?

Those questions belong to later ontology-mapping, assurance, and review
layers.

## Preconditions

Extraction requires:

1. an authenticated `owner` or `reviewer`;
2. an open participant session with granted or limited consent;
3. unexpired finite retention;
4. explicit `evidence_extraction` processing scope;
5. a staged source artifact that passed the Phase 2B malware gate;
6. valid encrypted content and a matching SHA-256 checksum; and
7. a parser approved for the source extension.

Withdrawal, closure, deletion, retention expiry, missing content, checksum
failure, or absent scope blocks extraction.

## Parser boundary

| Type | Working behavior |
|---|---|
| TXT | Bounded text decoding and paragraph or list segmentation |
| CSV | Bounded rows and columns rendered as inert text; formulas are never evaluated |
| RTF | Text controls only; destinations for embedded objects, metadata, fields, and pictures are ignored |
| DOCX | Main Word document XML only; no macros, relationships, linked content, or embedded-object execution |
| PDF | Selectable text through `pypdf`; no JavaScript, attachments, external links, forms, or OCR execution |
| DOC | Retained and routed to manual conversion |
| ZIP | Retained and routed to approved manual preparation; general archives are not expanded |
| PNG, JPG/JPEG, HEIC, TIFF, and other images | Not currently accepted; no durable image-decoding and OCR boundary is implemented |

Password-protected PDFs, image-only PDFs, malformed documents, unsafe XML
declarations, excessive archive expansion, and safety-limit breaches fail
closed with a recorded `failed` status or enter `review_required`.

The intake interface must state this image limitation before file selection.
Until a governed image pipeline exists, a participant or operator may provide
a locally prepared TXT or DOCX transcription while retaining the image as an
external original. Unapproved cloud OCR must not receive participant
material.

Future image support must:

1. retain the original image as the authoritative source;
2. inspect the image and decoder boundary before processing;
3. record format, checksum, dimensions, and relevant metadata handling;
4. use an approved local or explicitly authorized OCR process;
5. store OCR output as a distinct encrypted derived artifact;
6. preserve page, region, or bounding-box provenance where available;
7. disclose OCR method and confidence without treating it as evidence
   confidence;
8. require review and correction before downstream eligibility; and
9. share the session's withdrawal, deletion, and retention lifecycle.

The implementation applies limits of:

- 500,000 extracted characters;
- 500 evidence candidates;
- 2,000 characters per candidate;
- 250 PDF pages;
- 2 MB per decompressed PDF stream;
- 5,000 CSV rows and 100 columns; and
- 25 MB uncompressed DOCX content with bounded member count and compression
  ratio.

## Extraction record

Each extraction retains:

```text
extraction_id
intake_session_id
participant_id
source_artifact_id
source_artifact_checksum
extraction_status
parser_id
parser_profile
source_extension
storage_reference
extracted_text_checksum
extracted_character_count
evidence_candidates
warnings
created_by
created_at
updated_at
capability_assertions_created
```

`capability_assertions_created` must be an empty list.

The complete extracted text is encrypted in a separate session-scoped file.
Candidate text and review history reside in the encrypted session record.
Neither form enters Git, logs, a public registry, a remote service, Neo4j, or
browser-local persistence.

## Evidence candidate

An extracted candidate projects the existing Evidence fields:

```text
evidence_id
source_id
participant_id
evidence_text
evidence_type
source_locator
source_section
extraction_method
fidelity_status
review_status
created_at
```

Working operational fields additionally preserve:

```text
extracted_evidence_text
classification_basis
included_in_downstream
record_version
updated_at
```

The allowed evidence types are `activity`, `responsibility`, `output`,
`achievement`, `event`, `condition`, `statement`, and `other`.

Candidates begin as:

```text
extraction_method = automated
fidelity_status = normalized
review_status = unreviewed
included_in_downstream = false
```

Lexical or source-section classification is only a neutral evidence-type
proposal. It is not a capability, trait, proficiency, assessment, score, or
recommendation.

## Review

The local review actions are:

| Action | Current evidence status | Downstream eligibility |
|---|---|---:|
| Keep | `reviewed` | Yes |
| Correct wording | `reviewed` | Yes |
| Exclude | `superseded` | No |
| Dispute | `disputed` | No |

Every action appends an encrypted review event. A correction retains the
original extracted wording and records a new current version. Review does not
erase the extraction, manufacture independent corroboration, or create a
capability assertion.

Only candidates with `included_in_downstream=true` may enter a later
application-linking or capability-mapping proposal.

## Idempotency and provenance

An extraction is identified by source artifact, source checksum, and parser
identifier. Repeating the same extraction returns the existing encrypted
record. A source-content or parser-version change creates a new extraction
identity.

Every candidate retains the original `source_artifact_id` and a paragraph,
page, or row locator. The source remains authoritative; extracted text is a
derived, reviewable representation.

## Lifecycle

Extracted text, candidates, and review events share the participant session's
consent, withdrawal, deletion, and retention lifecycle. Session-key erasure
and directory deletion remove the extraction data with the source artifacts.

## Machine-readable projection

The requirements are mirrored in the
[machine-readable contract](../../data/contracts/pia_protected_evidence_extraction_contract_v0.1.json).

## Status

This contract is `working/proposed`, in progress, and subject to change. It
does not authorize remote model processing, OCR, automatic credential
discovery, capability mapping, report generation, graph projection, or
production operation.
