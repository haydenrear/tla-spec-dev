#!/usr/bin/env python3
"""Run and validate the experimental effect-provider projects."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


EXAMPLES_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLES_ROOT.parents[1]
PROJECTS = ("atomic_publisher", "legacy_payment_http", "reminder_worker")
REQUIRED_RESULT_KEYS = {
    "schema_version",
    "project",
    "run_id",
    "status",
    "command",
    "commit",
    "provider_contract",
    "seed",
    "cases",
    "controls",
    "mutants",
    "replay",
    "cleanup",
    "duration_seconds",
    "usage_descriptor",
    "oracle_findings",
    "limitations",
    "artifacts",
}
USAGE_KEYS = {
    "port",
    "provider",
    "binding_style",
    "state_scope",
    "fuzz_dimensions",
    "assertions",
    "cleanup",
    "bypass_limits",
}


def _default_run_id() -> str:
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    revision = subprocess.run(
        ["git", "rev-parse", "--short=12", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    return f"{now}-{revision}"


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def _frozen_evidence_digests() -> dict[str, str]:
    paths = [
        EXAMPLES_ROOT / "PREREGISTRATION.md",
        EXAMPLES_ROOT / "PREREGISTRATION.yaml",
        EXAMPLES_ROOT / "RESULTS.md",
        EXAMPLES_ROOT / "RESULTS.json",
    ]
    for project in PROJECTS:
        evidence_root = EXAMPLES_ROOT / project / "evidence"
        paths.extend(
            path
            for path in evidence_root.rglob("*")
            if path.is_file() and "validation-runs" not in path.relative_to(evidence_root).parts
        )
    return {
        str(path.relative_to(EXAMPLES_ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(paths)
    }


def _nonnegative_counts(path: Path, value: Any, keys: tuple[str, ...]) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected an object for {keys!r}")
    for key in keys:
        item = value.get(key)
        if isinstance(item, bool) or not isinstance(item, int) or item < 0:
            raise ValueError(f"{path}: {key!r} must be a non-negative integer")


def _validate_usage(project_root: Path, result: dict[str, Any]) -> None:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from extract_spec_manifest import parse_simple_yaml

    usage = result["usage_descriptor"]
    if not isinstance(usage, dict) or set(usage) != {"path", "sha256"}:
        raise ValueError(f"{project_root}: malformed usage_descriptor")
    usage_path = project_root / str(usage["path"])
    if not usage_path.is_file():
        raise ValueError(f"{project_root}: missing {usage_path.name}")
    digest = hashlib.sha256(usage_path.read_bytes()).hexdigest()
    if digest != usage["sha256"]:
        raise ValueError(f"{usage_path}: digest does not match result.json")
    document = parse_simple_yaml(usage_path.read_text(encoding="utf-8"))
    if document.get("version") != 1 or not isinstance(document.get("providers"), list):
        raise ValueError(f"{usage_path}: expected version 1 and a providers list")
    if not document["providers"]:
        raise ValueError(f"{usage_path}: at least one provider is required")
    described_ports: list[str] = []
    for index, provider in enumerate(document["providers"]):
        if not isinstance(provider, dict) or set(provider) != USAGE_KEYS:
            raise ValueError(
                f"{usage_path}: provider {index} must contain exactly {sorted(USAGE_KEYS)!r}"
            )
        if not isinstance(provider["port"], str) or not provider["port"]:
            raise ValueError(f"{usage_path}: provider {index} has an invalid port")
        if not isinstance(provider["provider"], str) or ":" not in provider["provider"]:
            raise ValueError(f"{usage_path}: provider {index} needs a module:object reference")
        if provider["binding_style"] not in {
            "explicit_injection",
            "self_installed",
            "external_fixture",
            "other",
        }:
            raise ValueError(f"{usage_path}: provider {index} has an invalid binding_style")
        for scalar in ("state_scope", "cleanup"):
            if not isinstance(provider[scalar], str) or not provider[scalar]:
                raise ValueError(f"{usage_path}: provider {index} has an invalid {scalar}")
        for sequence in ("fuzz_dimensions", "assertions", "bypass_limits"):
            values = provider[sequence]
            if not isinstance(values, list) or not all(
                isinstance(value, str) and value for value in values
            ):
                raise ValueError(f"{usage_path}: provider {index} has an invalid {sequence}")
        described_ports.append(provider["port"])
    if len(described_ports) != len(set(described_ports)):
        raise ValueError(f"{usage_path}: provider ports must be unique")

    manifest_path = project_root / "specs" / "program_model" / "spec_manifest.yaml"
    manifest = parse_simple_yaml(manifest_path.read_text(encoding="utf-8"))
    effect_ports = sorted(
        str(name)
        for name, definition in manifest.get("ports", {}).items()
        if isinstance(definition, dict) and definition.get("role") == "effect"
    )
    if sorted(described_ports) != effect_ports:
        raise ValueError(
            f"{usage_path}: described ports {sorted(described_ports)!r} do not match "
            f"generated effect ports {effect_ports!r}"
        )


def _validate_result(project: str, run_id: str, result_path: Path) -> dict[str, Any]:
    result = _read_json(result_path)
    missing = REQUIRED_RESULT_KEYS - set(result)
    if missing:
        raise ValueError(f"{result_path}: missing keys {sorted(missing)!r}")
    if result["schema_version"] != 1:
        raise ValueError(f"{result_path}: unsupported schema_version")
    if result["project"] != project or result["status"] != "pass":
        raise ValueError(f"{result_path}: project/status mismatch")
    if result["run_id"] != run_id:
        raise ValueError(f"{result_path}: run_id does not match requested run")
    contract = result["provider_contract"]
    if contract != {"name": "EffectProvider.bind", "version": 1}:
        raise ValueError(f"{result_path}: wrong provider contract")
    if not isinstance(result["command"], list) or not all(
        isinstance(item, str) and item for item in result["command"]
    ):
        raise ValueError(f"{result_path}: command must be a non-empty string list")
    if not isinstance(result["commit"], str) or not result["commit"]:
        raise ValueError(f"{result_path}: commit must be a non-empty string")
    if isinstance(result["seed"], bool) or not isinstance(result["seed"], int):
        raise ValueError(f"{result_path}: seed must be an integer")
    if isinstance(result["duration_seconds"], bool) or not isinstance(
        result["duration_seconds"], (int, float)
    ) or result["duration_seconds"] < 0:
        raise ValueError(f"{result_path}: duration_seconds must be non-negative")
    _nonnegative_counts(result_path, result["cases"], ("generated", "control_points", "external"))
    _nonnegative_counts(result_path, result["controls"], ("passed", "total"))
    _nonnegative_counts(result_path, result["mutants"], ("killed", "total"))
    _nonnegative_counts(result_path, result["replay"], ("attempted", "exact"))
    _nonnegative_counts(result_path, result["cleanup"], ("checked", "clean"))
    if result["controls"]["passed"] != result["controls"]["total"]:
        raise ValueError(f"{result_path}: not all controls passed")
    if result["mutants"]["killed"] != result["mutants"]["total"]:
        raise ValueError(f"{result_path}: not all mutants were killed")
    if result["replay"]["attempted"] != result["replay"]["exact"]:
        raise ValueError(f"{result_path}: not all replays were exact")
    if result["cleanup"]["checked"] != result["cleanup"]["clean"]:
        raise ValueError(f"{result_path}: cleanup is not exact")
    if not isinstance(result["replay"].get("interpreter"), str) or not result[
        "replay"
    ]["interpreter"]:
        raise ValueError(f"{result_path}: replay interpreter is required")
    findings = result["oracle_findings"]
    if not isinstance(findings, dict) or set(findings) != {
        "tla_owned",
        "provider_owned",
        "passive_external",
    }:
        raise ValueError(f"{result_path}: malformed oracle_findings")
    if not all(isinstance(value, list) for value in findings.values()):
        raise ValueError(f"{result_path}: oracle findings must be lists")
    if not isinstance(result["limitations"], list) or not isinstance(result["artifacts"], list):
        raise ValueError(f"{result_path}: limitations/artifacts must be lists")
    _validate_usage(EXAMPLES_ROOT / project, result)
    return result


def _run_project(project: str, run_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    project_root = EXAMPLES_ROOT / project
    result_path = project_root / "evidence" / "validation-runs" / run_id / "result.json"
    if result_path.parent.exists():
        raise FileExistsError(f"refusing to overwrite {result_path.parent}")
    if project == "legacy_payment_http":
        command = [
            "uv",
            "run",
            "--project",
            str(project_root),
            "python",
            str(project_root / "validate.py"),
            "--run-id",
            run_id,
        ]
    else:
        command = [
            sys.executable,
            str(project_root / "validate.py"),
            "--run-id",
            run_id,
        ]
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=900,
    )
    process = {
        "command": command,
        "returncode": completed.returncode,
        "duration_seconds": round(time.perf_counter() - started, 6),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    if completed.returncode != 0:
        raise RuntimeError(
            f"{project} validation failed with {completed.returncode}:\n"
            f"{completed.stdout}\n{completed.stderr}"
        )
    return _validate_result(project, run_id, result_path), process


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true")
    selection.add_argument("--project", action="append", choices=PROJECTS)
    parser.add_argument(
        "--fresh-evidence",
        action="store_true",
        help="Required acknowledgement that a new, non-overwriting evidence run will be created.",
    )
    parser.add_argument("--run-id", help="Optional aggregate run id; defaults to UTC time plus git revision.")
    args = parser.parse_args()
    if not args.fresh_evidence:
        parser.error("--fresh-evidence is required; validations never overwrite prior evidence")

    projects = list(PROJECTS if args.all else dict.fromkeys(args.project))
    aggregate_id = args.run_id or _default_run_id()
    aggregate_root = EXAMPLES_ROOT / "evidence" / "validation-runs" / aggregate_id
    if aggregate_root.exists():
        raise SystemExit(f"refusing to overwrite aggregate evidence {aggregate_root}")
    aggregate_root.mkdir(parents=True)

    started = time.perf_counter()
    frozen_before = _frozen_evidence_digests()
    results: dict[str, Any] = {}
    processes: dict[str, Any] = {}
    try:
        for project in projects:
            project_run_id = f"{aggregate_id}-{project}"
            result, process = _run_project(project, project_run_id)
            results[project] = result
            processes[project] = process
        frozen_after = _frozen_evidence_digests()
        if frozen_after != frozen_before:
            before_paths = set(frozen_before)
            after_paths = set(frozen_after)
            changed = sorted(
                path
                for path in before_paths & after_paths
                if frozen_before[path] != frozen_after[path]
            )
            raise RuntimeError(
                "frozen EP-03 evidence changed: "
                f"added={sorted(after_paths - before_paths)!r}, "
                f"removed={sorted(before_paths - after_paths)!r}, changed={changed!r}"
            )
    except Exception as error:
        failure = {
            "schema_version": 1,
            "run_id": aggregate_id,
            "status": "fail",
            "projects": results,
            "processes": processes,
            "error": f"{type(error).__name__}: {error}",
        }
        (aggregate_root / "aggregate.json").write_text(
            json.dumps(failure, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        raise

    aggregate = {
        "schema_version": 1,
        "run_id": aggregate_id,
        "status": "pass",
        "projects": results,
        "processes": processes,
        "duration_seconds": round(time.perf_counter() - started, 6),
    }
    output = aggregate_root / "aggregate.json"
    output.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "projects": projects, "result": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
