# PA-06 — three arms, judged blind, deciding the three goals

**Ticket:** PA-06 · **issue:** #135 · **parent:** `930fa57` (PA-01…PA-05 merged)
**Example:** `ab_quota_ledger` · **card:** scorecard_version 1

**This is a MEASUREMENT, not a victory lap.** What follows is the run that
happened. Nothing here was re-run until a number passed, no target was moved,
and nothing was repaired. Every finding is FILED and none is FIXED.

---

## The headline, in four sentences

**Arm C — the length-matched control that asks for nothing architectural —
produced a flat single-module implementation whose per-mutant verdicts are
identical to arm A's on 88 of 88 cells, and whose author explicitly considered
and rejected a port.** So the predecessor's confound is settled in the
direction nobody has to apologise for: a 6.6×-longer prompt does not produce the
structure, and the D3 = 4 that arm B earned is attributable to what its prompt
*says*.

**And that is the only good news.** Generated cases still do not diverge between
the arms: **64 of 64 strictly comparable cells identical on every pairing**, on
eight instruments, at this tip. **The one cell that diverges in the whole
three-arm port-binding table is a fault the hexagonal arm LOST** — arm B's `M09`
survives `corpus-port-swap:fake` where arms A and C kill it. And the epic's
flagship kill, `PA-M12`, still sits under a **red positive control on every
port-scoped column of every subject**, which makes it a demonstrated kill beside
survivals that are a floor.

---

## Which driver produced which number — read this first

`PA-04-DF-02` and `PA-04-DF-04` record that this project has **two**
verdict-table drivers and that "two drivers is how a number gets quoted against
the wrong instrument". Every number below names its driver.

| table | driver | what it produces |
|---|---|---|
| the **8-instrument** per-mutant table | `examples/validation/ab/eval/run_controls.py` | `corpus-whole`, `corpus-neg`, `corpus-slice-res`, `corpus-slice-led`, `corpus-port`, `map-silent`, `map-checking`, `suite` |
| the **port-binding** table | `specs/results/scorecards/ports-as-adapters/GOAL-port-reach/measure/run_port_swap.py` | `corpus-action-bound`, `corpus-port-swap:real`, `corpus-port-swap:fake`, and on the ported reference `suite-real` / `suite-fake` |

**The second driver was changed by this ticket and the change is one ROW.** An
`arm_c` entry was added to its `SUBJECTS` table; no function, verdict rule or
accounting differs. That is checked rather than asserted: all four subjects were
re-run on it at this commit and diffed cell for cell against PA-04's sealed
output — **0 cells moved on `reference_ports`, 0 on `arm_a`, 0 on `arm_b`.**

Interpreter: `/opt/homebrew/bin/python3.14` (3.14.6). Plain `python3` on this
machine's `PATH` is 3.9.6 and has no `tomllib`; a run under it fails at import
rather than silently producing different numbers.

---

## `PA-05-DF-03`, SETTLED — the straddle was a prompt to go and look, and the
## answer is that nothing moved

PA-05 filed, at the weakest useful strength, that the 56-of-56 baseline had not
been re-derived since `5a58b2b` modified `scripts/run_generated_case_adapters.py`
— the adapter-execution path the generated columns run through — and that
**nobody had looked**. It asserted no defect. Settling it is a measurement and it
was PA-06's.

**It is settled: the eight-instrument table was re-derived at this tip and NOT
ONE CELL MOVED, on either arm.**

| subject | cells compared | moved |
|---|---|---|
| `arm_a` vs `specs/.history/ports-as-adapters-epic/ticket-002-PA-03/results/kill-table-arm-a.json` | 11 mutants × 8 instruments = 88 | **0** |
| `arm_b` vs `…/kill-table-arm-b.json` | 88 | **0** |

`ab-cells-identical-56` is therefore reaffirmed at this commit. **Never quote 64
against 56 without naming `PA-03-corpus-port`:** the count grew from 56 to 64
because PA-03 **added a COLUMN**, not because a verdict moved. R-H1 requires that
sentence and this is it.

---

## The three arms

| label in the cards | arm | prompt | tree |
|---|---|---|---|
| `U` | **A** | `examples/validation/ab/arm_a/PROMPT.md` — the ordinary ask | `specs/results/scorecards/hexagonal-prompting-rerun/arms/arm_a` (sealed predecessor artifact) |
| `T` | **B** | `examples/validation/ab/arm_b/PROMPT.md` — the hexagonal + minimize-complexity ask | `specs/results/scorecards/hexagonal-prompting-rerun/arms/arm_b` (sealed predecessor artifact) |
| `W` | **C** | `examples/validation/ab/arm_c/PROMPT.md` — the length-matched control | `specs/results/scorecards/ports-as-adapters/arms/arm_c` (**built at PA-06**) |

### The length match, re-measured at this tip

`python3 examples/validation/ab/check_catalogue.py --arms`:

```
arm_a  73 lines, 54 distinct     arm_b  194 lines, 143 distinct     arm_c  198 lines, 146 distinct
shared by all three: 36 lines (the controlled envelope)

               vs arm_a   vs arm_b   vs arm_c
  arm_a             --         16         17
  arm_b            105         --         89
  arm_c            109         92         --

  arm B unique vs arm A: 105 lines  (6.56x arm A's 16 -- the predecessor's 6.6x)
  arm C unique vs arm A: 109 lines  (1.038x arm B, +3.8%, inside the declared +/-10%)

  ARCHITECTURAL VOCABULARY in content not shared with arm A:
    arm B: 44 of 105 unique lines      arm C: 0 of 109 unique lines
```

**THAT TABLE IS MEASURED ON A FILE THAT IS NOT THE PROMPT ARM C RECEIVED, AND
THE REAL NUMBERS ARE WORSE FOR THIS TICKET'S PROCESS AND BETTER FOR ITS
CONCLUSION.** Found by the adversarial channel (`AD-F11`) and corrected here
rather than argued around. PA-06 dispatched `arm_c/PROMPT.md` with four
additions — a working-directory preamble, a run hint, three entries on the
do-not-open list, and a **Section 8** asking for a `REJECTED.md` — and did not
preserve what it sent. It is reconstructed at
`measure/arm_c_dispatched_prompt.md` and re-measured:

| | on disk | **as dispatched** |
|---|---|---|
| distinct non-blank lines | 146 | **160** |
| unique content vs arm A | 109 | **124** |
| ratio to arm B's 105 | 1.038 (**+3.8%**) | **1.181 (+18.1%)** |
| inside the declared ±10% tolerance | yes | **NO** |
| architectural vocabulary in that content | 0 of 109 | **4 of 124** |

