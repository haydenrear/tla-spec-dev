# MF-023 — what pointing the toolchain at its own repository found

Every finding is reproduced from a recorded command in this directory. Where a
tool proved inadequate the finding is stated plainly rather than worked around,
per the ticket's governing rule: a hand migration that hides a broken tool is
the worst possible outcome.

---

## FINDING 1 — `analyze complexity` does not resolve `EXTENDS`, so it scores every decomposed model on a fraction of itself, and the error always points at PASS

**Severity: critical. This one undermines the epic's own binding gate.**

`scripts/analyze_complexity.py` is a single-file textual parser. It reads the
`VARIABLES` block of the file it is given and derives every domain by looking up
one literal operator name -- `TypeInvariant`, line 746 -- in that same file. It
never opens an EXTENDSed module.

| Target | Variables the tool sees | Reported bound | Verdict |
|---|---|---|---|
| pre-split `TlaSpecDevCli.tla` | 9 of 9 | 699,840 | FAIL (correct) |
| `Internal.tla` (7 vars) | 1 of 7 domains | **3** | FAIL, on wrong evidence |
| `External.tla` (9 composed) | **2** | **1** | **PASS** |
| shipped example `Internal.tla` | 0 of 6 domains | **1** | **PASS** |

Two mechanisms, one root cause:

1. **Cross-module operator references are unresolvable.** `Internal.tla` has a
   good `TypeInvariant` constraining all 7 variables, written against
   Core-defined domain names (`setup_phase \in SetupPhases`,
   `ticket_state \in [Tickets -> TicketStates]`). The tool understands only
   literal inline sets (`0..5`, `{"a","b"}`), so it reports 6 of 7 variables as
   "unconstrained by TypeInvariant -- excluded from the bound" and computes
   **bound = 3**. Factoring shared domains into Core -- the textbook
   decomposition move -- silently deletes them from the gate.
2. **EXTENDSed variables are invisible.** `External.tla` inherits 7 variables.
   The tool sees only its own 2, reports `bound = 1 (product of 0 bounded
   dimensions)`, and returns **VERDICT: PASS**.

**The error is never conservative.** Missing variables always shrink the bound,
so a decomposed model always looks cheaper than it is. `max_state_space_bound`
-- which MF-019 established as the binding budget at 70.0% -- cannot fail on any
decomposed model.

This is the degenerate escape rule 5 forbids: a hard gate that silently disables
itself. It fires not on malformed input but on the correct, mandated
architecture. The shipped example has been scored this way (bound 1, PASS) for
the entire epic.

Also structural: TLA+ forbids redefining an inherited operator, so **both views
cannot carry a `TypeInvariant` at once**. The tool's single hardcoded name is
incompatible with a two-view decomposition. Internal keeps the name so its gate
stays live; External's reported bound is vacuous no matter what and is reported
as such rather than banked.

Evidence: `analyze-complexity-presplit.txt`, `analyze-complexity-internal.txt`,
`analyze-complexity-external.txt`.

Recommendation (owner approval; this ticket declares no production scope):
resolve EXTENDS transitively before building the dimension table, and treat
"no TypeInvariant found" as a hard refusal rather than "everything unconstrained".

---

## FINDING 2 — the cut `analyze complexity` proposed does not fix the budget the same command reports as failing

The cut was proposed by the tool, and the proposal was **overridden**. The
override is the finding.

```
  graph modularity Q = 0.012 over the variable interaction graph
  C1: kill_test, lastCommand, result, setup_phase, spec_root, ticket_state  (6 variables, 14 actions)
  C2: complexity_gate, corpus_gate, effect_conformance  (3 variables, 4 actions)
  VERDICT: FAIL -- component C1 is touched by 14 actions, exceeding max_component_actions 8
```

The proposed C1 **is** the failing component, unchanged. Adopting it verbatim
would produce a decomposition that fails identically. Q = 0.012 is the tool
saying so: modularity near zero means the partition is no better than random.

