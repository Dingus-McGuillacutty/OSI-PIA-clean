# Development Worktree Checkpoint

Use this checkpoint at the beginning and end of every meaningful build round.
It prevents valid work from remaining invisible in an uncommitted worktree or
being omitted from a clean-release snapshot.

## Before starting a round

From the repository root:

```powershell
git status --short
git log -1 --oneline
```

If the worktree is already dirty, identify and record those files before
starting new work. Do not assume they belong to the current task.

## After implementation and tests

Run the focused tests, then:

```powershell
git diff --check
git status --short
python -m software.governance.validate_repository_governance
```

The governance check must pass, and every remaining modified or untracked file
must be intentionally classified as one of:

- ready to commit;
- intentionally carried forward and named in the next-step note; or
- unrelated user work that must be preserved and left untouched.

## Commit boundary

Every completed milestone should end with a focused commit. Immediately after
committing, verify:

```powershell
git status --short
git log -1 --oneline
```

The expected status output is empty. If it is not empty, stop and resolve the
remaining files before beginning the next milestone or creating a clean
release.

## Clean-release boundary

Before publishing a clean release, confirm the source worktree is clean and
that the intended milestone commit is `HEAD`. A clean release must be rebuilt
after any later commit; updating the desktop clone cannot retrieve changes that
were never included in the published snapshot.

## Conversation handoff

When switching between ChatGPT/Work and Codex, include the latest commit ID,
worktree state, tests run, and the next uncommitted scope. This keeps planning
and implementation on the same checkpoint.
