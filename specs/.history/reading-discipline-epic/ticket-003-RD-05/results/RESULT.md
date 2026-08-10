# RD-05 — the `effect_boundary` axis, implemented

**RD-04's design, executed. The evidence under it is exactly as wide as it was
when RD-04 wrote it, and nothing here makes it wider.** One axis, two
authoritative values, one demonstrated dimension, one example, one judge tier.

- **Tree:** `/Users/hayde/IdeaProjects/wt-epic-reading-discipline-RD-05`, a
  ticket worktree, branched from `epic/reading-discipline` at `c9237e6`
  (verified against the work order; the LOCAL ref was at `7514df0`, **14 commits
  behind** `origin/epic/reading-discipline`, and was fast-forwarded before
  `wt new` — RD-02 found four, SM-06 found twenty-one. *`git rev-list --count`
  says 14; an earlier draft of this line said eight, from counting the log by
  eye. Corrected against the command rather than left standing.*)
- **Design:** `references/architecture_tags.md`, §§1–12 RD-04's and §13 RD-05's.
- **Evidence:** `analysis/` in this directory — `tags.txt`, `result.json`,
  `compare-*.txt`, `audit.txt`, `scope-own-writing.txt`, all produced by the
  shipped commands.
- **Instruments used:** `scripts/code_complexity.py` (shipped, unchanged) and
  `score_tools.py scope` (RD-01, unchanged). **Nothing new measures anything;
  the derivation reads figures the complexity instrument already prints.**

---

## 1. Every shipped tag value, and its earn-its-place demonstration

**The vocabulary did not grow.** Two values carry refusal authority, two carry
none, and no value was admitted that RD-04 had not already demonstrated.

| value | authority | demonstration |
|---|---|---|
| `effectful` | **D3 only** | within `ab_quota_ledger`, 24 cards, D3 range **1–2**, disjoint from `ports-and-adapters`' 4–4. Re-derived from the cards on every `audit` |
| `ports-and-adapters` | **D3 only** | the same cell, 10 cards, D3 range **4–4** |
| `UNDERIVABLE:<reason>` | **none — always comparable** | not a value. Three reasons ship: `no-effect-surface`, `unparsed`, `unmeasurable`. 4 of 11 declared subjects derive one |
| `UNDEMONSTRATED:<name>` | **none — always comparable** | not a value. Zero instances ship |

**Two values were considered and NOT admitted**, and the reason is the same in
both cases — earn-its-place is a **deletion** rule and cannot admit anything:

- **`pure`** (RD-04 §9.3). `spec_double_compiler/` derives
  `UNDERIVABLE:no-effect-surface` and was scored D3 = 3 by **one** judge. A
  single card cannot establish a range: n = 1 in two of three cells. The named
  experiment is in §9.3 and was not run here.
- **`greenfield`** (RD-04 §9.4). Not architecture, and it fails earn-its-place
  on the record as it stands — `D2 = 2` on 35 of 35 cards of `ab_quota_ledger`,
  31 under the arm-pair framing and 4 under greenfield, so the rationales moved
  and the scores did not. Putting it on the architecture axis would be the first
  suppression key.

**The population's observed range is printed beside every `does not separate`
verdict**, and one of the four is marked `NULL-ENTAILED` (from `analysis/tags.txt`):

```
  does not separate ab_quota_ledger D1 effectful/ports-and-adapters: effectful [2, 4] n=24  ports-and-adapters [3, 4] n=10  population took [2, 3, 4]
  does not separate ab_quota_ledger D2 effectful/ports-and-adapters: effectful [2, 2] n=24  ports-and-adapters [2, 2] n=10  population took [2]  NULL-ENTAILED
  SEPARATES        ab_quota_ledger D3 effectful/ports-and-adapters: effectful [1, 2] n=24  ports-and-adapters [4, 4] n=10  tiers_measured=['opus']
  does not separate ab_quota_ledger D4 effectful/ports-and-adapters: effectful [2, 4] n=24  ports-and-adapters [2, 4] n=10  population took [2, 3, 4]
  does not separate ab_quota_ledger D5 effectful/ports-and-adapters: effectful [2, 4] n=24  ports-and-adapters [3, 4] n=10  population took [2, 3, 4]

1 of 5 (dimension, value-pair) cell(s) grant a refusal.
```

