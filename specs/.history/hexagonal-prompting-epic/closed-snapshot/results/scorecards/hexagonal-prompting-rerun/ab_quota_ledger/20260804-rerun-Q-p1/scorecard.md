# Scorecard — artifact Q, pass 1

**Judge:** claude-opus-5[1m] · blind to arm · scorecard_version 1
**Run:** 20260804-rerun-Q-p1 · commit 24ed3fa6c58e65a9735e6e3406fd5b10e8a34b9d

| | D1 | D2 | D3 | D4 | D5 | total |
|---|---|---|---|---|---|---|
| score | 3 | 2 | 4 | 3 | 4 | **16** |

Paths below are abbreviated: `artifact_Q/` is
`/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/b726dabf-a199-4b0c-8c2d-dda863fb43b7/scratchpad/blind/artifact_Q/`.
The JSON card carries them in full.

---

## What I ran, and what it printed

I did not accept the evidence packet's kill table or the artifact's NOTES.md as
findings. Both were treated as claims and re-derived.

### 1. Both suites, as shipped

```
$ QUOTA_LEDGER_DIR=.../artifact_Q QUOTA_LEDGER_IMPL=quota_ledger \
    uv run --with pytest python -m pytest .../ab/tests/test_behavior.py -q
28 passed in 0.04s

$ cd .../artifact_Q && uv run --with pytest python -m pytest tests/test_ledger.py -q
53 passed in 0.06s
```

Both counts match NOTES.md:14 and NOTES.md:27-28 exactly.

### 2. My own mutation run — I rebuilt the seeded catalogue

The packet's table is a measurement I did not witness, and `seeded_faults.toml`
is off limits. So I reconstructed all ten fault classes plus the negative
control as find/replace mutants against **this** tree, from the class names and
descriptions in the packet, asserted each pattern occurred **exactly once**
before applying it, and ran both suites on each mutated copy. These are *my*
mutants, not the catalogue's — the classes match, the exact edits will not.

| mutant (my reconstruction) | artifact's own suite | shared suite |
|---|---|---|
| M01 guard-zero-amount (`amount < 1` → `< 0`) | **KILLED** 4 failed, 49 passed | **KILLED** 2 failed, 26 passed |
| M02 guard-over-quota (`> available` → `> available+1`) | **KILLED** 2 failed, 51 passed | **KILLED** 3 failed, 25 passed |
| M03 guard-close-with-outstanding (disabled) | **KILLED** 2 failed, 51 passed | **KILLED** 2 failed, 26 passed |
| M04 durable-stale-total (line prints amount as total) | **KILLED** 4 failed, 49 passed | **KILLED** 2 failed, 26 passed |
| M05 durable-close-line-zero | **KILLED** 4 failed, 49 passed | **KILLED** 2 failed, 26 passed |
| M06 wrong-status-on-release | **KILLED** 2 failed, 51 passed | **KILLED** 1 failed, 27 passed |
| M07 positive control, wrong hold (`amount-1`) | **KILLED** 30 failed, 23 passed | **KILLED** 8 failed, 20 passed |
| M08 cross-aspect, commit refunds the hold | **KILLED** 6 failed, 47 passed | **KILLED** 2 failed, 26 passed |
| M09 ledger order reversed | **KILLED** 6 failed, 47 passed | **KILLED** 5 failed, 23 passed |
| M10 double refund on release | **KILLED** 6 failed, 47 passed | **KILLED** 2 failed, 26 passed |
| **N01 negative control — outstanding id order reversed** | **KILLED** 4 failed, 49 passed | **SURVIVED** 28 passed |
| BASELINE (unmutated) | 53 passed | 28 passed |

**The surprise of this round is the N01 row**, and it is the single most
interesting fact I found. The packet certifies N01 as a control that *must*
SURVIVE every generated instrument, and it does — corpus-whole, corpus-neg, both
slices, map-silent and map-checking all report SURVIVED (evidence_Q.md:42). The
shared 28-test contract lets it survive too; I confirmed that myself above. But
FEATURE.md's observable-state table says `outstanding_ids()` returns the live
ids **ascending**, so reversing that order is a genuine violation of the stated
requirement. Artifact Q's own hand-written tests catch it. Whatever else is true
of this artifact, its suite is strictly stronger than both the shared contract
and every model-derived instrument in the packet on at least one real spec rule.

