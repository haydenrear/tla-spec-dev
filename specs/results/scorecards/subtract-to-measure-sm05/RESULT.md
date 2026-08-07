# SM-05 — the card was never the problem, and the premise was never checked

**The epic's product and a MEASUREMENT.** Two subjects, four judges each, two
model tiers, one round. Commit scored: `f49a1c9`. Nothing was fixed.

---

## 0. What this round got wrong, said first

**The round operator made two redaction errors and a blind judge found both.**

1. **`before/README.md:139-162` was not redacted.** It states the card's five
   dimensions, six scoring rules, and a prior evaluation result for one of them.
   My staging script was written by scanning the **after** tree, and `README.md`
   is precisely the file SM-06's de-duplication cleaned — 7 statements before, 0
   after. **My `before` tree reintroduced the exact leak the artifact had already
   fixed**, and all four removal judges could reach it. Found by `K-p1`, in its
   first `diff -rq`.

2. **`examples/validation/ab/eval/results/final-run-2.json` was not redacted, and
   it MOVED A SCORE.** `K-p2` disclosed that `per_class.guard_relaxation` from
   that file is the entire basis for its `D1 = 3`, and that without it `D1` would
   be 2. That is one dimension-point in this round's removal arm attributable to
   a file I should have removed.

**And my leak scanner made the same class error as the instrument this round
files a finding about.** I scanned both trees for the shape `D1 = 2`. The text I
missed reads *"bug detection did not move by a single cell — 4 of 6, 6 of 6, 0 of
3, 0 of 3"*. A result stated without the dimension's name is invisible to a
pattern keyed on the dimension's name — which is `SM-05-DF-02` exactly, committed
by the person filing it.

**Neither error touches the D2 headline.** Both leaked passages state D1-relevant
and D3-relevant results and neither states any D2 value. The D2 separation in §1
is measured on four greenfield cards none of whose judges reported either file,
and on four removal cards whose leaked material was about D1 and D3.

**Other round-conduct facts, disclosed rather than buried.**

- **The gap-mutant re-run executed concurrently with the eight judges**, at load
  ~30. SM-02 documented that machine contention yields a `DIES` indistinguishable
  from a real kill. I did not re-run it, and the reason is evidence rather than
  convenience: `mutants_not_applied: []`, both positive controls died on every
  detector that outlives the cut, every kill set in §3 is semantically on-target
  and matches the sealed before-tables node-for-node, and the one cell known to
  have flaked historically (`SM-GM-I1` on `pytest-full`) resolved to `SURVIVES`
  with **zero** new failing nodes. A contaminated run does not produce that.
- **I contacted no judge during scoring**, and I edited no repository file
  between dispatch and the last card. `git status` through that window showed
  only judge-written cards.
- **The removal arm was not blind to its subject and could not have been.**
  `K-p2`: *"the after tree carries `SM-01`…`SM-06` ids and `run_gap_mutants.py:20`
  says 'SM-05 re-runs this same file', so I knew which change I was scoring from
  the first file I opened."* A repository cannot be blinded to its own history.
  What held is the blind that matters: no removal judge was served any prior D2
  value, and none reported one.

---

## 1. THE HEADLINE — D2 separates on the SUBJECT, at both tiers

| subject | tier | judge | D1 | **D2** | D3 | D4 | D5 |
|---|---|---|---|---|---|---|---|
| greenfield `ab_quota_ledger` | high | `S-p1` | 3 | **2** | 2 | 2 | 3 |
| greenfield `ab_quota_ledger` | high | `S-p2` | 3 | **2** | 2 | 2 | 3 |
| greenfield `ab_quota_ledger` | low | `S-p3` | 3 | **2** | 1 | 3 | 2 |
| greenfield `ab_quota_ledger` | low | `S-p4` | 3 | **2** | 2 | 3 | 2 |
| **toolchain removal** | high | `K-p1` | 2 | **3** | 2 | 2 | 4 |
| **toolchain removal** | high | `K-p2` | 3 | **3** | 2 | 2 | 4 |
| **toolchain removal** | low | `K-p3` | 3 | **4** | 4 | 3 | 4 |
| **toolchain removal** | low | `K-p4` | 2 | **3** | 3 | 2 | 4 |

