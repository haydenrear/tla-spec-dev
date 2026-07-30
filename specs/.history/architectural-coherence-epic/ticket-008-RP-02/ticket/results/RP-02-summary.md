# RP-02 — oracle leakage, and an audit that argued with its own corpus

Two defects, one root shape: **a number that was never measured, published as
if it had been.** The generator said it recovered nothing, so a fixture adapter
quietly went and got the answer from the oracle; the audit said everything was
recoverable, over a corpus that carried nothing.

## What changed

**1. A fourth recovery mechanism, `set-membership`.**
For an action whose body contains `v' = v \cup {i}` or `v' = v \ {i}`, the
argument is the element that ENTERED or LEFT that set. Every such conjunct of
the action is kept as an independent **witness** and they are cross-checked:
`Accept(i)` is witnessed by both `inbox` (left) and `accepted` (entered), and
the recovery only commits when every applicable witness names the same element.

The soundness bound is stated in the code and enforced by tests, not hoped for.
Recovery returns `UNCHECKED` when a witness sees two or more elements move at
once (which one was the argument?), when witnesses disagree (a conditional body
took a branch the recipe cannot see), or when neither side is a set. It never
guesses, and no case is ever dropped for failing to recover.

Preference order is unchanged in spirit — the mechanism that reads the least of
the after-state wins — with `set-membership` slotted between `except-index` and
`written-through`. It spends one observation, "which element moved in `v`", and
the audit now names that price per action under
`Observations the recovery consumed`. It does **not** make the whole
after-value of `v` tautological, so it is deliberately kept out of
`unavailable_checks`, which means exactly that.

**2. The audit is rendered from the corpus it audits.**
`render_audit(recipes)` became `render_audit(recipes, measurement)`, where the
measurement is counted case by case off the corpus that was just written. The
sentence

> Every parameter of every action is recoverable from its state pair.

is gone, and nine tests assert the exact string can never come back. In its
place: an unmeasured audit declares itself **STATIC** and makes no claim about
any corpus; an empty corpus makes no claim; a parameter the run failed to
recover on every case is **UNRECOVERABLE ON THIS CORPUS whatever the syntax
promised**; a partially failing run is reported per class as PARTIAL with both
counts; actions no case entered are *not exercised* rather than counted as
either a success or a failure; and a fully successful run gets a claim scoped
to the run and to the actions it entered.

One extra dishonesty surfaced while wiring the measurement in. `reminder_worker`
— the run that printed the universal claim next to `0/38 cases carry arguments`
— has **no formal parameters at all**. The old sentence was a vacuous universal
over an empty set, and its seven cases carry arguments the model states through
its own action marker. Those are now reported as **model-declared, not
recovered**, and this module takes no credit for them.

**3. The ex4 adapter no longer reads `case.after`.**
`_argument(case)` reads `case.input.params['i']`. An argument that did not
recover arrives as a non-`str` sentinel and is a **hard failure**, not a
fallback: an adapter that degraded to a no-op would report a green case for a
transition it never executed. The five `select()` overrides that named which
variables to diff are gone with the diff.

## What it bought, measured

| | before | after |
|---|---|---|
| parameters recovered on ex4 | 0 of 5 | **5 of 5** |
| cases carrying a real argument | 0 of 330 | **330 of 330** |
| `cases.py` sha256 | `33e07e0d…` | `94418905…`, byte-identical across two regenerations |
| ARM A / ARM B control | green | green, 330 cases, exit 0 |
| 12-mutant catalog | see below | **identical, cell for cell** |

## What it did not buy — the honest negative

Guard relaxation is **still 0 of 3** killed by the corpus and 3 of 3 by the
hand-written suite. The full 12-mutant catalog was re-run on BOTH instruments
and not one cell moved.

The reason is counted, not asserted:

```
action      cases  arg ENABLED  arg REJECTED
TOTAL         330          330             0
```

Every recovered argument is an argument the guard **accepts**. A relaxed guard
says yes where the model says no; the corpus never asks it that question. 220
refusable argument/before-state pairs exist in this state space and a TLC state
graph can emit none of them, because there is no edge for a transition that did
not fire.

EV-02 named two compounding causes — the structural one (enabled edges only)
and oracle leakage. **RP-02 removes the leakage half and the class does not
move.** That is the value of the negative: the whole of the remaining failure
is now attributable to the structural half, which is what the next epic needs
to know before it spends anything on this.

