#!/usr/bin/env python3
"""Coverage-audit close-2 (workflow complexity-descriptor-main-readiness):
mechanical Sweep-1 classifier + Sweep-2/3 area partitioner.

Rules are stated in the report (section 2). This script IS the recorded rule
application: a reader running it against sweep-raw-close2/ reproduces every row.

Plan-line citation scheme (stated in the report section 0):
  CP:NN = specs/desired_program_model/ticket_plan.yaml line NN (schedule_revision 2, at db78854/e2fdfa7)
  PS:NN = specs/.history/complexity-descriptor-epic/closed-snapshot/snapshots/desired_program_model/ticket_plan.yaml
          line NN (the predecessor workflow's sealed plan carrying the recorded
          owner rulings; incorporated by CP header lines 6-13 and CP:80, and by
          the dispatching instruction's do-not-relitigate direction).
"""
from __future__ import annotations

import re
from pathlib import Path

RAW = Path("specs/results/finalization/sweep-raw-close2")
SURFACE = [l.strip() for l in (RAW / "cac2-surface-all.txt").read_text().splitlines() if l.strip()]

# --- Sweep 1 rules (priority order) ---

LIFECYCLE = {
    "scripts/tla_spec_dev.py": ("represented", "all 14 @command actions", "CP:64, PS:524-525",
        "dispatch -> TlaSpecDevCli.tla:222-598 @commands; port map manifest:190-237. CHANGED since 5f84937 [READ diff]: runner spawn gains --fuzz-runs/--seed/--fuzz-iteration flags (default 1/0 = prior behavior; per-flag variants out-of-model PS:547-551; spawn still matches runner_process :140-142); CD-04 corpus help text reworded (wording only); scaffold epilog names providers.py/effect_provider_usage.yaml (text only). Zero new effect primitives in diff (grep)"),
    "scripts/onboard_program_model.py": ("represented", "ScaffoldProject", "PS:524-525 (scaffold; dispatch)",
        "ScaffoldProject TlaSpecDevCli.tla:255; spec_tree manifest:193. CHANGED [READ diff]: e7fcd09 scaffolded spec-unit test invokes runner by absolute path + --spec-dir; scaffold-content change under the same spec_tree writes; zero new effect primitives (grep)"),
    "scripts/new_ticket_workflow.py": ("represented", "ScaffoldWorkflow, OpenTicket", "PS:524-525 (scaffold workflow/open), CP:420",
        "ScaffoldWorkflow :295, OpenTicket :313; spec_tree manifest:203-204. CHANGED [READ diff]: CD-07 advisory wording (VAL-04); MR-DF-01/e7fcd09 semantic-tail carry into scaffolded manifests; same spec_tree writes, zero new effect primitives (grep)"),
    "scripts/budgets.py": ("partial", "RecordBudgets", "PS:524-525, CP:422",
        "RecordBudgets TlaSpecDevCli.tla:276; manifest:202 (deliberately-empty row). UNCOVERED: load/refusal semantics -- out-of-model per PS:544-551/PS:599 (recorded granularity limitation). CHANGED [READ diff]: CD-07 retired fuzzing-era keys (VAL-02) + 497ab99 docstring; zero new effect primitives (grep)"),
    "scripts/analyze_complexity.py": ("represented", "AnalyzeComplexity", "CP:66, CP:200 (CD-05), CP:339 (CD-06), CP:423 (CD-07), PS:524-525",
        "AnalyzeComplexity TlaSpecDevCli.tla:379-393 (verdict-level: complexity_gate' in {pass,fail}); evidence_report manifest:207. CHANGED [READ diff]: CD-05 domain resolution, CD-06 R/W attribution, CD-07 sentinel wording -- all inside the advisory scan whose internals are out-of-model per PS:530-533; verdict surface and --out writer unchanged; zero new effect primitives (grep)"),
    "scripts/fitness_functions.py": ("unrepresented", "none", "CP:67 named; PS:530-533 out-of-model",
        "the whole file is the fitness-function evaluation PS:530-533 declares out-of-model as transcription. CHANGED [READ diff]: CD-07 CONFIG ERROR path added then 497ab99 removed it (manifest rules evaluate identically with or without PyYAML -- CP:80 finalization amendment); zero new effect primitives (grep)"),
    "scripts/complexity_ledger.py": ("partial", "CloseTicket", "PS:524-525 (close)",
        "ledger write on close under CloseTicket spec_tree manifest:237. UNCOVERED: verdict/refusal machinery -- out-of-model per ESC-1 ruling PS:551-554 + PS:599. UNCHANGED since 5f84937 (name-status) [carried run-4 READ]"),
    "scripts/extract_spec_manifest.py": ("partial", "none directly", "PS:524-525 (parsing inside every modeled command)",
        "manifest parsing inside every modeled command; parse refusals out-of-model per PS:544-551/PS:599. CHANGED [READ diff]: 37c6c65/497ab99 constrained-parser extensions (float literals, single-line inline mappings, nesting rejected) -- pure parsing, zero new effect primitives (grep)"),
    "scripts/spec_evolution.py": ("represented", "CloseTicket", "PS:524-525 (close)",
        "CloseTicket TlaSpecDevCli.tla:598; deletes :154/:385/:477 declared spec_tree_delete manifest:151-153/:237; git spawn :99 declared git_metadata :159-161/:237. UNCHANGED since 5f84937 [carried run-4/5 READ]"),
    "scripts/skill_feedback.py": ("partial", "CloseTicket", "PS:524-525 (close)",
        "feedback file under spec-root results matches spec_tree. UNCOVERED: clock provenance -- out-of-model per ESC-7 ruling PS:559-560. UNCHANGED [carried]"),
    "scripts/spec_paths.py": ("partial", "none", "PS:524-525 (closure)",
        "path resolution inside modeled commands; no distinct effect surface. UNCHANGED [carried, INFERRED]"),
    "scripts/testgraph_channels.py": ("unrepresented", "none", "PS:524-525 (closure via runner), PS:521-522",
        "channel enforcement for external test-graph bindings; enforced behavior is test-graph integration surface per PS:521-522/CP:49. UNCHANGED [carried, INFERRED]"),
    "scripts/run_generated_case_adapters.py": ("represented", "RunSpecUnitTests, RunEffectConformance", "PS:524-525 (run; spawned child), CP:80",
        "RunSpecUnitTests TlaSpecDevCli.tla:541; spawn declared runner_process manifest:140-142/:236. CHANGED [READ diff, +1245 lines]: effect-provider machinery (EP-01..06 + 497ab99/e7fcd09) -- SHIPPED validation harness, out-of-model per CP:80; child-side effects behind the declared spawn (MF-027 standing); diff's only new primitives: provider work-dir mkdir :1381 under the existing work tree, PYTHONPATH env read :1138 for replay commands (grep)"),
    "scripts/corpus_diagnostics.py": ("represented", "AnalyzeCorpus", "CP:65, CP:129 (CD-04), PS:538-542",
        "AnalyzeCorpus TlaSpecDevCli.tla:415-426 (corpus_gate' in {pass,fail}); manifest:216 deliberately-empty row (R4-3 closed, print-only verified run 5). CHANGED [READ diff]: CD-04 REDESIGN QUESTION output replaces the suggested move; recommendation field removed from classify_cause; still print-only, exit codes unchanged, zero new effect primitives (grep). enforce_case_cap :826 retains 'Fix the diagram' on the generate/export path -- matches the model's own :420/:588 result strings"),
    "scripts/effect_conformance_report.py": ("represented", "RunEffectConformance", "PS:538-542, PS:557-558",
        "RunEffectConformance TlaSpecDevCli.tla:449-453; evidence_report + spec_tree declared manifest:228 (R4-2 closed, verified run 5). UNCHANGED since 5f84937 [carried]"),
    "scripts/effect_conformance.py": ("represented", "RunEffectConformance; effect_conformance' in RunSpecUnitTests", "PS:557-558, PS:538-542",
        "sandbox behind RunEffectConformance and RunSpecUnitTests; declared rows manifest:228/:236. UNCHANGED [carried]"),
    "scripts/kill_test.py": ("represented", "RunKillTest", "PS:538-542",
        "RunKillTest TlaSpecDevCli.tla:503; mutation_write :176-178 + corpus_process :187-189 declared on row :235 (R4-1 closed, verified run 5). UNCHANGED [carried]. Standing inventory: corpus_process declares the spawn, not the child (MF-027)"),
    "scripts/run_kill_test.py": ("represented", "RunKillTest", "PS:538-542",
        "drives kill_test per mutant; evidence_report write declared. UNCHANGED [carried]"),
    "spec_double_compiler/__init__.py": ("partial", "RunSpecUnitTests", "PS:524-525 (case runtime), CP:80",
        "runtime consumed by generated cases/adapters behind the declared runner spawn; internals out-of-model per CP:80. UNCHANGED [carried, INFERRED]"),
    "spec_double_compiler/runtime.py": ("partial", "RunSpecUnitTests", "PS:524-525 (case runtime), CP:80",
        "double-execution engine behind RunSpecUnitTests batches. CHANGED [READ diff]: EP-01 EffectProviderContext/EffectProvider protocol + immutable effects mapping -- pure datatypes, no I/O primitives; out-of-model per CP:80"),
    "spec_double_compiler/effects.py": ("partial", "RunSpecUnitTests", "CP:80 (spec_double_compiler/* = shipped validation harness)",
        "NEW file [READ in full, 25 lines]: deterministic seed derivation (sha256 over json framing) -- pure computation, no I/O, no clock, no OS randomness; provider-runtime support, out-of-model per CP:80"),
    "specs/current/adapter_case_runtime.py": ("partial", "RunSpecUnitTests", "CP:77 (adapter boundary; reconciled copy)",
        "harness shim; spawn drives the CLI under test. Diff-verified identical across current/program_model this run [carried]"),
    "specs/current/production_adapters.py": ("represented", "all 14 bound actions", "CP:77 (adapter boundary; reconciled copy)",
        "bindings case_adapters.toml <-> 14 @command actions. CHANGED [READ diff]: CD-04 AnalyzeCorpusAdapter assertion flipped from recommendation-labeled to asks_redesign_question_never_prescribes -- adapter tracks the reworded output; conformance green post-merge"),
    "specs/program_model/adapter_case_runtime.py": ("partial", "RunSpecUnitTests", "CP:77 (adapter_boundaries)",
        "identical role to the specs/current copy; diff-verified identical this run [carried]"),
    "specs/program_model/production_adapters.py": ("represented", "all 14 bound actions", "CP:77 (adapter_boundaries)",
        "reconciled binding set; diff-verified identical to specs/current copy this run [READ diff = same CD-04 change]"),
}

