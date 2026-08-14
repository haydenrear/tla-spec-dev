# `CA-07` close narrative

**Ticket**: consume one finding this epic produced into the program, as a TLA+
action or an adapter conformance case. **Subject named by the epic owner at
`schedule_revision 2`: `CA-06-DF-02`.**

**The one-line summary**: the finding is consumed as an adapter conformance
case that goes red on the defect and green after; **the constraint `CA-06` gave
for not fixing it does not bind, and that is checkable rather than argued**;
and consuming it exposed that the mechanism's real yield on a real subject is
**11 cases executed, 11 failing, 5 of them naming a genuine disagreement
between the model and the program**.

---

## 1. Was it consumed, or only routed?

`CA-05` built the disposition requirement and measured that **its own
instrument cannot tell consumption from routing** (`CA-05-DF-03`). So the
question has to be answered by artifacts, not by a field.

**It is consumption, and here is what makes it checkable by someone who does
not trust this document.** `14fbb10` is the epic tip this branch was cut from and `HEAD` is the ticket commit:

```bash
git checkout 14fbb10 -- scripts/generate_cases_from_tlc_dump.py \
  && uv run --with pytest --with pyyaml -m pytest tests/test_negative_corpus_adapter_conformance.py -q
#   3 failed, 2 passed   -- KeyError: 'account' x7, KeyError: 'order' x2

git checkout HEAD    -- scripts/generate_cases_from_tlc_dump.py \
  && uv run --with pytest --with pyyaml -m pytest tests/test_negative_corpus_adapter_conformance.py -q
#   5 passed
```

The artifact is `tests/test_negative_corpus_adapter_conformance.py`: **222
lines, five cases, and it did not exist at `14fbb10`.** Transcripts of both
sides are sealed at `regression-red.txt` and `regression-green.txt`.

**What makes it a *conformance* case rather than a unit test**, and this is the
load-bearing design decision: the defect is a disagreement between **two
artifacts** — what the corpus emits and what the adapter reads — and only one
of them lives in `scripts/`. **A test of the generator alone is green on either
keying, because either keying is internally consistent.** That is how this
survived three epics. So the central assertion compares the generator's output
against **the corpus already checked in** at
`examples/distributed_history/specs/generated/spec_unit/`, and a second case
hands the emitted arguments to the adapter classes that example's own
`case_adapters.toml` names, through the `run` entry point the shipped runner
uses. **Neither side of that comparison is written in the test.**

**The honest discount.** One input is transcribed: the pair of reachable states
the cases are built at, because TLC produces a state graph and a unit test may
not run one. Both are the model's own — `InternalInit` and the state one
`CreateAccount` later — a fifth case fails if the module's variables move
underneath them, and the two states reproduce **all four** refusal reasons the
full 11-case TLC run found. It is a smaller discount than a fixture and it is
not zero.

---

## 2. The constraint `CA-06` named, and why it does not bind

`CA-06` filed this finding and deliberately did not fix it:

> *"Re-keying the arguments CHANGES WHAT A CORPUS CONTAINS … the same rule
> forbids `CA-06` changing the keys of a corpus under the one fixture whose
> sealed kill tables are quoted throughout this programme."*

**Right as a caution, and its premise was never checked.** The names the
positive corpus uses are not recovered from a state pair at all — they are read
out of the module's own action-marker record. **`QuotaLedger` declares no
action marker.** It therefore declares no argument names, has nothing to
re-key, and cannot move.

**Measured, both keyings, `diff -r`:** 118 cases either side; the only
difference is the scratch directory recorded in `case_coverage.json`.
`quota-ledger-corpus-unchanged.txt`. **No sealed cell can move**, and the fix is
inert on every model that predates it by construction — it changes only models
that told the generator their argument names.

**So the answer to "can this be landed without disturbing sealed tables" is
yes**, and the reason it looked otherwise is that the row's `suggested_fix`
named the wrong mechanism. `CA-07-DF-01`: an `ActionRecipe` is keyed by the
**formal** names and cannot supply `account`. A ticket that followed the
suggested fix literally would have got nowhere. **This is the first time a
`suggested_fix` on this 255-row ledger has been executed rather than quoted, and
it was wrong on its central noun.**

---

## 3. The second face nobody read

The negative pass runs a cross-check before emitting anything — *"the corpus
never states something the checker itself has just been shown to get wrong."*
It compares `set(params_for_case(...))` against `set(signature.params)`:
**declared names against formal names.** On every model that declares an action
marker the sets never matched, every edge hit `continue`, and the check
examined nothing.

