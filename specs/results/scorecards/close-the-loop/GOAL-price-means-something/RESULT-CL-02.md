# CL-02 — a price stops being entailed by the shape of the removal

Ticket `CL-02`, issue #222, branch `feature/CL-02`, parent `10cf11a`.
Goal `GOAL-price-means-something`, contribution **direct**.
Local signal: `EXTINCT vs ENTAILED-SURVIVES on a real cut`.

**THE HEADLINE FIRST, AND IT IS THE UNINTERESTING DIRECTION: NOTHING CAME BACK
NON-ZERO.** Every historical removal with a published before-table was
re-priced with the corrected instrument, on both the entailed side and the
measured side, and the total is **0 priced results**. The one removal the census
claimed a non-zero price for now reads `EXTINCT`, which is not a price and is
not a zero — it is a refusal to measure. `RM-01-RF-1` is still `PRICED` and is
still the only price this project has.

---

## 1. What was wrong, reproduced before a line was changed

`NEXT-EPIC.md` §0-AAAAAAA §2 withdrew `RM-03`'s "first PRICED removal in this
project's history". Both halves reproduce at `10cf11a`, and the transcript is
`parent-10cf11a-same-commands.txt` beside this file.

```
$ price_removal.py entail --before .../rm03-gap-mutants-before.json --head 6298eee
ENTAILED-SURVIVES   RM03-GM-CTRL-C-...      <-- declared is_control, gap "NONE, on purpose"
UNDECIDED           RM03-GM-D4-...
UNDECIDED           RM03-GM-D5-...
ENTAILED-SURVIVES   RM03-GM-RUNNER-...      <-- the headline
```

**Four rows; the round's own zero-gap control returns the headline verdict.** For
every fault all of whose killing nodes lie inside a file the removal deletes,
`ENTAILED-SURVIVES` follows from `git show` alone and no other verdict is
reachable. So the verdict carried no information about the removal.

And the second half, which is worse because it is silent:

```
$ price_removal.py entail --before .../rm03-gap-mutants-before.json --head deadbeefdeadbeef
ENTAILED-SURVIVES   ... x4
exit=0
```

`node_present` answers `False` when `git show <head>:<path>` fails, and it failed
identically for *a path the removal deleted* and for *a head that names nothing*.
A typo'd, truncated or unfetched ref priced the whole table at exit 0.

---

## 2. `EXTINCT`, demonstrated on a real cut

`RM03-GM-RUNNER` is seeded into `examples/validation/gap_mutants/run_gap_mutants.py`,
which the removal at `6298eee` deletes whole.

```
EXTINCT             RM03-GM-RUNNER-an-unapplied-mutant-reports-a-survival
    habitat deleted by this removal: examples/validation/gap_mutants/run_gap_mutants.py
```

The distinction is one this repository had already written down and never
computed. `residual_faults.toml`'s `[[not_seedable]]` row:

> The fault class is EXTINCT, not UNWATCHED, and an extinct fault class costs
> nothing in the currency a gap mutant measures. What that removal DID cost is a
> CAPABILITY, NOT A DETECTION, and no gap mutant of any posture measures
> capability.

`ENTAILED-SURVIVES` says *a detection was taken away*. `EXTINCT` says *there is
nothing left to detect*. `is_priced_result` is false for it.

**It is head-sensitive, not a blanket downgrade.** RM-03 made two cuts. At
`1e6f691` (`card-dimensions-to-notes`) the same fault reads `UNDECIDED`, because
that removal does not touch its habitat. At `6298eee` it reads `EXTINCT`. One
fault, two heads, two verdicts — asserted by
`test_extinct_is_a_property_of_the_head_and_not_a_blanket_downgrade`.

### The bound, stated rather than left to be found

`EXTINCT` is file-granular, exactly as shallow as `node_present`. **A mechanism
RENAMED rather than deleted reads `EXTINCT` here and is not extinct.** It is an
upper bound on extinction in the same way `ENTAILED-SURVIVES` is an upper bound
on the price, and the bound travels with the verdict in `why`.

### The care that keeps it from cheapening SM-03

Habitat is read from the **edit ops**, never from the declared path list.
`SM-GM-I3-an-instrument-that-was-never-added-to-the-registry` edits
`scripts/gap_probe_instrument.py` with `op = "add_file"`, and that path is absent
at `bf0fb29` **because the mutant creates it**. Absence there is the fault's
precondition, not its extinction. A path-list rule would have called `SM-GM-I3`
extinct and lowered SM-03's price on a bookkeeping detail. Guarded by
`test_a_mutant_that_creates_its_own_habitat_is_never_extinct`.

---

## 3. A declared control can no longer be a priced result

`declared_control` reads the row's own declarations in the sealed table — never
its verdicts, which is what would let a result decide the exclusion:

| signal | what it says |
|---|---|
| `is_control` | the seeding author said so |
| `removed_by == "nothing"` | the removal is not on this row's causal path |
| `control_role` | a written role; a control that lost its flag |

