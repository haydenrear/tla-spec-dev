# `GOAL-judged-goals-compliant` — baseline

**Tree: `436c78c55c60c3ee45901223176124df5e38b6ff`**, the epic base, measured on
`epic/stabilize-substrate` before any ticket landed.

**Harness, run verbatim:**

```bash
uv run --with pyyaml python3 \
  specs/results/scorecards/score-drives-validation/GOAL-scored-at-goal-time/SV-03/analysis/baseline_is_a_card.py
```

**Raw output, sealed:** `baseline_is_a_card-436c78c.txt` in this directory. Every
figure below is re-readable from that file; nothing here is a recollection.

---

## 1. The figure

```
plans on disk (live + sealed)                              : 122
distinct epic goals                                        : 31
… naming a judged instrument                               : 20
… whose baseline the evaluation can OPEN                   :  0
sealed scorecard.json files under specs/results/scorecards : 95
```

**`0 of 20`.**

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

- **`0 of 20`** is the goal's figure: judged goals with an openable baseline.
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
`continues:` field naming the sealed predecessor entry. **`SS-03` must check
whether any other cross-epic ID reuse exists in the record**, because the census
reports that class as a lower count rather than as an error.

## 7. And a second one, which is why clause (a) is worded the way it is

**All five of this epic's harnesses are commands.** The census classified
**three of the five** as naming a *judged* instrument —
`GOAL-counted-figures-reach-the-record`, `GOAL-four-results-still-stand`,
`GOAL-judged-goals-compliant` — because its judged-instrument recogniser is a
**keyword matcher over the harness prose**.

That is `CA-08-DF-01`'s class seen from the other side: **a recogniser bound by
sentence form**. It means the denominator of 20 is, strictly, a claim about a
keyword matcher rather than about judged instruments.

**`SS-03` decides which is wrong, and must not fix it by rewording this plan
until the classification flips.** That is fitting to a known answer, `MF-020`.

## 8. The constraint that may bound the goal

**`R-H4` seals `specs/.history`, and most of the 20 live in sealed plans.** Eight
of the ten `summary` verdicts and several of the `directory` verdicts point into
`specs/.history/<workflow>/closed-snapshot/…`.

If compliance cannot be retrofitted without editing a sealed record, **that is
the result** — stated with the count, per clause (c). It is not a reason to
report a smaller denominator.
