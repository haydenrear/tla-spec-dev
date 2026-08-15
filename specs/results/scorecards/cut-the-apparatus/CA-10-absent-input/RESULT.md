# The absent-input class: one repair, and the extent measured

**Tree:** `epic/cut-the-apparatus` at `deabd4b` plus **one changed file**,
`examples/validation/scorecards/score_tools.py`. Nothing else was edited, and
nothing was edited while the suite was in flight.

Two questions were asked. **Part 1 — is the red count converging?** Yes: `11 → 7`,
with **zero denominator movement**. **Part 2 — how big is the class?** **48
instances across 30 of the 43 verdict-producing modules** under `scripts/` and
`examples/validation/`.

---

## 1. The repair, and its `R1`

`score_tools._finding_ids()` hard-coded the live ledger and returned an **empty
set** when it was gone, so `R-H3` reported every `filed_as` citation in the whole
scorecard record as naming an id that was never filed. `CA-10-DF-11`.

**Signature checked before writing, as instructed.** `CA-10-DF-06`'s published
one-line fix for `tests/test_disposition_requirement.py` was incomplete because
*that* module read the live path twice. **This module reads it once**, at the old
`:2788` — verified by `grep`, not assumed. `DEFAULT_SWEEP` at `:3448` carries the
same dead directory but is a different consumer with a different answer, and it is
**filed, not fixed** (§4).

The fix resolves through the same archived-ledger fallback `scripts/disposition.py`
uses, reusing its two `ARCHIVE_GLOBS` and its `(mtime, size, path)` ordering, and
**adds a third state the old signature could not express**:

```python
def _finding_ids() -> set[str] | None:      # was: -> set[str]
```

`None` means **nothing was read**. An empty set means **the ledger was read and
filed nothing**. The old return type could not tell those apart and answered the
second with the first — which is the class, in one line.

**`R1`: a demonstrated failing input on a real subject, failing before and passing
after.** The subject is this repository's own scorecard record.

| `score_tools.py audit`, this tree | violations | exit |
|---|---:|---:|
| **before** — live ledger absent, `_finding_ids()` → `set()` | **14** | **1** |
| **after** — resolved to the archived ledger, 287 ids | **0** | **0** |

It resolves to
`specs/.history/cut-the-apparatus-epic/closed-snapshot/deferred_findings.yaml` —
the address the entry manifest records under `findings_ledger`. Evidence:
`audit-after-fix.txt`.

**The third state is demonstrated too**, because a fallback that merely moves the
false PASS to a rarer input has not fixed the class. Against a tree with no ledger
live *or* archived (`SCORECARD_REPO_ROOT` pointed at an empty directory):
`_ledger_path()` → `None`, `_finding_ids()` → `None`, and `audit_rh3` emits **one
`UNVERIFIED` line** — *"Every `filed_as` citation below is UNCHECKED — not
verified, and NOT fabricated"* — instead of 14 fabrication claims. `UNVERIFIED`
does not increment the violation count, so the tool answers **undecided**, not
clean and not wrong.

---

## 2. The suite figure, with every movement attributed

Command, unchanged (`--with pyyaml` is required):

```bash
uv run --with pytest --with pyyaml -m pytest tests -q
```

| | failed | passed | skipped | collected |
|---|---:|---:|---:|---:|
| **baseline** (`40c998b`, the close performed) | **11** | **1458** | **22** | **1491** |
| **this tree** (baseline + the one-line class repair) | **7** | **1462** | **22** | **1491** |

`7 failed, 1462 passed, 22 skipped in 1242.60s (0:20:42)`, exit 1.
`--collect-only` → **1491**.

**Per `denominator_rule`, every unit of the movement is NUMERATOR, and there is
nothing else in it:**

```
reds        11 − 4 = 7        −4 NUMERATOR, 0 denominator
passes    1458 + 4 = 1462     +4 NUMERATOR, 0 denominator
skips       22 + 0 = 22       unchanged
collection 1491 + 0 = 1491    unchanged
7 + 1462 + 22 = 1491          exact
```

