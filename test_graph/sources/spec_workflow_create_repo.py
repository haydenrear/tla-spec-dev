# /// script
# requires-python = ">=3.10"
# dependencies = ["testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

import shutil
from pathlib import Path

from testgraphsdk import NodeResult, NodeSpec, node, procs


SPEC = (
    NodeSpec("spec.workflow.repo")
    .kind("testbed")
    .depends_on("spec.cli.install")
    .tags("spec-workflow", "git")
    .timeout("60s")
    .side_effects("fs:tmp")
    .output("repoPath", "string")
    .output("sourceRepo", "string")
    .output("ticketId", "string")
    .output("cliPath", "string")
)


@node(SPEC)
def main(ctx):
    source_repo = Path(__file__).resolve().parents[2]
    repo_dir = ctx.report_dir / "fixture-repos" / "spec-workflow-repo"
    cli_path = Path(ctx.get("spec.cli.install", "cliPath") or "")
    if repo_dir.exists():
        shutil.rmtree(repo_dir)
    repo_dir.mkdir(parents=True)
    (repo_dir / "README.md").write_text("# Spec Workflow Fixture\n", encoding="utf-8")

    result = NodeResult.pass_(SPEC.id)
    commands = [
        ("git-init", ["git", "init"]),
        ("git-branch", ["git", "branch", "-M", "main"]),
        ("git-email", ["git", "config", "user.email", "spec-workflow@example.invalid"]),
        ("git-name", ["git", "config", "user.name", "Spec Workflow Test"]),
        ("git-add", ["git", "add", "."]),
        ("git-commit", ["git", "commit", "-m", "initial program model"]),
    ]
    for label, argv in commands:
        record = procs.run(ctx, label, argv, cwd=repo_dir)
        result.process(record).assertion(f"{label} succeeded", record.exit_code == 0)

    return (
        result
        .assertion("installed CLI path exists", cli_path.is_file())
        .assertion("fixture repo starts without program model", not (repo_dir / "specs" / "program_model").exists())
        .artifact("fixture-repo", str(repo_dir))
        .publish("repoPath", str(repo_dir))
        .publish("sourceRepo", str(source_repo))
        .publish("ticketId", "FLOW-1")
        .publish("cliPath", str(cli_path))
    )


if __name__ == "__main__":
    main()
