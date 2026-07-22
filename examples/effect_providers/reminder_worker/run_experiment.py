#!/usr/bin/env python3
"""Run the preregistered reminder control, baseline, mutants, and probes."""

from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
from types import MappingProxyType, SimpleNamespace
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[2]
SPEC_ROOT = PROJECT_ROOT / "specs" / "program_model"
GENERATED_ROOT = PROJECT_ROOT / "generated"
CASES_ROOT = GENERATED_ROOT / "cases" / "spec-unit" / "reminder_internal_cases"
PREREGISTRATION = PROJECT_ROOT.parent / "PREREGISTRATION.yaml"
ROOT_SEED = 20260721
FUZZ_RUNS = 25
MUTANTS = tuple(f"RW-{index:02d}" for index in range(1, 13))
EXPECTED_DETECTORS = {
    "RW-01": "shared_journal",
    "RW-02": "shared_journal",
    "RW-03": "tla_projected_state",
    "RW-04": "tla_projected_state",
    "RW-05": "provider_local_assertion",
    "RW-06": "tla_output",
    "RW-07": "provider_local_assertion",
    "RW-08": "provider_local_assertion",
    "RW-09": "provider_local_assertion",
    "RW-10": "provider_local_assertion",
    "RW-11": "tla_projected_state",
    "RW-12": "tla_output",
}
EXPECTED_ACTIONS = (
    "ProcessEmpty",
    "ProcessNotDue",
    "ProcessAccepted",
    "ProcessRetryable",
    "ProcessPermanent",
    "ProcessDuplicate",
    "ProcessPendingRetry",
)
BASELINE_SCENARIOS = ("empty", "accepted", "retryable", "duplicate")
PORTS = ("ClockPort", "QueuePort", "OutboxPort", "NotifierPort")
AUTHORING_EDIT_RUN_ITERATIONS = 5


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def source_provenance() -> dict[str, str]:
    paths = (
        PROJECT_ROOT / "app.py",
        PROJECT_ROOT / "providers.py",
        PROJECT_ROOT / "adapter.py",
        PROJECT_ROOT / "run_experiment.py",
    )
    return {
        str(path.relative_to(PROJECT_ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
    }


def validate_preregistration() -> None:
    text = PREREGISTRATION.read_text(encoding="utf-8")
    section = text.split("  reminder_worker:\n", 1)[1].split("\noverall_decision:", 1)[0]
    ids = tuple(re.findall(r"id: (RW-\d{2})", section))
    detectors = dict(
        re.findall(r"id: (RW-\d{2}).*?expected_detector: ([a-z_]+)", section)
    )
    iterations_match = re.search(r"iteration_indices: \[([^]]+)\]", section)
    iterations = () if iterations_match is None else tuple(
        int(item.strip()) for item in iterations_match.group(1).split(",")
    )
    if ids != MUTANTS:
        raise AssertionError(f"preregistered mutant ids changed: {ids!r}")
    if detectors != EXPECTED_DETECTORS:
        raise AssertionError(f"preregistered detectors changed: {detectors!r}")
    if iterations != tuple(range(FUZZ_RUNS)):
        raise AssertionError(f"preregistered iterations changed: {iterations!r}")
    if "forbidden_rescue_surfaces" not in text or "framework_files_changed equals 0" not in section:
        raise AssertionError("no-framework-change rule missing from preregistration")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return round(ordered[max(0, math.ceil(len(ordered) * fraction) - 1)], 6)


def runtime_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    values = [float(row["duration_ms"]) for row in rows]
    return {
        "count": len(values),
        "minimum": None if not values else round(min(values), 6),
        "p50": percentile(values, 0.50),
        "p95": percentile(values, 0.95),
        "maximum": None if not values else round(max(values), 6),
        "total": round(sum(values), 6),
    }


def generated_cases() -> list[Any]:
    sys.path.insert(0, str(CASES_ROOT.parent))
    from reminder_internal_cases.cases import CASES

    actions = tuple(case.input.action for case in CASES)
    if actions != EXPECTED_ACTIONS:
        raise AssertionError(f"generated action/outcome coverage changed: {actions!r}")
    if any(case.before["scenario"] != case.input.params["scenario"] for case in CASES):
        raise AssertionError("generated scenario parameter does not refine the before state")
    return list(CASES)


def runner_command(*, fuzz_runs: int = FUZZ_RUNS) -> list[str]:
    return [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_generated_case_adapters.py"),
        str(CASES_ROOT),
        "--mapping",
        str(SPEC_ROOT / "case_adapters.toml"),
        "--spec-dir",
        str(SPEC_ROOT),
        "--batch",
        "--fuzz-runs",
        str(fuzz_runs),
        "--seed",
        str(ROOT_SEED),
        "--import-root",
        str(PROJECT_ROOT),
        "--import-root",
        str(GENERATED_ROOT),
    ]


def parse_failures(output: str) -> list[dict[str, Any]]:
    prefix = "EFFECT_FUZZ_FAILURE "
    failures: list[dict[str, Any]] = []
    for line in output.splitlines():
        if prefix in line:
            failures.append(json.loads(line.split(prefix, 1)[1]))
    return failures


def classify_failure(failure: dict[str, Any]) -> str:
    error = str(failure.get("error", ""))
    if "DETECTOR[shared_journal]" in error:
        return "shared_journal"
    if "DETECTOR[provider_local_assertion]" in error:
        return "provider_local_assertion"
    if "adapter after-state mismatch" in error:
        return "tla_projected_state"
    if "adapter output mismatch" in error:
        return "tla_output"
    if "bypass" in error.lower():
        return "passive_bypass_detector"
    return "unattributed"


def run_variant(run_root: Path, mutant: str | None) -> dict[str, Any]:
    name = "control" if mutant is None else mutant
    variant_root = run_root / "variants" / name
    variant_root.mkdir(parents=True)
    trace_path = variant_root / "trace.jsonl"
    cleanup_path = variant_root / "cleanup.jsonl"
    environment = os.environ.copy()
    environment["REMINDER_TRACE_LOG"] = str(trace_path)
    environment["REMINDER_CLEANUP_LOG"] = str(cleanup_path)
    if mutant is None:
        environment.pop("REMINDER_MUTANT", None)
    else:
        environment["REMINDER_MUTANT"] = mutant

    started = time.perf_counter()
    completed = subprocess.run(
        runner_command(),
        cwd=PROJECT_ROOT,
        env=environment,
        text=True,
        capture_output=True,
        timeout=120,
    )
    wall_ms = round((time.perf_counter() - started) * 1000, 6)
    (variant_root / "stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (variant_root / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
    combined = completed.stdout + "\n" + completed.stderr
    failures = parse_failures(combined)
    traces = read_jsonl(trace_path)
    cleanup = read_jsonl(cleanup_path)
    detectors = sorted({classify_failure(failure) for failure in failures})
    stable = {
        "mutant": mutant,
        "returncode": completed.returncode,
        "failures": [
            {
                "case": failure["case"],
                "iteration": failure["iteration"],
                "phase": failure["phase"],
                "error_type": failure["error_type"],
                "error": failure["error"],
            }
            for failure in failures
        ],
        "trace_digests": [row["digest"] for row in traces],
        "cleanup": [(row["case"], row["iteration"], row["registry_empty"]) for row in cleanup],
    }
    return {
        "name": name,
        "mutant": mutant,
        "returncode": completed.returncode,
        "wall_ms": wall_ms,
        "runtime_ms": runtime_stats(traces),
        "executed_points": len(traces),
        "cleanup_points": len(cleanup),
        "cleanup_all_empty": bool(cleanup) and all(row["registry_empty"] for row in cleanup),
        "actions": sorted({row["action"] for row in traces}),
        "concretization_seed_count": len(
            {row["bundle"]["concretization_seed"] for row in traces}
        ),
        "failures": failures,
        "triggered_detectors": detectors,
        "trace_digests": [row["digest"] for row in traces],
        "verdict_digest": canonical_digest(stable),
    }


def replay_first_failure(run_root: Path, variant: dict[str, Any]) -> dict[str, Any] | None:
    if not variant["failures"]:
        return None
    mutant = str(variant["mutant"])
    failure = variant["failures"][0]
    replay_root = run_root / "replays" / mutant
    replay_root.mkdir(parents=True)
    trace_path = replay_root / "trace.jsonl"
    cleanup_path = replay_root / "cleanup.jsonl"
    environment = os.environ.copy()
    environment["REMINDER_MUTANT"] = mutant
    environment["REMINDER_TRACE_LOG"] = str(trace_path)
    environment["REMINDER_CLEANUP_LOG"] = str(cleanup_path)
    command = shlex.split(str(failure["replay"]))
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=environment,
        text=True,
        capture_output=True,
        timeout=30,
    )
    replay_failures = parse_failures(completed.stdout + "\n" + completed.stderr)
    traces = read_jsonl(trace_path)
    cleanup = read_jsonl(cleanup_path)
    original_trace = next(
        row
        for row in read_jsonl(run_root / "variants" / mutant / "trace.jsonl")
        if row["case"] == failure["case"] and row["iteration"] == failure["iteration"]
    )
    same_failure = bool(replay_failures) and all(
        replay_failures[0][key] == failure[key]
        for key in ("case", "iteration", "phase", "error_type", "error")
    )
    same_digest = bool(traces) and traces[0]["digest"] == original_trace["digest"]
    cleanup_valid = (
        len(cleanup) == 1
        and cleanup[0]["registry_empty"]
        and cleanup[0]["case"] == failure["case"]
        and cleanup[0]["iteration"] == failure["iteration"]
    )
    return {
        "command": f"REMINDER_MUTANT={mutant} {failure['replay']}",
        "returncode": completed.returncode,
        "same_failure": same_failure,
        "same_transcript_digest": same_digest,
        "cleanup_points": len(cleanup),
        "cleanup_all_empty": cleanup_valid,
        "digest": None if not traces else traces[0]["digest"],
    }


HAND_STATES = {
    "empty": ({"queueState": "empty", "outboxState": "none", "receiptState": "none"}, "empty"),
    "accepted": ({"queueState": "ready", "outboxState": "none", "receiptState": "none"}, "accepted"),
    "retryable": ({"queueState": "ready", "outboxState": "none", "receiptState": "none"}, "retryable"),
    "duplicate": ({"queueState": "ready", "outboxState": "sent", "receiptState": "stored"}, "duplicate"),
}


def hand_case(scenario: str) -> Any:
    state, result = HAND_STATES[scenario]
    before = {
        "scenario": scenario,
        "queueState": state["queueState"],
        "outboxState": state["outboxState"],
        "notificationCount": 0,
        "receiptState": state["receiptState"],
        "result": "ready",
    }
    action = {
        "empty": "ProcessEmpty",
        "accepted": "ProcessAccepted",
        "retryable": "ProcessRetryable",
        "duplicate": "ProcessDuplicate",
    }[scenario]
    return SimpleNamespace(
        name=f"hand_{scenario}",
        before=before,
        input=SimpleNamespace(action=action, params={"scenario": scenario}),
        output={"status": result},
        after=None,
    )


def run_hand_point(case: Any, mutant: str | None, work_dir: Path) -> None:
    sys.path.insert(0, str(REPO_ROOT))
    sys.path.insert(0, str(PROJECT_ROOT))
    sys.path.insert(0, str(GENERATED_ROOT))
    from adapter import ReminderAdapter
    from providers import clock_provider, notifier_provider, outbox_provider, queue_provider
    from spec_double_compiler.effects import derive_effect_seed
    from spec_double_compiler.runtime import AdapterCaseContext, EffectProviderContext

    values: dict[str, Any] = {}
    providers = (clock_provider, queue_provider, outbox_provider, notifier_provider)
    prior = os.environ.get("REMINDER_MUTANT")
    if mutant is None:
        os.environ.pop("REMINDER_MUTANT", None)
    else:
        os.environ["REMINDER_MUTANT"] = mutant
    try:
        with ExitStack() as stack:
            for port, provider in zip(PORTS, providers, strict=True):
                context = EffectProviderContext(
                    port_name=port,
                    action=case.input.action,
                    case=case,
                    work_dir=work_dir,
                    iteration=0,
                    root_seed=ROOT_SEED,
                    derived_seed=derive_effect_seed(ROOT_SEED, case.name, 0, port),
                )
                values[port] = stack.enter_context(provider.bind(context))
            adapter = ReminderAdapter()
            adapter_context = AdapterCaseContext(
                kind="hand-baseline",
                case=case,
                work_dir=work_dir,
                mapping=None,
                shared={},
                effects=MappingProxyType(values),
            )
            adapter.setup(adapter_context)
            try:
                result = adapter.run(case, work_dir)
                if result.output != case.output:
                    raise AssertionError("hand baseline output mismatch")
            finally:
                adapter.teardown(adapter_context)
    finally:
        if prior is None:
            os.environ.pop("REMINDER_MUTANT", None)
        else:
            os.environ["REMINDER_MUTANT"] = prior


def run_baseline(run_root: Path) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for mutant in (None, *MUTANTS):
        errors: list[str] = []
        for scenario in BASELINE_SCENARIOS:
            try:
                run_hand_point(
                    hand_case(scenario),
                    mutant,
                    run_root / "baseline" / (mutant or "control") / scenario,
                )
            except BaseException as exc:
                errors.append(f"{scenario}: {type(exc).__name__}: {exc}")
        results.append(
            {
                "mutant": mutant,
                "verdict": "green" if not errors else "killed",
                "errors": errors,
            }
        )
    control = results[0]
    killed = sum(row["verdict"] == "killed" for row in results[1:])
    return {
        "scenarios": list(BASELINE_SCENARIOS),
        "control_green": control["verdict"] == "green",
        "control_errors": control["errors"],
        "killed": killed,
        "total": len(MUTANTS),
        "score": round(killed / len(MUTANTS), 6),
        "mutants": results[1:],
    }


def capability_probes() -> dict[str, Any]:
    from datetime import datetime, timezone
    import socket

    clock_value = datetime.now(timezone.utc).isoformat()
    attempts: list[tuple[Any, ...]] = []
    original_connect = socket.socket.connect

    def blocked_connect(_socket: Any, address: Any) -> None:
        attempts.append(tuple(address))
        raise OSError("passive probe blocked direct network bypass")

    socket.socket.connect = blocked_connect
    succeeded = False
    try:
        candidate = socket.socket()
        try:
            candidate.connect(("127.0.0.1", 9))
            succeeded = True
        except OSError:
            pass
        finally:
            candidate.close()
    finally:
        socket.socket.connect = original_connect
    return {
        "direct_clock_bypass": {
            "provider_intercepted": False,
            "value_obtained": bool(clock_value),
            "finding": "explicit ClockPort cannot intercept direct datetime access",
        },
        "direct_network_bypass": {
            "provider_intercepted": False,
            "passive_attempt_detected": bool(attempts),
            "outbound_socket_succeeded": succeeded,
            "attempts": attempts,
            "finding": "explicit NotifierPort needs a separate passive socket guard for bypasses",
        },
    }


def parse_tlc_metrics(output: str) -> list[dict[str, Any]]:
    states = re.findall(r"(\d+) states generated, (\d+) distinct states found", output)
    depths = re.findall(r"depth of the complete state graph search is (\d+)", output)
    walls = {
        name: float(value)
        for name, value in re.findall(r"MODEL_COMMAND_WALL_SECONDS (internal|external) ([0-9.]+)", output)
    }
    names = ["internal", "external"]
    return [
        {
            "model": names[index],
            "generated_states": int(pair[0]),
            "distinct_states": int(pair[1]),
            "search_depth": int(depths[index]),
            "wall_seconds": walls[names[index]],
            "wall_measurement_scope": "TLC plus case projection/package generation",
            "generated_cases": 7,
            "selected_cases": 7 if index == 0 else 0,
            "executed_cases": 7 if index == 0 else 0,
            "action_outcome_coverage": list(EXPECTED_ACTIONS) if index == 0 else [name.replace("Process", "Run") for name in EXPECTED_ACTIONS],
        }
        for index, pair in enumerate(states[:2])
    ]


def file_lines(paths: list[Path]) -> tuple[int, int]:
    existing = [path for path in paths if path.is_file()]
    return len(existing), sum(len(path.read_text(encoding="utf-8").splitlines()) for path in existing)


def changed_paths() -> list[str]:
    commands = [
        ["git", "diff", "--name-only", "141e63b"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ]
    paths: set[str] = set()
    for command in commands:
        completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=True)
        paths.update(line for line in completed.stdout.splitlines() if line)
    return sorted(paths)


def cost_record() -> dict[str, Any]:
    model_paths = sorted(SPEC_ROOT.glob("*"))
    groups = {
        "application": [PROJECT_ROOT / "app.py", PROJECT_ROOT / "reminder_cli.py"],
        "interface": [GENERATED_ROOT / "reminder_contract" / "types.py", GENERATED_ROOT / "reminder_contract" / "ports.py"],
        "provider": [PROJECT_ROOT / "providers.py"],
        "adapter": [PROJECT_ROOT / "adapter.py", PROJECT_ROOT / "external_adapter.py"],
        "projection_or_oracle": [SPEC_ROOT / "tlc_projection.py"],
        "model": [path for path in model_paths if path.suffix in {".tla", ".cfg", ".yaml", ".yml", ".toml"}],
        "experiment": [PROJECT_ROOT / "regenerate.py", PROJECT_ROOT / "run_experiment.py", PROJECT_ROOT / "test_reminder_worker.py", PROJECT_ROOT / "README.md"],
    }
    result: dict[str, Any] = {}
    for name, paths in groups.items():
        files, lines = file_lines(paths)
        result[f"{name}_files"] = files
        result[f"{name}_loc"] = lines
    retrieval_path = PROJECT_ROOT / "evidence" / "retrieval.json"
    retrieval = json.loads(retrieval_path.read_text(encoding="utf-8")) if retrieval_path.exists() else {}
    result.update(
        {
            "authoring_wall_minutes": round((time.time() - int(subprocess.run(["git", "show", "-s", "--format=%ct", "141e63b"], cwd=REPO_ROOT, text=True, capture_output=True, check=True).stdout)) / 60, 3),
            "authoring_wall_measurement": "shared concurrent wall-clock elapsed since preregistration; not person-effort",
            "authoring_edit_run_iterations": AUTHORING_EDIT_RUN_ITERATIONS,
            "retrieval_files_read": retrieval.get("files_read", 0),
            "retrieval_lines_read": retrieval.get("lines_read", 0),
            "retrieval_files_changed": retrieval.get("files_changed", 0),
            "retrieval_lines_changed": retrieval.get("lines_changed", 0),
        }
    )
    forbidden_prefixes = ("spec_double_compiler/", "scripts/", "templates/", "tests/")
    framework = [path for path in changed_paths() if path.startswith(forbidden_prefixes)]
    result["framework_files_changed"] = len(framework)
    result["framework_changed_paths"] = framework
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--skip-regenerate", action="store_true")
    args = parser.parse_args()
    validate_preregistration()
    measured_sources = source_provenance()

    run_root = PROJECT_ROOT / "evidence" / "runs" / args.run_id
    if run_root.exists():
        raise SystemExit(f"refusing to overwrite evidence run {run_root}")
    run_root.mkdir(parents=True)

    regeneration_output = ""
    if not args.skip_regenerate:
        completed = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "regenerate.py")],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            timeout=260,
        )
        regeneration_output = completed.stdout + "\n" + completed.stderr
        (run_root / "regenerate.txt").write_text(regeneration_output, encoding="utf-8")
        if completed.returncode != 0:
            raise SystemExit(f"regeneration failed; see {run_root / 'regenerate.txt'}")

    cases = generated_cases()
    control = run_variant(run_root, None)
    control_valid = (
        control["returncode"] == 0
        and control["executed_points"] == len(cases) * FUZZ_RUNS
        and control["cleanup_points"] == control["executed_points"]
        and control["cleanup_all_empty"]
        and tuple(control["actions"]) == tuple(sorted(EXPECTED_ACTIONS))
        and control["concretization_seed_count"] > 1
    )
    partial = {
        "schema_version": "ep03.reminder-worker.v1",
        "project": "reminder_worker",
        "run_id": args.run_id,
        "root_seed": ROOT_SEED,
        "iterations": list(range(FUZZ_RUNS)),
        "control": control,
        "control_valid": control_valid,
    }
    if not control_valid:
        (run_root / "results.json").write_text(json.dumps(partial, indent=2, sort_keys=True), encoding="utf-8")
        return 2

    variants = [run_variant(run_root, mutant) for mutant in MUTANTS]
    replays = {variant["mutant"]: replay_first_failure(run_root, variant) for variant in variants}
    mutations: list[dict[str, Any]] = []
    for variant in variants:
        first = variant["failures"][0] if variant["failures"] else None
        expected = EXPECTED_DETECTORS[str(variant["mutant"])]
        replay = replays[variant["mutant"]]
        cleanup_valid = (
            variant["cleanup_all_empty"]
            and variant["cleanup_points"] == variant["executed_points"]
        )
        replay_exact = bool(
            replay
            and replay["returncode"] != 0
            and replay["same_failure"]
            and replay["same_transcript_digest"]
            and replay["cleanup_all_empty"]
        )
        mutations.append(
            {
                "mutant_id": variant["mutant"],
                "expected_detector": expected,
                "verdict": "killed" if variant["returncode"] != 0 and variant["failures"] else "survived",
                "infrastructure_failure": variant["returncode"] != 0 and not variant["failures"],
                "triggered_detectors": variant["triggered_detectors"],
                "attribution_matches_preregistration": expected in variant["triggered_detectors"],
                "first_discovery_root_seed": None if first is None else first["root_seed"],
                "first_discovery_iteration": None if first is None else first["iteration"],
                "first_discovery_case": None if first is None else first["case"],
                "replay_command": None if replay is None else replay["command"],
                "replay_digest": None if replay is None else replay["digest"],
                "replay_returncode": None if replay is None else replay["returncode"],
                "replay_exact": replay_exact,
                "cleanup_points": variant["cleanup_points"],
                "cleanup_all_empty": variant["cleanup_all_empty"],
                "cleanup_valid": cleanup_valid,
                "replay_cleanup_points": None if replay is None else replay["cleanup_points"],
                "replay_cleanup_all_empty": bool(replay and replay["cleanup_all_empty"]),
                "executed_points": variant["executed_points"],
                "runtime_ms": variant["runtime_ms"],
                "verdict_digest": variant["verdict_digest"],
            }
        )
    killed = sum(row["verdict"] == "killed" for row in mutations)
    probes = capability_probes()
    baseline = run_baseline(run_root)
    costs = cost_record()
    sources_unchanged = measured_sources == source_provenance()
    infrastructure_clean = all(not row["infrastructure_failure"] for row in mutations)
    attribution_exact = all(row["attribution_matches_preregistration"] for row in mutations)
    replays_exact = all(row["replay_exact"] for row in mutations)
    cleanup_exact = all(
        row["cleanup_valid"] and row["replay_cleanup_all_empty"]
        for row in mutations
    )
    integrity_valid = (
        control_valid
        and infrastructure_clean
        and attribution_exact
        and replays_exact
        and cleanup_exact
        and baseline["control_green"]
        and costs["framework_files_changed"] == 0
        and sources_unchanged
    )
    if not integrity_valid:
        decision = "invalid_campaign"
    elif killed == 12:
        decision = "go"
    elif killed >= 10:
        decision = "investigate_one_generic_improvement"
    else:
        decision = "redesign"
    result = {
        **partial,
        "tlc": parse_tlc_metrics(regeneration_output),
        "generated_cases": {
            "count": len(cases),
            "actions": [case.input.action for case in cases],
            "source_model_sha256": canonical_digest(
                {
                    path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in (SPEC_ROOT / "Internal.tla", SPEC_ROOT / "Internal.cfg")
                }
            ),
            "package_sha256": canonical_digest(
                {
                    path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in sorted(CASES_ROOT.glob("*.py"))
                }
            ),
        },
        "effectful_mutation": {
            "killed": killed,
            "total": len(MUTANTS),
            "score": round(killed / len(MUTANTS), 6),
            "mutants": mutations,
        },
        "campaign_integrity": {
            "valid": integrity_valid,
            "control_valid": control_valid,
            "infrastructure_clean": infrastructure_clean,
            "attribution_exact": attribution_exact,
            "replays_exact": replays_exact,
            "cleanup_exact": cleanup_exact,
            "baseline_control_green": baseline["control_green"],
            "framework_audit_zero": costs["framework_files_changed"] == 0,
            "sources_unchanged": sources_unchanged,
        },
        "hand_written_baseline": baseline,
        "source_provenance": measured_sources,
        "capability_probes": probes,
        "cost": costs,
        "findings": {
            "action_helper_collapse_iterations": 1,
            "action_helper_collapse": "shared Finish helper initially erased seven outcome labels; direct top-level transitions fixed it before control",
            "semantic_provider_decisions_not_in_case": [
                "concrete unicode identifier, timestamp, receipt, and exception instance",
                "provider hard-codes stage before send and send before mark/ack ordering",
                "provider hard-codes one ClockPort read per point",
                "provider hard-codes duplicate-send rejection",
                "provider maps scenario/action to notifier success or retryable/permanent exception class",
            ],
            "duplicated_concretization_or_projection": [
                "provider reimplements cross-effect order and cardinality that are absent from terminal-state cases",
                "provider maps modeled scenario names to semantic response classes rather than receiving normalized generated effect-plan metadata",
                "provider snapshot manually projects concrete queue/outbox/receipt state into six TLA fields",
            ],
            "mutant_execution": "V0 stops after the first complete failing iteration: each killed mutant executed seven cases at iteration 0; only green controls covered all 175 representatives",
            "fuzz_breadth_claim": "12/12 demonstrates oracle coverage for the fixed catalog, not that later deterministic representatives discovered additional bugs",
            "survivors": [row["mutant_id"] for row in mutations if row["verdict"] == "survived"],
            "attribution_mismatches": [row["mutant_id"] for row in mutations if not row["attribution_matches_preregistration"]],
        },
        "decision": decision,
    }
    result["canonical_verdict_digest"] = canonical_digest(
        {
            "control": control["verdict_digest"],
            "mutants": [(row["mutant_id"], row["verdict"], row["triggered_detectors"], row["replay_exact"]) for row in mutations],
            "baseline": [(row["mutant"], row["verdict"]) for row in baseline["mutants"]],
            "probes": probes,
            "decision": result["decision"],
        }
    )
    (run_root / "results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"run": args.run_id, "killed": killed, "decision": result["decision"], "digest": result["canonical_verdict_digest"]}, sort_keys=True))
    return 0 if decision == "go" else 4


if __name__ == "__main__":
    raise SystemExit(main())