**Three of the four null verdicts are measurements and one is not.** D2 took a
single value across the comparison population, so no separation was possible on
it and that cell reports the example rather than the tag.

**The same-tag control holds on all five dimensions.** `arm_a` and `arm_c` are
two subjects of one example carrying the same derived value; they overlap
everywhere, D3 included. Without the control any two artifacts would pass,
because any two differ in something.

---

## 2. An `INCOMPARABLE` pair prints both scores — the actual output

`python3 examples/validation/scorecards/score_tools.py tags --compare arm_b arm_a`,
verbatim, preserved as `analysis/compare-arm_b-arm_a.txt`:

```
example: ab_quota_ledger
  arm_b [ports-and-adapters]   vs   arm_a [effectful]

D1  arm_b [3, 3, 3, 3, 3, 3, 3, 3, 3, 4]
    arm_a [2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4]
    -> comparable (ports-and-adapters/effectful has demonstrated no separation on D1, so a 'different architecture' objection is not available here)
D2  arm_b [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    arm_a [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    -> comparable (ports-and-adapters/effectful has demonstrated no separation on D2, so a 'different architecture' objection is not available here)
D3  arm_b [4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
    arm_a [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    -> INCOMPARABLE (effect_boundary: ports-and-adapters/effectful, demonstrated on D3, table row `effect_boundary-ab_quota_ledger-D3-effectful-vs-ports-and-adapters`, tiers measured ['opus'])
D4  arm_b [2, 3, 3, 3, 3, 3, 4, 4, 4, 4]
    arm_a [2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4]
    -> comparable (ports-and-adapters/effectful has demonstrated no separation on D4, so a 'different architecture' objection is not available here)
D5  arm_b [3, 3, 3, 3, 3, 3, 4, 4, 4, 4]
    arm_a [2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4]
    -> comparable (ports-and-adapters/effectful has demonstrated no separation on D5, so a 'different architecture' objection is not available here)

incomparable pairs reported: 1     absent: 0     comparable: 4
```

**The INCOMPARABLE row carries 28 numbers — every D3 score on both sides.** It
is the same shape as every other row; the verdict added a word and removed
nothing. `test_an_incomparable_pair_prints_both_score_sets` asserts that against
the cards on disk rather than against a remembered list, so the tag machinery
cannot supply its own expected answer.

---

## 3. Authority is per dimension — a D1 comparison the tag cannot refuse

The D1 row above **is** the proof: two subjects with different derived values,
and the verdict is `comparable` with the reason printed. There is no weighting
and no discount — on D1, D2, D4 and D5 the objection is simply **not available**.

Executed three ways:

- `test_the_tag_cannot_refuse_a_comparison_on_a_dimension_it_did_not_move`,
  parametrised over D1, D2, D4 and D5.
- `test_authority_is_keyed_on_dimension_and_value_pair` — the whole table is
  `[("D3", ["effectful", "ports-and-adapters"])]`. One row.
- `audit` re-derives it every run. A `[[demonstration]]` moved to any other
  dimension is a **VIOLATION**, demonstrated by
  `test_a_demonstration_the_cards_no_longer_support_is_a_violation`.

---

## 4. The invariant's statement, fixed — and no exemption taken

**`GATING_SCAN_EXEMPT` is unchanged at three entries.** RD-05 is not on it, and
`architecture_tags.py` is scanned repository-wide like any other file.

What changed is the **statement**.
`test_no_reader_of_this_instrument_gates_on_its_output` said a file "is not
allowed to branch on them, compare them, assert on them or exit on them". It now
forbids `refusing_uses` — a figure reaching a `raise`, an `assert`, an `exit`, or
a branch whose arm does one of those — and reports the rest as `observing_uses`.
The distinction is `CD-01`'s and it is written into the docstring: **choosing a
boundary is forbidden; observing where one already is is the thermometer's job.**

`architecture_tags.py` stays green because of a property it has, not a line in a
list, and `test_the_derivation_observes_and_never_refuses` pins the property
three ways: the file must read the instrument, the scan must reach it, and its
refusal list must be empty.

