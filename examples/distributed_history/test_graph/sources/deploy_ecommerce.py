# /// script
# requires-python = ">=3.11"
# dependencies = ["testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from testgraphsdk import NodeResult, NodeSpec, node


SPEC = (
    NodeSpec("ecommerce.deploy")
    .kind("testbed")
    .timeout("180s")
    .rerun(False)
    .output("baseUrl")
    .output("mode")
    .output("pid")
)


@node(SPEC)
def run(ctx):
    root = Path(__file__).resolve().parents[2]
    mode = os.environ.get("ECOMMERCE_TEST_MODE", "local")
    if mode == "k3d":
        return deploy_k3d(ctx, root)
    return deploy_local(ctx, root)


def deploy_local(ctx, root: Path) -> NodeResult:
    port = _free_port()
    db_path = ctx.report_dir / "ecommerce-local.db"
    stdout_path = ctx.report_dir / "ecommerce-service.stdout.log"
    stderr_path = ctx.report_dir / "ecommerce-service.stderr.log"
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": str(root),
            "ECOMMERCE_PORT": str(port),
            "ECOMMERCE_DB": str(db_path),
        }
    )
    stdout = stdout_path.open("wb")
    stderr = stderr_path.open("wb")
    process = subprocess.Popen(
        [sys.executable, "-m", "ecommerce_backend.service"],
        cwd=root,
        env=env,
        stdout=stdout,
        stderr=stderr,
        start_new_session=True,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        _wait_for_health(base_url)
    except Exception as exc:
        process.terminate()
        raise exc
    return (
        NodeResult.pass_(SPEC.id)
        .publish("baseUrl", base_url)
        .publish("mode", "local")
        .publish("pid", str(process.pid))
        .artifact("log", str(stdout_path))
        .artifact("log", str(stderr_path))
        .assertion("service healthy", True)
    )


def deploy_k3d(ctx, root: Path) -> NodeResult:
    missing = [name for name in ("docker", "k3d", "kubectl") if shutil.which(name) is None]
    if missing:
        return NodeResult.fail(SPEC.id, f"k3d mode requires missing tools: {', '.join(missing)}")
    log_path = ctx.report_dir / "k3d-deploy.log"
    command = f"{root / 'scripts' / 'k3d-up.sh'} && {root / 'scripts' / 'k8s-deploy.sh'}"
    with log_path.open("w", encoding="utf-8") as log:
        result = subprocess.run(["bash", "-lc", command], cwd=root, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        return NodeResult.fail(SPEC.id, f"k3d deploy failed with exit {result.returncode}").artifact("log", str(log_path))
    base_url = "http://127.0.0.1:18080"
    _wait_for_health(base_url)
    _wait_for_debug_state(base_url)
    return (
        NodeResult.pass_(SPEC.id)
        .publish("baseUrl", base_url)
        .publish("mode", "k3d")
        .publish("pid", "")
        .artifact("log", str(log_path))
        .assertion("service healthy", True)
    )


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_health(base_url: str) -> None:
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            with urlopen(base_url + "/health", timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError(f"service did not become healthy at {base_url}")


def _wait_for_debug_state(base_url: str) -> None:
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            with urlopen(base_url + "/debug/state", timeout=3) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"service did not expose projected debug state at {base_url}")


if __name__ == "__main__":
    run()
