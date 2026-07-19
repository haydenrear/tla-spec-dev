# MF-019 complexity ledger and retention evidence

Recorded **jointly**, per the standing objective in
`references/architecture_tractability.md`. This ticket mechanizes that
objective, so this ledger is unusual: it was produced **by the mechanism it
ships**, and the mechanized report is the sealed artifact at
`results/complexity-ledger-report.txt`. Whether that worked is recorded in §6.

## 1. Model complexity delta: ZERO, measured

| Metric | Before (epic tip `cb136f3`) | After MF-019 | Delta |
|---|---|---|---|
| State variables | 9 | 9 | 0 |
| Actions | 14 | 14 | 0 |
| Declared state-space bound | 699,840 | 699,840 | 0 |
| TLC distinct states | 231,621 | 231,621 | 0 |
| TLC states generated | 5,619,356 | 5,619,356 | 0 |
| Search depth | 25 | 25 | 0 |
| `max_distinct_states` usage | 46.3% of 500,000 | 46.3% | 0 pp |
| `max_state_space_bound` usage | 70.0% of 1,000,000 | 70.0% | 0 pp |

Measured, not asserted: `results/tlc-baseline.txt` (taken at branch time) and
`results/tlc-current.txt` (taken after implementation) are byte-identical in
their state counts.

### Why no `TrackComplexity` action / `complexity_ledger` variable was added

The plan entry prescribes `desired_actions: [TrackComplexity]` and
`current_increment.model_state: [complexity_ledger]`. Both are **withdrawn and
not implemented**. Two independent reasons, the first of which is a hard gate.

**Reason 1 — the static bound gate forbids it. Measured before any code was
written, as the brief required.**

`max_state_space_bound` is 1,000,000 and the model's declared bound is 699,840.
That is **1.43x of headroom**. The bound is a product of the bounded dimensions,
so adding *any* new bounded variable multiplies it by that variable's
cardinality:

| New variable cardinality | Resulting bound | Verdict |
|---|---|---|
| 2 (a boolean) | 1,399,680 | **BREACH** |
| 3 (`unknown`/`recorded`/`rejected`) | 2,099,520 | **BREACH** |
| 5 | 3,499,200 | **BREACH** |

Even a single boolean breaches. There is no cardinality at which the prescribed
`complexity_ledger` variable fits. Per governing rule 5 the cap is a hard gate,
and per rule 1 the response to a bad measurement is to change the architecture,
not the measurement — so the budget was **not** renegotiated and
`--allow-over-budget` was **not** used.

**This is the headroom finding this ticket owes the epic, and it is not the one
the brief anticipated.** The brief framed headroom in terms of
`max_distinct_states` (46.3% used, ~2.2x left). The binding constraint is
actually `max_state_space_bound` at **70.0% used, 1.43x left**. The next ticket
that wants a new state variable of any kind cannot have one. The root cause is
the same undecomposed single-module baseline that produces the C1 finding, and
the resolution is the same: **MF-023's Internal/External decomposition**, which
gives each component its own much smaller declared space.

**Reason 2 — the gate's decisive input is not state-machine state.**

The anti-gaming rule fires on a *conjunction*: a complexity **decrease** AND
degraded retention. The retention half is already modeled (`kill_test`,
`effect_conformance`, `corpus_gate`). The delta-direction half is a comparison
between this close's metrics and the **previous ledger entry** — history, not
current state. Representing it would mean carrying the previous entry's
complexity in the state machine, which is the variable reason 1 forbids.