**The four reds that moved are the four the repair predicted, and no others:**

| red at `40c998b` | now | movement |
|---|---|---|
| `test_score_tools::test_a_refuted_finding_stays_on_the_record_with_its_filing` | **green** | **numerator −1, repaired** |
| `test_score_tools::test_the_shipped_rh5_demonstration_still_goes_red` | **green** | **numerator −1, repaired** |
| `test_score_tools::test_the_repo_ledger_passes_its_own_audit` | **green** | **numerator −1, repaired** |
| `test_score_tools::test_the_repo_ledger_passes_its_own_audit_with_rh6` | **green** | **numerator −1, repaired** |
| `test_architecture_tags::test_the_same_tag_control_holds` | red, same cause | unchanged (deliberate, `RM-06-DF-01`) |
| `test_goal_baseline_is_a_card::…cannot_be_re_opened` | red, same cause | unchanged (**still the `CA-10-DF-13` cause**, not the declared one) |
| `test_instrument_demonstrations::test_every_declared_path_exists` | red, same cause | unchanged (declared, `CA-04-DF-04`) |
| `test_instrument_demonstrations::test_every_fast_demonstration_reproduces` | red, same cause | unchanged (declared, `CA-04-DF-04`) |
| `test_port_case_generation::…declares_no_orphan_port_name` | red, same cause | unchanged (the close, `specs/current/` gone) |
| `test_source_citations::…[specs/program_model/spec_manifest.yaml]` | red, same cause | unchanged |
| `test_ticket_retirement::…matching_close_receipts` | red, same cause | unchanged (`missing ticket plan`) |

**The expectation was 11 → 7 and the measurement is 11 → 7.** Four passes
appeared and four reds disappeared and they are the same four nodes; nothing was
collected, deleted, or skipped that was not collected, deleted, or skipped before.

**This is a repaired numerator, not a fallen denominator** — the distinction
`test_source_citations` cost this project last pass. The four tests still exist,
still run, still assert exactly what they asserted, and now pass because the thing
they assert became true.

### Answering the owner's actual question: are we fixing broken metrics, or did we break something?

**Neither the metric nor the subject moved except where the repair aimed.** The
collection count is byte-identical at 1491, the skip count is identical at 22, and
the seven survivors carry the same causes they carried at `40c998b`. **No red was
repaired that was not caused by the defect**, and **no declared baseline red was
touched** — including `test_goal_baseline_is_a_card`, which is still red for
`CA-10-DF-13`'s reason (a `FileNotFoundError` before its assertion) rather than
for the reason PR #272 counts it under. That divergence is **unchanged and still
filed**; it was not repaired here.

The honest qualification: **`11 → 7` restores the pre-close red count but not the
pre-close tree.** The pre-close figure was `7 failed / 1497 passed / 1504
collected / 0 skipped`. The reds match; the 22 skips, the 13 uncollected nodes and
the three vacuous passes (`CA-10-DF-14`) are all still there. **The count
converged. The tree did not.**

---

## 3. Part 2 — the class, named and measured

**`R1` requires a demonstrated *failing* input on a real subject. It does not
require a demonstrated *ABSENT* input.** That single gap is why all five of the
owner's exemplars shipped: each satisfied `R1` in full and still answered PASS to
the question it was built to refuse.

### 3.1 A correction to the framing: three of the five are already repaired

The owner's list names five live instruments. **Three are already fixed in this
tree, and the record does not say so.**

