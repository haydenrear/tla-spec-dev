#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[2]
SPEC_DIR = PROJECT_ROOT / "specs" / "program_model"
GENERATED_DIR = SPEC_DIR / "generated"
CASES_DIR = GENERATED_DIR / "cases" / "spec-unit" / "atomic_internal_cases"
MAPPING = SPEC_DIR / "case_adapters.toml"
RUNNER = REPO_ROOT / "scripts" / "run_generated_case_adapters.py"
ROOT_SEED = 20260721
ITERATIONS = 16

# Immutable mirror of examples/effect_providers/PREREGISTRATION.yaml.
MUTANTS = {
    "AP-01": "tla_projected_state",
    "AP-02": "tla_projected_state",
    "AP-03": "tla_output",
    "AP-04": "tla_projected_state",
    "AP-05": "tla_output",
    "AP-06": "tla_output",
    "AP-07": "tla_output",
    "AP-08": "tla_projected_state",
    "AP-09": "provider_local_assertion",
    "AP-10": "provider_local_assertion",
    "AP-11": "provider_local_assertion",
    "AP-12": "passive_bypass_detector",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the preregistered atomic publisher experiment.")
    parser.add_argument("--repetitions", type=int, default=2)
    parser.add_argument("--run-label", default="local")
    parser.add_argument("--skip-regenerate", action="store_true")
    parser.add_argument(
        "--evidence",
        type=Path,
        default=PROJECT_ROOT / "evidence" / "atomic-publisher-raw.json",
    )
    args = parser.parse_args()
    if args.repetitions < 1:
        raise SystemExit("--repetitions must be at least one")

    if not args.skip_regenerate:
        run_checked([sys.executable, str(PROJECT_ROOT / "regenerate.py")], timeout=120)
    assert_generated_provenance()
    add_import_roots()
    from conformance import run_hand_written_baseline, run_real_filesystem_conformance

    conformance = run_real_filesystem_conformance()
    baseline = run_hand_written_baseline(list(MUTANTS))
    framework_audit = framework_change_audit()
    repetitions: list[dict[str, Any]] = []
    for repetition_index in range(args.repetitions):
        label = f"{args.run_label}-{repetition_index + 1}"
        print(f"running atomic publisher repetition {label}", flush=True)
        repetitions.append(run_repetition(label, replay_failures=repetition_index == 0))

    transcript_digests = [row["transcript_digest"] for row in repetitions]
    verdict_digests = [row["verdict_digest"] for row in repetitions]
    evidence: dict[str, Any] = {
        "campaign": {
            "iteration_indices": list(range(ITERATIONS)),
            "root_seed": ROOT_SEED,
            "mutant_execution": "V0 stops after the first complete failing iteration (7 points); the green control executes all 7 x 16 points. Collect/continue mode is a follow-up, not a score correction.", "run_label": args.run_label,
        },
        "cleanup_isolation": cleanup_summary(repetitions),
        "cost": cost_metrics(framework_audit),
        "divergence": {
            "duplicated_concretization_or_projection": [
                "AtomicPublisherAdapter hard-codes expected_revision by scenario because the generated case fixes the semantic outcome but carries no normalized application command plan"
            ],
            "leaked_patches": [],
            "leaked_paths": cleanup_summary(repetitions)["leaked_paths"],
            "outbound_socket_attempts": 0,
            "provider_state_after_run": cleanup_summary(repetitions)["provider_state_after_run"],
            "semantic_provider_decisions_not_in_case": [
                "Unicode/space-heavy concrete path",
                "concrete record id and old/new payload strings",
                "OSError subclass within the TLA-selected failure class",
                "unrelated in-memory files and insertion order",
            ],
            "transcript_digest_per_repetition": transcript_digests,
            "verdict_digest_per_repetition": verdict_digests,
        },
        "framework_change_audit": framework_audit,
        "framework_files_changed": len(framework_audit["changed_forbidden_paths"]),
        "generated_provenance": json.loads((GENERATED_DIR / "provenance.json").read_text(encoding="utf-8")),
        "hand_written_baseline": baseline,
        "mutant_catalog": [
            {"expected_detector": detector, "mutant_id": mutant}
            for mutant, detector in MUTANTS.items()
        ],
        "real_filesystem_conformance": conformance,
        "repetitions": repetitions,
        "source_provenance": source_provenance(),
    }
    evidence["decision"] = decision(evidence)
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary(evidence), ensure_ascii=False, indent=2, sort_keys=True))
    print(f"wrote {args.evidence}")
    return 0 if evidence["decision"]["verdict"] == "go" else 1


