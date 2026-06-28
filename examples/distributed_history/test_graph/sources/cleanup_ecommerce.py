# /// script
# requires-python = ">=3.11"
# dependencies = ["testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from pathlib import Path

from testgraphsdk import NodeResult, NodeSpec, node


SPEC = (
    NodeSpec("ecommerce.cleanup")
    .kind("fixture")
    .depends_on("ecommerce.deploy")
    .tags("finalizer")
    .timeout("60s")
    .rerun(False)
)


@node(SPEC)
def run(ctx):
    mode = ctx.get("ecommerce.deploy", "mode") or "local"
    if mode == "k3d":
        return cleanup_k3d(ctx)
    pid = ctx.get("ecommerce.deploy", "pid")
    if not pid:
        return NodeResult.pass_(SPEC.id).assertion("local process pid published", False)
    try:
        os.kill(int(pid), signal.SIGTERM)
    except ProcessLookupError:
        return NodeResult.pass_(SPEC.id).assertion("local process already exited", True)
    return NodeResult.pass_(SPEC.id).assertion("local process terminated", True)


def cleanup_k3d(ctx) -> NodeResult:
    if os.environ.get("ECOMMERCE_KEEP_K3D", "0") == "1" or os.environ.get("ECOMMERCE_DELETE_K3D") == "0":
        return NodeResult.pass_(SPEC.id).log("leaving k3d cluster running because ECOMMERCE_KEEP_K3D=1 or ECOMMERCE_DELETE_K3D=0")
    cluster = os.environ.get("ECOMMERCE_K3D_CLUSTER", "ecommerce-history")
    log_path = ctx.report_dir / "k3d-cleanup.log"
    with log_path.open("w", encoding="utf-8") as log:
        result = subprocess.run(
            ["k3d", "cluster", "delete", cluster],
            stdout=log,
            stderr=subprocess.STDOUT,
        )
    remaining = _wait_for_no_k3d_containers(cluster)
    remaining_artifact = ctx.report_dir / "k3d-remaining-containers.json"
    remaining_artifact.write_text(json.dumps({"containers": remaining}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return (
        NodeResult.pass_(SPEC.id)
        .artifact("log", str(log_path))
        .artifact("json", str(remaining_artifact))
        .assertion("k3d cluster delete command succeeded", result.returncode == 0)
        .assertion("k3d containers removed", not remaining)
    )


def _wait_for_no_k3d_containers(cluster: str) -> list[str]:
    deadline = time.time() + 45
    remaining: list[str] = []
    while time.time() < deadline:
        remaining = _k3d_containers(cluster)
        if not remaining:
            return []
        time.sleep(1)
    return remaining


def _k3d_containers(cluster: str) -> list[str]:
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name=k3d-{cluster}", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return [f"docker ps failed: {result.stderr.strip()}"]
    return sorted(name for name in result.stdout.splitlines() if name)


if __name__ == "__main__":
    run()
