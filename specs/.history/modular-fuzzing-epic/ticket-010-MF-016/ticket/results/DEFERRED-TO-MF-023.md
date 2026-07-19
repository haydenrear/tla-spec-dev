# MF-016 — what MF-023 must actually run

MF-016 ships **mechanism with its empirical proof deferred**. That is the
expected outcome under the epic-wide spec-case-execution deferral (owner
direction 2026-07-18), and it is stated plainly here rather than papered over.

This ticket is the one whose value is inherently empirical: a kill test that has
never run against a real corpus has not yet falsified anything. Everything below
is what remains.

---

## 1. What IS proved, and by what

| Claim | Proved by | Status |
|---|---|---|
| Coverage is derived from the declarations every run | `tests/test_kill_test.py::TestCoverageIsComputedFromTheDeclarations` (5 tests) | proved |
| A new port/invariant breaks the kill test until seeded | same class, 2 tests | proved |
| Below floor fails, exit 1, no waiver | `TestTheFloorGateFailsBelowFloorWithNoWaiver` (6), `TestNothingWaivesTheFloor` (4) | proved |
| A partial catalog computes NO rate, exit 2 | `TestAPartialExperimentIsRefusedRatherThanScored` (4) | proved |
| A red control refuses instead of scoring | `TestTheControlRun` (6) | proved |
| A survivor names the variable and action to refine | `TestASurvivorPointsAtWhatToRefine` (4) | proved |
| Seeding restores the tree, even on exception | `TestSeedingIsSafe` (5) | proved |
| Abstraction validation refuses a dropped rate | `TestKillRatePreservingAbstraction` (5) | proved |
| Scoping narrows the obligation, never the measurement | `TestPerComponentScoping` (5) | proved |
| This repo's 19 boundaries all carry a live, non-stale mutant | `TestThisRepositorysCatalogCoversItsOwnBoundaries` (7) | proved |
| The CLI end-to-end: gate, refusal, waiver-inertness, evidence | `specs/current/tests/test_tla_spec_dev_kill_test_adapter.py` (13) | proved |
| A real kill test runs end-to-end over a real corpus | worked example, `example-kill-test-report.json` | **proved once, on the example** |

**NOT proved: this repository's own kill rate.** No mutant in
`specs/current/kill_mutants.toml` has ever been run against this repository's
distilled corpus, because case generation over the reachable state graph is
deferred. The 19 mutants are verified to apply, to be behavioral rather than
syntactic, and to restore cleanly — but whether the corpus *kills* them is
exactly the open empirical question.

---

## 2. Exactly what MF-023 must run

### 2.1 The toolchain's own kill test — the primary deliverable

After MF-023 performs the Internal/External decomposition and case generation
is unblocked:

```bash
# Per component, because a kill test measures one component's representation
# with that component's corpus. Omitting --cfg is the strict default and
# requires every invariant in the spec directory.
python3 scripts/run_kill_test.py \
  --target specs/current \
  --cfg Internal.cfg \
  --corpus-command "python3 scripts/run_generated_case_adapters.py \
      <generated>/spec-unit/tlaspecdevcli_program_cases \
      --mapping specs/current/case_adapters.toml --view internal --batch \
      --import-root specs/current" \
  --out specs/tickets/MF-023/results/kill-test-internal.json

python3 scripts/run_kill_test.py \
  --target specs/current --cfg External.cfg \
  --corpus-command "<the external corpus command>" \
  --out specs/tickets/MF-023/results/kill-test-external.json
```

**Expected outcomes MF-023 must not assume away:**

- The **control run comes first**. If the corpus is not green on the unmutated
  program, the kill test refuses (exit 2) and no rate is produced. Fix the
  corpus before reading any number. See §3.
- Some of the 19 mutants will very likely **survive**. That is the mechanism
  working, not a defect in it. Each survivor's report entry names the exact
  model variable and action to refine.
- Do **not** lower `kill_rate_floor`, waive a survivor, or delete a mutant to
  reach the floor. Refine the representation until the mutant dies. There is no
  flag for any of the alternatives, by design.
- After the Internal/External split, `required_boundaries` will pick up **both**
  new configs automatically and the catalog will go incomplete until faults are
  seeded for any new invariants. That refusal is expected; seed the mutants.

### 2.2 The blocking constraint MF-023 must resolve first

**The kill test cannot run inside the effect sandbox in this repository.**

`subprocess_case_runner` spawns a child process per mutant. Under the MF-027
effect oracle every observed `process.spawn` is `unobservable` *even when a
declared port matches it*, and this repository declares two such ports
(`tlc_process` → `*java*`, `test_process` → `*pytest*`). A kill-test run driven
inside the sandbox therefore produces `unobservable`, not `clean`, and the two
oracles deadlock: the effect oracle correctly refuses the very spawns the kill
test needs.

This is recorded as a finding, **not as something to relax**. Neither oracle
should be weakened. MF-023 must decide the resolution; the options visible from
here are:

1. Run the kill test strictly outside the effect sandbox (what
   `run_kill_test.py` does today, and what the note in every generated report
   says). Simplest, and the current behavior.
2. Give the kill test an in-process corpus runner so no spawn occurs. Removes
   the deadlock at the root but requires the corpus to be importable rather
   than executable.
3. Decide that `process.spawn` observability is a real capability gap and
   extend the sandbox to see through it — a much larger change, and the only
   one that would let both oracles run in one pass.

### 2.3 The worked example's three real survivors

The example kill test **did** run end-to-end. Its result is in
`example-kill-test-report.json`: **kill rate 0.571 (4/7)** against the 0.8
floor, control green, verdict `below_floor`. Three genuine survivors, each a
true finding about the example's representation:

