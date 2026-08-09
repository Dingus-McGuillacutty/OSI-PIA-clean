---
artifact_id: connector-002
domain: pia
layer: connector
authority: working
status: proposed
version: "0.1.0"
owner: pia-connectors
lifecycle_state: formulation
development_state: in_progress_subject_to_change
---

# Connector 002 — Credential Engine Registry

Connector 002 performs bounded, server-side searches of the Credential Engine
Registry for credentials absent from the accepted PIA definition library.

It conforms to the [Connector Standard](../Connector_Standard.md) and the
[Credential Resolution Linkage Contract](../../docs/contracts/PIA_Credential_Resolution_Linkage_Contract_v0.1.md).

## Boundary

The connector accepts only the minimized public credential descriptor:

- title;
- issuer hint;
- version hint;
- credential type;
- jurisdiction;
- governed source scope; and
- governed lookup purpose.

It never accepts participant identity, session identity, certificate numbers,
completion evidence, participant documents, notes, application evidence, or
performance evidence.

Results are candidates for independent Phase 3A review. A registry match does
not establish credential completion, current standing, proficiency,
application, performance, or professional identity.

## Operation

The connector uses the official Credential Engine CTDL Search API through the
protected intake server. The API key remains in a server-side environment
variable and is never returned to the browser, logs, result records, or Git.

External lookup is disabled unless the protected server is started with
`--enable-external-credential-lookup`.

Official interface references:

- [Credential Registry Search API Handbook](https://credreg.net/registry/searchapi)
- [Consuming Registry Data guidance](https://guidance.credentialengine.org/consuming-registry-data/)

## Canonical assets

- `config/connector_manifest.yaml` — governed identity and privacy boundary;
- `config/field_map.yaml` — minimized request and normalized candidate map;
- `docs/data_contract.md` — connector-specific obligations;
- `src/credential_engine_search.py` — canonical implementation reference; and
- `templates/README.md` — explains why no participant template is provided.
