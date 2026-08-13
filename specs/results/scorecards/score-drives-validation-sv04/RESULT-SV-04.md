# SV-04 — the loop reached the program, and the file it built is already wrong

**`GOAL-loop-reaches-the-program`. Branch point `86a8767`, verified with
`git rev-parse --short HEAD` rather than taken on trust — the charter records
that `wt new` branches from the local ref and has put tickets 4, 14 and 21
commits behind, and that a handed-out SHA failed to resolve once. This one
resolved and matched.**

Every number below names the tree it was taken at.

---

## 1. The one sentence

**A defect harvested from a sealed judge's note became a test file, and the test
file moved a score: `D3` reads `4, 4` on the arm that has it and `3, 3` on a
concurrently-judged control arm whose bytes are identical in every other
respect — and the same round found that the file's own docstring makes a claim
that is false.**

Seven epics had never carried a score into a test, a diagram, a model action or
an adapter. This is the first one. It is also the first round in this programme
to run **a concurrent negative control**, which is the only reason the first
sentence is a measurement rather than a story.

---

## 2. The harvested class, and it is real

**`HARVEST-CL-03.md` class `A1`** — *the real adapter's one distinguishing
property is observed by nothing.* Found by four judges across three epics, plus
two more in `CL-03`'s own round. **Filed once, as `RM-05-DF-05`. Consumed by
nothing, for seven epics.** That is the thing this ticket exists to change, and
the reason the work order forbids inventing a fresh defect.

Reproduced by this ticket **before anything was written**, at tree `86a8767`:

| | shared 28-case suite, real wiring | `ledger.txt` files created |
|---|---|---|
| control | 28 passed | **28** |
| `FileJournal` gutted to a list, zero filesystem calls | **28 passed** | **0** |

The suite is 28 cases (`pytest --collect-only`, tree `86a8767`;
`examples/validation/ab/tests/test_behavior.py` is byte-identical at every tree
in this ticket — `git diff 86a8767` on it is empty).

**The class is real.** This is its third independent reproduction.

---

## 3. What was built, and why that carrier

**`examples/validation/ab/tests/test_journal_conformance.py` — 14 cases.**

It is an **adapter conformance suite**: it exercises the two implementations of
the `LedgerJournal` port directly rather than through the domain, in two parts.

- **`TestPortContract`** — one parametrised source of cases run against
  `FileJournal` *and* `InMemoryJournal`. This reaches `journal_memory.py`
  **without a composition point wiring it**, so a fault on the fake side is
  visible in the same run as its mirror on the real side rather than only under
  a second wiring.
- **`TestDurableRecord`** — every assertion made **out of band**, through
  `record_on_disk()`, which opens the declared path with `Path.read_text()` and
  never calls `lines()`. This is the whole remedy: a suite that reads the record
  back through the adapter that wrote it is asking the writer whether it wrote,
  and gets the same answer from an adapter that touched no filesystem.

### Why a test, and why not the other carriers

**Not the shared contract suite.** `tests/test_behavior.py:3-6` says neither arm
may edit it — *"a change here is a change to the requirement, and two arms
measured against two requirements are not an A/B."* A durability case there
would also have to fail against the fake wiring, which runs the identical file.

**Not `reference_ports/` itself.** Putting the file inside the declared subject
scope would have changed the bytes the scored dimensions are pointed at, and the
counterfactual in §5 depends on those bytes not moving. **`reference_ports/` is
byte-identical to the predecessor round in both arms** — `diff -r` is the check.

**Not a diagram.** `references/scoring_validation.md` §5: `diagram`, `mermaid`,
`UML`, `C4` and `.svg` appear in **0 of 87 cards**. Building one to be scored
against a rung that does not exist is the shape `MF-020` names.

**Not a card change.** None was needed, which is the cheap outcome
`SV-07-DF-01` makes worth hunting for. See §7.

---

## 4. The discipline: justified by what it kills, not by what it scores

