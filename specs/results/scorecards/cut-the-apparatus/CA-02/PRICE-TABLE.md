# `CA-02` price table — the gap-mutant / removal-pricing machinery

**Format:** `specs/results/scorecards/cut-the-apparatus/GOAL-apparatus-cut/PRICE-TABLE-FORMAT.md`
**Base commit:** `37ab155b1c54724666031cd4698d7fdff58423b5` (`origin/epic/cut-the-apparatus`)
**Measured on:** this ticket's worktree, `feature/CA-02`.

---

## 0. CORRECTIONS — the cut is right, the first stated reasons were not

**Independent review of PR #264 returned RECOMMEND CHANGES on the PROSE, not the
tree.** The line accounting reproduced at three commits, the ledger is
append-only at the byte level, the sealed record still reads, and the suite
conclusion survives. **What follows is what this table claimed first, what the
record actually says, and who owns each error.** Nothing in the tree changed to
produce this section.

**The origin is the epic owner's, and it is filed as
[`CA-00-DF-05`](../../../../desired_program_model/deferred_findings.yaml)
(major, open) — read that row alongside this section; the two are one record,
not two.** Issue #254's sentence *"the removal-pricing instrument could only
ever return zero… 0 of 9 over the sealed table"* was copied into
`CUT-THE-APPARATUS-EPIC.md`, the canonical plan, the `GOAL-four-results-stand`
baseline **and `CA-02`'s work order** without being run against the record.
`CA-00-DF-05` names the origin as the owner's and records that **`CA-02` was the
ticket told to *"CHECK THAT DEPENDENCY EXPLICITLY"*.**

**So a share is this ticket's, and this table states it in its own words rather
than deferring to that row:** `CA-02` propagated the assertion instead of
checking it, and then **added a citation the owner never made** — `RD-02`, the
one ticket that had explicitly refused this deletion. `CA-00-DF-05` records the
class as *"a scoped result restated as an unqualified fact… the project's own
costliest recurring error, committed in the document that governs eight
tickets"*. **`R3` and `scope` exist to catch exactly this and neither the
charter's author nor this ticket ran them.**

| # | what this table claimed | what the record says | owner |
|---|---|---|---|
| 1 | `RD-02` cited as authority for deleting the pricer and the census | **`RD-02` REFUSED this deletion.** It titles itself *"the apparatus is load-bearing"*, and `RD-02-RESULT.md:292` says *"It is not deleted, and the reason is `MF-020` turned on myself: removing the instrument that prices removals removes the ability to detect that a removal was harmful."* It also scopes its `0 of 9` explicitly as **not** a claim about every mutant, and filed **`RD-02-DF-02` (major, open)** against exactly this restatement. | **CA-02** — added, not inherited |
| 2 | *"the instrument could only ever return zero"* | `NEXT-EPIC.md` §5: *"A non-zero was the informative outcome, **the instrument would have printed one**, and none appeared… The goal is met and **the instrument is not yet useful**."* `RM-02` §10.2: *"**the instrument can fire**, history remains free."* | **`CA-00-DF-05`** — owner's assertion, CA-02 propagated |
| 3 | *"`priced rows: []`, 0 of 10"* as one figure | **Two different statistics conflated.** `0 of 10 disagree with the measurement` is an **audit-agreement** count — *"`audit`'s ten sealed rows did not move"*. `priced rows: []` is the re-pricing sweep. And nine lines below it the same transcript prints `PRICED RM-01-RF-1…`, under the heading *"RM-01's known positive, measured (price, not entail)"*. **CL-02's headline keeps the exception this table dropped.** | **CA-02** |
| 4 | `RM-05-DF-01`'s *"no other verdict is reachable"* given as the standing reason to delete | **It describes the file BEFORE `CL-02` repaired it.** The file deleted here CONTAINS that repair — `EXTINCT`, `resolve_head`, `CONTROL_EXCLUDED`. The retirement row cited a repaired-and-closed defect as the reason to delete the repair. | **CA-02** |
| 5 | suite denominator `1566 → 1532` | **Measured: `1562 → 1528`.** Same −34 delta, **both endpoints wrong**. 1566 was DERIVED as `1532 + 34`; 1562 is what the epic baseline already records (both discarded runs collected 1562). 1532 was the count at `2244095` only, inflated by six `test_source_citations` params over this ticket's own `specs/tickets/CA-02/` workspace, which the close then moved to `.history`. **On a ticket whose whole frame is `denominator_rule`, in an epic whose baseline says that 7 *"was DERIVED, and has since been MEASURED"* — the same error one layer down.** | **CA-02** |
| 6 | *"the instrument that produced disproof 3 still runs at the tip"* | **It does not.** `specs/.../GOAL-price-means-something/repriced_history.py:21` loads the deleted `price_removal.py` and now dies with `FileNotFoundError`. **Disproof 3 is readable but no longer RE-DERIVABLE.** §5 of this epic's own price-table format demands that answer, and this table gave the wrong one in the single row where it matters most. | **CA-02** |

