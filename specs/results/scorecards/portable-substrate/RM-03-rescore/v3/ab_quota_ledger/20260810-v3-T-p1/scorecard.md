# Scorecard — ab_quota_ledger, artifact `T`, judge pass 1

`run_id`: `20260810-v3-T-p1` · scorecard_version 3 · rubric `examples/validation/scorecards/rubric_v3_frozen.md` digest `sha256:546f90e21d1254e0` · served `sha256:e1cab7c513e9d6dd`

**You are scoring artifact `T`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. How to read it against your judgement is one of the numbered scoring rules below.

## The rubric you are scoring against

**This is the whole rubric, and it is reproduced here so the bar for a score sits in the same file as the score.** Do NOT go and read `references/eval_scorecard.md`. That file also carries reading rules and prior results about these same dimensions, and a judge who reads those is being handed conclusions about the instrument they are the instrument for.

### The scoring rules

1. **Score artifacts, never claims.** A summary saying "the adapters assert content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped at 1, mechanically, by the schema check.
3. **Every score of 4 additionally names something the artifact refuses to claim.** The top of every scale requires a stated limit. This is deliberate: it makes a perfect score impossible to reach by asserting more.
4. **Prose quality is never an input.** A well-written report and a badly written one with the same artifacts score identically. Say so in the rationale if the writing tempted you.
5. **Two judges, independently, blind to each other.** Any dimension where they differ by more than 1 is recorded as `contested` and adjudicated by a third pass that must cite new evidence, not re-read the same lines.
6. **Blind to arm.** Where an eval has arms (with-prompt vs without), judges do not learn which artifact came from which until after scoring.
7. **The mechanical block is recorded, never scored.** Kill counts, complexity figures, case counts, determinism, runtime. It sits beside the judgement so a reader can see when the two disagree — and a disagreement is a finding.
8. **Say what you ran.** *(New in version 2.)* Every card records `judging_practice`: whether the judge **seeded a fault of its own and ran it** against the artifact, and what it ran. Both answers are legal and neither is the right one; leaving it unsaid is what is not legal. **D4's anchor 4 is only awardable when it says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. This is the anchor's own text made checkable, not a new bar.
9. **A judge is served the card, never the rubric file.** *(New in version 3.)* The scaffolded `scorecard.md` carries the rubric a judge needs. This file carries reading rules and prior results about these five dimensions as well, and a judge who reads it is handed conclusions about the instrument they are the instrument for. Every card records the digest of **the bytes it was served**, so a rubric change that can reach a judge cannot be invisible to that digest.

**Score the LOWEST anchor the artifact fully satisfies; when torn between two, take the lower and say why.**

### Judging practice — REQUIRED, and it is a field on the card

**Did you seed a fault of your own and run it against this artifact, or did you score the evidence packet?** Both are legal. Neither is the right answer. What is not legal is leaving it unsaid.

Fill `judging_practice` in `scorecard.json`: `executed_own_faults` true or false, and `what_was_run` listing what you actually ran.

**D4's anchor 4 is only awardable when this says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. If you did not run one, the highest D4 you can support is 3 — say that the packet asserts it and you did not verify it.

### D1 — bug detection

*Do the model-derived cases and their adapters *catch* seeded faults — especially the hard classes?*

- **0** — Cases exist and pass; no seeded fault is caught. A suite that is green on broken code.
- **1** — Catches faults that change a value the projection already prints. Misses everything requiring a content assertion.
- **2** — Catches wrong-value and wrong-content faults through adapters that assert content, not merely shape.
- **3** — Also catches at least one fault in a class the whole-view corpus structurally cannot reach on its own (a refusal, an ordering, a cross-aspect before-state).
- **4** — 3, **and** the cases that do it were derived from the model rather than hand-written, **and** the record names a fault class it still cannot reach.

### D2 — complexity

*Is the design as simple as its behavior requires, and no simpler?*

Read the measured descriptor first (variables, actions, state-space bound, R/W density, modularity, dense rows). Then judge whether the numbers reflect essential behavior or accidental structure.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state, no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the before and after figures are both recorded.
- **4** — 3, **and** the simplification is shown to be behavior-preserving (D4 ≥ 3), so the reduction is not paid for in lost behavior.

