import copy, dataclasses, importlib.util, sys, tempfile
from pathlib import Path

WT = Path("/Users/hayde/IdeaProjects/wt-57-mf032-case-execution-remaining")
TICKET = WT/"specs/tickets/MF-032/current"
sys.path.insert(0, str(TICKET))
CASESDIR = Path(sys.argv[1])
sys.path.insert(0, str(CASESDIR.parent))
import tlc_state_graph_cases.cases as C
pa_spec = importlib.util.spec_from_file_location("production_adapters", TICKET/"production_adapters.py")
pa = importlib.util.module_from_spec(pa_spec); sys.modules["production_adapters"]=pa; pa_spec.loader.exec_module(pa)

BY = C.CASES_BY_NAME
plan = [
    ("InstallLocalCliAdapter","case_0003_install_local_cli", lambda a: a.__setitem__("setup_phase", 3), "setup_phase 2->3"),
    ("ScaffoldWorkflowAdapter","case_0009_scaffold_workflow", lambda a: a.__setitem__("lastCommand","WRONG"), "lastCommand"),
    ("RecordBudgetsAdapter","case_0007_record_budgets", lambda a: a.__setitem__("setup_phase", 5), "setup_phase 4->5"),
    ("OpenTicketAdapter","case_0022_open_ticket", lambda a: dict(a["ticket_state"]).update() or a["ticket_state"].__setitem__(sorted(a["ticket_state"])[0], 2), "ticket_state value"),
]
for cls, cname, mut, negdesc in plan:
    adapter = getattr(pa, cls)()
    case = BY[cname]
    print("="*70)
    print(f"{cls}  <-  {cname}")
    print(f"  action={case.input.action}  before.setup_phase={dict(case.before)['setup_phase']}  before.ticket_state={dict(case.before).get('ticket_state')}")
    with tempfile.TemporaryDirectory() as d:
        res = adapter.run(case, work_dir=Path(d))
        comp = res["semantic_output"]["comparison"]
        print(f"  POSITIVE: conformant={comp['conformant']}")
        print(f"    CHECKED agreements ({len(comp['agreements'])}): {comp['agreements']}")
        print(f"    UNCHECKED ({len(comp['unchecked'])}): {comp['unchecked']}")
        print(f"    MISMATCH ({len(comp['disagreements'])}): {comp['disagreements']}")
    # negative control on the REAL case
    after = copy.deepcopy(dict(case.after)); mut(after)
    bad = dataclasses.replace(case, after=after)
    with tempfile.TemporaryDirectory() as d:
        try:
            adapter.run(bad, work_dir=Path(d))
            print(f"  NEGATIVE CONTROL ({negdesc}): *** DID NOT FAIL *** <-- BUG")
        except (AssertionError, pa.BeforeStateUnreachable) as e:
            print(f"  NEGATIVE CONTROL ({negdesc}): correctly REJECTED -> {type(e).__name__}: {str(e)[:140]}")
print("="*70)