**The result, measured in the archive tree:** the one failure RD-04 added at
escalation, `test_no_reader_of_this_instrument_gates_on_its_output`, is
**green**, and RD-04's own `analysis/derive_and_test.py` no longer trips it.
Zero refusals repository-wide outside the gitignored per-checkout homes.

### 4.1 And the scan was firing on the wrong line — `RD-05-DF-01`

The taint analysis **does not cross a function boundary**. RD-04's script was
flagged at `if out.returncode != 0` — a branch on a *subprocess exit status* —
and the three clause comparisons inside `derive(record)` that the whole §9.9
escalation is about **were never seen**, because `record` arrives as a parameter.
The escalated finding was true and the test reporting it was reporting something
else.

The taint set is also **name-keyed rather than scope-aware**: a local `args` in
`measure()` taints every `args` in the file, so `architecture_tags.py` reports
**53 observing uses and 0 refusals**, and a substantial share of the 53 is that
collision rather than a figure. Both directions at once. **An empty refusal list
is not evidence that no figure decides anything**, and the repair inherits the
blind spot unchanged rather than papering over it.

### 4.2 A second invariant, which the ruling does not cover — FOR OWNER REVIEW

**The archive comparison found this; no test RD-05 wrote caught it**, which is
the third time running that the like-for-like archive run is where the real
failure lives (RD-02 and RD-04 each reported the same).

`tests/test_produced_code_prompt.py` carries two assertions that **zero** Python
files under `examples/` and `prompts/` may refer to the instrument *at all*.
`architecture_tags.py` lives under `examples/validation/scorecards/` beside
`score_tools.py`, so both went red.

Three ways out were available and two were rejected:

- **Move it to `scripts/`** — rejected. `scripts/**` is in `EXECUTABLE_SURFACES`,
  so it would fail `test_nothing_executable_reads_this_instrument`, an older and
  stronger invariant, and it is not program surface anyway.
- **Read a previously written complexity JSON instead** — rejected, hard. That
  is the exact route `test_the_blind_spot_is_real` demonstrates the scan cannot
  see. Routing around a tripwire is the six-lines-of-YAML defeat this repository
  documents.
- **Restate the assertion as what it protects.** "Zero references at all" was a
  **proxy** for "nothing branches on it", written while nothing needed to refer
  to the instrument. The real property is now checkable, so the proxy was
  replaced by the thing it stood for: anything under those trees may read the
  figures; **nothing may refuse on them**. Every other file is still reported;
  the derivation is admitted only while `refusing_uses` is empty, and deleting it
  turns the test red on a missing file rather than green on a vacuous scan.

**§6b names the gating invariant and not this one.** Extending its reasoning here
is RD-05's reading and is flagged for the owner rather than presented as covered.

---

## 4.3 The card did not change, and that is measured rather than assumed

R-H1's text grew a third clause in `references/eval_scorecard.md`. **The standing
rule is that changing the card needs a `scorecard_version` bump, the old anchors
kept, and a re-score under both versions** — so whether the card changed is a
question with a computable answer, and it was computed rather than argued.

| digest | before (`c9237e6`) | after |
|---|---|---|
| `served_digest` v3 | `sha256:694280073db988fe` | **identical** |
| `served_digest` v2 | `sha256:fba145a46e7a7de2` | **identical** |
| `served_digest` v1 | `sha256:ea225ec882de02e4` | **identical** |
| `anchors_digest` | `sha256:eeccf4576bc6fd85` | **identical** |

`served_rubric` renders from the parsed structure — dimensions, anchors, caveats,
scoring rules — and `## Reading history` is outside it by construction, which is
the property SM-04 added `served_digest` to make checkable. **No judge is served
a different byte, no anchor moved, and no version bump is due.** The edit shows
up only as `PROSE-DRIFT`, which is a prompt to go and look and never a violation.

No new `R-H` id was created either: R-H1 absorbed the clause, so it inherits a
check that already runs. `audit` fails if the rubric declares an `R-H` with
nothing executing it, and it reports `0 violation(s)`.

---

## 5. What RD-05 settled, and how — and what stays open

### Settled