All four controls in the sealed record — `SM-GM-CTRL-A`, `SM-GM-CTRL-B`,
`RM-01-RF-CTRL`, `RM03-GM-CTRL-C` — declare the first two together.

`test_no_declared_control_in_any_sealed_table_can_be_a_priced_result` sweeps
every published before-table against every head the record names, in **both**
modes, and gives `price` the most favourable input a control could have (the
before-table as its own after-table). All are `CONTROL-EXCLUDED`; none is a
priced result.

**EXCLUDED IS NOT HIDDEN.** RM-05's defect was a control row *missing from the
output*, not a control row being scored — a renderer that dropped controls to
keep the table tidy would reproduce the omission exactly. Controls are printed,
in their own block, outside every denominator.

**`denominator_rule`.** The `entail` denominator fell from 4 rows to **3
subjects**, with 1 declared control excluded, and the renderer prints the
excluded count beside it. **The numerator did not fall because a subject was
reclassified downwards; it fell because a row that was never a subject stopped
being counted as one.** A control leaving the denominator without leaving the
numerator is the direction that makes a price look *larger*, so the excluded
count is printed rather than absorbed.

---

## 4. `--head` is validated

`resolve_head` runs `git rev-parse --verify <head>^{commit}` before any verdict is
computed, and raises `HeadNotResolvable`. The CLI exits **2** and prints no
table. Validated in the functions as well as at the CLI, so an importer that
skips `main` cannot skip the check.

**R1 — the demonstrated failing input is a real one.** Not a fixture: the sealed
RM-03 before-table with `--head deadbeefdeadbeef`, which at the parent printed
four `ENTAILED-SURVIVES` rows at exit 0 and now prints
`error: --head 'deadbeefdeadbeef' does not name a commit ...`, exit 2.

---

## 5. The re-priced history — and the number is zero

`repriced-history-sweep.txt` beside this file, produced by `repriced_history.py`
beside it, which **imports the shipped `price_removal.py` and swaps DATA only**
so what is reported is the instrument that ships rather than a re-typed copy of
it (`PA-04-DF-02`). It asserts nothing and returns 0 whatever it finds — a
non-zero total is the informative outcome and it would print one. Every removal
in `removals.toml` that has a published before-table, at the head the manifest
names:

| removal | ticket | head | subjects | priced | controls excluded |
|---|---|---|---|---|---|
| `ports-binding-machinery` | SM-02 | `0342a3a` | 9 | **0** | 2 |
| `hardcoded-enumeration-literal` | SM-03 | `bf0fb29` | 9 | **0** | 2 |
| `dead-port-binding-report-detector` | RD-02 | `bfd04af` | 1 | **0** | 0 |
| `card-dimensions-to-notes` | RM-03 | `1e6f691` | 3 | **0** | 1 |
| `gap-mutant-catalogue-and-runner` | RM-03 | `6298eee` | 3 | **0** | 1 |
| `hardcoded-enumeration-literal` (RM-01 residual pair) | SM-03 | `bf0fb29` | 1 | **0** | 1 |

**TOTAL PRICED RESULTS ACROSS RE-PRICED HISTORY: 0. No non-zero appeared.**

The measured side agrees, which matters because it is an independent reading.
Against RM-03's own published after-table at `6298eee`:

```
FREE           RM03-GM-D4-...     something still catches it after the cut
FREE           RM03-GM-D5-...     something still catches it after the cut
NOT-IN-TABLE   RM03-GM-RUNNER-... it could not be re-run: there was nothing to re-run it in
```

`NOT-IN-TABLE` on the measured side is what `EXTINCT` predicts on the entailed
side, and RM-03's after-table could not have been otherwise.

**`audit`'s ten sealed rows did not move.** 10 rows, `0 of 10 disagree`, no
`PRICED`, no `CONTROL-EXCLUDED`, no `EXTINCT` — no control appears in any
removal's `gap_mutants`, and no catalogue fault's habitat is deleted by the
removal it is priced against. Pinned by
`test_the_correction_does_not_move_the_sealed_audit_record`, so if a future
change moves it, the numerator moved and `0 of 10` stops being RM-01's number.

---

## 6. Both known positives reproduce

| positive | reads | where |
|---|---|---|
| `RM-01-RF-1` | `PRICED` (`price`), `UNDECIDED` (`entail`) | `test_rm01s_known_positive_still_prices_after_the_correction` |
| `SM-04-GM-T1` | v2 `CAUGHT` `total 8 does not equal the sum of dimensions (6)`; v3 `UNCAUGHT`, `new_problems == []` | `test_sm04_gm_t1_reproduces_from_an_independent_implementation` |

`RM-01-RF-1` is not extinct and is not a control: its habitat is
`examples/validation/instruments/instruments.toml`, which SM-03's removal does
**not** delete — asserted directly, `_show("bf0fb29", ...)` is non-empty.

---

## 7. What was REJECTED

**Rendering `EXTINCT` as `FREE`, or counting it as a zero.** It is a refusal to
price. An extinct fault costs nothing *in the currency a gap mutant measures*,
and what a removal like this does cost is a capability, which nothing here
measures. Calling it `FREE` would assert the removal was safe on evidence that
does not exist.

