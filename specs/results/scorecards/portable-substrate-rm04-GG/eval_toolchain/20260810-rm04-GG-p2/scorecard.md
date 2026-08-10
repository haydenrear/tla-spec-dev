# Scorecard — eval_toolchain, artifact `GG`, judge pass 2

`run_id`: `20260810-rm04-GG-p2` · scorecard_version 4 · rubric `references/eval_scorecard.md` digest `sha256:497c16ca85adeb4a` · served `sha256:a213a36770ccab09`

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

**Executed own faults:** false

**What was run:**

- Nothing executed. I read code and pre-recorded artifacts only: no pytest, no seeded fault, no script of my own run against the tree.
- Read `ab/reference_ports/{domain,journal_file,journal_memory,quota_ledger,quota_ledger_fake}.py` and its `README.md` in full.
- Read `ab/check_catalogue.py:805-854` (`verify_suite`) to confirm, from the code itself, that it actually executes `subprocess.run([..."pytest"...])` with `QUOTA_LEDGER_IMPL` set to each wiring in turn, rather than trusting the README's prose claim that it does.
- Read `ex4_pipeline_coherent/generated/pipeline_contract/{ports,fake,contract_tests}.py`, `specs/program_model/{adapters,providers}.py`, and `tests/driver.py`, and grepped the whole scope for `assert_ledger_store_port_conformance` and `ledger_store_provider` to check whether the generated fake-vs-real conformance path for `LedgerStorePort` is actually wired up anywhere (it is not: the fake's `persist` raises `NotImplementedError`, and the conformance function is never called).
- Read `runs/ex4-run4/scoring.md:17-38` for the recorded seeded-fault kill table.
- Read `ex3_over_complex/order_hub/order_hub.py` and `ex6_jenga/README.md` for the god-state / refusal fixtures.
- Read `instruments/demonstrate.py` (its blind-spot and non-gating sections) and `scorecards/score_tools.py`'s module-level structure (grepped for globals/`self.` state; found none of concern).
- Read `mechanical.json` beside this card.

## Your scores

### D2 — complexity

**Score:** 1

**Citations** (`file:line` — the bar is in the scoring rules above):

- `specs/results/scorecards/portable-substrate-rm04-GG/eval_toolchain/20260810-rm04-GG-p2/mechanical.json:15-23` — measured: 85 modules, 14,207 total lines / 11,161 code lines, 493 callables, 1,784 branch points, 704 effectful calls concentrated in 32 of 85 modules, only 3 declared interfaces, instance_state 80, module_state 6.
- `examples/validation/ex3_over_complex/order_hub/order_hub.py:1-6,16-30,33-38` — a single shared `hub` dict, every action (`place_order`, others) routing through `_stamp(hub, mode)`, which writes `hub["mode"]`, `hub["audit_log"]` and `hub["dirty"]` from one shared function called by every action. This is the file's own stated design ("Every operation routes through HUB, stamping the shared mode, audit log, and dirty flag on its way").
- `examples/validation/ab/reference_ports/domain.py:101-108,129-142,156-162` — `_available` is a fact (available quota) stored as its own mutable dict and kept in agreement by hand across three separate write sites (`reserve` decrements it, `release` increments it, `commit` must NOT touch it) rather than derived once from `_quota` minus outstanding/committed. This is exactly the "one fact stored twice" shape the D2 read-first note asks a judge to look for.

**Refuses to claim** (required and non-null for a score of 3): n/a — not the top score.

**Rationale:** Complexity is measured extensively (`mechanical.json`) and I can relate parts of the figures to parts of the design — `declared_interfaces: 3` against 85 modules matches what I independently found (one genuine port pattern, in `ab/reference_ports` and `ex4`'s `LedgerStorePort`, is rare in this scope, not the norm). But I cannot honestly sign the anchor-2 sentence "no god-state, no variable written from everywhere" for the artifact as declared: `ex3_over_complex/order_hub.py` is exactly that pattern, present and running, inside the declared scope. It is there on purpose, as a negative-control fixture the toolchain is meant to detect (`ex6_jenga` is the same shape) — but the anchor's claim is a blanket one about the artifact, not about the toolchain's own intentions, and the scope as declared includes files that falsify it. Separately, even inside the "good" reference design, `_available` is state kept in sync by hand at three sites rather than derived — a real, if modest, instance of the duplication the read-first note asks a judge to hunt for. There is no before/after simplification recorded for `examples/validation` itself (see the scoping note above), so 3 is unreachable regardless. I score 1 rather than 2: measured and reported, with a real but partial relationship argued, not a blanket "no god-state" I can defend for the whole declared scope.

### D3 — modularity

**Score:** 4

**Citations** (`file:line` — the bar is in the scoring rules above):

- `examples/validation/ab/reference_ports/domain.py:14-17,38-59` — `LedgerJournal` is a `Protocol` declared in the domain module; the module's own docstring states, and the imports confirm, that it imports neither adapter that satisfies it.
- `examples/validation/ab/reference_ports/journal_file.py:21-38` — the real adapter, `FileJournal`, a file on disk.
- `examples/validation/ab/reference_ports/journal_memory.py:33-44` — the fake adapter, `InMemoryJournal`, a real (non-recording) working implementation of the same port, kept in memory.
- `examples/validation/ab/reference_ports/quota_ledger.py:1-9,17-25` — the real composition point; its docstring names the specific swap ("replace `FileJournal` with `InMemoryJournal` on the line below and no domain file changes").
- `examples/validation/ab/reference_ports/quota_ledger_fake.py:30-38` — the fake composition point performing exactly that swap.
- `examples/validation/ab/check_catalogue.py:805-828,830-854` — `verify_suite()` is not a claim, it is code that runs: it `subprocess.run`s the shared suite with `QUOTA_LEDGER_DIR`/`QUOTA_LEDGER_IMPL` pointed at each wiring in turn, requires a GREEN control on the unmutated tree for each wiring before any mutant is admissible, and only then applies mutants. This is runtime evidence of what calls what, not import topology.
- `examples/validation/ab/tests/test_behavior.py:1-20` — one unedited suite file, the same cases, pointed at either wiring via an environment variable; not a separate suite per wiring.

I also checked whether `ex4_pipeline_coherent`'s own `LedgerStorePort` reaches the same bar and it does not: `ex4_pipeline_coherent/generated/pipeline_contract/fake.py:18-21` raises `NotImplementedError` for `persist`, and `contract_tests.py`'s `assert_ledger_store_port_conformance` (which would compare the fake against a real adapter) is never called anywhere in scope (checked by grep). `ex4`'s ARM A/B swap (`runs/ex4-run4/scoring.md:17-21`) is real evidence of anchor 3 (two real adapters, same domain, same 330 cases, both GREEN) but not of anchor 4 — no fake is exercised there.

**Refuses to claim** (required and non-null for a score of 4): `examples/validation/ab/reference_ports/quota_ledger_fake.py:14-22` states plainly what this construction does NOT do: "it does not assert that the two wirings agree. A test that only compares two wirings of one domain passes when the domain is wrong, because both wirings are wrong together." And `examples/validation/ab/reference_ports/README.md:68-77` names the limit on the demonstration itself: "It is one feature, `n = 1`, and the tree was written by the same author as the catalogue that seeds into it... `quota_ledger_fake.py` being four lines is evidence that the blind region was cheap to reach, **not** evidence that anybody would have reached it. Nobody did, for a whole epic."

**Rationale:** D3's anchors are phrased per-domain, per-adapter, per-port ("a domain," "an adapter," "a driven port"), not as a claim that every file in an 85-module, 14,207-line scope is hexagonal. On that reading I found one instance, fully evidenced at runtime rather than by import graph, that satisfies anchor 4 to the letter: a driven port declared in a domain that imports no adapter, a real and a fake adapter both implementing it, and the identical case suite executed (via subprocess, not merely claimed) against both, with a required green control. I am not generalizing this to "the whole scope is ports-and-adapters" — most of the scope (the CLI tooling in `scorecards/`, `gap_mutants/`, `removal_census/`, `instruments/`, most of `runs/`) neither declares nor needs a port boundary, and two fixtures (`ex3_over_complex`, `ex6_jenga`) are declared god-state with none at all. Unlike D2's "no god-state anywhere" clause, D3's clause is about whether declared boundaries are followed where they exist, so those unrelated fixtures don't falsify it the way they falsify D2.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `examples/validation/runs/ex4-run4/scoring.md:17-21,31-38` — control table and the F1-F6 kill matrix.
- `examples/validation/ab/reference_ports/journal_memory.py:7-21` — the BA-B14 finding this fixture exists to answer, quoted in an in-scope file (see Disclosures).
- `examples/validation/ex4_pipeline_coherent/generated/pipeline_contract/fake.py:18-21` — `persist` raises `NotImplementedError`.

**Note:** I did not seed a fault myself (see judging practice); this is a read of what is already recorded. What the recorded cases demonstrably caught: on the `ex4` pipeline, seeded faults F1 (wrong value), F2 (wrong field), F4 (wrong status) and F6 (off-by-one in-memory) were killed on both measurement arms; F3 (off-by-one, durable) and F5 (swallowed error) **survived** on ARM A (corpus alone, `silent_ledger_store_provider`) and were caught only by ARM B's content-asserting provider (`runs/ex4-run4/scoring.md:33,35`) — a real, cited example of a class the corpus-alone instrument demonstrably misses: anything whose only symptom is what got persisted, not what the projected in-memory state shows. What the artifact's own evidence says the whole approach misses as a class: `journal_memory.py:7-21` documents that a fault living inside an adapter with no composition point pointing at it "survives every instrument including the hand-written suite" — the entire reason `reference_ports/` was built. And concretely inside this scope, `ex4`'s own `LedgerStorePort` fake was never completed (`NotImplementedError` on `persist`), so any fault that could only be caught by a fake/real conformance check on that specific port could not have been caught by anything in this tree — it is untested by construction, not by result.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `examples/validation/ab/reference_ports/README.md:8-12,38-45`

**Note:** There is no baseline for `examples/validation` itself — no prior commit or prior version of this directory was supplied, and I found no artifact in scope that treats the directory as a whole as a before/after subject. That absence is the answer to this note, not a gap in it, per the instructions accompanying this card. Inside the scope, individual sub-projects carry their own internal preservation claims about *other* things: `ab/reference_ports/README.md:8-12` claims the ported `quota_ledger.py`'s behavior is `../reference/quota_ledger.py`'s "behaviour, statement for statement," and lines 38-45 say the claim is checked by running the one unedited shared suite against the flat reference, the real wiring and the fake wiring, requiring green on all three before any mutant is admissible. That is a behavior-preservation claim about the quota-ledger *feature* surviving a port-introducing refactor, not about `examples/validation` surviving anything — I did not re-run it myself to confirm it (see judging practice), so I am citing it as a documented claim in scope, not as something I independently verified still holds.

### N-D5 — honesty

**Citations** (`file:line`):

- `examples/validation/instruments/demonstrate.py:33-46,379-389`
- `examples/validation/ex6_jenga/README.md:14-37`
- `examples/validation/ex4_pipeline_coherent/generated/pipeline_contract/fake.py:18-21`

**Note:** Yes, refusal is present and cited, in more than one independent mechanism. `instruments/demonstrate.py:42-46` states of itself, in the file: "THIS IS NOT A GATE. It refuses nothing about the repository's design," and lines 33-40 make "the count of things our instruments cannot see" the thing the tool reports as its product rather than something to minimize; lines 379-389 name a specific, concrete blind spot by hand ("a repo tripwire that is a pytest FILE... has neither [a `__main__` guard nor a nonzero exit path] and is invisible to it") instead of leaving it for a reader to discover. `ex6_jenga/README.md:14-19,25-37` documents an architecture check that returns `unmappable` / the `unfalsifiable_coherence` refusal on a god-state model with a declared partition, rather than emitting a false `coherent`. And narrowly, `ex4_pipeline_coherent/generated/pipeline_contract/fake.py:18-21` raises `NotImplementedError` for an unimplemented fake method rather than silently no-opping it into a false pass. I did not find a case in what I read where the artifact certified something it could not see; where it names a limit, the limit is specific and cited, not generic disclaimer language.

## Verdict

The demonstrated real-adapter-and-fake port swap in `ab/reference_ports` (D3 = 4) is genuine and runtime-verified, but a reader should not extend it to the rest of this 85-module, 14,207-line scope, which also contains declared god-state fixtures (`ex3_over_complex`, `ex6_jenga`) that keep D2 at 1 and an unfinished fake on `ex4`'s own `LedgerStorePort` that the toolchain never exercises.

## Disclosures

- I read a verbatim quotation of the `BA-B14` finding from `specs/results/scorecards/hexagonal-prompting/FINDINGS.md`, reproduced inside two in-scope files: `examples/validation/ab/reference_ports/journal_memory.py:9-15` and `examples/validation/ab/reference_ports/README.md:20-24`. I did not open `FINDINGS.md` itself, and the quoted text names a different, already-named prior epic's arm-B result — it does not identify artifact `GG` or pre-answer a dimension score on *this* card. I am disclosing it because the instructions ask for anything touching "prior results about these dimensions," and this does, even indirectly and even though I reached it entirely inside my declared scope.
- I did not read `references/eval_scorecard.md`, any other `scorecard.json`/`scorecard.md`, any `UNBLINDING*`, `SEALED-BEFORE-DISPATCH.md`, `INSTRUMENT-LOG.toml`, or `RESULT.md`, and I did not open `examples/validation/scorecards/subjects.toml` at all. I read `examples/validation/scorecards/score_tools.py` only for its module-level structure (grepping for global/instance state as code I am scoring), never for anything that would map `GG` to an arm.
- I ran no code, no test, and no script of my own against this tree; nothing in the working tree was changed.
- What I rejected: scoring D2 and D3 as a flat average over the whole declared scope, which would have meant either crediting the whole 85-module tree with D3 = 4 on the strength of one fixture (the single-example-generalization mistake), or scoring D3 down to 0-1 because two unrelated, declared-bad fixtures exist somewhere in the same directory. I treated D2's "no god-state" clause as a blanket claim about the declared scope (falsified by `ex3_over_complex`, hence D2 = 1) and D3's "declared boundaries are followed" clause as a per-domain claim (satisfied by the one fully-evidenced instance, hence D3 = 4) because that is what the anchors' own wording asks for in each case — I flagged that asymmetry explicitly above rather than silently picking whichever reading produced a rounder number.