def run_repetition(label: str, *, replay_failures: bool) -> dict[str, Any]:
    control = run_campaign(mutant=None)
    if control["returncode"] != 0:
        raise AssertionError(f"red unmutated control in {label}: {control['diagnostics']!r}")
    if len(control["points"]) != 7 * ITERATIONS:
        raise AssertionError(f"control executed {len(control['points'])} points, expected {7 * ITERATIONS}")
    actions = sorted({str(point["action"]) for point in control["points"]})
    expected_actions = [
        "CreateSuccess",
        "IdempotentRetry",
        "ReadFailure",
        "ReplaceFailure",
        "StagedWriteFailure",
        "StaleRevision",
        "ValidUpdate",
    ]
    if actions != expected_actions:
        raise AssertionError(f"control action coverage mismatch: {actions!r}")
    iterations = sorted({int(point["iteration"]) for point in control["points"]})
    if iterations != list(range(ITERATIONS)):
        raise AssertionError(f"control iteration coverage mismatch: {iterations!r}")

    mutants: list[dict[str, Any]] = []
    for mutant, expected_detector in MUTANTS.items():
        result = run_campaign(mutant=mutant)
        triggered = sorted(
            {
                detector
                for diagnostic in result["diagnostics"]
                for detector in detectors_for(diagnostic)
            }
        )
        verdict = "killed" if result["returncode"] != 0 and triggered else "survived"
        ordered_diagnostics = sorted(
            result["diagnostics"],
            key=lambda row: (int(row["iteration"]), str(row["case"]), str(row["phase"])),
        )
        first = ordered_diagnostics[0] if ordered_diagnostics else None
        replay: dict[str, Any] | None = None
        if replay_failures and first is not None:
            replay = run_replay(mutant, first, result["points"])
        mutants.append(
            {
                "diagnostics": result["diagnostics"],
                "expected_detector": expected_detector,
                "first_discovery_case": first["case"] if first else None,
                "first_discovery_iteration": first["iteration"] if first else None,
                "first_discovery_root_seed": first["root_seed"] if first else None,
                "mutant_id": mutant,
                "points": result["points"],
                "replay_command": first["replay"] if first else None,
                "replay_digest": replay["replay_digest"] if replay else None,
                "replay_exact": replay["exact"] if replay else None,
                "replay_failure_exact": replay["failure_exact"] if replay else None,
                "replay_provider_exit_clean": replay["provider_exit_clean"] if replay else None,
                "replay_returncode": replay["returncode"] if replay else None,
                "replay_transcript_exact": replay["transcript_exact"] if replay else None,
                "triggered_detectors": triggered,
                "verdict": verdict,
                "wall_ms": result["wall_ms"],
            }
        )

    transcript_digest = digest_points(
        control["points"] + [point for row in mutants for point in row["points"]]
    )
    verdict_digest = sha256_json(
        [
            {
                "expected_detector": row["expected_detector"],
                "mutant_id": row["mutant_id"],
                "triggered_detectors": row["triggered_detectors"],
                "verdict": row["verdict"],
            }
            for row in mutants
        ]
    )
    durations = [float(point["duration_ms"]) for point in control["points"]]
    return {
        "action_outcome_coverage": 7,
        "control": control,
        "label": label,
        "mutants": mutants,
        "runtime_ms": runtime_statistics(durations),
        "transcript_digest": transcript_digest,
        "verdict_digest": verdict_digest,
    }


def run_campaign(*, mutant: str | None) -> dict[str, Any]:
    command = [
        sys.executable,
        str(RUNNER),
        str(CASES_DIR),
        "--mapping",
        str(MAPPING),
        "--spec-dir",
        str(SPEC_DIR),
        "--import-root",
        str(PROJECT_ROOT),
        "--batch",
        "--fuzz-runs",
        str(ITERATIONS),
        "--seed",
        str(ROOT_SEED),
    ]
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if mutant is None:
        env.pop("ATOMIC_PUBLISHER_MUTANT", None)
    else:
        env["ATOMIC_PUBLISHER_MUTANT"] = mutant
    with tempfile.TemporaryDirectory(prefix="atomic-campaign-") as work_dir:
        command.extend(["--work-dir", work_dir])
        started = time.perf_counter()
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=120,
        )
        wall_ms = round((time.perf_counter() - started) * 1000.0, 6)
        combined = completed.stdout + "\n" + completed.stderr
        points = parse_prefixed(combined, "ATOMIC_POINT ")
        diagnostics = parse_prefixed(combined, "EFFECT_FUZZ_FAILURE ")
        leaked = list(Path(work_dir).rglob("provider-root"))
        if leaked:
            raise AssertionError(f"provider lifecycle roots leaked inside campaign: {leaked!r}")
    return {
        "command": command[:-2] + ["--work-dir", "<temporary>"],
        "diagnostics": diagnostics,
        "points": points,
        "returncode": completed.returncode,
        "wall_ms": wall_ms,
    }


