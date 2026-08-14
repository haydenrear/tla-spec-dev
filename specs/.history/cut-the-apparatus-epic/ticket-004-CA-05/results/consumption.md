# Consumption: the disposition requirement

**An epic may not close while a finding it filed is undisposed.**

That sentence is the whole requirement. Everything below says what "disposed"
means, what refuses, what the numbers are, and — first — what this is not.

## What this is not

**It is not a gate on anyone's code.** Seven epics of static checking caught
**zero** bugs, and this epic adds no gate. Nothing here runs in CI, blocks a
merge, blocks a promotion, or inspects a subject artifact. It reads one file in
this repository and reports on **this project's own epics**.

It is also not a target on the consumption rate. A threshold on a consumption
number before the mechanism exists is `MF-020` — an axis fitted to a known
answer — and the mechanism is the thing being built. The rate is **reported**,
never **targeted**.

## The rule

Scope: the findings in `specs/desired_program_model/deferred_findings.yaml`
whose id prefix belongs to the epic being closed.

| clause | requirement |
|---|---|
| **D1** | every finding carries a `disposition` from the vocabulary, and it is not `open` |
| **D2** | a **terminal** disposition carries a `disposition_note` saying what was done |
| **D3** | a **deferral** names a successor in `disposition_ticket` |

**Vocabulary.** Terminal: `repaired`, `settled`, `refuted`, `consumed`,
`wontfix`. Deferral: `carried`. Undisposed: `open`. Anything else fails D1 —
the vocabulary is closed on purpose, because an open vocabulary is how
`disposition` became a field that 130 rows satisfied by saying nothing.

**`open` is the correct value while the epic runs.** A finding is filed `open`
and stays `open` until someone decides where it goes. The requirement bites at
**close-out**, not at filing.

Run it:

```bash
python3 scripts/disposition.py --epic cut-the-apparatus   # exit 1, REFUSED
python3 scripts/disposition.py --ticket CA-05             # exit 0, DISPOSED
python3 scripts/disposition.py --all                      # every epic
```

## What it refuses, on the real record

`R1` says an instrument ships with a demonstrated failing input on a **real
subject**, not a fixture. This project has shipped three instruments later found
blind, one of them **this epic**, and its false-PASS modes were found by a
reviewer rather than by its author. So the demonstration is the whole sealed
ledger — 220 rows, eight epics, nothing constructed for the occasion:

| epic | merged | verdict | why |
|---|---|---|---|
| ports-as-adapters | 2026-08-05 | **REFUSED** | 2 of 28 — `PA-01-DF-03` and `PA-05-DF-02` are terminal with no note (D2) |
| falsifiable-instruments | 2026-08-06 | **DISPOSED** | 30 of 30, all three clauses |
| subtract-to-measure | 2026-08-07 | **DISPOSED** | 30 of 30, all three clauses |
| reading-discipline | 2026-08-10 | **REFUSED** | 46 of 46 `open` |
| portable-substrate | 2026-08-10 | **REFUSED** | 27 `open` + 1 terminal with no note |
| close-the-loop | 2026-08-11 | **REFUSED** | 17 of 17 `open` |
| score-drives-validation | 2026-08-12 | **REFUSED** | 30 of 31 `open` |
| **cut-the-apparatus** | in flight | **REFUSED** | **10 of 10 `open` — this epic, right now** |

**133 of 220 findings are undisposed.**

**The refusal that matters is the last row.** The requirement is shipped by an
epic it refuses. `CA-05` can dispose its own findings and does; it cannot
dispose `CA-00`'s, `CA-01`'s or `CA-02`'s, so `cut-the-apparatus` stays refused
and the refusal is a live obligation on `CA-08`, not a hypothetical.

### The check discriminates, and that had to be shown separately

An instrument that refuses everything is a constant, not a measurement — the
mirror of harvest class `D1`, where every `SURVIVED` cell was a floor. Three
facts distinguish this one, all on real inputs:

- **two real sealed epics pass** — `falsifiable-instruments` and
  `subtract-to-measure`, 60 rows between them;
- **the refusals differ in size and in clause** — `ports-as-adapters` fails on
  **2 of 28** rows under D2 alone, which is not the behaviour of a rule that
  says no to whatever it is handed;
- **one real ticket slice passes inside a refused epic** — `--ticket CA-05`
  exits 0 while `--epic cut-the-apparatus` exits 1, same instrument, same file.

## The finding this produced: the practice existed and lapsed

The premise behind this work was *"consumption is 1 of 38 because nothing
requires it."* The record does not support the second half.

