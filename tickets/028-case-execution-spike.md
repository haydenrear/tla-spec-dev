# Spike: Make One Adapter Execute One Generated Case

Status: Open

**This is an investigation ticket. The deliverable is a measured answer, not a
finished feature.** Do not implement all sixteen adapters.

## Why

MF-023's dogfooding found that no adapter in this repository can execute a
generated case (FINDING 4). `run_generated_case_adapters.py` drives each case
through an adapter's `run(case, ...)`; all 16 adapter classes implement
`apply(target_repo, ...)`. Not one implements `run`.

The two paths never met. The spec-unit suite calls `apply()` directly, so the
adapters are thoroughly tested and **simultaneously unreachable from the
corpus**. Case execution was deferred in every ticket of this epic, so no run
crossed the seam. The first run that did found it immediately.

The consequence is that **three of the four oracles cannot produce a signal at
all**:

- effect conformance reports 0 observed effects over 40 cases, all 5 declared
  ports "dead" — a verdict that cannot be discharged while nothing runs;
- the kill test cannot compute a rate;
- corpus distillation has nothing real to distil.

Output and projected-state conformance are blocked by the same root cause.

## What makes this a spike rather than a fix

A generated case carries a **before-state**, an action, and an expected
**after-state**. So `run(case, ...)` must materialize an arbitrary before-state,
execute, and project the result for comparison. For a CLI whose state is a
filesystem tree plus a manifest, materializing a specified before-state means
*constructing a repository already in that state*.

Nobody currently knows what that costs per adapter. That unknown is the largest
item in the remaining epic and everything else waits behind it, so it should be
**measured once** before five or six tickets are scoped against a guess.

## Deliverable

1. **One adapter, one generated case, executed end to end.** Pick the adapter
   with the simplest state surface and say why you picked it. Getting a single
   case to genuinely run — before-state materialized, action executed,
   after-state projected and compared — is the whole deliverable.
2. **A written account of what it actually took**, in enough detail to scope the
   other fifteen: what the before-state materialization required, which parts
   were adapter-specific versus shared, what could be factored into a base
   class or helper, and what could not.
3. **A per-adapter difficulty assessment** across the remaining fifteen, banded
   (trivial / moderate / hard) with the reason for each band. This is the
   estimate the re-scope will be built on, so its honesty matters more than its
   optimism.
4. **An explicit recommendation** on shape: is this a `run()` shim over
   `apply()`, a shared before-state builder, a per-adapter rewrite, or something
   the current adapter design cannot support without changing?

## Acceptance criteria

- One case executes end to end against one real adapter, with the actual command
  output recorded as evidence — not a unit test standing in for a run.
- The account is specific enough that someone scoping the remaining fifteen can
  use it. "It was straightforward" is not an answer; what was straightforward,
  and what would differ for an adapter that mutates more state, is.
- The difficulty bands cover all fifteen remaining adapters and name the reason
  for each.
- **If the answer is that the current adapter design cannot support case
  execution without a redesign, say so.** That is a legitimate and valuable
  outcome, and far better than a heroic single case that does not generalize.
- **If the single case cannot be made to run at all, that is also a result.**
  Report where it stops and why, with the output. Do not implement partial
  machinery to disguise a blocked spike.

## Explicitly out of scope

The other fifteen adapters. The `EXTENDS` resolution bug (FINDING 1). The
`analyze corpus` OOM (FINDING 6). The component-metric design question
(FINDING 3). The silent default (FINDING 9). The alphabetical model pick
(FINDING 10). Those are separate tickets that will be scoped **after** this
spike returns a number.

## Note

MF-023's work — the Internal/External decomposition, the reconciled desyncs, the
stuttering fix, the `case_adapters.toml` bindings — lives on the open PR #50 and
is not merged. Do not duplicate it. Branch from the epic tip; if you need the
decomposition to run a case, say so, because that is itself a finding about the
ordering.
