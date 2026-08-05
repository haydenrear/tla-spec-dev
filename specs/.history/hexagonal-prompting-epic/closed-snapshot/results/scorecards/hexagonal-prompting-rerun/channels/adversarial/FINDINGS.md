# Adversarial channel — EVAL-RERUN

An agent was given this round's arms, catalogues, bindings, kill tables and run
record, told this round's eight headline claims, and told its job was to
falsify them. **FILE FINDINGS, FIX NOTHING.** Nothing in the repository was
modified by it; nothing was re-seeded and no instrument was re-run to improve a
number. The prompt is `PROMPT.md`.

## What it did before writing anything

1. **Regenerated all four corpora from scratch** from `QuotaLedger.tla`:
   43,128 / 118 / 2,438 / 56 — matching every shipped `cases` field.
2. **Re-ran `run_controls.py` end to end on both arms** against those fresh corpora.
3. **Hand-re-derived eight cells** with its own harness, sharing only
   `oracle.py` and the corpus — not the driver.
4. **Ran four probes designed to keep a control green while the thing it
   controls for is broken.**

**Every number in the shipped tables reproduced.** The findings are not about
arithmetic. They are about what the numbers are evidence *of*, and all three
SEVERE ones are about the controls — the part whose entire job is to say when
the rest is lying.

---

## SEVERE

### F1 — On arm B the positive control is insensitive to the exact failure it exists to detect

`oracle.py` states M07's purpose: if `Reserve` stops executing, M07 must go red.
The channel built `corpus-noreserve` — `corpus-whole` with every `Reserve` case
deleted and nothing else changed (42,540 cases, 3,440 executing) — reproducing
HP-06's regression exactly, and ran the sealed catalogue against it:

```
ARM A: corpus-noreserve  M07 = SURVIVED     <- control correctly goes RED
ARM B: corpus-noreserve  M07 = KILLED       <- control stays green through it
  case_0009_close_tenant: available: expected {'t1': 2, 't2': 2}, actual {'t1': 1, 't2': 1}
```

Arm B's M07 is killed by `CloseTenant` cases on states with **no live
reservation at all** — note `t2`, never touched, is also wrong. The substitute
inflates a *computation* that runs on every read, so it is detectable without
`Reserve` ever executing.

It is already visible in the shipped data: arm B's `M07 / corpus-neg` is KILLED
while that instrument's own control block records
`"Reserve": {"ran": 64, "ran_accepting": 0}`.

**Consequence.** `measure/catalogue_arm_b.toml` carries arm A's role string
verbatim — *"must die on every instrument that can execute an accepted
Reserve"* — and the round's own arm-B data contradicts it. **"Both controls are
GREEN on both arms" is true and means two different things on the two arms.**
The whole-view rows on **arm A** are backed by a control that demonstrably goes
red when its failure mode returns. The whole-view rows on **arm B** are not.

Filed as **EVAL-RERUN-DF-03**. Not fixed.

### F2 — A declared `[[limitation]]` silently converts a demonstrated KILL into NOT_DECIDABLE, and the "verification" cannot tell the difference

`run_controls.py` decides `NOT_DECIDABLE` **before** consulting the mutated run
and never checks whether the cell it suppresses would have been `KILLED`.

**Probe 1** — arm A's `corpus-neg` limitation, copied verbatim onto arm B, where
that cell is a demonstrated KILL:

```
M07 row:             {"corpus-neg": "NOT_DECIDABLE", "corpus-whole": "KILLED"}
control verdict:     {"green": true, "instruments_not_decidable": ["corpus-neg"]}
declared_limitation: {"verified": true, "witness_expected": 0, "witness_observed": 0}
exit=0
```

A cell the instrument demonstrably kills becomes NOT_DECIDABLE, the limitation
reports `verified: true`, the control reports green, exit 0, and **nothing in
the artifact says a kill was discarded.**

**Probe 2** — `verify_limitation` reads `counts.get(key, 0)`, so a **missing key
is indistinguishable from a measured zero.** Declared on arm A's M06, which
ships as KILLED under both instruments:

```
M06 row: {"corpus-slice-res": "KILLED", "corpus-whole": "NOT_DECIDABLE",
          "map-checking": "NOT_DECIDABLE"}
  witness "positive ThisActionDoesNotExist cases executed"  -> verified: true
  witness "negative Commit cases executed"                  -> verified: true
per_class output_oracle: {"corpus-whole": "0 of 0 (1 not decidable)"}
```

An action name that appears **nowhere in the model** "verifies". Two genuine
kills erased, class denominator collapsed to `0 of 0`, exit 0.

**This is a suppression key the project's own tripwire does not scan for.**
`seeded_faults.toml` promises that `expected_to_survive`, `known_survivor`,
`waiver` "and friends are scanned for by `scripts/kill_test.py` and reported
loudly". That scanner's 19 `SUPPRESSION_KEYS` do not include `limitation`,
`witness_ran_must_be` or `not_decidable`, and `run_controls.py` never invokes
it. The design intent is right; the implementation cannot distinguish *"this
instrument cannot decide this mutant"* from *"it decides it and we asked not to
be told."*