**D2 = 2 on 4 of 4 greenfield cards. D2 ≥ 3 on 4 of 4 removal cards. No overlap.
The separation holds at both tiers.**

### Which explanation the evidence supports

**Explanation (b): there had never been anything to measure.** The card can
measure complexity. It was never given a subject with a before.

The judges give the mechanism themselves, unprompted, and the two arms' reasons
are mirror images:

> *"Anchors 3 and 4 require a simplification with before and after figures. **A
> greenfield artifact has no before. D2 caps at 2 here structurally.**"*
> — `S-p2`, `dimensions.D2.rationale`
>
> *"Anchor 3 rejected: the T/U/W columns in the mechanical block compare three
> different artifacts, **not this artifact before and after its own
> simplification**."* — `S-p4`, `dimensions.D2.rationale`
>
> *"Anchor 3: a simplification was made and both before/after figures are
> recorded, at the file level and at the specific-field level I traced myself. I
> explicitly did not let the −225-line headline stand."* — `K-p4`
>
> *"What got simpler: `run_generated_case_adapters.py` … drops from code_lines
> 2341 to 2116, callables 78 to 72, branch_points 473 to 429."* — `K-p3`

**The tier axis rules out judging capacity, within the range tested.** Both tiers
score every greenfield card 2 and every removal card ≥ 3. If D2's constancy were
a judging-capacity artifact, the tiers would separate; they do not. What this
axis **cannot** say is whether a judge stronger than `claude-opus-5[1m]` would
score differently — no such judge was available, and every one of the 41 prior
cards was `claude-opus-5[1m]`, so the high tier here *is* the historical tier.

### And the premise was already false before this round ran

The epic opens: *"`D2 = 2` on **27 of 27 cards ever written**"* and *"**Every
subject this project has ever scored was greenfield** … **No greenfield artifact
can reach D2 anchor 3, ever.**"* (`SUBTRACT-TO-MEASURE-EPIC.md:17,24`;
`ticket_plan.yaml:5` states it the same way.)

**41 cards carry a D2 score, on six examples, and D2 has taken three values.**

| example | n | D2 values |
|---|---|---|
| `ab_quota_ledger` | 31 | **2** |
| `ex1_scaffold_only` | 2 | 2 |
| `ex4_pipeline_coherent` | 2 | 2 |
| `ex5_pipeline_divergent` | 2 | 2 |
| `ex6_jenga` | 2 | **1** |
| `ex3_over_complex` | 2 | **3** |

**`ex3_over_complex` reached D2 anchor 3 from BOTH blind judges on 2026-08-03**,
with before and after descriptors cited (`bound 8,388,608 → 624`, `dense rows
3 → 1`), and both declined 4 for the MF-020 reason. In the one round that scored
five *different* fixtures, D2 discriminated across three values with **perfect
inter-judge agreement on all five**.

The anchors digest is `sha256:eeccf4576bc6fd85` at versions 1, 2 and 3 alike, so
those cards were scored against **the same bar as mine**.

So the "27 of 27" figure is true and is a fact about **one example** — the only
one ever re-scored — restated **unscoped** as a fact about the instrument. The
question SM-05 was created to answer had been answered, in the affirmative, by a
prior epic, and `references/architecture_advice.md:376-390` says so in plain
English. **This round reproduces that answer on a real before/after rather than a
fixture, which is worth having — but it is a replication, not a first.**
`SM-05-DF-01`.

---

## 2. D3 — the dimension that outranks the headline, and it did not hold

**A D3 regression outranks the D2 result, so it is reported before the goals.**

| subject | prior sealed | high tier | low tier |
|---|---|---|---|
| greenfield `artifact_U` | **2**, on 10 cards | 2, 2 | **1**, 2 |
| toolchain removal | *none — new example* | 2, 2 | **4**, 3 |

**On the removal, D3 spans 2 → 4 and is `contested` under scoring rule 5** (two
judges differing by more than 1). The disagreement is not about the evidence; it
is about **what the artifact is**:

