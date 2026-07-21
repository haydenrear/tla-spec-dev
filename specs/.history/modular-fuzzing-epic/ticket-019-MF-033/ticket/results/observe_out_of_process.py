#!/usr/bin/env python3
"""MF-033 evidence driver: make the effect oracle observe out-of-process work.

This is a RESULTS-LOCAL driver, not a production script. It exists to produce
the ticket's headline measurement on this repository's own effect surface, using
only the capability added to ``scripts/effect_conformance.py`` (conflict key) and
the REAL declared ports from ``specs/current/spec_manifest.yaml``. It does not
touch the production runner or the production corpus mapping -- binding the
corpus is MF-023's surface -- so it drives one real, shelling-out production
adapter (``ScaffoldProjectAdapter``, the MF-028 measured case) directly through
its real ``subprocess.run`` spawn.

It runs the SAME adapter twice against the SAME declared ports:

  BEFORE  -- in-process EffectSandbox only (the MF-028 state): the child CLI's
             writes are invisible, so spec_tree is dead and the spawn is a
             blanket unobservable boundary.
  AFTER   -- EffectSandbox + WorkingTreeObserver: the child's writes are
             recovered out-of-process via a working-tree snapshot diff, matched
             against the declared ports, and the boundary finding is narrowed to
             the axes a filesystem diff genuinely cannot see.

Both reports are written as JSON evidence beside this file.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "specs" / "current"))

from effect_conformance import (  # noqa: E402
    EffectRecorder,
    EffectSandbox,
    WorkingTreeObserver,
    diff_effects,
    load_effect_declarations,
)
from extract_spec_manifest import load_manifest  # noqa: E402
from production_adapters import ScaffoldProjectAdapter  # noqa: E402

ACTION = "ScaffoldProject"
CASE = "mf033-scaffold-project-demo"


def declared():
    manifest = load_manifest(REPO_ROOT / "specs" / "current" / "spec_manifest.yaml")
    return load_effect_declarations(manifest)


def run_adapter(work_dir: Path, *, observe_out_of_process: bool) -> EffectRecorder:
    """Drive the real ScaffoldProject adapter's real subprocess spawn."""
    target_repo = work_dir / "target-repo"
    target_repo.mkdir(parents=True, exist_ok=True)
    recorder = EffectRecorder()
    adapter = ScaffoldProjectAdapter()
    with EffectSandbox(root=work_dir / "sandbox", recorder=recorder) as sandbox:
        with sandbox.observe(action=ACTION, case=CASE):
            if observe_out_of_process:
                # Watch the child's whole writable working area. The child CLI
                # runs with cwd=target_repo and writes specs/ under it.
                with WorkingTreeObserver(target_repo, recorder, action=ACTION, case=CASE):
                    adapter.apply(target_repo)
            else:
                adapter.apply(target_repo)
    return recorder


def report_for(recorder: EffectRecorder, decls):
    return diff_effects(
        decls,
        recorder.effects,
        cases=[CASE],
        case_actions={CASE: ACTION},
        unobservable=recorder.unobservable,
        out_of_process=recorder.out_of_process,
    )


def main() -> int:
    decls = declared()
    here = Path(__file__).resolve().parent

    with tempfile.TemporaryDirectory(prefix="mf033-before-") as before_dir:
        before = report_for(run_adapter(Path(before_dir), observe_out_of_process=False), decls)
    with tempfile.TemporaryDirectory(prefix="mf033-after-") as after_dir:
        after = report_for(run_adapter(Path(after_dir), observe_out_of_process=True), decls)

    before.write(here / "effect-conformance-before.json")
    after.write(here / "effect-conformance-after.json")

    def spec_tree_dead(report) -> bool:
        return any(d.port.port == "spec_tree" for d in report.dead_surface)

    print("=" * 78)
    print("MF-033: effect oracle observing out-of-process work on this repo's surface")
    print("=" * 78)
    print(f"declared ports: {before.declared}")
    print()
    print("--- BEFORE (in-process sandbox only; the MF-028 state) ---")
    print(before.summary())
    print(f"  spec_tree port dead? {spec_tree_dead(before)}")
    print(f"  observed effects: {len(before.observed)}  (child CLI writes are invisible)")
    print()
    print("--- AFTER (sandbox + WorkingTreeObserver out-of-process diff) ---")
    print(after.summary())
    print(f"  spec_tree port dead? {spec_tree_dead(after)}")
    oop = [e for e in after.observed if "out-of-process" in e.detail]
    spec_matches = [e for e in oop if "/specs/" in e.target]
    print(f"  out-of-process child effects recovered: {len(oop)}")
    print(f"    of which match the spec_tree glob **/specs/**: {len(spec_matches)}")
    print(f"  out-of-process coverage records: {len(after.out_of_process)} "
          f"(axes: {sorted({t for o in after.out_of_process for t in o.covered_types})})")
    print()
    print("--- residual (why the verdict is what it is) ---")
    for f in after.unobservable:
        print(f"  [{f.kind}] {f.reason}")
    print()
    print(json.dumps({
        "before_verdict": before.verdict,
        "after_verdict": after.verdict,
        "before_spec_tree_dead": spec_tree_dead(before),
        "after_spec_tree_dead": spec_tree_dead(after),
        "after_out_of_process_effects": len(oop),
        "after_spec_tree_matches": len(spec_matches),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
