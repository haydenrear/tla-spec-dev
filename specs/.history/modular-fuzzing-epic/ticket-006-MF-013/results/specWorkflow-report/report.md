# Validation report — specWorkflow-20260719-185241-ac7f8651

**Overall**: PASSED  
**Nodes**: 8 (passed=8, failed=0, errored=0)

| Node | Status | Duration | Input context | Captured stdout |
|---|---|---|---|---|
| `spec.cli.install` | **PASS** | 556ms | [context/spec.cli.install.input.json](context/spec.cli.install.input.json) | [node-logs/spec.cli.install.stdout.log](node-logs/spec.cli.install.stdout.log) |
| `spec.workflow.cleanup` | **PASS** | 95ms | [context/spec.workflow.cleanup.input.json](context/spec.workflow.cleanup.input.json) | [node-logs/spec.workflow.cleanup.stdout.log](node-logs/spec.workflow.cleanup.stdout.log) |
| `spec.workflow.close` | **PASS** | 336ms | [context/spec.workflow.close.input.json](context/spec.workflow.close.input.json) | [node-logs/spec.workflow.close.stdout.log](node-logs/spec.workflow.close.stdout.log) |
| `spec.workflow.complete` | **PASS** | 128ms | [context/spec.workflow.complete.input.json](context/spec.workflow.complete.input.json) | [node-logs/spec.workflow.complete.stdout.log](node-logs/spec.workflow.complete.stdout.log) |
| `spec.workflow.failure_cleanup_probe` | **PASS** | 15754ms | [context/spec.workflow.failure_cleanup_probe.input.json](context/spec.workflow.failure_cleanup_probe.input.json) | [node-logs/spec.workflow.failure_cleanup_probe.stdout.log](node-logs/spec.workflow.failure_cleanup_probe.stdout.log) |
| `spec.workflow.repo` | **PASS** | 173ms | [context/spec.workflow.repo.input.json](context/spec.workflow.repo.input.json) | [node-logs/spec.workflow.repo.stdout.log](node-logs/spec.workflow.repo.stdout.log) |
| `spec.workflow.spec_units` | **PASS** | 462ms | [context/spec.workflow.spec_units.input.json](context/spec.workflow.spec_units.input.json) | [node-logs/spec.workflow.spec_units.stdout.log](node-logs/spec.workflow.spec_units.stdout.log) |
| `spec.workflow.start` | **PASS** | 340ms | [context/spec.workflow.start.input.json](context/spec.workflow.start.input.json) | [node-logs/spec.workflow.start.stdout.log](node-logs/spec.workflow.start.stdout.log) |

## `spec.cli.install` — **PASS**

executor start: `2026-07-19T18:52:42.004941Z`  
executor end: `2026-07-19T18:52:42.560662Z`  
spawn exit code: 0

**Input context**: [context/spec.cli.install.input.json](context/spec.cli.install.input.json)

### Assertions

| Name | Status |
|---|---|
| install script succeeded | **PASS** |
| tla-spec-dev wrapper exists | **PASS** |

### Metrics

- `durationMs`: 499

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| install-tla-spec-dev | 0 | 499ms | 77194 | [`node-logs/spec.cli.install.install-tla-spec-dev.log`](node-logs/spec.cli.install.install-tla-spec-dev.log) |  |

### Artifacts

- `tla-spec-dev` — [`/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/tla-spec-dev-bin/tla-spec-dev`](/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/tla-spec-dev-bin/tla-spec-dev)

### Published context

- `cliPath`: `/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/tla-spec-dev-bin/tla-spec-dev`
- `binDir`: `/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/tla-spec-dev-bin`

**Node-process stdout**: [node-logs/spec.cli.install.stdout.log](node-logs/spec.cli.install.stdout.log)

---

## `spec.workflow.cleanup` — **PASS**

executor start: `2026-07-19T18:52:59.763124Z`  
executor end: `2026-07-19T18:52:59.858653Z`  
spawn exit code: 0

**Input context**: [context/spec.workflow.cleanup.input.json](context/spec.workflow.cleanup.input.json)

### Assertions

| Name | Status |
|---|---|
| fixture repo path was published | **PASS** |
| fixture repo removed | **PASS** |

### Metrics

- `removedRepos`: 1
- `durationMs`: 39

**Node-process stdout**: [node-logs/spec.workflow.cleanup.stdout.log](node-logs/spec.workflow.cleanup.stdout.log)

---

