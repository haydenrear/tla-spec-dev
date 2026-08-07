# Scorecard — toolchain_removal, artifact `K`, judge pass 3

`run_id`: `20260807-sm05rm-K-p3` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

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

- Copied `{{TREES}}/after/` to a scratch dir outside the repo and both trees. Ran
  `uv run --with pytest --with pyyaml python -m pytest tests/test_ab_three_arms_and_port_faults.py -q`
  as a baseline (23 passed, 5 failed — all 5 failures are `PREDICTIONS-PA.md`
  reads, consistent with the §1 redaction, not the artifact).
- Seeded my own fault: in `examples/validation/ab/reference_ports/journal_memory.py`,
  changed `self._lines.append(line)` to `self._lines.insert(0, line)` — an
  ordering fault, the same shape as the packet's `SM-GM-P1`. Reran the same test
  file: 20 passed, 8 failed. Three of the new failures beyond the redaction
  baseline are directly caused by my edit —
  `test_a_composition_point_wires_the_fake`,
  `test_both_wirings_of_one_domain_agree_on_the_feature`,
  `test_every_adapter_internal_mutant_occurs_exactly_once_and_reverts` — each on
  a content assertion (exact expected ledger-line sequence), not a shape check.
- Attempted to run `tests/test_card_has_one_home.py` (the SM-06 dedup checker)
  against the same scratch copy, to independently verify the M1/A1 finding in
  §2(c). It errored (`RubricError: rubric not found:
  .../references/eval_scorecard.md`) because that file is one of the §1
  redactions and I am separately forbidden from reading it. I did not work
  around this. For that mechanism I relied on the packet's own recorded
  mutant run (`data/dup-mutants-before.json`, `data/dup-mutants-after.json`)
  rather than my own execution — noted per-dimension below.
- Did not run the full suite (§6 already gives the unredacted numbers) or seed
  a fault against change (b), the instrument-registry derived walk.

## Your scores

### D1 — bug detection

**Score:** 3

**Citations** (`file:line` — the bar is in the scoring rules above):

- `data/gap-mutants-before.json:934` (`SM-GM-P1-fake-journal-records-newest-first`) — the plain, unassisted case corpus (`corpus-action-bound:fake` / `corpus-action-bound:real`) **SURVIVES** an ordering fault (fake journal records newest-first) both before and after the removal. The gap this mutant targets is stated in the same tree as "a class the whole-view corpus is documented as reaching poorly" — an ordering fault the flat corpus structurally misses.
- `tests/test_ab_three_arms_and_port_faults.py:314-324` (`test_a_composition_point_wires_the_fake`) and `:329-343` (`test_both_wirings_of_one_domain_agree_on_the_feature`) — content assertions (`assert ledger.ledger_lines() == [...]`, `assert real_obs == fake_obs`) that DO catch the ordering fault, in the after tree. Verified myself: seeding the same fault shape in my own scratch copy (see judging_practice) produced new failures at exactly these two tests plus `test_every_adapter_internal_mutant_occurs_exactly_once_and_reverts`.
- `scripts/run_generated_case_adapters.py:1148` — the general field-by-field after-state assertion (`raise AssertionError(f"adapter after-state mismatch...")`) is unchanged by the removal and is a content assertion, not a shape check, satisfying anchor 2 on its own.
- `data/gap-mutants-after-SM-03.json:237` and `:367` (`SM-GM-I1`, `SM-GM-I3`) — two faults that **SURVIVED** at the before commit (`data/gap-mutants-before.json:525`, `:655`) and **DIE** after change (b) (the derived-walk replacing the hard-coded instrument list): a fault class the artifact could not previously reach and now can.

**Refuses to claim** (required and non-null for a score of 4): n/a (score is 3)

