# FI-04 — narrative ledger

**A fixture whose arms CAN diverge, and an honest answer on generator vs suite.**

`model_delta_expectation: none expected`, and the measured delta is **zero**. No
TLA+ model, `.cfg`, manifest or production module changed. `effects` was not
touched, so `surface_cost_rule` has nothing to price: **no modelled surface was
added, and the state space is byte-identical** — TLC explores the same 2,649
states before and after. Everything below is the A/B fixture and its
instruments.

---

## 1. The decision, which is the ticket's headline

**Both, and each in one specific part.** Full reasoning:
`examples/validation/ab/eval/DECISION-fixture-or-goal.md`.

**`GOAL-cases-drive-ports`'s METRIC is retired** — *"the count of comparable
cells where the arms AGREE"*. Not the question; the metric. Two clauses were
already measured:

- **E1** — the instrument is the same on every arm. A corpus is a pure function
  of `(model, manifest, flags)` and the A/B holds one model and one manifest
  across arms by design, for the stated reason that otherwise a difference
  between arms could be a difference between their models.
- **E2** — `AD-F1` measured the three arms' **mutated** trees observationally
  identical on **10 of 11 rows**, over 28,561 command sequences.

And the corollary is what actually kills it: the catalogue holds the `semantic`
equal across arms, so a fault that satisfies the comparability rule is one both
arms have somewhere. **Any fault that could move the metric is by construction
not comparable.** The metric forbids its own answer. A third `MISSED` against it
would have been arithmetic.

**Replacement, and its null is not entailed:** *for one semantic fault, per arm,
the number of DISTINCT COMPOSITIONS under which one shared instrument returns
different verdicts.* Arm A **0** by construction, arm C **0** by a recorded
decision, arm B **1** measured. The same run proves it can come out zero on a
hexagonal arm: `FI-M15`, in arm B's **domain**, gives the same verdict under both
of arm B's compositions.

**The fixture is amended** in the one place the entailment leaves open — the
`--wiring` swap, which does not read the model and is therefore the only
instrument here that is a function of the arm's architecture.

---

## 2. What was measured

One semantic — *"the ledger's read-back silently drops every line beginning
`CLOSE`"* — re-anchored **by the property, not by the bytes**, onto four sites
whose `find` strings share nothing. Predictions sealed at `4697687`, before the
driver was pointed at any row.

| row | arm | homes | action-bound | `:real` | `:fake` | suite-real | suite-fake |
|---|---|---|---|---|---|---|---|
| `FI-M18` | A | 1 | KILLED | KILLED | **KILLED** | KILLED | *no such column* |
| `FI-M19` | C | 1 | KILLED | KILLED | **KILLED** | KILLED | *no such column* |
| `FI-M16` | B | 2, wired | KILLED | KILLED | **SURVIVED** | KILLED | SURVIVED |
| `FI-M17` | B | 2, unwired | SURVIVED | SURVIVED | **KILLED** | SURVIVED | KILLED |

**The divergence:** `corpus-port-swap:fake`, comparable row — arm A `KILLED`,
arm C `KILLED`, **arm B `SURVIVED`**. All three corpus columns executed **1,543
of 1,855 cases and 352 accepting `CloseTenant`** on every arm, so no `SURVIVED`
above is a reach problem.

**The architectural reason is measured, not asserted.** `divergence.py` computes
the composition count from the runs: two columns with identical evidence on every
row ran the same program. Arms A and C **1**, arm B **2**. `AD-F6` mechanised.

**Arm C is the check PA-04 asked for and it comes down on PA-04's side** — a
third independent re-anchoring, length-matched to arm B, zero architectural
vocabulary, landing on **arm A's** verdict.

**Read which way it points.** Swapping in arm B's own fake took a real durable
fault off the executed path and **no instrument said so**. `M09`'s direction,
reproduced with a content fault, on a class no arm had ever carried.

**`FI-M17` closes `PA-06-DF-04`**: the adapter-internal class now sits on an
artifact a prompt produced rather than on a fixture the epic authored. It has no
counterpart on A or C, and that is reported as a structural asymmetry rather
than as a `SURVIVED`.

