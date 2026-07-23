# ex3 run 1 — scored against PREDICTIONS.md (E3-*)

Run date 2026-07-21. Agent worked in a scratch copy; artifacts collected under
`artifacts/`. Every headline claim below was independently re-verified by the
epic owner in the agent's workspace (TLC re-run, tests re-run, descriptor and
fitness scan re-read, finding 1 reproduced).

| Prediction | Verdict | Evidence |
| --- | --- | --- |
| E3-P1 choose to refactor, no budget-raising | **PASS** | Agent refactored; budgets/thresholds untouched. Nuance beyond the prediction: it *defended* the audit-cap dense row as the program's real shape and left it (accepted complexity, argued from behavior) — exactly the intuition doc's "some components score badly and still need to exist." |
| E3-P2 complexity down: bound < 100,000, fewer dense rows, before/after recorded | **PASS (exceeded)** | Bound 8,388,608 → **624** (agent went past honest-domain-sizing by also deleting `mode`/`dirty`, which nothing read — legitimate, and predicted floor ~6,656 assumed they stayed). Dense rows 3 → 1. Both descriptors in `artifacts/`. |
| E3-P3 validated: TLC green, tests unmodified, red-flag doctrine applied | **PASS** | TLC 717 gen / 270 distinct, green (owner re-ran). Tests 6/6, zero assertion changes. Agent explicitly checked generated-and-distinct fell together with depth/outdegree constant — the ledger red-flag test, applied unprompted. |
| E3-P4 fitness function locks it in | **PASS (exceeded)** | Three composed rules, all holds (owner re-ran); agent also proved non-vacuity by re-widening a domain in a scratch copy until one FIRED. |
| E3-P5 run-2 determinism | pending run 2 |
| X-P1 no PATH wrapper | PASS (per report; no contrary evidence) |
| X-P2 findings filed, not fixed | **PASS** | 3 findings reported, none fixed; filed as VAL-01..VAL-03 in the epic backlog. |

## Findings filed from this run

- **VAL-01** (real, owner-reproduced): manifest-embedded fitness rules under a
  bare python3 mis-parse via the fallback manifest parser — flow-style leaves
  become `INVALID: ... got keys ['{fact']` with no "PyYAML missing" hint,
  while `references/fitness_functions.md` promises an advisory CONFIG ERROR.
  The documented `.json` escape hatch works.
- **VAL-02** (real): every scan of a per-README manifest warns
  `budgets block ... missing kill_rate_floor, max_symmetric_instances` —
  retired fuzzing-era keys the shipped docs no longer tell projects to set.
- **VAL-03** (minor): `run_tlc.sh` leaves a TLC `states/` scratch directory
  inside the target project's spec dir.

## Toolchain verdict for this run

The sharpest test passed: descriptor + intuition alone (no suggestions, no
gates) led the agent to the right refactor, with the right validation
discipline, and to *defend* the complexity that was genuinely load-bearing.
