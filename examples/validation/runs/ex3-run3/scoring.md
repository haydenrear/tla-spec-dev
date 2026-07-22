# ex3 run 3 — scored against PREDICTIONS.md (E3-* + R3-E3)

Run date 2026-07-22, against the main-readiness batch tip. Owner re-verified:
bound 624 with no warnings, three fitness rules hold, tests 6/6 and
byte-identical to the pristine example, decision doc grounded.

| Prediction | Verdict | Evidence |
| --- | --- | --- |
| E3-P1 choose to refactor, no budget-raising | **PASS** | Refactored; thresholds untouched. |
| E3-P2 bound < 100,000, fewer dense rows | **PASS** | 8,388,608 → 624; dense rows 3 → 1 (auditLog defended with named dependents). |
| E3-P3 validated, red-flag doctrine | **PASS** | TLC green (717/270, depth/outdegree constant, generated and distinct fell together — checked explicitly); tests unmodified. |
| E3-P4 fitness locks it in | **PASS** | Three rules (bound cap, per-domain widths, no-new-bookkeeping), all hold. |
| **R3-E3 convergence after the doc sharpening** | **PASS — the key result** | The agent applied the write-only-state test BY NAME, classified `mode`/`dirty` as bookkeeping ("stated intent is not a reader"), deleted them from model AND code — converging with run 1's now-canonical call where run 2 had diverged. It also correctly used the test's other edge: `auditLog` PASSES (guards read it, tests assert it) and was defended, not chased. VAL-15 is resolved by measurement. |
| X-P1/X-P2 | PASS | No PATH wrapper; 2 findings recorded, none fixed. |

## Findings from this run (minor, batched — no new backlog entries filed)

- The PyYAML manifest-block constraint behaved exactly as documented
  (CONFIG ERROR → .json fallback) — run 3 confirms VAL-01's fix; the agent
  suggests one doc line on the asymmetry (budgets/justification parse under
  the fallback, fitness rules don't). Folded into the run report only.
- Real observation worth carrying: the invariant-coverage section counts a
  TypeOK type conjunct (aliased through `Inv`) as "read by an invariant," so
  write-only variables show clean coverage and only the dense-row section
  points at them. The intuition doc's write-only-state test covers the gap;
  a sharper coverage line (distinguish type conjuncts from semantic reads)
  is a candidate future improvement. Recorded here for post-main triage.
