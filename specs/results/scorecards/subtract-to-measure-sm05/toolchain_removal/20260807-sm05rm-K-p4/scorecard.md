# Scorecard — toolchain_removal, artifact `K`, judge pass 4

`run_id`: `20260807-sm05rm-K-p4` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `K`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. How to read it against your judgement is one of the numbered scoring rules below.

## The rubric you are scoring against

**This is the whole rubric, and it is reproduced here so the bar for a score sits in the same file as the score.** Do NOT go and read `references/eval_scorecard.md`. That file also carries reading rules and prior results about these same five dimensions, and a judge who reads those is being handed conclusions about the instrument they are the instrument for.

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

**Executed own faults:** false

**What was run:**

- No fault was seeded or executed by me; I scored the packet's pre-recorded mutant runs.
- Static-only commands against copies of the two staged trees: `diff` of `scripts/run_generated_case_adapters.py` before vs. after; `grep`/`find` over both trees for import edges (`spec_double_compiler/*` vs. `scripts/*`), the `[ports.*]` TOML-reader asymmetry, and detector-name definitions in `examples/validation/gap_mutants/run_gap_mutants.py`.
- Read (not executed): `references/case_modules.md`, `tests/test_card_has_one_home.py`, `examples/validation/gap_mutants/run_gap_mutants.py`, `scripts/run_generated_case_adapters.py` (both trees), and the raw JSON in `data/`.

## Your scores

