#!/usr/bin/env bash
# EV-03 arm 3: RP-03's worked example ("Worked example: an internal-only
# project", references/case_modules.md) run VERBATIM against the repaired tree,
# from the DOCUMENTED location, with no copying.
#
# $PY is the pinned interpreter (see the run record); $REPO the epic checkout.
# Every step's exit code is printed. Step 6 is expected to FAIL -- that is
# CM-F5, and the point of the arm is to say whether it still holds.
set -u
: "${PY:?set PY to the pinned interpreter}"
: "${REPO:?set REPO to the repo root}"
export PYTHONDONTWRITEBYTECODE=1
export PATH="$HOME/.skill-manager/bin/cli:$PATH"

cd "$REPO/examples/validation/ex4_pipeline_coherent" || exit 1
OUT=$(mktemp -d)
echo "OUT=$OUT"
echo "PY=$PY  ($($PY -V 2>&1))"
echo

echo "=== STEP 1 -- the action set from a command ==="
$PY "$REPO/scripts/tla_spec_dev.py" --spec-root specs analyze architecture \
  specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg \
  --format json | $PY -c \
  "import json,sys; [print(a['name']) for a in sorted(json.load(sys.stdin)['measured']['actions'], key=lambda a: a['name'])]"
echo "STEP1_EXIT=$?"
echo

echo "=== STEP 2 -- the view's own corpus ==="
PYTHONPATH=$PWD $PY "$REPO/scripts/generate_cases_from_tlc_dump.py" \
  specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg \
  --out "$OUT" --package Pipeline_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected 2>&1 | grep -Ei "cases|states|recovered|params:" | head -12
echo "STEP2_EXIT=${PIPESTATUS[0]}"
echo

echo "=== STEP 3a -- the SLICE, generated from specs/case_modules/ IN PLACE ==="
PYTHONPATH=$PWD $PY "$REPO/scripts/generate_cases_from_tlc_dump.py" \
  specs/case_modules/Scenario_DeliveryPath.tla specs/case_modules/Scenario_DeliveryPath.cfg \
  --out "$OUT" --package Scenario_DeliveryPath_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected 2>&1 | grep -Ei "cases|states|recovered|params:" | head -12
echo "STEP3a_EXIT=${PIPESTATUS[0]}"
echo

echo "=== STEP 3b -- the GIVEN, generated from specs/case_modules/ IN PLACE ==="
PYTHONPATH=$PWD $PY "$REPO/scripts/generate_cases_from_tlc_dump.py" \
  specs/case_modules/Scenario_RecordAfterDelivery.tla specs/case_modules/Scenario_RecordAfterDelivery.cfg \
  --out "$OUT" --package Scenario_RecordAfterDelivery_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected 2>&1 | grep -Ei "cases|states|recovered|params:" | head -12
echo "STEP3b_EXIT=${PIPESTATUS[0]}"
echo

echo "=== recovered-argument counts per corpus (RP-03's adjacent fix) ==="
for p in Pipeline_cases Scenario_DeliveryPath_cases Scenario_RecordAfterDelivery_cases; do
  total=$(grep -c "params=" "$OUT/spec-unit/$p/cases.py")
  unchecked=$(grep -c "UNCHECKED" "$OUT/spec-unit/$p/cases.py")
  echo "  $p: params-bearing lines=$total  UNCHECKED=$unchecked"
done
echo

echo "=== STEP 4 -- validate + coverage ==="
$PY "$REPO/scripts/case_modules.py" validate \
  --manifest specs/program_model/spec_manifest.yaml
echo "STEP4a_EXIT=$?"
$PY "$REPO/scripts/case_modules.py" coverage \
  --manifest specs/program_model/spec_manifest.yaml \
  --actions-metadata specs/program_model/actions.yml --view internal \
  --corpus "$OUT/spec-unit/Scenario_DeliveryPath_cases" \
  --corpus "$OUT/spec-unit/Scenario_RecordAfterDelivery_cases" \
  --corpus "$OUT/spec-unit/Pipeline_cases"
echo "STEP4b_EXIT=$?"
echo

echo "=== STEP 5 -- EXECUTE the Given's corpus against the project's UNCHANGED adapters ==="
PYTHONPATH=$REPO:$PWD/generated $PY "$REPO/scripts/run_generated_case_adapters.py" \
  "$OUT/spec-unit/Scenario_RecordAfterDelivery_cases" \
  --mapping specs/program_model/case_adapters.toml \
  --spec-dir specs/program_model --view internal --batch \
  --import-root . --import-root ./generated 2>&1 | tail -8
echo "STEP5_EXIT=${PIPESTATUS[0]}"
echo

echo "=== STEP 6 -- the SAME command on the SLICE. CM-F5: does it still refuse? ==="
PYTHONPATH=$REPO:$PWD/generated $PY "$REPO/scripts/run_generated_case_adapters.py" \
  "$OUT/spec-unit/Scenario_DeliveryPath_cases" \
  --mapping specs/program_model/case_adapters.toml \
  --spec-dir specs/program_model --view internal --batch \
  --import-root . --import-root ./generated 2>&1 | tail -8
echo "STEP6_EXIT=${PIPESTATUS[0]}"
echo

echo "=== STEP 6b -- CM-F5 control: the slice under the CORPUS-ONLY mapping ==="
PYTHONPATH=$REPO:$PWD/generated $PY "$REPO/scripts/run_generated_case_adapters.py" \
  "$OUT/spec-unit/Scenario_DeliveryPath_cases" \
  --mapping specs/program_model/case_adapters_corpus_only.toml \
  --spec-dir specs/program_model --view internal --batch \
  --import-root . --import-root ./generated 2>&1 | tail -8
echo "STEP6b_EXIT=${PIPESTATUS[0]}"
echo

echo "=== fingerprints of the three generated corpora ==="
for p in Pipeline_cases Scenario_DeliveryPath_cases Scenario_RecordAfterDelivery_cases; do
  shasum -a 256 "$OUT/spec-unit/$p/cases.py"
done
echo
echo "=== the fixture is untouched ==="
cd "$REPO" && git status --porcelain examples/validation/ex4_pipeline_coherent
echo "(empty above == clean)"
rm -rf "$OUT"
