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
| `CL-01` | `scripts/complexity_ledger.py` — the `refinement` sub-object only | **RE-PRICED AND SHRUNK.** ~~report every clause in one pass~~ — **the gate already does that.** What survives: `refinement.searched` and `refinement.outcome` cascade, so satisfying the first reveals the second | ~4 lines: evaluate both sub-clauses before returning. **Was priced at ~20 lines against a defect that did not exist** — see `ROUND-1-RESULT.md` §2 | `PRICED` |
| `CL-02` | the close gate's plan-status check | name the accepted status values in the refusal | ~2 lines, one f-string | `PRICED` |
| `CL-03` | workflow close / `scaffold workflow` | EITHER scaffold the workflow-level ledger input (~5 lines, changes what a fresh tree contains — declare it) OR correct the message that names the wrong producer (~1 line) | **two different fixes, deliberately not conflated** | `OPEN` |
| `CL-04` | the `close` subparser | EITHER add `close workflow` as a thin wrapper (~15 lines, changes the CLI surface) OR name `scripts/close_tickets.py` in the error (~1 line) | as above, declare which | `OPEN` |
| `CL-05` | `generate cases` arguments | default `--actions-metadata` to `<spec dir>/actions.yml` when present AND print which file was used | ~6 lines. **The print is not optional — it is the safety**, because a project with an unintended actions.yml would start applying it | `PRICED` |
| `CL-06` | `analyze complexity` input resolution | when the named `.cfg` is absent, list the `.cfg` files beside the `.tla` | ~4 lines | `PRICED` |
| `CL-NOT-A-CHANGE` | `report_out_resolution` | **DO NOT CHANGE.** The surprising `--out` resolution is printed unprompted every run, and that is why it cost zero round trips | recorded so a later round does not "fix" a message doing its job | `REFUSED` |

## From round 1 — the first designed round

**The round's largest output was a SUBTRACTION.** See `ROUND-1-RESULT.md`.

| id | task | area | verdict | what changes | status |
|---|---|---|---|---|---|
| `CL-01` | `T2` | the `refinement` sub-object | `TOOL-COULD-HAVE-SAID` | re-priced ~20 lines → ~4; see above | `PRICED` |
| `CL-02` | `T2` | the plan-status check | `TOOL-COULD-HAVE-SAID` — agent: *"didn't say which file/field to edit … inferable but not spelled out"* | unchanged: name the accepted values | `PRICED` |
| `CL-07` | `T2` | the ticket ledger's TODO fields | `IRREDUCIBLE`-leaning | **none proposed.** The agent's worst moment was telling gating TODOs from recorded-not-refusing ones — but it resolved it from the file's own comments, so the tool did tell it. **Filed as measured, not as a change** | `REFUSED` |
| `CL-NOT-A-CHANGE` | `T4` | `report_out_resolution` | — | **CONFIRMED do-not-change by the agent that hit it**: *"not a blocker since the note explained it plainly"* | `REFUSED` |

### And one row that is a RESULT rather than a change

| id | what was measured |
|---|---|
| `CL-VALIDATED-301` | **`#301`'s remedy works.** `T4`'s agent: *"YES — the error message named the exact constraint and gave a concrete example path, which worked unmodified."* One round trip, remedy applied verbatim. **The first change in this programme measured as working by an agent that did not know it had been made** — and the shape `CL-02`, `CL-05`, `CL-06` are proposing to copy. |

---

## How this feeds the influence graph

Each row is an edge from **a region of the architecture** to **a measured cost**.
Rows accumulating on one region is the signal the whole programme is for:

> Which areas produced friction that every automated instrument missed?

Round 0 concentrated on the **close path** — `CL-01`, `CL-02`, `CL-03`, three of
six rows on one region — and round 1 **partly dissolved that concentration**:
`CL-01` shrank from ~20 lines to ~4 once the defect it named was measured and
found not to exist.

**That is the influence graph doing its job in the direction nobody wants it
to.** A region looked hot; a designed round made it cooler. Had the change been
made off round 0's price, ~20 lines would have been written against a defect
that was not there — and the close path would have been credited with a fix it
never needed, permanently, in a sealed record.

**The standing caution:** the close path is still the most-exercised operation
in the task set, so it has the most chances to produce a row. **A per-region
denominator — rows over invocations of that region — is what turns a count into
a rate**, and no round has one yet.
