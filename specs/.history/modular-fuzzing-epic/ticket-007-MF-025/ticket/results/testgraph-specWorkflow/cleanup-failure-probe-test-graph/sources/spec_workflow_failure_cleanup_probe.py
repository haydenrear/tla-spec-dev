# /// script
# requires-python = ">=3.10"
# dependencies = ["testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from testgraphsdk import NodeResult, NodeSpec, node, procs


SPEC = (
    NodeSpec("spec.workflow.failure_cleanup_probe")
    .kind("assertion")
    .depends_on("spec.workflow.close")
    .tags("spec-workflow", "failure-probe", "finalizer")
    .timeout("180s")
    .side_effects("filesystem:writes", "filesystem:delete", "git:writes")
)


PROBE_BUILD = """plugins {
    id("com.hayden.testgraphsdk.graph")
}

validationGraph {
    sourcesDir("sources")

    testGraph("cleanupFailureProbe") {
        node("sources/tla_spec_dev_cli_install.py")
        node("sources/spec_workflow_create_repo.py")
        node("sources/spec_workflow_force_failure.py")
        node("sources/spec_workflow_cleanup.py").dependsOn("spec.workflow.force_failure")
    }
}
"""


def copy_probe_project(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    ignore = shutil.ignore_patterns("build", ".gradle", "__pycache__", "*.pyc")
    for name in ["settings.gradle.kts", "gradlew", "gradle", "build-logic", "sdk", "sources"]:
        src = source / "test_graph" / name
        dst = target / name
        if src.is_dir():
            shutil.copytree(src, dst, ignore=ignore)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    (target / "build.gradle.kts").write_text(PROBE_BUILD, encoding="utf-8")


def latest_probe_run(probe_root: Path) -> Path | None:
    reports = probe_root / "build" / "validation-reports"
    if not reports.exists():
        return None
    candidates = [path for path in reports.iterdir() if path.is_dir() and path.name.startswith("cleanupFailureProbe-")]
    return max(candidates, key=lambda path: path.stat().st_mtime, default=None)


def node_by_id(summary: dict, node_id: str) -> dict:
    for node_summary in summary.get("nodes", []):
        if node_summary.get("nodeId") == node_id:
            return node_summary
    return {}


@node(SPEC)
def main(ctx):
    source_repo = Path(ctx.get("spec.workflow.repo", "sourceRepo") or "").resolve()
    probe_root = ctx.report_dir / "cleanup-failure-probe-test-graph"
    copy_probe_project(source_repo, probe_root)

    env = dict(os.environ)
    gradle_opts = env.get("GRADLE_OPTS", "")
    env["GRADLE_OPTS"] = f"{gradle_opts} -Dorg.gradle.daemon=false".strip()
    env["TLA_SPEC_DEV_SOURCE_REPO"] = str(source_repo)

    result = NodeResult.pass_(SPEC.id)
    record = procs.run(
        ctx,
        "cleanup-failure-probe",
        [str(probe_root / "gradlew"), "--console=plain", "cleanupFailureProbe"],
        cwd=probe_root,
        env=env,
    )
    result.process(record).assertion("probe graph failed as expected", record.exit_code != 0)

    run_dir = latest_probe_run(probe_root)
    summary_path = run_dir / "summary.json" if run_dir else None
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path and summary_path.exists() else {}
    repo_node = node_by_id(summary, "spec.workflow.repo")
    failure_node = node_by_id(summary, "spec.workflow.force_failure")
    cleanup_node = node_by_id(summary, "spec.workflow.cleanup")
    repo_path = Path(repo_node.get("published", {}).get("repoPath") or "")

    if run_dir:
        result.artifact("cleanup-failure-probe-report", str(run_dir / "report.md"))
        result.artifact("cleanup-failure-probe-summary", str(run_dir / "summary.json"))

    return (
        result
        .assertion("probe report was written", bool(summary))
        .assertion("repo allocation node passed", repo_node.get("status") == "passed")
        .assertion("forced downstream failure was captured", failure_node.get("status") == "failed")
        .assertion("cleanup finalizer ran after failure", cleanup_node.get("status") == "passed")
        .assertion("allocated fixture repo removed after failure", bool(str(repo_path)) and not repo_path.exists())
        .artifact("cleanup-failure-probe-root", str(probe_root))
    )


if __name__ == "__main__":
    main()
