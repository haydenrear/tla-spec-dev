# Current Program Model

EP-03 deliberately keeps the host CLI model unchanged. Its semantic work is
three independent example program models under `examples/effect_providers/`;
the host changes only gain measurement evidence, documentation, and a Test
Graph validation for those external examples. The preregistered experiment is
`examples/effect_providers/PREREGISTRATION.yaml`.

This directory is the executable whole-program model of what the repository
implements right now for the active ticket workflow.

Active ticket: `MF-012` - Modular fuzzing representation epic

Baseline:

- Program model manifest: `../program_model/spec_manifest.yaml`
- Program model TLA module: `../program_model/TlaSpecDevCli.tla`

Workflow:

1. Keep this model equivalent to the entire `specs/program_model` before
   implementation. Do not copy only the feature or ticket-local subset.
2. After each ticket slice lands in production code, update this directory with
   the implemented whole-program state, actions, invariants, adapter mappings,
   and tests while preserving existing modeled behavior.
3. Run TLC and current-model adapter/unit tests before adding broader
   integration or graph coverage.
4. Record validation evidence in `spec_manifest.yaml` and keep
   `../desired_program_model/ticket_plan.yaml` synchronized.

Do not model tests, test graph nodes, CI jobs, integration harnesses, or
validation workflow mechanics as TLA+ state/actions. Those belong in manifest
status, ticket evidence, or adapter validation commands.
