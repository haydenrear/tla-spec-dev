# MF-029 — per-action parameter recoverability audit

Audited against `specs/tickets/MF-029/current/TlaSpecDevCli.tla`, which is
byte-identical to `specs/current/TlaSpecDevCli.tla` and to the epic tip. **Zero
TLA+ model delta** — `git diff origin/epic/modular-fuzzing -- '*.tla' '*.cfg'`
is empty.

## Label count: fourteen actions, not thirteen

The issue and ticket both say "all thirteen labels". The module actually defines
**fourteen** parameterisable action labels, and TLC emits a **fifteenth** edge
label, `Stutter`, as a self-loop on every state (40,533 such edges in the
reduced corpus). All fifteen are audited below. This is a counting discrepancy
in the issue, not a gap in the model or the audit — the superset was audited, so
nothing is unexamined.

## The audit

| # | Action | Parameter | Mechanism | Source variable |
|---|---|---|---|---|
| 1 | `BuildSkillCli` | *(none)* | n/a — nullary | — |
| 2 | `InstallLocalCli` | *(none)* | n/a — nullary | — |
| 3 | `ScaffoldProject` | `root` | **written-through** | `spec_root'` |
| 4 | `RecordBudgets` | `root` | **guard-pinned** | `spec_root` |
| 5 | `ScaffoldWorkflow` | `root` | **guard-pinned** | `spec_root` |
| 6 | `OpenTicket` | `root` | **guard-pinned** | `spec_root` |
| 6 | `OpenTicket` | `ticket` | **except-index** | `ticket_state` |
| 7 | `UpdateTicketDesired` | `ticket` | **except-index** | `ticket_state` |
| 8 | `UpdateTicketCurrent` | `ticket` | **except-index** | `ticket_state` |
| 9 | `AnalyzeComplexity` | `root` | **guard-pinned** | `spec_root` |
| 10 | `AnalyzeCorpus` | `root` | **guard-pinned** | `spec_root` |
| 11 | `RunEffectConformance` | `root` | **guard-pinned** | `spec_root` |
| 12 | `RunKillTest` | `root` | **guard-pinned** | `spec_root` |
| 13 | `RunSpecUnitTests` | `root` | **guard-pinned** | `spec_root` |
| 13 | `RunSpecUnitTests` | `ticket` | **except-index** (conditional — see below) | `ticket_state` |
| 13 | `RunSpecUnitTests` | `override` | **UNRECOVERABLE → UNCHECKED** | — |
| 14 | `CloseTicket` | `root` | **guard-pinned** | `spec_root` |
| 14 | `CloseTicket` | `ticket` | **except-index** | `ticket_state` |
| 15 | `Stutter` | *(none)* | n/a — nullary | — |

The issue's table (five rows) was verified correct and extended to the full set.
The pattern **did** hold everywhere it could, with the two exceptions below.

## Findings

### FINDING 1 — `RunSpecUnitTests(override)` is genuinely unrecoverable

`override` is a `BOOLEAN` input that never reaches the after-state. It appears
only in the enabling condition:

```tla
/\ \/ complexity_gate = "pass"
   \/ /\ complexity_gate = "fail"
      /\ override
```

When `complexity_gate = "pass"` both values of `override` are enabled and
produce **byte-identical successor states**. The state pair therefore cannot
determine it, and no amount of generator cleverness changes that — the
information was never written down.

It is marked `UNCHECKED` and **never fabricated**. Note the partial case
honestly: when `complexity_gate = "fail"` the guard forces `override = TRUE`, so
it *is* recoverable on that subset of edges. This implementation does not exploit
that — recovering it would require the recipe builder to reason about disjunctive
guards, which is a large amount of machinery for one boolean. Under-claiming here
is the safe direction: `UNCHECKED` can only cause a check to be skipped, never to
pass falsely.

### FINDING 2 — `RunSpecUnitTests(ticket)` is recoverable only on the advancing edge

```tla
ticket_state' = IF corpus_gate' = "pass" /\ effect_conformance' = "clean"
                  THEN [ticket_state EXCEPT ![ticket] = TicketSpecUnitTestsPassed]
                  ELSE ticket_state
```

On the `ELSE` edge — a failing gate — `ticket_state` is **unchanged**, so no
index differs and the argument is not determined. The generator returns
`UNCHECKED` for those edges rather than guessing. In the reduced corpus 257,280
`RunSpecUnitTests` cases carry at least one `UNCHECKED` argument; **every one of
them is kept**. No case is dropped, filtered, or skipped for failing recovery.

### FINDING 3 — no action is entirely unrecoverable

Every action with parameters recovers at least one of them. There is no action
whose arguments are wholly unavailable.

## Which fields remain independently checkable, per action

This is the trap discipline, stated per action.

| Action | Recovered from | Fields NOT independently checkable | Fields still checkable |
|---|---|---|---|
| `ScaffoldProject` | `spec_root'` (after) | **`spec_root`** | `setup_phase`, `lastCommand`, `result`, all four gates |
| all 9 guard-pinned actions | `spec_root` (before) | *none* | **all after-state fields**, including `spec_root` |
| all 5 except-index actions | `ticket_state` diff | *which index changed* | the **value** at that index, and every other variable |
| `RunSpecUnitTests` | before + diff | *which index changed* | `corpus_gate'`, `effect_conformance'`, `lastCommand`, `result`, `ticket_state` values |

`ScaffoldProject` is the only action that sacrifices a field, and it is the one
the ticket flagged as closest to the trap. **Recovering `root` from `spec_root'`
is legitimate; then checking `spec_root'` against it is the MF-028 tautology.**
The recipe reports this in `ActionRecipe.unavailable_checks`, so a downstream
consumer cannot make that mistake silently, and
`test_only_written_through_actions_block_a_check` asserts that
`ScaffoldProject` is the *only* action in that position.

Guard-pinned recovery costs nothing: the parameter comes from the **before**
state, so every after-state field stays a genuine check.

## Negative controls — proof they actually fail

`specs/tickets/MF-029/results/negative_control_proof.txt` runs one deliberately
wrong expectation per action as a plain assertion:

```
14/14 negative controls failed as required; 0 vacuous.
```

Each prints the recovered-vs-expected diff, so the failure is visible rather
than asserted. `test_every_negative_control_actually_fails` runs the same set
under `pytest.raises(AssertionError)` in CI.

A negative control only proves a wrong *expectation* fails. To prove a wrong
*implementation* fails too, `mutation_proof.txt` mutates the recovery itself:

```
6/6 mutations caught.
```

**One of those six initially survived, and that is the most important result in
this ticket.** Mutation M6 — "guard-pinned reads the AFTER state instead of the
before state" — passed all 62 tests. It survived because `spec_root` is
`UNCHANGED` in every guard-pinned action, so before and after always agree and
no state pair the model can produce discriminates the two implementations. That
is *exactly* the MF-028 shape: a check that cannot fail, hiding behind a value
that happens to be right.

It was closed by
`test_guard_pinned_reads_the_before_state_not_the_after_state`, which feeds an
artificial pair where the two disagree and asserts the **before** value wins.
M6 is now caught. The hole was found by mutation testing, not by review — which
is the argument for keeping `mutation_proof.txt` runnable rather than treating
it as a one-off.

## Revertibility

Generator-side, as required. `--no-infer-params` restores `params={}` exactly,
`infer_params(..., recipes=None)` is inert, and a full revert is deleting
`scripts/infer_action_params.py` plus ~110 lines of wiring. Nothing in the spec
changed.
