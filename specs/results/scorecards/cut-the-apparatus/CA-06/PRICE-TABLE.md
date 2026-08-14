# `CA-06` price table

**Format: `specs/results/scorecards/cut-the-apparatus/GOAL-apparatus-cut/PRICE-TABLE-FORMAT.md`.**
Measured on `feature/CA-06` at branch point `e379d6b` (the epic tip after
`CA-01`, `CA-02`, `CA-03` and `CA-04` merged).

**Headline, stated before the tables because it changes how they should be read:
the dramatic shrink this ticket's work order asks for was not available, and the
reason is on the record rather than in the author's judgement.** The two things
that hold the mass — `--negative-cases` (290 lines of construction on a
1,043-line shared TLA+ expression parser and guard evaluator) and `--port-cases`
(397 on the same parser), **1,730 lines together** — were **measured and defended by
`SM-02` one epic ago in a shipped test that is still green**, in a file written
expressly to stop a later reader widening "defund `[ports.*]`" into "defund the
corpus". This ticket checked the work order against the record, per this epic's
own lesson 1, and the record refuses the deletion.

**So the measurement went the other way**, and produced `CA-06-DF-01`: those two
mechanisms **emit zero cases on any model whose next-state relation is not
literally named `Next`**, which is every model in this repository except the one
fixture they have ever been measured on. That is the result, and the cut below
is small on purpose.

---

## 1. The removal table

**No file was deleted.** Every removal is a function or a branch inside a file
that survives, so the rows are symbols rather than paths.

| surface | path — what went | lines | kind | finding |
|---|---|---|---|---|
| `scripts/` | `run_generated_case_adapters.py` — `write_case_program` + `generate_programs` (the per-case generated-program execution mode) | **−108** | py | `CA-06-DF-03` |
| `scripts/` | `run_generated_case_adapters.py` — `execute_programs` (its subprocess driver) | **−11** | py | `CA-06-DF-03` |
| `scripts/` | `run_generated_case_adapters.py` — `validate_effect_provider_execution_mode` and its call (the refusal that existed only to fence that mode) | **−17** | py | `CA-06-DF-03` |
| `scripts/` | `run_generated_case_adapters.py` — the two-way branch in `main()`, and the `args.batch` conjunct in `reexec_batch_if_needed` | **−13** | py | `CA-06-DF-03` |
| `scripts/` | `generate_cases_from_tlc_dump.py` — the hardcoded `"Next"` at both call sites | **−0** (replaced) | py | `CA-06-DF-01` |
| `tests/` | `test_effect_provider_fuzzing.py` — the `generate_programs` tail of the opaque-component test | **−22** | py | `CA-06-DF-03` |
| `tests/` | `test_effect_provider_runtime.py` — `test_provider_bearing_non_batch_execution_is_rejected`, and the non-batch half of the campaign test | **−22** | py | `CA-06-DF-03` |

## 2. The addition table — mandatory, and not omitted because it is unflattering

| surface | path | lines | kind | why |
|---|---|---|---|---|
| `scripts/` | `generate_cases_from_tlc_dump.py` — `resolve_next_relation` | **+39** | py | The `CA-06-DF-01` fix. **31 of those 39 lines are the docstring**, which records what was silently empty, on which models, and why the resolver it delegates to has been in the sibling module for three epics. |
| `scripts/` | `run_generated_case_adapters.py` — `default_import_roots_for` | **+31** | py | Derives the project root above `specs/` so `--import-root` need not be typed. **24 lines are docstring**, citing the sealed adopter transcript that reported the failure. |
| `scripts/` | `run_generated_case_adapters.py` — four tombstone comments and the `--batch` help text | **+47** | py | What each removal was, the finding that removed it, and what still accepts the flag. |
| `tests/` | `test_generate_cases_from_tlc_dump.py` — two `R1` regression tests | **+53** | py | The demonstrated failing input is `examples/distributed_history`, a **real subject**, not a fixture. Asserts the two models the modes were measured on resolve to `Next`, and that the fallback keeps the old behaviour. |
| `tests/` | `test_effect_provider_runtime.py` — the replacement half of the campaign test | **+28** | py | The removed half asserted a refusal that no longer exists. The replacement asserts what still has content: the run behaves identically with and without the now-inert `--batch`, which is what keeps the **27 live files** that pass `--batch`, and every sealed reproduction command, running. |

**The addition table is larger than the removal table in `tests/` and nearly as
large in `scripts/`, and that is `RD-02`'s finding happening again in this very
ticket** — *"every removal shipped instruments, tests and demonstrations to prove
the removal safe and nobody counted that as a cost"*. It is counted here.