This is a defect in the **shipped EVAL-STABLE driver**, so it applies to the
sealed reference run in `examples/validation/ab/eval/results/` as well as to
this round. Filed as **EVAL-RERUN-DF-02**. Not fixed.

### F3 — The `corpus-slice-led` limitation is verified against a missing key, and its stated cause is false on arm B

Both arms declare, in identical text, that the LEDGER slice *"cannot execute the
mutated line"*.

**(a) The verification is vacuous.** The witness is `positive Reserve executed
== 0`; `corpus-slice-led`'s control block has **no `Reserve` key at all**. The
zero came from `.get(..., 0)` on an absent key, by exactly the mechanism F2
exploits. On arm B this is the *only* declared limitation, so **100% of arm B's
limitations are "verified" by the absence of a count.** This round's own
sentence — *"each with a witness the driver verified against this run's own
executability counts"* — is false for that cell.

**(b) The stated cause is false on arm B.** Arm B's M07 lives in `_held`, which
`available()` calls on every read. The channel regenerated `corpus-slice-led`
with `available` added to the projector, so the *same* cases run:

```
ARM A: slice-led original = SURVIVED   slice-led + available = SURVIVED
ARM B: slice-led original = SURVIVED   slice-led + available = KILLED
```

Arm A's reason is sound. Arm B's is not: the only operative constraint is the
projection, not the corpus. One reason text, one witness, sound on one arm and
unsound on the other. Filed as **EVAL-RERUN-DF-04**. Not fixed.

---

## MODERATE

### F4 — The declared cause of the 294 skipped `Reserve` cases is wrong for 266 of them

Classifying all 588 `Reserve` cases against `oracle.allocatable_id`:

```
not-expressible total:                                                      294
  allocatable id OUTSIDE the model's ResIds (no case could ever express it): 266
  allocatable id inside ResIds but the case named another free one:           28
```

**Only 28 of 294 (9.5%) match the stated description** *"a case naming a
different id"*. For the other 266 the API's next id is `r3`, outside
`ResIds = {r1, r2}` entirely, so **no** choice of `r` could have been
expressible. The real mismatch is that the model allocates ids in any order from
a finite recycled domain while the API allocates a monotone prefix: **the
before-state, not the argument, is what the API cannot reach.**

Secondary: **"exactly half" is a coincidence of `|ResIds| = 2`**, not a property
of the refinement — it is `232 + 62` against `204 + 28 + 62`, two
sub-populations landing on symmetric splits for different reasons.

### F5 — 252 executed cases run from before-states the API can never reach, uncounted

```
EXECUTED from API-unreachable before-states:
  Commit 44, Release 44, CloseTenant 164  = 252 of 3,734 (6.7%)
```

The runs are not invalid — the installed structure is legal — but the round
declares the *same* refinement gap as a counted, per-action, never-netted-out
limitation on `Reserve` and is **silent about it on three other actions.** The
arithmetic is complete; the attribution is not.

### F6 — "76 comparable cells" over-counts what is comparable

`catalogue_arm_b.toml` says M07's arm-A and arm-B **cells** — plural, all seven
— are not the same experiment, and M08/M10 are seeded by addition, so three of
eleven rows are not the same diff. **Strictly comparable is 8 x 7 = 56 cells,
not 76.** The conclusion survives on the 56; the denominator quoted for it does
not.

### F7 — The bar's non-reproduction is caused by the union, not by the negative control

```
arm A: union=10 of 11  suite=10 of 11   |   without N01: union=10 of 10  suite=10 of 10
arm B: union=10 of 11  suite=10 of 11   |   without N01: union=10 of 10  suite=10 of 10
best single generated instrument: 7 (map-checking), both arms
```

**Delete N01 and the suite still ties the union, 10 to 10.** The tie is produced
by the union aggregate — which this round's own README calls "the forbidden
aggregate" two paragraphs later, and which no single generated instrument
approaches. The point about the *old* catalogue is fair; the headline
attributing the non-reproduction to N01 is supported by no cell.

### F8 — Arm B's M07 substitutes where the sealed rule requires a reported hole

`seeded_faults.toml`: *"A re-anchored mutant that cannot reproduce its `semantic`
on some arm is a REPORTED HOLE in that arm's row, never a silent omission and
never a survivor."* Arm B's M07 does not reproduce the sealed semantic (present
from construction, on every tenant, after any command, versus "breaks on the
very first accepted reservation"). The round substitutes and inherits M07's id,
`control_role` and class row — and F1 shows the substitute does not perform the
control's job.

---

## MINOR

