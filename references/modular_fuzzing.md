# Modular Representations And Spec-Guided Fuzzing

This reference defines what a good representation is, how to bound its
complexity, and how generated cases relate to fuzzing. Read it together with
`references/testgraph_adapters.md` and `references/edge-cases.md` before
authoring or reviewing any baseline. For moving an existing repository onto
this shape, read `references/migration.md`.

> ## Maturity: one shipped part, one experimental part
>
> This document covers two things at very different maturity, and the SKILL.md
> section "What Is Shipped And What Is Experimental" is the authority.
>
> - **SHIPPED and advisory:** the complexity **descriptor** — the dimension
>   table, state-space bound (or an explicit unknown), variables x actions
>   read/write matrix, graph-modularity score with near-decomposable clusters,
>   and dense-row / god-state detection. That is the "Budgets" section's
>   `analyze complexity` command and the decomposition method it supports. It
>   states facts and makes no suggestions (CD-01 removed the suggested-move
>   output); it never blocks.
> - **EXPERIMENTAL and NOT validated for bug-catching:** the differential-fuzzing
>   framing itself — "The Reframe", the "Oracles" (output/projected-state/effect
>   conformance), the mutation kill test, and the corpus discipline built on them.
>   It is real, retained infrastructure and an honest record of what was built,
>   but the **MF-038 kill probe measured that generated cases caught 0 of 9
>   subtle content/value/field/count bugs — kill rate 4/13 = 0.31** — with a green
>   control, because the oracles read effect *existence and process exit codes*,
>   not *content*. **The randomized-generation arm (Hypothesis) is a stub: the
>   design is two-armed (TLC exhaustive + Hypothesis random) and only the
>   exhaustive arm exists.** Do not expect any of it to catch bugs. Where a
>   passage below says a kill test "validates" a representation or that a baseline
>   without one is "unvalidated", read it as the *original design intent*, now
>   known not to hold — corrected inline.

## The Reframe (EXPERIMENTAL framing)

The workflow was designed as spec-guided differential fuzzing with a generated
reference implementation. This framing is a research aspiration, not a validated
capability (see the maturity note above):

- The TLA+ model is the input grammar and the oracle.
- TLC bounded exploration is the exhaustive input generator. Hypothesis
  strategies were meant to be the randomized generator — **but that arm is a
  stub and is not implemented**, so only TLC bounded-exhaustive generation
  exists today. Both were meant to feed the same oracle.
- The generated spec double is the reference implementation.
- Adapters are the fuzz harness.
- Invariants, projected-state assertions, and effect conformance are the
  sanitizers.
- The production program is the target.

The intended value system was empirical, like fuzzing: judge a representation by
the bugs it can catch, never by whether TLC passes. **That intent is unmet.** The
MF-038 probe showed the existing oracles do not catch content bugs (0 of 9, kill
rate 0.31), so today generated cases exercise the program but do not reliably
detect its faults. TLC passing still only proves the model is self-consistent, and
a passing kill test — as currently built — does not prove fidelity either.

Two failure modes follow from forgetting this:

- Optimizing only the cost metric. When the only visible numbers are TLC wall
  time and case count, the cheapest move is shrinking constants until TLC
  finishes. That produces a model too small to catch anything. Cost must be
  opposed by a value metric — see "Oracles" below.
- Structural compliance without fidelity. A checklist-complete baseline whose
  Test Graph adapters call program functions in-process is a fuzz harness
  that never executes the target.

The analogy imports fuzzing's economy, not its randomness. TLC is
bounded-exhaustive; the parts worth copying are harness quality dominating
everything, hard budgets, empirical value measurement, and corpus
distillation.

## Modular Representation Rule

Represent the program as a set of components. Each component is:

- Local state: bounded variables owned by that component alone.
- A pure transition: `(state, input) -> (state', output, effects)`.
- Declared effects: typed emissions on named ports. Effects are the only way
  anything leaves the component. One component's declared effects are another
  component's inputs, or externally observable behavior.
- Input ports: where inputs arrive — public-surface inputs or the effects of
  neighboring components.

TLA+ fits this exactly because actions are already pure relations over state.
Model effects as appends to named port variables (queues, sets, append logs).
Shared port types live in `Core.tla`. Production side-effect machinery —
databases, files, topics, HTTP calls — appears in the model only as the port
state that crosses a component boundary.