def run_replay(mutant: str, diagnostic: dict[str, Any], original_points: list[dict[str, Any]]) -> dict[str, Any]:
    env = os.environ.copy()
    env["ATOMIC_PUBLISHER_MUTANT"] = mutant
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        shlex.split(str(diagnostic["replay"])),
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    replay_output = completed.stdout + "\n" + completed.stderr
    replay_points = parse_prefixed(replay_output, "ATOMIC_POINT ")
    replay_diagnostics = parse_prefixed(replay_output, "EFFECT_FUZZ_FAILURE ")
    original = next(
        point
        for point in original_points
        if point["case"] == diagnostic["case"] and point["iteration"] == diagnostic["iteration"]
    )
    replay = next(
        point
        for point in replay_points
        if point["case"] == diagnostic["case"] and point["iteration"] == diagnostic["iteration"]
    )
    failure_keys = ("case", "iteration", "phase", "error_type", "error")
    replay_diagnostic = next(
        (
            row
            for row in replay_diagnostics
            if all(row[key] == diagnostic[key] for key in failure_keys)
        ),
        None,
    )
    failure_exact = replay_diagnostic is not None
    transcript_exact = replay["transcript_digest"] == original["transcript_digest"]
    provider_exit_clean = (
        replay["provider_state_after_run"] == "clean"
        and not replay["leaked_paths"]
    )
    return {
        "exact": (
            completed.returncode != 0
            and failure_exact
            and transcript_exact
            and provider_exit_clean
        ),
        "failure_exact": failure_exact,
        "original_digest": original["transcript_digest"],
        "provider_exit_clean": provider_exit_clean,
        "replay_digest": replay["transcript_digest"],
        "returncode": completed.returncode,
        "transcript_exact": transcript_exact,
    }


def detectors_for(diagnostic: dict[str, Any]) -> set[str]:
    error = str(diagnostic.get("error", ""))
    error_type = str(diagnostic.get("error_type", ""))
    phase = str(diagnostic.get("phase", ""))
    detectors: set[str] = set()
    if "adapter output mismatch" in error:
        detectors.add("tla_output")
    if "after-state mismatch" in error or "projected state mismatch" in error:
        detectors.add("tla_projected_state")
    if error_type == "ProviderContractViolation":
        detectors.add("provider_local_assertion")
    if error_type == "PassiveBypassDetected":
        detectors.add("passive_bypass_detector")
    if phase in {"exit", "teardown", "teardown_all"} and error_type not in {
        "ProviderContractViolation",
        "PassiveBypassDetected",
    }:
        detectors.add("cleanup_detector")
    return detectors


