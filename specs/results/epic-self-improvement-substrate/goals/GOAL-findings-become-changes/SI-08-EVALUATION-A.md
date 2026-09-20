# `GOAL-findings-become-changes` — Evaluation A (SI-08), frozen reading

**Measured 2026-09-20 at base `2131cdad`.**
Instrument, as the plan names it: `improvement_ledger.py` (built by SI-04);
advisory, exit 0 always. It exited **0**.

> **Statement.** A finding that names a skill ends as an applied change, or a
> declined one with a reason on the record — never as `recorded-local`.
>
> **Baseline (b7a7d203).** 37 skill-feedback blocks: 13 `recorded-local`, 4
> `wontfix`; 33 + 6 deferred rows with no `skill_change` field at all.
>
> **Target.** every finding carries a `skill_change` disposition — applied,
> declined with a recorded reason, or not-a-skill; 0 `recorded-local` at epic
> close.

---

## First: the instrument was reading a quarter of its own population

**The harness path in the assignment block is wrong, and the run it produces is
silently partial.** Both are measurement defects and both are filed.

1. The assignment names `python3 scripts/improvement_ledger.py`. There is no
   `scripts/` directory at the repository root. The script is at
   **`skills/spec-double-2/scripts/improvement_ledger.py`** (`SI-08-DF-02`).

2. Run with the ambient interpreter — `python3`, which is Homebrew **3.14** on
   this machine — the ledger cannot import PyYAML and **skips both YAML
   backlogs**, printing:

   ```
   ! .../deferred_findings_final.yaml: PyYAML is not importable under
     /opt/homebrew/opt/python@3.14/bin/python3.14 -- backlog NOT read
     (this is not an empty backlog)
   ```

   It then prints a complete-looking table over **36 records from 2 files**.
   The metric this goal declares is *"findings by disposition across
   skill_feedback.md, **both deferred backlogs**, and the matrix"* — 4 sources.
   **Re-run under `uv run --python 3.12 --with pyyaml`, the same script reads
   121 records across 4 files.** (`SI-08-DF-01`.)

   The warning is honest and says "this is not an empty backlog" — but the
   table below it is not marked partial, and 36 is the number a reader copies.
   **Every figure below is the 4-file figure.**

```
improvement ledger -- 121 record(s) across 4 file(s)
```

| source | records | skill-anchored | `skill_change` recorded |
|---|---|---|---|
| `deferred_findings_final.yaml` | 79 | 35 | 14 |
| `skill_feedback.md` | 29 | 19 | 5 |
| `SELF-IMPROVEMENT-MATRIX.md` | 7 | 2 | 0 |
| `deferred_findings_next.yaml` | 6 | 0 | 0 |
| **total** | **121** | **56** | **19** |

### And the 121 is itself short by 16, in the direction that flatters the goal

**The epic partitioned the backlog and did not tell the instrument.** The ledger
hardcodes exactly four sources (`improvement_ledger.py:82-83`). The per-ticket
partition `specs/results/deferred/{ticket}.yaml` — which
`git-epic-workflow/references/deferment.md:47` declares as `per_ticket_backlog`,
and which SI-15, the epic agent and this ticket were all instructed to file
into — is read by **nothing**:

| partition file | rows | carrying `skill_change` |
|---|---|---|
| `EPIC-AGENT.yaml` | 1 | 0 |
| `SI-15.yaml` | 5 | 0 |
| `SI-08.yaml` (this ticket) | 11 | 11 |
| **invisible to the ledger** | **16** | **11** |

The true population is **137, not 121**. And the bias is not neutral: the
partition holds a *disproportionate* share of the one field the goal is measured
on, so **the goal's own number is biased downward by the epic's filing
convention**, and the bias grows with every ticket that complies with it.

**This was deliberately not fixed.** Adding a glob to the ledger would change the
number the ledger reports for the goal *while that goal is being measured* — the
one change an evaluation ticket may not make silently. The figure is published
with its bias named instead (`SI-08-DF-11`), and SI-23 should re-read the goal
with the partition included, keeping SI-08's 121 on the record as the reading
taken before the fix.

---

## Clause 1 — "0 `recorded-local` at epic close"

### VERDICT: **MET.**

`recorded-local, filed nowhere .......... 0` — and 0 under **both** the partial
2-file read and the full 4-file read, so the result does not depend on the
defect above.

**Non-vacuity, because a zero from a renamed token would look identical.** The
detector is a live predicate on the parsed disposition
(`improvement_ledger.py:221-226`, `self.disposition == "recorded-local"`), not a
text search. Searching the four source files for the string finds exactly **one**
occurrence, in `specs/results/skill_feedback.md:1480` — and it is *prose
explaining why the status is no longer used* ("`status` is `recorded-local`
rather than `filed`… by owner direction"), not a record. The 13 baseline
`recorded-local` rows are in `specs/.history/ports-as-adapters-epic/…/manifest.json`
snapshots, which are sealed history and outside the ledger's population.

So: **13 → 0 is real**, on the population the instrument reads.

## Clause 2 — "every finding carries a `skill_change` disposition"

### VERDICT: **NOT MET.** 19 of 121 carry a parseable one; 102 do not.

| `skill_change` verb | records |
|---|---|
| **absent** | **94** |
| **malformed** (present, unparseable) | **8** |
| proposed | 10 |
| applied | 5 |
| declined | 4 |

- **94 of 121 (77.7%) carry no `skill_change` field at all.**
- **8 more carry one the reader cannot parse** — every one of them is a real
  disposition defeated by the grammar, e.g.
  `SF-102 'applied(28cf7b39) -- run_generated_case_adapters.py now carries'`.
  These are findings that *did* the right thing and still do not count. The
  grammar, not the author, is what fails here.
- The ledger's own D4 warning — skill-anchored, neither applied nor declined —
  stands at **55**.

The baseline's headline number improved (39 rows with no disposition → the
epic added 19 parseable dispositions where there were 0 in the deferred
backlogs), but the *target* is "every finding", and 102 of 121 do not carry one.

## Clause 3 — "applied, declined with a recorded reason, or not-a-skill"

### VERDICT: **NOT MET**, and the shortfall is concentrated in one place.

Only **9** records (5 applied + 4 declined) reach a terminal disposition. **10**
are `proposed` — which the improvement card is explicit is *not* a disposition:
a proposal routed to a successor is "the record of a disposition being owed".
The largest disposition bucket in the whole population is `pending` at **45**.

---

## Summary

| clause | baseline | measured | target | verdict |
|---|---|---|---|---|
| 0 `recorded-local` | 13 | **0** | 0 | **MET** |
| every finding carries a `skill_change` | 0 in backlogs; 39 rows without | **19 of 121 parseable; 94 absent, 8 malformed** | every finding | **NOT MET** |
| applied / declined-with-reason / not-a-skill | — | **9 terminal; 10 proposed; 45 pending** | terminal for all | **NOT MET** |

**What this reading does not establish.** The ledger counts records; it does not
verify that an `applied(<sha>)` token names a commit that exists or that changed
the unit it claims. No clause above should be read as "the change was made" —
only as "the record says so".