What the tool could not do, but its own evidence supports, is read *why* Q
collapsed. Its MEASURED R/W matrix shows `lastCommand` and `result` are the only
variables written by **all 14 actions** -- they connect everything to everything,
and no partition of a near-complete graph has good modularity. They are the hubs.
The cut that works moves them out, which is exactly the Internal/External channel
split the doctrine already mandates.

The tool supplied the measurement that determined the cut while proposing a
different, non-viable cut. Full reasoning in `cut-decision.md`.

---

## FINDING 3 — `max_component_actions` is unsatisfiable by ANY partition, so it is not measuring the cut

The epic's motivating finding -- `C1 is touched by 14 actions, exceeding
max_component_actions 8` -- was carried since MF-011 as a true finding that
decomposition would resolve at the root. **It does not, and cannot.**

From `component-cap-satisfiability.txt`, computed from the tool's own matrix:

```
  lastCommand          touched by 14 actions
  result               touched by 14 actions
  setup_phase          touched by 12 actions
  spec_root            touched by 10 actions
  ticket_state         touched by  5 actions
Lower bound on the action-count of ANY partition's largest component: 14
max_component_actions = 8  ->  SATISFIABLE BY SOME PARTITION: False
```

Even the **singleton** `{setup_phase}` is touched by 12 of 14 actions. Any
partition places it somewhere, and that component is touched by >=12 actions
however the rest is cut. After moving the two channel hubs to External,
Internal's floor is still 12.

The reason is structural and general to CLIs: `setup_phase` and `spec_root` are
read as preconditions by every command (`root = spec_root`, `setup_phase >= ...`).
The heuristic counts read-touches, so a variable every command validates makes
its component maximally coupled by construction. **The metric counts commands,
not coupling.**

This is the "gate comparing quantities that are not commensurable" that MF-017's
`budget-and-metric` category named as the live candidate, and the same class of
error MF-022 already corrected once for `max_distinct_states`.

**`max_component_actions` was NOT renegotiated and no `--allow-over-budget` was
used to make it pass.** The Internal view fails the heuristic and is reported
failing.

Recommendation (owner approval, not applied): count only write-touches, or
exclude read-only touches, or express the budget as coupling (Q) rather than a
raw count. The architectural alternative -- promoting `setup_phase`/`spec_root`
into a contract environment at the port, which the issue text says the budgets
presuppose -- is real and written up in `refinement.md`, but it is a scope
change requiring approval.

---

## FINDING 4 — no adapter in this repository can execute a generated case; the corpus path has never worked

**This is why nine tickets shipped green while a broken seam stayed hidden.**

`run_generated_case_adapters.py` drives each case through an adapter's
`run(case, ...)`. All **16** adapter classes in `production_adapters.py`
implement `apply(target_repo, ...)`. Not one implements `run`.

```
case_0006_analyze_complexity via AnalyzeComplexity: TypeError: adapter
  <production_adapters.AnalyzeComplexityAdapter object> does not define run(case, ...)
```

...for every case and every adapter (`effect-conformance-internal.txt`).

The two paths never met: the spec-unit suite calls `apply()` directly, so the
adapters are thoroughly tested and simultaneously unreachable from the corpus.
Case execution was deferred in every ticket of this epic, so no run crossed the
seam. **The first run that did found it immediately.**

Downstream consequences, all real:

- **Effect conformance reports `dead_surface`, 0 observed effects over 40 cases,
  all 5 declared ports dead** (`effect-conformance-internal.json`). MF-013 handed
  forward a requirement that each port be "observed by a case or removed". It
  cannot be discharged: nothing can be observed while no case can run. The ports
  are retained and the verdict reported honestly. Deleting five correctly-declared
  ports to turn `dead_surface` into `clean` would be gaming a metric by removing
  evidence -- rule 3.
- **The kill test cannot produce a rate** (FINDING 5).
- The verdict is `dead_surface`, **not** `unobservable`. MF-027 predicted this
  repository's two `process.spawn` ports would force `unobservable`; that
  prediction is not reached, because execution fails before any spawn occurs.
  The `unobservable`/`process.spawn` question remains **untested on a real
  corpus** and is NOT resolved by this ticket.

**Partially fixed here:** `case_adapters.toml` was missing bindings for four
model actions -- `RunEffectConformance`, `RunKillTest`, `UpdateTicketDesired`,
`UpdateTicketCurrent`. The first two already had adapter classes and were simply
never mapped. All 14 actions are now bound and two new adapters written. That
closes the binding desync; it does not fix the protocol mismatch, which is
production scope this ticket does not carry.

---

## FINDING 5 — the kill test's control run worked exactly as designed, and refused

```
CONTROL FAILED: the corpus does not pass on the UNMUTATED program, so every
mutant would be recorded as killed by that same pre-existing failure and the
kill rate would be a meaningless 1.0. Fix the corpus, then measure. Nothing has
been learned about the representation.