> **A drop in a complexity number is not evidence on its own.** MF-020: a metric can improve because an edge was deleted. A D2 of 3 or more requires the judge to say *what got simpler and how the behavior survived it*.

### D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

### D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

### D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

> **Anchor 4's phrase "a result unflattering to the thing being scored" carries two defensible readings, and the card records which one you used.** Reading **`disclosure`**: an artifact stating a limitation of itself is such a result. Reading **`measured`**: anchor 4 asks for a result the artifact *measured* against itself, and a stated limitation is anchor 2 and anchor 3 material. **Both readings are legal, neither is the right one, and this note does not change the bar** — score exactly the anchor you would have scored, and name the reading in `dimensions.D5.anchor_reading`. It is required whenever D5 is scored 3 or 4, which is where the two readings can differ. Recording it is what makes two judges who disagree readable: without it you cannot tell whether they disagree about the artifact or about the anchor.

### Judging practice — your answer

**Executed own faults:** **true**

**What was run:**

- **Baseline, own suite.** Pristine copy of `artifact_T` in a scratch dir: `uv run --with pytest python -m pytest tests/test_ledger.py -q` → **53 passed** in 0.13s.
- **Baseline, shared suite.** `QUOTA_LEDGER_DIR=<scratch> QUOTA_LEDGER_IMPL=quota_ledger uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q` from the repo root → **28 passed** in 0.11s. The suite file was not edited.
- **Eight faults of my own**, each seeded into a fresh copy, both suites run, copy discarded:

  | fault | where | own suite | shared suite |
  |---|---|---|---|
  | `J1-guard-amount-not-positive` (`amount < 1` → `amount < 0`) | domain.py:141 | KILLED (4) | KILLED (2) |
  | `J2-durable-total-is-amount` (COMMIT prints the amount in the running-total slot) | domain.py:159 | KILLED (4) | KILLED (2) |
  | `J3-commit-keeps-the-hold` (commit no longer removes the reservation) | domain.py:156 | KILLED (10) | KILLED (5) |
  | `J4-file-adapter-keeps-blank-line` (`records` uses `split("\n")`) | file_journal.py:35 | KILLED (24) | KILLED (8) |
  | `J5-ids-lexicographic` (`list(...)` → `sorted(...)`) | domain.py:129 | KILLED (2) | **SURVIVED** |
  | `J6-fake-adapter-aliases-its-list` (`records` returns its own list) | memory_journal.py:22 | KILLED (1) | **SURVIVED** |
  | `J7-release-writes-a-line` (release appends to the journal) | domain.py:169 | KILLED (6) | KILLED (1) |
  | `J8-close-line-omits-total` (CLOSE prints `0`) | domain.py:181 | KILLED (4) | KILLED (2) |

  Eight of eight caught by the artifact's own cases; **two of eight caught only by them**.
- **Swap test (D3 anchor 3).** Wrote a third `Journal` implementation the artifact has never seen — a sqlite-backed `SqliteJournal` — substituted it for `FileJournal(ledger_path)` at `__init__.py:39`, replayed the long mixed transcript, asserted the same literal expected values. Passed; `domain.py` sha256 `fe9ebd5558cbcf7c` before and after, unchanged.
- **Runtime call evidence (D3 caveat).** Wrapped the port in a spy walking `sys._getframe(1)` on every `append`. The only runtime callers are `quota_ledger.domain.commit` and `quota_ledger.domain.close_tenant`.
- **Domain isolation (D3 anchor 3).** Loaded `quota_ledger/domain.py` via `importlib` outside its package and drove `Ledger` with a hand-rolled nine-line Journal → `['COMMIT acme 3 3']`, with `pathlib` and `quota_ledger.file_journal` both absent from `sys.modules`.
- **Package import probe.** `import quota_ledger.domain` *does* load `quota_ledger.file_journal`, `quota_ledger.memory_journal` and `pathlib`, via the adapter imports at `__init__.py:22-24`. Recorded as a finding under D3, not as a deduction.
- All work done on copies under the session scratchpad. Nothing in the repository was modified except this card directory; the artifact directory was read only.

## Your scores

### D1 — bug detection

**Score: 3**

**Citations:**