**Rationale:** Anchor 3 is clearly met twice over, by two different mechanisms: an ordering fault the flat model-derived corpus cannot reach on its own is caught by content-asserting hand-written tests (I confirmed this myself, not just read it), and a fault class (a hollow demonstration node) that survived at the before commit is newly caught by the after-tree's derived-walk mechanism. I stopped short of anchor 4. Anchor 4 requires "the cases that do it were derived from the model rather than hand-written." The cases that actually catch the ordering fault in the after tree (`test_a_composition_point_wires_the_fake` etc.) are hand-written pytest functions, not TLC-derived case programs — the one avenue by which a genuinely model-derived case ever caught this fault (`corpus-port-swap`, riding the now-deleted `[ports.*]` machinery) is gone, and the artifact's own comment at `scripts/run_generated_case_adapters.py:308-312` states it had "zero unique kills across 28 tables" anyway. I considered scoring 4 on the strength of the gap-mutants and dup-mutants catalogues being "a corpus" in the rubric's parenthetical sense, and rejected it: those catalogues are hand-authored fault tables (a human wrote what to seed and what to assert), not derived from the TLA+ model the way the case corpus is. Rule: "when torn between two, take the lower and say why" — this is that case. The record does name a fault class it still cannot reach (`SM-GM-I2` survives both before and after, though the artifact itself attributes that specific survival to a defect in the mutant rather than a real gap; the derived walk's own declared blind spot — "a repository tripwire that is a pytest file... is invisible to it. Six such files exist," EVIDENCE.md §5 — is the cleaner example of a self-named, currently-real gap), but since the model-derived half of anchor 4 fails, the combination isn't satisfied.

### D2 — complexity

**Score:** 4

**Citations** (`file:line` — the bar is in the scoring rules above):

- `data/descriptor-before-3f58aca.json:1270` vs `data/descriptor-after-f49a1c9.json:1265` — the single file that carries the removal, `run_generated_case_adapters.py`: `code_lines` 2341 → 2116, `callables` 78 → 72, `branch_points` 473 → 429, `public_surface` 58 → 53, and `imports_internal` drops `generate_cases_from_tlc_dump.py` (matching the −1 `internal_import_edges` in EVIDENCE.md §3). `module_state: 0` on both sides — no module-level mutable global was added or removed.
- EVIDENCE.md §3 — the file-level −225 `code_lines` accounts for the entire measured `scripts/` total delta (21252 → 21027), so the reduction is not diffuse noise; it is this one removal.
- Behavior-preservation tie: D4 is scored 3 below (`data/gap-mutants-after-SM-02.json:967`, my own seeded fault) — the ordering-fault detection the deleted machinery claimed is still caught after the cut, so the −225/−6/−44 reduction was not paid for in lost behavior for the fault classes that were seeded.

**Refuses to claim** (required and non-null for a score of 4): The complexity instrument itself, `scripts/code_complexity.py:553,587,776-777`, reports `unresolved_constructs` — ten `getattr()`/`setattr()` sites (`EVIDENCE.md` §3) it cannot resolve, on both trees — and does not fold them into the totals it reports as measured.

**Rationale:** What got simpler: `run_generated_case_adapters.py` lost the `[ports.*]` binding branch of `load_mappings`, `apply_wiring`, `render_port_binding_report`, the port-first precedence in `adapter_for_case`, and the `--wiring`/`--port-manifest` flags (EVIDENCE.md §2(a)) — a real reduction in callables and branch points in the exact file, not a metric drop from an edge deleted elsewhere (the MF-020 caveat). How behavior survived it: the fault classes the deleted machinery claimed to catch (P1/P2/P3, an ordering fault and two swap-integrity faults) are still caught in the after tree, some by a still-live sibling driver (`run_port_swap.py`, reported as `portswap-suite-fake` in the mutant data) and some by the pre-existing hand-written suite (`tests/test_ab_three_arms_and_port_faults.py`) — the latter I verified myself by seeding the ordering fault and watching it fail. I am not crediting this as "unique" bug-catching capacity gained (D1 is capped at 3 for exactly that reason), only as complexity removed without a corresponding loss on the fault classes actually measured.

### D3 — modularity

**Score:** 4

**Citations** (`file:line` — the bar is in the scoring rules above):

