# Owner findings measured but NOT YET LEDGERED

The ledger is append-only and SS-05 is appending to its tail right now. Filing
from two worktrees at once produces the tail conflict this epic has already hit
twice. So these are held here, WITH THEIR MEASUREMENTS, and appended as
`SS-00-DF-NN` rows after SS-05 merges.

Holding them in a file rather than in the operator's head is deliberate: the
recurring failure in this epic is a figure that lived only in working memory
between being measured and being written down.

---

## PENDING-1 — my own ruling's "two more instruments failing" was a prediction stated as a measurement

**Refuted by SS-05 at d6805f8, before it registered either instrument.**

I recorded `planning_rules.an_instrument_a_ticket_SHIPS_must_be_REGISTERED` and
wrote into SS-05's objective, and into my report to the user:

> "the population goes 56 -> 58 with two more instruments FAILING, which is
> denominator movement in the UNFLATTERING direction and is the point"

Measured by SS-05 before registering either:
- `vacuity_probe.py` **REFUSES ALL THREE STATES CORRECTLY** — three distinct
  messages, exit 2. Its finding is `disposition: repaired`.
- `stranded_loaders.py` answers UNDECIDED-and-exit-0 in **identical words** for
  unreadable and empty. Its finding is `carried`.

So ONE fails, not two. 56 -> 58 with **one** failing.

**Why this is the eleventh corrected figure and not a rounding error:** the claim
was rhetorically load-bearing. I was arguing that registering instruments moves
the denominator in the unflattering direction, and "both fail" made that argument
land harder than "one fails". I did not run either contract before asserting the
outcome of both. THE ERROR IS THE SAME SHAPE AS "four skips unskip when SS-01
repoints" AND AS THE 13-vs-12 NODES: a prediction written in the grammar of a
measurement. Three instances now, all mine, all in this epic.

Severity: major. Channel: `operator-doing-the-work`. Disposition: repaired in
the plan text once SS-05 merges; the ruling itself STANDS — registering was
still right, and SS-05's measurement is exactly what registering was for.

---

## PENDING-2 — a bogus exit code and a true exit code, same command, both printing 0

**Demonstrated on a real subject, in one session, minutes apart.**

Obligation 9b exists in SS-08 because I read an exit code through a pipe while
verifying SS-07's identical error. I then did it a THIRD time:

```
/usr/bin/python3 .../score_tools.py audit 2>&1 | tail -25; echo "AUDIT_EXIT=$?"
  -> ModuleNotFoundError: No module named 'tomllib'
  -> AUDIT_EXIT=0
```

The script CRASHED. `$?` reported `tail`'s status. Then, run correctly:

```
uv run --with pyyaml python .../score_tools.py audit > $OUT 2>&1; echo "AUDIT_EXIT=$?"
  -> AUDIT_EXIT=0
  -> "0 violation(s)"
```

**BOTH PRINTED `AUDIT_EXIT=0`.** One is a crashed interpreter, one is a clean
audit. THE TWO ARE INDISTINGUISHABLE FROM THE NUMBER ALONE — and the failing
form is the one that looks like a pass, so nothing prompts a second look.

This is the same class as the registered instances (`SS-00-DF-09`): a verdict
produced from input the reporter could not see. Here the absent input is the
subprocess's own status, discarded by the shell.

Note also `/usr/bin/python3` lacks `tomllib` (needs 3.11+) while the default
`python3` (3.14) lacks `pyyaml`. NEITHER BARE INTERPRETER CAN RUN THIS
PROJECT'S OWN INSTRUMENTS. `uv run --with pyyaml python` can.

Severity: major. Channel: `operator-running-a-shipped-instrument`.
Disposition: open — the repair is not a checker, it is that obligation 9b must
be read as "never pipe a command whose exit code you intend to read", which is
stronger than "read exit codes unpiped".

**GOOD NEWS FROM THE CORRECT RUN, recorded because it is a guard result:**
`score_tools.py audit` reports **0 violations at the epic tip**, with every
`[[movement]]` readable and all nine `[[contested]]` entries re-derived on a
third pass. That is `GOAL-four-results-still-stand`'s guard holding at
f45a245 + the owner's two commits, measured independently of SS-07.

