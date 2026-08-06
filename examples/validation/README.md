# Validation examples — restart of the MF-037 plan (issue #62)

Three example projects, real agents doing real tickets, repeated runs.
Re-aimed after the complexity-descriptor epic (#71/#72/#73): the things under
test are the **descriptor** (CD-01), the **intuition doc** (CD-02), and the
**fitness functions** (CD-03) — there are no gates and no suggested moves.

| Example | Project | Tests |
| --- | --- | --- |
| ex1 scaffold-only | `ex1_scaffold_only/taskq` — small CLI, no specs yet | the new-user entry path: scaffold, scan, judge, configure fitness functions |
| ex2 ticket workflow | `../distributed_history` | a real ticket end-to-end on the internal/external example that the old gate regime made unusable |
| ex3 over-complex | `ex3_over_complex/order_hub` — god-state model, oversized domains | descriptor + intuition must lead an agent to a validated complexity-lowering refactor |

Protocol:

1. `PREDICTIONS.md` is committed BEFORE any dispatch.
2. Each run copies its example project into a scratch workspace; agents never
   work in this tree and are never shown `PREDICTIONS.md` or other runs'
   records.
3. The toolchain is used from the epic checkout via
   `python3 <repo>/scripts/tla_spec_dev.py` (never the PATH wrapper).
4. After each run the epic owner collects the agent's report and key
   artifacts under `runs/<example>-run<N>/` and scores it against the
   predictions.
5. Each example runs at least twice. Findings are filed, never fixed inline.
6. Run 4 onward (post effect-provider merge): tasks enter through
   `references/effectful_onboarding.md` and compose complexity minimization
   with agent-authored effect providers — see the run-4 addendum in
   PREDICTIONS.md. The example projects stay pristine fixtures; providers
   are authored by the agents in their scratch copies, per the product's
   own design.

## Architectural-coherence epic (EV-01, 2026-07-27)

Three fixtures added for the architecture / case-module / effect-provider
surface the three examples above never exercised. `PREDICTIONS.md` carries a
new section for them, committed before any dispatch.

| Example | Project | Tests |
| --- | --- | --- |
| ex4 pipeline coherent | `ex4_pipeline_coherent` — decomposable model, matching code, corpus, one effect port | the POSITIVE test the epic lacked: `coherent` with a detectable divergence; 6 seeded content faults across two measurement arms; two authored aspects; determinism |
| ex5 pipeline divergent | `ex5_pipeline_divergent` — the twin | 4 enumerated divergences + 1 absence with `file:line`; the worked map-gaming example and AC-04's refusal |
| ex6 jenga | `ex6_jenga` — synthetic god-state model + code | the `unfalsifiable_coherence` refusal, with 0 divergences that are NOT a clean result |

The **primary** incoherent example is not in this directory: it is this
repository's own `specs/program_model/TlaSpecDevCli.tla` (one component,
Q = 0.000, `lastCommand`/`result` written by all fifteen commands). `ex6_jenga`
is the control, and its README states exactly what it adds and does not add.

Fixture integrity: `python3 examples/validation/check_twins.py` asserts that
ex4 and ex5 still share one experiment — the four architecture inputs and the
behavioral suite must be byte-identical. Run it before and after every EV-02
run on either twin.

## Round 2 — EV-03 (2026-07-30)

The `architectural-coherence` epic repaired the 14 defects EV-02 found (RP-01..
RP-05, RP-07) and EV-03 re-ran the whole suite against the repaired tree,
**re-scored against the SAME `PREDICTIONS.md`** — that file was not edited.

Start at **`runs/ROUND-2-DELTA.md`**, the round-1 vs round-2 delta table.

| run | arm |
|---|---|
| `runs/ex5-run3` | the 203-partition sweep rerun (RP-01) + the answer key re-measured |
| `runs/ex4-run4` | both mutant catalogues, both arms, plus the case-module path end to end (RP-02, RP-03) |
| `runs/ex4-run5` | determinism and replay, 38 executions across two independently generated corpora |
| `runs/ex6-run2` | the refusals re-measured, including this repository's own declared partition |
| `runs/ex5-run4` | **blind run A** — DP-1, the centrepiece, on a fresh scratch copy |
| `runs/ex4-run6` | **blind run B** — aspect authoring, on a fresh scratch copy |

Protocol corrections in force from round 1, both binding:

- **fixtures carry purpose-written neutral text, not redaction stubs.** The
  round-2 sanitizers (`runs/ex5-run4/artifacts/sanitize_runA.py`,
  `runs/ex4-run6/artifacts/sanitize_runB.py`) assert that every replacement
  preserves the file's line count where the answer key is `file:line`, and the
  sanitized copy is verified to reproduce the identical divergence sites and the
  identical digests before dispatch;
- **DP-1 scoring compares the ARCHITECTURE digest as well as the map digest.**
  Round 2 applied it, both were unchanged — and then found a route to `coherent`
  that moves neither (EV-03-DF-03). A digest rule can only catch a lie told in a
  declared artifact.

**Interpreter (EV-02-DF-05, still open in the docs).** No `python3` on the eval
machine's PATH carries `yaml`, `pytest` and `tomllib` together. Every round-2
measurement used one pinned interpreter, built with:

```bash
uv venv --python 3.13 <scratch>/venv
uv pip install --python <scratch>/venv/bin/python pytest pyyaml
```

The toolchain's YAML fallback parser and PyYAML were checked to produce
byte-identical JSON on these fixtures before any number was taken.