| exemplar | state today | evidence |
|---|---|---|
| `CA-00-DF-04` — empty file → PASS | **repaired in part.** `blind_dispatch.py:104-123` (`MIN_REPORT_BYTES`, `DISPATCH_FAILURE_SIGNATURES`) exits **2** on an empty subject. The **`WEAK PASS` half survives** — §3.3 | run: empty subject → exit 2 |
| `CA-05-DF-06` — seven duplicate YAML keys certified clean | **repaired for four-space nesting only.** The refusal at `disposition.py:122-126` catches the shipped format; a duplicate at any *other* level, including a top-level `findings:`, still certifies clean | `CA-10-DF-22` |
| `CA-06-DF-01` — zero cases, `corpus gate PASS` | **repaired.** `resolve_next_relation` exists at `:2270` and **both** callers pass it. The **failure-reporting half survives** on the port path | `CA-10-DF-23` |
| `CA-06-DF-05` — `passed = not over_cap` | **live**, unchanged | `CA-10-DF-19` |
| `CA-10-DF-11` — ledger absent → empty set | **repaired by this pass** | §1 |

**Two of the five were live when this sweep began.** Reporting the class as five
live instruments would have overstated it, and each of the three partial repairs
left a *named half* behind — which is itself the more interesting fact than
either the repair or the defect.

### 3.2 The sub-shapes

So the next sweep is cheaper than this one:

1. `if not path.exists(): return set()/[]/{}` — an empty result fed to a verdict as if measured
2. `all(...)` / `not any(...)` over a possibly-empty collection — **vacuously true**
3. a **one-sided threshold** that zero trivially satisfies
4. `.get(k, default)` collapsing **both sides** of a comparison, so two empties match
5. `except (OSError, ValueError): return []` — unparseable becomes indistinguishable from absent
6. a **default-named lookup** that misses silently
7. an **empty selection** (`--only` matching nothing, a glob matching no file) reported as a satisfied population

### 3.3 The sweep

**43 verdict-producing modules read. 30 carry at least one instance. 48 instances.**
Full detail, with reproductions, is in ledger rows `CA-10-DF-17`…`CA-10-DF-25`.

