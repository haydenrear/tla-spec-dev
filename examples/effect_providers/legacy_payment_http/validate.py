#!/usr/bin/env python3
"""Run a non-overwriting validation of the legacy HTTP effect provider."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[2]
RUNS_ROOT = PROJECT_ROOT / "evidence" / "validation-runs"
USAGE = PROJECT_ROOT / "effect_provider_usage.yaml"
SEED = 20260721
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
        timeout=30,
    ).stdout.strip()


def _write_process(
    run_root: Path,
    name: str,
    command: list[str],
    *,
    cwd: Path,
    timeout: int,
    env: dict[str, str] | None = None,
    expect_nonzero: bool = False,
) -> subprocess.CompletedProcess[str]:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    duration = time.perf_counter() - started
    artifact = {
        "command": command,
        "cwd": str(cwd),
        "returncode": completed.returncode,
        "duration_seconds": round(duration, 6),
        "timeout_seconds": timeout,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    process_path = run_root / "processes" / f"{name}.json"
    process_path.parent.mkdir(parents=True, exist_ok=True)
    process_path.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    succeeded = completed.returncode != 0 if expect_nonzero else completed.returncode == 0
    if not succeeded:
        expectation = "non-zero" if expect_nonzero else "zero"
        raise RuntimeError(
            f"{name} returned {completed.returncode}; expected {expectation}; "
            f"see {process_path.relative_to(PROJECT_ROOT)}"
        )
    return completed


def _common_result(run_id: str, started: float) -> dict[str, Any]:
    interpreter = str(Path(sys.executable).absolute())
    return {
        "schema_version": 1,
        "project": "legacy_payment_http",
        "run_id": run_id,
        "status": "fail",
        "command": [interpreter, str(Path(__file__).resolve()), "--run-id", run_id],
        "commit": _git_head(),
        "provider_contract": {"name": "EffectProvider.bind", "version": 1},
        "seed": SEED,
        "cases": {"generated": 0, "control_points": 0, "external": 0},
        "controls": {"passed": 0, "total": 4},
        "mutants": {"killed": 0, "total": 12},
        "replay": {"attempted": 0, "exact": 0, "interpreter": interpreter},
        "cleanup": {"checked": 0, "clean": 0},
        "duration_seconds": round(time.perf_counter() - started, 6),
        "usage_descriptor": {"path": USAGE.name, "sha256": _sha256(USAGE)},
        "oracle_findings": {
            "tla_owned": [
                "seven semantic response classes",
                "decision reason reference class and retry count",
                "expected output and projected post-state",
            ],
            "provider_owned": [
                "concrete status timeout response bytes headers and opaque reference",
                "requests.Session.send installation and request-shape assertions",
                "per-point transcript state socket guard and cleanup",
            ],
            "passive_external": [
                "urllib and raw-socket bypass probes",
                "56 generated child-process cases against a real loopback HTTP server",
            ],
        },
        "limitations": [
            "The provider is compatibility-only because it patches requests.Session.send.",
            "Unrecognized clients, subprocesses, native networking, and already-captured callables can bypass an in-process patch.",
            "The strong hand-written four-scenario baseline kills the same fixed mutants; this catalog demonstrates systematic coverage and replay, not incremental mutation score.",
            "Killed mutants stop after the first complete killing iteration; only the green control and survivors execute all 32 iterations.",
        ],
        "artifacts": [],
    }


def _cross_cwd_replay(
    run_root: Path, experiment: dict[str, Any]
) -> tuple[bool, str]:
    mutation = experiment["mutations"][0]
    replay_command = shlex.split(str(mutation["replay_command"]))
    expected_interpreter = str(Path(sys.executable).absolute())
    if not replay_command or replay_command[0] != expected_interpreter:
        raise RuntimeError(
            "recorded replay did not preserve the dependency-bearing interpreter: "
            f"{replay_command[:1]!r} != {[expected_interpreter]!r}"
        )
    if any("site-packages" in item for item in replay_command):
        raise RuntimeError("recorded replay still contains the obsolete site-packages import-root workaround")

    replay_root = run_root / "cross-cwd-replay"
    replay_root.mkdir()
    transcript = replay_root / "transcript.jsonl"
    env = os.environ.copy()
    env["LEGACY_PAYMENT_TRANSCRIPT"] = str(transcript)
    env["LEGACY_PAYMENT_MUTANT"] = str(mutation["mutant_id"])
    completed = _write_process(
        run_root,
        "cross-cwd-replay",
        replay_command,
        cwd=replay_root,
        env=env,
        timeout=120,
        expect_nonzero=True,
    )
    rows = [
        json.loads(line)
        for line in transcript.read_text(encoding="utf-8").splitlines()
        if line
    ]
    marker = "EFFECT_FUZZ_FAILURE "
    diagnostics = [
        json.loads(line.split(marker, 1)[1])
        for line in (completed.stdout + completed.stderr).splitlines()
        if marker in line
    ]
    exact = (
        len(rows) == 1
        and len(diagnostics) == 1
        and rows[0]["transcript_digest"] == mutation["replay_digest"]
        and rows[0]["case"] == mutation["first_discovery_case"]
        and rows[0]["iteration"] == mutation["first_discovery_iteration"]
        and diagnostics[0]["case"] == mutation["first_discovery_case"]
        and diagnostics[0]["iteration"] == mutation["first_discovery_iteration"]
    )
    if not exact:
        raise RuntimeError("cross-working-directory replay did not match first discovery")
    return exact, replay_command[0]


def _validate(run_id: str, run_root: Path, result: dict[str, Any]) -> None:
    tlc2 = os.environ.get("TLC2_BIN") or shutil.which("tlc2")
    if not tlc2:
        raise RuntimeError("tlc2 is required (set TLC2_BIN or add tlc2 to PATH)")

    from scripts.run_experiment import _framework_snapshot

    framework_baseline = run_root / "framework-baseline.json"
    framework_baseline.write_text(
        json.dumps(_framework_snapshot(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    regeneration = run_root / "regeneration"
    _write_process(
        run_root,
        "regenerate",
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "regenerate.py"),
            "--tlc2",
            tlc2,
            "--evidence-dir",
            str(regeneration),
        ],
        cwd=PROJECT_ROOT,
        timeout=120,
    )

    experiment_path = run_root / "experiment.json"
    _write_process(
        run_root,
        "experiment",
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_experiment.py"),
            "--label",
            run_id,
            "--output",
            str(experiment_path),
            "--skip-regenerate",
            "--raw-dir",
            str(run_root / "experiment-raw"),
            "--generation-evidence",
            str(regeneration),
            "--framework-baseline",
            str(framework_baseline),
        ],
        cwd=PROJECT_ROOT,
        timeout=900,
    )
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    if experiment["stop_go"]["verdict"] != "go":
        raise RuntimeError("preregistered control/mutant/replay campaign returned no_go")

    _write_process(
        run_root,
        "focused-tests",
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=PROJECT_ROOT,
        timeout=120,
    )

    external_cases = PROJECT_ROOT / "generated" / "testgraph" / "payment_http_external_cases"
    external = _write_process(
        run_root,
        "external-56-cases",
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "run_generated_case_adapters.py"),
            str(external_cases),
            "--mapping",
            str(PROJECT_ROOT / "specs" / "program_model" / "testgraph_bindings.yml"),
            "--spec-dir",
            str(PROJECT_ROOT / "specs" / "program_model"),
            "--import-root",
            str(PROJECT_ROOT),
            "--view",
            "external",
            "--batch",
            "--work-dir",
            str(run_root / "external-work"),
        ],
        cwd=PROJECT_ROOT,
        timeout=120,
    )
    if "executed 56 cases in batch" not in external.stdout:
        raise RuntimeError("external rung did not report all 56 generated cases")

    cross_cwd_exact, replay_interpreter = _cross_cwd_replay(run_root, experiment)
    mutations = experiment["mutations"]
    internal_cases = int(experiment["campaign"]["generated_cases"])
    external_generation = json.loads(
        (regeneration / "tlc-generation.json").read_text(encoding="utf-8")
    )["views"]["external"]["generated_cases"]
    mutant_points = sum(int(row["executed_points"]) for row in mutations)
    replay_points = sum(int(row["replay_row_count"]) for row in mutations)
    cleanup_checks = int(experiment["control"]["executed_points"]) + mutant_points + replay_points + 1

    result.update(
        status="pass",
        cases={
            "generated": internal_cases + int(external_generation),
            "control_points": int(experiment["control"]["executed_points"]),
            "external": 56,
        },
        controls={"passed": 4, "total": 4},
        mutants={
            "killed": int(experiment["mutation_score"]["killed"]),
            "total": int(experiment["mutation_score"]["total"]),
        },
        replay={
            "attempted": len(mutations) + 1,
            "exact": sum(bool(row["replay_matches_first_discovery"]) for row in mutations)
            + int(cross_cwd_exact),
            "interpreter": replay_interpreter,
            "from_different_working_directory": cross_cwd_exact,
            "site_packages_import_root_workaround": False,
        },
        cleanup={"checked": cleanup_checks, "clean": cleanup_checks},
        artifacts=[
            "regeneration/tlc-generation.json",
            "framework-baseline.json",
            "processes/regenerate.json",
            "experiment.json",
            "experiment-raw/",
            "processes/experiment.json",
            "processes/focused-tests.json",
            "processes/external-56-cases.json",
            "processes/cross-cwd-replay.json",
            "cross-cwd-replay/transcript.jsonl",
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if not RUN_ID.fullmatch(args.run_id):
        parser.error("--run-id must use only letters, digits, dot, underscore, and hyphen")

    run_root = RUNS_ROOT / args.run_id
    try:
        run_root.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        raise SystemExit(f"refusing to overwrite existing validation evidence: {run_root}")

    started = time.perf_counter()
    result = _common_result(args.run_id, started)
    error: Exception | None = None
    try:
        _validate(args.run_id, run_root, result)
    except Exception as caught:
        error = caught
        result["limitations"].append(f"validation failure: {type(caught).__name__}: {caught}")
    result["duration_seconds"] = round(time.perf_counter() - started, 6)
    result_path = run_root / "result.json"
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {"status": result["status"], "result": str(result_path), "error": str(error) if error else None},
            sort_keys=True,
        )
    )
    return 0 if error is None and result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
