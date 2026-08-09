# RD-06 — the subjects, and everything measured about them

**RD-06 produces subjects. It scores none of them.** No D-number is assigned in
this directory, no artifact is ranked, and no comparison between subjects is
drawn. `tests/test_rd06_subjects.py::test_rd06_scored_nothing` is the executable
form of that claim, and it ships with a demonstrated failing input.

The design was sealed before anything was dispatched:
[`SEALED-BEFORE-DISPATCH.md`](SEALED-BEFORE-DISPATCH.md), committed at
`700936e` with no artifact on disk and no figure known. Read it first. Nothing
in it has been edited since.

---

## 1. The six subjects

Six trees, one example (`ab_quota_ledger`), all six against the **same sealed
`FEATURE.md`** and the **same shared behavioural suite** as the record.

| label | what it is | before | prompt as dispatched |
|---|---|---|---|
| `Z` | greenfield | — | [`artifact_Z.dispatched.md`](../../../../../examples/validation/ab/dispatch/reading-discipline/artifact_Z.dispatched.md) |
| `E` | greenfield | — | [`artifact_E.dispatched.md`](../../../../../examples/validation/ab/dispatch/reading-discipline/artifact_E.dispatched.md) |
| `N` | greenfield | — | [`artifact_N.dispatched.md`](../../../../../examples/validation/ab/dispatch/reading-discipline/artifact_N.dispatched.md) |
| `M` | **a revision of `Z`** | `Z` | [`artifact_M.dispatched.md`](../../../../../examples/validation/ab/dispatch/reading-discipline/artifact_M.dispatched.md) |
| `F` | **a revision of `E`** | `E` | [`artifact_F.dispatched.md`](../../../../../examples/validation/ab/dispatch/reading-discipline/artifact_F.dispatched.md) |
| `D` | **a revision of `N`** | `N` | [`artifact_D.dispatched.md`](../../../../../examples/validation/ab/dispatch/reading-discipline/artifact_D.dispatched.md) |

The trees are `../../blind/artifact_<label>/`. Labels are **opaque**: which arm
prompt produced which greenfield tree is in `UNBLINDING-rd06.md`, which no judge
is given. **The pairing above is published on purpose** — D2 anchor 3 cannot be
awarded by a judge who has not been told which tree is the before — and it
reveals nothing about the arms, because *every* greenfield tree was revised. A
subset would have made the unrevised arm identifiable by subtraction; that is
why the sealed design revised all three.

## 2. What makes these comparable to the sealed record, and what does not

**Held identical** to `hexagonal-prompting`, `hexagonal-prompting-rerun` and
`ports-as-adapters`: the sealed `FEATURE.md`; the shared behavioural suite
`examples/validation/ab/tests/test_behavior.py`, unchanged and un-editable by
any arm; the three arm prompt **sources**, unchanged; the seeded catalogue; the
example name.

**Not identical, stated rather than buried:**

- **The producing model is a different one** from the model that wrote the
  sealed arms. Every cross-round comparison of these subjects is confounded by
  it, and nothing here separates prompt from model. `R-H1`'s "unchanged
  instrument" clause is about the *card*; this is a fourth axis and RD-06 cannot
  close it.
- **The dispatch envelope differs from the sealed rounds'** — see §5.
- `N` and `D` carry a `mutation_check.py` their arm chose to ship, which the
  complexity instrument counts as a `code` module. Their figures in §4 include
  it. That is a property of the tree, not an error, and it is why `N`'s
  `code_lines` is not comparable line-for-line with `Z`'s.

## 3. The behavioural contract, per tree, with the tree named

`examples/validation/ab/tests/test_behavior.py`, run unchanged against each
tree, module found by importing rather than by believing the artifact's notes.
Machine record: [`suite-rd06.json`](suite-rd06.json).

| tree | module | shared contract |
|---|---|---|
| `artifact_Z` | `quota_ledger` | **28 passed** |
| `artifact_E` | `quota_ledger` | **28 passed** |
| `artifact_N` | `quota_ledger` | **28 passed** |
| `artifact_M` | `quota_ledger` | **28 passed** |
| `artifact_F` | `quota_ledger` | **28 passed** |
| `artifact_D` | `quota_ledger` | **28 passed** |

All six green, **both halves of every pair**. `FEATURE.md` calls passing this
suite *"a floor, not a result"*, and that is how it is recorded here.

## 4. The before/after — the shape the product side has never had

D2 anchor 3: *"a simplification was made and its effect measured — the before
and after figures are both recorded."* **No greenfield artifact can reach it.**
Three pairs now exist and both figures are on disk for each, one JSON record per
tree, produced by `scripts/code_complexity.py --json`.

**Two tables, never a delta.** `MF-020` — a figure falling is not evidence the
design improved — and `code_complexity.py` ships no comparison mode for exactly
that reason. The figures below are transcribed from the records; **no
subtraction is performed here and none may be read as a result.**

`totals_code_only` — modules the instrument classifies `role = code`:

| tree | code_lines | callables | classes | branch_points | instance_state | effectful_calls | declared_interfaces | public_surface | max_depth |
|---|---|---|---|---|---|---|---|---|---|
| `Z` **(before)** | 158 | 14 | 5 | 11 | 4 | 6 | 0 | 15 | 1 |
| `M` **(after)** | 156 | 14 | 5 | 11 | 4 | 6 | 0 | 15 | 1 |
| `E` **(before)** | 163 | 24 | 8 | 12 | 6 | 3 | 1 | 24 | 1 |
| `F` **(after)** | 163 | 24 | 8 | 12 | 6 | 3 | 1 | 24 | 1 |
| `N` **(before)** | 283 | 19 | 3 | 26 | 7 | 25 | 0 | 25 | 4 |
| `D` **(after)** | 280 | 19 | 3 | 27 | 6 | 25 | 0 | 25 | 4 |

Records: `complexity-artifact_<label>.json`. Every one has
`completeness.parsed_fraction = 1.0`.

**What each revision did, in its own words, is in the artifact's own
`REVISION-NOTES.md`** — which is the artifact's account and not this file's.
`score artifacts, never claims`: the notes say what the author says was done,
and the two trees say what was done.

**One of the three revisions changed no code at all.** `artifact_F` differs from
`artifact_E` by exactly one added file, `REVISION-NOTES.md`; not a line of
implementation or test was edited, added, deleted or renamed. Its author records
that it worked through every candidate and found each one to be carrying a
distinction. **That outcome is the fixture working, not the fixture failing.**
`revision/README.md` states the requirement in advance: *"a prompt that cannot
come back empty-handed is a prompt that will always report a simplification."*
It is recorded here as a result and nothing was re-dispatched to replace it —
the seal forbids that in as many words.

**And one figure the instrument does not move.** `Z` → `M`'s author records
removing two fields from a record type; `instance_state` reads 4 on both trees.
Recorded, not reconciled. The mechanical block exists so that a disagreement
between measurement and judgement is visible as a finding rather than resolved
by arithmetic, and this is one to look at rather than one to explain away here.

## 5. What was dispatched, and what the envelope cost

Every one of the six prompts is preserved with `provenance = "preserved"` and
verifies:
`python3 examples/validation/ab/dispatch_record.py verify --dir examples/validation/ab/dispatch/reading-discipline`
→ **6 rows, all unchanged, no RED.**

Each dispatch is **+5 / −0 distinct lines** against its source, and the added
envelope is **byte-identical across the arms except for the opaque label in the
working directory** — asserted by
`tests/test_rd06_subjects.py::test_the_greenfield_envelope_is_identical_across_the_three_arms`,
which also checks the envelope for the words `reading-discipline`, `hexagonal`,
`ports`, `adapter` and `complexity`. The repository root reached each agent
through a **neutral symlink**, so no path in any prompt names the epic.
`PA-06-DF-10`: the previous round's envelope carried the epic's own name into
the arm whose entire job was architectural silence.

Prompt figures measured **on the bytes that were sent**, under the opaque labels
([`prompts-rd06.json`](prompts-rd06.json)):

| | distinct lines | unique vs `Z` | unique vs `E` | unique vs `N` |
|---|---|---|---|---|
| `Z` | 59 | — | 18 | 19 |
| `E` | 148 | 107 | — | 91 |
| `N` | 151 | 111 | 94 | — |

Architectural-vocabulary probe over unique content: `E` **45 of 107** against
`Z`; `N` **1 of 111** against `Z`. **That single hit is the envelope**, not the
arm: it is the run-hint line `QUOTA_LEDGER_IMPL=<the module name you chose>`,
which is present in all three prompts and counts as unique only because the
working-directory label differs. It is reported rather than netted out.

These were measured by RD-06's own analysis and **not** by
`check_catalogue.py --arms --dispatch-dir`, which cannot reach a dispatch record
keyed on opaque labels and silently falls back to the prompt sources on disk —
filed as **`RD-06-DF-01`**.

## 6. The `effect_boundary` tag — RD-05's derivation USED

Declared in `subjects.toml` **before any tree existed** (commit `700936e`);
derived afterwards by `examples/validation/scorecards/architecture_tags.py` over
the trees. Machine record: [`tags-rd06.json`](tags-rd06.json).

| tree | **derived** | declared | agreement | `state_colocation` | clause a / b / c |
|---|---|---|---|---|---|
| `Z` | `effectful` | `effectful` | agree | 1.0 | ✗ / ✗ / ✗ |
| `E` | `ports-and-adapters` | `ports-and-adapters` | agree | 0.167 | ✓ / ✓ / ✓ |
| `N` | `effectful` | `effectful` | agree | 1.0 | ✗ / ✗ / ✗ |
| `M` | `effectful` | `effectful` | agree | 1.0 | ✗ / ✗ / ✗ |
| `F` | `ports-and-adapters` | `ports-and-adapters` | agree | 0.167 | ✓ / ✓ / ✓ |
| `D` | `effectful` | `effectful` | agree | 1.0 | ✗ / ✗ / ✗ |

**Zero `UNDERIVABLE`. Zero `TAG-DISPUTED`.** Every subject parsed completely and
every derivation agreed with the prior taken from the record. This is the tag's
first use outside the cards it was derived from.