| # | finding |
|---|---|
| F9 | `reference-run.json` is **not** byte-identical to `final-run-1.json`: it differs in `label`. `per_mutant`, `controls` and `evidence` are equal. Same class of over-claim (HP-06-DF-09) this round says it closed. |
| F10 | The shipped determinism pair is byte-identical **and carries the same label**, contradicting the README's "the only difference is the `--label` string" — and a same-label byte-identical pair is indistinguishable from `cp`. Claim 5 itself survives, independently reproduced; the shipped evidence is not self-authenticating. |
| F11 | The 39,100 refusal skips are recorded under the wrong reason. The substance is true (all seven `Refuse*` actions carry no params) but `can_run` tests `action not in BOUND_ACTIONS` first, so the argument check never fires and would report the same 39,100 if arguments *were* recoverable. |
| F12 | `map-silent` is not identical to `corpus-whole` "by construction": binding the port adds a `_decode`/`AppendLedgerLine` parse step that can raise where `corpus-whole` cannot. Identical on all 11 mutants here — verified — not by construction. |
| F13 | `REFUSED_ONLY_BY_R` claims "refused **only** by a constraint on `r`" from a regex for a standalone `r`. A compound reason would take a guard-relaxation case with it. Latent; not exercised — all 118 negative reasons are single conjuncts. |
| F14 | `mechanical.json`'s `state_writers` counts only attribute rebinding, so `_available` shows one writer although `reserve` and `release` mutate it in place. `max_writers_of_one_attribute: 2` is an **undercount on both arms** — and this is the block credited with exposing EVAL-RERUN-DF-01. |
| F15 | Claim 7 reproduces exactly on an independent AST recount, but holds only for *production* lines: `test_lines` is 252 (A) vs 190 (B), so production+test is **374 (A) vs 319 (B)**. Arm B's 129 includes the fake adapter that buys the shorter test file. |
| F16 | **NOT-A-FINDING against the round** — the attack brief said the union kills "9 of 11 on arm A"; the shipped README and JSON both say 10 of 11, and the channel recomputed 10 of 11. The round did not make the claim the brief attributed to it. |

---

## CLAIMS IT TRIED TO BREAK AND COULD NOT

A claim nobody attacked is not evidence. These were attacked and held.

| | claim, and how it was attacked |
|---|---|
| **C1** | **The corpora reproduce.** All four regenerated from the `.tla`: 43,128 / 118 / 2,438 / 56. |
| **C2** | **Every cell of both kill tables reproduces from scratch**, on fresh corpora, through a full independent run: `per_mutant`, `controls_on_unmutated_code`, `evidence`, `per_class` and `reality_witnesses` all identical modulo label, retained failure text and per-action counts included. Independently corroborates the determinism claim despite F10. |
| **C3** | **Eight cells re-derived OUTSIDE the driver**, with a harness sharing only `oracle.py` and the corpus. Eight of eight MATCH. |
| **C4** | **`KILLED` is attributable; no cell is killed for an unrelated reason.** Every retained failure string in both tables is an `AssertionError` naming the mutant's own semantic. The `try/except Exception` *would* score an infrastructure error as a kill; the retained text makes that visible and it did not happen. |
| **C5** | **Catalogue integrity re-proves**, exit 0, output byte-identical to the shipped files. Arm B's M06 and M10 share a `find` string and it still occurs exactly once, so they do not collide. |
| **C6** | **The executability accounting is arithmetically complete**: `ran + skipped == cases` per instrument and per action with no residue; `1872+784+784+(294+294)+39100 = 43128`; `3734/43128 = 8.658%`. |
| **C7** | **The EVAL-RERUN-DF-01 fix is correct and there is no second live instance.** Every module-level import in the pipeline was traced; none holds a handle on the mutated tree; `reference_binding` is on the purge list so the reference run was never exposed. The closest conceptual second instance — `verify_limitation` reading witness counts from the pristine control pass and applying them to mutated runs — is sound, because executability is a pure function of the corpus and a mutant cannot change how many cases run. |
| **C8** | **Arm B's two `addition` seedings are honest.** Arm A inflates `_available`; arm B inflates `_quota` and lets the derivation produce the same error. Net effect identical, reach symmetric, both die under exactly the same four instruments on both arms. "The `seeded_by` column does real work and the disclosure is accurate." |
| **C9** | **N01 is a genuine fault and does survive the hand-written suite.** The reality witness separates the trees through the public API on both arms; `outstanding_ids()` is only ever compared against `["r1"]` or `[]`; the three suite tests that create two or more live reservations never assert order; `28 passed` on both N01-mutated trees. |
| **C10** | **M09's retirement is correct.** The model's `ledger` is `Append(...)`, projected positionally, so ordering is expressible — M09 dies under four instruments while N01 (a set) survives all seven. |
| **C11** | **The negative corpus really does cover the refusals.** All six declared rejection reasons appear across its 118 cases; 94 execute; the 3-of-3 guard-relaxation headline reproduces exactly on both arms. |
| **C12** | **The mechanical figures reproduce** on an independent AST recount (framing caveat at F15). |

## The channel's own bottom line

> The measurement is arithmetically sound and fully reproducible. All three
> SEVERE findings are about the **controls**, and specifically about **arm B**:
> its positive control is insensitive to its own failure mode, its single
> declared limitation is "verified" by an absent count, and the suppression
> mechanism that produced that limitation can be shown — on this round's own
> data — to erase a kill the same round measured.