Fuzzing a component means enumerating inputs to its pure transition,
executing the real component code on those inputs, and measuring three
things: the output, the next state, and the observed side effects. Fuzzing
the External view means the same thing with inputs restricted to the public
surface of the deployed composition.

The soundness condition for a decomposition: no shared mutable state between
components except through declared ports. If two components write the same
variable without a port between them, the cut is wrong.

## Decomposing Into Fuzzable Components

When a model blows its budget, the fix is decomposition along measured
dimensions, not shrinking constants until TLC finishes. Perform this analysis
and record it as validation evidence:

1. Build the dimension table: for each state variable, its domain
   cardinality; the product is the state-space upper bound.
2. Build the variables x actions read/write matrix. Variables that only
   interact through a few actions are near-decomposable; those few actions
   are candidate port crossings.
3. Cut along minimum-interaction edges. Each cut becomes a declared port
   whose interface state is exactly what crosses the boundary — a queue's
   contents, a table's rows, an offset.
4. For each component, replace the far side of every port with a contract
   environment: a nondeterministic TLA+ action constrained by the neighbor's
   guarantee. This is what kills the state product — component state spaces
   add instead of multiplying, and interleavings collapse because the
   neighbor is one abstract action.
5. Keep one thin interface model containing only the port variables and
   crossing actions. Model-check it within budget. This is the
   protocol-between-components check that keeps the decomposition honest.
6. Use symmetry sets for identical actors and model the small scope: two
   instances, not N. Most interaction bugs manifest at cardinality two or
   three.

Default component-size heuristics (tunable per program, see "Budgets"):
at most ~6 state variables, ~8 actions, and 2 instances of any symmetric
actor per component model. A component above that gets cut again.

When the scan still warns and no clean cut is available — abstraction would
lose bug-catching power, or the R/W matrix is too dense for any narrow cut —
read `references/architecture_tractability.md`. It defines the three moves
(abstract, decompose, refactor), the diagnostics that choose among them,
and the creative representations for pieces that score poorly but must
exist in their current form. All three moves are recommendations the user
approves; a production refactor always requires explicit user approval.

## Budgets

Budgets are per-program and are set in conversation with the user during
scaffolding: propose the defaults below, ask which to adjust for this
program, and record the answers with a one-line rationale in
`spec_manifest.yaml`:

```yaml
budgets:
  tlc_seconds: 120                       # hard external timeout per TLC run
  max_distinct_states: 50000             # reachable states, per component model
  max_state_space_bound: 1000000         # static declared-representation ceiling
  max_internal_cases_per_component: 200
  max_external_cases_per_action: 50
  kill_rate_floor: 0.8                   # see "Mutation kill test"
  max_component_variables: 6
  max_component_actions: 8
  max_symmetric_instances: 2
```

`max_distinct_states` and `max_state_space_bound` measure different things and
are not interchangeable.

`max_state_space_bound` is the **advisory threshold** for the **static**
state-space upper bound reported by `analyze complexity`: the product of the
declared cardinality of every
bounded dimension in `TypeInvariant`. That figure is a Cartesian
over-approximation of the *declared representation* -- it ignores every action
guard, so it counts combinations the program can never occupy, and it routinely
over-approximates reachable states by two or three orders of magnitude. Its
ceiling therefore answers a capacity question: *if the type invariant were
tight, could TLC still finish inside `tlc_seconds`?* The default of 1,000,000
is derived from measured TLC throughput on a model of realistic expression cost
(~16,000 distinct states/sec, so ~1.9M within the 120s budget), rounded down
for slower hardware and more expensive models.

`max_distinct_states` is the advisory threshold for the **actual reachable**
states TLC finds. It can only be checked after a run, so `analyze complexity`
compares against it when a TLC report is supplied via `--tlc-report`.

Comparing the static bound against `max_distinct_states` is a category error: it
would warn about models that are comfortably within their real reachable budget.
This was MF-011's behavior and MF-022 corrected it, so each threshold now
measures the figure it was meant for.