## A claim in the fixture that turned out to be false

`seeded_faults.toml` and the ex4 README both state that a fault whose only
symptom is *acting on the wrong item* is a class this instrument **cannot
measure**, and decline to seed one on that basis. RP-02 seeded two. Both are
**KILLED — on the pre-fix instrument as well as the post-fix one.** The old
adapter was handed the *correct* argument by the diff and passed it in, so a
program that then ignored it still diverged in the projected after-state.

The prediction was never run. The leak's real cost was never kill power on this
fixture: it was that the argument was not in the artifact, nothing audited it,
the claim "the corpus tests arguments" was unfalsifiable, and the MF-028
vacuity trap (derive from `case.after`, then check against `case.after`) was
live in a file nobody re-read. Both artifacts are amended in place. **No
answer-key row is altered** — an answer key is a record, and the pre-RP-02
audit is kept beside the new one as `param_recovery_audit_pre_rp02.md` rather
than overwritten.

## Can a generated corpus ever catch guard relaxation?

Not by recovering parameters better, and not from the state graph alone. The
state graph is a record of what the model *did*; a guard is a claim about what
it *refuses*, and refusals leave no edge. Catching one needs a corpus that
carries **rejected inputs** — a case that says "call `Accept(i2)` in a state
where `i2 \notin inbox` and require a refusal". Everything needed to emit those
now exists: the argument domain is known, the guard is in the module the
generator already parses, and the recovered argument proves the adapter can be
driven by a stated argument rather than a derived one. What does not exist is a
*negative* case shape — expected-refusal, with its own oracle — and an
adapter contract that distinguishes "refused correctly" from "did nothing".
That is a corpus-generation ticket, not a parameter-recovery one, and it is the
single highest-value thing this measurement points at.

## Zero model delta

`diff -r specs/tickets/RP-02/current specs/tickets/RP-02/desired` is empty;
`git diff --stat HEAD -- specs/current specs/program_model` is empty; TLC on
ticket current reproduces EV-02's numbers exactly (32,122,220 generated /
1,292,951 distinct / depth 26, 0 left on queue). The obvious model-side fix —
a `lastInternalAction` marker declaring the argument — was searched for and
refused on MF-029's existing record: the state pair already implies the
element, and `max_state_space_bound` sits at 279.9% of cap where a single
boolean was already measured to breach it.

## Evidence

| what | where |
|---|---|
| corpus before/after, determinism, rejected-input count | `ex4-corpus-before-after.md` |
| the audit contradiction, three cases, verbatim | `audit-contradiction-fixed.md` |
| 12-mutant catalog, both instruments, and the wrong-item probe | `mutant-catalog-rerun.md` |
| machine-readable matrices | `mutant-matrix-before.json`, `mutant-matrix-after.json`, `wrong-item-probe.json` |
| re-runnable harness | `harness/` |
| TLC, spec-unit, repository tests, zero-delta | `tlc-current.txt`, `spec-unit-tests.txt`, `repository-unit-tests.txt`, `zero-model-delta.txt` |

## Deferred, not done here

`specs/desired_program_model/deferred_findings.yaml` still carries
**EV-01-DF-01** and **EV-02-DF-03** as open. Both are fixed by this ticket, but
that file is outside RP-02's declared conflict keys and is a likely concurrent
write from RP-01/RP-04/RP-05, so the disposition is left for the epic owner to
apply at integration:

* **EV-01-DF-01** → `fixed-inline`, `disposition_ticket: RP-02`. Note that the
  filing's second claim — that the corpus "loses it entirely over the class
  'acted on the wrong item'" — was measured and is FALSE; the class was killed
  before the fix as well as after it.
* **EV-02-DF-03** → `fixed-inline`, `disposition_ticket: RP-02`.

Two new findings this ticket produced and did not file (no conflict-safe file
to file them in):

* **RP-02-DF-01 (minor)** — `seeded_faults.toml` and the ex4 README asserted an
  unmeasurable fault class on a prediction that was never run, and the
  prediction was wrong. Amended in place; worth a protocol note that a
  "cannot measure" claim needs the same run-before-you-publish discipline as a
  kill number.
* **RP-02-DF-02 (major, for the next epic)** — a generated corpus contains zero
  rejected inputs by construction, so guard relaxation is unkillable no matter
  how good parameter recovery gets. Needs an expected-refusal case shape and an
  adapter contract that can express "refused correctly". See the section above.
