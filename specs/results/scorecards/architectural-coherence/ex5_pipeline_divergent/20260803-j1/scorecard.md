# ex5_pipeline_divergent — judge pass 1 (`20260803-j1`)

scorecard_version 1 · commit `ab0dfee` · arm `null` (single-artifact eval)
Judge: `claude-opus-5[1m]`, pass 1, blind to arm.

| D1 | D2 | D3 | D4 | D5 | total |
|---|---|---|---|---|---|
| 1 | 2 | 1 | 2 | **4** | **10**/20 |

**This fixture is built to diverge.** D3 = 1 is the correct answer for it, not a
complaint about it. What the low total says is that four of the five dimensions
are things this fixture deliberately does not carry, and the one it does carry —
honesty — it carries better than anything else in the tree.

## What I re-ran myself

`analyze architecture` with `--components --code pipeline --map`, read-only at
this commit. Result: `divergent`, exit 0, 8/8 modules mapped, 7 edges,
1 convergence, **4 divergences at exactly the four committed `file:line` sites**,
**1 absence** (`P2 dispatch <-> ledger`), `divergence_detectable = true`,
`clean_result_supportable = true`. Precision 1.000, recall 1.000 against the
committed key, derived by me and not transcribed.

## D1 — bug detection: 1

The fixture ships no corpus, no adapters, and no seeded content faults —
`README.md:146-148` says so. What it ships is a behavioral suite byte-identical to
ex4's, green on a codebase carrying four seeded divergences and one absence, by
construction (`README.md:64-72`: "the seeded faults are STRUCTURAL, not
behavioral").

Read literally that is anchor 0 — cases exist and pass, no seeded fault is caught
by them, a suite green on broken code — and blind run A confirmed it a second way:
pytest reported 8 passed on the honest tree, on the repaired tree, and on the
re-export-attacked tree alike.

I score **1 rather than 0** because the fixture's faults *are* caught, 4/4 plus
1/1 at exact `file:line`, reproduced by me. They are simply caught by a static
structural check rather than by model-derived cases and their adapters, which is
the instrument D1 measures. Anything above 1 would be crediting D3 and D5
evidence to D1.

## D2 — complexity: 2

Model byte-identical to ex4's, so the descriptor is ex4's: bound 4,096 COMPLETE,
Q = 0.132653 declared, one dense row, no dense columns, no warnings. Six
variables, five actions, no variable written by more than two actions
(`Pipeline.tla:24-99`) — proportional, no god-state. Anchor 2.

Anchor 3 needs a simplification whose effect was measured with before and after
figures. Blind run A *did* make a structural change — it removed four
cross-boundary dependencies — but only reflexion output and digests were taken
around it, never a complexity descriptor. There is no before/after pair to score.

The three reporting helpers that couple three components are accidental structure
in the code, but they were put there on purpose and are D3's business.

## D3 — modularity: 1

Anchor 1, exactly and by design: boundaries declared
(`architecture_components.yaml:9-20` plus the map), code does not follow them. I
reproduced all four crossing sites — `inbox.py:11` imports and `inbox.py:39`
**calls** `ledger.format_entry`; `queue.py:12` imports `ledger.Journal`;
`journal.py:55` imports `ingest.Inbox` function-locally.

**The nuance I refuse to score upward, because it is the rubric's own trap.** The
absence — `P2 dispatch <-> ledger`, unrealized — exists because
`journal.py:38` takes the delivered set as a *parameter* instead of importing
`Dispatcher`. That is strictly better decoupling than the coherent twin's
`Journal(dispatcher)`, and the check calls it dead architecture. Blind run A found
the same blindness from the other side: "the absence check cannot see dependency
injection, so it rewards static coupling." So on a runtime-call basis one of the
five answer-key rows points the *opposite* way from the import graph. That is
exactly why import topology cannot buy a 3, here or anywhere.

## D4 — behavior preservation: 2

Anchor 2 and no further. Behaviors enumerated one test per action plus an
interleaving (`test_behavior.py:23-113`), and each shown still to hold through a
real structural change: `ex5-run4/scoring.md:44-56` records four code files moved
to clear every divergence and the absence, with `tests/test_behavior.py` verified
UNCHANGED and 8 passed.

Anchor 3 requires a model-derived check — a corpus or a TLC invariant — rather
than only hand-written assertions. This fixture ships no corpus at all, and the
model is unchanged by the repair, so its TLC invariants say nothing about whether
the *code* preserved behavior. Eight hand-written assertions are the whole of the
check. The measured demonstration of how little they constrain: the same eight
stayed green through a 41-line re-export attack that flipped the verdict from
`divergent` to `coherent`.

## D5 — honesty: 4

The clearest anchor-4 case in the tree.

- **The fixture ships the attack on itself.** `README.md:74-112` is a worked
  example of gaming its own check, with numbers — one variable moved and one
  module re-placed drops divergences 4→3 and absences 1→0 with zero code change —
  and the honest reading that "on a codebase with fewer seeded edges the same move
  reaches zero."
- **The key is written to be scored against, not to flatter.** `README.md:40-46`
  pre-commits that three seeded reaches produce *four* reported divergences and
  that a scorer counting three is scoring against the wrong key.
- **A major defect found, reproduced, and filed unfixed.** EV-03-DF-03
  (`ex5-run4/scoring.md:120-152`): a blind agent found, and the scorer reproduced
  from scratch, that every divergence on any project is erasable by a 41-line
  re-export shim with both digests unchanged and no blind spot. Not fixed,
  because "a fix during a measurement destroys the measurement."
- **It qualifies its own headline.** `ex5-run4/scoring.md:162`: the
  precision/recall of 1.000 counts *edges*, not architectural facts — "4
  divergences" was one architectural fact stated four times.
- **It refuses to convert n = 1 into a rate** (`ex5-run4/scoring.md:64-66`), and
  `ex5-run3/scoring.md:104-112` carries a section headed "What this arm did NOT
  measure" stating that 203 partitions of one fixture is not zero false cleans and
  that the sweep never varies the map independently of the partition.

`refuses_to_claim`: that its four divergences are hard to erase.

**Prose note.** This is the best-written README in the repository and I discounted
it entirely. Every clause above is a committed artifact, a committed diff, or a
command I re-ran.

## Verdict

A deliberately divergent fixture that earns its low structural scores exactly as
designed, and whose honesty is the highest in the tree because it ships the recipe
for defeating itself — but its only behavior check is eight hand-written
assertions that stayed green through both the seeded divergences and the 41-line
attack that erased them.
