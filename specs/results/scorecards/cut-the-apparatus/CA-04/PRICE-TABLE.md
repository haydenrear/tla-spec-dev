# `CA-04` price table — the mutation kill test

**Format: `specs/results/scorecards/cut-the-apparatus/GOAL-apparatus-cut/PRICE-TABLE-FORMAT.md`.**
Measured on `feature/CA-04` at branch point `4302082` (the epic tip after `CA-02` merged).

**Headline, stated before the tables because it changed the shape of the cut:**
the work order asked for `kill_test.py` to be deleted outright and for
`candidate_note_bar.py` to go with it. **Neither deletion was made as
specified.** `kill_test.py` is not self-contained — the A/B evaluation
machinery imports it, and deleting it wholesale breaks the re-derivation of one
of the four load-bearing **disproofs**. `candidate_note_bar.py` rests on a
finding that says something else entirely. Both are measured below, and both are
`CA-04` findings rather than opinions.

---

## 1. The removal table — one row per deleted or reduced path

| surface | path | lines | kind | finding |
|---|---|---|---|---|
| `scripts/` | `kill_test.py` — the oracle-4 half (boundary derivation, seeding, control run, report, gate) | **−839** (1,149 → 310) | py | `RM-03-DF-05` |
| `scripts/` | `run_kill_test.py` — the CLI entry point for the gate | **−235** (deleted) | py | `RM-03-DF-05` |
| `scripts/` | `tla_spec_dev.py` — the `run kill-test` subparser and dispatch | **−31** | py | `RM-03-DF-05` |
| `tests/` | `test_kill_test.py` | **−1,013** (deleted) | py | `RM-03-DF-05` |
| `tests/` | `test_infer_action_params.py` — the `RunKillTest` recipes and the action enumeration | **−9** | py | `RM-03-DF-05` |
| `specs/` ×3 | `kill_mutants.toml` — the 29-mutant catalogue | **−396 each** (deleted) | toml | `RM-03-DF-05` |
| `specs/` ×3 | `TlaSpecDevCli.tla` — the `kill_test` variable, `RunKillTest`, `KillTestVerdictRequiresBudgets` | **−124 each** | tla | `RM-03-DF-05` |
| `specs/` ×3 | `production_adapters.py` — `RunKillTestAdapter` | **−211 each** | py | `RM-03-DF-05` |
| `specs/` ×3 | `spec_manifest.yaml` — `kill_rate_floor`, the `mutation_write` port, `RunKillTest`'s row, the `kill_test` justification | **−31 each** | yaml | `RM-03-DF-05` |
| `specs/` ×3 | `tests/test_tla_spec_dev_kill_test_adapter.py` | **−126 each** (deleted) | py | `RM-03-DF-05` |
| `specs/` ×3 | `case_adapters.toml`, `MC.cfg`, `MCsmall.cfg`, two adapter tests | **−7 each** | toml/cfg/py | `RM-03-DF-05` |

### The finding, quoted from the sealed record because the epic has been burned by unchecked quotation

`RM-03-DF-05`, read at `specs/desired_program_model/deferred_findings.yaml`:

> **"THE ONE HARD STATIC GATE LEFT IN THIS REPOSITORY IS A SPECIFIED ACTION OF
> THE MODEL, SO REMOVING IT IS A MODEL DELTA AND RM-03 DECLARES NONE.** … Every
> candidate RM-03 examined disclaims gatehood in its own docstring except one:
> `scripts/kill_test.py`, whose `kill_rate_floor` is described there as *"a hard
> gate, and the load-bearing one"* … Recorded loudly because it is the one
> removal that would have made this ticket's numbers look much better."

and its own `suggested_fix`, which asked for exactly this ticket:

> **"Open it as its own ticket against the CLI model."**

`RM-03-DF-05` also enumerated the model surface in advance — *"it appears in
`spec_manifest.yaml`, `kill_mutants.toml`, `production_adapters.py`,
`adapter_case_runtime.py` and three spec-unit adapter tests"* — and **every one
of those was found and cut.** The enumeration was accurate.

---

## 2. The addition table — mandatory, and not omitted when small