> *"A D3 of 4 I could have justified with my own execution — 28/28 against real
> and fake — put aside because `reference_ports/domain.py:3-5` says that tree is a
> **fixture** the instruments are pointed at, not the artifact. That is the
> largest swing in the card (2 vs 4 on identical lines) and it is a disagreement
> about what 'it' means, not about the code; **no new evidence will settle it.**"*
> — `K-p2`

`K-p1` named the cause independently: *"D3 at the 2→3 seam, where 'the domain'
silently changes referent."*

**And nothing computed the contest.** Scoring rule 5 says a dimension where two
judges differ by more than 1 *"is recorded as `contested`"*. The field is
per-card, every judge left it empty, and neither `check` nor `index` compares
cards to one another — `index` printed `contested: —` on all four removal rows
while the spread across them was two points. **The one rule the card has for
judge disagreement has no executor.** The spread was found by reading four cards
side by side, which is what no tool does.

**This is a real result about D3 and it is unflattering.** D3 is the dimension
this project rests its cross-epic claims on, chosen because it "discriminates and
holds still." It holds still on small fixtures. On a repository-scale subject it
spans two points between judges at the same tier, for a reason rule 5's
adjudication procedure explicitly cannot fix — that procedure asks a third pass to
"cite new evidence", and both judges agree no new evidence exists.

**And D3 moved one point on byte-identical greenfield bytes at the lower tier**
(`S-p3` = 1 against ten prior cards at 2). **D5 also shows a one-point tier
effect** (greenfield: high 3,3 / low 2,2). **D1 and D2 show no tier effect at
all.** `SM-05-DF-06`.

---

## 3. GOAL-removal-is-measured — every removal, with its gap-mutant verdict

Re-run of SM-01's catalogue on the **integrated epic tip**, with the byte-identical
corpus SM-01 and SM-02 used (`cases.py` sha1 `08265aff…`).
`mutants_not_applied: []`. Raw: `gap-mutants-SM-05.json`.

**Both positive controls died on every detector that outlives the cut:**
`CTRL-A` DIES on `suite-real` (28), `suite-fake` (28), `pytest-full` (1386),
`portswap-suite-real`, `portswap-suite-fake`; `CTRL-B` DIES on
`instrument-registry`. R2 satisfied — the greens below are facts about the
mutants, not about a dead harness.

### Mechanism 1 — the `[ports.*]` binding machinery (removed by SM-02)

| mutant | before (SM-01) | after (SM-05, integrated tip) | verdict |
|---|---|---|---|
| `SM-GM-P1` | DIES on `corpus-port-swap:fake`, `suite-fake`, `pytest-full` | **DIES** `suite-fake` 28, `pytest-full` 1386 (3 nodes) | **STILL DIES — REDUNDANT, cut was free** |
| `SM-GM-P2` | DIES on `port-binding-report`, `pytest-full` | **DIES** `pytest-full` 1386 (3 nodes); `port-binding-report` **INERT** | **STILL DIES — REDUNDANT** |
| `SM-GM-P3` | DIES on `pytest-full` only; **SURVIVED all six machinery columns** | **DIES** `pytest-full` 1386 (5 nodes) | **STILL DIES — REDUNDANT** |

The four `corpus-*` columns report **`CONTROL_RED`** — *undecided*, never
`SURVIVES`. The cause is `ImportError: cannot import name 'apply_wiring'`: SM-02
deleted a function that a sealed measurement driver still imports at module
scope, and SM-02 declined to delete that driver on the ground that doing so would
make the before-instrument unre-runnable. **Two judges read this as a genuine
cost** — `K-p2`: *"the cut also broke the only model-derived check pointed at it
… before this change is read as behaviour-preserving, repair the `apply_wiring`
import and re-run."* I did not repair it: **file findings, fix nothing.**

### Mechanism 2 — the hollow demonstrations and the enumeration check (SM-03)