---

## PENDING-3 — the rubric-drift prompt reaches 56 of 131 cards, and I reproduced the epic's own `rglob` defect finding it

### (a) THE POSITIVE RESULT FIRST, because it is the stronger one

SS-02 added 53 lines to `references/eval_scorecard.md` (commit `07b075c`) —
R1's third clause. Measured at the tip:

- **served digest UNCHANGED**: `sha256:2d7d4a0506d9b259`, card version 5
- **served bytes UNCHANGED**: 6281 at the tip, 6281 recorded at the baseline
- **rubric FILE sha CHANGED**: `b7fe75437bf68646` -> `674d497884fc124c`

`served_rubric` renders **from parsed structure only**, so doctrine prose added
outside the anchor ladder cannot reach a judge — and the digest correctly did
not move. `score_tools.check` already separates the three states by name:
`SERVED-DRIFT` ("the bar this judge read is not the bar in the tree"),
`PROSE-DRIFT` ("the rubric file changed in a part NO JUDGE IS SERVED — the
served digest is unchanged. **This is a prompt to go and look, never a
violation**"), and silence.

**THAT IS THE EPIC'S THESIS ALREADY IMPLEMENTED SOMEWHERE.** Three states kept
distinct, each with its own message, and the harmless one explicitly labelled
harmless instead of being either suppressed or escalated. It is the same shape
as SS-02's `set[str] | None` and SS-05's `invariants_absence_state()`. Worth
saying plainly: the fix shape this epic is repairing toward is not novel to the
epic — one instrument had it before we started.

### (b) THE COVERAGE LIMIT, which is the actual finding

`PROSE-DRIFT` is guarded by `elif block.get("file_sha256") and rubric.get(...)`.
An absent field is falsy, so the branch is skipped **silently**. Measured over
the live tree:

| | count |
|---|---|
| live cards (`.skill-manager` excluded) | 131 |
| record a rubric `file_sha256` | 56 |
| record NONE — drift prompt unreachable | **75** |
| carry the stale `b7fe…` | 8 |
| carry the current `674d…` | **0** |

So the prompt can fire for at most **56 of 131 (42.7%)**, and for the other 75
an absent field produces the same output as no drift. Zero cards carry the
current sha, so every live card predates SS-02's rubric change.

NOT YET ESTABLISHED, and I am not going to establish it as epic owner: whether
those 75 are cards sealed before the field existed (legitimate, and then the
honest fix is that `check` should say "cannot tell" rather than nothing), or
whether the field is being dropped by a live scaffold path (a real defect).
**The distinction decides whether this is a disclosure or a repair, and it is a
ticket's work, not an artifact's.**

### (c) TWO OWN-GOALS WHILE MEASURING IT, both this session

**I nearly filed a false finding.** I expected `audit` to emit `PROSE-DRIFT`,
saw zero, and started writing it up as a defect. The drift check is in
`check()`, not `audit()` — wrong command. Had I filed it, it would have been a
FALSE ALARM, the direction `SS-00-DF-09` names as the dangerous one because it
looks like diligence.

**And I reproduced the epic's own `rglob` defect.** My first sweep used
`pathlib.Path('.').rglob('scorecard.json')` and reported 262 cards, 112 with a
sha, 150 without, 16 stale. **Every one of those figures was exactly doubled**:
131 live cards and 131 vendored copies inside
`.skill-manager/skills/spec-double-compiler/`, which is a checkout of THIS
REPOSITORY at an older commit. The stale shas I first found were the vendored
copy's, not the record's.

That is the same mechanism found BY HAND in both instruments this epic shipped
(`SS-07-DF-08`, `SS-06-DF-05`) — an unbounded `rglob` that walks vendored
copies of the tree it is measuring. Three independent authors, same defect, same
session. **The population being swept is a contract, and none of the three of us
declared one.**

Severity: major (b), minor (c). Channel: `operator-running-own-instrument`.
Disposition: (a) no action, recorded as a positive result; (b) open, and the
live-vs-sealed question handed to a successor rather than guessed at; (c) open,
and the honest fix is that a sweep declares its root and excludes vendored
trees by contract, not by the author remembering.