**Seven mutants, run before the round was dispatched and sealed in
`PREDICTIONS-SV-04.md`.** Four were written for this ticket; **three are lifted
unchanged from the fixture's own `seeded_faults.toml`** (`PA-M11`, `PA-M12`,
`PA-M13`), so the suite is not measured only against faults its author invented.

| mutant | shared 28, real | shared 28, fake | conformance 14 |
|---|---|---|---|
| control | 28 pass | 28 pass | 14 pass |
| **M1** — `FileJournal` gutted (the harvested class) | **28 pass** | **28 pass** | **5 fail** |
| **M2** — record written to a path the port does not declare | **28 pass** | **28 pass** | **5 fail** |
| **M3** — appends buffered until somebody reads | **28 pass** | **28 pass** | **4 fail** |
| **M4** — the fake quietly starts writing a file | **28 pass** | **28 pass** | **1 fail** |
| `PA-M11` — real adapter drops CLOSE on read-back | 3 fail | 28 pass | 2 fail |
| `PA-M12` — the same fault in the fake | 28 pass | 3 fail | 2 fail |
| `PA-M13` — fake truncates stored lines | 28 pass | 6 fail | 3 fail |

**M1–M4 survive the shared suite 56 of 56 under both wirings and die under the
new file.** `PA-M11`/`PA-M12` need two wirings to be seen by the shared suite and
are seen by the new file in one run.

**Three of the 14 cases are killed by none of the seven** and were named in the
sealed predictions rather than quietly kept:
`test_a_new_journal_reports_no_lines` (both parametrisations) and
`test_reading_the_record_does_not_consume_it[FileJournal]`.

---

## 5. The re-score, and the counterfactual is MEASURED

### The design

A before/after against the sealed `close-the-loop-cl03-v5` cards would not have
been safe: **that round's own two passes scored `D2 = 2` and `D2 = 0` on
byte-identical bytes.** An instrument with that spread cannot have a one-round
difference attributed to a treatment. So this round runs **two arms, judged
concurrently, blind to each other and to which arm they hold**:

| arm | packet | check |
|---|---|---|
| `GL` = **CTL** | `FEATURE.md`, `tests/test_behavior.py`, `reference_ports/*` | **byte-identical to `CL-03`'s `blind/artifact_CL/`** (`diff -r` empty) |
| `LG` = **SV** | the same **plus** `tests/test_journal_conformance.py` | differs from `GL` by **exactly one added file** (`diff -r`) |

Same example (`toolchain_removal`), same subject (`toolchain_fixture`), same
declared boundary (`ports-and-adapters`), same judge model (`claude-opus-5[1m]`),
same card — version 5, `serve` = 6,281 bytes, 9 rungs, served digest
`sha256:2d7d4a0506d9b259`, `git diff` on `references/eval_scorecard.md` empty.
**`R-H1` and `R-H2` hold by construction: the packet is the only thing that
moves.**

### The result

| card | arm | D2 | **D3** | ran own faults |
|---|---|---|---|---|
| `20260812-sv04conf-GL-p1` | CTL | 2 | **3** | yes |
| `20260812-sv04conf-GL-p2` | CTL | 2 | **3** | yes |
| `20260812-sv04conf-LG-p1` | SV | 2 | **4** | yes |
| `20260812-sv04conf-LG-p2` | SV | 2 | **4** | yes |

**`D3` delta: +1, unanimous on both sides, with the control unanimous at the
predecessor's value.** All four cards pass `check --require-filled` with
**0 problems**, are sealed into `INSTRUMENT-LOG.toml`, and `audit` reports
**0 violations**. `contested` reports **no contested dimension in this round**.

### Would it have moved without the change? NO — and that is the measured part

**The control arm did not move.** Both `GL` judges reached `D3 = 3` by
independently reproducing the harvested class on the control packet, in their own
words:

> **`GL`-p1:** *"I made `FileJournal` write `'ZZ|COMMIT acme 3 3'` to disk and
> strip the prefix back off on read, and all 28 cases pass through both wirings
> with the durable file holding bytes `FEATURE.md` never describes."*