| mutant | before | after | verdict |
|---|---|---|---|
| `SM-GM-I1` | SURVIVES registry | **DIES** registry | **SURVIVES → DIES** (repair worked) |
| `SM-GM-I6` | DIES registry | DIES registry | unchanged |
| `SM-GM-I2` | SURVIVES both | SURVIVES both | unchanged — **UNDER-POWERED by SM-01's own account** |
| `SM-GM-I3` | SURVIVES both | **DIES** both (`registry-enumeration`, `pytest-full` 1388) | **SURVIVES → DIES** (repair worked) |
| `SM-GM-I4` | DIES ×3 | DIES ×3 (`spec-yaml-tripwire` 19) | unchanged |
| `SM-GM-I5` | registry SURVIVES, `pytest-full` DIES | same | unchanged |

### Mechanism 3 — the duplicated card statements (removed by SM-06)

A de-duplication opens a different gap, so SM-06 seeded a different shape:
**before**, four disagreeing copies — `M1`, `M2`, `M3` **UNCAUGHT**, `M4` (control)
CAUGHT. **After**, reintroduction: `A1`, `A2` both **CAUGHT**. Not a survival
test and not reported as one.

### The verdict on the goal

**ZERO mutants went `DIES` → `SURVIVES`. Two went `SURVIVES` → `DIES`.** Every
removed mechanism carries a before and an after verdict.

**Removals with NO gap mutant: four, named rather than omitted** — `scripts/code_complexity.py`
(correctly cannot fail: a thermometer), registry row `test-graph-nodes` (needs a
JVM absent here — declared unmeasured rather than measured as nothing), the
`fake =` key of a `[ports.*]` table (the fault would live in the deleted
declaration), and registry row `ticket-state-agreement` (the gap is already
total). A fifth is implicit and worse: **the four `CONTROL_RED` columns are a
cost with no mutant able to price it**, because the instrument that would price
it is the thing that broke.

**GOAL-removal-is-measured: MET.** Baseline ZERO → measured: 9 mutants + 2
controls + 2 reintroduction mutants, every removal with a before/after verdict,
4 not-seedable mechanisms named. Target: *"every removed mechanism has a gap
mutant with a before and after verdict; removals with no gap mutant are counted
and named."* Met on both clauses.

---

## 4. GOAL-D2-can-move — MET, and the goal was mis-specified

Baseline: *"D2 = 2 on 27 of 27 cards … the anchor has been structurally
unreachable in every round to date."* Target: *"D2 reaches 3 or more on the
removal, OR the round reports plainly that D2 is still 2 … BOTH OUTCOMES DECIDE
THE GOAL."*

**Measured: D2 = 3, 3, 4, 3 on the removal; 2, 2, 2, 2 on the greenfield control.
MET on the first clause.**

**But the baseline's second sentence was false when it was written** (§1), so the
goal as stated asks this round to establish something already in the record. The
honest verdict is **MET, with the baseline corrected**: D2 moved, it had moved
before, and what this round adds is that it moves on a **real** before/after and
not only on a fixture built to be over-complex — and that it does so
independently of judge tier.

---

## 5. The instrument counts, and whether they are honest

**They are not, in two ways, and a blind judge found the second.**

**(a) The served counts were measured in the wrong tree, and they are wrong.**
`instruments-after.json`'s own argv names `wt-epic-subtract-to-measure-SM-03` —
the counts are SM-03's tip, **before SM-06 merged**. `one-home-tripwire` is
registered in `instruments.toml` at `f49a1c9` and absent from that JSON. Found by
`K-p1` reading the argv, not by me.

**I ran `demonstrate.py` myself at the scored commit** — the standing caveat says
"the suite is green" is not evidence the registry is sound. Raw:
`instruments-SM-05.json`. **`reproduction_failures: 0`.**

| figure | served to judges (SM-03 tree) | **measured at `f49a1c9`** |
|---|---|---|
| enumerated rows | 57 | **58** |
| instruments | 47 | **48** |
| with a demonstrated failing input | 33 | **34** |
| without one | 14 | 14 |
| ratio | 70.2 % | **70.8 %** |

