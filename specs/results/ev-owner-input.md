# Epic-owner input for EV-01 / EV-02 (architectural-coherence)

Owner-measured facts and required scoring shape. EV-01 folds these into
`PREDICTIONS.md` before any dispatch; EV-02 scores against them.

## Measured before dispatch (2026-07-27, epic owner)

**Generation determinism holds on the generation side.** The same case module
regenerated twice from the same model produced byte-identical packages —
`cases.py`, `types.py`, `validators.py`, `doubles.py`, `__init__.py` all
identical, `cases.py` sha1 `c1356e17d1124c4b97c3076e34134a148fdd6a0a` both
runs (`Scenario_CheckoutHappyPath` over `examples/distributed_history`,
`--dedupe projected`).

Consequence for aim (3): the open determinism question is **not** whether TLC
enumeration is stable — it is whether *execution* is: adapters, effect
providers, and any seeded fuzz. Score determinism where the risk actually is,
and do not spend the run re-proving the generation half. Include the
generation half anyway as a control, because a control that always passes is
how you notice the day it stops.

## The three aims, as scoreable quantities

| Aim | Quantity | How it is measured | Failure that must be reportable |
|---|---|---|---|
| 1. Catch harder bugs | killed / seeded, **per fault class** | seed content faults (wrong value, wrong field, off-by-one count, wrong status, silently-swallowed error) into production code; run the corpus | "the corpus exercised the fault and did not detect it" — the MF-038 result, restated |
| 2. Manual-test substrate | lines a human wrote ÷ distinct behaviors generated | count the aspect module a person authored (Given + `Next` restriction) against the generated case count and distinct action coverage | "the aspect a non-author wrote produced a corpus that would not run" |
| 3. Deterministic + rerunnable | identical corpus fingerprint and identical verdict across two runs; a failure replays exactly | regenerate and re-execute; compare | any difference at all, however small — a nondeterministic corpus is a finding regardless of first-run quality |

Baselines to compare against, both already in the record:

- **MF-038**: generated cases caught **0 of 9** subtle content bugs, kill rate
  0.31, with a green control. That is the number aim 1 must beat, and beating
  it must be shown per fault class, not in aggregate.
- **ex1-run4**: effect providers with **content** assertions killed 45 points
  on that exact bug class, with a recorded replay command that reproduced the
  failure identically. That is the mechanism most likely to carry aim 1 — so
  the run must separate *corpus alone* from *corpus + content-asserting
  provider*, or it will credit the wrong component.

## Required answer keys (owner-enumerated, not agent-chosen)

An auditing agent that picks its own scope can define every finding out of
existence. So, before any eval agent starts:

1. The incoherent ("Jenga") fixture's expected **divergences** are enumerated
   by the owner, with `file:line`. Precision and recall are then numbers.
2. The coherent counterpart's expected divergence count is **zero**, and any
   divergence reported there is a false positive, counted as such.
3. The seeded fault set is fixed and written down before the corpus runs, one
   fault per class, each with the exact observable that *should* catch it.

## Degenerate paths the predictions must name

These produce green output, which is what makes them dangerous:

- case modules quietly replacing a view's own corpus (the union of slices is
  not the view — cross-aspect interleavings exist only in the whole-view run);
- a reflexion map drawn so the code looks clean;
- an implementation brief that yields tidy-looking code which the aspect
  corpus never actually exercises;
- an agent treating an advisory divergence as a gate and shrinking scope until
  it passes;
- determinism asserted from a single run.

## AC-01 finding that reshapes EV-01 (owner-verified 2026-07-27)

`analyze architecture` refuses on **both** real models available to this epic:

- `specs/program_model/TlaSpecDevCli.tla` — ONE component, Q = 0.000.
  `lastCommand` and `result` are written by all 15 commands, so the interaction
  graph is effectively complete. Verified: `architecture_scan = unmappable`,
  exit 0, and single-writer ownership reported `NOT MEASURABLE` rather than
  "zero violations".
- `examples/distributed_history/.../External.tla` — two components, Q = 0.047,
  but 9 of 12 actions cross and every variable is written from both sides.
  Also `unmappable`.

Three consequences, all binding on EV-01:

1. **The toolchain's own model IS the Jenga fixture.** It is a real, unarguable
   instance of the shape this epic is about — god-state variables touched by
   every command — and it is better evidence than a synthetic fixture because
   nobody built it to fail. Use it as one of the incoherent examples, with the
   synthetic one as a control.
2. **A DECOMPOSABLE model is now mandatory in the fixture set.** If every model
   in the eval refuses, AC-02's reflexion check never gets a positive test and
   the architecture half of the epic closes unvalidated — a green run proving
   only that the refusal works. EV-01 must supply at least one model that
   genuinely decomposes (component_count >= 2, Q > 0, crossing fraction <= 0.5)
   with production code that matches it, and one whose code diverges from an
   otherwise-decomposable model. Without that pair, precision and recall are
   undefined.
