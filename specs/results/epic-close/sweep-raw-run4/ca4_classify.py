#!/usr/bin/env python3
"""Coverage-audit run 4: mechanical Sweep-1 classifier + Sweep-2/3 area partitioner.

Rules are stated in the report (section 2). This script IS the recorded rule
application: a reader running it against sweep-raw-run4/ reproduces every row.
"""
from __future__ import annotations

import re
from pathlib import Path

RAW = Path("specs/results/epic-close/sweep-raw-run4")
SURFACE = [l.strip() for l in (RAW / "ca4-surface-all.txt").read_text().splitlines() if l.strip()]

# --- Sweep 1 rules (priority order; plan lines are ticket_plan.yaml at 400c51a) ---

LIFECYCLE = {
    # shipped CLI lifecycle closure (:524-525) via dispatch imports tla_spec_dev.py:62-203,
    # runner spawn :313-339/:358, adapter binding imports; PLUS the shipped experimental
    # commands the ESC-6 correction keeps modeled (:538-542): corpus/effect/kill files.
    "scripts/tla_spec_dev.py": ("represented", "all 14 @command actions", ":583, :524-525",
        "dispatch :62-203 -> TlaSpecDevCli.tla:215-599; port map manifest:209-231. Runner spawn :313-339/:358 now declared runner_process (manifest:187-189/:230, R3-3a FIXED); flag variants out-of-model per :547-551/:599 (recorded granularity limitation) [READ]"),
    "scripts/onboard_program_model.py": ("represented", "ScaffoldProject", ":524-525 (scaffold; dispatch :64)",
        "ScaffoldProject TlaSpecDevCli.tla:248; spec_tree manifest:212 [grep-level + run-3 READ carried]"),
    "scripts/new_ticket_workflow.py": ("represented", "ScaffoldWorkflow, OpenTicket", ":524-525 (scaffold workflow/open; dispatch :102,:124)",
        "ScaffoldWorkflow :287, OpenTicket :305; spec_tree manifest:222-223; toml:25-30 [grep-level]"),
    "scripts/budgets.py": ("partial", "RecordBudgets", ":524-525 (dispatch :89,:115)",
        "RecordBudgets TlaSpecDevCli.tla:269; manifest:221 (deliberately-empty effects row, DF-2 FIXED). UNCOVERED: load/refusal semantics -- out-of-model per :544-551/:599 (recorded granularity limitation) [grep-level]"),
    "scripts/analyze_complexity.py": ("represented", "AnalyzeComplexity", ":584, :2047 (CD-01), :2195 (CD-03)",
        "AnalyzeComplexity TlaSpecDevCli.tla:371-401; evidence_report manifest:226 (writer :1622-1623); toml:37-38; advisory internals out-of-model per :530-533 [READ regions]"),
    "scripts/fitness_functions.py": ("unrepresented", "none", ":584 named; :530-533 out-of-model",
        "the whole file is the fitness-function evaluation :530-533 declares out-of-model as transcription (run-2 G1 reclassified; unchanged) [READ header run 3]"),
    "scripts/complexity_ledger.py": ("partial", "CloseTicket", ":591, :2291 (CD-09)",
        "ledger write on close under CloseTicket spec_tree manifest:231. UNCOVERED: verdict/refusal machinery -- out-of-model per ESC-1 ruling :551-554 (validation harness; granularity limitation :599) [READ via spec_evolution]"),
    "scripts/extract_spec_manifest.py": ("partial", "none directly", ":524-525 (dispatch :203; analyze; runner :30)",
        "manifest parsing inside every modeled command; parse refusals out-of-model per :544-551/:599 [grep-level]"),
    "scripts/spec_evolution.py": ("represented", "CloseTicket", ":524-525 (close; dispatch :178)",
        "CloseTicket TlaSpecDevCli.tla:584-599. Deletes :154,:385,:477 now declared spec_tree_delete manifest:198-200/:231 (R3-2 FIXED); git spawn :99 declared git_metadata :206-208/:231 (R3-3b FIXED); ledger + validation refusals out-of-model :544-554/:599; timestamps out-of-model :559-560 [READ regions]"),
    "scripts/skill_feedback.py": ("partial", "CloseTicket", ":524-525 (close; spec_evolution.py:19)",
        "feedback file under spec-root results matches spec_tree. UNCOVERED: clock provenance :86 -- out-of-model per ESC-7 ruling :559-560 [READ head run 3]"),
    "scripts/spec_paths.py": ("partial", "none", ":524-525 (closure via runner :31)",
        "path resolution inside modeled commands; no distinct effect surface [INFERRED]"),
    "scripts/testgraph_channels.py": ("unrepresented", "none", ":524-525 (closure via runner :32)",
        "channel enforcement for external test-graph bindings; enforced behavior is test-graph integration surface per :521-522 [INFERRED]"),
    "scripts/run_generated_case_adapters.py": ("represented", "RunSpecUnitTests, RunEffectConformance", ":524-525 (run; spawned by tla_spec_dev.py:313-339)",
        "RunSpecUnitTests TlaSpecDevCli.tla:529-577; spawn now declared runner_process manifest:187-189/:230 (R3-3a FIXED); env re-exec :971,:990-998 out-of-model per :531 [grep-level + verified citations]"),
    "scripts/corpus_diagnostics.py": ("partial", "AnalyzeCorpus", ":538-542 (stays modeled), :524-525 (dispatch :148-151)",
        "AnalyzeCorpus TlaSpecDevCli.tla:403-437; toml:40-41. UNCOVERED: AnalyzeCorpus declares evidence_report (manifest:227) but the command has no writer and no --out (run():902-935 prints only) -- dead declared port = gap R4-3 [READ]"),
    "scripts/effect_conformance_report.py": ("partial", "RunEffectConformance", ":538-542, :557-558 (ESC-5/6 rulings)",
        "RunEffectConformance TlaSpecDevCli.tla:440-489; evidence_report exercised (report.write :107). UNCOVERED: work-dir writes :149,:163 land under **/specs/** with spec_tree NOT declared for the action (manifest:228 = [evidence_report] only) = gap R4-2 [READ]"),
    "scripts/effect_conformance.py": ("partial", "RunEffectConformance; effect_conformance' in RunSpecUnitTests", ":557-558 (ESC-5 ruling), :538-542",
        "sandbox behind RunEffectConformance :440 and RunSpecUnitTests :559; manifest:228. Sandbox root mkdir :619/:656 joins gap R4-2 on the effect-conformance path (covered by RunSpecUnitTests spec_tree on the runner path) [READ regions]"),
    "scripts/kill_test.py": ("partial", "RunKillTest", ":538-542 (stays modeled)",
        "RunKillTest TlaSpecDevCli.tla:493-525; manifest:229. UNCOVERED: mutation seed/restore write_text :548/:551 overwrites production source (scripts/**) matching NO declared port = gap R4-1; corpus spawn :609 matches test_process only for pytest-shaped commands [READ]"),
    "scripts/run_kill_test.py": ("partial", "RunKillTest", ":538-542, :524-525 (dispatch :171-176)",
        "run() :130 drives kill_test.seeded per mutant; report.write :225 -> evidence_report. UNCOVERED: shares gap R4-1 (spawn :198 of user-supplied corpus command; mutation writes) [READ]"),
    "spec_double_compiler/__init__.py": ("partial", "RunSpecUnitTests", ":524-525 (case runtime)",
        "runtime consumed by generated cases/adapters (manifest:130-132) [INFERRED]"),
    "spec_double_compiler/runtime.py": ("partial", "RunSpecUnitTests", ":524-525 (case runtime)",
        "double-execution engine behind RunSpecUnitTests batches [INFERRED]"),
    "specs/current/adapter_case_runtime.py": ("partial", "RunSpecUnitTests", ":2290 (CD-09), :2368 (CD-10)",
        "harness shim; :36 spawn drives the CLI under test [grep-level]"),
    "specs/current/production_adapters.py": ("represented", "all 14 bound actions", ":2290 (CD-09), :2368 (CD-10)",
        "bindings case_adapters.toml:13-53 <-> 14 @command actions (:590 wording now says '@command action set', ESC-8 FIXED); proven both ways by test_tla_spec_dev_binding_reconciliation.py [grep-level]"),
    "specs/program_model/adapter_case_runtime.py": ("partial", "RunSpecUnitTests", ":594 sibling (imported by production_adapters.py:23)",
        "identical role to the specs/current copy; diff-verified identical this run [INFERRED]"),
    "specs/program_model/production_adapters.py": ("represented", "all 14 bound actions", ":594 (adapter_boundaries)",
        "reconciled binding set; diff-verified identical to specs/current copy this run [grep-level]"),
}

