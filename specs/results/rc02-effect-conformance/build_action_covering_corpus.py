#!/usr/bin/env python3
"""RC-02 reproducer: the smallest corpus of this model the effect oracle can execute.

WHY THIS EXISTS, stated before the code so it cannot be mistaken for a normal
generation step. `tla-spec-dev generate cases specs/current/TlaSpecDevCli.tla
specs/current/MCsmall.cfg` produces **3,678,217 cases** (118,573 distinct states,
average outdegree 31) and a 7.4 GB `cases.py`. That is 18,391x the manifest's own
`max_internal_cases_per_component: 200`, so the shipped generator REFUSES the
corpus (exit 2) -- and even ignoring the gate, `run effect-conformance` executes
one adapter invocation per case, so the corpus cannot be imported, let alone run.
Projection does not rescue it: dropping `lastCommand` and `result` (the two
variables `adapter_case_runtime.UNPROJECTABLE_FIELDS` says no filesystem
inspection can recover) with `--dedupe projected` leaves 628,424 cases, and
additionally dropping `architecture_delta` leaves 96,056.

So this script builds the ACTION-COVERING SUBSET: for each action label in the
real TLC state graph, the first edge in dump order. It uses the shipped
`render_python_package` over the shipped model's real TLC dump -- the same
renderer `generate cases` calls -- so the cases are the generator's own output
for the edges it selects, not hand-written fixtures.

WHAT THIS IS AND IS NOT. It is a lower bound: fewer cases can only exercise
FEWER ports, so every dead-surface finding it reports is at least as severe as
the complete corpus would report, and no finding it reports can be an artifact
of the subsetting. It is NOT the corpus the model defines, it cannot show that a
port IS exercised in general, and it is not a substitute for
`generation_status: generated`.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts import case_modules  # noqa: E402
from scripts import generate_cases_from_tlc_dump as generator  # noqa: E402


#: The actions whose production adapter implements ``run(case, ...)``. The other
#: nine are ``apply()``-only spec-unit adapters (MF-028's case-execution segment
#: was built for setup + ticket only), and ``run effect-conformance`` aborts the
#: whole run on the first one it meets -- it never consults ``can_run`` and has
#: no skip path, unlike ``run_generated_case_adapters``. Both facts are RC-02
#: findings, recorded rather than repaired here.
def executable_actions(mapping_path: Path) -> set[str]:
    import tomllib

    from spec_double_compiler.runtime import load_object

    mapping = tomllib.loads(mapping_path.read_text(encoding="utf-8"))
    executable = set()
    for label, entry in mapping.get("adapters", {}).items():
        target = entry.get("adapter")
        if target and hasattr(load_object(target), "run"):
            executable.add(label)
    return executable


def main() -> int:
    dot = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    spec_dir = ROOT / "specs" / "current"
    tla = spec_dir / "TlaSpecDevCli.tla"
    sys.path.insert(0, str(spec_dir))
    sys.path.insert(0, str(ROOT / "scripts"))

    from spec_double_compiler.runtime import adapter_accepts_case, instantiate, load_object

    from run_generated_case_adapters import adapter_for_case, load_cases, load_mappings

    states, edges = generator.load_dot(dot)
    print(f"dump: {len(states)} states, {len(edges)} edges")

    runnable = executable_actions(spec_dir / "case_adapters.toml")
    print(f"adapters implementing run(case, ...): {len(runnable)} of 17 -- {sorted(runnable)}")

    search_path = case_modules.resolve_search_path(tla, [])
    recipes = generator.build_recipes_for_hierarchy(tla, search_path)

    def render(selected, package_dir):
        keep = {edge.source for edge in selected} | {edge.target for edge in selected}
        return generator.render_python_package(
            module=tla.stem,
            states={node: states[node] for node in keep},
            edges=selected,
            package_dir=package_dir,
            view="internal",
            action_metadata={},
            labelers=[],
            state_projector=None,
            output_projector=None,
            dedupe="none",
            param_recipes=recipes,
        )

    # Pass 1: the first CANDIDATE_DEPTH edges of each runnable action, rendered so
    # the adapters can be asked about real cases rather than about a guess at
    # their preconditions.
    CANDIDATE_DEPTH = 40
    candidates: dict[str, list] = {}
    for edge in edges:
        if edge.action in runnable and len(candidates.setdefault(edge.action, [])) < CANDIDATE_DEPTH:
            candidates[edge.action].append(edge)
    flat = [edge for action in sorted(candidates) for edge in candidates[action]]
    probe_dir = out.parent / "_candidates"
    render(flat, probe_dir)

    mappings = load_mappings(spec_dir / "case_adapters.toml")
    module = load_cases(probe_dir)
    chosen: dict[str, str] = {}
    rejections: dict[str, str] = {}
    for case in module.CASES:
        mapping = adapter_for_case(case, mappings)
        if mapping is None or mapping.label in chosen:
            continue
        accepted, reason = adapter_accepts_case(instantiate(load_object(mapping.adapter)), case)
        if accepted:
            chosen[mapping.label] = case.name
        else:
            rejections.setdefault(mapping.label, reason or "adapter rejected case")

    selected = [edge for edge in flat if _case_name_for(edge, flat) in set(chosen.values())]
    print(f"selected {len(selected)} cases, one per action its own adapter accepts:")
    for label in sorted(chosen):
        print(f"  {label:24s} {chosen[label]}")
    for label in sorted(set(rejections) - set(chosen)):
        print(f"  {label:24s} NO ACCEPTED CASE in {CANDIDATE_DEPTH}: {rejections[label]}")

    prepared = render(selected, out)
    print(f"wrote {len(prepared)} cases to {out}")
    return 0


def _case_name_for(edge, flat) -> str:
    return generator.case_name(flat.index(edge) + 1, edge.action)


if __name__ == "__main__":
    raise SystemExit(main())
