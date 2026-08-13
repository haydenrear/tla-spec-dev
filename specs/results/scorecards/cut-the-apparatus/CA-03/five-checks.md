# `SV-04-DF-05` — the five checks that passed a live defect, decided on the record

**CA-03. Measured at `4302082`.**

**Verdict: the registration hole is repaired in `scaffold`, all five checks are
kept, one is carried to `CA-08` as a priced removal candidate CA-03 may not
make, and NO GATE IS ADDED.**

---

## 0. The finding, quoted before it is used

`specs/desired_program_model/deferred_findings.yaml`, `SV-04-DF-05`:

> WHAT REPORTED CLEAN on SV-04's four unregistered cards, every one of them run
> before the gap was known:
>
> ```
> score_tools.py check --require-filled  ->  4 filled, 0 problem(s)
> score_tools.py seal                    ->  sealed 8 file(s)
> score_tools.py audit                   ->  0 violation(s)
> score_tools.py contested               ->  counts the groups correctly (3 -> 5)
> architecture_tags.py derive            ->  "16 of 20 decided; 4 refused",
>                                            BYTE-IDENTICAL before and after
>                                            the registration
> ```

Its `suggested_fix`, in full, because CA-03 takes the **first** half and rejects
the second:

> Have `scaffold` append the `[round-dir, arm-label]` pairs to the named
> subject's `labels` when it blinds `subject.name`, since it holds both values at
> that moment and the blinding is exactly what makes them necessary. **Failing
> that**, make `check` refuse a filled card that maps to no declared subject […]

**The second option is a new gate. CA-03 does not take it.** The first refuses
nothing and is what shipped.

---

## 1. The repair, and the failing input it ships with

**`SV-04-DF-05` is not a defect in any of the five checks. It is a defect in
`scaffold`**, which blinds `subject.name` — `F3`'s first defence, because a card
whose own `subject` names the arm hands a judge the arm before it scores — and
then does not write down the one thing that makes the blinded card attributable.
`architecture_tags.subject_of` falls back to `subjects.toml`'s `labels`, and
nothing wrote the entry.

**Shipped:** `score_tools.py` gains `register_round()` and `cmd_scaffold` calls
it after the cards are on disk, for blinded rounds carrying `--subject`, when the
round is under the scorecard root `subject_of` actually walks.

**It refuses nothing.** A round it cannot register still scaffolds; the tool
prints the exact TOML lines and the operator pastes them — which is precisely the
manual step SV-04 performed after the fact. The cards are the measurement and a
bookkeeping failure does not cost one.

### `R1`: the demonstrated failing input, on a real subject

`tests/test_score_tools.py::test_a_blinded_round_registers_itself_and_the_unregistered_card_is_the_failing_input`

The subject is **`toolchain_fixture` out of the real `subjects.toml`** — the exact
entry SV-04 filled in by hand, and the file's own comment beside it says so:

> SV-04's round is mapped HERE and not by its cards, and the reason is the
> blinding.

The test scaffolds a real blinded round, then:

1. **runs the failing input first and asserts it fails** — against the
   declaration file as it stood, `subject_of` returns `None` for all four cards,
   which is the state `check`, `seal`, `audit`, `contested` and `derive` all
   reported clean on;
2. asserts the same four cards now map to `toolchain_fixture`;
3. asserts **every pre-existing subject's labels, scope and declared value are
   untouched** — this file is the attribution record for every sealed card;
4. asserts idempotence, and that a second round registers beside the first;
5. asserts an **unblinded** round gets no entry, because its cards name the
   subject themselves.

Two more tests pin the boundaries: a round outside the scorecard root is not
registered and says so, and a registration that cannot be made leaves the file
byte-identical rather than writing something broken.

### What the repair is NOT

`subjects.toml` opens *"Nothing here is computed and nothing here may be."* That
sentence is about the **declaration** — `scope` and `declared_effect_boundary`,
which exist so derivation and declaration can disagree. `labels` is the record of
which cards scored the subject; the file's own comment says SV-04's round *"is
mapped HERE and not by its cards, and the reason is the blinding."* **No derived
value is written and no declared value is touched.**

### DECLARED BOUND: the repair fires only when `--subject` is passed, and `--subject` is optional

