"""Attribution probe: are the 4 test_score_tools reds caused by _finding_ids()
returning an empty set now that the live ledger is gone?

No repository file is edited. score_tools is imported and _finding_ids is
monkeypatched to read the ARCHIVED ledger, which is byte-identical to the live
file at the parent commit. If the violation count falls to what CA-08 measured,
the close is the whole cause.
"""
import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path("/Users/hayde/IdeaProjects/wt-epic-cut-the-apparatus")
ST = ROOT / "examples/validation/scorecards/score_tools.py"
SCORECARDS = ROOT / "specs/results/scorecards"
ARCHIVE = ROOT / "specs/.history/cut-the-apparatus-epic/closed-snapshot/deferred_findings.yaml"

spec = importlib.util.spec_from_file_location("st_probe", ST)
st = importlib.util.module_from_spec(spec)
sys.modules["st_probe"] = st
spec.loader.exec_module(st)

print("=== A. as the suite runs it (live ledger absent) ===")
print("_finding_ids() ->", len(st._finding_ids()), "ids")
code_a = st.main(["audit", "--root", str(SCORECARDS), "--quiet-ok"])
print("exit", code_a)

ids = set(re.findall(r"^\s*-\s+id:\s*\"?([A-Za-z0-9_.-]+)\"?", ARCHIVE.read_text(), re.M))
st._finding_ids = lambda: ids

print()
print("=== B. same tree, ledger resolved to the archive ===")
print("_finding_ids() ->", len(ids), "ids")
code_b = st.main(["audit", "--root", str(SCORECARDS), "--quiet-ok"])
print("exit", code_b)
