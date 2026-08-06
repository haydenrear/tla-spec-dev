# Epic: falsifiable instruments

**Starter for the next epic agent. Read this before the plan.**

Branch `epic/falsifiable-instruments`, cut from `main` at `fcdbe6f` after
`ports-as-adapters` merged. Canonical plan:
`specs/desired_program_model/ticket_plan.yaml`.

---

## 1. The one sentence

**Five of this project's instruments cannot produce the result that would refute
them, and that is why three epics of mechanism work moved nothing.**

Not a list of bugs. A property they share.

| instrument | the result it cannot produce | measured at |
|---|---|---|
| the port-scoped positive control | **red** — nothing is seeded in a port's region to trip it | `PA-03-DF-03`, `PA-04-DF-01` |
| the control-property probe | **fail** — a no-op reports `HOLDS` | `PA-06-DF-07` |
| the A/B experiment | **divergence** — the null is entailed by the fixture | `PA-06-DF-08` |
| the thermometer tripwire | a *correct* verdict — a docstring mention fails it, an aliased import passes it | `PA-06-DF-05` |
| the scorecard's D1/D4/D5 | a **stable** number — 4 points moved on byte-identical trees | `PA-06-DF-06` |

We already wrote the rule. `references/architecture_advice.md` **S2**: *"Every
criterion must have a demonstrated failing input and a demonstrated passing
input."* It was written for a scanner we deleted, and it was never turned on the
instruments we kept.

---

## 2. Why this and not "make the generator better"

Three epics have asked how to improve generation. The answer has been the same
every time and it is now three epics old:

> **On this fixture the generated corpus is still worse than a suite a competent
> engineer writes in an afternoon.**

`ports-as-adapters` sharpened it into something harder to ignore: across every
instrument on every arm, **no generated instrument has a unique kill.** Only the
hand-written `suite-fake` does. `suite-fake` *strictly dominates*
`corpus-port-swap:fake` — it kills everything that column kills, plus two more.

So the honest question is no longer "how do we make generation better." It is:

**Do we actually know that any of this works? And would we be able to tell if it
did not?**

Right now the answer is no, because the instruments cannot fail. Fix that first
and every subsequent number means something. Skip it and the next epic produces
another table nobody can act on.

---

## 3. What `ports-as-adapters` established, and what it did not

**Established, and worth building on:**

- **The architectural content in the prompt is not decoration.** D3: arm B 4/4,
  arm A 2/2, **arm C 1/1** — a length-matched control, *longer* than arm B, with
  no architectural vocabulary, scored the lowest of the three. Its author
  considered the exact seam arm B built and **declined it on merit**: *"a layer
  with no second implementation behind it and no test that needs to swap one
  in."* The predecessor's 6.6× confound is retired.
- **Structure is not bought with lost behavior.** D4 = 4/4 on both arms A and B.
- **A fault behind a port can be reached.** `PA-M12` — a fault inside a *fake*
  adapter — is `SURVIVED` under both action-bound columns and **`KILLED`** under
  `corpus-port-swap:fake`.

**Not established, and do not inherit it as if it were:**

- That the port machinery **catches** anything the suite did not. It does not.
- That the arms **can** diverge. The fixture entails the null.
- That any port-scoped kill number is a **count** rather than a floor.
- That D1, D4 or D5 can carry a cross-epic delta. They demonstrably cannot.

---

## 4. Doctrine that carries forward unchanged

Every one of these was bought with a measured failure. They are not up for
renegotiation in this epic.

- **No new gates.** Four epics of static checking caught zero bugs. Guidance goes
  in prompts; verdicts come from judged scorecards.
- **Complexity is a thermometer, never a thermostat.** It reports, refuses
  nothing, gates nothing. `CD-01`: it proposes no cut, because a tool that picks
  the boundary makes every edge legal by construction.
- **A metric falling is not evidence the design improved** (`MF-020`).
- **A declaration that nothing executes will drift.** Ship the check with the
  declaration, using the shipped builders, so a rename fails a test.
- **Commit predictions before dispatch, with at least three negatives.**
- **File findings; fix nothing during a measurement.**
- **Report per class, per arm, with executable counts. Never a single rate.**
- **Ask every blind agent what it REJECTED.** Measured value in the last epic:
  **18 of 19 findings** came from that question or from an explicit attack brief.
  The suite produced **one**, its first in four rounds, and it fired at the
  measuring ticket.
- **Never edit a target to match a result. Never re-run selectively until a
  number passes. Report the run that happened.**

---

## 5. Two rules this epic adds

**R1 — An instrument ships with a demonstrated failing input.** Not a test that
the instrument runs. A demonstration that it goes **red** when the thing it
watches is actually broken, and that the demonstration is re-runnable. This is
`architecture_advice.md` S2 applied to ourselves.

**R2 — A control that cannot fail is worse than no control.** It is the defect
this project has now hit four times, most recently in the ticket whose job was to
catch it. When a control cannot be made to work, it is **reported red**, never
made green by weakening what it asserts.

---

## 6. The standing rule, unchanged

**A low or unflattering result is the preferred outcome.** Every epic here
produced its best material by measuring something that did not work: the gate
that caught nothing, the repair that moved zero cells, the structure that arrived
and caught no bugs, the clean audit that was clean because of its own filter, and
now five instruments that cannot fail.

**An epic that closes with only good news about itself has not been measured.**
