# TlaSpecDevCli Program Model

This is the accepted baseline model for the shipped `tla-spec-dev` CLI we are
adding to this skill repository.

The model records the command workflow we want agents and users to follow:

- `tla-spec-dev --spec-root <root> scaffold project`
- `tla-spec-dev --spec-root <root> scaffold workflow`
- `tla-spec-dev --spec-root <root> open ticket <ticket-name>`
- desired-first ticket editing
- current reconciliation after implementation lands
- `tla-spec-dev --spec-root <root> run spec-unit-tests`
- `tla-spec-dev --spec-root <root> close ticket <ticket-name>`

It also models the skill-local build/install precondition for shipping a single
Python CLI entrypoint from the skill itself.

Files:

- `TlaSpecDevCli.tla`: canonical command workflow state machine.
- `MC.cfg`: bounded TLC config for the baseline.
- `spec_manifest.yaml`: command, port, result, invariant, and progressive
  disclosure metadata.
- `case_adapters.toml`: placeholder mapping for generated case adapters.
- `production_adapters.py`: placeholder adapter extension points.