- `tests/test_ab_three_arms_and_port_faults.py:346-357` (`test_the_domain_imports_neither_adapter`) — reads `domain.py`'s source and asserts neither `import journal_file` nor `import journal_memory` appears in it. This is a runtime-topology check (what the file actually contains), not an import-graph tool, so it clears the Round-2 caveat.
- `tests/test_ab_three_arms_and_port_faults.py:360-370` (`test_each_adapter_is_wired_by_exactly_one_composition_point`) — asserts `quota_ledger.py` wires `journal_file` and `quota_ledger_fake.py` wires `journal_memory`, and that neither wires the other's adapter. The specific swap: `quota_ledger_fake.py` is the whole composition point, and its own docstring (`examples/validation/ab/reference_ports/journal_memory.py:23-27`) says it is "four lines long."
- `tests/test_ab_three_arms_and_port_faults.py:314-324` and `:329-343` — both `test_a_composition_point_wires_the_fake` and `test_both_wirings_of_one_domain_agree_on_the_feature` actually drive the port through both the real (`journal_file`) and the fake (`journal_memory`) composition point with the identical scripted sequence (`_drive`, lines 302-311) and compare observations. I re-ran this myself (see judging_practice) and it passed on both wirings before my edit and failed only on the fake wiring's ordering after my edit — the two sides are genuinely independent at runtime, not just in name.

**Refuses to claim** (required and non-null for a score of 4): `test_both_wirings_of_one_domain_agree_on_the_feature`'s own docstring (`tests/test_ab_three_arms_and_port_faults.py:329-337`) states what it does NOT do: "it does not stand in for the shared suite... this test only establishes that the fake is substitutable at all." The artifact declines to claim that fake/real agreement on one scripted sequence is equivalent to the shared suite's expected-value coverage.

**Rationale:** This satisfies anchor 4 cleanly and I verified the runtime claim myself rather than trusting the docstrings. One scope limit worth naming: my evidence is drawn entirely from `examples/validation/ab/reference_ports/`, one reference example. I did not audit whether the rest of the toolchain's scripts (`effect_conformance.py`, `case_modules.py`, etc.) hold the same domain/adapter separation, and the removal itself (§2(a)) cuts a *generic, declarative* swap facility (any port swappable via a `[ports.*]` TOML table in the shared runner) in favor of what remains: hand-wired, per-example composition points that a developer writes by hand for each new port. The anchor doesn't ask for genericity, so I'm not scoring against that, but a reader should know the "adapter could be replaced without touching the domain" claim I'm citing now costs a bespoke Python module per swap rather than a config-table entry — the artifact traded a general mechanism for a demonstrated-but-narrower one.

### D4 — behavior preservation

**Score:** 3

**Citations** (`file:line` — the bar is in the scoring rules above):

- `data/gap-mutants-after-SM-02.json:967` (`SM-GM-P1`) — after the removal, `corpus-port-swap:*` goes `CONTROL_RED` (the mechanism that ran it is gone), but `portswap-suite-fake` still `DIES` and `pytest-full` still `DIES`, with `new_failing_nodes` naming `tests/test_ab_three_arms_and_port_faults.py::test_a_composition_point_wires_the_fake` etc. Same pattern for `SM-GM-P2` and `SM-GM-P3` in the same file.
- EVIDENCE.md §6 — the unredacted suite: 1177 passed/1 failed (before, the 1 a deliberately-left-red node) → 1386 passed (after). More behaviors enumerated and passing, not fewer.
- `data/dup-mutants-before.json:37,78,119` (M1, M2, M3 — three prose copies of the rubric, all `UNCAUGHT`) vs `data/dup-mutants-after.json:38,84` (A1, A2 — reintroducing the same shape, both `CAUGHT`) — behavior added by change (c), not merely preserved, shown on the same fault shape before and after.
- My own run (see judging_practice): seeded an ordering fault in `journal_memory.py` against the after tree and it was caught by three tests, not zero.

**Refuses to claim** (required and non-null for a score of 4): `scripts/run_generated_case_adapters.py:360-363` — `render_oracle_statement` states on every run: "mutation-kill-test: never carried by this runner... a green run here is not evidence any fault would die." The runner declines to claim mutation-kill coverage it does not carry.

**Rationale:** Anchor 2 is satisfied (behaviors enumerated per mutant, each shown still to hold, both in the packet and in my own run). I stopped at 3 rather than 4 for the same reason I capped D1 at 3: anchor 3's "model-derived (a corpus, a TLC invariant) rather than only hand-written assertions" is genuinely ambiguous here. The gap-mutants and dup-mutants catalogues are systematic and tabular, which tempted me toward reading them as "a corpus" — but every entry in `gap_mutants.toml` and the dup-mutants list is a fault a human chose and wrote a `find`/`replace` for, which is what the anchor's "hand-written assertions" phrase is contrasting against a TLC-derived case. I did demonstrate anchor 4's second half myself — a deliberate behavior-breaking change, shown caught, with `judging_practice.executed_own_faults: true` — but anchor 4 is written as "3, and..."; without a clean anchor-3, I'm not stacking a 4 on top of a 3 I only partly believe. Scoring the lower and saying why, per the stated rule.

