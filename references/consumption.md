# Consumption: the disposition requirement

**An epic may not close while a finding it filed is undisposed.**

That sentence is the whole requirement. Everything below says what "disposed"
means, what refuses, what the numbers are, and — first — what this is not.

## What this is not

**It is not a gate on anyone's code.** Nothing here runs in CI, blocks a merge,
blocks a promotion, or inspects a subject artifact. It reads one file in this
repository and reports on **this project's own epics**.

**The slogan, qualified — `CA-05` shipped it unqualified in three places and it
was false in its own PR.** The measured claim is *"seven epics of static checking
caught zero bugs **in a subject program**"*, and that stands. It is **not** the
claim that no check ever catches anything: `registry-enumeration-coverage`
caught this very ticket shipping an unregistered instrument, and a
set-completeness check over machine-derived metadata is a different class from a
static gate on program content.

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

**And one structural rule that precedes all three.** A row carrying the same key
twice is **refused before any clause is evaluated** — a clause verdict computed
over input a parser silently discarded is not a verdict. `CA-05-DF-06`: seven
rows did exactly this and the check certified them clean.

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
subject**, not a fixture. So the demonstration is the whole sealed ledger — 232
rows, eight epics, nothing constructed for the occasion:

| epic | merged | verdict | why |
|---|---|---|---|
| ports-as-adapters | 2026-08-05 | **REFUSED** | 2 of 28 under D2 — **and both are FALSE refusals, see below** |
| falsifiable-instruments | 2026-08-06 | **DISPOSED** | 30 of 30 |
| subtract-to-measure | 2026-08-07 | **DISPOSED** | 30 of 30 — **only after `CA-05-DF-06` repaired it; it was a FALSE pass** |
| reading-discipline | 2026-08-10 | **REFUSED** | 46 of 46 `open` |
| portable-substrate | 2026-08-10 | **REFUSED** | 27 `open` + 1 terminal with no note |
| close-the-loop | 2026-08-11 | **REFUSED** | 17 of 17 `open` |
| score-drives-validation | 2026-08-12 | **REFUSED** | 30 of 31 `open` |
| **cut-the-apparatus** | in flight | **REFUSED** | **16 of 22 `open` — this epic, right now** |

**139 of 232 findings are undisposed.** The 6 disposed rows in
`cut-the-apparatus` are `CA-05`'s own.

**The refusal that matters is the last row.** The requirement is shipped by an
epic it refuses. `CA-05` disposed its own findings; it cannot dispose `CA-00`'s,
`CA-01`'s or `CA-02`'s, so `cut-the-apparatus` stays refused and the refusal is a
live obligation on `CA-08`.

### How much this discriminates — the claim as first written is WITHDRAWN

`CA-05` originally argued that three facts proved the rule was not a constant:
two real epics passing, a narrow 2-of-28 refusal, and a passing ticket slice
inside a refused epic. **An independent reviewer of PR #265 took all three
apart, and was right.**

| the original leg | what it actually is |
|---|---|
| `subtract-to-measure` passes | **A FALSE PASS.** Seven rows carried duplicate `disposition_ticket` keys; the check read the discarded one. `CA-05-DF-06`. It passes legitimately only after the repair — and 10 of its 28 deferrals still **self-route** to its own evaluation ticket |
| `falsifiable-instruments` passes | The **closed-successor** case, which is the *normal* signature of an epic handing work to its successor — the weakest of the blind spots, not a clean acceptance |
| `ports-as-adapters` refuses narrowly, 2 of 28 | **BOTH ARE FALSE REFUSALS.** `PA-01-DF-03`'s record is in `suggested_fix` (*"Already applied."*) and `PA-05-DF-02`'s is in `status` (*"CENTRAL CLAIM REFUTED BY THE EPIC OWNER…"*). Each row records exactly what was done — in a key D2 does not read. **The tool discriminated on field naming, not on disposition** |
| `--ticket CA-05` passes | All three of its `carried` rows **self-route** to `#262` = `CA-08`, this epic's own evaluation ticket |

**So the honest statement of what this instrument separates is much narrower:**

> **D1 does real work and the other two clauses barely do any.** Four epics
> filed **122** findings and routed **none** of them; three epics routed **61**
> cross-epic. That gap is large, real, and no field-naming artifact explains it.
> **Everything beyond D1 — the narrow refusal, the per-clause variety, the
> passing slice — has been withdrawn or shown to be an artifact.**

