# SM-06 — one home for the card, and the copies nothing was watching

**Ticket:** [#173](https://github.com/haydenrear/tla-spec-dev/issues/173) ·
**epic:** `subtract-to-measure` · **parent:** `6aac1ec` (SM-04 merged) ·
**a REMOVAL ticket.**

`references/eval_scorecard.md` is now the one home for the card — dimensions,
anchors, scoring rules, judging protocol, reading rules — and nothing else
states any of them.

---

## 1. The gap mutant, run FIRST

`removal_is_a_delta_rule` asks for a mutant seeded in the gap a removal opens.
The gap a de-duplication opens is **not** "does it still work": nothing executed
the copies. It is

> **if a copy disagreed with the card, would anything go red?**

SM-01 did not seed for this one, so SM-06 seeded it — four copies made to
disagree, at `6aac1ec`, **before a single line was deleted**.

| | the copy | made to say | verdict |
|---|---|---|---|
| **M1** | a charter's dimension table | two keys carrying each other's titles | **UNCAUGHT** |
| **M2** | a scoring rule in a judge's evidence packet | its exact inversion | **UNCAUGHT** |
| **M3** | the same rule in every scaffolded `scorecard.md` | its exact inversion | **UNCAUGHT** |
| **M4** | an anchor inside a **sealed** `scorecard.md` — the **control** | an anchor that is not the card's | CAUGHT |

Every surface was asked, not just the suite:

| surface | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| `pytest tests -q` (1378 nodes) | 0 | 0 | 0 | **1**, 3 new failures |
| `score_tools.py check` | 0 | 0 | 0 | **0** |
| `score_tools.py audit` | 0 | 0 | 0 | **1** |
| `score_tools.py serve` | 0 | 0 | 0 | 0 |
| `demonstrate.py` | 0 | 0 | 0 | **1** |

**Three of four disagreeing copies were invisible to every instrument this
repository ships.** The one that was caught was the one something already
compared to the card. That is the whole finding, and it is the reason the copies
were dangerous rather than merely redundant.

**R2 is satisfied.** M4 is the control and it went red on three surfaces, so the
green on M1–M3 is a fact about the copies and not about a dead harness. A run
where all four were green would have measured nothing.

**And the control caught it for a reason nobody would have predicted.** `check`
was expected to catch M4 via `rubric.digest`. `check` returned **exit 0**. What
went red was `audit` — R-H4's seal digest. `rubric.digest` is recorded at
scaffold time and compared to the rubric; it never reads the anchors reproduced
*inside* a card, so it cannot see one edited afterwards. Filed as `SM-06-DF-03`.

Raw: `dup-mutants-before.json`. Re-run: `run_dup_mutants.py --before` (~50 min).

## 2. Re-run after the removal

Same script, `--after`, at `f26ec40`. The copies M1–M3 mutated are gone, so the
after-mutant is **reintroduction**: put a disagreeing copy back and require a
red. A removal that only deletes leaves the next author free to write it again.

| | the copy, put back | verdict |
|---|---|---|
| **A1** | `README.md`'s dimension table, keys carrying each other's titles | **CAUGHT** — suite + `demonstrate.py` |
| **A2** | a scoring rule reintroduced into `PORTS-AS-ADAPTERS-EPIC.md` as "optional" | **CAUGHT** — suite + `demonstrate.py` |

Both fail on exactly one node,
`tests/test_card_has_one_home.py::test_only_the_card_states_a_dimension_an_anchor_or_a_scoring_rule`.
Baseline at `f26ec40` is green on all five surfaces.

Raw: `dup-mutants-after.json`.

## 3. The count, before and after

Statements of a **dimension**, an **anchor** or a **scoring rule**, found with
needles parsed out of the card at run time. Only the card itself and
`specs/.history/` are excluded, so the two columns are the same surface.

| file | before | after | what happened |
|---|---|---|---|
| `PORTS-AS-ADAPTERS-EPIC.md` | 6 | **0** | §2, §6, §7 → pointers to the card and `SELF-IMPROVEMENT.md` |
| `README.md` | 7 | **0** | the summary of the card deleted, not corrected |
| `.../ports-as-adapters/measure/build_evidence_packets.py` | 4 | **0** | SM-04's named target: the packet a judge is handed |
| `PORTS-AS-ADAPTERS-STARTER-PROMPT.md` | 1 | **0** | → pointer |
| `references/hexagonal_prompting.md` | 1 | **0** | quoted anchor → "D3's anchor 3, in the card" |
| `examples/validation/scorecards/score_tools.py` | 6 | 5 | `_skeleton_md`'s copy deleted; 5 remain **guarded** |
| `tests/test_score_tools.py` | 1 | 1 | **guarded** |
| `examples/validation/PREDICTIONS-HP.md` | 4 | 4 | **record** — sealed pre-dispatch |
| `examples/validation/PREDICTIONS-PA.md` | 5 | 5 | **record** — sealed pre-dispatch |
| `specs/desired_program_model/deferred_findings.yaml` | 3 | 3 | **record** — findings quote their subject |
| **total** | **38 in 10 files** | **18 in 5 files** | |

**Live statements that nothing compares to the card: 20 → 0.**

### `denominator_rule`

**The numerator fell.** 20 statements were deleted and none added. The
denominator did not move: the scanned surface is identical on both sides (3,442
tracked files, same suffix set, same two exclusions), and **nothing was
reclassified out of scope to make the number fall** — the guarded and record
classes contribute the same 18 statements before and after, so `38 − 18 = 20`
and `29 − 9 = 20` agree across two different scopings. The fall is entirely
deletion.

**What did NOT fall, and is not claimed as a win:** the record class (12) is
untouched by construction, and the guarded class went 7 → 6 only because one
genuine copy left `score_tools.py`.

### The 18 that remain, and why each is not a stale copy

**Guarded (6).** A copy is legal only when **something executes a comparison of
it against the card**, so a disagreement is loud rather than silent — the same
bargain that made M4 the only mutant caught.

- `score_tools.NAMES` — `load_rubric` compares it to the card's parsed dimension
  titles and raises `RubricError` on disagreement.
- `tests/test_score_tools.py`'s fragments — each asserted to occur exactly once
  in the card before use.

The exemption is **earned by demonstration, not declared**:
`test_the_guarded_copies_are_really_guarded` makes `NAMES` disagree and requires
the refusal. `test_every_guarded_entry_still_restates_something` deletes the
exemption when the copy goes, so the list cannot rot.

**Records (12).** One principle — *a record of what was true when it was written
is not a live declaration* — with five instances: the card, `specs/.history/`,
records under `specs/results/`, the sealed `PREDICTIONS-*.md` that
`check_prediction_seal.py` reads as written, and `deferred_findings.yaml`. The
two wrong `PORTS-AS-ADAPTERS-EPIC.md` rows survive **verbatim** in the findings
that reported them, on purpose: a finding that deletes its own subject is not a
finding.

**Five carve-outs is the thing to watch.** Each is argued in the check's
docstring; none is executed as a rule. A sixth added without argument is how
this becomes a whitelist. Filed as part of `SM-06-DF-04`.

## 4. The check, and what it cannot see

`tests/test_card_has_one_home.py`. `declaration_executability_rule` applies to
this rule as much as to the ones it replaced.

- **Every needle is derived from the card at run time.** Nothing in the file
  spells a dimension, an anchor or a scoring rule — a checker carrying its own
  copy of the thing it de-duplicates would be the joke that writes itself, and a
  hardcoded list is the shape rejected at `EVAL-RERUN-DF-01` and at
  `ARM_MODULE_PREFIXES`.
- **A dimension is a key adjacent to *any* of the five titles**, not to its own.
  A copy that got the pairing *wrong* is the copy that has already done damage
  here, and a per-key needle would have been blind to exactly that. `"D2 = 2 on
  27 of 27 cards"` next to the word "complexity" is a citation of a score and is
  not flagged — `test_a_score_citation_is_not_a_statement_of_the_card` pins that,
  because a checker that flags ordinary talk about scores gets turned off.
- **Anchors and rules match on content words**, so a copy that swapped a comma
  for an "and" and shouted a word is still a copy. That is how M2's paraphrased
  copy was found.

**Registered** in `instruments.toml` as `one-home-tripwire`, by hand — a repo
tripwire that is a pytest file has no `__main__` and is invisible to
`[registry.enumeration]`, the hole SM-03 wrote down. That count is now **six**
such files, not five.

**Its failing demonstration stages the rubric to a second path.** A hand-written
offending charter would have put a copy of the card into the registry — the
violation, committed by the row that detects it. Staging the card twice produces
a perfect offender that can never drift, because it *is* the card.

### Declared blind spots — R2, pointed at the new instrument

- **A paraphrase escapes.** README stated one scoring rule in its own words,
  sharing no content-word run with the card's wording, and the scanner does not
  flag it. Several of the copies deleted here were paraphrases and were found by
  **reading**. No tightening finds them without matching ordinary English.
- **One scoring rule is not watched at all** — its lead sentence is three words,
  too short to match without flagging any sentence on the subject.

Both are **demonstrated** by `test_the_blind_spots_are_declared_and_still_real`,
which fails the day either stops being true, rather than being asserted in prose
that nothing executes. Filed as `SM-06-DF-04`.

**No new gate on the product.** This watches documents, not the program.

## 5. The card's content is unchanged

```
$ git diff HEAD -- references/eval_scorecard.md
(empty)

$ shasum -a 256 references/eval_scorecard.md
210618e0c6557592940d086d91c8e35502a521af07b9429364ea667d31998594

$ git show 6aac1ec:references/eval_scorecard.md | shasum -a 256
210618e0c6557592940d086d91c8e35502a521af07b9429364ea667d31998594

anchors_digest  sha256:eeccf4576bc6fd85     (identical at v1, v2 and v3)
rubric digest   sha256:546f90e21d1254e0
file_sha256     sha256:210618e0c6557592
served_digest   sha256:694280073db988fe
```

D2, D4 and D5 stay on the card. No anchor was tuned. SM-05's experiment is
untouched.

## 6. The three upstream PRs — reconciled, NOT merged

Merge authority is the owner's. All three remain **OPEN**.

| PR | what SM-06 changed |
|---|---|
| [`git-epic-skill#6`](https://github.com/haydenrear/git-epic-skill/pull/6) | two card statements removed: the "mixed instrument" bullet restated a scoring rule, and the worked example named a dimension. Added *"Name the instrument; do not copy it"* with the measured reason. `32 passed`, unchanged. |
| [`git-issue-skill#3`](https://github.com/haydenrear/git-issue-skill/pull/3) | scanned clean — no dimension, anchor or rule. Additive: an issue author is told not to paste a rubric into an issue body. |
| [`git-issue-workflow-skill#7`](https://github.com/haydenrear/git-issue-workflow-skill/pull/7) | scanned clean. Its disclaimer *"not the authority on any particular card"* became an instruction: cite the sealed card and the rubric version, and stop. |

All three stay **card-agnostic** and acquire no `example` / `arms` / `judges` /
`version` fields of their own. The three rows the contract was too narrow on —
`harness` may be a judged procedure, a target may be multi-clause or deliberately
unthresholded, a verdict may be per clause — were already carried by the PRs and
are unchanged by this reconciliation.

## 7. Acceptance

```
$ uv run --with pytest --with pyyaml python -m pytest tests -q
1386 passed in 471.39s

parent 6aac1ec: 1378 passed in 431.07s     (+8 = this ticket's)

$ python3 examples/validation/instruments/demonstrate.py --only one-home-tripwire
one-home-tripwire   ok   ok   -   demonstrated-can-fail
Every declared demonstration reproduced.

$ python3 examples/validation/instruments/demonstrate.py       (full, at f26ec40)
exit 0, 0 failures

$ python3 examples/validation/scorecards/score_tools.py audit   exit 0
$ python3 examples/validation/scorecards/score_tools.py check specs/results/scorecards   exit 0
```

**Parent-commit evidence.** `tests/test_card_has_one_home.py` does not exist at
`6aac1ec`, and its central assertion fails on the parent tree's content: the
before-census lists 38 statements in 10 files, 20 of them unguarded. The
mutant table in §1 is the same fact measured from the other side — the parent
commit could not detect a copy that disagreed with the card, on three of four
tries.

## 8. Findings filed — 5, at budget, none fixed

| id | severity | |
|---|---|---|
| `SM-06-DF-01` | major | nothing could detect a disagreeing copy; 3 of 4 uncaught |
| `SM-06-DF-02` | major | `served_digest` does not cover every byte a judge is served |
| `SM-06-DF-03` | minor | `check` did not catch an edited anchor; `audit` did |
| `SM-06-DF-04` | minor | the new check cannot see a paraphrase; one rule unwatched; five carve-outs |
| `SM-06-DF-05` | major | `wt new` branched from a stale local epic ref, 21 commits behind |

## 9. What was REJECTED

- **Correcting the `PORTS-AS-ADAPTERS-EPIC.md` baseline table instead of
  deleting it.** The obvious move, and the wrong one: a corrected copy is still
  a copy, and this table had already been corrected twice by hand. It is
  replaced by a pointer plus the narrative of *how* it went wrong, which is the
  part that cannot go stale.
- **Deleting the two wrong rows from `deferred_findings.yaml`.** The strongest
  temptation, because they are literally restatements of the card and my scanner
  flagged them. Kept: those findings *are about* those rows, and rewriting a
  finding to a pointer erases the evidence for the finding. Scoped out with the
  reason written down rather than silently skipped.
- **Editing the sealed `PREDICTIONS-*.md`** (9 statements). They are sealed
  pre-dispatch records that `check_prediction_seal.py` reads as written. Deleting
  from them would have cut the headline count from 20 to 29 for free — which is
  exactly the `denominator_rule` failure this epic named.
- **`score_tools.NAMES`.** Tempting to derive it from the card and drop five
  statements. That would have deleted a **check**, not a copy: `NAMES` exists so
  `load_rubric` refuses when the card's dimension titles drift, and deriving it
  makes the guard vacuous. Kept, and made to earn the exemption with a
  demonstration.
- **Widening the matcher to catch paraphrases.** Buys the coverage back in false
  positives on ordinary English, on a check whose entire value is that nobody
  turns it off. Declared as a blind spot instead.
- **Fixing `served_digest` to cover the whole scaffolded card** (`SM-06-DF-02`).
  In scope by proximity, out of scope by rule: it changes the card's own
  contract, which is SM-04's surface, and `FI-03-DF-02` already argued that
  trade-off in the other direction. Filed, not fixed.
- **Merging the three upstream PRs.** Reconciled and pushed; merge authority is
  the owner's and is a separate decision.