### D5 — honesty

**Score:** 4

**Citations** (`file:line` — the bar is in the scoring rules above):

- `scripts/run_generated_case_adapters.py:308-312` — the removal's own rationale, stated in the after tree, is a measured, unflattering fact about a component of the same artifact: "SM-02 removed the fifth, PA-04's real/fake port swap, on measured evidence: zero unique kills across 28 tables, and SM-01's `SM-GM-P3` survived all six of the swap's own columns at 1543 executed cases each while dying to the hand-written suite." This matches the raw data at `data/gap-mutants-before.json:934` exactly.
- `examples/validation/gap_mutants/run_gap_mutants.py:40-42` — explicit refusal to over-conclude: "Not a verdict about the removal. It reports what each detector did. Whether a SURVIVES is an acceptable price is SM-05's call and a human's, not this file's."
- `examples/validation/gap_mutants/run_gap_mutants.py:51-58` and `:98-103,397,401` — named, distinct refusal states (`CONTROL_RED`, `INERT`, `REMOVED`, `NOT_RUN`) rather than collapsing an undecided or a broken-control cell into `SURVIVES`/`DIES`. Exercised at `data/gap-mutants-after-SM-02.json:967`, where `corpus-port-swap:*` reports `CONTROL_RED` rather than either verdict once the mechanism it depends on is gone.
- `scripts/run_generated_case_adapters.py:296-372` (`render_oracle_statement`) — prints "ORACLES CARRIED" / "ORACLES **NOT** CARRIED" on every run, unprompted, including "no binding declares a projector... nothing here observes the real system's state except through the adapter's own returned after-state."
- EVIDENCE.md §4 — the packet itself names `SM-GM-I2` as "recorded by its own author as a defect in the mutant," and EVIDENCE.md §5 names the derived walk's declared blind spot: a repository tripwire that is a pytest file "has neither [a `__main__` guard nor a nonzero exit path] and is invisible to it. Six such files exist."

**Refuses to claim** (required and non-null for a score of 4): `scripts/run_generated_case_adapters.py:360-363` — the runner states, every run, that it never carries a mutation-kill oracle and "a green run here is not evidence any fault would die."

**Anchor reading** (required at 3 or 4; `disclosure` or `measured`): measured

