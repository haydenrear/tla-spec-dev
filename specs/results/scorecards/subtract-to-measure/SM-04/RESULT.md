# SM-04 — the version 2 to version 3 discontinuity, measured

**The card's own change rule:** *bump `scorecard_version`, keep the old anchors in
the file, and re-score at least one prior example under both versions so the
discontinuity is measured rather than assumed.* This is that re-score.

Everything below is one artifact, `artifact_U`, from `ab_quota_ledger` — the same
sealed, byte-identical tree PA-06, EVAL-RERUN and FI-03 scored. Four fresh blind
judges: two under version 2 against a frozen version 2 rubric, two under version
3, on the same day, from the same dispatch text.

---

## 0. What this round cannot measure, said first

- **A quarter of FI-03's power.** One artifact, four judges, twenty judge-scores.
  FI-03 measured its bump with three artifacts and twelve judges. Read every
  number below as a quarter of that.
- **A deliberately non-random artifact.** `artifact_U` is the artifact on which
  the D5 disagreement version 3 addresses was demonstrated. It was chosen for
  that reason, so any D5 result here is not a random sample.
- **THE DECONTAMINATION ITSELF IS UNMEASURED, AND CANNOT BE MEASURED WITHOUT
  CONTAMINATING TWO JUDGES ON PURPOSE.** The frozen version 2 rubric here differs
  from the shipped one at `0342a3a` by one edit — rule 8's `R-H5` cross-reference
  removed — because `scaffold` refuses to serve the original, which is the
  mechanism working. Both SM-04 arms were served the cleaned scaffold as well
  (`SM-04-DF-01`). So the version 2 arm here is *version 2's schema, served
  clean*, not version 2 as FI-03 shipped it. Every SM-04-against-FI-03 comparison
  below carries that confound and is labelled where it matters.
- **The blinding leaked, and all four judges disclosed it unprompted.** The
  opaque labels `H` and `R` were defeated by the packet itself:
  `blind/artifact_U/EVIDENCE.md:1` reads *"Evidence packet — artifact U"*. Every
  judge reported knowing `H`/`R` = `U`, and every judge reported still not
  knowing which **arm** produced it — which is the blind that matters, and it
  held. `used_labels()` re-labels the card and nothing re-labels the packet.
- **Judges shared one worktree and `git status` showed them each other's paths.**
  Three of four ran it to prove they had not touched the tree, and all three
  disclosed seeing the other cards' filenames. All three state they opened
  nothing and ran no diff.
- **THE ROUND OPERATOR CONTACTED TWO JUDGES MID-SCORE ON A FALSE ALARM. That was
  me and it should not have happened.** I read both pass-2 cards while their
  judges were still writing, saw the scaffolded placeholder under `## Disclosures`
  where content had not yet landed, and messaged both judges asking them to
  complete a section that was about to be complete. Both correctly refused to
  change anything; both re-verified `check` at 0 problems; **no score, rationale,
  citation, verdict, `anchor_reading` or `judging_practice` entry moved**, which
  is verifiable against the cards. It is disclosed because contacting a judge
  during scoring is the operator error this card's whole version 3 is about, and
  an operator who hides their own is not entitled to report anybody else's. The
  cause was reading a file mid-write, not a defect in any card.

---

## 1. Every card ever written about this artifact

