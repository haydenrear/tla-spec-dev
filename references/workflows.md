# Workflows

This reference describes the operational paths for projects that use an
evolving TLA+ program spec plus generated Python spec doubles.

## Scaffold A Project

Use this when a repository is adopting the desired/current loop after it already
has or is about to create an accepted `program_model`.

```bash
tla-spec-dev --spec-root specs scaffold project --name ProjectName
tla-spec-dev --spec-root specs scaffold workflow TICKET-123 "Ticket title"
```

This creates:

- `specs/program_model`
- `specs/desired_program_model`
- `specs/current`

For first onboarding of a repository with no accepted baseline, prefer
`tla-spec-dev --spec-root specs scaffold project --name ProjectName` and stop
there so only `specs/program_model` is created. Use the same `--spec-root` for
every later workflow command when the repository does not use `specs`.

The scaffold emits placeholders to restructure, not a finished baseline. It is
complete only when it carries both views (`Internal.tla` + `External.tla`), both
adapter mappings (`case_adapters.toml` + `testgraph_bindings.yml`), and the
adapters/projector/assertion in `adapters.py`. Read
`references/testgraph_adapters.md` and diff against
`examples/distributed_history/specs/program_model/` before calling it done.

## Scaffold A Spec

`scripts/scaffold_spec.py` is for **standalone tutorial/example specs only**.

```bash
python3 scripts/scaffold_spec.py workspace --root examples
```

Do not use it for production `specs/current` or `specs/desired_program_model`
work. It always emits both views (Core + Internal + External; `--views` is
additive only) because a single-module spec with no External view cannot
generate Test Graph cases — the project's public surface would never
be validated. Production baselines come from
`tla-spec-dev scaffold project`, and `specs/current` /
`specs/desired_program_model` are created from that accepted baseline by
`tla-spec-dev scaffold workflow`. Keep tickets in
`specs/desired_program_model/ticket_plan.yaml`.

## Work A Ticket

1. Update `specs/desired_program_model` with the intended whole-program state.
2. Update `specs/desired_program_model/ticket_plan.yaml` with the ticket id,
   status, dependencies, validation commands, and evidence slots.
3. Start the ticket workspace:

```bash
tla-spec-dev --spec-root specs open ticket <ticket-id>
```

4. Update `specs/tickets/<ticket-id>/desired` first. The ticket desired model is
   the whole-program state after this ticket, including TLA+, configs,
   spec-unit adapters/tests, and Test Graph bindings/adapters when applicable.
5. Update production code plus `specs/tickets/<ticket-id>/current`.
6. Run TLC and generated/adapted case tests for the selected slice:

```bash
tla-spec-dev --spec-root specs run spec-unit-tests --ticket <ticket-id>
```

7. Store evidence under the ticket `results/` directory or another referenced
   evidence path.
7a. **Attribute what the ticket hit, while you are still in it.** For each
   regression: what caught it (`channel`), what area it was in, and the
   assertion that pins it — or why none was added. For each case you wrote that
   passes: what it could **never** have caught, or `UNDECIDED` if you did not
   work it out. **Written now, not reconstructed at close** — memory
   reconstructs favourably. Nothing gates on this.
   See `references/bug_attribution.md` §4 and §6.
7b. **Place each regression on the influence graph.** The arc is
   *found → area → pinned*. Say which arcs this ticket completed and which
   stopped part-way, and add or amend the area's row in
   `examples/validation/agent_rounds/SELF-IMPROVEMENT-MATRIX.md`. **One or two
   lines is the right size** — the matrix accumulates across tickets and the
   reading happens at the epic, not here. An area with no regression this ticket
   gets no row.
8. Fill in the ticket's complexity-ledger input,
   `specs/tickets/<ticket-id>/results/complexity_ledger.yaml` (scaffolded by
   `open ticket` with TODO sentinels that fail the gate). The close refuses
   until it carries a refinement record, a narrative, a justification for any
   complexity increase, and validated-refactor evidence for any decrease.
   There is no override flag.
9. Mark the ticket closed in `ticket_plan.yaml`.
10. Close the ticket:

```bash
tla-spec-dev --spec-root specs close ticket <ticket-id> \
  --summary "What changed and why" \
  --result specs/results/tlc.txt \
  --result specs/results/adapter.txt
```