| Mutant | Refine | Why it survived |
|---|---|---|
| `store-projection_store` | `projections` / `ProjectOrder` | No generated case distinguishes the projected status, so the read model's advance is unmodeled |
| `inv-InternalInvariant` | `orders` / `Checkout` | No generated case checks out against a nonexistent account, so referential integrity is unexercised |
| `inv-Invariant` | `responses` / `SubmitCreateAccount` | The HTTP boundary is genuinely outside the in-process internal corpus; the external corpus must cover it |

MF-023 must refine the example's internal model until the first two die, and
run the external corpus to kill the third. The floor was **not** lowered to make
this pass, and `validate_kill_test()` in
`examples/run_distributed_history_validation.py` asserts the strict outcome, so
it will keep failing until the representation is actually refined.

### 2.4 Pre-existing blockers, unrelated to this ticket

- `python3 examples/run_distributed_history_validation.py --mode local`
  **cannot complete today**, and could not before this ticket either. Case
  generation for the example's **External** model is refused by the complexity
  gate: `component C2 is touched by 9 actions, exceeding max_component_actions
  8`. Verified pre-existing by re-running with this ticket's manifest removed.
  Same class as the toolchain's own live C1 finding. Not worked around; no
  `--allow-over-budget` was used.
- The toolchain's own live finding is now **`C1 is touched by 14 actions`**
  (was 13). `RunKillTest` is the 14th. This is the same TRUE finding about the
  undecomposed single-module baseline that MF-023 resolves at the root. No
  budget was renegotiated.

---

## 3. The defect this ticket found in its own first draft

Recorded because it is the most valuable thing the ticket learned, and because
a future change could reintroduce it.

The first end-to-end run of the worked example scored a **perfect 7/7, kill rate
1.000, PASS**. It was entirely spurious. The corpus command was already failing
on an unrelated effect-oracle `dead_surface` finding *before any mutant was
seeded*, and since "killed" is operationalized as "the corpus run failed", every
single mutant was recorded as killed by that one pre-existing failure.

A kill test without a control run reports its most flattering possible number
exactly when the corpus is most broken. `control_run()` and the
`control_failed` verdict exist because of this. It dominates every other
verdict, computes no rate, seeds no mutants, and has no skip flag.

The dead_surface finding itself was also real: the example manifest I first
wrote declared five `filesystem.write` ports that `EcommerceStore` never
crosses (it runs on in-memory sqlite). Per governing rule 4 the declarations
were removed rather than the finding suppressed — a port the program never
crosses is not a richer model, it is a wrong one.

---

## 4. Complexity delta, with retention evidence

| Figure | Before (epic tip `eda233d`) | After MF-016 | Delta |
|---|---|---|---|
| Variables | 8 | 9 | +1 (`kill_test`) |
| Declared bound | 174,960 | 699,840 | ×4 |
| TLC generated | 1,067,828 | 5,619,356 | ×5.26 |
| TLC distinct | 49,875 | 231,621 | ×4.64 |
| TLC depth | 24 | 25 | +1 |
| `max_distinct_states` usage | 10.0% | **46.3%** of 500,000 | +36.3pp |
| `max_state_space_bound` usage | 17.5% | 70.0% of 1,000,000 | +52.5pp |
| Repository unit tests | 315 | 373 | +58 |

Both caps still pass, but this is a **large** consumption — considerably more
than the "affordable" framing suggested, and the honest figure is reported
rather than the estimate. The negotiated budget's own note already says to
revisit `max_distinct_states` at MF-023, when decomposition gives each component
a much smaller state space; that revisit now matters more.

### Refinement search — searched, found a reduction, REFUSED it

Measured, not estimated. Collapsing `kill_test` from 4 values to 3
(`{"unknown", "pass", "fail"}`, merging `below_floor` and
`incomplete_catalog`):

- distinct states **231,621 → 171,039** — a real **26.2% reduction**
- generated **5,619,356 → 3,981,016**, depth unchanged at 25

**Refused**, on the standard MF-027 set when it refused its own measured 47%
reduction: the collapse deletes an externally-visible distinction. The two
verdicts have different remedies (`below_floor` → refine the model at the
surviving mutant's named variable; `incomplete_catalog` → seed a fault for the
uncovered boundary) and select different `result.next` strings, so merging them
would make the model blind to a real outcome of a modeled command.

**Retention evidence** (this is the part that makes the refusal checkable, not
merely asserted): each of the three non-`"unknown"` verdicts was confirmed
**individually reachable** by TLC, by adding `kill_test /= "<value>"` as an
invariant and observing the violation:

```
kill_test = "pass"                REACHABLE
kill_test = "below_floor"         REACHABLE
kill_test = "incomplete_catalog"  REACHABLE
```

The 4-value domain therefore represents the reachable set exactly — no dead
values padding the bound, and no reachable state the collapse would have
preserved. A cheaper representation exists; it is not a re-representation.

**Architectural recommendation, requiring owner approval, not applied:**
`analyze complexity` now reports that no configured invariant reads
`[lastCommand, result]` and suggests projecting them out. Notably the tool's own
output says this is "legitimate IFF the mutation kill rate holds afterwards
(tickets/016)" — this ticket built exactly that check (`--compare`). Separately,
`lastCommand` is the only model variable with **no** seeded mutant and **no**
invariant, justified solely by an effect. It is the weakest-justified element in
the model and the natural first candidate if the owner wants the bound reduced.
Both are recommendations for the owner; neither was applied.
