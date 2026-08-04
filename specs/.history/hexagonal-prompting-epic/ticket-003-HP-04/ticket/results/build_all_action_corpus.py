#!/usr/bin/env python3
"""HP-04: the corpus RC-02 could not run -- one case for EVERY modeled action.

RC-02's `build_action_covering_corpus.py` deliberately restricted itself to the
8 actions whose adapter implements `run(case, work_dir)`, because the effect
oracle ABORTED THE WHOLE RUN on the first `apply()`-only adapter it met
(RC-02-DF-03) and a corpus containing one produced no report at all. That
restriction is the thing HP-04 removes, so this builder drops it: it takes the
first edge in dump order for every action label in the real TLC state graph,
including the nine whose adapters cannot be driven by a case.

The point is not that those nine become runnable -- they do not, and HP-04 does
not pretend otherwise. The point is that the oracle now produces a REPORT over
all 18 offered actions instead of a traceback over the first 2, and that the
nine appear in it by name with a machine-readable reason instead of being
invisible.

Same caveats as RC-02's builder, unchanged: this is the action-covering subset,
not the corpus the model defines (`generate cases` on MCsmall produces 3,678,217
cases and a 7.4 GB `cases.py`, 18,391x this manifest's own cap). It is a LOWER
BOUND -- fewer cases can only exercise fewer ports.

    python3 build_all_action_corpus.py <dump.dot> <out-dir>
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from scripts import case_modules  # noqa: E402
from scripts import generate_cases_from_tlc_dump as generator  # noqa: E402


def main() -> int:
    dot = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    spec_dir = ROOT / "specs" / "current"
    tla = spec_dir / "TlaSpecDevCli.tla"

    states, edges = generator.load_dot(dot)
    print(f"dump: {len(states)} states, {len(edges)} edges")

    search_path = case_modules.resolve_search_path(tla, [])
    recipes = generator.build_recipes_for_hierarchy(tla, search_path)

    first_per_action: dict[str, object] = {}
    for edge in edges:
        first_per_action.setdefault(edge.action, edge)
    selected = [first_per_action[action] for action in sorted(first_per_action)]
    print(f"action labels in the dump: {len(first_per_action)} -- {sorted(first_per_action)}")

    keep = {edge.source for edge in selected} | {edge.target for edge in selected}
    prepared = generator.render_python_package(
        module=tla.stem,
        states={node: states[node] for node in keep},
        edges=selected,
        package_dir=out,
        view="internal",
        action_metadata={},
        labelers=[],
        state_projector=None,
        output_projector=None,
        dedupe="none",
        param_recipes=recipes,
    )
    print(f"wrote {len(prepared)} cases to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
