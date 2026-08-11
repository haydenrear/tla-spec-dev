# Scorecard — eval_toolchain, artifact `JJ`, judge pass 2

`run_id`: `20260810-rm04-JJ-p2` · scorecard_version 4 · rubric `references/eval_scorecard.md` digest `sha256:497c16ca85adeb4a` · served `sha256:a213a36770ccab09`

**You are scoring artifact `JJ`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

Diff the two trees yourself and decide whether one fact is stored twice — kept in agreement by hand across several write sites, and read in one place. Where a measured complexity descriptor exists you may read it, and on its own it decides nothing; where none exists that is not a gap in the evidence.

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

**Executed own faults:** false

**What was run:**

- No code was executed. Read every file in `examples/validation/gap_mutants/` (`price_removal.py`, `altered_score_probe.py`, `residual_faults.toml`) in full, and the before tree (`run_gap_mutants.py`, `gap_mutants.toml`) in full.
- Grepped the live repository for `run_gap_mutants.py`/`gap_mutants.toml`, `residual_faults.toml`, `price_removal` and `port`/`adapter`/`domain` language to trace whether anything still executes the old or new catalogue from inside this scope.
- Read `examples/validation/removal_census/removal_census.py`, `examples/validation/removal_census/removals.toml`, and `tests/test_price_removal.py` (outside my declared scope, read only to trace whether `residual_faults.toml`'s declared mutants are executed anywhere, and to check the `mechanical.json` figures against the artifact's own account of the cut they measure).
- Did not run `altered_score_probe.py` or `price_removal.py`: `altered_score_probe.py` writes a scratch scaffolded epic under `<tree>/specs/results/scorecards/rm01-probe` when pointed at a tree, and the task instructions forbid editing any file in the repository outside the card and forbid running the test suite; running it against this checkout would have done both.

## Your scores

### D2 — complexity

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `specs/results/scorecards/portable-substrate/GOAL-dimensions-replicate/RM-04/blind/artifact_JJ_before/run_gap_mutants.py:117-176` — the before-tree's staging/apply/restore capability, the thing being cut
- `specs/results/scorecards/portable-substrate/GOAL-dimensions-replicate/RM-04/blind/artifact_JJ_before/run_gap_mutants.py:430-594` — the before-tree's single 634-line orchestrator (staged family + ports family + control accounting) that no longer exists in scope
- `examples/validation/gap_mutants/price_removal.py:136-159` — `kill_set`, a pure function over an already-parsed dict, no state
- `examples/validation/gap_mutants/price_removal.py:201-248` — `price`, pure, no state
- `examples/validation/gap_mutants/price_removal.py:271-328` — `entail`, pure, no state
- `specs/results/scorecards/portable-substrate-rm04-JJ/eval_toolchain/20260810-rm04-JJ-p2/mechanical.json:13-43` — total_lines 633→706 and code_lines 489→539 both **rose**; branch_points 76→72 and effectful_calls 37→28 fell; declared_interfaces/instance_state/module_state are 0 in both trees
- `examples/validation/removal_census/removals.toml:651-659` — the repository's own removal census captions this exact cut "THE ONE REMOVAL IN THIS CENSUS WITH A NON-ZERO PRICE"
- `examples/validation/removal_census/removals.toml:661-676` — the removal record: `gap_mutants = ["RM03-GM-RUNNER-an-unapplied-mutant-reports-a-survival"]`, `deletes_detectors = ["pytest-gap-mutants"]`, cutting `run_gap_mutants.py` (629 lines) and `gap_mutants.toml` (728 lines) whole
- `tests/test_price_removal.py:298-318` — `test_nothing_in_the_repository_invokes_the_pricer`, confirming `residual_faults.toml` is named only in a comment and nothing executes it

**Refuses to claim** (required and non-null for a score of 3): n/a — not a 3

**Rationale:**

I diffed `examples/validation/gap_mutants/` against the named before tree myself. Before: one 633-line module (`run_gap_mutants.py`) that stages a `git archive` tree, applies a declared mutant, runs pytest/CLI detectors against the mutated and pristine trees, drives a "ports family" through the shipped port-swap driver, and enforces positive controls before reporting DIES/SURVIVES/INERT/CONTROL_RED/REMOVED. After: two modules — `price_removal.py` (529 lines of pure functions reading already-sealed before/after JSON tables) and `altered_score_probe.py` (177 lines, one live replication of a single named finding via the shipped CLI) — plus `residual_faults.toml`, a catalogue written in the *same schema* as the deleted `gap_mutants.toml` (`[[mutant.edit]]`/`[[mutant.detector]]`) but with no executor left anywhere in this scope to run it.

