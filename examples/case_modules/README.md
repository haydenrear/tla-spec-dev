# Case Modules — the probe that produced `references/case_modules.md`

Three BDD-style case modules over the `examples/distributed_history` External
view. They are **evidence, not a fixture**: they were written to answer one
question — does slicing a view into per-aspect case generators work with the
shipped toolchain, and what does it cost — and the answer is recorded in
`MEASUREMENTS.md`.

Each module EXTENDS `External` and declares no variables, no constants, and no
actions. Read `references/case_modules.md` before using the shape.

| module | form | aspect |
|---|---|---|
| `Scenario_CheckoutHappyPath` | slice (restricts `Next`) | account → cart → checkout → fulfillment |
| `Scenario_IdempotentResubmit` | Given (replaces `Init`) | resubmitting an applied command changes nothing |
| `Scenario_RejectedRequests` | slice | unknown account and empty cart are refused |

## Why they live here and not in `specs/program_model/`

TLA+ resolves `EXTENDS` from the same directory, so running these means copying
them next to `Core.tla` / `Internal.tla` / `External.tla`. They are kept out of
the example's accepted baseline deliberately: the baseline is a closed, promoted
model, and CM-F1 (`references/case_modules.md`) means an extra `*.tla` in that
directory changes which model the complexity ledger measures. The `Scenario_`
prefix keeps that pick unchanged, but the accepted baseline is not the place to
prove it.

## Reproducing the measurements

```bash
cp examples/case_modules/Scenario_*.tla examples/case_modules/Scenario_*.cfg \
   examples/distributed_history/specs/program_model/
cd examples/distributed_history

for m in Scenario_CheckoutHappyPath Scenario_IdempotentResubmit Scenario_RejectedRequests; do
  python3 ../../scripts/generate_cases_from_tlc_dump.py \
    specs/program_model/$m.tla specs/program_model/$m.cfg \
    --out /tmp/case-modules --package ${m}_cases --view external \
    --actions-metadata specs/program_model/actions.yml \
    --state-projector specs.program_model.tlc_projection:project_visible_state \
    --output-projector specs.program_model.tlc_projection:project_adapter_output \
    --dedupe projected
done

# the same bindings and adapters, unchanged, against a case-module package
python3 ../../scripts/run_generated_case_adapters.py \
  /tmp/case-modules/testgraph/Scenario_CheckoutHappyPath_cases \
  --mapping specs/program_model/testgraph_bindings.yml \
  --view external --batch --validate-only --import-root .
```

`tlc2` must be on PATH (it needs Java). Remove the copied `Scenario_*` files
from `specs/program_model/` afterwards — the accepted baseline keeps none.