## 3. The net figures, per surface, each with the tree it was measured on

Measured at `feature/CA-06` against branch point `e379d6b`, with
`find <surface> -name '*.py' -not -path '*/__pycache__/*' | xargs wc -l | tail -1`:

The per-file movement, CA-06's own, measured against branch point `e379d6b`
(which for these files equals the movement against the post-CA-05 epic tip,
since CA-05 touched none of them):

```
scripts/generate_cases_from_tlc_dump.py    3,471 -> 3,510    +39
scripts/run_generated_case_adapters.py     2,455 -> 2,392    -63
scripts/tla_spec_dev.py                      824 ->   844    +20   (--no-batch tombstone)
scripts/effect_conformance.py              1,845 -> 1,845      0   (citation repointed)
tests/test_generate_cases_from_tlc_dump.py   810 ->   863    +53
tests/test_case_adapter_runtime.py           614 ->   669    +55
tests/test_testgraph_channels.py             605 ->   612     +7
tests/test_effect_provider_fuzzing.py      1,545 -> 1,527    -18
tests/test_effect_provider_runtime.py      1,484 -> 1,490     +6
```

```
specs/ (all model kinds)                                       0   (NO model file changed --
                                                                    and see section 4, that is
                                                                    a defect, not a virtue)
```

`examples/validation/` is **exactly zero** and that is deliberate: nothing under
it was edited. The subject this ticket measured on, `examples/distributed_history`,
is outside `examples/validation/` and outside this ticket's `conflict_keys`, and
was **read and copied, never modified**.

**The card is reported separately and is never added to the above**
(`RM-03-DF-03`):

```
card: score_tools.py serve | wc -c    6,281 -> 6,281
      serve --digest-only             sha256:2d7d4a0506d9b259  (unchanged)
```

Clause (c) of `GOAL-apparatus-cut` holds: **the card did not grow.**

### After reconciling with the epic tip, and why the absolute figures moved

`CA-05` (#265) merged while this ticket was measuring, and `feature/CA-06` now
carries it. **The absolute figures at the PR head are therefore NOT this
ticket's delta:**

```
surface               (a) e379d6b   (b) 88165bd   (c) PR head   (c)-(b)   (c)-(a)
                        baseline     epic tip      this PR      CA-06     actual
                                     after CA-05                alone     movement
scripts/                   26,547       26,760       26,756        -4       +209
examples/validation/       14,854       14,854       14,854         0          0
tests/                     30,422       30,635       30,738      +103       +316
```

Command, at each ref:
`find <surface> -name '*.py' -not -path '*/__pycache__/*' | xargs wc -l | tail -1`

**ALL THREE COLUMNS PRINT, because the review was right that printing only the
counterfactual was a presentation failure.** `(c)-(b)` is CA-06's own
contribution; `(c)-(a)` is what actually happened to this branch, and the
difference between them is `CA-05`, which merged mid-ticket and brought
`scripts/disposition.py` and `tests/test_disposition_requirement.py` with it.
**Stating a counterfactual in the slot a reader expects an after-figure is how a
number later gets quoted without its qualifier** — this project's most expensive
recurring error, committed here and corrected at review.

**AND THE HONEST HEADLINE MOVED AGAIN WHEN THE REVIEW FIXES LANDED.** CA-06's
own `scripts/` figure was **−32** when the PR opened and is **−4** now: the
tombstones for `--no-batch`, the corrected test name and docstring, and the
docstring explaining the import-root bug the reviewer found cost 28 lines
between them. **The cut in `scripts/` is now approximately nothing**, and
`tests/` rose +103 rather than +41. **That is `RD-02`'s finding for the third
time in one ticket** — *"every removal shipped instruments, tests and
demonstrations to prove the removal safe and nobody counted that as a cost"* —
and responding to a review is itself one of those costs.

**One correction to the review, checked before writing it down:**
`examples/validation/` is **14,854 at all three refs — movement is exactly
zero**, not `+75`. Nothing under it was edited by CA-06 or by CA-05. Recorded
because this epic's rule is to check a figure rather than restate it, and that
applies to figures arriving from a reviewer as much as to figures arriving from
a work order.

The card is unchanged through the merge: **6,281 bytes,
`sha256:2d7d4a0506d9b259`.**

**Clause (a): −32 lines against a goal needing −13,066 across the epic. This
ticket was named "the largest single reduction in the epic" and it is not.**
Stated plainly rather than dressed up.

## 3b. The model delta, restated — the first version was wrong twice

**CA-06's PR said "no model delta" and gave this command as proof:**

```bash
git diff e379d6b -- '*.tla' '*.cfg' '*/spec_manifest.yaml' specs/current
```

**That command does not show it.** Run at the PR head it returns **48 files and
18,838 insertions**, because the globs sweep in this ticket's own
`specs/tickets/CA-06/` scaffold and `CA-05`'s history snapshots. **It is a
mis-scoped comparison straddling a merge — a milder instance of `CA-05-DF-07`'s
class**, and it is worth naming as such: the conclusion happened to be right and
the evidence offered for it was not.

**The command that does show it:**

```bash
git diff e379d6b -- specs/program_model specs/current \
    specs/desired_program_model/TlaSpecDevCli.tla \
    specs/desired_program_model/spec_manifest.yaml     # -> empty
```

**And "no model delta" was the wrong phrase anyway.** The accurate statement is
**no model work was done, and the model is now stale.** `spec_manifest.yaml` in
all three trees still declares two ports that exist only for the execution mode
this ticket deleted — `case_program_process` and `case_program_write`, both
listed under `RunSpecUnitTests`, both `@port`-annotated at
`TlaSpecDevCli.tla:506` and `:509` — and **all three of their declaration
comments cite line numbers inside code that no longer exists.**

**Those three dangling citations are MINE**, and CA-06 first reported them as
"INHERITED, UNDECLARED". A reviewer diffed the problem lists inside the
already-red `test_source_citations` params: **base 14 → head 17, and all three
new ones are this ticket's deletions** (`program_path`, `subprocess.run:2276`,
`:2392`, the last two now past the end of a 2,392-line file). **The red COUNT did
not move, which is exactly why prose missed it.**

