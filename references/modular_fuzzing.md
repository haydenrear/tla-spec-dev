# Modular Representations And Spec-Guided Fuzzing

This reference defines what a good representation is, how to bound its
complexity, and how generated cases relate to fuzzing. Read it together with
`references/testgraph_adapters.md` and `references/edge-cases.md` before
authoring or reviewing any baseline. For moving an existing repository onto
this shape, read `references/migration.md`.

## The Reframe

This workflow is spec-guided differential fuzzing with a generated reference
implementation:

- The TLA+ model is the input grammar and the oracle.
- TLC bounded exploration is the exhaustive input generator. Hypothesis
  strategies are the randomized generator. Both feed the same oracle.
- The generated spec double is the reference implementation.
- Adapters are the fuzz harness.
- Invariants, projected-state assertions, and effect conformance are the
  sanitizers.
- The production program is the target.

The value system is empirical, exactly like fuzzing: a representation is
judged by the bugs it can catch and the coverage it achieves per unit budget,
never by whether TLC passes. TLC passing only proves the model is
self-consistent. It says nothing about fidelity to the program.

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

When the gate still fails — abstraction would lose bug-catching power, or
the R/W matrix is too dense for any narrow cut — read
`references/architecture_tractability.md`. It defines the three moves
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
  max_distinct_states: 50000             # per component model
  max_internal_cases_per_component: 200
  max_external_cases_per_action: 50
  kill_rate_floor: 0.8                   # see "Mutation kill test"
  max_component_variables: 6
  max_component_actions: 8
  max_symmetric_instances: 2
```

Budgets are hard gates, not aspirations. A component model over budget is
decomposed or re-abstracted, never waited on. The 120-second TLC rule in
`SKILL.md` is the `tlc_seconds` default, and everything it says about
diagnosing state explosion before changing the model applies here.

Until the CLI mechanizes this analysis (see `tickets/011`), compute the
dimension table and read/write matrix by hand or with a throwaway script,
and attach them to the ticket's `results/` evidence.

## Oracles

Every fuzzed case is checked against up to four oracles. The first two
exist today; the third and fourth are what make a representation's quality
falsifiable.

1. Output conformance: the real component's normalized output equals the
   spec double's output for the same `(state, input)`.
2. Projected-state conformance: the real system's observed state projects
   onto the case's expected `after` state.
3. Effect conformance: run the component in a sandbox (temp directories,
   fake transports, recorded HTTP) and diff observed side effects against
   declared effects.
   - An observed effect with no declared port is a representation gap:
     model it, or record an explicit out-of-contract justification.
   - A declared effect never observed across the whole corpus is dead model
     surface: remove it or explain it.
4. Mutation kill test: the representation's falsifiable experiment.
   - Hypothesis: representation R captures the bug-relevant behavior of
     component C at its port surface.
   - Experiment: seed k faults into production code — at minimum one per
     port and one per invariant — run the generated cases, and require the
     kill rate to meet `kill_rate_floor`.
   - A surviving mutant at a modeled boundary is proof the representation is
     too abstract there, and points at the exact variable or action to
     refine.

A baseline without a passing kill test is unvalidated, the same way a fuzz
harness that reaches 2% coverage is rejected regardless of whether it
builds. Note the difference from the negative projected-state check in
`examples/distributed_history/`: that check swaps in a wrong expected
projection, which validates the harness plumbing. The kill test seeds a
wrong production behavior, which validates the representation.

The kill test is also what makes budgets safe: constants cannot be shrunk to
nothing, because a trivial model stops killing mutants. Cost cap plus value
floor is a real optimization target; either alone invites gaming.

## Corpus Discipline

Raw TLC edge lists are not a corpus. Distill them:

- Stratify: guarantee at least one case per `(action, label class)` using
  labelers, then fill remaining budget by state-predicate novelty.
- Cap: respect `max_internal_cases_per_component` and
  `max_external_cases_per_action`.
- No silent truncation: record what was dropped and by which rule in the
  generated manifest.
- Counterexamples, Hypothesis failures, and production bugs get promoted to
  named regression traces, exactly as fuzz crashes get minimized into the
  seed corpus.

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