**Controls, read out of the artifacts and never from an exit code**
(`FI-02-DF-02`): `control_red == []` and `unmutated_control_failed == []` on all
three arms; arm B additionally carries `FI-M15`, **the only in-region positive
control on any arm**, GREEN. Arm B's `SURVIVED` cells are counts, not floors.

**8 of 8 sealed predictions, four of them negatives.** Stated as weaker than it
looks: the rows were authored by the ticket that measured them (`FI-04-DF-03`).

---

## 3. Generator against suite — the honest answer, and it is not the one on file

The set comparison nobody had run (`generator_vs_suite.py`, reading only sealed
evidence):

| catalogue | authored by | generated union | suite | verdict |
|---|---|---|---|---|
| seeded / arm A | the fixture's own author | 10 of 11 | 10 of 11 | **IDENTICAL SETS** |
| seeded / arm B | the fixture's own author | 10 of 11 | 10 of 11 | **IDENTICAL SETS** |
| **blind / arm A** | **an independent blind agent** | 11 of 15 | 11 of 15 | **COMPLEMENTARY** — `BA-P11` generated-only, `BA-P05` suite-only |
| **blind / arm B** | **an independent blind agent** | 10 of 15 | 10 of 15 | **COMPLEMENTARY** — `BA-Q11` generated-only, `BA-Q05` suite-only |
| ports / `reference_ports` | the fixture's own author | 3 of 5 | 5 of 5 | **SUITE STRICTLY DOMINATES** |

`BA-P11`/`BA-Q11` is `identity_reuse`: ids numbered from the count of live
reservations, so an id is reissued once its predecessor resolves and a later
commit can silently overwrite a live hold. Four generated instruments kill it.
**The hand-written suite misses it, on both arms.**

**So the sentence three epics have carried — *"the generated corpus is worse than
a suite a competent engineer writes in an afternoon"* — is a property of WHO
WROTE THE CATALOGUE.** It holds where the catalogue author wrote the suite and it
**reverses into a tie with a kill each way** on the only catalogue that controls
for that. Filed as `FI-04-DF-01`. The arithmetic has been re-derivable from
sealed evidence since `b3a0199`; the round that produced the numbers reported the
union **count** and not the **sets**, and a union count cannot tell "the same
eleven" from "eleven each, differing by one in each direction".

**The answer: keep funding the corpus. Stop funding the `[ports.*]` binding
machinery on this evidence.** They are different claims and neither softens the
other:

- The corpus family has a demonstrated complementary kill against the suite on
  independently authored faults, and the negative corpus holds guard relaxation
  at **3 of 3** (seeded) and **5 of 5** (fresh) — a class that measured 0 on
  every instrument before it existed. Per-port generation reaches **83.2%**
  executable against the whole view's **8.66%**.
- The port machinery has **zero unique kills anywhere**, is **strictly dominated**
  by `suite-fake` on `reference_ports` (3 of 5 against 5 of 5), and on FI-04's own
  new rows decides **exactly** what the two suite columns decide — the divergence
  is produced by the four-line composition point, not by the `[ports.*]` table.

And note which piece carried the one kill that saves the generator: `BA-P11` dies
to `corpus-whole`, `corpus-slice-res`, `map-silent` and `map-checking` — the
oldest and least-defended parts — and to **neither** the negative corpus nor the
port corpus, the two things the last two epics were spent on.

---

## 4. What this does NOT show

- It does **not** show ported code is validated differently in general. It shows
  **this fixture can diverge**, which is what the goal asked, and the mutants and
  the fixture still share an author (`FI-04-DF-03`).
- It does **not** rescue the port machinery. See §3.
- It does **not** re-open `GOAL-cases-drive-ports`'s 64 of 64. Those numbers are
  correct; what is wrong is reading them as evidence about detection.
- It does **not** rest on any length or prompt claim. `FI-05-DF-02` records that
  arms A and B have no dispatch record, so arm B's 105 unique lines is a fact
  about a file on disk. FI-04 cites arm C's *architectural vocabulary* count and
  its author's recorded rejection, never a length ratio.

---

## 5. What I REJECTED

