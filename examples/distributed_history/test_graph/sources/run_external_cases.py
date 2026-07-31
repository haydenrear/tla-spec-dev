# /// script
# requires-python = ">=3.11"
# dependencies = ["testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from testgraphsdk import NodeResult, NodeSpec, ProcessRecord, node


SPEC = (
    NodeSpec("ecommerce.external_cases")
    .kind("action")
    .depends_on("ecommerce.deploy")
    .timeout("900s")
    .rerun(False)
    .output("workDir")
    .output("generatedRoot")
    .output("traceManifest")
)


@node(SPEC)
def run(ctx):
    root = Path(__file__).resolve().parents[2]
    # VAL-11: TLA_SPEC_DEV_ROOT points a standalone checkout of this example
    # at its toolchain; the fallback assumes the embedded-copy layout inside
    # the tla-spec-dev repository.
    repo = Path(os.environ.get("TLA_SPEC_DEV_ROOT", root.parents[1])).resolve()
    base_url = ctx.get("ecommerce.deploy", "baseUrl")
    if not base_url:
        return NodeResult.fail(SPEC.id, "missing baseUrl from ecommerce.deploy")

    work_dir = ctx.report_dir / "external-case-work"
    generated_root = ctx.report_dir / "generated"
    trace_manifest = generated_root / "testgraph" / "traces" / "manifest.json"
    log_path = ctx.report_dir / "external-cases.log"
    # ESC-MO005-03: the envelope has to say something about the TREE this run
    # read. Without it a run whose spec inputs were replaced mid-flight is
    # indistinguishable from one that found a real defect -- which is how a red
    # record survived as evidence for a defect that did not exist.
    input_digest_path = ctx.report_dir / "spec-input-digest.json"
    regenerate_command = [
        sys.executable,
        str(root / "scripts" / "regenerate_tlc_cases.py"),
        "--out",
        str(generated_root),
    ]
    command = [
        sys.executable,
        str(repo / "scripts" / "run_generated_case_adapters.py"),
        str(generated_root / "testgraph" / "ecommerce_external_cases"),
        "--mapping",
        str(root / "specs" / "program_model" / "testgraph_bindings.yml"),
        "--view",
        "external",
        "--batch",
        "--work-dir",
        str(work_dir),
        "--import-root",
        str(root),
        "--input-digest-out",
        str(input_digest_path),
    ]
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["ECOMMERCE_BASE_URL"] = base_url
    result = None
    with log_path.open("w", encoding="utf-8") as log:
        log.write("$ " + " ".join(regenerate_command) + "\n")
        regenerate_result = subprocess.run(regenerate_command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
        if regenerate_result.returncode == 0:
            log.write("$ " + " ".join(command) + "\n")
            result = subprocess.run(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
    regenerate_record = ProcessRecord(
        label="regenerate TLC case package",
        command=regenerate_command,
        exit_code=regenerate_result.returncode,
        log_path=str(log_path),
    )
    if regenerate_result.returncode != 0:
        return (
            NodeResult.fail(SPEC.id, f"TLC case generation failed with exit {regenerate_result.returncode}")
            .process(regenerate_record)
            .artifact("log", str(log_path))
            .publish("generatedRoot", str(generated_root))
        )
    if result is None:
        return NodeResult.fail(SPEC.id, "adapter batch did not run").process(regenerate_record).artifact("log", str(log_path))

    record = ProcessRecord(label="external adapter batch", command=command, exit_code=result.returncode, log_path=str(log_path))

    # Named reason first. A tree that was rewritten mid-run produces case
    # failures, so evaluating those first would report the symptom and bury the
    # cause -- which is exactly the record that has to stop being written.
    input_digest = _read_input_digest(input_digest_path)
    if input_digest is not None and not input_digest.get("stable", True):
        changed = input_digest.get("changed", [])
        return (
            NodeResult.fail(
                SPEC.id,
                "inputs changed during the run: the spec tree was rewritten while the "
                f"cases that read it were running ({len(changed)} files: {', '.join(changed[:5])}"
                f"{', ...' if len(changed) > 5 else ''}). This run's verdict is not evidence "
                "about the program.",
            )
            .process(regenerate_record)
            .process(record)
            .artifact("log", str(log_path))
            .artifact("specInputDigest", str(input_digest_path))
            .publish("specInputDigestBefore", str(input_digest.get("before", "")))
            .publish("specInputDigestAfter", str(input_digest.get("after", "")))
            .publish("specInputsChanged", json.dumps(changed))
        )

    expected_cases = _expected_case_names(trace_manifest)
    executed_cases = _executed_case_names(work_dir)
    node_result = (
        NodeResult.pass_(SPEC.id)
        .process(regenerate_record)
        .process(record)
        .artifact("log", str(log_path))
        .artifact("traceManifest", str(trace_manifest))
        .publish("workDir", str(work_dir))
        .publish("generatedRoot", str(generated_root))
        .publish("traceManifest", str(trace_manifest))
        .publish("caseNames", json.dumps(executed_cases))
        .publish("expectedCaseNames", json.dumps(expected_cases))
        .metric("expectedCaseCount", len(expected_cases))
        .metric("executedCaseCount", len(executed_cases))
        .artifact("specInputDigest", str(input_digest_path))
        .publish("specInputDigestBefore", str((input_digest or {}).get("before", "")))
        .publish("specInputDigestAfter", str((input_digest or {}).get("after", "")))
    )
    node_result.assertion(
        "spec inputs unchanged during the run",
        input_digest is not None and bool(input_digest.get("stable")),
    )
    node_result.assertion("external cases passed", result.returncode == 0)
    node_result.assertion("all generated external cases wrote program state", executed_cases == expected_cases)
    if result.returncode != 0:
        return (
            NodeResult.fail(SPEC.id, f"external cases failed with exit {result.returncode}")
            .process(regenerate_record)
            .process(record)
            .artifact("log", str(log_path))
            .artifact("traceManifest", str(trace_manifest))
            .publish("workDir", str(work_dir))
            .publish("generatedRoot", str(generated_root))
            .publish("traceManifest", str(trace_manifest))
            .publish("caseNames", json.dumps(executed_cases))
            .publish("expectedCaseNames", json.dumps(expected_cases))
            .metric("expectedCaseCount", len(expected_cases))
            .metric("executedCaseCount", len(executed_cases))
        )
    if executed_cases != expected_cases:
        return (
            NodeResult.fail(
                SPEC.id,
                f"external case evidence mismatch: executed={executed_cases}, expected={expected_cases}",
            )
            .process(regenerate_record)
            .process(record)
            .artifact("log", str(log_path))
            .artifact("traceManifest", str(trace_manifest))
            .publish("workDir", str(work_dir))
            .publish("generatedRoot", str(generated_root))
            .publish("traceManifest", str(trace_manifest))
            .publish("caseNames", json.dumps(executed_cases))
            .publish("expectedCaseNames", json.dumps(expected_cases))
            .metric("expectedCaseCount", len(expected_cases))
            .metric("executedCaseCount", len(executed_cases))
        )
    return node_result


def _read_input_digest(path: Path) -> dict | None:
    """The digest record the adapter runner writes, or None when it wrote none.

    None is not "stable": an older runner writes nothing, and this node treats
    that as an unanswered question rather than as an answer. The assertion above
    fails on None for the same reason.
    """
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _expected_case_names(manifest: Path) -> list[str]:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    return sorted(Path(name).stem for name in payload["traces"])


def _executed_case_names(work_dir: Path) -> list[str]:
    return sorted(
        json.loads(path.read_text(encoding="utf-8"))["case"]
        for path in (work_dir / "case-work").glob("*/program-state.json")
    )


if __name__ == "__main__":
    run()