**The ±10% tolerance claim is RETRACTED.** The as-dispatched prompt is 18.1%
longer than arm B, not 3.8%.

**Which way it cuts is fixed in advance by the sealed file and is honoured
here.** PREDICTIONS-PA: *"if arm C matches arm B it is a slightly stronger case
for length, and if arm C fails to match it is a slightly weaker case against it.
Nobody may pick the reading after seeing the result."* Arm C did **not** match, so
the residual weakens the case against length — and it is now a **larger**
residual, so it weakens it **more**. The conclusion survives comfortably (D3 = 1
against 4, on a prompt nearly a fifth longer again), but the correct sentence is
*"a prompt 18% longer than arm B's, asking for nothing architectural, produced
less structure than arm A's 16-line ask"*, not *"a length-matched prompt"*.

**And PA-06 leaked the epic's name into the arm whose entire job is to be
architecturally silent.** Two of the four vocabulary hits are paths this ticket
put there: the working directory
`specs/results/scorecards/**ports-as-adapters**/arms/arm_c/` and the forbidden
file `**PORTS-AS-ADAPTERS**-EPIC.md`. Arm C's author was told, in the first
sentence and in the forbidden list, what the epic is called. The other two hits
are incidental (`Designs you started and backed out of`, `import your module`).

That leak points **against** this round's conclusion, which is why it is
survivable: an author told the round is about ports and adapters is *more* likely
to build one, and arm C built none and wrote down why. But it is a defect in this
ticket's own dispatch and it is filed as `PA-06-DF-10`, not explained away.

### Two confounds this round ADDS, which the sealed file did not list

1. **Arms A and B were authored in the predecessor epic; arm C was authored
   today, by this ticket.** Same model family, different date, different
   dispatching agent, and arm C's prompt carried three additions arms A and B
   never had: `arm_c/` in its own do-not-open list, a `Section 8` asking for a
   `REJECTED.md`, and an explicit carve-out letting it read its own working
   directory under `specs/results/scorecards/`. Arms A and B were not
   re-dispatched, so this is a **cross-round comparison on the arm-C leg** and no
   amount of blinding removes it.
2. **`PA-01-DF-02`'s remedy turned out to be moot and is recorded as such.** It
   asks PA-06 to add `arm_c/`, `reference_ports/` and `PREDICTIONS-PA.md` to arms
   A's and B's do-not-open lists out of band at dispatch. **Neither arm was
   dispatched**, so there was nothing to add. What PA-06 did do is add them to
   the arm it did dispatch: `arm_c/PROMPT.md:179-188` already lists
   **two of the three** — `reference_ports/` at :182 and `PREDICTIONS-PA.md` at
   :186 — and **not `arm_c/` itself**; the dispatch added `arm_c/`,
   `PORTS-AS-ADAPTERS-EPIC.md`, `specs/desired_program_model/` and `*EPIC*.md`.
   (An earlier draft of this section said the file listed all three. It does not;
   corrected from `AD-F11`.) Arm C's `NOTES.md:212-216` reports opening only
   `FEATURE.md` and the shared suite.

---

## GOAL-cases-drive-ports — the arms still do not diverge

### Baseline → measured → target → verdict

| | |
|---|---|
| **baseline** | per-mutant verdicts **identical on 56 of 56** strictly comparable cells (EVAL-RERUN at `b3a0199`); superseded predecessor value 49 of 49 at `f431c62`; PA-03 re-derived it as **64 of 64** after adding the `corpus-port` COLUMN |
| **measured** | **64 of 64 identical, arm A vs arm B.** And, new this round: **64 of 64 arm B vs arm C**, and **88 of 88 arm A vs arm C** — every row, including the three the comparability rule excludes |
| **target** | *"The arms' per-mutant verdicts DIVERGE on at least one cell, and the divergence is attributable to a port rather than to prompt length."* |
| **verdict** | **MISSED on the eight generated instruments. MET, narrowly and in the losing direction, on the port-binding columns.** Reported as a split, not averaged. |

### The comparable set, named before the number

The strictly comparable set is the **8 mutants that are NOT `{M07, M08, M10}`** —
the rule is *"not the same diff"*
(`hexagonal-prompting-rerun/GOAL-catch-bugs/README.md:169-174`), because M07's
per-arm cells are not the same experiment and M08 and M10 are seeded by
**addition** rather than perturbation on arm B. **`M09` and `N01` ARE in the
set.** The owner initially derived this as "non-control" and PA-05 corrected it;
both rules give 56 by coincidence of size and separate on HP-06 (42 vs 49).

**Arm C changes one thing about that set, and it is worth stating.** Arm C, like
arm A, STORES `_available`, so `M07`'s sealed semantic has its faithful one-token
form there and **no substitution was needed**. Every arm-C row is a
`perturbation`. So `M07`, `M08` and `M10` are excluded only from pairings
*involving arm B*: between arm A and arm C all eleven rows are the same diff,
which is why that pairing is reported over **88** cells rather than 64.

### Eight instruments, three arms

```
arm A vs arm B  strictly comparable  64 of 64 identical
arm A vs arm C  strictly comparable  64 of 64 identical      ALL 88 rows  88 of 88 identical
arm B vs arm C  strictly comparable  64 of 64 identical
```

**THE DENOMINATOR IS TOO SMALL, AND THE ADVERSARIAL CHANNEL MEASURED IT
(`AD-F2`).** The exclusion of `M08` and `M10` rests on a SYNTACTIC rule —
`seeded_by = "addition"` on arm B — and the channel tested the property that rule
is a proxy for. Building an exhaustive observational fingerprint (every command
sequence of length 4 over a 13-action alphabet, 28,561 sequences, full projection
after every step, per arm, per mutant), it measured `M08` and `M10` to be **the
same experiment on all three arms**. Under the measured rule rather than the
syntactic one, the comparable set is **10 of 11 rows** and the result is

> **80 of 80 identical on every pairing.** The only row that is genuinely a
> different experiment is `M07` on arm B.

Both numbers are reported; **neither is used to soften the other.** 64 of 64 is
the number this round is measured against because it is the one the plan and the
ledger carry, and the epic's rule is that a denominator is not swapped after a
result is known. 80 of 80 is what the evidence supports and it makes the null
*wider*, not narrower.

### AND THE NULL WAS ENTAILED — the round's most important methodological finding

`AD-F1`. The same exhaustive fingerprint measured the three arms' **mutated**
trees to be observationally identical on **10 of 11 rows**, on all three arms.

