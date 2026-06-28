# TlaSpecDevCli Program Model

This is the accepted baseline model for the shipped `tla-spec-dev` CLI after
the CLI workflow tickets have closed.

The model records the command workflow agents and users follow:

- `tla-spec-dev --spec-root <root> scaffold project`
- `tla-spec-dev --spec-root <root> scaffold workflow`
- `tla-spec-dev --spec-root <root> open ticket <ticket-name>`
- desired-first ticket editing
- current reconciliation after implementation lands
- `tla-spec-dev --spec-root <root> run spec-unit-tests`
- `tla-spec-dev --spec-root <root> close ticket <ticket-name>`

It also includes production adapters and spec tests for the shipped CLI surface,
including the parent `specWorkflow` Test Graph validation.

Closed workflow history lives under
`../.history/tla-spec-dev-cli-workflow/`. New desired/current directories should
be scaffolded only when starting the next ticket workflow.
