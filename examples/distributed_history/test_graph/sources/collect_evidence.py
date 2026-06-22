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
    root = Path(__file__).resolve().parents[2]
    base_url = ctx.get("ecommerce.deploy", "baseUrl")
    if not base_url:
        return NodeResult.fail(SPEC.id, "missing baseUrl from ecommerce.deploy")
    with urlopen(base_url + "/debug/state", timeout=5) as response:
        state = json.loads(response.read().decode("utf-8"))
    artifact = ctx.report_dir / "ecommerce-final-state.json"
    artifact.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    work_dir = ctx.get("ecommerce.external_cases", "workDir")
    if not work_dir:
        return NodeResult.fail(SPEC.id, "missing workDir from ecommerce.external_cases")
    assertion_records = _load_assertion_records(Path(work_dir))
    expected_count = _expected_external_trace_count(root)
    assertion_artifact = ctx.report_dir / "projected-program-states.json"
    assertion_artifact.write_text(json.dumps(assertion_records, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    all_matched = bool(assertion_records) and all(record.get("matched") is True for record in assertion_records)
    return (
        NodeResult.pass_(SPEC.id)
        .artifact("json", str(artifact))
        .artifact("json", str(assertion_artifact))
        .metric("projectedAssertionFiles", len(assertion_records))
        .assertion("state projected", isinstance(state, dict))
        .assertion("projected assertion files written", len(assertion_records) == expected_count)
        .assertion("projected states matched", all_matched)
    )


def _load_assertion_records(work_dir: Path) -> list[dict]:
    records = []
    for path in sorted((work_dir / "case-work").glob("*/program-state.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


def _expected_external_trace_count(root: Path) -> int:
    manifest = root / "specs" / "generated" / "testgraph" / "traces" / "manifest.json"
    return int(json.loads(manifest.read_text(encoding="utf-8"))["trace_count"])


if __name__ == "__main__":
    run()
