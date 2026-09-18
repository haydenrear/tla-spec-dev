# tla-spec-dev

Development repository for the **`tla-spec-dev` plugin**: the TLA+ program-model
toolchain and the workflow skills that drive it, versioned, installed, synced and
improved as ONE unit.

It used to be one skill. SI-01 made the repository a plugin and moved the skill
surface to `skills/spec-double-2/`; SI-02 nested the five workflow skills beside
it. Downstream that is a single `skill-manager install`, a single version, and a
single `skt check` notification — see *Install Locally* below.

| contained skill | invoked as | upstream repository |
|---|---|---|
| `spec-double-2` | `tla-spec-dev:spec-double-2` | *(none — this repository is its history)* |
| `git-epic-workflow` | `tla-spec-dev:git-epic-workflow` | `haydenrear/git-epic-skill` |
| `git-issue-workflow` | `tla-spec-dev:git-issue-workflow` | `haydenrear/git-issue-workflow-skill` |
| `git-issue` | `tla-spec-dev:git-issue` | `haydenrear/git-issue-skill` |
| `discovery` | `tla-spec-dev:discovery` | `haydenrear/discovery-skill` |
| `test-graph` | `tla-spec-dev:test-graph` | `haydenrear/test_graph_skill` |
| `git-integration-repo` | `tla-spec-dev:git-integration-repo` | `haydenrear/git-integration-skill` |
| `plugin-repository` | `tla-spec-dev:plugin-repository` | `haydenrear/plugin-repository-skill` |

SI-12 added the last two. They were left outside the bundle at kickoff, and that
turned out to be the one thing keeping `GOAL-one-unit` clause 1 unsatisfiable:
both of them **import** skills this bundle contains, so every home carrying them
re-materialised standalone copies of three contained skills. `debugging` stays
outside — nothing in the bundle depends on it, so it creates no such cycle.

The seven with an upstream repository are **constituents** (`integration.toml`),
nested with `git subtree` at full history. They are ordinary tracked files — no
submodules, no gitlinks — and upstream work still reaches this repository with
`git subtree pull --prefix=skills/<name> <remote> main` until the owner declares
the freeze. The recipe and the remotes table are in
`specs/results/epic-self-improvement-substrate/migration/pulling-upstream.md`.

User-facing workflow guidance for the toolchain lives in:

- `skills/spec-double-2/SKILL.md`
- `skills/spec-double-2/references/typical_workflow.md`
- `skills/spec-double-2/references/generation_modes.md`
- `skills/spec-double-2/references/runtime_requirements.md`
- `skills/spec-double-2/references/codegen_contract.md`
- `skills/spec-double-2/references/conformance_testing.md`
- `skills/spec-double-2/references/testgraph_adapters.md`
- `skills/spec-double-2/references/edge-cases.md`
- `skills/spec-double-2/references/tla_profile.md`
- `skills/spec-double-2/references/spec_evolution.md`
- `skills/spec-double-2/references/workflows.md`

## Install Locally

```bash
skill-manager install file://$(pwd) --dry-run
skill-manager install file://$(pwd)
```

This installs the **plugin**, and every contained skill comes with it at one
version. `skill-manager list` gets one row (`KIND=plugin`), not six.

The contained `spec-double-2` skill declares CLI dependencies for `jinja2`,
`pytest`, and a `skill-script` installed `tlc2` wrapper. The `tlc2` wrapper
requires Java.

### Migrating a home that still carries the old standalone units

Run this **per home** — the operator's `~/.skill-manager`, then each project or
worktree `.skill-manager`. Until it is run, a home carries the same skill twice,
at two versions, with two sync paths and no rule about which one an agent read.
That duplication is the thing the bundle exists to remove, and installing the
plugin does **not** remove it on its own.