**Read that as a null result, not a vindication.** The axis's binding limit is
unchanged: `RD-04 §9.2`, the `state_colocation` threshold of `0.5` is a printed
constant that **has never been measured near its boundary**, and none of these
six subjects lands anywhere near it — the observed values are `0.167` and
`1.000`, the same chasm the sealed record shows. Six more subjects on the far
sides of an unmeasured threshold do not measure it. `RD-04-DF-04` stays open and
these subjects do not touch it.

## 7. Disclosures

Every producing agent was asked to disclose anything it opened. What they
volunteered:

- Three of the six ran a directory listing of `examples/validation/ab/` or of
  the repository root while orienting, and each disclosed it. None reports
  reading any file on its do-not-open list.
- **One subject's own `NOTES.md` carries a disclosure that partially identifies
  the arm that produced it, and its revision inherits the same file.** The
  specifics are in `UNBLINDING-rd06.md` and the finding is **`RD-06-DF-03`**,
  filed as **blocking and escalated**. RD-06 has not decided what to do about
  it, because every remedy binds RD-03: withholding a `NOTES.md` from judges,
  scoring the pair unblinded and saying so, or accepting a partially unblinded
  pair are all scoring decisions.
- **No artifact was edited.** A disclosed leak is recorded, never used as
  grounds to discard or amend — this project's own rule is that a subject is not
  discarded after its content has been seen.

## 7a. `scope` over RD-06's own writing, and which bound applies

```
score_tools.py scope --path <every file this ticket wrote>
  -> 0 counted figure(s): 0 REFUTED, 0 COUNT-MOVED, 0 HOLDS, 0 UNREACHABLE
```

**A zero here is not a clean bill of health, and reporting it as one would be
this epic's own defect.** The bound that applies is the first of the two known
ones: the checker counts a figure only in the form *`D<n>` + a binder + a value
+ a counted noun*. Every claim RD-06 writes about a dimension — *"D2 anchor 3
requires a simplification"*, *"D2 has read 2 on every greenfield card ever
written"* — is phrased outside that form, so the instrument **cannot reach any
of it** and does not even count it `UNREACHABLE`. It is invisible to the sweep
rather than passed by it.

The second bound, `REFUTED` for a true figure whose qualifier falls outside a
≤3-word window, applies to nothing here, because nothing here is of the counted
form at all.

The same run over `specs/desired_program_model/deferred_findings.yaml` reports
12 counted figures (5 REFUTED, 2 COUNT-MOVED, 4 HOLDS, 1 UNREACHABLE). **None of
them is RD-06's**: they are in entries filed at lines 6384–6694 by earlier
tickets. RD-06's three appended findings contribute zero counted figures, for
the same reason.

## 8. What RD-06 REJECTED

Sealed in advance (`SEALED-BEFORE-DISPATCH.md` §6) so it could not be assembled
afterwards to look thorough, plus what came up during the round:

- **Using a sealed tree (`blind/artifact_T`, `_U`, `_W`) as the "before".**
  Cheaper, and the before would already carry judged cards. Rejected: the two
  halves would have different provenance — another epic's dispatch, another
  model, another envelope — and a pair whose halves were produced under
  different conditions is not a controlled pair. It is the sideways move the
  `ports-as-adapters` packet made when it read a before/after across three arms.
- **Writing the revision prompt to ask for a specific simplification.** Would
  have raised the chance anchor 3 is reachable on all three pairs. Rejected: the
  before/after would then measure the ask, not the code. One pair coming back
  with no change is the evidence that it did not.
- **Producing only the treatment arm.** The cheapest route to a flattering
  comparison.
- **Revising only a subset of the arms**, or choosing which to revise after
  seeing the trees. Rejected as selection on the outcome, and it would have
  unblinded an arm by subtraction.
- **Re-dispatching the revision that changed nothing.** Refused: the seal says
  no further revision would be dispatched to obtain a better before/after, and
  a round that re-runs an arm until it likes the answer has measured nothing.
- **Recording the dispatch rows under the arm names** so that
  `check_catalogue.py --arms --dispatch-dir` could read them. Rejected: the
  dispatched bytes carry the opaque label, so an `arm_a`-keyed row would publish
  the mapping and unblind the round. Filed as `RD-06-DF-01` instead.
- **Repairing `subjects.toml`'s "ELEVEN SCOPES" note** and the five figures in
  `references/architecture_tags.md` that RD-06's own six subjects made stale.
  Rejected: rewriting a predecessor's figure so it matches a successor's file is
  how a number stops carrying the scope it was true at. Filed as `RD-06-DF-02`.

## 9. Reproducing everything above

```bash
# every figure in this file, rewritten from the trees on disk (~1 min)
uv run --python 3.13 python \
  specs/results/scorecards/reading-discipline/GOAL-product-round/RD-06/analysis/measure_subjects.py

# the dispatched bytes are still the dispatched bytes
python3 examples/validation/ab/dispatch_record.py verify \
  --dir examples/validation/ab/dispatch/reading-discipline

# the properties that decide whether the handover is honest
uv run --with pytest --with pyyaml python -m pytest tests/test_rd06_subjects.py -q
```
