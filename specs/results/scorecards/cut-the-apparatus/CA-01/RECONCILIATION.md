# CA-01 — reconciliation with the restored findings ledger

**Written AFTER `CA-01`'s spec ticket closed.** `RESULT.md`, `INVENTORY.md`,
`R1-demonstration.txt`, `COST.md` and `PROPOSED-DIFFS.md` are the evidence sealed
at close and are **not edited by this file** — the close-history snapshot at
`specs/.history/cut-the-apparatus-epic/ticket-000-CA-01/` is what they are sealed
against. This is an addendum, and it exists because one number in `RESULT.md` §5
was measured against a tree that has since been shown to be damaged.

---

## 1. What happened, and it is not CA-01's

The epic kickoff commit `87a526b` overwrote
`specs/desired_program_model/deferred_findings.yaml` — this repository's
cumulative **210-row findings ledger**, the *"210 findings"* issue #254 counts —
with `findings: []`. The epic owner filed it as `CA-00-DF-01` and restored the
ledger at `37ab155`.

**`feature/CA-01` was branched from the damaged commit `87a526b`.** So CA-01's
six findings were filed into an emptied file, and CA-01's suite figure was
measured against a damaged tree. Neither is CA-01's doing and neither is a defect
in this ticket's work.

## 2. The suite figure in `RESULT.md` §5 is SUPERSEDED

`RESULT.md` §5 reports **12 failed / 1554 passed** and attributes six reds to the
epic base and six to the epic owner's open suspects. **That attribution was
correct in shape and wrong in cause for five of the six suspects.**

The corrected figure is the epic owner's attributed baseline at
`specs/results/scorecards/cut-the-apparatus/GOAL-four-results-stand/baseline.md`:

> **7 reds at the epic branch after the restore** — 2 deliberate, 4
> inherited-and-undeclared, and `CA-00-DF-02`.

Restoring the ledger took the three affected files from **6 failed / 152 passed**
to **1 failed / 157 passed** on the same tree. `scorecard-audit` and
`scorecard-contested-drift` were downstream of the ledger damage.

**CA-01's own evidence pointed there and did not name the cause.** `RESULT.md` §5
records `blind-dispatch-check ok ok` green in the same run in which those two
reported `MISS`, and declined to attribute them to anything. That was the right
call with the information available and it was not the answer; the epic owner
found the cause.

**Superseded, not deleted.** `RESULT.md` §5 stays as written, because a figure
measured against a tree that was damaged at the time is evidence about the
measurement and about the damage, and this project's own rule is that a
discarded run is kept rather than removed.

## 3. What was reconciled

Merged `origin/epic/cut-the-apparatus` at `37ab155`. One conflict:
`deferred_findings.yaml`. Resolved to **218 findings** — the restored **212**
(210 + `CA-00-DF-01` + `CA-00-DF-02`), then CA-01's **six** appended last in ID
order.

Verified rather than asserted:

- the 212 restored rows are a **byte-exact prefix** of the merged file;
- parsed, `merged[:212]` is **semantically identical** to the restored ledger;
- **0 duplicate IDs** across 218;
- `CA-01-DF-01` and `CA-01-DF-06` remain `blocking: true`.

Nothing dropped, nothing reordered, no existing entry edited.

### One repair to CA-01's own rows, which the restore exposed

**`disposition` is present on 212 of 212 restored rows and was absent from all
six of CA-01's.** CA-01's findings were written against the emptied file and
never saw the schema. Added as `disposition: open` — true, and the value
`CA-00-DF-01` and `CA-00-DF-02` both carry.

This is a **second consequence of `CA-00-DF-01`**, quieter than the five reds and
worth recording separately: without the repair, CA-01's six would have been the
only rows in a 218-row ledger that a disposition census could not classify — in
the epic whose `GOAL-consumption-obligatory` is about that exact field. **An
emptied schema does not announce itself; it propagates into whatever is written
next.**

## 4. What was re-run, and why only this

The merge changed exactly two files on this branch: `deferred_findings.yaml` and
the goal's `baseline.md`. CA-01's own evidence files, instrument and
`instruments.toml` row were untouched. So the re-run was scoped to **everything
that reads the ledger**, not to another full suite:

```
uv run --with pytest --with pyyaml -m pytest \
  tests/test_score_tools.py tests/test_instrument_demonstrations.py \
  tests/test_goal_baseline_is_a_card.py tests/test_deferment_backlog_is_planning.py \
  tests/test_complexity_ledger.py tests/test_ticket_retirement.py -q
```

Result: `goal/CA-01-post-merge.txt`.

```
2 failed, 262 passed in 1077.54s (0:17:57)

FAILED tests/test_goal_baseline_is_a_card.py::test_a_real_epic_plans_judged_baseline_cannot_be_re_opened
FAILED tests/test_ticket_retirement.py::test_repository_canonical_delivered_plan_has_matching_close_receipts
```

**Both survivors are in the epic owner's 7-red attributed baseline**, and
neither is CA-01's:

| red | attribution |
|---|---|
| `test_a_real_epic_plans_judged_baseline_cannot_be_re_opened` | `CA-00-DF-02` — the `R1` instrument whose real subject is read from the live plan |
| `test_repository_canonical_delivered_plan_has_matching_close_receipts` | one of the 4 **inherited, undeclared** base reds |

**What cleared, and it is the load-bearing result of this reconciliation:** all
four `test_score_tools` reds and `test_instrument_demonstrations` now PASS —
**with CA-01's six findings appended to the ledger.** So the restore fixed them
*and* CA-01's rows conform to the restored schema rather than re-breaking the
audit that the emptied file had been failing. Had the `disposition` repair in §3
been skipped, this is the run that would have said so.

## 5. The instrument was re-verified against the drift the merge caused

`blind_dispatch.py check` derives its needles at run time, and **`git log` is one
of the sources**. The merge added three commit subjects to `git log -12`,
including CA-01's own two and the restore commit — **so the needle set changed
underneath the sealed demonstrations.**

```
python3 examples/validation/instruments/demonstrate.py --only blind-dispatch-check
blind-dispatch-check               ok     ok     skip   demonstrated-can-fail
```

Both halves still reproduce. **That is the drift occurring without breaking
yet**, and it is the same coupling class as `CA-00-DF-02`. The full analysis of
which half is exposed — the failing demonstration is anchored on literals in the
instrument's own source and cannot die; the passing demonstration asserts absence
and can be flipped to a false `REFUSED` by any future commit subject appearing in
the transcript — is in this PR's body under *"Does `blind_dispatch` have
`CA-00-DF-02`'s coupling?"*.

**Not repaired here.** The close is sealed; a semantic change to a shipped
demonstration wants an amendment ticket, not a rewrite of recorded evidence. The
fix is one line and is written down for whoever runs `CA-00-DF-02`'s proposed
census.