The close operation validates ticket-local `current == desired`, records a
complexity-ledger entry in `specs/results/complexity_ledger.json` (refusing
the close if the ledger gate rejects), moves `specs/tickets/<ticket-id>` to
`specs/.history/<workflow-name>/ticket-NNN-<ticket-id>/ticket/`, promotes
ticket `desired/` onto project `specs/current` — removing only paths that
were seeded into the ticket workspace and dropped there, and preserving
current-only files the ticket was never seeded with — and merges ticket-local
Test Graph artifacts into project specs.

The lower-level scripts remain implementation details behind the CLI. The
tla-spec-dev repository validates this CLI flow with its parent Test
Graph:

```bash
# NOT `~/.skill-manager`: the test-graph unit lives in the home THIS checkout is
# bound to (a project or worktree `.skill-manager`), and only that copy matches
# the units this checkout was resolved against. See references/runtime_requirements.md.
"$SKILL_MANAGER_HOME"/skills/test-graph/scripts/discover.py specWorkflow
"$SKILL_MANAGER_HOME"/skills/test-graph/scripts/run.py specWorkflow
```

## Complete A Spec Workflow

Use this when the desired/current loop has been mapped back into the durable
program model.

1. Confirm every ticket in `specs/desired_program_model/ticket_plan.yaml` has a
   closed status.
2. Confirm project `specs/current` and `specs/desired_program_model`
   semantically match.
3. Promote the converged model into `specs/program_model`.
4. Fill in the workflow-close ledger input,
   `specs/results/complexity_ledger_input.yaml`. It must include a
   `coverage_audit` block. Since 2026-08-04 it REFUSES NOTHING — the verdict is
   recorded and printed at every close, `not_run` included — but `pass` is still
   the only value that means "the surface was walked and no in-scope gap was
   found". Run `prompts/coverage_audit.md` if you want that read, and record the
   report path. See `references/coverage_audit.md`, "Status".
4a. **Write the attribution section of the close-out or evaluation.** Four
   questions, answered from the record by reading it — there is no tool and one
   is not wanted:
   - **CATCH** — per architectural area, how many regressions were caught by
     something `automated` and how many escaped to a `hand` or to `reading`.
   - **REACH** — which invariants are enforced on some surfaces and not others,
     and which claim full coverage without saying how they enumerated.
   - **BLIND** — which passing cases could never have caught the areas that keep
     escaping. A green sitting on an escaping area is the strongest single
     signal here.
   - **PRICE** — which proposals were priced before, and what they actually
     cost.
   Then say **what the record could not show**: how much of it carries an
   attribution at all, and which areas have escapes but **no denominator** —
   an area with one escape in two invocations and one with one escape in a
   hundred look identical until you say so. A clean report off a thin record
   certifies an absence nobody observed.

4b. **THE ARCHITECTURAL READ — this is a required task of the evaluation, not a
   footnote.** Run `prompts/regression_architecture.md` over the attribution
   records and the current self-improvement matrix. It asks which areas keep
   appearing in the `escaped to hand` column **across rounds**, and what about
   the SHAPE of the worst one makes bugs there hard to catch automatically. It
   must price its suggestion forward and must not choose it.
   **Judge the transcripts with `prompts/regression_judge.md`, two judges, blind
   to each other and to the matrix** — a self-graded attribution is the verdict
   an agent has an incentive to give.
   **No checker, gate, lint or static analyzer may be proposed as the answer.**
   That route is measured and closed here; if one is ever built it goes in a
   separate library. Nothing gates on any of this.
   See `references/bug_attribution.md` and
   `examples/validation/agent_rounds/SELF-IMPROVEMENT-MATRIX.md`.

5. Record a closed-workflow snapshot and remove temporary workflow directories:

```bash
python scripts/close_tickets.py \
  --repo-root . \
  --summary "Final mapping from desired/current into program_model"
```

The close record is written to
`specs/.history/<workflow-name>/closed-snapshot/`.

## Search Before Reading

For historical questions, search manifests and summaries first:

```bash
rg -n "<ticket-id>|<action>|<invariant>|<resource>" specs/.history
```

Open snapshots only after the manifest or summary proves relevance. This keeps
AI-assisted maintenance focused on the current state plus a small number of
append-only historical entries.