| file : line | absent / empty / unparseable input | behaviour | reachable | correct answer | row |
|---|---|---|---|---|---|
| `score_tools.py:2484` | `INSTRUMENT-LOG.toml` absent under `--root` | `0 violation(s)`, exit 0 | **yes** | refuse: no log, no rule checked | 18 |
| `score_tools.py:3293` | zero cards | `OK no judge group has a spread greater than 1` | **yes** | `UNVERIFIED` | 18 |
| `score_tools.py:2930` | zero cards | R-H1 clause 3 emits **nothing** | **yes** | `UNVERIFIED` | 18 |
| `score_tools.py:3590` | card corpus absent | `63 REFUTED` exit 1 → `0 REFUTED, 82 UNREACHABLE`, **exit 0** | **yes** | refuse, as `cmd_check:1189` does | 18 |
| `score_tools.py:3448` | `specs/desired_program_model/*.yaml` deleted | pattern matches 0 files silently; **17 REFUTED figures unswept** | **yes, today** | report `swept 0 of N patterns`; address waits on `CA-10-DF-10` | 18 |
| `corpus_diagnostics.py:889` | `cases.py` with `CASES = []` | `corpus gate PASS: 0 case(s)`, exit 0 — while an empty *trace* dir refuses at `:903` | **yes** | refuse, symmetrically with `:903` | 19 |
| `corpus_diagnostics.py:543` | no `spec_manifest.yaml` above the package | default caps used with `warn=False`; report prints them as measured | **yes** | name the fallback, or refuse | 19 |
| `corpus_diagnostics.py:916` | package declares no `SOURCE_VIEW` | **internal** cap (200) applied to an external corpus (50) → PASS at 4× | **yes** | refuse: an unattributable corpus has no cap | 19 |
| `run_generated_case_adapters.py:1571` | no `effects:` block found | `effects_active=False`: no sandbox, no diff, **no report even with `--effect-report`**, exit 0 | **yes** | refuse, as `effect_conformance_report.py:80` does | 19 |
| `testgraph_channels.py:336`, `:341` | adapter module unresolvable / `SyntaxError` | import-isolation gate reports the binding **clean** | **yes** | `ChannelViolation`: isolation UNDECIDED | 20 |
| `testgraph_channels.py:410` | empty external corpus → `actions=set()` | every binding skipped; `external channel enforcement passed` | **yes** | refuse an empty action set | 20 |
| `case_modules.py:552` | zero corpora / empty `actions.yml` | `UNCOVERED: none — every view action is entered` | **yes** | `UNCOVERED: UNDECIDED` | 20 |
| `generate_python.py:238` | `invariants:` absent, empty, or nulled | emits `def validate_state(state): return None` — **passes every state**; `validate_manifest` reports 0 errors | **yes — 2 shipped examples** | `raise NotImplementedError`, as `:270` does | 21 |
| `extract_spec_manifest.py:352` | `invariants:` absent | zero invariants checked, exit 0 PASS | **yes** | UNDECIDED | 21 |
| `scaffold_spec.py:651` / `onboard_program_model.py:824` | state missing the projected key | **both sides** project to empty → `"matched": true` | **yes** (ships into every scaffolded repo) | raise: "I projected nothing" ≠ "they agree" | 21 |
| `onboard_program_model.py:1219` | bindings with an empty `actions:` table | `…bindings_cover_external_actions` **passes** on 4 substrings | **yes** | enumerate the actions, or rename the test | 21 |
| `extract_spec_manifest.py:184` | duplicate YAML keys | last-wins **silently** — the mechanism under `CA-05-DF-06` | **yes** | `raise ValueError` | 22 |
| `disposition.py:126` | duplicate key not at 4-space indent (e.g. top-level `findings:`) | `DISPOSED … all three clauses hold`, exit 0, over a half-discarded parse | **yes** | duplicate-rejecting loader | 22 |
| `infer_action_params.py:227` | actions written `Foo(x) == body` on **one line** | 0 bodies, 0 recipes; empty audit table under *"the audit is complete rather than selective"*; **no `params:unchecked` label** | **yes** | refuse: N lines, 0 readable definitions | 22 |
| `analyze_complexity.py:1762` | `--tlc-report <missing path>` | silently ignored; output **byte-identical** to omitting the flag | **yes** | refuse (`EXIT_USAGE`), as `:2328` does | 23 |
| `analyze_complexity.py:1764` | `--baseline-tlc <missing path>` | MF-020 check skipped, and prints *"Pass `--baseline-tlc`"* — advice to pass the flag that **was** passed | **yes** | refuse | 23 |
| `analyze_complexity.py:1782` | TLC report that exists but does not parse | `max_distinct_states` never compared; **zero** findings | **yes** | explicit finding naming the unchecked budget | 23 |
| `complexity_ledger.py:612` | `distinct_states` unmeasurable | `directions` empty → **`direction: "zero"`** → Gates 1/2/3 all stand down → `VERDICT: recorded` | **yes** | a fourth direction, `unknown`, treated as `mixed` | 23 |
| `generate_cases_from_tlc_dump.py:2912` | signatures unresolvable | `signatures, _ = …` **discards the rejection dict**; every port narrated as *"the port's effect is outside the model"*; 0 cases, exit 0 | **yes** | thread `rejected` through, as the negative pass does | 23 |
| `generate_cases_from_tlc_dump.py:1336` | `--actions-metadata` omitted | the `R4-DF-04` zero-case coverage check iterates `set()` **in silence**; `set()` labelled *"the supplied actions metadata"* | **yes** | UNDECIDED | 23 |
| `code_complexity.py:919` | nonexistent path / no `.py` | *"nothing was left unmeasured by this instrument's own limits"* over **0/0** files | **yes** | gate on `files_seen` | 23 |
| `blind_dispatch.py:143` | live memory index absent; `--repo` not a git repo | `WEAK PASS`, **exit 0**; the `UNDECIDED` branch is **dead code** — the guard tests 4 hard-coded literals that are never empty | **yes** | test the **derived** classes only | 24 |
| `check_prediction_seal.py:279` | unreadable / absent kill table | **N05 downgraded to UNPARSED**, then *"No prediction is contradicted…"*, exit 0 | **yes** | not sealable-decidable → exit non-zero | 24 |
| `check_prediction_seal.py:294` | `controls.toml` absent | retired-control cross-check (the M09 clause) contributes nothing, silently | **yes** | refuse | 24 |
| `demonstrate.py:505` | `--only` matches no instrument | *"Every declared demonstration reproduced."* exit 0 | **yes** | refuse an empty selection | 24 |
| `demonstrate.py:447` | declared root absent | *"Every discovered executable has a row."* exit 0 | **yes** | refuse | 24 |
| `dispatch_record.py:266` | `dispatch.toml` absent / empty | *"evidence is self-consistent"* exit 0 — and `check_catalogue.py:697` **skips** its loud warning precisely because `--dispatch-dir` was passed | **yes** | refuse (exit 2) | 24 |
| `divergence.py:133`, `:141` | `per_mutant = {}` | two `all(...)` vacuously true → *"E1 holds … E2 holds"*, `NULL STILL ENTAILED`, exit 0. `rows_compared: 0` is **already recorded and nothing reads it** | **yes** | `rows_compared == 0` → UNDECIDED | 24 |
| `run_controls.py:573` | no row declares a `control_role` | `controls_red: []`, exit 0 — while the sibling `run_arm_swap.py:160` **refuses this exact condition** | **yes** | port the sibling's refusal | 24 |
| `architecture_tags.py:296` | wrong/absent `--scorecards`; card with no D3 citations | *"0 card(s) cite predominantly outside their declared scope"*; uncited cards leave the denominator silently | **yes** | report `rows == 0`, count the skips | 24 |
| `fitness_functions.py:103` | descriptor missing / wrong-shaped | every count fact → `0`, so `≤`/`== 0` rules report **holds**, not `unknown` — while `:111` gets it right and the docstring promises it | **yes** | `None`, as `:111` does | 24 |
| `fitness_functions.py:366` | `fitness_functions.yaml` empty / all comments | 0 rules, 0 errors → **no fitness section printed at all** | **yes** | error naming the empty file | 24 |
| `budgets.py:132` | manifest present but **unparseable** | `except Exception: return None` — indistinguishable from absent → permissive defaults | **yes** | distinguish absent from unparseable | 24 |
| `run_arm_swap.py:155` | artifact without `control_red` | *"no declared role was violated"* exit 0 | **no today** (latent) | `report["control_red"]` | 24 |
| `effect_conformance.py:998` | observer root does not exist | empty snapshot still records full `covered_types` — coverage **declared by a class constant**, not by what was seen | **no today** (latent) | derive coverage from a snapshot that succeeded | 24 |
| `spec_evolution.py:790` / `close_tickets.py:238` | `tickets: []` | *"every ticket complete"*; the close proceeds to delete both model directories | yes (open workflows) | UNDECIDED | 25 |
| `close_tickets.py:249` | empty / truncated plan | `ticket_plan_has_retirements` → `False`, **skipping** the retirement-authority check entirely | yes | UNDECIDED | 25 |
| `new_ticket_workflow.py:240` | baseline manifest absent, or missing the carry anchor | negotiated budgets/ports silently reverted to the bare template, exit 0 — the defect the function's **own docstring** exists to fix | yes | refuse, or warn | 25 |
| `new_ticket_workflow.py:312` | empty `specs/current/` | `seed_manifest.desired: []` recorded as a measurement; close prints *"basis: seed manifest recorded at open"* | narrow | `None`, not `[]` | 25 |

