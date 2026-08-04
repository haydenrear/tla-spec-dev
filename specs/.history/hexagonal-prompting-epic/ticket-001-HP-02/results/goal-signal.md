# HP-02 — goal signal

**What this is.** HP-02's three declared `local_signal` runs, each classified as
exactly one of *moved as expected* / *moved less than expected* / *no measurable
movement* / *moved the wrong way*.

**What this is not.** The measurement. HP-06 decides all three goals, with two
judges blind to arm and to each other. This pilot is **n = 1, one feature, one
operator, one day, not blind, nobody judged it**, and both arms were run by the
agent that wrote the treatment. Every number below is advisory and none of it
touches HP-02's pass/fail, which is decided by the REQUIRED validation matrix.

**Read this before the numbers**, because it is the finding: the local signal
came back **mixed, and negative on two of the three goals**. The one that moved
as expected moved on a reading I made myself rather than on a judgement.

## What the pilot ran

| | |
|---|---|
| arm A | `examples/validation/ab/arm_a/PROMPT.md`, dispatched verbatim to one fresh agent |
| arm B | `examples/validation/ab/arm_b/PROMPT.md` with HP-02's Section 1 filled, same |
| feature | `examples/validation/ab/FEATURE.md`, unchanged, both arms |
| trees | `specs/tickets/HP-02/results/pilot/arm_a/`, `.../arm_b/` |
| catalogues | `.../pilot/catalogue_arm_a.toml`, `.../catalogue_arm_b.toml` — the HP-01 catalogue re-anchored per arm, integrity proven per arm (`pilot-catalogue-integrity.txt`) |
| kill runner | `.../pilot/run_pilot_kills.py`, output in `pilot-kill-table.txt` |
| structure | `structure-reading.txt` |

Both arms passed the shared behavioral suite unchanged, 28 passed. So this is an
A/B and not a comparison against an arm that ran out of budget.

---

## GOAL-hexagonal-in-fact — `contribution: direct`

**Expected effect:** *"This IS the intervention. Arm B scores D3 >= 3 where arm A
scores 1–2; if D3 does not separate, the prompt is decoration and the epic says
so."*

**Declared signal:** run the prompt against one small fixture and read the
produced structure; report it whichever way it comes out.

### What came out

| | arm A | arm B |
|---|---|---|
| production files | 1 | 5 |
| production lines | 120 | 274 |
| domain imports its I/O | **yes** — `from pathlib import Path` at `arm_a/quota_ledger.py:11`, `.open("a")` at `:118`, in the same class that holds the guards | **no** — `arm_b/quota_ledger/domain.py` imports `dataclasses`, `typing`, and `.ports`, and nothing else; no `Path`, no `open`, no handle |
| a declared driven port | none | `DurableLedger` (`Protocol`), `quota_ledger/ports.py:13`, two methods |
| a real adapter | n/a (inline) | `FileLedgerAdapter`, `adapters/file_adapter.py:9` |
| a fake | none | `InMemoryLedgerAdapter`, `adapters/memory_adapter.py:14` — a working in-memory implementation, not a call recorder |
| composition point | n/a | `quota_ledger/__init__.py:22` is the only module that imports an adapter |
| named swap | none stated | stated at `__init__.py:11-14` and `memory_adapter.py:4-6` |
| same cases against real and fake | none | `tests/test_domain_port_swap.py:65`, `tests/test_port_conformance.py` |

Against the card's D3 anchors, arm A satisfies **1 at most** (a boundary named
in prose, and the code does not follow it) and arm B has, on its face, the
artifacts anchor 3 and anchor 4 are written about.

**Classification: moved as expected.**

**Three things that classification is not.** (1) I am not a blind judge and I
wrote the treatment; the card requires two of them, blind to arm. (2) n = 1.
(3) Confound 1 in the sealed predictions applies at full strength and is worse
than "longer": arm B's prompt is 194 lines against arm A's 73, and its unique
content is **6.6×** arm A's. Nothing here separates "hexagonal guidance helped"
from "a longer, more specific ask helped".

---

## GOAL-simpler-same-behavior — `contribution: direct`

**Expected effect:** *"Arm B's descriptor shows lower complexity at equal
behavior; D2 separates from arm A."*

**Declared signal:** `analyze complexity` on the produced artifact, before and
after.

### The declared signal could not run, and that is filed, not worked around

`analyze complexity` measures a **TLA+ model**. Both arms produce **Python**, and
the A/B deliberately holds **one model for both arms**, so the only artifact the
scanner can read is byte-identical across arms and cannot separate them. There
is also no "before": both arms wrote new code from one feature file, and "before
and after" presupposes a refactor this A/B is not.

Filed as **HP-02-DF-01** with three suggested dispositions for the owner.
Evidence of the run that exists: `complexity-descriptor-shared-model.txt` — the
scanner over the shared model, the same output for both arms.

No proxy metric was substituted. A line count wearing the declared harness's
name is how a number acquires authority it never had, and the card's own D2 text
says a drop in a complexity number is not evidence on its own.

### The nearest honest reading, stated as what it is

On plain counts of parts — the only thing available without an instrument — arm
B is **larger**: 5 production files against 1, 274 production lines against 120,
one `Protocol` and two implementations where arm A has a method.

Arm B did make two real representation reductions, and they are the kind the
prompt asked for: it does not store `available` (it computes
`quota - held - committed`, `domain.py:73-74`), and it keeps no in-memory mirror
of the ledger (`ledger_lines()` reads through the port, `domain.py:85-86`) where
arm A carries `self._lines` alongside the file (`arm_a/quota_ledger.py:46,120`).
So arm B has **fewer pieces of state that can drift** and **more modules**.

