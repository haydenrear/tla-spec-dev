# Scorecard — artifact Q, pass 2

Judge: `claude-opus-5[1m]`. Blind to arm. Scorecard version 1.
Total **14 / 20** — D1 3, D2 2, D3 4, D4 2, D5 3.

All paths below are absolute. `AQ/` abbreviates
`/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/b726dabf-a199-4b0c-8c2d-dda863fb43b7/scratchpad/blind/artifact_Q/`
and `EVAL/` abbreviates
`/Users/hayde/IdeaProjects/wt-epic-hexagonal-prompting-EVAL-RERUN/`.
Every citation in `scorecard.json` is written out in full.

---

## 0. Method — what I actually ran

The card says score artifacts, never claims, and run things. So the only
statements in this document that are not backed by a command I ran are
statements about what the source text says, which I read.

### 0.1 Baselines

```
$ QUOTA_LEDGER_DIR=AQ QUOTA_LEDGER_IMPL=quota_ledger \
    uv run --with pytest python -m pytest EVAL/examples/validation/ab/tests/test_behavior.py -q
28 passed in 0.04s

$ cd AQ && uv run --with pytest python -m pytest tests/test_ledger.py -q
53 passed in 0.05s
```

Both counts in `AQ/NOTES.md:14` and `AQ/NOTES.md:27-28` are exact.

### 0.2 My own mutation run

The packet's `suite` column is the **shared** contract — the same 28 tests run
against both arms — so it attributes nothing to this artifact. The artifact's
detection capability is `AQ/tests/test_ledger.py`, and nothing in the packet
measures it. So I re-seeded the catalogue myself.

Harness:
`/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/b726dabf-a199-4b0c-8c2d-dda863fb43b7/scratchpad/jQp2/mutate.py`.
Eleven mutants written as exact find/replace against a **copy** of this tree,
one per catalogue row, each with the same integrity discipline the packet
describes: the pattern is asserted to occur exactly once, the mutated file is
asserted to `ast.parse`, and apply-then-revert is asserted byte-identical.
Unmutated baseline green on both instruments before any mutant ran.

| mutant | class | seeded_by | own suite (53) | shared suite (28) |
|---|---|---|---|---|
| M01-guard-zero-amount | guard_relaxation | perturbation | **KILLED** | KILLED |
| M02-guard-over-quota | guard_relaxation | perturbation | **KILLED** | KILLED |
| M03-guard-close-outstanding | guard_relaxation | perturbation | **KILLED** | KILLED |
| M04-durable-stale-total | durable_content | perturbation | **KILLED** | KILLED |
| M05-durable-close-line-zero | durable_content | perturbation | **KILLED** | KILLED |
| M06-wrong-status-on-release | output_oracle | perturbation | **KILLED** | KILLED |
| M07-positive-control-wrong-hold | wrong_value | perturbation | **KILLED** | KILLED |
| M08-cross-aspect-commit-refunds-hold | cross_aspect | addition | **KILLED** | KILLED |
| M09-ledger-order | ordering | perturbation | **KILLED** | KILLED |
| M10-apply-only-double-refund | wrong_value | addition | **KILLED** | KILLED |
| N01-negctl-outstanding-id-order | ordering | perturbation | **KILLED** | SURVIVED |

**11 of 11.** The row that matters is the last one, and it is the thing that
surprised me most — see §1.

### 0.3 Runtime call topology

The card explicitly refuses import topology as evidence of modularity, so I
instrumented the running program: an audit hook armed after import, walking
`sys._getframe` (not `inspect.stack`, which recurses through `open`), plus a
recording stub in the `Journal` slot. I drove every command including every
rejection.

```
outbound calls the DOMAIN made across the boundary, in order:
    ('append', 'COMMIT acme 3 3')
    ('append', 'CLOSE acme 3')
    ('records', None)
distinct port methods called: ['append', 'records']
I/O originating inside quota_ledger during that run: NONE
with the real adapter, I/O originates in:
    [('open','quota_ledger.file_journal','__init__'),
     ('open','quota_ledger.file_journal','append'),
     ('open','quota_ledger.file_journal','records')]
```

Note the rejections produced **no** `append` — R4's durable half, observed at
runtime rather than asserted.

### 0.4 The swap, performed

```
$ diff -r base swap
39c39
<     return Ledger(quotas, FileJournal(ledger_path))
---
>     return Ledger(quotas, InMemoryJournal())

$ QUOTA_LEDGER_DIR=$PWD/swap ... pytest test_behavior.py -q
28 passed in 0.03s

ledger_lines() -> ['COMMIT acme 2 2', 'CLOSE acme 2']
file exists on disk -> False
```

