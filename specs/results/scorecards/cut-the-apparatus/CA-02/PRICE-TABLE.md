# `CA-02` price table — the gap-mutant / removal-pricing machinery

**Format:** `specs/results/scorecards/cut-the-apparatus/GOAL-apparatus-cut/PRICE-TABLE-FORMAT.md`
**Base commit:** `37ab155b1c54724666031cd4698d7fdff58423b5` (`origin/epic/cut-the-apparatus`)
**Measured on:** this ticket's worktree, `feature/CA-02`.

---

## 1. Removals — every row names the finding that justifies it

| surface | path | lines | kind | finding |
|---|---|---|---|---|
| `examples/validation/` | `gap_mutants/price_removal.py` | 838 | py | `RM-05-DF-01`, `CL-02` |
| `examples/validation/` | `gap_mutants/altered_score_probe.py` | 177 | py | `RM-02` |
| `examples/validation/` | `gap_mutants/residual_faults.toml` | 193 | toml | `RM-02` |
| `examples/validation/` | `removal_census/removal_census.py` | 429 | py | `RM-02`, `RD-02` (0 of 9), `CL-02` |
| `examples/validation/` | `removal_census/removals.toml` | 712 | toml | `RM-02` |
| `tests/` | `test_price_removal.py` | 602 | py | `RM-05-DF-01`, `CL-02` — tests only the above |
| `tests/` | `test_removal_census.py` | 286 | py | `RM-02`, `RD-02` — tests only the above |

**The findings, stated once so the table is readable on its own:**

- **`RM-05-DF-01` / `CL-02`** — for every fault all of whose killing nodes lie in
  a file the removal deletes, **`ENTAILED-SURVIVES` follows from `git show`
  alone** and no other verdict is reachable. `CL-02` re-priced the entire sealed
  history over kill sets: **`priced rows: []`, 0 of 10.** The instrument was
  sound and its answer was fixed in advance.
- **`RM-03`** — the *"first PRICED removal"* was **withdrawn** when its own
  zero-gap control returned the same verdict.
- **`RM-02`** — the catalogues are `ab_quota_ledger` fixtures with **no version
  an adopter receives**, and that argument *"survives a zero and survives a
  defective classifier producing one, because it is not a pricing argument."*
  It therefore does not depend on `CL-02`'s zero being correct.
- **`RD-02`** — a gap mutant can price a removal only if every detector that
  killed it is one the removal deletes: **0 of 9** over the sealed table.

## 2. Additions — mandatory, and not empty

| surface | path | lines | kind | why |
|---|---|---|---|---|
| `examples/validation/` | `gap_mutants/RETIRED.md` | 63 | md | **Keeps a sealed subject's declared scope resolvable.** `subject.rm04_removal_pricer` declares `scope = ["examples/validation/gap_mutants"]`; deleting the directory outright would leave a sealed card pointing at nothing. Costs **0 Python lines**. |
| `examples/validation/` | `instruments/instruments.toml` | **-45 net** | toml | Three `[[retired]]` records replacing three `[[instrument]]` rows, plus the re-pointed staging and the updated derivation figure. A capability that leaves a registry without a row is `FI-04-DF-04`. |
| `specs/` | `GOAL-apparatus-cut/PRICE-TABLE-FORMAT.md` | 96 | md | The epic's price-table format. **No code**, by construction. |
| `specs/` | `CA-02/PRICE-TABLE.md` | this file | md | The worked instance. |

**`instruments.toml` net movement:** 2,673 → 2,628 lines (**-45**), and it is
broken out rather than netted because this table's whole point is that additions
get counted: **-150** for the three instrument rows, **+8** for the staging
comment, **+97** for the three retired records.

**No new Python was added by this ticket. The `.py` count for additions is zero.**

## 3. Net figures, per surface, never combined with the card

```
surface                 before      after       delta
scripts/                 27,652     27,652          0
examples/validation/     15,901     14,457     -1,444
--------------------------------------------------------
local_signal total       43,553     42,109     -1,444

tests/                   32,162     31,274       -888
```

Measured with the goal's own command on this tree:

```
find scripts examples/validation -name '*.py' -not -path '*/__pycache__/*' | xargs wc -l | tail -1
```

### After reconciling with the epic tip — a second figure, not a correction

Merging `CA-01` (`a6bdf42`) into this branch adds
`examples/validation/instruments/blind_dispatch.py`, **+228 lines**:

```
surface                 base        CA-02 alone   reconciled tip
scripts/                 27,652     27,652        27,652
examples/validation/     15,901     14,457        14,685
-----------------------------------------------------------------
local_signal total       43,553     42,109        42,337
```

**These are two different measurements and must not be quoted
interchangeably.** `CA-02` removed **1,444** lines. The reconciled tip is
**-1,216** against the base because a sibling ticket added 228 back.
`denominator_rule`: against the base denominator of 43,553, this ticket's
numerator contribution is **-1,444**, and the tip's net is **-1,216**. **`CA-08`
decides the goal on the integrated tip, not on this ticket's figure**, and the
30% target (≤30,487) is a further **11,850 lines** away — see `CA-02-DF-01`.