## `spec.workflow.close` — **PASS**

executor start: `2026-07-19T18:52:43.670077Z`  
executor end: `2026-07-19T18:52:44.006478Z`  
spawn exit code: 0

**Input context**: [context/spec.workflow.close.input.json](context/spec.workflow.close.input.json)

### Assertions

| Name | Status |
|---|---|
| close-ticket succeeded | **PASS** |
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

- `durationMs`: 281

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| close-ticket | 0 | 133ms | 77244 | [`node-logs/spec.workflow.close.close-ticket.log`](node-logs/spec.workflow.close.close-ticket.log) |  |
| git-add | 0 | 35ms | 77248 | [`node-logs/spec.workflow.close.git-add.log`](node-logs/spec.workflow.close.git-add.log) |  |
| git-commit | 0 | 67ms | 77249 | [`node-logs/spec.workflow.close.git-commit.log`](node-logs/spec.workflow.close.git-commit.log) |  |
| git-status | 0 | 23ms | 77252 | [`node-logs/spec.workflow.close.git-status.log`](node-logs/spec.workflow.close.git-status.log) |  |

### Artifacts

- `history-manifest` — [`/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/spec-workflow-history-manifest.json`](/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/spec-workflow-history-manifest.json)

### Published context

- `historyDir`: `/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/fixture-repos/spec-workflow-repo/specs/.history/desired-ticket-workflow/ticket-000-FLOW-1`

**Node-process stdout**: [node-logs/spec.workflow.close.stdout.log](node-logs/spec.workflow.close.stdout.log)

---

## `spec.workflow.complete` — **PASS**

executor start: `2026-07-19T18:52:43.077924Z`  
executor end: `2026-07-19T18:52:43.205873Z`  
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

- `durationMs`: 75

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| git-add | 0 | 25ms | 77230 | [`node-logs/spec.workflow.complete.git-add.log`](node-logs/spec.workflow.complete.git-add.log) |  |
| git-commit | 0 | 45ms | 77231 | [`node-logs/spec.workflow.complete.git-commit.log`](node-logs/spec.workflow.complete.git-commit.log) |  |

### Artifacts

- `ticket-plan` — [`/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/fixture-repos/spec-workflow-repo/specs/desired_program_model/ticket_plan.yaml`](/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/fixture-repos/spec-workflow-repo/specs/desired_program_model/ticket_plan.yaml)

**Node-process stdout**: [node-logs/spec.workflow.complete.stdout.log](node-logs/spec.workflow.complete.stdout.log)

---

## `spec.workflow.failure_cleanup_probe` — **PASS**

executor start: `2026-07-19T18:52:44.007530Z`  
executor end: `2026-07-19T18:52:59.761959Z`  
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

- `durationMs`: 15701

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| cleanup-failure-probe | 1 | 15673ms | 77256 | [`node-logs/spec.workflow.failure_cleanup_probe.cleanup-failure-probe.log`](node-logs/spec.workflow.failure_cleanup_probe.cleanup-failure-probe.log) |  |

### Artifacts

- `cleanup-failure-probe-report` — [`/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/cleanup-failure-probe-test-graph/build/validation-reports/cleanupFailureProbe-20260719-185258-991f35fc/report.md`](/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/cleanup-failure-probe-test-graph/build/validation-reports/cleanupFailureProbe-20260719-185258-991f35fc/report.md)
- `cleanup-failure-probe-summary` — [`/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/cleanup-failure-probe-test-graph/build/validation-reports/cleanupFailureProbe-20260719-185258-991f35fc/summary.json`](/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/cleanup-failure-probe-test-graph/build/validation-reports/cleanupFailureProbe-20260719-185258-991f35fc/summary.json)
- `cleanup-failure-probe-root` — [`/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/cleanup-failure-probe-test-graph`](/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/cleanup-failure-probe-test-graph)

**Node-process stdout**: [node-logs/spec.workflow.failure_cleanup_probe.stdout.log](node-logs/spec.workflow.failure_cleanup_probe.stdout.log)

---

## `spec.workflow.repo` — **PASS**

executor start: `2026-07-19T18:52:42.562297Z`  
executor end: `2026-07-19T18:52:42.735600Z`  
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