REFUSING to seed any mutant. [...] There is no flag that skips the control.
```

Exit 2, no rate, no mutant seeded (`kill-test-internal.txt`).

This is the safeguard MF-016 built after catching itself reporting a spurious
7/7. **It is now validated on a real target rather than the worked example**:
handed a genuinely broken corpus (FINDING 4), it declined to report the
flattering number. That is the most valuable positive result in this ticket.

**This repository's kill rate remains unmeasured**, and is reported as unmeasured
rather than as anything else. Neither oracle was relaxed, `kill_rate_floor` was
not lowered, no mutant was deleted.

Secondary correctness result: on the system Python 3.9 `run_kill_test.py`
refuses outright rather than parsing the mutant catalog with the fallback
parser, on the stated grounds that a partially-read catalog would under-report
the required boundary set. Also a refusal rather than a degradation.

---

## FINDING 6 — `analyze corpus` is OOM-killed by exactly the corpus it exists to catch

`load_corpus()` (`corpus_diagnostics.py:873`) imports the generated package and
does `list(module.CASES)`.

Generating the Internal view at the real instance produced **999,635 cases in a
1.35 GB `cases.py`** -- 4,998x the `max_internal_cases_per_component: 200` cap.
Running the cap gate over it:

```
exit=137            # SIGKILL, out of memory
```

The gate cannot report on the condition it was built to detect. Its verdict is
available only for corpora small enough not to need it.

At a reduced instance (one ticket, one root -> 15,336 cases) the gate works and
is genuinely useful (`analyze-corpus-internal.txt`): it refuses (exit 1), trims
nothing, and reports distribution, dominant and starved strata, and a 4112x
skew. The diagnostic is good; only its implementation does not scale.

Two further real problems from the same run:

- **The cap is measured after the cost is paid.** Generation writes the whole
  1.35 GB corpus and *then* reports it over cap. The External view's generation
  **exhausted the disk** (704 MB `.dot` plus a partial `cases.py`) and had to be
  killed. A cap enforced only post-hoc does not protect the resource it caps.
- **The corpus is dominated by the oracle actions.** Measured
  (`corpus-distribution-internal.txt`): `RunSpecUnitTests` 39.6%,
  `RunEffectConformance` 17.1%, `RunKillTest` 12.9%, `AnalyzeComplexity` and
  `AnalyzeCorpus` 8.6% each -- 86.8% of the corpus -- while `BuildSkillCli`,
  `InstallLocalCli`, `ScaffoldProject` and `RecordBudgets` get **1-2 cases each**.
  The oracle actions are enabled at nearly every reachable state with a free
  choice of verdict, so they cross-multiply against the whole lifecycle state
  space. The bootstrap sequence -- what a new user hits first -- is the most
  starved stratum in the corpus.

---

## FINDING 7 — TLA+ stuttering was being emitted as spec cases (fixed, with proof)

The pre-split module carried `Stutter == UNCHANGED vars` as an explicit disjunct
of `Next`. In TLA+ this is redundant: `[][N]_v` already permits a step leaving
`v` unchanged. But case generation emitted **one `InternalStutter` case per
reachable state** -- 42,861 cases, 4.3% of the Internal corpus -- for which no
adapter can exist, because stuttering is not a program behavior.

Removed from both views. Measured, not assumed:

| | with disjunct | without |
|---|---|---|
| Internal distinct states | 42,861 | **42,861** |
| Internal depth | 24 | **24** |
| Internal generated | 999,636 | 956,775 (-42,861 exactly) |

Identical reachable behavior; only the self-loops disappear. A reduction with a
proven-identical reachable state set, not an abstraction.

---

## FINDING 8 — four desyncs that no oracle checks, now reconciled

MF-026 found these by reading. Each is fixed, and where possible a check now
prevents silent recurrence.

1. **`spec_manifest.yaml` pointed at `Core.tla`/`Internal.tla`/`External.tla` --
   all three absent -- and nothing failed.** The files exist.
   `tests/test_source_model_references.py` resolves *every* path-valued
   `source_model:` entry and **fails** on a dangling one. Verified by
   deliberately re-breaking a reference (2 failed), then restoring (3 passed).
   The previously-passing case now fails, as the acceptance criterion requires.
2. **`@port` annotations had empty intersection with declared effect ports.**
   Annotations named the *command* (`build_skill_cli`, `scaffold_project`,
   `run_kill_test`); declarations name the *boundary* (`cli_artifact`,
   `spec_tree`, `evidence_report`, `tlc_process`, `test_process`). The decomposed
   modules now annotate every action with the **declared port names**, so
   annotation and declaration are one vocabulary.
3. **Neither view existed.** Both now do.
4. **The manifest described an action absent from every model.**
   `ValidateTestGraphCli` appeared in `specs/program_model/spec_manifest.yaml`
   (as action, command, and port command) and in `case_adapters.toml`, but in no
   TLA module. It is a *validation harness* invocation, and the manifest's own
   `test_modeling_rule` forbids modeling validation harnesses as program
   behavior -- so the reconciliation is to drop it from the action vocabulary
   rather than invent a model action. Removed; `TestGraphCliAdapter` and its test
   are retained as an ordinary harness test.

Also reconciled: `specs/program_model/spec_manifest.yaml` still named
`cli_built`, `cli_installed`, `project_scaffolded`, `workflow_scaffolded`,
`active_tickets`, `desired_ready`, `current_ready`, `spec_unit_tests_passed` and
`closed_tickets` -- collapsed by MF-020, MF-022 and MF-025. Its state and action
inventory now matches the decomposed model.

---

## The escapes, tested

| Escape | Default path? | Visible? | Verdict |
|---|---|---|---|
| `--allow-over-budget` | **No.** Without it generation refuses, exit 2, naming the failing components (`gen-internal-refusal.txt`) | Yes -- refusal text names the flag | Correct. Used once, deliberately, recorded in `gen-internal-override.txt` |
| Case-cap override | **Does not exist.** Generation refused the over-cap corpus *even with* `--allow-over-budget` -- the flag covers only the complexity gate, exactly as modeled | Yes | Correct |
| Kill-test floor waiver | **Does not exist.** No flag skips the control run | Yes | Correct |
| Budgets fallback, `analyze complexity --manifest <path>` | Fires when the named manifest is unreadable | **Yes -- warns**, distinguishing "no readable spec manifest" from "budgets block is missing keys", and names the source | Visible. Still substitutes defaults and continues, and the VERDICT reads as authoritative. Recommend refusing on *unparseable* while defaulting only on *absent* |
| Budgets fallback, `analyze corpus` with **no** `--manifest` | **YES -- THIS IS THE DEFAULT PATH** | **NO. Completely silent.** | **FIRST-CLASS FINDING -- see FINDING 9** |

**One override did turn out to be a silent default**, and it was found by the
coverage audit rather than by the escape sweep in this section. The sweep's
original conclusion -- "no override turned out to be a silent default" -- was
**WRONG**, and is corrected in FINDING 9 rather than quietly amended. The error
is instructive: the sweep tested `analyze complexity --manifest <bad path>`,
which warns loudly, and generalized from it to "the budgets fallback is not
silent". It never tested the path where the flag is simply **omitted**, which is
both the silent one and the one an agent hits by default.

A second silent degradation, not an override at all, is FINDING 1: the static
bound gate disables itself on correct input with no warning whatsoever. That is
worse than a silent default flag, because there is no flag to audit.

---

## What could not be checked

Absence of a result is not a result.

- **MF-015's transitive import check produced no false positive against the real
  adapter tree -- but vacuously.** The risk MF-015 flagged was an adapter
  importing `spec_double_compiler.runtime` while the declared production package
  is the CLI. **No adapter in this repository imports `spec_double_compiler` at
  all**, and there are no Python Test Graph adapters. The scenario is not
  reproducible here, so the check remains unproven against a real instance of
  the case it was built for.
- **`unobservable` vs `process.spawn`** -- untested, blocked behind FINDING 4.
- **This repository's kill rate** -- unmeasured, blocked behind FINDING 4.
- **`run_distributed_history_validation.py --mode local`** -- still cannot
  complete. The example's External model is refused by the complexity gate
  (`C2 touched by 9 actions`), reproduced in this ticket. Pre-existing; the
  example runner remains unusable.


---

## FINDING 9 — `analyze corpus` gates against built-in defaults, silently, when `--manifest` is omitted

**This is the silent default the ticket asked to be hunted for, and the escape
sweep in this document initially missed it.** Found by the MF-026 coverage audit
re-run (escalation E-7), then reproduced directly.

`scripts/corpus_diagnostics.py:541`:

```python
budgets = load_budgets(manifest_path, warn=warn) if manifest_path else load_budgets(Path("__missing__"), warn=False)
```

When no manifest is supplied, the corpus cap gate loads `DEFAULT_BUDGETS` with
warnings **explicitly suppressed** -- `warn=False`, unconditionally, not
inherited from the caller's `warn`.

Reproduced (`override-silent-default.txt`):

```
$ python3 scripts/tla_spec_dev.py --spec-root specs analyze corpus <package> --view internal
corpus gate FAIL: 14304 internal case(s), cap max_internal_cases_per_component = 200 per component
source: <package path>
[...]

