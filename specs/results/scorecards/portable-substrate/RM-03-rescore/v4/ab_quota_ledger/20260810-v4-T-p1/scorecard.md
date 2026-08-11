# Scorecard — ab_quota_ledger, artifact `T`, judge pass 1

`run_id`: `20260810-v4-T-p1` · scorecard_version 4 · rubric `references/eval_scorecard.md` digest `sha256:1c5f60dab75f9a79` · served `sha256:9157db7edd640c79`

**You are scoring artifact `T`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. How to read it against your judgement is one of the numbered scoring rules below.

## The rubric you are scoring against

**This is the whole rubric, and it is reproduced here so the bar for a score sits in the same file as the score.** Do NOT go and read `references/eval_scorecard.md`. That file also carries reading rules and prior results about these same dimensions, and a judge who reads those is being handed conclusions about the instrument they are the instrument for.

### The scoring rules

1. **Score artifacts, never claims.** A summary saying "the adapters assert content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped at 1, mechanically, by the schema check.
3. **A score at the top of its scale additionally names something the artifact refuses to claim.** The top of every scale requires a stated limit. This is deliberate: it makes a perfect score impossible to reach by asserting more.
4. **Prose quality is never an input.** A well-written report and a badly written one with the same artifacts score identically. Say so in the rationale if the writing tempted you.
5. **Two judges, independently, blind to each other.** Any dimension where they differ by more than 1 is recorded as `contested` and adjudicated by a third pass that must cite new evidence, not re-read the same lines.
6. **Blind to arm.** Where an eval has arms (with-prompt vs without), judges do not learn which artifact came from which until after scoring.
7. **The mechanical block is recorded, never scored.** Kill counts, complexity figures, case counts, determinism, runtime. It sits beside the judgement so a reader can see when the two disagree — and a disagreement is a finding.
8. **Say what you ran.** *(New in version 2.)* Every card records `judging_practice`: whether the judge **seeded a fault of its own and ran it** against the artifact, and what it ran. Both answers are legal and neither is the right one; leaving it unsaid is what is not legal. From version 4 no anchor is gated on it and it is still required, because what a judge did is a variable in what a judge reports and a variable nothing records is a variable nobody can subtract.
9. **A judge is served the card, never the rubric file.** *(New in version 3.)* The scaffolded `scorecard.md` carries the rubric a judge needs. This file carries reading rules and prior results about these dimensions as well, and a judge who reads it is handed conclusions about the instrument they are the instrument for. Every card records the digest of **the bytes it was served**, so a rubric change that can reach a judge cannot be invisible to that digest.
10. **Answer every recorded note.** *(New in version 4.)* N-D1, N-D4 and N-D5 take no score and are required on every filled card. An empty note is not a legal card; *"I could not tell, and here is what I looked at"* is.

**Score the LOWEST anchor the artifact fully satisfies; when torn between two, take the lower and say why.**

### Judging practice — REQUIRED, and it is a field on the card

**Did you seed a fault of your own and run it against this artifact, or did you score the evidence packet?** Both are legal. Neither is the right answer. What is not legal is leaving it unsaid.

Fill `judging_practice` in `scorecard.json`: `executed_own_faults` true or false, and `what_was_run` listing what you actually ran.

**No anchor is gated on your answer.** The anchor that was is a recorded note now. Say what you ran because it is the variable that moves scores, not because a rung depends on it.

### D2 — complexity

*Is the design as simple as its behavior requires, and no simpler?*

Diff the two trees yourself and decide whether one fact is stored twice. A measured complexity descriptor may be read where one exists and it decides nothing: on the only simplification this project has ever measured, 19 of 21 axes were byte-identical and one moved the wrong way while eight judges found the removal independently.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state, no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the before and after figures are both recorded.

> **A drop in a complexity number is not evidence on its own.** MF-020: a metric can improve because an edge was deleted. A D2 of 3 requires the judge to say *what got simpler and how the behavior survived it*.