One line, in the composition module, no domain file touched, whole shared
contract still green, and the filesystem provably untouched.

### 0.5 Verifying every self-reported limit

| `NOTES.md` claim | my run |
|---|---|
| `available`/`committed` raise `KeyError` on unknown tenant, `is_closed` returns `False` (`:125-131`) | `KeyError: 'nobody'`, `KeyError: 'nobody'`, `False` — exact |
| non-integer amounts flow into the ledger line (`:142-145`) | `reserve('acme', 2.5)` → accepted `r1`; line `COMMIT acme 2.5 2.5`; `committed == 2.5` — exact |
| a failed durable write leaves memory moved, R2 unenforced (`:136-141`) | with an `append` that raises `OSError`: `committed == 3`, `outstanding == []`, ledger empty — exact |
| every behavioral case runs twice, two file-specific cases and the import check excepted (`:93-100`) | `--collect-only`: 50 ids carry both `[file]` and `[memory]`; exactly three singletons, and they are the three named |

Four out of four reproduced verbatim. Nothing in the record was inflated.

### 0.6 Adversarial probe (my own, not from the packet)

```
append('A\nB'): FileJournal -> ['A', 'B']    InMemoryJournal -> ['A\nB']   DIVERGE
append(''):     FileJournal -> []            InMemoryJournal -> ['']       DIVERGE
append('  '):   FileJournal -> ['  ']        InMemoryJournal -> ['  ']     agree
```

and, reachable through the public API with no mutation at all:

```
QuotaLedger({'ac\nme': 10}, path); commit(reserve('ac\nme', 3))
ledger_lines() == ['COMMIT ac', 'me 3 3']
```

One accepted commit, two ledger lines. R2 and R5 broken. `FEATURE.md` places
no constraint on tenant names. No test in either suite and no instrument in the
packet detects this, and the record does not name it.

---

## 1. D1 — Bug detection: **3**

Anchor 2 is met on content, not shape. The cases assert literal ledger
transcripts — `AQ/tests/test_ledger.py:124-129` pins four interleaved
per-tenant running totals as exact strings, `:148-152` pins the `CLOSE` line,
`:215-220` pins a whole mixed-run transcript. Those are what kill the
durable-content mutants: M04 (stale total) fails
`test_running_totals_are_per_tenant_and_interleave` and
`test_close_writes_exactly_one_line_with_the_final_total`, in both wirings.

Anchor 3 is met twice, and I checked both against the packet's own columns:

* **Refusals.** `evidence_Q.md:50` records `guard_relaxation` at **0 of 3** for
  `corpus-whole`, `corpus-slice-res`, `corpus-slice-led`, `map-silent` and
  `map-checking` — the whole-view corpus structurally cannot reach the refusal
  class here (91% of its cases are refusal edges carrying no arguments,
  `evidence_Q.md:90-95`). The artifact's own rejection table at
  `AQ/tests/test_ledger.py:161-199` kills all three, and does it the hard way:
  it snapshots a five-tuple *including the durable lines* before and after, so
  it catches a relaxed guard by the state change it lets through, not merely by
  a missing reason string.
* **Ordering.** N01 reverses the order of `outstanding_ids()`. It SURVIVED
  every generated instrument (`evidence_Q.md:42`) and SURVIVED the shared suite
  in my run — and the artifact's own suite KILLS it, at
  `AQ/tests/test_ledger.py:100-105`
  (`test_outstanding_ids_stay_ascending_past_ten`) and `:86-92`. This is the
  most interesting fact on the card. The author wrote that case *because* the
  implementation leans on a language guarantee (`list(self._outstanding)`
  relying on dict insertion order, `AQ/quota_ledger/domain.py:128-129`) and
  said so at `NOTES.md:86-91`. A design decision produced a targeted case that
  is the only thing in the entire measured apparatus that catches the
  corresponding fault. Note this is a genuine kill, not a false positive:
  `FEATURE.md` line 29 requires `outstanding_ids()` to return ids *ascending*,
  so reversing them is a real violation that the harness's negative control
  happens not to be designed to punish.

Not 4. Anchor 4 requires the cases to be **derived from the model rather than
hand-written**. There is no model, no corpus, no generator and no spec artifact
anywhere in this tree — the five files are three production modules, a
composition module and one hand-written pytest file. The record does name a
fault class it cannot reach (`NOTES.md:142-145`, non-integer amounts, which I
confirmed reaches the ledger), so half of anchor 4 is satisfied; the provenance
half is not, and the ladder is cumulative.

