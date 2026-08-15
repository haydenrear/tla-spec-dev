# `GOAL-absent-input-consumed` — baseline

**Tree: `436c78c55c60c3ee45901223176124df5e38b6ff`**, the epic base.

**Sources, both re-readable:**

- `specs/results/scorecards/cut-the-apparatus/CA-10-absent-input/RESULT.md` — the
  sweep, with the per-instance table
- `class-rows-436c78c.txt` in this directory — the nine ledger rows carrying the
  class, extracted from `specs/deferred_findings.yaml` at this tree

---

## 1. The figure

**48 instances across 30 of the 43 verdict-producing modules** under `scripts/`
and `examples/validation/`. **1 fixed, 47 open.**

Ledger rows `CA-10-DF-17` … `CA-10-DF-25`, **nine rows, all `disposition:
carried`** into this epic. `CA-10-DF-17` is the class statement; `-18` … `-25`
are the instrument families.

**No check exists.**

## 2. The class, and why every instance shipped

**An instrument returns a confident PASSING answer — PASS, clean, zero
violations, disposed, exit 0 — when handed an input that is ABSENT, EMPTY or
UNPARSEABLE.**

> **`R1` requires a demonstrated FAILING input on a real subject. It does not
> require a demonstrated ABSENT input. Every one of the instances satisfied `R1`
> in full** — an instrument can carry a passing `R1` demonstration, a failing
> `R1` demonstration, and still answer PASS to the question it was built to
> refuse, **because the third input was never in the contract.**

**That single sentence is the whole goal.** The doctrine extension is the
consumption; the repairs are downstream of it.

## 3. The one repair, and the shape it establishes

`score_tools._finding_ids()` hard-coded the live ledger and returned an **empty
set** when it was gone, so `R-H3` reported **every `filed_as` citation in the
whole scorecard record** as naming an id that was never filed.

**The repair was a signature change:**

```python
def _finding_ids() -> set[str] | None:      # was: -> set[str]
```

`None` means **nothing was read**. An empty set means **the ledger was read and
filed nothing**. *The old return type could not tell those apart and answered the
second with the first.* **That is the class in one line.**

| `score_tools.py audit` | violations | exit |
|---|---:|---:|
| before — ledger absent, `_finding_ids()` → `set()` | **14** | **1** |
| after — resolved to the archived ledger, 287 ids | **0** | **0** |

**And the third state was demonstrated too**, which is what makes it a fix rather
than a relocation of the false PASS: against a tree with no ledger live *or*
archived, `audit_rh3` emits **one `UNVERIFIED` line** — *"Every `filed_as`
citation below is UNCHECKED — not verified, and NOT fabricated"* — instead of 14
fabrication claims, and `UNVERIFIED` does not increment the violation count.
**The tool answers undecided: not clean, and not wrong.**

## 4. Instances that matter most, and why

| instance | behaviour | why it is first |
|---|---|---|
| `generate_python.py:238` | absent/empty `invariants:` → `def validate_state(state): return None` | **A state oracle that passes every state, and TWO SHIPPED EXAMPLES CARRY IT TODAY** with `validate_manifest` reporting zero errors. `CA-10-DF-21`: this is a defect **this toolchain scaffolds into every repository it touches** — the only instance that leaves this repository. |
| `corpus_diagnostics.py` | `passed = not over_cap` | an empty corpus **always passes** — the sink `CA-06-DF-01`'s zero-case generator drained into |
| `score_tools.py` `scope` | `--scorecards /nonexistent` → `0 REFUTED, 82 UNREACHABLE`, **exit 0** | the instrument `SS-04` extends **is itself an instance**. Its own absent-input answer is measured and must be handled, not inherited. |
| `disposition.py` | duplicate keys → certified clean | repaired for four-space nesting only; **still blind at any other indent, including a top-level `findings:`** |
| `blind_dispatch` | empty subject → PASS | repaired to exit 2; its **`UNDECIDED` branch is dead code** and the `WEAK PASS` half survives |

## 5. Two corrections that change how the goal is scoped

**First: three of the five originally-named exemplars were already repaired and
nothing in the record said so** — and **each left a named half behind**. Reporting
the class as five live instruments would have overstated it. **Do not assume a
filed finding is open. Check.**

**Second: measure before repairing.** The sweep is the authority on the size of
the class, not the exemplar list, and `SS-05` re-measures before it changes
anything. **A class quietly reported as smaller than it is, is the failure the
goal exists to prevent.**

## 6. The seven sub-shapes, which make the second sweep cheaper

From `CA-10-absent-input/RESULT.md` §3.2:

1. `if not path.exists(): return set()/[]/{}` — an empty result fed to a verdict
   as if measured
2. `all(...)` / `not any(...)` over a possibly-empty collection — **vacuously
   true**
3. a **one-sided threshold** that zero trivially satisfies
4. `.get(k, default)` collapsing **both sides** of a comparison, so two empties
   match
5. `except (OSError, ValueError): return []` — unparseable becomes
   indistinguishable from absent
6. a **default-named lookup** that misses silently
7. an **empty selection** (`--only` matching nothing, a glob matching no file)
   reported as a satisfied population

## 7. Why this is `consumption` and not `filing`

`GOAL-consumption-obligatory` measured harvest at **2 of 41** — *a floor*, since
12 of 95 cards were never swept — and the predecessor then produced **57
findings while consuming almost none into its own checks**. **Filing a finding
routes it; it does not change what the substrate checks.**

**`SS-02` lands the rule as an executed check. A doctrine line with no instrument
is a preference.**

## 8. The doctrine constraint the check must satisfy

Under the adjudicated static-gates doctrine, the check is **in the permitted
population**: static checks over **this project's own record, metadata and
method** have **3 catches : 1 false refusal** and the doctrine **may not refuse
them**. It **may** refuse a gate over subject-program content.

**So the check is scoped to this project's own instrument register and refuses
nothing about an adopter's code.** That boundary is clause (e) and it is not
negotiable.
