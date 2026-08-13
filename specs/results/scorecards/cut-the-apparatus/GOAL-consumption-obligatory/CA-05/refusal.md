# CA-05 — the disposition requirement, run against the sealed record

**REVISED after independent review of PR #265, which broke the first version of
this document.** The refusal stands; the *discrimination* argument built on it
did not. Both are below.

Ledger: **232 rows** at the merged epic tip (`4302082`, CA-02 in). Instrument:
`scripts/disposition.py`. Rule: `references/consumption.md`.

---

## 0. THE STRUCTURAL REFUSAL — a real historical corruption

`CA-05-DF-06`. Seven rows (`SM-05-DF-01`..`DF-07`) carried `disposition_ticket`
TWICE — `#188` above the note, `#169` below it. YAML keeps the last. The check
read the discarded value and printed `DISPOSED subtract-to-measure`.

**Found by a reviewer. Not by this ticket, and not by the instrument.**

```
$ python3 scripts/disposition.py --ledger <the pre-repair file> --epic subtract-to-measure
STRUCTURAL SM-05-DF-01: `disposition_ticket` appears 2x at lines 5677, 5680 -- YAML keeps the LAST and discards the rest without a word
STRUCTURAL SM-05-DF-02: `disposition_ticket` appears 2x at lines 5761, 5764 -- YAML keeps the LAST and discards the rest without a word
STRUCTURAL SM-05-DF-03: `disposition_ticket` appears 2x at lines 5830, 5833 -- YAML keeps the LAST and discards the rest without a word
STRUCTURAL SM-05-DF-04: `disposition_ticket` appears 2x at lines 5899, 5902 -- YAML keeps the LAST and discards the rest without a word
STRUCTURAL SM-05-DF-05: `disposition_ticket` appears 2x at lines 5984, 5987 -- YAML keeps the LAST and discards the rest without a word
STRUCTURAL SM-05-DF-06: `disposition_ticket` appears 2x at lines 6065, 6068 -- YAML keeps the LAST and discards the rest without a word
STRUCTURAL SM-05-DF-07: `disposition_ticket` appears 2x at lines 6126, 6129 -- YAML keeps the LAST and discards the rest without a word
/tmp/prefix2.yaml: 7 duplicate key(s) -- REFUSING to report a clause verdict over input a parser has silently discarded (CA-05-DF-06)
```

**The failing input is the real file as it stood in the record for six days —
not a fixture.** `R1` discharged on a genuine corruption.

---

## 1. THE REFUSAL — this epic's own close-out

```
$ python3 scripts/disposition.py --epic cut-the-apparatus
REFUSED  epic cut-the-apparatus: 16 of 22 findings undisposed
           D1: 16
           CA-00-DF-01: D1 `disposition: open` -- filed and routed nowhere
           CA-00-DF-02: D1 `disposition: open` -- filed and routed nowhere
           CA-00-DF-03: D1 `disposition: open` -- filed and routed nowhere
           CA-00-DF-04: D1 `disposition: open` -- filed and routed nowhere
           CA-01-DF-01: D1 `disposition: open` -- filed and routed nowhere
           ... and 11 more (use -v)
exit 1
```

---

## 2. EVERY EPIC

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
REFUSED  cut-the-apparatus: 16 of 22 findings undisposed
           D1: 16
           CA-00-DF-01: D1 `disposition: open` -- filed and routed nowhere
           CA-00-DF-02: D1 `disposition: open` -- filed and routed nowhere
           CA-00-DF-03: D1 `disposition: open` -- filed and routed nowhere
           CA-00-DF-04: D1 `disposition: open` -- filed and routed nowhere
           CA-01-DF-01: D1 `disposition: open` -- filed and routed nowhere
           ... and 11 more (use -v)
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

139 of 232 findings in specs/desired_program_model/deferred_findings.yaml are undisposed
exit 1
```

---

## 3. WHAT THIS DOES AND DOES NOT SHOW — the first version was wrong

`CA-05` argued three things proved the rule was not a constant. A reviewer took
all three apart:

| original leg | what it actually is |
|---|---|
| `subtract-to-measure` passes | **FALSE PASS** until `CA-05-DF-06` was repaired; 10 of its 28 deferrals still self-route |
| `falsifiable-instruments` passes | the **closed-successor** case — the normal signature of an epic closing, the weakest blind spot |
| `ports-as-adapters` refuses 2 of 28 | **BOTH FALSE REFUSALS** — `PA-01-DF-03`'s record is in `suggested_fix`, `PA-05-DF-02`'s in `status`. Discrimination on **field naming** |
| `--ticket CA-05` passes | all three of its `carried` rows **self-route** to `#262` = `CA-08` |

**What survives, and it is only this:**

> **D1 does real work; D2 and D3 barely do any.** Four epics filed **122**
> findings and routed **none**; three routed **61** cross-epic. That gap is
> large, real, and no field-naming artifact explains it.

Two field rewrites turn the whole backlog green, and the reviewer did it in one
script. **The instrument separates "wrote a disposition field" from "did not",
and not much more.**
