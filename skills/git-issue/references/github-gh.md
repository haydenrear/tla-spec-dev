# GitHub adapter — `gh` CLI

GitHub is the default tracker. Every issue operation goes through the `gh` CLI
(installed via `brew:gh` as a hard dependency of this skill). To target a
different tracker, replace only the commands here — the workflow in `SKILL.md`
is unchanged.

## Preconditions

```bash
gh auth status            # must be logged in
gh repo view --json nameWithOwner -q .nameWithOwner   # confirm the target repo
```

If `gh auth status` fails, the user runs `! gh auth login` in the session (the
`!` prefix runs it here so the device flow output is visible). Do not attempt to
store or generate tokens.

## Creating the issue

Write the rendered body (the template in `SKILL.md`) to a file, then create from
it so multi-line markdown and backticks survive intact:

```bash
gh issue create \
  --title "<concise imperative title>" \
  --body-file <path-to-rendered-body.md> \
  --label enhancement \
  --assignee @me
```

Capture the returned URL/number — later steps (spec ticket, PR) reference it.
To read it back:

```bash
gh issue view <number> --json number,url,title,body
```

## Scheduling an issue in an epic

Use the exact marker-delimited block in `references/epic-assignment.md`. For a
new issue, create the standard work order, capture the issue number/URL, record
that URL against its one planned spec ticket, then update the body with final
branch/worktree fields. For an existing issue, read its current body, preserve
everything outside the markers, and replace only the bounded assignment with
`gh issue edit --body-file`. A resume updates the existing block; it never
appends a duplicate.

## The References section is the discovery starting point

The `## References` block is the most load-bearing part of the body: it is the
implementer's entry into the codebase. Populate it from `references/discovery.md`
output. Prefer `path:line` anchors — they are clickable and unambiguous. Include
the specs (`*.tla`), test-graph nodes, and adapters the change touches, not just
product source.

## Labels for routing (optional but recommended)

- `spec-required` when the issue's Spec workflow section is REQUIRED, so spec
  work is visible in triage.
- `regression` / component labels to route the close-out test graphs.

Create missing labels with `gh label create <name>` before use.

## Linking the in-repo spec ticket

When close-out requires an in-repo spec ticket (opened by the implementer via
spec-double-compiler + tla-spec-dev — see `references/spec-workflow.md`), note in
the GitHub issue body that the spec ticket ID will be cross-linked back here, and
have the implementer comment the ticket path/URL on the issue:

```bash
gh issue comment <number> --body "Spec ticket: tickets/<id> (closed via tla-spec-dev)"
```

## Closing

The implementer closes the issue only after the close-out checklist passes
(`references/regression-close.md`), normally by the PR that merges the feature
branch (`Closes #<number>` in the PR body) or explicitly:

```bash
gh issue close <number> --comment "<summary of tests run + reports attached>"
```

This closing behavior is ordinary mode only. An epic ticket PR targets the epic
branch with `Refs #<number>` and stops for external review; the epic-owner agent
merges it into the epic branch at wave close, and the ticket agent neither merges
it nor closes the GitHub issue.
