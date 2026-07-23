# Validation report — cliWorkflow-20260719-194517-b9c84eff

**Overall**: PASSED  
**Nodes**: 2 (passed=2, failed=0, errored=0)

| Node | Status | Duration | Input context | Captured stdout |
|---|---|---|---|---|
| `spec.cli.help` | **PASS** | 1858ms | [context/spec.cli.help.input.json](context/spec.cli.help.input.json) | [node-logs/spec.cli.help.stdout.log](node-logs/spec.cli.help.stdout.log) |
| `spec.cli.install` | **PASS** | 616ms | [context/spec.cli.install.input.json](context/spec.cli.install.input.json) | [node-logs/spec.cli.install.stdout.log](node-logs/spec.cli.install.stdout.log) |

## `spec.cli.help` — **PASS**

executor start: `2026-07-19T19:45:18.075674Z`  
executor end: `2026-07-19T19:45:19.933482Z`  
spawn exit code: 0

**Input context**: [context/spec.cli.help.input.json](context/spec.cli.help.input.json)

### Assertions

| Name | Status |
|---|---|
| version succeeded | **PASS** |
| version mentions tla-spec-dev 0.1.0 | **PASS** |
| root-help succeeded | **PASS** |
| root-help mentions --spec-root | **PASS** |
| root-help mentions scaffold | **PASS** |
| root-help mentions open | **PASS** |
| root-help mentions run | **PASS** |
| root-help mentions close | **PASS** |
| scaffold-help succeeded | **PASS** |
| scaffold-help mentions project | **PASS** |
| scaffold-help mentions workflow | **PASS** |
| project-help succeeded | **PASS** |
| project-help mentions program_model | **PASS** |
| project-help mentions baseline | **PASS** |
| workflow-help succeeded | **PASS** |
| workflow-help mentions current | **PASS** |
| workflow-help mentions desired_program_model | **PASS** |
| open-ticket-help succeeded | **PASS** |
| open-ticket-help mentions ticket_name | **PASS** |
| open-ticket-help mentions desired-first | **PASS** |
| run-spec-units-help succeeded | **PASS** |
| run-spec-units-help mentions generated/adapted | **PASS** |
| run-spec-units-help mentions spec root | **PASS** |
| close-ticket-help succeeded | **PASS** |
| close-ticket-help mentions append-only history | **PASS** |
| close-ticket-help mentions ticket_name | **PASS** |
| incomplete-scaffold exited 2 | **PASS** |
| incomplete-scaffold mentions incomplete command: tla-spec-dev scaffold | **PASS** |
| incomplete-scaffold mentions next: | **PASS** |
| incomplete-open exited 2 | **PASS** |
| incomplete-open mentions incomplete command: tla-spec-dev open | **PASS** |
| incomplete-open mentions next: | **PASS** |
| incomplete-run exited 2 | **PASS** |
| incomplete-run mentions incomplete command: tla-spec-dev run | **PASS** |
| incomplete-run mentions next: | **PASS** |
| incomplete-close exited 2 | **PASS** |
| incomplete-close mentions incomplete command: tla-spec-dev close | **PASS** |
| incomplete-close mentions next: | **PASS** |
| cli path came from install node | **PASS** |

### Metrics

- `durationMs`: 1746

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| version | 0 | 140ms | 23596 | [`node-logs/spec.cli.help.version.log`](node-logs/spec.cli.help.version.log) |  |
| root-help | 0 | 141ms | 23597 | [`node-logs/spec.cli.help.root-help.log`](node-logs/spec.cli.help.root-help.log) |  |
| scaffold-help | 0 | 138ms | 23598 | [`node-logs/spec.cli.help.scaffold-help.log`](node-logs/spec.cli.help.scaffold-help.log) |  |
| project-help | 0 | 131ms | 23599 | [`node-logs/spec.cli.help.project-help.log`](node-logs/spec.cli.help.project-help.log) |  |
| workflow-help | 0 | 159ms | 23600 | [`node-logs/spec.cli.help.workflow-help.log`](node-logs/spec.cli.help.workflow-help.log) |  |
| open-ticket-help | 0 | 172ms | 23601 | [`node-logs/spec.cli.help.open-ticket-help.log`](node-logs/spec.cli.help.open-ticket-help.log) |  |
| run-spec-units-help | 0 | 146ms | 23602 | [`node-logs/spec.cli.help.run-spec-units-help.log`](node-logs/spec.cli.help.run-spec-units-help.log) |  |
| close-ticket-help | 0 | 146ms | 23603 | [`node-logs/spec.cli.help.close-ticket-help.log`](node-logs/spec.cli.help.close-ticket-help.log) |  |
| incomplete-scaffold | 2 | 145ms | 23604 | [`node-logs/spec.cli.help.incomplete-scaffold.log`](node-logs/spec.cli.help.incomplete-scaffold.log) |  |
| incomplete-open | 2 | 136ms | 23605 | [`node-logs/spec.cli.help.incomplete-open.log`](node-logs/spec.cli.help.incomplete-open.log) |  |
| incomplete-run | 2 | 140ms | 23607 | [`node-logs/spec.cli.help.incomplete-run.log`](node-logs/spec.cli.help.incomplete-run.log) |  |
| incomplete-close | 2 | 144ms | 23609 | [`node-logs/spec.cli.help.incomplete-close.log`](node-logs/spec.cli.help.incomplete-close.log) |  |

**Node-process stdout**: [node-logs/spec.cli.help.stdout.log](node-logs/spec.cli.help.stdout.log)

---

## `spec.cli.install` — **PASS**

executor start: `2026-07-19T19:45:17.456764Z`  
executor end: `2026-07-19T19:45:18.072243Z`  
spawn exit code: 0

**Input context**: [context/spec.cli.install.input.json](context/spec.cli.install.input.json)

### Assertions

| Name | Status |
|---|---|
| install script succeeded | **PASS** |
| tla-spec-dev wrapper exists | **PASS** |

### Metrics

- `durationMs`: 512

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| install-tla-spec-dev | 0 | 512ms | 23589 | [`node-logs/spec.cli.install.install-tla-spec-dev.log`](node-logs/spec.cli.install.install-tla-spec-dev.log) |  |

### Artifacts

- `tla-spec-dev` — [`/Users/hayde/IdeaProjects/wt-43-mf027-effect-oracle-observability/test_graph/build/validation-reports/cliWorkflow-20260719-194517-b9c84eff/tla-spec-dev-bin/tla-spec-dev`](/Users/hayde/IdeaProjects/wt-43-mf027-effect-oracle-observability/test_graph/build/validation-reports/cliWorkflow-20260719-194517-b9c84eff/tla-spec-dev-bin/tla-spec-dev)

### Published context

- `cliPath`: `/Users/hayde/IdeaProjects/wt-43-mf027-effect-oracle-observability/test_graph/build/validation-reports/cliWorkflow-20260719-194517-b9c84eff/tla-spec-dev-bin/tla-spec-dev`
- `binDir`: `/Users/hayde/IdeaProjects/wt-43-mf027-effect-oracle-observability/test_graph/build/validation-reports/cliWorkflow-20260719-194517-b9c84eff/tla-spec-dev-bin`

**Node-process stdout**: [node-logs/spec.cli.install.stdout.log](node-logs/spec.cli.install.stdout.log)

---

