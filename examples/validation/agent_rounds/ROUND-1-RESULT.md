# Round 1 — two tasks, two agents, and the round refuted its own author

**Toolchain under test:** `973c780` (merged `main`), via the installed
`spec-double-compiler` clone on PATH — verified to carry all five of this
session's fixes before the round ran.
**Agents:** 2 × `sonnet`, no toolchain source reading permitted, hard call budgets.
**Cost:** 98,166 subagent tokens total. **Both tasks completed.**

---

## 1. The numbers, against the predictions recorded before the round

| task | predicted | measured | tool calls | outcome |
|---|---|---|---|---|
| `T2-close-ticket` | **EXPENSIVE, 4+ round trips** | **2 round trips** | 10 | DONE |
| `T4-read-a-refusal` | CHEAP, 2 round trips | **1 round trip** | 7 | DONE |

**THE CONTROL HELD.** `T4` was declared the positive control: *"if T4 is
expensive the harness is measuring the agent, not the toolchain, and the round
is void."* It came in at 1 trip — better than predicted — so the harness is
measuring the tool.

**AND THE ROUND'S HEADLINE PREDICTION WAS WRONG.** `tasks.toml` committed the
consequence in advance:

> *"If this comes in at 1-2 trips the ledger's round-0 costs were an artifact of
> that agent and must be withdrawn."*

It came in at 2. **The withdrawal is §2.**

---

## 2. `F-01` IS REFUTED, AND THE REFUTATION IS THE MOST VALUABLE ROW IN THE ROUND

`FRICTION-LEDGER.md` `F-01` claimed:

> *three sequential refusals to close one ticket, each revealing one problem …
> all three were knowable on the first read.*

**The gate reports every failing top-level clause in ONE pass.** Measured
directly on a fresh tree with a completely unfilled ledger:

```
VERDICT: REJECTED -- close refused:
  - REJECTED -- no recursive refinement record. …
  - REJECTED -- no `narrative:` recorded. …
```

**Two clauses, one refusal.** The round-1 agent got the same shape and fixed
both in a single edit, which is why it paid 2 trips and not 4.

**So where did round 0's three trips come from?** Reconstructed from the
transcript, and none of it is what `F-01` said:

| round-0 trip | actual cause | the tool's fault? |
|---|---|---|
| 1 | the gate listed BOTH clauses; **the author was reading `tail -5` of the output and acted on the last line only** | **no — the author truncated the answer** |
| 2 | a blunt `sed`/regex edit **broke the ledger YAML** (`expected <block end>`) | **no — self-inflicted** |
| 3 | `refinement.outcome`, revealed after `refinement.searched` was set | **yes, and this one survives** |

**Two of three round-0 trips were the author's, not the toolchain's.** `F-01` is
withdrawn as written.

**What survives, measured:** the `refinement` sub-clauses **cascade**. Setting
`searched: true` satisfies the "no record" clause and *then* reveals `outcome`.
Verified in two passes. **That is one extra round trip, not two**, and it is
confined to one sub-object rather than being a property of the gate.

**And the round-1 agent independently judged the ledger refusal
`IRREDUCIBLE`-leaning**, on the grounds that *"the ledger file's own comments
explained the schema and which fields gate refusal"* — a second, independent
signal against `F-01`.

---

## 3. What stands

**`F-02` stands, and was hit independently.** The agent's first refusal was
`ticket TK-01 is not closed in ticket_plan.yaml: status=next`, and it graded it
**`TOOL-COULD-HAVE-SAID`**: *"the tool's own error message alone didn't say
which file/field to edit … it was inferable but not spelled out."*

**`F-05` is CONFIRMED as a do-not-change, by the agent that hit it.** `T4`'s
agent tripped on the doubled `specs/program_model/specs/` resolution and
reported: *"the tool's own note flagged this … a minor surprise but not a
blocker since the note explained it plainly."* **A surprising behaviour that
announces itself costs a sentence of confusion and zero round trips.** That is
the row every other row should be measured against.

---

## 4. A FIX SHIPPED THIS SESSION WAS INDEPENDENTLY MEASURED AS WORKING

`#301` put the remedy into the `--out` refusal. `T4` exists to test exactly that,
and the agent's verdict was unambiguous:

> **YES** — the error message named the exact constraint and gave a concrete
> example path to use instead, **which worked unmodified**.

**One round trip, remedy applied verbatim from the message.** This is the first
change in this programme measured as working by an agent that did not know it
had been made, and it is the shape `CL-02`, `CL-05` and `CL-06` are proposing to
copy.

---

## 5. What this round does NOT establish

- **`n=2`, one model, one arm.** No blind judging happened: the agents graded
  their own transcripts. `README.md` §4 specifies two blind judges reading the
  transcript, and **that was not done** — these are self-reports, and a
  self-reported `IRREDUCIBLE` is exactly the verdict an agent has an incentive
  to give.
- **Both agents were told the budget.** An agent that knows it has 8 calls
  behaves differently from one that does not. The budget is the interception
  mechanism and it is also a treatment.
- **`T1` and `T3` were not run.** `T3` is the one predicted to produce a SILENT
  wrong answer, which is the most valuable failure mode in the set and the only
  one that cannot be seen in a round-trip count.
- **The toolchain was the FIXED version.** Round 1 cannot say what any of these
  cost before this session's fixes; it is a baseline for the next round, not a
  delta on the last one.
