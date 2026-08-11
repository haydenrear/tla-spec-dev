"""CL-02. Re-price EVERY historical removal that has a published before-table,
with the corrected instrument, and print the total number of priced results.

    python3 specs/results/scorecards/close-the-loop/GOAL-price-means-something/repriced_history.py

It IMPORTS the shipped `price_removal.py` and swaps DATA only, so what is
reported is the instrument that ships rather than a re-typed copy of it
(`PA-04-DF-02`). NOT A GATE: nothing invokes it, it asserts nothing and it
returns 0 whatever it finds. Its output is `repriced-history-sweep.txt`.

A NON-ZERO TOTAL IS THE INFORMATIVE OUTCOME. At `feature/CL-02` it prints 0."""
import importlib.util, json, sys, tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

def mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

P = mod(ROOT / "examples/validation/gap_mutants/price_removal.py", "pr")
manifest = tomllib.loads((ROOT / "examples/validation/removal_census/removals.toml").read_text())
removals = {r["id"]: r for r in manifest["removal"]}

SM = "specs/results/scorecards/subtract-to-measure/before-state/gap-mutants-before.json"
RM3 = "specs/results/scorecards/portable-substrate/GOAL-dead-weight-gone/rm03-gap-mutants-before.json"
RD2 = "specs/results/scorecards/reading-discipline/GOAL-apparatus-priced/rd02-gap-mutant-before.json"
RF = "specs/results/scorecards/portable-substrate/GOAL-removal-can-be-priced/RM-01/residual-before-bf0fb29p.json"

# (removal id or label, before-table, head, explicit fault list or None)
PAIRS = [
    ("ports-binding-machinery", SM, "0342a3a", None),
    ("hardcoded-enumeration-literal", SM, "bf0fb29", None),
    ("dead-port-binding-report-detector", RD2, "bfd04af", None),
    ("card-dimensions-to-notes", RM3, "1e6f691", None),
    ("gap-mutant-catalogue-and-runner", RM3, "6298eee", None),
    # RM-01's residual pair -- the known positive, priced against SM-03's cut.
    ("hardcoded-enumeration-literal", RF, "bf0fb29", "RM-01 residual pair"),
]

print("=" * 100)
print("RE-PRICED HISTORY -- every removal with a before-table, corrected instrument")
print("=" * 100)
total_priced = 0
for rid, before_path, head, label in PAIRS:
    r = removals[rid]
    before = json.loads((ROOT / before_path).read_text())
    deleted = r.get("deletes_detectors", [])
    subjects = sorted(before["per_mutant"])
    rows = [P.entail(before, m, deleted, head) for m in subjects]
    name = f"{rid}  ({r['ticket']}, head {head})" + (f"  [{label}]" if label else "")
    print(f"\n--- {name}")
    print(f"    before-table: {before_path}")
    for row in rows:
        v = row["verdict"]
        mark = "  <<< PRICED RESULT" if P.is_priced_result(row) else ""
        print(f"    {v:<18} {row['mutant'][:70]}{mark}")
    priced = [x for x in rows if P.is_priced_result(x)]
    ctl = [x for x in rows if x["verdict"] == P.CONTROL_EXCLUDED]
    total_priced += len(priced)
    print(f"    => {len(priced)} priced of {len(rows)-len(ctl)} subject(s), "
          f"{len(ctl)} control(s) excluded")

print("\n" + "=" * 100)
print(f"TOTAL PRICED RESULTS ACROSS RE-PRICED HISTORY: {total_priced}")
print("=" * 100)

print("\n\n=== audit(): the measured before/after record, 10 sealed rows ===")
report = P.audit(manifest)
print(P.render_audit(report))
print("\npriced rows:", [r["mutant"] for r in report["rows"] if r["measured"] == P.PRICED])
print("this_instrument verdicts:", sorted({r["this_instrument"] for r in report["rows"]}))

print("\n\n=== RM-01's known positive, measured (price, not entail) ===")
rf_b = json.loads((ROOT / RF).read_text())
rf_a = json.loads((ROOT / "specs/results/scorecards/portable-substrate/GOAL-removal-can-be-priced/RM-01/residual-after-bf0fb29.json").read_text())
for m in sorted(rf_b["per_mutant"]):
    row = P.price(rf_b, rf_a, m, "bf0fb29", [])
    print(f"    {row['verdict']:<18} {m[:70]}")