| round | ver | pass | D1 | D2 | D3 | D4 | D5 | executed own faults | D5 reading |
|---|---|---|---|---|---|---|---|---|---|
| PA-06 sealed | 1 | p1 | 4 | 2 | 2 | 4 | 4 | — | — |
| PA-06 sealed | 1 | p2 | 3 | 2 | 2 | 4 | 4 | — | — |
| FI-03 v1 | 1 | p1 | 3 | 2 | 2 | 3 | 3 | no | — |
| FI-03 v1 | 1 | p2 | 3 | 2 | 2 | 4 | 3 | no | — |
| FI-03 v2 | 2 | p1 | 3 | 2 | 2 | 4 | 3 | **yes** | — |
| FI-03 v2 | 2 | p2 | 3 | 2 | 2 | 4 | 4 | **yes** | — |
| **SM-04 v2** | 2 | p1 | 3 | 2 | 2 | **2** | 3 | **yes** | — |
| **SM-04 v2** | 2 | p2 | 3 | 2 | 2 | 3 | 3 | **yes** | — |
| **SM-04 v3** | 3 | p1 | 3 | 2 | 2 | 3 | 3 | **yes** | `measured` |
| **SM-04 v3** | 3 | p2 | 3 | 2 | 2 | 4 | **2** | **yes** | — (D5 = 2) |

The set of values each dimension has ever taken on this artifact, over ten cards:

| | values ever recorded |
|---|---|
| D1 | 3, 4 |
| **D2** | **2. Only 2.** |
| **D3** | **2. Only 2.** |
| D4 | 2, 3, 4 — **the whole usable range** |
| D5 | 2, 3, 4 |

---

## 2. The version bump: 3 points over 10 judge-scores, worst 1

| comparison | judge-scores | summed \|movement\| | worst per judge | what moved |
|---|---|---|---|---|
| **SM-04 v2 → v3 — the bump** | 10 | **3** | **1** | p1 D4 2→3, p2 D4 3→4, p2 D5 3→2 |
| FI-03 v1 → v2 — the previous bump | 30 | 4 | 1 | D4 ×2, D5 ×2 |

Worst-case movement is the same as the previous bump: **1 point per judge, and
D2 and D3 did not move at all.** Per judge-score the rate is higher — 0.30
against 0.13 — on a quarter of the sample, so the interval is wide and the
comparison is weak. **Nothing here says the bump is free; what it says is that
nothing moved by more than one point and that the two dimensions the bump does
not touch did not move.**

Everything that moved is D4 or D5, which are the two dimensions already known to
move on unchanged input. Version 3 changes neither of their anchors.

---

## 3. THE RESULT THAT IS NOT ABOUT THE BUMP: D4 MOVES 2 POINTS AMONG JUDGES WHO ALL EXECUTED

FI-03's explanation for D4 was **judging practice**: *"the arm that matches
PA-06's practice is the arm that matches PA-06's numbers."* Version 2 made
practice a recorded field on exactly that reasoning, and gated D4's anchor 4 on
it.

Here, **all four judges recorded `executed_own_faults: true`** — 8, 17, 16 and 11
items in `what_was_run`, every one of them fault seeding against a scratch copy —
and D4 came out **2, 3, 3, 4**.

| comparison | both arms all-executing? | D4 movement |
|---|---|---|
| FI-03 v2 → SM-04 v2 | **yes, both** | p1 **4 → 2 (−2)**, p2 4 → 3 (−1) |
| FI-03 v2 → SM-04 v3 | **yes, both** | p1 4 → 3 (−1) |

**A two-point D4 movement on byte-identical bytes between two rounds whose judges
both executed their own faults.** Recording the practice made the variable
visible; it did not make the dimension stable, and it is now demonstrated that
practice does not explain the whole movement. `R-H5`'s standing caveat — *a D1,
D4 or D5 delta of ≤ 2 points per judge across rounds is within demonstrated
noise* — survives this round and is if anything reinforced.

**The confound, stated rather than absorbed.** The SM-04 arms were served a card
with three result-stating lines removed, two of which told the judge that
executing earns D4's anchor 4 and that D4 moves. D4 fell in **both** SM-04 arms
relative to FI-03 v2. That is consistent with the removed paragraph having been
*inflating* D4 — and it is a hypothesis, not a measurement: round, judges,
decontamination and dispatch all differ at once. Filed as `SM-04-DF-07`.
**Nothing in this ticket may be read as having established it.**

---

## 4. D2 AND D3 DID NOT MOVE, AND D2 STILL HAS NOT TAKEN A SECOND VALUE