**Complexity thresholds are advisory, not gates (MF-036).** A component model
over threshold produces a *warning and a recommendation* — decompose or
re-abstract — that names the component, variable, or action and a concrete move.
It **never blocks promotion, never refuses case generation, and never drives a
nonzero exit.** Complexity is a scanner: it tells the agent where the model is
dense so the owner can decide, with the user, whether to refactor. See
`references/architecture_tractability.md`, "Advisory, Not Blocking", which is
the governing doctrine and supersedes the older hard-gate framing. The 120-second
TLC rule in `SKILL.md` is the `tlc_seconds` default, and everything it says about
diagnosing state explosion before changing the model still applies as guidance.

The single exception is not a complexity gate at all: `analyze complexity` exits
nonzero only when it **cannot analyze** the model — an unresolved `EXTENDS`
hierarchy (the MF-030 fail-closed). "I could not measure this" is a genuine
error; "this model is complex" is a finding. Only the former is nonzero.

This analysis is mechanized. Run it and attach the report to the ticket's
`results/` evidence:

```bash
tla-spec-dev analyze complexity path/to/Model.tla path/to/MC.cfg \
  --out specs/tickets/<ticket>/results/analyze-complexity.txt
```

It prints the dimension table, the state-space upper bound with its dominant
dimensions, the variables x actions read/write matrix, the graph-modularity
score with near-decomposable clusters and candidate port-crossing actions,
and any variables lacking a justification linkage. When the model exceeds
`max_state_space_bound`, `max_component_variables`, `max_component_actions`, or
(with `--tlc-report`) `max_distinct_states`, it emits an advisory **warning**
that names the component/variable/action and **recommends** a concrete move —
but it still exits 0, and case generation still proceeds. The warnings are the
product; the old exit-nonzero-to-block was an over-promise (MF-036).

*History.* The complexity check was originally a hard gate with an
`--allow-over-budget` override. The override was withdrawn on 2026-07-18 as
degeneracy (an override flag turns a hard limit into a suggestion), and then on
2026-07-20 owner direction reframed the whole check as **advisory** after a
probe showed the gate hard-failed an ordinary 5-variable / 10-command CLI —
i.e. most real programs. There is no override flag now because there is nothing
to override: nothing blocks. A program that wants to record a tighter or looser
threshold still does so in `spec_manifest.yaml`, and that value tunes the
advisory warning rather than a build-breaking gate.

It emits **no suggested move**: CD-01 removed the abstract/decompose/refactor
chooser after validation showed it confidently wrong on standard TLA+. The
three moves remain the owner's design vocabulary in
`references/architecture_tractability.md`, applied by a person to the
descriptor's facts.

Two cautions the report carries in its own output, because both have already
cost real work:

- Every figure is labeled `[MEASURED]` — parsed from the spec + cfg. Any
  projected reduction an owner derives from it is **unverified** until the
  transition-level diff is read.
- Pass `--tlc-report` and `--baseline-tlc` to compare two TLC runs. A drop in
  generated states at constant distinct states and depth is reported as a RED
  FLAG, not a win: the distinct-state count is structurally blind to a deleted
  self-loop, because removing one returns to an already-known state.

## Oracles (EXPERIMENTAL — not validated for bug-catching)

Every fuzzed case is checked against up to four oracles. This whole section is
the experimental fuzzing layer. The oracles were designed to make a
representation's quality falsifiable; the MF-038 probe measured that, as built,
they do not catch content bugs (0 of 9; kill rate 0.31) because they check effect
*existence and shape*, not *content*. Read them as a modelling aid and a research
surface, not as a bug detector.

**All four are bounded to what is already modeled**, and that bound is
structural rather than incidental: output and projected-state conformance check
cases that exist, effect conformance checks a corpus generated *from the model*,
and the kill test seeds faults one per port and one per invariant — modeled
boundaries only. Unmodeled surface is never generated into a case, never
adapted, never mutated. **A subsystem with no representation is invisible to all
four while all four report green.** These oracles measure FIDELITY.
COMPLETENESS is measured by the coverage audit gate, below; neither implies the
other.

1. Output conformance: the real component's normalized output equals the
   spec double's output for the same `(state, input)`.
2. Projected-state conformance: the real system's observed state projects
   onto the case's expected `after` state.