### D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

## The recorded notes — REQUIRED, and they take no score

**Answer each in your own words and cite `file:line` as you would for a score.** There is no 0–4 here and there is no anchor ladder: these questions were scored for three versions and the numbers were measured not to mean the same thing twice. *"I could not tell, and here is what I looked at"* is a correct answer; an empty note is not.

### N-D1 — bug detection

What did the cases catch, and what class did they demonstrably miss? Name the fault you seeded if you seeded one.

### N-D4 — behavior preservation

Which behaviors of the baseline did you enumerate, and is each shown still to hold? If there is no baseline, say so — that is the answer, not a gap in the note.

### N-D5 — honesty

Does the artifact refuse rather than falsely certify, and does it name what it cannot see? Point at the refusal, or at its absence.

### Judging practice — your answer

**Executed own faults:** **true**

**What was run:**

- Copied `artifact_T` to a scratch directory. Every fault below was seeded there, run, and reverted; the repository tree was never written to (`git status --porcelain` shows only pre-existing modifications, none of them mine).
- Baseline: `uv run --with pytest python -m pytest tests/test_ledger.py -q` in the scratch copy — **53 passed** (matches `NOTES.md:27-28`).
- Baseline: the shared suite, `QUOTA_LEDGER_DIR=<scratch> QUOTA_LEDGER_IMPL=quota_ledger uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q` — **28 passed** (matches `NOTES.md:27`). Run with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` so nothing was written into the worktree.
- **SEEDED FAULT A** (adapter-localized): `FileJournal.records()` returns the lines reversed. → 6 failed / 47 passed, and *every* failure was a `[file]` parametrization; zero `[memory]` cases noticed. Reverted; 53 passed again.
- **SEEDED FAULT B** (domain, durable content): `Ledger.commit` journals the reservation amount in place of the running total. → 4 failed, symmetric across `[file]` and `[memory]`. Reverted.
- **SEEDED FAULT C** (boundary only, zero behavioral change): added `from .file_journal import FileJournal` to `domain.py` and bound it to an unused attribute. → exactly 1 failed, `test_the_domain_module_imports_no_adapter_and_nothing_that_does_io`; 52 passed. Reverted.
- **EXECUTED SWAP** (D3 anchor 3): replaced `FileJournal(ledger_path)` with `InMemoryJournal()` at `__init__.py:39`. → shared suite **28 passed**, no ledger file created anywhere, `domain.py` md5 unchanged at `2818df20c2f62c4ac480be73621fbb96`. Reverted.
- **PROBE D** (miss): `QuotaLedger({'acme':10}, path).reserve('acme', 2.5)` is accepted, commits, and writes `COMMIT acme 2.5 2.5`; `available` left at 7.5.
- **PROBE E** (miss): drove `Ledger` with a `Journal` whose `append` raises `OSError` — commit propagated the error with `committed('acme') == 4`, outstanding empty, zero durable records.
- **PROBE F** (miss, undisclosed by the artifact): under `python -O` the assert at `domain.py:74` is stripped and `Result.rejected('not_a_real_reason')` returns a rejection outside the six-word vocabulary.
- Collection counts: `pytest --collect-only` — 16 `[file]` and 16 `[memory]` node ids plus 9 parametrized rejection cases per wiring and 3 unparametrized, i.e. **25 identical cases run against each implementation**.

## Your scores

### D2 — complexity

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:118-120` — `available` derived, never stored
- `.../quota_ledger/domain.py:146-149` — `_issued` written only by `reserve`, only after every guard
- `.../quota_ledger/domain.py:156-158` — `commit` is the only writer of `_committed`
- `.../quota_ledger/domain.py:180-181` — `close_tenant` is the only writer of `_closed`
- `.../quota_ledger/domain.py:186-191` — one place knows which reservations belong to a tenant
- `.../quota_ledger/domain.py:48-57` and `.../quota_ledger/domain.py:74` — the reason vocabulary, stored twice, kept by an assert
- `.../EVIDENCE.md:324-342` — the mechanical block: three artifacts at one instant, not one artifact at two
- `.../NOTES.md:70-84` — the derived-`available` argument

