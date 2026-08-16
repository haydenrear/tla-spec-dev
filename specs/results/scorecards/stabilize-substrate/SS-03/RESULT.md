# `SS-03` — this project's own judged goals, measured rather than fixed

**Ticket:** `SS-03`, issue #274, epic `stabilize-substrate`.
**Branch base:** `25600fa04ef26eb352cf3e6db5990e7f36a20ea8` — the epic tip,
resolved once from `origin/epic/stabilize-substrate` and branched from the OID.
**Every figure below names the tree it was measured on.**

**AMENDED AFTER INDEPENDENT REVIEW.** PR #281 was sent to a reviewer instructed
to refute it. Verdict CHANGES: ten claims confirmed, three refuted, two partial.
Everything below carries the amendments; §10 lists what the review broke and what
it confirmed, and **the largest finding in this ticket is now one the reviewer
found, not one I did** (`SS-03-DF-05`).

**The short version, and it is the unflattering one.** The numerator has never
moved off zero and this ticket did not move it. The denominator moved twice, in
both directions, for two different reasons — once because the corpus grew and
once because the instrument was repaired. And the deepest result is that for
**14 of the 23 judged goals no card produced the baseline number at all**, so
the rule they are being measured against is not merely unmet for them, it is
**unsatisfiable**.

---

## 1. The census, re-derived — and `0 of 18` is wrong twice over

