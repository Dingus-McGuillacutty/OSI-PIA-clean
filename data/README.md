# Data Boundary

## Repository contents

This directory contains versioned contracts, non-personal templates, and
explicitly synthetic contract fixtures. It does not contain participant
datasets.

The working Phase 1 intake materials are:

- the
  [machine-readable record contract](contracts/pia_intake_phase1_contract_v0.1.json);
- [empty contract templates](templates/pia-intake-v0.1/); and
- the
  [participant-free synthetic package](fixtures/pia-intake-phase1-synthetic/).

They remain `working/proposed`, in progress, and subject to change.

The participant-free Phase 3 credential-definition materials are:

- the
  [machine-readable catalog contract](contracts/pia_credential_definition_catalog_contract_v0.2.json);
- the
  [public reference catalog](reference/pia-credential-library-v0.2/); and
- the
  [human-readable catalog contract](../docs/contracts/PIA_Credential_Definition_Catalog_Contract_v0.2.md).

The Phase 3B credential-resolution linkage materials are:

- the
  [machine-readable minimized lookup contract](contracts/pia_credential_lookup_request_contract_v0.1.json);
  and
- the
  [human-readable lookup contract](../docs/contracts/PIA_Credential_Lookup_Request_Contract_v0.1.md);
- the
  [machine-readable linkage contract](contracts/pia_credential_resolution_linkage_contract_v0.1.json);
  and
- the
  [human-readable linkage contract](../docs/contracts/PIA_Credential_Resolution_Linkage_Contract_v0.1.md).

The public catalog may contain bounded summaries and fingerprints of lawful
public issuer sources. It must not contain participant completion,
application, performance, identity, contact, or private-source data.

## Participant datasets

Participant source, normalized, derived, and graph-import datasets remain
outside version control. When testing or importing participant material:

1. keep the dataset in a private local location;
2. pass that location explicitly to the relevant validator, importer, or
   connector;
3. preserve consent, provenance, access, retention, and correction controls;
4. remove temporary working copies when the bounded task is complete.

The compatibility path `data/PIA-participants/` is ignored so existing local
workflows can use it without making its contents eligible for commit.

The Phase 2A localhost intake remains synthetic-only. The working Phase 2B
participant-intake candidate uses a separately initialized encrypted store
outside the repository. Its controls and remaining operational approval gate
are defined in the
[Phase 2B Protection Profile](../architecture/pia-intake/PIA_Phase_2B_Protection_Profile.md).
Do not place its store or recovery bundle under `data/`, another repository
path, or the same storage-failure boundary.

Automated tests should construct case-specific mutations in temporary
directories. Any durable fixture under `data/fixtures/` or `tests/fixtures/`
must be clearly marked as synthetic and must contain no participant-derived
or personally identifying material.

The current-tree boundary does not erase prior Git objects. Historical
exposure is governed separately by MIG-010 in the
[Repository Migration Plan](../governance/Repository_Migration_Plan.md) and
the [Clean Release Standard](../governance/CLEAN_RELEASE_STANDARD.md).