- `artifact_T/tests/test_ledger.py:108-114` — literal durable content asserted, not shape
- `artifact_T/tests/test_ledger.py:142-152` — the CLOSE transcript, exact strings
- `artifact_T/tests/test_ledger.py:161-199` — the refusal class: reason **and** full inertness including the journal
- `artifact_T/tests/test_ledger.py:100-105` — the ordering class, past `r10`
- `artifact_T/tests/test_ledger.py:1-12` — "My own tests": the cases that reach the hard classes are hand-written, in their own words
- `artifact_T/EVIDENCE.md:111-119` — `guard_relaxation`: corpus-whole 0 of 3, suite 3 of 3
- `artifact_T/EVIDENCE.md:263` — `positive: {deciding: [], green: false}`

**Refuses to claim:** _(not required below 4)_

**Rationale:**

Anchor 2 is met on **content**, and I verified it rather than reading it: the cases assert literal durable records (`ledger_lines() == ["COMMIT acme 3 3"]`, test_ledger.py:114), so my J2 (running total replaced by the reservation amount) and J8 (CLOSE total zeroed) both died, 4 cases each.

Anchor 3 is met twice over, by my own runs:

1. **Refusal class.** `test_a_rejection_names_its_reason_and_changes_nothing` (test_ledger.py:161-199) asserts the reason *and* inertness across every query including the journal, and killed my J1 guard relaxation. The packet independently records that the whole-view corpus reaches **0 of 3** guard_relaxation faults while the class is reachable at all (EVIDENCE.md:111-119) — exactly the anchor's "class the whole-view corpus structurally cannot reach on its own".
2. **Ordering class.** `test_outstanding_ids_stay_ascending_past_ten` (test_ledger.py:100-105) killed my J5 (`list` → `sorted`, lexicographic) while the shared behavioral suite **SURVIVED** it — an ordering fault caught only by this artifact's own cases.

I refused anchor 4 on **both** of its extra legs. *First leg:* the cases that reach the hard classes are hand-written and say so on line 1 of the file; the model-derived corpora are byte-identical across all three artifacts (EVIDENCE.md:53-56), so crediting them here would score the instrument, not the artifact. *Second leg:* even reading the corpora as the artifact's cases, the record's own control coverage reports the positive polarity with no deciding control and `green: false` (EVIDENCE.md:263), and the packet's own rule is that a number under a red control is a floor. Torn between 3 and 4 only under the corpus reading; took the lower.

**Prose tempted me here** — NOTES.md is unusually well argued and every test carries a docstring that pre-explains it, which reads like coverage. I ignored the prose and scored the eight faults I ran.

### D2 — complexity

**Score: 2**

**Citations:**

- `artifact_T/quota_ledger/domain.py:87-104` — three written pieces of state, one writer's worth of meaning each
- `artifact_T/quota_ledger/domain.py:118-120` — `available` derived, not stored
- `artifact_T/quota_ledger/domain.py:146-148`, `:156-158`, `:180-181` — the actual writers, checked against source rather than docstring
- `artifact_T/NOTES.md:53-56` — refuses to indirect anything else
- `artifact_T/NOTES.md:68-84` — the simplification argued
- `artifact_T/EVIDENCE.md:324-342` — the mechanical block (read first, **not** scored)

**Refuses to claim:** _(not required below 4)_

**Rationale:**

I read the measured descriptor first and then went to the code; the two agree on anchor 2. Every written variable has one writer's worth of meaning, and I checked each against the source rather than the docstring claiming it: `_committed` only in `commit` (domain.py:158), `_closed` only in `close_tenant` (domain.py:180), `_issued` only in `reserve` and only after all four guards pass (domain.py:146), `_outstanding` by reserve/commit/release. No god-state, nothing written from everywhere, `max_depth` 1. The relationship between figures and design is *argued*, not merely reported (domain.py:118-120 with NOTES.md:68-84), and the artifact explicitly declines further indirection (NOTES.md:53-56).

It stops there. **Anchor 3 requires "the before and after figures are both recorded", and no before/after figure exists for this artifact.** Two simplifications are argued in prose — deriving `available`, and a factory instead of a nine-method delegating class (NOTES.md:118-123) — and neither carries the complexity of the design it replaced. The mechanical block is a cross-**artifact** column, not a before/after of a change made to this one; the packet itself says one column cannot reach anchor 3 (EVIDENCE.md:4-5), and three different artifacts are not one artifact measured twice. I can satisfy the caveat's *narrative* half (what got simpler: `available` derived, three writers avoided; how behavior survived: my J3 mutant, which makes commit keep the hold, killed 10 cases) but not the anchor's literal requirement. Torn between 2 and 3, took the lower.