# Wrapper/plumbing rows now PLACED by the ESC-3 ruling :554-557 (out-of-model).
PLUMBING = {
    "scripts/close_spec_workflow.py": "close wrapper; rmtree :49 not performed by a modeled action, no port owed per :556-557",
    "scripts/close_ticket.py": "close wrapper",
    "scripts/close_tickets.py": "batch close (promotion_rule :565 forbids ticket agents running it); unlink :127 / rmtree :232 not performed by a modeled action",
    "scripts/close-spec-workflow.py": "compat shim",
    "scripts/close-ticket.py": "compat shim",
    "scripts/start_ticket.py": "open wrapper",
    "scripts/scaffold_spec.py": "tutorial scaffold wrapper",
    "scripts/scaffold_spec_workflow.py": "workflow scaffold wrapper",
    "scripts/run_tlc.sh": "TLC runner wrapper",
    "specs/desired_program_model/production_adapters.py": "desired-tree adapter copy",
    "specs/desired_program_model/adapter_case_runtime.py": "desired-tree adapter copy",
}

EXPERIMENTAL_GENERATE = {
    "scripts/generate_cases_from_tlc_dump.py": ":585, :598 (`generate` unmodeled -- recorded limitation), :542",
    "scripts/export_testgraph_cases.py": ":521-522 (test-graph integration); also the generate pipeline per :598",
}


