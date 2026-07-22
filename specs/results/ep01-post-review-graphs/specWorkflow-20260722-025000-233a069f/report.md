# Validation report — specWorkflow-20260722-025000-233a069f

**Overall**: PASSED
**Nodes**: 8 (passed=8, failed=0, errored=0)

| Node | Status | Duration | Input context | Captured stdout |
|---|---|---|---|---|
| `spec.cli.install` | **PASS** | 331ms | [context/spec.cli.install.input.json](context/spec.cli.install.input.json) | [node-logs/spec.cli.install.stdout.log](node-logs/spec.cli.install.stdout.log) |
| `spec.workflow.cleanup` | **PASS** | 91ms | [context/spec.workflow.cleanup.input.json](context/spec.workflow.cleanup.input.json) | [node-logs/spec.workflow.cleanup.stdout.log](node-logs/spec.workflow.cleanup.stdout.log) |
| `spec.workflow.close` | **PASS** | 352ms | [context/spec.workflow.close.input.json](context/spec.workflow.close.input.json) | [node-logs/spec.workflow.close.stdout.log](node-logs/spec.workflow.close.stdout.log) |
| `spec.workflow.complete` | **PASS** | 138ms | [context/spec.workflow.complete.input.json](context/spec.workflow.complete.input.json) | [node-logs/spec.workflow.complete.stdout.log](node-logs/spec.workflow.complete.stdout.log) |
| `spec.workflow.failure_cleanup_probe` | **PASS** | 9061ms | [context/spec.workflow.failure_cleanup_probe.input.json](context/spec.workflow.failure_cleanup_probe.input.json) | [node-logs/spec.workflow.failure_cleanup_probe.stdout.log](node-logs/spec.workflow.failure_cleanup_probe.stdout.log) |
| `spec.workflow.repo` | **PASS** | 162ms | [context/spec.workflow.repo.input.json](context/spec.workflow.repo.input.json) | [node-logs/spec.workflow.repo.stdout.log](node-logs/spec.workflow.repo.stdout.log) |
| `spec.workflow.spec_units` | **PASS** | 437ms | [context/spec.workflow.spec_units.input.json](context/spec.workflow.spec_units.input.json) | [node-logs/spec.workflow.spec_units.stdout.log](node-logs/spec.workflow.spec_units.stdout.log) |
| `spec.workflow.start` | **PASS** | 345ms | [context/spec.workflow.start.input.json](context/spec.workflow.start.input.json) | [node-logs/spec.workflow.start.stdout.log](node-logs/spec.workflow.start.stdout.log) |

## `spec.cli.install` — **PASS**

executor start: `2026-07-22T02:50:00.137597Z`
executor end: `2026-07-22T02:50:00.468250Z`
spawn exit code: 0

**Input context**: [context/spec.cli.install.input.json](context/spec.cli.install.input.json)

### Assertions

| Name | Status |
|---|---|
| install script succeeded | **PASS** |
| tla-spec-dev wrapper exists | **PASS** |

### Metrics

- `durationMs`: 275

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| install-tla-spec-dev | 0 | 275ms | 86554 | [`node-logs/spec.cli.install.install-tla-spec-dev.log`](node-logs/spec.cli.install.install-tla-spec-dev.log) |  |

### Artifacts

- `tla-spec-dev` — [`/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/tla-spec-dev-bin/tla-spec-dev`](/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/tla-spec-dev-bin/tla-spec-dev)

### Published context

- `cliPath`: `/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/tla-spec-dev-bin/tla-spec-dev`
- `binDir`: `/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/tla-spec-dev-bin`

**Node-process stdout**: [node-logs/spec.cli.install.stdout.log](node-logs/spec.cli.install.stdout.log)

---

## `spec.workflow.cleanup` — **PASS**

executor start: `2026-07-22T02:50:10.971903Z`
executor end: `2026-07-22T02:50:11.062977Z`
spawn exit code: 0

**Input context**: [context/spec.workflow.cleanup.input.json](context/spec.workflow.cleanup.input.json)

### Assertions

| Name | Status |
|---|---|
| fixture repo path was published | **PASS** |
| fixture repo removed | **PASS** |

### Metrics

