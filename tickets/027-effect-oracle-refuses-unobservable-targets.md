# The Effect Oracle Must Refuse Targets It Cannot Observe

Status: Open

Amendment to MF-013, which shipped correct behavior with a silent boundary.

## The defect

`EffectSandbox` observes by monkeypatching the **in-process Python runtime**:
`builtins.open`, `os` mutators, `subprocess.run`/`Popen`, `socket.connect`.
That gives it a hard edge it does not currently declare:

- A **Java or Kotlin adapter runs in a separate JVM** and is entirely
  invisible. No patch crosses the process boundary. This is not hypothetical —
  the Test Graph SDK ships Java (`test_graph/sdk/java/.../Node.java`), so JVM
  nodes are first-class in this toolchain.
- A **spawned subprocess** is recorded as a spawn, while everything it does is
  unobserved. Files the child writes never appear.
- Neither case reports a problem. **The oracle returns green.**

A clean effect-conformance report on a target the sandbox cannot observe is
indistinguishable from a clean report on one it can. That is the exact defect
class this epic has purged five times — corpus filtering, gap suppression, a
self-disabling justification check, a budgets fallback that hid a broken
parser, and an override that made a hard gate advisory. Silent degradation
dressed as success.

The problem is **not** that the oracle is Python-only. A Python-only oracle is
useful and honest if it says so. The problem is that it does not say so.

## Why this is not solved by scrapping the oracle

Effect conformance is one of exactly three members of the doctrine's constraint
set — "rerun the constraint set (kill rate, effect conformance, external
coverage)" — and that set exists specifically to catch complexity minimization
done the cheap way, including "quietly dropping a boundary". The kill test
catches inadequate representation *at modeled boundaries*; effect conformance
catches boundaries that were **never modeled at all**. Nothing else does.

## What to build

1. **Declare the observable scope, and refuse outside it.** The sandbox
   determines whether a target is observable in-process. If it is not — a JVM
   node, a non-Python runtime, an adapter that delegates across a process
   boundary — the run **FAILS** with an explicit "target not observable"
   verdict. It must never return a clean report for a target it could not see.
2. **Make the subprocess boundary an explicit finding.** A spawn is currently
   recorded while its effects are invisible. That gap must surface as an
   unobservable-boundary finding rather than as silence, naming the process.
3. **Record the External/test-graph gap as a known limitation.** Exported
   Test Graph cases run in JBang/uv nodes outside this sandbox and receive no
   effect checking at all (`export_testgraph_cases.py` has zero references to
   effect conformance). Document it, and file the follow-up: observing a JVM
   target needs a different mechanism — a JVM agent, syscall capture, or a
   container-level recorder — behind the same port-declaration schema. That is
   a second implementation, not an extension, and is out of scope here.

## Acceptance criteria

- An adapter that is not observable in-process produces a **failing** verdict
  naming why, never a clean report. Prove it with a test that runs a
  deliberately unobservable target and asserts the failure.
- A subprocess spawn produces an explicit unobservable-boundary finding naming
  the process, not silence. Prove it with a test.
- No configuration, flag, annotation, or manifest entry can downgrade an
  unobservable-target verdict to a pass. Prove the inverse, as MF-013 did for
  gap suppression — this is the regression guard against reintroducing the
  silence.
- The External/test-graph gap is documented as a known limitation in
  `references/modular_fuzzing.md` alongside the effect-conformance oracle, with
  a filed follow-up issue for JVM-capable observation.
- `SKILL.md` states the oracle's observable scope plainly, so a user onboarding
  a JVM project learns it from the documentation rather than from a false green.

## Note

This repository is Python, so the oracle works fully against it and MF-023's
dogfooding is unaffected. The gap matters for users onboarding other-language
targets — which is precisely who would be misled, and who is least able to
notice.