**Rule 7 tempted me twice and I refused both times.** On the mechanical figures this artifact is the *largest* of the three (4 modules, 202 code_lines, 23 callables, 25 public_surface against 1/78/11/11) — an invitation to mark it down. It is also the only one to push branching out of its effectful module (`branch_points_in_effectful_modules` 1 vs 10 and 10) — an invitation to mark it up. Neither figure is a score and I converted neither.

### D3 — modularity

**Score: 4**

**Citations:**

- `artifact_T/quota_ledger/domain.py:22-43` — the `Journal` port, contract written on the Protocol
- `artifact_T/quota_ledger/domain.py:159`, `:181` — the only two outward calls
- `artifact_T/quota_ledger/__init__.py:37-39` — the composition point, and the one line the swap touches
- `artifact_T/quota_ledger/memory_journal.py:14-22` — a working second implementation, not a mock
- `artifact_T/quota_ledger/file_journal.py:25-35` — the real adapter, sole owner of paths/encodings/newlines
- `artifact_T/tests/test_ledger.py:26-36` — one fixture parametrized over real and fake
- `artifact_T/tests/test_ledger.py:42-71` — the port contract asserted against both
- `artifact_T/tests/test_ledger.py:260-270` — the artifact's own import check (see the nuance below)

**Refuses to claim:** **That the port isolates the record *format*.** NOTES.md:57-66 states plainly that `COMMIT <tenant> <amount> <total>` is behavior, so the two f-strings live in the domain (domain.py:159,181) and the port carries a finished string — a change of line format is a *domain* change, not an adapter change, and the boundary is deliberately not drawn where a naive reading of ports-and-adapters would draw it. It likewise refuses to claim anything else is indirected: "no port in front of the arithmetic, no repository interface over the reservations dict, no service layer" (NOTES.md:53-56).

**Rationale:**

The caveat says import topology is not modularity and a 3+ needs **runtime call** evidence, so I got runtime call evidence instead of reading the import test.

1. I loaded `domain.py` in isolation with `importlib`, outside its package, handed the `Ledger` a nine-line Journal of my own, and drove reserve/commit: it produced `['COMMIT acme 3 3']` with `pathlib` and `quota_ledger.file_journal` both absent from `sys.modules`. The domain runs to completion with no adapter in the process.
2. I **named and then performed** the specific swap anchor 3 asks for: a sqlite-backed `SqliteJournal` the artifact has never seen, substituted at `__init__.py:39`, identical expected values on the long transcript, `domain.py` sha256 byte-identical before and after.
3. Runtime callers of the port, captured by a spy frame walk, are exactly `quota_ledger.domain.commit` and `quota_ledger.domain.close_tenant` and nothing else — what the caveat asks for, and what an import graph could not have told me.

Anchor 4 is met and I did not take it on the artifact's word. One fixture over `FileJournal` and `InMemoryJournal` (test_ledger.py:26-36), 53 passing from one case list; the port contract asserted against both including the caller-owns-the-list clause (test_ledger.py:42-71). I proved **both wirings actually execute** rather than one silently shadowing the other, by seeding an adapter-local fault into each: J4 (file only) killed 24 cases, J6 (memory only) killed exactly 1. Cases assert literal values, never that the two wirings agree (test_ledger.py:124-129) — which matters, because two wirings of the same domain agree with each other even when the domain is wrong.

**A nuance that did not change the score but belongs on the record:** importing `quota_ledger.domain` *through the package* does load `file_journal`, `memory_journal` and `pathlib`, because `__init__.py:22-24` imports both adapters at the composition point. The artifact's own boundary test (test_ledger.py:260-270) parses `domain.py`'s import statements only and would still pass in that world. The module-level claim is literally true; the package-level consequence is undisclosed. Anchor 3 asks about the domain, which I ran standalone, so this stands as a finding rather than a deduction.

### D4 — behavior preservation

**Score: 2**

**Citations:**

