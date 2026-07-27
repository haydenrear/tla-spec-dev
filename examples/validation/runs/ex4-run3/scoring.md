# ex4 run 3 — blind run B: author an aspect from the public surface only (aim 2)

Run date 2026-07-27, EV-02. **Blind agent run**, dispatched by the epic owner.
QA-engineer persona; never saw `PREDICTIONS.md`, the answer key, the
seeded-fault table (removed from the copy), or any epic context. Owner-scored;
the numbers below were re-derived here from the agent's preserved tree
(`scratchpad/eval-runs/runB-aspect`) against its pristine snapshot.

## Aim 2 — the measured ratio

The agent authored one Given-form aspect, `Scenario_OutcomeLedger`
(Deliver, Fail, Record), plus its manifest block.

| item | measured here | owner's count |
|---|---|---|
| `.tla` lines | 36 total / **32 non-blank** | 36 |
| `.cfg` lines | 6 | 6 |
| manifest block | **18** | 18 |
| **authored total** | **56 non-blank / 60 raw** | **60** |
| **cases generated** | **38** over 3 actions, from 24 states | 38 |
| toolchain-generated lines from those 60 | 1,162 | 1,162 |
| `case_modules.py validate` / `coverage` | exit 0 / exit 0 | ✓ |

**A2-P1 PASS** (EV-01's two aspects reproduce exactly — 14 lines → 50 cases, 22
lines → 6 cases, view 330; measured independently in `../ex4-run1/scoring.md`).
**A2-P3 PASS, and now from the outside**: an aspect written by someone who had
never seen the fixture generates and runs against the same `actions.yml`, the
same adapters and the same providers, with no adapter change.

**A2-P2 honoured.** The honest ratio for run B is **0.63 cases per authored
line** (38 / 60) — a Given, and Givens divide. Quoting the slice's 3.6 alone,
here or in EV-01, would sell the mechanism.

### The result that exceeds the prediction

**38 Given-form cases killed EXACTLY what the 330-case whole-view corpus killed**
on the agent's own 12-mutant catalog. An **8.7× reduction with zero measured
loss of kill power.** No prediction anticipated this; A2-P2 only claimed the
Given "divides, and dividing is what it is for." It divides *and holds*, at
least on this model and this catalog. **Scored: BEAT the prediction**, with the
bound stated — one model, one catalog of 12, authored by the same agent that
authored the aspect.

## Aim 1, unplanned — the agent's own 12-mutant catalog

| class | mutants | slice (38) | view (330) | hand-written pytest |
|---|---|---|---|---|
| wrong write on an enabled transition | M5–M8, M10 | **5 killed** | 5 killed | 4 killed (**M10 MISSED**) |
| guard relaxation | M1–M3 | 0 | 0 | **3 killed** |
| ordering / sequence | M9, M11, M12 | 0 | 0 | 0 |
| equivalent mutant | M4 | n/a | n/a | n/a |

Honest denominator: **5 of 11 non-equivalent**, or **5 of the 8 the model can
even express**. Three mechanism-attributed conclusions, all of which corroborate
EV-02's own measurements from a different direction:

1. **The corpus and the hand-written suite are COMPLEMENTS; neither subsumes the
   other.** M10 (durable ledger persists only the last entry) is killed by the
   corpus and missed by every hand-written test, because `tests/` never binds
   the `LedgerStorePort` boundary. M1–M3 are the reverse. **Never report these
   as a single kill rate** — the same discipline DP-8 imposes on ARM A vs ARM B.
   M10 is the independent replication of this ticket's F3/F5 result: the durable
   side is invisible to everything that does not bind the port.
2. **Guard relaxation is invisible by construction.** A generated corpus replays
   only ENABLED edges, so it contains no rejected inputs: a service that accepts
   what the model forbids passes every case. Compounded by the adapter
   recovering the action argument from the case's AFTER-state, so it only ever
   calls with the argument that was going to succeed. **This is EV-01-DF-01
   confirmed independently, from the outside, by an agent who had never seen
   it** — and it converts DF-01 from a caveat about the fixture into a
   structural statement about generated corpora. It is the reason ARM A's 4/6
   is an upper bound (`../ex4-run1/scoring.md`).
3. **Ordering is invisible at every layer.** `ledger` and `queue` are TLA+
   **sets**; the code implements them as ordered lists documented "append-only"
   and "in insertion order". The projector sorts, the adapter uses `frozenset`,
   the provider compares `sorted()`. A ledger that silently reverses is
   undetectable by any of the three. **Modeling gap, not a tool bug — and no
   case module can fix it.**

## The single most important finding of the epic

Working from the **README alone**, the agent found that **the public surface is
false of the model**. Verified here directly in `Pipeline.tla`:

