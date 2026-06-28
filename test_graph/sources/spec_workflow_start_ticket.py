# /// script
# requires-python = ">=3.10"
# dependencies = ["testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

import sys
from pathlib import Path

from testgraphsdk import NodeResult, NodeSpec, node, procs


SPEC = (
    NodeSpec("spec.workflow.start")
    .kind("action")
    .depends_on("spec.workflow.repo")
    .tags("spec-workflow", "git")
    .timeout("60s")
    .side_effects("filesystem:writes", "git:writes")
    .output("ticketDir", "string")
)


@node(SPEC)
def main(ctx):
    repo = Path(ctx.get("spec.workflow.repo", "repoPath") or "")
    source_repo = Path(ctx.get("spec.workflow.repo", "sourceRepo") or "")
    ticket_id = ctx.get("spec.workflow.repo", "ticketId") or "FLOW-1"
    ticket_dir = repo / "specs" / "tickets" / ticket_id

    result = NodeResult.pass_(SPEC.id)
    commands = [
        (
            "scaffold-workflow",
            [
                sys.executable,
                str(source_repo / "scripts" / "new_ticket_workflow.py"),
                ticket_id,
                "Spec workflow end to end",
                "--repo-root",
                str(repo),
            ],
        ),
        (
            "start-ticket",
            [
                sys.executable,
                str(source_repo / "scripts" / "start_ticket.py"),
                ticket_id,
                "--repo-root",
                str(repo),
            ],
        ),
        ("git-add", ["git", "add", "."]),
        ("git-commit", ["git", "commit", "-m", "start ticket workflow"]),
    ]
    for label, argv in commands:
        record = procs.run(ctx, label, argv, cwd=repo)
        result.process(record).assertion(f"{label} succeeded", record.exit_code == 0)

    current_tla = ticket_dir / "current" / "ProgramModel.tla"
    desired_tla = ticket_dir / "desired" / "ProgramModel.tla"
    return (
        result
        .assertion("ticket directory exists", ticket_dir.is_dir())
        .assertion("ticket current copied", current_tla.is_file())
        .assertion("ticket desired copied from current", desired_tla.is_file() and desired_tla.read_text() == current_tla.read_text())
        .assertion("ticket metadata written", (ticket_dir / "ticket.yaml").is_file())
        .artifact("ticket-dir", str(ticket_dir))
        .publish("ticketDir", str(ticket_dir))
    )


if __name__ == "__main__":
    main()
