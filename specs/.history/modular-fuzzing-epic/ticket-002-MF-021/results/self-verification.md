# MF-021 — self-verification: the fix survives its own promotion

This ticket is the first that can prove its own fix, by surviving the exact
operation it repairs. MF-021's own `close ticket` promotion is a live instance
of the defect.

## The setup is genuinely adversarial

`specs/tickets/MF-021/desired/` was seeded by `open ticket` **before** the fix
existed, so it does not contain `tests/test_current_ticket_workflow.py`:

```
$ comm -23 <(cd specs/current && find . -type f | sort) \
           <(cd specs/tickets/MF-021/desired && find . -type f | sort)
./tests/test_current_ticket_workflow.py
```

Under the pre-fix `replace_tree`, promoting this ticket would have deleted that
file for the **third** consecutive time — the same file MF-012 and MF-020 both
lost, carrying MF-012's budgets retention test.

Note also that MF-021's workspace was opened before `seed_manifest` was written,
so it exercises the **safe default** path (`seed_recorded: false`): with no
record of what the ticket was offered, no deletion intent is provable, so
promotion preserves everything and reports that basis. The fix protects even the
tickets that predate it.

## Pre-close inventory of `specs/current`

```
case_adapters.toml
MC.cfg
production_adapters.py
README.md
spec_manifest.yaml
tests/test_current_ticket_workflow.py      <-- the repeat casualty
tests/test_tla_spec_dev_budgets_adapter.py
tests/test_tla_spec_dev_cli_adapter.py
tests/test_tla_spec_dev_run_adapter.py
tests/test_tla_spec_dev_scaffold_adapter.py
tests/test_tla_spec_dev_test_graph_adapter.py
tests/test_tla_spec_dev_ticket_adapter.py
TlaSpecDevCli.tla
```

## Post-close result

See `self-verification-postclose.txt` for the raw diff and the close command's
own promotion report, captured immediately after
`tla-spec-dev --spec-root specs close ticket MF-021`.