### 3.4 What the sweep found that is *not* the class

Recorded so the census cannot be read as a rate. **Thirteen of the 43 modules
carry no instance**, and the close-path instruments in particular refuse
correctly and loudly: `load_ticket_plan:218`, `record_complexity_ledger:1479`
(*"it does not estimate and it does not skip"*),
`close_tickets.validate_equivalent:122` — which **carries the exact anti-vacuity
guard this class predicts is missing**, `no semantic model files found to
compare` — `validate_equivalent_model_dirs:981`,
`tla_spec_dev.run_spec_unit_tests:414` (refuses when zero tests *and* zero case
packages were discovered), all of `spec_paths.py`,
`export_testgraph_cases.resolve_manifest:150`, `extract_spec_manifest.validate_manifest`
on an empty file, `discover_baseline:141`, `kill_test.parse_mutants:199`,
`check_twins.py:44`, and `skill_feedback.filing_status:219`, which **fails
closed** on an unparseable feedback document.

The scaffolded adapter tests use `pytest.mark.skipif` with a reason — **a skip is
an undecided verdict that announces itself**, which is the shape the whole class
is missing, and it is already in this repository.

---

## 4. What was fixed, what was filed, and one thing deliberately left alone

**Fixed: one line's worth, in one file.** `_finding_ids` and its two call sites.
That is the whole of the repair, and it is the only hit in the sweep that is the
**resolve-through-the-archived-fallback** class.