**Not repaired here, and enumerated so the next ticket need not rediscover it:**
2 manifest port blocks × 3 trees, 2 `@port` annotations × 3 trees, 1
`RunSpecUnitTests` list entry × 3 trees, 3 citation comments × 3 trees, plus
`tests/test_port_declarations.py:136`, which asserts `case_program_process` by
name. Removing a port declaration whose effect can no longer occur changes no
variable, action or bound, **so it needs no TLC — only the test.** Filed in
`CA-06-DF-03`'s `blast_radius`.

**TLC was still legitimately skipped**: `specs/tickets/CA-06/current` equals
`desired`, and no variable, action or bound moved.

## 4. What the tree can no longer do

**The runner can no longer write a standalone, self-contained Python program per
case and run each in its own interpreter.** That mode produced one file per case
under `<work-dir>/programs/`, importable and runnable on its own, which is a real
capability: a case could be handed to someone as a script. **What the record says
it was worth: nothing measured in PRODUCTION.** Every production invocation in
this repository — both READMEs, `examples/validation/instruments/instruments.toml`,
the `distributed_history` Test Graph node and its adapter test,
`examples/run_distributed_history_validation.py` at three call sites, and all
three effect-provider validators — passes `--batch`, and the mode carried
strictly fewer oracles: effect providers could not run in it at all, which is why
a refusal existed in the code to fence it off. **The mode with fewer oracles was
the default.**

**CORRECTED AT REVIEW: "zero live callers" was FALSE.** Two TEST call sites
reached the deleted mode by passing no execution-mode flag at all —
`tests/test_case_adapter_runtime.py`'s subprocess test (which was *named* for
the mode) and `tests/test_testgraph_channels.py::_run_adapters` — and
`scripts/tla_spec_dev.py` still ships `--no-batch`, now a silent no-op. **The
loader grep searched for `--batch` and every one of these is characterised by
the ABSENCE of a flag; a grep cannot find an absent argument.** All three are
now renamed, annotated or tombstoned, and the correction is carried in
`CA-06-DF-03`. **The cut still stands on the narrower justification: no
production consumer, fewer oracles, and it was the default.**

**No refusal replaced it.** `no_new_gates_rule` is intact: this ticket removed a
mechanism and a refusal and added neither.

**Nothing else was removed.** In particular the negative corpus, the port corpus,
the guard evaluator, the TLA+ expression parser, parameter recovery, the
complexity advisory and the coverage and param-recovery reports **all survive
untouched**, and §5 of the PR body says why each was left.

## 5. Which sealed results depended on it

**READABLE and RE-DERIVABLE answered separately, per the format.**