$ ... | grep -ci "warning\|default"
0
```

Zero occurrences of "warning" or "default" anywhere in the output. The gate
prints `cap max_internal_cases_per_component = 200` exactly as it would if that
number came from the negotiated manifest, and the VERDICT reads as authoritative.

Why this is the worst shape of escape, by this epic's own doctrine:

- **It is the default path.** Every other override in the toolchain requires the
  agent to type something (`--allow-over-budget`). This one is what happens when
  the agent says **nothing**. `references/architecture_tractability.md` states
  overrides "must not make degradation what happens when the agent says
  nothing" -- this one does exactly that.
- **It is invisible.** There is no line in the output to audit, so it cannot be
  caught in review of the evidence. Compare `--allow-over-budget`, which is
  explicit, loud, and recorded.
- **It silently discards a negotiated budget.** `max_distinct_states` was
  negotiated 50000 -> 500000 with a recorded derivation. A gate reading defaults
  is not reading that negotiation, and says so nowhere.
- **It is the same defect MF-013 already found once**, in the same helper. MF-013
  found `analyze complexity` silently falling back because the manifest was
  invalid YAML, called it "precisely the conditional check that silently
  disables itself when its input is absent that rule 5 forbids", and fixed the
  YAML. The `warn=False` call site was not found then and has been live
  throughout.

**Not fixed here** -- this ticket declares no production scope (`conflict_keys.production: []`).
**Recommendation (owner approval):** make the absent-manifest path either resolve
the manifest from the spec root (the CLI knows it -- `--spec-root` is a global
argument) or refuse. `warn=False` should not be reachable from a gate at all: a
budget the user did not declare is a budget the user did not agree to, and a
gate that does not say which budgets it used has not reported its verdict.

---

## FINDING 10 — `close ticket` picks the model file alphabetically, so on a decomposed tree it measures `Core.tla` and computes a fictitious −100% complexity collapse

The MF-019 complexity ledger **refused this ticket's close**. The refusal is
correct in its conclusion and wrong in its arithmetic, and both halves matter.

`scripts/spec_evolution.py:542-545`:

```python
tla_files = sorted(p for p in model_dir.glob("*.tla") if not p.name.startswith("MC"))
tla_path = tla_files[0]
```

**Alphabetically first.** On a decomposed tree that is `Core.tla` — the module
that by design carries constants and vocabulary and **no variables and no
actions**. `MC.cfg` no longer exists either, so the cfg falls through to
`sorted(glob("*.cfg"))[0]` = `External.cfg`. The ledger therefore measured
`Core.tla` against `External.cfg` and reported (`close-ticket-REFUSED.txt`):

```
  measured: variables=0 actions=0 bound=1
  delta:    direction=decrease (vs MF-026)
            variables: 9 -> 0 = -9 (-100.0%)
            actions: 14 -> 0 = -14 (-100.0%)
            bound: 699,840 -> 1 = -699,839 (-100.0%)
