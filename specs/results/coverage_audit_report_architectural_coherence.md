# Coverage Audit Report — architectural-coherence epic (MF-026 gate)

**Round 4 — re-audited against RC-02 at `ab0dfee`.** Rounds 1-3 are preserved in
this file's git history; their raws are unmodified under
`coverage-audit-arch-coherence-raw/`. Round 4 re-enumerates, and sweeps RC-02's
own diff as program surface.

## VERDICT

- **Verdict:** **`pass`**
- **In-scope gaps: 0.** First `pass` in this audit's history.
- **Escalations: 0.**
- **New gaps created by RC-02: 0.**
- **`scope_source`:** `specs/desired_program_model/ticket_plan.yaml:259-282`
  (`representation_scope`), governed by `:26-96` and `:97-106`.

| | R1 | R2 | R3 | **R4** |
|---|---|---|---|---|
| Verdict | `incomplete` | `fail` | `fail` | **`pass`** |
| In-scope gaps | 12 | 9 | 3 | **0** |
| — of which newly created | — | 0 | **3** | **0** |
| Escalations | 7 (187 rows) | 4 (121 rows) | 0 | **0** |
| In-model surface, read | — | 46/46 | 52/52 | **52/52** |

**But read §3 before closing.** The gate is clean; two findings about the oracle
RC-02 enabled are not, and one of them is new. Neither is a coverage gap and
neither changes the verdict — recording them as anything else would be the
inflation this doctrine forbids.

- **Model:** 11 variables, 18 `Next` disjuncts, 17 `@command` actions, 12 ports.
- **Suite:** 1068 passed, 0 failed (re-run, not read).
- **Raw:** `coverage-audit-arch-coherence-raw/round4/` · **Reproducer:** `round4/cac_ac_classify_v4.py`

---

## 1. Verdict on N-1 / N-2 / N-3, and RC-02's diff swept as surface

### 1.1 The three gaps

| Gap | Verified? | Evidence |
|---|---|---|
| **N-1** — three ports declared, attached to no action | **CLOSED — model it** | Mechanically re-derived across all three trees: **12 ports declared, 12 referenced by an action row, 12 carrying `@port` annotations — `DECLARED-BUT-UNUSED = NONE`, `UNDECLARED = NONE`, `in-ports-not-annotated = NONE`** in `current`, `desired_program_model` **and** `program_model`. Row: `InstallLocalCli: [cli_artifact, cli_download, cli_artifact_delete, cli_selftest_process]` at `:335`/`:333`/`:335`. The `InstallLocalCli`-over-both-actions choice is defensible on the evidence RC-02 cites; and it is not load-bearing for coverage, since either placement attaches the ports. |
| **N-2** — `generate cases` wrote and deleted at caller-chosen locations | **CLOSED — change the program** | `spec_paths.resolve_spec_tree_out` (`:131`) applied at `generate_cases_from_tlc_dump.py:1273` (`--out`) and `:1275` (`--dot`, `is_file=True`). The `rmtree` is constrained by construction — `metadir` derives from `dot_path.parent`, which is now guarded. Not exempted: the four in-repo callers were **moved**, verified in the `production_adapters.py` diff (`--out .../generated` → `--out .../specs/generated`). Choosing a new guard over `resolve_evidence_out` is correct: `GenerateCases` declares `spec_tree` at `**/specs/**`, not `evidence_report` at `**/results/**`. |
| **N-3** — a citation stale in the commit that wrote it | **CLOSED — model it, and the class killed** | `tests/test_source_citations.py` requires citations be **file-qualified** and **content-anchored** (`file.py:116 (subprocess.run)`), so a one-line shift fails where a "does the line exist" check would pass. Two parametrised tests, green in the 1068. |

**No forbidden disposition anywhere.** `grep -niE 'justified|accept as-is|acceptable risk|out of contract|low priority|not worth modeling|unlikely in practice'` over `specs/results/rc02-gap-closure.md` returns nothing.

### 1.2 RC-02's diff swept as program surface

This instruction found 2 of 3 gaps last round, so it was run again in full.

