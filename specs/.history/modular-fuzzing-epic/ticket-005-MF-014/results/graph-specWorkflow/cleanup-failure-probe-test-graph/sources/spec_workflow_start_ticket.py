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
    ticket_id = ctx.get("spec.workflow.repo", "ticketId") or "FLOW-1"
    cli_path = Path(ctx.get("spec.workflow.repo", "cliPath") or "")
    ticket_dir = repo / "specs" / "tickets" / ticket_id

    result = NodeResult.pass_(SPEC.id)
    commands = [
        (
            "cli-scaffold-project",
            [
                str(cli_path),
                "--spec-root",
                "specs",
                "scaffold",
                "project",
                "--name",
                "ProgramModel",
            ],
        ),
        (
            "cli-scaffold-workflow",
            [
                str(cli_path),
                "--spec-root",
                "specs",
                "scaffold",
                "workflow",
                ticket_id,
                "Spec workflow end to end",
            ],
        ),
        (
            "cli-open-ticket",
            [
                str(cli_path),
                "--spec-root",
                "specs",
                "open",
                "ticket",
                ticket_id,
            ],
        ),
        ("git-add", ["git", "add", "."]),
        ("git-commit", ["git", "commit", "-m", "start ticket workflow"]),
    ]
    for label, argv in commands:
        record = procs.run(ctx, label, argv, cwd=repo)
        result.process(record).assertion(f"{label} succeeded", record.exit_code == 0)

    # The accepted baseline is a three-module model with both views and both
    # adapter mappings. A single-module baseline generates no Test Graph cases,
    # so it can never be validated against its public surface.
    baseline_files = [
        "Core.tla",
        "Internal.tla",
        "Internal.cfg",
        "External.tla",
        "External.cfg",
        "actions.yml",
        "adapters.py",
        "case_adapters.toml",
        "testgraph_bindings.yml",
        "tlc_projection.py",
        "spec_manifest.yaml",
    ]
    program_model = repo / "specs" / "program_model"
    missing_baseline = [name for name in baseline_files if not (program_model / name).is_file()]

    def copied(name: str) -> bool:
        current = ticket_dir / "current" / name
        desired = ticket_dir / "desired" / name
        return (
            current.is_file()
            and desired.is_file()
            and desired.read_text() == current.read_text()
        )

    not_copied = [name for name in baseline_files if not copied(name)]

    return (
        result
        .assertion("program model scaffolded by CLI with both views", not missing_baseline)
        .assertion("project workflow scaffolded by CLI", (repo / "specs" / "desired_program_model" / "ticket_plan.yaml").is_file())
        .assertion("ticket directory exists", ticket_dir.is_dir())
        .assertion("ticket current + desired carry the whole baseline", not not_copied)
        .assertion(
            "no single-module stand-in left behind",
            not (program_model / "ProgramModel.tla").exists() and not (program_model / "MC.cfg").exists(),
        )
        .assertion("ticket metadata written", (ticket_dir / "ticket.yaml").is_file())
        .metric("baselineFilesMissing", len(missing_baseline))
        .metric("baselineFilesNotCopiedToTicket", len(not_copied))
        .artifact("ticket-dir", str(ticket_dir))
        .publish("ticketDir", str(ticket_dir))
    )


if __name__ == "__main__":
    main()