**D2 = 2 on 31 of 31 cards ever written about `ab_quota_ledger`** — the four here
are the 28th to the 31st. **D3 = 2 on all ten cards about this artifact.**

Every judge gave the same reason for D2, unprompted, and none of them was served
the fact that anyone before them had:

> *"No before/after of any simplification is recorded, so 3 is unreachable."*
> — SM-04 v2 p2
>
> *"zero complexity measurement and no before/after of any simplification."*
> — SM-04 v3 p1

This is `FI-06-DF-05` reproduced under a decontaminated card: **the anchor is
what pins D2, not the artifacts.** It is exactly why `do_not_retire_untested_rule`
exists and exactly why `SM-05` is the ticket that decides it. This round adds a
fourth independent pair of judges saying anchor 3 is structurally unreachable for
a greenfield artifact, and **changes nothing about the anchor.**

### And a wider crack in D2 than the one version 3 was built for

The v3 p1 judge, unprompted, in Disclosures:

> *"read strictly cumulatively, anchor 2 sits above anchor 0's 'complexity is
> unmeasured', and this artifact measures none — forcing 0. I went with 2 per the
> dimension's own `read_first`, but this is a **2-to-4-point spread** on one
> artifact depending on how a judge reads cumulativity — a far wider crack than
> the D5 one this card version exists to record."*

Filed as `SM-04-DF-06`. **NOT FIXED.** Rewriting D2's anchors is the one thing
this ticket may not do: it would pre-decide `SM-05`.

---

## 5. Did the D5 mechanism do what it was built for? Yes, and once.

Version 3 records which of two defensible readings of D5's anchor 4 a judge
scored under. One card reached the boundary and named its reading:

- **v3 p1: D5 = 3, `anchor_reading: measured`**, and in the same breath:
  *"Under `disclosure` this artifact is a 4 on the same lines — a one-point
  spread attributable entirely to the anchor."*

That sentence is the whole point of the field. A reader can now separate *these
two judges disagree about the artifact* from *these two judges disagree about the
anchor*, and in this case it is the second.

**Both v2 judges independently declined D5 = 4 on the same distinction**, without
the field and without being told the distinction existed:

> *"I put the score aside on the word **result**: anchor 4 asks the record to
> contain an unflattering *result*, and every measured number the artifact reports
> about itself is a pass."* — v2 p1
>
> *"the record does carry unflattering results, but every one is about the spec's
> ambiguity or the author's process and none about its own checking; I flagged
> that if an adjudicator thinks that distinction isn't in the anchor's text,
> D5 → 4."* — v2 p2

Four judges, three of whom articulated the same two readings without prompting.
The ambiguity is real, it is not an artefact of the wording version 3 added, and
**version 3 does not resolve it.** It makes it recordable. Resolving it means
moving an anchor, which requires its own version bump with its own measured
discontinuity, and is not this ticket's to take.

**The one card that did not reach the field found the sharper thing.** v3 p2
scored D5 = 2, below the boundary, so the rule required no reading — and that
judge recorded, unprompted, *why the question never arose*:

> *"My first pass had D5 at 3, with anchor 4 turning entirely on the reading —
> under `disclosure` it would have been 4, under `measured` 3, a clean one-point
> delta from the anchor alone. Then a probe killed anchor 3 itself ...
> **the two readings only diverge once anchor 3 holds, and here it does not.**"*

That is a correction to version 3's own design note, from a judge who could not
see it: the two readings are not independent of the score below them. The field
is required at 3 and 4 because that is where they can differ, and this judge
shows the condition is narrower still — they can only differ *given* anchor 3.
The rule as shipped over-collects rather than under-collects, which is the safe
direction, and the card should eventually say so.

Two data points in one round is not a mechanism proven. It is a mechanism that
fired once, did what it said, and was immediately given a limit by the judge it
did not fire on.

---

## 6. The anchors did not move

```
anchors digest, recomputed from the file by score_tools.py check
  version 1  sha256:eeccf4576bc6fd85
  version 2  sha256:eeccf4576bc6fd85
  version 3  sha256:eeccf4576bc6fd85
```

