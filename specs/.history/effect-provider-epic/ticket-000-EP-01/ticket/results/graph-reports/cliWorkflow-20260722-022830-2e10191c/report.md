# Validation report — cliWorkflow-20260722-022830-2e10191c

**Overall**: PASSED
**Nodes**: 2 (passed=2, failed=0, errored=0)

| Node | Status | Duration | Input context | Captured stdout |
|---|---|---|---|---|
| `spec.cli.help` | **PASS** | 769ms | [context/spec.cli.help.input.json](context/spec.cli.help.input.json) | [node-logs/spec.cli.help.stdout.log](node-logs/spec.cli.help.stdout.log) |
| `spec.cli.install` | **PASS** | 298ms | [context/spec.cli.install.input.json](context/spec.cli.install.input.json) | [node-logs/spec.cli.install.stdout.log](node-logs/spec.cli.install.stdout.log) |

## `spec.cli.help` — **PASS**

executor start: `2026-07-22T02:28:30.727434Z`
executor end: `2026-07-22T02:28:31.496088Z`
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

- `durationMs`: 714

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| version | 0 | 56ms | 17763 | [`node-logs/spec.cli.help.version.log`](node-logs/spec.cli.help.version.log) |  |
| root-help | 0 | 58ms | 17764 | [`node-logs/spec.cli.help.root-help.log`](node-logs/spec.cli.help.root-help.log) |  |
| scaffold-help | 0 | 59ms | 17765 | [`node-logs/spec.cli.help.scaffold-help.log`](node-logs/spec.cli.help.scaffold-help.log) |  |
| project-help | 0 | 56ms | 17766 | [`node-logs/spec.cli.help.project-help.log`](node-logs/spec.cli.help.project-help.log) |  |
| workflow-help | 0 | 57ms | 17767 | [`node-logs/spec.cli.help.workflow-help.log`](node-logs/spec.cli.help.workflow-help.log) |  |
| open-ticket-help | 0 | 61ms | 17768 | [`node-logs/spec.cli.help.open-ticket-help.log`](node-logs/spec.cli.help.open-ticket-help.log) |  |
| run-spec-units-help | 0 | 70ms | 17769 | [`node-logs/spec.cli.help.run-spec-units-help.log`](node-logs/spec.cli.help.run-spec-units-help.log) |  |
| close-ticket-help | 0 | 62ms | 17770 | [`node-logs/spec.cli.help.close-ticket-help.log`](node-logs/spec.cli.help.close-ticket-help.log) |  |
| incomplete-scaffold | 2 | 59ms | 17771 | [`node-logs/spec.cli.help.incomplete-scaffold.log`](node-logs/spec.cli.help.incomplete-scaffold.log) |  |
| incomplete-open | 2 | 59ms | 17772 | [`node-logs/spec.cli.help.incomplete-open.log`](node-logs/spec.cli.help.incomplete-open.log) |  |
| incomplete-run | 2 | 58ms | 17773 | [`node-logs/spec.cli.help.incomplete-run.log`](node-logs/spec.cli.help.incomplete-run.log) |  |
| incomplete-close | 2 | 56ms | 17774 | [`node-logs/spec.cli.help.incomplete-close.log`](node-logs/spec.cli.help.incomplete-close.log) |  |

**Node-process stdout**: [node-logs/spec.cli.help.stdout.log](node-logs/spec.cli.help.stdout.log)

---

## `spec.cli.install` — **PASS**

executor start: `2026-07-22T02:28:30.427001Z`
executor end: `2026-07-22T02:28:30.725470Z`
spawn exit code: 0

**Input context**: [context/spec.cli.install.input.json](context/spec.cli.install.input.json)

### Assertions

| Name | Status |
|---|---|
| install script succeeded | **PASS** |
| tla-spec-dev wrapper exists | **PASS** |

### Metrics

- `durationMs`: 243

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| install-tla-spec-dev | 0 | 243ms | 17756 | [`node-logs/spec.cli.install.install-tla-spec-dev.log`](node-logs/spec.cli.install.install-tla-spec-dev.log) |  |

### Artifacts

- `tla-spec-dev` — [`/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/cliWorkflow-20260722-022830-2e10191c/tla-spec-dev-bin/tla-spec-dev`](/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/cliWorkflow-20260722-022830-2e10191c/tla-spec-dev-bin/tla-spec-dev)

### Published context

- `cliPath`: `/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/cliWorkflow-20260722-022830-2e10191c/tla-spec-dev-bin/tla-spec-dev`
- `binDir`: `/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/cliWorkflow-20260722-022830-2e10191c/tla-spec-dev-bin`

**Node-process stdout**: [node-logs/spec.cli.install.stdout.log](node-logs/spec.cli.install.stdout.log)

---