**Raised by independent review of PR #266, verified, and stated rather than
fixed.** `cmd_scaffold`'s registration is guarded by `if args.subject and not
args.unblinded`. `--subject` has `default=None`. **So a blinded round scaffolded
without `--subject` is untouched by this fix and still produces cards that map to
no declared subject.**

**`SV-04-DF-05`'s own reproduction command is exactly that case:**

> Scaffold any multi-arm round (blinding is the default):
> `score_tools.py scaffold <dir> --example E --arms A,B --judges 2`.

**No `--subject`. The finding's own reproduction still reproduces.**

**This is a real bound and it is the strongest argument for the option I
rejected**: making `check` refuse a filled card that maps to no declared subject
would have covered the no-`--subject` case too, because it acts at read time on
any card. I still decline it — it is a sixth gate and this epic forbids one — but
the trade is not free and the record should say which half of the defect each
option covers:

| | round WITH `--subject` | round WITHOUT `--subject` |
|---|---|---|
| **shipped: `scaffold` records** | covered | **NOT covered** |
| rejected: `check` refuses | covered | covered |

**Why the shipped half is still the right half.** A round scaffolded without
`--subject` has declared no scope either, so `check`'s A5 scope defence never
engaged for it and it was never comparable to begin with; the `--subject` case is
the one where a round *did* everything right and was still invisible. But that is
an argument about which half matters more, **not** a claim to have closed the
defect, and the first version of this document read as the latter.

### DECLARED: this ticket added a runtime writer outside its `conflict_keys`

`register_round` **writes** `examples/validation/scorecards/subjects.toml` at
scaffold time. That file is **not** in CA-03's `conflict_keys`
(`production: ["examples/validation/scorecards/score_tools.py"]`). **No conflict
arose** — no other CA ticket touches it, the file is byte-unchanged in this PR's
diff, and it is byte-unchanged after a full 1,525-test suite run. **But the
ownership is now shared at runtime and is declared here** so the next ticket
editing `subjects.toml` knows a tool writes it.

---

## 2. The five, decided

> **CORRECTED after independent review of PR #266.** Four figures in the first
> version of this table were wrong, and **three of the four were wrong because I
> restated somebody else's number instead of re-deriving it** — which is exactly
> the discipline this ticket claims as its contribution, and the `CA-00-DF-05`
> class for the third time in this epic, once by me. **Every figure below has now
> been re-derived from the record by this document.** The corrections are §3a.
> **No verdict changed**, which is worth saying plainly: the case for keeping
> `audit` and `contested` survives its own numbers being wrong, and that is luck
> rather than method.

| check | what it has caught | verdict |
|---|---|---|
| **`check`** | **The rule-8 case is a COUNTERFACTUAL and is WITHDRAWN** (§3a.4). The real case: **it executes CL-01's second seal** (§3) — a primary catch on a live class. | **KEEP** |
| **`seal`** | No recorded firing of its own refusal in eight epics. But R-H4 is on the do-not-cut list and **has nothing to verify without the digests `seal` writes**. | **KEEP**, with the blind spot recorded (`CA-03-DF-04`) |
| **`audit`** | **9** `SUPERSEDED-UNMARKED` on `SM-04`; **10 on `CL-03`, spanning 3 distinct `measured_at` commits and carrying 4 `goal-*` claims** — re-derived here (§3a.2). It **surfaces** `SCOPE-DRIFT`, which is **computed in `architecture_tags.scope_drift()`** (§3a.3). The `R-H5` catch is **self-reported, with no instrument record** (§3a.1). | **KEEP** |
| **`contested`** | Found **the only spread greater than 1 in 49 sealed cards** — walked past by the producing round, that epic's close and an `index` run (`INSTRUMENT-LOG.toml:2608-2641`). RD-03's six groups are **`contested`'s, not `audit`'s**. **Nine recordings. ZERO adjudications, ever** (§3a.1). | **KEEP** |
| **`derive`** | **Nothing, and it cannot** — `architecture_tags.py:36-37`: *"It is not a gate. It refuses nothing about any artifact"*; `:600-602`: *"Every command prints; none of them refuses anything."* Subsumed by `audit_rh1_architecture`, which re-derives the same table plus `SCOPE-DRIFT`. | **CARRIED to the NEXT EPIC** — outside CA-03's `conflict_keys`, and CA-08 is chartered *"FILE FINDINGS, FIX NOTHING"* (`CA-03-DF-03`) |

### §3a. The four corrections, each re-derived

**1. "Eight adjudications since" — REFUTED. The number is ZERO.**
All **9** `[[contested]]` entries in `INSTRUMENT-LOG.toml` carry
`third_pass = "none"`, and `:2949` says it outright:

> `third_pass = "none"`. **Rule 5's remedy has never been applied to anything in
> this repository**, and running one here would be a measurement made during a
> measurement.

The correct word is **recordings**, not adjudications. `contested` **records** a
spread; nothing has ever adjudicated one. That strengthens rather than weakens
the case for keeping it — the recording is the entire product.

**2. "Four rounds' claims, two of them goal decisions" — REFUTED on both terms,
and it is CL-03's own sentence, which I repeated.**

Re-derived by diffing the `under_review` population across CL-03's own commit
`62a45d5` (the count moves `2 → 12`, so CL-03 parked exactly **10**):

```
CL-03's ten, by measured_at:   8878cd5 x6,  51fe73d x2,  2098d55 x2
distinct measured_at commits:  3          (not 4)
goal-* claims:                 4          (not 2)
  goal-port-reach-clause-1-pa06, goal-port-reach-clause-2-pa06,
  goal-cases-drive-ports-missed-at-pa06, goal-complexity-measurable-met