- `artifact_T/EVIDENCE.md:59-63` — the shared suite, byte-identical for every artifact: the baseline enumeration
- `artifact_T/NOTES.md:16-28` — the invocation, which I ran (28 passed)
- `artifact_T/tests/test_ledger.py:202-226` — R1/R2/R3/R5 off one concrete transcript
- `artifact_T/tests/test_ledger.py:175-199` — R4 including the durable side
- `artifact_T/tests/test_ledger.py:1-12` — every case in scope is hand-written
- `artifact_T/EVIDENCE.md:111-119` — corpus-whole 0 of 3 on guard_relaxation, suite 3 of 3
- `artifact_T/EVIDENCE.md:263` — positive polarity: no deciding control, `green: false`
- `artifact_T/EVIDENCE.md:282-316` — M07 SURVIVED on all three port-bound instruments, 294 accepting `Reserve` cases each

**Refuses to claim:** _(not required below 4)_

**Rationale:**

Anchor 2 is met and I confirmed it by running: the shared behavioral suite is the baseline enumeration (EVIDENCE.md:59-63) and passes **28/28** here. The artifact maps its own cases to numbered requirements and reads them off one concrete transcript rather than a shape check (test_ledger.py:202-226, :175-199).

**This is the dimension where my judgement sits closest to the boundary**, so the reasoning in full. Anchor 3 wants the check to be model-derived rather than only hand-written. Inside this artifact's declared scope there is **no model-derived check at all** — every case in `tests/` is hand-written and the file's first line says so. The corpora do exist in the record and ran clean on unmutated code, so a judge could read "the check" as including the evaluator's corpus and score 3. I refused, for two independent reasons:

1. Those corpora are byte-identical across all three artifacts (EVIDENCE.md:53-56, `cases.py` sha1 recorded). They are *the instrument*, not this artifact's check; a clean run of them is evidence about observability of the code, not about a check the artifact carries.
2. **Decisively:** the corpus is not currently trustworthy as a preservation check *on this artifact*. The record's own control coverage reports the positive polarity with no deciding control, `green: false` (EVIDENCE.md:263), and the port-binding block shows the declared positive control **M07 SURVIVING on all three port-bound instruments while each executed 294 accepting `Reserve` cases** (EVIDENCE.md:282-316). An instrument that misses a wrong-hold fault with 294 relevant cases executed cannot certify that behavior was preserved. The packet's own rule: a number under a red control is a floor.

On top of that, the model-derived whole-view corpus is strictly **weaker** than the hand-written suite on a whole class here — guard_relaxation 0 of 3 versus 3 of 3 (EVIDENCE.md:111-119). Torn between 2 and 3; took the lower.

Note the consequence, because a reader should see it: `executed_own_faults` is **true** and all eight faults I seeded were caught — anchor 4's *substance* ("the check is demonstrated to be capable of failing") is satisfied in fact, and I demonstrated it myself — but anchor 4 is nested under anchor 3 and so is unreachable from a 2. I did not lift D4 to 3 to unlock it; that would be scoring backwards from the answer I wanted.

### D5 — honesty

**Score: 4**

**Citations:**

- `artifact_T/NOTES.md:125-147` — four numbered unspecified-behavior interpretations
- `artifact_T/NOTES.md:136-141` — "the one place I can name where R2 is not enforced by construction"
- `artifact_T/NOTES.md:149-157` — discloses its own reading discipline, including a file it declined to open that was *not* on the list
- `artifact_T/quota_ledger/domain.py:1-11` — the limits in the code, not only in a report
- `artifact_T/quota_ledger/file_journal.py:16-22` — truncation stated as a decision
- `artifact_T/EVIDENCE.md:263` — `positive: deciding [], green: false` printed instead of a kill-table headline
- `artifact_T/EVIDENCE.md:282-316` — the artifact's own port binding recorded failing a control it must pass
- `artifact_T/EVIDENCE.md:168` — the **fake** binding SURVIVED M09 where the **real** binding KILLED it
- `artifact_T/EVIDENCE.md:219-234` — `decides_nothing: true`, with a written retirement reason rather than a quiet deletion

**Refuses to claim:** **That R2 — every commit has a durable record — is enforced by construction.** NOTES.md:136-141 names the failed-durable-write window it did not close: `commit` and `close_tenant` update memory *then* append, so a raising append would leave memory moved with no durable record, and the artifact declined to invent a rollback or write-ahead ordering the feature does not specify. It likewise refuses to claim non-integer amounts are handled (NOTES.md:142-145) or any reopen-and-resume behavior (NOTES.md:132-135).