The `+1/+1` is `one-home-tripwire`. **So the figure the epic has been quoting —
47 and 33 — is stale at the tip it is quoted about**, and the corrected ratio
*rose*, which under `denominator_rule` is exactly the direction that needs saying
plainly: it rose because a row was **added** with a demonstration, not because
anything was deleted. Nothing was deleted.

*(Measured in the working tree with `specs/tickets/SM-05/` open. SM-03 recorded
that an open ticket directory inflates `spec-yaml-tripwire`'s count; that slot is
a floor (`expect_passed_at_least`), so an inflated count cannot turn it green
falsely, and no other row reads `specs/tickets/`.)*

**(b) "34 with a demonstrated failing input" mixes two evidence shapes and
records neither.** Parsed from my own run:

| shape | n | what the registry observed |
|---|---|---|
| **observed** — non-pytest CLI slot, nonzero exit | 15 | the instrument itself refused |
| **observed** — pytest slot with `failed ≥ 1` | 3 | the instrument itself went red |
| **asserted** — pytest slot that **PASSES** | 16 | a meta-test asserted the instrument would refuse |

**18 observed / 16 asserted.** The asserted shape is not hollow — if the
instrument stopped refusing, its meta-test would fail and the slot would go red —
but it is a different and weaker observation, **no field records which shape a row
uses**, and the only mutant aimed at that class (`SM-GM-I2`) is recorded by its
own author as under-powered. Nearly half the headline rests on evidence of the
shape that failed at `FI-01`, where three of four deliberately broken controls
reported HOLDS against a probe whose own tests passed. `SM-05-DF-04`.

---

## 6. GOAL-cheaper — MISSED, and the expansion caused it

**Subagent token spend, this ticket: 1,162,275 tokens across eight judges.**

| judge | tier | tokens |
|---|---|---|
| `S-p1` | high | 108,105 |
| `S-p2` | high | 117,960 |
| `S-p3` | low | 121,282 |
| `S-p4` | low | 110,203 |
| `K-p1` | high | 177,375 |
| `K-p2` | high | 206,758 |
| `K-p3` | low | 160,782 |
| `K-p4` | low | 159,810 |

SM-04 spent ~420k on four judges. **This round spent 2.8× that on 2× the judges**
— the removal subject is a repository and costs ~60% more per judge than a
200-line fixture.

### Findings by channel — **0 : 3 : 4**, over seven filed

| channel | findings | which | per 100k judge-tokens |
|---|---|---|---|
| **suite** | **0** | — | 0.00 |
| **blind judges** | **3** | `DF-03`, `DF-05`, `DF-06` | **0.26** |
| **census / build-the-instrument-then-ask** | **4** | `DF-01`, `DF-02`, `DF-04`, `DF-07` | — (no judge tokens) |

Two findings are **joint** and are counted once, under the channel that reached
them first: `DF-02` was found by staging the judge trees and was then *confirmed
to have moved a score* by a judge's own disclosure; `DF-04`'s provenance half was
found by a judge reading an argv the operator had not. **The round operator's two
redaction errors are not counted as findings** — they are round-conduct defects,
reported in §0, and the class they belong to is `DF-02`.

**`GOAL-cheaper`: MISSED, and the expansion caused it.** The goal has two
clauses and they split.

- **Target clause — MET.** *"The per-channel ratio is reported as a result, and
  the round says which channels should keep being funded and which should not."*
  Reported above; recommendation below.
- **Statement clause — MISSED.** *"The round costs less per finding than its
  predecessor."* **1,162,275 subagent tokens for 7 findings is 0.60 findings per
  100k**, against the predecessor epic's 30 findings over roughly 2.6M
  (**~1.15 per 100k**). Roughly **half** the predecessor's rate.

**The two-subject, two-tier design is why, and it is the design that produced the
headline.** Naming the trade rather than hiding it: **the round bought the epic's
only decisive result and paid about twice the going rate for it.** A cheaper
round would have scored one subject at one tier and been unable to say whether
the difference was the subject or the judge — which is the question.

