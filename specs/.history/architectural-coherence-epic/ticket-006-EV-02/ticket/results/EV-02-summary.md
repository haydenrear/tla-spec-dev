# EV-02 — the evals as a fact-finding mission, and the follow-up charter

The last ticket of `architectural-coherence`. **The deliverable is findings, not
fixes.** Nothing was fixed inline; five findings were filed at exactly the
deferment budget; the fixtures are byte-identical before and after.

## What ran

| run | what it measured | record |
|---|---|---|
| `ex4-run1` | aim 1 (six seeded faults × two declared arms, with control), aim 2 (both aspects), aim 3 generation control | `examples/validation/runs/ex4-run1/scoring.md` |
| `ex4-run2` | the two-run rule: the whole aim-1 matrix re-executed over an independently generated corpus; failure replay | `examples/validation/runs/ex4-run2/scoring.md` |
| `ex4-run3` | blind agent: author an aspect from the public surface only | `examples/validation/runs/ex4-run3/scoring.md` |
| `ex5-run1` | the enumerated answer key; blind agent: DP-1, the centrepiece | `examples/validation/runs/ex5-run1/scoring.md` |
| `ex5-run2` | EV-01-DF-02 verified independently and its blast radius enumerated | `examples/validation/runs/ex5-run2/scoring.md` |
| `ex6-run1` | both refusals: the synthetic Jenga and this repository's own model | `examples/validation/runs/ex6-run1/scoring.md` |

## The headline numbers

**Aim 1 — control GREEN on both arms (330 cases, exit 0) before any mutant.**

| id | fault class | ARM A (corpus alone) | ARM B (+ content provider) | predicted |
|---|---|---|---|---|
| F1 | wrong value | KILLED (44 pts, `tla_projected_state`) | KILLED (88) | A and B ✓ |
| F2 | wrong field | KILLED (88, `tla_output`) | KILLED (88) | A and B ✓ |
| F3 | off-by-one, durable | **SURVIVED** | KILLED (44, `provider_content_assertion`) | B only ✓ |
| F4 | wrong status | KILLED (22, `tla_output`) | KILLED (22) | A and B ✓ |
| F5 | swallowed error | **SURVIVED** | KILLED (44, `provider_content_assertion`) | B only ✓ |
| F6 | off-by-one, in-memory | KILLED (15 of 66, `tla_output`) | KILLED (15) | A and B ✓ |

**ARM A: 4 of 6. ARM B: 6 of 6.** Baseline MF-038: 0 of 9, kill rate 0.31.
Every per-fault prediction held, including both predicted survivors.

**The caveat that must travel with the 4/6:** MF-029 recovers 0 of 5 parameters
on this model, so the adapter takes the action argument from the oracle
(EV-01-DF-01). ARM A's 4/6 is an **upper bound** on what a corpus with honestly
recovered parameters would achieve. Confirmed independently by the blind aspect
agent, who had never been told DF-01 existed. Attribute per mechanism: F4's kill
is the **content-bearing output projection**, F3/F5's are the **provider**.

**Aim 3 — determinism, both halves.** Generation byte-identical (same `cases.py`
sha256 EV-01 recorded, across worktrees, output paths and two Python
interpreters). Execution byte-identical across 14 executions **including twelve
failing ones**. Three seeded failures replayed verbatim from the runner's own
`replay` command, twice each: **6 of 6 reproduce the originating error exactly.**
A3-P3 converted from prediction to measurement.

**The architecture half — precision 1.000, recall 1.000.** All four seeded
divergences at the exact `file:line`, plus the absence, plus zero false
positives on the coherent twin. Every refusal held. Every scan exit 0.

## EV-01-DF-02, promoted into scope: verified, and worse than filed

- The failed decomposition criteria appear **nowhere** in the reflexion report —
  not in the text, not in the JSON, and `blind_spots` is `[]`.
- **The fully degenerate case is not caught.** A declared ONE-component partition
  on a codebase with four real divergences reports `coherent`, exit 0. The guard
  reads `if not report.unported_pairs and len(names) >= 2` and excludes the one
  blob it exists for. `divergence_detectable` is computed `false` and no consumer
  reads it. **DP-2 scored MISSED.**