- `durationMs`: 120

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| git-init | 0 | 24ms | 77211 | [`node-logs/spec.workflow.repo.git-init.log`](node-logs/spec.workflow.repo.git-init.log) |  |
| git-branch | 0 | 15ms | 77212 | [`node-logs/spec.workflow.repo.git-branch.log`](node-logs/spec.workflow.repo.git-branch.log) |  |
| git-email | 0 | 15ms | 77213 | [`node-logs/spec.workflow.repo.git-email.log`](node-logs/spec.workflow.repo.git-email.log) |  |
| git-name | 0 | 17ms | 77214 | [`node-logs/spec.workflow.repo.git-name.log`](node-logs/spec.workflow.repo.git-name.log) |  |
| git-add | 0 | 17ms | 77215 | [`node-logs/spec.workflow.repo.git-add.log`](node-logs/spec.workflow.repo.git-add.log) |  |
| git-commit | 0 | 29ms | 77216 | [`node-logs/spec.workflow.repo.git-commit.log`](node-logs/spec.workflow.repo.git-commit.log) |  |

### Artifacts

- `fixture-repo` — [`/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/fixture-repos/spec-workflow-repo`](/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/fixture-repos/spec-workflow-repo)

### Published context

- `repoPath`: `/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/fixture-repos/spec-workflow-repo`
- `sourceRepo`: `/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance`
- `ticketId`: `FLOW-1`
- `cliPath`: `/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/tla-spec-dev-bin/tla-spec-dev`

**Node-process stdout**: [node-logs/spec.workflow.repo.stdout.log](node-logs/spec.workflow.repo.stdout.log)

---

## `spec.workflow.spec_units` — **PASS**

executor start: `2026-07-19T18:52:43.207126Z`  
executor end: `2026-07-19T18:52:43.669144Z`  
spawn exit code: 0

**Input context**: [context/spec.workflow.spec_units.input.json](context/spec.workflow.spec_units.input.json)

### Assertions

| Name | Status |
|---|---|
| cli spec-unit tests succeeded | **PASS** |
| spec-unit output names ticket current | **PASS** |
| spec-unit output reports pass | **PASS** |

### Metrics

- `durationMs`: 411

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| cli-run-spec-unit-tests | 0 | 411ms | 77236 | [`node-logs/spec.workflow.spec_units.cli-run-spec-unit-tests.log`](node-logs/spec.workflow.spec_units.cli-run-spec-unit-tests.log) |  |

### Artifacts

- `spec-unit-log` — [`/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/node-logs/spec.workflow.spec_units.cli-run-spec-unit-tests.log`](/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/node-logs/spec.workflow.spec_units.cli-run-spec-unit-tests.log)

**Node-process stdout**: [node-logs/spec.workflow.spec_units.stdout.log](node-logs/spec.workflow.spec_units.stdout.log)

---

## `spec.workflow.start` — **PASS**

executor start: `2026-07-19T18:52:42.736789Z`  
executor end: `2026-07-19T18:52:43.076142Z`  
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
- `durationMs`: 285

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| cli-scaffold-project | 0 | 56ms | 77221 | [`node-logs/spec.workflow.start.cli-scaffold-project.log`](node-logs/spec.workflow.start.cli-scaffold-project.log) |  |
| cli-scaffold-workflow | 0 | 65ms | 77222 | [`node-logs/spec.workflow.start.cli-scaffold-workflow.log`](node-logs/spec.workflow.start.cli-scaffold-workflow.log) |  |
| cli-open-ticket | 0 | 70ms | 77223 | [`node-logs/spec.workflow.start.cli-open-ticket.log`](node-logs/spec.workflow.start.cli-open-ticket.log) |  |
| git-add | 0 | 42ms | 77224 | [`node-logs/spec.workflow.start.git-add.log`](node-logs/spec.workflow.start.git-add.log) |  |
| git-commit | 0 | 48ms | 77225 | [`node-logs/spec.workflow.start.git-commit.log`](node-logs/spec.workflow.start.git-commit.log) |  |

### Artifacts

- `ticket-dir` — [`/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/fixture-repos/spec-workflow-repo/specs/tickets/FLOW-1`](/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/fixture-repos/spec-workflow-repo/specs/tickets/FLOW-1)

### Published context

- `ticketDir`: `/Users/hayde/IdeaProjects/wt-15-mf013-effect-conformance/test_graph/build/validation-reports/specWorkflow-20260719-185241-ac7f8651/fixture-repos/spec-workflow-repo/specs/tickets/FLOW-1`

**Node-process stdout**: [node-logs/spec.workflow.start.stdout.log](node-logs/spec.workflow.start.stdout.log)

---

