# EV-01 — eval fixtures and committed predictions

**Zero TLA+ model delta, as planned.** `specs/.history/architectural-coherence-epic/ticket-005-EV-01/ticket/current` and
`specs/.history/architectural-coherence-epic/ticket-005-EV-01/ticket/desired` are byte-identical (`zero-model-delta.txt`, an
empty `diff -r`). No action was invented to have a delta. EV-01 builds the
instrument that will judge this epic; it does not change the program the
instrument measures.

## What was built

| fixture | purpose | answer key |
|---|---|---|
| `examples/validation/ex4_pipeline_coherent` | the POSITIVE architecture test the epic never had, plus the corpus / fault / aspect / determinism arms | `coherent`, 0 divergences, 0 absences, `divergence_detectable = true`; 6 seeded faults; 2 authored aspects; corpus fingerprint |
| `examples/validation/ex5_pipeline_divergent` | the twin: same model, same behavior, reaching code | 4 divergences with `file:line` + 1 absence, enumerated in advance; the worked map-gaming example and AC-04's refusal of it |
| `examples/validation/ex6_jenga` | the synthetic Jenga (CONTROL) | `unmappable` / `unfalsifiable_coherence`, 0 divergences that are NOT a clean result |
| `specs/program_model/TlaSpecDevCli.tla` | the REAL Jenga — used as-is, not rebuilt | one component, Q = 0.000, `unmappable`, ownership `NOT MEASURABLE` |
| `examples/validation/PREDICTIONS.md` | the epic's predictions, committed before any dispatch | 8 degenerate paths, DP-1 the centrepiece |
| `examples/validation/check_twins.py` | fixture-integrity gate for the twins | 5 files must stay byte-identical |

## Validation matrix

| check | command | result |
|---|---|---|
| TLC, ticket current | `bash scripts/run_tlc.sh specs/.history/architectural-coherence-epic/ticket-005-EV-01/ticket/current/TlaSpecDevCli.tla specs/.history/architectural-coherence-epic/ticket-005-EV-01/ticket/current/MC.cfg` | GREEN — 32,122,220 generated / 1,292,951 distinct / depth 26, 0 left on queue (`tlc-current.txt`) |
| spec unit tests | `python3 scripts/tla_spec_dev.py --spec-root specs run spec-unit-tests --ticket EV-01` | PASS, 2 targets, 71 + 68 (`spec-unit-tests.txt`) |
| repository unit tests | `uv run --with pytest --with pyyaml -m pytest tests -q` | 864 passed, 1 failed — the known-red `test_skill_requires_two_minute_case_generation_budget`, already filed as CM-01-DF-01 and explicitly not this ticket's (`repository-unit-tests.txt`) |
| zero model delta | `diff -r .../current .../desired` | empty (`zero-model-delta.txt`) |
| twin integrity | `python3 examples/validation/check_twins.py` | holds, 5 files identical (`twin-integrity.txt`) |

## Every fixture command EV-01 actually ran

Kept under each fixture's `evidence/`:

- `ex4`: TLC (114 distinct / depth 11); `analyze architecture` declared
  partition (Q = 0.133, all three criteria met); reflexion → `coherent`
  (`evidence/reflexion.txt`, `.json`); `generate_python` (typed ports);
  generation → 330 cases from 121 states (`evidence/generation.log`); **ARM A
  control green** (`evidence/control-armA-corpus-only.log`); **ARM B control
  green** (`evidence/control-armB-corpus-plus-provider.log`); ARM B rerun,
  byte-identical (`evidence/control-armB-rerun.log`); two case-module
  generations (50 and 6 cases); `case_modules validate` and `coverage`
  (`UNCOVERED: none`); behavior suite 8/8; regeneration fingerprint identical
  (`evidence/corpus_fingerprint.txt`).
- `ex5`: reflexion → `divergent`, 4 divergences + 1 absence; the gamed
  partition (`gamed/reflexion.gamed.txt`, 4 → 3 divergences, 1 → 0 absences,
  no code change); the AC-04 delta across it → `unattributable`
  (`gamed/delta-gamed.txt`); behavior suite 8/8 on the byte-identical file.
- `ex6`: TLC (166 distinct / depth 8); emergent descriptor (1 component,
  Q = 0.000); declared descriptor (Q = −0.186, two criteria FAIL); reflexion →
  `unmappable` / `unfalsifiable_coherence`, `divergence_detectable = false`.

## Existing examples: checked, not patched

- `examples/distributed_history` — `case_modules validate` exit 0 for all three
  declared modules; example test suite passes; both `Scenario_RejectedRequests`
  (14 cases) and `Scenario_IdempotentResubmit` (16 cases) reproduce
  `examples/case_modules/MEASUREMENTS.md` exactly, with **0** spurious
  zero-case warnings (the CM-01 fix holds).
- `examples/effect_providers` — `tests/test_effect_provider_example_validation.py`
  passes.
- `examples/validation/ex3_over_complex` — `analyze complexity` reproduces the
  PREDICTIONS.md baseline (`bound = 8,388,608`, the advisory warning fires,
  exit 0).
- **Breakage found was FILED, not patched:** EV-01-DF-03 (the AC-02 dogfood
  record contradicts its own measurement and its edge counts have drifted).

## Deferred findings filed (3 of a budget of 5)

| id | severity | one line |
|---|---|---|
| EV-01-DF-01 | major | MF-029 recovers 0 of 5 parameters on a set-membership model, so adapters must take the argument from the oracle — one whole fault class leaves the corpus's reach, silently |
| EV-01-DF-02 | major | a DECLARED partition the descriptor calls NOT DECOMPOSING is still consumed, and the reflexion check reports `coherent` against it with no signal in the report |
| EV-01-DF-03 | minor | the AC-02 dogfood record says the check "found edges across both" unported pairs; the measurement says 0 divergences — and the edge counts have drifted 258 → 263 |

The known-red `test_skill_requires_two_minute_case_generation_budget` is
CM-01-DF-01 and was not re-filed.
