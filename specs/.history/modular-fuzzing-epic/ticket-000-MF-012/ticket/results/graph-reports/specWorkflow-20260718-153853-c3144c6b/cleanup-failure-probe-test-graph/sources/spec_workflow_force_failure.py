# /// script
# requires-python = ">=3.10"
# dependencies = ["testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

from pathlib import Path

from testgraphsdk import NodeResult, NodeSpec, node


SPEC = (
    NodeSpec("spec.workflow.force_failure")
    .kind("assertion")
    .depends_on("spec.workflow.repo")
    .tags("spec-workflow", "failure-probe")
    .timeout("30s")
)


@node(SPEC)
def main(ctx):
    repo = Path(ctx.get("spec.workflow.repo", "repoPath") or "")
    return (
        NodeResult.fail(SPEC.id, "forced downstream failure after fixture repo allocation")
        .assertion("fixture repo exists before forced failure", repo.is_dir())
        .artifact("fixture-repo", str(repo))
    )


if __name__ == "__main__":
    main()
