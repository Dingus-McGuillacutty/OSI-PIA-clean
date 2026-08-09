---
artifact_id: contract-pia-credential-resolution-linkage-001
domain: pia
layer: contract
authority: working
status: proposed
version: "0.1.0"
owner: pia-intake
lifecycle_state: formulation
development_state: in_progress_subject_to_change
---

# PIA Credential Resolution Linkage Contract v0.1

## Purpose

This contract links protected participant intake to reusable public credential
definitions without exporting the participant relationship.

The linkage answers:

> What public definition, review task, registry candidate, or narrowly scoped
> clarification is appropriate for this credential descriptor?

It does not answer:

> Did the participant complete, retain, apply, or perform this credential?

## Storage separation

The protected session retains:

- the participant-to-credential relationship;
- the entered public descriptor;
- the local lookup result;
- any external public candidates associated with this intake;
- clarification responses;
- timestamps and the local audit relationship.

These records are encrypted with the participant session and share its
withdrawal, deletion, and retention lifecycle.

The public catalog and external connector receive no participant, session,
certificate-number, completion, document, note, employment, application, or
performance field.

## Minimization gate

The bridge constructs a new seven-field request conforming to the
[Credential Lookup Request Contract](PIA_Credential_Lookup_Request_Contract_v0.1.md).

It must not serialize a participant record and remove selected fields. This
rule prevents new private fields from crossing the boundary merely because a
deny list was not updated.

## Resolution order

1. Confirm active authorization, finite retention, and
   `credential_definition` processing scope.
2. Construct and validate the participant-free request.
3. Check the governed PIA credential catalog.
4. Reuse an accepted definition or route an existing pending definition to
   Phase 3A.
5. Ask a participant only for a missing issuer, exact title, or version
   distinction.
6. For a catalog miss, optionally use an approved server-side public registry
   connector.
7. Treat every external result as a candidate requiring Phase 3A review.
8. Store the private relationship only in the encrypted participant session.

## External connector controls

The current connector supports the Credential Engine Registry Search API.
Operational use requires:

- an approved Credential Engine account and Search API key;
- explicit server startup authorization;
- an allowlisted production or sandbox HTTPS endpoint;
- a server-side environment variable for the API key;
- bounded query results and response size;
- primary-source registry-result filtering;
- source identity, timestamps, publishing metadata, and fingerprints;
- fail-closed handling for authentication, availability, rate, format, or
  policy failures; and
- independent Phase 3A review before catalog acceptance.

The browser never receives the API key.

## Clarification

Clarification is allowed only when the local resolver identifies an issuer,
exact-title, or version distinction that the participant may know. The
response:

- is optional and bounded;
- remains private and encrypted;
- is recorded in clarification history;
- reruns the minimization gate;
- does not become issuer verification; and
- creates no capability, completion, current-standing, application, or
  performance claim.

## Withdrawal and deletion

Withdrawal immediately blocks new resolution and clarification. Session
deletion erases the encrypted credential relationship and its private
clarifications with the rest of the participant session.

Reusable public definitions already accepted through independent review are
not participant data and are not deleted with a participant session.

## Machine-readable projection

The field, storage, connector, clarification, and state requirements are
mirrored in the
[machine-readable contract](../../data/contracts/pia_credential_resolution_linkage_contract_v0.1.json).

## Status

This contract is `working/proposed`, in progress, and subject to change. It
does not authorize automated document extraction, autonomous definition
acceptance, capability mapping, report generation, or graph projection.
