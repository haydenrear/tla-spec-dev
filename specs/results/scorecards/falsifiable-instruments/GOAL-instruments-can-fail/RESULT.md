# `GOAL-instruments-can-fail` — decided at FI-06

| | |
|---|---|
| **baseline** | *roughly 0 of ~9.* No instrument in this repository had ever shipped a demonstrated failing input. Five were known incapable of producing a refuting result. Measured at `da075ce`. |
| **harness** | FI-02's enumeration, re-run at FI-06 on the integrated tip so the count describes the epic rather than a branch. |
| **measured** | **40 enumerated · 5 not-an-instrument · 35 instruments · 26 with a demonstrated failing input · 9 without · 12 with a demonstrated blind spot · 0 reproduction failures.** Artifact: `../measure/instruments-at-the-tip.json`, `demonstrate.py --format json` at `6c05d22`, exit 0. |
| **target** | *"Every shipped instrument is ENUMERATED and CLASSIFIED … **NO TARGET ON THE RATIO** … What is targeted is that **NOTHING IS SILENTLY OMITTED** from the enumeration."* |
| **verdict** | **MISSED.** The classification clause is met and is real work. **The goal's only target is not met, and the mechanism that would meet it was never built.** |

---

## Why MISSED and not "met with a caveat"

The goal deliberately refuses a target on the ratio, so the ratio cannot decide
it. It names exactly one thing to be targeted and that is the thing that failed.

`tests/test_instrument_demonstrations.py::test_the_named_instruments_are_all_enumerated`
asserts `required <= enumerated` over a literal list of paths. It catches a
**rename**. It structurally **cannot** catch an instrument that was never added,
because a new instrument is not in `required` and the subset relation stays true.
That is `FI-04-DF-04`, filed inside this epic and not closed.

**It failed three times inside the epic with the suite fully green** — FI-04's
`divergence.py`, and both of FI-05's — each caught only because a ticket agent
thought to look during a reconcile.

**FI-06's adversarial channel found at least eight more** (`FI-06-DF-01`), each
verified absent from `instruments.toml` by `tomllib` lookup and present on disk:

```
examples/validation/ab/eval/run_arm_swap.py       SystemExit(status or report_control_state(out))
examples/validation/instruments/demonstrate.py    the enumerator itself
tests/test_instrument_demonstrations.py           the enumerator's own tripwire
tests/test_produced_code_prompt.py                gating scan over examples/ and prompts/
scripts/extract_spec_manifest.py                  validate_manifest; main() returns 1
scripts/generate_python.py:967                    same predicate; generation REFUSES
examples/run_distributed_history_validation.py    incl. an explicit NEGATIVE control
examples/validate_split_desired_workflow.py       SystemExit on scaffold drift
examples/effect_providers/run_validations.py      + three validate.py under it
```

**`run_arm_swap.py` was shipped by FI-04 in the same directory, in the same
reconcile, as the instrument FI-04 registered by hand while writing the finding
about exactly this failure.** And `extract_spec_manifest.py` is **red on the
shipped tree right now** — exit 1, three `missing required manifest key` errors,
watched by nothing, sharing its predicate with the code generator.

---

## The numerator does not survive either

**All twelve `kind = "pytest"` failing slots declare `expect_exit = 0` and
nothing else.** `judge()` checks the exit code and substrings; `run_pytest` never
inspects output; pytest exits 0 when every collected test is **skipped**. A probe
registry whose failing slot is one `@pytest.mark.skip` test reports `ok`,
`WITH a demonstrated failing input 1`, `Every declared demonstration reproduced`,
exit 0. **This is the `R-H5` staleness failure generalised: a demonstration can
stop running entirely and the harness still calls it reproduced.**
`FI-06-DF-02`.

**Two rows have `failing.nodes` byte-identical to `passing.nodes`** —
`complexity-ledger` and `case-modules-validate`. There is no seeded break;
confirmed by excision rather than by reading. **A third,
`control-decision-driver`, goes red for a different reason than the one it
states** — `run_controls.py:613-618` short-circuits before the suite ever runs.
`FI-06-DF-03`.

```
                                      reported      honest
instruments enumerated                      35      >= 43   (floor; nothing enforces completeness)
with a demonstrated failing input           26      <= 23
   of which cannot go quietly green         --         11
without one                                  9      >= 20
```

**`26 of 35` is not a ratio over a known set. The denominator is a floor and the
numerator is a ceiling.**

---

## What the goal DID buy, and it is not nothing

1. **The baseline was wrong by nearly 4×.** The charter said *"roughly 0 of ~9"*;
   the enumeration found **35**. Before this epic nobody in this project knew how
   many instruments it shipped to within a factor of four. That alone justifies
   the ticket.
2. **Twelve declared blind spots**, six of which fail toward **green** — a class
   of defect that was previously invisible by construction. `run_controls.py`
   giving 15 of 15 false `SURVIVED` on a ported tree; the blinding sanitiser
   passing the exact leak sentence `PA-06-DF-11` measured; `dispatch-record`
   verifying GREEN on the empty evidence directory that is arms A and B's live
   state.
3. **R2 was followed, once, and visibly.** `port-scoped-control-check` ships a
   failing demonstration and **no passing one**, because `PA-M14` is inert on
   `reference_ports` and R2 says it is reported red rather than re-anchored into
   looking fine. No green was manufactured.
4. **The `R-H5` staleness class is now guarded on the cli slots.** FI-02's audit
   demonstration was pinned to `R-H5`; FI-03 implemented `R-H5`; the
   demonstration went green; and `test_every_fast_demonstration_reproduces`
   **caught it on the merge**, because that row asserts both `expect_exit = 1`
   and an `expect_output`. `FI-06-DF-02` is the same lesson not applied to the
   pytest slots.
5. **One row re-demonstrated itself on this ticket.** `ticket-state-agreement`
   is classified `no-instrument-exists`. After `open ticket FI-06`:
   `specs/tickets/FI-06/ticket.yaml:48` says `"status": "active"`,
   `ticket_plan.yaml:27` says `active_ticket: null`, and `ticket_plan.yaml:117`
   says FI-06 is `planned`. Three files disagree, the file an agent reads first
   is one of the wrong ones, and nothing compares them.

---

## What must happen before this goal is asked again

**Close `FI-04-DF-04`, with its own suggested fix and not by lengthening the
literal** — which the repository has already rejected twice
(`EVAL-RERUN-DF-01`'s module-name list, `FI-01-DF-01`'s `ARM_MODULE_PREFIXES`):

> have `close ticket` refuse when a ticket's diff adds an executable under a
> declared instrument root and the registry gained no row in the same commit.

One predicate over the diff, no taxonomy, and it puts the question to the author
who knows the answer. The eight rows above are the backlog it would have caught.

**Until then, no count derived from this registry should be quoted without the
sentence "the denominator is a floor."**
