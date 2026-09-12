# OSI–PIA Artifact Metadata Contract v0.1

**Status:** Working contract  
**Purpose:** Keep artifact metadata machine-readable, registry-backed, and
consistent across research, evidence, architecture, software, and publication
records.

## Contract principle

Metadata is a control surface, not free-form decoration. A new value must be
introduced through a reviewed contract change before it is used in an artifact.
Until then, authors must use the controlled vocabularies defined in the
machine-readable contract:

[`data/contracts/osi_pia_artifact_metadata_contract_v0.1.json`](../../data/contracts/osi_pia_artifact_metadata_contract_v0.1.json)

The repository governance validator enforces these values on every assurance
run. A metadata failure blocks publication until it is corrected or formally
reviewed.

## Required front matter

Every governed Markdown artifact with front matter MUST provide:

```yaml
artifact_id: unique-lowercase-id
domain: shared | osi | pia | implementation | test
layer: governed-layer
authority: canonical | supporting | working | historical
status: active | proposed | review-required | deprecated | superseded | retired
version: version-string
owner: stewardship-role
```

`artifact_id` is stable and unique across the repository. It is not changed
when a file is renamed or moved.

## Status and lifecycle are different

`status` describes the artifact's current workflow disposition. It is limited
to the values in the required front matter above.

`lifecycle_state` describes where the knowledge is in the developmental model:

```yaml
lifecycle_state: observation | exploration | formulation | congruence |
                  validation | promotion | stewardship
```

Do not create status values such as `exploratory` or `observed`. Express those
ideas with `status: proposed` or `status: active` plus the appropriate
`lifecycle_state`.

Optional review metadata is also controlled:

```yaml
review_cycle: annual | semiannual | quarterly | milestone | event-driven
last_reviewed: YYYY-MM-DD
```

When `review_cycle` is present, `last_reviewed` is required.

## Registry coupling

Every governed artifact MUST have one row in its primary registry. The row's
artifact ID, authority, status, owner, version, and canonical location must
agree with the artifact. Add or update the registry row in the same commit as
the artifact change.

Registration records inventory and authority; it does not promote working or
exploratory material. Promotion remains a governed decision.

## Introducing a new term

When an author needs a value not in the contract:

1. leave the artifact in a valid existing state;
2. record the proposed term and its meaning in the appropriate research or ADR
   record;
3. update the contract and validator through review; and
4. update templates and registries in the same governed change.

The validator must reject the new value until step 3 is complete. This keeps
the repository from silently accumulating local vocabulary that machines or
humans might mistake for accepted architecture.

## Authoring checklist

Before committing a governed artifact, confirm:

- front matter uses only contract values;
- `status` and `lifecycle_state` have not been conflated;
- the artifact ID is unique;
- the primary registry row exists and matches;
- links resolve to the canonical location; and
- the publication encoding and governance checks pass.

## Versioning

This contract uses semantic versioning. A new controlled value, required field,
or validation rule requires at least a minor version change and a corresponding
validator/template update.
