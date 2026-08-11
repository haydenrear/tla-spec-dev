# Scorecard — eval_toolchain, artifact `GG`, judge pass 1

`run_id`: `20260810-rm04-GG-p1` · scorecard_version 4 · rubric `references/eval_scorecard.md` digest `sha256:497c16ca85adeb4a` · served `sha256:a213a36770ccab09`

**You are scoring artifact `GG`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

**Executed own faults:** true

**What was run:**

- Copied `examples/validation/ab/reference_ports/` into a scratch directory (the repository was not written to) and ran a probe I wrote myself — six expected-value cases of my own, not the artifact's suite and not pytest — through **both** composition points (`quota_ledger`, `quota_ledger_fake`), under four faults I seeded myself:
  - `JF-1` domain: `commit` stops adding the reserved amount to the running total.
  - `JF-2` **fake** adapter: `InMemoryJournal.lines()` reverses order.
  - `JF-3` **real** adapter: `FileJournal.lines()` reverses order.
  - `JF-4` **real** adapter: `append`/`lines` stop touching the filesystem entirely and keep the record on the instance.
- Measured result (control first):

  | fault | real wiring | fake wiring |
  |---|---|---|
  | none (control) | green | green |
  | JF-1 domain | KILLED (case c2) | KILLED (case c2) |
  | JF-2 fake adapter | **survived** | KILLED (case c3) |
  | JF-3 real adapter | KILLED (case c3) | **survived** |
  | JF-4 real adapter, no filesystem | **survived** | **survived** |

- A durability read that does **not** go through the adapter: under `JF-4` the port reports `['COMMIT acme 3 3']` while the ledger file on disk is empty.
- Static checks by hand: import statements of `ex5_pipeline_divergent/pipeline/**`, `ex6_jenga/hub/**` and `runs/ex2-run4/artifacts/providers.py`, compared against `mechanical.json`'s `internal_import_edges`.
- I did **not** run the repository's test suite, `check_catalogue.py`, `check_twins.py` or `score_tools.py check`, and I did not modify any file in the repository.

## Your scores

### D2 — complexity

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `examples/validation/ab/reference/quota_ledger.py:34-41`
- `examples/validation/ab/reference_ports/domain.py:28-35`
- `examples/validation/ab/tests/test_behavior.py:285-292`
- `examples/validation/scorecards/score_tools.py:127`
- `examples/validation/scorecards/architecture_tags.py:65`
- `examples/validation/scorecards/architecture_tags.py:274`
- `examples/validation/scorecards/score_tools.py:1010-1023`
- `examples/validation/ex3_over_complex/order_hub/order_hub.py:26-29`
- `examples/validation/README.md:12`
- `examples/validation/scorecards/architecture_tags.py:138-220`

**Refuses to claim** (required and non-null for a score of 3): I do not claim the 14,207-line figure is proportionate as a whole — I checked duplication and god-state at the sites above and did not audit all 85 modules; and I do not claim the artifact is *unable* to reach 3, only that nothing I can reach records a before.

**Rationale:**

Above 1: complexity is not merely reported, a relationship between the figures and the design is argued *and computed* inside the artifact — `architecture_tags.derive()` (`architecture_tags.py:138-220`) turns figures the shipped instrument already prints (`declared_interfaces`, `instance_state`, `modules_with_effectful_calls`) into three named clauses about where a boundary is, and states which clause it deliberately refuses to include (import topology, `:159-167`).

Below 3: **there is no before tree for this artifact and no before figures.** `mechanical.json` records an `after` block only (`mechanical.json:13-14`); there is no `before`. The only before/after pairs inside the declared scope — `runs/ex2-run*/artifacts/descriptor_before.txt` / `descriptor_after.txt` — are recordings of a *different* subject measured during an agent run (a scratch copy of `distributed_history`), and the pair is not a simplification at all: the "after" spec has **grown** an action and Q moves 0.170 → 0.187. Anchor 3 asks that *a simplification was made and its effect measured, both figures recorded*; on this scope nothing of the kind exists, and inventing one would be exactly the MF-020 error the caveat names.

At 2 rather than lower, with the reservation stated plainly. The one god-state in the scope is `ex3_over_complex/order_hub/order_hub.py:26-29`, where `_stamp` writes `mode`, `audit_log` and `dirty` on every one of four operations — a variable written from everywhere. I score it as behaviour-required rather than as a defect, because the module's whole behaviour is *to be* a god-state fixture (`README.md:12` declares it as such), and a fixture that cannot express the property the instrument looks for produces a zero that says nothing. That reading is a judgement and I record it as one.

