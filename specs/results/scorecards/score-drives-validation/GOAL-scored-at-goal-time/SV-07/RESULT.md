# SV-07 — the note was cheap in bytes and it was never free

**Branch point `c9be7b5`, verified with `git rev-parse --short HEAD` rather than
taken on trust.** The epic charter records that `wt new` branches from the local
ref and has put tickets 4, 14 and 21 commits behind, and that a handed-out SHA
has failed to resolve once. This one resolved and matched. Every number below
names the tree it was taken at, and the tree with this ticket's ticket workspace
open is a different tree from the tree without it — which is stated wherever it
changes a count, because `denominator_rule` covers suite counts too.

---

## 1. What the work order asked for, and what came back

**Asked:** ship `references/scoring_validation.md`'s cheapest carrier for
demonstrated refutability — a sharpened recorded-note prompt, priced at **−15
bytes** and **no new rung** — collapsing the duplication that pays for it, and do
it **without restoring a retired dimension, without adding a rung, and without
forcing a card bump**.

**Came back:** the prompt is built, priced with the real renderer at exactly the
figure SV-02 predicted, and **it cannot be put into the card at this ticket,
because a recorded note's prompt is inside both of the card's seals and editing
one costs the version bump the work order forbids.** That is `SV-07-DF-01` and it
is the ticket's main result.

**Shipped instead, at zero bytes on the served surface:**
`scripts/candidate_note_bar.py`, which **derives** the candidate bar from the card
at run time, applies the one substitution, adds the version row the change rule
requires, and prices the result. It writes nothing unless asked. Nothing in this
ticket adopts it, and `tests/test_candidate_note_bar.py` ends with the shortest
test in the file asserting exactly that.

---

## 2. The surface metric, before and after

`serve | wc -c` at `c9be7b5`, and at `c9be7b5` plus this ticket:

| | bytes | rungs |
|---|---|---|
| the card, before | **6,281** | 9 |
| the card, after | **6,281** | 9 |
| **delta** | **0** | **0** |

The card was not touched. `references/eval_scorecard.md` is byte-identical to its
state at the branch point; `git diff c9be7b5 -- references/eval_scorecard.md` is
empty and is the check, not this sentence.

And the candidate the generator produces, rendered by the same renderer a judge
would be served by:

| | bytes | rungs | anchors digest |
|---|---|---|---|
| card, version 5 | 6,281 | 9 | `sha256:f73b4d82638f09df` |
| candidate, version 6 | **6,266** | **9** | `sha256:f73b4d82638f09df` |
| **delta** | **−15** | **+0** | **UNCHANGED** |

**The anchors digest is byte-identical**, which is the executable form of *"do
not add a rung"*: a candidate that grew one would move that digest and fail
`test_the_candidate_adds_no_rung_and_moves_no_anchor` before anybody read its
prose. **Exactly one served line differs**, and it is the note prompt.

`python3 scripts/candidate_note_bar.py` re-derives all six numbers in under a
second.

---

## 3. The deduplication that pays for it

The served surface asks a judge **three times** whether it seeded a fault of its
own, and the third time is inside the recorded note. In served order: a numbered
scoring rule, then the required judging-practice block, then the note prompt's
last sentence. The first two are load-bearing — one is the rule, one is the field
a card must carry — and the third is a restatement of them in a place a judge has
already read both.

The candidate spends those bytes on the two things judges volunteer anyway when
no ladder is under them: **the denominator of the artifact's own checking**, and
**the reason the region it stays green on is structural**. The whole of the
change to what a judge reads is this, and it is machine-extracted rather than
retyped here:

```
- What did the cases catch, and what class did they demonstrably miss? Name the fault you seeded if you seeded one.
+ What went red when you broke it, with the denominator, and what class stays green by construction?
```

**It names no tool.** `test_the_candidate_asks_nothing_about_where_a_case_came_from`
executes that: hand-written, generated, property-based, fuzzed and model-derived
cases satisfy it or fail it identically, which is the whole property. A prompt
that asked for a provenance would be the retired clause returning under a new
name, and that is the trap the work order names.

---

## 4. `SV-07-DF-01` — the finding, and how it was demonstrated