D2 is currently a check that the record lives under one particular key. D3 is
satisfied by a successor inside the filing epic, by a bare string that resolves
to nothing, and with no note at all. **Two field rewrites turn the entire
backlog green**, and the reviewer did it in one script.

## The finding this produced: the practice existed and lapsed

The premise behind this work was *"consumption is 1 of 38 because nothing
requires it."* The record does not support the second half.

**Three consecutive epics disposed their findings.** `ports-as-adapters` opened
five purpose-built carry-forward issues (**#144–#148, all still open today**) and
routed 14 rows into them. `falsifiable-instruments` routed 29 rows into
`subtract-to-measure`'s tickets `SM-02`…`SM-05` (#166–#169), a note on each
saying what the successor was expected to do. `subtract-to-measure` routed 18
rows onward — 11 into `RD-02` (#189), 7 into `RD-01` (#188).

**61 rows routed cross-epic, not 83.** 83 is every `carried` row; **22 of those
self-route** to a ticket of the filing epic (12 `PA` rows to `PA-06`, 10 `SM`
rows to `SM-05`/#169) and routed nothing anywhere. The reviewer of PR #265
computed 54 from the rows `CA-05-DF-06` repaired; honouring `#188` moves
`subtract-to-measure` from 11 to 18.

**Then it stopped.** Every epic merging on or after 2026-08-10 filed its findings
`open` and named no successor: reading-discipline 46, portable-substrate 28,
close-the-loop 17, score-drives-validation 30. **122 rows in the four closed
epics, zero deferrals** — 143 including `cut-the-apparatus`'s 22 at the merged
tip. *(An earlier version of this page said 121, which was an arithmetic slip
restated without being re-derived — `CA-00-DF-05`'s own class.)*

**The boundary is 2026-08-07 → 2026-08-10.** *(An earlier version said "stopped
dead on 2026-08-08"; nothing happened on that date.)* `reading-discipline` is
the epic that consumed its predecessor's deferrals (#189) and deferred none of
its own.

### A companion observation, deliberately demoted

`SELF-IMPROVEMENT.md` also stops at `SM-05` (2026-08-07, `73ebeb6`), and the
three epics with a section there are the three that disposed.

**`CA-05` originally called this an "exact correlation across eight epics in
both directions". That is WITHDRAWN.** They are not two independent registers:
`d3f483d` writes **both files in one commit**, and they are two outputs of the
**same close-out ritual by the same actor**, so their co-lapse is *definitional*
rather than evidential. It is also **one** observation — two step functions
sharing one changepoint — not eight. It corroborates nothing, and is kept only
because it locates the ritual that lapsed.

**The core finding survives all of that**: a disposition practice ran for three
epics and stopped without one line of discussion in any record. **A practice that
lapses silently is a worse failure mode than one that never existed**, because
the first was working and nobody was watching.

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

### What is enforced, and what is only described — say it plainly

**`disposition`'s vocabulary is enforced. `channel`'s was not**, and both were
described here as "closed". That asymmetry is harvest class `C2` — a property
true of any declared value — and the reviewer of PR #265 named it.

Closed now, and **advisory on purpose**: `disposition.py --all` prints an
`ADVISORY (not a clause)` line for any `channel` outside the vocabulary. It
never changes a disposition verdict, because the channel of a finding has
nothing to do with whether it was routed.

**What still is not enforced, stated rather than implied:** nothing validates
this file's schema at all — not this script beyond duplicate keys and channel
tokens, not `close_tickets.py`, not `score_tools.py`, not the four test files
that read it. `CA-05-DF-06`'s residual class is live in every one of them.

### Reconciling with `CA-02` and `CA-00`, which populated the fields first

`CA-02` shipped `cost: {basis, value}` exactly as `CL-04` proposed it.
**Adopted verbatim, no change.**

`CA-02` also shipped `channel` as a **free-text sentence**, and `CA-00-DF-05`
carries `channel: "blind reviewer dispatched to refute"`. **`CA-05` says that
shape is wrong, and the reason is the field's own purpose.** The complaint that
produced this field was that the channel signal *"exists only as free text
inside `found_by`, which is why this measurement is expensive every time."* A
free-text `channel` relocates the free text; it does not remove it, and the next
census still classifies by hand.

**Reconciled by `CA-05`, losing not one word: six rows** — `CA-02`'s five and
the owner's `CA-00-DF-05` — now carry a vocabulary token in `channel` with the
original sentence intact in `channel_note`.

| row | token | prose preserved in `channel_note` |
|---|---|---|
| `CA-00-DF-05` | `independent-review` | *"blind reviewer dispatched to refute"* |
| `CA-02-DF-01` | `operator-doing-the-work` | *"measured while implementing the assigned slice…"* |
| `CA-02-DF-02` | `the-suite` | *"a red raised by this ticket's own targeted run…"* |
| `CA-02-DF-03` | `operator-doing-the-work` | *"noticed while checking, per the work order…"* |
| `CA-02-DF-04` | `operator-doing-the-work` | *"raised by the ticket against its own work…"* |
| `CA-02-DF-05` | `census` | *"traced deliberately, because the work order required…"* |

`independent-review` exists **because of `CA-00-DF-05`**: no prior token covered
a reviewer dispatched to refute, and two of the sharpest findings in this epic
came through that channel — including the one that broke this ticket's own
headline.

**Declined:** retro-classifying the 210 rows filed before the field existed.
Assigning a channel from somebody else's prose **is** the hand classification the
field exists to end, and in bulk it would manufacture a clean history nobody
measured.

## What this requirement does not decide

It checks that a finding was **routed**, not that it was **fixed**. `carried`
with a named successor satisfies D3, and that is deliberate: an epic that cannot
fix something must still say where it went. Whether the successor ever consumed
it is a separate measurement, and this instrument does not make it.

**Its known blindness, `CA-05-DF-03`, widened after review — four of these five
faces were found by a reviewer, not by the author:**

- **(a) Self-routing passes.** An epic may defer a finding to its own ticket and
  satisfy D3 with full marks. 22 real rows do it — **and so do all three of
  `CA-05`'s own deferrals**, which name `#262` = `CA-08`, this epic's own
  evaluation ticket. **This is the dead case**, and the first version of this
  page did not name it.
- **(b) The successor need not be an issue, or resolve to anything.** Any
  non-empty string passes; 14 real rows name a bare ticket id.
- **(c) A deferral needs no note at all.** D2 binds terminal dispositions only;
  17 real `carried` rows have none.
- **(d) Two field rewrites turn the whole backlog green**, and the reviewer of
  PR #265 did it in one script.
- **(e)** A row carried to an issue closed unread passes. **This was the only
  face `CA-05` declared on its own, and it is the weakest** — it is the normal
  signature of an epic handing work to its successor.

**Faces (a) and (c) are cheap to close and `CA-05` still declines**, because a
rule refusing self-routing would refuse this ticket's own three deferrals and
there is no external successor to point them at yet. That is an argument for the
next epic opening carry-forward issues the way `ports-as-adapters` did
(#144–#148) — **not** an argument for weakening the rule.

---

## The honest alternative, re-argued — and the case is weaker than `CA-05` first put it

The owner's framing was: *"Either a filed finding must receive a disposition
before an epic can close, or the honest description is a measurement programme
rather than a self-improvement loop. Both are respectable; the current state is
neither."*

`CA-05` retired the alternative on the grounds that a working requirement
refused a real close-out. **The reviewer's judgement is that this was the weakest
available evidence, and on the evidence that is correct:**

- **refusing is nearly free** — 6 of 8 epics refuse, and 4 of those refuse
  because every row says `open`;
- **both acceptances are the instrument's blind cases** — one was a false pass
  until repaired and still self-routes 10 rows; the other is the
  closed-successor case;
- **the discrimination leg was two false refusals**, on field naming.

**So the retirement is qualified, not withdrawn.** What is true:

> **A requirement now exists, it is documented, it runs, and it refuses the epic
> that shipped it.** That is a real change from a state where nothing asked.

**What is not yet true, and must not be claimed:**

> **Nothing has been consumed *because* of it.** The rate is still **1 in 41**.
> The mechanism that used to route findings was switched off for four epics
> while every consumption figure was published. **No finding has yet been
> carried into the program because this requirement forced it.**

**The honest description today is therefore still closer to "a measurement
programme with a newly installed close-out requirement" than to "a
self-improvement loop."** The alternative is **not refuted — it is deferred by
one epic.** The test is `CA-08` and its successors: if a finding is consumed
*because* the requirement refused a close-out, the loop language is earned. If
the next epic's findings are routed and nothing downstream reads them, then the
measurement-programme description was right all along and should be adopted
without embarrassment.

**`CA-05`'s own sentence, which is stronger than the case it first made for
retirement, and is kept here for that reason:** *the loop has closed once in 41,
and the mechanism was switched off for four epics while every consumption figure
was published.*