```
Fail(i)   ==  i \in delivered  /\  delivered' = delivered \ {i}  /\  failed' = failed \cup {i}
Record(i) ==  i \in delivered  /\  i \notin ledger  /\  ledger' = ledger \cup {i}
```

Once an item fails it leaves `delivered`, so `Record(i)` can never again be
enabled for it: **a failed item can never reach the ledger.** The public README
promises the opposite, in two places — *"a failed item is recorded as failed"*
and *"the ledger records each outcome"* (both verified in the run's pristine
snapshot). The model's own invariant `LedgerIsDownstream == ledger \subseteq
(delivered \cup failed)` reserves room for exactly the behavior the model then
makes unreachable.

**No case module could ever catch this.** A case module may not add an action,
and there is no action to enter; a corpus can only test behavior the model has.
**The value came from the human-facing act of authoring the aspect, not from the
cases it generated.**

This is the one result in EV-02 that no prediction contains and no metric in the
epic measures. It is an argument for the manual-test-starter path **whose
strength is not expressible as a kill rate**, and it belongs in `NEXT-EPIC.md`
on its own line.

## Aim 2's real limit — A2-P4 scored, and it is sharper than predicted

A2-P4 predicted that an agent asked to decompose `ex4` without an author would
produce a plausible aspect list anyway rather than the correct output. **PASS**,
and the run supplies the mechanism the prediction lacked:

- A **slice** is writable from action names alone: README + `actions.yml`.
- A **Given** must constrain **every** variable of the view, which forced
  knowledge of all six internal state variables and each action's guard. The
  README names none of them.

**So "a non-author can write an aspect" holds for slices and FAILS for Givens.**
Neither `references/case_modules.md` nor `aspect_decomposition.md` states this.
The mechanism with the best measured ratio (the Given, 8.7× with no loss) is
precisely the one that cannot be written from outside. **EV-02-DF-04, filed.**

**Step 0 is unenforceable** (predicted, confirmed): the prompt requires the
aspect list to come from the model author and never be derived. Nothing stopped
the agent producing a complete, schema-valid, coverage-clean decomposition with
no author in the loop; the `Source` column is free text and is never checked.
The agent flagged its own violation — the best available outcome, and not a
control. **EV-02-DF-04, filed.**

## Doc/tooling friction — 8 items, all reproducible (X-P3 scored FAIL)

Recorded from the agent's report. Item 2 was **independently reproduced in this
worktree** (`../ex4-run1/artifacts/inplace.log`, TLC exit 150).

1. `aspect_decomposition.md` Step 1's command does not run as written
   (`--spec-root` ignored for the positional path); its `jq` pipeline assumes
   JSON-only stdout.
2. **A case module cannot generate from where the docs put it.** TLC runs with
   cwd = the `.tla`'s directory and no module search path, so a module in
   `specs/case_modules/` cannot `EXTENDS` a view in `specs/program_model/`. The
   checked-in module is **not reproducible in place**; the failure is a 30-line
   TLC `AbortException` preceded by a misleading fail-closed paragraph.
   **The sharpest of the eight** — the shipped convention and the shipped tool
   disagree. (= EV-02-DF-02.)
3. `--out` resolves against the `.tla`'s directory, not cwd — undocumented.
4. **Every documented command path assumes an external view** (`--view
   external`, `testgraph/`, `testgraph_bindings.yml`). An internal-only project
   has no worked example anywhere.
5. `run_generated_case_adapters.py` needs two `--import-root` flags; the error
   names one.
6. Interpreter roulette: no `python3` on PATH has both `yaml` (toolchain) and
   `pytest` (README); neither doc states an environment requirement.
   (Independently hit here — EV-02-DF-05.)
7. `param_recovery_audit.md` says "every parameter is recoverable" while the
   same run reports **0 of 38** cases carrying arguments. **The audit
   contradicts the corpus it audits**, and it is the audit for EV-01-DF-01.
   **EV-02-DF-03, filed.**
8. Nothing in the repo was modified by the run (owner-verified clean).

**X-P3 FAILS on this run.** Six of the eight items are cases where the docs were
insufficient and the agent had to read behavior or source to proceed. **X-P1 and
X-P2 PASS** — no PATH wrapper, nothing fixed inline.

## Protocol finding

The agent's 12-mutant catalog is **not re-derivable from the preserved tree**:
mutants were applied in place and restored, and no catalog file survives. Aim 1
numbers from a blind run should ship the catalog as an artifact the way
`seeded_faults.toml` does, or they cannot be re-scored. **EV-02-PROTO-02, filed.**

## Artifacts

`artifacts/BLIND-RUN-B-RESULT.md` (the owner's scored report). The agent's tree
and its pristine snapshot are the owner's, at `scratchpad/eval-runs/runB-aspect`
and `scratchpad/runB-pristine`; neither was modified.
