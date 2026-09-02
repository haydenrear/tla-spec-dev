#!/usr/bin/env python3
"""Run the distributed_history example and validate projected-state evidence.

RETIRED STEP: the mutation kill test (MF-016 oracle 4)
------------------------------------------------------
`main` used to call `validate_kill_test()`, which shelled out to
`scripts/run_kill_test.py`. **That script does not exist.** `CA-04` (6bf1687)
deliberately cut the oracle-4 gate -- the `kill_test` variable, the
`RunKillTest` action, the `KillTestVerdictRequiresBudgets` invariant,
`RunKillTestAdapter`, `kill_rate_floor`, the `mutation_write` port and three
mutant catalogues -- and deleted the runner with them, retaining
`scripts/kill_test.py` only as the catalogue parser a disproof still depends on.
This caller was not cut with it, so the step could only ever fail:

    can't open file '.../scripts/run_kill_test.py': [Errno 2] No such file

Nothing was red, and the reason is worth keeping: this file had ALREADY been
dead one step earlier, refused by the `spec_tree` rule before it ever reached
the kill test (see `_driver_generated_root`). Two dead steps stacked, and the
first hid the second.

The measurement the step recorded is kept here rather than lost with it. The
last real end-to-end run scored **0.571 (4/7)** against a 0.8 floor, with three
survivors, each a true finding about the example's representation:

  * `store-projection_store` -> refine `projections` / `ProjectOrder`. No
    generated case distinguishes the projected status, so the read model's
    advance is unmodeled.
  * `inv-InternalInvariant`  -> refine `orders` / `Checkout`. No generated case
    checks out against a nonexistent account, so referential integrity is
    unexercised.
  * `inv-Invariant`          -> refine `responses` / `SubmitCreateAccount`. The
    HTTP boundary is genuinely outside the in-process internal corpus; the
    external corpus is what must cover it.

Those are still open. Refining the model until they die is real work; the floor
was never lowered and the survivors were never waived, because doing either is
the degeneracy the kill test existed to prevent.
"""

from __future__ import annotations

import argparse
import importlib.util
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


def _driver_generated_root(example_root: Path) -> Path:
    """Where the example's own driver writes -- ASKED, not repeated.

    This line used to read ``test_graph/build/generated/validation``, and
    `#301`'s ``spec_tree`` rule refused it: the port declares target
    ``**/specs/**``, so a write outside a ``specs/`` directory is an undeclared
    effect. `#314` moved the DRIVER's default under ``specs/generated`` and this
    file, which overrides that default on the command line, was not moved with
    it. The flagship example's top-level validation has been dead since:

        ERROR: --out must write under a `specs/` directory ...

    Nothing was red for it. The pin added with `#314`
    (``tests/test_example_drivers_write_inside_spec_tree.py``) asserts a
    driver's DEFAULT is acceptable, and this caller never uses the default.

    So the path is read out of the driver rather than spelled again here. That
    is the E-14 lesson applied: the same rename orphaned a consumer that had
    repeated the string, and the repair was to import the value instead of
    retyping it. A second copy of a path is a second thing to forget.
    """
    driver = example_root / "scripts" / "regenerate_tlc_cases.py"
    if driver.is_file():
        spec = importlib.util.spec_from_file_location("_dh_regenerate", driver)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except Exception:  # pragma: no cover - a broken driver is its own error
                pass
            else:
                default = getattr(module, "DEFAULT_GENERATED_DIR", None)
                if default is not None:
                    return Path(default)
    # The driver could not be read. Fall back to the layout `#314` chose, and
    # say so rather than silently reverting to the refused path.
    return example_root / "specs" / "generated"

DEFAULT_EXAMPLE_ROOT = REPO_ROOT / "examples" / "distributed_history"
# VAL-11: these are set from the target example path in main(); the defaults
# keep module-level readers working when the embedded copy is the target.
EXAMPLE_ROOT = DEFAULT_EXAMPLE_ROOT
TEST_GRAPH_ROOT = EXAMPLE_ROOT / "test_graph"
GENERATED_ROOT = _driver_generated_root(EXAMPLE_ROOT)
CLUSTER_NAME = "ecommerce-history"

