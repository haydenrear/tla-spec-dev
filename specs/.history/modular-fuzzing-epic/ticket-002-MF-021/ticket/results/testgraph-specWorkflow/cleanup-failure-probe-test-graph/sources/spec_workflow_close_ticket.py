# /// script
# requires-python = ">=3.10"
# dependencies = ["testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from testgraphsdk import NodeResult, NodeSpec, node, procs


SPEC = (
    NodeSpec("spec.workflow.close")
    .kind("assertion")
    .depends_on("spec.workflow.spec_units")
    .tags("spec-workflow", "git")
    .timeout("60s")
    .side_effects("filesystem:writes", "git:writes")
    .output("historyDir", "string")
)


@node(SPEC)
def main(ctx):
    repo = Path(ctx.get("spec.workflow.repo", "repoPath") or "")
    ticket_id = ctx.get("spec.workflow.repo", "ticketId") or "FLOW-1"
    cli_path = Path(ctx.get("spec.workflow.repo", "cliPath") or "")
    ticket_dir = repo / "specs" / "tickets" / ticket_id
    history_dir = repo / "specs" / ".history" / "desired-ticket-workflow" / f"ticket-000-{ticket_id}"

    result = NodeResult.pass_(SPEC.id)
    close_record = procs.run(
        ctx,
        "close-ticket",
        [
            str(cli_path),
            "--spec-root",
            "specs",
            "close",
            "ticket",
            ticket_id,
            "--summary",
            "closed from Test Graph",
            "--result",
            str(ticket_dir / "results" / "tlc.txt"),
        ],
        cwd=repo,
    )
    result.process(close_record).assertion("close-ticket succeeded", close_record.exit_code == 0)

    manifest_path = history_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    manifest_artifact = ctx.report_dir / "spec-workflow-history-manifest.json"
    if manifest_path.exists():
        shutil.copy2(manifest_path, manifest_artifact)

    assertions = {
        "active ticket directory removed": not ticket_dir.exists(),
        "history directory exists": history_dir.is_dir(),
        "history contains ticket current": (history_dir / "ticket" / "current" / "Internal.tla").is_file(),
        "history contains ticket external view": (history_dir / "ticket" / "current" / "External.tla").is_file(),
        "project current promoted internal view": "CompleteTicket"
        in (repo / "specs" / "current" / "Internal.tla").read_text(encoding="utf-8"),
        "project current promoted external view": "SubmitCompleteTicket"
        in (repo / "specs" / "current" / "External.tla").read_text(encoding="utf-8"),
        "project current promoted Test Graph binding": "SubmitCompleteTicket"
        in (repo / "specs" / "current" / "testgraph_bindings.yml").read_text(encoding="utf-8"),
        "project current has spec adapter": (repo / "specs" / "current" / "spec_adapters" / "complete_ticket_adapter.py").is_file(),
        "project current has adapter test": (repo / "specs" / "current" / "tests" / "test_complete_ticket_adapter.py").is_file(),
        "project testgraph bindings merged": (repo / "specs" / "testgraph" / "bindings.yml").is_file(),
        "project test_graph sources merged": (repo / "specs" / "test_graph" / "sources" / "complete_ticket_external.py").is_file(),
        "history captured result": (history_dir / "results" / "tlc.txt").is_file(),
        "manifest records replace promotion": manifest.get("promotion", {}).get("operation") == "replace project current with ticket desired and merge ticket artifacts into project specs",
    }
    for name, ok in assertions.items():
        result.assertion(name, ok)

    for label, argv in [
        ("git-add", ["git", "add", "."]),
        ("git-commit", ["git", "commit", "-m", "close ticket workflow"]),
        ("git-status", ["git", "status", "--short"]),
    ]:
        record = procs.run(ctx, label, argv, cwd=repo)
        result.process(record).assertion(f"{label} succeeded", record.exit_code == 0)
    status = subprocess.run(["git", "status", "--short"], cwd=repo, capture_output=True, text=True, check=False)
    result.assertion("git working tree clean after close commit", status.returncode == 0 and status.stdout.strip() == "")

    return (
        result
        .artifact("history-manifest", str(manifest_artifact))
        .publish("historyDir", str(history_dir))
    )


if __name__ == "__main__":
    main()
