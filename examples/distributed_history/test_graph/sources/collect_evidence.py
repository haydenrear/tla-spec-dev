# /// script
# requires-python = ">=3.11"
# dependencies = ["testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

import json
from pathlib import Path
from urllib.request import urlopen

from testgraphsdk import NodeResult, NodeSpec, node


SPEC = (
    NodeSpec("ecommerce.evidence")
    .kind("evidence")
    .depends_on("ecommerce.external_cases")
    .timeout("30s")
)


@node(SPEC)
def run(ctx):
    base_url = ctx.get("ecommerce.deploy", "baseUrl")
    if not base_url:
        return NodeResult.fail(SPEC.id, "missing baseUrl from ecommerce.deploy")
    with urlopen(base_url + "/debug/state", timeout=5) as response:
        state = json.loads(response.read().decode("utf-8"))
    artifact = ctx.report_dir / "ecommerce-final-state.json"
    artifact.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return NodeResult.pass_(SPEC.id).artifact("json", str(artifact)).assertion("state projected", isinstance(state, dict))


if __name__ == "__main__":
    run()
