#!/usr/bin/env bash
# HP-04 -- GOAL-hexagonal-in-fact, local signal: "run one aspect's corpus
# against a real adapter and a fake".
#
# Scorecard D3 anchor 4 wants a driven port exercised by a real adapter AND a
# fake with the SAME CASES PASSING AGAINST BOTH. `ex4_pipeline_coherent` ships
# the real `LedgerStorePort` adapter (a file on disk); `fake_ledger_store.py`
# beside this script is the fake (in memory), carrying the identical content
# assertion so that "both pass" is not "the fake asserts less".
#
# Two corpora, deliberately:
#   the GIVEN  (Scenario_RecordAfterDelivery) -- ENTERS the port. Passing
#              against both is the anchor-4 claim.
#   the SLICE  (Scenario_DeliveryPath)        -- does NOT enter the port. Before
#              HP-04 it could not run at all under any shipped mapping (CM-F5),
#              and its run must SAY that it carries no oracle for the port.
set -u
: "${PY:?set PY to the interpreter}"
: "${REPO:?set REPO to the repo root}"
export PYTHONDONTWRITEBYTECODE=1
HERE="$REPO/specs/tickets/HP-04/results/real_and_fake"
EX4="$REPO/examples/validation/ex4_pipeline_coherent"

cd "$EX4" || exit 1
TMP=$(mktemp -d)
OUT="$TMP/specs/wt"
mkdir -p "$OUT"

for module in Scenario_RecordAfterDelivery Scenario_DeliveryPath; do
  PYTHONPATH=$PWD $PY "$REPO/scripts/generate_cases_from_tlc_dump.py" \
    "specs/case_modules/$module.tla" "specs/case_modules/$module.cfg" \
    --out "$OUT" --package "${module}_cases" --view internal \
    --actions-metadata specs/program_model/actions.yml \
    --state-projector specs.program_model.tlc_projection:project_visible_state \
    --output-projector specs.program_model.tlc_projection:project_adapter_output \
    --dedupe projected >/dev/null 2>&1
  echo "generated ${module}_cases (exit $?)"
done
echo

run () {  # $1 = corpus package, $2 = mapping path, $3 = label
  echo "=== $3 ==="
  PYTHONPATH=$REPO:$PWD/generated:$HERE $PY "$REPO/scripts/run_generated_case_adapters.py" \
    "$OUT/spec-unit/$1" --mapping "$2" \
    --spec-dir specs/program_model --view internal --batch \
    --import-root . --import-root ./generated --import-root "$HERE" 2>&1 | tail -6
  echo "EXIT=${PIPESTATUS[0]}"
  echo
}

run Scenario_RecordAfterDelivery_cases specs/program_model/case_adapters.toml \
    "GIVEN corpus -> REAL adapter (FileLedgerStore, on disk)"
run Scenario_RecordAfterDelivery_cases "$HERE/case_adapters_fake.toml" \
    "GIVEN corpus -> FAKE adapter (InMemoryLedgerStore)"
run Scenario_DeliveryPath_cases specs/program_model/case_adapters.toml \
    "SLICE corpus -> REAL mapping (must run, and must say what it does NOT carry)"
run Scenario_DeliveryPath_cases "$HERE/case_adapters_fake.toml" \
    "SLICE corpus -> FAKE mapping"

echo "=== the fixture is untouched ==="
cd "$REPO" && git status --porcelain examples/validation/ex4_pipeline_coherent
echo "(empty above == clean)"
rm -rf "$TMP"