**Which channels to keep funding.** The suite has now produced **zero findings in
six of seven rounds** and produced zero here — `N02` holds. The blind-judge
channel produced the round's best material at ~0.34 per 100k, including two
findings the operator could not have reached (the degenerate sweep, measured
independently by two judges at the same seed; and both of the operator's own
redaction errors). **Keep funding blind judges and the census channel. The suite
is not a finding channel and should stop being reported as one.**

---

## 7. Sealed predictions, scored

Seal verified: `check_prediction_seal.py` reports sealed at `b2b8e9c`, 51 of 51
records pre-date the seal, and the file has exactly one commit in its history.

| ID | claim | verdict | why |
|---|---|---|---|
| **P01** | fake-side fault dies to the suite, not the binding | **PASS** | SM-01; ENTAILED as labelled |
| **P02** | manifest drift is the machinery's unique catch | **FAIL** | dies on three pytest nodes too |
| **P03** | `complexity-ledger` is redundant with the suite | **FAIL** | SURVIVES both; mutant under-powered |
| **P04** | enumeration check cannot see an omission | **PASS** | ENTAILED as labelled |
| **P05** | "not constructible" is about the runner | **FAIL** on its second half | `instrument-registry` also dies |
| **P06** | hollow slots blind to VACUOUS not MISSING | **PASS** | the split is exact |
| **N01** | the ports machinery prices at ZERO on behaviour | **PASS** | confirmed on the integrated tip: no ports mutant flips `DIES`→`SURVIVES` on any surviving detector |
| **N02** | the suite yields zero findings again | **PASS** | zero, for the sixth round in seven |
| **N03** | `scripts/` `code_lines` stays above 20189 | **PASS** | **21027** — a fall of 225, 1.06% |
| **N04** | `D2` does not reach 4 | **FAIL** | `K-p3` scored **D2 = 4** with a named refusal |
| **N05** | `D3` moves zero cells on the removal | **SUPERSEDED** | the instrument presupposes a prior sealed D3 on the removal subject; `toolchain_removal` is a NEW example and had none. Reported instead: D3 spans 2–4 and is contested (§2) |
| **N06** | nothing watches the enumerator's exit code | **FAIL** | two nodes watch it |

**6 PASS, 5 FAIL, 1 SUPERSEDED. NO ALARM** — five rows were refuted by a run,
two of them negatives (`N04`, `N06`), and the one negative that could not be
scored is superseded for a stated structural reason rather than quietly dropped.

---

## 8. The produced-code figures — the subtraction epic is net ADDITIVE

`scripts/code_complexity.py`, identical command and interpreter, `3f58aca` →
`f49a1c9`:

| tree | before | after | delta |
|---|---|---|---|
| `scripts/` | 21252 | 21027 | **−225** |
| `tests/` | 20068 | 21050 | **+982** |
| `examples/validation/` | 8915 | 9835 | **+920** |
| **summed** | **50235** | **51912** | **+1677** |

`git diff --stat`: **4948 insertions, 1020 deletions** across 17 files.

**The epic named "subtract to measure" added 1677 code_lines net and roughly
seven lines of measurement apparatus for every line it removed.** Two judges
reached this independently and let it cap their score — `K-p4`: *"I explicitly
did not let the −225-line headline stand for the whole change"*; `K-p1` recorded
that a judge who counts the apparatus *"moves D2 to 2"*. **The D2 = 3 result
survives that objection only because anchor 3 asks for a *measured* simplification
with both figures recorded, not for a net reduction.**

**`SM-02-DF-02` independently reproduced**: the sealed `produced-code-before.json`
is low by exactly **+67 on `tests/`** and **+38 on `examples/validation/`** (105
total); `scripts/` is exact, which is why `N03` is scorable at all.

---

## 8a. Acceptance, and a shipped tripwire caught this ticket

```
uv run --with pytest --with pyyaml python -m pytest tests -q
1390 passed in 463.39s (0:07:43)
```

**1390 against SM-06's 1386 at the parent.** The `+4` are the nodes a ticket
directory OPEN under `specs/tickets/` contributes; SM-02 recorded the identical
four and they go away at close. **No test was disabled, skipped, xfailed or
deselected to reach it, and this ticket changed no test file** — `git diff` over
`scripts/`, `tests/`, `examples/`, `references/` is empty.