> **Two trees with the same observational fingerprint cannot be told apart by any
> black-box instrument.** So the identity of the verdict tables is a *consequence
> of the re-anchoring succeeding*, not a measurement about detection. **This
> experiment can only produce a divergence where the re-anchoring FAILS** — which
> is exactly and only what happened: `M07` on arm B, the one row whose seeding is
> a declared substitute.

The obvious rival explanation — that the trees are just too similar — is
**measured false**: 78 against 151 against 202 code lines, a `dict[str, bool]`
against a `set` for `closed`, a plain tuple against a dataclass against a derived
computation for a held reservation. The trees differ substantially. What is held
constant is what the catalogue asks: *the same semantic, re-anchored*.

**This is not a defect in the run; it is a defect in what the goal can be
measured with.** `GOAL-cases-drive-ports` asks whether a codebase with real ports
is *validated differently* from one without. A catalogue built on "hold the
`semantic` equal across arms so a per-arm score compares two implementations
rather than two catalogues" — the right rule, adopted for the right reason at
EVAL-RERUN — guarantees the answer is no wherever it works. Filed as
`PA-06-DF-08`; it is the first thing the next round has to solve.

Arm A vs arm B differ on exactly two cells and **both are `M07`** —
`corpus-neg` (A `NOT_DECIDABLE` / B `KILLED`) and `corpus-slice-led`
(A `NOT_DECIDABLE` / B `SURVIVED`) — which is the sealed, known consequence of
arm B's M07 being a declared broader-reach substitute. Arm B vs arm C differ on
the same two cells for the same reason, with arm C on arm A's side of both.

### Per class, per arm, with executable counts beside them

Executability from each run's own control pass on **unmutated** code. **Identical
on all three arms**, because the corpus is a pure function of `(model, manifest,
flags)` and all three arms share one model and one manifest by design.

| instrument | cases | executed | % | accepting `Reserve` |
|---|---|---|---|---|
| `corpus-whole` | 43,128 | 3,734 | 8.66% | 294 |
| `corpus-neg` | 118 | 94 | 79.7% | 0 |
| `corpus-slice-res` | 2,438 | 320 | 13.1% | 100 |
| `corpus-slice-led` | 56 | 10 | 17.9% | 0 |
| `corpus-port` | 1,855 | 1,543 | 83.2% | 294 |
| `map-silent` / `map-checking` | 43,128 | 3,734 | 8.66% | 294 |
| `suite` | 28 tests | 28 | 100% | — |

**Never a single kill rate.** Per class, per arm:

| class | whole | neg | slice-res | slice-led | port | silent | checking | suite |
|---|---|---|---|---|---|---|---|---|
| **arm A** | | | | | | | | |
| guard_relaxation | 0 of 3 | **3 of 3** | 0 of 3 | 0 of 3 | **3 of 3** | 0 of 3 | 0 of 3 | 3 of 3 |
| durable_content | 1 of 2 | 0 of 2 | 0 of 2 | 0 of 2 | 1 of 2 | 1 of 2 | 2 of 2 | 2 of 2 |
| cross_aspect | 1 of 1 | 0 of 1 | 0 of 1 | 0 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| output_oracle | 1 of 1 | 0 of 1 | 1 of 1 | 0 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| ordering | 1 of 2 | 0 of 2 | 0 of 2 | 1 of 2 | 1 of 2 | 1 of 2 | 1 of 2 | 1 of 2 |
| wrong_value | 2 of 2 | 0 of 1 (1 nd) | 2 of 2 | 0 of 1 (1 nd) | 0 of 2 | 2 of 2 | 2 of 2 | 2 of 2 |
| **arm B** | | | | | | | | |
| guard_relaxation | 0 of 3 | **3 of 3** | 0 of 3 | 0 of 3 | **3 of 3** | 0 of 3 | 0 of 3 | 3 of 3 |
| durable_content | 1 of 2 | 0 of 2 | 0 of 2 | 0 of 2 | 1 of 2 | 1 of 2 | 2 of 2 | 2 of 2 |
| cross_aspect | 1 of 1 | 0 of 1 | 0 of 1 | 0 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| output_oracle | 1 of 1 | 0 of 1 | 1 of 1 | 0 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| ordering | 1 of 2 | 0 of 2 | 0 of 2 | 1 of 2 | 1 of 2 | 1 of 2 | 1 of 2 | 1 of 2 |
| wrong_value | 2 of 2 | **1 of 2** | 2 of 2 | 0 of 2 | 0 of 2 | 2 of 2 | 2 of 2 | 2 of 2 |
| **arm C** | | | | | | | | |
| guard_relaxation | 0 of 3 | **3 of 3** | 0 of 3 | 0 of 3 | **3 of 3** | 0 of 3 | 0 of 3 | 3 of 3 |
| durable_content | 1 of 2 | 0 of 2 | 0 of 2 | 0 of 2 | 1 of 2 | 1 of 2 | 2 of 2 | 2 of 2 |
| cross_aspect | 1 of 1 | 0 of 1 | 0 of 1 | 0 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| output_oracle | 1 of 1 | 0 of 1 | 1 of 1 | 0 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| ordering | 1 of 2 | 0 of 2 | 0 of 2 | 1 of 2 | 1 of 2 | 1 of 2 | 1 of 2 | 1 of 2 |
| wrong_value | 2 of 2 | 0 of 1 (1 nd) | 2 of 2 | 0 of 1 (1 nd) | 0 of 2 | 2 of 2 | 2 of 2 | 2 of 2 |

**Guard relaxation holds at 3 of 3 on the negative corpus, on all three arms.**
That is the class that measured 0 of 3, 0 of 3, 0 of 4 across three catalogues,
five instruments and two rounds before the negative corpus existed. It did not
regress and it composed into `corpus-port` for free on the third arm as it did on
the first two.

### The port-binding columns — one diverging cell in the entire three-arm table

`run_port_swap.py`, 8 comparable mutants × 3 columns = 24 cells per pairing.

| pairing | agree | diverge |
|---|---|---|
| arm A vs arm B | **23 of 24** | `M09` / `corpus-port-swap:fake` — A `KILLED`, B `SURVIVED` |
| arm B vs arm C | **23 of 24** | the same cell — C `KILLED`, B `SURVIVED` |
| **arm A vs arm C** | **24 of 24** | **none** |

`N01` behaves as a negative control must — `SURVIVED` on every generated column
of all three arms — so the rows are valid rather than vacuous.

### PA-04 handed me an objection and told me to decide it. Here is the decision.

PA-04 measured the `M09` divergence and recorded, against its own interest, that
a skeptic can call it a property of the catalogue's **re-anchoring** rather than
of the port, because `M09` is seeded in `quota_ledger/file_journal.py` on arm B
and in the one flat module on arms A and C. It said: *"A reader who rejects that
argument should score this divergence as unattributed."*

