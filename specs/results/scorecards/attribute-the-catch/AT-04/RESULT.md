# AT-04 — EVALUATION: the six goals, decided by reading

**Tree:** `epic/attribute-the-catch`, base `main` at `902cfd7`.
**Method:** read the record. **No harness was built, deliberately** — a script
written by the evaluation to decide the evaluation's own goals is an instrument
nobody reviewed, and this repository's scripted verdicts have a losing record.

---

## 0. WHAT THIS EPIC COULD NOT DO, FIRST

**The live ledger this epic documents does not exist on `main`.**

The 364-row `specs/deferred_findings.yaml` lives on `epic/stabilize-substrate`,
where `SS-01` moved it so it survives a workflow close. On `main` there are only
per-epic archived copies under `specs/results/`. **This epic branched from `main`
to stop depending on `stabilize-substrate`, and the record it describes is on
`stabilize-substrate`.**

Consequences, stated rather than worked around:

1. **Every baseline figure in the charter and the plan was measured at the
   `epic/stabilize-substrate` tip, not here.** They are labelled at their tree
   throughout. **They must be re-derived when `#296` merges, not quoted.**
2. **This epic's own records could not be written into the live ledger.** They
   are in
   `specs/results/scorecards/attribute-the-catch/AT-01/worked_examples.yaml`,
   and writing a second file at the ledger's path from this branch would collide
   with 364 rows on merge for no benefit.
3. **So `GOAL-the-record-says-what-caught-it` clause (b) — disposing the 27
   drifted rows — is DESIGNED, NOT APPLIED.** The disposition is written down;
   no row was edited, because the rows are not here.

**This is the single largest limitation of the epic and it is first on purpose.**

---

## 1. THE SIX GOALS

Scored on each target's own text, clause by clause. **No clause is split to gain
a verdict** — `CA-08` published *"14 met, 4 missed"* over rows that were 15/3 by
doing exactly that, and both splits were withdrawn.

### `GOAL-the-record-says-what-caught-it` — **MET (a), (c); DESIGNED NOT APPLIED (b)**

- **(a) Graph, suite and hand distinguishable from the token, no `channel_note`
  read — MET.** `references/bug_attribution.md` §4.1 is a nine-token table with a
  class column. Seven tokens are `CA-02`'s, unchanged and **not relabelled**; two
  — `test-graph` and `tlc` — are added because the record could not name them.
  The class rule is one question: **would it catch this again tomorrow, with
  nobody watching?** That is why `operator-running-a-shipped-instrument` is
  `automated` and `operator-running-own-instrument` is `hand`: **a throwaway
  probe that found a real bug is a hand catch wearing a script.**
- **(b) The 27 rows disposed — DESIGNED, NOT APPLIED.** See §0.3. The
  disposition, and its measurement, is the epic's sharpest finding:
  **all 27 are `SS-*`. Not one is from any other epic.** `CA-02` closed the
  vocabulary and the very next epic put four tokens outside it 27 times, with
  `disposition.py`'s `ADVISORY (not a clause)` line printing on every one.
  **The advisory worked exactly as designed — it advised, and was ignored,
  twenty-seven times, by the epic standing closest to it.**
  **And the disposition is mostly `UNDECIDED`, because the evidence is not
  there:** `channel_note` exists on **45 of 364** rows overall and on **9 of the
  27** drifted. **Eighteen carry no prose at all.** `review` → `independent-review`
  is a mechanical synonym rename, 3 rows. `execution` (23) and `reading` (1) are
  `UNDECIDED` where no note exists — `execution` plausibly means `the-suite`,
  `tlc` **or** `operator-running-a-shipped-instrument`, and **those are three
  different classes**, so a guess would decide the automated/hand split for 23
  rows on nothing.