- **Blast radius, enumerated:** all 203 set partitions of the divergent twin's
  variables — 71 `divergent`, 120 `unmappable`, **12 `coherent`, and all 12 fail
  the criteria while zero of the 12 honest partitions produce a clean.**
- **Downstream does NOT inherit.** AC-04's delta refuses even the maximal gaming
  move (`unattributable`, stable basis 0 → 0); the ledger reads the delta report
  and never the verdict; nothing blocks on `architecture_scan`. The radius is
  narrow in consequence and wide in record.
- **The mitigation exists in the wrong artifact.** AC-03's prompt documents this
  defect by name and adds Gate B (V1 refuses, V3 degrades). AC-03 is a prompt;
  AC-02 is a program.

Filed as **EV-02-DF-01**.

## The finding worth more than any mechanism the epic shipped

Working from the public README alone, the blind aspect author found that
**the public surface is false of the model**: `Fail(i)` removes `i` from
`delivered` and `Record(i)` requires `i \in delivered`, so a failed item can
never reach the ledger — while the README promises exactly that. **No case
module could ever catch it**: a case module may not add an action and there is
no action to enter. The value came from the act of authoring the aspect, not
from the cases it generated. Its strength is not expressible as a kill rate.

## Findings filed (5 — at budget, none fixed)

| id | severity | what |
|---|---|---|
| EV-02-DF-01 | major | false `coherent` from a declared non-decomposing / one-blob partition; `len(names) >= 2`; Gate B is in the prompt, not the program |
| EV-02-DF-02 | major | a checked-in case module cannot be generated where the convention puts it (TLC cwd, no module search path, exit 150) |
| EV-02-DF-03 | minor | `param_recovery_audit.md` contradicts the corpus it audits (the audit for EV-01-DF-01) |
| EV-02-DF-04 | major | a Given cannot be written from the public surface; Step 0's provenance rule is unenforceable |
| EV-02-DF-05 | minor | X-P3 fails: six documentation friction items, rooted in every published command assuming an external view |

Two eval-protocol findings (EV-02-PROTO-01 redaction that announces itself,
EV-02-PROTO-02 a blind run's mutant catalog must be an artifact) are recorded in
`NEXT-EPIC.md` §4 rather than in the repository backlog: they are about how to
run an eval, not defects in this repository.

## Validation matrix

| check | result | evidence |
|---|---|---|
| zero TLA+ model delta | `current` == `desired`, byte for byte | `zero-model-delta.txt` |
| TLC | green — 32,122,220 generated / 1,292,951 distinct / depth 26, 0 left on queue | `tlc-current.txt` |
| spec-unit tests | 2 targets, 71 + 68, exit 0 | `spec-unit-tests.txt` |
| repository unit tests | 864 passed, 1 failed — `test_skill_requires_two_minute_case_generation_budget`, the documentation-content guard already filed as **CM-01-DF-01** and explicitly not this ticket's | `repository-unit-tests.txt` |
| fixture integrity | `check_twins.py` exit 0 before and after; `git status` on `examples/` clean after every mutant | `twin-integrity.txt`, `fixture-restored.txt` |
| test graphs | `cliWorkflow` green. `specWorkflow` RED at `spec.workflow.failure_cleanup_probe` ("node launcher exited with live descendants") — **reproduced identically on the unmodified epic tip 60d4a51**, so it is a pre-existing baseline red, not this ticket's. Escalated to the owner rather than filed, to stay at the deferment budget of 5. | `test-graphs.txt` |

## Measurement evidence

`kill-matrix-run1.json`, `kill-matrix-run2.json`,
`determinism-run1-vs-run2.json` (the 14-row identity table),
`replay.json`, `df02-blast-radius.json` (all 203 partitions).
The three harness scripts are kept at
`examples/validation/runs/ex4-run1/artifacts/` so every number is re-derivable.

**`NEXT-EPIC.md`** at the repository root is this ticket's most valuable output:
what the evidence killed, what survived, what the next epic should build
(NE-01..04), and the do-not-re-litigate section.