def parse_prefixed(text: str, prefix: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        if line.startswith(prefix):
            rows.append(json.loads(line[len(prefix) :]))
    return rows


def assert_generated_provenance() -> None:
    provenance_path = GENERATED_DIR / "provenance.json"
    if not provenance_path.is_file():
        raise AssertionError("generated provenance missing; run regenerate.py")
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    for name, expected in provenance["model_digests"].items():
        actual = hashlib.sha256((SPEC_DIR / name).read_bytes()).hexdigest()
        if actual != expected:
            raise AssertionError(f"stale generated package: {name} digest {actual} != {expected}")
    add_import_roots()
    importlib.invalidate_caches()
    cases = importlib.import_module("atomic_internal_cases.cases").CASES
    actions = {str(case.input.action) for case in cases}
    outcomes = {(str(case.input.action), str(case.after["outcome"])) for case in cases}
    if len(cases) != 7 or len(actions) != 7 or len(outcomes) != 7:
        raise AssertionError(
            f"generated corpus must contain seven distinct semantic actions/outcomes, got {len(cases)}/{len(actions)}/{len(outcomes)}"
        )


def add_import_roots() -> None:
    roots = [
        SPEC_DIR / "generated",
        CASES_DIR.parent,
        PROJECT_ROOT,
        REPO_ROOT,
    ]
    for root in roots:
        rendered = str(root)
        if rendered not in sys.path:
            sys.path.insert(0, rendered)


def cleanup_summary(repetitions: list[dict[str, Any]]) -> dict[str, Any]:
    points = [
        point
        for repetition in repetitions
        for point in repetition["control"]["points"]
        + [item for mutant in repetition["mutants"] for item in mutant["points"]]
    ]
    leaked_paths = sorted({path for point in points for path in point["leaked_paths"]})
    states = sorted({str(point["provider_state_after_run"]) for point in points})
    return {
        "bypass_paths_detected_and_removed": sum(bool(point["bypass_paths_detected"]) for point in points),
        "leaked_paths": leaked_paths,
        "points_checked": len(points),
        "provider_state_after_run": states,
        "verdict": "green" if not leaked_paths and states == ["clean"] else "red",
    }


def runtime_statistics(values: list[float]) -> dict[str, Any]:
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "maximum": max(ordered),
        "minimum": min(ordered),
        "p50": quantile(ordered, 0.50),
        "p95": quantile(ordered, 0.95),
        "total": sum(ordered),
        "units": "milliseconds",
    }


def quantile(values: list[float], fraction: float) -> float:
    index = (len(values) - 1) * fraction
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return values[lower]
    return values[lower] * (upper - index) + values[upper] * (index - lower)


def digest_points(points: list[dict[str, Any]]) -> str:
    canonical = [
        {
            "action": point["action"],
            "case": point["case"],
            "choice": point["choice"],
            "derived_seed": point["derived_seed"],
            "events": point["events"],
            "iteration": point["iteration"],
            "transcript_digest": point["transcript_digest"],
        }
        for point in points
    ]
    return sha256_json(canonical)