Neither tree has a god-object: `declared_interfaces`, `instance_state` and `module_state` are all 0 before and after, and the after-tree's functions are stateless (`kill_set`, `price`, `entail` each take a dict and return one). That much satisfies anchor 2 — complexity proportional to behavior, no state written from everywhere.

It does not reach 3, on the artifact's own record rather than mine. `mechanical.json` shows total and code lines went *up*, not down (633→706, 489→539), so this is not even a line-count-driven "simplification" story on its face — but the caveat cuts the other way here, not toward crediting a falling number, but toward refusing to credit ANY reading of these figures as a preserved-behavior simplification. `removals.toml` names this precise cut — deleting `run_gap_mutants.py` and `gap_mutants.toml` from this directory — as the one removal in its whole census with a non-zero price: its own seeded gap mutant reads `ENTAILED-SURVIVES` at head, meaning every killing node the removed mechanism had is now gone. The live seed→run→verdict-against-a-staged-tree capability was not preserved by a cleverer design; it was cut, on adoption grounds, and the repository says so in its own words. A D2 of 3 requires me to say what got simpler *and how the behavior survived it*, and by the artifact's own account the behavior did not survive — so 2 is the honest ceiling.

### D3 — modularity

**Score:** 0

**Citations** (`file:line` — the bar is in the scoring rules above):

- `specs/results/scorecards/portable-substrate-rm04-JJ/eval_toolchain/20260810-rm04-JJ-p2/mechanical.json:21` and `:38` — `declared_interfaces: 0` in both the after and before scope
- `examples/validation/gap_mutants/price_removal.py:336-341` — `_shipped_discriminating`: one hard import of the real classifier by path manipulation, no declared interface, no second implementation ever consulted
- `examples/validation/gap_mutants/altered_score_probe.py:101-106` — the only occurrence of the word "port" anywhere in this scope: fixture text (`"that anything but the durable side is behind a port"`) inside a synthetic scorecard the probe scaffolds and discards, not a boundary the artifact itself observes

**Refuses to claim** (required and non-null for a score of 4): n/a — not a 4

**Rationale:**

There is no ports-and-adapters structure anywhere in `examples/validation/gap_mutants/`. `mechanical.json` records `declared_interfaces: 0` for both the before and after scope, and reading the code confirms it: `price_removal.py` reaches the one piece of logic it depends on (`removal_census.discriminating`) through a raw `sys.path.insert` + `import`, not through any declared port, and it is never swapped for a fake — the docstring's own stated reason for importing rather than reimplementing is avoiding a second copy of the same logic (`PA-04-DF-02`), which is a DRY argument, not an architectural one. The only appearance of "port"/"adapter"/"domain" language in the whole scope is inert fixture data inside `altered_score_probe.py`'s `fill()` helper, which is building a *synthetic scorecard for a different subject* (`quota_ledger/domain.py`) to replicate one finding — it says nothing about this artifact's own architecture. Anchor 0 fully applies: no boundary is discernible, because the artifact does not attempt one. I did not find a driven port, a declared interface, or an adapter that could be swapped, real or fake.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `examples/validation/gap_mutants/altered_score_probe.py:1-42,118-177`
- `examples/validation/gap_mutants/price_removal.py:78-82,251-263`
- `tests/test_price_removal.py:298-318`

**Note:**

I did not execute anything in this scope (see judging practice), so this is read, not run. `altered_score_probe.py` drives the shipped `score_tools.py` CLI directly (scaffold, then check) to replicate exactly one named finding — `SM-04-GM-T1`: a single dimension score altered on an already-written, unsealed card, with nothing else touched, and the kill is decided by subtracting the `INVALID ...` problem set before the alteration from the set after. By its own docstring it claims nothing beyond that one shape of tamper, and it says so plainly: "NOT A GATE. Nothing invokes it." I could not tell whether it still reports `CAUGHT` against the live tree, because running it would have written a scratch card under `specs/results/scorecards/rm01-probe` in this checkout, which the task forbids. `price_removal.py` catches nothing live either — `tests/test_price_removal.py:298-318` shows the repository itself asserts nothing invokes the pricer — but its `_loss_reason` logic distinguishes three ways a kill can be lost (detector removed, node removed, detector weakened) and states outright that the third — a node that keeps its id and changes its body — is "the class no survivorship test can see." I read that as a documented, honestly-bounded claim, not a demonstrated one; I have no run of my own that shows it firing on a real weakened node.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `specs/results/scorecards/portable-substrate/GOAL-dimensions-replicate/RM-04/blind/artifact_JJ_before/run_gap_mutants.py:117-176,197-304,311-422,551-568`
- `examples/validation/gap_mutants/price_removal.py:201-248`
- `examples/validation/removal_census/removals.toml:651-676`
- `tests/test_price_removal.py:298-318`

