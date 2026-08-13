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

---

## 2. The five, decided

| check | what it has caught | verdict |
|---|---|---|
| **`check`** | Rejected a real card on rule 8 (`RM-05/RESULT.md:125-127`). **And it executes CL-01's second seal** — see §3. | **KEEP** |
| **`seal`** | No recorded firing of its own refusal in eight epics. But R-H4 is on the do-not-cut list and **has nothing to verify without the digests `seal` writes**. | **KEEP**, with the blind spot recorded (`CA-03-DF-04`) |
| **`audit`** | The strongest record of the five: 9 `SUPERSEDED-UNMARKED` on `SM-04`, 10 on `CL-03` over four rounds' claims, the **epic owner's own unexecuted `R-H5` rejected at close within the minute**, `SCOPE-DRIFT` on two of four real `toolchain_removal` cards, and RD-03's six unrecorded contested groups. | **KEEP** |
| **`contested`** | Found **the only spread greater than 1 in 49 sealed cards** — walked past by the producing round, that epic's close and an `index` run (`INSTRUMENT-LOG.toml:2608-2641`). Eight adjudications since. | **KEEP** |
| **`derive`** | **Nothing, and it cannot** — `architecture_tags.py:36-37`: *"It is not a gate. It refuses nothing about any artifact"*; `:600-602`: *"Every command prints; none of them refuses anything."* Subsumed by `audit_rh1_architecture`, which re-derives the same table plus `SCOPE-DRIFT`. | **CARRIED to `CA-08`** — outside CA-03's `conflict_keys` (`CA-03-DF-03`) |

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
the claim is narrower than it reads.** Over subject code the claim stands. Over
this project's own record, static checks have caught real defects and changed
outcomes in at least five epics — the six citations are in §2's `audit`,
`check` and `contested` rows, and this epic adds the
`registry-enumeration-coverage` tripwire catching `CA-05`.

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