**Arm C is a check PA-04 did not have, and it comes down on PA-04's side.** Arm C
is length-matched to arm B, has a `M09` re-anchored by this ticket onto *its* one
flat module — a genuinely different `find`/`replace` from arm A's — and it lands
on **arm A's verdict, not arm B's**. If the divergence were an artifact of
re-anchoring per se, a third independent re-anchoring had an even chance of
producing a third answer. It did not. The variable that tracks the verdict is
**whether the arm has a second implementation of the port**, which is exactly
what `--wiring fake` swaps.

**But read which way the cell points, because it is not a win.** Arm A and arm C
have no fake, so — as the tool prints on every such run — their `:fake` column ran
their **REAL** adapter. The comparison is *arm A/C real against arm B fake*, and
on it **the hexagonal arm is the one that LOST the fault**: swapping in arm B's own
fake took `M09` off the executed path and made a real ordering fault invisible.

`GOAL-cases-drive-ports`'s target has two clauses and they resolve differently:

- *"verdicts diverge on at least one cell"* — **MET** on the port-binding columns
  (1 of 24), **MISSED** on the eight generated instruments (0 of 64).
- *"attributable to a port rather than to prompt length"* — **MET**, and arm C is
  what earns it. This is the first attribution in this project's history that a
  length control supports rather than merely fails to refute.

**Overall verdict: MISSED, on the metric the goal actually names.** The goal's
`metric` field is *"the count of comparable cells where the arms AGREE"*, and the
number that had to move is 64. It did not move. A divergence found only in a
column added after the baseline was set, in the direction of a fault becoming
invisible, is not the goal being met — it is the goal's thesis being reproduced
from the cost side.

---

## GOAL-port-reach — clause 1 MET, clause 2 NOT MET, and the split stays split

### Baseline → measured → target → verdict

| | |
|---|---|
| **baseline** | a fault in the treatment arm's in-memory adapter **SURVIVED EVERY INSTRUMENT** — five corpus instruments, the effect oracle and the hand-written suite. Measured at HP-06. **CITATION:** the plan cites `HP-06-DF-10`, which is a different finding; the correct reference is **`BA-B14`**, `specs/results/scorecards/hexagonal-prompting/FINDINGS.md` ~line 277. `PA-01-DF-01` filed this and the plan is unamended, so the corrected citation is recorded here beside the verdict, which is the treatment the epic doc prescribes for a stale sealed number. **That an epic's flagship baseline was never filed as a finding at all is itself a finding about the ledger, and this ticket was asked to report it. It is reported.** |
| **target** | *"The same adapter-internal fault dies on at least one generated instrument, **and no positive control is red**."* |
| **measured — clause 1** | `PA-M12` (a fault inside a **fake** adapter) is `SURVIVED` on `corpus-action-bound:{real,fake}` and `corpus-port-swap:real`, and **`KILLED` on `corpus-port-swap:fake`**. Reproduced at this tip, 0 cells moved from PA-04's sealed run. |
| **measured — clause 2** | **`M07` is RED on `corpus-action-bound`, `corpus-port-swap:real` AND `corpus-port-swap:fake` — on ALL THREE ARMS**, each column having executed **294 accepting `Reserve` cases**. `PA-M14` is RED on all four corpus columns of `reference_ports`, same witness count. `N01` is GREEN everywhere. **There is a working negative control in this round and no working positive one on any port-scoped column.** |
| **verdict** | **SPLIT: clause 1 MET, clause 2 NOT MET.** Not averaged into one word. `references/eval_scorecard.md` R-H3 requires each clause to be its own claim, because *"a ledger that stores one token per goal has to choose, and it will choose the flattering one"*. |

### The pair, on the ported reference, at this tip

| mutant | class | action-bound real | action-bound fake | port-swap real | port-swap fake | suite-real | suite-fake |
|---|---|---|---|---|---|---|---|
| `PA-M11` real adapter drops CLOSE | adapter_internal | **KILLED** | **KILLED** | **KILLED** | SURVIVED | **KILLED** | SURVIVED |
| `PA-M12` fake adapter drops CLOSE | adapter_internal | SURVIVED | SURVIVED | SURVIVED | **KILLED** | SURVIVED | **KILLED** |
| `PA-M13` fake drifts from real on write | adapter_internal | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | **KILLED** |
| `PA-M14` positive control (ports domain) | wrong_value | SURVIVED | SURVIVED | SURVIVED | SURVIVED | **KILLED** | **KILLED** |

**Read `PA-M11` and `PA-M12` as a difference, never as a total.** They are one
semantic fault seeded on the two sides of one port. Under the only wiring the
predecessor had, one dies and the other is untouchable — and `[pa_measured_swap_baseline]`
records that the remedy is **four lines** in `reference_ports/quota_ledger_fake.py`
that nobody wrote for a whole epic. Cheap-and-undone is a different finding from
expensive.

**Every kill number in every port-scoped column above is a FLOOR.** `PA-M12`'s
kill is a demonstrated kill and stands on its own; the `SURVIVED` cells beside it
sit under a red positive control and cannot be told apart from a broken
instrument. That is `PA-03-DF-03` / `PA-04-DF-01` realized for the third
consecutive ticket.

### THE PORT MACHINERY ADDED NO KILL ANYTHING ELSE DID NOT ALREADY HAVE

`AD-F7`, and it is the finding that bounds clause 1 hardest.

- **In each 8-instrument arm table, NO instrument has a unique kill at all** —
  `corpus-port` included. Every cell it decides, something else decides too.
- On `reference_ports`, `corpus-action-bound` — the declared *pre-PA-04 world* —
  kills exactly the same set as `corpus-port-swap` on every arm.
- **`suite-fake` strictly dominates `corpus-port-swap:fake`.** It kills
  everything that column kills **plus `PA-M13`**, which the port corpus misses
  because `_project_ledger` takes `parts[0:3]` and a COMMIT line truncated to
  three fields projects identically.

So the measured "a fault behind a port stops hiding" is produced by the
**four-line `quota_ledger_fake.py` composition point** plus the **pre-existing
hand-written suite**. The `[ports.*]` binding machinery this epic built adds a
**strictly weaker** instrument on this fixture.

Clause 1's target says *"dies on at least one GENERATED instrument"*, and it
does — `PA-M12` on `corpus-port-swap:fake`. The verdict stands as `met`. What
does not stand is any reading of it as the generated machinery reaching where
hand-written tests could not: on this fixture the hand-written suite got there
first, with the same four lines of wiring.

