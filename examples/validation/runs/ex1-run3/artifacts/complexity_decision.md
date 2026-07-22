# Complexity decision for taskq

Decision: **no complexity refactor is warranted** — neither of the model nor
of the program. Advisory record only; nothing here blocks anything.

Descriptor evidence: `validation_artifacts/descriptor.txt` (External view =
whole program, Internal view appended). Reading order per
`references/complexity_intuition.md`, "Deciding Whether And How To Refactor".

## The facts, walked in the reading order

1. **Unknowns: none.** Every variable has a resolved domain (`tasks` 64,
   `lastOutcome` 8, `exitCode` 2); no `(unconstrained)` rows, so the printed
   bound understates nothing.

2. **Bound vs behavior: proportional.** External bound = 1,024; Internal =
   512. The dominant dimension is `tasks` at 64 = 4^3 — exactly the four
   lifecycle statuses (absent/pending/running/done) over the three names the
   finite model needs to exercise the cap of 2. Every status distinction is
   read by a guard (`add` requires absent, `start` requires pending, `finish`
   requires running) and by `RunningCapInvariant`. `lastOutcome`'s 8 values
   are the eight distinct CLI outcomes, each a different printed message the
   project's own tests assert (`tests/test_taskq.py`); `exitCode`'s 2 values
   are the real 0/1 process results. No dimension is wider than the
   distinctions the behavior makes — no `0..N` counter smuggled in where the
   program distinguishes only a few situations. TLC confirms tractability:
   488 distinct reachable states (External), complete in under a second,
   against a `max_distinct_states` budget of 50,000.

3. **Dense rows/columns: all flagged, all defensible.** All three variables
   are dense rows and 7/8 actions are dense columns. This is the
   irreducible-small-core signature the intuition doc calls out in worked
   example 4's honesty note: in a 3-variable model of a CLI where *every
   invocation* produces a message and an exit code, the outcome pair is
   necessarily touched by every action. Applying the write-only-state test:
   `lastOutcome` and `exitCode` are **not** write-only bookkeeping — both
   have nameable dependents: `OutcomeConsistencyInvariant` reads
   `lastOutcome` against the task map (beyond its type conjunct),
   `ExitCodeInvariant` ties `exitCode` to `lastOutcome`, and the concrete
   consumers are the CLI's stdout and process exit code, asserted verbatim by
   `tests/test_taskq.py` (e.g. `== "started a"`,
   `== "error: too many running tasks"`). That is example-5 deliberate
   observability with named readers, not example-3 smear.

4. **Clusters: single component, Q = 0.000 — expected, not a finding.**
   Q answers "does a narrow decomposition cut exist?"; for a 3-variable model
   whose one real state variable (`tasks`) is coupled to its own output
   channel, the honest answer is no cut, and none is needed. There is no
   second subsystem to separate. The matrix itself is the good shape: `tasks`
   is written only by the three success actions, reject actions only read it,
   `CliList` touches nothing but `exitCode`.

5. **Coverage and justification: complete.** Every variable is read by at
   least one configured invariant and every variable has a justification
   linkage in `spec_manifest.yaml`. No invisible state.

6. **Thresholds:** no warnings; every metric is far inside the default
   budgets (bound 1,024 vs 1,000,000; 488 distinct vs 50,000; 3 variables vs
   6; 8 actions vs 8 — at the component-action heuristic exactly, not over).

## What would change this decision

- A bookkeeping variable written by every action with no invariant or
  consumer reading it (an audit trail, a cache epoch) — remove it or give it
  a reader.
- A numeric dimension wider than the program's distinctions (e.g. modeling a
  running *count* 0..K instead of deriving it from `tasks`).
- Growth of the CLI into genuinely separate subsystems (e.g. a scheduler plus
  a persistence layer) — at that point the R/W matrix should show a cut, and
  the fitness rules below are configured to notify the agent who gets there.

The configured fitness functions (`specs/program_model/fitness_functions.json`
— JSON, not YAML, because the CLI runs under a bare `python3` without PyYAML)
encode the shape this decision settles on: bound stays small and known, and
state stays fully invariant-covered and justified.
