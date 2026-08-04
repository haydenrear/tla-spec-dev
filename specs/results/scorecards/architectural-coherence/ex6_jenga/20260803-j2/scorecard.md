# ex6_jenga — judge pass 2 (run 20260803-j2)

Scorecard version 1. Commit `ab0dfee`. Arm: none (single-artifact eval).
`ex6_jenga` is a deliberately incoherent control. **A low D3 is the correct
result**, and D1/D4 at the floor reflect a fixture with no detection instrument
and no behavior to preserve — not a defect. Never average this card with ex4's.

| dim | score | one line |
|---|---|---|
| D1 bug detection | 0 | no cases, adapters, tests or seeded faults exist |
| D2 complexity | 1 | measured and argued; god-state by construction, so anchor 2 is unreachable |
| D3 modularity | 1 | declared boundaries, code reaches everywhere including by reflection |
| D4 behavior preservation | 0 | no baseline, no suite, nothing changed, nothing checked |
| D5 honesty | 4 | the refusal reproduces, and the fixture argues against its own importance |
| **total** | **6**/20 | |

## What I reproduced

Running the reflexion check on the shipped fixture at scoring time:

```
architecture_scan = unmappable            exit 0
convergences 7   divergences 0   absences 0
divergence_detectable = false
[unfalsifiable_coherence]     every one of the 3 component pairs has a port
[partition_does_not_decompose] modularity_q -0.1856 (rule > 0),
                               crossing_action_fraction 0.8 (rule <= 0.5)
partition decomposes: NO      a clean result is NOT SUPPORTABLE on this basis
```

That matches the README's answer key on every row it states (verdict,
`divergence_detectable = false`, 7 convergences, 0 divergences, 0 absences, exit
0, all three pairs ported), and adds the second basis limit the README's key does
not list — an under-claim, recorded by `ex6-run2`, not an over-claim.

The complexity descriptor I also re-ran: bound **1,344**, Q = 0.000 over one
emergent component, dense rows `dirty` 5/5, `lastCommand` 5/5, `auditLog` 4/5,
`status` 4/5, and "no justification: table in the manifest — dead-weight analysis
skipped".

## D1 — 0, and D4 — 0

Both are floors reached by absence, not by failure. The fixture ships a model, a
partition, a map, three code modules and the recorded refusal. There are no
cases, no adapters, no providers, no tests, no seeded behavioral faults; both
runs are explicitly mechanical with no agent. Nothing was changed, so nothing was
preserved.

One drift worth recording under D4 and not scored: the committed
`evidence/reflexion.txt` predates the round-2 verdict rule — it carries the old
single-reason verdict and no partition-decomposition block — so the shipped
evidence file no longer matches what the tool prints, though the verdict is the
same.

## D2 — 1

The figures are measured, reported, and *argued against the design*: "Every
action below writes all four variables. That is the fixture" (`Jenga.tla:41`),
and the README states the expected model-side numbers in advance. Anchor 2 asks
for complexity proportional to behavior with no god-state; this is a god state on
purpose. So the highest anchor fully satisfied is 1 and there is no route higher
without changing what the fixture is.

## D3 — 1

Boundaries are declared — orders owns `status`, billing the audit trail, notify
the flags — and the code does not follow them. I read the three modules: every
one imports both others; `billing/audit.py:19-22` reaches into orders' class
dictionary by reflection; `notify/flags.py:15-23` polls both collaborators and
re-stamps its own flags, which is the "coordination by polling" the fixture set
out to exhibit. There is no port object anywhere in the code.

The important reading note: the reflexion check reports **0 divergences** here,
and that is not a modularity signal. Every component pair is ported because every
action writes every variable, which is exactly why the verdict is `unmappable`
and why the fixture's scoring rule marks "reports 0 divergences as a clean
result" a FAIL.

Not 0 only because a declaration exists and each class does own its own field, so
a boundary is discernible on paper before the code walks through it.

## D5 — 4

This is the dimension the fixture exists for, and it earns the top anchor:

- **Refusal in the program, not in prose** (anchor 3): I reproduced
  `unmappable` with two basis limits and the sentence "there is no flag, key,
  annotation, or environment variable that turns it into `coherent`", plus
  "UNMAPPABLE is not 'clean with caveats' and not 'nothing found'".
- **Limits named in the artifact** (anchor 2): the README's scoring rule marks
  three distinct ways of reporting this fixture as a FAIL, including "fixes" that
  declare an escaping partition.
- **Unflattering results** (anchor 4), and they are aimed inward:
  the README spends its first section arguing that this synthetic fixture is
  *worse* evidence than the repository's own model and labels itself the control;
  it files a finding against the very mechanism it demonstrates
  (`consumable_as_architecture` is true for any declared partition, so the
  criteria table does not stand between a project and a false clean, and
  `unfalsifiable_coherence` "catches the fully degenerate case only"); and
  `ex6-run1` scored the epic's own prediction **MISSED**, publishing the
  asymmetry that turned the headline refusal into a clean.

**Refuses to claim**: that 0 divergences is a clean result; that its 7
convergences show the code respects a boundary; that it is the primary evidence
in this epic; and that its refusal mechanism reaches beyond the degenerate case.