- **New effect sites in RC-02's in-model diff: zero.** `git diff 31a6061 ab0dfee -- scripts/spec_paths.py scripts/generate_cases_from_tlc_dump.py specs/*/production_adapters.py`, filtered to added lines matching any effect primitive, returns **only prose** — comments naming effects, not performing them. The diff is a path guard, comment rewrites, four moved callers, and tests.
- **State space provably unmoved without re-running TLC.** Stripping comments from all three `TlaSpecDevCli.tla` files and diffing round 3 → round 4 yields **IDENTICAL** in every tree. RC-02's model change is annotation only, so the 10,331,543 / depth 26 figure I measured independently in round 3 still holds by construction. RC-02's claim of an identical re-run is consistent.
- **Full re-enumeration:** `N = M = 6,210`; **IN 40 / out-of-model 6,170 / ESCALATION 0**. In-model surface 52 files (40 `.py` + 12 non-source), **all read, 0 inferred**.
- **Every CLI leaf has a modeled action.** The external surface grew 93 → **110** (17 subcommands, 11 positionals, 82 options). The 11 **leaf** subcommands map 1:1 onto modeled actions; with `BuildSkillCli`, `InstallLocalCli`, `RecordBudgets`, `UpdateTicketDesired`, `UpdateTicketCurrent` and `CloseTicketWeakened` that is 17, matching the 17 `@command` annotations exactly.
- **All 199 write/create sites in the 40 in-model modules enumerated** (`round4/in-model-write-sites.txt`). Every one resolves to a declared port, a path guard, or a quoted inventory line. The ~150 in `production_adapters.py` / `adapter_case_runtime.py` are the spec-unit adapters building fixture repos in temp trees: in-model as **surface** (`:273`, which answered round-2 ESC-9) and out-of-model as **behavior** under `semantic_model_rule`'s first sentence — "integration harnesses, or validation scripts". Quoted line, so inventory, not gap and not escalation.

### 1.3 One finding that is neither a gap nor an escalation: the plan's inventory arithmetic is stale

`ticket_plan.yaml:63` and `:255` say the granularity limitation covers **"72 of the 78 options"** and **"the five group subcommands"**. The surface is now **82 options, 11 positionals and six group subcommands** — `generate` and `generate cases` were added by RC-01 and the counts were not.

I am not counting this as a gap (the plan is not in-model surface) and not as an escalation (the *rule* is stated generally — "per-flag CLI variants are out-of-model" — and plainly covers the 76 non-guard options; only the appended arithmetic drifted). But it is the fourth ticket in a row to ship a stale internal figure, in the one document this gate reads its scope from, and it is exactly the class N-3's checker was built for. **`tests/test_source_citations.py` does not cover `ticket_plan.yaml` counts.** Recommend extending the count-check RC-01 wrote for the manifests to the plan's own inventory arithmetic.

---

## 2. Does the loop terminate?

**Round 4 says yes, and the round-3 alarm was a real signal about a real
mechanism — just not the one it looked like.**

| Round | Remediation shipped | Gaps closed | Gaps created |
|---|---|---|---|
| RC-01 | 2 actions, 1 variable, 4 ports, 1 CLI subcommand, 5 invariant rewrites | 9 | **3** |
| RC-02 | 0 actions, 0 variables, 0 ports, 0 subcommands (a guard, comments, two checkers) | 3 | **0** |

Round 3's worrying data point was that **100% of the remaining gaps were newly
created**, which is consistent with "modelling surface reliably produces new
unmodelled surface". Round 4 discriminates between that hypothesis and a simpler
one, and the simpler one wins:

> **New gaps scale with new MODELLED SURFACE, not with remediation.** RC-01 added
> a subcommand, two actions, a variable and four ports and produced three gaps —
> ~0.4 gaps per unit of new modelled surface, and two of the three were in
> precisely the surface it added. RC-02 added none and produced none.

So the loop **is convergent**, and the convergence condition is legible: it
terminates when a ticket stops adding model surface. It is not a treadmill. But
the corollary is the number worth carrying into the owner's decision:

> **Every increment of model surface has cost ~1.5 new gaps and ~8× state space.**
> RC-01 took the model from 1,292,951 to 10,331,543 distinct states (7.99×,
> bound 9.53×) and created three gaps closing nine. That is the price of coverage
> on this model, measured over two rounds rather than asserted.

12 → 9 → 3 → 0 with 7 → 4 → 0 → 0 escalations. **If you are closing on the gate,
close: it is zero and the zero is earned.**

---

## 3. The judgement you asked for, separately from the verdict

> *Of the surface still unmodelled, is any of it load-bearing for GENERATING
> CASES or for the ORACLE seeing effects — as opposed to bookkeeping fidelity
> about our own CLI?*

**No. The remaining unmodelled surface is bookkeeping.** And the more useful
half of the answer: **the two things you care about are blocked by surface that
is already modelled, and more coverage makes the first strictly worse and does
nothing for the second.** I verified both by running them, not by reasoning.

### 3.1 The full inventory, classified against your question

| Inventoried surface | Load-bearing for generation? | For effect observation? |
|---|---|---|
| External view; 76 non-guard options; 6 group subcommands' exit-2 | **No** — cases are enumerated from the TLA state graph, not from the flag surface | **No** |
| `tests/**`, `test_graph/**`, `specs/*/tests/**` | No | No |
| `examples/**` | No (other programs) | No |
| Wrapper/close/start/scaffold scripts; advisory internals | No | No |
| `spec_double_compiler/**`, `templates/**` | It **is** the generator, but nothing about it needs modelling for generation to work | No |
| Adapter fixture writes | No | Only as noise — see §3.3 |