**Anchor reading: `measured`**

**Rationale:**

Anchor 2 is met **in the artifact**, not only in a report: the limits are written into the code a reader will actually open (domain.py:1-11; file_journal.py:16-22), alongside four numbered interpretations at NOTES.md:125-147.

Anchor 3 is met in the strong sense the anchor means — the artifact declines to certify what it did not build. Asked to make R2 hold, it names the exact window where R2 is *not* enforced rather than reporting R2 clean (NOTES.md:136-141). Three further refusals sit beside it: no invented unknown-tenant query result, no invented reopen/resume, no type check that would have become a seventh rejection reason against a vocabulary fixed at six. The record's instrument side refuses in the same register, with `decides_nothing: true` on the retired control and a written reason rather than a deletion (EVIDENCE.md:219-234).

Anchor 4 is met **under both readings the card names**, which is why the score is stable and worth stating. I scored under the stricter `measured` reading: the record contains results measured against this artifact that are unflattering to it — M07 SURVIVED on `corpus-action-bound`, `corpus-port-swap:fake` and `corpus-port-swap:real`, each having executed 294 accepting `Reserve` cases (EVIDENCE.md:282-316), and the coverage line prints `green: false` rather than a headline (EVIDENCE.md:263). Sharper still, and directly against the artifact's proudest claim: at EVIDENCE.md:168 the **fake** binding SURVIVED M09 where the **real** binding KILLED it — the second implementation the artifact offers as proof that its port is a port is measured missing an ordering fault the real one catches. Under the `disclosure` reading the score is also 4, carried by NOTES.md:136-141 alone. Since the anchor is satisfied under either reading, my number does not depend on which reading a second judge picks — only my citations do.

**Prose tempted me hardest here.** NOTES.md is candid in a voice easy to mistake for evidence. I checked each disclosure against code — the truncate at file_journal.py:27 is real, the missing type check is real (`amount < 1` at domain.py:141 accepts `2.5`), and the R2 window is real (domain.py:157-159 mutates `_committed` before the append) — and scored the checked facts, not the candor.

## Verdict

A genuine ports-and-adapters build whose boundary I verified by execution rather than by import graph — I ran the domain standalone with no adapter in the process and swapped in a sqlite journal I wrote myself with `domain.py` byte-unchanged (D3=4) — but every check it carries is hand-written, no before/after complexity figure exists for either simplification it argues, and the model-derived corpora that would lift D2 and D4 sit under a positive control the record itself reports as not green, so treat the corpus columns as a floor and read D2=2 and D4=2 as "unproven by a model-derived check", not as "behavior lost".

## Disclosures

**Nothing I was not meant to see.** I did not open `references/eval_scorecard.md`, `examples/validation/scorecards/rubric_v3_frozen.md`, any other rubric file, anything under `specs/results/scorecards/` outside `artifact_T` and this card directory, any `*-EPIC.md`, `NEXT-EPIC.md`, `references/portable_scorecard.md`, any `UNBLINDING.md`, or any other judge's card. I did not learn which arm `T` is, and I did not look. Note that EVIDENCE.md itself quotes `references/eval_scorecard.md` rule 7 at its line 9 and cites `examples/validation/ab/eval/controls.toml` at line 233; I read those quotations because they are inside the artifact I was told to read every file of, and I did not follow either pointer.

**What I ran that changed nothing in the tree.** All eight seeded faults, the swap test, the spy, and the isolation probe were executed on copies under the session scratchpad, then discarded. I ran the shared behavioral suite from the repo root with `QUOTA_LEDGER_DIR` pointed at a scratch copy; the suite file was not edited. The only files I modified are `scorecard.md` and `scorecard.json` in this directory. I did **not** re-run the artifact's suite as my evidence for anything — every score above rests on faults I introduced or on code I read.

### What I rejected