What keeps 2 from being comfortable is a fact stored **three** times and kept in agreement by hand. The rejection vocabulary is a literal collection in `reference/quota_ledger.py:34-41`, again in `reference_ports/domain.py:28-35` (whose comment says "unchanged from the flat reference" — i.e. maintained by hand), and a **third** time in `tests/test_behavior.py:285-292`, where the test that exists to police the vocabulary compares observations against its own private copy rather than against either module's `REJECTION_REASONS`. Drift in either module would not be seen by the test named for it. The same shape appears in the scorecard tooling: `DIMS` is declared at `score_tools.py:127` and again at `architecture_tags.py:65`, and the judge tier is derived twice — carefully at `score_tools.py:1010-1023` (three tiers, `None` on ambiguity) and inline at `architecture_tags.py:274` (two tiers, `"?"` otherwise). **These two copies have already diverged**: a `haiku` judge is a tier to `score_tools` and a `?` to `architecture_tags`, whose `tiers_measured` loop is hardcoded to `("opus", "sonnet")`. `score_tools` already loads `architecture_tags` as a module (`score_tools.py:269-279`), so the duplication is not forced by the packaging.

Prose quality was a real temptation here and I am saying so per rule 4: the docstrings in this tree are the best-argued I have read, and several of them argue for a design decision rather than evidencing it. I scored the code.

### D3 — modularity

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `examples/validation/ab/reference_ports/domain.py:38-58`
- `examples/validation/ab/reference_ports/quota_ledger.py:24-25`
- `examples/validation/ab/reference_ports/quota_ledger_fake.py:37-38`
- `examples/validation/ab/check_catalogue.py:174-180`
- `examples/validation/ab/reference_ports/README.md:3-6`
- `examples/validation/scorecards/architecture_tags.py:63`
- `examples/validation/scorecards/architecture_tags.py:121-135`
- `examples/validation/scorecards/architecture_tags.py:268-290`
- `examples/validation/scorecards/architecture_tags.py:529-546`
- `examples/validation/check_twins.py:26-32`
- `examples/validation/ab/check_catalogue.py:609-631`

**Refuses to claim** (required and non-null for a score of 4): I do not claim the harness's pure functions constitute a domain in the anchor's sense, and I do not claim that the 4-shaped evidence I executed generalises past the ~200 lines of `ab/reference_ports`.

**Rationale:**

**The anchor-4 evidence exists, I executed it, and I am still not awarding it at this scope.** A driven port is declared in the domain's own vocabulary (`domain.py:38-58`), two implementations satisfy it, and two composition points hand one or the other to the identical `ReservationBook` (`quota_ledger.py:24-25`, `quota_ledger_fake.py:37-38`). I ran my own cases through both. The named swap is `FileJournal` → `InMemoryJournal` at one constructor line, and it is real at runtime, not in the import graph: my domain fault `JF-1` died on **both** wirings with the same cases, and my two adapter faults died on exactly one wiring each — `JF-2` (fake) survived the real wiring and `JF-3` (real) survived the fake one. That is evidence about what *calls* what, which is what the caveat asks for, and it satisfies anchor 4's letter for that subtree.

I take the lower anchor for one reason and the artifact supplies it: **that subtree is a fixture, and it is 5 modules of the 85 in the declared scope.** Its own first line says `THIS IS NOT AN ARM ... It is a fixture` (`reference_ports/README.md:3-6`, `:66`). The artifact itself computes the failure mode of crediting it — `scope_drift()` at `architecture_tags.py:529-546` exists because a card once scored D3 = 4 with every citation pointing at a fixture, and it records that "a scope change is not an architecture change and must never be read as one". Awarding 3 or 4 to `examples/validation` on the strength of `ab/reference_ports` would be that card again.

At the declared scope, the artifact's own domain — the eval harness's scoring, deriving and checking logic — **does** import and perform its I/O, with no port. `architecture_tags.py` computes the effect-boundary tag and, in the same module, names its instrument as a path constant (`:63`) and shells out to it with `subprocess.run` (`:121-135`), and reads every card off disk in the function that builds the rows it computes over (`:268-290`). To point that derivation at a different complexity instrument or a different card store, you edit the module that does the deriving: there is no seam to substitute one at. The same holds for `score_tools.py` and `check_catalogue.py`. There is a real functional-core discipline here — `derive`, `check`, `contested_of`, `verdict`, `scope_drift` are pure over plain dicts — and it is worth saying, but a pure function in an effectful module is not an adapter that could be replaced without touching the domain.

