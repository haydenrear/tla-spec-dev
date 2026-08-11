# CL-04 — the loop runs, once, on our own repository, and the version label is still not sealed

**EVALUATION. It measures and fixes nothing.** Ticket `CL-04`, issue #224, branch
`feature/CL-04`, branch point `0adfb79` (verified with `git rev-parse` before any
work — the owner's SHA resolved this time, and it was checked anyway).

**Predictions sealed `2026-08-11T21:00:12Z`** in commit `ab73164`, before a single
command in Parts 1–3 was run and before either blind agent was dispatched.
`PREDICTIONS-CL-04.md` sits beside this file. **Three of eleven were falsified.**
The alarm condition declared in advance — *all eleven hold* — was **not**
triggered.

---

## 1. The three goals, decided

| goal | decision |
|---|---|
| **`GOAL-change-rule-runnable`** | **MET AS WRITTEN, AND THE HEADLINE IT IS QUOTED FOR IS NOT.** A stranger's bump costs no source edit — demonstrated a second time, independently, by CL-04. But the change rule fails loudly only *upwards*. Downwards it is silent, and `scaffold --card-version 4` at the tip stamps a card `version 4` and serves it version 5's bytes. `CL-04-DF-01`. |
| **`GOAL-price-means-something`** | **MET.** All four target clauses reproduce independently at the tip. And the honest addendum: the goal is met and the instrument still has exactly one price to its name. |
| **`GOAL-loop-closes-once`** | **MET.** Reproduced from the sealed cards without re-running a judge: D3 `4, 4 → 3, 3`, one judge model, one artifact, one tag, card version the only mover. **And the closure has no negative control**, so what it establishes is narrower than "the card can detect this". `CL-04-DF-05`. |

---

## 2. The predictions, scored

| | prediction | outcome |
|---|---|---|
| **P1** | base surface is 6,319, not 6,409 | **HELD** — 6,319 stdout at `a662675`; 6,411 with stderr |
| **P2** | tip is 6,281 / 9 rungs, did not grow | **HELD** — −38 bytes, −0.6%, rungs 9 → 9 |
| **P3** | five versions, five distinct served digests | **FALSIFIED** — **four**. v4 and v5 return the same digest, and it is v5's. §4 |
| **P4** | a stranger's *next* bump breaks nothing | see §5 |
| **P5** | an unsupported version is refused loudly | **HELD** — `--card-version 7` exits 2 and names the two edits |
| **P6** | the price reproduces and is still zero | **HELD** — `priced rows: []`, `RM-01-RF-1` still the only price |
| **P7** | the closure reproduces from sealed bytes alone | **HELD** — verified four ways, no judge re-run |
| **P8** | the tip suite is 2 failed, the inherited two | see §10 |
| **P9** | 11–14 findings, budget **exceeded** not capped | **HELD** — 11, budget 5 per ticket, CL-03 escalated its sixth |
| **P10** | zero shipped-toolchain findings; `scripts/` byte-identical | **HELD** — 0 of 11, and `scripts/`, `spec_double_compiler/`, `templates/`, `skill-scripts/` and `SKILL.md` are **byte-identical across the whole epic** |
| **P11** | no token basis exists anywhere in the record | **FALSIFIED** — it exists, it is named `subagent_tokens`, and four prior rounds recorded one. §9 |

**P3 and P11 are the two that taught me something**, and both were falsified in
the direction that made me *more* wrong rather than less: P3 assumed the seal
covered more than it does, P11 assumed the record was emptier than it is.

---

## 3. The served surface, before and after

```
                          a662675 (epic base)      0adfb79 (epic tip)
serve | wc -c                   6,319                    6,281      -38  (-0.6%)
serve 2>&1 | wc -c              6,411                    6,373      <- the 6,409 error
rungs                               9                        9      unchanged
```

**It did not grow. It fell.** Measured in two clean detached checkouts,
`wt-cl04-base-a662675` and `wt-cl04-tip-0adfb79`, **not** `git archive` trees.
Rungs counted the way `tests/test_score_tools.py:2687` counts them.

The 38 bytes are the D3 caveat (138 bytes) paid for out of a sentence of scoring
rule 9 that restated the served preamble verbatim. **The payment is real**:
diffing the two served surfaces shows rule 9 losing exactly the duplicated
clause and D3's caveat gaining the new one. Nothing left the served surface that
was not already on it twice.

**`CL-01-DF-01` reproduces and is slightly worse than filed.** The gap between
stdout and stdout+stderr is **92 bytes today**, not 90 — the stderr line carries
the served digest and the rubric file hash, so its length moves whenever those
do. A budget quoted as `6,409` was never reproducible from any command and now
is not even reproducible as *the same mistake*.

---

## 4. `--digest-only` for every version — and P3's falsification

**Requested so no sealed card is silently re-based. None is. But only one
version is reproducible.**

| `--card-version` | `--digest-only` returns | the table declares | verdict |
|---|---|---|---|
| 1 | `sha256:a753de37842e4953` | — (nothing, deliberately) | **bytes no judge was ever handed** |
| 2 | `sha256:d6bc48a44641aead` | — | **bytes no judge was ever handed** |
| 3 | `sha256:116146e48ecec13b` | — | **bytes no judge was ever handed** |
| 4 | `sha256:2d7d4a0506d9b259` | `sha256:a213a36770ccab09` | **CONTRADICTS THE TABLE — it is v5's digest** |
| 5 | `sha256:2d7d4a0506d9b259` | `sha256:2d7d4a0506d9b259` | correct |
| 6, 7 | REFUSED, exit 2 | not declared | correct, and loud |

`serve --card-version 4` and `--card-version 5` produce **byte-identical**
output, 6,281 bytes each. **`--card-version` labels; it does not gate.** The only
thing that has ever reproduced version 4's served bytes is
`--rubric examples/validation/scorecards/rubric_v4_frozen.md`, a frozen copy of
the whole file, which returns `sha256:a213a36770ccab09` exactly.

**And a new card can still be misstamped.** At the tip:

```
$ score_tools.py scaffold /tmp/probe --example probe --arms A --judges 1 --card-version 4
scaffolded 1 arm(s) x 1 judge(s) = 1 card(s)
$ # the card:  scorecard_version: 4     served_digest: sha256:2d7d4a0506d9b259
$ score_tools.py check /tmp/probe
1 scorecard(s) checked, ... 0 problem(s)
```

That is the epic's own baseline defect — *"a v5 card is stamped version 4 with
`check` reporting 0 problems"* — **alive at the tip with its direction
reversed.** CL-01 closed the upward direction completely and well. The downward
direction was never in scope and nobody looked.

**Why the guard cannot catch it.** `scaffold --card-version 1|2|3` **is** refused,
loudly and correctly, naming `rubric_v3_frozen.md` as the remedy — but it refuses
because *"the current file carries no anchors for D1, D4, D5"*. The check is
**structural**. Versions 4 and 5 share a dimension set, so no structure
distinguishes them and the guard is silent. The one signal that would separate
them is the declared served digest, which is in the same table `check` already
parses and is not consulted.

**`serve` and `scaffold` also disagree with each other.** `scaffold --card-version 1`
refuses; `serve --card-version 1` emits a **two-dimension** card (D2, D3) labelled
version 1 — version 1 was a five-dimension card. The card file states the rule
`serve` is breaking, one paragraph above the table it breaks: rows 1–3 *"can
never declare"* a served digest because *"rendering them from this file would
produce a digest no judge was ever handed."* `--digest-only` produces exactly
that digest for four of the five versions.

**What is NOT wrong, so the finding is not read wider than it is.** **No sealed
card is re-based.** The four CL-03 cards carry their own recorded digests, and
`check` correctly reports **SERVED-DRIFT** on both version 4 cards — *"the bar
this judge read is not the bar in the tree"*. Rows 1–3 declare no served digest,
so no published row is contradicted by any of this. **The damage is to
reproduction, not to the record.** Filed as `CL-04-DF-01`.

---

## 5. `GOAL-change-rule-runnable` — decided

**A bump costs no source edit, and I did one myself rather than take CL-03's
word.** In a disposable worktree at `0adfb79` I bumped the card 5 → 6 as a
stranger would: `**Scorecard version 5.**` → `6`, plus one row in
`### Version history`. **One file, two insertions, one deletion, zero Python.**

```
$ git diff --stat
 references/eval_scorecard.md | 3 ++-
$ score_tools.py serve 2>&1 >/dev/null | grep served
served digest sha256:2d7d4a0506d9b259 (card version 6, rubric file sha256:b75b4c47d07e367f)
```

The served digest correctly does **not** move, because no served byte changed —
which is the truthful answer and the one that shows the second seal is measuring
bytes rather than version numbers.

**One usability observation, not a finding.** The order is forced and nowhere
stated: `serve` refuses until the history row exists, so an adopter must add the
row with placeholder digests, *then* compute them, *then* fill them in. It works;
it is a two-pass ritual a stranger discovers by hitting the refusal.

### P4 — does the repair generalise to the *next* bump?

CL-03 reported that four of CL-01's own tests went red on the first correct bump,
because their demonstrated failing input was the literal `5`, and repaired them
to read what the file declares. **P4 predicted the repair generalises.** The full
suite against the v6 bump is in §10.

### The decision

**MET as the goal is written.** A version bump without a source edit: **yes,
twice, independently.** An unsupported version refused loudly with a demonstrated
failing input: **yes, upwards.** The served bytes sealed: **yes, and exercised on
a real bump** — version 5 is the first row in the card's history whose served
digest moves while its anchors digest holds, which is the exact class CL-01 built
the second seal for. No growth in the served surface: **yes, it fell.**

**And the headline this goal is quoted for is not established.** "A stranger can
bump a card version" is demonstrated. "A stranger can run the loop" is a
different and much larger claim; see §7.

---

## 6. `GOAL-price-means-something` — decided

Re-run at the tip, independently of CL-02's transcripts:

- **`EXTINCT` separates.** `RM03-GM-RUNNER` reads `EXTINCT` at `6298eee` with its
  habitat named, and `UNDECIDED` for the two faults whose killing nodes survive.
  One fault, two heads, two verdicts.
- **Controls are excluded and still printed.** `RM03-GM-CTRL-C` appears under
  `DECLARED CONTROLS -- shown, never priced, in no denominator`, and the footer
  prints `0 of 3 subject(s) ENTAILED-SURVIVES; 1 EXTINCT (not a price); 1 declared
  control(s) excluded` — the excluded count beside the denominator, not absorbed
  into it. `denominator_rule` satisfied in the renderer itself.
- **`--head` is validated.** `deadbeefdeadbeef` → exit **2**, no table.
- **Both known positives reproduce.** `RM-01-RF-1` reads `PRICED`; its control
  reads `CONTROL-EXCLUDED`.
- **Re-priced history: `priced rows: []`.** `0 of 10 disagree` with the
  measurement, `0 lost kills DETECTOR-WEAKENED`, `this_instrument verdicts:
  ['NO-KILL-TO-LOSE', 'UNDECIDED']`.

**MET on every clause.** And the sentence the goal's own target demands be said:
**no target was placed on any price, and no number was tuned.** The informative
outcome would have been a non-zero, the instrument would have printed one, and
none appeared.

**The addendum, which is the useful part.** Two epics have now been spent making
the pricer mean something and it has priced exactly one thing, `RM-01-RF-1`, which
it could already price. `CL-02-DF-02` is CL-02's own record that the remaining
route to a spurious `PRICED` — an all-`INERT` after-table — is still open. The
goal is met. **The instrument is not yet useful, and meeting the goal is not
evidence that it will become useful.**

---

## 7. `GOAL-loop-closes-once` — decided, and what one closure buys an adopter

**It closed.** Verified from the sealed cards at the tip, with no judge re-run:

| card | version | rubric source | served digest | D2 | **D3** |
|---|---|---|---|---|---|
| `20260811-cl03v4-CL-p1` | 4 | `rubric_v4_frozen.md` | `a213a36770ccab09` | 2 | **4** |
| `20260811-cl03v4-CL-p2` | 4 | `rubric_v4_frozen.md` | `a213a36770ccab09` | 2 | **4** |
| `20260811-cl03v5-CL-p1` | 5 | `references/eval_scorecard.md` | `2d7d4a0506d9b259` | 2 | **3** |
| `20260811-cl03v5-CL-p2` | 5 | `references/eval_scorecard.md` | `2d7d4a0506d9b259` | 0 | **3** |

`judge.model` is **`claude-opus-5[1m]` on all four**. Subject scope is
`examples/validation/ab/reference_ports` on all four, architecture tag
`ports-and-adapters` on all four. **The card version is the only mover.** `R-H1`
and `R-H2` hold by construction and nothing is averaged.

The regression was real and pre-existing: `RM-05-DF-05`, found independently by
judges in two prior tickets, neither looking for it.

### What this establishes for an adopter

1. **The mechanism is complete.** Every step of regression → card iteration →
   architectural delta → re-score has a runnable command and left a sealed
   artifact behind. Before this epic, no step after "filing" had ever been run.
2. **A caveat is a working lever, and it is cheap.** 138 served bytes, no anchor
   added, no anchor reworded, and a dimension moved a full point on two
   independent judges. Set against six epics of static gates that moved bug
   detection by zero cells, that is the most encouraging measurement in the
   record.
3. **The second seal catches the class of change that was invisible.** Version 5
   is the first history row whose served digest moves while its anchors digest
   holds, and `check` reports SERVED-DRIFT across the boundary.

### What it does not establish — and this is longer, deliberately

1. **n = 1, and every degree of freedom was held at our value.** Our repository,
   our fixture, our judges, our regression, one artifact, one dimension, one
   direction, two passes a side. `R-H1`/`R-H2` forbid averaging across examples;
   they equally forbid generalising from one.
2. **There is no negative control, and that is the gap that matters most.** The
   version-5 caveat says *"if the only observer of the effect the port exists for
   is the adapter that wrote it, say so and take 3."* It was applied to an
   artifact that has exactly that property, and the score went to 3. **A caveat
   instructing a judge to take 3 in condition X, applied to an artifact with
   condition X, moving the score to 3, is the minimum possible evidence that a
   caveat is wired up.** It demonstrates the plumbing. It does not measure
   discrimination. **No artifact lacking the hole was scored under both
   versions**, so *"the caveat moves D3"* and *"the caveat moves D3 on artifacts
   that have the defect"* are not separated by anything in the record. Filed as
   `CL-04-DF-05`; it should be the next epic's first ticket, and a null there is
   the informative outcome.
3. **Blinding leaked, and the round says so.** The fixture's own docstrings quote
   `BA-B14` including *"the fake that earned arm B its `D3 = 4`"* — the packet
   hands a judge a prior D3 number before it forms its own. Both v4 judges
   disclosed it unprompted. CL-03 reports it as cutting *against* its own result,
   which is the right treatment, and it is still an uncontrolled variable present
   in both arms. `judge.blind_to_arm` is `false` on all four cards.
4. **Nothing about this was priced, and CL-03 says so.** The card iteration
   carries no cost figure and makes no claim the pricer would have to support.
5. **It was run by the people who built it.** Which is the question the epic is
   named for, and §8 is where it is answered.

**MET.** The loop closed once, end to end, on a real regression nobody
manufactured. **What an adopter can take from it is a recipe, not a warrant.**

---

## 8. Is the loop transferable, or only runnable by us?

**MEASURED, NOT ARGUED — and the answer is better than the epic expected.**

CL-04 dispatched a blind adopter probe: an agent told it worked at a different
company, handed only the files the skill ships (`SKILL.md`, `README.md`,
`references/`, `examples/`, `scripts/`, `templates/`) and **forbidden our `.py`
source, everything under `specs/`, our `tests/`, our `*-EPIC.md` files and our
git history**. It was told to write its own artifact and run the loop.

**It ran the whole loop end to end**: serve → scaffold → fill → check → index →
seal → audit → bump the card to version 6 → re-serve → re-score the same commit
under both versions → declare the movement → `audit` clean, `0 violation(s)`,
exit 0. Its artifact was a 103-line Python reminder scheduler it wrote itself,
one driven port, two adapters, four seeded faults of which three were caught.

**Its card iteration moved its own scores on a byte-identical commit: D2 2 → 3
and D3 3 → 4**, because it rewrote D3's caveat and widened D2's anchor 3 to suit
its own codebase. **That is an independent replication of the loop's mechanism,
on a foreign artifact, by an agent that did not build it** — and in the *opposite
direction* from CL-03's, which is worth more than a second copy of the same
result would have been.

### The single most transferable thing the probe found

It **rejected scoring its own artifact D3 = 4 under version 5**, and said why:

> *"The v5 caveat's escape clause fires exactly: nothing but `JsonFileStore` ever
> reads the JSON file. I took 3 and said so. The caveat did real work on a real
> artifact it was never written for."*

**Our D3 caveat, written for our fixture's `FileJournal` hole, correctly fired on
a stranger's independently written reminder scheduler that happened to have the
same single-observer property.** CL-03's closure showed the caveat works on the
artifact it was written for. This shows it works on one it was not.

**And it still is not the negative control.** Both firings are the same
direction — condition present, score taken down to 3. Nobody has yet scored an
artifact *lacking* the property under both versions. The probe was also its own
judge, so artifact author and scorer are the same agent, which CL-03's design
avoided. `CL-04-DF-05` stands unchanged.

### What blocks transfer, from the probe's own numbered list

Fifteen blockers. Three matter:

1. **The architecture axis is a check that cannot fail when under-installed.**
   The adopter page lists three files; a fourth, `scripts/code_complexity.py`, is
   required and named only in `references/architecture_tags.md:125`. Without it
   every subject reads `UNDERIVABLE:unmeasurable` — **and the probe then pointed a
   subject's `scope` at a directory that does not exist and got byte-identical
   output.** A real scope and a fabricated one are indistinguishable. `audit`
   makes it worse by reporting the scope *"is absent"* when the scope is present
   and the derivation is what returned nothing. That is the
   `absent` / `checked, none found` conflation this project's own `subjects.toml`
   header says it keeps finding, shipped inside the axis that carries D3's
   refusal authority.
2. **The movement ledger is undiscoverable from the adopter page.**
   `adopting_the_scorecard.md` never mentions `INSTRUMENT-LOG.toml` or
   `[[movement]]`, and a card bump makes both mandatory at the next `audit`. The
   key format is documented nowhere; the probe brute-forced four wrong shapes.
   **The only working example of the syntax in the tree is our own private
   measurement record.**
3. **`seal` crashes with a raw traceback on the layout section 3 tells you to
   build**, and `tags` prints `REFUSED:` and exits **0**.

Filed together as `CL-04-DF-06`, **escalated as the sixth against a budget of
five**, because (1) is a check reporting a clean on nothing.

### The answer

**PARTIAL, leaning yes — and "partial" is a promotion from where this epic
started.** The epic's premise was that the loop *"cannot be run by anyone who did
not build it."* **That premise is now false.** An adopter who follows the four
documented commands succeeds. An adopter who then runs `audit`, reads its `OPEN`
findings and tries to close them — the move their own card bump makes mandatory —
hits an undocumented config format and guesses or gives up.

**What this does NOT establish**, and the distinction is the whole of §7: the
probe demonstrates that **the mechanism transfers**. It says nothing about
whether the *scores* transfer, whether the card discriminates on a foreign
codebase, or whether a second adopter with a different artifact would agree. One
adopter, one artifact, self-judged, n = 1 again.

---

## 9. Cost: findings by channel, the token basis, and the shipped toolchain

### 9.1 The token basis — NAMED, and P11's falsification

**I predicted no basis existed anywhere. That was wrong, and being wrong about it
is the useful part.** The basis exists, it has a name, and four prior rounds
recorded one:

| round | figure | basis, as that round stated it |
|---|---|---|
| RD-03 | 1.14 / 100k | *"input + output + cache_creation, excluding cache reads"* — **named** |
| SM-05 | 0.60 / 100k, 1,162,275 tokens | `subagent_tokens`, basis **not** named |
| RD-03 (own subagents) | 4,958,128 **or** 1,643,036 | *the same work, two bases, 3× apart* |
| RM-05 | 6.48 reported / 1.08 filed per 100k, 463,261 tokens | `subagent_tokens`, *"composition undocumented"* |

**THE TOKEN BASIS FOR THIS ROUND: the harness's `subagent_tokens` field,
composition undocumented, summed over CL-04's two dispatched agents.** It is the
same field RM-05 used and it is **not** comparable to RD-03's 1.14, because
RD-03's basis is a different and named one, and RD-03's own run differs by 3×
between two bases on identical work.

**AND FOR THE THREE TICKETS THAT DID THE EPIC'S WORK, THE RATIO IS
UNCOMPUTABLE.** The string `token` appears **nowhere** under
`specs/results/scorecards/close-the-loop/` — not in CL-01's commit body, not in
`RESULT-CL-02.md`, not in `CL-03/RESULT.md`, `HARVEST-CL-03.md` or
`PREDICTIONS-CL-03.md`. Independently confirmed by the blind census, which was
asked the question cold and found no CL spend figure by any grep.

**This is the second consecutive epic to record none, and the reason is
structural.** `RD-03-DF-13`'s repair lasted one round. `portable-substrate`
recorded none and re-filed it. `close-the-loop` has recorded none. It is not
three agents forgetting: **no artifact in the repository asks for the number.**
`ticket_plan.yaml`'s `acceptance.assertions` do not require it; the close-out
path does not require it; the only place it is ever demanded is the prose of the
evaluation ticket's dispatch, which arrives after the other tickets have finished
and their spend is gone. Filed as `CL-04-DF-02`.

### 9.2 Was the numerator budget-capped?

**No. It was budget-EXCEEDED, and that is the better failure.** The deferment
budget is **5 per ticket**, `blocking: escalate`.

| ticket | filed | against budget 5 |
|---|---|---|
| CL-01 | 2 | under |
| CL-02 | 3 | under |
| CL-03 | **6** | **over — the sixth escalated in its own text** |
| CL-04 | 5 | at budget |
| **epic** | **11** (+5 = 16 with CL-04) | |

Last epic the numerator was capped: **30 claims came back, 5 were filed**, so
`filed / 100k` measured the budget rather than the yield. **This epic nothing was
dropped for budget.** CL-03 hit the cap and escalated rather than discarding,
which is what `blocking: escalate` is for and is the first time in the record it
has been exercised.

### 9.3 Findings by channel

Assigned by the blind census agent, from each finding's own text, with no
hypothesis supplied. Its per-finding table is auditable in §11.

| channel | CL findings |
|---|---|
| operator doing the work | **7** |
| blind judge | **2** |
| census over the sealed record | **1** |
| operator running an instrument they built | **1** |
| **the suite** | **0** |
| unclear | 0 (**1** under the census's own stricter reading) |

**The suite is a hard zero.** Last epic it produced four — and RM-05 already
diagnosed why: *"the channel was never the suite; it was paying somebody to read
it."* No ticket in this epic was funded to read suite output, and the suite
produced nothing. **The diagnosis predicted this epic's zero and the zero
confirms the diagnosis.**

**Seven of eleven came from an operator doing ordinary work** — reading,
implementing, merging, provisioning. The instrumented channels produced a
minority of the round. The census flags a limitation I am passing on rather than
smoothing over: **the channel vocabulary has no slot for "operator running a
shipped instrument they did not build"**, and three findings landed in "operator
doing the work" by the absence of that option rather than by fit.

**The ratio.** With the basis named as above and the numerator not budget-capped:
`11 filed / <subagent_tokens for CL-01..CL-03> ` is **uncomputable** — the
denominator does not exist. For CL-04 itself the denominator exists and is
reported in §11. **Printing a ratio with one half missing is the thing this
finding is about, so no epic-level ratio is printed here.**

### 9.4 The shipped toolchain, counted separately

**CL epic: 0 of 11. Whole ledger: 10 of 173.**

Definition applied: `scripts/`, `spec_double_compiler/`, `templates/`,
`skill-scripts/`, root `SKILL.md`. Explicitly excluding `examples/`,
`references/`, `specs/`, `tests/`.

| epic | shipped / total |
|---|---|
| PA (ports-as-adapters) | 4 / 28 |
| SM (subtract-to-measure) | 3 / 30 |
| RM (portable-substrate) | 2 / 28 |
| RD (reading-discipline) | 1 / 46 |
| FI (falsifiable-instruments) | 0 / 30 |
| **CL (close-the-loop)** | **0 / 11** |

**And the shipped toolchain is byte-identical across this entire epic.**

```
$ git diff --stat a662675..0adfb79 -- scripts/ spec_double_compiler/ templates/ skill-scripts/ SKILL.md
$ # (no output)
```

`scripts/` was byte-identical through all of `portable-substrate` and is
byte-identical through all of `close-the-loop`. **Two consecutive epics have
changed zero bytes of the thing this repository ships.**

**THE CAVEAT THAT MAKES THE ZERO HONEST, AND THE BLIND CENSUS RAISED IT
UNPROMPTED.** Every CL finding about a *tool* names
`examples/validation/scorecards/score_tools.py`,
`examples/validation/scorecards/architecture_tags.py`, or
`examples/validation/gap_mutants/price_removal.py`. **Those are the instruments
this programme actually runs**, and under the stated definition they are
`examples/`, not shipped toolchain. Under a definition that counted them, CL would
be **at least 5 of 11**, not 0 of 11. The `0 of 11` is arithmetically correct and
describes something narrower than it sounds like. Two further facts from the same
census, both new:

- **Every one of the ten shipped-toolchain findings in 173 rows is under
  `scripts/`.** `spec_double_compiler/`, `templates/`, `skill-scripts/` and
  `SKILL.md` have been named in **zero** finding surfaces across six epics.
- Under `surface OR evidence` rather than `surface` alone the ledger figure is
  **11 of 173**, not 10. The question asked for `surface`; the alternative is
  printed so the delta is not a surprise later.

---

## 10. The suite numbers, with their trees

**Every number names its tree. No `git archive` figure appears here** — several
of these nodes read git history and an archive has no `.git`. All three runs went
to paths carrying this ticket's id, never to a shared `baseline.txt`
(`CL-02-DF-03`).

| tree | commit | working state | result |
|---|---|---|---|
| `wt-cl04-base-a662675` | `a662675` | **clean detached checkout, epic base** | **2 failed, 1469 passed** in 1100s |
| `wt-cl04-tip-0adfb79` | `0adfb79` | **clean detached checkout, epic tip** | **2 failed, 1496 passed** in 1251s |
| `wt-cl04-v6probe` | `0adfb79` + a stranger's v6 bump | one file changed, `references/eval_scorecard.md` | **see §5 / P4** |

**The two failures are the same two at both ends, and they are the inherited
deliberate reds. Neither was repaired:**

```
FAILED tests/test_architecture_tags.py::test_the_same_tag_control_holds
FAILED tests/test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer
```

**P8 HELD.** At the tip the pricer grep names two narrative documents,
`NEXT-EPIC.md` and `CLOSE-THE-LOOP-EPIC.md`; at the base it names one, because
the epic charter did not exist yet. **CL-04's own `RESULT.md` does not add a
third** — the test exempts everything under `specs/`, which is where this file
lives. `NEXT-EPIC.md` still trips it and still should.

### `denominator_rule`, measured on two clean checkouts

```
a662675   1,471 collected
0adfb79   1,498 collected      +27
```

**The whole +27 is numerator, and it decomposes exactly:**

| file | base | tip | delta | whose |
|---|---|---|---|---|
| `tests/test_price_removal.py` | 11 | 22 | **+11** | CL-02 |
| `tests/test_score_tools.py` | 97 | 113 | **+16** | CL-01 and CL-03 |
| everything else | — | — | **0** | |

**No file lost a test. No file was added or removed. Nothing was skipped or
weakened.**

**And `test_spec_yaml_valid.py` did not move at all** — which is worth stating
because both CL-02 and CL-03 reported it moving in *their* trees. It is
parametrised over spec YAML files, and `open ticket` scaffolds a ticket workspace
containing more of them, so it rises inside a ticket worktree and not in a clean
checkout of the same commit. **Both predecessors' figures were correct for the
trees they named; measuring the epic on two clean detached checkouts removes that
term entirely.** CL-04's own worktree will carry the same inflation once
`open ticket CL-04` runs, which is exactly why neither of the two numbers above
was taken from it.

---

## 11. The blind agents, and what they REJECTED

**Two dispatched, both after the predictions were sealed, both given a hard
forbidden read-set and asked what they rejected.**

### Agent 1 — the adopter probe

**Spend: 102,034 `subagent_tokens`, 65 tool uses, 731s.** Read-set: the shipped
files only. Disclosed one boundary contact unprompted: it ran `git status
--porcelain` in the checkout at the end *to prove it had written nothing there*,
and named it as a git command rather than burying it.

**What it REJECTED:**

- **Reading `score_tools.py` or `architecture_tags.py` at any point.** Tempting
  twice — after the third failed `[[movement]]` guess, and when `tags` returned
  identical output for a real and a fake path. It brute-forced the first and
  inferred the second from a docs line. *"The probe is worthless if I resolve it
  the way I could rather than the way an adopter would."*
- **Cribbing the `[[movement]]` format from our `INSTRUMENT-LOG.toml`**, which
  was in the checkout and would have answered it in ten seconds. Rejected because
  it is a private results file, not documentation — *"an adopter
  reverse-engineering a config format from someone else's results file is the
  failure, not the fix."*
- **The harsher reading of the `seal` crash** — that `seal` is broken. `--root`
  is documented, in the wrong section. Downgraded.
- **The charitable reading of the architecture axis** — that `UNDERIVABLE` is the
  axis honestly failing open, a design the docs defend at length. Rejected
  because a fabricated scope produced identical output to a real one: *"fail-open
  is a virtue when the derivation ran; here it never ran."*
- **The harsher reading of the tier check** — that it is Anthropic-only and
  hostile to outsiders. It tested `gpt-5`, `gemini-3-pro` and `llama-4-70b`
  first; all degrade to warnings. *"The blocker is a missing sentence in the docs,
  not a lock-out."*
- **Treating the drift warnings on a frozen-rubric re-score as a bug.** Its first
  draft called them "the tool contradicting its own change rule". Demoted to
  noise: they are warnings, exit 0, with the right instruction attached.
- **Scoring its own artifact D3 = 4 under version 5.** §8.
- **"Partial" on the grounds of the architecture axis alone** — it is documented
  as optional and the core commands run without it.
- **Filing two cosmetic blockers as cosmetic-only.** Kept on the list because
  both are first-contact surfaces asserting something false about the card's
  current shape.

**And it named what worked, unprompted**, which is why the negative findings are
worth reading: it verified the "optional means optional" claim *destructively* by
deleting both optional files and re-running everything — all exit 0, nothing
crashed, nothing wanted a placeholder. It called the tier error and the two
digest errors *"model examples of a refusal that hands you the fix"*, and
confirmed that `--card-version` against a frozen copy reproduced our original
card exactly, digest for digest.

### Agent 2 — the findings census

**Spend: 84,214 `subagent_tokens`, 29 tool uses, 505s.** Read-set: the ledger,
the plan, `.history/` directory listings, and `git log` on the ledger only.

**It disclosed two contamination points rather than burying them**, which is the
behaviour that makes its independence checkable: the authorised repo-wide grep
for question 5 put single lines from forbidden files on its screen, and
`ticket_plan.yaml` — an allowed file — contains the owner's own prior answer,
*"10 of 162 across five epics"*. **It states it computed 10 of 173 before that
line came into view, and notes 173 − 11 = 162, so the two agree.**

**What it REJECTED:**

- **Classifying `CL-03-DF-04` as `the suite`**, though half of it is literally
  *"a correct bump turned four of its tests red"*. Rejected because the red was
  caused by a deliberate operator rehearsal rather than encountered, and because
  `found_by` names the operator act. **It flagged this as the single assignment
  it would most defend splitting, and as the only reason `the suite` is 0 rather
  than 1.**
- **Widening "shipped toolchain" to include `examples/validation/scorecards/*.py`.**
  It would take CL from 0 of 11 to at least 5 of 11. Rejected as *"exactly the
  kind of boundary-shift that makes a count non-reproducible"* — and then
  reported the consequence anyway so the narrowness of the 0 is visible. §9.4.
- **Counting `evidence` as well as `surface`**, which gives 11 of 173 rather than
  10. The question asked for `surface`; the alternative is printed.
- **Counting path mentions rather than findings** (`scripts/` is named 15 times
  across the 10).
- **Deriving the epic mapping from prefix letters** — rejected in favour of
  reading `.history/` directory listings, *which is what caught that `RM-*` is
  `portable-substrate`, not a removal epic.*
- **Four channel reassignments**, each argued: `CL-01-DF-01` and `CL-02-DF-02` to
  "operator running an instrument they built" (both instruments predate the
  ticket); `CL-03-DF-01` to "blind judge" (the readers were sweeping, not
  scoring); `CL-03-DF-05` to "blind judge" (that would credit a prior epic's
  judge for a fact CL-03 re-derived).
- **Putting `CL-01-DF-02` and `CL-02-DF-01` in `unclear`.** It kept them out and
  then **published the strict-reading tally alongside**, so the 0 in `unclear` can
  be audited rather than trusted.

**Anomalies it raised that nobody asked about**, and two of them are structural:

- **The ledger has no `channel` field**, after five epics of rounds being asked
  to report findings by channel. The signal exists only as free text inside
  `found_by`, on 57 of 173 rows. **That is why this measurement is expensive
  every single time.**
- **Two severity vocabularies.** 168 rows use `major`/`minor`/`blocking`; RM-04's
  five use `high`/`medium`. The same five are the only rows in the ledger with no
  `suggested_fix`. All five RD-05 rows are missing `reproduction`, `evidence` and
  `why_out_of_scope`.
- **The ledger is not strictly append-only in history** — it shrank at two
  commits (`4728193` 10→7, `e074ae5` 36→35) before being restored at the
  following reconcile.
- **Seven epics in `.history/` have zero rows in this ledger**, and `PA-01-DF-01`
  cites `HP-06-DF-10` by id — an id that exists nowhere in it.

### The ratio, with its basis, its cap and its channel

**Basis: the harness's `subagent_tokens` field, composition undocumented.** The
same field RM-05 used; **not** comparable to RD-03's named
`input + output + cache_creation` basis, and RD-03's own run differed by 3×
between two bases on identical work.

| channel | findings filed | `subagent_tokens` | per 100k |
|---|---|---|---|
| blind adopter probe | **1** (`CL-04-DF-06`) | 102,034 | **0.98** |
| blind census | **0** | 84,214 | **0.00** |
| **both blind channels** | **1** | **186,248** | **0.54** |
| operator (CL-04 itself) | 5 | **not measured by this field** | — |

**The numerator was NOT budget-capped and nothing was dropped**: CL-04 filed six
against a budget of five and escalated the sixth, exactly as CL-03 did. The
denominator covers the dispatched agents only — **CL-04's own operator spend is
not captured by `subagent_tokens` and is therefore missing**, which is the same
bound RM-05 reported for its three channels and is the reason the "both blind
channels" row is the only honest total on the page.

**The census filing zero is not a failure of that channel.** It corroborated
`CL-04-DF-02` independently and cold, contributed the boundary caveat that makes
§9.4's zero honest, and produced four ledger-schema anomalies nobody had asked
for. **A channel that verifies somebody else's number and finds it right is doing
the job**; counting only novel findings prices that at zero, which is a defect in
the metric and not in the channel.

---

## 12. Findings filed

**Five, at budget, none escalated. Nothing was fixed.**

| id | severity | what |
|---|---|---|
| `CL-04-DF-01` | major | The change rule fails loudly upwards and silently downwards: `scaffold --card-version 4` stamps 4 and serves 5; `--digest-only` reproduces nothing but the current version; `serve` and `scaffold` disagree on the same request |
| `CL-04-DF-02` | major | The per-token ratio has lapsed for two consecutive epics because nothing in the plan, the template or the close-out asks for it |
| `CL-04-DF-03` | minor | Every count in the harvest's method paragraph reproduces except the one that names no field set — and that is the one the headline quotes |
| `CL-04-DF-04` | minor | "Roughly one in six became a finding" is a multiplicity restated as a rate; the measured rate is ~1 of 38 |
| `CL-04-DF-05` | major | The loop closure has no negative control, so "the caveat moves D3" and "the caveat moves D3 on artifacts with the defect" are not separated |

---

## 13. What surprised me, and what passed too cleanly

**The alarm did not fire, and I want to be explicit about why that is not
self-congratulation.** Three of eleven predictions were falsified. But **P1, P2,
P6, P7, P9 and P10 were predictions that the predecessors' own reports would
reproduce**, and reports in this project have been reproducing reliably for
several epics. They were not hard. The three that taught me anything were P3, P4
and P11, and **two of those three were falsified** — which is roughly the hit
rate the epic doc asks for and is not evidence that the evaluation was
well-designed.

**What actually surprised me, in order:**

1. **`--card-version` does not gate content at all.** I expected the version
   number to select a bar. It selects a label. The whole four-versus-five
   comparison that carries the epic's headline was produced by an operator
   keeping a frozen copy of a file, and if that operator convention had lapsed
   the comparison would have silently compared version 5 against version 5.
2. **The refusal that works is structural and cannot ever be extended.** `1|2|3`
   are refused because D1/D4/D5 anchors are gone. That is luck, not design, and
   it will stop working the moment two adjacent versions share a dimension set —
   which 4 and 5 already do.
3. **The token basis existed and I had assumed it did not.** I was about to
   report "there is no basis anywhere" as a finding. The record has four figures
   across three named or half-named bases, and the real defect is narrower and
   worse: the basis lapses because nothing asks for it.
4. **The suite's zero was predicted by the previous epic's diagnosis** and
   confirmed. That is the one place in this record where a prior round's causal
   claim made a forward prediction and the prediction came true.
5. **Two consecutive epics have changed zero bytes of `scripts/`.** The thing
   this repository ships has not moved in two epics of work about whether it can
   be adopted.