**What does not change:** the cut itself, every line figure, the card, the suite
conclusion, and `CA-02-DF-01`. **The reviewer confirmed `CA-02-DF-01`
independently and made it stronger** — there are **zero references to any pricer
symbol anywhere in `scripts/`**, which is **63.5%** of the goal's denominator,
and the **11,850**-line gap to the target is exact.

**Two artifacts still carry the SUPERSEDED wording, deliberately.** The sealed
close-history narrative at
`specs/.history/cut-the-apparatus-epic/ticket-001-CA-02`, and the copy of it the
close wrote into `specs/results/complexity_ledger.json`. **Neither is rewritten**
— sealed close output is not edited after the fact, which is the same rule that
stops this ticket repairing `repriced_history.py` — and **this section is what
supersedes both**. A reader who finds the old sentences there should read them
against this table.

**The charter and the goal baseline were the epic owner's to correct, and they
now ARE.** This paragraph previously said they *"both still list"* the refuted
sentence; **that stopped being true at `fc39224`** and the claim is withdrawn
here rather than left to rot. `CUT-THE-APPARATUS-EPIC.md` §2 now reads *"the
removal-pricing instrument **is not yet useful**"* under a `CA-00-DF-05`
correction block; the `GOAL-four-results-stand` disproof row was rewritten the
same way and marked `(CORRECTED, CA-00-DF-05)`; the canonical plan went with
them. The only occurrences of the old wording left in either file are **inside
those correction blocks, quoting what they used to say** — the same shape as
this section. **Checked against the merged tree, not assumed.**

---

## 1. Removals — every row names the finding that justifies it

| surface | path | lines | kind | finding |
|---|---|---|---|---|
| `examples/validation/` | `gap_mutants/price_removal.py` | 838 | py | `RM-05-DF-01`, `CL-02` |
| `examples/validation/` | `gap_mutants/altered_score_probe.py` | 177 | py | `RM-02` |
| `examples/validation/` | `gap_mutants/residual_faults.toml` | 193 | toml | `RM-02` |
| `examples/validation/` | `removal_census/removal_census.py` | 429 | py | `RM-02`, `CL-02` |
| `examples/validation/` | `removal_census/removals.toml` | 712 | toml | `RM-02` |
| `tests/` | `test_price_removal.py` | 602 | py | `RM-05-DF-01`, `CL-02` — tests only the above |
| `tests/` | `test_removal_census.py` | 286 | py | `RM-02`, `CL-02` — tests only the above |

**The findings, stated once so the table is readable on its own.** These
statements are the CORRECTED ones; §0 above records what they said first and why
that was wrong.

- **`RM-02` — the load-bearing reason, and the only one that carries the cut on
  its own.** The catalogues are `ab_quota_ledger` fixtures with **no version an
  adopter receives**, and that argument *"survives a zero and survives a
  defective classifier producing one, **because it is not a pricing
  argument**."* It therefore does not depend on any pricing number being right,
  which matters here because the pricing numbers were misread.
- **`NEXT-EPIC.md` §5 — what the instrument actually did.** *"A non-zero was the
  informative outcome, **the instrument would have printed one**, and none
  appeared… The goal is met and **the instrument is not yet useful**."* That is
  the defensible sentence: **not yet useful**, not incapable.
- **`RM-02` §10.2 reads the same sweep the same way** — *"and still returned
  **0 of 10 PRICED**: **the instrument can fire**, history remains free."*
- **`CL-02`** — re-priced every historical removal with a published before-table
  and got **0 priced results in that sweep** (`priced rows: []`), while its own
  headline keeps the exception: ***"`RM-01-RF-1` is still `PRICED` and is still
  the only price this project has."*** The removal the census had claimed a
  non-zero price for reads `EXTINCT` — **not a price and not a zero, a refusal
  to measure**.
- **`RM-03`** — the *"first PRICED removal"* was **withdrawn** when its own
  zero-gap control returned the same verdict. `RM-01`'s price was not withdrawn
  with it.
- **`RM-05-DF-01`** — for a fault whose killing nodes all lie in a file the
  removal deletes, `ENTAILED-SURVIVES` follows from `git show` alone. **Scoped
  carefully**: that finding also says, pre-emptively, *"WHAT SURVIVES, STATED SO
  THIS FINDING CANNOT BE QUOTED AS 'THE EPIC PRICED NOTHING'… The epic HAS a
  priced removal."* **And it describes the file BEFORE `CL-02` repaired it** —
  see §0, item 4.