**Reading habitat from the declared path list instead of the edit ops.** Simpler,
one line shorter, and it would have declared `SM-GM-I3` extinct at `bf0fb29` and
made SM-03's removal look cheaper. §2.

**Dropping control rows from the rendered table.** Tidier, and it is precisely the
failure RM-05 found. Controls are printed and excluded, not hidden.

**Fixing `RM-05-DF-02` — `price` returning `PRICED` over an all-`INERT`
after-table — inside this commit.** It still reproduces and is filed as
`CL-02-DF-02`. Refusing an all-undecidable after-table can only turn a `PRICED`
into a refusal, which makes past removals look **cheaper**; making that change in
the commit that reports a re-priced history is the tuning this goal fails a
ticket for.

**Pinning `RECORD`'s floating `head = "HEAD"`** for `dead-port-binding-report-detector`,
which `removals.toml` pins to `bfd04af`. Filed as `CL-02-DF-01`. Changing it moves
`audit`'s ten sealed rows in the same commit as the measurement taken against them.

**Repairing `test_nothing_in_the_repository_invokes_the_pricer`.** Inherited
deliberately; it now names two narrative documents because this epic's charter
mentions `price_removal`. Not repaired, not allow-listed, and not deepened — no
new mention of the pricer was added outside `specs/`.

**Nothing was adjusted after a result was seen.** The four-row and unresolvable-head
transcripts in §1 were captured at the parent before any edit, and are in the tree.

---

## 8. The suite, with its tree

**`2 failed, 1492 passed in 1099.20s`**, `uv run --with pytest --with pyyaml
python -m pytest tests -q`, in the real checkout
`/Users/hayde/IdeaProjects/wt-epic-close-the-loop-CL-02` at `feature/CL-02`
(working tree, parent `10cf11a`). **Not a `git archive` tree** — several of these
nodes read git history and an archive has no `.git`.

**The two failures are the two inherited deliberate reds, and neither was
repaired:**

| node | why it is red |
|---|---|
| `tests/test_architecture_tags.py::test_the_same_tag_control_holds` | `RM-06-DF-01` — the same-tag control cannot tell treatment from architecture |
| `tests/test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer` | now names **two** narrative documents: `NEXT-EPIC.md` and `CLOSE-THE-LOOP-EPIC.md`, because this epic's own charter mentions `price_removal` |

### `denominator_rule` on the suite count

Baseline **1479 collected** (2 failed + 1477 passed) at `10cf11a`, measured by
`--collect-only` on a clean checkout of that commit. Now **1494 collected**
(2 failed + 1492 passed). **+15, and the failure count did not move.**

| delta | file | cause |
|---|---|---|
| **+11** | `tests/test_price_removal.py` | THE NUMERATOR ROSE — the eleven tests this ticket adds, all passing, all of which fail at `10cf11a` |
| **+4** | `tests/test_spec_yaml_valid.py` | THE DENOMINATOR ROSE — it is parametrized over spec YAML files, and `open ticket CL-02` scaffolded a ticket workspace containing more of them |

The `+4` is `+6 −2`: `complexity_ledger.yaml` and `ticket.yaml` were unique
parameter ids at the parent and became `…0`/`…1` once a second of each existed,
and two `spec_manifest.yaml` ids are new. **No test was removed, skipped or
weakened**, and nothing in the removed pair is a lost assertion.

### Every new behaviour fails on the parent

All eleven were run against `10cf11a`'s `price_removal.py` with the new test file
in place: **11 failed, and the head-validation one fails by printing the four
`ENTAILED-SURVIVES` rows at exit 0** rather than by a missing attribute.

## 9. Reproduce

```
git checkout feature/CL-02        # or 10cf11a for the "before" column

python3 examples/validation/gap_mutants/price_removal.py entail \
  --before specs/results/scorecards/portable-substrate/GOAL-dead-weight-gone/rm03-gap-mutants-before.json \
  --head 6298eee                         # EXTINCT + CONTROL-EXCLUDED; at 10cf11a, two ENTAILED-SURVIVES

python3 examples/validation/gap_mutants/price_removal.py entail \
  --before specs/results/scorecards/portable-substrate/GOAL-dead-weight-gone/rm03-gap-mutants-before.json \
  --head deadbeefdeadbeef                # exit 2; at 10cf11a, four ENTAILED-SURVIVES at exit 0

python3 specs/results/scorecards/close-the-loop/GOAL-price-means-something/repriced_history.py
                                         # TOTAL PRICED RESULTS ACROSS RE-PRICED HISTORY: 0

uv run --with pytest --with pyyaml python -m pytest tests/test_price_removal.py -q
python3 examples/validation/scorecards/score_tools.py serve | wc -c   # 6319, unchanged
```

`parent-10cf11a-same-commands.txt` is the same two commands captured at the
parent, before a line of this ticket was written.

**No new gates.** Nothing in the repository invokes the pricer, no close path
consults it, and its exit code refuses nothing about the design.
