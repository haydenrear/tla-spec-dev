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

from testgraphsdk import NodeResult, NodeSpec, node


SPEC = (
    NodeSpec("spec.workflow.cleanup")
    .kind("fixture")
    .depends_on("spec.workflow.repo")
    .tags("spec-workflow", "finalizer")
    .timeout("30s")
    .rerun(False)
    .side_effects("fs:tmp")
)


@node(SPEC)
def main(ctx):
    repo = Path(ctx.get("spec.workflow.repo", "repoPath") or "")
    existed = repo.exists()
    if existed:
        shutil.rmtree(repo)
    return (
        NodeResult.pass_(SPEC.id)
        .assertion("fixture repo path was published", bool(str(repo)))
        .assertion("fixture repo removed", not repo.exists())
        .metric("removedRepos", 1 if existed else 0)
    )


if __name__ == "__main__":
    main()
