# RC-02 — model delta: NONE, measured

`model_delta_expectation` was NONE, with the standing instruction that if the
state space moves at all, say why before closing. **It did not move.**

| | RC-01 (`05acf8c`) | MF-026 round 3 (independent) | **RC-02** |
|---|---|---|---|
| states generated | 392,923,694 | 392,923,694 | **392,923,694** |
| distinct states | 10,331,543 | 10,331,543 | **10,331,543** |
| depth | 26 | 26 | **26** |
| wall clock | 11min 15s | 11min 22s | **11min 24s** |
| result | no error | no error | **no error** |

Evidence: `specs/tickets/RC-02/results/tlc-current.txt`
(`bash scripts/run_tlc.sh specs/current/TlaSpecDevCli.tla specs/current/MC.cfg`).

Every figure is identical to RC-01's and to the auditor's independent
reproduction, to the state. That is the expected result and the reason to expect
it is structural rather than lucky:

* the only edits to any `.tla` module are **comment lines** — three `@port`
  annotations and a paragraph above `InstallLocalCli`. Nothing parses `@port`;
  `TlaSpecDevCli.tla` says so where the tag is defined. No variable, guard,
  disjunct, invariant or constant changed, in any of the three trees.
* the manifest edits are `effects.actions` rows and comments. TLC does not read
  `spec_manifest.yaml`.
* the program change (N-2) constrains where `generate cases` may write. The
  model's `GenerateCases` action records no verdict and touches only
  `lastCommand` and `result`; a refusal at the CLI is not a modeled transition,
  exactly as the three `--out` refusals RC-01 added were not.

The advisory budget position is unchanged and is restated rather than
renegotiated: `budgets.tlc_seconds` is 120 and this model takes 684s to check,
5.7x over. Nothing enforces it (`scripts/run_tlc.sh` applies no timeout), so
nothing failed. RC-01 flagged this for the owner; RC-02 neither improves nor
worsens it, and does not touch the budget.

## Suite

| | epic tip `a866957` | RC-02 |
|---|---|---|
| `uv run --with pytest --with pyyaml python -m pytest tests -q` | **980 passed, 0 failed** | **1076 passed, 0 failed** |

+96 collected: 88 tests this ticket wrote (80 citation checks — two assertions
over 40 scoped files; 6 manifest port/mirror checks over three trees; 2
`generate cases --out` constraint checks) and 8 that `open ticket RC-02`
scaffolded into `specs/tickets/RC-02/`, collected by
`tests/test_spec_yaml_valid.py`.

Two existing tests and three spec adapters were UPDATED, not relaxed, for the
N-2 constraint: they passed an absolute `--out` outside any `specs/` directory
and now pass one inside. Each asserts exactly what it asserted before.

Project spec-unit tests: **73 passed** (`run spec-unit-tests --scope project`,
exit 0) — `specs/tickets/RC-02/results/spec-unit-project.txt`.