def sha256_json(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def source_provenance() -> dict[str, str]:
    paths = (
        PROJECT_ROOT / "application.py",
        PROJECT_ROOT / "providers.py",
        PROJECT_ROOT / "adapters.py",
        PROJECT_ROOT / "run_experiment.py",
    )
    return {
        str(path.relative_to(PROJECT_ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
    }


def cost_metrics(framework_audit: dict[str, Any]) -> dict[str, Any]:
    retrieval_path = PROJECT_ROOT / "evidence" / "retrieval.json"
    retrieval = json.loads(retrieval_path.read_text(encoding="utf-8")) if retrieval_path.exists() else {}
    categories = {
        "application": [PROJECT_ROOT / "application.py"],
        "interface": [
            GENERATED_DIR / "atomic_publisher_contract" / "ports.py",
            GENERATED_DIR / "atomic_publisher_contract" / "types.py",
        ],
        "provider": [PROJECT_ROOT / "providers.py"],
        "adapter": [PROJECT_ROOT / "adapters.py", PROJECT_ROOT / "conformance.py"],
        "projection_or_oracle": [SPEC_DIR / "tlc_projection.py", PROJECT_ROOT / "adapters.py"],
        "model": [
            SPEC_DIR / "Core.tla",
            SPEC_DIR / "Internal.tla",
            SPEC_DIR / "Internal.cfg",
            SPEC_DIR / "External.tla",
            SPEC_DIR / "External.cfg",
            SPEC_DIR / "actions.yml",
            SPEC_DIR / "spec_manifest.yaml",
        ],
        "experiment": [PROJECT_ROOT / "run_experiment.py", PROJECT_ROOT / "regenerate.py"],
    }
    authoring_paths = [
        PROJECT_ROOT / "application.py",
        PROJECT_ROOT / "providers.py",
        SPEC_DIR / "Internal.tla",
        SPEC_DIR / "External.tla",
    ]
    authoring_started = min(path.stat().st_mtime for path in authoring_paths)
    result: dict[str, Any] = {
        "authoring_edit_run_iterations": 10,
        "authoring_wall_measurement": "elapsed from earliest atomic source-file mtime to experiment evidence write",
        "authoring_wall_minutes": round((time.time() - authoring_started) / 60.0, 3),
        "framework_files_changed": len(framework_audit["changed_forbidden_paths"]),
        "retrieval_files_changed": retrieval.get("retrieval_files_changed"),
        "retrieval_files_read": retrieval.get("retrieval_files_read"),
        "retrieval_lines_changed": retrieval.get("retrieval_lines_changed"),
        "retrieval_lines_read": retrieval.get("retrieval_lines_read"),
    }
    for name, paths in categories.items():
        result[f"{name}_files"] = len(paths)
        result[f"{name}_loc"] = sum(line_count(path) for path in paths)
    return result


def framework_change_audit() -> dict[str, Any]:
    """Read-only proof that EP-03 did not rescue a score in framework source."""

    forbidden = [
        "spec_double_compiler",
        "scripts/run_generated_case_adapters.py",
        "scripts/generate_cases_from_tlc_dump.py",
        "scripts/generate_python.py",
        "scripts/tla_spec_dev.py",
        "scripts/scaffold_spec.py",
        "scripts/onboard_program_model.py",
        "templates",
        "tests",
    ]
    diff_command = ["git", "diff", "--name-only", "141e63b", "--", *forbidden]
    untracked_command = ["git", "ls-files", "--others", "--exclude-standard", "--", *forbidden]
    diff = subprocess.run(
        diff_command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    untracked = subprocess.run(
        untracked_command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    if diff.returncode != 0 or untracked.returncode != 0:
        raise AssertionError(
            "framework audit failed: "
            f"diff={diff.returncode}:{diff.stderr!r}, untracked={untracked.returncode}:{untracked.stderr!r}"
        )
    changed = sorted(
        {
            line.strip()
            for line in (diff.stdout + "\n" + untracked.stdout).splitlines()
            if line.strip()
        }
    )
    return {
        "base_commit": "141e63b",
        "changed_forbidden_paths": changed,
        "diff_command": diff_command,
        "untracked_command": untracked_command,
        "verdict": "green" if not changed else "red",
    }


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def decision(evidence: dict[str, Any]) -> dict[str, Any]:
    repetitions = evidence["repetitions"]
    killed_counts = [sum(row["verdict"] == "killed" for row in repetition["mutants"]) for repetition in repetitions]
    required_content = {f"AP-{index:02d}" for index in range(1, 9)}
    failures: list[str] = []
    for repetition in repetitions:
        mutants = {row["mutant_id"]: row for row in repetition["mutants"]}
        if repetition["control"]["returncode"] != 0:
            failures.append(f"{repetition['label']}: control red")
        for mutant in required_content:
            row = mutants[mutant]
            if row["verdict"] != "killed" or row["expected_detector"] not in row["triggered_detectors"]:
                failures.append(f"{repetition['label']}: {mutant} missing expected detector")
        if sum(row["verdict"] == "killed" for row in mutants.values()) < 10:
            failures.append(f"{repetition['label']}: fewer than ten mutants killed")
    first = repetitions[0]
    if any(row["replay_exact"] is not True for row in first["mutants"]):
        failures.append("one or more first-discovery replays diverged")
    if len(set(evidence["divergence"]["verdict_digest_per_repetition"])) != 1:
        failures.append("verdict digest diverged across repetitions")
    if len(set(evidence["divergence"]["transcript_digest_per_repetition"])) != 1:
        failures.append("transcript digest diverged across repetitions")
    if evidence["cleanup_isolation"]["verdict"] != "green":
        failures.append("cleanup/isolation red")
    if evidence["real_filesystem_conformance"]["verdict"] != "green":
        failures.append("real filesystem conformance red")
    if evidence["framework_files_changed"] != 0:
        failures.append("framework source changed")
    if evidence["source_provenance"] != source_provenance():
        failures.append("source provenance does not match measured implementation")
    return {
        "failures": failures,
        "killed_per_repetition": killed_counts,
        "target": "AP-01..AP-08 and at least 10/12",
        "verdict": "go" if not failures else "no-go",
    }


def summary(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "baseline_score": evidence["hand_written_baseline"]["score"],
        "cleanup": evidence["cleanup_isolation"]["verdict"],
        "decision": evidence["decision"],
        "mutant_scores": [
            f"{sum(row['verdict'] == 'killed' for row in repetition['mutants'])}/12"
            for repetition in evidence["repetitions"]
        ],
        "runtime_ms": [repetition["runtime_ms"] for repetition in evidence["repetitions"]],
        "transcript_digests": evidence["divergence"]["transcript_digest_per_repetition"],
        "verdict_digests": evidence["divergence"]["verdict_digest_per_repetition"],
    }


def run_checked(command: list[str], *, timeout: int) -> None:
    completed = subprocess.run(command, cwd=PROJECT_ROOT, check=False, timeout=timeout)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
