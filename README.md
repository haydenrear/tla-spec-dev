# Spec Double Compiler

Development repository for the `spec-double-compiler` skill.

User-facing workflow guidance lives in:

- `SKILL.md`
- `references/typical_workflow.md`
- `references/generation_modes.md`
- `references/runtime_requirements.md`
- `references/codegen_contract.md`
- `references/conformance_testing.md`
- `references/testgraph_adapters.md`
- `references/edge-cases.md`
- `references/tla_profile.md`
- `references/spec_evolution.md`
- `references/workflows.md`

## Install Locally

```bash
skill-manager install file://$(pwd) --dry-run
skill-manager install file://$(pwd)
```

The skill declares CLI dependencies for `jinja2`, `pytest`, and a
`skill-script` installed `tlc2` wrapper. The `tlc2` wrapper requires Java.

## Develop

Run focused checks while editing:

```bash
python3 -m py_compile scripts/*.py tests/*.py spec_double_compiler/*.py
uv run --with pytest -m pytest tests
uv run examples/distributed_history/tests/test_ecommerce_backend.py
uv run examples/distributed_history/specs/program_model/tests/test_ecommerce_adapters.py
```

The distributed ecommerce example tests include PEP 723 uv script headers, so
`uv run <test-file>` retrieves pytest even when the ambient interpreter does
not have it installed.

For production repositories that use the desired/current migration loop,
scaffold the workflow directories first:

```bash
python3 scripts/tla_spec_dev.py --spec-root specs scaffold project --name ProjectName
python3 scripts/tla_spec_dev.py --spec-root specs scaffold workflow TICKET-123 "Ticket title"
python3 scripts/tla_spec_dev.py --spec-root specs open ticket TICKET-123
python3 scripts/tla_spec_dev.py --spec-root specs run spec-unit-tests --ticket TICKET-123
```

The installed wrapper exposes the same workflow as `tla-spec-dev`; the
repository path uses `python3 scripts/tla_spec_dev.py` so local development does
not depend on a prior skill install. Use the same `--spec-root` for every
project, workflow, ticket, run, and close command.

## Regenerate Examples

The active checked-in example is `examples/distributed_history`. Regenerate
its TLC-derived internal and external case packages into an ignored build
directory:

```bash
uv run examples/distributed_history/scripts/regenerate_tlc_cases.py \
  --out test_graph/build/generated/manual
```

Run the generated internal/spec-unit cases:

```bash
python3 scripts/run_generated_case_adapters.py \
  examples/distributed_history/test_graph/build/generated/manual/spec-unit/ecommerce_internal_cases \
  --mapping examples/distributed_history/specs/program_model/case_adapters.toml \
  --view internal \
  --batch \
  --import-root examples/distributed_history
```

View-aware case generation writes explicit internal and external outputs:

```bash
python3 scripts/generate_cases_from_tlc_dump.py path/to/Internal.tla path/to/Internal.cfg --out generated --package internal_cases --view internal --actions-metadata model/actions.yml
python3 scripts/generate_cases_from_tlc_dump.py path/to/External.tla path/to/External.cfg --out generated --package external_cases --view external --actions-metadata model/actions.yml
python3 scripts/export_testgraph_cases.py generated/testgraph/external_cases --out generated/testgraph/traces --bindings model/testgraph_bindings.yml
```

`--bindings` is required: export is gated on every external binding declaring
a `channel`, on no adapter, projector, expected-projection, or assertion
module importing the declared `external.production_package` (checked by
static import analysis, transitively across first-party helpers), and on
`external.port_bindings` naming each port `double` or `real` with at
least one `real`. The same gate runs in the adapter runner. See "External
channel enforcement" in `references/testgraph_adapters.md`.

External adapter bindings may include `kind` to batch cases that need the same
external harness setup and cleanup. Batch adapters can define optional
`setup_all(ctx)`, `teardown_all(ctx)`, `setup(ctx)`, and `teardown(ctx)` hooks.
Use these hooks for integration-state preparation such as clearing database
rows, committing Kafka offsets, preparing a CLI workspace, or removing
per-trace test fixtures.

For external assertions, configure `projector = "module:Object"` to retrieve
the actual deployed state. By default, the runner compares that actual state to
the generated TLA case's `after` state. Use `expected_projection` when only a
projection of the TLA state is externally observable, and use `assertion` only
for custom comparison logic.

Relative case outputs such as `--out cases` are resolved under the spec
directory. A command run from the repository root and the same command run from
the spec directory should produce the same spec-local artifact layout.

Adapter mapping validation:

```bash
python3 scripts/run_generated_case_adapters.py \
  examples/distributed_history/test_graph/build/generated/manual/testgraph/ecommerce_external_cases \
  --mapping examples/distributed_history/specs/program_model/testgraph_bindings.yml \
  --view external \
  --batch \
  --validate-only \
  --import-root examples/distributed_history
```

For larger case sets, use batch mode:

```bash
python3 scripts/run_generated_case_adapters.py path/to/generated_cases --mapping path/to/case_adapters.toml --batch --validate-capabilities
```

## Evaluation Scorecards

Every eval in this repository is scored on one standardized card, by an agent
judge, **against artifacts**. The card is the unit of comparison across epics —
its rubric and anchors are `references/eval_scorecard.md`, and it is versioned so
that changing it is a deliberate, recorded act rather than silent drift.