#: The one line the negative projected-state control rewrites, and the value it
#: rewrites it to. Named here so the fixture and the refusal that guards it read
#: the same string.
REAL_EXPECTED_PROJECTION = (
    "expected_projection: specs.program_model.adapters:ExpectedClusterProjection"
)
WRONG_EXPECTED_PROJECTION = "expected_projection: wrong_projection:WrongExpectedProjection"


def run(command: list[str], *, cwd: Path = REPO_ROOT, env: dict[str, str] | None = None) -> None:
    # flush=True: the child writes straight to the shared stdout, so an
    # unflushed echo would appear after the output of the command it announces.
    print("$ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "example_root",
        nargs="?",
        type=Path,
        default=DEFAULT_EXAMPLE_ROOT,
        help=(
            "Path to the distributed_history example to validate. Defaults to "
            "the copy embedded in this repository; pass a standalone checkout "
            "to validate it instead (VAL-11). Pair with TLA_SPEC_DEV_ROOT when "
            "the example does not live inside the toolchain repository."
        ),
    )
    parser.add_argument("--mode", choices=["local", "k3d"], default="k3d")
    parser.add_argument("--keep-k3d", action="store_true", help="Leave the k3d cluster and image after a k3d run.")
    args = parser.parse_args()

    global EXAMPLE_ROOT, TEST_GRAPH_ROOT, GENERATED_ROOT
    EXAMPLE_ROOT = args.example_root.resolve()
    if not (EXAMPLE_ROOT / "specs" / "program_model").is_dir():
        raise SystemExit(
            f"ERROR: {EXAMPLE_ROOT} does not look like a distributed_history "
            "example (missing specs/program_model)"
        )
    TEST_GRAPH_ROOT = EXAMPLE_ROOT / "test_graph"
    GENERATED_ROOT = _driver_generated_root(EXAMPLE_ROOT)

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
            mapping = tmp_path / "wrong_bindings.yml"
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
    """The REAL external bindings, with exactly one thing wrong.

    This used to hand-write a parallel TOML copy of the binding set in the old
    `[actions.<Action>]` shape. `MF-015` then made an ``external:`` block
    declaring `production_package` and `port_bindings` mandatory, and the
    hand-written copy did not have one, so the negative control stopped
    demonstrating anything:

        negative projected-state check failed for the wrong reason:
        ERROR: external channel enforcement failed for 1 binding(s)
          problem: no external: block declaring production_package and port_bindings

    The runner caught that and refused rather than counting it as a pass, which
    is the right behaviour and the only reason this is a finding rather than a
    silent false green. It stayed unseen because this whole file had been dead
    two steps earlier (see `_driver_generated_root`).

    A control has to be the real thing with ONE fault introduced, or it is not a
    control -- so the fixture is now derived from the shipped bindings and
    changes a single line. A second hand-maintained copy of a binding set is a
    second thing to forget, and this is the third time in this epic that a
    repeated string outlived the thing it repeated.
    """
    source = EXAMPLE_ROOT / "specs" / "program_model" / "testgraph_bindings.yml"
    text = source.read_text(encoding="utf-8")
    wrong = text.replace(REAL_EXPECTED_PROJECTION, WRONG_EXPECTED_PROJECTION)
    if wrong == text:
        # A fixture that changed nothing is a control that proves nothing, and
        # it would go green for the worst possible reason. Refuse instead.
        raise SystemExit(
            f"ERROR: {source} no longer declares {REAL_EXPECTED_PROJECTION!r}, so the "
            "negative projected-state control could not introduce its fault. The "
            "control must be the real binding set with one thing wrong; update the "
            "anchor rather than letting this pass."
        )
    return wrong

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
    file_cases = sorted(
        json.loads(path.read_text(encoding="utf-8"))["case"]
        for path in per_case_files
    )
    if file_cases != expected_cases:
        raise SystemExit(f"expected per-case program-state files {expected_cases}, got {file_cases}")


def expected_external_trace_names(manifest: Path) -> list[str]:
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