**Note:**

There is a baseline, and it is the before tree I was handed. I enumerated five behaviors of `run_gap_mutants.py`: (1) stage a `git archive` of any ref; (2) apply a declared mutant's edits into that tree, refusing loudly on an ambiguous or no-op anchor; (3) run each detector against the mutated and pristine trees and diff failing nodes into DIES/SURVIVES/INERT/CONTROL_RED/REMOVED; (4) drive a "ports family" of mutants through the shipped `run_port_swap.py`; (5) enforce positive controls so a `SURVIVES` behind a dead control is reported undecided rather than credited. None of the five hold in the current scope. `examples/validation/gap_mutants/` no longer contains a staging/apply/restore/run-detector loop, and nothing in the live tree consumes `residual_faults.toml`'s `[[mutant.edit]]`/`[[mutant.detector]]` declarations to execute them — confirmed by grep and by `tests/test_price_removal.py:298-318`, which asserts exactly that. What replaced it is narrower by design: `price_removal.py` reads two already-sealed JSON tables and reports a verdict per fault; `altered_score_probe.py` replicates one prior finding via the shipped CLI. The repository's own removal census records this specific cut as its one removal with "a non-zero price" (`removals.toml:651-659`). So the baseline's live-execution behavior is not shown still to hold — it is shown, on the artifact's own record, to be gone.

### N-D5 — honesty

**Citations** (`file:line`):

- `examples/validation/gap_mutants/price_removal.py:65-73,78-82,323-327`
- `examples/validation/gap_mutants/altered_score_probe.py:40-41,94-102`
- `examples/validation/removal_census/removal_census.py:22-33,288-296`
- `examples/validation/removal_census/removals.toml:651-659`

**Note:**

Refusal discipline is where most of this artifact's word count goes. `price_removal.py` states its own soundness bound twice — in the module docstring and again inline at the point it matters — that `ENTAILED-SURVIVES` "cannot see a kill the after tree ADDED," and the file has no code path that emits an `ENTAILED-DIES`. `altered_score_probe.py` keeps a first, confounded run of itself on the record rather than quietly fixing it (it names the discarded artifact, `sm04-gm-t1-*-confounded.json`) and states "NOT A GATE. Nothing invokes it." `removal_census.py` refuses to emit a total over removals even though its own CLI parser accepts the flag, purely so the refusal has somewhere to happen, and explains why in the same breath: a total is exactly what hid the epic's real cost before. And the removal this whole scored diff turns on is captioned by the repository itself as the one entry in its census with a non-zero price, rather than folded quietly into a simplification narrative. I did not find a place in scope where the artifact certified something it had not checked.

## Verdict

Score `examples/validation/gap_mutants/` as a stateless, honestly-bounded analysis toolkit with no ports-and-adapters architecture at all (D3=0) whose apparent complexity improvement is not a preserved-behavior simplification (D2=2, not 3) — the repository's own removal census records that this exact cut, from a live mutant-execution catalogue to a pair of passive pricing/probe tools, has a non-zero price, so read the mechanical figures as a scope reduction, not a free simplification.

## Disclosures

Nothing that identifies the arm or the mapping. I read `examples/validation/removal_census/removal_census.py`, `examples/validation/removal_census/removals.toml`, and `tests/test_price_removal.py` — outside my declared scope but not on the forbidden list — to trace whether `residual_faults.toml`'s declared mutants are executed anywhere and to understand what the diff I was asked to make actually cost. `removals.toml` is what let me disqualify D2 from a 3: it names this specific cut as the census's one non-zero-price removal, in its own words, and I would not have found that from the scoped directory alone — it is the best finding in this pass and it came from reading one file adjacent to the scope, not from re-reading the scoped files harder. I rejected running `altered_score_probe.py` against the live checkout because it writes a scratch scaffolded card under `specs/results/scorecards/rm01-probe` in whatever `--tree` it is given, which would have edited a file outside the card in violation of the task's instructions; nothing I did changed the tree.
