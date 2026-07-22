# Fresh-agent review: legacy payment HTTP

## Verdict

An agent can implement the generic `EffectProvider.bind(context)` contract for
this arbitrary repository without a framework-owned HTTP adapter. The accepted
run changed zero framework files during validation and passed the common result
validator. That does not make the HTTP patch a generally safe provider: it is a
project-owned compatibility layer whose boundary and bypasses must remain
visible.

The accepted evidence is
[`evidence/validation-runs/agent-ep06-http-v3/result.json`](evidence/validation-runs/agent-ep06-http-v3/result.json).
It regenerated 56 internal and 56 external cases, executed 1,792 green control
points, killed 12/12 fixed mutants, replayed all 12 discoveries exactly, and
ran one additional exact replay from a different working directory. All 56
external cases crossed a child-process and real loopback-HTTP boundary.

## Ownership that stayed understandable

TLA+ owns the seven semantic response classes and their allowed decision,
reason, reference class, attempt count, output, and post-state. It does not
describe HTTP byte layout, timeout subclasses, or monkey-patch mechanics.

The provider owns concrete 502/503/504 representatives, connect/read timeout
selection, JSON layout, header casing, malformed bytes, opaque authorization
references, request-shape assertions, transcripts, process-global patch setup,
and cleanup. The adapter performs one visible refinement: it maps the concrete
authorization reference back to the TLA+ `opaque` class.

Passive/external validation owns facts the self-installed provider cannot prove:
`urllib` and raw sockets bypass `requests.Session.send`, a socket guard blocks
the known in-process attempts, and the external rung proves the application
against real loopback HTTP in a child process.

## Measured cost and benefit

The accepted run took 41.04 seconds. TLC regeneration took 2.10 seconds, the
full internal control/mutant/replay campaign 5.34 seconds, focused tests 0.70
seconds, and the 56 child-process loopback cases 32.71 seconds. Cleanup was
observed clean at all 2,477 counted execution/replay points. Control point
runtime was 0.17 ms p50 and 0.31 ms p95, so the real-boundary rung—not provider
fuzzing—is the recurring runtime cost.

The original project evidence records 402 provider lines, 165 adapter lines,
321 model lines, and 1,646 experiment/test lines, with 291.79 authoring minutes
over 14 edit/run iterations. The reusable `validate.py` and usage descriptor
make reruns cheap, but they do not erase that up-front experiment-design cost.

The strong four-scenario hand-written baseline also killed 12/12 mutants.
Accordingly, this fixed catalog shows no mutation-score gain from generated
cases. The measured benefit is instead complete cross-product execution,
deterministic representative variation, per-point cleanup, a recorded semantic
oracle, and exact failure replay. A future catalog needs representation- or
cross-product-specific mutants before claiming incremental bug discovery.

## Replay and concurrent-agent findings

EP-05 fixed the virtualenv replay defect. Every accepted replay command records
the project `.venv` interpreter, carries no explicit `site-packages` import
root, and executes successfully. The additional PH-01 replay ran verbatim from
the evidence directory and reproduced the same case, iteration, transcript
digest, and nonzero structured failure.

The first versioned run exposed a separate harness assumption: a repository-wide
"no dirty framework files" check rejected a test concurrently created by
another agent before this validation began. The durable invariant is now byte
equality between a validation-start framework snapshot and the post-campaign
snapshot. This keeps the no-rescue-edit gate meaningful in a shared worktree.

## Limits and recurring patterns to watch

- A self-installed provider yields `None`, so runtime signature preflight
  cannot prove that the patch implements generated `PaymentHttpPort.send`.
  The typed port still documents the semantic boundary, but this integration
  trades explicit conformance for legacy compatibility.
- `requests.Session.send` is process-global and not safe for overlapping
  provider scopes or uncontrolled parallel tests. Captured callables, other
  HTTP clients, subprocesses, and native networking may bypass it.
- The provider and adapter share concrete-reference refinement knowledge. This
  duplication is small here but is a recurring drift risk.
- Killed mutants stop after the first complete killing iteration and then
  replay. Only the control and a survivor cover all 32 mutation iterations;
  reports must not present a killed mutant as 56 × 32 execution.
- Deterministic representatives only amplify existing assertions. They cannot
  repair an underspecified TLA+ outcome or an adapter that projects too little.

## Recommendations

Keep this HTTP implementation project-local; do not promote it into the
framework library. Promote only recurring, domain-neutral mechanisms after
more repositories show the need: the usage descriptor, validation-start
framework snapshot, non-overwriting result schema, and exact cross-directory
replay check.

For effectful modeling, prioritize explicit injection in new code and require a
declared bypass list plus a real-boundary rung for self-installed integrations.
Add collect/continue campaign support if full representative sensitivity after
first discovery becomes a decision metric. Consider a generated/domain-neutral
refinement hook only after multiple projects demonstrate the same concrete-to-
semantic projection duplication.
