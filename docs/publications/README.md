# OSI Publication Framework

This directory contains the canonical Markdown sources for Organizational Systems Intelligence (OSI) and Professional Identity Architecture (PIA) publications.

## Structure

```text
docs/publications/
├── README.md
├── standards/
├── templates/
├── style/
├── examples/
│   ├── Good/
│   └── AntiPatterns/
├── PR/
├── TR/
├── OR/
├── VR/
├── MP/
├── WP/
└── GD/
```

## Directory Purposes

- `standards/` — publication, ethics, neutrality, and governance standards.
- `templates/` — reusable source templates for publication families.
- `style/` — terminology, visual identity, formatting, and editorial guidance.
- `examples/Good/` — approved examples demonstrating correct application.
- `examples/AntiPatterns/` — annotated examples demonstrating methodological and ethical errors.
- `PR/` — Participant Reviews.
- `TR/` — Technical Reports.
- `OR/` — Organizational Reports.
- `VR/` — Validation Reports.
- `MP/` — Methodology Papers.
- `WP/` — Working Papers.
- `GD/` — Governance Documents.

## Canonical Format

Markdown is the canonical repository source. RTF, DOCX, PDF, HTML, and other presentation formats are generated or distribution artifacts unless specifically designated otherwise.

## PIA output models

- [PIA Professional Identity and Resume Output Model](standards/PIA_PROFESSIONAL_IDENTITY_OUTPUT_MODEL.md)
  records the working capability-centered resume/professional-identity format,
  its separation from participant review and methodology outputs, and a fully
  synthetic redacted example.

## Required Analytical Discipline

Interpretive publications should preserve the sequence:

> Evidence → Observation → Interpretation → Confidence

All publications are governed by Narrative Neutrality, provenance preservation, participant authority, and the ethical commitments of OSI.

## Evidence visualization release

The [Live Sandbox Graph Tour](../evidence/visualizations/LIVE_SANDBOX_GRAPH_TOUR.md)
is a reusable synthetic publication artifact. It pairs conceptual diagrams
with bounded implementation views from the validated PIA-Sandbox and
OSI-Sandbox projections. Its editable Mermaid source is retained beside the
rendered documentation, and its participant-safe status is part of the
publication assurance boundary.
