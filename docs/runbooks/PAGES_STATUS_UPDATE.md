# GitHub Pages Status Update Runbook

GitHub Pages is a public publication surface, not a separate source of truth.
The source of record is [`docs/PROJECT_STATUS.md`](../PROJECT_STATUS.md). This
runbook keeps the rendered Pages status current and prevents a stale status
page from giving readers or machines an outdated view of the project.

## When to run this

Run the status update whenever any of the following occurs:

- a project milestone is completed;
- a public article, evidence tour, or other Pages artifact is added, removed,
  or materially revised;
- a governance, authority, lifecycle, or authorization boundary changes;
- a machine-orientation or discoverability intervention changes the public
  navigation path; or
- the monthly maintenance review is due, even if no material change occurred.

The status update belongs in the same work round as the change that makes it
necessary. Do not defer it until after a public release has already been
announced.

## Update the source status

In `docs/PROJECT_STATUS.md`:

1. Update `last_reviewed` and the machine-readable `as_of` date.
2. Bump the document version when the present-state description changes.
3. Update `current_focus` and the **Current Public Status** paragraph.
4. Reconcile the operational-state table, current evidence flow, and explicit
   authorization boundaries with the latest validated work.
5. Keep the status bounded: distinguish demonstrated, working/proposed,
   exploratory, historical, and not-authorized material.
6. Keep the Pages-facing language plain enough for a first-time reader while
   retaining the exact authority and lifecycle distinctions used by the
   metadata contract.

If a public article or hub changed, also reconcile its article index and the
publication registry in the same commit. If a milestone changed, update the
history index and the applicable registry.

## Validate before pushing

From the repository root, run:

```powershell
python -m software.governance.validate_repository_governance --root .
powershell -ExecutionPolicy Bypass -File .\scripts\check_publication_encoding.ps1
git diff --check
```

The governance validator is the release gate. It checks metadata, registries,
links, ontology identifiers, tracked paths, and restricted participant traces.
Do not publish a status update if that gate fails.

## Verify the rendered Pages surface

After the commit is pushed and GitHub Pages has completed its deployment, check
both public views:

- [Pages landing page](https://dingus-mcguillacutty.github.io/OSI-PIA-clean/)
- [Rendered project status](https://dingus-mcguillacutty.github.io/OSI-PIA-clean/PROJECT_STATUS.html)

Confirm that:

- the visible review date matches the source status;
- the current focus and public-status boundary are present;
- newly published hubs or articles are reachable from the landing path; and
- no old article count, stale date, broken link, or unrendered metadata block
  remains visible.

If Pages is temporarily behind the source commit, record the deployment delay
as an environment observation and recheck after the workflow completes. Do not
silently edit the source again just to compensate for propagation time.

## Record the checkpoint

For a milestone or publication round, record the source commit, validation
result, Pages deployment state, and verification date in the associated
milestone or release note. This preserves the distinction between:

```text
source status updated
→ Pages deployment completed
→ rendered status verified
```

The rendered page communicates current project state; it does not create
authority, promote research, or authorize production participant processing.
