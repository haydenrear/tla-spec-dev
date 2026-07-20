# MF-023 — validation matrix

All commands run in the ticket worktree at the pinned epic tip 5575566.
Toolchain pinned to `python3 scripts/tla_spec_dev.py` throughout; the PATH
`tla-spec-dev` (which execs the stale installed skill at `da0a7ff`) was never
invoked, and `skill-manager sync` was never run.

| # | Check | Command | Result | Evidence |
|---|---|---|---|---|
| 1 | TLC — pre-split baseline | `bash scripts/run_tlc.sh …/current/TlaSpecDevCli.tla …/current/MC.cfg` | **PASS** — 5,619,356 generated / 231,621 distinct / depth 25, no error | `tlc-baseline-presplit.txt` |
| 2 | TLC — Internal view | `bash scripts/run_tlc.sh …/Internal.tla …/Internal.cfg` | **PASS** — 956,775 / 42,861 / depth 24, 14 invariants, no error | `tlc-internal-desired.txt` |
| 3 | TLC — External view | `bash scripts/run_tlc.sh …/External.tla …/External.cfg` | **PASS** — 5,387,735 / 231,621 / depth 25, 15 invariants, no error | `tlc-external-desired.txt` |
| 4 | Retention vs baseline | comparison of 1 and 3 | **EXACT** — identical distinct states and depth; generated differs by exactly 231,621 (one removed stutter self-loop per state) | `retention.md` |
| 5 | Spec-unit tests | `python3 scripts/tla_spec_dev.py --spec-root specs run spec-unit-tests --ticket MF-023` | **PASS** — 48 + 45 passed, 2 targets | `spec-unit-tests.txt` |
| 6 | Repository unit tests | `uv run --with pytest --with pyyaml -m pytest tests -q` | **PASS** — **427 passed** (baseline 420, no regression) | `repository-unit-tests.txt` |
| 7 | Test graph `specWorkflow` | `python3 <test-graph>/scripts/run.py specWorkflow` | **PASS** — BUILD SUCCESSFUL | `graph-specWorkflow.txt`, `graph-reports/` |
| 8 | Test graph `cliWorkflow` | `python3 <test-graph>/scripts/run.py cliWorkflow` | **PASS** — BUILD SUCCESSFUL | `graph-cliWorkflow.txt`, `graph-reports/` |
| 9 | `analyze complexity` — pre-split | `… analyze complexity …/TlaSpecDevCli.tla …/MC.cfg` | FAIL (correct) — C1 14 actions > 8; proposed the cut | `analyze-complexity-presplit.txt` |
| 10 | `analyze complexity` — Internal | `… analyze complexity …/Internal.tla …/Internal.cfg` | **FAIL, reported not tuned** — C1 7 vars > 6, 14 actions > 8 | `analyze-complexity-internal.txt` |
| 11 | `analyze complexity` — External | `… analyze complexity …/External.tla …/External.cfg` | PASS, but **VACUOUS** — sees 2 of 9 variables (FINDING 1) | `analyze-complexity-external.txt` |
| 12 | Case generation — refusal | generation without `--allow-over-budget` | **REFUSED, exit 2**, naming the failing components | `gen-internal-refusal.txt` |
| 13 | Case generation — Internal | with explicit `--allow-over-budget` | ran; 999,635 cases / 1.35 GB at full instance | `gen-internal-override.txt` |
| 14 | Case generation — External | no override needed (gate passed vacuously) | **KILLED** — exhausted the disk (FINDING 6) | `gen-external.txt` |
| 15 | `analyze corpus` — full instance | `… analyze corpus <1M-case package>` | **OOM-KILLED, exit 137** (FINDING 6) | `findings.md` |
| 16 | `analyze corpus` — reduced instance | `… analyze corpus <15,336-case package>` | **FAIL (correct), exit 1** — over cap, nothing trimmed, 4112x skew reported | `analyze-corpus-internal.txt` |
| 17 | Effect-conformance sweep | `run_generated_case_adapters.py … --batch --effect-report` | **`dead_surface`** — 0 observed effects over 40 cases, 5/5 ports dead (FINDING 4) | `effect-conformance-internal.json/.txt` |
| 18 | Mutation kill test | `run_kill_test.py --target … --cfg Internal.cfg --corpus-command …` | **`control_failed`, exit 2** — no rate computed, no mutant seeded (FINDING 5) | `kill-test-internal.txt/.json` |
| 19 | Kill-test boundary coverage | `run_kill_test.py --target specs/current --list-boundaries` | **20/20** boundaries carry a seeded fault (was 19/20 after the split; fault seeded, not waived) | `repository-unit-tests.txt` |
| 20 | Dangling-reference case | `pytest tests/test_source_model_references.py` | **now FAILS when a reference dangles** (verified by re-breaking: 2 failed → restored: 3 passed) | `findings.md` FINDING 8 |
| 21 | Component-cap satisfiability | derived from the tool's MEASURED matrix | **unsatisfiable by ANY partition** — singleton `{setup_phase}` is touched by 12/14 actions | `component-cap-satisfiability.txt` |
| 22 | Coverage audit (MF-026) | `prompts/coverage_audit.md`, per view | see `coverage-audit.md` | `coverage-audit.md` |
| 23 | Post-promotion unit suite | `uv run --with pytest --with pyyaml -m pytest tests -q` | see `post-promotion-verification.md` | `post-promotion-verification.md` |

## Deferred runs, all now executed

Every run deferred across the epic was executed. Three of them **could not
complete**, and the reason in each case is recorded as a first-class finding
rather than worked around:

| Deferred run | Executed? | Outcome |
|---|---|---|
| Case generation over the reachable state graph | yes | Internal completed (999,635 cases); External exhausted the disk |
| The distilled-corpus run | yes | gate FAILS correctly at reduced instance; OOM at full instance |
| The effect-conformance sweep | yes | `dead_surface` — no adapter can execute a case |
| The mutation kill test | yes | `control_failed` — correctly refused to compute a rate |

Nothing in this table was reported as passing on the strength of a run that did
not happen.