### 3.2 Generation is blocked by modelled surface, and coverage made it worse

`tla-spec-dev generate cases specs/current/TlaSpecDevCli.tla specs/current/MCsmall.cfg`
was run in full by RC-02 (`generate-cases-mcsmall.txt`) — **on `MCsmall.cfg`, the
config that exists expressly to make a corpus tractable.** It produced
**3,678,217 cases** from 118,573 distinct states, a **7.4 GB `cases.py`** CPython
cannot import, and **18,391× the manifest's own
`max_internal_cases_per_component: 200`**, so the shipped cap gate refused it and
exited 2. I confirmed the tractable-config premise independently in round 3:
MCsmall is 118,573 distinct states at depth 16; `MC.cfg` is 10,331,543 at depth 26.

**Every one of those 3.7M cases comes from surface that is modelled.** The
blocker is not a coverage gap; it is that the modelled state graph is ~87× larger
than the corpus cap, on the small config. And the direction of travel is the
decision-relevant part:

> **Closing coverage gaps grew the state space 7.99×, and the corpus grows with
> it.** RC-01 closed nine gaps and made generation ~8× harder. There is no
> version of "model more of the CLI" that improves case generation on this model;
> the two objectives are directly opposed.

### 3.3 The oracle is blocked by the process boundary, not by coverage

**The oracle ran, and I re-ran it three times myself rather than reading the
report.** Verdict `unobservable`, exit 1, every time. What it reports:

- **9 of 12 ports report DEAD** — `spec_tree_delete`, `evidence_report`,
  `git_metadata`, `test_process`, `runner_process`, `mutation_write`,
  `corpus_process`, `cli_download`, `cli_artifact_delete`. Only three are
  exercised (`cli_artifact`, `cli_selftest_process`, `spec_tree`). The program
  demonstrably performs most of the dead ones.
- **0 of the 14 stable gaps are effects of the action under test.** All 14
  enumerated (`round4/verify-effect-conformance-run2.txt`): 13 are the adapter
  spawning `python3 scripts/tla_spec_dev.py … scaffold project|scaffold
  workflow|open ticket` to replay a case's precondition, and 1 is the sandbox
  creating its own work directory.
- The reason is stated by the tool itself, `effect_conformance.py:1141-1145`:
  *"in-process CPython only … No patch crosses a process boundary."* Every
  adapter spawns the CLI as a child, so the program's real writes happen where
  the sandbox cannot see them.

**RC-02 characterised this correctly and I am confirming it, not discovering it**
— its README already names the adapter's `materialize_before` replay as the
source and calls the `unobservable` verdict the honest one. Credit where due.

**The consequence for your question is decisive:** a port declared for an action
whose effects occur in a child process is dead on arrival. **No amount of
additional model coverage moves that number.** The fix is instrumentation across
the process boundary (or in-process adapters), which is an oracle change, not a
model change. RC-02 also reports 9 of 17 adapters cannot execute a case at all.

### 3.4 New finding: the oracle's gap count is not reproducible **[major, mine]**

RC-02 reported one run. I ran the identical corpus against the identical tree
three times with the documented command:

| Run | observed | gaps | dead | verdict |
|---|---|---|---|---|
| RC-02, committed | 57 | **20** | 9 | `unobservable` |
| mine, run 1 | 67 | **15** | 9 | `unobservable` |
| mine, run 2 | 50 | **14** | 9 | `unobservable` |
| mine, run 3 | 50 | **14** | 9 | `unobservable` |

**Stable:** verdict, 8 cases, 12 declared ports, **9 dead ports**, 15 unobservable
targets, exit 1. **Not stable:** observed effects (50-67) and **the gap count
(14-20, a 43% spread)** — the number that would gate.

**Mechanism, identified:** `specs/current/.effect-conformance-work/` is untracked
and **persists between runs**. A first run observes the directory creation a
later run does not, so the observed-effect count depends on working-tree state
left by previous runs. My run 1 was a first run in this tree; runs 2 and 3 were
not; RC-02's was a third point on the same curve.

This contradicts the epic's own eval aim (3) — *"BE RERUNNABLE AND DETERMINISTIC…
Score determinism by rerunning, not by asserting it. A nondeterministic corpus is
a finding, however good its first run"* — and it was found by doing exactly that.

**It is not a coverage gap** — it is a fidelity/correctness defect in
`scripts/effect_conformance.py`, and MF-026 measures completeness. Counting it
would inflate the verdict. **But it is load-bearing for your question**: the
oracle's headline finding is not reproducible, so it cannot yet gate anything.
**The dead-port count is stable at 9**, which is the half RC-02's N-1
counterfactual relied on — that conclusion survives, and RC-02's own concession
stands: `cli_download` and `cli_artifact_delete` report dead in both arms, so my
round-3 "one run would have caught G-9" was right about the mechanism and
one-third right about the instance.

