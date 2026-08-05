# Author a seeded-fault catalogue from scratch, against two implementations

You have never seen the catalogue this project already uses, and you must not go
looking for it. Your value here is precisely that you do not know what it
contains: the last two rounds found that a catalogue written by the author of
the mechanisms flatters those mechanisms by roughly a quarter.

## What you are given

Repository root: `/Users/hayde/IdeaProjects/wt-epic-hexagonal-prompting-EVAL-RERUN`

- Implementation **ONE**: `/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/b726dabf-a199-4b0c-8c2d-dda863fb43b7/scratchpad/blind/artifact_P`
- Implementation **TWO**: `/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/b726dabf-a199-4b0c-8c2d-dda863fb43b7/scratchpad/blind/artifact_Q`
- The requirement: `examples/validation/ab/FEATURE.md`
- The state machine both are measured against: `examples/validation/ab/model/QuotaLedger.tla`
  and `examples/validation/ab/model/QuotaLedger.cfg` and `model/spec_manifest.yaml`
- The shared hand-written behavioral suite: `examples/validation/ab/tests/test_behavior.py`

## Files you MUST NOT open

- `examples/validation/ab/seeded_faults.toml`
- `examples/validation/ab/check_catalogue.py`
- `examples/validation/ab/reference/`
- `examples/validation/ab/README.md`
- `examples/validation/ab/eval/`
- `examples/validation/PREDICTIONS-HP.md`
- anything under `specs/results/scorecards/` or `specs/.history/`
- `NEXT-EPIC.md`

If you open one by accident, say so at the top of your output.

## What to produce

Write to `/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/b726dabf-a199-4b0c-8c2d-dda863fb43b7/scratchpad/channels/blind_author/`:

1. `catalogue_P.toml` and `catalogue_Q.toml` — a fault catalogue per
   implementation. TOML shape, one `[[mutants]]` table each, with these fields,
   all required:

   ```toml
   [catalogue]
   id = "BLIND-AUTHOR-P"
   anchored_on = "<the file the mutants mostly live in>"

   [[mutants]]
   id = "BA-P01"
   fault_class = "<your own class name; invent the taxonomy you need>"
   gap_targeted = "<what kind of checking you expect to miss this, and why>"
   boundary_kind = "invariant"        # or "port"
   boundary_ref = "<the rule of FEATURE.md it violates>"
   refine_variable = "<the model variable a survivor says to go and refine>"
   refine_action = "<the model action likewise>"
   path = "<path relative to the implementation root>"
   find = "<exact text, must occur EXACTLY ONCE in that file>"
   replace = "<exact replacement>"
   description = "<one line>"
   semantic = "<the behavior change, in implementation-independent terms>"
   ```

   Aim for 10-15 mutants per implementation. Seed faults you think are REAL —
   the kind a competent engineer actually writes — and deliberately include some
   in classes you suspect nothing can see.

2. `VERIFY.md` — proof, per mutant, that:
   - the `find` occurs **exactly once** in its file,
   - apply-then-revert is byte-identical,
   - the mutated file still parses,
   - **the mutant is a real defect and not an equivalent mutant** — show a
     concrete input/observation, run against both the clean and the mutated
     tree, where the two differ. A mutant you cannot separate from correct
     behavior must be dropped and recorded in REJECTED, not shipped.

   Write your own throwaway scripts under your output directory. Do NOT modify
   either implementation permanently.

3. `REJECTED.md` — **this is the most valuable thing you will produce.** Every
   fault you considered and did NOT seed, and why. Two rounds running, this
   section has been worth more than the catalogue. Be specific: name the class,
   the reason, and whether the reason is "this is not a real fault" or "I could
   not find a way to observe it", because those are very different and the
   second one has been wrong before.

4. `FINDINGS.md` — anything you noticed about the requirement, the model, the
   shared suite, or the two implementations that is *not* a mutant. Disagreements
   between the specification and the model, between the model and the code,
   between the two implementations in UNMUTATED code, assertions nothing holds,
   answer keys leaking into files you were allowed to read. Number them.

Do not run any harness in `examples/validation/ab/eval/` or under
`specs/results/`. Do not commit anything to git.
