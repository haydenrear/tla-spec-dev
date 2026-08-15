# CA-05 — the disposition requirement, run against the sealed record

Tree `a6bdf42bd5467310f8c5b7a8f5fcc1f9a8509d75` on `feature/CA-05`. Ledger: 225 rows (220 at the epic tip + this ticket's 5).
Instrument: `scripts/disposition.py`. Rule: `references/consumption.md`.

**`R1` asks for a demonstrated failing input on a REAL subject. Every input below is the real ledger; nothing here is a fixture.**

---

## 1. THE REFUSAL — this epic's own close-out

```
$ python3 scripts/disposition.py --epic cut-the-apparatus -v
REFUSED  epic cut-the-apparatus: 10 of 15 findings undisposed
           D1: 10
           CA-00-DF-01: D1 `disposition: open` -- filed and routed nowhere
           CA-00-DF-02: D1 `disposition: open` -- filed and routed nowhere
           CA-00-DF-03: D1 `disposition: open` -- filed and routed nowhere
           CA-00-DF-04: D1 `disposition: open` -- filed and routed nowhere
           CA-01-DF-01: D1 `disposition: open` -- filed and routed nowhere
           CA-01-DF-02: D1 `disposition: open` -- filed and routed nowhere
           CA-01-DF-03: D1 `disposition: open` -- filed and routed nowhere
           CA-01-DF-04: D1 `disposition: open` -- filed and routed nowhere
           CA-01-DF-05: D1 `disposition: open` -- filed and routed nowhere
           CA-01-DF-06: D1 `disposition: open` -- filed and routed nowhere
exit 1
```

The requirement is shipped by an epic it refuses. `CA-05` disposed its own 5 rows;
it cannot dispose `CA-00`'s or `CA-01`'s, so the refusal is a live obligation on `CA-08`.

---

## 2. THE ACCEPTANCE — a real slice that passes

```
$ python3 scripts/disposition.py --ticket CA-05
DISPOSED ticket CA-05: 5 findings, all three clauses hold
exit 0
```

Same instrument, same file, opposite verdict. **A rule that refuses everything is a
constant, not a measurement** — the mirror of harvest class `D1`, where every
`SURVIVED` cell was a floor. This is the check that it discriminates.

---

## 3. EVERY EPIC IN THE RECORD

```
$ python3 scripts/disposition.py --all
REFUSED  close-the-loop: 17 of 17 findings undisposed
           D1: 17
           CL-01-DF-01: D1 `disposition: open` -- filed and routed nowhere
           CL-01-DF-02: D1 `disposition: open` -- filed and routed nowhere
           CL-03-DF-01: D1 `disposition: open` -- filed and routed nowhere
           CL-03-DF-02: D1 `disposition: open` -- filed and routed nowhere
           CL-03-DF-03: D1 `disposition: open` -- filed and routed nowhere
           ... and 12 more (use -v)
REFUSED  cut-the-apparatus: 10 of 15 findings undisposed
           D1: 10
           CA-00-DF-01: D1 `disposition: open` -- filed and routed nowhere
           CA-00-DF-02: D1 `disposition: open` -- filed and routed nowhere
           CA-00-DF-03: D1 `disposition: open` -- filed and routed nowhere
           CA-00-DF-04: D1 `disposition: open` -- filed and routed nowhere
           CA-01-DF-01: D1 `disposition: open` -- filed and routed nowhere
           ... and 5 more (use -v)
DISPOSED falsifiable-instruments: 30 findings, all three clauses hold
REFUSED  portable-substrate: 28 of 28 findings undisposed
           D1: 27
           D2: 1
           RM-01-DF-01: D1 `disposition: open` -- filed and routed nowhere
           RM-01-DF-02: D1 `disposition: open` -- filed and routed nowhere
           RM-01-DF-03: D1 `disposition: open` -- filed and routed nowhere
           RM-01-DF-04: D1 `disposition: open` -- filed and routed nowhere
           RM-02-DF-01: D1 `disposition: open` -- filed and routed nowhere
           ... and 23 more (use -v)
REFUSED  ports-as-adapters: 2 of 28 findings undisposed
           D2: 2
           PA-01-DF-03: D2 `repaired` with no `disposition_note` -- no record of what was done
           PA-05-DF-02: D2 `refuted` with no `disposition_note` -- no record of what was done
REFUSED  reading-discipline: 46 of 46 findings undisposed
           D1: 46
           RD-01-DF-01: D1 `disposition: open` -- filed and routed nowhere
           RD-01-DF-02: D1 `disposition: open` -- filed and routed nowhere
           RD-01-DF-03: D1 `disposition: open` -- filed and routed nowhere
           RD-01-DF-04: D1 `disposition: open` -- filed and routed nowhere
           RD-01-DF-05: D1 `disposition: open` -- filed and routed nowhere
           ... and 41 more (use -v)
REFUSED  score-drives-validation: 30 of 31 findings undisposed
           D1: 30
           SV-02-DF-01: D1 `disposition: open` -- filed and routed nowhere
           SV-02-DF-02: D1 `disposition: open` -- filed and routed nowhere
           SV-02-DF-03: D1 `disposition: open` -- filed and routed nowhere
           SV-02-DF-04: D1 `disposition: open` -- filed and routed nowhere
           SV-06-DF-01: D1 `disposition: open` -- filed and routed nowhere
           ... and 25 more (use -v)
DISPOSED subtract-to-measure: 30 findings, all three clauses hold

133 of 225 findings in specs/desired_program_model/deferred_findings.yaml are undisposed
exit 1
```

---

## What this shows

| verdict | epics |
|---|---|
| **DISPOSED** | `falsifiable-instruments` (30/30), `subtract-to-measure` (30/30) |
| **REFUSED, narrowly** | `ports-as-adapters` — **2 of 28**, both D2 |
| **REFUSED, wholesale** | `reading-discipline` 46/46, `portable-substrate` 28/28, `close-the-loop` 17/17, `score-drives-validation` 30/31, `cut-the-apparatus` 10/15 |

**Two real sealed epics pass. The refusals differ in size and in clause.** A rule
that says no to whatever it is handed does not fail `ports-as-adapters` on two rows
out of twenty-eight under one clause.

**Declared blindness (`CA-05-DF-03`):** the check measures ROUTING, not CONSUMPTION.
`falsifiable-instruments` passes with 29 rows carried to four issues that closed
the following day, and the check cannot tell that from a real handoff.