## 2. D2 — Complexity: **2**

**I reject the owner's amendment.** Two reasons, and I want the second on the
record because it makes the first cost-free.

1. The amendment asks me to read the two mechanical columns as the "before and
   after" of a simplification. They are not: they are two independent
   implementations of one specification that never shared an ancestor. Anchor 3
   asks for *a simplification and its measured effect*; between two unrelated
   designs there is no simplification, only a difference. The card's own MF-020
   guard makes this explicit — "a D2 of 3 or more requires the judge to say
   *what got simpler and how the behavior survived it*" — and I cannot answer
   that question about a delta that no one performed.
2. Accepting it would not have helped this artifact anyway. On
   `evidence_Q.md:108-118` this column is **higher** on every structural figure
   that differs: 4 modules vs 1, 129 vs 122 production lines, 25 vs 20 public
   names, 2 vs 1 `io_imports`. The only figure moving the other way is
   `test_lines` (190 vs 252), which is not a complexity property of the design.
   So the amendment is one I can reject without it being a thumb on the scale.

Anchor 2 is met, and I measured it myself with an AST pass rather than trusting
the packet's `max_writers_of_one_attribute`:

```
_closed        writers = [__init__, close_tenant]
_committed     writers = [__init__, commit]
_issued        writers = [__init__, reserve]
_outstanding   writers = [__init__, commit, release, reserve]
_quota         writers = [__init__]
'available' stored as an attribute?: False
```

No god-state, no variable written from everywhere; the most-written piece of
state is the outstanding map, written by exactly the three commands whose
meaning is to add or remove a reservation. `available` is derived on demand
(`AQ/quota_ledger/domain.py:118-120`), which is why R1 is true by construction
and why "committing does not give the hold back" falls out of the arithmetic
instead of being maintained — the reasoning at
`AQ/quota_ledger/domain.py:87-104` and `AQ/NOTES.md:70-84` is a real property of
the code, not a story about it.

Is the four-module split accidental structure for a 129-line program? I decided
no. There is exactly one port, for the one genuinely external thing, and the
record explicitly declines the indirection it did not need
(`AQ/NOTES.md:53-55`: no port in front of the arithmetic, no repository
interface over the reservations dict, no service layer) — which I verified:
`domain.py` contains one `Protocol` and no other injected collaborator. The
structure buys something I could measure (§0.3, §0.4), so it is not decoration.

Anchor 3 fails cleanly: the artifact records **no figures at all** for its one
claimed simplification. It argues the derivation in prose and measures neither
side of it.

## 3. D3 — Modularity: **4**

The card's warning ("import topology is not modularity ... requires evidence
about what *calls* what at runtime") is why §0.3 and §0.4 exist rather than a
reading of import statements.

* Anchor 2 — the port is identifiable and carries a written contract:
  `AQ/quota_ledger/domain.py:22-43`.
* Anchor 3 — the domain does not import its I/O, and more importantly does not
  *perform* any: with a stub in the port slot, driving the entire command
  surface produced zero file opens from any `quota_ledger` module, and its only
  outbound calls were `append` and `records`. With the real adapter every
  `open` originated in `AQ/quota_ledger/file_journal.py:25-35` and nowhere else.
  The specific swap, named and then actually performed: replace
  `FileJournal(ledger_path)` with `InMemoryJournal()` at
  `AQ/quota_ledger/__init__.py:39`; `diff -r` shows that one line; 28/28 of the
  shared contract still passes; the ledger file is never created on disk.
* Anchor 4 — a driven port exercised by a real adapter *and* a fake with the
  same cases passing against both. `AQ/tests/test_ledger.py:26-36` is a
  two-value parametrized fixture and `--collect-only` confirms 50 of 53 ids
  carry both `[file]` and `[memory]`. This is not the weak version of that
  test: `AQ/tests/test_ledger.py:5-9` states, and the code obeys, that no case
  asserts merely that the two wirings agree — every case asserts a literal
  expected value. Under mutation each killing case failed in *both* wirings,
  which is the check that the fake is load-bearing rather than a second copy of
  the same blind spot.

`AQ/tests/test_ledger.py:260-270` is worth singling out: it parses `domain.py`
with `ast` and asserts the import set is exactly `{__future__, dataclasses,
typing}`. The artifact converts its own architectural claim into a check that
can fail. That is the right instinct, and it is why I trusted nothing else here
either.

