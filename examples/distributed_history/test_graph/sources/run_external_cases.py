# /// script
# requires-python = ">=3.11"
# dependencies = ["testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from testgraphsdk import NodeResult, NodeSpec, ProcessRecord, node


SPEC = (
    NodeSpec("ecommerce.external_cases")
    .kind("action")
    .depends_on("ecommerce.deploy")
    .timeout("120s")
    .rerun(False)
    .output("workDir")
)


@node(SPEC)
def run(ctx):
    root = Path(__file__).resolve().parents[2]
    repo = root.parents[1]
    base_url = ctx.get("ecommerce.deploy", "baseUrl")
    if not base_url:
        return NodeResult.fail(SPEC.id, "missing baseUrl from ecommerce.deploy")

    work_dir = ctx.report_dir / "external-case-work"
    log_path = ctx.report_dir / "external-cases.log"
    command = [
        sys.executable,
        str(repo / "scripts" / "run_generated_case_adapters.py"),
        str(root / "specs" / "generated" / "testgraph" / "ecommerce_external_cases"),
        "--mapping",
        str(root / "specs" / "program_model" / "testgraph_bindings.yml"),
        "--view",
        "external",
        "--batch",
        "--work-dir",
        str(work_dir),
        "--import-root",
        str(root),
    ]
    env = os.environ.copy()
    env["ECOMMERCE_BASE_URL"] = base_url
    with log_path.open("w", encoding="utf-8") as log:
        result = subprocess.run(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
    record = ProcessRecord(label="external adapter batch", command=command, exit_code=result.returncode, log_path=str(log_path))
    node_result = NodeResult.pass_(SPEC.id).process(record).artifact("log", str(log_path)).publish("workDir", str(work_dir))
    node_result.assertion("external cases passed", result.returncode == 0)
    if result.returncode != 0:
        return NodeResult.fail(SPEC.id, f"external cases failed with exit {result.returncode}").process(record).artifact("log", str(log_path))
    return node_result


if __name__ == "__main__":
    run()
