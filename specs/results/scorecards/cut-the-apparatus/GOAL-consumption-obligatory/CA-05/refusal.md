# CA-05 — the disposition requirement at the RECONCILED epic tip

Tree: `feature/CA-05` merged with `e379d6b` (CA-01..CA-04 all in). Ledger
**245 rows** = the tip's 239 + this ticket's 6.

---

## 1. THE REFUSAL — this epic, still refused, now on ALL THREE clauses

```
$ python3 scripts/disposition.py --epic cut-the-apparatus
REFUSED  epic cut-the-apparatus: 24 of 35 findings undisposed
           D1: 16
           D2: 2
           D3: 6
           CA-00-DF-01: D1 `disposition: open` -- filed and routed nowhere
           CA-00-DF-02: D1 `disposition: open` -- filed and routed nowhere
exit 1
```

**It does not pass. 16 rows from `CA-00`, `CA-01` and `CA-02` are still `open` —
that is what is outstanding and those are who owe it.**

---

## 2. TWO THINGS THAT HAD NOT HAPPENED BEFORE

**`CA-03` satisfied all three clauses VOLUNTARILY** — five rows, vocabulary token,
`channel_note`, complete disposition — adopted from the proposal alone **while
this PR was open and unmerged**. First ticket other than the author to meet it.

**`CA-04` tried and failed 8 rows** — and the disposition work WAS done, in other
keys: `CA-04-DF-01`'s refutation is in `summary`, `CA-04-DF-02` names its
successor in prose. **D2/D3 false refusals over the whole record: 10**, each
inspected individually. D1's 134 remain genuine.

**The rule is deliberately NOT changed.** Demoting D2/D3 after seeing this epic's
numbers is `MF-020`; `CA-08` must not measure a rule that moved after seeing its
data; and it would not rescue this epic anyway (16 D1 rows either way).

---

## 3. EVERY EPIC

```
REFUSED  close-the-loop: 17 of 17 findings undisposed
REFUSED  cut-the-apparatus: 24 of 35 findings undisposed
DISPOSED falsifiable-instruments: 30 findings, all three clauses hold
REFUSED  portable-substrate: 28 of 28 findings undisposed
REFUSED  ports-as-adapters: 2 of 28 findings undisposed
REFUSED  reading-discipline: 45 of 46 findings undisposed
REFUSED  score-drives-validation: 29 of 31 findings undisposed
DISPOSED subtract-to-measure: 30 findings, all three clauses hold
145 of 245 findings in specs/desired_program_model/deferred_findings.yaml are undisposed
```

---

## 4. CONSUMPTION OR ROUTING? — answered by hand, because the instrument cannot

`CA-03` and `CA-04` disposed findings from CLOSED epics. **The instrument cannot
tell a consumed row from a plausible sentence** — that is `CA-05-DF-03`. So
`CA-05` opened the artifacts:

| row | claim | verification |
|---|---|---|
| `SV-04-DF-05` | `cmd_scaffold` calls `register_round()`; R1 test shipped | **VERIFIED** — test exists and passes; `register_round` ×2 in `score_tools.py` |
| `RD-03-DF-08` | cut already made at card v4, `eval_scorecard.md:769` | **VERIFIED** — line 769 says exactly that |

**Genuine consumption in both.** And `SV-04-DF-05` carries harvest class `F3`
into program validation: **the numerator rises 1 -> 2 of 41, denominator held.**

**The general answer is the uncomfortable one:** that took two commands and a
judgement, done by a person. Any future *"N consumed"* from this field alone is a
count of CLAIMS. Read it as routing unless somebody opened the artifact.
