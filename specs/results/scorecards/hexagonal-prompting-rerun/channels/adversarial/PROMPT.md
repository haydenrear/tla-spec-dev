# Attack this measurement. Your job is to falsify it, not to confirm it.

A measurement round has just been run in
`/Users/hayde/IdeaProjects/wt-epic-hexagonal-prompting-EVAL-RERUN`. You are the
adversarial channel. The previous two rounds each produced ~17 findings from a
pass like this one and ZERO from re-running the test suite, and six of the last
round's findings falsified a claim the round had already written down.

**Assume every number below is wrong until you have re-derived it yourself.**

## What was run

The run record is under
`specs/results/scorecards/hexagonal-prompting-rerun/`:

- `arms/arm_a/`, `arms/arm_b/` — two implementations of
  `examples/validation/ab/FEATURE.md`, produced by two different prompts
  (`examples/validation/ab/arm_a/PROMPT.md`, `arm_b/PROMPT.md`).
- `measure/catalogue_arm_{a,b}.toml` — the sealed catalogue
  (`examples/validation/ab/seeded_faults.toml`) re-anchored onto each tree.
- `measure/controls_arm_{a,b}.toml` — the positive/negative control record.
- `measure/rerun_arm_{a,b}_binding.py` — how the oracle reaches each tree.
- `GOAL-catch-bugs/kill-table-arm-{a,b}.json` — the per-mutant, per-instrument
  tables, plus `determinism-arm-{a,b}-run-2.json` and `reference-run.json`.
- `GOAL-simpler-same-behavior/mechanical.json` — the size/state/branch capture.

The driver is `examples/validation/ab/eval/run_controls.py`; the oracle is
`examples/validation/ab/eval/oracle.py`. Corpora were generated from
`examples/validation/ab/model/QuotaLedger.tla` with
`python3 scripts/tla_spec_dev.py --spec-root specs generate cases ...`
(never invoke `tla-spec-dev` from PATH).

## The claims this round intends to make. Break them.

1. **The positive control M07 is GREEN on both arms** — killed by every
   instrument that can execute the action it lives in, `NOT_DECIDABLE` on the
   two that provably cannot.
2. **The negative control N01 is GREEN on both arms** — survives every
   instrument, with a reality witness proving it is a fault and not an
   equivalent mutant.
3. **Every per-mutant verdict is identical between the two arms** except M07's
   `corpus-neg` cell, which the arm-B catalogue declares is not the same
   experiment. The structural difference between the two designs caught nothing.
4. **`corpus-whole` executes 3,734 of 43,128 cases (8.7%)**, 39,100 of the
   skips being refusal edges with no arguments, and **exactly half of `Reserve`
   (294 of 588) is structurally unreachable** because the model chooses an id
   the API allocates.
5. **The run is deterministic**: two full runs of all seven instruments on BOTH
   arms are byte-identical, failure text and per-action counts included.
6. **The hand-written suite kills 10 of 11 on both arms; the union of the six
   generated instruments kills 9 of 11 on arm A and 10 of 11 on arm B**, and the
   one mutant no instrument kills is the negative control, which also survives
   the suite.
7. **The mechanical block says arm B is LARGER**: 129 production lines to 122,
   11 branches to 10, 4 modules to 1, 25 public names to 20.
8. **`N01` survives the hand-written suite**, so the "the suite kills 10 of 10"
   bar this project has quoted for two epics rests on a catalogue containing no
   mutant that suite could miss.

## Specific things worth trying

- Re-derive at least three cells of each kill table yourself, from scratch, by
  applying the mutant and running the instrument. Do the tables reproduce?
- Does `KILLED` mean what the report says it means? What exactly makes a case
  raise? Could a cell be killed for a reason unrelated to the seeded fault?
- Are the two arms' catalogues really seeding the SAME semantic? Read
  `semantic` on each row and check the diff actually produces it.
- The arm-B catalogue seeds two mutants by ADDITION rather than perturbation,
  and substitutes a broader-reach variant for M07. Is that honest, or does it
  smuggle in an advantage or a disadvantage?
- `measure/rerun_arm_*_binding.py` carries a CACHE DISCLOSURE about a defect
  caught mid-run. Is the fix correct? Is there a second instance of the same
  class of problem anywhere in the pipeline?
- Are the declared `NOT_DECIDABLE` limitations actually verified, or believed?
- Is the executability accounting complete — does every case land in exactly one
  of ran / skipped, per action?
- Does anything in the round's own prose overstate what was measured?

## What to write

`/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/b726dabf-a199-4b0c-8c2d-dda863fb43b7/scratchpad/channels/adversarial/FINDINGS.md`

Numbered findings. For each: what you did, what you observed (paste it), which
claim it damages, and a severity of SEVERE / MODERATE / MINOR / NOT-A-FINDING.
Include a section **CLAIMS I TRIED TO BREAK AND COULD NOT**, with what you ran —
a claim that survived a real attack is evidence, and a claim nobody attacked is
not.

**FILE FINDINGS, FIX NOTHING.** Do not repair the harness, do not re-seed a
mutant, do not edit any catalogue or any result. Do not commit anything to git.
Write only under your own output directory.
