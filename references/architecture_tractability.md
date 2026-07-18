# Architecture Tractability And The Three Moves

This reference governs what happens when a program resists tractable
representation. It extends the decomposition method in
`references/modular_fuzzing.md` with the architectural doctrine: when the
model cannot be made tractable, sometimes the model is wrong, sometimes the
program is wrong, and sometimes the program is fine and the representation
needs a more creative shape. The agent's job is to diagnose which — and then
to **recommend, never decide**. Every architectural move below is a
recommendation that the user approves, adjusts, or vetoes.

## The Standing Objective: Programming As Complexity Minimization

The whole point of this workflow is to minimize the complexity of the
program. TLA+ gives us something programming has always lacked: a
**measurable metric of program complexity** — the state-space bound, the
distinct-state count, the action count, the R/W-matrix density. That turns
programming into an optimization problem:

```text
minimize   complexity(program), as measured through its TLA+ model
subject to all behaviors retained:
           - kill rate >= kill_rate_floor
           - effect conformance clean (no undeclared effects)
           - external surface fully covered by generated cases
           - the program represented in its ENTIRETY
```

Rules that follow:

- **The objective is standing, not triggered.** Do not wait for a gate
  failure. On every ticket, every review, every model change, actively look
  for a design that retains the behaviors at lower measured complexity.
  Gate failure is merely the forced case of an optimization that should be
  running continuously.
- **Minimize through design, verify through TLA+.** The complexity that
  must go down is the program's, demonstrated by its model. Lowering the
  number the cheap way — omitting behavior from the model, narrowing
  domains past usefulness, quietly dropping a boundary — is **gaming the
  metric**, and the constraint set exists to catch it: a complexity drop
  accompanied by a kill-rate drop, a new unjustified coverage gap, or lost
  external coverage is rejected, not celebrated.
- **The metric is only meaningful under the constraints.** The complexity
  of a partial representation is not the complexity of the program. Full
  representation first; minimization second; both always.
- **Report deltas jointly.** A complexity delta is only evidence when
  presented alongside the behavior-retention evidence from the same run.
  Never report one without the other.

### The Recursive Refinement Loop

Complexity minimization is part of the working loop, not a one-time design
activity. Every pass through the ticket lifecycle includes a refinement
check, and the loop recurses — each refinement changes the measurements,
which may expose the next refinement:

1. Measure: run the complexity analysis; record the metrics as the ticket's
   complexity ledger entry.
2. Compare: diff against the previous ledger entry. Complexity up requires
   a recorded justification naming the new essential behavior. Complexity
   flat or down: continue.
3. Refine: ask explicitly — can the architecture be refined to lower the
   measured complexity while retaining the behaviors? Use the three moves
   and their diagnostics. Emit any candidate as a recommendation with
   evidence for user approval.
4. Verify: after an approved refinement, rerun the constraint set (kill
   rate, effect conformance, external coverage) and the measurement. A
   refinement that lowers complexity but degrades retention is reverted.
5. Recurse: a landed refinement re-opens step 1 — decompositions expose
   projectable state, projections expose narrower cuts. Stop when a full
   pass yields no approvable candidate, and record that as the ticket's
   refinement evidence (searched, found none) rather than silence.

## The Principle

Tractability is an architectural fitness function. The model checker is an
architecture critic: when TLC cannot explore the program within budget, that
is a review finding about the program, not a tooling inconvenience.

Grounding, in brief:

- Dijkstra argued that correctness proof is only feasible when the code is
  designed from the start to be easily proved — provability as a design
  force that shapes program structure.
- The defect-prediction literature (Nagappan et al., Microsoft systems)
  shows complexity and coupling metrics statistically predict post-release
  failures. A failed complexity gate is an early defect-risk signal.
  **Record gate failures as findings**, never silently work around them.
- AWS's TLA+ experience describes a ladder of abstraction — several middle
  levels, each verified against the one above — and reports that much of
  the value came from specification forcing design simplification.

The user's version of the principle: if the architecture is too complex to
be represented tractably, it should be refactored or represented through
another layer of abstraction. Once tractable, it is simpler to represent and
bugs are easier to catch. If the architecture is too complex, it probably
has many bugs and needs simplification to remove them.

## The Two Symmetric Failure Modes

