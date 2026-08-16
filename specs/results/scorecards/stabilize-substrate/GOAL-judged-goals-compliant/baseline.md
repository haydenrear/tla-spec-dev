# `GOAL-judged-goals-compliant` — baseline

**Tree: `436c78c55c60c3ee45901223176124df5e38b6ff`**, the epic base, measured on
`epic/stabilize-substrate` before any ticket landed.

**Harness, run verbatim:**

```bash
uv run --with pyyaml python3 \
  specs/results/scorecards/score-drives-validation/GOAL-scored-at-goal-time/SV-03/analysis/baseline_is_a_card.py
```

**Raw output, sealed:** `baseline_is_a_card-436c78c-CLEAN.txt` in this directory,
measured by `SS-03` in a **detached worktree at `436c78c` with an empty
`git status --porcelain`**. Every figure in §1 is re-readable from that file.

> **CORRECTED BY `SS-03`.** These two lines used to name
> `baseline_is_a_card-436c78c.txt` and claim *"every figure below is re-readable
> from that file"*. **That sentence was false.** The file it named was produced
> at kickoff on a working tree that **already carried this epic's
> `ticket_plan.yaml` and three uncommitted `baseline.md` files**, and it reports
> **123 plans, 36 goals, 23 judged** — not the `122 / 31 / 20` in §1. **No sealed
> artifact anywhere in the record produced `0 of 20`** until `SS-03` measured
> one. The mislabelled file is kept, renamed
> `baseline_is_a_card-KICKOFF-MISLABELLED-post-plan-population.txt`, headed with
> what it actually is, and cited by nothing. **`SS-03-DF-05`**, found by the
> `SS-03` independent reviewer; source: this epic's own kickoff.

---

## 1. The figure

```
plans on disk (live + sealed)                              : 122
distinct epic goals                                        : 31
… naming a judged instrument                               : 20
… whose baseline the evaluation can OPEN                   :  0
sealed scorecard.json files under specs/results/scorecards : 95
```

**`0 of 20`. SUPERSEDED — see §7.1.** The numerator holds at zero everywhere; the
denominator reads `24` at the epic tip and `17` under the repaired instrument.
This figure remains correct **at `436c78c`, on a clean tree**, and is kept
unedited for that reason.

| verdict | count | meaning |
|---|---:|---|
| **card** | **0** | resolves to the sealed card that produced the number |
| directory | 8 | a folder, and the goal does not say which card |
| summary | 10 | a document, not a card |
| unresolvable | 1 | path-shaped, does not resolve at this tree |
| prose | 1 | no path at all |
| no-evidence | 0 | |
| not-judged | 11 | no judged instrument named — legal and out of scope |

## 2. Issue #271 says `0 of 18`. That figure is corrected here, and the correction is `denominator_rule`

**The numerator held at zero. The denominator rose by two.** `18` is the figure
`SV-05` measured at `3e16b96`, before `cut-the-apparatus` added its four goals.
Quoting `18` at this tree pairs a current numerator with a superseded
denominator, which is the error `CA-07-DF-08` cost the last epic.

`SV-06` at `a527305` and `SV-03` at `5620c9a` both read **27 goals / 87 cards**;
`SV-05` at `3e16b96` read **27 / 95**; this tree reads **31 / 95**. The harness
prints its own cross-check line against `SV-06` so the drift is visible in the
raw output.

## 3. What the two counts of *this* measurement are, so they are not confused later

- **`0 of 20`** is the goal's figure at `436c78c`: judged goals with an openable
  baseline. **`SS-03` supersedes it — §7.1.**
- **`0 of 31`** is a different figure — `baseline.evidence` pointing at a
  `scorecard.json` — unchanged across `SV-06`, `SV-03`, `SV-05` and this tree.
  It is a **string test**; the `0 of 20` **resolves against the filesystem**.
  They are not interchangeable and the second is the stronger claim.

## 4. The cause is established, and it is ours

`SV-05-DF-05`. Four blind agents, none given this repository, were handed a copy
of the six surveyed skill files and one **fictional** epic plan, under a prompt
that never used the words *rubric*, *score* or *card*.

**The arm on the UNPATCHED text already produced a card-backed baseline** — four
named evidence files, the instrument pinned by blob SHA, the scored artifact
fixed as a file list, the instrument's two prior runs on a different subject
refused, the two judges never averaged. Every property the escalated edit was
written to buy.

**What it could not do was find a branch to stand in.** It wrote *"per
`goals-and-evaluation.md` (`Harness does not exist`) this goal takes the wave-1
route"* — routing a judged instrument that plainly **does** exist into the branch
for one that does not.

**So the diffs buy the TIMING, not the CARD**, and `SV-06`'s *"buys the whole of
the target"* is corrected. **The compliance rate of zero is this project's own.**

## 5. The four escalated diffs are merged upstream — verified, not assumed

