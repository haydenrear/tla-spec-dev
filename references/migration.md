# Migrating To Modular Representations

This guide moves a repository onto the modular pure-function/side-effect
representation defined in `references/modular_fuzzing.md`. It applies to two
starting points:

- A repository already onboarded with a monolithic `Internal.tla` /
  `External.tla` baseline.
- A repository whose sources were never structured for this, where effects
  are tangled through the code.

Migration is ordinary ticket work: use `specs/desired_program_model` for the
plan and one ticket per component. The desired model is where the component
inventory, budgets, and refactor decisions live — not chat.

The end state to aim for: every component passes output, projected-state,
and effect conformance across its distilled corpus, and its kill test meets
the floor. At that point the component is deterministic-in-contract — given
`(state, input)`, its externally relevant behavior is fixed — and the
External run over the real deployment becomes predictable from the model.
That determinism is the acceptance criterion of the whole migration, not
file structure.

## Phase 0: Budgets

Before touching any spec, set the budgets with the user. Propose the
defaults from `references/modular_fuzzing.md`, ask which to adjust for this
program, and record the agreed values plus a one-line rationale in
`spec_manifest.yaml` under `budgets:`. Every later phase treats them as hard
gates.

## Phase 1: Inventory

Identify component candidates from both directions and reconcile them:

- From the code: modules, services, workers, queues, and stores that already
  have process or ownership boundaries.
- From the existing model, if one exists: build the variables x actions
  read/write matrix of the monolithic spec. Variable clusters that interact
  through few actions are components; the crossing actions are ports.

Write the inventory into `specs/desired_program_model` as the ticket plan:
one ticket per component, ordered smallest-first, with dependencies where
one component's declared effects are another's inputs. Prefer starting with
the component whose side effects look most tangled — it teaches the most
about whether the budgets and profile fit this program.

## Phase 2: Component Representation (per ticket)

For each component ticket:

1. Write the component model: local state, one action per input, pure
   transition, declared effects as port-variable appends. Contract
   environments stand in for neighbors.
2. Run the complexity analysis from `references/modular_fuzzing.md`. Over
   budget means cut again or re-abstract; record the dimension table and
   the decision in ticket `results/`.
3. Model-check the component and the shared interface model within
   `tlc_seconds`.
4. Generate and distill the component corpus within the case caps.

## Phase 3: Effect Conformance And Invited Refactors

Build the component's sandbox harness: run the real component code with
temp directories, fake transports, and recorded boundaries, then diff
observed side effects against declared effects.

Undeclared observed effects are the migration's main signal — and so are
complexity-gate failures (see `references/architecture_tractability.md`).
For each one, choose exactly one:

- Model it: add the port and effect to the representation.
- Justify it: record an explicit out-of-contract note in the manifest.
- Refactor the source: this is the invited outcome, not a failure — but it
  is a **recommendation the user must approve** before any production
  change begins. Present the evidence (effect diff, dimension table, R/W
  matrix, failed-abstraction kill results), the target shape, and the
  cost. If the user vetoes — some pieces score poorly and still need to
  exist in that form — escalate to a creative representation from
  `references/architecture_tractability.md` instead of looping on domain
  shrinking. When approved: extract the pure transition into a functional
  core and push the effect emission to the port boundary (functional core,
  imperative shell). The spec drives the refactor; the effect diff verifies
  convergence. Refactors are normal production changes — they go through
  the same ticket's current/desired loop and tests.

Iterate until the effect diff is clean or every residue is justified.

## Phase 4: Kill Test (per component)

Seed at minimum one fault per port and one per invariant into the component's
production code, run the distilled corpus, and require the kill rate to meet
`kill_rate_floor`. A surviving mutant at a modeled boundary means the
representation is too abstract there: refine the variable or action it
points at and rerun. Store the mutants, the kill matrix, and the outcome in
ticket `results/` — later tickets reuse the baseline mutants and add one new
mutant at whatever boundary they change.

## Phase 5: Composition And External

Once components exist:

1. Wire the composition: one component's declared effects feed another's
   input ports; check the thin interface model.
2. Rebuild `External.tla` as public inputs plus observable projection only.
   Push any component-level detail found there down into the component
   representations. External must get thinner during this migration, not
   thicker.
3. Verify channel authenticity for every Test Graph adapter: separate
   process or deployment, declared channel, no in-process imports of the
   production package.
4. Stand up the integration ladder as graph runs: one-real-component
   experiments where localization is worth the cost, and the all-real
   public-surface run as the top rung. Record the chosen rungs in
   `spec_manifest.yaml`.

## Phase 6: Close-Out And Skill Feedback

Close tickets through the normal workflow until current equals desired,
promote, and clean up.

Then run the retro. **You do not have to remember to.** Every close-out —
`tla-spec-dev close ticket` and the workflow close — emits
`specs/results/skill_feedback.md` and appends a `## Close-out …` entry to it,
covering what the migration could not express or automate:

- `surviving-mutants` — mutants that survived and why the profile or
  generators could not reach them;
- `unmodelable-effects` — observed effects that had no reasonable modeling as
  port state;
- `budget-and-metric` — budget values that had to move, and gates or metrics
  that measured the wrong quantity or were blind to a real change;
- `profile-schema-cli` — places the constrained TLA+ profile, the manifest
  schema, or the CLI forced a workaround, produced a wrong result, or
  destroyed data.

Each finding is a `### SF-NNN` block of `- key: value` lines. The required
fields exist so a finding is *evidence about a real target*, not a wish:
`target:` (the exact surface — command, script and function, budget key,
manifest field), `observed_on:` (the repository/module/ticket it was run
against), `evidence:` (a durable path, not prose), `severity:`,
`root_cause:` (`tool` / `spec` / `target` — a correct implementation of a
wrong specification is `spec`, and filing it against the code files it in the
wrong place), and `workaround_applied:`. Category-specific fields structure the
common cases; the emitted template lists them, with worked examples.

Turn each item into a concrete recommendation against the
spec-double-compiler skill itself — a ticket or PR on the skill repository —
and record its URL in `recommendation:` with `status: filed`. If you looked
and found nothing, set `feedback_status: none-found`; silence is not an
answer.

Close-out reads the document back and records **whether feedback was filed and
where** in the append-only history entry (`feedback_filed`,
`feedback_filed_where`, and the full `skill_feedback` record in
`manifest.json`), and prints the unfiled findings by id. The document is
append-only: close-out writes the template once and thereafter only appends,
so a filled finding is never overwritten by the next close.

This feedback loop is part of the workflow, not optional polish: the skill
improves only through what real migrations fail to express.
