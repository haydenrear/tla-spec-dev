#!/usr/bin/env bash
# RP-03 / EV-02-DF-05 -- the internal-view worked example, run verbatim.
#
# Every command below is COPIED FROM references/case_modules.md, "Worked example:
# an internal-only project", with nothing edited. Its recorded output is
# internal-view-worked-example.txt beside this file.
export PATH="$HOME/.skill-manager/bin/cli:$PATH"   # tlc2; not part of the doc

set -x
export REPO=$(git rev-parse --show-toplevel)
cd "$REPO/examples/validation/ex4_pipeline_coherent"
export OUT=$(mktemp -d)

# 0. The action set comes from a command, not from attention
#    (prompts/aspect_decomposition.md, Step 1).
python3 "$REPO/scripts/tla_spec_dev.py" --spec-root specs analyze architecture \
  specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg \
  --format json | python3 -c \
  "import json,sys; [print(a['name']) for a in sorted(json.load(sys.stdin)['measured']['actions'], key=lambda a: a['name'])]"

python3 -c "
import sys
sys.path.insert(0, sys.argv[3])
from pathlib import Path
from extract_spec_manifest import load_manifest
actions = load_manifest(Path(sys.argv[1])).get('actions') or {}
for name in sorted(actions):
    if (actions[name] or {}).get('layer') == sys.argv[2]:
        print(name)
" specs/program_model/actions.yml internal "$REPO/scripts"

# 1. The view's own corpus. Case modules are ADDITIVE: this keeps running.
PYTHONPATH=$PWD python3 "$REPO/scripts/generate_cases_from_tlc_dump.py" \
  specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg \
  --out "$OUT" --package Pipeline_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected

# 2. The slice, generated FROM specs/case_modules/ -- in place, nothing copied.
PYTHONPATH=$PWD python3 "$REPO/scripts/generate_cases_from_tlc_dump.py" \
  specs/case_modules/Scenario_DeliveryPath.tla specs/case_modules/Scenario_DeliveryPath.cfg \
  --out "$OUT" --package Scenario_DeliveryPath_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected

# 3. The Given, same way.
PYTHONPATH=$PWD python3 "$REPO/scripts/generate_cases_from_tlc_dump.py" \
  specs/case_modules/Scenario_RecordAfterDelivery.tla specs/case_modules/Scenario_RecordAfterDelivery.cfg \
  --out "$OUT" --package Scenario_RecordAfterDelivery_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected

# 4. The declaration.
python3 "$REPO/scripts/case_modules.py" validate \
  --manifest specs/program_model/spec_manifest.yaml

# 5. Aggregate coverage across the two modules AND the view's own corpus.
python3 "$REPO/scripts/case_modules.py" coverage \
  --manifest specs/program_model/spec_manifest.yaml \
  --actions-metadata specs/program_model/actions.yml --view internal \
  --corpus "$OUT/spec-unit/Scenario_DeliveryPath_cases" \
  --corpus "$OUT/spec-unit/Scenario_RecordAfterDelivery_cases" \
  --corpus "$OUT/spec-unit/Pipeline_cases"

# 6. Run a case-module corpus against the project's EXISTING adapters. Two
#    --import-root: the project, and the parent of the generated package.
python3 "$REPO/scripts/run_generated_case_adapters.py" \
  "$OUT/spec-unit/Scenario_RecordAfterDelivery_cases" \
  --mapping specs/program_model/case_adapters.toml \
  --spec-dir specs/program_model --view internal --batch \
  --import-root . --import-root ./generated

# 7. The same command on the SLICE refuses, and the refusal is CM-F5, not a
#    mistake in the command. Expected to exit nonzero.
python3 "$REPO/scripts/run_generated_case_adapters.py" \
  "$OUT/spec-unit/Scenario_DeliveryPath_cases" \
  --mapping specs/program_model/case_adapters.toml \
  --spec-dir specs/program_model --view internal --batch \
  --import-root . --import-root ./generated

echo "worked example finished; step 7 is expected to have exited nonzero"
