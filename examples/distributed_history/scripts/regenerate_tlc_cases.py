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
from pathlib import Path


EXAMPLE_ROOT = Path(__file__).resolve().parents[1]
# VAL-11: a standalone checkout of this example is not nested inside the
# tla-spec-dev repository, so the toolchain root cannot always be derived from
# this file's location. TLA_SPEC_DEV_ROOT overrides it; the embedded-copy
# layout (examples/distributed_history inside the toolchain repo) is the
# fallback.
REPO_ROOT = Path(os.environ.get("TLA_SPEC_DEV_ROOT", EXAMPLE_ROOT.parents[1])).resolve()
SPEC_DIR = EXAMPLE_ROOT / "specs" / "program_model"
# RC-02 (tla-spec-dev #301): `resolve_spec_tree_out` refuses any --out
# outside a `specs/` directory, because the `spec_tree` effect port declares
# target `**/specs/**` and a write anywhere else is an undeclared effect.
# This default was `test_graph/build/generated` and the refusal made this
# script unrunnable as written -- it is a committed driver with no caller,
# so nothing went red. `specs/generated/` is already in this example's
# .gitignore, and the refusal's own REMEDY names this shape.
DEFAULT_GENERATED_DIR = EXAMPLE_ROOT / "specs" / "generated"


def run(command: list[str]) -> None:
    # flush=True: the child process writes straight to the shared stdout, so an
    # unflushed echo would appear after the output of the command it announces.
    print("$ " + " ".join(command), flush=True)
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
        help="Generated case root. Must resolve under a `specs/` directory (RC-02). Defaults to specs/generated, where the committed corpus lives.",
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
    # RC-02: `--dot` is constrained the same way as `--out`, and for a stronger
    # reason -- run_tlc_dump derives the TLC metadir from the dot path's PARENT
    # and `shutil.rmtree`s it, so a dot path in a system temp dir is a
    # destructive delete outside the tree the `spec_tree_delete` port declares.
    # This used to be a TemporaryDirectory, which the refusal now rejects. The
    # dot files go beside the corpus they describe; `specs/generated/` is
    # already in this example's .gitignore, so nothing new is tracked.
    dot_dir = generated_dir / "dot"
    dot_dir.mkdir(parents=True, exist_ok=True)
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
            str(dot_dir / "Internal.dot"),
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
            str(dot_dir / "External.dot"),
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
            # VAL-09: the exporter requires --bindings (MF-015 channel
            # enforcement) and needs --manifest because the generated corpus
            # lives in a build directory, outside the spec tree that holds
            # spec_manifest.yaml.
            "--bindings",
            str(SPEC_DIR / "testgraph_bindings.yml"),
            "--manifest",
            str(SPEC_DIR / "spec_manifest.yaml"),
        ]
    )
    print(f"generated TLC-derived cases under {generated_dir}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