**Classification: moved the wrong way** — on a substitute reading, in the
direction the `expected_effect` names, and **unmeasured on the declared
instrument**.

This reproduces HP-01's sealed **N01** exactly: *"ports, adapters, and an
inversion boundary are more parts, more indirection, and a larger descriptor,
not fewer."* HP-02 does not claim credit for that and did not tune anything
toward it.

---

## GOAL-catch-bugs — `contribution: guard`

**Expected effect:** *"Must not REDUCE bug detection. A prompt that produces
prettier code whose adapters catch less has failed."*

**Declared signal:** the HP-01 seeded catalogue against the arm-B artifact.

### The table, per class, per arm, per instrument

Two instruments, never merged. `suite` is the SHARED hand-written suite —
identical for both arms, so its row is a fact about the suite. `own` is the
arm's own tests, whatever the arm chose to write, and that is the row the guard
is actually about.

| class | A:suite | A:own | B:suite | B:own |
|---|---|---|---|---|
| guard_relaxation (M01–M03) | 3/3 | **1/3** | 3/3 | **0/3** |
| durable_content (M04, M05) | 2/2 | 2/2 | 2/2 | 2/2 |
| cross_aspect (M08) | 1/1 | 0/1 | 1/1 | 0/1 |
| output_oracle (M06) | 1/1 | 0/1 | 1/1 | 0/1 |
| wrong_value (M07, M10) | 2/2 | 0/2 | 2/2 | 0/2 |
| ordering (M09) | 1/1 | 1/1 | 1/1 | 1/1 |
| **total** | 10/10 | **4/10** | 10/10 | **3/10** |

### Reading it

**The shared suite is flat at 10/10 on both arms.** It reproduces HP-01's
reference measurement on two different programs. No separation, and none was
available: it is the same file run twice.

**Arm B's own tests caught one fewer than arm A's**, and it is M01 — the
zero-amount guard. Arm A asserts `reserve("acme", 0).status == "rejected"` on an
open tenant (`arm_a/test_quota_ledger.py:61`) and kills it. Arm B calls
`reserve(t, 0)` three times and never once on an open, known tenant: twice
inside rejection-*ordering* tests where an earlier guard fires first
(`test_acceptance_extra.py:30,44`), once inside the real-vs-fake scenario
(`test_domain_port_swap.py:48`). Under the mutant every one of those still
returns the reason the test asserts.

Arm B wrote **3.6× the test code** (222 lines, 11 tests, 3 files against 62
lines, 6 tests, 1 file) and caught one fault fewer.

**The `own` instrument fails its own positive control, on both arms.** M07 — the
blatant conservation break, seeded in nobody's gap precisely so that a table of
zeros can be told from a broken instrument — **survives both arms' own tests**.
By the catalogue's own doctrine (P05: *"if M07 survives, every other number in
the round is void"*), the `own` row is **not citeable as a kill measurement**.
What it does show is weaker and still worth saying: neither arm's self-authored
tests are an adequate instrument, and arm B's extra volume did not change that.

**Classification: moved the wrong way** — one cell, on an instrument that failed
its own positive control, with the `suite` row flat. Reported rather than
rounded to "flat", because the guard is the thing this ticket is supposed to be
honest about.

This is consistent with HP-01's sealed **N04**: the prompt changes the code and
the cases come from the model, so the prompt is not where D1 moves.

---

## The pilot found a hole in the prompt, and the prompt was changed after

This is the sharpest thing the pilot produced, and it is unflattering to the
treatment.

Arm B's real-vs-fake test is a **differential** assertion:

```python
assert scenario(fake_book) == scenario(real_book)   # test_domain_port_swap.py:71
```

Two wirings of the **same domain**. Every domain-logic fault moves both sides
identically, so this test **cannot fail** for any fault in the rules — including
the M01 it was in a position to catch. The artifact the prompt asked for, and
that the card's D3 anchor 4 is written about, is by construction blind to the
faults D1 is written about. That is not a defect in arm B's agent; it followed
the instruction as written.

**The prompt has been amended**, in both copies, with one sentence:

> **Each case asserts an expected value, not merely that the two agree** — two
> wirings of the same domain agree with each other even when the domain is
> wrong, so a test that only compares them can never fail for a reason you care
> about.

**The amendment is UNMEASURED, and the pilot above measured the text before
it.** The pilot was not re-run afterwards, deliberately: re-running a signal
after changing the thing until a better number appears is the pattern the
workflow forbids, and one more non-blind n = 1 run would not settle it anyway.
HP-06's A/B is the first measurement of the shipped text.

## Summary

| goal | contribution | expected | measured | classification |
|---|---|---|---|---|
| GOAL-hexagonal-in-fact | direct | arm B ≥ 3 where arm A is 1–2 | arm B has the anchor-3 and anchor-4 artifacts; arm A has neither | **moved as expected** (my reading, not a judgement; n = 1; length confound 6.4×) |
| GOAL-simpler-same-behavior | direct | arm B's descriptor lower at equal behavior | declared instrument cannot run (HP-02-DF-01); on parts, arm B is larger — 5 files / 274 lines vs 1 / 120 | **moved the wrong way** (substitute reading), **unmeasured** (declared instrument) |
| GOAL-catch-bugs | guard | must not reduce detection | shared suite 10/10 both arms; arm-own 4/10 A vs 3/10 B, and the arm-own positive control survives on both | **moved the wrong way** (one cell, on an instrument that failed its control) |

Two of three came back negative. That is the result, and per the epic plan it is
the kind of result the round is for: an epic that closes with only good news
about itself has not been measured.
