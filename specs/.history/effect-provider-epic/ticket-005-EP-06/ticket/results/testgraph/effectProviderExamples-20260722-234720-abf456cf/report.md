# Validation report — effectProviderExamples-20260722-234720-abf456cf

**Overall**: PASSED
**Nodes**: 1 (passed=1, failed=0, errored=0)

| Node | Status | Duration | Input context | Captured stdout |
|---|---|---|---|---|
| `effect.providers.examples` | **PASS** | 61014ms | [context/effect.providers.examples.input.json](context/effect.providers.examples.input.json) | [node-logs/effect.providers.examples.stdout.log](node-logs/effect.providers.examples.stdout.log) |

## `effect.providers.examples` — **PASS**

executor start: `2026-07-22T23:47:20.115577Z`
executor end: `2026-07-22T23:48:21.129897Z`
spawn exit code: 0

**Input context**: [context/effect.providers.examples.input.json](context/effect.providers.examples.input.json)

### Assertions

| Name | Status |
|---|---|
| repository-level repeatable validation passed | **PASS** |
| aggregate contains three passing independent projects | **PASS** |
| all examples use the replacement generic provider contract | **PASS** |
| controls and fixed mutant catalogs are green | **PASS** |
| exact replay and cleanup survive repeated use | **PASS** |
| all 70 real-boundary cases are represented (observed 70) | **PASS** |
| results distinguish all three oracle ownership layers {'tla_owned': 10, 'provider_owned': 10, 'passive_external': 8} | **PASS** |
| surviving limitations remain explicit | **PASS** |

### Metrics

- `projectsValidated`: 3
- `fixedMutantsUnique`: 36
- `effectfulMutantExecutionsKilled`: 48
- `effectfulMutantExecutionsTotal`: 48
- `exactReplays`: 37
- `cleanupChecks`: 3140
- `externalCasesValidated`: 70
- `durationMs`: 60961

### Subprocesses

| Label | Exit | Duration | PID | Log | Error |
|---|---|---|---|---|---|
| repeatable-effect-provider-validations | 0 | 59019ms | 95534 | [`node-logs/effect.providers.examples.repeatable-effect-provider-validations.log`](node-logs/effect.providers.examples.repeatable-effect-provider-validations.log) |  |

### Artifacts

- `aggregate-results` — [`/private/tmp/tla-spec-dev-101-ep06-repeatable-example-validation/examples/effect_providers/evidence/validation-runs/testgraph-1784764040160583000/aggregate.json`](/private/tmp/tla-spec-dev-101-ep06-repeatable-example-validation/examples/effect_providers/evidence/validation-runs/testgraph-1784764040160583000/aggregate.json)
- `atomic_publisher-result` — [`/private/tmp/tla-spec-dev-101-ep06-repeatable-example-validation/examples/effect_providers/atomic_publisher/evidence/validation-runs/testgraph-1784764040160583000-atomic_publisher/result.json`](/private/tmp/tla-spec-dev-101-ep06-repeatable-example-validation/examples/effect_providers/atomic_publisher/evidence/validation-runs/testgraph-1784764040160583000-atomic_publisher/result.json)
- `legacy_payment_http-result` — [`/private/tmp/tla-spec-dev-101-ep06-repeatable-example-validation/examples/effect_providers/legacy_payment_http/evidence/validation-runs/testgraph-1784764040160583000-legacy_payment_http/result.json`](/private/tmp/tla-spec-dev-101-ep06-repeatable-example-validation/examples/effect_providers/legacy_payment_http/evidence/validation-runs/testgraph-1784764040160583000-legacy_payment_http/result.json)
- `reminder_worker-result` — [`/private/tmp/tla-spec-dev-101-ep06-repeatable-example-validation/examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/result.json`](/private/tmp/tla-spec-dev-101-ep06-repeatable-example-validation/examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/result.json)

**Node-process stdout**: [node-logs/effect.providers.examples.stdout.log](node-logs/effect.providers.examples.stdout.log)

---