| question | how |
|---|---|
| **§9.9** thermostat | **By the owner's ruling, not by RD-05.** The invariant's statement was fixed; no exemption taken. §4 above |
| **§7.3** null-entailment | Shipped as a column, not a note. Every non-separating cell prints its population range; a single-point range prints `NULL-ENTAILED` |
| **§9.8** `scope` and subject scope | Settled the **second** way §9.8 permits: an unresolvable subject scope is **not** resolved to the example. `subjects.toml` puts the subject upstream of the checker; `RD-04-DF-01` stays open because the checker itself is unchanged |
| **§9.7** composite subjects, *partly* | The re-attribution half only: `SCOPE-DRIFT` names 2 of `toolchain_removal`'s 4 cards **beside** them, never editing them (R-H4). Whether one round may emit several scoped cards, and how `contested` groups them, is **untouched** |

### Left open — deliberately, and two of them must stay open

**§9.1 — the separation is `opus`-only, n = 0 in `sonnet`.** This is the axis's
binding limit and RD-05 did not narrow it by a single card. The demonstration row
carries `tiers_measured = ["opus"]`, `audit` re-derives that field, and declaring
`["opus", "sonnet"]` is a VIOLATION until two `sonnet` judges score
`blind/artifact_T`. `test_the_one_row_carries_its_tier_limit` asserts it.
**Nothing RD-05 built makes that evidence wider.**

**The thermostat scope — ruled, but the ruling's limit stands.** §6b's own third
condition says a ruling that a mechanism is sound does not make the evidence
under it wider than it is. §4.2 above is the first thing that ruling did not
reach, found within one ticket.

Also open and untouched: **§9.2** the `0.5` threshold (now a printed constant,
still never measured near its boundary), **§9.3** `pure` at one data point,
**§9.4** `greenfield`, **§9.5** non-Python subjects, **§9.6** the author
confound, **§9.10** `arm_a` D3 = 2 against `arm_c` D3 = 1.

---

## 6. Suite — four runs, each naming its tree

**Only the archive pair is like-for-like** (RD-02's method, `RD-01-DF-02`'s
reason: `wt new` creates gitignored per-checkout homes holding full copies of the
card, the instrument and the sealed scorecards, and two tripwires walk them).
Archives built with `git archive <sha> | tar -x -C <clean dir>`.

| tree | commit | result |
|---|---|---|
| archive, **no homes** — the parent | `c9237e6` | **11 failed, 1419 passed, 9 skipped** |
| archive, **no homes** — RD-05 first tip | `4ec3028` | **12 failed, 1449 passed, 9 skipped** |
| archive, **no homes** — RD-05 second tip | `5ccda71` | **10 failed, 1455 passed, 9 skipped** |
| archive, **no homes** — RD-05 final tip | `67e3085` | **10 failed, 1457 passed, 9 skipped** |
| ticket worktree | `67e3085` | **2 failed, 1474 passed** |

### 6.1 The like-for-like diff, member by member

**Parent → first tip (`4ec3028`): one failure removed, two added.**

- **Removed:** `test_code_complexity.py::test_no_reader_of_this_instrument_gates_on_its_output`
  — RD-04's escalated failure, green under the corrected statement.
- **Added:** `test_produced_code_prompt.py::test_nothing_executable_consumes_the_instrument_after_the_prompt_landed`
  and `::test_the_prompt_mentions_it_only_as_prose` — §4.2, a real regression in
  a second invariant, which **no test RD-05 wrote caught**. It is reported here
  rather than quietly re-measured away: the first tip was worse than the parent
  and the archive run is the only thing that said so.

**Parent → final tip (`67e3085`): exactly one member removed, nothing added.**

```
< FAILED tests/test_code_complexity.py::test_no_reader_of_this_instrument_gates_on_its_output
```

That is the whole diff. The denominator moved too, so it is accounted for by
`pytest --collect-only` on both archives rather than asserted: **1439 → 1476
collected, +37**, and every one is named —

| where | count |
|---|---|
| `tests/test_architecture_tags.py`, new | **+32** |
| `test_code_complexity.py::test_the_derivation_observes_and_never_refuses`, new | +1 |
| `test_spec_yaml_valid.py::test_spec_yaml_parses`, parametrised over the specs tree | **+4** — the four YAML files `start_ticket.py RD-05` scaffolded, not tests RD-05 wrote |
| `test_produced_code_prompt.py`, renamed | 0 |

