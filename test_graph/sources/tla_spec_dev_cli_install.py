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
    # SI-01 set SKILL_DIR to the skill surface (source_repo/skills/spec-double-2)
    # because that is where the installer lived. SI-11 moved the two
    # `skill-script:` deps to the PLUGIN manifest and their installers to the
    # plugin root, because a skill-script dep is resolved by the INSTALLED UNIT's
    # name and a contained skill's name never reaches the resolver at all
    # (SIS-W2-F-05). So the real install environment is the plugin's dir and the
    # plugin's name, and this node reproduces the real one.
    #
    # This node is why that matters here: when it failed, the graph's cleanup
    # node ran and deleted 27 tracked files of test_graph/ itself, taking the
    # next two graphs with it. A stale path in this file does not just fail a
    # check.
    plugin_dir = source_repo
    bin_dir = ctx.report_dir / "tla-spec-dev-bin"
    cache_dir = ctx.report_dir / "tla-spec-dev-cache"
    env = {
        **os.environ,
        "SKILL_MANAGER_BIN_DIR": str(bin_dir),
        "SKILL_MANAGER_CACHE_DIR": str(cache_dir),
        "SKILL_DIR": str(plugin_dir),
        "SKILL_NAME": "tla-spec-dev",
    }

    result = NodeResult.pass_(SPEC.id)
    record = procs.run(
        ctx,
        "install-tla-spec-dev",
        ["bash", str(plugin_dir / "skill-scripts" / "install-tla-spec-dev.sh")],
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