| result | readable | re-derivable |
|---|---|---|
| `SV-04` — a score can produce a test and the re-score sees it | yes | **yes, run: `examples/validation/ab/tests/test_journal_conformance.py` → `14 passed in 0.26s`**, matching the sealed figure of 14 exactly |
| `SM-02` — the `[ports.*]` cut | yes | yes — `tests/test_ports_binding_removed.py` passes unchanged, including both assertions that `--port-cases` and `--negative-cases` survive |
| every sealed reproduction command carrying `--batch` under `specs/results/` | yes | **yes — `--batch` is still accepted**, which is the whole reason it was kept rather than deleted |
| `HP-03`, `PA-03`, `SM-01` kill tables over `QuotaLedger` | yes | yes — `find_next_relation` returns `Next` for `QuotaLedger`, so `CA-06-DF-01`'s fix is a **byte-level no-op** on every corpus those tables were computed from |

The mechanical loader check required by §5 of the format is
`loader-check.txt` in this directory, and it runs **both** greps: paths **and**
interfaces, because `CA-04-DF-06` established that the path grep alone is blind
to a removed symbol, flag or manifest key.

## 6. Suite movement, under `denominator_rule`

```
baseline:      8 reds at e379d6b   8 failed / 1462 passed  in 1354.07s  (pytest-baseline.txt)
first run:    10 reds             10 failed / 1465 passed  in 1339.03s  (pytest-after.txt)
after review:  9 reds              9 failed / 1484 passed  in 1280.52s  (pytest-after-review.txt)
repaired:      8 reds             (targeted re-run of tests/test_source_citations.py:
                                   3 failed / 77 passed -- the 3 inherited spec_manifest params)
```

**THE SAME DEFECT BIT THREE TIMES AND THAT IS WORTH RECORDING RATHER THAN
TIDYING AWAY.** `scripts/effect_conformance.py:1684` cites
`run_generated_case_adapters.py:<line> (case-work)`. Deleting 108 lines moved the
anchor `1354 -> 1405`; adding the review's import-root docstring moved it
`1405 -> 1413`. **Every edit to a file that something cites by line number
re-breaks the citation**, and it went red again on the review round for exactly
the reason it went red on the first. Repointed each time, and the test caught it
each time. **This is the strongest argument in this ticket for content anchors
over line numbers**, and `RC-02` — which built the anchor mechanism — already
made it.

**The two extra reds were MINE, they were found by the suite rather than by
prose, and they were REPAIRED rather than declared** — because they are not
findings about the tree, they are stale citations *caused by this ticket's own
deletion*:

```
test_source_citations.py::...[scripts/run_generated_case_adapters.py]
    the new `default_import_roots_for` docstring cited the adopter transcript
    with no parenthesised anchor -- "an unanchored line number cannot be
    checked and goes stale silently". Anchored on `--import-root`.

test_source_citations.py::...[scripts/effect_conformance.py]
    effect_conformance.py:1684 cited run_generated_case_adapters.py:1354
    (case-work). Deleting 108 lines above it moved the anchor to :1405.
    Re-pointed.
```

**This is `RC-02`'s instrument working exactly as its docstring says it should:**
*"A line shift now breaks a test instead of a reader."* It is the first time in
this epic that a cut's collateral damage was caught by a test rather than by a
successor ticket, and it is worth recording as such.

```
movement after repair:  numerator 0, denominator -1, because
           test_provider_bearing_non_batch_execution_is_rejected was DELETED
           along with the mode whose refusal it asserted. It did not start
           passing; its subject stopped existing. Two R1 regression tests were
           added, so the pass count rises 1462 -> 1465.
```

The 8 baseline reds, listed so any change is attributable:

```
test_architecture_tags.py::test_the_same_tag_control_holds                     DELIBERATE (RM-06-DF-01)
test_goal_baseline_is_a_card.py::...judged_baseline_cannot_be_re_opened        CA-00-DF-02
test_instrument_demonstrations.py::test_every_declared_path_exists             INHERITED
test_instrument_demonstrations.py::test_every_fast_demonstration_reproduces    INHERITED
test_source_citations.py::...[specs/current/spec_manifest.yaml]                INHERITED, UNDECLARED
test_source_citations.py::...[specs/desired_program_model/spec_manifest.yaml]  INHERITED, UNDECLARED
test_source_citations.py::...[specs/program_model/spec_manifest.yaml]          INHERITED, UNDECLARED
test_ticket_retirement.py::...delivered_plan_has_matching_close_receipts       INHERITED
```

**None was repaired.**