**What tempers this and what a third pass should look at.** I falsified an
in-artifact claim: `AQ/quota_ledger/memory_journal.py:3-8` says the fake is "a
working implementation of the same port, obeying the same contract". It is not,
for two inputs the contract at `domain.py:30-39` explicitly admits — `'A\nB'`
comes back as two records from the file adapter and one from the fake, and `''`
comes back as zero records from the file adapter and one from the fake. The
port-contract cases at `AQ/tests/test_ledger.py:42-71` happen to be inputs both
satisfy. I still award 4, because the anchor asks for the same cases passing
against a real adapter and a fake and that is demonstrated at runtime rather
than asserted; a judge who reads the anchor as demanding a faithful double would
land on 3, and I would not call that wrong. This divergence is not academic —
see the reachable defect in §5.

## 4. D4 — Behavior preservation: **2**

There is no baseline and no refactor in this example, so I read "the behaviors
the baseline exhibited" as the rules the specification fixes, which is the only
reading that gives the dimension content here.

Anchor 2 is fully met and enumerated **by name**. `AQ/tests/test_ledger.py:175-199`
is R4 across nine distinct rejections, comparing a five-tuple snapshot that
includes `ledger_lines()` — so it catches a rejection that leaks a durable
write, which is the part most suites forget. `AQ/tests/test_ledger.py:202-226`
reads R1, R2, R3 and R5 off one concrete expected transcript. The shared
contract re-enumerates them independently at
`EVAL/examples/validation/ab/tests/test_behavior.py:239-281`. I ran both (53 and
28 green) and read the assertions to confirm they compare against literal
expected values rather than against the implementation's own output.

Anchor 3 fails on **provenance**, not on strength. Every check in this tree is
hand-written; there is no corpus, no TLC invariant, no model. The model-derived
instruments in the packet belong to the harness — they are applied *to* this
artifact, not shipped *by* it — and on this artifact they are notably weak
(`corpus-whole` 0 of 3 on refusals, 8.7% of cases executable,
`evidence_Q.md:82,90-95`). Crediting the artifact for an instrument someone else
pointed at it would be scoring the harness.

I record the tension plainly, because the card asks me to take the lower and say
why: I *did* demonstrate anchor 4's substance in §0.2 — eleven deliberate
behavior-breaking changes, all eleven caught, so this check is demonstrably
capable of failing and is not a suite that is green on broken code. But anchor 4
is defined as "3, **and** ...", and 3 is unmet. So 2. This is the dimension I
would most expect a second judge to disagree with, and the disagreement would be
about whether provenance or demonstrated capability governs the ladder.

## 5. D5 — Honesty: **3**

Anchor 2 is met **inside the artifact** and not only in the report, which is the
part of this anchor that usually fails. `AQ/tests/test_ledger.py:5-9` names the
blind spot of its own method — "two wirings of the same domain agree with each
other even when the domain is wrong" — and the suite is then written to avoid
it. `AQ/quota_ledger/file_journal.py:13-23` names the truncation decision and
the framing the adapter adds and strips. `AQ/quota_ledger/domain.py:73-75`
refuses at runtime to construct a rejection outside the declared six-reason
vocabulary.

Anchor 3 is met in substance, and I verified the refusal is warranted rather
than decorative. `AQ/NOTES.md:136-141` declines to claim R2 holds under a failed
durable write and names the exact hole; I built a journal whose `append` raises
and reproduced it — `committed('acme') == 3` in memory against an empty durable
ledger. That is the `unobservable`-over-false-clean doctrine applied to itself:
the easy sentence was "R2 holds by construction", and the artifact refused it
and was right to. `AQ/NOTES.md:142-145` likewise admits that non-integer amounts
flow into the ledger line, which I reproduced exactly
(`COMMIT acme 2.5 2.5`). `AQ/NOTES.md:102-123` records a conflict between the
feature's fixed constructor signature and its own structural commitment, and the
cost it paid, rather than smoothing it over.

I stop at 3 rather than 4, and take the lower as the card instructs, for two
reasons that are about evidence rather than tone:

1. **An in-artifact claim about its own reach is false as stated.**
   `AQ/quota_ledger/memory_journal.py:3-8` asserts the fake obeys "the same
   contract"; §0.6 shows it does not. Anchor 4 is the top of a scale that must
   be "impossible to reach by asserting more", and this is an assertion that
   reaches for credit the artifact has not earned. It is small, and it is
   exactly the shape of thing this dimension exists to catch.
