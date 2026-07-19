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
    NodeSpec("spec.cli.help")
    .kind("assertion")
    .depends_on("spec.cli.install")
    .tags("spec-workflow", "cli")
    .timeout("60s")
)


def run_and_assert(ctx, result: NodeResult, label: str, argv: list[str], expected: list[str]) -> NodeResult:
    record = procs.run(ctx, label, argv)
    result.process(record).assertion(f"{label} succeeded", record.exit_code == 0)
    output = ""
    if record.log_path:
        output = (ctx.report_dir / record.log_path).read_text(encoding="utf-8")
    for needle in expected:
        result.assertion(f"{label} mentions {needle}", needle in output)
    return result


def run_and_assert_exit(ctx, result: NodeResult, label: str, argv: list[str], expected_exit: int, expected: list[str]) -> NodeResult:
    record = procs.run(ctx, label, argv)
    result.process(record).assertion(f"{label} exited {expected_exit}", record.exit_code == expected_exit)
    output = ""
    if record.log_path:
        output = (ctx.report_dir / record.log_path).read_text(encoding="utf-8")
    for needle in expected:
        result.assertion(f"{label} mentions {needle}", needle in output)
    return result


@node(SPEC)
def main(ctx):
    cli = Path(ctx.get("spec.cli.install", "cliPath") or "")
    result = NodeResult.pass_(SPEC.id)
    commands = [
        ("version", [str(cli), "--version"], ["tla-spec-dev 0.1.0"]),
        ("root-help", [str(cli), "--help"], ["--spec-root", "scaffold", "open", "run", "close"]),
        ("scaffold-help", [str(cli), "scaffold", "--help"], ["project", "workflow"]),
        ("project-help", [str(cli), "scaffold", "project", "--help"], ["program_model", "baseline"]),
        ("workflow-help", [str(cli), "scaffold", "workflow", "--help"], ["current", "desired_program_model"]),
        ("open-ticket-help", [str(cli), "open", "ticket", "--help"], ["ticket_name", "desired-first"]),
        ("run-spec-units-help", [str(cli), "run", "spec-unit-tests", "--help"], ["generated/adapted", "spec root"]),
        ("close-ticket-help", [str(cli), "close", "ticket", "--help"], ["append-only history", "ticket_name"]),
    ]
    for label, argv, expected in commands:
        result = run_and_assert(ctx, result, label, argv, expected)
    for command in ["scaffold", "open", "run", "close"]:
        result = run_and_assert_exit(
            ctx,
            result,
            f"incomplete-{command}",
            [str(cli), command],
            2,
            [f"incomplete command: tla-spec-dev {command}", "next:"],
        )
    return result.assertion("cli path came from install node", cli.is_file())


if __name__ == "__main__":
    main()
