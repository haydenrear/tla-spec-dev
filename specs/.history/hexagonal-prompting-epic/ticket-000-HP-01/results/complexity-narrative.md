# HP-01 complexity narrative

**Direction: zero.** HP-01 adds no modeled representation, removes none, and
changes no action, variable, invariant or config of `TlaSpecDevCli`. The
measured delta against `architectural-coherence-epic` is `direction=zero`, and
that is the ticket's declared `model_delta_expectation` verbatim: *"none — and
that is deliberate."*

## Why zero is the right answer here, and not an omission

The plan's `surface_cost_rule` is the most important rule in this epic and it
was written from a measurement, not a preference: the predecessor cost roughly
**1.5 new coverage gaps and 8× state space per surface-adding ticket**, and its
corpus grew to 18,391× its own cap. Under that rule, added model surface is a
**cost to be justified**, not a virtue to be demonstrated. A harness ticket that
invented an action so its ledger entry would look substantial would be paying
that cost to produce a nicer-looking record.

HP-01's entire product is an experiment: a feature specification, two arm
prompts, a reference tree, a shared behavioral suite, a seeded fault catalogue,
an integrity harness, and a sealed predictions file. Every one of those lives
under `examples/validation/`, which `representation_scope` puts explicitly
**out of model** — *"examples/\*\* — fixtures and eval subjects; what the
toolchain is pointed AT."*

## The one thing that could be mistaken for added surface

HP-01 ships `examples/validation/ab/model/QuotaLedger.tla` and its `.cfg`, TLC
green at **2649 distinct states, depth 8**, with four invariants.

That is a **fixture model** — the state machine of the *subject program the A/B
implements*, not of the toolchain. It is what the two arms are measured
through, and it exists because HP-06 must generate cases from a model that is
identical across arms; if each arm produced its own, a D1 difference between
arms could be a difference between their models and nobody could attribute it.

It adds **zero** actions and **zero** variables to `TlaSpecDevCli`, which is the
modeled program surface. `results/zero-model-delta.txt` records the empty
`git diff --stat` over `specs/program_model`, the desired-model TLA+/cfgs, and
`specs/current` that demonstrates it.

Its state space was kept deliberately small — two tenants, two reservation ids,
amounts `{0,1,2}`, quota 2 — for the same reason: `RC-02-DF-04` and
`MF026-R4-F-01` recorded `generate cases` on MCsmall producing 3,678,217 cases
and a 7.4 GB file CPython cannot import. A fixture whose corpus nobody can run
is not a fixture, and HP-03 inherits this one.

## The refinement search, and what it found

Searched: yes. Found: nothing to apply.

The search asked whether any representation this ticket touches could be made
smaller while retaining behavior. The honest answer is that there is no modeled
representation in scope to reduce — the ticket's `implementation_scope` is
`examples/validation/` and its `conflict_keys.tla` is empty. Recording
"searched, found none" rather than skipping the step is the point of the step.

Two reductions *were* made inside the fixture, and neither is a model
reduction, so neither is claimed as one:

1. The A/B model's constants were chosen to keep the state graph at 2649
   states rather than letting it grow — a deliberate cost control on HP-03's
   inherited corpus, argued above.
2. `available` in `reference/quota_ledger.py` is **stored rather than
   derived**, which is the *less* reduced of the two options. Deriving it would
   have been simpler and would have made `R1` conservation true by
   construction — and would thereby have deleted the entire cross-aspect fault
   surface that M08 is seeded into. That is MF-020 read in reverse: a
   simplification that silently removes the behavior a measurement depends on
   is not a simplification worth having. The choice is recorded in the
   reference's module docstring so a later reader does not "clean it up".

## The unflattering result this ticket measured about itself

`check_catalogue.py --verify-suite`, with a green control on the unmutated
reference: **the hand-written suite kills 10 of 10 mutants**, including the
ordering negative control.

That is a high bar set *against* this epic's own instruments. If the generated
corpus scores below 10 of 10 on this fixture, the generator is worse here than
a test suite a competent engineer writes in an afternoon, and HP-06 is
instructed — in `README.md`, in `seeded_faults.toml`, and in
`PREDICTIONS-HP.md` — to report exactly that rather than reporting the corpus's
kills in isolation where they would read as a success.

**One of HP-01's own ten predictions was wrong.** M02 was annotated
`SURVIVES` on the reasoning that the shared suite never issues two overlapping
partial reserves; it was killed by `test_reserve_exhausts_the_quota_exactly`,
because after globex reserves 4 of 4 a further reserve of 1 is not greater than
the quota of 4 and the mutant accepts it. Arithmetic the author got wrong. It
is corrected in place with the error recorded beside it, which is legitimate
only because nothing had been dispatched; after dispatch the catalogue is
sealed and a wrong prediction becomes a finding instead of an edit.

That correction is the whole argument for running the verification at all.
Without it the catalogue would have shipped an annotation asserting the suite
is blind to a guard-relaxation fault it is not blind to — which is precisely
how round 1's guard-relaxation explanation survived an entire epic while being
false.

## Findings filed, not fixed

- **HP-01-DF-01** (major): the epic's own acceptance command is red at the epic
  tip — 3 failed / 1066 passed on an untouched `17601f7`, against a dispatch
  that stated "1039 passed, 14 skipped". Cause: `resolve_cited` in
  `tests/test_source_citations.py` resolves cited files by unique basename via
  `rglob`, excluding only `.git` and `generated`; the per-checkout Skill Manager
  home that `wt new` creates contains an installed copy of this skill, so every
  basename has two matches. It passes in a plain clone and fails in every
  checkout the workflow mandates.
- **HP-01-DF-02** (minor): the shipped EV-01 catalogue is rejected by the
  shipped `kill_test` parser (`effect_port` vs `port`).

Neither is fixed here. `tests/**` is outside HP-01's `implementation_scope` and
inside HP-03's, HP-04's and HP-05's, so a fix from this ticket would collide
with three unstarted tickets; and the EV-01 catalogue is a sealed answer key
whose own header forbids exactly that amendment.

## Retention members

`kill_rate`, `effect_conformance` and `external_coverage` are all `not_run`,
which is the honest value. HP-01 seeds a catalogue and proves its integrity; it
deliberately does **not** score it. A fixture author who runs his own
instrument and reports the number has removed the measurement — that is EV-01's
recorded discipline and it carries forward. HP-06 scores it, on the integrated
epic tip, blind to arm.

The one number HP-01 *did* measure — the 10 of 10 suite baseline — is about
**HP-01's own hand-written suite against HP-01's own reference**, touches no arm
and no mechanism the epic ships, and is recorded precisely because it is
unflattering to the epic.
