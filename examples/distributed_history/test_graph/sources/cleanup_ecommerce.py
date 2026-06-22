# /// script
# requires-python = ">=3.11"
# dependencies = ["testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

import os
import signal
import subprocess
from pathlib import Path

from testgraphsdk import NodeResult, NodeSpec, node


SPEC = (
    NodeSpec("ecommerce.cleanup")
    .kind("fixture")
    .depends_on("ecommerce.evidence")
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
    if os.environ.get("ECOMMERCE_DELETE_K3D", "0") != "1":
        return NodeResult.pass_(SPEC.id).log("leaving k3d cluster running; set ECOMMERCE_DELETE_K3D=1 to delete it")
    log_path = ctx.report_dir / "k3d-cleanup.log"
    with log_path.open("w", encoding="utf-8") as log:
        result = subprocess.run(
            ["k3d", "cluster", "delete", os.environ.get("ECOMMERCE_K3D_CLUSTER", "ecommerce-history")],
            stdout=log,
            stderr=subprocess.STDOUT,
        )
    return NodeResult.pass_(SPEC.id).artifact("log", str(log_path)).assertion("k3d cluster deleted", result.returncode == 0)


if __name__ == "__main__":
    run()