```bash
# 0. Name the home EXPLICITLY, by using its own entrypoint.
#    Exporting SKILL_MANAGER_HOME is NOT enough and is not silently ignored:
#    each shim binds the home it lives in, so the operator's ~/.skill-manager
#    shim REFUSES rather than edit a home it does not own --
#      "refusing to run against a home you did not name ...
#       this entrypoint binds the home it lives in, so it cannot honour
#       SKILL_MANAGER_HOME."
#    Use that home's own shim (or pass --home to any other one).
HOME_DIR=/path/to/.skill-manager                 # or $HOME/.skill-manager
SM="$HOME_DIR/bin/cli/skill-manager"             # equivalently: skill-manager --home "$HOME_DIR"

# 1. Install the bundle.
#    Once merged, straight from the coord:
"$SM" install github:haydenrear/tla-spec-dev --yes
#
#    From a CHECKOUT while the change is unmerged, stage it first with
#    `git archive`. Do NOT use `file://$(pwd)` on a checkout that carries its
#    own `.skill-manager/`: the installer stages the whole directory, including
#    that gitignored home, and recurses into
#    `.skill-manager/cache/stage-*/staged/.skill-manager/cache/stage-*/...`
#    until the path blows up. Measured; it fails with
#    "BuildResolveGraphFromSource: 1 coord(s) failed to resolve".
STAGE=$(mktemp -d) && git archive HEAD | tar -x -C "$STAGE"
"$SM" install "file://$STAGE" --yes

# 2. Remove the now-duplicated standalone units. `uninstall`, not `remove`:
#    `remove` is lower-level and leaves agent symlinks and MCP registrations
#    behind, which is how a "removed" skill keeps resolving.
#    git-integration-repo and plugin-repository were added to this list by
#    SI-12. Until they go, they re-install three of the others as standalone
#    copies every time they resolve -- they are the reason the list is eight
#    long rather than six.
for u in spec-double-compiler git-epic-workflow git-issue-workflow \
         git-issue discovery test-graph \
         git-integration-repo plugin-repository; do
  "$SM" uninstall "$u" --yes 2>/dev/null || true   # absent is fine
done

