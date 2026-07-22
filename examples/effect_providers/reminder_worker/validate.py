#!/usr/bin/env python3
"""Create one non-overwriting reminder-worker validation evidence run."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[2]
SPEC_ROOT = PROJECT_ROOT / "specs" / "program_model"
RUNS_ROOT = PROJECT_ROOT / "evidence" / "validation-runs"
USAGE_DESCRIPTOR = PROJECT_ROOT / "effect_provider_usage.yaml"
ROOT_SEED = 20260721
EXPECTED_CASES_PER_VIEW = 7
EXPECTED_MUTANTS = 12
EXPECTED_FUZZ_RUNS = 25

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(REPO_ROOT))

import run_experiment as campaign  # noqa: E402


def _relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def _project_digests() -> dict[str, str]:
    """Snapshot every persistent project file outside versioned validation runs."""

    result: dict[str, str] = {}
    for path in sorted(PROJECT_ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(PROJECT_ROOT)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        if relative.parts[:2] == ("evidence", "validation-runs"):
            continue
        result[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _source_digests() -> dict[str, str]:
    paths = (
        PROJECT_ROOT / "app.py",
        PROJECT_ROOT / "providers.py",
        PROJECT_ROOT / "adapter.py",
        PROJECT_ROOT / "external_adapter.py",
        PROJECT_ROOT / "regenerate.py",
        PROJECT_ROOT / "run_experiment.py",
        PROJECT_ROOT / "validate.py",
        USAGE_DESCRIPTOR,
    )
    return {
        str(path.relative_to(PROJECT_ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
    }


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
        "replay": {
            "attempted": 0,
            "exact": 0,
            "interpreter": str(Path(sys.executable).absolute()),
        },
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
        "source_digests": _source_digests(),
    }


def _configure_campaign(generated_root: Path) -> None:
    campaign.GENERATED_ROOT = generated_root
    campaign.CASES_ROOT = (
        generated_root / "cases" / "spec-unit" / "reminder_internal_cases"
    )


def _run_campaign(run_root: Path, regeneration_output: str) -> dict[str, Any]:
    raw_root = run_root / "campaign"
    raw_root.mkdir()
    campaign.validate_preregistration()
    cases = campaign.generated_cases()
    if len(cases) != EXPECTED_CASES_PER_VIEW:
        raise AssertionError(f"expected 7 generated internal cases, got {len(cases)}")

    control = campaign.run_variant(raw_root, None)
    control_valid = (
        control["returncode"] == 0
        and control["executed_points"] == len(cases) * EXPECTED_FUZZ_RUNS
        and control["cleanup_points"] == control["executed_points"]
        and control["cleanup_all_empty"]
        and tuple(control["actions"]) == tuple(sorted(campaign.EXPECTED_ACTIONS))
        and control["concretization_seed_count"] > 1
    )
    if not control_valid:
        raise AssertionError(f"generated effect control was not complete and green: {control!r}")

    variants = [campaign.run_variant(raw_root, mutant) for mutant in campaign.MUTANTS]
    replays = {
        str(variant["mutant"]): campaign.replay_first_failure(raw_root, variant)
        for variant in variants
    }
    mutations: list[dict[str, Any]] = []
    for variant in variants:
        mutant = str(variant["mutant"])
        first = variant["failures"][0] if variant["failures"] else None
        expected = campaign.EXPECTED_DETECTORS[mutant]
        replay = replays[mutant]
        expected_executed = (
            0
            if first is None
            else len(cases) * (int(first["iteration"]) + 1)
        )
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
            and replay["cleanup_points"] == 1
        )
        killed = bool(
            variant["returncode"] != 0
            and variant["failures"]
            and expected in variant["triggered_detectors"]
            and variant["executed_points"] == expected_executed
            and cleanup_valid
            and replay_exact
        )
        mutations.append(
            {
                "mutant_id": mutant,
                "verdict": "killed" if killed else "invalid_or_survived",
                "expected_detector": expected,
                "triggered_detectors": variant["triggered_detectors"],
                "first_discovery_case": None if first is None else first["case"],
                "first_discovery_iteration": None if first is None else first["iteration"],
                "executed_points": variant["executed_points"],
                "cleanup_points": variant["cleanup_points"],
                "cleanup_exact": cleanup_valid,
                "replay": replay,
                "replay_exact": replay_exact,
                "runtime_ms": variant["runtime_ms"],
                "verdict_digest": variant["verdict_digest"],
            }
        )

    baseline = campaign.run_baseline(raw_root)
    probes = campaign.capability_probes()
    from providers import active_point_count

    active_points_after_campaign = active_point_count()
    tlc = campaign.parse_tlc_metrics(regeneration_output)
    if len(tlc) != 2 or any(row["wall_seconds"] >= 120 for row in tlc):
        raise AssertionError(f"TLC evidence is missing or exceeded 120 seconds: {tlc!r}")

    killed = sum(row["verdict"] == "killed" for row in mutations)
    replay_exact_count = sum(row["replay_exact"] for row in mutations)
    cleanup_checked = (
        int(control["cleanup_points"])
        + sum(int(row["cleanup_points"]) for row in mutations)
        + sum(int(row["replay"]["cleanup_points"]) for row in mutations if row["replay"])
    )
    cleanup_clean = (
        cleanup_checked
        if control["cleanup_all_empty"]
        and all(
            row["cleanup_exact"]
            and row["replay"] is not None
            and row["replay"]["cleanup_all_empty"]
            for row in mutations
        )
        and active_points_after_campaign == 0
        else 0
    )
    replay_interpreters = {
        shlex.split(str(variant["failures"][0]["replay"]))[0]
        for variant in variants
        if variant["failures"]
    }
    expected_interpreter = str(Path(sys.executable).absolute())
    if replay_interpreters != {expected_interpreter}:
        raise AssertionError(
            "recorded replay did not preserve the originating interpreter: "
            f"{sorted(replay_interpreters)!r} != {[expected_interpreter]!r}"
        )

    valid = (
        killed == EXPECTED_MUTANTS
        and replay_exact_count == EXPECTED_MUTANTS
        and baseline["control_green"]
        and cleanup_clean == cleanup_checked
        and not probes["direct_network_bypass"]["outbound_socket_succeeded"]
    )
    detail = {
        "schema_version": 1,
        "control": control,
        "control_valid": control_valid,
        "mutations": mutations,
        "mutants_killed": killed,
        "replays_exact": replay_exact_count,
        "cleanup": {"checked": cleanup_checked, "clean": cleanup_clean},
        "hand_written_baseline": baseline,
        "capability_probes": probes,
        "active_points_after_campaign": active_points_after_campaign,
        "tlc": tlc,
        "valid": valid,
        "limitations": [
            "all fixed mutants are discovered in iteration zero; later representatives measure control breadth, not incremental discovery",
            "the runner stops a mutant after its first complete failing iteration rather than collecting every failing representative",
        ],
    }
    _write_json(run_root / "campaign.json", detail)
    if not valid:
        raise AssertionError("effect campaign, replay, or cleanup gate failed")
    return detail


def _external_command(generated_root: Path, run_root: Path) -> list[str]:
    return [
        str(Path(sys.executable).absolute()),
        str(REPO_ROOT / "scripts" / "run_generated_case_adapters.py"),
        str(generated_root / "cases" / "testgraph" / "reminder_external_cases"),
        "--mapping",
        str(SPEC_ROOT / "testgraph_bindings.yml"),
        "--spec-dir",
        str(SPEC_ROOT),
        "--view",
        "external",
        "--batch",
        "--validate-capabilities",
        "--import-root",
        str(PROJECT_ROOT),
        "--import-root",
        str(generated_root),
        "--work-dir",
        str(run_root / "external-work"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if (
        not args.run_id.strip()
        or args.run_id in {".", ".."}
        or Path(args.run_id).name != args.run_id
    ):
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
    result = _default_result(run_id=args.run_id, command=command, commit=_git_head())
    result_path = run_root / "result.json"
    steps_path = run_root / "steps.json"
    steps: list[dict[str, Any]] = []
    generated_root = run_root / "generated"
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    before = _project_digests()

    try:
        tlc2 = os.environ.get("TLC2") or shutil.which("tlc2")
        if not tlc2:
            raise AssertionError("tlc2 is unavailable; install/sync spec-double-compiler CLI dependencies")
        regeneration_log = run_root / "regeneration.log"
        steps.append(
            _run_step(
                name="regeneration_and_tlc",
                command=[
                    interpreter,
                    str(PROJECT_ROOT / "regenerate.py"),
                    "--tlc2",
                    tlc2,
                    "--out",
                    str(generated_root),
                ],
                log_path=regeneration_log,
                timeout=120,
                env=env,
            )
        )
        _configure_campaign(generated_root)
        campaign_detail = _run_campaign(
            run_root,
            regeneration_log.read_text(encoding="utf-8"),
        )

        external_env = env.copy()
        external_env["REMINDER_GENERATED_ROOT"] = str(generated_root)
        external_log = run_root / "external.log"
        steps.append(
            _run_step(
                name="real_cli_external_rung",
                command=_external_command(generated_root, run_root),
                log_path=external_log,
                timeout=120,
                env=external_env,
            )
        )
        external_output = external_log.read_text(encoding="utf-8")
        if "executed 7 cases in batch" not in external_output:
            raise AssertionError("external rung did not report all seven generated cases")

        steps.append(
            _run_step(
                name="focused_tests",
                command=[interpreter, str(PROJECT_ROOT / "test_reminder_worker.py")],
                log_path=run_root / "focused-tests.log",
                timeout=120,
                env=env,
            )
        )

        after = _project_digests()
        if after != before:
            before_paths = set(before)
            after_paths = set(after)
            changed = sorted(
                path
                for path in before_paths & after_paths
                if before[path] != after[path]
            )
            raise AssertionError(
                "validation mutated persistent project or frozen EP-03 evidence: "
                f"added={sorted(after_paths - before_paths)!r}, "
                f"removed={sorted(before_paths - after_paths)!r}, changed={changed!r}"
            )

        result["cases"] = {
            "generated": EXPECTED_CASES_PER_VIEW * 2,
            "control_points": int(campaign_detail["control"]["executed_points"]),
            "external": EXPECTED_CASES_PER_VIEW,
        }
        result["controls"] = {"passed": 6, "total": 6}
        result["mutants"] = {
            "killed": int(campaign_detail["mutants_killed"]),
            "total": EXPECTED_MUTANTS,
        }
        result["replay"] = {
            "attempted": EXPECTED_MUTANTS,
            "exact": int(campaign_detail["replays_exact"]),
            "interpreter": interpreter,
        }
        result["cleanup"] = campaign_detail["cleanup"]
        result["oracle_findings"] = {
            "tla_owned": [
                "seven scenario-specific terminal outcomes",
                "queue, outbox, notification-count, receipt, result, and output projections",
                "delivery invariant connecting sent outbox entries to stored receipts",
            ],
            "provider_owned": [
                "one correlated bundle of unicode job/message values, time, receipt, and exception subclass",
                "stage-before-send and send-before-mark-before-ack ordering in a shared journal",
                "one clock read, duplicate-send rejection, payload identity, and effect cardinality",
                "point-local four-provider registry acquisition and reverse-order cleanup",
            ],
            "passive_external": [
                "direct datetime access is confirmed to bypass ClockPort",
                "a passive socket guard detects and blocks the direct-network bypass probe",
                "seven generated External cases pass through a real CLI child process and file-persisted queue/outbox",
            ],
        }
        result["limitations"] = [
            "terminal TLA cases do not encode the cross-port journal, so the provider duplicates ordering and cardinality rules",
            "scenario names are manually mapped to notifier success, retryable subclasses, or permanent subclasses",
            "the provider manually projects concrete shared state back into six TLA fields",
            "direct datetime, direct network, external broker, database, filesystem, thread, and child-process effects bypass explicit in-process bindings",
            "the CLI rung uses separate repository adapters and validates terminal semantics, not identity with the in-process provider implementation",
            *campaign_detail["limitations"],
        ]
        result["status"] = "pass"
    except BaseException as error:
        result["limitations"].append(
            f"validation failure: {type(error).__name__}: {error}"
        )
    finally:
        final_snapshot = _project_digests()
        if final_snapshot != before:
            before_paths = set(before)
            after_paths = set(final_snapshot)
            changed = sorted(
                path
                for path in before_paths & after_paths
                if before[path] != final_snapshot[path]
            )
            result["status"] = "fail"
            result["limitations"].append(
                "validation mutated persistent project or frozen EP-03 evidence: "
                f"added={sorted(after_paths - before_paths)!r}, "
                f"removed={sorted(before_paths - after_paths)!r}, changed={changed!r}"
            )
        result["duration_seconds"] = round(time.perf_counter() - started, 6)
        _write_json(steps_path, steps)
        result["artifacts"] = [
            _relative(path)
            for path in (
                run_root / "regeneration.log",
                run_root / "campaign.json",
                run_root / "campaign",
                run_root / "external.log",
                run_root / "external-work",
                run_root / "focused-tests.log",
                steps_path,
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
