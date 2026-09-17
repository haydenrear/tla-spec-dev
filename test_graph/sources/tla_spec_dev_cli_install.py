# /// script
# requires-python = ">=3.10"
# dependencies = ["testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

import os
from pathlib import Path

from testgraphsdk import NodeResult, NodeSpec, node, procs


SPEC = (
    NodeSpec("spec.cli.install")
    .kind("testbed")
    .tags("spec-workflow", "cli")
    .timeout("60s")
    .side_effects("fs:tmp")
    .output("cliPath", "string")
    .output("binDir", "string")
)


@node(SPEC)
def main(ctx):
    source_repo = Path(
        os.environ.get("TLA_SPEC_DEV_SOURCE_REPO")
        or Path(__file__).resolve().parents[2]
    )
    # SI-01: SKILL_DIR is the SKILL surface, which is no longer the repo root.
    skill_dir = source_repo / "skills" / "spec-double-2"
    bin_dir = ctx.report_dir / "tla-spec-dev-bin"
    cache_dir = ctx.report_dir / "tla-spec-dev-cache"
    env = {
        **os.environ,
        "SKILL_MANAGER_BIN_DIR": str(bin_dir),
        "SKILL_MANAGER_CACHE_DIR": str(cache_dir),
        "SKILL_DIR": str(skill_dir),
        "SKILL_NAME": "spec-double-2",
    }

    result = NodeResult.pass_(SPEC.id)
    record = procs.run(
        ctx,
        "install-tla-spec-dev",
        ["bash", str(skill_dir / "skill-scripts" / "install-tla-spec-dev.sh")],
        cwd=source_repo,
        env=env,
    )
    cli_path = bin_dir / "tla-spec-dev"
    result.process(record).assertion("install script succeeded", record.exit_code == 0)
    return (
        result
        .assertion("tla-spec-dev wrapper exists", cli_path.is_file())
        .artifact("tla-spec-dev", str(cli_path))
        .publish("cliPath", str(cli_path))
        .publish("binDir", str(bin_dir))
    )


if __name__ == "__main__":
    main()
