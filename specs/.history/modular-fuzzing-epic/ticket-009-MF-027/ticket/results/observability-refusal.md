# MF-027 acceptance evidence: the oracle refuses what it cannot observe

## 1. How observability is determined

`assess_target_observability()` in `scripts/effect_conformance.py`. Observability
is granted **only on positive evidence** and refused by default.

The single piece of evidence that counts is `resolved`: a live Python object,
imported into *this* interpreter, that the runner is about to call directly.
Both runners pass the adapter object they already hold:

- `scripts/run_generated_case_adapters.py` (the ENFORCING copy, inside
  `run spec-unit-tests`)
- `scripts/effect_conformance_report.py` (the standalone reporting command)

Both call `EffectSandbox.require_observable(...)` **before** executing the
adapter. The refusal is recorded on the recorder at that moment; the return value
is informational, so a caller that ignores it still cannot produce a clean
report.

A target is refused when any of these hold:

| Condition | Example |
|---|---|
| Declared `runtime` is not in-process CPython | `runtime = "jvm"` |
| `kind` / `channel` / reference names an out-of-process runtime | `kind = "java"`, `jbang nodes/Verify.java` |
| No live Python object was resolved | adapter could not be imported |
| Reference is not a Python `module:object` | `/usr/bin/env python3 run.py` |

**The polarity is the point.** Defaulting to "observable" and refusing only on a
list of recognised non-Python markers would mean every runtime nobody thought to
enumerate silently reports clean — the exact defect MF-027 closes. Defaulting to
refusal costs an unrecognised runtime's author an explicit message they can read
and act on. Pinned by
`TestObservabilityAssessment::test_unrecognised_runtime_defaults_to_refusal_not_to_clean`.

## 2. An unobservable target FAILS rather than returning clean

`EffectConformanceReport`:

- `unobservable` is a third finding list, added to the **same** conjunction as
  `gaps` and `dead_surface` in `ok` — not beside it, so there is no second code
  path that could be relaxed independently.
- `verdict` tests `unobservable` **first**. It dominates: a diff computed over a
  target that was never seen carries no information, so reporting it as `clean`
  — or even as `gaps` — would assert something the run has no evidence for.

Proof, `TestUnobservableTargetFails`:

- `test_jvm_target_fails_rather_than_reporting_clean` — the fixture's observed
  effect **matches its declared port**, so under MF-013 this exact input
  produced `verdict=clean, ok=True`. It now produces `verdict=unobservable,
  ok=False` with `gaps == []` and `dead_surface == []`. This is the false green,
  removed.
- `test_failure_names_why` — the message names the target and the reason.
- `test_unobservable_outranks_gaps_and_dead_surface` — precedence.
- `test_evidence_json_records_the_refusal_and_the_scope` — the JSON evidence
  carries `unobservable_targets` and an `observable_scope` statement.

## 3. A subprocess spawn surfaces as an explicit finding

Derived in `diff_effects` from the observation itself, so no declaration
suppresses it. Every observed `process.spawn` yields an
`UnobservableTarget(kind="process-boundary")` naming the command.

Proof, `TestSubprocessBoundaryIsAnExplicitFinding`:

- `test_spawn_surfaces_as_an_unobservable_finding_naming_the_process` — the
  finding names `java -jar tla2tools.jar`.
- `test_declaring_a_spawn_port_does_not_silence_the_boundary` — **the subtle
  half.** A declared `process.spawn` port makes the spawn itself non-gap, and
  under MF-013 that was the end of it: verdict clean. Declaring `tlc_process`
  says "I spawn java"; it does not say what java then wrote. The run now refuses
  even though `gaps == []`.
- `test_end_to_end_real_spawn_through_the_sandbox` — a real `subprocess.run`
  through the real patches.
- `test_a_child_that_writes_is_proof_the_boundary_is_real` — spawns a child that
  writes a real file, asserts the file exists, and asserts the sandbox recorded
  **no** write for it. That is the concrete harm the finding declares.

## 4. The inverse test: nothing downgrades the verdict

`TestNothingDowngradesAnUnobservableVerdict`, built exactly as MF-013 built its
gap-suppression inverse. Every test asserts the NEGATIVE. There is deliberately
no test that an opt-out works, because no opt-out exists.

Coverage:

- manifest-level `observable: true`, `assume_observable`, `allow_unobservable`,
  `trusted_runtime`, `justification` prose
- port-level `skip_observability`
- **every** key in `SUPPRESSION_KEYS` applied at once — identical verdict,
  identical `ok`, identical finding count
- lying in the manifest (`runtime: python` on a JBang reference) does not create
  observability
- environment variables (`EFFECT_CONFORMANCE_ALLOW_UNOBSERVABLE`,
  `SPEC_DOUBLE_SKIP_OBSERVABILITY`, `TLA_SPEC_DEV_ASSUME_OBSERVABLE`)
- structural: `diff_effects` accepts no suppression keyword; `EffectRecorder`
  exposes no `clear_unobservable`/`waive`; `EffectConformanceReport.ok`'s source
  (comments stripped) contains no `config`/`flag`/`os.environ`/`getattr(`/
  `manifest`/`if` — the gate is a pure conjunction of finding lists
- CLI: `scripts/effect_conformance_report.py` contains no `--allow-unobservable`,
  `--skip-observability`, `--assume-observable`, `--no-observability`, or
  `--ignore-unobservable`

The observability-shaped keys were added to `SUPPRESSION_KEYS` so they are
scanned and **reported** in `ignored_suppression_keys` rather than silently
ignored — an author must not be able to believe a refusal was waived.

## 5. Documentation

- `references/modular_fuzzing.md` — "Observable scope of the effect oracle
  (MF-027)" and "Known limitation: exported Test Graph cases get no effect
  checking", both under Oracles alongside oracle 3.
- `SKILL.md` — Testing Layers item 3 now states the observable scope plainly,
  headed "read this before onboarding a non-Python project".
- Follow-up filed: https://github.com/haydenrear/tla-spec-dev/issues/44

## Consequence worth flagging to the epic owner

This repository's promoted manifest declares two `process.spawn` ports
(`tlc_process` -> `*java*`, `test_process` -> `*pytest*`). Under the new rule, a
**real corpus run of this repository** will therefore report `unobservable`
rather than `clean`, because the harness genuinely cannot see inside the `java`
and `pytest` children it spawns.

That is the correct and intended outcome — it is a true statement about what the
oracle can see — but it means MF-023's dogfooding sweep must either run those
boundaries through in-process adapters or record the refusal as a known,
accurate limitation. Corpus execution is deferred epic-wide to MF-023 (#30), so
no sweep was run here. Flagged rather than worked around.