**Rationale:** Anchor 2 and 3 are well covered — refusal states are load-bearing in the verdict rule (`CONTROL_RED`/`INERT`/`REMOVED`), not decorative, and I saw them actually fire in the data rather than only being declared. For anchor 4 I used the `measured` reading deliberately: "zero unique kills across 28 tables" is not the artifact disclosing a general limitation of itself (that would be anchor 2/3 material, per the caveat) — it is a specific, quantified, unflattering result the artifact's own instrumentation produced about a component of itself, used as the stated reason for that component's removal. One thing I noticed but am NOT citing as anchor-4 evidence: EVIDENCE.md §2(a) notes "a leftover `[ports.*]` table is now ignored rather than rejected by one of the two TOML readers and rejected by the other" (I confirmed this myself at `scripts/run_generated_case_adapters.py:383-385` vs `:425-426` — `tomllib.loads` silently drops an unrecognized top-level table while `parse_simple_mapping_toml`'s fallback path raises `ValueError` on the same input). This is a real inconsistency in the after tree, but I did not find it self-disclosed anywhere in the artifact's own text — only in the evidence packet's neutral description of the diff — so under my chosen reading it isn't a result the artifact itself surfaced about itself, and I am naming it here rather than folding it into a score it does not clearly support.

## Verdict

The removal cuts real, measured complexity from exactly the file it claims to (D2=4) without losing the specific fault-catching it claims to preserve (D4=3, D1=3) — its own stated justification ("zero unique kills across 28 tables") checks out against the raw mutant data and against a fault I seeded myself, and the artifact is honest about what it no longer carries (D5=4); the one place I'd push back is D1/D4's ceiling, which the artifact cannot reach on the strict "model-derived, not hand-written" reading of anchor 4 no matter how good its hand-written suite is.

## Disclosures

- **What I ran, beyond the packet:** copied `{{TREES}}/after/` to a scratch dir outside both trees and the repo; ran `tests/test_ab_three_arms_and_port_faults.py` as a baseline (23 passed / 5 failed, the 5 all `PREDICTIONS-PA.md` reads — a §1 redaction, not a defect); seeded my own ordering fault in `journal_memory.py` (`append` → `insert(0, ...)`) and reran, getting 3 new failures beyond the redaction baseline, all on content assertions. Also attempted `tests/test_card_has_one_home.py` against the same scratch copy; it errored because `references/eval_scorecard.md` is both a §1 redaction and a file I am separately forbidden from reading, so I did not chase it further and relied on the packet's own `dup-mutants-*.json` for that mechanism instead of my own execution. Nothing outside my own scratch copy was modified; neither staged tree was touched.
- **What I saw that I was not meant to see:** nothing I'm aware of. I did not open `references/eval_scorecard.md`, any other judge's card, or any path under the live `wt-epic-subtract-to-measure-SM-05` checkout other than my own `CARD_DIR`. I did read the four files EVIDENCE.md §1 explicitly names as not-redacted-on-purpose (`test_card_has_one_home.py`, `test_score_tools.py`, and the two `reference_ports`/README files) but did not go looking for the sentences it warned me about inside them, and I don't believe I registered any past-round score from them — the sentences I actually used from `test_card_has_one_home.py` were about the M1-M4 mutant table and the matcher's own stated blind spots, which EVIDENCE.md already surfaces neutrally.
- **What I REJECTED:**
  - **D1 = 4, rejected → 3.** The gap-mutants and dup-mutants catalogues are systematic and tabular, and I was tempted to read that as "a corpus" in the D1/D4 anchor-4 sense. I rejected it: every entry in those catalogues is a fault a human chose and hand-authored a `find`/`replace` for, which is exactly what the anchor is contrasting against a TLC-derived case. The one avenue by which a genuinely model-derived case ever caught the ordering fault (`corpus-port-swap`) is the mechanism that got removed, and the artifact's own comment says it had zero unique kills anyway.
  - **D4 = 4, rejected → 3**, for the same reason, even though I have exactly the kind of hands-on evidence (my own seeded fault, caught) that anchor 4's second clause asks for. I did not want to stack that clause on an anchor-3 I only partly believe.
  - **A D1/D4 anchor-4 citation using `SM-GM-I2`, rejected.** It survives both before and after, which reads like "a fault class it still cannot reach" — but EVIDENCE.md §4 already says the artifact attributes that specific survival to a defect in the mutant (it perturbs a reported field, not the refusal path it aimed at), not to a real gap in the mechanism. Using it as anchor-4 evidence would have been citing a claim the packet itself walks back.
  - **D5 anchor-4 evidence from the TOML-reader asymmetry, rejected.** I confirmed it myself (`tomllib.loads` silently drops a leftover `[ports.*]` table; the fallback parser raises on the identical input) and it is a real, unflattering inconsistency in the after tree — but I could not find it named anywhere inside the artifact's own text, only in the evidence packet's neutral description of the diff. Under the `measured` reading I chose, that's not the artifact producing a result about itself, so I left it out of the D5 citations and named it here instead.
  - **A D3 score without the scope caveat, rejected.** My D3=4 evidence is entirely from `examples/validation/ab/reference_ports/`, one example. I did not check whether the rest of the toolchain holds the same separation, and I said so in the D3 rationale rather than letting one well-instrumented example stand in for the whole artifact.
- **Something worth flagging that isn't a score:** the mechanical block (`mechanical.json` beside this card) was served to me empty — `figures.kills`, `.complexity_of_produced_code`, `.case_counts`, `.determinism`, and `.runtime_seconds` are all `{}`/`null`, and `commit` is blank. Rule 7 says that block "sits beside the judgement so a reader can see when the two disagree." With nothing in it there's no mechanical figure to disagree with mine; I'm noting the gap rather than guessing at numbers to fill it, since I was told to fill `scorecard.md`/`scorecard.json` and not that file.
