#!/usr/bin/env python3
"""A BUG ORACLE, not a kill table. Six independent implementations of one
FEATURE.md are run side by side on identical input sequences; wherever they
disagree, at most one of them can be right, and the disagreement is a candidate
defect to read against FEATURE.md by hand.

This CROSSES the architecture boundary on purpose and says so: the question it
answers is "does any tree have a bug", which is a question about the product,
not about detection. No number from this script is compared across arms.
"""
import itertools, json, random, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TREES = ["artifact_Z", "artifact_M", "artifact_N", "artifact_D", "artifact_E", "artifact_F"]

CHILD = r'''
import sys, json, importlib
from pathlib import Path
tree, work, plan_path = sys.argv[1:4]
sys.path.insert(0, tree)
module = importlib.import_module("quota_ledger")
plan = json.loads(Path(plan_path).read_text())
out = []
for si, script in enumerate(plan):
    quotas = script["quotas"]
    path = Path(work) / f"ledger-{si}.txt"
    trace = []
    try:
        book = module.QuotaLedger(dict(quotas), path)
    except Exception as e:
        out.append([["CONSTRUCT-RAISED", type(e).__name__]]); continue
    def obs():
        row = {}
        for t in quotas:
            try: row[f"avail:{t}"] = book.available(t)
            except Exception as e: row[f"avail:{t}"] = f"RAISE {type(e).__name__}"
            try: row[f"comm:{t}"] = book.committed(t)
            except Exception as e: row[f"comm:{t}"] = f"RAISE {type(e).__name__}"
            try: row[f"closed:{t}"] = book.is_closed(t)
            except Exception as e: row[f"closed:{t}"] = f"RAISE {type(e).__name__}"
        try: row["out"] = list(book.outstanding_ids())
        except Exception as e: row["out"] = f"RAISE {type(e).__name__}"
        try: row["led"] = list(book.ledger_lines())
        except Exception as e: row["led"] = f"RAISE {type(e).__name__}"
        return row
    for op, args in script["ops"]:
        try:
            r = getattr(book, op)(*args)
            reported = [r.status, getattr(r, "reason", None)]
            if op == "reserve":
                reported.append(getattr(r, "reservation_id", None))
        except Exception as e:
            reported = ["RAISED", type(e).__name__]
        trace.append([op, args, reported, obs()])
    out.append(trace)
print(json.dumps(out))
'''

def build_plans(seed, count):
    rng = random.Random(seed)
    plans = []
    for _ in range(count):
        quotas = {"acme": rng.randint(0, 8), "globex": rng.randint(0, 8)}
        ops = []
        for _ in range(30):
            op = rng.choice(["reserve", "reserve", "commit", "release", "close_tenant"])
            if op == "reserve":
                ops.append([op, [rng.choice(["acme", "globex", "nobody", "acme x"]),
                                 rng.choice([-1, 0, 1, 2, 3, 9, 2.5])]])
            elif op == "close_tenant":
                ops.append([op, [rng.choice(["acme", "globex", "nobody"])]])
            else:
                ops.append([op, [f"r{rng.randint(1, 12)}"]])
        plans.append({"quotas": quotas, "ops": ops})
    return plans

def main():
    plans = build_plans(20260809, int(sys.argv[1]) if len(sys.argv) > 1 else 300)
    results = {}
    with tempfile.TemporaryDirectory() as raw:
        plan_path = Path(raw) / "plan.json"
        plan_path.write_text(json.dumps(plans))
        child = Path(raw) / "child.py"
        child.write_text(CHILD)
        for tree in TREES:
            work = Path(raw) / tree
            work.mkdir()
            done = subprocess.run([sys.executable, str(child), str(HERE / "trees" / tree),
                                   str(work), str(plan_path)],
                                  capture_output=True, text=True)
            if done.returncode != 0:
                print(f"{tree} FAILED\n{done.stderr[-1500:]}"); return 1
            results[tree] = json.loads(done.stdout)
    report = {}
    for a, b in itertools.combinations(TREES, 2):
        diffs = []
        for si, (ta, tb) in enumerate(zip(results[a], results[b])):
            for oi, (ra, rb) in enumerate(zip(ta, tb)):
                if ra != rb:
                    diffs.append({"script": si, "op_index": oi, "quotas": plans[si]["quotas"],
                                  "op": ra[0], "args": ra[1],
                                  a: {"reported": ra[2], "observed": ra[3]},
                                  b: {"reported": rb[2], "observed": rb[3]}})
                    break
        report[f"{a} vs {b}"] = {"scripts_with_a_divergence": len(diffs), "first": diffs[:2]}
        print(f"{a:<12} vs {b:<12} divergent scripts: {len(diffs)}")
    (HERE / "out" / "crossdiff.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0

raise SystemExit(main())
