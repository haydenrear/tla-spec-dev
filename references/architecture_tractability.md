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
minimize   complexity(program), as measured through its TLA+ model  # SHIPPED: the scanner measures this
subject to all behaviors retained:
           - kill rate >= kill_rate_floor            # EXPERIMENTAL: not validated (MF-038: 0/9 content bugs, 0.31)
           - effect conformance clean                # EXPERIMENTAL: existence/exit-code oracle, not content
           - external surface fully covered by generated cases
           - the program represented in its ENTIRETY
```

The complexity metric (the objective) is the shipped, working scanner. The
behavior-retention constraints are the **experimental** faithfulness layer: the
kill rate and effect conformance are not yet validated to catch bugs (MF-038
measured 0 of 9 content bugs killed, kill rate 0.31), so treat them as advisory
diagnostics, not as satisfied/violated gates. The objective is real and usable
today; the constraints are a research aspiration under test (MF-037). See SKILL.md,
"What Is Shipped And What Is Experimental".

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

Guidance therefore cannot be taste — it must be a procedure with checks on both
sides. The **shipped** side is the complexity scanner: it catches over-detail
(state explosion, dense R/W matrix) and is validated for that. The other side —
effect conformance and the mutation kill test in `references/modular_fuzzing.md`,
meant to catch over-abstraction — is **experimental and not validated for
bug-catching** (MF-038: 0 of 9 content bugs killed, kill rate 0.31). So today only
the over-detail check is trustworthy; guard against over-abstraction with human
review until the faithfulness oracles are proven (MF-037). This reference is the
doctrine for what to do when complexity squeezes.

## The Three Moves

When the complexity gate fails, there are exactly three moves. Diagnostics
from the dimension table and the variables x actions read/write matrix
choose among them. The output of the diagnosis is a **recommendation with
evidence**; the user approves the move before it is taken.

### Move 1 — Abstract (change the representation, not the code)

Project variables no invariant reads, quotient equivalent states,
symmetry-reduce identical actors, coarsen domains, hide internal progress
between commit points.

The intended validity test was empirical: **an abstraction is legitimate iff the
kill rate holds after it** — abstract a dimension, rerun the kill test, kill rate
holds means accidental detail, kill rate drops means essential. **This test relies
on the experimental kill test, which MF-038 showed does not catch content bugs
(0/9, kill rate 0.31), so it cannot be trusted for this yet.** Until the kill test
is validated (MF-037), judge abstractions by human review of what behavior the
removed dimension carried, not by the kill rate alone.

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

## Advisory, Not Blocking (governing reframe, 2026-07-20)

**This reverses the hard-gate framing below, and outranks it.** Added by owner
direction after a probe measured what the complexity gate does to ordinary
programs: a 5-variable, 10-command model — an unremarkable CLI over shared
state — hard-failed promotion, because `component C1 is touched by 10 actions`
exceeds the cap of 8. Any program with more than eight commands over shared
state fails. That is most real programs. As a hard gate, the complexity metric
fails in nearly every user's project instead of helping them.

The correction: **complexity is a scanner, not a gate.** It produces metrics,
warnings, and recommendations, and tells the agent where to refactor. **It
never blocks promotion.** The useful content — the dimension table, the
state-space bound, the R/W matrix, the modularity score, dense-row / god-state
detection, the suggested moves — was always the point; the exit-nonzero that
sat on top of it was an over-promise.

Rules, superseding the hard-gate rule (rule 5 below):

- **Nothing blocks promotion.** Not the state-space bound, not the
  component-size heuristics, not the kill rate, not effect conformance. Every
  check emits warnings and recommendations. A gate is *earned*, per check, only
  once real-app validation shows it is trustworthy enough to block on — and
  until then it advises.
- **A warning names what and where, and recommends.** "Component C1 is touched
  by 10 actions; consider splitting X and Y to their own component" — not
  "FAIL, exit 1". The agent decides, with the user, whether to act.
- **Complexity minimization is still the objective** — the agent should
  refactor complexity out when the scan says so. The difference is that the
  scan *advises* the refactor rather than *forcing* it by refusing to ship.
- **Faithfulness checks (effect conformance, kill test) advise too, for now.**
  They test whether the model represents the program, which is a stronger claim
  than "too complex" — but the owner has not yet seen them help on a real app,
  so they report rather than block until MF-037 and real-app testing prove
  them.

**What does NOT change: evidence integrity.** A scanner fed doctored input is
worthless, so the anti-degeneracy rules below still hold as *rules about not
corrupting the measurement* — do not drop cases, suppress an effect gap, or
silence a finding, because that lies to the scan. The distinction is now sharp:
you may not falsify the measurement (evidence integrity, hard), but the
measurement may not block you (advisory, not a gate). "Never game the metric by
removing evidence" survives; "the metric fails your build" does not.

## No Degenerate Escapes

*Historical framing, retained for the reasoning. The hard-gate conclusion is
superseded by "Advisory, Not Blocking" above; the evidence-integrity reasoning
still holds.*

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
5. **The diagram has complexity thresholds.** *(Superseded by "Advisory, Not
   Blocking": as originally written this rule made case caps, the state-space
   bound, and the component-size heuristics hard gates that fail over the limit.
   They are now advisory — they warn and recommend, and do not block.)* Raising a
   threshold is still a per-program decision recorded with its rationale and
   reviewed as such — an explicit, visible act, never an override flag, a fallback
   default, or a conditional check that silently disables itself when its input is
   absent. The evidence-integrity half of this rule is what endures: you tune the
   threshold in the open, you do not doctor the input to it.

**A rule with an escape hatch is not a rule.** When you find yourself
writing "or record a justification", "unless overridden", "falls back to",
or "when present" into a gate, you are building degeneracy. Write the
failure instead.

**A boundary is not an escape hatch, and the difference is countable.** The
coverage audit gate (MF-026, `references/coverage_audit.md`) turns on exactly
this distinction. Its findings are classified against a scope the *plan*
declares — one decision, made once by the owner, reviewed once, visible in one
place. That is a boundary. Had the gate instead let each finding be closed by a
recorded justification, it would have been the out-of-contract suppression
purged from MF-013, rebuilt one level up: **one reviewable boundary decision is
a boundary; N per-finding justifications are an escape hatch.** The test to
apply when adding any new gate is whether the number of judgment calls scales
with the number of findings. If it does, you have built degeneracy regardless of
how principled each individual call looks.

The corollary is that an auditing agent must never choose its own scope. An
agent that picks the boundary can define every finding out of existence, and no
amount of per-finding rigor recovers from that.

**Evidence integrity and advisory diagnosis are different things**, and the next
section is not a loophole in this one. This paragraph originally drew the line
between "advisory diagnosis" and "hard gates" and put case caps, the state-space
bound, component-size heuristics, the kill-rate floor, and effect conformance on
the *gate* side. **"Advisory, Not Blocking" above reverses that**: none of those
block anymore — they warn and recommend. What survives is the *evidence-integrity*
rule, which is orthogonal to blocking: you may not falsify the measurement (drop
cases, suppress a gap, silence a finding) even though the measurement no longer
fails your build. "Some pieces score badly and still need to exist in that form"
licenses a representation. A piece that genuinely wants a looser threshold gets it
raised explicitly, in the manifest, with a rationale — recorded as a reviewable
decision, not to unblock a build (nothing was blocked) but to keep the advisory
warning meaningful.

## Recommendations, Never Verdicts

The diagnosis output is advisory everywhere it appears — CLI output, ticket
evidence, migration notes. Under "Advisory, Not Blocking" the thresholds are now
advisory too, so this is no longer a contrast between advice and gates; it is the
rule set for how the advice (suggested moves and scores) is presented. Rules:

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
