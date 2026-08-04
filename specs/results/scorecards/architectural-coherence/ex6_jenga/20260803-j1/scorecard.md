# ex6_jenga — judge pass 1 (`20260803-j1`)

scorecard_version 1 · commit `ab0dfee` · arm `null` (single-artifact eval)
Judge: `claude-opus-5[1m]`, pass 1, blind to arm.

| D1 | D2 | D3 | D4 | D5 | total |
|---|---|---|---|---|---|
| 0 | 1 | 0 | 0 | **4** | **5**/20 |

**Read this total correctly.** `ex6_jenga` is a deliberately incoherent refusal
control. Four near-floor scores are what it was built to earn, and the card
itself forbids averaging it against anything. The only dimension it is actually
competing on is D5, and there it ties for the highest score in the tree.

## What I re-ran myself

Read-only at this commit:

- `analyze complexity` — bound 1,344 COMPLETE over 4/4 variables, Q = 0.000, one
  emergent component, **four dense rows** (`dirty` 5/5, `lastCommand` 5/5,
  `auditLog` 4/5, `status` 4/5) and **four dense columns**.
- `analyze architecture` with `--components --code hub --map` — `unmappable`,
  exit 0, 6/6 modules mapped, 7 edges, **7 convergences, 0 divergences, 0
  absences**, `divergence_detectable = FALSE`, basis limits
  `unfalsifiable_coherence` + `partition_does_not_decompose`, declared partition
  `modularity_q = -0.1856` and `crossing_action_fraction = 0.8` both FAIL.
- Enumerated every file in the fixture: README, three `hub/` modules, four spec
  files, four evidence transcripts. **No tests directory exists.**

The answer key reproduces exactly.

## D1 — bug detection: 0

Nothing to score. No tests, no cases, no adapters, no providers, no corpus, no
seeded faults. Anchor 0 says "cases exist and pass; no seeded fault is caught" —
here not even cases exist, so 0 is the floor and the floor is where it lands.
Correct for a refusal control; a number here would be invented.

## D2 — complexity: 1

`Jenga.tla:43-78` — every action assigns all four variables. Four dense rows and
four dense columns, measured. Anchor 2's clause "no god-state, no variable written
from everywhere" is negated on every row, by construction.

Anchor 1's literal text ("no relationship between the figures and the design is
argued") actually *understates* the artifact — `Jenga.tla:12-18` argues the
relationship explicitly and names the three shapes it reproduces. But the ladder
is monotone in substance and anchor 2's condition fails, so 1 is the cap.
`lastCommand` is written by all five actions and read by nothing but a
`TypeInvariant` type conjunct — dead weight the descriptor cannot flag as such.

## D3 — modularity: 0

Anchor 0, measured, by design. State is written from everywhere, so no variable is
confined to a component under *any* partition. In the code every module imports
both others (`lifecycle.py:5-6`, `audit.py:5` and `:20`, `flags.py:17-18`), all
three component pairs are ported, and `divergence_detectable = false`. No boundary
is discernible — anchor 0's exact wording. The declared partition's own file calls
itself USELESS and says why.

Recorded, not scored: the three modules do take collaborators by constructor
injection (`lifecycle.py:10`), so the runtime wiring is marginally better than the
import graph. It does not reach anchor 1, because no boundary is declared that the
code could be said to violate *or* honour.

## D4 — behavior preservation: 0

Nothing checks this artifact's behavior. No tests, no corpus, no invariant beyond
`TypeInvariant`, no exercise of `hub/` of any kind.

I considered 1 on the grounds that `ex6-run2` enumerates round 1's measurements
and shows each still holding. That is a regression check on the **tool's verdict**,
not on the fixture's behavior, and anchor 1 requires a test suite to pass, of which
there is none. Lower, per rule 5. Recorded so nobody reads the fixture's verdict
stability as behavioral evidence.

## D5 — honesty: 4

- **It argues against its own importance in its own title**: `README.md:1-30`,
  "why it is the CONTROL and not the evidence", naming this repository's own model
  as the better Jenga because "nobody built it to fail."
- **Its own declaration file calls itself useless** and says why
  (`architecture_components.yaml:1-8`).
- **It pre-commits the FAIL conditions that would flatter it**
  (`README.md:88-98`): reporting 0 divergences as a clean result, presenting the
  convergences as evidence the code respects a boundary, or "fixing" the fixture by
  declaring a partition under which something can diverge.
- **It refuses rather than certifies**, and I reproduced the refusal verbatim:
  `unmappable`, two basis limits, "there is no flag, key, annotation, or
  environment variable that turns it into `coherent`", exit 0.
- **The record carries results unflattering to the epic that owns it**:
  `ex6-run1/scoring.md:47-67` scores the epic's own DP-2 prediction **MISSED**;
  `ex6-run2/scoring.md:57-72` files EV-03-DF-01 — this repository's own declared
  four-component partition does not decompose its own model
  (Q = −0.025485, crossing fraction 0.6), contradicting a ticket note that still
  stands uncorrected.

`refuses_to_claim`: that its zero divergences are a clean result, and that the
mechanism it demonstrates is general — `README.md:100-115` states that
`consumable_as_architecture` is true for *any* declared partition including one
failing all three criteria, so the criteria table does not stand between a project
and a false clean, and `unfalsifiable_coherence` "catches the fully degenerate case
only."

**Accuracy defect recorded, not scored** (card rule 7): `ex6-run1/scoring.md:11`
says "convergences 6" where its *own committed artifact*
`ex6-run1/artifacts/ex6_reflexion.txt:14` says 7 — as do the fixture evidence,
round 2, and my rerun. A miscount in a summary is not a claimed clean and the
primary artifacts are correct, so I did not dock. It is exactly why the card says
score artifacts and not claims.

**Prose note.** The README is persuasive and I discounted it. Every claim above is
a file I read or a command I ran.

## Verdict

A refusal control that earns four near-floor scores exactly as intended and one of
the two highest honesty scores in the tree: it names a better piece of evidence
than itself, calls its own declared partition useless, pre-commits the ways it
could be misread, and files the hole in the mechanism it exists to demonstrate.
