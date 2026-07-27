# Implementation Brief — `CreateAccount` in `C1`

> **Read this instead of the model.** Every constraint below was measured from
> the TLA+ model by `tla-spec-dev analyze architecture`; none was invented for
> you. You do not need to open the spec. You do need to honor the constraints,
> or say why you could not.

- **Confidence:** `FULL` — every decomposition criterion is met and no vacuity
  test fires. This is the only `FULL` render of the four in AC-03's evidence.
  Read the caveat in §6 anyway.
- **Descriptor:** `specs/tickets/AC-03/results/architecture_descriptor_example_internal.json`
  (`tla-spec-dev/architecture-descriptor` v1)
- **Model:** `examples/distributed_history/specs/program_model/Internal.tla`
  + `Internal.cfg` @ `e73b7d1`
- **Partition:** `emergent` (greedy modularity maximization over the variable
  interaction graph) — `decomposes: true`,
  `consumable_as_architecture: true`, `Q = 0.00692`

---

## 1. The work

Implement the account-creation transition of the order service's internal view:
register a new account if it does not already exist, and record that this was
the last internal action taken.

---

## 2. Where it lives — MEASURED

| | |
|---|---|
| Component | `C1` (unnamed — the partition is emergent; see §6) |
| Variables in it | `accounts`, `carts`, `lastInternalAction`, `orders` |
| It **owns** (writes confined here) | `accounts`, `carts` |
| This action's reads | `C1`: `accounts` |
| This action's writes | `C1`: `accounts`, `lastInternalAction` |
| Internal to the component? | **yes** — `CreateAccount` is in `C1.internal_actions` and appears in no port |

---

## 3. The constraints

These are not preferences. Each one is a fact about the model, and code that
breaks it makes the model wrong about the program.

1. **Write only these variables:** `accounts` and `lastInternalAction`.
   Not `carts` — `C1` owns it, but this action does not write it. Not `orders`.
   Any other program state you write is state the model does not have.
2. **Reach only these components, only through these actions:** *none.*
   `CreateAccount` is **internal to `C1`**. The model has exactly one port,
   `P1: C1 <-> C2`, crossed only by `Checkout` and `ProjectOrder`. This action
   is neither. It must not touch `outbox` or `projections` — the whole of `C2`
   — in any way, including reading one.
3. **Effects at the boundary.** **UNMAPPED, not empty.** This project's
   `spec_manifest.yaml` carries no `effects:` block at all, so there is no
   declared port for this or any other action, and the effect oracle has
   nothing to check against. That is an *absent* row, which claims *nobody
   mapped this*, not *this action performs no effect*. Treat the effect surface
   of this action as unconstrained by the model and unverified — and keep the
   transition pure anyway, so that whoever declares the ports later finds them
   at one boundary instead of scattered.
4. **One externally visible commitment.** `CreateAccount` does not appear in
   `spanning_actions`: it commits in `C1` only. Keep it that way — one commit
   point, and nothing externally visible before it.
5. **Coordination is explicit, and it is these variables.** `CreateAccount`
   coordinates with nothing: it has no far side. The model's only cross-
   component channel is `P1`, whose far-side writes are `outbox` (by
   `Checkout`) and `outbox`, `projections` (by `ProjectOrder`). If your
   implementation needs to signal the projection side — a flag, a poll, a
   queue read — that is protocol state this action does not have. Add it to the
   model or do not add it to the code.
6. **The component's own state stays single-writer.** `accounts` is written
   only from `C1`, by `CreateAccount` alone, and it does **not** appear in
   `single_writer_violations`. It is genuinely private: you are its only
   writer, and you may reason about it as owned. **MEASURED VIOLATION on the
   other variable you write:** `lastInternalAction` is written from `C1` and
   `C2` by all four actions. It is shared; do not treat it as private and do
   not derive control flow from its previous value.

---

## 4. What you may NOT do

- Do not write a variable outside §3.1, or introduce program state that is not
  a modeled variable.
- Do not call into a component §3.2 does not list — for `CreateAccount` that is
  *any* other component — even transitively, even "just to read".
- Do not invent an effect port. §3.3 says the model declares none; that is a
  gap to report, not a licence to emit whatever you like and call it declared.
- Do not split this action into two externally visible commitments, or merge it
  with another modeled action.
- Do not "fix the architecture." This brief reports what the model measures. It
  proposes no cut, no refactor, and no target shape (CD-01). If you think the
  boundary is wrong, that is a finding for the owner, not a change for you.
- Do not edit the model to match code you wrote. The model changes through the
  ticket workflow, deliberately, before the code.

---

## 5. If a constraint is impossible

**Stop and say so.** Name the constraint, the line of work that collides with
it, and what you would need. A constraint you silently break costs more than
one you report: the model still claims it holds, every oracle downstream still
reports green, and the next change is made against a boundary that no longer
exists.

This brief is **advisory**. It gates nothing, refuses nothing, and blocks no
merge. Reporting the collision is the whole of what it asks.

---

## 6. Provenance — how much this brief is worth

**Does the partition this brief cites actually decompose the model?**

| criterion | measured | rule | met |
|---|---|---|---|
| `component_count` | 2 | `>= 2` | Y |
| `modularity_q` | 0.00692 | `> 0` | Y |
| `crossing_action_fraction` | 0.5 | `<= 0.5` | Y |

**FULL** — every criterion met. The boundary this brief names is one the
model's own interaction graph shows, with no declaration involved. Vacuity
tests: `V1` no (2 components); `V2` no (`C1` owns `accounts` and `carts`, and
has 2 internal actions); `V3` no (0.5 is not `> 0.5`).

Three things `FULL` does **not** mean, and a reader should hold all three:

1. **`FULL` describes the partition, not every clause.** §3.3 is `UNMAPPED`
   here — the strongest possible partition does not supply an effect
   declaration the manifest never wrote.
2. **The margins are thin.** Q = 0.007 clears its rule by 0.007 and sits far
   below Newman's conventional 0.3 for significant community structure (which
   this toolchain reports next to Q and never applies as a criterion).
   `crossing_action_fraction` clears its rule by *exactly* zero. One more
   crossing action in a four-action model and this brief would be `DEGRADED`.
3. **The components have no names.** An emergent partition yields `C1` and
   `C2`, and "you are in C1" is markedly less usable to a coding agent than
   "you are in `orders`". Naming is what a **declared** partition buys even
   when the emergent one already decomposes.

---

## 7. Reproduce this brief

```bash
python3 scripts/tla_spec_dev.py --spec-root specs analyze architecture \
  examples/distributed_history/specs/program_model/Internal.tla \
  examples/distributed_history/specs/program_model/Internal.cfg \
  --format json > descriptor.json

jq '.measured.partition.components[] | select(.id=="C1")'            descriptor.json
jq '.measured.actions[]          | select(.name=="CreateAccount")'   descriptor.json
jq '.measured.crossing_actions[] | select(.action=="CreateAccount")' descriptor.json   # empty: internal
jq '.measured.spanning_actions[] | select(.action=="CreateAccount")' descriptor.json   # empty: one commitment
jq '.measured.ownership.single_writer_violations' descriptor.json
jq '.measured.partition.criteria, .measured.partition.consumable_as_architecture' descriptor.json
#   examples/distributed_history/specs/program_model/spec_manifest.yaml has NO
#   `effects:` key -- hence §3.3 UNMAPPED.
```

Rendered by `prompts/implementation_brief.md` on 2026-07-27.
