# ex1 run 4 — scored against PREDICTIONS.md (R4-E1, R4-X1, R4-X2)

Run date 2026-07-22, composed surface, fresh onboarding. Owner verified: 48
EFFECT_FUZZ_FAILURE lines in the kill-probe evidence, the 1,640-point
campaign green, descriptors/fitness re-read, provider + usage descriptor
collected.

| Prediction | Verdict | Evidence |
| --- | --- | --- |
| R4-X2 complexity first | **PASS (exceeded)** | Not just ordering — the descriptor AND the corpus gate together priced a representation refactor mid-onboarding: the cli response variable moved to the per-case output oracle, External 424 → 63 distinct, corpus 3,055 → 454, bound clean 64, behavior untouched. The complexity surface actively shaped the effectful surface's cost, which is the "why this order" claim demonstrated. |
| R4-E1 port + content provider + campaign | **PASS** | TaskStorePort (load/persist) over the real taskq.json boundary; all 16 actions declare complete effect_ports; provider materializes before-state, fuzzes directory/file-representation dimensions from derived_seed, asserts persisted map == modeled after-state (which doubles as no-write-on-error), statuses ⊆ STATES, cap ≤ 2; campaign green over 1,640 points. |
| R4-E1 kill probe with replay | **PASS — the headline** | The exact MF-038 bug class (finish persists "pending", message/exit unchanged): 45 points killed, every one by the provider CONTENT assertion; the recorded replay command reproduced the identical failure (same case, iteration, derived seed); restore verified green. The 0/9 era is measurably over. |
| R4-X1 docs suffice | **PARTIAL → findings** | The agent completed everything but needed route-arounds for six real findings (below); the sequence-item parser bug (its finding 1) was already fixed at 37c6c65 before this scoring — the agent ran against the pre-fix tip. |

## Findings → filed as R4-DF-01..05 (post-main triage unless noted)

- **R4-DF-01** (fixed in docs same-day): Stage-5 command fails on a freshly
  onboarded repo (default target `specs/current`); onboarding doc now shows
  `--target specs/program_model`.
- **R4-DF-02**: the scaffolded `test_spec_unit_adapters.py` breaks once
  providers are configured — `python -m` invocation hits the runner's
  top-level `from effect_conformance import ...` (`ModuleNotFoundError`) and
  `--spec-dir` becomes mandatory. Scaffold template + runner import defect.
- **R4-DF-03**: replay commands are not self-contained — originating
  `PYTHONPATH` is not recorded, and CLI-pytest-surfaced failures record the
  ephemeral `uv run` interpreter, in tension with effect_providers.md's
  portability claim.
- **R4-DF-04**: pure alias wrapper actions (`CliAdd(t) == AddTask(t)`) are
  attributed to the inner definition site in the TLC dump — 7 of 9 external
  actions silently generated ZERO cases until anchored. Undocumented;
  silent-zero is the dangerous part.
- **R4-DF-05**: a red pytest step halts `run spec-unit-tests` before the
  case-adapters campaign runs, masking the campaign's own failure output.
- Observations (documented behavior): record-constructor domains honestly
  unknown; MF-029 parameter inference 328/328 internal, 0/454 external
  through wrappers.

## Verdict

Fresh-project onboarding of the composed surface works end to end from the
docs, the complexity stage measurably cheapened the effect stage, and the
provider's content assertions killed the precise bug class the old fuzzing
missed 9 of 9 times — with deterministic replay. Compounding confirmed.
