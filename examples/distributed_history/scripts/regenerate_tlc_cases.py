#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Regenerate distributed_history cases from TLC output."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


EXAMPLE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXAMPLE_ROOT.parents[1]
SPEC_DIR = EXAMPLE_ROOT / "specs" / "program_model"
DEFAULT_GENERATED_DIR = EXAMPLE_ROOT / "test_graph" / "build" / "generated"


def run(command: list[str]) -> None:
    print("$ " + " ".join(command))
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    subprocess.run(command, cwd=EXAMPLE_ROOT, env=env, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tlc2", default=os.environ.get("TLC2", "tlc2"), help="TLC executable. Defaults to $TLC2 or tlc2.")
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_GENERATED_DIR,
        help="Generated case root. Defaults to test_graph/build/generated.",
    )
    args = parser.parse_args()
    generated_dir = args.out if args.out.is_absolute() else EXAMPLE_ROOT / args.out
    generated_dir = generated_dir.resolve()

    for path in [
        generated_dir / "spec-unit" / "ecommerce_internal_cases",
        generated_dir / "spec_unit" / "ecommerce_internal_cases",
        generated_dir / "testgraph" / "ecommerce_external_cases",
        generated_dir / "testgraph" / "traces",
    ]:
        if path.exists():
            shutil.rmtree(path)

    common = [
        "--actions-metadata",
        str(SPEC_DIR / "actions.yml"),
        "--tlc2",
        args.tlc2,
        "--state-projector",
        "specs.program_model.tlc_projection:project_visible_state",
        "--output-projector",
        "specs.program_model.tlc_projection:project_adapter_output",
        "--dedupe",
        "projected",
    ]
    with tempfile.TemporaryDirectory(prefix="distributed-history-tlc-") as tmp:
        tmp_path = Path(tmp)
        run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "generate_cases_from_tlc_dump.py"),
                str(SPEC_DIR / "Internal.tla"),
                str(SPEC_DIR / "Internal.cfg"),
                "--out",
                str(generated_dir),
                "--package",
                "ecommerce_internal_cases",
                "--view",
                "internal",
                "--dot",
                str(tmp_path / "Internal.dot"),
                *common,
            ]
        )
        run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "generate_cases_from_tlc_dump.py"),
                str(SPEC_DIR / "External.tla"),
                str(SPEC_DIR / "External.cfg"),
                "--out",
                str(generated_dir),
                "--package",
                "ecommerce_external_cases",
                "--view",
                "external",
                "--dot",
                str(tmp_path / "External.dot"),
                *common,
            ]
        )
    run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "export_testgraph_cases.py"),
            str(generated_dir / "testgraph" / "ecommerce_external_cases"),
            "--out",
            str(generated_dir / "testgraph" / "traces"),
        ]
    )
    print(f"generated TLC-derived cases under {generated_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
