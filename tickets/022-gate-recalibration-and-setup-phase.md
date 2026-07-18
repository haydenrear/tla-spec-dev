# Recalibrate The Bound Gate And Collapse Setup Booleans

Status: Open

Two changes bundled by owner decision because both touch the model and the
budgets block, so they land as one `TlaSpecDevCli.tla` touch rather than two.

Report their complexity deltas **separately**. Bundling the work must not
bundle the measurement: one change makes the bound smaller and the other
changes what the bound is compared against, and conflating them would produce
exactly the kind of unattributable figure this epic has already had to
withdraw once.

## Part 1 — the bound gate is miscalibrated

MF-011 gates the static state-space upper bound against `max_distinct_states`.
The two quantities are incommensurable.

| Quantity | Value |
|---|---|
| Static upper bound (what is gated) | 1,179,648 |
| Actual reachable distinct states | 2,923 |
| `max_distinct_states` budget | 50,000 |

The bound over-approximates reachable states by roughly **400x**, so the gate
fails a model whose actual distinct-state count is **17x under its own
budget**.

The decisive evidence is not the ratio. It is that applying the only
structural reduction the tool itself recommends — the `setup_phase` collapse
in Part 2 — yields a bound of **73,728, which still fails** the 50,000 budget.
**A gate that its own recommended optimum cannot satisfy is wrong by
construction.**

Left unfixed this blocks MF-014, which needs case generation, and forces
routine `--allow-over-budget`, which defeats the gate entirely.

**The error is in the MF-011 specification, not its implementation.** Issue #13
instructed comparing the estimate to `max_distinct_states` and that is exactly
what was built. This is the second spec-level error of this class in the epic,
after the withdrawn -13.1% generated-states projection.

### Part 1 acceptance criteria

- `budgets:` carries a distinct `max_state_space_bound`; the static bound is
  gated against it. `max_distinct_states` is retained for post-TLC comparison
  against actual reachable states.
- The default is justified against real measurements and stated explicitly.
  **Do not reverse-engineer a number that makes this repository pass** — that
  is gaming the metric with extra steps. If the honest default still fails
  here, report that as a finding.
- `scaffold project` / `scaffold workflow` emit the new budget, and
  `load_budgets` supplies it with the documented fallback-and-warning.
- The component-size heuristics are untouched and still fire. `C1 is touched
  by 11 actions, exceeding max_component_actions 8` is a genuine architecture
  finding and must survive this ticket.
- After both parts, `analyze complexity` passes on this repository's own
  model — and the pass is honest, i.e. actual reachable states remain far
  under `max_distinct_states`.

## Part 2 — collapse the setup booleans

Owner-approved architectural move, found independently by two agents: the
MF-020 ledger surfaced it, and MF-011's new analyzer derived it from the model
alone without being told it existed.

`cli_built`, `cli_installed`, `project_scaffolded`, `budgets_recorded`, and
`workflow_scaffolded` form a strict bootstrap chain pinned by their own action
guards. Only 6 of their 32 combinations are reachable; the other 26 are
declared state the program can never occupy. Replace them with a single
ordinal `setup_phase \in 0..5`.

Measured before scheduling: **11 -> 7 state variables**, declared bound
**393,216 -> 73,728**, at identical reachable states.

### Part 2 acceptance criteria

- The five booleans are gone; `setup_phase` carries the bootstrap ordering.
- Every invariant and action guard expressed over them has an equivalent over
  `setup_phase`. Enumerate the before/after mapping — it is the deliverable
  that proves nothing was silently dropped.
- **Reachable distinct states and search depth are unchanged by the collapse.**
  This is the retention proof. Establish the pre-collapse baseline on-branch
  first so the comparison is real rather than quoted.
- No adapter still references a removed boolean.

## Note on measurement discipline

Part 1 changes what the bound is compared against. Part 2 changes the bound
itself. Record: the bound before and after Part 2, the gate verdict before and
after Part 1, and the reachable-state count throughout (which should move only
where Part 1's new gate state legitimately adds behavior). A single blended
"complexity improved" figure is not acceptable.

Watch for the self-loop trap recorded in the plan: a drop in *generated*
states at constant *distinct* states is a red flag, not a win.