So of the 38 extra passes, 33 are tests this ticket wrote and 4 are the ticket
workflow's own scaffold being validated; the last is the failure that stopped
failing. **The numerator fell by one and the denominator rose by 37**, and
saying which is the `denominator_rule`.

### 6.2 The worktree number, and why it is not the comparison

**Both of its two failures are `RD-01-DF-02`'s class, and neither reproduces in
the archive tree at the same commit.**

- `test_no_reader_of_this_instrument_gates_on_its_output` fails with **88
  refusing uses, every one under `.skill-manager/`** — the gitignored
  per-checkout home `wt new` creates, holding a full copy of the instrument and
  its tests. RD-04 saw 248 items across four homes; this worktree has one home
  and 88. In the archive tree the same test is **green**, which is RD-05's
  headline result.
- `test_card_has_one_home::test_only_the_card_states_a_dimension_an_anchor_or_a_scoring_rule`
  reports exactly one offender, `tests/test_score_tools.py:540` — and the file it
  read is
  `.skill-manager/skills/spec-double-compiler/tests/test_score_tools.py`.
  **Zero RD-05 files are flagged by it**, checked directly rather than inferred:
  `architecture_tags.py` restates no anchor, no dimension and no scoring rule,
  which is the discipline RD-04 had to apply to two of its own files.

**So the worktree figure is not comparable to either archive figure.** It is
reported rather than dropped, and it is also the third independent reproduction
of a false-positive class that has been misread as a green for several rounds.

**The parent is not green in any tree.** Eleven failures at `c9237e6` with no
homes — RD-02's and RD-04's finding, reproduced independently a third time.
Eight of the eleven are `test_score_tools.py` and `test_prediction_seal.py`
failing because **an archive tree has no `.git`**, so every commit an era
boundary names fails to resolve; they are a property of the measurement method,
not of the tree, and they are identical on both sides of the comparison.

---

## 7. R3 applied to RD-05's own writing

`score_tools.py scope --path references/architecture_tags.md --path references/eval_scorecard.md`,
preserved as `analysis/scope-own-writing.txt`:

```
5 counted figure(s): 1 REFUTED, 0 COUNT-MOVED, 3 HOLDS, 1 UNREACHABLE
```

**Every one of the five pre-dates RD-05.** The REFUTED is
`references/eval_scorecard.md`'s historical *"D2 = 2 on 27 of 27 cards"*, present
at `c9237e6` and unmoved; the 3 HOLDS and the 1 UNREACHABLE are RD-04's, the
UNREACHABLE being the demonstrated failing input RD-04 left in place on purpose.
**RD-05 adds zero counted figures to either file** — the parent's
`eval_scorecard.md` reports `1 counted figure(s): 1 REFUTED` and so does the tip.

### 7.1 And `scope` refutes this document, for quoting the figure it is reporting

Run over this file, `scope` reports **3 counted figures: 1 REFUTED, 2 HOLDS**
(`analysis/scope-result-md.txt`).

- Both HOLDS are the same figure of RD-05's own — *"`D2 = 2` on 35 of 35 cards
  of `ab_quota_ledger`"*, in §1 and again in this bullet — deliberately phrased
  at example scope so the checker can resolve it.
- **The REFUTED is §7's own sentence naming the historical claim**, *"D2 = 2 on
  27 of 27 cards"*, written there in order to say that it is the pre-existing
  false one. `scope` refutes the mention, at population 49, and names eight
  counterexamples.

**The checker cannot tell a claim from a mention of a claim.** RD-01 already
counted nine refuted figures that were *quotations carrying a claim forward*;
this is the same mechanism with the sign flipped — a quotation carrying a claim
forward **in order to report it as false** is refuted identically. A third bound
beside `RD-02-DF-01`'s dimension token and `RD-04-DF-01`'s qualifier window.

**The sentence is left exactly as written.** Rephrasing it to dodge the checker
would be editing a target to match a result, and the count is more honest with
the refutation in it: `GOAL-scope-loss-catchable`'s headline is a count of
REFUTED verdicts, and this is one that names no false belief anywhere.

