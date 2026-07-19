# /// script
# requires-python = ">=3.10"
# dependencies = ["testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

from pathlib import Path

from testgraphsdk import NodeResult, NodeSpec, node, procs


SPEC = (
    NodeSpec("spec.workflow.spec_units")
    .kind("assertion")
    .depends_on("spec.workflow.complete")
    .tags("spec-workflow", "git", "spec-unit")
    .timeout("60s")
    .side_effects("filesystem:writes")
)


@node(SPEC)
def main(ctx):
    repo = Path(ctx.get("spec.workflow.repo", "repoPath") or "")
    ticket_id = ctx.get("spec.workflow.repo", "ticketId") or "FLOW-1"
    cli_path = Path(ctx.get("spec.workflow.repo", "cliPath") or "")

    result = NodeResult.pass_(SPEC.id)
    record = procs.run(
        ctx,
        "cli-run-spec-unit-tests",
        [
            str(cli_path),
            "--spec-root",
            "specs",
            "run",
            "spec-unit-tests",
            "--ticket",
            ticket_id,
        ],
        cwd=repo,
    )
    result.process(record).assertion("cli spec-unit tests succeeded", record.exit_code == 0)
    output = ""
    if record.log_path:
        output = (ctx.report_dir / record.log_path).read_text(encoding="utf-8")
    return (
        result
        .assertion("spec-unit output names ticket current", f"specs/tickets/{ticket_id}/current" in output)
        .assertion("spec-unit output reports pass", "spec-unit validation passed" in output)
        .artifact("spec-unit-log", str(ctx.report_dir / record.log_path) if record.log_path else "")
    )


if __name__ == "__main__":
    main()