> **`GL`-p2:** *"(a) … reversed, prefixed garbage … (b) … writing to
> `<path>.elsewhere` so no file ever appears at the caller's path … (c) deleting
> the filesystem from `FileJournal` entirely … 28 passed"* — three separate
> demonstrations, all green.

And both `SV` judges attacked the new file rather than believing it:

> **`LG`-p1:** *"`JF-2`, the real adapter rewritten to touch no filesystem,
> survived 28/28 behavioural cases in BOTH wirings and died only against
> `tests/test_journal_conformance.py:181-210` … So the conformance file's central
> claim about itself is true and I verified it rather than accepting it."*

> **`LG`-p2:** *"I did not take that on the docstring's word. I seeded a fault
> that replaces `FileJournal`'s body with a plain in-memory buffer … 28/28 shared
> cases pass through the REAL wiring with zero `ledger.txt` files created, and 5
> conformance cases kill it. So the out-of-band observer is load-bearing."*

**Four judges, four independent reproductions of the harvested class, and the
score separates exactly on whether an out-of-band observer is present.**

### Was the validation tuned to the score?

The check the project asks for is whether the case is justified by a defect. §4
is that justification and it was sealed before the round. Two further facts:

- **The scored scope's bytes never moved.** Nothing was made to look better; a
  blind spot was made observable.
- **The same file that raised `D3` also lowered the artifact's honesty on its own
  terms**, because it shipped a false sentence (§6). A file written to move a
  number would not have volunteered a list of its own blind spots for a judge to
  falsify — and one of them was falsified.

---

## 6. The unflattering result, and it is the one worth keeping

**`tests/test_journal_conformance.py:41-43` makes a claim that is false.** The
file's "WHAT THIS SUITE STILL CANNOT SEE" list says:

> *"A domain that stopped calling the port entirely is invisible here and visible
> to `test_behavior.py`; the two suites are complements."*

`LG`-p1 seeded `JF-5` — the domain keeps a private shadow list, appends to it
instead of calling the port, and returns it from `ledger_lines()` — and reported
**70 of 70 case-executions green**. **The operator reproduced it independently:**

```
JF-5, the domain never calls the port at all
  shared 28, real wiring: 28 passed
  shared 28, fake wiring: 28 passed
  conformance 14:         14 passed
```

**The second half of that sentence is false. The two suites are not complements
where the file says they are.** This is `HARVEST-CL-03.md` class `E1` —
*documentation asserting what the code does not do* — committed by the very file
written to consume class `A1`, and caught inside one round.

**It is filed (`SV-04-DF-01`) and NOT repaired.** Four sealed cards were written
against these exact bytes; editing the file now would leave the record describing
bytes that no longer exist.

**A second class survives everything**, found by `LG`-p2 and reproduced by the
operator: `FEATURE.md:104`'s *"nothing is ever rewritten."* An adapter that reads
the whole file back and rewrites it on every append is content- and
order-identical and passes **28 real / 28 fake / 14 conformance — 70 of 70**.
The packet asserts append-only as an **outcome** and never as a **mechanism**,
and the new file's own blind-spot list omits it. `SV-04-DF-05`.

---

## 7. The card was not touched, and no bump was needed

```
serve | wc -c    6,281  ->  6,281     (0)
rungs                9  ->      9     (no anchor added, deleted or reworded)
served digest    sha256:2d7d4a0506d9b259  ->  unchanged
git diff 86a8767 -- references/eval_scorecard.md   ->  empty
```

**No card change was required and none was made**, which is the outcome
`SV-07-DF-01` makes worth designing for: it measured that **both carriers — a
scored rung and a recorded note alike — cost a version bump**, because a note's
prompt sits inside both of the card's seals. A closure that needs no card change
pays none of that, and this one did not. **The loop reached the program without
spending a byte of the surface it must not grow.**

---

## 8. The predictions, scored — and two are wrong

Sealed at **`2026-08-12T17:42:26-04:00`** in commit `60f2699`, before any judge
was dispatched and before any judge prompt existed, with all four cards
`unfilled`.