Anchor 2 is fully satisfied and that is a genuine result, not a consolation. The boundaries this artifact declares are followed *and executed*: `check_twins.py:26-32` digests the four architecture inputs plus the suite and fails if the twins drift; `check_catalogue.py:609-631` checks `ADAPTER_IMPLEMENTATIONS` in **both** directions, so renaming an adapter fails there instead of orphaning a declaration; `check_catalogue.py:174-180` names the three wirings the one suite is pointed at. Cross-boundary calls in the fixture trees go through something identifiable as a port. What is missing for 3 is not a declaration — it is that the largest part of the scope has no port to declare.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `examples/validation/ab/tests/test_behavior.py:112-137`
- `examples/validation/ab/tests/test_behavior.py:284-301`
- `examples/validation/ab/reference_ports/journal_file.py:32-38`
- `examples/validation/ab/reference_ports/domain.py:41-43`
- `examples/validation/ab/check_catalogue.py:469-543`
- `examples/validation/ab/check_catalogue.py:1217-1232`

**Note:**

I seeded four faults of my own (listed under judging practice) and ran them, so this note is measured rather than read.

**Caught.** The expected-value cases catch a domain fault on both sides of the port (`JF-1`, killed by my running-total case on both wirings — the assertion shape is `test_behavior.py:112-137`), and they catch an ordering fault in *whichever* adapter the composition point actually wires in (`JF-2` on the fake, `JF-3` on the real). The pair is the artifact's own claim and it holds: the difference between the two rows is the size of the region the port creates.

**Demonstrably missed: durability.** `JF-4` — a `FileJournal` that stops touching the filesystem altogether and keeps the record on the instance — **survived every case on both wirings**, and my out-of-band read showed the port reporting `['COMMIT acme 3 3']` while the ledger file on disk was empty. The port's declared job is "a record that outlives the run" (`domain.py:41-43`) and no case in this tree reads that record by any route other than the adapter that wrote it: `ledger_lines()` is the only observer (`test_behavior.py:119`, `:192`, `:277-281`). So the real adapter's one distinguishing property against the fake — persistence — is unverified, and a "real" adapter that is secretly a second fake passes as the real one. This is a class distinct from `adapter_internal` as the catalogue defines it (`check_catalogue.py:121-134`): the fault is *inside* the real adapter and still invisible, because the oracle never leaves the adapter.

I also note what the catalogue harness does verify, since it is unusual and it is code rather than a claim: `check_integrity` asserts each `find` occurs exactly once, that apply/revert is byte-identical, and that the mutant still parses (`check_catalogue.py:469-543`), and `--demonstrate` runs deliberately broken controls that declare the verdict the probe must return, so the probe ships with a demonstrated failing input (`check_catalogue.py:1217-1232`). I did not execute either.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `examples/validation/check_twins.py:26-32`
- `examples/validation/ab/check_catalogue.py:174-180`
- `examples/validation/ab/check_catalogue.py:838-853`
- `examples/validation/ab/reference_ports/domain.py:8-12`
- `examples/validation/runs/ex2-run1/artifacts/descriptor_before.txt:44`
- `examples/validation/runs/ex2-run1/artifacts/descriptor_after.txt:44`

**Note:**

**There is no baseline for this artifact and I was not given one.** `examples/validation` has no before tree in my scope, `mechanical.json` carries no `before` block, and I am not able to reach one. So "which behaviours of the baseline are shown still to hold" has no subject at the scope I am scoring, and that is the answer rather than a gap in the note.

What I could do instead, I did. Inside the scope there is one claim of behavioural identity that is checkable: `domain.py:8-12` asserts that the ported reference is `reference/quota_ledger.py`'s behaviour "statement for statement". I enumerated six behaviours from the feature — reserve holds and writes nothing; commit moves the hold and writes one line with the running total; running totals accumulate; the ledger is append-only and ordered across tenants; `close_tenant` refuses while a reservation is outstanding (the cross-aspect guard); a rejection names a declared reason and changes nothing — and ran all six through both composition points. All six passed identically on both, and my domain fault broke the same case on both, so the two wirings are demonstrably the same domain. I did **not** compare either against the flat `reference/`, so the "statement for statement" claim against the flat tree remains unchecked by me.

The artifact does mechanise preservation where it has a baseline of its own: `check_twins.py:26-32` digests the five files the twins must share, and `check_catalogue.py:838-853` refuses a whole column of results if the suite is not green on the unmutated tree first — a control run, so a "kill" cannot predate the mutant. Note also that the one before/after pair in the scope is not a preservation record: `descriptor_before.txt:44` and `descriptor_after.txt:44` show Q rising 0.170 → 0.187 because the after-spec gained an action.

