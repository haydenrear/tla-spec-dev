# SI-01 — migrate the skill surface into a plugin

Ticket `SI-01`, wave 1 of `epic/self-improvement-substrate`, issue
[#334](https://github.com/haydenrear/tla-spec-dev/issues/334).
Branch `feature/334-plugin-migration`, based on `4d563e2d` (the epic tip).

The repository becomes a skill-manager **plugin** named `tla-spec-dev`; the skill surface
moves from the repo root to `skills/spec-double-2/`. `spec_double_compiler` (the package)
and `tla-spec-dev` (the CLI) keep their names.

## The rule this evidence is built around

**A red result means nothing until you know what red looked like before.** Every matrix
entry here was measured twice — once on this branch, once on a pre-move checkout of
`4d563e2d` — because the repository was already carrying failures before this ticket
started, and without the second measurement there is no way to tell them apart. Two of the
three "failures" below turned out to be pre-existing, and one regression turned out to be
genuinely mine.

| # | file | what it is |
|---|---|---|
| 1 | `pytest-before-migration.txt` | the repository suite on the pinned base, **before any file moved**: 10 failed, 1551 passed, 5 skipped |
| 2 | `pytest-after-migration.txt` | the same suite on this branch: 10 failed, 1551 passed, 5 skipped — **the same 10**, zero new |
| 3 | `spec-unit-tests.txt` | the assignment's spec-unit command (errors — see below) and the project-scope substitute actually run |
| 4 | `spec-unit-baseline-at-4d563e2d.txt` | the same project-scope command on a pristine pre-move tree: **identical 7 failures** |
| 5 | `graphs-summary.txt` | the three declared graphs, and the one regression that made a graph red |
| 6 | `graphs-specWorkflow-cliWorkflow-effectProviderExamples.txt` | the first full graph run |
| 7 | `graph-effectProviderExamples-after-fix.txt` | that graph green after the regression was repaired |
| 8 | `effect-providers-baseline-at-4d563e2d.txt` | the effect-provider validation on a pre-move checkout |
| 9 | `citations-vs-4d563e2d.diff` | line citations: checker-vs-checker, identical after normalizing the moved prefix |
| 10 | `citations-checker-at-4d563e2d.txt`, `citations-checker-after-migration.txt` | the two checker runs behind #9 |
| 11 | `eval-plugin-resolves.txt` | the eval plugin's symlinks and CLI shim after the move |
| 12 | `model-trees-agree.txt` | the adapter copies still agree across the three model trees; TLA+ changes are comment-only |
| 13 | `local-signal-GOAL-one-unit.txt` | the declared local signal for `GOAL-one-unit` |

## Results

**Repository unit suite** — 10 failed, 1551 passed, 5 skipped, identical to the baseline.
`comm -13` over the two sorted failure lists is empty: **zero new failures**. The migration
initially produced **26** of them; all 26 were repaired.

**Spec-unit** — the assignment names
`... run spec-unit-tests --ticket SI-01`, which exits with
`ERROR: spec-unit target does not exist: specs/tickets/SI-01/desired`. That workspace does
not exist on the epic branch. The assignment's *Model ownership* block makes scaffolding it
the epic agent's move and forbids the ticket agent from running `open ticket`, so this is
**reported, not repaired**, and project scope was run instead: 7 failed, 49 passed —
identical, test for test, to the same command on a pristine pre-move checkout.

**Graphs** — `specWorkflow` ✅, `cliWorkflow` ✅, `effectProviderExamples` ✅.
The last one was red twice first, and **the first failure was mine**: the effect-provider
examples import `spec_double_compiler` directly and every runner put `REPO_ROOT` on
`sys.path` to make that resolve. The package moved; the import died. Fixed at all 9
injection sites. A baseline run of the same validation on a fresh pre-move checkout failed
at `reminder_worker` — a failure this branch does *not* reproduce, recorded in
`graphs-summary.txt` as an unexplained fresh-checkout artifact rather than dressed up as a
finding either way.

**Citations** — `--fix` repairs numbers, never paths, so the cited paths were repointed by
hand and `--fix` was then run. Verified tool-against-tool, not by counting: identical
output after normalizing the prefix. (Counting them with two different `grep` patterns
first produced a bogus 21-vs-22 "change"; only running the same tool on both trees settled
it.)

**Model** — no TLA+ action added, removed or changed. All three `TlaSpecDevCli.tla` copies
change 14 lines, all 14 of them comments naming script paths, which is exactly what the
assignment's `tla` conflict key anticipated. The adapter copies remain byte-identical
across `program_model`, `current` and `desired_program_model`.

**Goal signal (`GOAL-one-unit`, contribution: enabling)** — `--help` and `--version` both
exit 0 from the checkout, and all three graphs are green. Expected effect was *none on its
own*; classification: **no measurable movement**, which is the right answer for an enabling
slice. The unit count moves in SI-02. Decided by SI-08.

## Deferred findings

`SI-01-DF-01` and `SI-01-DF-02`, appended to `specs/results/deferred_findings_final.yaml`
(35 → 37 rows). Budget 5, mode `batch`, 2 used.
