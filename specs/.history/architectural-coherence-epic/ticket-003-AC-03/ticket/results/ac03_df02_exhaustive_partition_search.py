#!/usr/bin/env python3
"""AC-03-DF-02 reproduction: the emergent partition search is greedy, and
"this model does not decompose" is a statement about the search, not the model.

Enumerates ALL set partitions of the variables of specs/current/TlaSpecDevCli.tla
(Bell(10) = 115,975) and scores each with the SHIPPED modularity function and
the SHIPPED decomposition criteria. Run from the repository root:

    python3 specs/tickets/AC-03/results/ac03_df02_exhaustive_partition_search.py

Observed 2026-07-27 at e73b7d1:

    partitions examined: 115975
    partitions meeting ALL THREE criteria: 2
      Q=0.0029  crossing=0.188  [corpus_gate, effect_conformance] | [rest]
      Q=0.0003  crossing=0.438  [corpus_gate, effect_conformance, ticket_state] | [rest]

while `analyze architecture` on the same spec reports one component, Q = 0.000,
and "this model DOES NOT DECOMPOSE".

Confirm the first result with the shipped tool itself:

    cat > /tmp/exh.yaml <<'YAML'
    architecture:
      components:
        - name: corpus_evidence
          variables: [corpus_gate, effect_conformance]
        - name: rest
          variables: [architecture_scan, complexity_gate, kill_test, lastCommand,
                      result, setup_phase, spec_root, ticket_state]
    YAML
    python3 scripts/tla_spec_dev.py --spec-root specs analyze architecture \
      specs/current/TlaSpecDevCli.tla specs/current/MC.cfg --components /tmp/exh.yaml

    -> MEASURED RESULT: the partition is a cut -- every criterion above is met.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, "scripts")

import analyze_architecture as aa  # noqa: E402
from analyze_complexity import interaction_graph, modularity  # noqa: E402

TLA = Path("specs/current/TlaSpecDevCli.tla")
CFG = Path("specs/current/MC.cfg")


def set_partitions(collection: list[str]):
    if len(collection) == 1:
        yield [collection]
        return
    first, rest = collection[0], collection[1:]
    for smaller in set_partitions(rest):
        for n, subset in enumerate(smaller):
            yield smaller[:n] + [[first] + subset] + smaller[n + 1 :]
        yield [[first]] + smaller


def main() -> int:
    descriptor = aa.analyze(TLA, CFG)
    variables = sorted(descriptor.variables)
    actions = descriptor.actions
    weights = interaction_graph(actions, variables)
    touched = [(a.name, set(a.reads) | set(a.writes)) for a in actions]

    cuts = []
    examined = 0
    for raw in set_partitions(variables):
        examined += 1
        if len(raw) < 2:  # criterion 1: component_count >= 2
            continue
        parts = [set(x) for x in raw]
        q = modularity(parts, weights)
        if q <= 0:  # criterion 2: modularity_q > 0
            continue
        index = {v: i for i, part in enumerate(parts) for v in part}
        crossing = sum(
            1 for _, vs in touched if len({index[v] for v in vs if v in index}) > 1
        )
        fraction = crossing / len(touched)
        if fraction > 0.5:  # criterion 3: crossing_action_fraction <= 0.5
            continue
        cuts.append((q, fraction, raw))

    print(f"variables: {len(variables)}  actions: {len(actions)}")
    print(f"partitions examined: {examined}")
    print(f"partitions meeting ALL THREE criteria: {len(cuts)}")
    for q, fraction, raw in sorted(cuts, reverse=True, key=lambda t: t[0]):
        print(f"  Q={q:.4f}  crossing={fraction:.3f}  {raw}")

    emergent = aa.analyze(TLA, CFG)
    print(
        f"\nshipped emergent partition: {len(emergent.components)} component(s), "
        f"Q = {emergent.modularity_q:.6f}, decomposes = {emergent.decomposes}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
