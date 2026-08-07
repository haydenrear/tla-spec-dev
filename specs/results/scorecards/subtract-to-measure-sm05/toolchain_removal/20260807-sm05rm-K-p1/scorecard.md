# Scorecard — toolchain_removal, artifact `K`, judge pass 1

`run_id`: `20260807-sm05rm-K-p1` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

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

**Executed own faults:** true

**What was run:**

- Copied `<TREES>/after/` to a scratch directory outside both trees and the repository. Neither staged tree was modified. All runs used `uv run --with pytest [--with pyyaml] python`, CPython 3.14.6, pytest 9.1.1.
- **Control, real wiring.** `QUOTA_LEDGER_IMPL=quota_ledger` over `examples/validation/ab/tests/test_behavior.py` → **28 passed**.
- **Control, fake wiring.** `QUOTA_LEDGER_IMPL=quota_ledger_fake`, same 28 cases → **28 passed**.
- **JUDGE-F1** (mine; real adapter, content truncation): `journal_file.py` `append` drops the trailing running-total field from every written line. → real **7 failed / 21 passed**, fake **28 passed**.
- **JUDGE-F2** (mine; fake adapter, dropped first entry — deliberately *not* SM-GM-P1's reversal): `journal_memory.py` `lines()` returns `[...][1:]`. → fake **7 failed / 21 passed**, real **28 passed**.
- **JUDGE-F3** (mine; domain, refusal class): the `outstanding_reservations` guard removed from `domain.py` `close_tenant`, so `close_tenant` accepts where it must refuse. → **2 failed / 26 passed under BOTH wirings**.
- **Model-derived corpus, control.** `scripts/run_generated_case_adapters.py` over `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases` (`--view internal --batch`), staged as the `corpus-runner` registry row stages it. → exit 0, "executed 4 cases in batch".
- **JUDGE-F4a** (the registry row's own value fault, re-run by me): order persisted `"pending"` instead of `"accepted"`. → **KILLED**, `adapter after-state mismatch … orders: expected {… 'status': 'accepted'}, actual {… 'status': 'pending'}`.
- **JUDGE-F4b** (mine; refusal class, same corpus): the `empty_cart` 409 guard removed from `checkout`. → **SURVIVED**, exit 0, "executed 4 cases in batch".
- `python scripts/run_generated_case_adapters.py --help` and the runner's oracle statement, read off four live runs.
- I did **not** run `pytest tests -q` on either staged tree. §6 records it on unredacted checkouts and re-running a redacted copy would have produced failures I could not attribute.

## Your scores

### D1 — bug detection

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `<TREES>/after/scripts/run_generated_case_adapters.py:1148` — the kill mechanism: `raise AssertionError(f"adapter after-state mismatch for {case.name}: {detail}")`, a field-by-field after-state comparison, not a shape check. I made it fire (JUDGE-F4a).
- `<TREES>/after/examples/validation/instruments/instruments.toml:114-131` — the `corpus-runner` demonstrated failing input: stage, mutate one persisted field, `expect_exit = 1`, `expect_output = ["adapter after-state mismatch"]`. Reproduced by me at the after tree.
- `<TREES>/after/examples/validation/gap_mutants/gap_mutants.toml:145-168` — SM-GM-P1, the ordering fault. In `data/gap-mutants-before.json` it dies on `corpus-port-swap:fake` — the only **model-derived** column that ever killed a hard-class fault here — and that column is what change (a) deletes.
- `<TREES>/after/examples/validation/gap_mutants/gap_mutants.toml:194-217` — SM-GM-P3, which survived all eight non-`pytest-full` columns before the cut and four of five after it.
- `<TREES>/after/scripts/run_generated_case_adapters.py:351,361` — the runner naming its own reach limit on every run: "NO DURABLE-WRITE ORACLE is in this run and a kill count from it is a FLOOR"; "mutation-kill-test: never carried by this runner … a green run here is not evidence any fault would die".

**Refuses to claim** (required and non-null for a score of 4): n/a at 2.

**Rationale:**

Anchor 2 is satisfied and I verified it rather than reading it. The generated corpus, driven through a bound adapter, killed a wrong-content fault by comparing the persisted record field by field (`status` `accepted` → `pending`); the assertion is on content, and `:1148` is where it is made.

Anchor 3 is **not decided at the scored commit**, and that is the whole of the gap between 2 and 3.

- *Ordering.* The one decided model-derived kill of a hard class in this evidence is `corpus-port-swap:fake` killing SM-GM-P1 at the **before** commit. That column is exactly what the change under score removes. After the cut, P1 still dies — on `suite-fake`, `portswap-suite-fake` and `pytest-full`, all hand-written — so the *fault* is still caught and the *model-derived reach into that class* is not shown to be.
- *Refusal.* I went looking for it myself. I removed the `empty_cart` guard from the example the registry's own row uses and ran the same generated corpus: it survived, exit 0, four cases executed. The corpus that ships with that example carries no negative case that reaches the guard.
- The counter-claim exists — "`--negative-cases` still owns guard relaxation **3 of 3**, a class no other instrument has reached" (`references/case_modules.md:472`, restated at `tests/test_ports_binding_removed.py:16-18,220`) — but it is prose in this packet. Rule 1 says the code is the evidence, and the generation of refusal cases *is* asserted executably (`tests/test_port_case_generation.py:433`, `tests/test_generate_cases_from_tlc_dump.py:711`) while the **kill** is not measured anywhere I was given.
- Compounding it: in `data/gap-mutants-after-SM-02.json` all four corpus columns report `CONTROL_RED`, with the evidence string `ImportError: cannot import name 'apply_wiring'`. The cut deleted a function a measurement driver still called, so every model-derived cell in the after table is undecided by the runner's own — correct — rule. I could not inspect that driver: it lives under `specs/results/scorecards/`, which §1 redacted. Stated rather than guessed.

Torn between 2 and 3; took the lower, because the only evidence that would lift it is a before-commit measurement of a column the change deletes.

Prose quality did tempt me on this dimension. `gap_mutants.toml` is the best-written mutant catalogue I have read and it argues its own limits unprompted; I have scored the cells, not the paragraphs.

### D2 — complexity

**Score:** 3

**Citations** (`file:line` — the bar is in the scoring rules above):

- `data/descriptor-before-3f58aca.json` / `data/descriptor-after-f49a1c9.json`, `reports[target=scripts].modules[path=run_generated_case_adapters.py]` — the whole of the `scripts/` reduction is one module: `code_lines` 2341 → 2116, `branch_points` 473 → 429, `callables` 78 → 72, `public_surface` 58 → 53, `imports_internal` 5 → 4 (`generate_cases_from_tlc_dump.py` dropped). Nothing else in `scripts/` moved.
- `<TREES>/after/scripts/run_generated_case_adapters.py:968-983` — `adapter_for_case`, the precedence rule after the simplification: one sort on declaration order, and a docstring stating what the removed rule used to do.
- `<TREES>/after/tests/test_ports_binding_removed.py:128-143` — the removed surface asserted absent by reading the shipped dataclass fields and by `hasattr` on the module, so the reduction is checked rather than claimed.
- `<TREES>/after/scripts/code_complexity.py:728` — the instrument's own statement that its effect figure "UNDERCOUNTS by construction"; `:587` and `:776` carry the `unresolved_constructs` list (ten `getattr`/`setattr` sites, identical on both trees).
- `<TREES>/after/references/case_modules.md:436-480` — the section kept rather than deleted, stating what the removed mechanism was, what was measured about it, and what replaced it.

**Refuses to claim** (required and non-null for a score of 4): n/a at 3.

**Rationale:**

Measured, reported, and the figures are argued against the design, so 1 is passed. Anchor 2 holds on the descriptor's own state measures: `module_state` is 2 across 33 `scripts/` modules and 0 in the changed module, `instance_state` 31, no variable written from everywhere and no god-state.

Anchor 3 needs *what got simpler and how the behavior survived it*, and both are answerable here without taking anyone's word:

- **What got simpler.** A single feature — the `[ports.*]` binding facility — in a single module. It is traceable to the line: 2341 → 2116, −44 branch points, −5 public names, and one internal import edge gone. This is the one direction the MF-020 caveat warns about (a number falling because an edge was deleted), and here the edge deletion *is* the change, so the caveat is not evaded — it is the subject.
- **How the behavior survived.** Each fault the facility claimed to cover was re-run: SM-GM-P1's kill moves to the four-line fake composition point, SM-GM-P2's to `pytest-full`, and SM-GM-P3 was never caught by the facility at all — it survived all six columns the machinery owned at 1543 executed cases each while the positive control died on those same six in the same run.

I stopped at 3, and there are two independent reasons.

- Anchor 4 is gated on D4 ≥ 3, and D4 is 2.
- Independently, the reduction is **not** behavior-preserving. `render_port_binding_report` was the only executable reconciliation between a binding table and `spec_manifest.yaml`, and it is gone; its detector cell is `INERT` after the cut. The artifact does not pretend otherwise — it prices it — but "priced" is not "preserved".

**Where the anchor did not fit, stated rather than smoothed.** The read_first note asks for variables, actions, state-space bound, R/W density, dense rows — a spec descriptor. This subject is a CLI toolchain and the instrument produces a *code* descriptor, so I mapped state-space onto `module_state`/`instance_state` and dense rows onto `max_branch_points_in_callable`. Under that mapping one figure argues against anchor 2 and I record it: the changed module's busiest and deepest callable is `_execute_points_in_batch` at 85 branch points and depth 11, **identical before and after**. The cut removed a feature; it did not touch the accidental structure the descriptor points at. Two further limits of the measurement, neither of which the packet claims otherwise: the descriptor's four targets do not include `spec_double_compiler/`, which is where the toolchain's actual Protocol ports live, so the package that carries the boundary is unmeasured; and `references/` reports 0 code_lines, so change (a)'s 123 lines of documentation are invisible to it.

### D3 — modularity

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `<TREES>/after/spec_double_compiler/runtime.py:33` — `class EffectProvider(Protocol)`, and `:95` — `class CaseAdapter(Protocol)`. These are the toolchain's ports: the single contract an adapter implements.
- `<TREES>/after/scripts/run_generated_case_adapters.py:1285` — the runner calls across that boundary through `call_adapter`/`instantiate`/`load_object`, i.e. by dotted path resolved at run time, not by import.
- `<TREES>/after/scripts/run_generated_case_adapters.py:968-983` — `adapter_for_case`: which adapter drives a case is decided from the mapping file at run time.
- `<TREES>/after/tests/test_ports_binding_removed.py:93-112` — that resolution exercised as a call: two labels on one case, `load_mappings` + `adapter_for_case`, and the returned binding is `m:Action`. Runtime behavior, not import topology.
- `data/descriptor-after-f49a1c9.json`, `reports[target=scripts].totals` — `declared_interfaces: 0`, `modules_with_effectful_calls: 30` of `modules: 33`, `effectful_calls: 519`. The toolchain's own modules reach `print`, `write_text`, `mkdtemp`, `chmod` directly.

**Refuses to claim** (required and non-null for a score of 4): n/a at 2.

**Rationale:**

Anchor 2 is clearly met: there is a named port (`CaseAdapter`), the code goes through it, and which implementation is behind it is config, resolved at run time by `load_object`. That is not an import check — I watched the resolution happen in a call.

Anchor 3 is not met **for the artifact**. "The domain does not import its I/O" is false of this toolchain: 30 of its 33 `scripts/` modules make effect calls directly and the changed module does its own `mkdtemp`, `chmod`, `write_text` and subprocess work inline. There is no seam at which the runner's own I/O could be replaced.

**This is the dimension where the ladder was written for a different shape of subject, and I am not going to smooth it.** Anchor 4 asks for "a driven port exercised by a real adapter *and* a fake, with the same cases passing against both". That exists here, and I proved it myself: 28 identical hand-written cases pass against `quota_ledger` and against `quota_ledger_fake`; my JUDGE-F1 reddens exactly the real column (7 failed / 28 passed) and my JUDGE-F2 reddens exactly the fake one (28 passed / 7 failed). Anchor 4's text is satisfied on the nose. **I did not award it**, because that port is in `examples/validation/ab/reference_ports/` — a fixture the toolchain *measures against*, checked into the toolchain's repo. Scoring the toolchain 4 for the architecture of its own test fixture scores the wrong artifact, and this rubric's D3 has no rung for "the subject is a measuring instrument whose fixtures are hexagonal and whose own code is a pile of CLIs". Where it broke: between anchors 2 and 3, the ladder silently changes what "the domain" refers to.

One thing a reader should have beside this score. The change under review deletes the toolchain's own `[ports.*]` real/fake swap — the mechanism whose entire product was a demonstration of this dimension's top anchor. It was deleted on measurement that it bought zero unique kills across 28 tables and could not detect that its own fake was a second real adapter. So the artifact's D3-4 *affordance* went down by a deliberate act, and the measurement says the affordance was hollow. That is a finding about this rubric at least as much as about the artifact.

### D4 — behavior preservation

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `<TREES>/after/tests/test_ports_binding_removed.py:137-143` — the six removed entry points enumerated by name in a parametrize and asserted unreachable; `:175-189` runs `--help` and the rejected `--wiring` invocation, so both halves of the removed command line are checked by running them.
- `<TREES>/after/tests/test_ports_binding_removed.py:198-220` — the second claim, kept separate on purpose: `PortDeclaration`, `load_port_catalog`, `--port-cases`, `--negative-cases` asserted still present, so "the cut did not widen" is executable.
- `<TREES>/after/examples/validation/gap_mutants/run_gap_mutants.py:62-71` — verdicts are computed against a pristine staged tree's failure **set**, never an exit code, so a pre-existing red cannot be read as a kill.
- `<TREES>/after/examples/validation/gap_mutants/run_gap_mutants.py:291-295,397-401` — `REMOVED` / `INERT` / `CONTROL_RED` are separate verdicts from `SURVIVES`; a detector that no longer exists is never counted as having failed to catch something.
- `<TREES>/after/tests/test_score_tools.py:1013-1057` — change (d) measured on both sides in one executing test, including the half that got worse.
- `data/gap-mutants-after-SM-02.json`, `detectors_with_a_red_control` — all four corpus columns, reason `ImportError: cannot import name 'apply_wiring'`.

**Refuses to claim** (required and non-null for a score of 4): n/a at 2.

**Rationale:**

Anchor 1 is passed by a distance: 1177+1 → 1386 passing (§6) is present but is the least of the evidence, and the artifact does not lean on it.

Anchor 2 I award, **with the anchor stretched, and here is where it broke.** Read literally — "the behaviors the baseline exhibited are enumerated and each is shown still to hold" — the change under score fails it by construction: it is a *removal*, twelve named pieces are enumerated precisely so they can be shown *not* to hold, and one behavior (`render_port_binding_report`, the only executable reconciliation between a binding table and the manifest) is simply gone. The ladder has no rung between "behavior changed and nobody checked" (0) and "everything still holds" (2), which is the entire space a deliberate subtraction lives in. I read anchor 2 as satisfied by *enumerated, and each re-run against the detector that claimed it, with the ones that no longer hold named and priced* — which is what `run_gap_mutants.py` plus `test_ports_binding_removed.py` plus `test_score_tools.py:1013` actually do. A judge who reads anchor 2 strictly would score this 1, and I would not call that wrong; it would be a disagreement about the anchor, not about the artifact.

Anchor 3 fails on the evidence, and this is the decidable part. It asks for the check to be **model-derived** rather than only hand-written assertions. At the after commit it is not:

- the four model-derived corpus columns report `CONTROL_RED` in the SM-02 re-run, because the cut deleted `apply_wiring` while a measurement driver still imported it;
- every cell that decides anything after the cut is `pytest-full`, `suite-real`, `suite-fake`, `instrument-registry` or `registry-enumeration` — hand-written;
- my own runs land the same way. JUDGE-F3, a refusal-class behavior break, was caught by the hand-written suite under both wirings; my one model-derived run against a refusal (JUDGE-F4b) **survived**.

Anchor 4 is therefore out of reach even though `judging_practice.executed_own_faults` is `true` and the gate is open. I ran the faults, and the running is what showed the model-derived check is not demonstrated capable of failing on the classes at issue at this commit. Recorded as a result, not as a shortfall in the practice.

One provenance limit that bears on the whole dimension and that the packet does not state: the §4 and §5 "after" runs were measured in the SM-02 and SM-03 worktrees, not at `f49a1c9` — the argv in `data/instruments-after.json` names `wt-epic-subtract-to-measure-SM-03`. Only §3 and §6 are at the scored commit. Nothing in this evidence re-runs the gap mutants at `f49a1c9` itself, so whether the `apply_wiring` caller was ever repaired is unknown to me and unknowable from a tree with `specs/results/scorecards/` redacted.

### D5 — honesty

**Score:** 4

**Citations** (`file:line` — the bar is in the scoring rules above):

- `<TREES>/after/scripts/run_generated_case_adapters.py:351,361,370` — every run prints "ORACLES **NOT** CARRIED", naming what this run's mapping does *not* observe, that a kill count from it "is a FLOOR", and that a green run here "is not evidence any fault would die". I saw this printed on all four of my own corpus runs, including the one that survived.
- `<TREES>/after/scripts/effect_conformance.py:182` — `VERDICT_UNOBSERVABLE = "unobservable"`, with `:283` `UnobservableTarget` and `:410` `assess_target_observability`; the docstring at `:23-38` states that observability is granted only on positive evidence and refused otherwise, and that a refused target is "a **failure**, not a clean report". This is anchor 3's wording implemented rather than asserted.
- `<TREES>/after/examples/validation/gap_mutants/run_gap_mutants.py:44-60` — three inherited defects wired into the verdict rule, each named with its finding id, including "a `SURVIVES` with nothing executed is not a survival".
- `<TREES>/after/examples/validation/gap_mutants/gap_mutants.toml:11-16` and `:453-504` — "not a kill catalogue and not a gate … makes no claim about a fault class it does not seed", plus four mechanisms declared *unmeasurable* with a reason each, rather than dropped from the denominator.
- `<TREES>/after/examples/validation/gap_mutants/gap_mutants.toml:552-578` — a positive control's anchor was moved, and the move is disclosed in the catalogue with the reason, the tripwire that caught it, and the sentence "re-anchoring a positive control is one step away from editing a target to match a result".
- `<TREES>/after/examples/validation/instruments/instruments.toml:68-71` and `:1066-1069` — the new derived walk's blind spot declared in the same file that ships the walk: a repo tripwire that is a pytest file has no `__main__` and no exit path, six such files exist, and they are registered by hand.
- `<TREES>/after/examples/validation/instruments/instruments.toml:1071-1085` — **measured against itself**: four disagreeing copies of the card were planted, and the 1378-test suite, `demonstrate.py`, `check`, `audit` and `serve` were green on three of the four. Only the control was caught.
- `<TREES>/after/tests/test_card_has_one_home.py:412-428` — a test that asserts its own declared blind spots are *still real* and fails if one closes, so the admission cannot quietly become false.
- `<TREES>/after/tests/test_score_tools.py:1013-1057` — change (d) priced on both sides in one executing test: sealed, "still dies … the cut was free"; unsealed, "**NOW SURVIVES**. That is the price", asserted as `after_unsealed == []` with a message telling a future reader to re-price if anything ever catches it again.
- `<TREES>/after/references/case_modules.md:448-460` — the removed mechanism's own epitaph: zero unique kills across 28 tables, absent from every blind-authored table, and "the swap could not detect that its own fake was not a fake".
- `<TREES>/after/references/case_modules.md:476-480` — a residue of the cut filed as an open defect (`SM-02-DF-01`) rather than fixed or omitted.

**Refuses to claim** (required and non-null for a score of 4):

That a green run of its own corpus is evidence of anything about faults. The runner states, unprompted and on every invocation, that it carries no durable-write oracle when none is bound, that "a kill count from it is a **FLOOR**", and that the mutation kill-test is "never carried by this runner … a green run here is not evidence any fault would die" (`scripts/run_generated_case_adapters.py:351,361`). Alongside it, `scripts/effect_conformance.py:182` refuses to certify an unobserved target at all rather than certifying it clean, and `gap_mutants.toml:11-16` refuses to claim its nine faults are the fault classes those regions admit.

**Anchor reading** (required at 3 or 4; `disclosure` or `measured`): `measured`

**Rationale:**

Anchor 2 and anchor 3 are met by code, not by a report — the refusal verdicts are constants in the harness and the "not carried" statement is emitted at run time, which I confirmed by running it four times.

Anchor 4 under the **stricter** reading, which is why the reading is worth recording. I did not need to count a stated limitation as an unflattering result; there are at least four results the artifact *measured against itself* and kept:

1. Three of four planted disagreeing copies of the card were missed by the entire suite plus four other instruments (`instruments.toml:1071-1085`).
2. Change (d) made an altered score on an unsealed card undetectable, asserted as an executing test whose failure message asks a future reader to re-price the removal (`test_score_tools.py:1052-1056`).
3. The mechanism the epic removed could not detect that its own fake was a second real adapter, at 1543 executed cases per column, while the positive control died on those same columns in the same run (`case_modules.md:457-460`, `test_ports_binding_removed.py:9-12`).
4. The honest denominator got *worse* on the change's own headline figure: instruments with a demonstrated failing input fell 74.3 % → 70.2 % (§5), because the derived walk found executables the hand-written list could not see. A registry optimizing its own ratio would not have shipped that walk.

I record one thing on the other side of the ledger, because a D5 of 4 should carry its counterweight. The evidence packet's §1 claims to be "the entire redaction" and names four files it could not delete; it missed a fifth. `<TREES>/before/README.md:139-162` states the card's five dimensions, six of its scoring rules, and four prior evaluation results for one of these dimensions in a single line. §7 says the packet contains no such thing. This is a defect in the packet and in the redaction, not in the artifact, so it does not move D5 — and it is worth noticing that the copy the redaction missed is precisely the copy change (c) deleted, so the artifact under score had already fixed the leak that shipping its own "before" state reintroduced.

## Verdict

A removal that was measured instead of asserted — the deleted port-swap machinery is shown to have bought zero unique kills and to have been blind to the one failure it existed to prevent — but at the scored commit every cell that still decides anything is hand-written, and the four model-derived columns are undecided because the cut left a live caller of a function it deleted; treat the subtraction as earned and the model-derived reach as unmeasured until those columns are re-run at `f49a1c9`.

## Disclosures

**What I saw that I was not meant to see.**

1. **`<TREES>/before/README.md:139-162`, which the redaction missed.** I hit it in the first minute, running `diff -rq before after` to find the change surface, and read the diff hunk before I knew what it was. It carries the card's five dimensions, six scoring rules, and — the part §7 promises is absent — four prior results for one of these five dimensions stated as a run of figures with the sentence that they did not move. §1 asserts it is "the entire redaction" and names four files it could not delete; this is a fifth, and it is the one carrying prior results. **Did it move anything?** It set an expectation about where this project's scores sit before I had opened a single artifact. My D1 of 2 came from my own two runs — a content kill I reproduced and a refusal that survived — and I believe I would have landed there regardless, but I cannot claim the number is uncontaminated, so I am recording the exposure rather than defending the score.
2. **`<TREES>/after/examples/validation/ab/reference_ports/journal_memory.py:9-22`**, named in §1. It states a prior D3 score for a different artifact in a prior round. I read it while designing JUDGE-F2 and needed to know what the file did. It cut *against* flattery rather than for it: it is part of why I did not award D3 = 4 off my own real/fake experiment (see below).
3. **`<TREES>/after/tests/test_score_tools.py:1025`**, named in §1 — a fixture dict containing `"score": 4` with a citation and a `refuses_to_claim` string. Fixture data for a checker test. Moved nothing.
4. I did **not** read `references/eval_scorecard.md` (absent from both trees; I did not go looking), any sibling of my card directory, any `-p2`/`-p3`/`-p4` directory, any `PREDICTIONS*`, `*EPIC*`, `RESULT*`, `INDEX.md`, `SELF-IMPROVEMENT.md`, `INSTRUMENT-LOG.toml` or `UNBLINDING.md`, or anything under the live checkout other than my own three card files. I made no attempt to resolve what `K` is and do not know.

**What I ran that changed anything.** Nothing inside either staged tree. Everything ran on copies under my own scratch directory: one copy of `after/` plus three per-fault copies and three staged `distributed_history` trees. The full list of runs is in the judging-practice section above. I did not run `pytest tests -q`; §6 records it on unredacted checkouts and a redacted copy would have produced failures I could not attribute to the artifact rather than to §1.

**What I REJECTED.**

- **D3 = 4, which I nearly gave and which my own evidence supports on the anchor's literal text.** JUDGE-F1 and JUDGE-F2 are a clean demonstration: 28 identical cases green against both a real adapter and a fake, and a fault seeded on either side reddens exactly that side and leaves the other green. That is anchor 4, word for word, and I generated it rather than read it. I rejected it because the port is in `examples/validation/ab/reference_ports/` — the toolchain's *fixture*, the thing it measures against — and the toolchain's own code has no such seam (`declared_interfaces: 0` across `scripts/`, 30 of 33 modules calling effect sinks directly). Awarding it would have scored a fixture and called it an architecture. **This is the single most consequential judgement on this card and a second judge could reasonably differ by two.**
- **D2 = 4.** Closed by its own gate (D4 = 2), but I would have refused it anyway: `render_port_binding_report` was the only executable reconciliation between a binding table and the manifest, and it is gone. Priced is not preserved.
- **D5 = 3 under the `disclosure` reading**, which I held for a while, because so much of what impressed me is disclosure and the softer reading would have made 4 nearly automatic and therefore worthless. I rejected it once I found results the artifact measured *against itself* and kept — the three-of-four miss, and an executing test asserting the change made something undetectable. Under the strict reading anchor 4 is reached on merit, which makes the soft reading moot.
- **§3's headline, in the direction it points.** `scripts/` fell 225 lines, 1.06 %, and effectively all of it is one module; the three measured trees rose 1677 net. The epic bought a 225-line subtraction with a 633-line mutation harness and a 313-line enumerator rewrite — roughly seven lines of apparatus per line removed. I did **not** score that as complexity growth, on the ground that measuring equipment is not the design, and I record that I considered it: a judge who counts the apparatus moves D2 to 2, and that reading is defensible.
- **"Guard relaxation 3 of 3" and "83.2 % executable" as D1 evidence.** They appear in three places as prose. Rule 1 says the code is the evidence, and no measurement in this packet decides either. So I tried to reach the refusal class myself with the corpus that actually ships (JUDGE-F4b) and it survived. That survival is a fact about the example's four-case corpus, not a refutation of the claim — I am not asserting the claim is false, I am declining to score it as evidence.
- **Reading the four `CONTROL_RED` corpus cells as survivals.** The runner forbids it and the runner is right. But I also declined to read them as harmless, which is the easier mistake: the reason is `ImportError: cannot import name 'apply_wiring'` — the cut deleted a function a live measurement driver still calls — and the effect is that every model-derived column in the after table is undecided. **I could not tell a redaction failure from a real one here**, because the driver lives under `specs/results/scorecards/`, which §1 deleted from my trees. Named rather than guessed, per the dispatch.
- **The suite figure as behavior-preservation evidence.** 1177 → 1386 passing is in §6 and I gave it no weight beyond anchor 1. A suite that grew by 209 nodes in the same change that removed 21 is not an argument that the removed 21 were covered.

**Where the anchors did not fit, collected.** D3, at the seam between anchors 2 and 3, where "the domain" silently changes referent between a spec-double subject and a CLI toolchain whose fixtures are hexagonal and whose own code is not. D4, across its whole ladder, which has no rung for a deliberate, measured subtraction: read strictly this artifact scores 1 for doing the most careful job of behavior accounting I have seen on this card, and I scored 2 by stretching "shown still to hold" into "re-measured, with the losses named". D2's `read_first` note, which asks for a spec descriptor from an instrument that produces a code descriptor. Each is argued in the rationale above rather than smoothed into a number.

**One thing I left alone.** `mechanical.json` beside this card is scaffolded and empty, including its `commit` field. The dispatch named `scorecard.md` and `scorecard.json` as the files I fill, so I did not write it; the figures a reader would want in it (kill cells before/after, the descriptor deltas, 4 executed cases, 28 suite cases, my six fault runs) are in the citations above.
