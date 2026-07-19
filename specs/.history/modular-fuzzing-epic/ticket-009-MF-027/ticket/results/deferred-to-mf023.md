# MF-027 validations deferred to MF-023 (#30)

Per the epic-wide instruction in the assignment block, spec-case execution is
deferred to MF-023. Not run here:

- spec-case generation
- the corpus run
- the effect-conformance sweep over a real corpus
- the mutation kill test

MF-027 was validated with unit tests, synthetic adapters, fixtures, and the
repository test graphs instead.

## Specifically for MF-027, MF-023 must confirm

1. **The repository's own corpus run now reports `unobservable`.** The promoted
   manifest declares `tlc_process` (`process.spawn` -> `*java*`) and
   `test_process` (`process.spawn` -> `*pytest*`). Every observed spawn now
   produces a process-boundary finding, so a real sweep of this repository will
   refuse rather than report clean. This is accurate — the harness cannot see
   inside those children — but MF-023 must decide whether to route those
   boundaries through in-process adapters or record the refusal as a known
   limitation of the dogfooding sweep. It must NOT be resolved by relaxing the
   rule; no such relaxation exists, and the inverse test in
   `tests/test_effect_conformance.py` guards against adding one.

2. **No false refusal against the REAL adapter tree.** The observability
   assessment refuses on `kind`/`channel`/reference markers. Fixtures cannot
   prove the real `specs/program_model/production_adapters.py` bindings all
   resolve to in-process Python objects and are correctly granted observability.
   MF-023 runs against the real tree and can.

3. **The kill test for the `unobservable` verdict.** MF-027's retention evidence
   rests on the invariant linkage and the externally-visible `result.next`; the
   kill-test leg is deferred to MF-016 (#17) / MF-023.