**Refuses to claim** (required and non-null for a score of 3):

The artifact refuses to claim its durable side is atomic. `NOTES.md:136-141` states that `commit` and `close_tenant` move memory and *then* append, that a raising append would leave memory moved with no durable record, and calls this "the one place I can name where R2 is not enforced by construction." It declines to add rollback machinery rather than claim safety it does not have — a complexity refused, not a simplification measured.

**Rationale:**

I diffed the tree myself rather than reading a figure. Every piece of written state has a disjoint, nameable writer: `_committed` only in `commit` (`domain.py:156-158`), `_closed` only in `close_tenant` (`domain.py:180-181`), `_issued` only in `reserve` and only after all four guards pass (`domain.py:146-149`), `_quota` never after `__init__`. `_outstanding` has three writers — add in reserve, remove in commit, remove in release — but each write means one thing, and the tenant→reservation relation is looked up in exactly one place (`domain.py:186-191`). `available` is not stored at all (`domain.py:118-120`), so conservation cannot drift and `commit` needs no code to keep it. No god-state, no variable written from everywhere: that is anchor 2, decided on the code.

**I refused anchor 3.** It requires a simplification whose effect was *measured*, before and after figures both recorded, and no before tree exists. The mechanical block (`EVIDENCE.md:324-342`) compares three different artifacts at one instant, and on it this artifact is the **largest** of the three (4 modules vs 1; 202 `code_lines` vs 151 and 78; 25 `public_surface` vs 20 and 11). `NOTES.md:70-84` argues the derived-`available` decision in exactly the shape the caveat demands — what got simpler and how the behavior survived — but argues it against a counterfactual that was never built, and an unbuilt alternative is not a before figure.

I was also tempted **down** to anchor 1, whose text ("measured and reported; no relationship between the figures and the design is argued") is literally true here: nothing in `NOTES.md` or the code ever cites a complexity figure. I kept 2 because anchor 2 asks about the design, not about whether the artifact argued anything, and the design is the thing I can read.

One near-miss on "one fact stored twice": the six rejection reasons live both in `REJECTION_REASONS` (`domain.py:48-57`) and as inline literals at each call site, guarded only by an `assert` (`domain.py:74`) that I showed vanishes under `python -O`. A duplication with a weak keeper — not enough to pull the score to 1.

*Prose quality was not an input.* `NOTES.md` is unusually well argued and that is precisely why I checked its two strongest claims by running them instead of reading them. The writing did tempt me.

### D3 — modularity

**Score:** **4**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `.../quota_ledger/domain.py:13-16` — the domain's entire import list
- `.../quota_ledger/domain.py:22-43` — the `Journal` port and its written contract
- `.../quota_ledger/domain.py:106-114` — constructor injection; the domain never builds one
- `.../quota_ledger/domain.py:131-132`, `.../quota_ledger/domain.py:159`, `.../quota_ledger/domain.py:181` — every cross-boundary **call** at runtime, and there are only three
- `.../quota_ledger/__init__.py:37-39` — the composition point and the one line the swap touches
- `.../quota_ledger/file_journal.py:25-35` — the real driven adapter
- `.../quota_ledger/memory_journal.py:14-22` — the fake, a working implementation and not a mock
- `.../tests/test_ledger.py:26-36` — one case list, two wirings
- `.../tests/test_ledger.py:117-131` — literal expected transcripts, not "the two wirings agree"
- `.../tests/test_ledger.py:260-270` — the boundary's executable keeper
- `.../EVIDENCE.md:158-170` — the port corpus bound to real and to fake

**Refuses to claim** (required and non-null for a score of 4):