```

A total complexity collapse that did not happen. The manifest declares
`module: External`; the selector does not consult it.

This compounds FINDING 1. Between them, **the ledger cannot measure a decomposed
model at all**: the file selector picks the empty module, and even pointed at the
right one the parser cannot resolve `EXTENDS`, so any view reports fewer
variables than the model has. On a decomposed tree the ledger can only ever
report a decrease.

### The deadlock, stated plainly

The gate's rule is: a complexity **decrease** is REJECTED while retention
evidence is DEGRADED. Here:

- The decrease it measured (−100%) is **fictitious**, an artifact of the file
  selector.
- The retention degradation is **real**: `effect_conformance=dead_surface`,
  `kill_rate=incomplete_catalog`, `external_coverage=incomplete`. All three are
  honestly recorded and all three trace to FINDING 4 — no adapter implements the
  case-runner protocol, so no port can be observed and no kill rate computed.

So the gate reaches the right verdict for partly the wrong reason. And it cannot
be satisfied from inside this ticket:

- **Restore the retention evidence** — blocked. It requires changing the adapter
  protocol in `production_adapters.py`, and this ticket declares
  `conflict_keys.production: []`.
- **Withdraw the reduction** — not expressible. The ledger computes the delta
  itself from `analyze complexity`; there is no input by which a ticket can
  decline to claim a reduction it never claimed.
- **Override** — does not exist, by design: *"There is no override flag."*

**No override was attempted, `--accept-new` was not used, and no retention
verdict was softened to get past the gate.** Turning `dead_surface` into `clean`
by deleting the five correctly-declared ports, or recording the unmeasured kill
rate as anything other than unmeasured, would have passed the gate and would
have been precisely the degeneracy this epic exists to prevent.

**The MF-023 spec ticket is therefore left OPEN**, and this ticket stops at
PR-open rather than self-merging. The repository-owner deviation note authorizes
self-merge *"after the spec ticket is closed and the full validation matrix is
green"* — neither precondition holds, so the authorization does not apply.

### Assessment

This is the gate working. MF-019 recorded that its anti-gaming check had never
fired on measured evidence; it has now, and it fired against the ticket that
built the evidence. The correct response to a gate you cannot satisfy honestly is
to stop and report, which is what this ticket does.

The two defects that should be fixed before the close is retried, in order:

1. **The file selector must honor the manifest's declared `module:`** rather than
   taking `sorted(*.tla)[0]`. As written, every decomposed repository — the
   architecture the skill mandates — gets its ledger measured against the empty
   Core module.
2. **FINDING 1** — resolve `EXTENDS` so a view's real bound is measurable.

Then the genuine delta can be measured (Internal 231,621 → 42,861 distinct,
an 81.5% real reduction; External unchanged at exact retention) and the gate can
adjudicate the real numbers instead of an artifact.
