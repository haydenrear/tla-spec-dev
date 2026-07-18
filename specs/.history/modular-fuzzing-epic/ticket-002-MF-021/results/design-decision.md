# MF-021 — design decision: why the seed manifest, not a guard

## The defect is the asymmetry, and the asymmetry is *deliberate*

`open ticket` seeds the ticket workspace from project `specs/current` through a
filter (`scripts/new_ticket_workflow.py`):

```python
skip_project_tests = {PROJECT_WORKFLOW_TEST}   # "tests/test_current_ticket_workflow.py"
copy_workflow_tree(source_current, current_dir, skip_paths=skip_project_tests)
copy_workflow_tree(source_current, desired_dir, skip_paths=skip_project_tests)
```

`close ticket` then promoted that filtered tree back over the unfiltered one:

```python
replace_tree(active_dir / "desired", specs_dir / "current")   # rmtree, then copy
```

A filtered read paired with an unfiltered write. Every promotion deleted
`tests/test_current_ticket_workflow.py` by construction — not occasionally, but
always. MF-012 and MF-020 were not bad luck; they were the design executing
correctly.

## Two candidate fixes, and why the obvious one is wrong

**Rejected — repair the seeding.** Stop excluding `PROJECT_WORKFLOW_TEST` so
`desired/` carries it and promotion writes it back. Rejected on two grounds:

1. *It corrupts the workspace to protect the project.* That test asserts about
   project `specs/current` itself (`SPEC_ROOT/current/spec_manifest.yaml`,
   `SPEC_ROOT/desired_program_model/ticket_plan.yaml`). Copied into a ticket
   tree it either fails or asserts about the wrong root, and it would then run
   in every ticket's spec-unit gate. The exclusion is *correct*; it was the
   promotion side that never learned about it.
2. *It does not subsume the deletion problem — it only closes one instance.*
   MF-020 also lost `refinement-probe/`, which was never excluded: it was
   created in `specs/current` **after** the ticket was opened. No amount of
   seed-filter repair reaches a path that did not exist at seeding time. The
   general defect is "promotion deletes paths it has no information about", and
   the skip list is only one source of such paths.

**Chosen — make promotion provenance-aware.** Record at `open` exactly which
paths were seeded into the workspace; at `close`, use that record to decide
removals. This repairs the asymmetry at its root — the two ends now exchange
the information they were missing — and covers *every* source of current-only
paths, not just the skip list.

## Reconciling "whole-program working copy" with "do not delete"

These pull in opposite directions and the resolution is the substance of this
ticket. The reconciliation is that **existence is the wrong question;
provenance is the right one.**

`specs/current` must not become an accumulating union of every file any ticket
ever produced — so a ticket *must* be able to delete. But a ticket can only
have decided about a file it was actually given. So:

| Path in `specs/current` but not in ticket `desired/` | Was it seeded? | Promotion |
|---|---|---|
| Ticket was given it and dropped it | yes | **removed** — a recorded deletion decision |
| Excluded from the workspace by design | no | **preserved** — no decision exists |
| Added to `specs/current` after `open` | no | **preserved** — no decision exists |

The whole-program-copy semantics survive intact: deletions still propagate, so
`specs/current` tracks the program rather than accumulating. What no longer
propagates is deletion-by-default of paths the ticket never saw — which was
never a semantic, only an artifact of `rmtree`.

Both halves are pinned by tests that fail if either is weakened:
`test_promotion_still_removes_a_path_the_ticket_deleted` guards the working-copy
half; `test_promotion_preserves_a_current_only_test_file` guards the other.

## Implementation

- `scripts/new_ticket_workflow.py` — `workflow_tree_seed_paths()` computes the
  logical seeded set (stable across `--force` and resumed scaffolds);
  `ticket_state_payload()` records it in `ticket.yaml` as `seed_manifest`
  (`desired`, `excluded`, `source`).
- `scripts/spec_evolution.py` — `promote_current_tree()` replaces
  `replace_tree` on the promotion path, partitioning `current - desired` into
  `removed` (seeded) and `preserved` (unseeded); `load_ticket_seed_manifest()`
  reads the record back; `print_promotion_report()` enumerates both sets on
  close so nothing leaves `specs/current` unannounced.
- **Safe default:** a ticket opened before this landed has no `seed_manifest`.
  That is treated as *no deletion intent is provable*, not as an empty seed, so
  promotion preserves everything and reports the basis. MF-021's own workspace
  is exactly such a ticket (opened before the fix existed) — see
  `self-verification.md`.

## Model impact: none, deliberately

TLC is unchanged at **919 distinct states, depth 21, 11 variables**. No new
close-failure path was modelled because the chosen resolution introduces none:
`close ticket` succeeds and preserves, rather than aborting. The plan's
`semantic_model_rule` would have made an abort a legitimate model addition;
preserve-and-enumerate is a change to promotion's file-level effect, not to the
command's state machine, so the model correctly does not move.