3. Effect conformance: run the component in a sandbox (temp directories,
   fake transports, recorded HTTP) and diff observed side effects against
   declared effects.
   - An observed effect with no declared port **fails**. The model is blind
     to real behavior, which is the one thing a representation may not be.
     Model the effect, or change the program so it no longer emits it.
     There is no third option, and in particular there is no annotation
     that makes it acceptable.
   - A declared effect never observed across the whole corpus is dead model
     surface: remove it, or produce a case that exercises it. Prose
     explaining why it is unobserved does not resolve it.

   - **A target the sandbox cannot observe fails.** See "Observable scope"
     below. The oracle never returns a clean report on something it could not
     see.

   *Amended 2026-07-18.* This previously read "model it, or record an
   explicit out-of-contract justification" and "remove it or explain it".
   Both escapes are withdrawn: they let a representation stay blind to real
   behavior provided someone wrote a sentence about it. See "No Degenerate
   Escapes" in `architecture_tractability.md`, and note that the CEGAR
   section there already treats an undeclared observed effect as evidence
   that *demands* a model addition.

### Observable scope of the effect oracle (MF-027)

**The shipped oracle observes the in-process CPython runtime, and nothing
else.** `EffectSandbox` (`scripts/effect_conformance.py`) works by
monkeypatching `builtins.open`, the `os` / `shutil` / `pathlib.Path`
mutators, `subprocess.run`/`Popen`, and `socket.connect` **in the
interpreter that is running the harness**. No patch crosses a process
boundary.

That is a legitimate scope. A Python-only oracle is useful and honest — as
long as it says so. Until 2026-07-19 it did not, and that was the defect:

- A **Java or Kotlin adapter in a separate JVM** produced zero observations.
  Zero observations diffed against declared ports produced an empty gap
  list, and an empty gap list read as `clean`. Not hypothetical: the Test
  Graph SDK ships Java (`test_graph/sdk/java/.../Node.java`), so JVM nodes
  are first-class in this toolchain.
- A **spawned subprocess** was recorded as a `process.spawn` and nothing
  else. Everything the child did — every file it wrote, every socket it
  opened — was invisible, and silently so.

A clean report on a target the sandbox cannot see is indistinguishable from
a clean report on one it can. That is the silent-degradation class this epic
has purged repeatedly.

**The oracle now refuses.** Observability is granted only on positive
evidence: the adapter was resolved to a live Python object and called
in-process. Anything else — a declared non-Python `runtime`, a binding whose
`kind`/`channel`/reference names a JVM/JBang/node/container runtime, or a
target the runner could not resolve into this interpreter — yields the
`unobservable` verdict, which **fails**. Every observed `process.spawn`
additionally yields an explicit process-boundary finding naming the command,
*even when the spawn matches a declared port*: declaring `tlc_process` says
"I spawn java", not "here is what java then wrote".

`unobservable` outranks `gaps` and `dead_surface`. A diff computed over a
target that was never seen carries no information, so promoting a gap count
from it would dress an absence of evidence as a measurement.

**No configuration downgrades this verdict.** There is no flag, annotation,
manifest entry, or environment variable that turns an unobservable target
into a pass, and `tests/test_effect_conformance.py` proves the inverse
directly (`TestNothingDowngradesAnUnobservableVerdict`), exactly as MF-013
did for gap suppression. Observability-shaped keys such as
`assume_observable`, `skip_observability`, and `trusted_runtime` are scanned,
reported in `ignored_suppression_keys`, and honored not at all. The opt-out
is the silence.

### Known limitation: exported Test Graph cases get no effect checking

`scripts/export_testgraph_cases.py` has **zero** references to effect
conformance, and this is not an oversight in that script — it is the same
process boundary described above. Exported External cases execute in JBang
and uv Test Graph nodes, in their own processes, outside any `EffectSandbox`.
They therefore receive **no effect checking at all**.

Two consequences worth stating plainly:

1. External coverage and effect conformance are independent members of the
   constraint set. A green Test Graph run says nothing about effects.
2. For a non-Python project, the effect oracle currently covers whatever
   part of the system has in-process Python adapters, and refuses the rest.
   For a pure-JVM project that is the entire system, and the honest output
   is a refusal rather than a green report.

