# SV-01 — the negative control ran, and the caveat DISCRIMINATES

**`GOAL-caveat-discriminates`, harnessed. Decided by `SV-05`.**

---

## 1. The one sentence

**On an artifact that plainly LACKS the single-observer property, `D3` read
`4, 4` under card version 4 and `4, 4` under card version 5 — same bytes, same
judge model, same architecture tag, same packet, same dispatch text, the card
version the only mover.** The version-5 caveat did **not** fire, both version 5
judges checked its condition explicitly and found it false by citation, and
`close-the-loop`'s `4, 4 → 3, 3` is therefore a **detection and not a
recalibration**.

**The prediction said so, in advance, and it is on the record.**

---

## 2. The prediction, and when it was sealed

Sealed in commit **`5e07dce`**, **`2026-08-12T16:37:51Z`**, before any judge
agent was launched, while all four cards were unfilled skeletons, and **before
the operator ran the mutation probe that `P6` predicts the outcome of.**
`PREDICTIONS-SV-01.md` beside this file. *(The file's own prose says `16:39Z`;
the commit timestamp is authoritative and is 69 seconds EARLIER, so the seal is
tighter than the file claims, not looser.)*

| | prediction | outcome |
|---|---|---|
| **P1** | both v4 judges award `D3 = 4` | **HELD** — `4, 4` |
| **P2** | at least one v5 judge quotes the caveat and states its condition is not met, citing a non-adapter observer | **HELD — both did**, both citing `tests/test_ledger.py:244/247` |
| **P3** | **THE HEADLINE — `D3` holds at 4 on BOTH v5 passes** | **HELD** — `4, 4` |
| **P4** | `D2` unmoved across the version boundary | **HELD** — `2` on all four cards |
| **P5** | `serve \| wc -c` still 6,281 bytes / 9 rungs | **HELD** — measured, §6 |
| **P6** | gutting `FileJournal` to a list fails ≥1 case in the artifact's own suite | **HELD** — `1 failed, 52 passed` |
| **P7** | the suite reports the same two inherited reds at this tree as at `a527305` | §7 |

**Four of the four real predictions held.** That is a weaker epistemic position
than CL-03's, which got two of four wrong, and this document says so rather than
treating agreement as strength. **§9 states what would have made this round more
informative and did not happen.**

---

## 3. The measurement

One artifact — subject `sv01_negative_control`, declared in `subjects.toml`
**before the scaffold ran** — scored four times with fresh, mutually blind
judges. Two under version 4 from `rubric_v4_frozen.md`, two under version 5.

| card | version | served digest | D2 | **D3** | ran own faults |
|---|---|---|---|---|---|
| `20260812-sv01v4-GL-p1` | 4 | `a213a36770ccab09` | 2 | **4** | yes |
| `20260812-sv01v4-GL-p2` | 4 | `a213a36770ccab09` | 2 | **4** | yes |
| `20260812-sv01v5-GL-p1` | 5 | `2d7d4a0506d9b259` | 2 | **4** | yes |
| `20260812-sv01v5-GL-p2` | 5 | `2d7d4a0506d9b259` | 2 | **4** | yes |

**`D3` delta across the version boundary: 0. `D2` delta: 0.** All four judges
were `claude-opus-5[1m]` — **the tier is recorded on the full model id**, which
is the thing four judge models under two labels made necessary.

`R-H1`/`R-H2` hold by construction: one example, one scope, one architecture
tag, one judge model, and the instrument axis is the only thing that moves.
**Nothing here is averaged with anything.**

### The two v5 judges checked the caveat rather than inheriting it

> **v5 p1:** *"I checked the caveat's escape hatch and it does not bite here.
> `InMemoryJournal` is a working second implementation, not a mock, so this is
> not 'two fakes'. And the real adapter is not doing nothing real: the effect the
> port exists for is observed by something that is NOT the adapter that wrote it,
> at `tests/test_ledger.py:244` and `:247`, which read the raw file with
> `path.read_text()` and assert the exact bytes … framing that `records()` strips
> and therefore cannot vouch for."*

> **v5 p2:** *"Anchor 4 is satisfied on the letter and I tested the caveat's
> demotion condition directly rather than assuming it … with the caveat's
> demotion condition tested and found false, since `tests/test_ledger.py:241-248`
> observes the disk with the adapter out of the loop."*

