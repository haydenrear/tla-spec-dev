# ex2 run 2 — scored against PREDICTIONS.md (E2-*), plus run-1 divergence

Run date 2026-07-21. Identical instructions, fresh pristine copy. Owner
re-verified the descriptors, the model delta (the new cancellation invariant
is textually identical to run 1's), and the manifest cap rationale.

| Prediction | Verdict | Evidence |
| --- | --- | --- |
| E2-P1 no complexity refusal; advisory only | **PASS** | Scanner exit 0 both scans; two advisory component warnings changed nothing. The only refusal was again the corpus hard gate on the PRISTINE baseline (VAL-08 reproduced exactly, same wording), resolved via its documented accept path. |
| E2-P2 ticket completes, tests green | **PASS** | Same end-to-end depth as run 1: TLC green (External 123,528 distinct, 4s), 199 internal + 1,648 external cases against the live monolith, channel enforcement 13 bindings, test graph 4/4 with 256 cancellation cases. |
| E2-P3 bound=4 not misread | **PASS** | "A floor over one variable, not a model size"; exclusions read correctly; TLC growth (49,386→123,528) correctly identified as where the change shows up since the enlarged dimension is unbounded. |
| E2-P4 no complexity waivers | **PASS** | Complexity thresholds untouched; corpus cap 50→400 with recorded rationale via the gate's documented path, after establishing the baseline already fails. |

## Run 1 vs run 2 divergence

Convergence is striking on everything semantic: same Core/Internal placement,
same `o \in outbox` cancellation window, a **textually identical** new
invariant (`cancelled => projections[o] = "none"`), same route shape, same
descriptor interpretation, same pristine-gate diagnosis with nearly the same
cap (392 vs 400). Divergence is scope texture: run 2 also modeled the 409
already-fulfilled negative action (1,648 vs 1,520 cases) and richer
production edges (404/idempotent-200), and its cluster cut landed as
9+14 actions with two advisory warnings where run 1 got 8+13 with one —
same seam, slightly different membership. Both within protocol tolerance;
WHETHER and WHERE converged, breadth varied.

VAL-08/09/10/11 all reproduced independently (VAL-10 sharpened: the
generator PASSes a corpus at cap 400 that the exporter then REFUSES at its
silent default 50 — an internal inconsistency, not just a gap). Run 2 did
not mention the corpus gate's suggested-move line (VAL-13) — not a
contradiction, just unreported. New minor polish items filed together as
VAL-18.

## Toolchain verdict for this run

Second independent confirmation that the formerly-unusable ticket path
completes end to end with complexity purely advisory, and that the
descriptor's least-flattering shape (bound 4, nine exclusions) is read
correctly by real agents twice out of twice.
