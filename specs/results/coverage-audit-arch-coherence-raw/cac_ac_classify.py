#!/usr/bin/env python3
"""Reproduce every table row set in the architectural-coherence coverage audit.

Run from the repository root:

    python3 specs/results/coverage-audit-arch-coherence-raw/cac_ac_classify.py

Reads only the raw enumeration outputs committed beside this file and writes
markdown fragments back into the same directory. Nothing here is hand-curated:
a reader applying the rules below to the raw files lands on the same rows.

Scope classification implements prompts/coverage_audit.md Step 0's closure rule
verbatim: an `implementation_scope` entry naming a FILE scopes that file only;
directory closure counts only where the plan writes a trailing slash. Anything
else is an ESCALATION -- never an inference, and never "out of scope", because
the architectural-coherence plan declares no exclusion rule at all.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN = "specs/desired_program_model/ticket_plan.yaml"

# --------------------------------------------------------------------------
# Step 0 scope, transcribed from the plan with its line numbers. CP:N == plan
# line N. Directory entries carry the plan's own trailing slash.
# --------------------------------------------------------------------------
SCOPE_DIRS: list[tuple[str, str]] = [
    ("examples/validation/runs/", "CP:784 (EV-02)"),
    ("examples/validation/", "CP:707 (EV-01), CP:1364 (EV-03)"),
    ("examples/case_modules/", "CP:708 (EV-01)"),
    ("examples/distributed_history/", "CP:709 (EV-01)"),
    ("examples/effect_providers/", "CP:710 (EV-01)"),
    ("specs/current/tests/", "CP:287 (AC-01)"),
    ("tests/", "CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03)"),
    ("prompts/", "CP:495 (AC-03)"),
    ("templates/", "CP:496 (AC-03)"),
    ("test_graph/", "CP:1272 (RP-07)"),
]

SCOPE_FILES: dict[str, str] = {
    "scripts/spec_evolution.py": "CP:207 (CM-01)",
    "scripts/generate_cases_from_tlc_dump.py": "CP:208 (CM-01), CP:966 (RP-02), CP:1210 (RP-03), CP:150 (service_catalog)",
    "scripts/budgets.py": "CP:209 (CM-01)",
    "references/case_modules.md": "CP:211 (CM-01), CP:497 (AC-03), CP:1211 (RP-03)",
    "scripts/analyze_architecture.py": "CP:283 (AC-01), CP:379 (AC-02), CP:872 (RP-01)",
    "scripts/tla_spec_dev.py": "CP:284 (AC-01)",
    "specs/current/TlaSpecDevCli.tla": "CP:285 (AC-01)",
    "specs/current/MC.cfg": "CP:286 (AC-01)",
    "references/architecture_coherence.md": "CP:288 (AC-01), CP:381 (AC-02), CP:874 (RP-01)",
    "SKILL.md": "CP:289 (AC-01), CP:498 (AC-03)",
    "scripts/architecture_reflexion.py": "CP:378 (AC-02), CP:607 (AC-04), CP:871 (RP-01)",
    "scripts/complexity_ledger.py": "CP:606 (AC-04), CP:1078 (RP-04)",
    "references/architecture_tractability.md": "CP:608 (AC-04)",
    "NEXT-EPIC.md": "CP:785 (EV-02), CP:1365 (EV-03)",
    "scripts/infer_action_params.py": "CP:965 (RP-02)",
    "scripts/analyze_complexity.py": "CP:1077 (RP-04)",
    "references/generation_modes.md": "CP:1144 (RP-05)",
    "specs/program_model/architecture_components.yaml": "CP:1145 (RP-05)",
    "scripts/case_modules.py": "CP:1209 (RP-03)",
    "specs/current/tests/test_tla_spec_dev_analyze_adapter.py": "CP:159 (service_catalog.adapter_boundaries)",
    "prompts/implementation_brief.md": "CP:156 (service_catalog.desired_boundaries)",
    "prompts/aspect_decomposition.md": "CP:157 (service_catalog.desired_boundaries), CP:1212 (RP-03)",
    "prompts/coverage_audit.md": "CP:152 (service_catalog.existing_boundaries)",
}


def scope_of(path: str) -> tuple[str, str]:
    """Return (classification, plan-line citation)."""
    if path in SCOPE_FILES:
        return "in-scope", SCOPE_FILES[path]
    for prefix, cite in SCOPE_DIRS:
        if path.startswith(prefix):
            return "in-scope", cite
    return "ESCALATION", "none - no plan line names it"


# --------------------------------------------------------------------------
# Step 1 representation index -> the only things a Sweep-1 row may map TO.
# Rows not listed here take the default polarity `unrepresented`.
# Every entry below was established by READING the cited code, not the path.
# --------------------------------------------------------------------------
M = "specs/desired_program_model/TlaSpecDevCli.tla"
REPRESENTED: dict[str, tuple[str, str, str]] = {
    "scripts/tla_spec_dev.py": (
        "BuildSkillCli, InstallLocalCli, ScaffoldProject, ScaffoldWorkflow, OpenTicket, "
        "AnalyzeComplexity, AnalyzeCorpus, AnalyzeArchitecture, RunEffectConformance, "
        "RunKillTest, RunSpecUnitTests, CloseTicket",
        "represented",
        f"{M}:228-663 vs dispatcher tla_spec_dev.py:385-731",
    ),
    "scripts/analyze_architecture.py": (
        "AnalyzeArchitecture",
        "partial",
        f"{M}:650 (action) vs analyze_architecture.py:1010 run(); UNCOVERED: the --out "
        "descriptor write (:1116-1117) has no declared port and no manifest actions row",
    ),
    "scripts/architecture_reflexion.py": (
        "AnalyzeArchitecture",
        "partial",
        f"{M}:650 vs architecture_reflexion.py compare/--out :2290-2291; UNCOVERED: the "
        "--out reflexion write and the --baseline delta write have no declared port",
    ),
    "scripts/analyze_complexity.py": (
        "AnalyzeComplexity",
        "partial",
        f"{M}:393 vs analyze_complexity.py:2293-2294; UNCOVERED: --out accepts an "
        "arbitrary path, the declared evidence_report port targets only **/results/**",
    ),
    "scripts/spec_evolution.py": (
        "CloseTicket",
        "partial",
        f"{M}:619 vs spec_evolution.py create_ticket_history_entry; UNCOVERED: "
        "record_complexity_ledger (:770) and the workflow-close path have no action",
    ),
    "scripts/budgets.py": (
        "RecordBudgets",
        "represented",
        f"{M}:286; budgets.py has zero effect sites, matching spec_manifest.yaml's "
        "deliberately EMPTY RecordBudgets row (spec_manifest.yaml:204)",
    ),
    "scripts/complexity_ledger.py": (
        "CloseTicket, ScaffoldWorkflow",
        "partial",
        f"{M}:619/:305 via spec_evolution.record_complexity_ledger and "
        "new_ticket_workflow.py:1006; UNCOVERED: no action represents the architecture_delta "
        "ledger member AC-04 added",
    ),
    "scripts/case_modules.py": (
        "none",
        "unrepresented",
        "standalone main() (case_modules.py:832+); not reachable from tla_spec_dev.py's "
        "parser (grep: no case_modules entry in build_parser)",
    ),
    "scripts/generate_cases_from_tlc_dump.py": (
        "none",
        "unrepresented",
        "no `generate` subcommand exists in tla_spec_dev.py:385-731; spawns java "
        "(:115), rmtree (:139), writes packages (:881-882)",
    ),
    "scripts/infer_action_params.py": (
        "none",
        "unrepresented",
        "standalone; writes the recovery audit at :825-826, no CLI subcommand",
    ),
}


def read_lines(name: str) -> list[str]:
    p = HERE / name
    if not p.exists():
        sys.exit(f"missing raw file: {p}")
    return [ln.rstrip("\n") for ln in p.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]


# --------------------------------------------------------------------------
# Sweep 1
# --------------------------------------------------------------------------
def sweep1() -> None:
    files = read_lines("sweep1-surface.txt")
    rows = []
    counts = {"in-scope": 0, "ESCALATION": 0}
    verdicts: dict[str, int] = {}
    for i, f in enumerate(files, 1):
        cls, cite = scope_of(f)
        counts[cls] += 1
        action, verdict, ev = REPRESENTED.get(f, ("none", "unrepresented", "-"))
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
        rows.append(f"| {i} | `{f}` | {cls} | {cite} | {action} | `{verdict}` | {ev} |")
    out = HERE / "sweep1-table.md"
    hdr = ("| # | Module (`path`) | In/Out of scope | Plan line | Spec action(s) representing it "
           "| Verdict | Evidence (`file:line`) |\n|---|---|---|---|---|---|---|")
    out.write_text(hdr + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
    print(f"SWEEP1 N={len(files)} M={len(rows)} equal={len(files) == len(rows)}")
    print(f"  scope: {counts}")
    print(f"  verdicts: {verdicts}")


# --------------------------------------------------------------------------
# Sweep 2 -- group rules. Ordered; first match wins; every raw hit lands in
# exactly one group. `*-N` groups are the LEXICAL-ONLY collapse: the token
# matched but the line performs no such effect (str.replace, list.remove,
# `def run(`, the word "time" in prose). Recorded, never silently dropped.
# --------------------------------------------------------------------------
EFFECT_RULES: dict[str, list[tuple[str, str, str]]] = {
    "filesystem": [
        ("FS-D", r"(rmtree|\.unlink\(|os\.remove\(|os\.rename\(|os\.replace\(|shutil\.move\(|replace_tree)",
         "DESTRUCTIVE: delete / rename / overwrite-in-place of a real path"),
        ("FS-W", r"(write_text|write_bytes|\.mkdir\(|makedirs|shutil\.copy|copytree|copyfile|copy2)",
         "WRITE/CREATE: creates or overwrites a file or directory"),
        ("FS-T", r"(tempfile|mkdtemp|NamedTemporaryFile|TemporaryDirectory)",
         "TEMP WORKDIR: creates a temporary tree"),
        ("FS-R", r"(read_text|read_bytes|\bopen\(|\.open\(|Path\(|Paths\.|glob|iterdir|rglob)",
         "READ / PATH CONSTRUCTION: no mutation of the filesystem"),
        ("FS-N", r".", "LEXICAL ONLY: token matched prose, a str/list method, or an identifier"),
    ],
    "subprocess": [
        ("SP-S", r"(subprocess|Popen|check_output|check_call|os\.system|execv|execve|\bspawn\w*\(|ProcessBuilder|Runtime\.getRuntime)",
         "REAL SPAWN: starts a child process"),
        ("SP-N", r".", "LEXICAL ONLY: bare `run`/`call`/`system` with no spawn primitive on the line"),
    ],
    "network": [
        ("NW-S", r"(\bsocket\b|urlopen|urlretrieve|urllib|httpx|aiohttp|HTTPConnection|HttpClient|requests\.(get|post|put|delete|Session)|\bcurl\b|\bwget\b)",
         "REAL NETWORK: opens or issues a network connection"),
        ("NW-N", r".", "LEXICAL ONLY: `connect`/`requests` as a word, a fixture name, or a comment"),
    ],
    "environment": [
        ("EN-S", r"(os\.environ|getenv|putenv|load_dotenv|expanduser|sys\.argv|System\.getenv)",
         "REAL ENVIRONMENT READ/WRITE: process environment, HOME expansion, or argv"),
        ("EN-N", r".", "LEXICAL ONLY: dict.setdefault, the word PATH in prose, an argparse dest"),
    ],
    "clock": [
        ("CL-S", r"(datetime\.(now|utcnow|today)|time\.time\(|time\.monotonic|perf_counter|\.sleep\(|strftime|timestamp\(\)|Instant\.now|System\.currentTimeMillis)",
         "REAL CLOCK READ / SLEEP: nondeterministic wall-clock or elapsed-time dependency"),
        ("CL-N", r".", "LEXICAL ONLY: the words time/now/today, a `timeout` identifier, a module import"),
    ],
    "randomness": [
        ("RN-S", r"(random\.|randint|\.shuffle\(|uuid4|uuid1|secrets\.|urandom|token_hex|Random\()",
         "REAL RANDOMNESS: nondeterministic value source"),
        ("RN-N", r".", "LEXICAL ONLY: `choice`/`sample`/`random` as a word or an argparse choices= list"),
    ],
    "persistent": [
        ("PT-S", r"(sqlite3|psycopg|pymysql|\bredis\b|boto3|create_engine|\.cursor\(\)|sessionmaker)",
         "REAL PERSISTENT STORE: database or object-store client"),
        ("PT-N", r".", "LEXICAL ONLY: `execute`/`commit`/`session`/`engine` as words (git commit, subprocess execute, a session id)"),
    ],
    "jvm_native": [
        ("JV-S", r"(ProcessBuilder|HttpClient|System\.getenv|Runtime\.getRuntime|Files\.[a-z]|Paths\.get|new File\()",
         "REAL JVM/NATIVE EFFECT: process, network, env, or file API on the JVM side"),
        ("JV-N", r".", "LEXICAL ONLY: the words File/exec/Runtime in Kotlin/Java prose, an import, or a type name"),
    ],
}


def split_hit(line: str) -> tuple[str, str, str]:
    """`path:lineno:text` -> (path, lineno, text)."""
    parts = line.split(":", 2)
    if len(parts) < 3:
        return line, "?", ""
    return parts[0], parts[1], parts[2]


def sweep2() -> None:
    summary = []
    for cat, rules in EFFECT_RULES.items():
        hits = read_lines(f"effects-{cat}.txt")
        buckets: dict[str, list[tuple[str, str, str]]] = {g: [] for g, _, _ in rules}
        for h in hits:
            path, ln, text = split_hit(h)
            for g, pat, _ in rules:
                if re.search(pat, text):
                    buckets[g].append((path, ln, text))
                    break
        assigned = sum(len(v) for v in buckets.values())
        assert assigned == len(hits), f"{cat}: {assigned} != {len(hits)}"
        lines = [f"| Group | Distinct effect semantics | Raw hits | in-scope hits | ESCALATION hits |",
                 "|---|---|---|---|---|"]
        for g, _, desc in rules:
            b = buckets[g]
            ins = sum(1 for p, _, _ in b if scope_of(p)[0] == "in-scope")
            lines.append(f"| `{g}` | {desc} | {len(b)} | {ins} | {len(b) - ins} |")
        (HERE / f"effects-{cat}-groups.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        summary.append((cat, len(hits), len(rules), {g: len(v) for g, v in buckets.items()}))
        # destructive filesystem sites get a per-site table, never a group
        if cat == "filesystem":
            rows = []
            for i, (p, ln, text) in enumerate(buckets["FS-D"], 1):
                cls, cite = scope_of(p)
                rows.append(f"| {i} | `{p}:{ln}` | `{text.strip()[:110]}` | {cls} | {cite} |")
            (HERE / "effects-destructive-sites.md").write_text(
                "| # | Site | Line | In/Out | Plan line |\n|---|---|---|---|---|\n" + "\n".join(rows) + "\n",
                encoding="utf-8")
            print(f"  destructive per-site rows = {len(rows)}")
    for cat, raw, ngroups, counts in summary:
        print(f"SWEEP2 {cat}: raw={raw} groups={ngroups} {counts}")


# --------------------------------------------------------------------------
# Sweep 3 -- one table per behavior class, grouped by distinct failure/branch
# semantics. Same accounting contract: first match wins, every hit placed once.
# --------------------------------------------------------------------------
BEHAVIOR_RULES: dict[str, list[tuple[str, str, str]]] = {
    "errorpaths": [
        ("EP-RAISE", r"\braise\b", "RAISES: the site refuses and propagates"),
        ("EP-CATCH-SILENT", r"except[^:]*:\s*(pass|return None|continue)|except.*:\s*$",
         "CATCHES: handler that may swallow (pass/None/continue or a block handler)"),
        ("EP-CATCH", r"\bexcept\b", "CATCHES: handler with a non-silent body"),
        ("EP-TRY", r"try:", "TRY BLOCK opener"),
        ("EP-N", r".", "LEXICAL ONLY: the words except/raise in prose or a docstring"),
    ],
    "retries": [
        ("RT-S", r"(for\s+attempt|range\(\s*(max_)?(retries|attempts)|retry\(|\bbackoff\b|max_tries|while\s+attempt)",
         "REAL RETRY LOOP"),
        ("RT-N", r".", "LEXICAL ONLY: the words retry/attempt/attempts in prose, an identifier, or a message"),
    ],
    "timeouts": [
        ("TO-S", r"(timeout\s*=|--timeout|TimeoutError|\bdeadline\b\s*=|expires\s*=|awaitWithTimeout|withTimeout)",
         "REAL TIMEOUT / DEADLINE"),
        ("TO-N", r".", "LEXICAL ONLY: the word timeout in prose or a help string"),
    ],
    "fallbacks": [
        ("FB-IMPORT", r"except\s+(ModuleNotFound|Import)Error|ImportError",
         "IMPORT FALLBACK: an optional dependency changes behaviour when absent"),
        ("FB-SILENT", r"(\.get\([^)]*,\s*(None|\[\]|\{\}|False|0|\"\")|or None|except[^:]*:\s*pass)",
         "SILENT DEFAULT: a missing input yields a default rather than a refusal"),
        ("FB-DEFAULT", r"\bdefaults?\b", "DECLARED DEFAULT: argparse/config default"),
        ("FB-N", r".", "LEXICAL ONLY: the word fallback in prose"),
    ],
    "concurrency": [
        ("CC-S", r"(threading|Thread\(|\basync def\b|\bawait\b|Lock\(|multiprocessing|concurrent\.futures|Semaphore|setDaemon|daemon\s*=)",
         "REAL CONCURRENCY PRIMITIVE"),
        ("CC-N", r".", "LEXICAL ONLY: the words thread/lock/daemon in prose or an identifier"),
    ],
    "configbranches": [
        ("CB-ENV", r"(os\.environ|getenv|System\.getenv)", "ENVIRONMENT-DRIVEN BRANCH"),
        ("CB-FLAG", r"(--no-|--allow|--force|--dry-run|args\.[a-z_]+\b.*\bif\b|\bif\s+args\.)",
         "CLI-FLAG-DRIVEN BRANCH"),
        ("CB-KEY", r"\.get\(\"", "CONFIG-KEY LOOKUP: behaviour depends on a manifest/JSON key"),
        ("CB-N", r".", "LEXICAL ONLY: the words flag/enabled/disabled in prose"),
    ],
}


def sweep3() -> None:
    for cls, rules in BEHAVIOR_RULES.items():
        hits = read_lines(f"behavior-{cls}.txt")
        buckets: dict[str, list[tuple[str, str, str]]] = {g: [] for g, _, _ in rules}
        for h in hits:
            path, ln, text = split_hit(h)
            for g, pat, _ in rules:
                if re.search(pat, text):
                    buckets[g].append((path, ln, text))
                    break
        assigned = sum(len(v) for v in buckets.values())
        assert assigned == len(hits), f"{cls}: {assigned} != {len(hits)}"
        lines = ["| Group | Distinct behavior semantics | Raw hits | in-scope hits | ESCALATION hits |",
                 "|---|---|---|---|---|"]
        for g, _, desc in rules:
            b = buckets[g]
            ins = sum(1 for p, _, _ in b if scope_of(p)[0] == "in-scope")
            lines.append(f"| `{g}` | {desc} | {len(b)} | {ins} | {len(b) - ins} |")
        (HERE / f"behavior-{cls}-groups.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"SWEEP3 {cls}: raw={len(hits)} groups={len(rules)} " +
              str({g: len(v) for g, v in buckets.items()}))


if __name__ == "__main__":
    sweep1()
    sweep2()
    sweep3()