`references/scoring_validation.md` section 6 prices a note prompt at −15 bytes
against +682 for a restored scored dimension, and section 7 concludes: *"Carrier
R requires a version bump and would hand every adopter that experience. **The
free carriers do not.**"*

**The second sentence is false.** A recorded note's prompt is inside both of the
card's seals — it is in the payload `load_rubric` digests, and it is in the bytes
`serve` emits, which `## Version history` declares per version and
`score_tools.version_history_problems` recomputes for the current row. Put the
priced prompt into the card and change nothing else, and the card's own change
rule refuses it, in the tree's own words:

```
version 5 declares served digest sha256:2d7d4a0506d9b259 but the bytes this file
serves digest to sha256:4af772c5b075bd6b. Something a judge READS moved -- a
caveat, a preamble, a scoring rule or a note -- without a version bump. Bump the
card, or restore the text; a served surface that changes under a fixed version is
the card changing silently where the anchors digest cannot see it.
```

**The card's own version 5 row is the precedent and says so out loud**: it moved
no anchor, moved only served bytes, and took a bump to do it. That is the class of
change CL-01's second seal was built to catch, and a note prompt is squarely in
it.

### The demonstrated failing input, on real sealed cards (`R1`)

Not a fixture. `tests/test_candidate_note_bar.py::test_the_note_prompt_is_inside_both_seals`
runs two halves:

1. the change rule above, executed against a card carrying the candidate prompt
   and **nothing else** — no bumped declaration, no version row;
2. the two **real** version-5 cards under
   `specs/results/scorecards/close-the-loop-cl03-v5/toolchain_removal/` —
   `20260811-cl03v5-CL-p1` and `-p2`. Both record
   `sha256:2d7d4a0506d9b259`, both agree with the shipped bar today, and both go
   **SERVED-DRIFT** against the candidate. The same cards checked against the
   shipped bar do **not** drift, so the drift is a fact about the candidate and
   not about the cards (`R2`).

Run over the whole record at `c9be7b5` — 87 cards, all filled — `check` with the
candidate served reports **48** SERVED-DRIFT notes against **46** at the shipped
bar, and **68** RUBRIC-DRIFT against **66**. **Both deltas are the same two
cards**, which is the two seals showing up separately, exactly as the card's
version-history section says they should. Problem count is **330** on both sides:
a note prompt re-bases what a card was served and violates nothing — it is not a
rule the record breaks, it is a bar the record stops being comparable to.

### What the finding costs the epic's reasoning

Both carriers cost a version bump. A bump is an `INSTRUMENT-LOG.toml` era
boundary — the log already carries one per bump, `SM-04-scorecard-v3`,
`RM-03-scorecard-v4`, `CL-03-scorecard-v5` — plus the change rule's re-score of a
prior example under both versions, plus CL-04's blocker 2 handed to every
adopter. **That was SV-02's decisive argument against the rung, and the note pays
it too.** What still separates them is 4 permanent rungs and 682 bytes, which is
a real difference and is not the difference the recommendation rested on.

**`serve | wc -c` is not the binding constraint for note-shaped changes**, and
nothing said so before this ticket tried to spend it.

---

## 5. What was NOT done, and why each one was a rule rather than a preference

- **D4 was not restored.** SV-02 rejected it *"for now, not on principle — the
  round justifying it hasn't run"*, an anchor is permanent, and the change rule
  forbids deleting a shipped one. Nothing here adds, deletes or rewords an
  anchor, and the anchors digest proves it rather than promising it.
- **No rung was added.** 9 rungs before, 9 after, on the card and on the
  candidate.
- **The card was not bumped.** The work order says a required bump is a finding
  and not a licence. It is filed as one.
- **No new gate.** The generator always exits 0 unless it cannot read the card,
  writes nothing without `--out`, and nothing in production imports it. The only
  new assertions are in a test file, about a generator, not about anybody's
  artifact.
- **No skill was edited and `skill-manager sync` was never run.**
- **SV-02's page was not rewritten.** A predecessor's statement at a
  predecessor's scope is filed and left standing, the way `RM-02` left
  `architecture_tags.md` section 2.2 and the way SV-02 itself left the card's D4
  retirement sentence.