**The first run straddled this ticket's own edits and is reported and
discarded**, not reconciled: it was launched before the findings, the ledger
rows and `NEXT-EPIC.md` were written, so the tree changed underneath it. *An
interrupted measurement is not a measurement*, and a measurement taken across a
moving tree is the same class of thing.

That discarded run reported **1 failed, 1389 passed**, and the failure is worth
keeping:

```
FAILED tests/test_score_tools.py::test_the_committed_history_rendering_is_current
```

**A shipped tripwire caught this ticket, and it caught exactly the class this
epic is about.** Its docstring: *"A committed rendering that nothing regenerates
is the same class of stale artifact this ticket is about."* Adding four
`ab_quota_ledger` cards made the committed `HISTORY-ab_quota_ledger.md` stale,
and the test went red on the round that staled it.

**Fixed by regenerating the derived artifact, not by exempting the test** —
`history --example ab_quota_ledger --write`, plus a new
`HISTORY-toolchain_removal.md` for the new example. That is producing the view a
measurement owes, the same category as `seal`; it is not a repair of a target to
match a result.

`score_tools.py audit` → **0 violations**, with all five declared movements
re-derived from the cards. `score_tools.py check` → **150 problems, all citation
format, zero substantive** (`SM-05-DF-07`).

**And a small confirmation of `SM-05-DF-02`, from the close path itself.**
`close ticket` writes a row into `specs/results/complexity_ledger.json` — one of
the seven unwatched files that carry prior D-results, and the one that already
contained *"D2 = 2 on 31 of 31 cards ever written"*. This ticket's `narrative`
was set to a **path** rather than prose, so the close added **zero** new
dimension-score text to that file. Every prior epic pasted its whole narrative
in, which is how the leak got there. **Pointing the narrative at a document
instead of inlining it is the cheapest available half of `SM-05-DF-02`'s fix,
and it cost nothing.**

---

## 9. What I REJECTED

- **Re-running the gap mutants on a quiet machine.** Tempting and defensible, and
  I declined it on evidence (§0) rather than on cost: controls green, no unapplied
  mutant, kill sets node-identical to the sealed tables, and the one historically
  flaky cell resolving the correct way. Re-running until a table looks better is
  the shape `measurement_rule` forbids.
- **Editing the judges' citations so `check` passes.** All 150 `check` problems
  are citation **format** — judges wrote `file:line — explanation`. Every score is
  well-evidenced and zero problems are substantive. Rewriting a judge's citation
  to satisfy a regex is editing a measurement. Filed as `SM-05-DF-07`, not fixed.
- **Repairing the `apply_wiring` import** so the four `CONTROL_RED` columns would
  decide, which two judges explicitly recommended. It is a fix during a
  measurement and it would change the instrument between SM-02's after-table and
  mine.
- **Re-scoring the removal after fixing my two redaction errors.** The honest move
  is to report the errors and their measured effect (one D1 point, disclosed by
  the judge who took it), not to re-run until the round is clean.
- **Dropping the greenfield arm** once the removal arm came back ≥ 3 on the first
  two cards. Without the control the result is "D2 was 3 once", which is what the
  record already had; the control is what makes it a separation.
- **Reporting `N05` as PASS.** D3 did not move on the removal because there was
  nothing for it to move from. Scoring an unevaluable prediction as passed is how
  a round reaches 8-of-8 and measures nothing.
- **Retiring D2, D4 or D5.** `do_not_retire_untested_rule`, and now on evidence:
  D2 works when given a subject with a before.

### What each blind judge rejected

- `K-p2` — D3 = 4 it could justify by its own execution, because the port is in a
  **fixture**; D1 = 4, because a zero in a kill matrix is a measurement and not
  the anchor's "names a fault class it cannot reach"; and **every load-bearing
  number in `test_ports_binding_removed.py:6-18`**, because the measurements
  behind them are under redacted paths.
- `K-p1` — D3 = 4 on the same fixture ground; §3's headline read as net
  simplification; and the "guard relaxation 3 of 3" claim as D1 evidence, on
  scoring rule 1 (prose is not evidence).