1. **Generating a per-arm corpus from a per-arm manifest.** The cleanest way to
   break `E1`: let each arm's real architecture drive its own `effects`
   declaration, so a ported arm gets a port corpus and a flat one does not.
   Rejected because it breaks the fixture's load-bearing control — one model and
   one manifest for both arms — and a `D1` difference between arms would stop
   being attributable. It would also be a **modelled-surface addition** priced
   before the fact under `surface_cost_rule` and I could not state what it buys
   beyond what the swap already gives.
2. **Seeding `FI-M17`'s "fake drifts from real" semantic onto arms A and C by
   nearest bytes.** It would have produced a fourth comparable row and a bigger
   divergence table. It is exactly the re-anchoring artefact `PA-06-DF-08` is
   about, and the catalogue row now forbids it in writing.
3. **Declaring a `suite-fake` column on arms A and C.** It would have run
   `suite-real` twice and reported the duplicate as an independent measurement —
   `AD-F6` with the sign flipped. Reported as `NOT_APPLICABLE` instead.
4. **Retiring `GOAL-cases-drive-ports` outright.** The question is good; only the
   metric is unanswerable. Retiring the question would have thrown away the one
   thing the epic has that is worth measuring.
5. **Keeping the metric and widening the comparable set to 10 of 11 rows.**
   `AD-F2` supports 80 of 80. It makes the null *wider*, not narrower, and it
   does not touch the corollary.
6. **Fixing `run_port_swap.py`.** Two defects met in this ticket —
   `FI-02-DF-02`'s exit code and `FI-04-DF-02`'s vacuous no-violation sentence —
   and both were filed, not fixed. A fix during a measurement destroys the
   measurement and FI-04's own cells would be the first casualty. `run_arm_swap.py`
   re-reads the artifact instead and returns nonzero **for its own runs only**.
7. **Extending `run_controls.py` so it could measure a ported tree.**
   `FI-01-DF-01` is blocking and its suggested fix is known. Repairing the driver
   that decides kill tables, in the ticket quoting kill tables, is two instrument
   changes in one commit.
8. **Adding a `StateGraphPortInteraction` assertion.** PA-03 rejected it for want
   of an adapter; PA-04 rejected it because it would confound the divergence with
   a changed assertion. Rejected a third time for PA-04's reason: FI-04's whole
   result is that the only variable is the binding.
9. **Re-running the blind-author channel against the port columns.** The single
   most valuable follow-up and the honest control for §3's remaining half — and a
   channel dispatch whose prompt should be reviewable before it runs. Named in
   `FI-04-DF-03`'s `suggested_fix` rather than done half-way here.
10. **Reporting a kill rate anywhere.** Per class, per arm, with executable
    counts beside every number, and the arm-B rows read as a difference.

---

## 6. Findings filed, not fixed

`FI-04-DF-01` (major) — the dominance sentence is a property of the catalogue's
author and reverses on the blind catalogue; re-derivable since `b3a0199`.

`FI-04-DF-02` (minor) — `run_port_swap.py` prints "no control's declared role was
violated" over a run containing no control at all. Adjacent to `FI-02-DF-02` and
a different defect.

`FI-04-DF-03` (minor) — self-audit: FI-04 wrote the mutants it measured, and the
first arm-C run was `CONTROL_RED` from a missing PYTHONPATH — the instrument
behaving correctly, and the exact condition under which the *other* driver
produces a false green instead.

---

## 7. Acceptance

```
uv run --with pytest --with pyyaml python -m pytest tests -q
1 failed, 1234 passed
```

The one failure is `tests/test_code_complexity.py::test_nothing_executable_reads_this_instrument`
— `PA-06-DF-05`, carried out of the predecessor epic as issue #147. **Red on the
parent `51fe73d` with the identical assertion**, verified by `git archive`. The
owner has since confirmed it is a **false positive**: it fires on a docstring
*mention* in `build_evidence_packets.py`, and FI-02 ships the replacement.

Parent-commit evidence for the new behaviour, with `divergence.py` and
`generator_vs_suite.py` copied into the archive so the failures are about the
FIXTURE rather than about the code being new:

```
git archive 51fe73d -> 16 failed, 3 passed
```

The three that pass are the two synthetic R1 demonstrations and
`test_the_dominance_result_is_a_property_of_who_wrote_the_catalogue`, whose
passing on the parent **is** `FI-04-DF-01`.