- **A checked-in frozen candidate was rejected.** `tests/test_card_has_one_home.py`
  measured what a second copy of the card costs — four copies were made to
  disagree and **three of four were UNCAUGHT by the whole suite** — and its
  exemption is earned only by something that executes a comparison against the
  card. There is nothing yet to compare a *future* candidate against, because the
  row it would be compared to does not exist. **A generator has no copy to
  drift**: change the card and the candidate changes with it, or the generator
  stops matching and refuses.
- **A checker that a note carries a denominator was rejected**, because SV-02
  rejected it under `no_new_gates_rule` and seven epics of static checking have
  caught nothing. The denominator is a number a round reports, not a number a
  gate demands.
- **`demonstration_grade` was not productionised.** SV-02 says in terms that it
  is a regex over prose never validated against a human read, and its own section
  9 lists "whether it measures anything" as unsettled. Shipping it as an
  instrument would be shipping a fourth blind one.

---

## 6. What this leaves open, stated as open

- **Whether the candidate wording changes what judges write.** This ticket
  produced the arm and ran no round. SV-02 section 9's first bullet — one prior
  example re-scored under both wordings — is still the experiment that decides
  it, and it now decides the prompt and the rung *together*, because they are
  known to cost the same bump. `--out` exists so that round can be run in one
  command instead of by hand-freezing a file.
- **Whether the property survives contact with an adopter.** Everything here is
  priced from a record where we wrote both the artifact and the instrument.
  `RM-02` section 7 said it, SV-02 repeated it, and it is still true.
- **Whether a card bump is affordable at all.** CL-03 paid for one with a four-card
  re-score one epic ago, so the answer is probably yes and it is a judging round,
  which is SV-05's to spend, not this ticket's.

---

## 7. Numbers, with their trees

**`scope`, run over both trees.** Every row names its tree; the sweep is a joint
property of the record and the card population and moves when either does.

| tree | counted | REFUTED | COUNT-MOVED | HOLDS | UNREACHABLE |
|---|---|---|---|---|---|
| `c9be7b5` — the branch point, checked out clean | 97 | 71 | 0 | 6 | 20 |
| `c9be7b5` + SV-07 | 97 | 71 | 0 | 6 | 20 |

**SV-07's delta on `scope` is zero on every column.** This ticket's pages carry no
bind-and-value figure the checker can reach, which is a fact about the pages and
not a clean bill of health for them — the same bound SV-02 recorded as
`RD-02-DF-01`.

**The suite**, `uv run --with pytest --with pyyaml python -m pytest tests -q`,
which is the acceptance command the plan declares:

| tree | result |
|---|---|
| `c9be7b5`, checked out clean, **before `open ticket SV-07`** | **2 failed, 1518 passed** |
| `c9be7b5` + SV-07, **after `close ticket SV-07`** | **2 failed, 1528 passed** |

**The two reds are the two the epic charter says are inherited deliberately, by
name at both ends** — `test_architecture_tags.py::test_the_same_tag_control_holds`
(`RM-06-DF-01`) and
`test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer`, whose
unguarded offenders are the two narrative documents `CLOSE-THE-LOOP-EPIC.md` and
`NEXT-EPIC.md`. **Neither was repaired.** Nothing else went red at either end.

**+10 passing, and `denominator_rule` says which side each came from.** Eight are
`tests/test_candidate_note_bar.py`, which is this ticket's. The other two are
`tests/test_instrument_demonstrations.py`: the generator is an executable that
refuses, so the registry's discovery scan required a row for it, and the row
carries the demonstrations that go with it. **Neither end carries an open ticket
workspace** — the before run was collected before `open ticket` and the after run
after `close ticket` consumed it — so no parametrised yaml count moved between
them, which is stated because that count *does* move when a workspace is open.

The registry row is not a formality: `demonstrate.py --only candidate-note-bar
--tier all` reproduces both declared demonstrations, and the one that matters is
the failing one — **a generator of this kind is far likelier to print a confident
wrong number than to crash**, so its failing input is a card whose note bullet
was renamed, where a naive substitution would silently miss and price a change it
never made.

And the arm is runnable end to end, which is the point of shipping the generator
rather than the prose: `scaffold --rubric <the candidate>` emits cards against it
without a complaint, so SV-05's both-wordings round is a command rather than a
hand-freeze.