| | prediction | outcome |
|---|---|---|
| **P1** | at least one `LG` pass scores `D3 = 4` | **HELD** — both did |
| **P2** | at least one `LG` pass reasons about `CL-03-DF-02`'s anchor-4 tension | **REFUTED — and it is a result** |
| **P3** | both `GL` passes score `D3 = 3` | **HELD** — the control did not move |
| **P4** | at least one `LG` N-D1 reports durability CAUGHT with a denominator | **HELD** — both did |
| **P5** | the four D2 scores are not all equal; at least one pair contested | **REFUTED** — all four are 2 |
| **P6** | at least one `LG` card names a specific weakness in the new file | **HELD** — and it found a false claim |
| **P7** | the served surface does not move | **HELD** |

### P2 is refuted, and it corrects a filed finding

`CL-03-DF-02` records a `v4` judge's reasoning that **rung 4 is unsatisfiable by
any suite that does assert durability, "since such a case must fail the fake"** —
*"the anchor structurally rewards blindness to the property that makes the real
adapter real."*

**Measured false in its strong form.** No `LG` card reasons about the tension,
because **there is no tension to reason about**: the durability cases are
parametrised over the durable adapters only, so the set of cases run against both
implementations is untouched and anchor 4's literal text stays satisfied — both
`LG` judges ran the shared 28 through both wirings and said so. **A suite can
assert durability without any case failing against the fake.** The anchor does
not reward blindness; it rewards putting the two kinds of case in two places.

`CL-03-DF-02`'s weaker half stands: the anchor's text does not *ask* for the
out-of-band observer, and it took the version 5 caveat to make its absence cost
anything. **The finding is corrected, not deleted** — `SV-04-DF-04`.

### P5 is refuted, and the honest reading is that it cuts against §5's caution

D2 was `2, 0` in the predecessor round on identical bytes and is `2, 2, 2, 2`
here. **The instability that justified building a control arm did not recur.**
That does not retire the caution — a spread that appears in one round of two is
still a spread — but the control arm is reported here as *earned by the
predecessor's variance and not by this round's*, which is the honest description.

---

## 9. Suite numbers, every one with its tree

`denominator_rule`, including suite counts. **No figure below is a `git archive`
figure.**

| suite | count | tree |
|---|---|---|
| repository suite | **2 failed, 1528 passed** (21:38) | `86a8767`, pristine detached checkout at `scratchpad/SV-04/operator/baseline-86a8767`, `git status` 0 entries |
| repository suite | **3 failed, 1527 passed** (21:06) — **the third was SV-04's own**, §9c | `feature/SV-04` at `66b96ff`, `git status` 0 entries |
| repository suite | **2 failed, 1528 passed** (21:59) — the two inherited reds and no third | `feature/SV-04` at `ebfed2e`, `git status` 0 entries |
| shared behavioural contract | **28** cases | `examples/validation/ab/tests/test_behavior.py`, byte-identical at every tree in this ticket (`git diff 86a8767` empty) |
| adapter conformance (new) | **14** cases | `feature/SV-04`; does not exist at `86a8767` |
| round cards | **4** filled, 0 problems, 0 audit violations | `feature/SV-04` |

**The two reds at the branch point are the two the charter declares** and neither
is repaired:
`tests/test_architecture_tags.py::test_the_same_tag_control_holds` (`RM-06-DF-01`)
and `tests/test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer`
(the pricer grep tripped by `CLOSE-THE-LOOP-EPIC.md` and `NEXT-EPIC.md`).
**`RM-06-DF-01`'s failure text is byte-identical at the branch point and at this
tree** — the same nine separating pairs, in the same order — which is the check
that SV-04 did not quietly narrow an inherited red while touching `subjects.toml`.

---

## 9c. SV-04 shipped a third red, and four gates said clean

