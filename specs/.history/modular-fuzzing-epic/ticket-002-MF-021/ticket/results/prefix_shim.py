"""Pre-fix behaviour shim: proves the MF-021 regression tests actually fail.

A regression test that passes both before and after a fix proves nothing. This
pytest plugin restores the EXACT pre-fix ``promote_ticket_outputs`` -- the one
that called ``replace_tree`` (``shutil.rmtree(dst)`` then copy) -- and rebinds
it into the regression module, so the suite runs unchanged against the old
behaviour.

Usage:
    uv run --with pytest -m pytest tests/test_promotion_preserves_current.py -q \
        -p specs.tickets.MF-021.results.prefix_shim
(or via -p with the file on sys.path; see prefix-failure.txt for the exact
command and its recorded output.)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.spec_evolution import merge_tree, rel  # noqa: E402


def _prefix_replace_tree(src: Path, dst: Path) -> list[dict[str, Any]]:
    """Verbatim pre-fix scripts/spec_evolution.py:369."""
    import shutil

    if dst.exists():
        shutil.rmtree(dst)
    return merge_tree(src, dst)


def _prefix_promote_ticket_outputs(active_dir: Path, specs_dir: Path) -> dict[str, Any]:
    """Verbatim pre-fix scripts/spec_evolution.py:375."""
    merged = [
        {
            "role": "current",
            "source": rel(active_dir / "desired"),
            "destination": rel(specs_dir / "current"),
            "operation": "replace",
            "files": _prefix_replace_tree(active_dir / "desired", specs_dir / "current"),
        }
    ]
    for name in ("testgraph", "test_graph"):
        source = active_dir / name
        if source.exists():
            merged.append(
                {
                    "role": name,
                    "source": rel(source),
                    "destination": rel(specs_dir / name),
                    "operation": "merge",
                    "files": merge_tree(source, specs_dir / name),
                }
            )
    return {
        "source": rel(active_dir),
        "destination": rel(specs_dir),
        "operation": "replace project current with ticket desired and merge ticket artifacts into project specs",
        "merged": merged,
    }


def pytest_collection_modifyitems(session, config, items):  # noqa: ARG001
    """Rebind the name the regression module imported, after collection."""
    for item in items:
        module = item.module
        if hasattr(module, "promote_ticket_outputs"):
            module.promote_ticket_outputs = _prefix_promote_ticket_outputs
    print("\n[prefix_shim] promote_ticket_outputs rebound to PRE-FIX replace_tree behaviour")
