#!/usr/bin/env bash
# HP-04 -- CM-F5 / EV-03-DF-02, re-run against the hexagonal-prompting tree.
#
# This is EV-03's `case_modules_worked_example.sh` (ex4-run4) with ONE
# environmental change and nothing else: `--out` now has to resolve under a
# `specs/` directory (RC-01/RC-02 constrained it so the `spec_tree` port stays
# true), and EV-03's `mktemp -d` does not.  So OUT is `<tmp>/specs/wt`.
#
# The measured question is unchanged and is asked in three places:
#   STEP 5  -- the GIVEN's corpus, which has always executed.
#   STEP 6  -- the SLICE against the mapping the fixture ships.  CM-F5.
#   STEP 6b -- the SLICE against the fixture's SECOND shipped mapping.
#              EV-03-DF-02: this refuses too, so the fixture has ZERO working
#              configurations for its own slice.
#
# $PY is the interpreter, $REPO the checkout.  Nothing under
# examples/validation/ex4_pipeline_coherent is written; the last step proves it.
set -u
: "${PY:?set PY to the interpreter}"
: "${REPO:?set REPO to the repo root}"
export PYTHONDONTWRITEBYTECODE=1

cd "$REPO/examples/validation/ex4_pipeline_coherent" || exit 1
TMP=$(mktemp -d)
OUT="$TMP/specs/wt"
mkdir -p "$OUT"
echo "OUT=$OUT"
echo "PY=$PY  ($($PY -V 2>&1))"
echo

echo "=== STEP 2 -- the view's own corpus ==="
PYTHONPATH=$PWD $PY "$REPO/scripts/generate_cases_from_tlc_dump.py" \
  specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg \
  --out "$OUT" --package Pipeline_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected 2>&1 | grep -Ei "^wrote|cases$|Largest" | head -6
echo "STEP2_EXIT=${PIPESTATUS[0]}"
echo

echo "=== STEP 3a -- the SLICE, generated from specs/case_modules/ IN PLACE ==="
PYTHONPATH=$PWD $PY "$REPO/scripts/generate_cases_from_tlc_dump.py" \
  specs/case_modules/Scenario_DeliveryPath.tla specs/case_modules/Scenario_DeliveryPath.cfg \
  --out "$OUT" --package Scenario_DeliveryPath_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected 2>&1 | grep -Ei "^wrote|cases$|Largest" | head -6
echo "STEP3a_EXIT=${PIPESTATUS[0]}"
echo

echo "=== STEP 3b -- the GIVEN, generated from specs/case_modules/ IN PLACE ==="
PYTHONPATH=$PWD $PY "$REPO/scripts/generate_cases_from_tlc_dump.py" \
  specs/case_modules/Scenario_RecordAfterDelivery.tla specs/case_modules/Scenario_RecordAfterDelivery.cfg \
  --out "$OUT" --package Scenario_RecordAfterDelivery_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected 2>&1 | grep -Ei "^wrote|cases$|Largest" | head -6
echo "STEP3b_EXIT=${PIPESTATUS[0]}"
echo

echo "=== STEP 5 -- EXECUTE the GIVEN's corpus against the project's UNCHANGED adapters ==="
PYTHONPATH=$REPO:$PWD/generated $PY "$REPO/scripts/run_generated_case_adapters.py" \
  "$OUT/spec-unit/Scenario_RecordAfterDelivery_cases" \
  --mapping specs/program_model/case_adapters.toml \
  --spec-dir specs/program_model --view internal --batch \
  --import-root . --import-root ./generated 2>&1 | tail -12
echo "STEP5_EXIT=${PIPESTATUS[0]}"
echo

echo "=== STEP 6 -- the SAME command on the SLICE. CM-F5: does it still refuse? ==="
PYTHONPATH=$REPO:$PWD/generated $PY "$REPO/scripts/run_generated_case_adapters.py" \
  "$OUT/spec-unit/Scenario_DeliveryPath_cases" \
  --mapping specs/program_model/case_adapters.toml \
  --spec-dir specs/program_model --view internal --batch \
  --import-root . --import-root ./generated 2>&1 | tail -12
echo "STEP6_EXIT=${PIPESTATUS[0]}"
echo

echo "=== STEP 6b -- EV-03-DF-02 control: the slice under the CORPUS-ONLY mapping ==="
PYTHONPATH=$REPO:$PWD/generated $PY "$REPO/scripts/run_generated_case_adapters.py" \
  "$OUT/spec-unit/Scenario_DeliveryPath_cases" \
  --mapping specs/program_model/case_adapters_corpus_only.toml \
  --spec-dir specs/program_model --view internal --batch \
  --import-root . --import-root ./generated 2>&1 | tail -12
echo "STEP6b_EXIT=${PIPESTATUS[0]}"
echo

echo "=== the fixture is untouched ==="
cd "$REPO" && git status --porcelain examples/validation/ex4_pipeline_coherent
echo "(empty above == clean)"
rm -rf "$TMP"
