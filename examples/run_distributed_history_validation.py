#!/usr/bin/env python3
"""Run the distributed_history example and validate projected-state evidence."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_ROOT = REPO_ROOT / "examples" / "distributed_history"
TEST_GRAPH_ROOT = EXAMPLE_ROOT / "test_graph"
CLUSTER_NAME = "ecommerce-history"


def run(command: list[str], *, cwd: Path = REPO_ROOT, env: dict[str, str] | None = None) -> None:
    print("$ " + " ".join(command))
    subprocess.run(command, cwd=cwd, env=env, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["local", "k3d"], default="local")
    parser.add_argument("--keep-k3d", action="store_true", help="Leave the k3d cluster and image after a k3d run.")
    args = parser.parse_args()

    env = os.environ.copy()
    env["ECOMMERCE_TEST_MODE"] = args.mode
    if args.mode == "k3d" and not args.keep_k3d:
        env["ECOMMERCE_DELETE_K3D"] = "1"

    cleanup_build_outputs()
    try:
        validate_internal_cases()
        run_test_graph(env)
        report_dir = latest_report_dir()
        validate_report(report_dir)
        validate_projected_state_artifacts(report_dir)
        print(f"distributed_history validation ok: mode={args.mode} report={report_dir}")
        return 0
    finally:
        if args.mode == "k3d" and not args.keep_k3d:
            cleanup_k3d()


def validate_internal_cases() -> None:
    run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "run_generated_case_adapters.py"),
            str(EXAMPLE_ROOT / "specs" / "generated" / "spec_unit" / "ecommerce_internal_cases"),
            "--mapping",
            str(EXAMPLE_ROOT / "specs" / "program_model" / "case_adapters.toml"),
            "--view",
            "internal",
            "--batch",
            "--work-dir",
            "/tmp/ecommerce-internal-work",
            "--import-root",
            str(EXAMPLE_ROOT),
        ],
        cwd=EXAMPLE_ROOT,
    )


def run_test_graph(env: dict[str, str]) -> None:
    run(
        [
            str(TEST_GRAPH_ROOT / "gradlew"),
            "--no-daemon",
            "-p",
            str(TEST_GRAPH_ROOT),
            "ecommerceExternal",
        ],
        cwd=TEST_GRAPH_ROOT,
        env=env,
    )


def latest_report_dir() -> Path:
    reports_root = TEST_GRAPH_ROOT / "build" / "validation-reports"
    reports = [path for path in reports_root.iterdir() if path.is_dir()]
    if not reports:
        raise SystemExit(f"no validation reports found under {reports_root}")
    return max(reports, key=lambda path: path.stat().st_mtime)


def validate_report(report_dir: Path) -> None:
    summary = json.loads((report_dir / "summary.json").read_text(encoding="utf-8"))
    nodes = summary.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise SystemExit(f"test graph did not pass: {report_dir / 'summary.json'}")
    failed = [
        {"nodeId": node.get("nodeId"), "status": node.get("status"), "failureMessage": node.get("failureMessage")}
        for node in nodes
        if node.get("status") != "passed"
    ]
    if failed:
        raise SystemExit(f"test graph did not pass: {failed}")


def validate_projected_state_artifacts(report_dir: Path) -> None:
    aggregate = report_dir / "projected-program-states.json"
    if not aggregate.exists():
        raise SystemExit(f"missing projected-state aggregate artifact: {aggregate}")
    records = json.loads(aggregate.read_text(encoding="utf-8"))
    if len(records) != 4:
        raise SystemExit(f"expected 4 projected-state records, got {len(records)}")

    required = {
        "case",
        "action",
        "params",
        "expected_program_state",
        "actual_projected_program_state",
        "matched",
    }
    for record in records:
        missing = sorted(required - set(record))
        if missing:
            raise SystemExit(f"projected-state record missing fields {missing}: {record}")
        if record["matched"] is not True:
            raise SystemExit(f"projected-state assertion did not match: {record['case']}")
        if record["expected_program_state"] != record["actual_projected_program_state"]:
            raise SystemExit(f"projected-state payload mismatch: {record['case']}")

    work_dir = report_dir / "external-case-work" / "case-work"
    per_case_files = sorted(work_dir.glob("*/program-state.json"))
    if len(per_case_files) != 4:
        raise SystemExit(f"expected 4 per-case program-state.json files, got {len(per_case_files)}")


def cleanup_build_outputs() -> None:
    for path in [
        TEST_GRAPH_ROOT / ".gradle",
        TEST_GRAPH_ROOT / "build",
        TEST_GRAPH_ROOT / "build-logic" / ".gradle",
        TEST_GRAPH_ROOT / "build-logic" / "build",
    ]:
        if path.exists():
            shutil.rmtree(path)
    for path in EXAMPLE_ROOT.rglob("__pycache__"):
        shutil.rmtree(path)


def cleanup_k3d() -> None:
    subprocess.run(["k3d", "cluster", "delete", CLUSTER_NAME], check=False)
    subprocess.run(["docker", "rmi", "ecommerce-history:local"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    raise SystemExit(main())