### 3. The adapter swap, actually performed

NOTES.md:46-47 states the swap in one sentence. I ran it.

```
one-line edit in quota_ledger/__init__.py:39, nothing else touched:
  return Ledger(quotas, FileJournal(ledger_path))
    ->  return Ledger(quotas, InMemoryJournal())

SHARED 28-test contract, real FileJournal REPLACED by the fake, domain untouched:
   28 passed in 0.03s
   domain.py byte-identical: True
   file_journal.py still present and unreferenced by domain: True
```

The *entire specified behavior of the program* survives replacement of its only
I/O adapter, with zero domain edits.

### 4. Runtime decoupling, not import topology

The card is explicit that a D3 of 3+ needs evidence about what *calls* what at
runtime. I wrapped `builtins.open` and drove a full
`reserve` → `commit` → `close_tenant` cycle through the domain wired to the fake:

```
files opened during full domain exercise on the fake: []
```

Zero filesystem calls — not merely zero filesystem imports.

### 5. The parametrization, verified rather than read

```
$ pytest tests/test_ledger.py -q -k "file"     26 passed, 27 deselected
$ pytest tests/test_ledger.py -q -k "memory"   25 passed, 28 deselected
```

25 identical cases run against both adapters, plus one file-only case. I
specifically checked for the standard way this anchor is faked — a test that
asserts the two wirings *agree with each other* — and found none; every case
asserts a literal expected value, so a domain wrong in both wirings still fails.
The artifact names this trap itself, in the test file, at test_ledger.py:5-9.

### 6. Every self-reported defect, executed

```
reserve('acme', 2.5) -> accepted;  ledger_lines -> ['COMMIT acme 2.5 2.5']
available('nobody')  -> KeyError: 'nobody'
committed('nobody')  -> KeyError: 'nobody'
is_closed('nobody')  -> False
Journal.append raises OSError:
  committed('acme') AFTER the failed durable write -> 3 | outstanding -> [] | R2 broken: True
```

All four disclosures in NOTES.md:125-145 are true and reproduce exactly as
written. Nothing in the notes overstated the artifact.

### 7. Static checks

20 test functions, none without an assertion. `domain.py` imports exactly
`{__future__, dataclasses, typing}`, which the artifact proves about itself by
AST-parsing its own domain module (test_ledger.py:260-270).

---

## D1 — Bug detection: **3**

Anchor 2 is met by **content**, not shape. The suite asserts exact durable
strings: `artifact_Q/tests/test_ledger.py:117-131` pins the four-line transcript
`['COMMIT globex 1 1','COMMIT acme 4 4','COMMIT acme 2 6','COMMIT globex 3 4']`,
and `:202-226` a five-line one. My M04 and M05 mutants — both content faults
that leave every shape intact — died against it.

Anchor 3 is met twice. The packet's executability table (evidence_Q.md:82) shows
corpus-whole executing **0** of every `Refuse*` action, so the refusal class is
structurally unreachable for the whole-view corpus; artifact Q's R4 table
(`tests/test_ledger.py:161-199`) kills all three guard-relaxation mutants and
additionally asserts that a rejection writes no durable line. And the ordering
class: N01, which no generated instrument and not the shared suite can reach,
dies against `tests/test_ledger.py:100-105`, a case written past `r10` precisely
because a naive lexicographic sort would put `r10` before `r2`.

**Capped at 3 for one unambiguous reason.** Anchor 4 requires that the cases
doing this were *derived from the model rather than hand-written*. This tree is
six files: four source, one test, one NOTES.md. There is no model, no TLA+, no
corpus, no generator, no property-based strategy. `tests/test_ledger.py` is
hand-written pytest. The *other* half of anchor 4 is genuinely present — the
record does name fault classes it cannot reach (NOTES.md:136-145) — but half an
anchor is not the anchor, and the card says take the lower.

## D2 — Complexity: **2**

**I rejected the owner's amendment.** Four reasons; the fourth decides it.

1. The card's own rule 7 makes the mechanical block *recorded, never scored*.
   The amendment converts it into the substance of a score.