**Which bound applies to everything else RD-05 wrote:** `RD-02-DF-01`. `scope` is
keyed on a `\bD[1-5]\b` token, so every figure in this document that names its
subject in words — *"7 of 11 subjects decided"*, *"2 of 4 cards cite outside
their scope"*, *"1 of 5 cells grants a refusal"*, *"53 observing uses and 0
refusals"* — **is not counted at all.** Not refused, not `UNREACHABLE`, invisible.
`RD-04-DF-01`'s bound does not bite here because RD-05 wrote no
qualifier-after-the-count figure; it would if this document tried to state its
own headline in the shape the design most wants, which is why RD-04 left that
figure in place as a demonstration rather than fixing the sentence.

---

## 8. What RD-05 rejected

RD-04's twelve rejections stand. RD-05 adds seven, and **every one of the first
four would have widened the tag's authority**:

1. **Granting authority on any dimension other than D3.** D1, D2, D4 and D5
   overlap over 34 cards. The table is keyed on the dimension precisely so this
   cannot happen by accident, and `audit` re-derives it so it cannot happen by
   drift.
2. **Letting `UNDERIVABLE` refuse anything.** Four of eleven subjects derive one.
   Making a refusal to derive worth something is attack A2 and it is the cheapest
   attack in the set — an author who cannot move a figure can always break the
   measurement.
3. **Admitting `pure` on `spec_double_compiler/`'s within-example signal.** It is
   real, it is n = 1 in two of three cells, and one card cannot establish a
   range. Earn-its-place is a deletion rule and admitting on it is the misuse RD-04
   named.
4. **Admitting `greenfield` because the ceiling argument is good.** It is a good
   argument. RD-04 §7.2 says the rationale-based admission route is the door A1
   walks through, and a value admitted on prose is a value that can be argued onto
   any comparison.
5. **Adding `GATING_SCAN_EXEMPT` an entry, or moving the derivation somewhere the
   scan does not reach.** §4 and §4.2. Both were available; both hide a rule that
   is correct.
6. **Reading a previously written complexity JSON to stay invisible to the scan.**
   §4.2. It is the demonstrated blind spot, and using it deliberately would be
   defeating a tripwire rather than satisfying it.
7. **Caching the derivation to keep `audit` fast.** `RD-05-DF-05`. Re-derivation
   is the whole anti-staleness property; a cache is the staleness the clause
   exists to prevent, at 1.1 s.

---

## 9. Findings filed — five, none fixed inline

| id | what |
|---|---|
| `RD-05-DF-01` | The gating scan does not cross a function boundary and its taint set is name-keyed, so it missed the clauses §9.9 escalated and flags comparisons that touch no figure. An empty refusal list is not coverage. |
| `RD-05-DF-02` | The one place a declaration can still move a refusal: the label→subject mapping decides which cards enter the comparison, and nothing derives it. 1 of 49 cards maps to no subject and nothing checks that. |
| `RD-05-DF-03` | RD-04's design page disagrees with its own machine record in one cell (`ex6_jenga` state co-location). Corrected beside the table, not in it. |
| `RD-05-DF-04` | `SCOPE-DRIFT` attributes by a scope's last path segment, so two scopes sharing a basename would collide. Reproduces RD-04 §1.5 exactly; a prefix match found only one of the two real drifts. |
| `RD-05-DF-05` | The table re-derives on every `audit` at ~1.1 s, and in a tree where the declared scopes are absent the clause reports UNVERIFIED and checks nothing — so a green audit there says nothing about the table. |

---

## 10. What this is worth, stated low

**One axis, one dimension, one example, one judge tier, one demonstration row.**
The axis explains the only contested group in 49 sealed cards and it explains
nothing else: not the D2 greenfield class, not `arm_a` D3 = 2 against `arm_c`
D3 = 1, not three of the five `architectural-coherence` fixtures, which touch no
outside world and stay comparable to everything.

**The thing most likely to be wrong is the predicate, not the principle** — the
risk §6b names by name. RD-05 kept it checkable against the artifact
(`analysis/result.json` re-derives in about a second, and
`test_the_derivation_reproduces_rd04s_sealed_machine_record` compares it to
RD-04's sealed record rather than to the page that argues for it), and
`RD-05-DF-01` says plainly that the tripwire which was supposed to notice a
misfiring predicate cannot see one.
