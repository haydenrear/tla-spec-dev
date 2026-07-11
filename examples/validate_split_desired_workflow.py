#!/usr/bin/env python3
"""Validate the split desired-view scaffold contract."""

from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.scaffold_spec import parse_views, scaffold  # noqa: E402


def main() -> int:
    with TemporaryDirectory(prefix="tla-spec-desired-views-") as tmp:
        target = scaffold("request-flow", Path(tmp), parse_views("internal,external"))
        expected = [
            # The accepted baseline shape, flat, with both views and both
            # adapter mappings. Same shape as `tla-spec-dev scaffold project`.
            "Core.tla",
            "Internal.tla",
            "Internal.cfg",
            "External.tla",
            "External.cfg",
            "actions.yml",
            "adapters.py",
            "case_adapters.toml",
            "testgraph_bindings.yml",
            "tlc_projection.py",
            "spec_manifest.yaml",
            # Active desired overlays for an open workflow.
            "DesiredCore.tla",
            "DesiredInternal.tla",
            "DesiredExternal.tla",
        ]
        missing = [path for path in expected if not (target / path).exists()]
        forbidden = [
            "model/Desired.tla",
            "model/Desired.cfg",
            # The old divergent layout, and the single-module stand-in it implied.
            "model/Core.tla",
            "testgraph/bindings.yml",
            "RequestFlow.tla",
            "MC.cfg",
        ]
        stale = [path for path in forbidden if (target / path).exists()]
        if missing or stale:
            raise SystemExit(f"split desired scaffold failed: missing={missing} stale={stale}")

    program_model = REPO_ROOT / "examples" / "distributed_history" / "specs" / "program_model"
    stale_program_desired = [path.name for path in program_model.glob("Desired*")]
    if stale_program_desired:
        raise SystemExit(f"closed program_model still contains desired files: {stale_program_desired}")

    print("split desired workflow scaffold ok")
    print("new active workflows create DesiredCore/DesiredInternal/DesiredExternal, not Desired.tla")
    print("closed distributed_history program_model contains only Core/Internal/External")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