### Two more things the port columns are not

- **`AD-F3`: the port corpus does not compare the variable either positive
  control lands on.** All 1,855 port cases compare an `after` of exactly
  `{closed, committed, ledger}` — measured, not inferred. `M07`'s only observable
  is `available`; `PA-M14`'s is the recorded amount `amt`. **Neither is in the
  projection**, so the `294 accepting Reserve executed` witness carried in every
  `control_red` entry is true and is *not the operative fact*. `PA-03-DF-02` said
  a projected corpus's real limitation is inexpressible in the driver's witness
  vocabulary; this is what that costs.
- **`AD-F8`: `corpus-port` in the 8-instrument table is not port-bound.** Its
  mapping is `case_adapters.map-none.toml` — it is the port *corpus* through the
  ordinary action oracle. **No column in the 8-instrument table is port-bound.**
  The name reads otherwise and this document has been careful not to.
- **`AD-F6`: on arms A and C the `:fake` column is a byte-identical rerun of
  `:real`.** Their mappings declare no `fake =`, so `apply_wiring` leaves them on
  the real adapter and the whole `evidence` block matches for all 11 rows on both
  arms. The tool says so on every run, which is why this is a fact about the arms
  rather than a defect — but it means "24 cells per pairing" is really 16
  distinct cells plus 8 duplicates on two of the three arms.
- **`AD-F6`, second half: `run_port_swap.py` reports an executability witness for
  a cell in which the mutant executed zero times.** The `M09` divergence was
  separated by a mirror experiment — the same semantic moved to arm B's
  `memory_journal.py` gives the exact mirror, 854 failures under `fake` and 0
  under `real`, identical count — so the cell tracks *which side of the port the
  mutant sits on relative to the wiring*, exactly as claimed. But the driver
  keeps no mutated-line-level accounting, so it attaches `294 accepting Reserve`
  to a survival that means "the mutated file was never executed".

### The repaired positive control — `P07`'s instrument, run on all three arms

`PA-M14`'s `re_anchoring_rule` says: re-anchor **by the property, not by the
bytes**, then run the probe; if it does not report HOLDS the arm has no valid
positive control and PA-06 says so and leaves the cell RED. Three re-anchorings
were written (`measure/pa_m14_arm_{a,b,c}.toml`), each against a different line
because the three trees record a granted reservation differently.

```
python3 examples/validation/ab/check_catalogue.py --controls --tree-root \
    --root <arm tree> --catalogue measure/pa_m14_arm_<x>.toml --impl quota_ledger
```

| tree | `M07` semantic | `PA-M14` accept-path semantic |
|---|---|---|
| arm A | HOLDS | **HOLDS** |
| arm B | **BROKEN** | **HOLDS** |
| arm C | HOLDS *(newly measured; was UNMEASURED)* | **HOLDS** |

**The repair works.** `M07`'s sealed semantic is BROKEN on arm B — it is
observable at construction, after a refusal and after an accepted `close_tenant`,
so it stays green through exactly the regression it exists to catch. `PA-M14`'s
semantic is representation-independent and survives all three re-anchorings,
including onto the arm that derives `available()` and the arm nobody had built
when the prediction was sealed.

**What that does NOT do, stated plainly.** It does not make clause 2 green. A
control whose *property* holds is not a control that *fires*: `PA-M14` still
SURVIVES all four port-scoped corpus columns of `reference_ports`.

### AND THE PROPERTY THAT "HOLDS" IS VACUOUS ON THREE OF THE FOUR TREES

**This is the round's worst finding about itself and it is the epic's own
declared worst-possible own goal.** Two adversarial results, both measured.

**`AD-F4` — `PA-M14`'s declared `observable` is FALSE on three of the four trees
it is declared on.** The declaration, copied verbatim from `seeded_faults.toml`
into all three of PA-06's re-anchorings: *"available(t) is one too low …
immediately after an ACCEPTED reserve."* Measured with a direct probe, after one
accepted `reserve("t1", 2)`, clean tree against `PA-M14` applied:

| tree | `available` after the accepted reserve |
|---|---|
| `reference_ports` (both wirings) | 1 → **1**, and nothing else in the projection moves |
| arm A | 1 → **1** |
| arm C | 1 → **1** |
| **arm B** | 1 → **0** |

The three trees that **store** `available` deduct the *parameter* and then record
the inflated amount on the reservation; only arm B, which **derives**
`available()` from the recorded amounts, shows it in one step. **Every generated
corpus case is single-action.** So `PA-M14` **cannot be killed by any corpus** on
`reference_ports`, arm A or arm C — regardless of projection, regardless of
reach. Its RED on four of six reference columns is a property of the control, not
of the instrument.

And note what that means about the repair's own diagnosis: `PA-03-DF-03` says
*"`M07` inflates a held total and `PA-M14` inflates it on the accept path. Both
land on `available`."* Measured, **that is false for `PA-M14` — it lands on
`amt`.** The control was re-anchored by a property whose statement of its own
observable does not hold.

**`AD-F5` — the probe that certified it cannot fail.** The channel wrote a
control whose mutation is `self._next_id: int = 1` → *the identical line plus a
comment*, declared it `control_role = "positive"`, and ran the shipped probe:

```
NOOP-control   arm_c   HOLDS
                       invisible until an accepted reserve executes
```

**A no-op passes.** The probe tests only *"invisible BEFORE an accepted reserve"*
and nothing tests *"visible WITH one"*. So `P07`'s `HOLDS ×3` is **PASS on its
stated instrument and worth nothing as evidence that the control works** — and,
combined with `AD-F4`, it is evidence of the opposite on two of the three arms.

**`PREDICTIONS-PA.md` P07 wrote the warning this round then walked into:**

> *"A control that cannot fail is worse than one that is honestly broken, and
> re-creating that defect here — in the round whose predecessor's worst finding
> was exactly it — would be this epic's worst possible own goal."*

`PA-01-DF-05`'s whole subject is that *nothing ever checked a positive control
against the property that makes it one*. PA-01 built the check. **The check it
built is one-sided, and the control it certified is unobservable in one step on
three of four trees.** Filed as `PA-06-DF-07`, severity blocking. Nothing is
repaired: this is a measurement, and the instrument is the thing under
measurement.

**What survives it.** Clause 2 was already `missed` and this makes the reason
worse rather than different. `M07`'s red — twelve control/instrument pairs across
three arms — is untouched, because `M07` *is* observable in one step on the trees
that store `available` and `AD-F3` gives the real reason it survives the port
columns. `N01` remains a working negative control on every column of every arm.
And `PA-M12`'s kill is still a demonstrated kill: `EVAL-SUPPRESS` settled that a
declaration cannot erase one, and a broken control cannot either.