Byte-identical at all three versions, and `version_history_problems` recomputes
it on every `check`. **D2, D4 and D5 are all still on the card. No anchor was
tuned.**

What the version 3 bump changed in the bytes a judge is served, diffed exactly:

```
+ the "this is the whole rubric, do not go and read the file" paragraph
+ scoring rule 9
+ D5's note that anchor 4 has two readings and the card records which
```

Three additions, nothing removed, no anchor text altered by one byte. Served
digests: version 2 `sha256:93680919b7aa4ed8`, version 3
`sha256:694280073db988fe`.

---

## 7. A shipped tripwire caught this ticket, and it was not fixed by exemption

Declaring `scorecard_version 3` as a `[[change]]` in `INSTRUMENT-LOG.toml` made
`audit` report **nine `SUPERSEDED-UNMARKED` violations at once** — every ledger
claim still `current` on the far side of it. R-H3 working as designed, on the
ticket that shipped the change.

The card's own straddle warning says what to do: *a straddle is a prompt to go
and look, never a finding on its own — `audit` cannot tell you whether the repair
touched the cells that number is about.* So each of the nine was answered from
the raw data:

| claim | disposition | why |
|---|---|---|
| 5 PA-06 kill / port-reach / complexity claims | **re-affirmed** at `2098d55` | the change declares two paths; nothing under `examples/validation/ab/`, `scripts/code_complexity.py` or `ports-as-adapters/measure/` imports `score_tools` or reads the rubric — the three files that name them do so in a docstring |
| `pa06-scores-moved-on-unchanged-artifacts` | **re-affirmed, and widened** | SM-04 adds four judge-scores on the same arm; the movement it records is a sample from a range, not an episode |
| `fi03-d4-and-d5-cannot-carry-a-delta` | **re-affirmed, strengthened** | the D4 half of its explanation is now tested and does not hold; the claim's verdict is more firmly MISSED |
| `fi03-d2-d3-zero-on-sixty-judge-scores` | **re-affirmed on 20 more** | and split, because D3 holding still and D2 never having moved are opposite facts |
| `fi03-stable-against-the-adjacent-row` | **SUPERSEDED** | *"at most one dimension-point per judge"* was a property of two adjacent rounds, not of the instrument. SM-04 moved D4 by two. Superseded by `sm04-rescore-moves-two-points-with-practice-held` |

`fi03-practice-explains-the-d4-movement` was not flagged — `delta_basis =
"within_run"` exempts it, correctly, since its contrast was measured in one
session. It gets a `[[note]]` instead: **what it measured stands; the sentence in
its `why` claiming the diagnosis holds does not.**

**And a cost this ticket pays and does not hide.** The change is declared with
**no `affects`**, which applies it to every card rather than to the one example
SM-04 re-scored — the true scoping, and scoping it narrower would have been a
false narrowing that happens to keep the audit quiet. `audit` now prints **22
`OPEN` lines** for cards measured before the bar that carry no note. Every one is
correct and every one is `SM-04-DF-02` restated by a machine. They were not
silenced with twenty-two lines of boilerplate. The cost is real: 22 standing
OPENs dilute the channel a genuine one would arrive on, and the next round should
say so rather than learn to skim past them.

---

## 8. Provenance

- Artifacts: `specs/results/scorecards/ports-as-adapters/blind/artifact_U/`, unmodified.
- Dispatch: `JUDGE-DISPATCH.md` beside this file, identical for all four judges
  except the card path and the label.
- Frozen version 2 rubric: `rubric_v2_frozen.md` beside this file.
- Cards: `specs/results/scorecards/subtract-to-measure-sm04-rescore-v2/` and
  `.../-v3/`, both `check` clean at 0 problems.
- Commit scored: `2098d55`.
- Cost: four judges, 4.3 minutes to 11 minutes each, ~420k subagent tokens total.
