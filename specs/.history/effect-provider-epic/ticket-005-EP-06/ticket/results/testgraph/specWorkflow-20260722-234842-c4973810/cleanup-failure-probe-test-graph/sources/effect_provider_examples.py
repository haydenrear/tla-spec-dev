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
from pathlib import Path
import sys
import time
from typing import Any

from testgraphsdk import NodeResult, NodeSpec, node, procs


SPEC = (
    NodeSpec("effect.providers.examples")
    .kind("assertion")
    .tags("effect-providers", "generated-cases", "mutation", "external", "repeatable")
    .timeout("1800s")
    .side_effects("filesystem:writes", "process:spawn", "network:loopback")
)

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples" / "effect_providers"
PROJECTS = ("atomic_publisher", "legacy_payment_http", "reminder_worker")


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def forbidden_helper_hits() -> list[str]:
    hits: list[str] = []
    forbidden = ("temporary_root_provider", "context_provider")
    for project in PROJECTS:
        root = EXAMPLES / project
        for path in sorted(root.rglob("*.py")):
            if "generated" in path.parts or "evidence" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                if token in text:
                    hits.append(f"{path.relative_to(REPO_ROOT)}:{token}")
    return hits


@node(SPEC)
def main(ctx):
    run_id = f"testgraph-{time.time_ns()}"
    environment = {
        **os.environ,
        "UV_CACHE_DIR": str(ctx.report_dir / "uv-cache"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    command = [
        sys.executable,
        str(EXAMPLES / "run_validations.py"),
        "--all",
        "--fresh-evidence",
        "--run-id",
        run_id,
    ]
    record = procs.run(
        ctx,
        "repeatable-effect-provider-validations",
        command,
        cwd=REPO_ROOT,
        env=environment,
    )
    result = NodeResult.pass_(SPEC.id)
    result.process(record).assertion(
        "repository-level repeatable validation passed",
        record.exit_code == 0,
    )

    aggregate_path = EXAMPLES / "evidence" / "validation-runs" / run_id / "aggregate.json"
    if record.exit_code != 0 or not aggregate_path.is_file():
        return result.assertion(
            "aggregate evidence was written",
            False,
        )

    aggregate = load(aggregate_path)
    projects = aggregate.get("projects", {})
    result.assertion(
        "aggregate contains three passing independent projects",
        aggregate.get("status") == "pass"
        and set(projects) == set(PROJECTS)
        and all(projects[name]["status"] == "pass" for name in PROJECTS),
    )
    result.assertion(
        "all examples use the replacement generic provider contract",
        all(
            projects[name]["provider_contract"]
            == {"name": "EffectProvider.bind", "version": 1}
            for name in PROJECTS
        )
        and not forbidden_helper_hits(),
    )

    controls_passed = sum(projects[name]["controls"]["passed"] for name in PROJECTS)
    controls_total = sum(projects[name]["controls"]["total"] for name in PROJECTS)
    mutants_killed = sum(projects[name]["mutants"]["killed"] for name in PROJECTS)
    mutants_total = sum(projects[name]["mutants"]["total"] for name in PROJECTS)
    replays_exact = sum(projects[name]["replay"]["exact"] for name in PROJECTS)
    replays_attempted = sum(projects[name]["replay"]["attempted"] for name in PROJECTS)
    cleanup_clean = sum(projects[name]["cleanup"]["clean"] for name in PROJECTS)
    cleanup_checked = sum(projects[name]["cleanup"]["checked"] for name in PROJECTS)
    external_cases = sum(projects[name]["cases"]["external"] for name in PROJECTS)

    result.assertion(
        "controls and fixed mutant catalogs are green",
        controls_total > 0
        and controls_passed == controls_total
        and all(projects[name]["mutants"]["total"] >= 12 for name in PROJECTS)
        and mutants_killed == mutants_total,
    )
    result.assertion(
        "exact replay and cleanup survive repeated use",
        replays_attempted > 0
        and replays_exact == replays_attempted
        and cleanup_checked > 0
        and cleanup_clean == cleanup_checked,
    )
    result.assertion(
        f"all 70 real-boundary cases are represented (observed {external_cases})",
        external_cases == 70,
    )

    ownership = {
        key: sum(
            len(projects[name]["oracle_findings"][key]) for name in PROJECTS
        )
        for key in ("tla_owned", "provider_owned", "passive_external")
    }
    result.assertion(
        f"results distinguish all three oracle ownership layers {ownership}",
        all(count > 0 for count in ownership.values()),
    )
    result.assertion(
        "surviving limitations remain explicit",
        all(projects[name]["limitations"] for name in PROJECTS),
    )

    result = (
        result.metric("projectsValidated", len(projects))
        .metric("fixedMutantsUnique", 36)
        .metric("effectfulMutantExecutionsKilled", mutants_killed)
        .metric("effectfulMutantExecutionsTotal", mutants_total)
        .metric("exactReplays", replays_exact)
        .metric("cleanupChecks", cleanup_clean)
        .metric("externalCasesValidated", external_cases)
        .artifact("aggregate-results", str(aggregate_path))
    )
    for name in PROJECTS:
        project_result = (
            EXAMPLES
            / name
            / "evidence"
            / "validation-runs"
            / f"{run_id}-{name}"
            / "result.json"
        )
        result.artifact(f"{name}-result", str(project_result))
    return result


if __name__ == "__main__":
    main()