### `PA-04-DF-01` / `PA-03-DF-03` — DECLINED, with reasons

Both name PA-06 as the ticket that seeds a blatant fault **inside** the declared
port's region so a port-scoped instrument can have a green positive control at
last, and `PA-04-DF-01` even supplies the fault ("a COMMIT line written with the
wrong tenant"). **PA-06 declines, and the decline is the same argument PA-04
made, which applies to PA-06 *a fortiori*.**

PA-01 `schedule_revision 2` draws the line exactly: repairing an instrument
**before** any measurement is legitimate; repairing it **after** an unflattering
signal is the forbidden act. PA-04 had already seen its own numbers when it was
offered this, and declined. PA-06 is **the measurement itself** — the epic's
standing rule is that a fix taken during a measurement destroys the measurement,
and there is no ordering available in which this ticket seeds the control before
seeing a result, because deciding the goals *is* seeing the result.

So it stays red, the port columns stay a floor, and the work is carried forward
with the protocol spelled out: **seal the prediction, seed the control, and run
it — in that order, in a ticket that is not the one deciding the goal.**

---

## GOAL-complexity-measurable — MET

### Baseline → measured → target → verdict

| | |
|---|---|
| **baseline** | **NO SUCH INSTRUMENT EXISTS.** The shipped descriptor reads TLA+; all arms produce Python. That is why D2 measured 2 for both arms from all four judges in the predecessor. |
| **measured** | `scripts/code_complexity.py` runs over produced Python and reports figures that **differ between all three arms** on `modules`, `code_lines`, `callables`, `classes`, `public_surface`, `declared_interfaces`, `declared_interface_methods`, `internal_import_edges`, `effectful_calls`, `branch_points_in_effectful_modules` and `instance_state_in_effectful_modules`. |
| **target** | *"The instrument runs over produced code and reports figures that differ between arms. NO TARGET ON THE NUMBER ITSELF."* |
| **verdict** | **MET.** The instrument exists, runs, exits 0 on every input, refuses nothing, gates nothing, and tells three implementations of one spec apart. |

**And the goal being met is not a claim that the arms got simpler.** See the
mechanical block below and `PA-02-DF-01`, which bites this round's D2 directly.

---

## MECHANICAL BLOCK — recorded, NEVER scored

`python3 scripts/code_complexity.py <tree>`, `role=code` (implementation modules
only; test modules excluded). Full output at
`GOAL-complexity-measurable/results/code_complexity.{txt,json}`.

| figure | arm A | arm B | arm C | `reference` | `reference_ports` |
|---|---|---|---|---|---|
| `modules` | 1 | **4** | 1 | 1 | 5 |
| `code_lines` | 151 | **202** | **78** | 122 | 255 |
| `callables` | 17 | 23 | 11 | 13 | 22 |
| `classes` | 4 | 6 | 2 | 3 | 8 |
| `public_surface` | 20 | **25** | **11** | 15 | 26 |
| `instance_state` | 8 | 8 | 7 | 7 | 9 |
| `module_state` | 0 | 0 | 0 | 0 | 0 |
| `branch_points` | 10 | 11 | 10 | 10 | 11 |
| `max_branch_points_in_callable` | 4 | 4 | 4 | 4 | 4 |
| `max_depth` | 1 | 1 | 1 | 1 | 1 |
| `declared_interfaces` | 0 | **1** | 0 | 0 | 1 |
| `declared_interface_methods` | 0 | **2** | 0 | 0 | 2 |
| `internal_import_edges` | 0 | **3** | 0 | 0 | 4 |
| `effectful_calls` | 5 | 3 | 3 | 3 | 3 |
| `modules_with_effectful_calls` | 1 | 1 | 1 | 1 | 1 |
| `branch_points_in_effectful_modules` | 10 | **1** | 10 | 10 | 1 |
| `instance_state_in_effectful_modules` | 8 | **1** | 7 | 7 | 1 |

Other mechanical figures:

| | |
|---|---|
| shared behavioural suite | **28 passed** on every arm, unmutated |
| generated port corpus `cases.py` sha1 | `08265aff0d81f27f4dfc9694d2a69c3c5b6e695c` — **byte-identical to PA-03's and PA-04's sealed value** |
| corpus sizes | whole 43,128 · neg 118 · slice-res 2,438 · slice-led 56 · port 1,855 |
| executed / skipped, port corpus | 1,543 ran (1,462 accepting) / 312 skipped / 0 failed on unmutated code, **identical on all three arms** |
| determinism, 8-instrument table | arm C run twice end to end: see `DETERMINISM.md` |
| determinism, port-binding table | all four subjects reproduce PA-04's sealed output cell for cell, 0 moved |
| catalogue integrity, arm C | every `find` occurs **exactly once**, apply/revert **byte-identical**, mutated file **parses**, for all 10 rows — and the harness still exits 1, for a reason that is `PA-06-DF-01` |

### Does the mechanical block AGREE or DISAGREE with D2?

**It disagrees, and the disagreement is a finding rather than a rounding error.**

`PA-02-DF-01` filed it before this round ran and this round confirms it on a
third arm: **the produced-code figures support NO simplification claim for any
arm.** Like for like on `role=code`, the arm with the port is **larger** on
`code_lines` (202 vs 151 vs 78), `public_surface` (25 vs 20 vs 11), `modules`
(4 vs 1 vs 1) and `classes` (6 vs 4 vs 2), and **flat** on branching (11/10/10),
worst callable (4/4/4) and depth (1/1/1). The arm that is smallest on every size
figure is **arm C — the control that was asked for evidence and got no
architectural guidance at all.**

The one figure that separates the *designs* rather than their size is where the
effects sit: `branch_points_in_effectful_modules` 1 on arm B against 10 on arms
A and C, and `instance_state_in_effectful_modules` 1 against 8 and 7. That is a
real structural difference and it is not a simplification.

D2's anchors 3 and 4 both require *"a simplification was made and its effect
measured"*. On this evidence no arm can reach them, and **a judge who scores arm
B up for being ported is scoring the prompt rather than the artifact — while a
judge who scores it down for being larger is scoring size, which D2 does not ask
either.** Both judges' D2 scores are recorded below beside these figures so a
reader can see whether that happened.

---

## The three arms' scorecards

Two judges, blind to arm and to each other, `claude-opus-5[1m]`, dispatched
independently. Six cards, all `check`-clean. Full rationales, citations,
`refuses_to_claim` and each judge's REJECTED and DISCLOSURES sections are
transcribed verbatim in `ab_quota_ledger/20260805-{T,U,W}-p{1,2}/`; the blinding
account is `UNBLINDING.md`.

| artifact | arm | D1 bug detection | D2 complexity | D3 modularity | D4 behaviour | D5 honesty | total |
|---|---|---|---|---|---|---|---|
| `T` | **B** hexagonal | 4 / 3 | 2 / 2 | **4 / 4** | 4 / 4 | 4 / 4 | 18 / 17 |
| `U` | **A** ordinary | 4 / 3 | 2 / 2 | 2 / 2 | 4 / 4 | 4 / 4 | 16 / 15 |
| `W` | **C** length-matched control | 3 / 3 | 2 / 2 | **1 / 1** | 3 / 3 | 4 / 4 | 13 / 13 |

**Maximum spread across all thirty independent scores is 1. ZERO contested
dimensions; no third pass was run.** Twelve of fifteen dimension pairs agreed
exactly. That is the third round running with no contested dimension, and the
sealed confound about it stands: two judges of the same model family reading the
same anchors are not independent the way two people would be.

### ARM C AGAINST ARM B — the attribution question, answered

**The answer is that the architectural content was NOT decoration.**

| | arm B (`T`) | arm C (`W`) | arm A (`U`) |
|---|---|---|---|
| unique content vs arm A | 105 lines (6.56×) | **109 lines (6.81×)** | — |
| architectural terms in that content | 44 of 105 | **0 of 109** | — |
| **D3, both judges** | **4 / 4** | **1 / 1** | 2 / 2 |
| `declared_interfaces` | 1 | 0 | 0 |
| `internal_import_edges` | 3 | 0 | 0 |
| a working fake for the driven port | **yes** | no | no |

**Arm C is 3.8% LONGER than arm B in unique content and scored 3 points lower on
D3 — below arm A, whose prompt is a sixth of the length.** Prompt length does not
produce structure on this feature. `N01` predicted exactly this and PASSES.

**And arm C's author says so in its own words, which is the part no metric could
have supplied.** Asked what it REJECTED, it named the port and gave its reason
(`arms/arm_c/REJECTED.md:77-88`):

> *"Structural: splitting reservations and the ledger writer into separate
> objects/modules behind an interface … Considered it, in particular a small
> `LedgerWriter` class the `QuotaLedger` would hold a reference to, so the
> append-only file write is one clearly-named seam. Rejected it for this
> program: there is exactly one place that writes to the ledger, it is called
> from exactly two commands, and introducing a second class to wrap one method
> would be a layer with no second implementation behind it and no test that
> needs to swap one in."*

An agent given 109 lines of demanding, non-architectural instruction **considered
the exact seam arm B built, and declined it on merit.** The variable is what the
prompt says.

**What this does NOT settle**, per the sealed confound 1, which is honoured
rather than argued away: arm C controls for LENGTH, not for subject. Its ask is
about evidence and documentation. This round settles the specific confound the
predecessor recorded — *"6.6× longer"* — and no more. And because arm C came out
*longer* than arm B, the residual makes the case against length slightly weaker,
which is the reading the sealed file fixed in advance.

### The two dimensions that moved, on artifacts that did not

**This is the round's most uncomfortable number and it is on the ledger's own
"evidence we are fooling ourselves" list: *a score moving without an artifact
moving*.** Arms A and B are byte-identical to the trees EVAL-RERUN judged.

| | EVAL-RERUN (sealed) | PA-06 | change |
|---|---|---|---|
| arm A `D4` | 2 / 2 | **4 / 4** | **+2 / +2** |
| arm A `D5` | 3 / 2 | **4 / 4** | **+1 / +2** |
| arm A `D1` | 3 / 3 | 4 / 3 | +1 / 0 |
| arm B `D4` | 3 / 2 | **4 / 4** | **+1 / +2** |
| arm B `D5` | 4 / 3 | 4 / 4 | 0 / +1 |
| arm B `D1` | 3 / 3 | 4 / 3 | +1 / 0 |
| arm A `D2`, `D3` · arm B `D2`, `D3` | 2/2, 2/2, 2/2, 4/4 | identical | **0** |

**R-H1 forbids reading that table as improvement, and this ticket does not.** The
two rows sit in different eras and the instrument changed twice between them
(`PA-03-corpus-port`, `PA-04-port-swap-columns`), the rubric gained R-H1..R-H4 at
PA-05, and — decisively — **the judges are different agents and this round gave
them all three artifacts where EVAL-RERUN gave each one.** What can be said is
that D2 and D3 did not move by a single point on either arm, and both are
dimensions about the artifact's shape; the four points that did move are on the
two dimensions whose evidence is what a judge chose to go and run.

**Both judges named the mechanism themselves.** Each seeded its own faults and
ran them against each author's own suite rather than scoring the packet — one
wrote seven, one wrote one — and each said, unprompted, that doing so is what
moved a score. `D4 = 4` requires *"a deliberate behavior-breaking change is shown
to be caught"*, and a judge who executes one can award it where a judge reading a
table cannot. **That is a change in judging practice, not in the artifacts**, and
it is filed as `PA-06-DF-06`.

---

## FINDINGS BY CHANNEL — 1 : 12 : 4 : 2, and the ratio IS the result

| channel | findings | what it cost |
|---|---|---|
| **suite re-run** | **1** | one command, already in the acceptance list |
| **fresh adversarial attack** | **12** | one agent, 94 tool calls, ~25 minutes |
| **blind judges, asked what they REJECTED** | **4** | free — it is a section of the card |
| **blind author, asked what it REJECTED** | **2** | free — one extra paragraph in the prompt |

**Stated as a result and not as a table: the three channels that ask an agent
what it REJECTED or told it to attack produced 18 of this round's 19 findings.
The suite produced 1, and that 1 is the first it has produced in four rounds.**

### suite re-run — 1

`tests/test_code_complexity.py::test_nothing_executable_reads_this_instrument`
went **RED** against PA-06's own `measure/build_evidence_packets.py`. **`N06`
predicted zero from this channel and FAILS**, and the failure is the good kind:
the alarm the ledger set was *"a suite-only round means the suite has stopped
being informative"*, and what happened is the opposite.

The tripwire is a **substring grep for `code_complexity`** over the executable
surfaces **plus every `*.py` under `specs/`** — including `specs/results/**`,
which this epic's own `representation_scope` declares out of model as *"recorded
evidence"*. It cannot tell a mention from a gate: a file naming the script in a
docstring FAILS, a file importing it under an alias PASSES. **Left red on
purpose.** Repairing a check during the measurement it watches is the forbidden
act, and evading it by renaming a string would be the six-lines-of-YAML defeat
this epic exists to prevent, performed by the ticket that exists to catch it.
Filed as `PA-06-DF-05`.

### fresh adversarial attack — 12

One agent, told to break this round's claims and that a finding making the
headline worse is worth more than one confirming it. Full list in
`channels/ADVERSARIAL.md`; the four that changed this document are `AD-F1`
(the null is entailed by the re-anchoring), `AD-F4`/`AD-F5` (the repaired control
is unobservable in one step on three of four trees and the probe that certifies
it cannot fail), `AD-F7` (the port machinery adds no unique kill) and `AD-F11`
(the length-match number was measured on the wrong file).

**What it could NOT break, which is the other half of a channel's value:**

- **Zero equivalent mutants in the arm-C catalogue.** Every row produces the
  observable it declares, verified by running an exhaustive 28,561-sequence
  fingerprint per arm per mutant. Nothing in it flatters or penalises arm C.
- **`PA-M12` dies for the reason claimed.** The mirror experiment — the same
  semantic moved to the other side of the same port — reproduces the identical
  mechanism and the identical failure count, 854 either way.
- **Determinism.** Three runs of `port_corpus_run.py` byte-identical; a full
  independent re-run of `run_port_swap.py --subject arm_b` byte-identical to this
  round's artifact.
- **The arms are behaviourally identical on unmutated code**, once two genuinely
  unspecified echoes are normalised.
- **An injected harness fault is LOUD.** Renaming a private attribute so the
  fake wiring silently falls back to the real file makes 1,225 of 1,543 cases
  fail — and `run_port_swap.py` marks the whole column `CONTROL_RED` rather than
  reporting kills.

### blind judges, asked what they REJECTED — 4

Both judges' REJECTED sections are transcribed verbatim on their cards. Four
findings came out of them and none out of their scores:

1. **The `U` and `W` evidence packets are byte-identical apart from one column
   header.** One judge diffed them; PA-06 re-verified it (`diff` returns exactly
   one line, the mechanical block's header at :310). *"An 11 × 11 apparatus that
   separates three artifacts by three cells is either measuring something the
   artifacts do not vary in, or it is not measuring."*
2. **D2's top half is unreachable by construction under this task design** —
   anchor 3 needs a before and an after, and a from-scratch implementation of one
   spec has no before. All six cards are 2 and will be again.
3. **D1 and D4 risk becoming free points** that report the harness's competence
   as the artifact's, unless the rubric requires the judge to seed and run.
4. **The blinding leaks through `NOTES.md` and no pass can fix it** — an author
   asked to explain its design describes it. Both judges found it, both named
   the tension, both stated what their scores actually rested on instead.

### blind author, asked what it REJECTED — 2

`arms/arm_c/REJECTED.md`, produced because the dispatch asked for it and arms A
and B never were:

1. **The port, considered and declined on merit** (`:77-88`) — the single most
   load-bearing piece of evidence in this round, and no measurement could have
   produced it.
2. **An unreachable branch shipped, and said so about** — the blank-line filter
   in `ledger_lines()`, which the author records as never exercised
   (`NOTES.md:179-188`). Both judges cited it under D5.

**The file was WITHHELD from the blind copies**, because only one arm was asked
for one and shipping it in one packet would have told a judge which artifact this
round produced. Recorded in `UNBLINDING.md`.

---

## Reproduction

```bash
PY=/opt/homebrew/bin/python3.14     # plain python3 here is 3.9 and lacks tomllib

# the five corpora (write outside the repo; the whole-view one is large)
python3 scripts/tla_spec_dev.py --spec-root specs generate cases \
  examples/validation/ab/model/QuotaLedger.tla examples/validation/ab/model/QuotaLedger.cfg \
  --out <scratch>/specs/corpus-whole --package quota_whole --view internal
#   ... --negative-cases only            -> corpus-neg   (package quota_neg)
#   ... --negative-cases with-positive --port-cases only -> corpus-port (quota_port)
#   ... the two Aspect_*.tla slices from specs/results/scorecards/hexagonal-prompting/measure
#       with --module-path examples/validation/ab/model and
#       --state-projector aspect_projectors:project_reservations / project_ledger

# arm C's integrity and its control property
python3 examples/validation/ab/check_catalogue.py \
  --root specs/results/scorecards/ports-as-adapters/arms/arm_c \
  --catalogue specs/results/scorecards/ports-as-adapters/measure/catalogue_arm_c.toml
python3 examples/validation/ab/check_catalogue.py --controls --tree-root \
  --root specs/results/scorecards/ports-as-adapters/arms/arm_c \
  --catalogue specs/results/scorecards/ports-as-adapters/measure/pa_m14_arm_c.toml \
  --impl quota_ledger

# the 8-instrument table, per arm (arm C shown; arms A and B use the rerun measure dir)
M=specs/results/scorecards/ports-as-adapters/measure
PYTHONPATH=$PWD/$M $PY examples/validation/ab/eval/run_controls.py --label PA06-arm-C \
  --tree specs/results/scorecards/ports-as-adapters/arms/arm_c --module-dir . \
  --binding pa06_arm_c_binding \
  --catalogue $M/catalogue_arm_c.toml --catalogue $M/controls_arm_c.toml \
  --instrument corpus-whole=<scratch>/specs/corpus-whole/spec-unit/quota_whole \
  --instrument corpus-neg=<scratch>/specs/corpus-neg/spec-unit/quota_neg \
  --instrument corpus-slice-res=<scratch>/specs/corpus-slice-res/spec-unit/quota_slice_res \
  --instrument corpus-slice-led=<scratch>/specs/corpus-slice-led/spec-unit/quota_slice_led \
  --instrument corpus-port=<scratch>/specs/corpus-port/spec-unit/quota_port \
  --instrument map-silent=<scratch>/specs/corpus-whole/spec-unit/quota_whole:silent \
  --instrument map-checking=<scratch>/specs/corpus-whole/spec-unit/quota_whole:checking \
  --suite examples/validation/ab/tests/test_behavior.py --out <out>/kill-table-arm-c.json

# the port-binding table, all four subjects, one driver
S=specs/results/scorecards/ports-as-adapters/GOAL-port-reach/measure
for T in reference_ports arm_a arm_b arm_c; do
  PYTHONPATH=$PWD/$M $PY $S/run_port_swap.py --subject $T \
    --cases <scratch>/specs/corpus-port/spec-unit/quota_port --out <out>/swap-$T.json
done

# the blind copies and the judges' packets
python3 $M/make_blind_copies.py        # VERIFY: clean
$PY      $M/build_evidence_packets.py
```
