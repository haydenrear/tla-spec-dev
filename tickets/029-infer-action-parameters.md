# Infer Action Parameters In The Case Generator

Status: Open

Every one of the 57,617 generated cases carries `params={}`. The generator
records *that* an action fired, not *with what*. Until this is fixed, every
downstream adapter fix buys reachability testing rather than argument testing —
which for a CLI is most of the point.

## This is a generator change, not a model change

**Do not add state to the TLA+ model.** No `lastInternalAction` marker, no
action-name variable, no argument-binding variable. This was considered and
rejected by the repository owner for two reasons:

1. **It is unnecessary.** The parameters are recoverable from the case's own
   before/after state pair, which the generator already has.
2. **It is unaffordable.** `max_state_space_bound` sits at 70% and MF-019
   proved a *boolean* variable breaches it. A marker carrying action names plus
   argument bindings would force decomposition before it could land.

Being generator-side is also what makes this **experimental and cheaply
revertible**, which was an explicit condition of approval: nothing in the spec
changes, and reverting is deleting a function.

## The parameters are recoverable — verified

| Action | Parameter | Recovery |
|---|---|---|
| `OpenTicket(root, ticket)` | `root` | guard `root = spec_root` pins it to the before-state |
| | `ticket` | `ticket_state' = [… EXCEPT ![ticket] = …]` — the index that changed |
| `UpdateTicketDesired(ticket)` | `ticket` | EXCEPT-index diff |
| `CloseTicket(root, ticket)` | both | guard + EXCEPT-index |
| `ScaffoldProject(root)` | `root` | written into `spec_root'` in the after-state |

Three recovery mechanisms cover these: **guard-pinned** (the parameter is
constrained equal to a before-state value), **EXCEPT-index** (the parameter is
the index whose entry changed), and **written-through** (the parameter appears
in the after-state).

That table covers the actions inspected so far. **Audit all thirteen labels** —
do not assume the pattern holds, and report any action where it does not.

## The trap this ticket must avoid

MF-028's spike wrote a tautology into its own work: it defaulted `spec_root`
from `case.after`, then "checked" the result against `case.after`. It passed
vacuously. The spike caught it only because **a negative control that should
have failed, passed.**

The discipline:

- Derive a parameter from the **before-state** and the **transition**. Never
  from the field being checked.
- Where a parameter genuinely cannot be recovered, mark it **UNCHECKED** and
  say so. Do not fabricate a value that makes a comparison succeed.
- **Every action needs a negative control** — a deliberately wrong expectation
  that must make the check fail. A check that cannot fail is not a check.

## Acceptance criteria

- Generated cases carry real `params` for every action where recovery is
  possible, derived from the state pair.
- A per-action recoverability audit covering **all thirteen labels**, naming
  the mechanism used (guard-pinned / EXCEPT-index / written-through) or the
  reason recovery is impossible.
- Parameters that cannot be recovered are marked **UNCHECKED**, never
  fabricated. An action whose parameters are entirely unrecoverable is a
  finding, reported plainly.
- **A negative-control test per action**, proving the parameter check can
  actually fail. This is the regression guard against the tautology.
- **Zero TLA+ model delta.** If you conclude the model must change, stop and
  report rather than changing it — that reopens a decision the owner already
  made.
- No case is dropped, filtered, or skipped because its parameters could not be
  recovered. Mark and keep.

## Out of scope

The fifteen remaining adapters, the two adapters that do not exist
(`UpdateTicketDesired`/`UpdateTicketCurrent`), `EXTENDS` resolution, the
`analyze corpus` OOM, the component-metric design question, the silent default,
and the alphabetical model pick. Those are scoped **after** this ticket, because
this one determines whether they buy signal or theatre.

## Note

MF-023's decomposition and MF-028's spike bindings live on open PR #50 and the
merged MF-028 work respectively. Do not duplicate either.