**Filed, not fixed: 47.** Rows `CA-10-DF-17`…`CA-10-DF-25`, each with a file, a
line, the behaviour, a reachability call, a reproduction and the correct answer.
The correct answer is **UNDECIDED or a refusal** in every one of the 47 — not a
repair that makes the instrument pass.

**`score_tools.py:3448` is the one that looks like the fix and is not.**
`DEFAULT_SWEEP` still globs `specs/desired_program_model/*.yaml`, the same deleted
directory, in the same file, and `LEDGER_ARCHIVE_GLOBS` now sits 600 lines above
it. Resolving it through the archive would be a two-line change and it was
**deliberately not made**: `DEFAULT_SWEEP`'s own docstring **declares
`specs/.history/**` out of scope**, because sweeping the archive *"would report
one claim once per epic that ever snapshotted it, which is a denominator about
the archive rather than about the record."* Changing it overrides a written design
decision, which is a statement about what the check is for, not a repair. It is
the exact sibling of `CA-10-DF-16` and gets the same answer: **decide it with
`CA-10-DF-10`**, which decides where a cumulative ledger lives, rather than before
it. The cost of leaving it is measured and recorded: **17 REFUTED figures
currently unswept**.

**No declared baseline red was repaired.** No red's cause changed under a stable
name in this pass; the two cases where that had already happened
(`test_ticket_retirement`, `test_goal_baseline_is_a_card`) are unchanged and
remain filed as `CA-10-DF-13` and its sibling.

---

## 5. Where these rows live

The close left **no live ledger**, so the nine rows are appended to the archive the
entry manifest records under `findings_ledger`:
`specs/.history/cut-the-apparatus-epic/closed-snapshot/deferred_findings.yaml`,
**287 → 296 rows**.

**Appending falsifies `resolve_ledger`'s own claim** that an archived ledger is
*"FROZEN at that close … never about work done since."* That is `CA-10-DF-10`,
already filed by the previous pass; it is **not re-filed here and not contradicted**
— it is now falsified a second time, by the second task performed after the close.

One consequence worth stating plainly, because this pass created it: **the repaired
`_finding_ids` reads the same file these rows are appended to.** Adding rows can
only add ids, so it can only make more `filed_as` citations resolve and never
fewer — the audit's verdict cannot be worsened by this append, only widened. And
the resolution still depends on `CA-10-DF-09`'s size tie-break: the named artifact
wins over the model-snapshot copy **only because it is larger**, which this append
makes more true rather than less.

**`GOAL-apparatus-cut`'s acceptance line is untouched. It is the owner's.**
