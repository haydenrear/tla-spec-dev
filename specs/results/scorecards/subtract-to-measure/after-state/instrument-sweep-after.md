# Instrument registry -- AFTER state, at the SM-03 tip

Derived by parsing `examples/validation/instruments/instruments.toml` directly,
by the same method `instrument-sweep-before.md` used, so the two are comparable.
The registry's own run of record is `instruments-after.json` /
`instruments-after.txt`: **exit 0, every declared demonstration reproduced.**

## The count, before against after

| figure | before (SM-01) | after (SM-03) | moved by |
|---|---|---|---|
| enumerated rows | 40 | **57** | +17 rows for 18 unregistered executables |
| classified `not-an-instrument` | 5 | **10** | +5, each a checked-and-rejected candidate |
| instruments | 35 | **47** | **+12** |
| with a demonstrated failing input | 26 | **33** | **+7** |
| without one | 9 | **14** | +5 |
| with a demonstrated blind spot | 12 | **15** | +3, all three admissions of what SM-03's own repairs cannot see |
| distinct declared paths | 38 | **56** | +18 |
| pytest slots asserting ONLY `expect_exit` | 12 failing (every one) | **0** | all 43 pytest slots now carry an executable count |
| rows where `failing` and `passing` are the same command | 2 | **0** | both repaired to cite refusing and accepting nodes separately |

**THE RATIO FELL: 26 of 35 (74.3%) -> 33 of 47 (70.2%).**

## `denominator_rule`, answered directly

**Nothing was deleted.** Not one row, not one demonstration, not one instrument.
So no part of this movement can be a denominator that shrank.

The numerator rose by 7 and the denominator rose by 12, and the two are
different populations, so they are reported apart:

| change | numerator | denominator | what it was |
|---|---|---|---|
| **REPAIRS** (rows already counted) | **+2** | 0 | `spec-yaml-tripwire` and `source-citation-tripwire`, whose `no-demonstration-constructible` was a fact about the runner |
| **REPAIRS** (rows already in the numerator) | 0 | 0 | the twelve `expect_exit = 0` slots and the two degenerate pairs -- repaired, already counted, invisible to this table and the largest part of the work |
| **NEW ROWS** | **+5** | **+12** | 18 executables the enumeration could not see |
| **DELETIONS** | **0** | **0** | none |

The twelve repaired slots move no figure in this table. That is worth saying
plainly, because it is the ticket's main product and the count cannot show it:
a row that was `ok` for the wrong reason and is now `ok` for the right one
reads identically. The evidence that it changed is `SM-GM-I1`, which survived
the registry at SM-01 and dies against it now.

## The 14 instruments that cannot be shown to fail
- `produced-code-instrument` (demonstrated-cannot-fail)
- `suite-verification` (demonstrated-cannot-fail)
- `port-swap-driver` (demonstrated-cannot-fail)
- `manifest-self-records-tripwire` (no-demonstration-constructible)
- `port-declaration-tripwire` (no-demonstration-constructible)
- `test-graph-nodes` (no-demonstration-constructible)
- `ticket-state-agreement` (no-instrument-exists)
- `generation-refusal` (no-demonstration-constructible)
- `docs-generation-refusal` (no-demonstration-constructible)
- `tlc-dump-case-generation` (no-demonstration-constructible)
- `scaffold-overwrite-refusal` (no-demonstration-constructible)
- `workflow-convergence` (no-demonstration-constructible)
- `arm-swap-driver` (no-demonstration-constructible)
- `onboarding-scaffold` (no-demonstration-constructible)

`scripts/code_complexity.py` -- the `produced-code-instrument` row -- is in that
list and **is not a removal target**. It is a thermometer: it reports, refuses
nothing, and `EXIT_OK = 0` is the only exit constant in the file. Refusing
nothing is its design, so there is no gap to seed and no claim to falsify. Named
here so its presence in the count is a decision on the record.

`suite-verification` and `port-swap-driver` are the other two
`demonstrated-cannot-fail` rows and they are **not** in that position: both
claim to catch something and neither can be shown to.

## The pytest slots, now counted

43 pytest slots, 43 carrying an executable count and
0 without one. `tests/test_instrument_demonstrations.py::test_every_pytest_slot_declares_an_executable_count`
makes it mandatory, so a slot added later cannot arrive uncounted.

## What SM-05 should read this against

`../before-state/instrument-sweep-before.md`, figure for figure. The one number
that is NOT comparable across the two is the denominator, and that is the
result: before it was hand-enumerated, after it is derived from the tree by
`demonstrate.py --check-enumeration`. `26 of 35` was a ratio over the set
somebody remembered.

