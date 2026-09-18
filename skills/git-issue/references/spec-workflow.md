# Deciding and instructing the spec workflow

Some issues change **state-machine behavior**; those must carry a spec workflow
so the TLA+ specs, generated Python doubles, test-graph cases, and adapter
conformance tests move together. This is driven by the **spec-double-compiler**
skill (installed from `github:haydenrear/tla-spec-dev`), which provides the
`tla-spec-dev` CLI. This reference is about what the *issue* must say — the
mechanics live in that skill.

## Epic assignment override

An epic owner scaffolds the shared workflow exactly once on the epic branch and
plans all stable ticket IDs before dispatch. An epic issue therefore always
marks the spec workflow **REQUIRED**, maps to exactly one existing plan entry,
and embeds that ID in `ticket.spec_id`; the ticket agent runs:

```bash
tla-spec-dev --spec-root specs open ticket <stable-ticket-id>
```

It must not scaffold another workflow, create an ad hoc ticket, edit sibling
plan statuses, or run workflow-wide close/promotion. It updates the assigned
ticket's TLA+ model, spec-unit adapters, generated cases, Test Graph adapters
and graphs, and then closes only that ticket with the evidence declared in the
assignment. See `references/epic-assignment.md`.

## Decide: REQUIRED or NOT

The default is **NOT REQUIRED**. A spec pass is not cheap: it opens a ticket
workspace, edits a model, runs TLC and closes with evidence, and measured
across three eval rounds it consumed a large share of a ticket's tokens while
catching nothing the regression graphs did not. Charge it only where it pays.

Mark the Spec workflow section **REQUIRED** only when discovery can name, in
the issue body, the concrete model element that changes:

- a specific `Internal.tla` action, state variable, or invariant the change
  adds, removes, or alters, or
- a specific externally observable behavior in `External.tla` (when the
  project has the optional External view), or
- a generated spec double or spec-unit adapter the change breaks.

If you cannot write that line, mark **NOT REQUIRED** and say why in one line
(docs, refactor with identical behavior, build or tooling, a change with no
named model element). The implementer can challenge it. An epic assignment is
the one exception: it is always REQUIRED and names its ticket, because the
epic owner already planned the model change.

When REQUIRED, scope it: the implementer edits the ticket `desired/` model for
the named element, runs TLC once, and closes. The issue must not ask for the
optional layer (External view, adapters, providers, Test Graph bindings) unless
the repository already has it and the change touches it.

## What the issue must specify when REQUIRED

Fill the template's Spec workflow block with concrete, discovered edits:

- **Internal.tla** — the vars/actions/invariants to add or change.
- **External.tla** — the observable interface/behavior to add or change.
- **Test graph** — the spec-graph nodes/cases to add or update so the new
  behavior is exercised (see `references/regression-close.md` and the
  test-graph skill).
- **Unit-test adapters** — the adapter conformance tests that must be added or
  updated so the real implementation matches the generated double.

## The instruction to embed

> On feature-branch creation, open the spec workflow with **spec-double-compiler
> + tla-spec-dev**: edit `Internal.tla`/`External.tla` as above, regenerate the
> spec doubles, add/update the test-graph spec cases and adapter conformance
> tests, and open the in-repo spec ticket that this issue closes out.

The spec ticket opened here is what the close-out step attaches reports to and
closes via `tla-spec-dev` — see `references/regression-close.md`. Cross-link the
ticket back to the GitHub issue (`references/github-gh.md`).

That instruction is for an ordinary issue. In epic mode, replace "open the spec
workflow" with "open the assigned ticket in the existing shared workflow" and
retain the assignment's one-ticket-only boundary.