```

**The `10` is right. Both qualifiers were wrong**, and in opposite directions.
`CL-03/RESULT.md:249` reads *"Four rounds' claims, two of them goal decisions"*;
neither figure survives re-derivation from the ledger it describes.

**3. `SCOPE-DRIFT` is not `audit`'s catch.** It is computed in
`architecture_tags.scope_drift()` (`:557`) and `audit` **surfaces** it via
`module.scope_drift(rows, subjects)` at `score_tools.py:2928`. Crediting the
finding to `audit` credits the wrong instrument. Likewise **RD-03's six
contested groups are `contested`'s**, not `audit`'s.

**4. `check`'s "rejected a real card on rule 8" is a COUNTERFACTUAL, and is
withdrawn.** My source was `RM-05/RESULT.md:125-126` — itself a restatement. The
primary source is
`falsifiable-instruments/GOAL-scorecard-carries-a-delta/RESULT.md:190-193`:

> Under `scorecard_version 2` that exact card **is** rejected by `check`.

**Present-conditional tense, about a version-1 card, evaluated against a rule
that did not exist when it was written.** `check` never refused that card in
flight. **`check` is still kept** — on the second seal, which is primary and
which §3 shows is executed by `check` and nothing else.

**And the `R-H5` catch is self-reported, with no instrument record.** The only
evidence anywhere is the epic owner's own prose at
`references/eval_scorecard.md:562-569` — *"that first draft numbered it `R-H5`
and `audit` rejected it within the minute"* — restated since in two frozen
rubrics, `references/architecture_tags.md`, and now `score_tools.py:2840-2844`.
**No audit transcript, no violation line, no timestamp; the record gives a day,
not a minute.** Labelled here at the epic owner's own instruction: *"a
self-report laundered into doctrine through four restatements is worse than no
evidence, because it looks like evidence."*

### Why `derive` is not cut here

`examples/validation/scorecards/architecture_tags.py` is not in CA-03's
`conflict_keys`, whose only production key is `score_tools.py`. This epic's rule
is that a defect outside the slice is **deferred, not fixed**. It is also the file
that computes **standing result 2**, so the cut wants an owner who is measuring
that result rather than one passing through. The price to state is real and may
not be worth paying: `derive` is the only surface that prints the per-subject
derived-versus-declared table on its own, and `RD-04-DF-02` — three of five
fixtures with no effect surface, scored on D3 anyway — was surfaced by reading
exactly that output.

**AND IT IS NOT ROUTED TO `CA-08`. Epic owner's decision on review of PR #266,
and it is right:** `CA-08`'s plan objective is **"FILE FINDINGS, FIX NOTHING"**,
so routing the one cut this ticket found a case for to `CA-08` would land it on a
ticket chartered not to make it. **`CA-03-DF-03` is carried to the NEXT EPIC.**
No rescope is opened for it: this epic is already long, `derive` computes
standing result 2, and **cutting it late is precisely the risk
`GOAL-four-results-stand` exists to prevent.**

**So the honest summary of this ticket's cutting is: the one deletion it found a
case for is identified, justified, priced — and deliberately not made in this
epic.**

---

## 3. The trap, and it is in the charter

**"CL-01's second seal" is executed by `check`, not by `seal`.**

`version_history_problems` (`score_tools.py:747-808`, gated on
`SERVED_SEAL_FROM = 4`) is called from `cmd_check` at `:1183-1185` **and nowhere
else**. `cmd_seal` (`:3431-3470`) does `read_bytes()` and `hashlib.sha256`, and
nothing more.

The charter and three work orders defend `seal` by citing that catch. Anyone
who cut `check` on the strength of *"five checks passed a live defect"* would cut
the second seal while believing they had preserved it. Filed as `CA-03-DF-04`.

---

## 4. `SV-04-DF-05`'s own framing, tested against the record

The finding says five checks *"are not doing the job they claim."* **Two of the
five never claimed the job.** `seal` claims to hash bytes and refuse an edit to a
sealed card; `derive` claims, in its own file, to refuse nothing. Neither is
specified to notice an unregistered subject. Of the three that plausibly could
have, only `check` is proposed by the finding itself as the repair site — and
CA-03 declines that, because it is a gate, and because the defect is in the
command that **created** the unregistered card rather than in the commands that
read it afterwards.

**Five checks passing a live defect is not five failures. It is one failure, in
`scaffold`, observed five times.**

---

## 5. On "static gates catch nothing — seven epics, zero bugs"

The work order asked CA-03 to say whether its work bears on this. **It does, and
the claim is narrower than it reads** — but the case is **weaker than the first
version of this document said**, and the corrections in §3a all cut against me.

**What survives re-derivation:**

| catch | instrument | standing |
|---|---|---|
| 9 `SUPERSEDED-UNMARKED` on `SM-04` | `audit` | **holds** |
| 10 on `CL-03`, over 3 `measured_at` commits, 4 of them `goal-*` | `audit` | **holds** (qualifiers corrected) |
| the only spread > 1 in 49 cards; RD-03's six groups | `contested` | **holds** |
| `SCOPE-DRIFT` on two of four real `toolchain_removal` cards | **`architecture_tags.scope_drift()`**, surfaced by `audit` | **holds, re-attributed** |
| `registry-enumeration-coverage` catching `CA-05` | a repo tripwire | **holds** |
| the `R-H5` rejection at close | `audit`, **self-reported** | **weak — no instrument record** |
| `check` rejecting a card on rule 8 | — | **WITHDRAWN, counterfactual** |

**Five hold, one is weak, one is withdrawn.** The restatement stands — static
checks over subject code have caught zero bugs in seven epics; static checks over
this project's own **record** have caught real defects in several. **But one of
the seven citations I offered was not a catch at all, and another is the epic
owner's own unwitnessed sentence repeated four times.** A claim about evidence
quality that ships two bad citations has made its own point.

**This is not a licence to add a gate**, and CA-03 added none. Filed as
`CA-03-DF-05`, carried to `CA-08`, which decides it.

---

## 6. What CA-03 rejected

- **Making `check` refuse an unregistered card.** `SV-04-DF-05`'s own second
  suggestion, and a sixth gate. Rejected on the ticket's own instruction and on
  the charter's.
- **Cutting any of the five.** Four have a case; the fifth is out of scope.
- **Cutting `contested` for redundancy with `audit`'s R-H6.** The redundancy is
  real and is measured in §2, but `contested` alone carries `tier_split_of`, and
  `INSTRUMENT-LOG.toml:2916-2919` says a tier split is deliberately outside R-H6:
  *"a tier split is not a spread and R-H6 keeps them apart."* `contested` is also
  on the do-not-cut list.
- **Making `scaffold` refuse when it cannot register.** The cards are already
  written at that point; a refusal would either lose a measurement or lie about
  what happened.
- **Registering rounds scaffolded outside the scorecard root.** No reader could
  match the entry, and it would put unmatched paths into the one file that is all
  declaration.