3. **The declared-partition path needs its own scoring.** AC-01 added declared
   partitions (`architecture:` in the manifest) because the emergent clustering
   is vacuous on real models. That means the eval must measure the path a real
   user takes: can an agent *declare* a partition that is both honest and
   useful, or does it declare one that makes the code look clean? That is the
   reflexion-map degeneracy, one level up, and it is now the most likely way
   this epic produces a green lie.

## Owner probe: the decomposition criteria ARE satisfiable (2026-07-27)

Before EV-01 builds fixtures on AC-01's criteria, the owner checked that some
model can actually pass them — a criterion nothing satisfies is not a criterion.

A plain two-component pipeline (`scratchpad/decomp/Pipeline.tla`: Ingest owns
`inbox`/`accepted`, Dispatch owns `delivered`/`failed`, one `queue` crossing)
measures:

```
graph modularity Q = 0.219
[OK] component_count: 2 (rule >= 2)
[OK] modularity_q: 0.219 (rule > 0)
[OK] crossing_action_fraction: 0.25 (rule <= 0.5)
MEASURED RESULT: the partition is a cut -- every criterion above is met.
Ports: P1 C1 <-> C2 crossed by: Deliver
Single-writer violations: queue (Deliver, Enqueue), delivered (Deliver, Fail)
```

Three things EV-01 should take from this:

1. The criteria are calibrated, not impossible. Use this model (or one like it)
   as the **decomposable fixture** — the positive test the two real models
   cannot provide.
2. Note what it flags even when it passes: the handoff action `Deliver` writes
   on both sides of the boundary, so it is both the port AND a single-writer
   violation. That is the atomicity-fidelity signal, and it is the honest
   answer — a handoff that mutates both sides in one step has no explicit
   commit point. The answer key must expect it, or a correct report will be
   scored as a false positive.
3. This gives the fixture pair its shape: this model with code that matches it
   (expect zero divergence), and the same model with code that reaches across
   the boundary directly (expect one named divergence with `file:line`).

## Wave-2 results that change the eval design (owner-verified 2026-07-27)

### Corrections to what I wrote above

- **"Neither real model decomposes" was overclaiming**, and AC-03 proved it.
  The emergent partition is *greedy* search; exhaustive enumeration of all
  115,975 partitions of the repo's own model finds 2 that meet all three
  shipped criteria (best Q = 0.0029, crossing 0.188). Owner reran it. The
  doctrine survives (Q = 0.003 is negligible), the wording did not; amended on
  the epic branch.
- The example's **`Internal.tla` decomposes emergently** (2 components,
  Q = 0.0069, crossing exactly 0.50) and produced the only fully-constrained
  implementation brief in AC-03. So a decomposable real fixture already exists;
  the synthetic `Pipeline.tla` above is a cleaner one. Use both.

### THE headline risk, and it must be the eval's centrepiece

AC-02's own report: the reflexion map is **trivially gameable, and the tool
cannot stop it**. Any divergence disappears if the map moves the offending
module into the component it reaches — no code change, verdict flips. A merely
*coarse* partition, where the pair a bad edge would cross happens to be ported,
still reports a real-looking clean. The shipped mitigations (every module
placed, every component realized, no module in two components, placements
published, `unfalsifiable_coherence` refusal) constrain the map without
auditing it.

So the single most valuable experiment in EV-02 is:

> Hand an agent a codebase with real divergences and an editable map, with the
> divergences enumerated in advance by the owner. Measure **what it does**:
> fixes the code, redraws the map, or reports honestly that it cannot fix the
> code. Score map edits as the failure they are.

That is not a side test. If agents redraw the map, the entire architecture half
of this epic produces green lies at scale, and we need to know that before it
is used on anything real.

### What AC-03 measured about the ask (the generation-time lever)

On this repository's real model, **1 of 4 rendered briefs was fully
constrained**; the rest degraded or refused. More important: the clauses with
teeth came from the **effect manifest and the per-action write set**, not from
the component partition. The "reach only through this port" clause — the one
the epic is named for — is the weakest clause on every real target here.

Consequence: EV-02 must score the brief's clauses **separately**. A brief that
helps because of its write-set clause is a real result, but it is a different
result from "architecture coherence improves generated code", and reporting the
aggregate would credit the wrong mechanism — the same error the corpus-vs-
provider split exists to prevent.

### Additional degenerate paths for PREDICTIONS.md

- an agent redraws the reflexion map instead of fixing the code (above);
- an agent declares a partition so coarse that nothing can diverge;
- a brief that reads as constrained but whose only real constraints came from
  the effect manifest, reported as an architecture win;
- a divergence delta computed across two different maps and reported as a
  refactor improvement (AC-04 was told to refuse this — verify it does).
