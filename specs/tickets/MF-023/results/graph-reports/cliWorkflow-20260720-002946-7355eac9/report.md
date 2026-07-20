# Validation report — cliWorkflow-20260720-002946-7355eac9

**Overall**: PASSED  
**Nodes**: 2 (passed=2, failed=0, errored=0)

| Node | Status | Duration | Input context | Captured stdout |
|---|---|---|---|---|
| `spec.cli.help` | **PASS** | 765ms | [context/spec.cli.help.input.json](context/spec.cli.help.input.json) | [node-logs/spec.cli.help.stdout.log](node-logs/spec.cli.help.stdout.log) |
| `spec.cli.install` | **PASS** | 387ms | [context/spec.cli.install.input.json](context/spec.cli.install.input.json) | [node-logs/spec.cli.install.stdout.log](node-logs/spec.cli.install.stdout.log) |

## `spec.cli.help` — **PASS**

executor start: `2026-07-20T00:29:47.122651Z`  
executor end: `2026-07-20T00:29:47.887460Z`  
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

- `durationMs`: 713

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| version | 0 | 58ms | 91105 | [`node-logs/spec.cli.help.version.log`](node-logs/spec.cli.help.version.log) |  |
| root-help | 0 | 66ms | 91110 | [`node-logs/spec.cli.help.root-help.log`](node-logs/spec.cli.help.root-help.log) |  |
| scaffold-help | 0 | 67ms | 91122 | [`node-logs/spec.cli.help.scaffold-help.log`](node-logs/spec.cli.help.scaffold-help.log) |  |
| project-help | 0 | 61ms | 91123 | [`node-logs/spec.cli.help.project-help.log`](node-logs/spec.cli.help.project-help.log) |  |
| workflow-help | 0 | 58ms | 91124 | [`node-logs/spec.cli.help.workflow-help.log`](node-logs/spec.cli.help.workflow-help.log) |  |
| open-ticket-help | 0 | 58ms | 91125 | [`node-logs/spec.cli.help.open-ticket-help.log`](node-logs/spec.cli.help.open-ticket-help.log) |  |
| run-spec-units-help | 0 | 57ms | 91126 | [`node-logs/spec.cli.help.run-spec-units-help.log`](node-logs/spec.cli.help.run-spec-units-help.log) |  |
| close-ticket-help | 0 | 58ms | 91127 | [`node-logs/spec.cli.help.close-ticket-help.log`](node-logs/spec.cli.help.close-ticket-help.log) |  |
| incomplete-scaffold | 2 | 55ms | 91128 | [`node-logs/spec.cli.help.incomplete-scaffold.log`](node-logs/spec.cli.help.incomplete-scaffold.log) |  |
| incomplete-open | 2 | 55ms | 91129 | [`node-logs/spec.cli.help.incomplete-open.log`](node-logs/spec.cli.help.incomplete-open.log) |  |
| incomplete-run | 2 | 58ms | 91130 | [`node-logs/spec.cli.help.incomplete-run.log`](node-logs/spec.cli.help.incomplete-run.log) |  |
| incomplete-close | 2 | 56ms | 91142 | [`node-logs/spec.cli.help.incomplete-close.log`](node-logs/spec.cli.help.incomplete-close.log) |  |

**Node-process stdout**: [node-logs/spec.cli.help.stdout.log](node-logs/spec.cli.help.stdout.log)

---

## `spec.cli.install` — **PASS**

executor start: `2026-07-20T00:29:46.733176Z`  
executor end: `2026-07-20T00:29:47.120713Z`  
spawn exit code: 0

**Input context**: [context/spec.cli.install.input.json](context/spec.cli.install.input.json)

### Assertions

| Name | Status |
|---|---|
| install script succeeded | **PASS** |
| tla-spec-dev wrapper exists | **PASS** |

### Metrics

- `durationMs`: 335

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| install-tla-spec-dev | 0 | 336ms | 90986 | [`node-logs/spec.cli.install.install-tla-spec-dev.log`](node-logs/spec.cli.install.install-tla-spec-dev.log) |  |

### Artifacts

- `tla-spec-dev` — [`/Users/hayde/IdeaProjects/wt-30-mf023-decompose-dogfooding/test_graph/build/validation-reports/cliWorkflow-20260720-002946-7355eac9/tla-spec-dev-bin/tla-spec-dev`](/Users/hayde/IdeaProjects/wt-30-mf023-decompose-dogfooding/test_graph/build/validation-reports/cliWorkflow-20260720-002946-7355eac9/tla-spec-dev-bin/tla-spec-dev)

### Published context

- `cliPath`: `/Users/hayde/IdeaProjects/wt-30-mf023-decompose-dogfooding/test_graph/build/validation-reports/cliWorkflow-20260720-002946-7355eac9/tla-spec-dev-bin/tla-spec-dev`
- `binDir`: `/Users/hayde/IdeaProjects/wt-30-mf023-decompose-dogfooding/test_graph/build/validation-reports/cliWorkflow-20260720-002946-7355eac9/tla-spec-dev-bin`

**Node-process stdout**: [node-logs/spec.cli.install.stdout.log](node-logs/spec.cli.install.stdout.log)

---