2. The two columns are not a before and an after. Nothing was transformed from
   one into the other, so there is no "what got simpler" available — and the
   card requires me to *say what got simpler* for any D2 ≥ 3.
3. On every mechanical figure that differs, this artifact is the **larger**:
   module_count 4 vs 1, production_lines 129 vs 122, public_name_count 25 vs 20,
   branches 11 vs 10, io_imports `os,pathlib` vs `pathlib`
   (evidence_Q.md:113-121). Granting the amendment would not credit Q with a
   simplification; it would credit the other column.
4. **Decisive:** the mechanical block does not contain the figures the
   artifact's one real simplification would move. That simplification is
   deriving `available` rather than storing it
   (`artifact_Q/quota_ledger/domain.py:118-120`, argued at NOTES.md:70-84), and
   its entire point is one fewer mutable variable with fewer writers. The block
   reports `mutable_state_count` 8 vs 8 and `max_writers_of_one_attribute` 2 vs
   2, and the packet itself states `state_writers` "discriminates nothing"
   (evidence_Q.md:120-121). The amendment asks me to read a before/after out of
   a block that demonstrably does not measure the thing in question.

Anchor 2 is comfortably met and I want to be clear the 2 is not grudging. State
is `_quota`, `_committed`, `_closed`, `_outstanding`, `_issued`, `_journal`
(domain.py:106-114). No god-state: `_committed` is written by `commit` alone,
`_closed` by `close_tenant` alone. Eleven branches against a specification that
mandates at least nine rejection branches, so the branch count is essentially
all essential. NOTES.md:53-55 declines further indirection and I verified the
code matches — no repository interface over the reservations dict, no service
layer, no port in front of the arithmetic.

Anchor 3 fails on its literal words: a simplification was **argued**, and its
counterfactual described in prose, but **no before figure and no after figure
were ever recorded for it**. That is the whole gap.

I did not penalize the four-module split. FEATURE.md deliberately unspecifies
whether the durable side is reached through an interface and warns judges not to
read a difference there as a defect.

## D3 — Modularity: **4**

Anchor 3, demonstrated rather than asserted: the swap I name is
`quota_ledger/__init__.py:39`, and running it keeps the full 28-case shared
contract green with `domain.py` byte-identical (§3 above), plus zero runtime
filesystem calls through the fake (§4). The port is declared in the domain's own
vocabulary with a binding written contract (`domain.py:22-43`) and the domain
imports only `__future__`, `dataclasses`, `typing` (`domain.py:13-16`).

Anchor 4: the driven port is exercised by a real adapter *and* a fake from one
case list (`tests/test_ledger.py:26-36`), with 25 identical cases passing against
both (§5), and the fake (`quota_ledger/memory_journal.py:14-22`) is a working
implementation of the contract rather than a mock.

**`refuses_to_claim`:** that the port isolates the record *format*. The domain
renders the finished line and the Journal carries a pre-rendered string, so no
Journal implementation can change what a record says — only where it goes.
NOTES.md:57-66 states this as a deliberate boundary choice instead of claiming
full format independence, and NOTES.md:53-55 refuses to claim anything else is
indirected.

## D4 — Behavior preservation: **3**

There is no baseline and nothing was refactored, so I read anchor 2's "the
behaviors the baseline exhibited" as *the behaviors FEATURE.md specifies*, and I
say so rather than smuggling it. On that reading anchor 2 holds: R1–R5 are
enumerated by name and each shown to hold (`tests/test_ledger.py:176` carries R4
including the durable side; `:203` reads R1, R2, R3 and R5 off one concrete
transcript), and every command's accept and reject path is covered.

The artifact clears anchor 1's exclusion because it *does* argue coverage of the
behavior at issue. NOTES.md:76-79 anticipates the MF-020 failure mode of its own
simplification — that deriving `available` might be a deletion rather than a
derivation — and names the two assertions that pin the surviving behavior. I
tested that guard instead of believing it: my M08 mutant made `commit` refund the
hold, and 6 of the artifact's tests and 2 shared tests failed.

Anchor 3 rests on the packet, not the tree: a model-derived corpus executed 3734
cases on this artifact and raised on none on the unmutated tree, so the checking
is not *only* hand-written assertions.