| surface | path | lines | kind | why |
|---|---|---|---|---|
| `scripts/` | `kill_test.py` — new module docstring | **+56** | py | Records what the module was, the finding that removed it, and **why the parser/scanner survives**, with the measurement behind that decision. Replaces an 86-line docstring about a gate that no longer exists. |
| `specs/` ×3 | `TlaSpecDevCli.tla` — the removal note above `VARIABLES` | **+21 each** | tla | States **what the model can no longer express** (§4) in the file where the next reader will look for the missing variable. |
| `specs/` ×3 | `production_adapters.py`, `spec_manifest.yaml` | **+6 / +17 each** | py/yaml | Tombstones naming `RM-03-DF-05`, and the note that every `kill_tests:` list is now empty because the catalogues they cited are gone. |
| `tests/` | `test_infer_action_params.py` | **+5** | py | The action-set docstring records that `RunKillTest` left the model and that the set **tracks** the model rather than being repaired to match it. |

**No new file was created by this cut, and no new instrument.** The one thing
this ticket added to the repository outside a tombstone is this table and the
evidence beside it.

---

## 3. The net figures, per surface, each with the tree it was measured on

Measured at `feature/CA-04` against branch point `4302082`, with
`find <surface> -name '*.py' -not -path '*/__pycache__/*' | xargs wc -l | tail -1`:

```
surface                 before      after       delta
scripts/                 27,652     26,547     -1,105
examples/validation/     14,685     14,685          0
                        -------    -------    -------
GOAL-apparatus-cut       42,337     41,232     -1,105

tests/                   31,274     30,252     -1,022
specs/ (all kinds)            —          —     -2,685
```

`examples/validation/` is **exactly zero** and that is deliberate: no file under
it was edited, because the two consumers this cut touches live there and are
outside this ticket's conflict keys (§5, §7).

**The card is reported separately and is never added to the above**
(`RM-03-DF-03`):

```
card: score_tools.py serve | wc -c    6,281 -> 6,281
      serve --digest-only             sha256:2d7d4a0506d9b259  (unchanged)
```

Clause (c) of `GOAL-apparatus-cut` holds: **the card did not grow.**

---

## 4. What the tree can no longer do

**The repository has no way to validate a model against the program.** This is
the real capability removed, and `TlaSpecDevCli.tla`'s own comment said so
before this ticket deleted it: `kill_test` was *"the only one of the four
[oracles] that validates the representation against the PROGRAM rather than
against itself. TLC proves self-consistency, analyze corpus proves
tractability, effect conformance proves the boundaries are declared; none of
them can tell a faithful model from a vacuous one. This can."* That sentence is
now false of this toolchain, and nothing replaces it.

**The cost caps have lost their matching value floor.** Every other budget in
the manifest is a cost cap — `max_distinct_states`, the case caps, the component
heuristics — and the model's own rationale for the floor was that cost caps
alone are gameable in one obvious direction: *"shrink the model toward nothing
and every cap passes."* `kill_rate_floor` was the counterweight. **A model
shrunk toward nothing now satisfies every budget the model still states.**
Whether that matters is an empirical question and the record's answer is the
reason for the cut: **seven epics, zero bugs caught by a static check.**

**Coverage can now drift behind the model silently.** `required_boundaries`
recomputed the obligation every run from the port declarations and the
`INVARIANTS` block, so declaring a new port *broke* the kill test until somebody
seeded a fault for it. That pressure is gone: a new port or invariant now
imposes no obligation anywhere.

**Abstraction validation is gone.** `compare_reports` implemented
`references/architecture_tractability.md`'s licence — an abstraction is
permitted iff the kill rate holds after it — and was the mechanism that told a
legitimate simplification from a disguised deletion. **Nothing in the tree now
distinguishes those two.** This epic is a cutting epic, so it is worth saying
plainly that the instrument for detecting over-cutting was itself cut.

**And one thing the model can no longer be measured as exceeding.** Removing a
4-valued variable divided the repository's own declared state-space bound by
exactly 4: **1,111,320 → 277,830**, which is now **under** the declared
`max_state_space_bound` of 1,000,000 for the first time. The scanner no longer
warns about this model. That is a real consequence and it is not obviously good
news: the bound fell because the model got smaller, not because it got better.

