# SV-04 — predictions, sealed BEFORE the round runs

**Sealed in the commit that adds this file, before any judge was dispatched and
before any judge prompt was written.** The commit timestamp is the seal. Nothing
in the round directory carries a filled card at the moment this is committed:
all four `scorecard.json` files are `status: skeleton`.

Written by the SV-04 operator, who has read `HARVEST-CL-03.md`, both sealed
`close-the-loop-cl03-v5` cards and `references/scoring_validation.md`, and is
therefore **not blind**. The judges are, to each other, to which arm they hold,
and to this ticket's purpose.

---

## The design, so a reader can price the predictions

**Two arms, one artifact, one difference.**

| arm | packet | relationship to the record |
|---|---|---|
| `GL` | `FEATURE.md`, `tests/test_behavior.py`, `reference_ports/*` | **byte-identical to `CL-03`'s `blind/artifact_CL/`**, verified by `diff -r`. It is the concurrent NEGATIVE CONTROL. |
| `LG` | the same, **plus** `tests/test_journal_conformance.py` | differs from `GL` by exactly one added file, verified by `diff -r`. |

**`examples/validation/ab/reference_ports/` — the declared subject scope — is
byte-identical in both arms and byte-identical to the predecessor round.** The
treatment is not a change to the scored scope. It is a change to what the scored
scope's durable effect is *checked by*.

**The instrument is unchanged**: card version 5, `serve` = 6,281 bytes, 9 rungs,
served digest `sha256:2d7d4a0506d9b259`, `git diff` on
`references/eval_scorecard.md` empty. Same example (`toolchain_removal`), same
subject (`toolchain_fixture`), same declared boundary (`ports-and-adapters`),
same judge model as the predecessor round.

**Why there is a control arm at all.** The predecessor round's own two passes
scored **D2 = 2 and D2 = 0 on byte-identical bytes**. An instrument with that
much pass-to-pass spread cannot have a one-round before/after difference
attributed to a treatment. `GL` is what makes the comparison a measurement
rather than a story, and it is the debt the epic charter names in §4 — *a null is
the informative outcome.*

---

## What was actually built, and why

The defect is **`HARVEST-CL-03.md` class `A1`**, filed once as `RM-05-DF-05` and
consumed by nothing: *the real adapter's one distinguishing property is observed
by nothing.* It was re-reproduced by this ticket before anything was written:

```
shared 28-case suite, real wiring, FileJournal gutted to a list:  28 passed
                                   ledger.txt files created:      0  (28 at control)
```

`tests/test_journal_conformance.py` is 14 cases in one file. It exercises the two
adapters directly, and every assertion about the durable record is made by
`Path.read_text()` on the declared path rather than through `lines()`.

**It is justified by what it kills, not by what it might score.** Seven mutants,
measured before this file was sealed — four written for this ticket, **three
lifted unchanged from the fixture's own `seeded_faults.toml`** (`PA-M11`,
`PA-M12`, `PA-M13`):

| mutant | shared 28, real | shared 28, fake | conformance 14 |
|---|---|---|---|
| control | 28 pass | 28 pass | 14 pass |
| M1 — `FileJournal` gutted (the harvested class) | **28 pass** | **28 pass** | **5 fail** |
| M2 — record written to a path the port does not declare | **28 pass** | **28 pass** | **5 fail** |
| M3 — appends buffered until somebody reads | **28 pass** | **28 pass** | **4 fail** |
| M4 — the FAKE quietly starts writing a file | **28 pass** | **28 pass** | **1 fail** |
| `PA-M11` — real adapter drops CLOSE on read-back | 3 fail | 28 pass | 2 fail |
| `PA-M12` — same fault in the fake | 28 pass | 3 fail | 2 fail |
| `PA-M13` — fake truncates stored lines | 28 pass | 6 fail | 3 fail |