**`CA-06`'s own sealed report prints the zero**: `cross-check: 0 ENABLED
edge(s)` over a dump holding 141 of them. Repaired here, with the same
`declared_param_names` inverted:

| | `distributed_history` | `QuotaLedger` |
|---|---:|---:|
| before | **0** | 4,028 |
| after | **141**, 0 disagreed | 4,028 |

**0 of 141 disagreed, so no action was suppressed and no corpus shrank.** This
is `CA-06-DF-01`'s shape a second time: a mechanism measured only on the one
model where its bug is invisible.

---

## 4. What consuming it exposed, filed and not fixed

With the keying repaired the 11 cases execute — and **all 11 still fail**,
now on the output comparison. **Reporting that as a success would be false.**
The failures split two ways (`CA-07-DF-02`):

- **6 of 11 are a reporting gap.** `AddCartItem` ×2 and `Checkout` ×4 refuse
  correctly (`404 account_not_found`, `409 empty_cart`); the adapter returns
  `{status, body}` and the corpus expects a `StateGraphRejection`. No adapter
  outside the `ab` fixture has ever had a rejection contract.
- **5 of 11 are a behaviour divergence.** `CreateAccount` returns **201** on an
  account that already exists (`domain.py:88`, `insert or ignore`) against a
  model that guards `a \notin accounts`; `ProjectOrder` returns **200
  `{"processed": 0}`** for an order not in the outbox against a model that
  guards `o \in outbox`. **The implementation does not refuse.**

**Whether the model over-constrains or the implementation under-refuses is not
decided here.** Both readings are live — an idempotent create is a defensible
design. Filed for `CA-08`, not repaired: *file findings, fix nothing during a
measurement*, and repairing it would mean choosing between changing
`Internal.tla` and changing a real example's implementation, which is an owner
decision on a surface this ticket's conflict keys do not name.

**And the limit on the claim, because the oracle cannot support more**: since
no adapter here carries a rejection contract at all, this run **cannot
mechanically separate** "refuses but cannot say so" from "does not refuse".
The split was read off the status codes and confirmed against `domain.py` **by
hand**.

---

## 5. `MF-020`, stated because it governs this ticket harder than any other

**The regression asserts that the adapter can READ the arguments the corpus
names. It does not assert that a negative case passes.** That omission is
deliberate. Making the 11 pass requires changing the adapters or the model —
tuning the subject to the instrument, on a defect found while running it.

**No score was moved and none was sought.** `SV-04`'s precedent carries its
caveat and this ticket did not invoke it: no judged round was run, no scorecard
was produced, and the card did not change (`6,281`,
`sha256:2d7d4a0506d9b259`). The local signal declared for
`GOAL-consumption-obligatory` is *"the new … adapter conformance case failing
on the defect and passing after"*, and that is exactly what was measured —
3 failed → 5 passed.

**One `MF-020` exposure disclosed rather than hidden**: the two states the
regression builds at were chosen before the fix, to cover every action the
model lets the generator negate, and the coverage claim (*all four refusal
reasons*) was checked afterwards. The states were **not** selected to make any
particular case fail.

---

## 6. Scope, declared rather than left for a reviewer

**This ticket edited `scripts/generate_cases_from_tlc_dump.py`, and its plan
entry declares `conflict_keys.production: []`.** `CA-07` was reserved at
planning with an unknown subject; the `schedule_revision 2` amendment named
`CA-06-DF-02`, whose own `surface.production` is that file, and **rewrote the
objective without re-deriving the scope**. There is no way to consume the
finding without touching it.

**No actual collision occurred** — `CA-06` owns that file and is merged, `CA-08`
is wave 5 and depends on this ticket, nothing else was in flight. **The
declaration was stale, not violated in spirit.** Filed as `CA-07-DF-03`, with
the fix being to re-derive a reserved ticket's conflict keys from the named
finding's own `surface` block at triage. **This ticket did not edit its own
conflict keys**: a ticket that widened its declared scope to match what it had
already done would leave no record that the departure happened.

---

## 7. Suite

**Baseline established by running it, not recalled**: `8 failed, 1481 passed`
at `14fbb10` in this worktree (`pytest-baseline.txt`), item-for-item:

```
test_architecture_tags.py::test_the_same_tag_control_holds                       DELIBERATE (RM-06-DF-01)
test_goal_baseline_is_a_card.py::...judged_baseline_cannot_be_re_opened          CA-00-DF-02
test_instrument_demonstrations.py::test_every_declared_path_exists               inherited
test_instrument_demonstrations.py::test_every_fast_demonstration_reproduces      CA-00-DF-01
test_source_citations.py::...[specs/current/spec_manifest.yaml]                  inherited
test_source_citations.py::...[specs/desired_program_model/spec_manifest.yaml]    inherited
test_source_citations.py::...[specs/program_model/spec_manifest.yaml]            inherited
test_ticket_retirement.py::...delivered_plan_has_matching_close_receipts         inherited
```

**At the head this ticket closed: `8 failed, 1490 passed`**
(`pytest-after.txt`), and the failure set is **identical item for item**:

```bash
$ diff <(grep ^FAILED pytest-baseline.txt | sort) <(grep ^FAILED pytest-after.txt | sort)
        (no output)
