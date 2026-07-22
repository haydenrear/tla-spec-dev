#!/usr/bin/env python3
"""Create one non-overwriting atomic-publisher validation evidence run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[2]
RUNS_ROOT = PROJECT_ROOT / "evidence" / "validation-runs"
USAGE_DESCRIPTOR = PROJECT_ROOT / "effect_provider_usage.yaml"
ROOT_SEED = 20260721


def _relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
        timeout=10,
    ).stdout.strip()


def _framework_snapshot() -> dict[str, str]:
    from run_experiment import framework_snapshot

    return framework_snapshot()


def _run_step(
    *,
    name: str,
    command: list[str],
    log_path: Path,
    timeout: int,
    env: dict[str, str],
) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        duration = round(time.perf_counter() - started, 6)
        stdout = error.stdout or ""
        stderr = error.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        log_path.write_text(
            f"$ {shlex.join(command)}\n\n{stdout}\n{stderr}\n"
            f"TIMEOUT after {timeout} seconds\n",
            encoding="utf-8",
        )
        raise AssertionError(f"{name} exceeded its {timeout}-second bound") from error

    duration = round(time.perf_counter() - started, 6)
    log_path.write_text(
        f"$ {shlex.join(command)}\n\n{completed.stdout}\n{completed.stderr}",
        encoding="utf-8",
    )
    result = {
        "command": command,
        "duration_seconds": duration,
        "log": _relative(log_path),
        "name": name,
        "returncode": completed.returncode,
        "timeout_seconds": timeout,
    }
    if completed.returncode != 0:
        raise AssertionError(
            f"{name} failed with {completed.returncode}; see {_relative(log_path)}"
        )
    return result


def _default_result(*, run_id: str, command: list[str], commit: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "project": PROJECT_ROOT.name,
        "run_id": run_id,
        "status": "fail",
        "command": command,
        "commit": commit,
        "provider_contract": {"name": "EffectProvider.bind", "version": 1},
        "seed": ROOT_SEED,
        "cases": {"generated": 0, "control_points": 0, "external": 0},
        "controls": {"passed": 0, "total": 0},
        "mutants": {"killed": 0, "total": 0},
        "replay": {"attempted": 0, "exact": 0, "interpreter": str(Path(sys.executable).absolute())},
        "cleanup": {"checked": 0, "clean": 0},
        "duration_seconds": 0.0,
        "usage_descriptor": {
            "path": USAGE_DESCRIPTOR.name,
            "sha256": hashlib.sha256(USAGE_DESCRIPTOR.read_bytes()).hexdigest(),
        },
        "oracle_findings": {
            "tla_owned": [],
            "provider_owned": [],
            "passive_external": [],
        },
        "limitations": [],
        "artifacts": [],
    }


def _summarize(raw: dict[str, Any], provenance: dict[str, Any], result: dict[str, Any]) -> None:
    repetitions = raw["repetitions"]
    controls = [row["control"] for row in repetitions]
    mutant_rows = [mutant for row in repetitions for mutant in row["mutants"]]
    replay_rows = [mutant for mutant in repetitions[0]["mutants"] if mutant["replay_exact"] is not None]
    generation_views = provenance["views"]
    cleanup_checked = int(raw["cleanup_isolation"]["points_checked"])
    cleanup_green = raw["cleanup_isolation"]["verdict"] == "green"
    real_rows = raw["real_filesystem_conformance"]["outcomes"]

    replay_interpreters = {
        shlex.split(str(row["replay_command"]))[0]
        for row in replay_rows
        if row.get("replay_command")
    }
    if len(replay_interpreters) != 1:
        raise AssertionError(f"expected one replay interpreter, got {sorted(replay_interpreters)!r}")
    replay_interpreter = next(iter(replay_interpreters))

    if raw["decision"]["verdict"] != "go":
        raise AssertionError(f"preregistered decision was {raw['decision']!r}")
    if not all(control["returncode"] == 0 for control in controls):
        raise AssertionError("one or more generated green controls failed")
    if not all(row["verdict"] == "killed" for row in mutant_rows):
        raise AssertionError("one or more fixed mutants survived")
    if not all(row["replay_exact"] is True for row in replay_rows):
        raise AssertionError("one or more first-discovery replays diverged")
    if not cleanup_green:
        raise AssertionError("provider cleanup/isolation was not green")
    if raw["real_filesystem_conformance"]["verdict"] != "green" or not all(
        row["matched"] for row in real_rows
    ):
        raise AssertionError("real filesystem boundary did not match every modeled outcome")
    if raw["framework_files_changed"] != 0:
        raise AssertionError("the example validation changed framework source")

    result["cases"] = {
        "generated": sum(int(view["generated_cases"]) for view in generation_views.values()),
        "control_points": sum(len(control["points"]) for control in controls),
        "external": int(generation_views["external"]["generated_cases"]),
    }
    result["controls"] = {"passed": len(controls), "total": len(controls)}
    result["mutants"] = {
        "killed": sum(row["verdict"] == "killed" for row in mutant_rows),
        "total": len(mutant_rows),
    }
    result["replay"] = {
        "attempted": len(replay_rows),
        "exact": sum(row["replay_exact"] is True for row in replay_rows),
        "interpreter": replay_interpreter,
    }
    result["cleanup"] = {
        "checked": cleanup_checked,
        "clean": cleanup_checked if cleanup_green else 0,
    }
    result["oracle_findings"] = {
        "tla_owned": [
            "seven distinct semantic outcome classes",
            "result status, revision, and idempotence",
            "projected symbolic record state",
            "ordered filesystem protocol trace including delete_stage",
        ],
        "provider_owned": [
            "deterministic concrete paths, record values, unrelated files, and OSError subclasses",
            "canonical byte projection and strict per-point protocol journal",
            "point-local state acquisition, active-binding accounting, and cleanup",
        ],
        "passive_external": [
            "bounded physical-file bypass audit under the provider root",
            f"real TemporaryDirectory filesystem outcomes matched {len(real_rows)}/{len(real_rows)}",
            "external subprocess CLI projects result and filesystem artifacts independently",
        ],
    }
    result["limitations"] = [
        "the passive bypass audit sees only in-process files under the provider-owned root",
        "the adapter duplicates scenario-to-expected-revision input semantics absent from the generated case",
        "representative enumeration is deterministic but not exhaustive and does not shrink failures",
        "the real filesystem rung injects bounded OS failures; it does not induce every host failure mode",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if not args.run_id.strip() or args.run_id in {".", ".."} or Path(args.run_id).name != args.run_id:
        parser.error("--run-id must be one non-empty path component")

    RUNS_ROOT.mkdir(parents=True, exist_ok=True)
    run_root = RUNS_ROOT / args.run_id
    try:
        run_root.mkdir()
    except FileExistsError as error:
        raise SystemExit(f"refusing to overwrite existing evidence {run_root}") from error

    started = time.perf_counter()
    interpreter = str(Path(sys.executable).absolute())
    command = [interpreter, str(Path(__file__).resolve()), "--run-id", args.run_id]
    commit = _git_head()
    result = _default_result(run_id=args.run_id, command=command, commit=commit)
    steps: list[dict[str, Any]] = []
    step_path = run_root / "steps.json"
    result_path = run_root / "result.json"
    generation_path = run_root / "generated-provenance.json"
    experiment_path = run_root / "experiment.json"
    framework_baseline_path = run_root / "framework-baseline.json"
    real_boundary_path = run_root / "real-filesystem.json"
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    _write_json(framework_baseline_path, _framework_snapshot())

    try:
        steps.append(
            _run_step(
                name="regeneration",
                command=[
                    interpreter,
                    str(PROJECT_ROOT / "regenerate.py"),
                    "--provenance-out",
                    str(generation_path),
                ],
                log_path=run_root / "regeneration.log",
                timeout=120,
                env=env,
            )
        )
        steps.append(
            _run_step(
                name="preregistered_experiment",
                command=[
                    interpreter,
                    str(PROJECT_ROOT / "run_experiment.py"),
                    "--skip-regenerate",
                    "--repetitions",
                    "2",
                    "--run-label",
                    args.run_id,
                    "--evidence",
                    str(experiment_path),
                    "--framework-baseline",
                    str(framework_baseline_path),
                ],
                log_path=run_root / "experiment.log",
                timeout=600,
                env=env,
            )
        )
        raw = json.loads(experiment_path.read_text(encoding="utf-8"))
        provenance = json.loads(generation_path.read_text(encoding="utf-8"))
        _write_json(real_boundary_path, raw["real_filesystem_conformance"])
        _summarize(raw, provenance, result)
        steps.append(
            _run_step(
                name="focused_tests",
                command=[interpreter, str(PROJECT_ROOT / "test_atomic_publisher.py")],
                log_path=run_root / "focused-tests.log",
                timeout=120,
                env=env,
            )
        )
        result["status"] = "pass"
    except BaseException as error:
        result["limitations"].append(f"validation failure: {type(error).__name__}: {error}")
    finally:
        result["duration_seconds"] = round(time.perf_counter() - started, 6)
        _write_json(step_path, steps)
        result["artifacts"] = [
            _relative(path)
            for path in (
                run_root / "regeneration.log",
                generation_path,
                framework_baseline_path,
                run_root / "experiment.log",
                experiment_path,
                real_boundary_path,
                run_root / "focused-tests.log",
                step_path,
            )
            if path.exists()
        ]
        _write_json(result_path, result)

    print(
        json.dumps(
            {
                "status": result["status"],
                "run_id": args.run_id,
                "result": str(result_path),
            },
            sort_keys=True,
        )
    )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
