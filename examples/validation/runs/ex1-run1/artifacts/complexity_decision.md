# Complexity Decision: taskq

Decision: **no complexity refactor is warranted.** Neither the model nor the
program needs restructuring. Reasoning follows the reading order in
`references/complexity_intuition.md`, grounded in the facts in
`validation_artifacts/descriptor.txt` (scan of `External.tla` + `External.cfg`
with `spec_manifest.yaml`, TLC report attached).

## 1. Unknowns

Two `(unconstrained)` rows: `lastInternalAction` and `lastCli`. Both are
deliberate observability channels, the same shape as the toolchain's own
`lastCommand`/`result` example (intuition doc, example 5):

- `lastCli` records the last command/target/exit so Test Graph cases can
  assert exit behavior. It is not invisible state: `CliExitCodeInvariant` and
  `CliResultConsistency` both read it (only `lastInternalAction` appears in
  the "no configured invariant reads" list).
- `lastInternalAction` exists purely to label spec-unit cases; it carries no
  program fact the store does not already carry.

Both carry a justification linkage in the manifest ("every variable has a
recorded justification linkage"). These are honest unknowns with owner-known
reasons, and I note the printed bound excludes them.

## 2. Bound vs behavior

`bound = 64`, one bounded dimension, `tasks: 64 (100.0% of the bound in log
space)` — i.e. `4^3` for three task names with domain
`{"absent", "pending", "running", "done"}`. Those four values are exactly the
distinctions taskq's behavior makes (a name missing from taskq.json plus the
three stored statuses); every value is distinguished by some guard
(`AddTask`/`StartTask`/`FinishTask` guards) or invariant. There is no
representation weight: no counter wider than its distinctions, no dimension no
invariant reads contributing to the bound. TLC confirms proportionality:
1,377 distinct reachable states, depth 11, finishes in under a second, well
inside `max_distinct_states: 50,000`.

## 3. Dense rows and columns

- `lastCli touched by 9/12 actions` (all writes): the observability channel —
  every CLI action records its exit by design. Discounted per intuition-doc
  example 5.
- `tasks touched by 7/12 actions`: `tasks` **is** the program — taskq's whole
  job is transitioning one name→status map. A store variable in a 3-variable
  model behaving like a lifecycle hub (example 2's "read the row before
  reacting"): written by exactly the three internal transitions, read by the
  five guard/error paths. Not bookkeeping smeared across actions.
- Dense columns are the internal transitions plus error-guard actions touching
  2 of 3 variables — an artifact of the model having only 3 variables, not of
  transactions doing several subsystems' work.

## 4. Clusters / modularity

`Q = 0.000`, single component. A one-store CLI genuinely is one component;
there is no second subsystem to cut toward, and with 64 bound / 1,377
reachable states there is no tractability pressure to decompose. The single
advisory warning — "component C1 is touched by 12 actions, exceeding
max_component_actions 8" — is the component-size heuristic counting each
CLI error variant (`CliAddDuplicate`, `CliStartNotPending`,
`CliStartCapFull`, `CliFinishNotRunning`, `CliUsageError`) as a separate
action. The production surface is four commands; the extra actions are the
negative/edge cases the External view is supposed to enumerate for Test Graph
generation. Enumerating them is modeling value, not coupling.

## 5. Coverage

Only `lastInternalAction` is read by no configured invariant — deliberate
(case-labeling channel, see 1). `tasks` and `lastCli` are read by the
configured invariant stack (`TypeInvariant`, `RunningCapInvariant`,
`CliExitCodeInvariant`, `CliResultConsistency`).

## Conclusion

Complexity is proportional to essential behavior in both directions: the
program makes exactly the distinctions the model carries, and the model
carries no distinctions the program does not make. The one threshold warning
is explained by error-path enumeration and accepted as-is (no budget change
needed — the defaults are far above this model everywhere it is measured).
The shape worth keeping is encoded as fitness functions (step 4) so future
agents are notified if it drifts: bound stays small and known, `tasks` domain
stays at 4, and the store stays covered by invariants.