Empirical evaluation of LLM-written TLA+ (SIGOPS 2026, "Can LLMs model
real-world systems in TLA+?") found models near-perfect on syntax but ~46%
on conformance: agents write textbook templates, not the actual system. Two
systematic failures, and they are symmetric:

- **Over-detail (transcription):** modeling the code's mechanisms. Explodes
  state and admits spurious states the real system never reaches.
- **Over-abstraction:** merging multi-step operations into one atomic
  action, making states the system routinely passes through unreachable.

Guidance therefore cannot be taste — it must be a procedure with empirical
checks on both sides. The oracles in `references/modular_fuzzing.md` are
those checks: effect conformance and the mutation kill test catch
over-abstraction; the complexity gate catches over-detail. This reference is
the doctrine for what to do when the gates squeeze from both sides.

## The Three Moves

When the complexity gate fails, there are exactly three moves. Diagnostics
from the dimension table and the variables x actions read/write matrix
choose among them. The output of the diagnosis is a **recommendation with
evidence**; the user approves the move before it is taken.

### Move 1 — Abstract (change the representation, not the code)

Project variables no invariant reads, quotient equivalent states,
symmetry-reduce identical actors, coarsen domains, hide internal progress
between commit points.

Validity is empirical, not judgment: **an abstraction is legitimate iff the
kill rate holds after it.** Abstract a dimension, rerun the kill test. Kill
rate holds → the dimension was accidental detail. Kill rate drops → it was
essential; put it back. This turns essential-vs-accidental complexity into
a measurement.

### Move 2 — Decompose (cut into components with ports)

Valid iff the R/W matrix actually has modular structure: variable clusters
with narrow crossings. Graph modularity of the matrix is a number; high
modularity means a cut exists, and the analysis can name it. Follow the
port-cut method in `references/modular_fuzzing.md`.

### Move 3 — Refactor the program (user approval REQUIRED)

Triggered when neither other move works: abstraction loses kills, and no
narrow cut exists because the matrix is dense. **That failed search is
itself the finding.** Dense rows name the god-state; dense columns name the
actions that touch everything. Emit an architecture finding with those
pointers — "these three variables are written by seven actions across what
should be four components" — and present it to the user with:

- the evidence (dimension table, matrix, failed-abstraction kill results);
- the concrete refactor recommendation and its target shape (below);
- the expected tractability and coverage gain;
- the cost and risk of the production change.

Never begin a production refactor from a gate failure without explicit user
approval. The user may know why the piece exists in the shape it does.

Refactor target shapes (for when the user approves):

- functional core / imperative shell — extract the pure transition, push
  effects to port boundaries;
- single-writer state — each variable owned by exactly one component;
- explicit commit points — one externally visible commitment per action;
- explicit protocol state instead of implicit coordination — status fields
  and queues model tractably; shared mutable rows and polling do not.

## No Degenerate Escapes

Added 2026-07-18 by owner direction, after an audit found the same defect in
several places at once: **every hard rule had grown a documented bypass.**
Filter the corpus to fit a cap. Suppress an effect gap with an
out-of-contract justification. Pass `--allow-over-budget`. Fall back to
default budgets with a warning. Each looked reasonable alone. Together they
made every limit optional, which is the same as having no limits — and worse
than none, because the tooling still reports success.

The governing rules. They outrank any older text in this repository that
conflicts with them, including elsewhere in these references:

1. **Complexity is pushed out, not accommodated.** Recursively modularize
   the architecture, and the TLA+ spec with it, to minimize measured
   complexity while retaining every behavior. When a measurement is bad,
   the architecture changes. The measurement does not get adjusted, and the
   thing being measured does not get trimmed.
2. **The tools inform the architecture.** TLA+, the analysis commands, the
   adapters, and the oracles exist to tell you where complexity actually
   is. Their output is input to a design decision — never a number to be
   satisfied by other means.
3. **Never game a metric or a tool by removing evidence.** Do not drop,
   filter, sample, or truncate cases; do not suppress a gap report; do not
   silence a finding. Not silently, and not with a recorded rule either — a
   recorded deletion is still a deletion. When the evidence is
   inconvenient, the architecture is what changes.
4. **The diagram is a faithful representation of the program.** If the
   program cannot be represented in the diagram, **the program changes.**
   There is no third option. An observed effect with no declared port, a
   behavior that will not model, a shape that resists the views — each is a
   statement about the program, not a gap to be annotated and waived.
5. **The diagram has strict complexity limits.** Case caps, the
   state-space bound, and the component-size heuristics are hard gates.
   Over the limit fails. Raising a limit is a per-program decision recorded
   with its rationale and reviewed as such — an explicit, visible act, never
   an override flag, a fallback default, or a conditional check that
   silently disables itself when its input is absent.

**A rule with an escape hatch is not a rule.** When you find yourself
writing "or record a justification", "unless overridden", "falls back to",
or "when present" into a gate, you are building degeneracy. Write the
failure instead.

**Hard gates and advisory diagnosis are different things**, and the next
section is not a loophole in this one. Suggested moves, modularity scores,
and refactor targets are advisory: they propose architecture and require
user approval. Case caps, the state-space bound, component-size heuristics,
the kill-rate floor, and effect conformance are gates: they fail. "Some
pieces score badly and still need to exist in that form" licenses a
representation, never a breach of a limit. A piece that genuinely must
exceed a cap gets that cap raised explicitly, in the manifest, with a
rationale — it does not get waved through.

## Recommendations, Never Verdicts

The diagnosis output is advisory everywhere it appears — CLI output, ticket
evidence, migration notes. This governs **suggested moves and scores**, not
the hard gates enumerated in the previous section. Rules:

- Every suggested move is labeled a recommendation and carries its
  evidence. The user approves, adjusts, or vetoes.
- A poor score is not a verdict on the code. **Some pieces of a program
  score badly and still need to exist in that form** — performance-critical
  paths, protocol-mandated shapes, third-party constraints, domain
  complexity that is genuinely irreducible.
- When the user vetoes a move ("this piece must stay as it is"), do not
  loop on shrinking domains. Escalate to a creative representation from the
  next section and record the veto plus the chosen representation in the
  manifest.

## Irreducible Pieces: Creative Representations

When a piece is both intractable and untouchable, the representation must
get creative. These shapes may not look like a "correct" state-machine
model at first — that is expected. Choose with the user:

- **Contract-only (opaque) modeling:** model the piece as a
  nondeterministic environment constrained by its observed guarantees.
  Neighbors are verified against the contract; the contract itself is
  validated by trace conformance — record real traces at the piece's
  boundary and check membership — instead of state exploration.
- **Many small lenses instead of one big mirror:** several per-concern
  projections of the same piece (a data-integrity view, an ordering view, a
  lifecycle view), each independently tractable, each with its own
  refinement obligation. No single diagram must carry the whole piece.
- **Data abstraction:** replace rich payloads with symbolic tokens keeping
  only the distinctions invariants need (two colors of message, not the
  message schema).
- **Temporal decomposition:** model phases or epochs separately with
  explicit handoff invariants between them.
- **Statistical arm:** when bounded-exhaustive is impossible, lean on the
  randomized Hypothesis arm with the same oracles, and record coverage as
  sampled, not exhaustive — no silent claims of exhaustiveness.
- **Accepted-intractable:** record the piece in `known_gaps` with the veto
  rationale and compensating validation — extra mutants at its boundary,
  extra external cases through its public surface.

## Grow The Model By Evidence, Not By Transcription

Agents default to transcribing code downward and then shrinking until TLC
finishes. Invert it, in the shape of counterexample-guided abstraction
refinement (CEGAR) with a richer oracle:

1. Start with the **coarsest** model that expresses the public behavior and
   its invariants — a handful of fact-variables.
2. Add a variable, guard, or effect **only when evidence demands it**:
   - a spurious counterexample: the model allows what the system forbids;
   - a **surviving mutant**: the model cannot see a real bug;
   - an undeclared observed effect: the model is blind to real behavior.
3. Record the justification with each addition.

Every element of the model earns its place by killing a mutant, carrying an
effect, or supporting an invariant. A per-variable justification table in
the manifest makes this auditable; the complexity analysis flags
unjustified variables as dead weight. The state budget is then spent
exclusively on bug-relevant distinctions — the representation that catches
the most bugs per state.

## Intuitiveness Tests

Three self-checks an agent applies to any representation:

- **Facts, not mechanisms.** A variable is a fact a domain expert would
  recognize (`orders_awaiting_fulfillment`), never a data structure the
  code happens to use.
- **The narratability test.** Read a TLC trace aloud. If it narrates as a
  story about the domain, the level is right. If it narrates as
  data-structure shuffling, you are transcribing.
- **Atomicity fidelity.** Action boundaries are the system's commit points
  — the moments effects become visible outside the component — not code
  function boundaries. One action per externally visible commitment;
  everything between commit points is hidden progress. (This is the exact
  boundary LLM-written specs get wrong most often.)

## Deferred Direction: Domain-Driven Representations

A planned research direction (tickets/018) strengthens Move 1 and Move 2 by
relocating the abstraction into the code: domain value objects and enums
make illegal states unrepresentable, so the spec's small domains become the
actual domains rather than optimistic approximations, and aggregate
boundaries with fixed command/event protocols make interaction cardinality
the number of message types. Keep it in mind when designing diagnostics,
effect declarations, and kill tests — do not foreclose it.

## Where This Is Mechanized

- `tla-spec-dev analyze complexity` (tickets/011): emits the dimension
  table, R/W matrix, modularity score, unjustified-variable flags, and a
  suggested move **labeled as a recommendation requiring user approval**.
- Mutation kill test (tickets/016): doubles as the abstraction validator —
  kill-rate-preserving abstraction is legitimate abstraction.
- `references/migration.md` Phase 3: refactors are invited from effect-diff
  evidence and from gate-failure evidence alike, and always pass through
  user approval.

## Sources

- Dijkstra, structured programming and design-for-provability:
  https://arxiv.org/pdf/1810.11673
- How AWS Uses Formal Methods:
  https://cacm.acm.org/research/how-amazon-web-services-uses-formal-methods/
- Nagappan et al., Mining Metrics to Predict Component Failures:
  https://www.st.cs.uni-saarland.de/publications/files/nagappan-icse-2006.pdf
- CEGAR: https://en.wikipedia.org/wiki/Counterexample-guided_abstraction_refinement
- Can LLMs model real-world systems in TLA+? (SIGOPS 2026):
  https://www.sigops.org/2026/can-llms-model-real-world-systems-in-tla/
- Out of the Tar Pit (essential vs accidental complexity):
  https://blog.acolyer.org/2015/03/20/out-of-the-tar-pit/
