# taskq complexity decision

Decision: **no complexity refactor is warranted** — neither of the model nor
of the program. The descriptor shows complexity proportional to taskq's
essential behavior, with two deliberate, justified observability channels as
the only unknowns. Record the shape as fitness functions (done, see
`fitness_functions.json`) and move on.

Inputs: `validation_artifacts/descriptor.txt` (External whole-program scan and
Internal scan, 2026-07-21), read with the reading order from
`references/complexity_intuition.md` ("Deciding Whether And How To Refactor").

## 1. Unknowns first

Two `(unconstrained)` rows: `lastInternalAction` and `lastExternalAction`.
Both are deliberate observability channels that label generated cases with the
action that produced them — the same pattern the toolchain's own baseline uses
for `lastCommand`/`result` (intuition doc, example 5). Both carry a recorded
justification in `spec_manifest.yaml` (`Justification linkage: every variable
has a recorded justification linkage`), and neither holds program state: no
guard reads them, no invariant needs them. These are honest unknowns with an
owner-known reason, not holes.

## 2. Bound vs behavior

`bound = 1,152` (External), from exactly three dimensions:

- `tasks: 64` (59.0% in log space) — `4^3`: three task names, four lifecycle
  statuses (`absent/pending/running/done`). Every value is a distinction the
  program actually makes: guards distinguish all four statuses (add requires
  absent, start requires pending, finish requires running), and the running
  cap needs at least 3 names to be exercised against `MaxRunning = 2`. No
  representation width here.
- `cliMessage: 9` (31.2%) — the CLI's real message classes: one per success
  path (added/started/finished/listed), one per distinct error taskq.py
  prints (exists / not pending / too many / not running), plus initial
  "none". `CliErrorExitInvariant` and `TooManyMeansCapReached` read it, so
  the dimension is invariant-load-bearing, not bookkeeping.
- `cliExit: 2` — the two exit codes the CLI actually produces on modeled
  paths.

TLC reaches 1,238 distinct states in under a second; every advisory threshold
has orders-of-magnitude headroom (`No complexity warnings`). Nothing to
abstract: there is no wide counter, no epoch, no dimension no property reads.

## 3. Dense rows and columns

Dense rows: `cliExit` and `cliMessage` (8/12 actions), `tasks` (7/12).

- `cliExit`/`cliMessage` are written by exactly the 8 CLI invocations —
  that is the CLI response contract: every command run produces an exit code
  and a message. A response channel written once per public action is a
  protocol-mandated shape, not bookkeeping smeared across transitions
  (contrast: intuition example 3's `audit_log`, which was *also* read by
  nothing; these two are read by three invariants).
- `tasks` is the task store — the program *is* this variable. In a 12-action
  model of a single-store CLI, the store being touched by most actions is
  the lifecycle-hub pattern of intuition example 2, and the flag is
  small-model threshold noise: read the row and the writes are exactly the
  three lifecycle transitions; the other four touches are read-only error
  guards.

Dense columns: the four negative invocations (`CliAddDuplicate`,
`CliStartNotPending`, `CliStartOverCap`, `CliFinishNotRunning`). Each reads
`tasks` (to establish the rejection condition) and writes the two response
variables — three of five variables trips the more-than-half threshold. None
of them is a transaction doing several subsystems' work; each is one CLI run.

## 4. Clusters

Q = 0.044 is low, and that is expected: a CLI wrapping one store is a
pipeline-like shape with no block structure to find (intuition example 2 —
"do not read Q as a quality score"). The clusters are nevertheless nameable:
C1 = the CLI response channel (`cliExit`, `cliMessage`), C2 = the task store
plus its case-label channel, C3 = the external case-label channel. The
port-crossing actions are the four error invocations, i.e. the places where
the public surface reads the store — a real boundary, so a decomposition cut
exists if the program ever grows enough to need one. It does not today.

## 5. Coverage

Variables no configured invariant reads: only the two observability channels
(deliberate, see 1). Every state-carrying variable — `tasks`, `cliExit`,
`cliMessage` — is read by at least one configured invariant, so all program
state is verification-load-bearing. `unjustified_count = 0`.

## Conclusion

Complexity is proportional to essential behavior in both directions: nothing
in the bound is representation weight, and no essential distinction is
missing (lifecycle, cap of 2, duplicate rejection, error/exit contract are
all modeled and invariant-checked). The three dense rows and four dense
columns are the accepted shape of a single-store CLI with a response channel.
The shape worth keeping is now encoded as two composed fitness functions
(`specs/program_model/fitness_functions.json`) so any later change that
widens a domain, adds unverified state, or breaks the density pattern
notifies the next agent instead of drifting silently.
