# Analyze Complexity Command

Status: Open

Agents currently discover state explosion by running TLC, timing out, and
poking constants. The decomposition method in
`references/modular_fuzzing.md` needs the dimension analysis mechanized so
there is a number to engineer against before TLC ever runs.

Add `tla-spec-dev analyze complexity`.

Acceptance criteria:

- Parses a spec + cfg and prints the per-variable domain cardinality table
  and the state-space upper bound.
- Prints the variables x actions read/write matrix and flags near-decomposable
  variable clusters with their candidate port-crossing actions.
- Reads `budgets:` from `spec_manifest.yaml` and exits nonzero when the
  estimate exceeds `max_distinct_states` or a component exceeds
  `max_component_variables` / `max_component_actions`.
- Case generation refuses to run (with an override flag) when the gate fails,
  printing the dominant dimensions instead of timing out.
- Computes a graph-modularity score for the R/W matrix and emits a suggested
  move — abstract, decompose (with the candidate cut), or refactor (with the
  dense rows/columns as the finding) — **explicitly labeled a recommendation
  requiring user approval**, never auto-applied. See
  `references/architecture_tractability.md`.
- Flags variables with no recorded justification (no invariant, effect, or
  kill-test linkage) as dead weight when a justification table is present in
  the manifest.
- Output is writable as evidence into a ticket `results/` directory.