### N-D5 — honesty

**Citations** (`file:line`):

- `examples/validation/ab/reference_ports/README.md:68-77`
- `examples/validation/scorecards/architecture_tags.py:84-89`
- `examples/validation/scorecards/architecture_tags.py:326-329`
- `examples/validation/scorecards/score_tools.py:437-444`
- `examples/validation/scorecards/score_tools.py:36-38`
- `examples/validation/ab/check_catalogue.py:86-88`
- `examples/validation/ab/check_catalogue.py:576-580`
- `examples/validation/ab/check_catalogue.py:778-781`
- `examples/validation/scorecards/subjects.toml:155-165`

**Note:**

Yes, and at a density I have not seen before — the refusals are in code and in constants, not only in prose.

It refuses to certify: `--controls` reports `BROKEN` / `INERT` / `OUT_OF_REGION` and converts none of them into anything (`check_catalogue.py:86-88`), and a control measured `INERT` is **kept in the catalogue saying so** rather than deleted to keep a count tidy (`:576-580`). `architecture_tags.py:84-89` prints that its own `STATE_COLOCATION_MAX` threshold **is not measured** and that no artifact near it has ever been seen, and `:326-329` lists three things its demonstration table cannot see. `score_tools.py:437-444` says of its own leak detector "THIS IS A BACKSTOP AND IT IS NOT THE MECHANISM ... This list cannot be complete", and `:36-38` states that its own `scope` command exits 1 on this repository's record and calls that a demonstrated failing input rather than a defect. `check_catalogue.py:778-781` labels its architectural-vocabulary probe "a vocabulary probe, not a semantic judgement" and names what it cannot detect. `reference_ports/README.md:68-77` refuses three claims the tree could easily have made, including that its four-line fake is evidence anybody *would* have reached the blind region.

The sharpest instance is `subjects.toml:155-165`, which declines to rewrite a predecessor's stale figure to match the current file and files the discrepancy as a finding instead. The same file also discloses a live leak in its own instrument — see Disclosures; disclosing it is honest and it does not stop the leak from having reached me.

Two places where the refusal is thinner. The durability blind spot in N-D1 is not named anywhere I found: the tree names the region a port *creates* (`reference_ports/README.md:24`) but not that its real adapter's defining property is unasserted. And `mechanical.json`'s import-edge block asserts edges that do not exist in the tree (Disclosures), which is a measurement stated with more confidence than it has earned — though rule 7 puts that block outside the score.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

-

**Note:**

### N-D4 — behavior preservation

**Citations** (`file:line`):

-

**Note:**

### N-D5 — honesty

**Citations** (`file:line`):

-

**Note:**

## Verdict

D2 = 2 and D3 = 2 at the declared scope: the harness's own logic is duplicated by hand across modules and performs its I/O in the modules that compute, while the anchor-4-shaped port evidence — which I executed and which holds — lives in a 5-module fixture inside the scope, so read this card as "the fixture is ports-and-adapters and the harness around it is not", and note the disclosed leak below before comparing it with any other card.

## Disclosures

**LEAK, disclosed in full: `examples/validation/scorecards/subjects.toml` pre-answers both of my dimensions for my exact scope.** It is inside my declared scope and I was told I could read it as code. I read it in one pass and it identifies my subject and hands me two conclusions:

- `subjects.toml:263-267` declares `[subject.rm04_eval_harness]` with `example = "eval_toolchain"` and `scope = ["examples/validation"]` — byte-identical to my card's `example` and `subject.scope` — and gives it `declared_effect_boundary = "ports-and-adapters"`. That is the value of the axis my card's `subject.axis` names (`effect_boundary`) and the axis the artifact's own `architecture_tags.py:88-94` says has authority **on D3 and on no other dimension**. It is a declared answer to the dimension I was scoring.
- `subjects.toml:233-236` states that two of the three RM-04 subjects have no before tree and that **"D2 is bounded at 2 for them by anchor 3"**, and that the bound is a prediction sealed before dispatch. `examples/validation` is one of those two. That is a pre-answer to my D2 ceiling.
- `subjects.toml:244-254` says all of this out loud — "THE SUBJECT CONTAINS THE FILE YOU ARE READING ... A judge who opens it can match a scope to a declared value and read the D3 answer off it" — and records that withholding the value was considered and rejected. The exposure is disclosed by the artifact; it still reached me.
- Read together with `subjects.toml:257-274`, the file also tells me which declared subject I hold (`rm04_eval_harness`), which the blinding rules in `score_tools.py:700-728` are written to prevent a card from carrying.