Direct precedent, accepted at post-merge review: **MF-017** (same close path,
same stale-plan-field situation, tracked as issue #33) and **MF-021**. And the
governing precedent for *not* doing it anyway is in this model's own comments —
MF-016 declined to model the promotion interlock because "the shipped `close
ticket` does not yet enforce it... Writing the guard into the model anyway would
make the model assert a behavior the program does not have."

**Note the honest asymmetry, because it cuts against this ticket.** Unlike
MF-017, MF-019 *does* add a real refusal to `close ticket`: the CLI genuinely
exits non-zero when the ledger gate fails, which is externally visible behavior
of the modeled command. By the MF-011 standard ("a hard gate that is not
represented is not a gate") that behavior *should* appear in the model. It does
not, and the reason is a budget breach rather than a judgment that it is
unmodelable. **That is a gap, recorded as a gap.** It is handed to MF-023 in
`results/DEFERRED-TO-MF-023.md`, and it should be modeled once decomposition
makes room.

## 2. Retention evidence (joint requirement)

| Constraint | Evidence | Result |
|---|---|---|
| TLC, ticket-local current | `results/tlc-current.txt` | No error; 231,621 distinct, depth 25 |
| Repository unit tests | `results/repository-unit-tests.txt` | **415 passed** (370 baseline + 45) |
| Spec-unit tests (MF-019) | `results/spec-unit-tests.txt` | 2 targets, 48 + 45 passed |
| Test Graph `specWorkflow` | `results/testgraph-specWorkflow.txt` | BUILD SUCCESSFUL, 8/8 nodes |
| Test Graph `cliWorkflow` | `results/testgraph-cliWorkflow.txt` | BUILD SUCCESSFUL, 2/2 nodes |
| `analyze complexity` | `results/analyze-complexity.txt` | exit 1 — live C1 finding, unchanged |
| Kill rate | — | **DEFERRED to MF-023** (epic-wide policy) |
| Effect conformance | — | **DEFERRED to MF-023** (epic-wide policy) |
| External coverage | — | **DEFERRED to MF-023** (epic-wide policy) |

The +45 repository tests are 41 new ledger tests plus 4 additional
parameterizations of the existing `test_spec_yaml_valid.py`, which enumerates
YAML files and now sees the scaffolded ledger inputs. Fully accounted for:
370 + 41 + 4 = 415. No pre-existing test was
deleted, skipped, or relaxed.

**The three deferred members are recorded as `deferred`, not as `pass`.** This
matters and it is not a formality: writing `pass` there would have been
fabricating retention evidence in the very mechanism built to refuse fabricated
retention evidence. Because this ticket's delta is **zero**, the anti-gaming
gate does not fire — it gates *reductions*, and no reduction is claimed. Had
this ticket claimed a reduction on this evidence, its own gate would have
refused the close. That asymmetry is the design working.

## 3. Refinement search: searched, found none NEW

Searched. No new reduction found. The standing candidates were re-read and are
deliberately **not re-litigated**:

- **Project `lastCommand` / `result`** — the tool's own `SUGGESTED MOVE:
  ABSTRACT`. Recorded by MF-011 as requiring the kill rate to hold afterwards,
  and MF-016 built that check. `PROJECTED`/`UNVERIFIED`; the runs are MF-023's.
- **Collapse `kill_test` 4 -> 3** — MF-016 **measured** 26.2% and **refused** it,
  proving all four values individually TLC-reachable.
- **Collapse the three failure verdicts** — MF-027 **measured** 47% and
  **refused** it, because it deletes externally-visible `result.next`
  distinctions.
- **Further `ticket_state` collapse** — MF-025 searched and found none; all six
  ordinals are individually reachable.

Re-taking any of these would contradict a prior ticket's recorded refusal on
evidence I did not re-measure. Per the MF-020 lesson, **no projected reduction
is claimed anywhere in this ledger.**

Surfaces new to this ticket were searched for duplication and none was found
worth removing: the red-flag detector is **delegated to MF-011's
`compare_tlc_reports`** rather than reimplemented, and the YAML subset parser is
**reused from `extract_spec_manifest`** rather than added as a dependency. Both
are reductions in the sense that matters — code that was not written.

## 4. Complexity added by this ticket, stated honestly

In the MF-021 style, because the model delta is zero and the real cost is
elsewhere:

- `scripts/complexity_ledger.py`: ~600 lines, new.
- `scripts/spec_evolution.py`: +~110 lines (the gate, at both close paths).
- `scripts/new_ticket_workflow.py`: +~7 lines (scaffold the input template).
- `tests/test_complexity_ledger.py`: 41 tests, new.
- `tests/conftest.py`: new, ~60 lines.
- Spec-unit adapter + test: 1 adapter, 4 conformance tests.
- Model: **zero**.

The justification is that this is the epic's enforcement instrument for its own
premise. Eleven tickets recorded this by hand and the record drifted while they
did: filenames diverged (`complexity-ledger.md`, `complexity_delta.md`,
`complexity-delta.md`), and **MF-016 wrote no ledger file at all** — its delta,
its retention evidence and its refused 26.2% reduction live inside
`DEFERRED-TO-MF-023.md`. A standing objective that depends on everyone
remembering to write a file is a stance, not an objective.

## 5. Does the mechanized format reproduce the eleven manual ledgers?

**Partly, and the shortfall is deliberate.** Tested directly in
`tests/test_complexity_ledger.py::TestReproducesTheElevenManualLedgers`, which
replays all eleven with their recorded figures.

**Reproduced:** every delta direction (6 increases, 3 decreases, 3 zeros — some
tickets appear in more than one class across their sub-parts); every gate
verdict, i.e. each of the six increases is refused without its justification and
each of the three decreases is refused under degraded retention; and MF-020's
correction, whose generated-states delta is 0 rather than the withdrawn -13.1%.

**NOT reproduced by the machine-checked core, by design:** per-part attribution
of one delta to two independent changes (MF-022); per-value TLC reachability
proofs (MF-016); outdegree distribution and bound density (MF-025); complexity
measured in lines of code and persisted fields (MF-021); negotiated-budget
provenance and cross-tree propagation (MF-027); a missed-target root cause that
retro-corrects a prior ledger (MF-020); a domain-cardinality justification tied
to specific `result.next` strings (MF-013).

These ride in the **required narrative**, verbatim and unparsed. A schema tight
enough to validate all of them would have to be loose enough to mean nothing —
so the core is narrow, the narrative is mandatory, and the format was not
trimmed to fit the mechanism.

**One thing the manual record could not do that the mechanism now does:** the
eleven ledgers do not form a chain. They key their baselines variously to a git
SHA (MF-015), a tree path (MF-027), a ticket id, and in one case to a ticket
that promoted *later* (MF-014 cites an "MF-017 tip"). The mechanized ledger
derives the previous entry from the append-only record instead of citing one, so
the chain cannot drift.

## 6. Did the mechanism work on its own ticket?

**Yes, and it caught a real defect in itself.**

This ledger's figures and gate verdict were produced by
`close ticket` running the shipped gate; the sealed report is
`results/complexity-ledger-report.txt` and the input is
`results/complexity_ledger.yaml`.

Two defects the mechanism surfaced during its own construction, both fixed:

1. **The ledger could not be read back without PyYAML.** The spec-unit runner
   invokes pytest without `pyyaml`, so the first close wrote the ledger as JSON
   and the second close tried to parse it with the YAML subset parser and
   crashed. Found by the spec-unit adapters, not by reasoning. Fixed by
   separating the two concerns: the human-written *input* is YAML (read via
   PyYAML or the repository's existing subset parser), the machine-written
   *ledger* is JSON.

2. **The close recommended a commit that omitted the ledger.** `git add` listed
   the history entry, promoted current and skill feedback, but not
   `specs/results/complexity_ledger.json` — so the recorded delta would have
   been left uncommitted. Found by the `specWorkflow` graph's clean-tree
   assertion. An append-only record that is not committed is not a record.

## 7. Interaction with MF-017, checked as instructed

MF-017's skill-feedback emission and this ticket's ledger both hang off the same
close path. They compose without interference: the ledger gate runs **before**
the history entry is created and before promotion, so a refused close mutates
nothing, while feedback emission stays after promotion where it was. Both
records land in the same history manifest (`complexity_ledger` alongside
`skill_feedback`) and both paths join the same commit recommendation. The three
MF-017 skill-feedback tests and the MF-017 spec-unit adapter pass unchanged
apart from supplying a ledger input.

## 8. Live findings — NOT worked around

- `C1 is touched by 14 actions, exceeding max_component_actions 8`. Unchanged by
  this ticket, still failing, resolved at the root by MF-023. No renegotiation,
  no override, no `--allow-over-budget`.
- `max_state_space_bound` at 70.0% with 1.43x headroom (§1). New finding,
  reported rather than accommodated.

## 9. Negotiated budget

`max_distinct_states: 500000`, negotiated 2026-07-19 from the documented default
50000, with its derivation recorded as comments in `spec_manifest.yaml`. The
value **and all of its rationale comments** were carried through
`specs/tickets/MF-019/desired`, `specs/tickets/MF-019/current`, and verified
present in `specs/current` **after** promotion — the SF-003 blind spot (#32).
Verification: `results/budget-retention.txt`.

## 10. Validations deferred to MF-023

Per the epic-wide deferral, this ticket did **not** run: case generation over
the reachable state graph, the distilled-corpus run, the effect-conformance
sweep, or the mutation kill test. Consequently the three retention constraints
this ticket's own gate consumes are recorded as `deferred` rather than measured.
MF-023 must exercise them, and specifically must re-run this ticket's gate with
**real** retention verdicts — including checking that a `process.spawn` target
reporting `unobservable` is refused rather than read as `clean`. See
`results/DEFERRED-TO-MF-023.md`.