### What survived the cut, and why it is not the gate

`scripts/kill_test.py` keeps **310 lines**: the TOML catalogue parser
(`load_catalog`, `parse_mutants`, `Mutant`) and the suppression-key tripwire
(`SUPPRESSION_KEYS`, `scan_for_suppression`). Neither computes a rate, neither
has an exit code, and neither is a gate. They were retained for a measured
reason, in §5.

---

## 5. Which sealed results depended on it — checked with a run, never assumed

**READABLE and RE-DERIVABLE are answered separately, as the format requires.**

### Disproof 1 — "model-derived cases do not catch bugs hand-written tests miss"

This is the disproof the work order named, and the question it asked was
*"whether the zero-unique-kills disproof is still reproducible once the
instrument that produced it is gone."*

**The premise of that question is wrong, and this is the ticket's main finding.**
`scripts/kill_test.py` **did not produce that result.** It is oracle 4 over
*this repository's own* declared ports. The 0-vs-4 table was produced by `RD-03`'s
cross-tree probe over the `ab_quota_ledger` fixture — a different instrument, a
different subject, a different model. Verified by reading the sealed record:
`specs/results/scorecards/reading-discipline/GOAL-product-round/RD-03/RESULT.md`
records the table, and `…/RD-03/probe/COMMANDS.md` records every command. The
probe harness is self-contained under `…/RD-03/probe/harness/`, and the only
mention of `kill_test` anywhere in RD-03's evidence tree is one audit line about
an unrelated change.

**But the answer is still not "unaffected", and this is where the cut changed
shape.** `RD-03`'s model-derived instrument columns — `corpus-whole`,
`corpus-neg`, `map-silent`, `map-checking`, the four whose zero is the disproof —
were run through this driver:

```
PYTHONPATH=$SCR/bindings python3 examples/validation/ab/eval/run_controls.py …
```

and `run_controls.py:165` carries a **module-scope** import:

```python
from scripts.kill_test import scan_for_suppression  # noqa: E402
```

**Measured, by parking the file and running the driver:**

```
BEFORE: run_controls.py LOADS OK
AFTER : ModuleNotFoundError: No module named 'scripts.kill_test'
        (examples/validation/ab/eval/run_controls.py, line 165, in <module>)
```

A wholesale deletion of `kill_test.py` would therefore have left disproof 1
**readable but no longer re-derivable** — the precise failure `CA-02` made with
`repriced_history.py` one ticket earlier, and the failure this format's §5 was
rewritten to prevent. **The retained 310 lines exist because of that
measurement, not because of caution.**

**Verdict: still readable, still re-derivable.** With the parser/scanner
retained, `run_controls.py` loads and `check_catalogue.py` runs.

**ADDED AFTER REVIEW — the case for retention is stronger than this ticket made
it, and the extra evidence was inside `tests/`.** Independent review found
**three more in-repo consumers** that `CA-04` did not name, all importing
`SUPPRESSION_KEYS` from this module:

```
tests/test_eval_controls.py:503             from scripts.kill_test import SUPPRESSION_KEYS
tests/test_ab_three_arms_and_port_faults.py:573   import kill_test  ->  kill_test.SUPPRESSION_KEYS
tests/test_falsifiable_controls.py:470            import kill_test  ->  kill_test.SUPPRESSION_KEYS
```

`tests/` is **inside this ticket's `implementation_scope`**, so a wholesale
deletion would have added **three more reds in a surface this ticket owns**, on
top of breaking the two `examples/` instruments. The retained 310 lines are load-
bearing for five known consumers, not two. **`CA-04` verified the two it found
and stopped looking**, which is a smaller version of the same reading failure
this table is otherwise about.

### The RM-03-protected instrument

`examples/validation/ab/check_catalogue.py` — which `RM-03` explicitly refused to
delete as *"the arm-dispatch integrity instrument whose `--arms` mode produced
FI-06's retraction of PA-06's tolerance claim"* — calls
`kill_test.load_catalog()` at line 465 to load every catalogue *"via the SHIPPED
parser"*. Measured the same way:

```
BEFORE: "Catalogue integrity holds: every pattern occurs exactly once,
         every mutant applies and reverts cleanly, and every declared gap is seeded."
AFTER : ModuleNotFoundError: No module named 'kill_test'
```

**Verdict: still runs** at this tip, unchanged output.

### DISCLOSED AFTER REVIEW — the shipped skill still tells adopters to run the deleted command, and the loader check cannot see it

**`SKILL.md:1167` and `SKILL.md:1174` still instruct adopters to run the command
this ticket deleted.** Line 1174: *"Run it with `tla-spec-dev run kill-test
--corpus-command "<corpus>"`, and…"*. Measured at this tip:

```
$ python3 scripts/tla_spec_dev.py --spec-root specs run kill-test --corpus-command "pytest"
tla-spec-dev run: error: argument target: invalid choice: 'kill-test'
                  (choose from 'spec-unit-tests', 'effect-conformance')
```

**This is the same class as `SV-06-DF-04`** — root `SKILL.md` shipping a
description of something the toolchain no longer has — **found in the ticket
whose own headline finding is about that exact surface, and missed by that
ticket.** Root `SKILL.md` is inside `CL-04`'s narrow shipped-toolchain
definition, so it counts as shipped-bytes damage rather than an internal note.

**And the instance matters less than what it exposes about the check that
missed it.** `PRICE-TABLE-FORMAT.md` §5's required loader check is:

```bash
git grep -n "$(basename <deleted-path>)" -- specs/ references/ scripts/ examples/ tests/
```

**It greps deleted PATHS. `run kill-test` is a deleted CLI SURFACE, and no path
grep can reach it** — there is no basename to search for. §1 of this very table
lists that subparser among the things deleted, and the check still could not see
it. The check is sound for files and **structurally blind to interface
removals**: CLI subcommands, public function exports, manifest keys, TOML
sections. `CA-04` declared the lesser `references/modular_fuzzing.md:415`
staleness as under-budget bookkeeping and **missed the larger one directly above
it, because the tool it was given only looks for paths.**

**The check needs a second half for surfaces**, something of the shape
`git grep -n "run kill-test\|kill-test" -- SKILL.md references/ prompts/ templates/`
run against the command strings a removal retires. Filed as `CA-04-DF-06`, which
is the **sixth** finding against a declared budget of five — recorded as an
overrun rather than dropped, because the deferment policy's `blocking: escalate`
applies and the epic owner asked for it by name.

### The other three results and the other three disproofs

| result | rests on the kill test? | checked how |
|---|---|---|
| Asking for an architecture changes the architecture (arm C, 1/1) | **No** | `examples/validation/ab/arm_{a,b,c}` and the ports-as-adapters scorecards; no path through `kill_test.py` |
| D3 separates architectures on a second example | **No** | `specs/results/scorecards/portable-substrate/`; judged cards, no instrument here |
| D3's v5 caveat discriminates (`SV-01`) | **No** | sealed v4/v5 scorecard trees; `score_tools.py`, untouched by this ticket |
| A score can produce a test and the re-score sees it (`SV-04`) | **No** | `specs/results/scorecards/score-drives-validation-sv04/`; untouched |
| Static gates catch nothing | **No** — this cut *acts on* it | seven epics of record |
| The removal-pricing instrument is not yet useful | **No** | `CA-02`'s surface, not this one |
| Three of five dimensions graded toolchain ownership | **No** | anchor-rationale counts over sealed cards |

### The instruments `RM-02` called the substrate's best export

`scope`, `seal`, `contested`, the blinding mechanism, `R-H1`/`R-H2`/`R-H4`/`R3`
and the version/served double seal all live in
`examples/validation/scorecards/score_tools.py`, which **this ticket did not
touch** (it is `CA-03`'s conflict key). The card digest is unchanged, which is
the double seal reporting for itself.

---

## 6. Suite movement, under `denominator_rule`

```
baseline:  6 reds at THIS branch point (4302082)
after:     10 reds   -- measured, full suite: 10 failed, 1461 passed in 1193.54s (0:19:53)
movement:  numerator +4, denominator -1,022 test lines (test_kill_test.py 1,013
           plus 9 lines of RunKillTest recipes), because the tests of the deleted
           gate went with the gate