Checked on this worktree's own Skill Manager home at kickoff:
`git-epic-workflow/references/goals-and-evaluation.md` carries **both** the third
baseline branch (*"Harness is judged and this subject has never been scored under
it"*) and the evidence-is-a-card paragraph (*"`baseline.evidence` is the card,
not the folder it sits in"*). It also carries the blindness-disclosure section.

**So `SS-03` is not blocked on an escalation.** The text ships. The gap is
compliance.

## 6. A defect this epic's own kickoff committed, and its own instrument caught

The first draft of this plan **reused the predecessor's `GOAL-four-results-stand`
ID** for the carried goal. The harness then reported **35** distinct goals where
**36** exist: it collapsed the two same-ID goals into one row, silently, and the
collapse presented as a *smaller denominator*.

The ID was changed to `GOAL-four-results-still-stand` with an explicit
`continues:` field naming the sealed predecessor entry — **a workaround this
finding forced, not the fix.**

**Filed as `SS-00-DF-02` and assigned to `SS-03`, to be repaired before `SS-08`
runs.** The direction is why: an undetected collision **shrinks M**, which
**inflates** the `N of M` rate this instrument exists to compute. `SS-03` must
also **check the record for existing collisions** rather than treating this as a
future-only concern.

## 7. And a second one, which is why clause (a) is worded the way it is

**All five of this epic's harnesses are commands.** The census classified
**three of the five** as naming a *judged* instrument —
`GOAL-counted-figures-reach-the-record`, `GOAL-four-results-still-stand`,
`GOAL-judged-goals-compliant` — because its judged-instrument recogniser is a
**keyword matcher over the harness prose**.

That is `CA-08-DF-01`'s class seen from the other side: **a recogniser bound by
sentence form**. It means the denominator of 20 is, strictly, a claim about a
keyword matcher rather than about judged instruments.

**Filed as `SS-00-DF-03` and assigned to `SS-03`, to be repaired before `SS-08`
runs.** Classify on a **declared field**, not on prose, and answer `UNDECIDED`
for a harness that cannot be classified from declared data.

**`SS-03` must not fix it by rewording this plan until the classification
flips** — that is fitting to a known answer, `MF-020` — and **must coordinate with
`SS-04`**, which repairs the same class of bound in `scope`. Two instruments
quietly sharing one recogniser is how a single defect becomes two wrong figures.

**If the repair moves `0 of 20`, this baseline is superseded and the movement is
the finding** — stated with numerator and denominator named, in either direction,
never applied silently as a correction.

### 7.1 It moved. `SS-03` records the movement here, in the file that owns it

**THIS BASELINE IS SUPERSEDED. The numerator never left zero; the denominator
moved three times.**

| tree | recogniser | figure |
|---|---|---|
| `436c78c` (§1, clean) | keyword over four fields | **`0 of 20`** |
| `25600fa` (epic tip) | keyword over four fields | **`0 of 24`** |
| `25600fa` (`SS-03`, stage one) | declared `kind` alone | **`0 of 23`** |
| `25600fa` (`SS-03`, **shipped**) | declared `kind`, prose may only withhold | **`0 of 17`, 6 `UNDECIDED`** |

- **`20 → 24` is CORPUS movement with no repair in it.** Scaffolding this epic's
  own workflow added five goals to the live plan and four matched the keyword
  list. `0 of 20` is therefore already stale for every ticket agent on this
  branch, which is `denominator_rule` applied to this epic's own figure.
- **`24 → 23` is `SS-00-DF-03`'s repair** — judged-ness from the declared `kind`
  rather than harness prose. Net `−1`, but the **composition changed on 13 of 36
  goals** (7 out, 6 in), so the net understates it badly.
- **`23 → 17` is the `SS-03` independent review's amendment.** Where a goal
  declares `kind: eval` *and* names no judge, rubric, card or dimension anywhere
  in its statement, metric, harness or target, the record's two signals disagree
  and the answer is `UNDECIDED`. **The six refused are exactly the six goals
  `SV-03-DF-02` already named** as naming no judged instrument while declaring
  `kind: eval` — so the veto reproduces a filed finding's list rather than
  inventing one.

**By verdict at the tip:** `card 0`, `card-via-index 8`, `directory 3`,
`summary 5`, `unresolvable 0`, `prose 1`, `no-evidence 0`, `not-judged 13`,
`undecided 6`, `id-collision 0`. **Without the additive index** the same 17 read
`directory 8 / summary 7 / unresolvable 1 / prose 1`, and **that is the column
comparable to `0 of 20`** — `card-via-index` is drawn from those classes, not
added beside them.

**Clause (c), counted: every judged goal is declared only under
`specs/.history`.** `23 of 23` under stage one, `17 of 17` under the shipped
rule. **Not one can be made compliant without editing a sealed record, and none
was edited.** And for **15 of the 23 examined, no card produced the number at
all** — the rule is unsatisfiable for them, not merely unmet (`SS-03-DF-03`).

Raw output: `baseline_is_a_card-436c78c-CLEAN.txt` here, and
`../SS-03/baseline_is_a_card-SS-03-tip.txt` and
`../SS-03/baseline_is_a_card-25600fa-PRE-REPAIR.txt`.

## 8. The constraint that may bound the goal

**`R-H4` seals `specs/.history`, and most of the 20 live in sealed plans.** Eight
of the ten `summary` verdicts and several of the `directory` verdicts point into
`specs/.history/<workflow>/closed-snapshot/…`.

If compliance cannot be retrofitted without editing a sealed record, **that is
the result** — stated with the count, per clause (c). It is not a reason to
report a smaller denominator.
