# SI-27 local signal — GOAL-findings-become-changes (contribution: direct)

Instrument: `skills/spec-double-2/scripts/improvement_ledger.py`, the harness the
plan names for this goal. Run under `uv run --python 3.12 --with pyyaml`, because
the ambient `python3` on this machine cannot import PyYAML and the script then
silently reads 2 of its 4 sources with no PARTIAL marker (SI-08-DF-01).

Both runs are over the SAME working tree; only
`specs/results/deferred_findings_final.yaml` differs (the pre-SI-27 copy was
restored into place for the BEFORE run and the reconciled copy put back after).

| | records across 4 files | `pending` bin | D4: skill-anchored, no change |
|---|---|---|---|
| before SI-27 | **129** | **53** | 57 |
| after SI-27  | **160** | **0**  | 63 |

+31 = the 28 rows absorbed from the per-ticket partition (which the instrument
could not see, SI-08-DF-11) plus the 3 SI-27 filed. The `pending` bin is empty
for the first time in this epic: every one of the 118 ledger rows carries a
disposition, and every one of the 80 that were open carries a
`disposition_note` naming what was measured and when.

**D4 moved the WRONG WAY, by +6, and that is reported rather than omitted.**
Absorbing the partition made six skill-anchored rows visible whose
`skill_change` is `proposed(...)` rather than `applied` or `declined`, so the
"anchored to a skill, no change to that skill" bin grew from 57 to 63. Nothing
got worse; six rows that were already true stopped being invisible. That is the
same direction as the headline — the instrument now counts a population it
could not see — and it is why a bin growing is not automatically bad news.

SI-27 applied no skill changes itself, and could not: its conflict keys are
three files and every fix it found reaches outside them. The bulk of the 63 are
still `skill_feedback.md` SF-rows where `skill_change=(absent)` means nobody was
asked, not `none` (`bug_attribution.md` §2a) — the largest unexamined part of
the record, named in the seeded REACH rows.

Classification against `expected_effect` ("a finding that nobody can answer is
not routing, and the record stops reading the same whether a place was clean or
never examined"): **moved as expected.**

* the query that failed — SI-16-DF-02 and SI-16-DF-03 against the ledger —
  now answers, because both rows are in it;
* 0 rows are `pending`, against 80 unsettled at the base;
* REACH (6), BLIND (9) and PRICE (3) are no longer empty:
  `specs/results/deferred/attribution/attribution.yaml`.