```

### First: the baseline is 6 here, not the 7 in `GOAL-four-results-stand/baseline.md`

**This is a denominator move by `CA-02`, not a repair by this ticket, and it is
recorded rather than quietly adopted.** `baseline.md`'s 7 was measured at
**PR #263's head (CA-01)**, and its list names
`test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer` as one
of the **two deliberate** reds. `CA-02` then deleted the pricer **and that test
file**: `ls tests/test_price_removal.py` -> *No such file or directory* at
`4302082`. So one deliberate red left by **denominator**, and the branch point
carries **6**. Issue #258's "Suite baseline: 6 reds" is correct **for this tree**
and `baseline.md`'s 7 is correct **for the tree it was measured on**; the two are
not in conflict and neither should be quoted without its tree.

**The 6 baseline reds, all present and all untouched:**

```
test_architecture_tags.py::test_the_same_tag_control_holds                      DELIBERATE (RM-06-DF-01)
test_goal_baseline_is_a_card.py::...cannot_be_re_opened                         CA-00-DF-02
test_source_citations.py::...[specs/current/spec_manifest.yaml]                 INHERITED, UNDECLARED
test_source_citations.py::...[specs/desired_program_model/spec_manifest.yaml]   INHERITED, UNDECLARED
test_source_citations.py::...[specs/program_model/spec_manifest.yaml]           INHERITED, UNDECLARED
test_ticket_retirement.py::...delivered_plan_has_matching_close_receipts        INHERITED, UNDECLARED
```

**The 4 new reds, each with its cause. None is repaired.**

| new red | cause | in this ticket's scope? |
|---|---|---|
| `test_instrument_demonstrations.py::test_every_declared_path_exists` | `examples/validation/instruments/instruments.toml:189,228` declare `paths = ["scripts/run_kill_test.py"]`, now deleted | **No** — `examples/` is outside this ticket's conflict keys. `CA-04-DF-04`. |
| `test_instrument_demonstrations.py::test_every_fast_demonstration_reproduces` | the `kill-test-floor` and `kill-test-boundary-coverage` demonstration rows shell out to `run_kill_test.py` | **No** — same file. `CA-04-DF-04`. |
| `test_analyze_complexity.py::test_repository_own_model_reproduces_the_recorded_state_space_bound` | the declared bound fell **1,111,320 → 277,830** when a 4-valued variable left the model | Yes, and **deliberately not repaired** — see below |
| `test_analyze_complexity.py::test_repository_own_model_has_landed_the_setup_phase_collapse` | the projected `221,184` factor no longer divides the bound, for the same reason | Yes, and **deliberately not repaired** |

**Why the two bound assertions were left red rather than updated.** They assert
specific measured figures carrying `MF-011`/`MF-014`/`MF-025` provenance in their
own comments. Rewriting them to the number this ticket just produced is fitting a
test to a known answer, which is `MF-020`, refused three times by this project.
The figures are **stated here** so the epic owner can decide whether to re-record
them; that decision is not a cutting ticket's to make.

### Three checks that fired, were repaired, and are reported anyway

**A first full-suite run measured 13 failed / 1458 passed.** Three of those
thirteen were **self-declarations of the model's own shape** that had gone stale,
and they were updated rather than left:

| check | what it asserts | action |
|---|---|---|
| `test_spec_manifest_records.py::test_the_manifest_states_the_counts_of_the_model_beside_it` ×3 trees | the manifest's *"this tree's model has 9 variables and 17 Next disjuncts"* must equal the module beside it | updated to **8 variables and 16 Next disjuncts (15 @command actions plus Stutter)** |
| `specs/*/tests/test_tla_spec_dev_binding_reconciliation.py::test_the_model_has_the_expected_sixteen_command_actions` | the model has exactly 16 command actions | updated to **15**, renamed, `RunKillTest not in actions` asserted |
| `tests/test_infer_action_params.py::test_all_sixteen_action_labels_are_audited` | set equality with the model's action set | `RunKillTest` recipes removed, docstring records why |

### CORRECTED after independent review — the original argument here was overstated

**What the first version of this section claimed:** that the three updated
checks are "records that track the model" while the two `analyze_complexity`
bound assertions are "measured historical figures", and that rewriting the
latter would be `MF-020`. **The review marked that split OVERSTATED and it was
right on both halves.**

**Half one — the distinction does not separate what I said it separates.**
`test_repository_own_model_reproduces_the_recorded_state_space_bound` **also
asserts live variable counts** — `completeness.total == 9`,
`completeness.resolved == 7`, `set(result.unbounded) == {"lastCommand",
"result"}` — which is exactly the kind of model-tracking record I updated in the
manifest. The test is *both* kinds at once, so the line I drew cannot be what
decided it.

**Half two — `MF-020` was the wrong doctrine, and a precedent refutes it.**
`MF-020` forbids *adding* an axis, test, rung or case fitted to a known answer.
Maintaining a derivation chain across a removal is not that, and **a prior
removal-only ticket already did it**, in this test's own comment:

> *"AC-01's factor of 4 (architecture_scan) and RC-01's factor of 6
> (architecture_delta) were both REMOVED 2026-08-04 with the static architecture
> scanners, so they are no longer divided out here: **the chain gets SHORTER
> when model surface goes away, which is the point.**"*

**The real reason these two are left red, which is stronger and is about what is
missing rather than about doctrine:** the repository's own complexity ledger
licenses a **decrease** only against the `validated_refactor` evidence set, and
`scripts/complexity_ledger.py` gate 3 says so in terms:

> *"REJECTED -- complexity decreased but the validated-refactor basis is
> UNVERIFIED … A decrease is licensed only by the validated-refactor evidence
> set from the same run (`validated_refactor:` -- `tlc_before`, `tlc_after`,
> `behavior_tests`, `descriptor_comparison`). **Absent evidence is not passing
> evidence.**"*

**`CA-04` ran no TLC — on either side.** The `model_delta_expectation` called for
none because the delta is a removal, and none was run. So the bound movement
**1,111,320 → 277,830 is MEASURED but NOT VALIDATED**, and writing `277,830`
into the test as the repository's licensed bound would record a decrease this
repository's own gate refuses to license. **Leaving the test red is the honest
state: the number is known and the licence for it is not.**

**So the ticket's model delta is PRICED but NOT VALIDATED**, and that belongs in
the headline rather than in a footnote. A successor that wants these two tests
green should run `tlc_before`/`tlc_after` and record the `validated_refactor`
basis — that is the missing work, and it is a real cost this cut did not pay.

**What survives of the original distinction, narrowed to where it holds:** a
**shipped record that would state a falsehood to an adopter** — the manifest's
*"this tree's model has 9 variables and 17 Next disjuncts"* — is different in
kind from **a red test, which states nothing to anyone**. That is why the
manifest was corrected and the tests were not. It does **not** separate the two
action-enumeration tests from the bound test, and that claim is withdrawn.

**The first run is kept at `pytest-repo-unit-superseded.txt`** rather than
deleted, because a discarded run is evidence about method. The published figure
is the second, run from a clean start on the final tree.

---

## 6a. RE-MEASURED AT THE PROMOTED TIP, after merging CA-03

**`CA-03` merged between the measurement above and this promotion, so every
figure was taken again on the merged tree rather than carried forward.** Merge
commit `b581439`; epic tip `24cd340` is an ancestor of `feature/CA-04`.

### Lines, per surface, at the promoted tip

```
surface                 4302082    CA-03 tip   CA-04 promoted   CA-04's own delta
scripts/                 27,652      27,652         26,547            -1,105
examples/validation/     14,685      14,854         14,854                 0
                        -------     -------        -------           -------
GOAL-apparatus-cut       42,337      42,506         41,401            -1,105
```

**`examples/validation/` rose by 169 lines and none of it is mine** — it is
`CA-03`'s. It is reported here rather than netted against my cut, because a
combined figure would read `-936` and silently attribute another ticket's
addition to this one. **Each surface keeps its own tree.**

```
card: serve | wc -c   6,281 -> 6,281   digest sha256:2d7d4a0506d9b259 (unchanged)
```

### Suite at the promoted tip, under `denominator_rule`

```
CA-03 tip 24cd340:   6 failed / 1525 passed   (1,531 collected)  -- CA-03's own measurement
CA-04 promoted:     10 failed / 1464 passed   (1,474 collected)  -- 1235.75s (0:20:35)

numerator:    +4     the same four, named below; THE SET DID NOT CHANGE
denominator:  -57 collected tests, because the tests of the deleted gate went
              with the gate (test_kill_test.py plus the RunKillTest recipes in
              test_infer_action_params.py). Passed ALSO rises by CA-03's new
              tests, so 1,525 -> 1,464 is NOT a loss of 61 passing tests and
              must not be read as one.
```

**The four new reds are the same four, on a different baseline tree:**

```
test_analyze_complexity.py::test_repository_own_model_reproduces_the_recorded_state_space_bound
test_analyze_complexity.py::test_repository_own_model_has_landed_the_setup_phase_collapse
test_instrument_demonstrations.py::test_every_declared_path_exists
test_instrument_demonstrations.py::test_every_fast_demonstration_reproduces
```

and the six baseline reds are `CA-03`'s six, unchanged and unrepaired. **No new
red appeared from the merge and none of mine went away** — checked rather than
assumed, since `CA-03` touched `score_tools.py`, `subjects.toml` and
`tests/test_score_tools.py`.

**Spec-unit at the promoted tip:** `1 failed / 55 passed`; the failure is the
inherited `active_ticket: PA-01`, which `CA-03` also carried (`1 failed / 68
passed`). The 68 → 55 move is the same denominator effect — the three
`test_tla_spec_dev_kill_test_adapter.py` files went with the action.
**Ticket-local: 53 passed / 0 failed.**

### Ledger at the promoted tip

```
226 base -> 231 (CA-03's five) -> 237 (CA-04's six)
duplicate IDs                       NONE
rows missing a disposition          NONE
pre-existing rows altered by CA-04  NONE
CA-03's two disposition edits       PRESERVED (RD-03-DF-08 consumed,
                                    SV-04-DF-05 repaired)
duplicate YAML keys                 7, all `disposition_ticket`, all on
                                    SM-05-DF-01..07 -- pre-existing at base,
                                    none of them CA-04's. CA-05-DF-06.
```

---

## 7. What was REJECTED — including everything that would have made this look bigger

Doctrine: *"Ask every blind agent what it REJECTED — it has produced more than
any check."*

- **`scripts/candidate_note_bar.py` (281) and `tests/test_candidate_note_bar.py`
  (217) — the work order's second deletion, REFUSED on three independent
  grounds.** `CA-04-DF-01`, `CA-04-DF-02`.
  1. **The finding cited does not say it.** Issue #258, `ticket_plan.yaml` and
     the epic's own summary attribute *"281 lines, nothing imports it"* to
     `SV-06-DF-04`. `SV-06-DF-04` is about **`SKILL.md:1337` describing a
     five-dimension card**. It does not mention `candidate_note_bar.py`.
  2. **The claim's second half is false.** *"the shortest test in its own file
     asserts that"* — the shortest test is
     `test_the_shipped_card_is_untouched_by_all_of_this` (5 lines), and it
     asserts the **card is still 6,281 bytes**. It says nothing about imports.
     It is also **the only test in the entire suite that asserts 6,281**, which
     is `GOAL-apparatus-cut` clause (c)'s own guard.
  3. **It is the reproduction of an OPEN finding.** `SV-07-DF-01` names
     `python3 scripts/candidate_note_bar.py` and
     `tests/test_candidate_note_bar.py::test_the_note_prompt_is_inside_both_seals`
     as its `reproduction`, and its `suggested_fix` requires
     `candidate_note_bar.py --out` to supply the candidate arm of the
     both-wordings round `SV-02` says is owed. Deleting it repeats `CA-02`'s
     error against a finding that is still open.

  4. **ADDED AFTER REVIEW — a fourth ground this ticket missed.**
     `examples/validation/instruments/instruments.toml:814` declares
     `[[instrument]] id = "candidate-note-bar"` with
     `paths = ["scripts/candidate_note_bar.py"]` and **two demonstration nodes**
     on its test file — `test_the_generator_refuses_a_card_it_cannot_derive_from`
     and `test_the_candidate_adds_no_rung_and_moves_no_anchor`. Deleting the two
     files would have added **two more instrument reds**, in the same registry
     that already supplies two of this ticket's four declared reds.

  **"Nothing imports it" is true and is not evidence of inertness** — the
  script's own docstring advertises it as a deliberate property: *"is imported
  by no production code, and is not a gate."* **And it is why the claim was
  believed**: the registry entry, the two demonstration nodes and the open
  finding that names the script are all invisible to the word "imports".

- **`scripts/fitness_functions.py` (450) — examined and NOT cut.** `CA-04-DF-05`.
  The work order asked for "dead levers only". The sealed record says this is
  not one: `RM-03-DF-04` records that *"`fitness_functions.py` says of itself
  that firings are advisory … **See RM-03-DF-05 for the one that is left**"* —
  i.e. the record already named `kill_test.py` as the sole surviving gate. No
  finding names a dead lever inside `fitness_functions.py`, so cutting any part
  of it would be a deletion with no finding behind it and would fail
  `GOAL-apparatus-cut` clause (b) *even though the lines would have fallen*.

- **Deleting `kill_test.py` outright for another 310 lines.** Rejected on the
  measurement in §5. It would have moved `scripts/` to −1,415, within sight of
  the expected −1,430, and it would have broken a load-bearing disproof's
  re-derivation and an `RM-03`-protected instrument. **The number was available
  and was not taken.**

- **Editing `examples/validation/instruments/instruments.toml` to clear the two
  new reds.** It is outside this ticket's conflict keys and implementation
  scope, and the deferment policy says defer rather than fix. Filed as
  `CA-04-DF-04` with the exact rows.

- **Repairing `examples/run_distributed_history_validation.py`**, which invokes
  `run_kill_test.py` at step 3 of 7 and now dies. Same reason. `CA-04-DF-04`.

- **Repairing any baseline red.** Untouched, all 6.

- **Updating `references/modular_fuzzing.md:415`**, which still describes
  *"(`scripts/kill_test.py`, `scripts/run_kill_test.py`). Five properties are…"*
  as a live instrument. `references/` is outside this ticket's
  `implementation_scope`. It is bookkeeping of the same kind as `CA-04-DF-04`
  and belongs with it; recorded here because the required loader check found it
  and a finding budget of 5 was already spent.

---

## 8. Goal contribution, measured

| goal | contribution | expected | measured | classification |
|---|---|---|---|---|
| `GOAL-apparatus-cut` | direct | −1,430 or more from `scripts/` | **−1,105** from `scripts/`; combined 42,337 → 41,232 | **moved less than expected** |
| `GOAL-four-results-stand` | guard | none expected; verify disproof 1 | four results and four disproofs all still reproduce; **4 new reds declared**, the **6 baseline reds at `4302082`** intact | **no measurable movement** (guard held) |
| `GOAL-consumption-obligatory` | direct | consume `RM-03`'s cut and the inert-bytes finding | `RM-03-DF-05` **consumed**; the inert-bytes finding **refuted, not consumed** | **moved less than expected** |
| `GOAL-blind-dispatch` | guard | none expected | nothing in this ticket dispatched a judge | **no measurable movement** |

**Why `GOAL-apparatus-cut` came in 325 lines short, stated plainly rather than
explained away:** the `expected_effect` was arithmetic over two whole files —
`kill_test.py` 1,149 + `candidate_note_bar.py` 281. One of those files could not
be deleted whole without breaking a disproof, and the other rested on a
misattributed finding. **The shortfall is the finding.** Taking the full 1,430
was available in both cases and was refused in both cases, which is clause (b)
of the same goal doing its job.