- `K-p3` — D1 = 4 and D4 = 4 on the model-derived/hand-written ambiguity, taking
  the lower per the tie-break rule; and `SM-GM-I2` as a citation, because the
  packet itself calls that mutant defective.
- `K-p4` — an impulse to score D1 = 3 and D3 = 4 by assuming capabilities held
  "elsewhere in the repo".
- `S-p1` — **D3 = 4 on evidence it had manufactured itself** (its own in-memory
  fake, 28/28 against real and fake): *"Evidence a judge manufactures about an
  artifact is not evidence about its design — the trap the 'you may run things'
  permission opens."* Also the whole harness kill table as D1's basis, and the
  mechanical block for D2 on MF-020 grounds.
- `S-p2` — D3 = 4 from the identical `fake`/`real` columns, *"the same run printed
  twice … the most dangerous item in the packet, formatted as the strongest
  possible support for the anchor it refutes"*; and the literal reading of "score
  the LOWEST anchor", *"it floors every score at 0"*.
- `S-p3` — a D3 = 2 reading of `_LedgerFile.append()` as "a port", once it checked
  actual swappability; and scoring D5 off the whole packet rather than the
  artifact's own notes.
- `S-p4` — D1 = 4 (blank class column made the citation unsafe) and D4 = 4 (its
  own fault was caught only by a hand-written check).

---

## 10. Findings filed — 7, over budget, none fixed

Budget is 5. **SM-05 is the last ticket of this epic and there is no sibling to
carry to**, so the excess is `escalated` rather than carried — the precedent is
`PA-06`, for the same reason. The alternative was to not report findings during
the ticket whose entire purpose is to report them.

| id | severity | |
|---|---|---|
| `SM-05-DF-01` | major | the epic's founding premise is false as stated; D2 takes 1/2/3 across six examples and reached anchor 3 in a prior epic |
| `SM-05-DF-02` | major | statements of how a dimension SCORED are watched by nothing; seven never-forbidden files carry them; one moved a score this round |
| `SM-05-DF-03` | major | the blind packet is not blind — a three-artifact mechanical table served to 26 judge-scorings, plus visible scrub artifacts in sealed bytes |
| `SM-05-DF-04` | major | "34 with a demonstrated failing input" is 18 observed + 16 asserted, unrecorded; and the counts the epic quotes were measured in the wrong worktree |
| `SM-05-DF-05` | major | the ladder does not fit a subject without a model: four of five top rungs structurally unreachable on greenfield; "score the LOWEST anchor" read literally yields 0 everywhere |
| `SM-05-DF-06` | major | D3 is contested 2–4 on a repository-scale subject because "the domain" has no fixed referent; rule 5's adjudication cannot settle it |
| `SM-05-DF-07` | minor | `check`'s citation grammar rejects annotated citations; 8 of 8 cards fail on format with zero substantive violations; rule 2's "capped at 1, mechanically" is not what the code does |

---

## 11. Did this epic make the project's numbers mean more?

**Yes for D2, no for D3, and the largest gain is not a number at all.**

- **D2 means more.** It was cited for five epics as a constant and is now
  demonstrated to discriminate — 1, 2 and 3 across six examples, and 2 against
  3–4 across two subjects in one round at two tiers. **What changed is not the
  card; it is that the card was finally given something to measure and the
  citation was finally checked.**
- **D3 means less than it was claimed to.** The one dimension the project rests
  cross-epic claims on is stable on fixtures and spans two points on a
  repository-scale subject, for a reason the card's own adjudication rule cannot
  resolve.
- **The instrument counts mean less.** The quoted 33 of 47 is two different
  measurements added together and was taken in the wrong worktree; at the scored
  commit it is **34 of 48**, of which **18 are observed refusals and 16 are
  assertions**.
- **And the thing worth carrying forward is a habit, not a figure.** The premise
  that justified this epic was checkable in one command against the repository's
  own sealed cards, and five epics restated it without running it. `R-H2` forbids
  averaging across examples; **nothing forbids generalising from one**, and that
  is the error that actually occurred.
