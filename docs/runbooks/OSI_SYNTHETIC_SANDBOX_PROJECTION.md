# OSI Synthetic Sandbox Projection Runbook

## Boundary

Use this runbook only with the embedded synthetic record. Do not modify it to
carry organizational material. `OSI-Sandbox` must be a separate local Neo4j
database; do not use `osi-reference`.

## One-time setup

Create and start an empty local Neo4j database named `OSI-Sandbox` in Neo4j
Desktop. The preflight does not create databases and the import will refuse
any other database name.

## Controlled test

From the repository root, first prove the deliberately invalid package is
blocked before a password prompt or graph connection:

```powershell
python -m software.importer.osi_synthetic_sandbox_import --exercise-invalid-package
```

Then perform the deliberate synthetic import:

```powershell
python -m software.importer.osi_synthetic_sandbox_import `
  --apply-synthetic `
  --windowed-password
```

Copy the returned `OSI-SANDBOX-RUN-...` identifier. Validate it read-only:

```powershell
python -m software.importer.validate_osi_synthetic_sandbox_import `
  --run-id 'OSI-SANDBOX-RUN-PASTE-THE-RETURNED-ID' `
  --windowed-password
```

Run the deliberate import and the read-only validation one more time. A
successful second validation must still report every global cardinality as
`1` and `idempotent_structure: True`.

The expanded package reports three relationships and three paths. Its
read-only validator also requires one completed `OSIImportRun` audit record.

## Rollback test

To remove only the observation relationships written by a specific synthetic
run, use its full run ID:

```powershell
python -m software.importer.osi_synthetic_sandbox_import `
  --rollback-run-id 'OSI-SANDBOX-RUN-PASTE-FULL-ID-HERE' `
  --windowed-password
```

An unknown, malformed, or superseded run ID must return a controlled exception
without broad deletion. Rollback is limited to the exact tagged observation
relationships; it is not a production retention or deletion mechanism.

## Expected interpretation

Success demonstrates a guarded, repeatable graph mechanics path for three
embedded synthetic observations. It does not validate OSI analytics, a real
organization, organizational assessment, or any diagnostic conclusion.
