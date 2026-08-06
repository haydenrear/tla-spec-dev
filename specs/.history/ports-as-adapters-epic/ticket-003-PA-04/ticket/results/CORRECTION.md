# CORRECTION to this snapshot — the instrument was repaired after it was recorded

This snapshot was written at `5a58b2b`, when `close ticket PA-04` ran. The epic
owner's review then found a defect in the measurement driver, and the artifacts
in this directory were regenerated with the repaired instrument.

**Nothing about the measured cells changed.** Verified by diffing every
`per_mutant[*].cells` block before and after: identical on all three subjects.
What changed is the CONTROL ACCOUNTING that was missing beside them.

## Which numbers went stale, and why

| field | recorded at `5a58b2b` | corrected | why |
|---|---|---|---|
| `control_red` | `[]` | **4 pairs** (reference_ports), 3 (each arm) | The field only reported instruments that failed on UNMUTATED code. It never executed a control's declared ROLE, so `PA-M14` surviving four columns that each ran 294 accepting `Reserve` cases did not raise. |
| `GOAL-port-reach` verdict | "**MET**" | **clause 1 MET, clause 2 NOT MET** | The target reads "…and no positive control is red". Clause 2 was failing at the moment "MET" was written, and the same document already said every port kill number was a floor. |
| `M09` control state | flagged nothing | **RETIRED, decides nothing** | `retired_control` was not read. Found by running the fix. |

## Why this repair is legitimate after the numbers were seen

**It makes the result worse.** It converts a reported "met" into a split verdict
and puts a red control beside the ticket's best number. That direction is always
allowed. The reverse — seeding an in-region positive control to make the column
green — was available, is named in `PA-03-DF-03`'s own `suggested_fix`, and was
declined twice for the reason that it would be repairing an instrument after an
unflattering signal. See `PA-04-DF-01`.

The defect itself is filed as **`PA-04-DF-04`**, with the test that fails on
`5a58b2b`: `tests/test_control_role_is_executed.py` (16 pass at HEAD, 13 fail
there).

## The demonstrated kill is untouched

`PA-M12` KILLED on `corpus-port-swap:fake` is a demonstrated kill and stands on
its own — a red control cannot erase one (EVAL-SUPPRESS). What the red control
does is make the SURVIVED cells beside it a FLOOR rather than evidence.
