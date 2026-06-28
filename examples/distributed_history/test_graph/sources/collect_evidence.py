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


K3D_EXPECTED_TRAFFIC = {
    "gateway": {
        "/accounts": {201},
        "/cart/items": {202, 404},
        "/checkout": {200, 202, 404, 409},
        "/worker/drain": {200},
    },
    "account": {"/accounts": {201}},
    "cart": {"/cart/items": {202, 404}},
    "checkout": {"/checkout": {200, 202, 404, 409}},
    "worker": {"/worker/drain": {200}},
    "database": {
        "/accounts": {201},
        "/cart/items": {202, 404},
        "/checkout": {200, 202, 404, 409},
        "/worker/drain": {200},
    },
    "queue": {
        "/queue/enqueue": {202},
        "/queue/drain": {200},
    },
}

LOCAL_EXPECTED_TRAFFIC = {
    "monolith": {
        "/accounts": {201},
        "/cart/items": {202, 404},
        "/checkout": {200, 202, 404, 409},
        "/worker/drain": {200},
    }
}


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
    mode = ctx.get("ecommerce.deploy", "mode") or "k3d"
    with urlopen(base_url + "/debug/state", timeout=5) as response:
        state = json.loads(response.read().decode("utf-8"))
    artifact = ctx.report_dir / "ecommerce-final-state.json"
    artifact.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with urlopen(base_url + "/debug/traffic", timeout=10) as response:
        traffic = json.loads(response.read().decode("utf-8"))
    traffic_artifact = ctx.report_dir / "ecommerce-service-traffic.json"
    traffic_artifact.write_text(json.dumps(traffic, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    work_dir = ctx.get("ecommerce.external_cases", "workDir")
    if not work_dir:
        return NodeResult.fail(SPEC.id, "missing workDir from ecommerce.external_cases")
    trace_manifest = ctx.get("ecommerce.external_cases", "traceManifest")
    if not trace_manifest:
        return NodeResult.fail(SPEC.id, "missing traceManifest from ecommerce.external_cases")
    assertion_records = _load_assertion_records(Path(work_dir))
    expected_cases = _expected_external_trace_names(Path(trace_manifest))
    observed_cases = sorted(str(record.get("case")) for record in assertion_records)
    assertion_artifact = ctx.report_dir / "projected-program-states.json"
    assertion_artifact.write_text(json.dumps(assertion_records, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    all_matched = bool(assertion_records) and all(record.get("matched") is True for record in assertion_records)
    node_result = (
        NodeResult.pass_(SPEC.id)
        .artifact("json", str(artifact))
        .artifact("json", str(assertion_artifact))
        .artifact("json", str(traffic_artifact))
        .metric("projectedAssertionFiles", len(assertion_records))
        .assertion("state projected", isinstance(state, dict))
        .assertion("projected assertion files written", observed_cases == expected_cases)
        .assertion("projected states matched", all_matched)
    )
    expected_traffic = K3D_EXPECTED_TRAFFIC if mode == "k3d" else LOCAL_EXPECTED_TRAFFIC
    for role, path_statuses in expected_traffic.items():
        for path, statuses in path_statuses.items():
            node_result.assertion(
                f"{role} received {path} statuses {sorted(statuses)}",
                _observed_statuses(traffic, role, path).issuperset(statuses),
            )
    return node_result


def _load_assertion_records(work_dir: Path) -> list[dict]:
    records = []
    for path in sorted((work_dir / "case-work").glob("*/program-state.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


def _expected_external_trace_names(manifest: Path) -> list[str]:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    return sorted(Path(name).stem for name in payload["traces"])


def _observed_statuses(traffic: dict, role: str, path: str) -> set[int]:
    records = traffic.get("traffic", {}).get(role, [])
    return {
        int(record["status"])
        for record in records
        if record.get("method") == "POST" and record.get("path") == path and "response" in record
    }


if __name__ == "__main__":
    run()
