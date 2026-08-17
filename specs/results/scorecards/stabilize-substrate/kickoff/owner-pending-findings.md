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
