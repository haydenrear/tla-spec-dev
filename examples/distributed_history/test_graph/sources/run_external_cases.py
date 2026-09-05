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



def _export(scratch_root: Path, exported_root: Path) -> None:
    """Move the generated tree out of `specs/` and leave nothing behind.

    Idempotent and never raises: this runs on the failure paths too, and a
    cleanup that can fail turns one red node into two problems.
    """
    import shutil

    try:
        if scratch_root.is_dir():
            if exported_root.exists():
                shutil.rmtree(exported_root, ignore_errors=True)
            exported_root.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(scratch_root), str(exported_root))
        # Drop the `.testgraph` parent once the last run in it is gone, so a
        # long-lived checkout does not accumulate empty run directories inside
        # its spec tree.
        parent = scratch_root.parent
        if parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()
    except OSError:
        pass


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
    # RC-02: generation writes under `specs/`, exports land in the report dir.
    #
    # This used to generate straight into `ctx.report_dir / "generated"`, and
    # `#301` refuses that -- the `spec_tree` and `spec_tree_delete` ports declare
    # target `**/specs/**`, and the generator also rmtree's a metadir derived
    # from its own output path, so a build tree is an undeclared destructive
    # write. The node had been red since, with `TLC case generation failed with
    # exit 1` as its whole account of why.
    #
    # The refusal's own remedy names this exact case: *"A Test Graph node
    # generating into its build tree wants --out <spec-root>/specs/generated/
    # testgraph/<run-id> -- pass it ABSOLUTE"*, and then *"keep only exported
    # artifacts (traces, reports) under your own report directory."* Both halves
    # are done here: generate into a per-run scratch inside the spec tree, then
    # MOVE the finished tree out to the report dir, so nothing lingers in
    # `specs/` and downstream nodes still read it where they always did.
    #
    # The scratch name is dotted so it cannot be mistaken for a view root. E-06
    # was a committed corpus one separator away from `spec-unit`; a run-scoped
    # directory sitting beside real corpora is the same hazard with a timer on it.
    scratch_root = root / "specs" / "generated" / ".testgraph" / ctx.report_dir.name
    exported_root = ctx.report_dir / "generated"
    generated_root = scratch_root
    trace_manifest = exported_root / "testgraph" / "traces" / "manifest.json"
    log_path = ctx.report_dir / "external-cases.log"
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
        # A FAILED generation still leaves a partial tree inside `specs/`, and a
        # scratch directory that outlives its run is indistinguishable from a
        # corpus to everything that looks at the spec tree afterwards.
        _export(scratch_root, exported_root)
        return (
            NodeResult.fail(SPEC.id, f"TLC case generation failed with exit {regenerate_result.returncode}")
            .process(regenerate_record)
            .artifact("log", str(log_path))
            .publish("generatedRoot", str(exported_root))
        )
    if result is None:
        _export(scratch_root, exported_root)
        return NodeResult.fail(SPEC.id, "adapter batch did not run").process(regenerate_record).artifact("log", str(log_path))

    record = ProcessRecord(label="external adapter batch", command=command, exit_code=result.returncode, log_path=str(log_path))

    # The generated tree leaves the spec directory now that it is finished:
    # `specs/` is where a spec_tree write is DECLARED, not where a build output
    # belongs. Moved rather than copied so the scratch cannot be left behind.
    _export(scratch_root, exported_root)
    generated_root = exported_root

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