**`RD-02` is deliberately NOT cited.** It was cited here in the first version of
this table and that citation was wrong; see §0, item 1.

## 2. Additions — mandatory, and not empty

| surface | path | lines | kind | why |
|---|---|---|---|---|
| `examples/validation/` | `gap_mutants/RETIRED.md` | 63 | md | **Keeps a sealed subject's declared scope resolvable.** `subject.rm04_removal_pricer` declares `scope = ["examples/validation/gap_mutants"]`; deleting the directory outright would leave a sealed card pointing at nothing. Costs **0 Python lines**. |
| `examples/validation/` | `instruments/instruments.toml` | **-45 net** | toml | Three `[[retired]]` records replacing three `[[instrument]]` rows, plus the re-pointed staging and the updated derivation figure. A capability that leaves a registry without a row is `FI-04-DF-04`. |
| `specs/` | `GOAL-apparatus-cut/PRICE-TABLE-FORMAT.md` | 96 | md | The epic's price-table format. **No code**, by construction. |
| `specs/` | `CA-02/PRICE-TABLE.md` | this file | md | The worked instance. |

**`instruments.toml` net movement, both endpoints given** — broken out rather
than netted, because this table's whole point is that additions get counted:

```
2,673  at CA-02's base 37ab155
2,628  CA-02 alone (-45):  -150 three instrument rows
                           +  8 staging comment
                           + 97 three retired records
2,703  AT THE RECONCILED PR HEAD (+75 against CA-02 alone)
```

**The +75 is `CA-01`'s `blind-dispatch-check` row, not this ticket's**, and the
reconciled figure was missing from the first version of this table. Same
discipline as the Python columns: **`CA-02` alone and the integrated tip are two
different measurements and neither substitutes for the other.**

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
`NO-KILL-TO-LOSE` verdict, no `entail`, no `price`.

**What the record says that capability was worth, stated correctly.** `CL-02`
re-priced every historical removal carrying a published before-table and got
**0 priced results in that sweep**. It did **not** find the instrument
incapable: `NEXT-EPIC.md` §5 is explicit that *"a non-zero was the informative
outcome, **the instrument would have printed one**, and none appeared… the
instrument is **not yet useful**"*, and `RM-02` §10.2 reads the same sweep as
***"the instrument can fire**, history remains free."* **And one price stands:
`RM-01-RF-1` is `PRICED` and is, in `CL-02`'s own words, *"still the only price
this project has."*** What was removed is an instrument that **had fired once in
the project's history and was not yet useful**, not one that could never fire.

`RM-03` had already recorded that `price` reads a measured after-table **nothing
in this repository produces any more**, and kept `entail` on soundness grounds.
**The earlier version of this table justified deleting `entail` by quoting
`RM-05-DF-01`'s "no other verdict is reachable" — which describes the file
BEFORE `CL-02` repaired it**, and the file deleted here contains that repair
(`EXTINCT`, `resolve_head`, `CONTROL_EXCLUDED`). So the honest statement of what
`entail` cost is **not** that its answer was foregone; it is that after `CL-02`'s
repair it was a sound instrument with **no measured after-table in the repository
to run against**, on catalogues **no adopter receives** — which is `RM-02`'s
argument, and `RM-02`'s argument alone.

**It cannot compute whether a removal is discriminating.** `removal_census.py
discriminate`'s own registry row recorded that the condition is computed over
**detector names** and is unsound in both directions — `pytest-full` is the whole
suite, which no removal deletes, so any fault the suite kills was classified
`NON-DISCRIMINATING` before anything ran. **`RD-02`'s `0 of 9` is deliberately
not quoted here**: it is scoped to one catalogue, `RD-02` refused this very
deletion, and `RD-02-DF-02` (major, open) is filed against restating it more
broadly. See §0, item 1.

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
| **Disproof 3** (*"the removal-pricing instrument returned no price over the sealed history"*) | **READABLE — but NOT re-derivable. This is the row this cut broke.** | Its transcripts are sealed under `specs/.../GOAL-price-means-something/` and `.../GOAL-removal-can-be-priced/` and are untouched, so the result still READS. **The instrument that produced it does NOT still run at the tip**: `specs/.../GOAL-price-means-something/repriced_history.py:21` loads the deleted `price_removal.py` and now dies with `FileNotFoundError` (reproduced, not assumed). §5 of this epic's format demands exactly this answer and the first version of this table gave the wrong one. `CA-02-DF-04`. |

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

baseline:  7 reds / 1562 collected   (2 deliberate, 4 inherited-undeclared,
                                      1 CA-00-DF-02)