Closing this properly needs a **different observation mechanism** behind the
same port-declaration schema — a JVM agent, syscall capture (eBPF/dtrace),
or a container-level recorder — so that declarations stay portable while the
recorder is swapped per runtime. That is a second implementation, not an
extension of `EffectSandbox`, and it is tracked separately in
[issue #44](https://github.com/haydenrear/tla-spec-dev/issues/44),
"JVM-capable effect observation behind the port-declaration schema". It is
explicitly **out of scope** for MF-027.
4. Mutation kill test: the representation's falsifiable experiment.
   - Hypothesis: representation R captures the bug-relevant behavior of
     component C at its port surface.
   - Experiment: seed k faults into production code — at minimum one per
     port and one per invariant — run the generated cases, and require the
     kill rate to meet `kill_rate_floor`.
   - A surviving mutant at a modeled boundary is proof the representation is
     too abstract there, and points at the exact variable or action to
     refine.

The original doctrine here was "a baseline without a passing kill test is
unvalidated." **MF-038 falsified that as a bug-catching claim**: the kill test
passed its control and still let all 9 subtle content bugs survive (kill rate
0.31), so a passing kill test does not establish that a baseline catches bugs.
The kill test remains useful as a *coverage* signal — it tells you a seeded fault
at a boundary was exercised — but not as validation. Note the difference from the
negative projected-state check in
`examples/distributed_history/`: that check swaps in a wrong expected
projection, which validates the harness plumbing. The kill test seeds a
wrong production behavior, which validates the representation.

The kill test was *intended* to make budgets safe — constants cannot be shrunk
to nothing if a trivial model stops killing mutants, so cost cap plus value floor
would be a real optimization target. **That safety is not yet real**: because the
kill test does not catch content bugs (MF-038), it cannot currently be trusted to
detect a model shrunk past usefulness. Until it earns that role on a real app
(MF-037), guard against over-shrinking with human review of the R/W matrix and the
retained behavior, not with the kill rate.

**Mechanized by MF-016** as `tla-spec-dev run kill-test`
(`scripts/kill_test.py`, `scripts/run_kill_test.py`). Five properties are
load-bearing, and each exists to close a specific way the experiment could be
faked:

- **Coverage is computed, not promised.** The required boundary set — one per
  declared port, one per invariant — is re-derived on every run from
  `effects.components.*.ports` in the manifest and the `INVARIANT(S)` blocks
  of every `*.cfg` in the spec directory. A boundary with no seeded fault is an
  `incomplete_catalog` refusal (exit 2) and **no kill rate is computed at all**,
  because a number over a surface nobody covered asserts what the run has no
  evidence for. Declaring a new port breaks the kill test until a fault is
  seeded for it, so the experiment cannot drift behind the model.
- **The control run.** "Killed" means "the corpus run failed", so a corpus that
  is already red kills every mutant trivially and reports a perfect 1.0. The
  corpus is therefore run **unmutated first**, and a red control refuses
  (`control_failed`) without seeding anything. This is not a precaution: the
  first real run of the worked `distributed_history` kill test scored 7/7
  exactly this way, every "kill" being one unrelated pre-existing failure.
- **A survivor is a pointer, not a statistic.** Every mutant must declare
  `refine_variable` and `refine_action`; the loader rejects one that does not.
  A survivor reports "the representation is too abstract at variable X /
  action Y", which is actionable, rather than a decimal that dropped.
- **No waiver (evidence integrity, retained).** There is no `--allow-below-floor`,
  no `--accept-survivors`, no expected-to-survive annotation, and no manifest key
  that records a sub-floor rate as acceptable. Suppression-shaped keys are scanned
  for, reported in `ignored_suppression_keys`, and honored never. This
  anti-suppression discipline stays — you may not doctor the measurement. Note the
  reframe, though: the below-floor result is now **advisory** (it reports, it does
  not block), because the floor is not yet a validated bug-catching threshold
  (MF-038). "Do not falsify the measurement" survives; "the measurement fails your
  build" does not.
- **Per-component scoping narrows the obligation, never the measurement.**
  `--cfg` selects which model's invariants must be covered, because a
  repository with Internal and External models has two kill tests rather than
  one blended one. Omitting it is the strict default (every config required),
  and every mutant in the catalog runs either way — so an out-of-scope survivor
  still reports.

**Abstraction validation.** `--baseline` and `--compare` implement
`architecture_tractability.md`'s rule that an abstraction is legitimate iff the
kill rate holds after it. A rate that drops is refused; so is a swap that holds
the aggregate rate while losing a previously-killed mutant, because the rate is
an aggregate and a lost boundary is still a lost boundary. This is what
distinguishes a genuine re-representation from a deletion wearing its costume,
and it is what lets the standing complexity objective be pursued honestly.

**Onboarding and promotion are the required kill-test moments.** Per-ticket work
reuses the baseline mutants plus one new mutant at the changed boundary. There
is deliberately no enforcing copy inside `run spec-unit-tests`, unlike the
effect oracle: the effect oracle observes a corpus run that was happening
anyway, whereas the kill test runs the whole corpus once per mutant. Folding
that into every spec-unit invocation would make the inner loop unusable, and a
gate people disable to get work done protects nothing.

**Known constraint in this repository.** The runner spawns a child process per
mutant, and under the MF-027 effect oracle a `process.spawn` is `unobservable`
even when a declared port matches it. The kill test must therefore run OUTSIDE
the effect sandbox here. Neither oracle is relaxed to resolve this; see
`specs/tickets/MF-016/results/DEFERRED-TO-MF-023.md`.

## The Coverage Audit Gate — required at the end of every epic

The four oracles above cannot see what the model does not represent. The
coverage audit closes that hole, and it is **a required end-of-epic step**, not
an optional review.

**Ordering, and it is load-bearing in both directions:**

> **after every mechanism ticket has landed, and before final end-to-end
> integration.**

*After the mechanisms*, because the audit measures the model as the epic
actually leaves it — run earlier it reports gaps that later tickets were always
going to close. *Before final integration*, because it is a **promotion gate**;
an audit run after integration is a report, not a gate.

The procedure is a sub-agent prompt, `prompts/coverage_audit.md`, filling
`templates/coverage_audit_report.md`. It requires four sweeps — program surface,
effects enumerated **by category**, behaviors (error paths, retries, timeouts,
fallbacks, concurrency, config branches), and Internal/External reported
**separately** — each as a table whose row set is produced by a recorded
enumeration command, with every row dispositioned and carrying `file:line`
evidence.

**Gate semantics.** In-scope gaps are HARD: per the fourth governing rule, model
it or change the program, and there is no third option. Out-of-scope surface is
inventoried and does not gate. **The scope is declared once, in the plan, and
reviewed once — never waived per finding.** A gate whose findings can each be
closed by a recorded justification is the out-of-contract suppression purged
from MF-013, rebuilt one level up; one reviewable boundary decision is a
boundary, N per-finding justifications are an escape hatch. The prompt therefore
offers no "justified" or "accept as-is" disposition for an in-scope gap, and
requires the scope to be **read from the plan** rather than chosen by the
auditing agent. Remediation is advisory; the gap is not.

The verdict is recorded in the complexity ledger's `coverage_audit` block, so an
epic that skipped the audit is visible rather than silent. It defaults to
`not_run` and **refuses the workflow close** at anything but `pass` —
`incomplete` is not a pass. Full doctrine: `references/coverage_audit.md`.

## Corpus Discipline

Raw TLC edge lists are not a corpus. But the fix is **upstream, in the
diagram** — not downstream, by deleting cases.

**Amended 2026-07-18 (owner direction).** This section previously said to
distill the corpus: stratify, cap, and record what was dropped. That is
withdrawn. Filtering cases to fit a budget under-represents the program,
which the standing objective in `architecture_tractability.md` forbids
outright, and the `kill_rate_floor` does not make it safe — the kill test
only samples for damage at seeded faults, so a dropped case no mutant probes
is invisible to it. Dropping is also the wrong response to the signal:

- Cases are **never** dropped, filtered, sampled, or truncated to satisfy a
  budget. Not silently, and not with a recorded drop rule either. This is the
  evidence-integrity rule and it endures regardless of blocking.
- Case caps (`max_internal_cases_per_component`,
  `max_external_cases_per_action`) still fail the `analyze corpus` / export
  **command** over budget (nonzero exit, report written, nothing trimmed) — that
  command contract is unchanged in code. What changed is the doctrine around it:
  per "Advisory, Not Blocking", a faithfulness/corpus finding **does not gate
  promotion** (`close ticket` does not run it), so over-budget is a finding about
  the diagram surfaced for the owner, not a promotion blocker. It is part of the
  experimental corpus layer either way.
- Caps are per-program and negotiable, like every other budget: raise one
  with a recorded one-line rationale when the program genuinely needs it.
  That is an explicit, reviewable decision. Silent trimming is not.
- Labelers survive, repurposed from selection criteria to **diagnostic
  strata**. Their job is to show the distribution, not to choose survivors.

A lopsided corpus is **evidence about the representation**. If one action
emits two hundred near-identical cases while another emits two, the model is
enumerating redundant interleavings — interchangeable values, an
unconstrained ordering, or an action enabled across many equivalent states.
The corpus is the symptom; the diagram is the defect.

Corpus diagnostics therefore report, on a cap failure: the distribution per
`(action, label class)`, which strata dominate, which are starved, and what
varies across the redundant group. This is the corpus analogue of
`analyze complexity`'s descriptor facts, and it follows the same doctrine
(CD-04, resolving VAL-13): the gate states the measurement and then asks a
**redesign question** — can the architecture be redesigned to make the
program simpler, so the redundant cases are never generated? — pointing at
the complexity descriptor (`analyze complexity`) and
`references/complexity_intuition.md` as the judgment inputs. It prescribes
no move, and nothing is ever auto-applied; the judgment belongs to the
reader, per the CD-02 framing: take this complexity descriptor to consider
how to refactor complexity out of the app.

The command is `tla-spec-dev analyze corpus <cases-dir>`, and the same gate
runs automatically at the end of case generation and before Test Graph
export. It reads the caps through `scripts/budgets.py`, exits nonzero over
budget, and prints the exact `budgets:` edit — raised cap value, `source:
negotiated`, and a `rationale:` slot — that constitutes the accept path.
Three causes are measured from what actually varies across the redundant
group: values that are **permutations of one multiset** (unconstrained
ordering), **parameters sweeping a domain over a fixed transition shape**
(interchangeable values), and **one change shape replayed from many distinct
source states** (action enabled across equivalent states). The cause naming
is diagnosis, not a to-do list — what to change, if anything, is the
reader's redesign judgment.

Two properties are structural rather than merely intended. The export gate
measures the **complete** corpus before `--label`/`--case`/`--limit`
selection applies, so a narrow flag can never bring a corpus under cap. And
generation writes the whole package **before** the gate runs, so the
artifacts on disk hold every generated case whether the gate passes or fails.
The case caps never had an `--allow-over-budget` equivalent and never will:
raising a cap in the manifest with a recorded rationale is a different
verdict, not a bypassed one. That is the same conclusion the amendment above
reached for the complexity gate's own override, from the other direction —
see "No Degenerate Escapes" in `architecture_tractability.md`.

Counterexamples, Hypothesis failures, and production bugs are still promoted
to named regression traces, exactly as fuzz crashes get minimized into the
seed corpus. That part was always right and is unchanged.

The fuzzing analogy has a limit worth naming, since this section was
originally derived from it: fuzzing distills because its inputs are random
and its corpus is unbounded, so redundancy is inherent and unfixable. TLC is
bounded-exhaustive and its output is a function of the diagram you wrote.
Redundancy there is not inherent — it is a fact about your model, and it is
fixable at the source.

## What Belongs In External

External stays central: it generates the cases that run against the real
deployed program. Its content rule is strict:

- External contains exactly the public input surface and the externally
  observable projection of composed state. Nothing component-level.
- Component detail lives in the component representations; External stays
  thin because they carry the weight. Each public action should refine to a
  sequence of component actions (hidden progress).
- An External adapter must drive the program as deployed: separate
  process or real deployment, through a declared channel (http, cli, fs,
  queue, k8s), observing only externally visible state. An adapter that
  imports the production package in-process is a spec-unit adapter wearing
  an External badge — rebind it as Internal or fix it.

Ports give External its integration ladder. Every port has two conformant
implementations: the generated spec double and the real component, with
conformance tests proving they agree — that is the differential oracle. A
run configuration binds each port to `double` or `real`:

- All doubles: the spec-unit sanity rung. Direct `tla-spec-dev` runs, never
  a graph node.
- One real component at a time: controlled experiments. If all-doubles
  passes and swapping in the real queue fails, the defect is localized to
  the queue adapter or its conformance. One variable per experiment.
- All real, driven only through public channels: the top rung, the full
  Test Graph run.

Graph nodes are the rungs that exercise at least one real, externally driven
component. Record which rungs a repository runs, and why, in
`spec_manifest.yaml` alongside the budgets.
