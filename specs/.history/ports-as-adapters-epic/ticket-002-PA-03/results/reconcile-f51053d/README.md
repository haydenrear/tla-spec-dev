# PA-03 re-measured on the epic tip after PA-02 merged

**The sealed pre-merge runs one directory up are NOT edited and NOT restated.**
This directory holds the same measurement re-run end to end on the reconciled
tree, in the shape EVAL-SUPPRESS used for the same situation.

- **Pre-merge run:** branch point `1cad5ea`.
- **Re-run:** `feature/PA-03` merged with `origin/epic/ports-as-adapters` at
  `f51053d` (PA-02), then at `5cf13ee` (the owner's D1 correction, documentation
  only).

## Not one cell moved

| | arm A | arm B |
|---|---|---|
| per-mutant cells differing from the pre-merge run | **0 of 88** | **0 of 88** |
| `per_class` block identical | yes | yes |
| per-instrument executability identical | yes | yes |
| controls red | `M07` (`corpus-port` only) | `M07` (`corpus-port` only) |

**Strictly comparable cells between the arms: 8 mutants x 8 instruments = 64,
all 64 identical.** Unchanged from the pre-merge run, and unchanged from the
56-of-56 baseline it reproduces.

Guard relaxation: **3 of 3 on `corpus-neg` and 3 of 3 on `corpus-port`, both
arms.** `corpus-port` executes 1,543 of 1,855 cases (83.2%) including **294
accepting `Reserve` cases**, and still does not decide `M07` — the blind spot is
the projection, unchanged.

## The corpora were regenerated, not reused

All five corpora were generated again from the `.tla` on the reconciled tree.
Every `cases.py` is **byte-identical** to the pre-merge generation:

| corpus | cases | `cases.py` vs pre-merge |
|---|---|---|
| `corpus-whole` | 43,128 | SAME |
| `corpus-neg` | 118 | SAME |
| `corpus-slice-res` | 2,438 | SAME |
| `corpus-slice-led` | 56 | SAME |
| `corpus-port` | 1,855 | SAME |

Two further independent generations of `corpus-port` on the reconciled tree are
byte-identical to each other across every package file, and its `cases.py`
(`08265aff…`) and `docs.md` (`2304fa76…`) match the pre-merge hashes exactly.
`case_coverage.json` differs in one field only — `source`, which records the
output directory — and the directory is a different scratch path.

## The cap verdict is the pre-existing one

PA-02 changed nothing on the cap path: `git diff 1cad5ea f51053d -- scripts/corpus_diagnostics.py scripts/budgets.py scripts/case_modules.py examples/validation/ab/model/* specs/current/spec_manifest.yaml`
is **empty**.

The verdicts on the reconciled tree are the same distribution as before, which
is HP-03-DF-02's standing behaviour on an uncalibrated default of 200:

| corpus | cases | over cap |
|---|---|---|
| `corpus-whole` | 43,128 | yes, exit 2 |
| `corpus-slice-res` | 2,438 | yes, exit 2 |
| `corpus-port` | 1,855 | yes, exit 2 |
| `corpus-neg` | 118 | no |
| `corpus-slice-led` | 56 | no |

`--port-cases` remains off by default, so no existing corpus moved.

## Conflict surface

Three files, all resolved as union appends with the predecessor's entries first:
`specs/desired_program_model/deferred_findings.yaml` (PA-01 x5, PA-02 x2,
PA-03 x3), `specs/results/complexity_ledger.json` (86 base entries, then
PA-02's, then PA-03's two), `specs/results/skill_feedback.md`.
`ticket_plan.yaml` auto-merged; the epic-plan validator reports OK.

**No source overlap.** PA-02 owns `scripts/code_complexity.py`,
`tests/test_code_complexity.py` and `references/complexity_intuition.md`; PA-03
owns `scripts/generate_cases_from_tlc_dump.py`,
`tests/test_port_case_generation.py`, `prompts/hexagonal_implementation.md` and
`references/generation_modes.md`. Neither side edited a file the other did.

Full suite on the reconciled tree: **1095 passed** (1058 for PA-03 alone, plus
PA-02's `tests/test_code_complexity.py`).

## PA-02-DF-01 reads onto this ticket

Recorded here rather than by editing the sealed narrative. PA-02's produced-code
instrument, like for like on implementation-only figures, **supports no
simplification claim for either arm** — the ported tree is larger on
`code_lines`, `public_surface`, `modules` and `classes`, and flat on branching
and depth.

That is the same finding as this ticket's, reached by an instrument that has
never agreed with this one before: **the port costs size and buys structure, not
simplicity**, and **the port boundary became visible to generation and no verdict
moved**. Two independent measurements, one conclusion — the structure arrived
and, so far, it has not changed what anything catches. PA-06 should read them
together.