# 3. Confirm: ONE unit, eight contained skills, and no standalone leftovers.
"$SM" show tla-spec-dev                  # lists the contained skills
"$SM" list | grep -E 'tla-spec-dev|spec-double|git-issue|git-epic|discovery|test-graph|git-integration|plugin-repository'
ls "$HOME_DIR/plugins/tla-spec-dev/skills/"
"$SM" show test-graph                    # expected: "unit not found" -- it is contained now
```

Order matters in one direction only: install before uninstall, so the home is
never briefly without the skills. Uninstalling first and then hitting a failed
install leaves the home carrying neither — which is exactly what happened the
first time this sequence was run, and why step 1 is written the way it is.

Two things change for anything that addressed those skills by their **old**
identity, and both are silent rather than loud:

- a contained skill's bytes are at
  `<home>/plugins/tla-spec-dev/skills/<unit>/`, **not** `<home>/skills/<unit>/`,
  so a hardcoded store path stops existing;
- a `skill-imports: unit: <contained-skill>` no longer validates — address the
  plugin instead (`unit: tla-spec-dev`, `path: skills/<unit>/<file>`);
- a `skill_references = ["github:haydenrear/<bundled-repo>"]` does **not**
  error. It installs a second standalone copy. Point it at this repository's
  coord instead.

`plugin-repository/references/imports.md` has the measured evidence for all
three. `plugin-repository/scripts/verify.sh`, run from this repository's root,
checks the first two inside the bundle.

**`skills/<name>/` never gets its own `.git` here.** The constituents were
nested with `git subtree`, so they are already plain tracked files; there is no
`finalize.sh` step to run and running one would restore state this model does
not use.

## Develop

Run focused checks while editing:

```bash
python3 -m py_compile scripts/*.py tests/*.py spec_double_compiler/*.py
uv run --with pytest --with pyyaml -m pytest tests   # pyyaml is REQUIRED: without it 12 tests red spuriously
uv run examples/distributed_history/tests/test_ecommerce_backend.py
uv run examples/distributed_history/specs/program_model/tests/test_ecommerce_adapters.py
```

The distributed ecommerce example tests include PEP 723 uv script headers, so
`uv run <test-file>` retrieves pytest even when the ambient interpreter does
not have it installed.

For production repositories that use the desired/current migration loop,
scaffold the workflow directories first:

```bash
python3 skills/spec-double-2/scripts/tla_spec_dev.py --spec-root specs scaffold project --name ProjectName
python3 skills/spec-double-2/scripts/tla_spec_dev.py --spec-root specs scaffold workflow TICKET-123 "Ticket title"
python3 skills/spec-double-2/scripts/tla_spec_dev.py --spec-root specs open ticket TICKET-123
python3 skills/spec-double-2/scripts/tla_spec_dev.py --spec-root specs run spec-unit-tests --ticket TICKET-123
```

The installed wrapper exposes the same workflow as `tla-spec-dev`; the
repository path uses `python3 skills/spec-double-2/scripts/tla_spec_dev.py` so local development does
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
python3 skills/spec-double-2/scripts/run_generated_case_adapters.py \
  examples/distributed_history/test_graph/build/generated/manual/spec-unit/ecommerce_internal_cases \
  --mapping examples/distributed_history/specs/program_model/case_adapters.toml \
  --view internal \
  --batch \
  --import-root examples/distributed_history
```

View-aware case generation writes explicit internal and external outputs:

```bash
python3 skills/spec-double-2/scripts/generate_cases_from_tlc_dump.py path/to/Internal.tla path/to/Internal.cfg --out generated --package internal_cases --view internal --actions-metadata model/actions.yml
python3 skills/spec-double-2/scripts/generate_cases_from_tlc_dump.py path/to/External.tla path/to/External.cfg --out generated --package external_cases --view external --actions-metadata model/actions.yml
python3 skills/spec-double-2/scripts/export_testgraph_cases.py generated/testgraph/external_cases --out generated/testgraph/traces --bindings model/testgraph_bindings.yml
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
python3 skills/spec-double-2/scripts/run_generated_case_adapters.py \
  examples/distributed_history/test_graph/build/generated/manual/testgraph/ecommerce_external_cases \
  --mapping examples/distributed_history/specs/program_model/testgraph_bindings.yml \
  --view external \
  --batch \
  --validate-only \
  --import-root examples/distributed_history
```

For larger case sets, use batch mode:

```bash
python3 skills/spec-double-2/scripts/run_generated_case_adapters.py path/to/generated_cases --mapping path/to/case_adapters.toml --batch --validate-capabilities
```

## Evaluation Scorecards

Every eval in this repository is scored on one standardized card, by an agent
judge, **against artifacts**. The card is the unit of comparison across epics,
and it is versioned so that changing it is a deliberate, recorded act rather
than silent drift.

**`references/eval_scorecard.md` is the one home for that card** — the five
dimensions, their anchors, the scoring rules, the judging protocol, and the
rules for reading a history. **Nothing else in this repository states any of
them, this file included**, and `tests/test_card_has_one_home.py` executes that
rather than asking anyone to remember it. Its argument for judging rather than
computing is in the card's own `## Why a judged scorecard and not a metric`,
on the record of every mechanical gate this project shipped; the scanners that
argument retired were removed on 2026-08-04 and what they established is now
`references/architecture_advice.md`.

**This section used to summarise the card, and the summary is deleted rather
than corrected.** A summary of a versioned rubric is a copy that nothing
compares to the rubric. Four copies were made to disagree with the card at
`6aac1ec` and **three of the four were missed by the entire test suite,
`demonstrate.py`, `check`, `audit` and `serve` together** — the one that was
caught was the one something already compared
(`specs/results/scorecards/subtract-to-measure/SM-06/`). Read the card.

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

**The rules for reading a history are the card's** (`## Reading history`,
`R-H1`..`R-H5`), and `score_tools.py audit` executes every one of them. They are
not repeated here: a reading rule stated in two places is a reading rule that
can disagree with itself, and the audit only knows about one of the two.

```bash
python3 examples/validation/scorecards/score_tools.py history --example <example>
python3 examples/validation/scorecards/score_tools.py audit
```

## Spec Evolution History

Use append-only close records to keep active context small without losing
history.
After each ticket is marked closed in
`specs/desired_program_model/ticket_plan.yaml`:

```bash
python3 skills/spec-double-2/scripts/tla_spec_dev.py --spec-root specs open ticket TICKET-123
python3 skills/spec-double-2/scripts/tla_spec_dev.py --spec-root specs close ticket TICKET-123 \
  --summary "Kept generated cases spec-local" \
  --result specs/results/tlc.txt
```

`open ticket` creates `specs/tickets/TICKET-123/desired` for parallel
ticket work (add `--with-current` for a ticket-local `current/` too). `close ticket` moves that ticket directory into
history, promotes the ticket `desired/` (there is no ticket `current/` unless opened `--with-current`), replaces project
`specs/current` with ticket `desired/`, and merges ticket-local Test Graph
artifacts back into project specs.

The parent repository also has a Test Graph that exercises this workflow in a
disposable git repository under the graph build directory:

```bash
# NOT `~/.skill-manager`: the test-graph unit lives in the home THIS checkout is
# bound to (a project or worktree `.skill-manager`), and only that copy matches
# the units this checkout was resolved against. See references/runtime_requirements.md.
$(for d in "$SKILL_MANAGER_HOME"/skills/test-graph "$SKILL_MANAGER_HOME"/plugins/*/skills/test-graph; do [ -d "$d" ] && { printf %s "$d"; break; }; done)/scripts/discover.py specWorkflow
$(for d in "$SKILL_MANAGER_HOME"/skills/test-graph "$SKILL_MANAGER_HOME"/plugins/*/skills/test-graph; do [ -d "$d" ] && { printf %s "$d"; break; }; done)/scripts/run.py specWorkflow
```

At the end of a desired/current workflow:

```bash
python3 skills/spec-double-2/scripts/close_tickets.py --repo-root . --summary "Promoted desired/current into program_model"
```

These commands write under `specs/.history/<workflow-name>/`, refuse to
overwrite an existing close entry, and print a recommended git commit command
for the history directory.

The lower-level `start_ticket.py`, `close-ticket.py`, and `close_tickets.py`
scripts remain implementation details for the CLI and for workflow closeout.
New onboarding documentation should lead with `tla-spec-dev`.

## Repository Shape

The root is the PLUGIN. Skill surface lives under `skills/<name>/`; everything
the plugin is *about* — the model, the tests, the examples, the graphs — stays at
the root, because it belongs to the repository rather than to any one skill.

- `.claude-plugin/plugin.json`, `skill-manager-plugin.toml`: the plugin markers.
  Their `name` and `version` must agree; `plugin-repository/scripts/release.sh`
  is the only thing that should change a version, because it writes both.
- `integration.toml`: the constituent list — the five nested skill repos, their
  remotes and branches. Read by `verify.sh`, `refresh.sh` and `propagate.sh`.
- `skills/spec-double-2/`: the toolchain skill — `SKILL.md`, and the
  `scripts/`, `spec_double_compiler/`, `templates/`, `references/`, `prompts/`
  and `skill-scripts/` that used to sit at this repository's root.
  `references/` includes `eval_scorecard.md` (the judged evaluation rubric),
  `hexagonal_prompting.md` (architecture as a prompt, not a check), and
  `architecture_advice.md` (what the removed static architecture scanners
  established, as rules to follow and as the specification a replacement must
  meet). `prompts/` are the sub-agent prompts shipped as artifacts — the
  coverage audit, the implementation brief, aspect decomposition, and the
  hexagonal ask.
- `skills/{git-epic-workflow,git-issue-workflow,git-issue,discovery,test-graph}/`:
  the nested workflow skills, each still its own upstream repository.
- `examples/`: checked-in examples and generated artifacts.
- `examples/validation/`: eval fixtures, A/B arms, seeded fault catalogues, and
  `scorecards/score_tools.py` (the scorecard schema checker and indexer).
- `specs/results/scorecards/`: judged scorecards per epic, plus
  `SELF-IMPROVEMENT.md`, the cross-epic ledger.
- `test_graph/`: parent repository Test Graph, including `specWorkflow` for the ticket workflow CLI.
- `tests/`: unit tests for parsers, generators, runners, and workflow scripts.
- `tickets/`: small roadmap/history notes for this skill implementation.
