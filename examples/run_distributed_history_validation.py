#!/usr/bin/env python3
"""Run the distributed_history example and validate projected-state evidence."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_ROOT = REPO_ROOT / "examples" / "distributed_history"
TEST_GRAPH_ROOT = EXAMPLE_ROOT / "test_graph"
GENERATED_ROOT = TEST_GRAPH_ROOT / "build" / "generated" / "validation"
CLUSTER_NAME = "ecommerce-history"


def run(command: list[str], *, cwd: Path = REPO_ROOT, env: dict[str, str] | None = None) -> None:
    print("$ " + " ".join(command))
    subprocess.run(command, cwd=cwd, env=env, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["local", "k3d"], default="k3d")
    parser.add_argument("--keep-k3d", action="store_true", help="Leave the k3d cluster and image after a k3d run.")
    args = parser.parse_args()

    env = os.environ.copy()
    env["ECOMMERCE_TEST_MODE"] = args.mode
    if args.mode == "k3d":
        if args.keep_k3d:
            env["ECOMMERCE_KEEP_K3D"] = "1"
            env["ECOMMERCE_DELETE_K3D"] = "0"
        else:
            env["ECOMMERCE_DELETE_K3D"] = "1"

    cleanup_build_outputs()
    try:
        regenerate_tlc_cases()
        validate_internal_cases()
        validate_projected_state_assertion_catches_mismatch()
        run_test_graph(env)
        report_dir = latest_report_dir()
        validate_report(report_dir)
        validate_projected_state_artifacts(report_dir)
        print(f"distributed_history validation ok: mode={args.mode} report={report_dir}")
        return 0
    finally:
        if args.mode == "k3d" and not args.keep_k3d:
            cleanup_k3d()


def regenerate_tlc_cases() -> None:
    run(
        [
            sys.executable,
            str(EXAMPLE_ROOT / "scripts" / "regenerate_tlc_cases.py"),
            "--out",
            str(GENERATED_ROOT),
        ],
        cwd=EXAMPLE_ROOT,
    )


def validate_internal_cases() -> None:
    run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "run_generated_case_adapters.py"),
            str(GENERATED_ROOT / "spec-unit" / "ecommerce_internal_cases"),
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


def validate_projected_state_assertion_catches_mismatch() -> None:
    port = free_port()
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": str(EXAMPLE_ROOT),
            "ECOMMERCE_PORT": str(port),
            "ECOMMERCE_DB": f"/tmp/ecommerce-negative-{port}.db",
        }
    )
    process = subprocess.Popen(
        [sys.executable, "-m", "ecommerce_backend.service"],
        cwd=EXAMPLE_ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        base_url = f"http://127.0.0.1:{port}"
        wait_for_health(base_url)
        with tempfile.TemporaryDirectory(prefix="ecommerce-negative-") as tmp:
            tmp_path = Path(tmp)
            projection_module = tmp_path / "wrong_projection.py"
            projection_module.write_text(
                """
class WrongExpectedProjection:
    def expected_state(self, context):
        state = dict(context.case.after)
        state["accounts"] = ["wrong-account"]
        return state
""".lstrip(),
                encoding="utf-8",
            )
            mapping = tmp_path / "wrong_bindings.toml"
            mapping.write_text(wrong_projection_mapping(), encoding="utf-8")
            command = [
                sys.executable,
                str(REPO_ROOT / "scripts" / "run_generated_case_adapters.py"),
                str(GENERATED_ROOT / "testgraph" / "ecommerce_external_cases"),
                "--mapping",
                str(mapping),
                "--view",
                "external",
                "--label",
                "SubmitCreateAccount",
                "--limit",
                "1",
                "--batch",
                "--work-dir",
                str(tmp_path / "work"),
                "--import-root",
                str(EXAMPLE_ROOT),
                "--import-root",
                str(tmp_path),
            ]
            negative_env = os.environ.copy()
            negative_env["ECOMMERCE_BASE_URL"] = base_url
            print("$ " + " ".join(command) + "  # expected to fail")
            result = subprocess.run(command, cwd=EXAMPLE_ROOT, env=negative_env, text=True, capture_output=True)
            combined = result.stdout + result.stderr
            if result.returncode == 0:
                raise SystemExit("negative projected-state check unexpectedly passed")
            if "projected cluster state mismatch" not in combined:
                raise SystemExit(f"negative projected-state check failed for the wrong reason:\n{combined}")
            mismatch_files = sorted((tmp_path / "work" / "case-work").glob("*/program-state.json"))
            if len(mismatch_files) != 1:
                raise SystemExit(f"negative projected-state check did not write exactly one evidence file: {mismatch_files}")
            mismatch_file = mismatch_files[0]
            mismatch = json.loads(mismatch_file.read_text(encoding="utf-8"))
            if mismatch.get("matched") is not False:
                raise SystemExit(f"negative projected-state evidence did not record matched=false: {mismatch}")
            print("negative projected-state assertion check ok")
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


def wrong_projection_mapping() -> str:
    blocks = []
    for action, adapter in {
        "SubmitCreateAccount": "CreateAccountHttpAdapter",
        "SubmitDuplicateCreateAccount": "CreateAccountHttpAdapter",
        "SubmitAddCartItem": "AddCartItemHttpAdapter",
        "SubmitDuplicateAddCartItem": "AddCartItemHttpAdapter",
        "SubmitAddCartItemMissingAccount": "AddCartItemHttpAdapter",
        "SubmitCheckout": "CheckoutHttpAdapter",
        "SubmitCheckoutMissingAccount": "CheckoutHttpAdapter",
        "SubmitCheckoutEmptyCart": "CheckoutHttpAdapter",
        "SubmitDuplicateCheckout": "CheckoutHttpAdapter",
        "RunFulfillmentWorker": "RunFulfillmentWorkerHttpAdapter",
        "RunFulfillmentWorkerNoop": "RunFulfillmentWorkerHttpAdapter",
    }.items():
        blocks.append(
            f"""
[actions.{action}]
view = "external"
layer = "external"
controllability = "e2e_direct"
kind = "ecommerce-http"
adapter = "specs.program_model.adapters:{adapter}"
projector = "specs.program_model.adapters:ClusterStateProjector"
expected_projection = "wrong_projection:WrongExpectedProjection"
assertion = "specs.program_model.adapters:ProjectedStateAssertion"
""".strip()
        )
    return "\n\n".join(blocks) + "\n"


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
    expected_cases = expected_external_trace_names(report_dir / "generated" / "testgraph" / "traces" / "manifest.json")
    aggregate = report_dir / "projected-program-states.json"
    if not aggregate.exists():
        raise SystemExit(f"missing projected-state aggregate artifact: {aggregate}")
    records = json.loads(aggregate.read_text(encoding="utf-8"))
    record_cases = sorted(str(record.get("case")) for record in records)
    if record_cases != expected_cases:
        raise SystemExit(f"expected projected-state cases {expected_cases}, got {record_cases}")

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
    file_cases = sorted(path.parent.name for path in per_case_files)
    if file_cases != expected_cases:
        raise SystemExit(f"expected per-case program-state files {expected_cases}, got {file_cases}")


def expected_external_trace_names(manifest: Path = GENERATED_ROOT / "testgraph" / "traces" / "manifest.json") -> list[str]:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    return sorted(Path(name).stem for name in payload["traces"])


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


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_health(base_url: str) -> None:
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with urlopen(base_url + "/health", timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.1)
    raise SystemExit(f"service did not become healthy at {base_url}")


if __name__ == "__main__":
    raise SystemExit(main())