**Three consecutive epics disposed their findings.** `ports-as-adapters` opened
five purpose-built carry-forward issues (**#144–#148, all still open today**) and
routed 14 rows into them. `falsifiable-instruments` routed 29 rows into
`subtract-to-measure`'s own tickets `SM-02`…`SM-05` (#166–#169) with a note on
each saying what the successor was expected to do. `subtract-to-measure` routed
28 rows onward the same way, 11 of them into `RD-02` (#189).

**Then it stopped dead.** Every epic that merged on or after 2026-08-10 filed
100% of its findings `open` and named no successor: reading-discipline 46,
portable-substrate 27, close-the-loop 17, score-drives-validation 30,
cut-the-apparatus 10 so far. **121 rows in five epics, zero deferrals.**

The boundary is exact and slightly cruel: **`reading-discipline` is the epic
that consumed its predecessor's deferrals (#189) and deferred none of its own.**

So the honest diagnosis is not *"nothing requires it."* It is **a working
practice lapsed and nobody noticed for four epics**, because nothing reported on
it. The requirement above is less an invention than a restoration with a
counter attached.

## The register, and the true denominator

`HARVEST-CL-03.md` is the register the consumption rate is measured against.
Its 38 classes were swept from **83 cards on 2026-08-11** and it was **untouched
for a whole epic afterwards**.

**`SV-01-DF-05` filed three new defect classes into the ledger and not into the
harvest.** They are appended to the register by `CA-05` as `G1`, `G2`, `G3`.

**Per `denominator_rule`, which half moved:**

> **The denominator rose from 38 to 41. The numerator did not move.**
> **1 of 38 (2.6%) → 1 of 41 (2.4%).** No consumption was lost and no
> regression occurred; the rate fell because the register was repaired. The
> classes named by a ledger row go **4 of 38 → 4 of 41** on the same arithmetic.

**41 is a floor, not a recount.** The sweep read 83 cards; the tree now holds
**95**. Twelve cards have been sealed since and **nobody has swept them**, so 41
is what one bounded, reproducible repair yields — not what a re-run of `CL-03`'s
method would yield. Quoting 41 as "the number of known classes" would be the
same error as quoting 38 was.

**And read the numerator honestly.** Four of 41 classes are named by a ledger
row, and **three of those four are this project catching itself committing the
class** — `E1` reproduced in the very file written to consume `A1`, `F3`
reproduced inside the instrument, `F6` reproduced by a round's own two judges.
**Only `A1` was consumed into program validation.** Detection catching itself is
not consumption, and a table that reports 4 without that sentence is
overstating by a factor of four.

## The two fields

**`channel`** — asked for six epics ago, so every findings-by-channel table in
`SELF-IMPROVEMENT.md` has been a hand classification of free text. The
vocabulary is the one the record already used:

`blind-judges`, `census`, `operator-doing-the-work`,
`operator-running-a-shipped-instrument`, `operator-running-own-instrument`,
`the-suite`, `independent-review`.

`operator-running-a-shipped-instrument` exists because `RM-05`'s census found
three findings landing in `operator-doing-the-work` **by the absence of that
option rather than by fit**. `independent-review` is added by `CA-05`: `CA-01`'s
blocking finding was refuted by a reviewer, and no existing token covers it.

**`cost`** — `CL-04` proposed it three epics ago and nothing recorded one since,
because nothing asked. Two subkeys, both free text, both required to mean
anything:

```yaml
cost:
  basis: "what was counted, and what it excludes"
  value: "the number, with its unit"
```

**Name the basis or the number is uncomparable.** `SV-05`'s 353,816 tokens at
0.57 findings per 100k is comparable to `SV-01`'s 0.98 **only** because both
named `subagent_tokens` as the basis. That is the first time two rounds in this
programme were comparable at all, and it is the entire argument for the field.

### Reconciling with `CA-02`, which populated both first

`CA-02` shipped `cost: {basis, value}` exactly as `CL-04` proposed it.
**Adopted verbatim, no change.**

`CA-02` also shipped `channel` as a **free-text sentence** — *"measured while
implementing the assigned slice — a grep the work order's own wording predicted
would find something."* **`CA-05` says that shape is wrong, and the reason is
the field's own purpose.** The complaint that produced this field was that the
channel signal *"exists only as free text inside `found_by`, which is why this
measurement is expensive every time."* A free-text `channel` relocates the free
text; it does not remove it, and the next census still classifies by hand.

**The reconciliation loses none of `CA-02`'s words.** `channel` takes one token
from the closed vocabulary; `CA-02`'s sentences move to `channel_note`, intact.
`CA-02`'s prose is good and worth keeping — it is simply not a category.

## What this requirement does not decide

It checks that a finding was **routed**, not that it was **fixed**. `carried`
with a live successor satisfies D3, and that is deliberate: an epic that cannot
fix something must still say where it went. Whether the successor ever consumed
it is a separate measurement, and this instrument does not make it.

**Named as its known blindness, in the shape `R1` asks for**: a row can satisfy
all three clauses by being `carried` to an issue that is then closed without
anyone reading it. `falsifiable-instruments` passes with 29 rows pointed at four
issues that closed the following day. **The check cannot tell that from a real
handoff, and does not claim to.**
