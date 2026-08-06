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
model, and these are a probe.

They used to be kept out for a second reason — CM-F1, where an extra `*.tla` in
that directory changed which model the complexity ledger measured, and the
`Scenario_` prefix was the convention holding that pick still. CM-01 fixed that:
the example's `spec_manifest.yaml` now declares `model: {tla: External.tla, cfg:
External.cfg}`, so no file dropped into the directory can move the measurement.
The prefix is now just a name.

The set of modules the example runs, and the claim the Given asserts, are
declared in that same manifest under `case_modules:`. The declarations stay even
though the module files do not — that is what gives generation its per-module
action scope and gives the coverage report something to aggregate against.

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

# per-action coverage across the three modules, against the view's action set.
# Add `--corpus /tmp/case-modules/testgraph/External_cases` after a whole-view
# run to fill the view column; without it that column reads UNMEASURED, which
# is not the same fact as zero. Reports, never gates; always exits 0.
python3 ../../scripts/case_modules.py coverage \
  --manifest specs/program_model/spec_manifest.yaml \
  --actions-metadata specs/program_model/actions.yml --view external \
  --corpus /tmp/case-modules/testgraph/Scenario_CheckoutHappyPath_cases \
  --corpus /tmp/case-modules/testgraph/Scenario_IdempotentResubmit_cases \
  --corpus /tmp/case-modules/testgraph/Scenario_RejectedRequests_cases
```

`tlc2` must be on PATH (it needs Java). Remove the copied `Scenario_*` files
from `specs/program_model/` afterwards — the accepted baseline keeps none.

Reproduced 2026-07-27 on the CM-01 branch: 160 / 16 / 14 cases and 732 for the
whole view, unchanged, and zero spurious zero-case warnings now that the modules
are declared. Evidence: `specs/tickets/CM-01/results/`.