- `removedRepos`: 1
- `durationMs`: 35

**Node-process stdout**: [node-logs/spec.workflow.cleanup.stdout.log](node-logs/spec.workflow.cleanup.stdout.log)

---

## `spec.workflow.close` — **PASS**

executor start: `2026-07-22T02:50:01.556478Z`
executor end: `2026-07-22T02:50:01.908592Z`
spawn exit code: 0

**Input context**: [context/spec.workflow.close.input.json](context/spec.workflow.close.input.json)

### Assertions

| Name | Status |
|---|---|
| open ticket scaffolded the complexity ledger input with TODO sentinels | **PASS** |
| close-ticket succeeded | **PASS** |
| close wrote a complexity ledger entry | **PASS** |
| ledger entry records the delta jointly with retention evidence | **PASS** |
| ledger entry carries the required refinement record | **PASS** |
| ledger entry verdict is recorded | **PASS** |
| active ticket directory removed | **PASS** |
| history directory exists | **PASS** |
| history contains ticket current | **PASS** |
| history contains ticket external view | **PASS** |
| project current promoted internal view | **PASS** |
| project current promoted external view | **PASS** |
| project current promoted Test Graph binding | **PASS** |
| project current has spec adapter | **PASS** |
| project current has adapter test | **PASS** |
| project testgraph bindings merged | **PASS** |
| project test_graph sources merged | **PASS** |
| history captured result | **PASS** |
| manifest records replace promotion | **PASS** |
| git-add succeeded | **PASS** |
| git-commit succeeded | **PASS** |
| git-status succeeded | **PASS** |
| git working tree clean after close commit | **PASS** |

### Metrics

- `durationMs`: 296

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| close-ticket | 0 | 148ms | 86595 | [`node-logs/spec.workflow.close.close-ticket.log`](node-logs/spec.workflow.close.close-ticket.log) |  |
| git-add | 0 | 40ms | 86599 | [`node-logs/spec.workflow.close.git-add.log`](node-logs/spec.workflow.close.git-add.log) |  |
| git-commit | 0 | 65ms | 86600 | [`node-logs/spec.workflow.close.git-commit.log`](node-logs/spec.workflow.close.git-commit.log) |  |
| git-status | 0 | 22ms | 86603 | [`node-logs/spec.workflow.close.git-status.log`](node-logs/spec.workflow.close.git-status.log) |  |

### Artifacts

- `history-manifest` — [`/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/spec-workflow-history-manifest.json`](/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/spec-workflow-history-manifest.json)

### Published context

- `historyDir`: `/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/fixture-repos/spec-workflow-repo/specs/.history/desired-ticket-workflow/ticket-000-FLOW-1`

**Node-process stdout**: [node-logs/spec.workflow.close.stdout.log](node-logs/spec.workflow.close.stdout.log)

---

## `spec.workflow.complete` — **PASS**

executor start: `2026-07-22T02:50:00.979631Z`
executor end: `2026-07-22T02:50:01.117838Z`
spawn exit code: 0

**Input context**: [context/spec.workflow.complete.input.json](context/spec.workflow.complete.input.json)

### Assertions

| Name | Status |
|---|---|
| git-add succeeded | **PASS** |
| git-commit succeeded | **PASS** |
| ticket plan marked done | **PASS** |
| desired internal view updated first-class | **PASS** |
| desired external view updated first-class | **PASS** |
| new external action mapped for Test Graph | **PASS** |
| current matches desired across both views | **PASS** |
| ticket spec adapter written | **PASS** |
| ticket Test Graph binding written | **PASS** |

### Metrics

- `durationMs`: 84

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| git-add | 0 | 36ms | 86582 | [`node-logs/spec.workflow.complete.git-add.log`](node-logs/spec.workflow.complete.git-add.log) |  |
| git-commit | 0 | 44ms | 86583 | [`node-logs/spec.workflow.complete.git-commit.log`](node-logs/spec.workflow.complete.git-commit.log) |  |

### Artifacts

- `ticket-plan` — [`/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/fixture-repos/spec-workflow-repo/specs/desired_program_model/ticket_plan.yaml`](/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/fixture-repos/spec-workflow-repo/specs/desired_program_model/ticket_plan.yaml)

