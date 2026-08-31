#!/usr/bin/env python3
"""Regenerate typed ports and runnable cases from the checked model."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[2]
SPEC_ROOT = PROJECT_ROOT / "specs" / "program_model"
GENERATED_ROOT = PROJECT_ROOT / "specs" / "generated"


def run(
    command: list[str],
    *,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
    metric_label: str | None = None,
) -> None:
    print("$ " + " ".join(command), flush=True)
    started = __import__("time").perf_counter()
    subprocess.run(command, cwd=PROJECT_ROOT, env=env, check=True, timeout=timeout)
    if metric_label is not None:
        elapsed = __import__("time").perf_counter() - started
        print(f"MODEL_COMMAND_WALL_SECONDS {metric_label} {elapsed:.6f}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tlc2", default=os.environ.get("TLC2", "tlc2"))
    parser.add_argument(
        "--out",
        type=Path,
        default=GENERATED_ROOT,
        help="Generated artifact root; defaults to the checked project tree.",
    )
    args = parser.parse_args()
    generated_root = args.out.resolve()

    for path in (generated_root / "reminder_contract", generated_root / "cases"):
        if path.exists():
            shutil.rmtree(path)

    run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "generate_python.py"),
            str(SPEC_ROOT / "spec_manifest.yaml"),
            "--out",
            str(generated_root),
        ]
    )

    projection_env = os.environ.copy()
    projection_env["PYTHONPATH"] = os.pathsep.join(
        [str(SPEC_ROOT), projection_env.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)
    common = [
        "--actions-metadata",
        str(SPEC_ROOT / "actions.yml"),
        "--tlc2",
        args.tlc2,
        "--state-projector",
        "tlc_projection:project_state",
        "--output-projector",
        "tlc_projection:project_output",
        "--dedupe",
        "projected",
    ]
    with tempfile.TemporaryDirectory(prefix="reminder-tlc-") as temporary:
        # RC-02 (E-08): the TLC metadir is derived from this path's PARENT and
        # rmtree'd, so a temp dir here is a destructive delete outside the tree
        # `spec_tree_delete` declares, and the refusal made the
        # effectProviderExamples test graph node RED on main.
        dot_root = generated_root / "dot"
        dot_root.mkdir(parents=True, exist_ok=True)
        run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "generate_cases_from_tlc_dump.py"),
                str(SPEC_ROOT / "Internal.tla"),
                str(SPEC_ROOT / "Internal.cfg"),
                "--out",
                str(generated_root / "cases"),
                "--package",
                "reminder_internal_cases",
                "--view",
                "internal",
                "--dot",
                str(dot_root / "Internal.dot"),
                *common,
            ],
            env=projection_env,
            timeout=120,
            metric_label="internal",
        )
        run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "generate_cases_from_tlc_dump.py"),
                str(SPEC_ROOT / "External.tla"),
                str(SPEC_ROOT / "External.cfg"),
                "--out",
                str(generated_root / "cases"),
                "--package",
                "reminder_external_cases",
                "--view",
                "external",
                "--dot",
                str(dot_root / "External.dot"),
                *common,
            ],
            env=projection_env,
            timeout=120,
            metric_label="external",
        )
    print(f"generated reminder artifacts under {generated_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
