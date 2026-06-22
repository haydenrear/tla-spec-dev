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
            "model/Core.tla",
            "model/Internal.tla",
            "model/External.tla",
            "model/DesiredCore.tla",
            "model/DesiredInternal.tla",
            "model/DesiredExternal.tla",
            "model/actions.yml",
            "testgraph/bindings.yml",
            "testgraph/selectors.yml",
            "testgraph/assertions.yml",
        ]
        missing = [path for path in expected if not (target / path).exists()]
        forbidden = [
            "model/Desired.tla",
            "model/Desired.cfg",
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