**The card, reported separately and added to nothing:**

```
examples/validation/scorecards/score_tools.py serve | wc -c
  6,281 -> 6,281        UNCHANGED
serve --digest-only
  sha256:2d7d4a0506d9b259 -> sha256:2d7d4a0506d9b259   UNCHANGED
```

**`scripts/` did not move, and that is a finding rather than an omission** — see
§7.

## 4. What the tree can no longer do

**It cannot price a removal.** No `ENTAILED-SURVIVES` / `FREE` /
`NO-KILL-TO-LOSE` verdict, no `entail`, no `price`. **What the record says that
capability was worth: `CL-02` ran it over ten sealed before/after rows and
returned `priced rows: []` — zero.** `RM-03` had already recorded that `price`
reads a measured after-table **nothing in this repository produces any more**,
and kept `entail` on soundness grounds. `CA-02`'s finding is that soundness was
never the binding constraint: **the sound half is the half whose answer was
determined by `git show` before it ran.**

**It cannot compute whether a removal is discriminating.** `removal_census.py
discriminate` measured that condition at 0 of 9, and its own registry row
recorded that the condition is computed over **detector names** and is unsound in
both directions — `pytest-full` is the whole suite, which no removal deletes, so
any fault the suite kills was classified `NON-DISCRIMINATING` before anything
ran.

**It cannot refuse a stale removal manifest**, because there is no removal
manifest. The **1,677-line** figure that manifest existed to keep honest is in
the sealed record, and this epic's price-table format §2 carries the discipline
forward as a mandatory column.

**It cannot re-run `SM-04-GM-T1` from an independent implementation** — the only
mutant in this project's history that went `DIES -> SURVIVES`. **The finding
stays readable in the sealed record; what is lost is the ability to reproduce it**,
on a fixture no adopter has.

## 5. Sealed results — checked, not assumed

| sealed result | still stands? | how it was checked |
|---|---|---|
| **1. Asking for an architecture changes the architecture** | **yes** | Rests on `examples/validation/ab/arm_a`, `arm_b`, `arm_c` and `specs/results/scorecards/ports-as-adapters/`. None touched. |
| **2. D3 separates architectures on more than one example** | **yes** | Rests on `rm04_scripts` (scope `scripts/`, **byte-identical**, 0 lines moved) vs `rm04_eval_harness` (scope `examples/validation`). `rm04_removal_pricer` **is named in no separation claim** — the baseline says so explicitly. |
| **3. D3's v5 caveat discriminates** | **yes** | `SV-01`, scored on a copy of `arm_b`'s tree under `specs/`. Not touched. |
| **4. A score can produce a test and the re-score sees it** | **yes** | `SV-04`, sealed under `specs/results/scorecards/score-drives-validation-sv04/`. Not touched. |
| **`HISTORY-toolchain_removal.md`** | **reads** | 8,158 bytes, opens and renders. **It contains no reference to `price_removal`, `removal_census`, `altered_score_probe`, `residual_faults` or `gap_mutant`** — checked by grep, not assumed. |
| **Disproof 3** (*"the instrument could only ever return zero"*) | **yes, and it is the justification for this cut** | Its evidence is `CL-02`'s sealed `priced rows: []` and `RD-02`'s 0 of 9, both under `specs/`. |

### The one sealed thing this cut DID move, stated rather than buried

**`subject.rm04_removal_pricer` became underivable.** Its declared scope is
`examples/validation/gap_mutants`, and that directory now holds only a tombstone,
so the tag derivation reports `UNDERIVABLE:no-effect-surface` for it.

```
before:  17 of 21 subject(s) decided; 4 refused
after:   16 of 21 subject(s) decided; 5 refused
```

**`denominator_rule`: the numerator FELL 17 -> 16; the denominator HELD at 21.**
Nothing left the population — the subject is still declared and its sealed cards
(`portable-substrate-rm04-JJ`) still read. It lost its effect surface, not its
membership. Refusals rose 4 -> 5, and **`CA-02` is the first step at which a
decision became a refusal**: the four previous moves of this figure
(13/17 -> 16/20 -> 17/21) were all upward and all caused by someone *declaring* a
subject. `RD-06-DF-04` predicted the figure would move whenever a subject was
declared; it was **right about the mechanism and incomplete about the direction**.

The `registry-enumeration-coverage` demonstration also had to be re-pointed: it
staged `altered_score_probe.py` purely as *a file satisfying the executable
predicate*. It now stages `examples/validation/instruments/demonstrate.py`, which
is that instrument's own `paths` entry and so cannot go stale independently of
the row citing it.

**The D2 before/after that `portable-substrate-rm04-JJ` scored is NOT lost.** Its
before tree is materialised in the repository at
`specs/results/scorecards/portable-substrate/GOAL-dimensions-replicate/RM-04/blind/artifact_JJ_before`
and is untouched by this cut.

## 6. Suite movement under `denominator_rule`