```

**+9 passing**: the 5 cases of the new conformance file, plus 4 elsewhere that
the fix unblocked.

**Not one of the 8 was repaired.** One new red appeared during the work and was
declared with its cause and fixed: the line-number citation of `CA-07-DF-04`.
The three manifest citation reds were checked to be **identical** before and
after this branch's edit, by re-running the test on both trees and diffing the
15 stale citations it reports.

**Measurement point, stated exactly.** That run is at the **pre-close** head.
What lands after it is the plan's `status: planned -> done` flip and the close
receipt, read only by `test_ticket_retirement` — already one of the 8 inherited
reds either way. Its verdict at the closed head is recorded separately in
`pytest-ticket-retirement-after-close.txt`.

---

## 8. What was refused

- **Making the 11 negative cases pass.** `MF-020`, and §4's finding is worth
  more than a green run.
- **Giving the shipped adapters a rejection contract.** It would repair the
  thing this ticket just measured, it touches an example's adapters, and the 6
  correct refusals are the demonstrated failing input a later ticket needs for
  it (`R1`).
- **Changing `Internal.tla` to stop guarding what the implementation does not
  enforce.** A specification decision with a TLC budget, not a ticket's to take
  while measuring.
- **Editing this ticket's own `conflict_keys` to cover the file it edited.**
  §6.
- **Sweeping the repository's line-number self-citations onto content anchors.**
  `CA-06` already argued for it; a ticket consuming one finding should not carry
  a repository-wide sweep. Suggested subtractively on `CA-07-DF-04`.
- **Re-running any judged round, or quoting `SV-04`'s D3 movement as support.**
  No judge ran; `GOAL-blind-dispatch`'s `local_signal` is `N/A` for this ticket
  and stayed that way.
- **Fixing `CA-06-DF-05`'s one-sided corpus gate**, which prints `PASS` over an
  empty corpus and would have printed it over this defect too. Carried to
  `CA-08` by `CA-06`; not reopened here.

---

## 9. Evidence

All under `specs/results/scorecards/cut-the-apparatus/CA-07/`:

| file | what it carries |
|---|---|
| `RESULTS.md` | the measurement, the two faces of the defect, what the fix does and does not buy |
| `PRICE-TABLE.md` | lines per surface, the card, what the tree can now do |
| `regression-red.txt` / `regression-green.txt` | `3 failed, 2 passed` → `5 passed` |
| `negative-corpus-execution-before.txt` / `-after.txt` | 11 `KeyError` → 11 executed, 11 output mismatches, with the status codes |
| `quota-ledger-corpus-unchanged.txt` | the sealed fixture on both keyings, `diff -r` |
| `line-counts.txt` | per-surface counts and the card |
| `pytest-baseline.txt` / `pytest-after.txt` | the suite either side |
| `disposition.txt` | `DISPOSED ticket CA-07: 4 findings, all three clauses hold` |

**Findings**: `CA-07-DF-01` (settled), `CA-07-DF-02` (carried, `CA-08`),
`CA-07-DF-03` (carried, `CA-08`), `CA-07-DF-04` (carried, `CA-08`). Four rows,
all disposed, `scripts/disposition.py --ticket CA-07` exit 0. `CA-06-DF-02`
moved `carried` → **`consumed`**.

**The consumption count, per `denominator_rule`.** `CA-06-DF-02` is a **ledger
row filed by this epic**, not one of `HARVEST-CL-03`'s 41 classes — so **the
harvest numerator does not move and stays 1 of 41**. What moves is the ledger's
own terminal-disposition count: `consumed` goes **2 → 3** over a ledger that
grew **251 → 255 rows** in the same commit. **The numerator rose by one and the
denominator rose by four**, and quoting either number without the other
overstates the loop.