**This is the negative half of the pair CL-03 could not supply.** CL-03's v5
judges quoted the caveat and took 3. This round's v5 judges quoted the same
caveat, applied the same test, and kept 4. **The caveat's effect is conditional
on the condition it names.**

---

## 4. Why the artifact qualifies — declared before the round, then proved mechanically

Declared in `subjects.toml` and in `PREDICTIONS-SV-01.md` before any judge
existed: `tests/test_ledger.py:244` and `:247` assert the exact bytes at the
ledger path with `path.read_text()` — **an observer of the durable effect that
is not the adapter that wrote it.**

Then proved by the mutation CL-03's operator and both its v5 judges ran, on
**this** artifact, **after the prediction was sealed**:

| tree | `tests/test_ledger.py` (the artifact's own) | the shared 28-case suite |
|---|---|---|
| unmutated | **53 passed** | **28 passed** |
| `FileJournal` gutted to an in-memory list, zero filesystem contact | **1 failed, 52 passed** | **28 passed** |

**CL-03's artifact passed 28/28 through both wirings under the same mutation.**
This one dies. That is the difference between the two cells, and it is
mechanical rather than rhetorical.

**AND THE SECOND ROW IS THE SCOPE BOUND ON THIS WHOLE RESULT.** The shared
behavioral suite — the same file, unedited, that both rounds used — is **blind
to durability on this artifact too**. Everything that separates this artifact
from CL-03's lives in **tests its own author wrote**. So the honest statement of
what was measured is: *the caveat discriminates for a judge who reads or runs the
artifact's own suite.* It says nothing about a judge scoring from a shared
contract alone. Filed as `SV-01-DF-04`.

---

## 5. What the judges rejected — and the 3 they nearly gave

**Every one of the four was asked what it REJECTED, and all four rejected a
lower `D3`.** The reasons are the substance of this round.

- **v5 p1 rejected `D3 = 3`, and proved the case for it first.** *"The shipped
  composition root at `__init__.py:39` is exercised by no case … swap that line
  to `InMemoryJournal()`, delete durability outright, and all 53 + 28 still
  pass."* It kept 4 because *"anchor 4 asks a specific question that is measurably
  answered yes, and the gap is coverage of the composition root"* — recorded
  under `N-D1` rather than laundered into a score.
- **v5 p2 rejected `D3 = 3`, calling it the closest call on the card.** *"F5 — a
  `FileJournal` that keeps a shadow list and never opens a file — passes all 26
  paired cases and all 28 shared cases, killed by exactly one test. That is very
  near 'the real adapter does nothing real'. I kept 4 because the caveat's stated
  test is whether the ONLY observer is the writing adapter, and it isn't;
  demoting would have applied a condition the rubric doesn't state."*
- **v4 p1 rejected `D3 = 3`** on the ground that the fake is cheap — *"scoring
  low because I'd have written a harsher rubric substitutes my rubric for the
  served one. If anchor 4 should cost more, fix the anchor, not the judge."*
- **v4 p2 rejected `D3 = 3`** on the composition-root finding, for the same
  reason as v5 p1.

**Read that carefully, because it is the strongest thing in this document and it
cuts both ways.** A route to 3 was available on this artifact and all four judges
found it independently — *one test, and only one, separates the real adapter from
a fake*. The two version 5 judges declined it **by applying the caveat's literal
condition and finding it false.** The caveat is therefore doing discrimination
work rather than acting as general downward pressure — **and it is a narrow
margin, one test wide, which the caveat's own wording is what keeps on the right
side of.**

Also rejected, by three of four judges independently: **`D2 = 0`**, which the
literal ladder demands. See `SV-01-DF-02`.

---

## 6. The served surface — the metric

```
serve | wc -c    6,281   (unchanged)
rungs                9   (unchanged)
served_digest    sha256:2d7d4a0506d9b259   (unchanged)
```

**The card was not touched.** No anchor, no caveat, no scoring rule, no rung. A
negative control is a measurement, and a measurement that edits its own
instrument has measured nothing. **`serve` is byte-identical to `a527305`.**

The version 4 arm reproduces `sha256:a213a36770ccab09` byte for byte from
`rubric_v4_frozen.md` with `--card-version 4`. **That is the fifth consecutive
round to reproduce an old card by operator sequencing rather than by tooling —
`FI-06-DF-11(c)`, still open, now five of five.**

### The instrument's own counts, at this ticket's tree

```
check specs/results/scorecards      91 cards, 91 filled, 330 problems
audit                               0 violation(s)
contested --root ...                9 contested dimensions over 37 judge groups,
                                    0 unrecorded, 0 tier splits in this round
```

**330 is the same figure CL-03 reported over 87 cards.** The card count rose to
91 because this round added four and **no sealed card was edited**. This round
introduces **no new problem and no new contested dimension**: `D2` and `D3` are
unanimous on both sides, so there is nothing to record.

---

## 7. Suite numbers, with their trees

**Every number below names the tree it came from. No `git archive` figure
appears here** — these tests read git history and an archive has no `.git`.

| tree | commit | working state | result |
|---|---|---|---|
| `.../scratchpad/SV-01/operator/baseline-a527305` | `a527305` | **clean detached `git worktree` checkout of the epic branch point** | **3 failed, 1495 passed** (1189.70s) |
| `wt-epic-score-drives-validation-SV-01` | this ticket | the work | *(§7.2)* |

### 7.1 THE STATED BASELINE IS 2 AND THE MEASURED BASELINE IS 3

**The work order for this ticket says "2 failed at `a527305` in a real
checkout — both deliberate and inherited". A clean checkout of `a527305` fails
THREE.** The third is not this ticket's, it is not new, and it is not repaired.

| # | red at `a527305` | what it is |
|---|---|---|
| 1 | `tests/test_architecture_tags.py::test_the_same_tag_control_holds` | `RM-06-DF-01`, inherited and deliberate |
| 2 | `tests/test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer` | the pricer grep tripped by narrative documents, inherited and deliberate |
| **3** | **`tests/test_card_has_one_home.py::test_only_the_card_states_a_dimension_an_anchor_or_a_scoring_rule`** | **tripped by the epic's OWN opening commit** |

The third names four lines, all of them written by `a527305` itself:
`SCORE-DRIVES-VALIDATION-EPIC.md:40-41` (*"it serves exactly two scored
dimensions — **D2 complexity** and **D3 modularity**"*) and
`specs/desired_program_model/ticket_plan.yaml:8` (the same sentence in the
epic's own charter text).

**It is the SAME CLASS as red 2**: a narrative document that has to describe the
instrument, tripping a static check on the instrument's description. The epic
charter states the rule *"no new gates — seven epics of static checking, zero
bugs caught"*, and its own opening commit is the seventh epic in a row to be
caught by one of the old ones for saying what it is about.

**It is not repaired, for the same reason the other two are not**, and because
repairing it means editing the epic charter, which is not this ticket's surface.
**The offender list is byte-identical at this ticket's tree** — SV-01's own
documents add no offender — which is how it was established that the third red is
inherited and not produced here.

### 7.2 This ticket's tree

---

## 8. What SV-01 REJECTED

- **Manufacturing a control artifact by repairing CL-03's fixture.** A tree built
  to lack the property, by the round measuring whether the property matters, is
  `MF-020` in its purest form. Rejected before anything was written.
- **Scoring the original directory rather than a copy.**
  `specs/results/scorecards/ports-as-adapters/blind/artifact_T` sits two
  directories from **ten published cards scoring the same bytes**, and
  `_subject_block` refuses to blind a scope path that spells a published label.
  The tool's own remedy — copy the tree somewhere that names no label — is what
  was done.
- **Copying `EVIDENCE.md` with the artifact.** Its first line names the published
  label. It is the producing round's instrument output, not part of the artifact.
  Excluded, and the exclusion is declared in `subjects.toml` rather than left
  silent, because it means this scope is **not** byte-identical to that directory.
- **Reusing CL-03's four v4 cards instead of running fresh ones.** Two v4 cards
  on these exact bytes already exist and read `D3 = 4`. They are a **different
  round, packet and dispatch**, so using them would have made the card version
  one of several movers. They appear in §3 of the predictions as a stated prior
  and **are not averaged with anything here.**
- **Running an unblinded round, as CL-03 did.** CL-03's reason — one artifact,
  one arm, the treatment is the card version — applies here too, and blinding was
  used anyway: `subject.name` is `null`, `declared_effect_boundary` is withheld,
  and the label is drawn from a pool excluding every published label. It cost
  nothing and it is strictly better.
- **Breaking the `4, 4` tie with a third pass.** There is no tie. Had `D3` come
  back split, the sealed predictions committed in advance to recording it as
  contested and NOT adjudicating it — a third pass produces a third number.
- **Repairing anything the judges found.** Four independent judges found the same
  untested requirement; it is **filed** (`SV-01-DF-05`), not fixed. This round
  fixes nothing during a measurement.
- **Discarding a card over a disclosed leak.** All four judges were handed a
  scratch directory holding a prior round's artifact and a prior `D3 = 4`
  (`SV-01-DF-01`). Discarding a card after seeing its score is the one move a
  round may not make. It is recorded, and it is reported as cutting toward the
  predicted answer.

---

## 9. What this result does NOT establish — read before quoting it

1. **ONE ARTIFACT, ONE MODEL.** `claude-opus-5[1m]` on all four cards. The
   caveat's behaviour under `claude-sonnet-4-5` or any other judge is unmeasured
   here. `R3`: this claim's scope is one scope, one example, four cards.
2. **THE POSITIVE CELL IS STILL ONE ARTIFACT.** The pair is now
   `has-the-property → 3` (CL-03) and `lacks-it → 4` (here). **Two cells is a
   negative control, not a calibration curve.** Nothing licenses a claim about
   how the caveat behaves on artifacts unlike either.
3. **THE TWO CELLS ARE ON DIFFERENT EXAMPLES.** CL-03 scored `toolchain_removal`
   / `toolchain_fixture`; this round scored `ab_quota_ledger` /
   `sv01_negative_control`. Both derive the **same architecture tag**
   (`ports-and-adapters`), which is why the pairing is legitimate — but **the
   two deltas are not two rows of one table** and must never be averaged. What is
   compared is *a delta of −1 under a true condition* against *a delta of 0 under
   a false one*.
4. **AGREEMENT IS NOT STRENGTH.** All four sealed predictions held. A round whose
   every prediction holds has learned less than one that was surprised, and the
   most informative thing here was produced by asking the judges what they
   rejected — where a route to 3 turned out to exist on this artifact and be one
   test wide.
5. **THE DISCRIMINATION IS CONDITIONAL ON THE ARTIFACT'S OWN TESTS** (§4), and a
   prior `D3 = 4` was one `ls` away from every judge (§`SV-01-DF-01`).

---

## 10. What this settles elsewhere, and what inherits nothing

**Because the answer is NOT a null, no claim elsewhere is corrected.** The rule
this ticket was opened under — *a null must be reported as loudly as CL-03
reported the move, naming every claim that inherits the correction* — is
discharged by there being no null, and the list is stated so that its emptiness
is a measured result rather than an omission:

| claim | status after SV-01 |
|---|---|
| `CL-03` RESULT §1: *"D3 went 4, 4 to 3, 3 … the card iteration moved the score"* | **stands, and is now a detection** — it has its negative control |
| `CL-04`: *"our D3 caveat fired on a stranger's artifact it was never written for"* | **stands** — the blind adopter's firing is now one of two same-direction firings with an opposite-direction control beside them |
| `NEXT-EPIC.md` §0-AAAAAAAA §2 / `CL-04-DF-05`: *"it demonstrates plumbing … it does not measure discrimination"* | **discharged.** The missing cell is filled. |
| `SCORE-DRIVES-VALIDATION-EPIC.md` §4: *"the D3 caveat has no negative control"* | **no longer true**, as of this ticket |
| `GOAL-caveat-discriminates` baseline: *"no artifact lacking the property has ever been scored under both versions"* | **superseded by measurement** — one has, and the result is `4, 4` both sides |

**Had `D3` come back `3, 3`, every row above would have needed rewriting and
this section would have been the document.** It was written before the numbers
were known, in `PREDICTIONS-SV-01.md` §5.

---

## 11. Findings filed — five, none repaired

| id | what |
|---|---|
| `SV-01-DF-01` | **the judge scratch paths were not ticket-specific and all four held a prior round's artifact and a prior `D3 = 4`** |
| `SV-01-DF-02` | **`D2`'s ladder is non-monotone: rungs 0 and 2 are simultaneously satisfiable**, and it names the cause of `cl03-v5-d2-spread-2` |
| `SV-01-DF-03` | `git status` leaks sibling cards and the dispatch's forbidden list did not name it |
| `SV-01-DF-04` | the shared behavioral suite is blind to the property the caveat names, so the discrimination is conditional on artifact-authored tests |
| `SV-01-DF-05` | **three defect classes four judges found in the scored artifact that BOTH suites miss** — filed rather than left in card notes, which is the consumption step this programme measured as its bottleneck |
