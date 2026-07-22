# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest"]
# ///
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[3]
# VAL-11: TLA_SPEC_DEV_ROOT points a standalone checkout of this example at
# its toolchain; the fallback assumes the embedded-copy layout inside the
# tla-spec-dev repository.
REPO = Path(os.environ.get("TLA_SPEC_DEV_ROOT", ROOT.parents[1])).resolve()


def test_internal_adapters_run_in_batch(tmp_path):
    generated_root = _regenerate_cases(tmp_path)
    command = [
        sys.executable,
        str(REPO / "scripts" / "run_generated_case_adapters.py"),
        str(generated_root / "spec-unit" / "ecommerce_internal_cases"),
        "--mapping",
        str(ROOT / "specs" / "program_model" / "case_adapters.toml"),
        "--view",
        "internal",
        "--batch",
        "--work-dir",
        str(tmp_path / "internal-work"),
        "--import-root",
        str(ROOT),
    ]
    subprocess.run(command, check=True)


def test_external_adapters_project_cluster_state(tmp_path):
    generated_root = _regenerate_cases(tmp_path)
    env = os.environ.copy()
    env["ECOMMERCE_PORT"] = "18081"
    env["ECOMMERCE_DB"] = str(tmp_path / "ecommerce.db")
    process = subprocess.Popen(
        [sys.executable, "-m", "ecommerce_backend.service"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_health("http://127.0.0.1:18081")
        env["ECOMMERCE_BASE_URL"] = "http://127.0.0.1:18081"
        command = [
            sys.executable,
            str(REPO / "scripts" / "run_generated_case_adapters.py"),
            str(generated_root / "testgraph" / "ecommerce_external_cases"),
            "--mapping",
            str(ROOT / "specs" / "program_model" / "testgraph_bindings.yml"),
            "--view",
            "external",
            "--batch",
            "--work-dir",
            str(tmp_path / "external-work"),
            "--import-root",
            str(ROOT),
        ]
        subprocess.run(command, check=True, env=env)
    finally:
        process.terminate()
        process.wait(timeout=10)


def _regenerate_cases(tmp_path):
    generated_root = tmp_path / "generated"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "regenerate_tlc_cases.py"),
            "--out",
            str(generated_root),
        ],
        cwd=ROOT,
        check=True,
    )
    return generated_root


def _wait_for_health(base_url):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with urlopen(base_url + "/health", timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.1)
    raise AssertionError(f"service did not become healthy at {base_url}")


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__]))