The artifact refuses to claim its domain is free of the durable format. `NOTES.md:57-66` says outright that `COMMIT <tenant> <amount> <total>` is rendered inside `Ledger.commit` and `Ledger.close_tenant` (`domain.py:159`, `:181`), that this is deliberate because the line content *is* behavior, and that the file adapter owns only the trailing newline — so the rules do know the wire form of the record, and the artifact says so instead of claiming a clean split. It also refuses to claim more ports than it has (`NOTES.md:53-56`: "Nothing else is indirected. There is no port in front of the arithmetic, no repository interface over the reservations dict, no service layer."), and `NOTES.md:102-123` records that `FEATURE.md`'s `QuotaLedger(quotas, path)` and the no-path-in-the-domain rule genuinely conflict, and that `QuotaLedger` is therefore a factory function and **not** the domain object — a seam named instead of papered over.

**Rationale:**

The caveat forbids settling this on import topology, so I settled it by running it.

**Anchor 3, executed.** I replaced `FileJournal(ledger_path)` with `InMemoryJournal()` at the single line `__init__.py:39` — the named swap — and the shared behavioral suite went **28 passed** with *no file created anywhere* and `domain.py` byte-identical before and after (md5 `2818df20c2f62c4ac480be73621fbb96`, equal to the artifact's own file). An adapter replaced without touching the domain, demonstrated rather than asserted.

**Runtime coupling is what the port allows and nothing more.** The `Ledger` receives a `Journal` by constructor (`domain.py:106-114`) and the only calls it ever makes across the boundary are `append` at `domain.py:159` and `:181` and `records` at `domain.py:131-132` — the two methods the Protocol declares (`domain.py:22-43`). The domain's imports really are `{__future__, dataclasses, typing}` (`domain.py:13-16`), and the artifact does not ask me to take that on trust: `test_ledger.py:260-270` parses them. I seeded a boundary violation with *zero* behavioral effect and exactly that one test failed and nothing else did, so the boundary has a keeper that bites on structure alone.

**Anchor 4.** The driven port has a real implementation (`file_journal.py:25-35`) and a working fake (`memory_journal.py:14-22`), and one case list runs against both through a parametrized fixture (`test_ledger.py:26-36`) — I collected it: **25 identical cases per wiring**, plus 3 unparametrized, 53 passed. The cases assert literal expected transcripts rather than agreement between the wirings (`test_ledger.py:117-131`), which is the failure mode that would make a real/fake pair worthless, and I confirmed it bites both ways: my seeded stale-total fault killed `[file]` and `[memory]` symmetrically.

**I was genuinely torn toward 3.** `EVIDENCE.md:158-170` shows `M09` KILLED under `corpus-port-swap:real` and SURVIVED under `corpus-port-swap:fake`, so the fake binding is blind to at least one fault — and I reproduced that shape myself: reversing `FileJournal.records()` produced 6 failures, every one a `[file]` case, zero `[memory]`. I did not take 3, because anchor 4 asks for the same cases *passing* against both, which I measured directly on working code; divergence under a fault localized in one implementation is what a real/fake pair is *supposed* to show, and it was caught precisely because the real adapter stayed in the case list rather than being replaced by the fake.

*Prose quality was not an input:* `NOTES.md:46-51` states the swap in one sentence, and I would have scored this identically had the sentence been absent, because I ran the swap.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `.../tests/test_ledger.py:26-31`, `.../tests/test_ledger.py:117-131`, `.../tests/test_ledger.py:241-254`, `.../tests/test_ledger.py:260-270`
- `.../quota_ledger/domain.py:141-142`, `.../quota_ledger/domain.py:156-159`, `.../quota_ledger/domain.py:74`
- `.../NOTES.md:136-145`
- `.../EVIDENCE.md:111-120`, `.../EVIDENCE.md:196-218`, `.../EVIDENCE.md:282-315`

**Note:**

I seeded three faults and ran three probes.

**Caught.** (A) A fault localized in the *real* adapter — `FileJournal.records()` reversed — 6 failures, all of them `[file]` parametrizations. It was caught only because the real adapter is in the case list (`test_ledger.py:26-31`) and because two cases assert the bytes on disk directly (`test_ledger.py:241-254`). (B) A domain durable-content fault — commit journalling the amount instead of the running total — 4 failures, symmetric across both wirings, because the cases assert literal transcripts (`test_ledger.py:117-131`) rather than that the two wirings agree with each other. (C) A pure boundary violation with no behavioral effect at all — `domain.py` importing its adapter — caught by exactly one case (`test_ledger.py:260-270`) and by nothing else, which is the only reason a structure-only regression is detectable here at all.

**Demonstrably missed, three classes.** (i) Type discipline on amounts: `reserve('acme', 2.5)` is accepted, commits, and writes `COMMIT acme 2.5 2.5`; the guard is `amount < 1` (`domain.py:141-142`) and nothing pins integrality. `NOTES.md:142-145` predicts this exactly. (ii) Durable-write failure: with an append that raises, memory moves and nothing durable is written (`domain.py:156-159` orders the mutation before the append). `NOTES.md:136-141` predicts this exactly. (iii) **Not predicted anywhere:** the rejection vocabulary is enforced only by an `assert` (`domain.py:74`), so under `python -O` `Result.rejected()` will mint any string, and no case pins the six reasons with assertions off.

**From the packet rather than my own runs.** The `guard_relaxation` class survived `corpus-whole`, `map-silent` and `map-checking` 0-of-3 and was caught only by `corpus-neg`, `corpus-port` and the hand-written suite (`EVIDENCE.md:111-120`) — positive-edge replay is blind to a relaxed guard as a *class*. And the positive control is **not green** (`EVIDENCE.md:196-218`), with `M07` SURVIVING all three port-binding columns while each executed 294 accepting `Reserve` cases (`EVIDENCE.md:282-315`), so every zero in those columns is a floor and cannot be read as reach.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `.../EVIDENCE.md:59-63`, `.../NOTES.md:16-28`
- `.../quota_ledger/__init__.py:37-39`, `.../quota_ledger/domain.py:131-132`
- `.../tests/test_ledger.py:77-105`, `.../tests/test_ledger.py:241-254`

**Note:**

There are two different things called a baseline here, and only one of them exists.

**There is no predecessor tree.** This artifact is a fresh implementation of a feature spec, not a refactor of an earlier version, so "preservation" cannot mean "unchanged from before" and no before/after enumeration is possible. That is the answer, not a gap.

**There is a shared external baseline:** `examples/validation/ab/tests/test_behavior.py`, unchanged and byte-identical for every artifact (`EVIDENCE.md:59-63`). I ran it myself against this tree — **28 passed** — rather than reading the claim at `NOTES.md:27`. Enumerated and shown to hold on top of it: the artifact's own 25 behavioral cases, each run twice, covering hold-without-writing, ascending non-reused ids past `r10`, per-tenant interleaved running totals, release writing nothing, close writing one final line, all six rejection reasons leaving every observable *and* the journal unchanged, and quota exhaustion and recovery — 53 passed, re-confirmed after each seeded fault was reverted.

**The sharp finding is about the baseline's reach, not the artifact's.** When I swapped the durable side out entirely at `__init__.py:39` so that no file was ever created, all 28 shared cases still passed. The shared suite therefore preserves *nothing* about the file on disk — it reads the ledger only through `Ledger.ledger_lines()` (`domain.py:131-132`) — and the only cases in existence that hold the file's actual bytes are the artifact's own two (`test_ledger.py:241-254`). A reader comparing artifacts on the shared suite alone is not comparing anything about durability.

### N-D5 — honesty

**Citations** (`file:line`):

- `.../NOTES.md:125-147`, `.../NOTES.md:102-123`, `.../NOTES.md:149-157`
- `.../EVIDENCE.md:196-218`, `.../EVIDENCE.md:265-276`, `.../EVIDENCE.md:344-347`
- `.../quota_ledger/domain.py:74`

**Note:**

It refuses, specifically, and its refusals are true — I tested two of them.

`NOTES.md:125-147` lists four things the feature does not specify with the interpretation picked for each, and item 3 does not hedge: *"This is the one place I can name where R2 is not enforced by construction."* I drove the ledger with an append that raises and got exactly the state it describes; I called `reserve` with `2.5` and got exactly the leak item 4 describes. Both refusals are load-bearing rather than decorative.

`NOTES.md:102-123` records the one place the feature spec and the structure ask conflict, and explains that `QuotaLedger` is therefore a factory function and **not** the domain object, plus the alternative it rejected and why. `NOTES.md:149-157` declares which files were not opened and volunteers one that was *not* on the prohibition list (`examples/validation/ab/README.md`) as also unopened because it "looked likely to describe the comparison" — a refusal against its own interest, which is the kind that costs something.

The evidence packet is honest against itself too: it declares the positive control not green (`EVIDENCE.md:196-218`), prints "limitations rejected by this run's own evidence" where its own numbers contradict a *declared* limitation (`EVIDENCE.md:265-276`), and states that `effectful_calls` UNDERCOUNTS by construction with 18 sink names left out (`EVIDENCE.md:344-347`).

**Where it falls short of complete:** two things it could have seen and does not name anywhere — that the rejection vocabulary is enforced only by an assert and evaporates under `python -O` (`domain.py:74`), and that the shared suite it reports as "28 passed" still passes with no durable file at all, so that number is not evidence about the file adapter. So: it refuses rather than falsely certifies, it names real blind spots, and its enumeration of blind spots is not exhaustive.

## Verdict

Treat this as a ports-and-adapters implementation that holds when you pull on it — I swapped the whole durable side at `__init__.py:39` and all 28 shared cases still passed with `domain.py` byte-identical — but do not read it as a *measured* simplification (it is the largest of the three trees in the mechanical block and no before tree exists), and note that blindness failed for me: my own `scorecard.json` names subject `arm_b`, so I knew which arm `T` was before I scored it.

## Disclosures

- **BLINDNESS FAILED, and not by my choice.** This card's own `subject.name` is `arm_b`, so the file I was told to fill in told me which arm artifact `T` is before I read a line of the artifact. Recorded in the verdict as the card instructs. I did not read `arm_a/`, `arm_b/` or `arm_c/`, and I did not read `artifact_U` or `artifact_W`.
- **RUBRIC-ADJACENT LEAK via the checker I was instructed to run.** To learn what the schema would enforce I read `examples/validation/scorecards/score_tools.py` — a checker, not on the prohibition list — and its source comments carry **prior results about these very dimensions on this very example**: that D2 "has taken one value on every card ever written about `ab_quota_ledger`", that one model "judged D3 2, 2 and sonnet 4, 3 on the same artifact", and that "four judges scored three different subjects of one artifact once already, and D3 came out 2, 2, 3, 4." That is exactly the class of conclusion rule 9 exists to keep away from a judge. I had already settled D2=2 and D3=4 from the code and from my own executed faults and swap **before** reading it, and neither number moved after. Recording it rather than being asked to.
- **What I did not read:** `references/eval_scorecard.md`, `examples/validation/scorecards/rubric_v3_frozen.md`, any `*-EPIC.md`, `NEXT-EPIC.md`, `references/portable_scorecard.md`, any `UNBLINDING.md`, any other judge's card (including the `-p2` card in this same tree), or anything under `specs/results/scorecards/` other than `artifact_T` and this directory. Also not read: `examples/validation/ab/README.md`, `seeded_faults.toml`, `controls.toml`, `check_catalogue.py`. I ran `examples/validation/ab/tests/test_behavior.py` without reading it.
- **REJECTED — D2 anchor 3.** The pull was real: `NOTES.md:70-84` argues the derived-`available` decision in exactly the shape the caveat demands. I refused because anchor 3 requires before **and** after figures recorded and there is no before tree — the alternative was never built, so it was never measured. The mechanical block is three artifacts at one instant, not one artifact at two instants; reading it as a before/after would be me supplying the simplification the artifact did not make.
- **REJECTED — converting the mechanical block into D2.** On those figures this artifact is the most complex of the three (4 modules, 202 `code_lines`, 25 `public_surface` against 1/78/11), and it would have been easy to let that pull the score to 1. Rule 7 says the block is recorded and never scored, and anchor 2 asks about the design's proportion to its behavior — the extra modules *are* the behavior being asked for here. Recording the disagreement instead: measurement says largest, judgement says proportionate.
- **REJECTED — dropping D3 to 3.** `EVIDENCE.md:158-170` shows the fake binding SURVIVING a mutant the real binding KILLS, and I reproduced that shape myself. It is tempting to read that as "the pair is not really equivalent, so anchor 4 is not earned." I refused: anchor 4 asks for the same cases *passing* against both, which I measured on working code (25 cases per wiring, 53 passed), and a fault living in one implementation *should* diverge — that divergence is the pair working, and it is caught precisely because the real adapter stayed in the case list rather than being replaced by the fake.
- **AMBIGUOUS IN THE CARD — "Score the LOWEST anchor the artifact fully satisfies."** Read literally that scores everything 0, since anchor 0 is "fully satisfied" by nothing being required of it. I read it as the standard ladder rule — the highest rung fully satisfied, and the lower of two when torn — and I said in each rationale which rung I was torn against and why I did not take it. If the intended reading is the literal one, both my numbers are wrong in the same direction and a re-read of the rationales will show it.
- **AMBIGUOUS IN THE CARD — D2's `read_first` says "Diff the two trees yourself."** My declared scope is one tree. I resolved it as diffing this tree against the design the artifact says it rejected, and recorded that this is a counterfactual and not a measurement.
- **UNANSWERABLE FROM MY SCOPE.** `mechanical.json` beside this card is a scaffold with every figure empty and no commit. I left it untouched, since the card says the mechanical block is recorded and never scored and I was told to edit only what the card asks for; the figures I did read are the ones inside the artifact's own `EVIDENCE.md`.
- **TREE CHANGES: none in the repository.** Every fault was seeded in a copy under a scratch directory and reverted there; the shared suite was run with `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` so no bytecode or cache was written into the worktree. The pre-existing `git status` modifications in this worktree are not mine.
- **THE RUBRIC FILE MOVED WHILE I WAS JUDGING.** I ran the checker twice. The first run reported only `PROSE-DRIFT` (rubric file changed in a part no judge is served; served digest unchanged). Minutes later, with no edit of mine to anything outside my own card directory, the same command reported `RUBRIC-DRIFT` (`sha256:1c5f60dab75f9a79` → `sha256:497c16ca85adeb4a`) **and** `SERVED-DRIFT` (`sha256:9157db7edd640c79` → `sha256:a213a36770ccab09`) — i.e. the *served* bytes of the rubric changed underneath this run, and the tracked modifications I saw in `git status` at the start of the session (`references/eval_scorecard.md`, `score_tools.py`, two test files) were gone by the end. Something else was editing the rubric concurrently. I did not read it, so I cannot say what moved; I am recording that it did, because that is precisely what the served digest exists to make visible. My card is scored against the bytes reproduced in this file, whose digests are the ones in the header.
- **PROSE TEMPTED ME AND IS NOT AN INPUT.** `NOTES.md` is the best-written artifact prose I have scored, and the specific risk was that its self-criticism reads as verification. That is exactly why I executed its two named gaps and its one-line swap rather than citing them: every claim I credited above, I ran.