def classify(path: str):
    if path in LIFECYCLE:
        v, act, line, ev = LIFECYCLE[path]
        return ("in", line, act, v, ev)
    if path in PLUMBING:
        return ("out", ":554-557 (ESC-3 ruling: wrapper scripts, run_tlc.sh, desired-tree adapter copies are toolchain plumbing, out-of-model)",
                "-", "unrepresented", PLUMBING[path] + "; placed by the run-3 escalation ruling [not read]")
    if path in EXPERIMENTAL_GENERATE:
        return ("out", EXPERIMENTAL_GENERATE[path], "-", "unrepresented",
                "generate/export surface; default polarity, not read")
    parts = path.split("/")
    base = parts[-1]
    if "graph-reports" in path or path.startswith("test_graph/") or "/test_graph/" in path:
        return ("out", ":521-522 (test graph nodes / integration harnesses)", "-", "unrepresented",
                "test-graph node/harness surface; default polarity, not read")
    if path.startswith("tests/"):
        note = "pytest job; default polarity, not read"
        if base in ("test_analyze_complexity.py", "test_fitness_functions.py", "test_complexity_ledger.py"):
            note = "pytest job; in scope as change surface only (:2048/:2196/:2291); not read"
        if base == "test_kill_test.py":
            note = "pytest job; modified by CD-10 under objective text :2361-2362 though not an implementation_scope path; not read"
        return ("out", ":521 (pytest jobs)", "-", "unrepresented", note)
    if "/tests/" in path and base.startswith(("test_", "conftest")):
        return ("out", ":521 (pytest jobs)", "-", "unrepresented", "pytest job; default polarity, not read")
    if path.startswith("examples/") and ("validation" in parts[1] or base.startswith("validate") or base.startswith("run_")):
        if base in ("run_distributed_history_validation.py", "validate_split_desired_workflow.py"):
            return ("out", ":521-522 (validation scripts)", "-", "unrepresented", "validation entry script; default polarity, not read")
    if path.startswith("specs/tickets/"):
        return ("out", ":524-525 (totality: archived ticket snapshot outside the shipped CLI lifecycle closure)", "-",
                "unrepresented", "archived ticket-tree copy; default polarity, not read")
    return ("out", ":524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2)", "-",
            "unrepresented", "outside the shipped CLI lifecycle; default polarity, not read")


# --- emit sweep-1 table ---
rows = []
counts = {"in": 0, "out": 0}
verdicts = {"represented": 0, "partial": 0, "unrepresented": 0}
for i, p in enumerate(sorted(SURFACE), 1):
    scope, line, act, verdict, ev = classify(p)
    counts[scope] += 1
    verdicts[verdict] += 1
    rows.append(f"| {i} | `{p}` | {scope} | {line} | {act} | {verdict} | {ev} |")

out = Path(RAW / "sweep1_table.md")
out.write_text("\n".join(rows) + "\n")
print(f"rows={len(rows)} in={counts['in']} out={counts['out']} verdicts={verdicts}")

# --- area partition for sweeps 2/3 ---
LIFE_SET = set(LIFECYCLE) - {
    "spec_double_compiler/__init__.py", "spec_double_compiler/runtime.py",
    "specs/current/adapter_case_runtime.py", "specs/current/production_adapters.py",
    "specs/program_model/adapter_case_runtime.py", "specs/program_model/production_adapters.py",
}

def area(path: str) -> str:
    base = path.split("/")[-1]
    if base in ("production_adapters.py", "adapter_case_runtime.py"):
        return "adapters"
    if "graph-reports" in path or path.startswith("test_graph/") or "/test_graph/" in path:
        return "testgraph"
    if path.startswith("tests/"):
        return "repo-tests"
    if "/tests/" in path:
        return "spec-tests"
    if path.startswith("spec_double_compiler/"):
        return "prod-runtime"
    if path.startswith("examples/"):
        return "examples"
    if path.startswith("skill-scripts/"):
        return "skill-scripts"
    if path in LIFE_SET:
        return "lifecycle"
    if path.startswith("scripts/"):
        return "other-scripts"
    return "specs-other"

for cat in ["filesystem", "subprocess", "network", "environment", "clock",
            "randomness", "persistent_store", "behaviors_error", "behaviors_retry",
            "behaviors_timeout", "behaviors_fallback", "behaviors_concurrency",
            "behaviors_config"]:
    f = RAW / f"{cat}.txt"
    per = {}
    total = 0
    for l in f.read_text().splitlines():
        if not l.strip():
            continue
        total += 1
        per.setdefault(area(l.split(":", 1)[0]), 0)
        per[area(l.split(":", 1)[0])] += 1
    print(cat, total, dict(sorted(per.items(), key=lambda kv: -kv[1])))

# --- destructive sites ---
pat = re.compile(r"shutil\.rmtree|\.unlink\(|os\.remove\(")
dest = [l for l in (RAW / "filesystem.txt").read_text().splitlines() if pat.search(l)]
(Path(RAW / "destructive_sites.txt")).write_text("\n".join(dest) + "\n")
print("destructive-primitive lines:", len(dest))
for l in dest:
    print("  ", l[:150])