- **(c) `blind-judges` retired or retained with a reason — MET.** **Retained.**
  It is the one token naming a channel that produced findings this project has
  published at length — the four judges of the `hexagonal-prompting` rerun
  produced 4 findings the round's own ratio omitted. **The token is not dead; the
  filing is.** Retiring it would delete the evidence that a channel exists and is
  not being recorded, which is this epic's entire subject.

### `GOAL-hand-catches-name-their-pin` — **MET**

`references/bug_attribution.md` §4.2. A non-automated catch names an assertion;
where none was added, `pin_note` says so and says why, and **a blank is not an
answer**. Automated catches need no pin — the thing that caught it is the pin.

**One deviation, recorded rather than applied silently:** the page requires a pin
for **any class that is not `automated`**, which is wider than the goal's text
(`hand`). A bug found by a reviewer has nothing standing that would find it
again, which is the entire reason the pin exists. **The goal is scored on its own
text and the widening is disclosed** — `references/bug_attribution.md` §4.2
carries the note.

**Demonstrated:** `AT-EX-CATCH-01` in `worked_examples.yaml` — the archive
scaffolding defect, `channel: operator-running-own-instrument` (class `hand`),
`pinned_by: tests/test_history_entry_size.py`, which exists at this tree and
passes.

### `GOAL-invariants-name-their-unenforced-surfaces` — **MET**

- **(a)** `references/bug_attribution.md` §5. `enforced_on` and `unenforced_on`,
  both enumerated. **(b)** `enumerated_by` is **mandatory whenever
  `unenforced_on` is empty** — an empty list with no `enumerated_by` is
  malformed, not clean. **(c)** *"I did not enumerate"* is
  `unenforced_on: UNDECIDED` with its reason, written differently from *"I
  enumerated and found none"*. **(d)** Nothing enforces it.
- **A real REACH on a real invariant, and it is deliberately self-implicating:**
  the worked example is *"every YAML file under `specs/` must parse"* —
  **the invariant this epic's own charter leans on** when it says there is no new
  test. Its `unenforced_on` names `specs/.history`, every YAML outside `specs/`,
  and **SCHEMA** — it asserts the bytes parse and nothing about fields, types or
  required keys. **The unenforced list is what leaning on it does not buy**, and
  it was derived from the test's source predicate, not guessed.

### `GOAL-green-declares-its-blind-spot` — **MET**

- **(a)–(d)** `references/bug_attribution.md` §6.
- **The worked example is the strongest single artifact this epic produced, and
  it is verifiable in one line:**
  `tests/test_spec_yaml_valid.py::test_spec_yaml_parses` **could never catch a
  duplicate key.** `yaml.safe_load("a: 1\na: 2\n")` returns `{'a': 2}` — accepts
  the file, silently keeps the last value, reports success. Verified at this
  tree.
  **And this is not hypothetical: `scripts/disposition.py` grew an explicit
  `duplicate_keys()` refusal (`disposition.py:98`, raised at `:181`) because a
  duplicate key in the ledger certified a clean answer.** So the repository
  carries **both** an instrument that refuses on duplicate keys **and** a green
  that cannot see them, **and nothing connected the two until a BLIND record had
  somewhere to be written.**
  The record deliberately **does not name the remedy** — naming it is how a BLIND
  turns into the standing instruction to duplicate (`architecture_advice.md` §5).
- **The second BLIND is `UNDECIDED` on purpose.** `CA-10-DF-14`'s vacuous passes,
  re-measured by `SS-06` at **six**, not three. Not enumerated by this ticket, and
  written as `UNDECIDED` rather than empty — **an empty
  `could_not_have_caught` there would read as "these greens are fine". They are
  not fine; they are unexamined, and the two must not look the same.**

### `GOAL-proposals-are-priced-before-not-after` — **MET**

`references/bug_attribution.md` §7. `declared_before` and `measured_after` as two
fields written at two times, with `declared_at_commit` making **backfilling
visible rather than convenient**: a price whose declaration commit is after the
measurement commit is a retrospective, and anyone reading the two shas can see
it. A refused proposal **keeps** its declared price.