at head:   6 reds / 1528 collected

movement:  NUMERATOR   7 -> 6      (-1)
           DENOMINATOR 1562 -> 1528 (-34 tests collected)
cause:     test_nothing_in_the_repository_invokes_the_pricer was DELETED WITH
           ITS SUBJECT, along with the other 33 tests in the two deleted test
           files (22 in test_price_removal.py, 12 in test_removal_census.py).
           IT WAS NOT REPAIRED.
```

**BOTH ENDPOINTS ARE MEASURED, and the first version of this table had both
wrong.** It reported `1566 -> 1532`: 1566 was **derived** as `1532 + 34`, and
1532 was `pytest --collect-only` at `2244095`, a commit whose tree still carried
this ticket's own `specs/tickets/CA-02/` workspace and therefore six extra
`test_source_citations` parametrisations that the close then moved to
`.history`. **1562** is the count both discarded epic-base runs collected
(`9 + 1553` and `12 + 1550`) and is what the epic baseline already records;
**1528** is `--collect-only` at this PR head. The **−34 delta was right in both
tellings**, which is exactly why the wrong endpoints survived a self-check — see
§0, item 5.

```
runs:      6 failed, 1526 passed in 1092.83s (0:18:12)  @ f92f0a5  (pre-merge)
           6 failed, 1526 passed in 1130.91s (0:18:50)  @ 2244095  (reconciled)
           6 failed, 1522 passed in 1167.65s (0:19:27)  @ 148a155  (PR HEAD)
           SAME SIX FAILURES IN ALL THREE. 1522 + 6 = 1528 = collection.
evidence:  specs/results/scorecards/cut-the-apparatus/CA-02/pytest-repo-unit.txt
           specs/results/scorecards/cut-the-apparatus/CA-02/pytest-repo-unit-reconciled.txt
           specs/results/scorecards/cut-the-apparatus/CA-02/pytest-repo-unit-head.txt
```

**PROVENANCE OF THE EVIDENCE, stated because it was not stated before.** The two
committed transcripts were produced at `f92f0a5` and `2244095` — **neither is the
PR head**. `2244095` precedes the close commit, which rewrites
`specs/desired_program_model/ticket_plan.yaml` and moves `specs/tickets/CA-02/`
— and **two of the six reds read those paths at test time**
(`test_ticket_retirement`, `test_source_citations`). So the committed evidence
was consistent with the conclusion but **did not establish it at the head**.

**A third run at `148a155` now does**, recorded in `pytest-repo-unit-head.txt`:
**6 failed, 1522 passed**, the same six failures, and `1522 + 6 = 1528` matches
the measured collection exactly. The passed count differs from the earlier runs
by precisely the six collection items the close removed. **The only delta
between the run commit and the PR head is that transcript and this paragraph**,
and neither can enter collection — `CITATION_SCOPE` is a fixed glob list
(`scripts/*.py` plus three named manifests), so nothing under
`specs/results/scorecards/` is collectable. Verified by reading the constant,
not assumed.

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

## 6a. The findings ledger, with its provenance stated correctly

**212 → 225 rows**, append-only, ids unique, both loaders, every row
dispositioned. The 13 added since the epic base split as:

| rows | whose | which |
|---|---|---|
| 2 | **the epic owner**, via `CA-01`'s independent reviewer | `CA-00-DF-03`, `CA-00-DF-04` |
| 6 | `CA-01` | `CA-01-DF-01` … `CA-01-DF-06` |
| 5 | `CA-02` | `CA-02-DF-01` … `CA-02-DF-05` |

**The first version of this record said "preserving `CA-01`'s 8".** Six are
`CA-01`'s; **two are the owner's**, filed by the reviewer dispatched against
`CA-01`. Corrected here. The merge that combined them was resolved by rebuilding
from the epic tip and re-appending, not hunk-by-hunk, so neither ticket's rows
could be dropped — and it was verified that `CA-01` modified none of the 212 base
rows.

**`channel` and `cost` are a PROPOSAL, and `CA-05` owns the schema.** `CA-02` is
`enabling` on `GOAL-consumption-obligatory` with `expected_effect: none`;
populating those fields is `CA-05`'s `direct` contribution and **this ticket
pre-empted it**. The fields stay, per the epic owner, but **`CA-05` may rewrite
this shape and `CA-02` does not defend it.** Two review criticisms are recorded
in each row's `schema_note` rather than argued with: **`channel` is free-text
sentences, not a controlled vocabulary**, so a findings-by-channel table still
needs hand classification — the exact work the field exists to eliminate; and
**`cost.value` is `"negligible"` in four of five rows with no token basis**,
while `CA-08` requires the basis be named.

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