### D1 — bug detection

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `data/gap-mutants-before.json:276-341` — `SM-GM-CTRL-A-commit-credits-one-too-many`, detector `corpus-action-bound:fake`: model-derived generated cases kill a domain value fault with a content assertion (`"committed: expected {'t1': 1, 't2': 0}, actual {'t1': 2, 't2': 0}"`), verdict `DIES`. Confirms anchor 2 (content, not shape) for the mechanism as it stood at the before commit.
- `after/scripts/run_generated_case_adapters.py:1148` — the same content-comparison assertion (`"adapter after-state mismatch for {case.name}: {detail}"`) is present unchanged in the after tree, so the code path that produced the above kill still exists post-change.
- `data/gap-mutants-before.json:962-971` — `SM-GM-P1`, detector `corpus-port-swap:fake`: a model-derived case corpus kills an **ordering** fault (`"ledger: expected (('CLOSE','t1',0),('CLOSE','t2',0)), actual (('CLOSE','t2',0),('CLOSE','t1',0))"`) — the class the whole-view corpus is documented as reaching poorly (anchor 3's bar), at the before commit.
- `data/gap-mutants-after-SM-02.json:250-274` — after the removal, that same class of check (`corpus-port-swap:*` **and**, collaterally, `corpus-action-bound:*`) reports `CONTROL_RED` with `"executed": 0` for this fixture, not a kill. The only detectors still killing `SM-GM-P1`/`SM-GM-P3` post-change are `pytest-full`, `suite-fake` and `portswap-suite-fake` — all named as hand-written in `after/references/case_modules.md:451-454` (`"the hand-written suite driven through ... quota_ledger_fake.py, four lines, no binding table"`).

**Refuses to claim** (required and non-null for a score of 4): n/a (score below 4)

**Rationale:** Anchor 2 is clearly met: model-derived generated cases with adapters that assert content (not merely shape) kill a wrong-value domain fault, and the code path doing so is unchanged in the after tree. Anchor 3 (a fault class the whole-view corpus structurally can't reach — here, ordering) *was* met by model-derived cases at the before commit (`corpus-port-swap:fake` on `SM-GM-P1`), but the packet's own after-the-change measurement (`gap-mutants-after-SM-02.json`) shows that exact model-derived path going `CONTROL_RED` — zero cases executed — for the fixture in evidence, with the catch now carried only by hand-written suites. I read this literally rather than charitably: the evidence I have does **not** show a model-derived case catching a hard-class fault *in the after tree*. That caps this at 2. I could not tell, from what's in the packet, whether other fixtures elsewhere in the repo still exercise a model-derived ordering/refusal catch post-change (`references/case_modules.md:469-474` says the port corpus generation itself — `--port-cases`, `--negative-cases` — was not removed and still reaches 83.2% executable and owns guard-relaxation 3-of-3), so I am not claiming the whole toolchain lost this capability, only that the evidence in front of me doesn't demonstrate it for the mechanism under test. Anchor 4 is not reachable given that gap.

### D2 — complexity

**Score:** 3

**Citations** (`file:line` — the bar is in the scoring rules above):

- `data/descriptor-before-3f58aca.json:1624` vs. `data/descriptor-after-f49a1c9.json:1619` — `scripts/` `code_lines` 21252 → 21027 (−225, −1.06%); matching EVIDENCE.md §3's `branch_points` 3272→3228 and `callables` 803→797, both before/after figures recorded from one instrument run on both trees.
- `before/scripts/run_generated_case_adapters.py:81,85,91` — the deleted state was narrowly scoped: three fields (`binds`, `port`, `fake`) on one dataclass, written at exactly one site (`before/scripts/run_generated_case_adapters.py:299-330`), not a value threaded through the module.
- `data/gap-mutants-after-SM-02.json:250-274` and `after/references/case_modules.md:448-460` — the effect of the removal was measured, including its cost, not just its size: "zero unique kills across 28 tables" and `SM-GM-P3` "survived all six columns the machinery owned."

**Refuses to claim** (required and non-null for a score of 4): n/a (score capped below 4; see D4)

**Rationale:** The removed state was small and singly-written, consistent with proportional complexity rather than a god-object (anchor 2). A simplification was made and both before/after figures for it are recorded (anchor 3) — the packet does this at the file level (§3) and I additionally traced the specific fields and the single write-site removed, so this isn't just "a metric dropped." I am explicitly **not** reading the drop as free evidence of anything: EVIDENCE.md's own summed total across the three code-carrying trees rose by 1677 lines (mostly new test/measurement infrastructure — `tests/test_gap_mutants.py`, `tests/test_card_has_one_home.py`, `gap_mutants.toml`), so the "toolchain" as a whole did not get smaller; a 225-line, single-mechanism cut in `scripts/` was paid for with a much larger investment in harnesses that measure and guard that cut. That is a defensible trade (self-verification infrastructure is a different kind of complexity than domain god-state) but it means "the design is as simple as its behavior requires" is true of the cut component, not of the change as a whole, and I say so rather than let the headline −225 stand for the whole. Anchor 4 needs D4 ≥ 3, which I did not reach (see D4), so this stops at 3.

### D3 — modularity

**Score:** 3

**Citations** (`file:line` — the bar is in the scoring rules above):

- `after/spec_double_compiler/runtime.py:1-8`, `after/spec_double_compiler/effects.py:3-6` — the domain package imports only `__future__`, `importlib`, `contextlib`, `dataclasses`, `pathlib`, `types`, `typing`, `hashlib`, `json`: no I/O, no `scripts`/`tests` import.
- `after/scripts/run_generated_case_adapters.py:1285` (and 555, 994, 1015, 1150, 1199, 1230, 1479, 1506, 1545) — the CLI/adapter-runner imports *from* `spec_double_compiler`, never the reverse (`grep -rn "import scripts\|from scripts" spec_double_compiler/` returns nothing).
- `after/scripts/run_generated_case_adapters.py:207-223` — `[actions.<label>].adapter = "module:object"` is read from a mapping table and instantiated by name; the specific swap I name: pointing that string at `examples/validation/ab/reference_ports/journal_memory.py:InMemoryJournal` vs. a different implementation module changes which adapter runs without touching `spec_double_compiler/` at all.

**Refuses to claim** (required and non-null for a score of 4): n/a (see rationale — anchor 4's specific evidence was withdrawn by this change, not merely absent)

**Rationale:** The domain/adapter import direction is clean and verified at runtime-relevant call sites, not just by directory naming, and I named a concrete swap (anchor 3). I did **not** award anchor 4. Before this change, anchor 4's exact bar — a driven port exercised by a real adapter *and* a fake, same cases passing against both — was met by `--wiring real|fake` over a `[ports.*]` table (`before/scripts/run_generated_case_adapters.py:76-91,299-330`). This change deleted that mechanism specifically because measurement showed it added nothing (`after/references/case_modules.md:448-460`). What still produces `corpus-port-swap:*` results post-change is `run_port_swap.py`, invoked from a path under `specs/results/scorecards/ports-as-adapters/GOAL-port-reach/measure/` (visible in `data/gap-mutants-before.json`'s recorded `argv`) — i.e. the epic's own measurement apparatus, not a script shipped under `scripts/`, `tests/`, or `examples/validation/` the way the rest of the scored toolchain is. I am not confident that counts as "the artifact" rather than "the harness measuring the artifact," and for the fixture in evidence it is now `CONTROL_RED` anyway (see D1). So: the swap-with-a-fake capability that would support anchor 4 is not demonstrated, on the evidence given, to be part of what a user of this toolchain gets after the change.

### D4 — behavior preservation

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `data/gap-mutants-before.json` and `data/gap-mutants-after-SM-02.json` / `-SM-03.json` — 9 gap mutants + 2 positive controls enumerated in one catalogue (`examples/validation/gap_mutants/gap_mutants.toml`) and re-run after each change; `data/dup-mutants-before.json:37-165` / `data/dup-mutants-after.json:38-89` — 4 more, enumerated and re-run for change (c). This is a real enumeration (anchor 2's first clause).
- `data/gap-mutants-after-SM-03.json:367-415` — `SM-GM-I3` flips from survived-by-both-available-detectors (before) to killed by both `pytest-full` and `registry-enumeration` after change (b): a previously-missed behavior is now shown to hold, not merely unchanged.
- `data/gap-mutants-after-SM-02.json:250-274` — but 4 detector columns (`corpus-action-bound:fake/real`, `corpus-port-swap:fake/real`) go from a determinate `DIES`/`SURVIVES` before the change to `CONTROL_RED`, `"executed": 0` after — including on `SM-GM-CTRL-A`, a **domain** fault unrelated to ports. Whatever those columns used to show still holding is no longer shown to hold; it's shown *undecided*.
- `data/dup-mutants-after.json:38,84` — only 2 of the 3 previously-uncaught dedup faults (`M1`→`A1`, and a new `A2`) are demonstrated fixed; `M2` (`build_evidence_packets.py`) and `M3` (`score_tools.py`'s `_skeleton_md`) are not re-tested with an equivalent reintroduced mutant in this packet, so I cannot say those two specific gaps are closed, only that the file `after/tests/test_card_has_one_home.py:102-105,136-143` claims `build_evidence_packets.py` is in-scope now.

**Refuses to claim** (required and non-null for a score of 4): n/a (score below 4; see `judging_practice` — anchor 4 needs `executed_own_faults: true`, which this card does not have)

**Rationale:** The baseline behaviors are enumerated in a real catalogue and most are shown still to hold, with one improvement (`SM-GM-I3`) and one pre-existing, documented, unaffected miss (`SM-GM-I2`, whose own author already recorded it perturbs a reported field rather than the refusal path it targets). That supports anchor 2, mostly. I did not award it cleanly because a real subset — 4 columns, including a check on a fault that has nothing to do with what was removed (`SM-GM-CTRL-A`) — moved from "shown to hold" to "undecided" as a side effect of the change, and that is disclosed rather than hidden but is still a real gap in "each is shown still to hold." I considered anchor 3 (model-derived check) and rejected it: the gap-mutant catalogue that does most of the enumerating here is a hand-curated fault table (each entry has a hand-written `edit`/`find`/`replace` and a hand-written `claims_to_catch`), not a corpus generated from the TLA+ model or a TLC invariant, even though some of the *detectors* it drives (`corpus-action-bound`, `corpus-port-swap`) do run model-derived cases. I think this is a place where the anchor's language ("a corpus, a TLC invariant") was written with the generated-spec-doubles artifact in mind and fits awkwardly onto a mutation-testing harness built to price a removal — I'm scoring what's in front of me rather than stretching the anchor to fit, and saying plainly that the fit is imperfect. Anchor 4 is unreachable on this card because I did not execute a fault myself (`judging_practice.executed_own_faults = false`); I would score the artifact's *claim* to anchor 4 as plausible (the whole catalogue is built on exactly this method) but I did not verify it, so I do not award it.

### D5 — honesty

**Score:** 4

**Citations** (`file:line` — the bar is in the scoring rules above):

- `after/scripts/run_generated_case_adapters.py:308-312` — `render_oracle_statement`'s docstring states, in the shipped source, the measured reason for the removal: *"zero unique kills across 28 tables"* and that `SM-GM-P3` *"survived all six of the swap's own columns at 1543 executed cases each while dying to the hand-written suite."* This is a result unflattering to the mechanism this artifact's own before-state carried — recorded, not omitted.
- `after/references/case_modules.md:459-460` — *"The swap could not detect that its own fake was not a fake — the one failure a port swap exists to make impossible."* Same result, stated a second, plainer way.
- `after/examples/validation/gap_mutants/run_gap_mutants.py:51-54` — the verdict rule itself refuses a false clean: *"a column whose control is red is reported `CONTROL_RED`, never `SURVIVES`"* — and `data/gap-mutants-after-SM-02.json:250-274` shows this rule firing for real, on 4 columns, rather than the harness staying silent about its own broken state.
- EVIDENCE.md §5 (packet, not tree, but reporting an artifact-stated fact) / the after tree's registry-enumeration code — the derived instrument walk names its own blind spot unprompted: a `__main__`-guard-plus-nonzero-exit predicate is invisible to pytest-file tripwires, and six such files are named as existing.

**Refuses to claim** (required and non-null for a score of 4): The derived registry walk refuses to claim it can see repository tripwires implemented as pytest files rather than `__main__`-guarded scripts — it names the predicate that misses them and counts six files it cannot see (EVIDENCE.md §5, corroborated by the registry-enumeration behavior in the after tree).

**Anchor reading** (required at 3 or 4; `disclosure` or `measured`): measured

**Rationale:** This clears anchor 3 easily — `CONTROL_RED` is exactly "unobservable rather than a false clean," demonstrated firing in the actual after-commit data, not just declared as a policy. For anchor 4 I used the **measured** reading deliberately, not the disclosure reading: "zero unique kills across 28 tables" and "survived all six columns" are results the artifact's own predecessor state was measured against and failed, and that failure is what's cited in the shipped source as the reason for the change — this is stronger than a stated limitation, it's a demonstrated failure of the thing being scored (the before-state machinery is squarely part of "the artifact... presented at two commits"). I considered the disclosure reading (the pytest-file blind spot, or `CONTROL_RED` itself) and decided that material better supports anchor 2/3, which is where I used it; I did not want to spend the same evidence twice under different labels.

## Verdict

The removal is honestly measured and mostly paid-for, but the evidence given does not show the toolchain's model-derived (as opposed to hand-written) detection still reaching the hard fault classes after the cut, and a non-trivial side effect — a domain-fault detector column going from a decided kill to `CONTROL_RED` — was disclosed but not closed.

## Disclosures

- I read `after/references/case_modules.md` in full (not just the excerpt EVIDENCE.md pointed at); it restates, in its own words, the same "zero unique kills" / "SM-GM-P3 survived all six columns" result that I also found via the raw JSON. I did not treat the prose as evidence on its own (rule 1) — every claim I cite from it is one I independently confirmed against `data/gap-mutants-*.json` or the source. Disclosed per §1's instruction, though this file is not one of the four named there; it is `references/case_modules.md`, not one of the four exempted paths, but it was present (unredacted) in both trees and is plainly in-scope source, not epic bookkeeping, so I read it without hesitation and don't believe it crosses the line in §1/§2 of the dispatch.
- I did **not** learn or infer which arm (`K`) maps to which named epic mechanism beyond what EVIDENCE.md §2 already tells every judge (it names the four changes neutrally). I made no attempt to find `references/eval_scorecard.md`, `*EPIC*.md`, or any other judge's card, and did not list or open anything under `/Users/hayde/IdeaProjects/wt-epic-subtract-to-measure-SM-05/` outside my own `CARD_DIR`.
- What I rejected: I nearly scored D1 at 3, reasoning that the port corpus generation itself (`--port-cases`, 83.2% executable, per `case_modules.md:469-474`) "obviously still works" so the ordering-class catch "must" still be reachable somewhere in the full repo. I put that down — the packet's own after-the-change JSON shows the specific model-derived columns for the fixture in evidence going `CONTROL_RED`, and scoring on what I'd guess is true elsewhere rather than what's shown is exactly the thing rule 1 exists to prevent. I recorded the gap instead of smoothing over it.
- I also nearly scored D3 at 4 on the strength of `corpus-port-swap:fake`/`:real` still appearing as named columns in the after-state JSON (evidence a real/fake comparison still runs somewhere). I put that down too, once I traced the invoking script's path in the recorded `argv` to `specs/results/scorecards/.../measure/run_port_swap.py` — i.e., the epic's measurement harness, not a shipped part of `scripts/`, `tests/`, or `examples/validation/`. Reasonable people could disagree on where the artifact's boundary is drawn here; I said so rather than picking silently.
- I did not seed or run a fault of my own (`judging_practice.executed_own_faults = false`). Given the packet already contains extensive before/after mutant re-runs produced by the artifact's own harness, and reproducing a ~450s full-suite run plus a `git archive`-staged mutation pass was not something I could do reliably against a redacted, non-git tree in the time available, I chose to score the evidence packet rather than approximate a re-run. This caps D4 at 3 regardless of other evidence, per rule 8, and I landed at 2 on separate grounds anyway.
- D2's anchor-4 caveat (MF-020) gave me pause on the headline `scripts/` −225 lines: I checked the *other* two code-carrying trees rose by 1677 lines net before deciding 3 was earned rather than assuming the drop spoke for itself.