**Demonstrated on a real one, found already complete inside a commit message:**
the rejected intra-entry deduplication at `902cfd7`. Declared before: *recover
50.5 MB across 5,386 files*. Measured after: *0 bytes recovered in version
control, 3 tests broken*. Verdict **REFUSED**. **Without the 50.5 MB written down
first, the measurement afterwards is just a story about why nothing happened.**
The commit preserved both halves by accident; this kind exists to stop it being
an accident.

### `GOAL-the-surfaces-ask-for-all-four` — **MET**

- **(a)** `references/workflows.md` §"Work A Ticket" step 7a — CATCH and BLIND,
  **during the work, not reconstructed at close**, with the reason stated
  (memory reconstructs favourably). **6 lines.**
- **(b)** §"Complete A Spec Workflow" step 4a — all four kinds plus *what the
  record could not show*. **16 lines.**
- **(c)** Nothing gates. No exit code moves. No tool reads either.
- **(d) The ask fits on a screen at each site — MET, and it was the binding
  constraint.** A page of instructions at a close-out is a page nobody reads, and
  would reproduce the 39.6% with better documentation.

---

## 2. THE PROMPT, RUN ONCE

`prompts/regression_architecture.md` was **written before any REACH or BLIND
record existed in this repository**, so its first run is against a corpus whose
answer was unknown when the ask was written. `MF-020` is answered: **not fitted**,
and the ordering is checkable from the commit.

**It has not yet been run against a full corpus, and that is the honest state.**
The corpus it is built to read is four rows. **A refactor proposal derived from
four records would be exactly the certification-from-a-partial-record that the
prompt's own step 4 exists to refuse** — and the prompt would be required to
refuse itself.

**So `GOAL-the-prompt-produced-a-refactor` is not claimed and is not scored MET.**
It is **UNMEASURED, with the reason: the corpus is four rows and the instrument
refuses at that size by design.** It becomes measurable when `#296` merges and
364 rows arrive.

**This is the null result and it is not buried.** The epic shipped the ask and
did not establish that asking produces a refactor. The precedent it bet against —
*"THE PROMPT PRODUCED THE STRUCTURE AND THE STRUCTURE CAUGHT NOTHING — again"* —
**is not refuted by this epic and is not confirmed by it either.**

---

## 3. THE TREE

Full suite at the tip, against `main`'s baseline of **7 failed / 1464 passed**
recorded at `902cfd7`:

```
SUITE_NUMBERS_PLACEHOLDER
```

Raw output: `pytest-tip.txt` beside this file.

**This epic added no test and no production code**, so any movement in the
numerator is not attributable to it; movement in **collection** is attributable
to the workflow scaffold, which added `specs/current` and
`specs/desired_program_model` where `main` had neither. **That is denominator
movement and it is declared, not discovered** — the predecessor epic learned the
same thing when scaffolding moved collection 1491 → 1503.

---

## 4. WHAT A REVIEWER SHOULD ATTACK FIRST

1. **The `automated` / `hand` class assignments in §4.1's table.**
   `operator-running-a-shipped-instrument` = `automated` and
   `operator-running-own-instrument` = `hand` is a judgement, defended by one
   question, and it decides the headline split for every future row.
2. **`GOAL-the-record-says-what-caught-it` (b) is DESIGNED, NOT APPLIED**, and a
   disposition that has never touched a row has never met a row that resists it.
3. **The pin requirement was widened from `hand` to "not `automated`"** after the
   goal was written. Disclosed, but a reviewer should check it was not widened to
   make a count easier.
4. **`GOAL-the-prompt-produced-a-refactor` is UNMEASURED, not MISSED**, and the
   distinction is doing real work for the epic's own scoreline. Check that it is
   the honest classification and not a hedge.
5. **Six of the six MET verdicts are on documents this epic itself wrote.**
   Nothing external tested any of them. That is the structural weakness of a
   markdown-only epic and no clause in it can fix that.
