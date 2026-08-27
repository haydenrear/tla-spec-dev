# Friction ledger — what actually cost an agent time, measured on a real run

**Round 0 is not a designed round. It is a transcript.** On 2026-08-26/27 an
agent drove this toolchain end to end — scaffold, open, generate, close ticket,
close workflow — to verify four defect fixes. Every row below is friction that
agent actually hit, in order, with what it had to do to get past it.

**Why this is the right seed for a designed round.** A task set written by
someone who already knows the answers tests the wrong thing (`MF-020`). These
rows were produced by an agent that did NOT know the answers, doing real work,
before any round existed. **They are the only rows in this file whose difficulty
was not chosen.**

**Every row carries what a fix would cost, declared BEFORE anyone tries it** —
`references/bug_attribution.md` §7. A row with no price is a complaint.

---

## The rule for reading this

**`channel: operator-doing-the-work` on every row, class `hand`.** Nothing
standing reported any of it. That is the finding: **the toolchain's refusals are
correct and its ORDERING is not**, and no test can see ordering because every
test supplies a correct input on the first try.

---

## F-01 — Three sequential refusals to close one ticket, each revealing one problem

**Cost: 3 round trips, ~4 minutes, and the agent nearly concluded the close was broken.**

```
close ticket TK-01  ->  REJECTED -- no `narrative:` recorded
close ticket TK-01  ->  REJECTED -- no recursive refinement record. Set `refinement.searched: true`
close ticket TK-01  ->  REJECTED -- refinement record has no outcome. Set `refinement.outcome`
```

**All three are the same file, `complexity_ledger.yaml`, and all three were
knowable on the first read.** The gate validates, stops at the first failure,
and returns. An agent pays one full edit-and-retry cycle per clause.

- **region:** `scripts/complexity_ledger.py`, the close-out gate
- **what a fix costs, declared before:** report EVERY unsatisfied clause in one
  pass instead of the first. Roughly a loop and an accumulator in the verdict
  builder; ~20 lines; no change to what is required, only to how many trips it
  takes to learn it. **Risk: none identified — the clauses are already evaluated
  independently.**

## F-02 — `close ticket` refuses on plan status with no way to discover the required value

**Cost: 1 round trip + a grep of the source.**

```
ERROR: ticket TK-01 is not closed in ticket_plan.yaml: status=next
```

`next` is what `scaffold workflow` WROTE. The gate does not say which values it
accepts, and the accepted set (`accepted|closed|complete|completed|done`) is in
`spec_evolution.py`, not in the message.

- **region:** the close gate's status check
- **price:** name the accepted values in the error. One f-string. **~2 lines.**

## F-03 — The workflow close needs a file `open ticket` does not scaffold

**Cost: 1 round trip, then a hunt for a template.**

```
ERROR: complexity ledger input not found: specs/results/complexity_ledger_input.yaml
The standing objective is mechanized as a required close-out step.
`open ticket` scaffolds this file; fill it in before closing.
```

**The message says `open ticket` scaffolds it. `open ticket` scaffolds the
per-TICKET ledger, not the per-WORKFLOW one.** The agent copied a ticket ledger
over as a guess and it worked — which means the file was obtainable, and the
message pointed at the wrong producer.

- **region:** workflow close; the message and/or the scaffolder
- **price:** either scaffold the workflow-level file at `scaffold workflow`
  (~5 lines, and it changes what a fresh tree contains — declare it), or correct
  the message to name the real producer (~1 line). **The second is cheaper and
  the first is more useful; they are not the same fix and should not be
  conflated.**

## F-04 — `close workflow` is not a CLI verb

**Cost: 1 round trip.**

```
tla-spec-dev close workflow  ->  invalid choice: 'workflow' (choose from 'ticket')
```

`references/workflows.md` documents the workflow close as
`python scripts/close_tickets.py`. The CLI offers `close ticket` and nothing
else, so an agent that learned `close ticket` reasonably tries `close workflow`.

- **region:** the `close` subparser
- **price:** either add the verb as a thin wrapper (~15 lines) or make the
  error name `scripts/close_tickets.py` (~1 line). **Declare which; the wrapper
  changes the CLI's surface and the message does not.**

## F-05 — A relative `--out` resolves against the SPEC directory, not the cwd

**Cost: 0 round trips — but only because the tool PRINTS the resolution.**

```
--out specs/generated/manual  ->  <repo>/specs/program_model/specs/generated/manual
```

**This one is a positive result and belongs in the ledger as one.** The
behaviour is surprising and the tool says so, unprompted, every time. The agent
noticed the doubled `specs/` immediately because the resolution was printed.

- **region:** `report_out_resolution`
- **price of changing it: DO NOT.** Recorded here so a later round does not
  "fix" a message that is doing its job. This is the shape the other four rows
  are missing.

## F-06 — `generate cases` silently declares nothing without `--actions-metadata`

**Cost: one full generate run producing a coverage record with
`declared_view_actions: []`, and the agent initially concluded its own change
had not worked.**

The zero-case check added in #300 is inert unless `--actions-metadata` is
passed. Nothing says so. `actions.yml` sits beside the `.tla` and is not picked
up by default.

- **region:** `generate cases` argument handling
- **price:** default `--actions-metadata` to `<spec dir>/actions.yml` when it
  exists, and PRINT which file was used or that none was found. ~6 lines.
  **Risk: a project with an actions.yml it did not intend to apply would start
  applying it — so the print is not optional, it is the safety.**

## F-07 — `analyze complexity` reports a missing file without saying what IS there

**Cost: 1 round trip.**

```
ERROR: config not found: specs/program_model/MC.cfg
```

The directory contains `Internal.cfg` and `External.cfg`. The agent guessed the
name from the scaffold's docs.

- **region:** `analyze complexity` input resolution
- **price:** list the `.cfg` files beside the `.tla` when the named one is
  absent. ~4 lines.

---

## What this ledger is NOT

**It is not a bug list.** Every refusal above is CORRECT: the gate should
refuse, the file should be required, the path should resolve where it does.
**What is measured is the number of round trips an agent pays to learn a thing
the tool already knew.**

**And it is not yet a measurement.** Round 0 is `n=1`, one agent, no control,
and that agent had read this repository's source for hours before it started —
so it is the FRIENDLIEST possible case and the costs above are **lower bounds**.
A designed round with an agent that has not read the source is the measurement;
this is the seed that says what to measure.