**How I handled it, so a reader can discount this card rather than guess at it.** I reached D2 = 2 from the packet and the tree: `mechanical.json` records an `after` block and no `before`, and the only before/after pair inside the scope measures a different subject and shows growth, not simplification. I reached D3 = 2 from code I read and a probe I ran, and the scope-drift argument I used to take the lower anchor is the artifact's own (`architecture_tags.py:529-546`). Both scores agree with the leaked declaration, and I cannot prove to you that seeing it moved nothing — if this card is used as an independent measurement of the instrument, that agreement should be treated as contaminated in the D3 direction (the declaration says `ports-and-adapters`; I scored the lower anchor, i.e. *against* it, which is the direction a leak is least likely to have produced).

**Disagreements between the mechanical block and the tree.** Rule 7 says the block is recorded and never scored, and that a disagreement is a finding. There are three:

- `mechanical.json:265-288` lists six import edges among `ex6_jenga/hub/**`, forming a complete 3-cycle including `notify/flags.py → billing/audit.py` and `notify/flags.py → orders/lifecycle.py`. `ex6_jenga/hub/notify/flags.py:3` imports nothing but `__future__`. Every edge out of that file is fabricated; the tree has three edges, not six.
- `mechanical.json:213-215` claims `ex5_pipeline_divergent/pipeline/dispatch/delivery.py → ex4_pipeline_coherent/pipeline/ingest/queue.py`. The actual statement is `from pipeline.ingest.queue import WorkQueue` (`ex5_pipeline_divergent/pipeline/dispatch/delivery.py:10`), resolving inside ex5's own tree. The twins have identical relative paths, so the edge resolver appears to bind to the first tree it finds. Same defect at `mechanical.json:297-300`, which claims `runs/ex2-run4/artifacts/providers.py → ab/reference_ports/domain.py`; that file's line 30 reads `from ecommerce_backend.domain import EcommerceStore`, matched on the basename `domain`.
- `mechanical.json:6` records commit `82936ef3bce29e3551cd83dd3673bf60f4eec162`; `git rev-parse HEAD` in the tree I scored is `dd71b11a0282a662f60d7bca0c34671ba9e12235`. The figures beside my judgement were measured at a different commit from the one I judged.

The first two matter beyond bookkeeping: the block's `internal_import_edges` is the most modularity-shaped figure in it, and it is wrong in both directions available to it (asserting edges that do not exist, and attributing real edges to the wrong file). It is a live demonstration of the D3 caveat — import topology is not modularity, and here it is not even topology.

**What I ran that changed nothing in the tree.** All fault seeding was done on a copy under my scratch directory. `git status` was clean when I started and I wrote no file in the repository other than this card and its JSON. I did not run the repository's test suite, `check_catalogue.py`, `check_twins.py` or `score_tools.py check`.

**What I rejected.**

- **Rejected: D3 = 4.** I have the runtime evidence for it — my own cases, one domain fault dying on both wirings, one adapter fault dying on each — and I still rejected it, because at the declared scope it rests entirely on `ab/reference_ports`, and the artifact's own `scope_drift()` was written after a card scored D3 = 4 on citations that were all to a fixture.
- **Rejected: D3 = 3 via the functional core.** `derive`, `check`, `contested_of`, `verdict` and `scope_drift` really are pure functions over plain dicts, and a generous reading calls that a domain that does not import its I/O. I rejected it: they share modules with `subprocess.run` and `read_text`, the instrument they call is a module-level path constant (`architecture_tags.py:63`), and there is no seam at which an adapter could be substituted without editing those modules.
- **Rejected: D2 = 1 on the god-state in `ex3_over_complex` and `ex6_jenga`.** By the letter of anchor 2 the scope contains a variable written from everywhere (`ex3_over_complex/order_hub/order_hub.py:26-29`). I rejected the deduction because those modules' entire behaviour is to be that fixture, which is the "as simple as its behaviour requires" clause working correctly. Another judge could reasonably score 1 here and I would not call them wrong.
- **Rejected: treating `runs/ex2-run*/artifacts/descriptor_before.txt` + `descriptor_after.txt` as D2 anchor 3's before/after.** They are before/after for a different subject, taken during a recorded agent run, and the after is larger than the before.
- **Rejected: reading anything under `specs/results/scorecards/` outside this directory, and `references/eval_scorecard.md`.** Not opened.