# Wrapper/plumbing rows PLACED by the ESC-3 ruling PS:554-557 (out-of-model).
PLUMBING = {
    "scripts/close_spec_workflow.py": "close wrapper; deletes not performed by a modeled action",
    "scripts/close_ticket.py": "close wrapper",
    "scripts/close_tickets.py": "batch close (promotion_rule CP:52 forbids ticket agents running it)",
    "scripts/close-spec-workflow.py": "compat shim",
    "scripts/close-ticket.py": "compat shim",
    "scripts/start_ticket.py": "open wrapper",
    "scripts/scaffold_spec.py": "tutorial scaffold wrapper; CHANGED (provider scaffold lines) [READ diff scan: zero new effect primitives]",
    "scripts/scaffold_spec_workflow.py": "workflow scaffold wrapper",
    "scripts/run_tlc.sh": "TLC runner wrapper; CHANGED [READ diff in full]: CD-07 VAL-03 -metadir to mktemp -d + trap rm -rf (destructive site, per-site row in Sweep 2; targets its own temp dir, not the spec tree); named CP:424 as CD-07 change surface, still out-of-model per PS:554-557",
    "specs/desired_program_model/production_adapters.py": "desired-tree adapter copy (diff-identical to current, verified this run)",
    "specs/desired_program_model/adapter_case_runtime.py": "desired-tree adapter copy, NEW in the desired tree this workflow (diff-identical to current, verified this run)",
}

