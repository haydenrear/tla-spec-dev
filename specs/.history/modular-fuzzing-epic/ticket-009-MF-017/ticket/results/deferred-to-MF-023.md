# MF-017: validations deferred to MF-023 (#30)

Required by `planning_rules.case_execution_rule` (owner direction 2026-07-18):
each ticket records which validations it did not run, so the dogfooding ticket
inherits an accurate checklist.

## Not run by this ticket — MF-023 must exercise them

| Deferred validation | Why it is deferred | What MF-023 must do |
|---|---|---|
| Case generation over the reachable state graph | Epic-wide deferral. Also blocked at source by the surviving MF-011 gate finding: `C1 is touched by 11 actions, exceeding max_component_actions 8`. That is a TRUE finding about the undecomposed single-module baseline. | Decompose into Internal/External, then generate. Do **not** pass `--allow-over-budget` and do **not** renegotiate `max_component_actions`. |
| Distilled-corpus run | Requires generated cases. | Run after decomposition. |
| Effect-conformance sweep | Requires generated cases. | Run after decomposition. |
| Mutation kill test / kill rate | Requires generated cases; kill-rate evidence is also MF-019's anti-gaming input. | Run after decomposition; feed surviving mutants into the feedback loop below. |
| Generated spec cases for the new `SkillFeedbackCloseOutAdapter` | The adapter itself is validated by the spec-unit tests below; only its *generated-case* execution is deferred. | Include `CloseTicket` in the generated-case run and confirm the adapter conforms. |

## Run and green in this ticket

- TLC on ticket-local current — `tlc-current.txt` (2,923 distinct, depth 23)
- `python3 scripts/tla_spec_dev.py --spec-root specs run spec-unit-tests --ticket MF-017` — `spec-unit-tests.txt`
- `uv run --with pytest -m pytest tests -q` — `pytest-repository.txt` (171 passed)
- Test graphs `specWorkflow` + `cliWorkflow` — `graph-*.txt`, reports under `graph-reports/`

## MF-023 is this mechanism's first real consumer

MF-023 decomposes this repository by running the finished toolchain on itself,
and is instructed that tool inadequacies found during that run are first-class
findings outranking a clean migration. **`specs/results/skill_feedback.md` is
where that material goes.** Concretely, MF-023 should expect to record:

- `surviving-mutants` — mutants the decomposed model's generators cannot reach,
  with `why_unreached:` naming the generator/strategy/profile rule at fault.
- `unmodelable-effects` — filesystem, git, and subprocess effects of the CLI
  that have no reasonable port-state modeling, with `why_not_port_state:`.
- `budget-and-metric` — every budget that had to move to make the decomposed
  model pass, and any gate comparing quantities that are not commensurable
  (the `max_component_actions` finding above is the live candidate: if the
  decomposition cannot satisfy it, say so as a finding rather than raising it).
- `profile-schema-cli` — every step of the decomposition that needed a manual
  workaround, with `forced_workaround:` and `data_loss:`.

Close-out records whether those were filed and where; an unreviewed retro is
recorded as **not filed**, not silently accepted.