**I was genuinely torn between 3 and 4 and took the lower, as the card
instructs.** Anchor 4 is factually satisfied — ten deliberate behavior-breaking
changes, 10 of 10 caught by the artifact's suite and 10 of 10 by the shared one,
so the check is demonstrably capable of failing. But every one of those
demonstrations came from **outside** the artifact: from a harness its author
never saw, and from me, just now. The artifact's own record contains no mutation
run, no deliberately broken variant, no kill-capability evidence of any kind. An
artifact that never tried to break itself has not *shown* its checks can fail; it
was shown *about*. That is the distance between 3 and 4 here, and it is a gap the
author could have closed cheaply and did not.

## D5 — Honesty: **4**

I treated the self-reported limits as claims to falsify, and executed all four
(§6). Every one is true and reproducible — including the one that matters most,
NOTES.md:136-141, which refuses to claim R2 holds under a failed durable write.
I injected a Journal whose `append` raises, and got `committed('acme') == 3`
against an empty journal: **R2 genuinely broken, exactly as disclosed.** The
non-integer disclosure is equally real, producing the literal ledger line
`COMMIT acme 2.5 2.5`.

Anchor 2 is met in the artifact and not only in a report: `tests/test_ledger.py:5-9`
names, inside the test file, the blind spot of the cheaper design that would have
compared the two wirings to each other. Anchor 3 is met in code as well as prose:
`quota_ledger/domain.py:72-75` asserts a rejection reason is one of the declared
six rather than letting an undeclared reason through — a refusal to emit rather
than a silent certification. Anchor 4 is met by the two verified defects above:
the record carries a named hole in one of the feature's own five rules, in the
one place a reader would look.

**`refuses_to_claim`:** that R2 is enforced by construction; also any behavior
for non-integer amounts (refusing to invent a seventh rejection reason when the
vocabulary is fixed at six), and any unknown-tenant result on the query side
(the feature gives queries no status vocabulary).

---

## On prose quality, which the card forbids as an input

This artifact is the best-written thing I have scored on this card, and that is
exactly why I ran everything. NOTES.md is organized, concedes its own warts, and
uses the vocabulary a judge wants to hear — "This is a *derivation*, not a
deletion", "because 'does not import' is a claim about the file rather than about
intent". That register is what a sophisticated artifact optimizing for a judge
would produce, so I treated the polish as a reason for suspicion rather than
credit. Concretely: I re-derived the 53 and 28 counts, re-ran the swap the notes
describe in one sentence, checked the parametrization for the agree-with-itself
cheat, AST-checked the import claim independently of the artifact's own AST test,
and executed all four confessed defects. Every claim held. The score reflects
what executed; had the same prose sat on top of an artifact where the swap did
not run or the confessed defects were not real, D3 and D5 would have collapsed.

The two scores I withheld are both withheld for structural reasons the writing
could not have fixed: D1 and D4 are capped because nothing in this tree is
model-derived, and D2 is capped because a simplification was argued and never
measured.

## Things I did not do

- I opened none of the forbidden files. While verifying NOTES.md's claim that it
  left the repository clean, `git status --porcelain` printed one untracked path
  under `specs/results/scorecards/`. I read the path in that output and opened
  nothing under it. I disclose it because the rule is about the directory and I
  would rather over-report.
- I did not guess which prompt produced this artifact, and I have not inferred
  it. The packet's `seeded_by` column and the mechanical block both invite the
  inference; I declined to draw one, and no part of this card rests on any belief
  about which arm this is.
- I did not modify the artifact, the repository, or git. All mutation and swap
  work ran on copies in a scratch directory.

## Verdict

Ship it as the modularity reference for this example: a one-line adapter swap
that I ran keeps the full 28-case contract green with the domain byte-identical
and zero filesystem calls, and all four of its self-reported defects reproduce
exactly as written — but do not read its D2 as a simplification result, because
no before/after figures for its one real simplification exist anywhere and I
rejected the pair-as-measurement amendment on the grounds that the mechanical
block reports 8 vs 8 state and 2 vs 2 writers, which is precisely the measurement
the amendment would need and does not have.