EXPERIMENTAL_GENERATE = {
    "scripts/generate_cases_from_tlc_dump.py": "PS:542/PS:598 (`generate` unmodeled -- recorded limitation), CP:53; CHANGED (e7fcd09 zero-case warning) [READ diff scan: zero new effect primitives]",
    "scripts/export_testgraph_cases.py": "PS:521-522 (test-graph integration) + PS:598; CD-08 change surface CP:273 (manifest resolution / loud failure) [READ diff scan: zero new effect primitives]",
    "scripts/generate_python.py": "PS:542/PS:598 generate pipeline codegen; CHANGED (ports.py.j2 provider hook) [diff scan only]",
    "scripts/generate_docs.py": "PS:542/PS:598 generate pipeline codegen",
    "scripts/infer_action_params.py": "PS:542/PS:598 generate pipeline support",
}


def classify(path: str):
    if path in LIFECYCLE:
        v, act, line, ev = LIFECYCLE[path]
        return ("in", line, act, v, ev)
    if path in PLUMBING:
        return ("out", "PS:554-557 (ESC-3 ruling: wrapper scripts, run_tlc.sh, desired-tree adapter copies are toolchain plumbing, out-of-model)",
                "-", "unrepresented", PLUMBING[path])
    if path in EXPERIMENTAL_GENERATE:
        return ("out", EXPERIMENTAL_GENERATE[path], "-", "unrepresented",
                "generate/export surface; default polarity")
    parts = path.split("/")
    base = parts[-1]
    if path.startswith("examples/effect_providers/"):
        return ("out", "CP:80 (examples/effect_providers/* are EXPERIMENTAL validation fixtures carrying 12 recorded, unwaived model-completeness gaps; promotion-blocked, never enter specs/program_model)",
                "-", "unrepresented", "effect-provider fixture; default polarity, not read")
    if "graph-reports" in path or path.startswith("test_graph/") or "/test_graph/" in path:
        return ("out", "CP:49 first sentence (test graph nodes) / PS:521-522", "-", "unrepresented",
                "test-graph node/harness surface; default polarity, not read")
    if path.startswith("tests/"):
        note = "pytest job; default polarity, not read"
        if base.startswith("test_effect_provider"):
            note = "pytest job; provider-harness suite per CP:80; not read"
        return ("out", "CP:49 (pytest jobs)", "-", "unrepresented", note)
    if "/tests/" in path and (base.startswith("test_") or base == "conftest.py"):
        return ("out", "CP:49 (pytest jobs)", "-", "unrepresented", "pytest job; default polarity, not read")
    if path.startswith("examples/validation/") or base in ("run_distributed_history_validation.py", "validate_split_desired_workflow.py"):
        return ("out", "CP:49 (validation scripts) / PS:521-522", "-", "unrepresented",
                "validation harness/evidence surface; default polarity, not read")
    if path.startswith("examples/distributed_history/"):
        return ("out", "PS:524-525 (totality: outside the shipped CLI lifecycle closure); product example named CP:69 with BEHAVIORAL acceptance CP:271-272/CP:75 (CD-08), not modeled surface",
                "-", "unrepresented", "shipped example fixture; default polarity, not read (CD-08 end-to-end evidence is the behavioral gate)")
    if path.startswith("specs/tickets/"):
        return ("out", "PS:524-525 (totality: archived ticket snapshot outside the shipped CLI lifecycle closure)", "-",
                "unrepresented", "archived ticket-tree copy; default polarity, not read")
    if path.startswith("specs/results/"):
        return ("out", "CP:49 (validation scripts) + PS:524-525 (audit tooling; run-5 row-359 precedent)", "-",
                "unrepresented", "coverage-audit tooling/raws; default polarity")
    if path == "templates/python/ports.py.j2":
        return ("out", "CP:80 (templates/python/ports.py.j2 = shipped validation harness/toolchain plumbing, out-of-model)",
                "-", "unrepresented", "provider-aware port template; CHANGED [diff scan]; default polarity")
    if path.startswith("templates/"):
        return ("out", "PS:542/PS:598 (generate pipeline unmodeled -- recorded limitation) + PS:524-525", "-",
                "unrepresented", "codegen template consumed by the generate pipeline; default polarity, not read")
    return ("out", "PS:524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2)", "-",
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
    "spec_double_compiler/effects.py",
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
    if path.startswith("examples/effect_providers/"):
        return "effect-providers"
    if path.startswith("examples/validation/"):
        return "validation-evidence"
    if path.startswith("examples/"):
        return "examples-other"
    if path.startswith("skill-scripts/"):
        return "skill-scripts"
    if path.startswith("templates/"):
        return "templates"
    if path.startswith("specs/results/"):
        return "audit-tooling"
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
        a = area(l.split(":", 1)[0])
        per[a] = per.get(a, 0) + 1
    print(cat, total, dict(sorted(per.items(), key=lambda kv: -kv[1])))

# --- destructive sites (always per-site; scanned over the FULL surface, not
# --- the category raws, because the sh temp-dir sites use mktemp/rm -rf which
# --- the category patterns do not carry) ---
pat = re.compile(r"shutil\.rmtree|\.rmtree\(|\.unlink\(|os\.remove\(|rm -rf|deleteRecursively|Files\.delete|mktemp")
dest = []
for p in SURFACE:
    try:
        text = Path(p).read_text(errors="replace")
    except OSError:
        continue
    for n, line in enumerate(text.splitlines(), 1):
        if pat.search(line):
            dest.append(f"{p}:{n}:{line}")
(Path(RAW / "destructive_sites.txt")).write_text("\n".join(dest) + "\n")
print("destructive-primitive lines:", len(dest))
per = {}
for l in dest:
    a = area(l.split(":", 1)[0])
    per[a] = per.get(a, 0) + 1
print("destructive by area:", dict(sorted(per.items(), key=lambda kv: -kv[1])))