**The `66b96ff` run above is 3 failed, not 2, and the third one is this ticket's.**
`tests/test_architecture_tags.py::test_a_card_with_no_subject_is_legal_and_is_every_sealed_card`
failed `(82, 87)`: five rows mapped to no declared subject where exactly one is
allowed, and four of the five were this round's cards.

**The cause is the blinding, working correctly.** `scaffold` on a multi-arm round
writes `subject.name: null` with `blinded: true`, because a card whose own
`subject` field names the arm hands a judge the arm before it scores — `F3`'s
first defence. A blinded card therefore carries the scope and not the name, and
`architecture_tags.subject_of` must fall back to the `labels` list in
`subjects.toml`. **Nothing writes that entry**, and `scaffold` holds both the
round directory and the arm labels at the moment it blinds them.

**Everything in the round's own toolchain reported clean on the unregistered
cards** — re-demonstrated by reverting the registration and running each again:

```
check --require-filled   4 filled, 0 problem(s)
seal                     sealed 8 file(s)
audit                    0 violation(s)
contested                counts the groups correctly, 3 -> 5
architecture_tags derive "16 of 20 decided; 4 refused" -- BYTE-IDENTICAL either way
```

Only a repository test caught it, and it sits behind a 21-minute suite. **This is
the `C` class — gates that report clean on broken input — inside the scoring
toolchain itself**, and the consequence is not cosmetic: a round can be
scaffolded, judged, sealed into `INSTRUMENT-LOG.toml` and audited while its cards
are invisible to every architecture-tag comparison, which is the comparability
machinery `RD-05` built them for.

**Repaired here**, because the registration is this round's own close-out step
and the red is this ticket's, not an inherited one: `[subject.toolchain_fixture]`
now carries `["score-drives-validation-sv04", "GL"]` and `["…", "LG"]`.
**`scaffold` was NOT changed** — it is the instrument this round was run through,
and editing it after the arms were judged is the one thing `R-H2` forbids.
Filed as `SV-04-DF-05`.

**The repair is verified by a full run and not by the one test**: `ebfed2e` is
**2 failed, 1528 passed**, which is the branch point's count exactly — same two
reds, same pass total. The new conformance file adds no row to this suite because
it lives under `examples/validation/ab/tests/` and `pytest tests` does not collect
it; that is why the total returns to the baseline's rather than exceeding it.

**And the operator got that wrong once, which is worth recording.** The first
baseline run reported **12 failed** and cost a re-run to explain. Ten of the
twelve were `ModuleNotFoundError: No module named 'yaml'`. The invocation the
sealed record uses carries `--with pyyaml`; **`README.md:35` does not**, and a
ticket that follows the README reads twelve reds against a charter that promises
two. Escalated in §11 rather than filed — the finding budget is spent, on
`SV-02`'s precedent for the same situation.

---

## 9b. `scope` run over this page — and the delta is zero, for a reason

```
python3 examples/validation/scorecards/score_tools.py scope
```

| tree | counted | REFUTED | COUNT-MOVED | HOLDS | UNREACHABLE |
|---|---|---|---|---|---|
| `86a8767` — the branch point | 97 | 71 | 0 | 6 | 20 |
| `86a8767` + SV-04 — this tree | **97** | **71** | **0** | **6** | **20** |

**SV-04's delta is zero on every column**, and no row anywhere in the output
names a file this ticket wrote.

**That is not the same as this page being checked.** The figures here are in
tables and in prose that carry no bind-and-value form, so `scope` is **blind to
them rather than satisfied by them** — `RD-02-DF-01`, stated here rather than
left for a reader to find. `RM-02-DF-05` also applies: the counted-noun pattern
admits no underscore, so `toolchain_removal` written immediately after a count is
refused before the search for a named example runs, which is why every count on
this page names its tree in the sentence beside it instead.

**And one operator error worth leaving in, because it is the class this project
keeps paying for.** The first `scope` run here was issued as
`timeout 500 python3 …` and died with `ModuleNotFoundError: No module named
'tomllib'`, which was nearly written up as a property of the tool. It is not.
`python3` in this shell is an alias, `timeout` does not expand aliases, and the
`python3` on `PATH` is a different interpreter. **A figure taken through a
wrapper is a figure about the wrapper**, which is `RM-02`'s complaint about
`git archive` in a second costume, and it was caught only because the number
contradicted five earlier subcommands that had run clean.