| tree | recogniser | figure | population |
|---|---|---|---|
| `ea624b9` (issue #271) | keyword | `0 of 18` | pre-`cut-the-apparatus` |
| `436c78c` (epic base, charter §0) | keyword | **`0 of 20`** | 122 plans, 31 goals |
| **`25600fa`** (this ticket's base) | keyword | **`0 of 24`** | 123 plans, 36 goals |
| `25600fa` (SS-03 stage one) | declared `kind` alone | `0 of 23` | 123 plans, 36 goals |
| **`e4b13a2`+ (SHIPPED)** | **declared `kind`, prose may only withhold** | **`0 of 17`, 6 `UNDECIDED`** | 123 plans, 36 goals |

**`0 of 20` had no sealed artifact behind it until this ticket made one.** The
file the goal pointed at reports 123/36/23, not 122/31/20 — see §10.1. A clean
`436c78c`, measured in a detached worktree with an empty `git status`, does give
`0 of 20`, and is now sealed as `baseline_is_a_card-436c78c-CLEAN.txt`.

**`0 of 18` is corrected explicitly and twice.** The charter already corrected it
to `0 of 20` at `436c78c`, and that correction is right at that tree. **It is
already stale for every ticket agent on this epic**: at `25600fa`, the tree every
`SS` ticket branches from, the unrepaired instrument reads **`0 of 24`**.
Re-derived, not quoted — `baseline_is_a_card-25600fa-PRE-REPAIR.txt` in this
directory is the raw output.

**Both movements are denominator movements. The numerator held at zero in all
four rows.**

- `18 → 20`: `cut-the-apparatus` added goals. Charter §0, already stated.
- `20 → 24`: **scaffolding this epic's own workflow** added five goals to the
  live plan and four of them matched the keyword list. **Corpus movement, no
  repair involved.** `denominator_rule`.
- `24 → 23`: **`SS-00-DF-03`'s repair**, stage one. Net `−1`, and the net badly
  understates it — see §3.
- `23 → 17`: **the review's amendment to that repair.** Six goals move to
  `UNDECIDED`, and they are exactly the six `SV-03-DF-02` already disputed — §3.1.

**A figure that already moved inside the charter, again.** Charter §0 and
`GOAL-judged-goals-compliant`'s baseline both say the census classified **three**
of this epic's five goals as judged. At `25600fa` it is **four** — commit
`25600fa` itself edited the plan's prose, and the keyword matcher followed the
prose. **That is `SS-00-DF-03` demonstrating itself between two commits of the
same plan.**

---

## 2. `SS-00-DF-02` — the id collision, repaired, with its failing input

**The repair.** `distinct_goals` keys on the DECLARED `(workflow, goal id)` pair
— `status.workflow`, falling back to `epic.id`, never inferred from the path. A
reused id is reported as its own verdict class, `id-collision`, and is **never
resolved**: the census names both workflows and stops.

**The demonstrated failing input, on the real record.** The kickoff's first plan
draft reused `GOAL-four-results-stand` and was never committed, so the subject is
reconstructed over **every plan on disk** by renaming exactly the one id the
kickoff renamed and then backed out. Nothing on disk is touched; the rename is in
memory.

```
ids renamed in the in-memory draft                 : 1
OLD key (id alone)  -> distinct goals              : 35
NEW key (workflow, id) -> distinct goals           : 36
collisions named rather than collapsed             : ['GOAL-four-results-stand']
```

**35 where 36 exist — the kickoff's measured figure, reproduced exactly.** Pinned
by `tests/test_goal_baseline_is_a_card.py::test_a_reused_goal_id_is_named_and_never_collapsed`.

**The record was checked for EXISTING collisions, as the finding demanded.**
**Zero.** 123 plans, 36 distinct `(workflow, id)` pairs, 36 distinct ids — the
two counts agree, so the census's denominator is not currently understated. The
`continues:` field on `GOAL-four-results-still-stand` is why, and it remains what
the finding called it: a workaround, not the fix. A future reuse is now named
instead of absorbed.

---

## 3. `SS-00-DF-03` — the keyword matcher, retired, and what replaced it

**Classification now reads the DECLARED `kind` field**, whose four values are
fixed by `goals-and-evaluation.md`'s "Goal kinds": `eval` is the judged/scored
kind; `quality` is "an invariant/coverage/robustness property **with a deciding
command**"; `perf` needs a baseline run; `integration` names a graph. A goal
declaring **no recognised kind is `UNDECIDED`** — never PASS, never a confident
`not-judged` (`r1_now_requires_an_absent_input`; the same shape as
`set[str] → set[str] | None`).

**`MF-020`: this was not fitted to a known answer, and the evidence is that it
moves goals in BOTH directions.**

| | count | effect |
|---|---:|---|
| prose said judged, declared kind says **command** (over-reach) | **7** | leave the judged set |
| prose said not judged, declared kind says **judged** (under-reach) | **6** | enter the judged set |
| **total disagreement** | **13 of 36** | 36% of the record |

A rule fitted to "this epic's five goals must stop being judged" would have moved
seven out and nothing in. Six sealed goals of other epics entered the denominator
because the record says they are `eval`. **The net is `−1`; the churn is 13.**

**No harness string in the plan was reworded to flip a classification.** The
`kind` values this repair reads were written at kickoff, before the finding was
filed. **`SS-00-DF-03`'s own `suggested_fix` names `kind` as the option to
take** — the field was the owner's suggestion, not this ticket's invention.

### 3.1 The review amended this, and the amendment makes it worse — correctly

**`SV-03-DF-02` is in the ledger at this tree and I did not cite it.** It names
nine goals as naming no judged instrument — *"decided by seeded mutants, a bench,
or findings-per-token"* — and **six of my six "under-reach" re-admissions are
inside that list.** I re-admitted all six on a `kind: eval` field without
rebutting the prior finding, then reported them among the "unsatisfiable" and
escalated a skill diff on that basis. The review is right that this cannot stand.

**The rebuttal, and it is not a defence of the re-admission.** `SV-03-DF-02` read
the *harness prose*; the plan declares `kind: eval`. **Both are in the record and
they contradict each other**, and nothing in this repository validates
`epic_goals`, so `kind` is a convention the record keeps rather than a field
anything enforces. A convention contradicted by a filed finding is not declared
data an instrument may lean on. **So the answer is neither: it is `UNDECIDED`.**

**The shipped rule, amended.** The declared field still decides, and the retired
keyword recogniser gets **one vote which is a veto with no positive power**:
where a goal declares `kind: eval` and its statement, metric, harness and target
name no judge, rubric, card or dimension anywhere, the two signals disagree and
the verdict is `UNDECIDED`. **Prose can move a goal out of a confident class and
into a refusal; it can never put one in.** That is the direction that matters —
`SS-00-DF-03` was prose *asserting* judged-ness and inflating a denominator.

**The rule refuses six goals, and they are exactly `SV-03-DF-02`'s six.** Not a
set I chose: the veto reproduces a filed finding's own list, and the three of its
nine that it does not refuse are the three declaring a command kind, where field
and finding agree. Pinned by
`test_what_the_rule_refuses_is_exactly_the_prior_findings_disputed_goals`.

**Movement: `0 of 23` → `0 of 17`, six goals to `UNDECIDED`. Numerator still
zero.** Denominator fell because the instrument stopped answering a question the
record does not answer.

### 3.2 And a stricter rule the review is also right about, measured and NOT adopted

**15 of the 23 declared-judged goals have harness text naming no judge, rubric,
card or dimension** — many are bare ticket pointers like `"CL-01, decided by
CL-04"`. Under the shipped rule 8 of those survive as judged, because the
keyword lives in their `metric` or `statement` instead. The census prints the
counterfactual:

| rule | judged |
|---|---:|
| (A) declared field alone — SS-03 stage one | 23 |
| **(B) SHIPPED** — declared field, prose may only withhold | **17** |
| (C) the `harness` field itself must name a judge/rubric/card/dimension | **9** |

**(C) is not shipped and the reason is directional:** it decides judged-ness from
the harness *string*, which is the exact field `SS-00-DF-03` established cannot
carry that decision. Adopting it makes the recogniser **more** prose-bound, not
less. It is printed with all eight goals named so a reader who prefers (C) can
have it, and so the choice is on the record rather than inside the number.

**The retired matcher is kept as `keyword_judged()` and asserts nothing.** It is
printed beside the declared answer so all 13 disagreements are on the record by
name and any of them can be contested.

**Coordination with `SS-04` — and this is a PREDICTION, not a verified fact.**
`SS-04` repairs the same class of bound in `scope`. **`SS-04` does not exist
yet**, so "they do not share a recogniser" cannot be verified against it. What IS
verified, today: this classifier reads one declared YAML field and does no text
matching to assert anything;
`SS-03`'s classifier reads one declared YAML field of the plan schema and does no
text matching at all; `scope`'s problem is recognising counted figures in free
prose, which is a different problem with a different failure mode. Nothing in
`baseline_is_a_card.py` is importable by `score_tools.py` and nothing imports it.

**The rule was run against the sealed record before shipping, and what it refuses
is reported.** Over 123 plans and 36 goals it refuses **nothing** — `undecided` is
`0`, because every goal in this record declares a `kind`. The `UNDECIDED` branch
is therefore exercised only by the absent-input demonstrations
(`{}`, `kind: ""`, `kind: vibes`, and a `kind: null` goal whose prose is loud with
judged vocabulary). **A branch with no live subject is worth saying out loud**:
the refusal path is real and tested, and this record gives it nothing to refuse.

---

## 4. The result the ticket is actually for — and it bounds the goal

### 4.1 Clause (c), counted: 23 of 23 are sealed

**Every judged goal is declared ONLY in a plan under `specs/.history`** — `23 of
23` under stage one, `17 of 17` under the shipped rule. Not one is in the live
plan; the live plan's five goals all declare `kind: quality` and are command
goals.

**So `23 of 23` cannot be made compliant without editing a record `R-H4` seals,
and none was edited.** Under the inherited keyword population of 24, the split is
`20` sealed and `4` reachable — and those four are this epic's own, which the
repaired recogniser says are not judged goals at all. **Either way the reachable
judged population is zero.**

### 4.2 And for most of them the rule is unsatisfiable, not merely unmet

Every judged goal's baseline was read against the sealed cards. `SS-03-DF-03`.

| what produced the baseline number | goals |
|---|---:|
| an exact, nameable set of cards | **6** |
| a card population that is exactly enumerable | **2** |
| **no card at all** | **15** |
| | **23** |

**Corrected by the review from 9/14 to 8/15.** `GOAL-loop-closes-once`'s
`baseline.value` begins literally *"ZERO."* — an absence claim — and this index's
own header says a card list is listed only where the cards produced **the
headline**. I filed it `population-figure` on the strength of a *supporting*
clause (22 cards, re-derived and correct). By my own stated criterion that is
corroboration, not attribution. Moved, and the 22 cards are recorded in that
entry's prose rather than in `cards:` **so that they cannot be counted**.

**And a circularity the review named that I have not repaired.** The 15
`no-card-produced-it` entries are exactly the entries with `cards: []`, and both
were decided by the same pass — the one that went looking for cards and did not
find them. **Nothing here independently separates "no card could carry this" from
"I could not attribute it".** Each entry argues the distinction in its `note:`,
and an argument is not a test. **Treat 15 as an upper bound on the unsatisfiable
population, not as a measurement.**

The 14 are absence claims (*"NOT MEASURED"*, *"NO TAGS EXIST"*, *"0 FOR 7
EPICS"*, *"ZERO"*, *"NEVER ASKED"*), surveys of skills or instruments, per-mutant
kill-table counts, byte counts from `serve | wc -c`, and source-literal readings.
**A judged card carries a dimension score and a rationale. It carries no
per-mutant cell, no instrument enumeration and no absence.**

**This reframes the figure.** `goals-and-evaluation.md`'s rule — *"`baseline.evidence`
is the card, not the folder"* — is written for a baseline that a card produced.
If the 14 are excluded as out of the rule's reach, **the honest denominator is 9
and the numerator is still zero.** That is not a better number; it is a more
truthful one, and the correction is escalated rather than applied, because the
sentence that needs changing is in a skill this repository reads and never edits.

### 4.3 The additive index — and it is not compliance

`GOAL-judged-goals-compliant/baseline_resolution_index.yaml`: **23 entries — one
per goal that was judged under stage one — 8 carrying an exact card list (120
card references), 15 carrying `cards: []` and the reason no card can be listed.**
Of the **17** goals the shipped rule still calls judged, **8 are located by the
index and 9 are not.** Every listed card was
verified to exist, to parse, and to carry a field that reproduces part of the
goal's `baseline.value`; the three population figures were re-derived
independently at this tree (27 of 27 with `D2 = 2`; 22 cards with `D3 = 4`;
55 of 59 with `D1 = 3`, the four exceptions named).

**The instrument reports these as `card-via-index`, a verdict class of its own,
and NEVER adds them to `card`.** Pinned by a test. An index entry is SS-03's
assertion about somebody else's sealed number; a compliant goal is the epic that
wrote the number saying so itself. **The `card` count is 0 at the tip and the
index cannot move it.**

Two of the index's entries record that the sealed figure they locate **has since
been refuted** (`GOAL-D2-can-move`'s `27 of 27` was re-derived as `35 of 35`;
`GOAL-validation-is-scorable`'s `55 of 59` as `56 of 63`). The index says which
cards produced the sealed number. **It does not say the sealed number holds.**

### 4.4 Path defects found while doing it

Six, all reported and none repaired (they are in sealed plans). **The review
noted these were prose-only with no ledger id; the load-bearing one is now
filed as `SS-03-DF-07`** because it is `SS-01`'s live surface and `SS-01` and
`SS-08` must both meet it. The other five stay prose: each is a pointer inside a
plan `R-H4` seals, none is anyone's live surface, and filing five rows that name
no actionable surface is the routing-instead-of-consuming the epic warns about.

1. `GOAL-simpler-same-behavior` — declared path drops one segment; the cards are
   under `.../scorecards/architectural-coherence/ex3_over_complex/`. This is the
   whole cause of its `unresolvable` verdict.
2. **`SS-03-DF-07`** — `GOAL-instruments-can-fail` cites
   `specs/desired_program_model/deferred_findings.yaml`, which **the ledger
   relocation deleted**. A sealed goal's evidence became unresolvable because a
   live path moved under it, and `R-H4` forbids repairing it where it broke.
   **The general form: the seal protects a record's TEXT and protects nothing
   the record POINTS AT** — a sealed baseline is only as re-readable as the
   mutable tree around it, which no rule in this project states. All four
   finding ids the baseline cites do resolve at the ledger's new path, so the
   content survived and only the pointer broke. `SS-01`'s surface; filed, not
   fixed.
3. `GOAL-scope-loss-catchable` and `GOAL-tags-earn-their-place` — cite
   `specs/results/scorecards/subtract-to-measure/`, which holds **zero** cards at
   any depth and has no `SM-05` subdirectory.
4. `GOAL-loop-reaches-the-program` — cites `close-the-loop/`, **zero** cards.
5. `GOAL-loop-closes-once` — section pointer names `RM-05/RESULT.md — section 4`,
   which is a different section; the claim is §1.3.
6. `GOAL-portable` and `GOAL-validation-is-scorable` — name card populations by
   **count** ("the 73 sealed cards", "the 87 sealed cards") with no path. Both
   happen to reproduce exactly as a `run_id` date slice; **nothing in the record
   says that is the rule.**

---

## 5. Clause (a): this epic's own five goals

**All five now resolve to a concrete artifact the evaluation can re-read**, and
in every case it is the **sealed raw output of the command that produced the
number**, listed before the narrative. Verified by resolution, not by assertion.

| goal | `baseline.evidence` now resolves to |
|---|---|
| `GOAL-absent-input-consumed` | `class-rows-436c78c.txt` |
| `GOAL-tree-stabilizes` | `kickoff/pytest-baseline-436c78c.txt`, then `collection-436c78c.txt` |
| `GOAL-judged-goals-compliant` | `baseline_is_a_card-436c78c.txt`, then `SS-03/baseline_is_a_card-SS-03-tip.txt` |
| `GOAL-counted-figures-reach-the-record` | `scope-work-directing-docs-436c78c.txt`, then `scope-whole-record-436c78c.json` |
| `GOAL-four-results-still-stand` | `serve-digest-436c78c.txt`, then `audit-436c78c.txt` |

**Nothing but the `evidence` pointer was touched.** No `baseline.value` was
edited except `GOAL-judged-goals-compliant`'s, which carries an **appended,
explicitly labelled supersession paragraph** naming both movements with numerator
and denominator — never a silent correction, and the original sentence is intact
above it. No `measured_at` changed. **No `baseline.md` of another goal was
edited**, because four of the five sit outside this ticket's conflict keys.

**And no test asserts that these five comply.** The file's own rule — *"a test
that failed until every plan cited a card would be the eighth gate, and a gate on
the epic owner's prose"* — survives this ticket intact.

---

## 6. A defect this ticket committed, measured, and repaired: `SS-03-DF-02`

**Recorded because hiding it would remove the record of what happened.** While
repointing the five evidence fields, SS-03 left an unquoted `": "` inside one of
them. The plan stopped parsing. The next census run reported **122 plans and 31
goals instead of 123 and 36** — five goals gone — **with no warning, no error and
no line saying a plan had been skipped**, because `every_plan` wrapped
`yaml.safe_load` in `except Exception: continue`.

**That is `SS-00-DF-02`'s direction on a different input**, and it is the
absent-input class on the instrument that measures the absent-input class: *"read
and found nothing"* answered with *"read nothing"*, confidently.

Repaired in the same file: `_walk_plans` returns the plans that parsed **and**
the plans that did not, and the population block now prints
`plans that DID NOT PARSE and were dropped (SS-03-DF-02) : N` with each file and
its parser error. **At this tree that number is 0** — verified, not assumed, and
nothing before this ticket would have said so.

---

## 7. `SS-03-DF-04`: the plan loads with both loaders and they disagree

The epic notes require that the plan load with both loaders. It does. **They are
not equal.** At least six scalars differ between `yaml.safe_load` and
`scripts.extract_spec_manifest.parse_simple_yaml`, including `epic.base_note`,
`purpose`, two ticket `objective`s and two `baseline.value`s. **The divergence is
pre-existing** — it reproduces at `25600fa` before any SS-03 edit — and **the five
`evidence` fields SS-03 wrote are identical under both loaders**, checked. Filed,
not repaired: neither loader is in this ticket's conflict keys.

*"Both loaders accept it"* and *"both loaders agree what it says"* are different
claims, and the epic currently asserts the first while relying on the second.

---

## 8. The tree — FIVE numbers that sum, and they sum at three points

**SS-01 added an `xfail(strict=True)`, so the tree has five buckets, not four.**
The base this ticket compares against is no longer its own `17/1483/4/1504`;
that figure is historical. **The comparison base is the merged epic tip.**

```
$ uv run --with pytest --with pyyaml -m pytest tests -q
epic tip 50046b2      8 failed / 1509 passed / 0 skipped / 1 xfailed   collection 1518
SS-03 pre-close       8 failed / 1524 passed / 0 skipped / 1 xfailed   collection 1533
SS-03 POST-CLOSE      7 failed / 1521 passed / 0 skipped / 1 xfailed   collection 1529
```

`8+1509+0+1 = 1518` ✓  `8+1524+0+1 = 1533` ✓  `7+1521+0+1 = 1529` ✓

**`7 / 1521 / 0 / 1 / 1529` IS THE AUTHORITATIVE FIGURE** — it is the tree this
branch actually ships and the one `SS-08` will stand in. §8.2 explains why a
different figure is sealed inside the history entry.

### 8.1 Epic tip → SS-03 pre-close: every movement attributed

| | tip | pre-close | movement | attribution |
|---|---:|---:|---:|---|
| failed | 8 | 8 | **0** | **and that is not "nothing happened"** — see below |
| passed | 1509 | **1524** | **+15** | all 15 newly collected nodes are green |
| skipped | 0 | 0 | **0** | SS-01 cleared all four; nothing here re-introduces one |
| xfailed | 1 | 1 | **0** | SS-01's strict xfail, untouched |
| collected | 1518 | **1533** | **+15, DENOMINATOR ROSE** | `+17/−2`: `+10` SS-03 tests, `+1` the YAML sweep picking up the resolution index on its own, `+6/−2` from `open ticket SS-03` re-parametrising four sweeps |

**The flat red count hides a swap and is reported rather than left flat.** One red
cleared — `test_a_real_epic_plans_judged_baseline_cannot_be_re_opened`, the `R1`
subject this ticket moved — and **one new red appeared, mine**:
`test_a_reused_goal_id_is_named_and_never_collapsed`, which asserted
`renamed == 1` when the merge made it 2. **A red count that does not move is not
evidence that nothing moved**, which is this epic's own thesis pointed at its own
report.

**That new red is `SS-03-DF-08`, and it is my own `SS-03-DF-01` committed a
second time**: every `close ticket` snapshots the live plan under
`specs/.history`, each snapshot declares the same workflow and carries the same
goal, so the count was 1 when I wrote it and 2 the moment SS-01 merged.
**The collapse figure it demonstrates — OLD key 35 where 36 goals exist — is
unchanged on the merged tree.** What I had pinned was incidental to the record's
size. Repaired; two instances of this class in one ticket, both in one file,
**both found by the record moving rather than by any check.**

### 8.2 The close changes the tree it seals — disclosed, not left for `SS-08`

`close ticket` **seals the history entry and removes the ticket workspace in one
operation**, so the sealed entry can never describe the tree it produces. `SS-01`
hit this and disclosed it; so does this ticket.

| | sealed inside `…/ticket-001-SS-03/results/` | live tree after close |
|---|---|---|
| figure | `8 / 1524 / 0 / 1 / 1533` | **`7 / 1521 / 0 / 1 / 1529`** |

**The `−4 / −3 / −1` between them has TWO causes, and attributing all of it to
the close would be wrong:**

1. **`SS-03-DF-08`'s repair: `−1 failed`, `+1 passed`, collection flat.** The
   pre-close run was taken before I fixed the `renamed == 1` assertion.
2. **The close's workspace removal: `−4 collected`, `−4 passed`.** Deleting
   `specs/tickets/SS-03/` collapses six re-parametrised ids back into two —
   `complexity_ledger.yaml0/1` and `ticket.yaml0/1` become
   `complexity_ledger.yaml` and `ticket.yaml`, and `spec_manifest.yaml6/7`
   disappear. `−6/+2 = −4`, node for node.

`1524 + 1 − 4 = 1521` ✓  `8 − 1 = 7` ✓  `1533 − 4 = 1529` ✓

**The `+4` and the `−4` are the epic's own machinery and NET TO ZERO across the
pair, so neither belongs to this ticket's slice.** `open ticket` inflates
collection by 4 and `close ticket` removes it again, on every ticket — the owner
has since measured the same thing and amended the plan to say so. **This
ticket's real contribution to collection is `+11`**: 10 tests and the one node
the YAML sweep added by finding the resolution index on its own.

**Which is authoritative: the POST-CLOSE figure**, `7 / 1521 / 0 / 1 / 1529`.
The sealed one describes a tree that no longer exists on any branch. It is not
wrong — it is a faithful record of what was measured — but it is not the tree
anyone can stand in, and `SS-08` must use the post-close figure.

### 8.3 The 7 reds at the tip, enumerated so they sum

| file | rows | owner / cause |
|---|---:|---|
| `test_source_citations.py` | **3** | two from the scaffolded manifests (`SS-06`'s), one inherited (`specs/program_model/spec_manifest.yaml`) |
| `test_instrument_demonstrations.py` | 2 | **deliberate**, `CA-04-DF-04` |
| `test_architecture_tags.py` | 1 | **deliberate**, `RM-06-DF-01` |
| `test_ticket_retirement.py` | 1 | seven tickets still `planned`; clears as they close |
| | **7** | |

`3 + 2 + 1 + 1 = 7` ✓ — **three are deliberate and were not repaired silently.**
**The nine reds that were `SS-01`'s at my base are all gone**, and `audit` now
reads **0 violations on this checkout** where it read 9: `SS-00-DF-01` is
repaired upstream and I did not touch it.

## 9. What this ticket did NOT do

- **It did not move the numerator.** `card` is 0 at the tip, as at the base.
  Nothing in the record was made compliant, because doing so requires editing a
  sealed plan.
- **It did not build the sweep** that would consume `SS-03-DF-01` as a class —
  a check that no test indexes the live plan by a goal id it has not first
  asserted exists. One instance repaired; the class is filed.
- **It did not write the skill diff** `SS-03-DF-03` calls for. Skills are read
  from this repository and never edited; it is escalated in the PR body.
- **It did not repair the two evidence paths that belong to `SS-01`** or the two
  sealed command goals whose evidence does not resolve.
- **It added no gate.** `baseline_is_a_card.py` still has no failing exit path,
  is imported by nothing in `scripts/`, and exits 0 on every input including the
  failing one — executed at the end of every run, not asserted.
- **`SS-03-DF-07` is NOT resolved by SS-01, and I checked rather than assumed.**
  `do_not_assume_a_filed_finding_is_open` cuts both ways. At the merged tip
  `test -e specs/desired_program_model/deferred_findings.yaml` is still false and
  `git log 25600fa..50046b2` on that path is empty — nothing was restored or
  shimmed. **What SS-01 did fix is the other half**: `disposition.LEDGER` and
  `score_tools.LEDGER_LIVE` both name the new path, so every live consumer reads
  the ledger where it is. **The content is reachable; the sealed pointer is not**,
  and that is exactly the half `R-H4` makes unfixable in place.
- **It did not re-run `skill-manager home close-out --into`**, per the owner's
  instruction. **Nothing was changed inside this worktree's Skill Manager home**
  at any point in this ticket — the last gate run before the instruction reported
  `safe: true`, zero blockers, all 22 units `unchanged`, and no edit has been made
  to it since.

## 9.1 Reconciliation onto the merged epic tip

Merged `50046b2` (SS-01) into `feature/SS-03`. **One conflict, in
`specs/deferred_findings.yaml`, resolved mechanically and verified:** both
branches are pure appends onto a **byte-identical 299-row base** — checked by
extracting all three merge stages and comparing, not assumed — so the resolution
is SS-01's seven rows then mine. **313 rows**, then **314** once `SS-03-DF-08`
was filed at reconciliation. Nothing dropped, reordered or renumbered;
`disposition.py --ticket SS-03` reports `DISPOSED`.

Everything else auto-merged. My five `baseline.evidence` pointers survived intact
and `SS-01`'s `status: closed` was preserved.

---

## 10. What the independent review broke, and what it confirmed

PR #281 was dispatched to a reviewer instructed to **refute** it. **Verdict:
CHANGES** — ten claims confirmed, **three refuted**, two partial. Every refutation
is repaired above; this section is the record of what was wrong and who found it.

### 10.1 `M1` — the largest finding in this ticket is the reviewer's

**I pointed a goal at a file and verified that the path resolved.** I then wrote
*"verified by resolution, not asserted"*. **Resolution was verified; content was
not.** The file — `baseline_is_a_card-436c78c.txt`, cited by
`GOAL-judged-goals-compliant`'s `baseline.evidence` and by its `baseline.md` as
the source *"every figure below is re-readable from"* — **reports 123 plans, 36
goals and 23 judged**. A clean `436c78c` reports `122 / 31 / 20`.

**No sealed artifact anywhere in the record produced `0 of 20`** until this
amendment measured one. `SS-03-DF-05`. Repaired: a clean run sealed from a
detached worktree with an empty `git status`, the goal repointed at it, the
mislabelled file renamed and headed rather than deleted, `baseline.md`'s false
sentence corrected. **The mechanism is not repaired**: no baseline in this record
carries evidence that its tree matched its commit, and the other four kickoff
baselines have never been checked this way. **`SS-08` must not quote one
unchecked.**

**A path that opens is not a number that reproduces**, and I wrote the stronger
claim from the weaker check.

### 10.2 `M2` and `M3` — I filed `SS-03-DF-02` against myself and then shipped it twice more

`SS-03-DF-06`. In the same commit as the finding about swallowing a parse
failure: `load_index` swallowed everything and returned `{}`; `distinct_goals`
dropped unkeyable goals from plans that parsed perfectly; and `classify`'s
docstring said *"NEVER raises"* while a scalar `baseline:` raised
`AttributeError` out of `main` and **exited 1** — a declared non-gate acting as a
gate on malformed input. All three repaired, each with an executed failing input.

**Filing a finding about a class does not make its author able to see the class.**
That is `consumption_is_changing_what_the_substrate_checks` demonstrated against
the party quoting it, and it is the most useful thing in this ticket.

### 10.3 `M9` — my repair delivers the weaker guarantee, and the code now says so

`SS-00-DF-02` says a collision must not shrink the denominator. **What is
protected is the distinct-goal line**, which cannot fall. **The compliance
denominator is not protected**: `id-collision` counts in neither `judged_total`
nor the command total, so a collision between two judged goals takes
`judged_total` from 17 to 16 while printing `id-collision : 2`. **Visible rather
than silent is the improvement; it is not the absence of movement the finding's
sentence asks for.** Fixing it means deciding whether an ambiguous goal belongs
in a compliance denominator at all — the owner's call, not the instrument's.
Documented in `census`, restated here, not repaired.

### 10.4 `M5` — surfaces I modified outside my own conflict keys

My declared `workflow` conflict keys are
`specs/results/scorecards/stabilize-substrate/GOAL-judged-goals-compliant/` and
`.../SS-03/`. **I modified three surfaces outside them and the first version of
this document disclosed none of them:**

| surface | why | authority |
|---|---|---|
| `tests/test_goal_baseline_is_a_card.py` | the red assigned to me by issue #274 lives here | **the plan lists this file under `SS-06`.** The owner has confirmed this is a plan inconsistency, is handling it as a schedule amendment, and directed me not to change conflict keys myself |
| `specs/desired_program_model/ticket_plan.yaml` | clause (a) is about `baseline.evidence` fields, which live here | listed in my `implementation_scope`; shared with every other ticket |
| `.../SV-03/analysis/baseline_is_a_card.py` | both kickoff defects are in this file | listed in my `implementation_scope`; named as `SS-00-DF-03`'s surface |

**Only `evidence:` pointers and one appended supersession paragraph were changed
in the shared plan.** No other ticket's entry, status, dependency or conflict key
was touched.

### 10.5 What the review confirmed, so it is not re-done

The census figures re-derive exactly, and the reviewer isolated the `24 → 23`
movement independently and got 23 — **the plan edits contribute zero to it**,
which is cleaner than my own evidence showed. All three population figures
re-derive to the card (142 references then, 120 now, 0 missing). The committed
`FAILED` lists are byte-identical to the evidence and `+10` decomposes node for
node as `+12 / −2`. `R-H4` is clean: **zero bytes changed under
`specs/.history`**. `SS-01`'s surfaces are untouched.

The reviewer also named `SS-00-DF-03`'s mechanism more sharply than I did: **the
token that flipped `GOAL-tree-stabilizes` into the judged set is `score_tools`,
added by commit `25600fa` itself, inside a clause about a different finding.**

### 10.6 Where I disagree with the review

**Nowhere on the three refutations** — `M1`, `M2` and `M3` are correct,
reproducible, and repaired.

One qualification, on `M3`'s figure rather than its substance: the reviewer
measured the without-index column as `11/9/2/1`. At the amended tip it is
`8/7/1/1`, because six goals moved to `UNDECIDED` after `M4`. **The reviewer's
number was right for the tree it was measured on**, and the comment it refuted —
*"comparable line for line"* — was wrong on both trees, which is the point.