**Node-process stdout**: [node-logs/spec.workflow.complete.stdout.log](node-logs/spec.workflow.complete.stdout.log)

---

## `spec.workflow.failure_cleanup_probe` — **PASS**

executor start: `2026-07-22T02:50:01.909824Z`
executor end: `2026-07-22T02:50:10.970580Z`
spawn exit code: 0

**Input context**: [context/spec.workflow.failure_cleanup_probe.input.json](context/spec.workflow.failure_cleanup_probe.input.json)

### Assertions

| Name | Status |
|---|---|
| probe graph failed as expected | **PASS** |
| probe report was written | **PASS** |
| repo allocation node passed | **PASS** |
| forced downstream failure was captured | **PASS** |
| cleanup finalizer ran after failure | **PASS** |
| allocated fixture repo removed after failure | **PASS** |

### Metrics

- `durationMs`: 9006

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| cleanup-failure-probe | 1 | 8981ms | 86607 | [`node-logs/spec.workflow.failure_cleanup_probe.cleanup-failure-probe.log`](node-logs/spec.workflow.failure_cleanup_probe.cleanup-failure-probe.log) |  |

### Artifacts

- `cleanup-failure-probe-report` — [`/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/cleanup-failure-probe-test-graph/build/validation-reports/cleanupFailureProbe-20260722-025009-1fce3414/report.md`](/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/cleanup-failure-probe-test-graph/build/validation-reports/cleanupFailureProbe-20260722-025009-1fce3414/report.md)
- `cleanup-failure-probe-summary` — [`/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/cleanup-failure-probe-test-graph/build/validation-reports/cleanupFailureProbe-20260722-025009-1fce3414/summary.json`](/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/cleanup-failure-probe-test-graph/build/validation-reports/cleanupFailureProbe-20260722-025009-1fce3414/summary.json)
- `cleanup-failure-probe-root` — [`/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/cleanup-failure-probe-test-graph`](/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/cleanup-failure-probe-test-graph)

**Node-process stdout**: [node-logs/spec.workflow.failure_cleanup_probe.stdout.log](node-logs/spec.workflow.failure_cleanup_probe.stdout.log)

---

## `spec.workflow.repo` — **PASS**

executor start: `2026-07-22T02:50:00.470074Z`
executor end: `2026-07-22T02:50:00.632107Z`
spawn exit code: 0

**Input context**: [context/spec.workflow.repo.input.json](context/spec.workflow.repo.input.json)

### Assertions

| Name | Status |
|---|---|
| git-init succeeded | **PASS** |
| git-branch succeeded | **PASS** |
| git-email succeeded | **PASS** |
| git-name succeeded | **PASS** |
| git-add succeeded | **PASS** |
| git-commit succeeded | **PASS** |
| installed CLI path exists | **PASS** |
| fixture repo starts without program model | **PASS** |

### Metrics

- `durationMs`: 108

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| git-init | 0 | 21ms | 86562 | [`node-logs/spec.workflow.repo.git-init.log`](node-logs/spec.workflow.repo.git-init.log) |  |
| git-branch | 0 | 14ms | 86563 | [`node-logs/spec.workflow.repo.git-branch.log`](node-logs/spec.workflow.repo.git-branch.log) |  |
| git-email | 0 | 15ms | 86564 | [`node-logs/spec.workflow.repo.git-email.log`](node-logs/spec.workflow.repo.git-email.log) |  |
| git-name | 0 | 14ms | 86565 | [`node-logs/spec.workflow.repo.git-name.log`](node-logs/spec.workflow.repo.git-name.log) |  |
| git-add | 0 | 15ms | 86566 | [`node-logs/spec.workflow.repo.git-add.log`](node-logs/spec.workflow.repo.git-add.log) |  |
| git-commit | 0 | 26ms | 86567 | [`node-logs/spec.workflow.repo.git-commit.log`](node-logs/spec.workflow.repo.git-commit.log) |  |

### Artifacts

- `fixture-repo` — [`/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/fixture-repos/spec-workflow-repo`](/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/fixture-repos/spec-workflow-repo)

### Published context