**Why judged and not computed.** Every mechanical gate this project shipped was
defeated cheaply and none of them ever caught a bug: the complexity gate failed
every normal program and was retired to advisory; the architecture check reported
a clean on a divergent codebase for six lines of YAML, then for a 41-line
re-export file, both with every declaration digest unchanged. The argument for
judgement is not that it cannot be gamed. It is that **a number computed from an
artifact can be optimized by editing the artifact, while a judgement that must
cite the artifact can only be satisfied by changing what the artifact is.**

Five dimensions, 0–4 each:

| | | |
|---|---|---|
| **D1** | bug detection | do the model-derived cases and their adapters *catch* seeded faults |
| **D2** | complexity | is the design as simple as its behavior requires |
| **D3** | modularity | ports and adapters *in fact* — domain independent of I/O, adapters swappable |
| **D4** | behavior preservation | does the simpler design still do everything the baseline did |
| **D5** | honesty | does it refuse rather than falsely certify |

The rules that make a score hard to game are structural, not exhortation:

- **Score artifacts, never claims.** A report sentence asserting a property is
  not evidence; the code is.
- **Any score ≥ 2 without a `file:line` citation is mechanically capped at 1.**
- **A score of 4 must name something the artifact refuses to claim**, so the top
  of every scale is unreachable by asserting more.
- **Prose quality is never an input.**
- **Two judges score blind**; a spread greater than 1 is `contested` and needs a
  third pass citing *new* evidence.
- **The mechanical block sits beside the judgement and is never scored** — when
  measurement and judgement disagree, that disagreement is itself a finding.

Check and index a set of cards:

```bash
python3 examples/validation/scorecards/score_tools.py check specs/results/scorecards/<epic>
python3 examples/validation/scorecards/score_tools.py index specs/results/scorecards/<epic>
```

Results live in `specs/results/scorecards/<epic>/<example>/<run>/` — deliberately,
because the workflow close copies `specs/results/` into
`specs/.history/<workflow>/closed-snapshot/results/`. **Every epic's scorecards
are sealed with the epic that produced them**, which is what makes comparison
across epics possible at all.

`specs/results/scorecards/SELF-IMPROVEMENT.md` is the cross-epic index. **The
metric is the delta, not the total.** It also records, written down *before*
results arrive rather than after, what would count as evidence we are fooling
ourselves — every prediction passing, findings arriving only from the suite, a
score moving without an artifact moving.

Two rules a reader will otherwise get wrong:

- **Never average across examples.** A deliberately incoherent fixture is
  *supposed* to score low on D3; averaging it with a coherent one produces a
  number about nothing. Compare the same example across epics, or two arms of one
  eval.
- **A judged score is not a kill count.** The mechanical block carries kill
  tables, and they are reported **per class per arm, never as a single rate** — a
  number reported without naming its arm is uninterpretable.

## Spec Evolution History

Use append-only close records to keep active context small without losing
history.
After each ticket is marked closed in
`specs/desired_program_model/ticket_plan.yaml`:

```bash
python3 scripts/tla_spec_dev.py --spec-root specs open ticket TICKET-123
python3 scripts/tla_spec_dev.py --spec-root specs close ticket TICKET-123 \
  --summary "Kept generated cases spec-local" \
  --result specs/results/tlc.txt
```

`open ticket` creates `specs/tickets/TICKET-123/current` and `desired` for
parallel ticket work. `close ticket` moves that ticket directory into
history, validates ticket `current/ == desired/`, replaces project
`specs/current` with ticket `desired/`, and merges ticket-local Test Graph
artifacts back into project specs.

The parent repository also has a Test Graph that exercises this workflow in a
disposable git repository under the graph build directory:

```bash
/Users/hayde/.skill-manager/skills/test-graph/scripts/discover.py specWorkflow
/Users/hayde/.skill-manager/skills/test-graph/scripts/run.py specWorkflow
```

At the end of a desired/current workflow:

```bash
python3 scripts/close_tickets.py --repo-root . --summary "Promoted desired/current into program_model"
```

These commands write under `specs/.history/<workflow-name>/`, refuse to
overwrite an existing close entry, and print a recommended git commit command
for the history directory.

The lower-level `start_ticket.py`, `close-ticket.py`, and `close_tickets.py`
scripts remain implementation details for the CLI and for workflow closeout.
New onboarding documentation should lead with `tla-spec-dev`.

## Repository Shape

- `scripts/`: scaffold, generation, TLC-case, adapter-runner, history, and workflow-closeout CLIs.
- `spec_double_compiler/`: importable runtime used by generated case runners.
- `templates/`: Jinja templates for generated Python/TLA artifacts.
- `examples/`: checked-in examples and generated artifacts.
- `references/`: user-facing skill references, including
  `eval_scorecard.md` (the judged evaluation rubric) and
  `hexagonal_prompting.md` (architecture as a prompt, not a check).
- `prompts/`: sub-agent prompts shipped as artifacts — the coverage audit, the
  implementation brief, aspect decomposition, and the hexagonal ask.
- `examples/validation/`: eval fixtures, A/B arms, seeded fault catalogues, and
  `scorecards/score_tools.py` (the scorecard schema checker and indexer).
- `specs/results/scorecards/`: judged scorecards per epic, plus
  `SELF-IMPROVEMENT.md`, the cross-epic ledger.
- `test_graph/`: parent repository Test Graph, including `specWorkflow` for the ticket workflow CLI.
- `tests/`: unit tests for parsers, generators, runners, and workflow scripts.
- `tickets/`: small roadmap/history notes for this skill implementation.