---

## 10. Blinding — every disclosure, recorded

**Blinded by mechanism**: arms emitted as `GL`/`LG` from a label pool that
excludes every label a prior round published; the mapping was written to
`UNBLINDING.md`, which no judge was given.

**Three leak classes, all volunteered by the judges, none used to discard a
card.**

1. **The packet narrates prior scores at its own judge.** All four judges
   disclosed it. `reference_ports/README.md:20-23` and
   `journal_memory.py:9-15` quote `BA-B14` verbatim including *"the fake that
   earned arm B its D3 = 4"* — a prior score, on the dimension they are the
   instrument for. This is `HARVEST-CL-03.md` `F3`, sixth instance, and it
   **pre-exists this ticket**: those bytes are in both arms and in the
   predecessor round.
2. **This ticket added a seventh instance, and it was declared in advance.**
   `test_journal_conformance.py:16-18` cites `RM-05-DF-05`. `LG`-p2 named it.
   The sealed predictions carry it as a known disclosure, and the point of the
   `GL` arm is that it is **not** exposed to it — which is why the pair still
   means something.
3. **NEW, and it is in our instrument rather than in an artifact.**
   `examples/validation/scorecards/score_tools.py` narrates prior judges' score
   distributions in its own source comments — five sites, including
   *"`opus` judged D3 2, 2 and `sonnet` 4, 3 on the same artifact"*,
   *"D3 came out 2, 2, 3, 4"* and *"D2 has taken one value on every card ever
   written about `ab_quota_ledger`"*. **Every judge is instructed to run `check`
   from that file.** Two of four disclosed reading them. `SV-04-DF-02`.

---

## 11. What was REJECTED — especially what would have moved the score more easily

- **Adding the durability case to `tests/test_behavior.py`.** The single
  cheapest way to make the shared suite look better, and it would have broken
  the A/B the file exists to serve, and failed against the fake wiring.
- **Editing `reference_ports/` to make the adapter more obviously real** — for
  instance making `FileJournal` reopen rather than truncate. It would have moved
  the scored scope's bytes and destroyed the counterfactual; and repairing an
  artifact during a measurement is what the doctrine forbids.
- **Reporting D3 `3, 3 → 4, 4` against the sealed `cl03-v5` cards and stopping
  there.** It is the same headline for a quarter of the work, and it would have
  rested on an instrument that had just scored the same bytes `2` and `0`. The
  control arm is the difference between a claim and a measurement.
- **Fixing the false docstring sentence found in §6.** It would have made this
  page tidier and made four sealed cards describe bytes that no longer exist.
- **Deleting the three cases that killed nothing**, to report 14 of 14 justified
  instead of 11 of 14. They are named in the sealed predictions instead.
- **Proposing a rung, a note prompt, or any card change.** `SV-07-DF-01` prices
  both carriers at a version bump; the closure did not need one, and needing none
  is the better result.
- **Repairing either inherited red**, or the `--with pyyaml` gap in `README.md`.
- **A diagram.** Zero evidence in 87 cards that one has ever been scored.

---

## 12. What this ticket CANNOT settle

- **`n = 2` per arm, one artifact, one feature.** The `D3` separation is four
  cards.
- **The control is concurrent, not paired.** `GL` and `LG` were judged by
  different agent instances; the arms bound judge variance rather than eliminate
  it.
- **The operator is not blind** and wrote the artifact, the mutants and the
  packets.
- **Whether the file is *good* validation is not settled by `D3` going to 4.**
  Two of its claims were falsified inside the same round. The score moved; the
  suite still misses the domain-bypass class and the rewrite class entirely.
- **Nothing here shows an adopter would build this**, or that a conformance suite
  is the right carrier for any defect other than this one.
