# Change ledger — what the rounds say we have to change

**This is the file the owner asked for: the running list that feeds attribution
and the influence graph.** Every entry is a CATCH in
`references/bug_attribution.md`'s sense, with `channel` naming the round that
produced it, an architectural `area` in prose, and a price DECLARED BEFORE the
change is attempted.

**Nothing here is fixed yet.** A change ledger whose entries are already done is
a changelog; this is the input to the decision, not the record of it.

---

## Status key

| status | meaning |
|---|---|
| `OPEN` | filed, not decided |
| `PRICED` | a cost is declared and the owner has not chosen |
| `ACCEPTED` | the owner chose to make it |
| `REFUSED` | the owner chose not to, WITH A REASON — and the declared price stands as the record of what it would have cost |

**`REFUSED` is a first-class outcome.** `GOAL-consumption-obligatory` measured
this project harvesting 1-of-41 findings; a ledger that can only say "done" or
"not yet" produces that number again.

---

## From round 0 — `FRICTION-LEDGER.md`, an agent's real run

| id | area | what changes | price, declared before | status |
|---|---|---|---|---|
| `CL-01` | `scripts/complexity_ledger.py` — the close gate | report EVERY unsatisfied clause in one pass, not the first | ~20 lines, a loop and an accumulator; the clauses are already evaluated independently, so no change to what is required | `PRICED` |
| `CL-02` | the close gate's plan-status check | name the accepted status values in the refusal | ~2 lines, one f-string | `PRICED` |
| `CL-03` | workflow close / `scaffold workflow` | EITHER scaffold the workflow-level ledger input (~5 lines, changes what a fresh tree contains — declare it) OR correct the message that names the wrong producer (~1 line) | **two different fixes, deliberately not conflated** | `OPEN` |
| `CL-04` | the `close` subparser | EITHER add `close workflow` as a thin wrapper (~15 lines, changes the CLI surface) OR name `scripts/close_tickets.py` in the error (~1 line) | as above, declare which | `OPEN` |
| `CL-05` | `generate cases` arguments | default `--actions-metadata` to `<spec dir>/actions.yml` when present AND print which file was used | ~6 lines. **The print is not optional — it is the safety**, because a project with an unintended actions.yml would start applying it | `PRICED` |
| `CL-06` | `analyze complexity` input resolution | when the named `.cfg` is absent, list the `.cfg` files beside the `.tla` | ~4 lines | `PRICED` |
| `CL-NOT-A-CHANGE` | `report_out_resolution` | **DO NOT CHANGE.** The surprising `--out` resolution is printed unprompted every run, and that is why it cost zero round trips | recorded so a later round does not "fix" a message doing its job | `REFUSED` |

## From round 1 — the first designed round

*Filed when the round reports. Each row will carry the task id that produced it
and the judge verdict — `TOOL-COULD-HAVE-SAID` / `DOC-COULD-HAVE-SAID` /
`IRREDUCIBLE` — because only the first class becomes a change.*

---

## How this feeds the influence graph

Each row is an edge from **a region of the architecture** to **a measured cost**.
Rows accumulating on one region is the signal the whole programme is for:

> Which areas produced friction that every automated instrument missed?

Round 0 already concentrates: **`CL-01`, `CL-02` and `CL-03` are all the CLOSE
PATH**, three of six rows on one region. That is a hypothesis, not a result —
`n=1`, one agent, and the close path is also the most-exercised operation in the
set, so it has the most chances to produce a row. **A round with a per-region
denominator is what turns it into a rate.**