### 3.5 The honest balance, both ways

**Against continuing:** two eval rounds moved bug detection by zero cells; the
scanner's decomposition criterion (`modularity_q > 0`) cannot fail and flipped on
one added variable; every check shipped has been defeated cheaply; generation is
87× over its own cap on the small config and coverage made it 8× worse; the
oracle sees the harness rather than the program and its gap count varies 43%
between runs.

**For the record, what modelling did buy:** the guard-flag work (round 3 §6.1,
which I reproduced with TLC) found a genuine safety defect — `ClosedTicketsPassed
SpecUnitTests` held over 1,292,951 states **for the wrong reason**, because
`--accept-new`'s bypass was not in the state space at all. That is one real,
otherwise-invisible defect in four rounds, in this CLI's own lifecycle rather
than in a user's program.

**My read: that supports your redirect rather than undercutting it.** The
technique found a bug about *its own bookkeeping*, at a cost of 8× state space
and three new gaps, while the thing you want — catching content bugs in a user's
program — was measured at zero. **The remaining gaps are bookkeeping, the number
is zero, and I would close on it.**

---

## 4. Dispositions

**In-scope gaps: none. Escalations: none.**

**Out-of-model inventory** — 6,170 source rows against `:275-282`, plus the
External view (`:253`), 76 non-guard options and six group subcommands (`:255`,
whose arithmetic is stale — §1.3), harness and wrapper surface (`:83-96`,
`:27-29`), and `specs/.history/**` (`:277`).

**Findings recorded, not counted as gaps** (each a fidelity or record defect, not
unmodelled surface):

| # | Finding | Severity | Owner |
|---|---|---|---|
| **F-1** | Effect-conformance gap count varies 14→20 across runs of an identical corpus; mechanism is a persisted `.effect-conformance-work/` | major | `scripts/effect_conformance.py` |
| **F-2** | 0 of 14 gaps are program effects; 9 of 12 ports dead because the sandbox does not cross the process boundary (confirming RC-02) | major | oracle design |
| **F-3** | `ticket_plan.yaml:63`/`:255` say "72 of the 78 options" and "five group subcommands"; the surface is 82 and six | minor | the plan |

---

## 5. Verdict

- In-scope gaps: **0** · Escalations: **0** · New gaps from RC-02: **0**
- **Verdict: `pass`**

`PASS` is defined as zero in-scope gaps with a possibly non-empty out-of-scope
inventory. That is the state. The declared in-model surface is 52 files, all
read; the row set is 6,210 with every row disposed against a quoted plan line;
port↔action consistency, `@port` mirroring, manifest counts and internal
citations are all now enforced by shipped parametrised tests rather than by an
auditor's attention.

**The gate no longer refuses the workflow close.** Whether the epic *should*
close is your call and §3 is my input to it, not a gate condition.

The proposed ledger block is at
`round4/coverage_audit_ledger_input_proposed.yaml` and is **not applied**.

---

## 6. Attestation

1. **Row counts.** Sweep 1: N = M = 6,210, asserted in-script. In-model: 40 `.py`
   + 12 non-source = 52, all read, 0 inferred. External surface: 110, walked from
   the shipped `argparse` tree. In-model write sites: 199, all enumerated and
   dispositioned. Rounds 1-3 raws unmodified.
2. **Surface not walked.** Non-source files outside the 12 in-model ones; all
   out-of-model by plan line. Code executed this round: the full test suite, the
   effect oracle ×3, and (round 3) TLC.
3. **Read vs inferred.** 52/52 in-model read. 6,170 out-of-model classified from
   path against explicit globs — classification, not coverage.
4. **Scope decided by reasoning:** none. No filter applied.
5. **Reproducible?** Yes — `round4/cac_ac_classify_v4.py`, and the oracle
   nondeterminism is a three-command recipe anyone can repeat.
6. **Findings about the prompt.** Rounds 1-3 stand. Round 4 adds one: **the
   prompt has no notion of a verdict that is clean but uninformative.** This
   report is a `pass`, and the two most decision-relevant facts in it — that the
   oracle cannot see the program, and that closing coverage gaps grew the corpus
   8× past its own cap — are recorded in §3 only because the coordinator asked a
   question the procedure does not contain. A gate that returns `pass` while the
   instrument behind it reports `unobservable` should be required to say so in
   the verdict, not in an appendix. **Recommend a mandatory "what this pass does
   not tell you" section**, sourced from the oracle's own last verdict, so that a
   future reader of a clean MF-026 report cannot mistake it for a working
   toolchain.