2. **There is a reachable defect the record does not name.** A tenant name
   containing a newline makes one accepted `commit` emit two ledger lines
   (`['COMMIT ac', 'me 3 3']`), breaking R2 and R5 through the public API with
   no mutation applied. The record names four unspecified areas carefully and
   this is not among them; neither suite and no instrument in the packet reaches
   it. An artifact that enumerates its blind spots this well is judged against a
   higher bar for the one it missed.

Anchor 4's "unflattering result" is otherwise genuinely present, so a judge who
weighed the two points above as immaterial would reach 4. I did not, because
both are things I *measured*, and the difference between 3 and 4 on this
dimension should be decided by measurement.

---

## 6. Prose quality

The card requires me to say so if the writing tempted me. **It did.** This is
the best-argued artifact record I have read in this format: it explains *why*
`available` is derived, distinguishes derivation from deletion, pre-empts the
lexicographic-sort objection, and names a conflict it could have hidden. The
temptation was to score the reasoning. I did not: every score above rests on a
command I ran or a line I read, and the two places the writing is most
persuasive (§2 the simplification argument, §5 the honesty section) are exactly
the two places I scored *below* what the prose invites — D2 at 2 because no
figures were recorded, D5 at 3 because one confident sentence turned out to be
false when I tested it. Had this same code shipped with a two-line README, D1,
D3 and D4 would be identical, because none of them depends on a sentence.

## 7. What surprised me

1. **The artifact's own suite kills the negative control.** N01 is the row the
   packet uses to prove the generated instruments are not crying wolf — it must
   survive everything, and it does survive everything the packet measured, and
   the shared suite too. This artifact catches it, because it wrote a case
   specifically for the one place it relied on a language guarantee. A
   hand-written suite beating the model-derived corpus on an *ordering* fault is
   the opposite of what the corpus is for, and a reader comparing the mechanical
   block to this judgement should notice the disagreement.
2. **The `addition` column predicted nothing about detectability.** M08 and M10
   had to be *invented* rather than perturbed because this design has nowhere
   for a refund fault to live (`available` is derived, so there is no stored
   number to double-credit) — and both died anyway, in both wirings.
3. **The fake and the real adapter are not interchangeable**, in an artifact
   whose central architectural claim is that they are, and the gap is reachable
   from the public API through a tenant name.

## 8. Disclosures

* I opened **none** of the forbidden paths: nothing under
  `EVAL/specs/results/scorecards/`, nothing under `EVAL/specs/.history/`, not
  `arm_a/`, not `arm_b/`, not `EVAL/examples/validation/ab/README.md`, not
  `PREDICTIONS-HP.md`, not `seeded_faults.toml`, not `NEXT-EPIC.md`, and no other
  judge's output. I read exactly four things outside my own scratch work:
  `EVAL/references/eval_scorecard.md`, `EVAL/examples/validation/ab/FEATURE.md`,
  `EVAL/examples/validation/ab/tests/test_behavior.py`, and the artifact tree
  plus `evidence_Q.md`.
* **I did read one file I did not write and had not expected.** While setting up
  my mutation work I found
  `/private/tmp/.../scratchpad/mut/run.py` already present in the shared
  scratchpad, written by a concurrent process seconds after I had emptied that
  directory. I read it before realising it was not mine. It is a mutation
  driver: mutant find/replace definitions and a pytest invocation. It contains
  **no scores, no rationale, no conclusions and no arm labels**, so it did not
  tell me what anyone concluded — but it is plausibly another judge's harness,
  so I disclose it. I immediately moved my work to an isolated directory
  (`scratchpad/jQp2/`) and wrote my own driver; my mutant set had already been
  designed from `evidence_Q.md`'s catalogue table before I opened that file, and
  it differs from it (different M02, M03, M07 and M09 encodings, and I run the
  artifact's own suite as an instrument, which that script also does).
* **I have not learned and do not infer which prompt produced this artifact.** I
  note only that the packet's mechanical block labels the columns P and Q; I did
  not attempt to reason from the columns to the arms.
* **I modified nothing.** All mutation work ran on copies under
  `scratchpad/jQp2/`. Running pytest inside the artifact tree created
  `__pycache__` and `.pytest_cache` directories, which I deleted; I then
  re-verified the SHA-1 of all five source files and `NOTES.md` against the
  values I took before starting, and they are unchanged. `git status` in the
  evaluation repository shows only an untracked
  `specs/results/scorecards/hexagonal-prompting-rerun/` that I neither created
  nor opened.
