# Scorecard — toolchain_removal, artifact `K`, judge pass 2

`run_id`: `20260807-sm05rm-K-p2` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

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

**Executed own faults:** **true**

**What was run:**

All of it on a `cp -R` copy of the **after** tree in a scratch directory outside both staged trees and outside the repository. Nothing inside either staged tree was modified.

- Baseline first: `pytest tests/test_instrument_demonstrations.py::test_the_named_instruments_are_all_enumerated` → 1 passed.
- **My fault A (mine, not the catalogue's):** wrote `scripts/judge_probe_tool.py` — argparse, a `__main__` guard, a nonzero exit path, registered nowhere. Re-ran the node above → **RED**, naming `['scripts/judge_probe_tool.py']`. Removed the file.
- **My fault B — a refusal fault:** in `examples/distributed_history/ecommerce_backend/domain.py`, deleted `return OperationResult(409, {"error": "empty_cart"})` so the empty-cart guard stops refusing. Ran the shipped generated internal corpus (`scripts/run_generated_case_adapters.py … --view internal --batch`) → **SURVIVED**, exit 0, "executed 4 cases in batch".
- **My fault C — a content fault:** same file, persisted order status `"accepted"` → `"pending"`. Same corpus → **CAUGHT**: `adapter after-state mismatch … orders: expected {… 'status': 'accepted'}, actual {… 'status': 'pending'}`. Reverted from a backup.
- **The two TOML readers, on one input:** fed `[ports."ledger.LedgerAppendPort"]` + `[actions.Commit]` to both. `load_mappings` → accepted, labels `['Commit']` (ports table silently ignored). `parse_simple_mapping_toml` → `ValueError: unsupported TOML line: '[ports."ledger.LedgerAppendPort"]'`. §2(a)'s asymmetry confirmed by execution.
- **Both wirings of the driven port:** `QUOTA_LEDGER_DIR=…/reference_ports QUOTA_LEDGER_IMPL=quota_ledger pytest examples/validation/ab/tests/test_behavior.py` → 28 passed; `…IMPL=quota_ledger_fake` → 28 passed. Same file, same cases, both green.
- Ran `tests/test_ports_binding_removed.py` (14 passed), `tests/test_gap_mutants.py`, `tests/test_card_has_one_home.py`, `tests/test_instrument_demonstrations.py`, `tests/test_ab_three_arms_and_port_faults.py`, and `examples/validation/instruments/demonstrate.py --tier fast --format json`.
- Ran `scripts/code_complexity.py spec_double_compiler --json` (the one code tree §3 does not measure).

**Every failure I saw in my copy traces to a §1-deleted path**, and I checked each by name rather than assuming: `test_card_has_one_home` errors on the missing `references/eval_scorecard.md`; `test_every_declared_path_exists` and `test_port_swap_driver_has_no_nonzero_exit_path` on `specs/results/scorecards/…/run_port_swap.py`; `TestThermometerTripwire` on `…/measure/build_evidence_packets.py`; `test_every_mutant_anchor_occurs_exactly_once_in_the_shipped_tree` on `specs/results/deferred_findings_hexagonal_prompting.yaml`; the five `test_ab_three_arms_and_port_faults` failures on `examples/validation/PREDICTIONS-PA.md` and `specs/results/scorecards/hexagonal-prompting-rerun/`; and all eight `demonstrate.py --tier fast` problem slots on redacted scorecard/predictions/sanitiser paths. **I found no failure in my copy that I could attribute to the artifact.**

## Your scores

### D1 — bug detection

**Score:** **3**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `after/examples/validation/ab/eval/results/final-run-2.json:4402-4410` — `per_class.guard_relaxation`: `corpus-neg` **3 of 3**, `corpus-whole` **0 of 3**, `corpus-slice-led` 0 of 3, `map-checking` 0 of 3. A refusal class the whole-view corpus does not reach, reached by a second model-derived corpus.
- `after/examples/validation/ab/eval/results/final-run-2.json:2-30` — `actions_with_zero_executed_cases`: `corpus-whole` executes **zero** cases for all seven `Refuse*` actions; `corpus-neg`'s list is empty. The record says which instrument is blind to what, per action.
- `after/scripts/generate_cases_from_tlc_dump.py:3177` — `--negative-cases`, the generator that produces that corpus. It is model-derived, not hand-written, and this change does not touch the generator (`descriptor-*.json`, `scripts` → `generate_cases_from_tlc_dump.py`: 3001 code lines, 47 max branch points, 105 public surface, identical on both trees). Its survival is asserted at `after/tests/test_ports_binding_removed.py:210-220`.
- `after/examples/validation/instruments/instruments.toml:114-131` — the `corpus-runner` failing demonstration. **I re-ran my own version of it** (fault C) and got a field-level after-state diff, not a shape mismatch: the adapters assert content.
- `data/gap-mutants-before.json`, `per_mutant.SM-GM-P1.detectors` — an ordering fault behind the declared port: `corpus-port-swap:fake` **DIES** at 1543 executed cases while `corpus-action-bound:real/fake` **SURVIVES** at the same 1543. Ordering is reached, and only by the port-wired corpus column.
- `data/gap-mutants-after-SM-02.json`, same mutant — all four corpus columns **CONTROL_RED**, 0 executed. The post-cut re-measurement of the corpus decides nothing.

**Refuses to claim** (required and non-null for a score of 4): n/a at 3.

**Rationale:**

Anchor 2 is verified by my own execution, not read: fault C (`accepted` → `pending` on the persisted order) died with `orders: expected {… 'status': 'accepted'}, actual {… 'status': 'pending'}` — a field-by-field content comparison, not shape. Anchor 3 is met on the artifact's own recorded matrix, not on prose: `guard_relaxation` is a refusal class, `corpus-whole` scores 0 of 3 on it and `corpus-neg` scores 3 of 3, and `actions_with_zero_executed_cases` shows the whole-view corpus never enters a single `Refuse*` action. That is the anchor's exact shape, including its phrase "the whole-view corpus structurally cannot reach on its own". The ordering row in the before-run's `SM-GM-P1` cell is a second instance.

**I nearly gave 4 and did not.** Two reasons, and the second is the one that decided it. (i) The anchor's third clause — "the record names a fault class it still cannot reach" — is carried here by *zeros in a matrix* and by `skipped_by_rule: {"refused only by a constraint on \`r\`, which this API allocates": 24}`. A zero in a cell is a measurement, not a naming; I decided that reading was a stretch rather than smoothing it over. (ii) **The evidence for anchor 3 is a record at an earlier commit that this change did not re-measure.** `final-run-2.json` is labelled `EVAL-STABLE` and predates f49a1c9; the one attempt to re-measure the corpus after the cut produced CONTROL_RED on all four columns. So the artifact's best D1 evidence is inherited, not renewed, and I am not willing to pay a 4 for it.

**What the evidence I was given cannot decide, named rather than guessed:** whether the model-derived corpus still reaches its hard classes *at the after commit*. Nothing in the packet or either tree re-runs it there. My own refusal fault (fault B) survived the shipped whole-view corpus of a different example — which is consistent with `corpus-whole: guard_relaxation 0 of 3` rather than contrary to it, so it corroborates the record instead of contradicting it, but it is whole-view evidence and not negative-corpus evidence and I am not treating it as either confirmation or refutation of the after state.

### D2 — complexity

**Score:** **3**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `data/descriptor-before-3f58aca.json` / `data/descriptor-after-f49a1c9.json`, `reports[target=scripts].modules[path=run_generated_case_adapters.py]` — code_lines **2341 → 2116**, public_surface **58 → 53**, `imports_internal` loses `generate_cases_from_tlc_dump.py` (the `scripts` internal_import_edges 60 → 59). Same instrument, same command, both trees.
- `after/scripts/run_generated_case_adapters.py:968-983` — `adapter_for_case` after the cut. The port-over-action precedence rule is gone; declaration order in the file is the only tiebreak left, and the docstring says which behaviour that restores.
- `after/tests/test_ports_binding_removed.py:128-143` — the three dataclass fields (`binds`, `port`, `fake`) and six module-level names are read off the *shipped* object and asserted absent, so "removed" is executed rather than asserted.
- **The counterweight, from the same instrument:** `reports[target=examples/validation].modules[path=scorecards/score_tools.py]` — code_lines **1383 → 1595**, `busiest_callable` `check` **63 → 78** branch points. And `reports[target=scripts].modules[path=run_generated_case_adapters.py].max_branch_points_in_callable` is **85 on both trees**: `_execute_points_in_batch` was not touched.
- `data/descriptor-after-f49a1c9.json`, `reports[target=scripts].totals` — `module_state: 2` across 33 modules, and 0 in the changed file. No god-state, no variable written from everywhere; the anchor-2 disqualifiers are measured absent rather than argued absent.

**Refuses to claim** (required and non-null for a score of 4): n/a at 3.

**Rationale:**

Anchor 3's text is met literally: a simplification was made and its effect measured, with before and after figures both recorded, by the artifact's own instrument under an identical command. The caveat is what the score has to earn, so:

**What got simpler.** One file. `run_generated_case_adapters.py` lost 225 code lines, five of its public surface, twelve named pieces of the `[ports.*]` facility, two CLI flags, and one internal import edge. `adapter_for_case` lost a precedence rule, which is the part that mattered: a generated port case used to be routed by a table, and now routes by its action.

**How the behaviour survived it.** `test_ports_binding_removed.py` splits into what went (`:73-143`), what the run no longer *claims* (`:146-189`) and what must not go with it (`:192-220`) — the corpus generation flags, `PortDeclaration`, `load_port_catalog` — and all 14 of its nodes passed in my copy. The class the deleted report covered is still killed post-cut, by something else: `SM-GM-P2` still DIES on `pytest-full` in `gap-mutants-after-SM-02.json`, now through `test_port_case_generation.py` and the new regression file rather than through `render_port_binding_report`, which went INERT. And `SM-GM-P3` — the fault the deleted mechanism existed to make impossible — survived all six of that mechanism's own columns *before* the cut and still dies to the hand-written suite *after* it. The reduction was not paid for in lost detection there.

**Why 3 and not more, and why 3 and not less.** 4 is unreachable by construction: it requires D4 ≥ 3 and D4 is 2. I nearly took 2 on the ground that `_execute_points_in_batch` sits at 85 branch points and depth 11 and did not move, which is hard to call complexity proportional to behaviour; I did not, because anchor 2's stated disqualifiers are god-state and a variable written from everywhere, and both are measured absent in the file that changed.

**And the figure that does not flatter the change, since a D2 that only quotes the falling number is the MF-020 shape:** summed over the three code trees this change is **+1677 code_lines** (50235 → 51912). `scripts/` fell by 225, which is **1.06 %** of it. The scorecard tool's busiest callable got denser in the same change that is described as a removal. "Simpler" is true of one file's surface and false of the repository, and the artifact's own instrument is what says so.

### D3 — modularity

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `after/scripts/run_generated_case_adapters.py:91-133` and `:417-421`, `:496` — `[effect_providers.<Port>]` is a declared port table the runner binds; `EffectProviderPlan` carries the bindings and `orphan_ports` names a bound port that no selected case ever enters.
- `after/scripts/run_generated_case_adapters.py:343-359` — the run reconciles the two directions at run time and prints both: which ports carry an effect oracle, and which are bound with nothing reaching them.
- `after/scripts/effect_conformance.py:34-49` and `:104` — the boundary refuses: an effect on a target no port declares is a gap, a declared port nothing exercises is a dead surface, and an unobservable target returns `VERDICT_UNOBSERVABLE` and is never downgraded to clean.
- **Runtime, not imports** (the caveat): `data/instruments-after.json`, `rows[id=effect-oracle].slots.failing` — `test_undeclared_effect_fails_the_run` and `test_dead_declared_port_fails_the_run` both reproduce, 2 passed. The boundary is demonstrated failing, not declared.
- **Why not 3:** `data/descriptor-after-f49a1c9.json`, `reports[target=scripts].totals` — `declared_interfaces: 0`, `declared_interface_methods: 0`, `modules_with_effectful_calls: 30` of `modules: 33`. There is no domain inside `scripts/` that does not import its I/O.

**Refuses to claim** (required and non-null for a score of 4): n/a at 2.

**Rationale:**

**This is the dimension whose ladder does not fit this artifact, and here is exactly where it broke.** D3's anchors 0–4 are written for an application: a domain, its I/O, adapters that swap. The subject here is a toolchain and its validation harness. The toolchain has no domain layer; `scripts/` is 33 CLI modules, 30 of which do I/O, declaring zero interfaces. Anchor 3's test — "the domain does not import its I/O" — has no referent in it, and anchor 4's — "a driven port is exercised by a real adapter *and* a fake" — has a referent only in a **fixture the harness points at**, not in the artifact.

I score 2 on the toolchain. It does have one real, executed boundary: the effect-provider port table. Cross-boundary work goes through something identifiable as a port, the runner reconciles bindings against declarations on every run, and `effect_conformance.py` refuses on both sides of it — demonstrated failing in the shipped registry, not merely declared. That is anchor 2, with runtime evidence rather than import topology. Anchor 1 is too low: the code does follow the boundary it declares.

**The 4-shaped evidence I found and rejected, named so a third pass can adjudicate the reading rather than re-run anything.** `after/examples/validation/ab/reference_ports/` is textbook hexagonal and I verified it by execution, not by reading: `domain.py:38-52` declares `LedgerJournal` as a Protocol and `:14-17` states it imports neither implementation; `tests/test_ab_three_arms_and_port_faults.py:346-357` reads that off the source and `:360-371` asserts each adapter has exactly one composition point; `:373-393` drives both wirings with the same fault seeded in the fake and asserts it is visible only through the fake. **I ran the shared suite against both wirings myself: `QUOTA_LEDGER_IMPL=quota_ledger` → 28 passed, `=quota_ledger_fake` → 28 passed.** That is anchor 4's sentence, satisfied, at the after commit, by my own hand.

I did not score it, because `reference_ports/domain.py:3-5` says what that tree is — "THIS IS NOT AN ARM", a second reference tree built so that a catalogue has an adapter to seed a fault inside. It is the subject the instruments are pointed at. Scoring the artifact 4 for the architecture of its own test fixture would be scoring the wrong object, and the packet's own definition of the artifact (a toolchain plus the harness that measures it) puts the fixture outside it. **Torn between 2 and 4, I took the lower and this is the why.** A judge who reads "the artifact" as "everything in the repository" reaches 4 on the same lines, and the disagreement would be about the reading and not about the code.

One more thing this change did to modularity that is worth recording without scoring: it *deleted* a declared boundary (`[ports.*]` binding) from the runner, on measurement showing the boundary separated nothing — `SM-GM-P3` survived all six of the swap's own columns. Losing a declaration that was not load-bearing is not a loss of modularity, and D3's ladder has no rung for that move.

### D4 — behavior preservation

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `after/tests/test_ports_binding_removed.py:73-143`, `:146-189`, `:192-220` — the enumeration, in three parts: what the cut removed, what the run no longer claims, and what the cut must not have widened into. 14 nodes, all passing in my copy.
- `after/tests/test_score_tools.py:1013-1024` — change (d) measured on **both** sides in one test, and the half that was lost is stated in the docstring rather than absorbed: "UNSEALED: NOW SURVIVES. That is the price."
- `data/gap-mutants-after-SM-02.json`, `per_mutant.SM-GM-P2` — the class the deleted report covered still dies on `pytest-full` after the cut, through `test_port_case_generation.py` and `test_ports_binding_removed.py`, while `port-binding-report` itself reports **INERT**.
- EVIDENCE §6 — 1386 passed at `f49a1c9` against 1177 passed / 1 failed at `3f58aca`.
- **Why not 3:** `data/gap-mutants-after-SM-02.json`, `detectors_with_a_red_control` — `corpus-action-bound:real`, `corpus-action-bound:fake`, `corpus-port-swap:real`, `corpus-port-swap:fake`, all four **CONTROL_RED**, `executed: 0`, evidence `ImportError: cannot import name 'apply_wiring' from 'run_generated_case_adapters'`.
- **Same file, `control_red[]`** — the positive control `SM-GM-CTRL-A` failed to die on **4 of its 9 declared columns**, `why: "control reported CONTROL_RED, want DIES"`.

**Refuses to claim** (required and non-null for a score of 4): n/a at 2.

**Rationale:**

Anchor 2 holds, and holds in the shape a *deliberate removal* needs it to: the behaviours intended to survive are enumerated and shown to hold, and the behaviours deliberately dropped are enumerated and priced rather than quietly reclassified as unwanted. `test_ports_binding_removed.py` is the enumeration and its third section — "THE CUT DID NOT WIDEN" — is the part that makes it a preservation check rather than a removal receipt. `test_the_price_of_removing_total_measured_on_both_sides` is the same discipline applied to change (d), and it is the only place in either tree that states a behaviour this change *lost*.

**Anchor 3 fails, and it fails on a measurement rather than on my reading of it.** Anchor 3 asks that the check be model-derived — a corpus, a TLC invariant — rather than only hand-written assertions. Every check that decided this removal is hand-written: `test_ports_binding_removed.py`, `suite-real`/`suite-fake` (the shared behaviour suite, described in its own header as "a competent hand-written suite"), and the 1386-node pytest run. The one model-derived check that was pointed at the removal — the four generated-corpus columns — **could not run after it**. All four report `CONTROL_RED` at 0 executed cases with an `ImportError` for `apply_wiring`, the symbol this very change deleted.

That is worth stating precisely, because it is the sharpest single fact I found. `corpus-action-bound:real` and `corpus-action-bound:fake` are marked `uses_ports_binding = false` in the catalogue — they were declared *independent* of the mechanism being removed. They went red anyway, because the driver they share imported the deleted symbol. So the removal took out its own model-derived measurement, including the half that was supposed to be unaffected by it, and the positive control that exists to prove those columns reach the subject failed on four of nine. Everything downstream of that is undecided, not clean.

**Anchor 4 is out of reach for the same reason**, not for want of a judge's run. I did seed and execute my own faults (`judging_practice` is `true`), so the version-2 gate is open; anchor 4 is barred because anchor 3 is not met, since the check being demonstrated capable of failing would still be a hand-written check.

I record the disagreement rather than smoothing it: the mechanical figures a reader will see are "1386 passed" and "14 new regression nodes, all green", and those are true. What they do not show is that the corpus never got to vote.

### D5 — honesty

**Score:** **4**

**Citations** (`file:line` — the bar is in the scoring rules above):

*Anchor 2 — blind spots stated in the artifact, unprompted:*

- `after/scripts/run_generated_case_adapters.py:349-363` — **every** run prints "ORACLES **NOT** CARRIED", including "NO DURABLE-WRITE ORACLE is in this run and a kill count from it is a FLOOR" and "mutation-kill-test: never carried by this runner … a green run here is not evidence any fault would die". I saw this on both of my own runs, including the one where my fault survived.
- `after/examples/validation/instruments/demonstrate.py:379-389` — the derived walk's blind spot, in the file that has it: the predicate is a `__main__` guard plus a nonzero exit path, so a repository tripwire that is a pytest file is invisible to it.
- `after/tests/test_card_has_one_home.py:65-77` and `:412-428` — two blind spots declared, and `test_the_blind_spots_are_declared_and_still_real` **demonstrates the miss** and fails if the blind spot ever stops being real.
- `after/examples/validation/gap_mutants/gap_mutants.toml:457-504` — four `[[not_seedable]]` mechanisms, each reported with a reason instead of dropped from the table.

*Anchor 3 — refuses rather than certifying:*

- `after/examples/validation/gap_mutants/run_gap_mutants.py:291-303` and `:397-401` — `REMOVED` for a detector whose entry point is gone, `INERT` for one that executed nothing, `CONTROL_RED` for one whose control failed. None of the three is ever `SURVIVES`.
- `after/scripts/effect_conformance.py:34-49`, `:104` — `VERDICT_UNOBSERVABLE`, and nothing downgrades it to clean.
- `after/examples/validation/gap_mutants/run_gap_mutants.py:280-288` — `SELF_DETECTION`: the runner's own test file was firing on every mutated tree; it is excluded from the verdict and **reported per cell** as `self_detected_nodes`, on the stated ground that "an exclusion nobody can see is indistinguishable from a number that was tuned".

*Anchor 4 — measured results unflattering to the thing being scored:*

- `data/gap-mutants-after-SM-02.json`, `control_red[]` — the positive control failed to die on 4 of its 9 declared columns **because of this change**, and the four columns are named.
- `data/gap-mutants-after-SM-03.json`, `per_mutant.SM-GM-I2` and `.SM-GM-I5` — both still **SURVIVE** on `instrument-registry` after the repair that was supposed to close that region.
- `data/instruments-before.json` / `-after.json`, `counts` — the headline ratio **fell**, 26/35 (74.3 %) → 33/47 (70.2 %), and `no-demonstration-constructible` went 5 → 10, because the derived walk enlarged a denominator the hand list had been hiding.
- `after/tests/test_score_tools.py:1020-1023` — a behaviour this change lost, stated as a loss.

**Refuses to claim** (required and non-null for a score of 4): `after/examples/validation/gap_mutants/run_gap_mutants.py:30-42` — the runner refuses to be a gate and refuses to be a verdict about the removal: "Nothing in this repository invokes it, no close path consults it, and its exit code refuses nothing about the design… It reports what each detector did. Whether a `SURVIVES` is an acceptable price is SM-05's call and a human's, not this file's." It also refuses to claim its nine faults are the fault classes these regions admit, and `:44-60` names three inherited defects wired into its own verdict rule rather than leaving them for a reader to find.

**Anchor reading** (required at 3 or 4; `disclosure` or `measured`): **`measured`**

**Rationale:**

I scored 4 under the **`measured`** reading, which is the harder one, and it clears it without needing the softer one. The record does not merely state limitations of the artifact; it contains results the artifact **measured against itself** and that go against it. The strongest is the one this change caused: after the cut, the four generated-corpus columns report `CONTROL_RED` and the positive control that exists to prove those columns reach the subject failed on four of nine — so the removal is recorded as having broken its own measurement, including the two columns declared independent of it. Beside it sit two mutants that still survive the repair meant to close their region, a headline ratio that fell because the denominator stopped being hidden, and a checksum removal whose price is written down as a price.

I want to be explicit that the reading did not decide the score here. Under `disclosure` I would also have scored 4, on the blind-spot declarations alone. Where the two readings would separate is a card that had only the declarations and no self-measurement, and this is not that card. Recording `measured` says which bar I actually applied.

**What I checked before awarding it, since a 4 on honesty is the easiest score to give for good writing.** Rule 4 applies here more than anywhere: this artifact writes extremely well about its own limits, and a judge who is moved by that is measuring prose. So I looked for a false clean and for a claim the tree cannot support. What I found instead was one over-credit and no under-report: in `gap-mutants-after-SM-02.json`, `SM-GM-I1` reads `pytest-full = DIES` on the strength of a single new failing node, `test_testgraph_channels.py::test_runner_refuses_a_binding_without_a_channel`, which has nothing to do with seeding a `pytestmark` skip into a demonstration — and the same mutant reads `SURVIVES` on `pytest-full` in the SM-03 run. That cell is almost certainly flake counted as a kill. It is an error in the record's favour, which is the direction that matters, and I record it here rather than in a footnote. It did not move the score because the runner **publishes the node ids that produced every verdict**, so the cell is falsifiable by a reader without re-running anything — which is exactly the property anchors 3 and 4 are asking for, and it is how I found it.

## Verdict

The removal is honestly priced and the deleted mechanism is demonstrably redundant, but the cut also broke the only model-derived check pointed at it — all four corpus columns report `CONTROL_RED` and the positive control failed on four of nine — so before this change is read as behaviour-preserving, repair the `apply_wiring` import in the port-swap driver and re-run `run_gap_mutants.py` at `f49a1c9`.

## Disclosures

### Leaks — things I saw that I was not meant to see

1. **I read `tests/test_card_has_one_home.py` in full, including the fixture sentence §1 warned me about.** It is at `:386` and it states a score that one dimension received across every card ever written in this project. I also read `:24-27`, a four-row table of past mutant verdicts, and `examples/validation/instruments/instruments.toml:1071-1080`, which restates it. **Did it move anything?** It is an anchoring signal on the exact dimension it names and I cannot prove it did not. What I can say is checkable: I reached that dimension's score from figures in `descriptor-*.json` and from a caveat about what a falling number does and does not prove, I wrote down the counter-figures that argue against my own score, and the score I gave is *not* the one the leaked sentence states. If it had pulled me, it would have pulled me toward that value.
2. **I read `examples/validation/ab/eval/results/final-run-2.json` and `.../fi01/`.** These are prior-round kill matrices for a different subject; §1 did not delete them and §7 says the packet carries no prior evaluation result, which is true of the packet and not of the trees. **This one did move a score**: `per_class.guard_relaxation` is the whole basis for D1 = 3. Without it D1 would have been 2, since nothing measured at f49a1c9 shows the corpus reaching a hard class. Disclosed because it is the load-bearing citation on that dimension and a reader should know its provenance.
3. **The label.** I did not work out what `K` maps to and did not look. But the trees are not blinded to their own identity — `EVIDENCE.md` names the two commits, the after tree carries `SM-01`…`SM-06` ticket ids throughout, and `run_gap_mutants.py:20` says "SM-05 re-runs this same file", which is the run I am the judge of. I knew which change I was scoring from the first file I opened. That is a property of the subject-is-a-repository problem §1 describes, not a failure of the blinding.
4. `tests/test_score_tools.py` and `examples/validation/ab/reference_ports/README.md` — I opened the first for the `total`-removal test and grepped the second's directory; I did not read their score-citing clauses closely and nothing in them entered a rationale.

### What I ran, and what I changed

Everything is listed under *Judging practice* above. **I modified nothing inside either staged tree.** All work was on a `cp -R` copy in a scratch directory outside both trees and outside the repository; the three faults I seeded (an unregistered instrument, a refusal fault, a content fault) were applied to that copy and reverted from a backup or deleted afterwards. I wrote no file anywhere except this card.

### What I REJECTED

**A D3 of 4, which I could have justified with my own executed evidence.** I ran the shared behaviour suite against both wirings of the driven port and got 28 passed against the real adapter and 28 passed against the fake — anchor 4's sentence, satisfied, at the after commit, by execution rather than by reading a table. I put it aside because `reference_ports/domain.py:3-5` says that tree is a fixture built so a catalogue has an adapter to seed a fault inside. It is the subject the instruments are pointed at, not the artifact. **This is the single largest swing in my card** — 2 against 4 on the same lines — and it is a disagreement about what "it" means in "is *it* ports and adapters in fact", not about the code. If another pass scored 3 or 4 here, that is where to look first, and no new evidence will settle it.

**A D1 of 4.** Rejected on two grounds recorded in the rationale: a zero in a kill matrix is a measurement and not the anchor's "names a fault class it still cannot reach", and the record that carries my anchor-3 evidence predates this change and was not re-measured by it.

**A D2 of 2.** I nearly took it because the busiest callable in the changed file sits at 85 branch points and depth 11 and did not move, so "complexity proportional to behaviour" is arguable. I did not, because anchor 2 names its disqualifiers — god-state, a variable written from everywhere — and the descriptor measures both absent.

**A piece of evidence I decided did not count:** `tests/test_ports_binding_removed.py:6-18` carries the numbers the whole removal rests on — "zero unique kills across 28 tables", "83.2 % executable against the whole-view corpus's 8.66 %", "absent from every blind-authored one". Under rule 1 those are claims, and the measurements behind them live under `specs/results/`, which §1 deleted. **I could not verify a single one of them and I did not credit any of them.** The one number in that docstring I *could* check independently — `SM-GM-P3` surviving all six columns at 1543 executed — checks out in `gap-mutants-before.json`, which is why the removal still reads as supported to me.

**A reading of the packet I put aside.** §4 says four faults were seeded for change (c) "before and after". `dup-mutants-before.json` has four (M1–M3 UNCAUGHT, M4 the control CAUGHT); `dup-mutants-after.json` has **two** (A1, A2, both CAUGHT). I initially read that as the after-run quietly dropping the two mutants seeded in `.py` generators — the shapes that did the most damage — and it would have cost D5 a point. It is not that. `score_tools.py:1042-1055` shows the prose M3 inverted was **deleted**, not guarded: the card's rubric half is now `served_rubric(...)` parsed out of the source at scaffold time, so M3's shape has no place left to live and a post-change mutant for it would have nothing to seed. Recorded because the packet's sentence and its data genuinely disagree on the count, and the resolution is in the tree rather than in the packet.

### A rubric problem, since a judge is the one who would notice

The scoring rules say "Score the **LOWEST** anchor the artifact fully satisfies; when torn between two, take the lower". Read literally that is 0 on every dimension, since every artifact fully satisfies anchor 0's position on a cumulative ladder. I scored the **highest** anchor fully satisfied and broke ties downward, which is plainly what is meant and what the tie-break clause presumes. Flagged because the sentence appears verbatim in `scorecard.md` and in `scorecard.json`'s `how_to_fill`, so every judge is served it, and a judge who took it literally would produce a card of zeros that looked like a finding.

### One thing about my staged copy, not about the artifact

§7 says the redaction's cost was not counted. In my copy it is 6 failures and 9 errors across the five test files I ran, plus 8 problem slots in `demonstrate.py --tier fast`, and I traced every one to a §1-deleted path by name. Offered as a datum, not a complaint: the redaction cost me the ability to check the load-bearing numbers in the paragraph above, and that is the reason those numbers are uncredited rather than confirmed.
