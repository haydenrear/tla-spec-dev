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
    .tags("spec-workflow", "git")
    .timeout("60s")
    .side_effects("filesystem:writes", "git:writes")
    .output("repoPath", "string")
    .output("sourceRepo", "string")
    .output("ticketId", "string")
)


PROGRAM_TLA = """----------------------------- MODULE ProgramModel -----------------------------
EXTENDS TLC

VARIABLES accepted

vars == <<accepted>>

Init == accepted = FALSE

Accept == accepted' = TRUE

Next == Accept

Spec == Init /\\ [][Next]_vars

AcceptedBoolean == accepted \\in BOOLEAN

=============================================================================
"""


@node(SPEC)
def main(ctx):
    source_repo = Path(__file__).resolve().parents[2]
    repo_dir = ctx.report_dir / "fixture-repos" / "spec-workflow-repo"
    if repo_dir.exists():
        shutil.rmtree(repo_dir)
    specs = repo_dir / "specs" / "program_model"
    specs.mkdir(parents=True)
    (specs / "ProgramModel.tla").write_text(PROGRAM_TLA, encoding="utf-8")
    (specs / "MC.cfg").write_text("SPECIFICATION Spec\nINVARIANTS AcceptedBoolean\n", encoding="utf-8")
    (specs / "spec_manifest.yaml").write_text(
        "module: ProgramModel\npackage: program_model_cases\n",
        encoding="utf-8",
    )

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
        .assertion("program model exists", (specs / "ProgramModel.tla").is_file())
        .artifact("fixture-repo", str(repo_dir))
        .publish("repoPath", str(repo_dir))
        .publish("sourceRepo", str(source_repo))
        .publish("ticketId", "FLOW-1")
    )


if __name__ == "__main__":
    main()