**M1–M4 survive the shared suite under both wirings — 56 of 56 green on each —
and die under the new file.** `PA-M11`/`PA-M12` need two wirings to be seen by
the shared suite and are seen by the new file in one run.

**Three of the 14 cases are killed by none of the seven mutants**:
`test_a_new_journal_reports_no_lines[FileJournal]`, the same `[InMemoryJournal]`,
and `test_reading_the_record_does_not_consume_it[FileJournal]`. They are named
here rather than quietly kept.

---

## The predictions

Each is falsifiable, and each says what would refute it.

**`P1` — D3 moves on the treatment arm.** Both predecessor cards scored `D3 = 3`
and both quoted the version 5 caveat — *"if the only observer of the effect the
port exists for is the adapter that wrote it, say so and take 3"* — as the
reason. That condition is false of arm `LG`. **Prediction: at least one `LG` pass
scores `D3 = 4`.** REFUTED IF both `LG` passes score 3 or lower.

**`P2` — and it may legitimately fail, for a reason already filed.**
`CL-03-DF-02` says anchor 4's *"the same cases passing against both"* structurally
excludes a durability case, because such a case must fail against the fake.
**Prediction: at least one `LG` pass reasons explicitly about that tension**,
whichever way it then scores. REFUTED IF no `LG` card mentions it.

**`P3` — the control does NOT move.** **Prediction: both `GL` passes score
`D3 = 3`**, reproducing the predecessor. REFUTED IF any `GL` pass scores 4 —
which would mean `P1`'s movement, if it happens, is judge variance and not the
file. **This is the prediction that decides whether the round measured anything.**

**`P4` — the note is where the movement is cleanest.** **Prediction: at least one
`LG` N-D1 note reports the durability class as CAUGHT with a denominator, where
both predecessor notes reported it missed at 28/28** ("all 28 cases passed",
"class one — DURABILITY"). REFUTED IF both `LG` notes still name durability as a
demonstrably missed class without qualification.

**`P5` — D2 is unstable on identical bytes, again.** The scored scope is
byte-identical across all four cards and across the predecessor round.
**Prediction: the four D2 scores are not all equal, and at least one pair differs
by more than 1** (`contested` under scoring rule 5). REFUTED IF all four agree.
This is a prediction about the instrument, not about the artifact, and it is the
reason no D2 movement in this round may be read as a treatment effect.

**`P6` — a judge finds a hole in the new file.** **Prediction: at least one `LG`
card names a specific weakness in `test_journal_conformance.py`** — a case that
cannot fail, a class it still misses, or the fact that it never constructs a
`QuotaLedger`. REFUTED IF all four cards treat it as sound.

**`P7` — the surface metric does not move.** **Prediction: `serve | wc -c` is
6,281 and the rung count is 9 at the end of this ticket, and the served digest is
still `sha256:2d7d4a0506d9b259`.** REFUTED IF any of the three changes. No card
change is intended; if one turns out to be required, `SV-07-DF-01` prices it at a
version bump for a note as much as for a rung, and that becomes a finding rather
than a free move.

---

## What this round CANNOT settle, stated before it runs

- **One artifact, one feature, two judges per arm.** `n = 2` per cell.
- **The operator is not blind** and wrote both the mutants and the new file.
- **The control arm is concurrent, not paired**: `GL` and `LG` are judged by
  different agent instances, so `P3` bounds judge variance rather than
  eliminating it.
- **A judge that reads `test_journal_conformance.py`'s own docstring is being
  handed the defect the file was written for.** That is a disclosure, not a
  discovery, and any `LG` card that reports the durability hole is reporting
  something the packet told it. `F3` in `HARVEST-CL-03.md` is the class; this
  round adds an instance and says so in advance. **The `GL` arm is not exposed to
  it, which is the only reason the pair means anything.**
- **Nothing here decides whether the case belongs in the shared contract suite.**
  It deliberately does not go there: `tests/test_behavior.py` is the A/B's shared
  requirement and an arm-visible change to it would make two arms incomparable.
