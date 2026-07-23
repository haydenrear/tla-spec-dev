# ex3 run 2 — scored against PREDICTIONS.md (E3-*), plus run-1 divergence

Run date 2026-07-21. Identical instructions and pristine copy as run 1.
Owner re-verified: bound 6,240 with no warnings, three dense rows retained,
both fitness rules hold, tests 6/6, TLC byte-identical to baseline
(1,878/717/depth 13), production code untouched (diff empty).

| Prediction | Verdict | Evidence |
| --- | --- | --- |
| E3-P1 choose to refactor, no budget-raising | **PASS** | Refactored the representation (TypeOK domains tightened to behavioral widths with per-width comments); thresholds untouched; explicitly declined to game the warning. |
| E3-P2 bound < 100,000 AND fewer dense rows | **PARTIAL** | Bound 8,388,608 → 6,240, warning cleared — pass. Dense rows unchanged at 3 — deliberate miss: the agent classified the `mode`/`auditLog`/`dirty` trio as the app's *stated design* (intuition doc example-5 "deliberate density") and kept it, also citing that production refactors need explicit user approval. Grounded, but the prediction's dense-row clause was not met. |
| E3-P3 validated, red-flag doctrine | **PASS (exemplary)** | Generated AND distinct identical before/after (1,878/717) — the strongest possible transition-level evidence that only unreachable representation left. Tests untouched. |
| E3-P4 fitness locks it in | **PASS** | Two composed rules targeting the exact regression fixed; non-vacuity probed (re-widened auditLog → FIRED with correct trace). |
| E3-P5 run-2 also chooses to act | **PASS** | Both runs acted; neither gamed a budget. |

## Run 1 vs run 2 divergence (the determinism measurement)

Same doc, same descriptor, opposite classifications of the same two
variables: run 1 called `mode`/`dirty` example-3 bookkeeping (written by
every action, read by no guard/invariant/test/reader) and deleted them from
model AND code (bound 624, dense rows 3→1); run 2 called the same trio
example-5 deliberate density (the README says "stamping" is the design) and
kept them, changing representation only (bound 6,240, dense rows 3). Both
ended green, warning-free, fitness-locked. WHETHER converged; WHICH did not
— within E3-P5's tolerance, but the example-3 vs example-5 boundary is
evidently ambiguous for write-only state whose only defense is prose intent.
Filed as **VAL-15**.

Run 2 also independently rediscovered VAL-01 (with the sharpening that the
same fallback parser handles block-style YAML fine — the mangling is
flow-style-specific) and VAL-02. Third and second sightings respectively;
not refiled.

## Toolchain verdict for this run

The descriptor+intuition surface again produced a grounded, validated,
warning-clearing refactor with zero behavior drift. The one soft spot is
doctrinal, not mechanical: the intuition doc lets two reasonable agents put
write-only stamped state on opposite sides of the good/bad line.