- **D1 anchor 4, twice.** Once because the cases reaching the hard classes are hand-written (test_ledger.py:1); once because even on the reading that credits the shared corpora, the record's own positive control is not green (EVIDENCE.md:263) and the packet's own rule makes those numbers a floor.
- **D2 anchor 3.** Two simplifications are argued well in prose and neither has a before figure. The cross-artifact mechanical column is not a before/after of *this* artifact, and EVIDENCE.md:4-5 concedes as much. I refused to accept a comparison across three different artifacts as one artifact measured twice.
- **D2, the mechanical block in both directions.** T is the biggest artifact on modules/lines/callables/public surface, and simultaneously the only one that keeps branching out of its effectful module. Both were live temptations. Rule 7 forbids converting either into a score.
- **D4 anchor 3, and with it a reachable anchor 4.** I had `executed_own_faults: true` and 8/8 kills in hand, which is exactly what anchor 4 describes, and anchor 4 is nested under an anchor 3 I judge unmet. Taking 3 on the corpus reading would have handed me a 4. I did not.
- **The artifact's own import test as D3 evidence** (test_ledger.py:260-270). It parses import statements, which is the thing the D3 caveat says is not modularity. I replaced it with a standalone `importlib` load and a runtime spy, and in doing so found that the *package* does drag `pathlib` and the file adapter in — a gap the artifact's test cannot see.
- **Scoring D3 down for that package-level import.** Tempting, but anchor 3 is about the domain, and I ran the domain with no adapter in the process. Recorded as a finding instead.

### Ambiguous or unanswerable in the card

1. **"Score the LOWEST anchor the artifact fully satisfies" is literally wrong as written.** An artifact satisfying 0 through 4 would score 0. I read it as: credit no anchor unless fully satisfied, and when torn between two, take the lower — which is what the following sentence and `how_to_fill[0]` actually say. Worth fixing, because a judge reading it literally would score every artifact 0.
2. **The card never says whether "the artifact" means the author's deliverable or the whole scored directory,** and `EVIDENCE.md` — an evaluator-produced packet — sits inside the declared scope. This decides D1 (are the shared corpora "the cases"?), D4 (is the corpus "the check"?) and D5 anchor 4 under the `measured` reading (are the packet's measurements "the record"?). I resolved it consistently: the corpora are the *instrument*, not the artifact's own cases or checks, and I said so in each rationale — but a second judge resolving it the other way would land at D1=4 and D4=3 with the same evidence, and the card gives no way to tell that apart from a disagreement about the artifact. This is a bigger source of judge divergence here than the D5 anchor-reading ambiguity the card *does* instrument.
3. **D4's anchor nesting makes `judging_practice` partly decorative.** Rule 8 exists so that anchor 4 requires a judge to run something. I ran eight faults, all caught, and still cannot award anchor 4 because anchor 3's model-derived leg fails independently. The rule buys nothing when the artifact ships no model-derived check — the judge's own execution is discarded by the nesting.
4. **D2's anchor 3 is unreachable for any artifact built once.** "A simplification was made and its effect measured — before and after figures both recorded" presupposes a refactor with a measured predecessor. A greenfield artifact that is simple from the first commit is structurally capped at 2, no matter how well its simplicity is argued. That is a property of the anchor, not of this artifact, and it means D2 here is measuring build history rather than complexity.
5. **The card I was served is not the rubric now in the tree.** The validator reports `SERVED-DRIFT` on this card: I was served `sha256:e1cab7c513e9d6dd` and the tree now serves `sha256:5945e264e193ca06` (and `RUBRIC-DRIFT`, scaffolded `546f90e21d1254e0` vs current `497c16ca85adeb4a`). This is rule 9's digest doing exactly its job, so I am recording it and changing nothing: I scored the bytes I was given, and the checker's own message says a filled card is evidence and is not edited. Every score above should be read against `e1cab7c513e9d6dd`, not against whatever the current rubric says. Neither line is counted as a problem; my card checks with **0 problems**.
6. **Incidental, from the validator, not from reading:** running `check` over the whole `v3` directory printed diagnostics for a sibling card `20260810-v3-T-p2`, from which I learned that a second pass on this same artifact exists and is currently `status: filled` with all five scores `None`. I did not open it and I do not know its judgement. Flagging only because rule 5's independence assumes two judges, and one of the two is not yet scored.
7. **`mechanical.json` beside this card is empty** — every figure block is `{}` and `commit` is `""` (mechanical.json:6-16). The card's own section says that file "holds kill counts, complexity figures, case counts, determinism and runtime". It holds none. I used EVIDENCE.md's mechanical block instead, which is where those figures actually are. I did not edit `mechanical.json`, as it is not mine to fill.