```
command:   uv run --with pytest --with pyyaml -m pytest tests -q
measured:  6 failed, 1526 passed in 1092.83s (0:18:12)   @ f92f0a5
evidence:  specs/results/scorecards/cut-the-apparatus/CA-02/pytest-repo-unit.txt

baseline:  7 reds / 1566 collected   (2 deliberate, 4 inherited-undeclared,
                                      1 CA-00-DF-02)
after:     6 reds / 1532 collected

movement:  NUMERATOR  7 -> 6   (-1)
           DENOMINATOR 1566 -> 1532 (-34 tests collected)
cause:     test_nothing_in_the_repository_invokes_the_pricer was DELETED WITH
           ITS SUBJECT, along with the other 33 tests in the two deleted test
           files (22 in test_price_removal.py, 12 in test_removal_census.py).
           IT WAS NOT REPAIRED.
```

**Zero new reds.** The six that remain are exactly the baseline seven minus the
deleted one, each still failing for its own recorded cause:

| red | status |
|---|---|
| `test_the_same_tag_control_holds` | DELIBERATE (`RM-06-DF-01`) — **intact, unrepaired** |
| `test_a_real_epic_plans_judged_baseline_cannot_be_re_opened` | `CA-00-DF-02` — intact |
| `test_source_citations` × 3 (the three spec manifests) | inherited-undeclared — intact |
| `test_ticket_retirement…close_receipts` | inherited-undeclared — intact |

`test_every_fast_demonstration_reproduces` is **green**: the
`architecture-tag-derivation` figure was updated to `16 of 21` in the same commit
that caused it to move, so the cut did not leave a stale demonstration behind.

### A run that is NOT the baseline, recorded rather than deleted

**Run 1 was discarded.** It was killed by the harness at 79% with no summary
line, after competing for CPU with **two concurrent full-suite runs from another
session's `CA-01` review** (3 suites on one machine; my pytest sat at 0% CPU in
`SN` state). It was *also* contaminated by this ticket writing
`local-signal-apparatus-cut.txt` into `specs/` while it was in flight — **the
same class as the epic owner's contaminated kickoff baseline, committed by the
ticket that had been warned about it.** Run 2 was launched detached on a clean,
fully-committed tree with nothing edited during it.

### The deliberate pricer-grep red: deleted, not repaired

`tests/test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer`
is one of the two deliberate reds. **This ticket deleted the file it lived in,
because that file tests only the pricer.** That is a **denominator** move.

**It was never a code failure.** The test runs `git grep -l price_removal` and
allows every code path that legitimately names it. At the base, exactly **two**
files tripped it, and both are narrative documents:

```
CLOSE-THE-LOOP-EPIC.md
NEXT-EPIC.md
```

`RM-05` recorded the same thing when it first went red:

> *"the available repair is the test's own allow-list; taking it would be editing
> a target so a result passes, which an evaluation may not do."*

**So the honest accounting is:**

- The red is **gone from the count**, and **not one line of its cause was fixed**.
  Both narrative documents still name `price_removal`, and this price table names
  it many times more.
- Had the test been **kept**, it would be **red for exactly the same reason
  today** — prose, not code. Its subject is gone; its cause is not.
- **Nothing was repaired and nothing should be reported as repaired.** The
  numerator fell because the assertion left the suite, not because the tree
  changed to satisfy it.

**The other deliberate red — `RM-06-DF-01`'s
`test_the_same_tag_control_holds` — is untouched and still red.**

## 7. What this ticket REJECTED

- **Cutting anything from `scripts/complexity_ledger.py`.** The work order
  anticipated *"whatever in `complexity_ledger.py` exists only to feed them."*
  **Measured: nothing does.** A search of all 1,245 lines for `gap_mutant`,
  `price`, `removal`, `residual`, `census` and `mutant` returns **one** hit — the
  word *"removed"* inside an unrelated prose string at line 854. The file does
  not import, invoke or reference any cut surface, and it does not even satisfy
  the registry's executable predicate. **`scripts/` therefore moved zero lines,
  and `tests/test_complexity_ledger.py` was not touched.** Cutting it to make the
  `scripts/` column non-zero would have been a cut with no finding behind it —
  clause (b) of `GOAL-apparatus-cut` failing even though the lines fell.
- **Repairing the pricer-grep red by widening its allow-list**, and the tidier
  variant of the same move — keeping the test after deleting its subject. Both
  are `RM-05`'s *"editing a target so a result passes."*
- **Deleting `examples/validation/gap_mutants/` outright.** It is a sealed
  subject's declared scope. The tombstone costs 0 Python lines and keeps the
  record readable.
- **Deleting the three registry rows instead of retiring them.** `FI-04-DF-04` is
  exactly the class of a capability vanishing from a registry without a row.
- **Writing a price-table generator.** A tool for measuring the cutting of
  apparatus is apparatus, and `RD-02`'s census is the worked example of that
  becoming a thing a later ticket has to remove.
- **Restoring a Python file under `gap_mutants/` to keep the derivation at
  17 of 21.** That is fitting the tree to a demonstration's expected output —
  `MF-020`. The figure was updated and the movement stated instead.
- **Touching `tests/test_architecture_tags.py`.** It is outside this ticket's
  conflict keys and carries a deliberate red.