- `repoPath`: `/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/fixture-repos/spec-workflow-repo`
- `sourceRepo`: `/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime`
- `ticketId`: `FLOW-1`
- `cliPath`: `/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/tla-spec-dev-bin/tla-spec-dev`

**Node-process stdout**: [node-logs/spec.workflow.repo.stdout.log](node-logs/spec.workflow.repo.stdout.log)

---

## `spec.workflow.spec_units` — **PASS**

executor start: `2026-07-22T02:50:01.118959Z`
executor end: `2026-07-22T02:50:01.555212Z`
spawn exit code: 0

**Input context**: [context/spec.workflow.spec_units.input.json](context/spec.workflow.spec_units.input.json)

### Assertions

| Name | Status |
|---|---|
| cli spec-unit tests succeeded | **PASS** |
| spec-unit output names ticket current | **PASS** |
| spec-unit output reports pass | **PASS** |

### Metrics

- `durationMs`: 381

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| cli-run-spec-unit-tests | 0 | 381ms | 86588 | [`node-logs/spec.workflow.spec_units.cli-run-spec-unit-tests.log`](node-logs/spec.workflow.spec_units.cli-run-spec-unit-tests.log) |  |

### Artifacts

- `spec-unit-log` — [`/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/node-logs/spec.workflow.spec_units.cli-run-spec-unit-tests.log`](/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/node-logs/spec.workflow.spec_units.cli-run-spec-unit-tests.log)

**Node-process stdout**: [node-logs/spec.workflow.spec_units.stdout.log](node-logs/spec.workflow.spec_units.stdout.log)

---

## `spec.workflow.start` — **PASS**

executor start: `2026-07-22T02:50:00.633405Z`
executor end: `2026-07-22T02:50:00.978382Z`
spawn exit code: 0

**Input context**: [context/spec.workflow.start.input.json](context/spec.workflow.start.input.json)

### Assertions

| Name | Status |
|---|---|
| cli-scaffold-project succeeded | **PASS** |
| cli-scaffold-workflow succeeded | **PASS** |
| cli-open-ticket succeeded | **PASS** |
| git-add succeeded | **PASS** |
| git-commit succeeded | **PASS** |
| program model scaffolded by CLI with both views | **PASS** |
| project workflow scaffolded by CLI | **PASS** |
| ticket directory exists | **PASS** |
| ticket current + desired carry the whole baseline | **PASS** |
| no single-module stand-in left behind | **PASS** |
| ticket metadata written | **PASS** |

### Metrics

- `baselineFilesMissing`: 0
- `baselineFilesNotCopiedToTicket`: 0
- `durationMs`: 292

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| cli-scaffold-project | 0 | 62ms | 86572 | [`node-logs/spec.workflow.start.cli-scaffold-project.log`](node-logs/spec.workflow.start.cli-scaffold-project.log) |  |
| cli-scaffold-workflow | 0 | 70ms | 86573 | [`node-logs/spec.workflow.start.cli-scaffold-workflow.log`](node-logs/spec.workflow.start.cli-scaffold-workflow.log) |  |
| cli-open-ticket | 0 | 69ms | 86574 | [`node-logs/spec.workflow.start.cli-open-ticket.log`](node-logs/spec.workflow.start.cli-open-ticket.log) |  |
| git-add | 0 | 39ms | 86575 | [`node-logs/spec.workflow.start.git-add.log`](node-logs/spec.workflow.start.git-add.log) |  |
| git-commit | 0 | 50ms | 86576 | [`node-logs/spec.workflow.start.git-commit.log`](node-logs/spec.workflow.start.git-commit.log) |  |

### Artifacts

- `ticket-dir` — [`/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/fixture-repos/spec-workflow-repo/specs/tickets/FLOW-1`](/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/fixture-repos/spec-workflow-repo/specs/tickets/FLOW-1)

### Published context

- `ticketDir`: `/private/tmp/tla-spec-dev-77-ep01-effect-provider-runtime/test_graph/build/validation-reports/specWorkflow-20260722-025000-233a069f/fixture-repos/spec-workflow-repo/specs/tickets/FLOW-1`

**Node-process stdout**: [node-logs/spec.workflow.start.stdout.log](node-logs/spec.workflow.start.stdout.log)

---
