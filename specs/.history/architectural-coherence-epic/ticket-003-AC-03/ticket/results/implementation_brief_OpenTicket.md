# Implementation Brief — `OpenTicket` in `workflow`

> **Read this instead of the model.** Every constraint below was measured from
> the TLA+ model by `tla-spec-dev analyze architecture`; none was invented for
> you. You do not need to open the spec. You do need to honor the constraints,
> or say why you could not.

- **Confidence:** `DEGRADED` — the partition is declared, and its
  `modularity_q` criterion fails (Q = -0.018). §6.
- **Descriptor:** `specs/tickets/AC-03/results/architecture_descriptor_declared.json`
  (`tla-spec-dev/architecture-descriptor` v1)
- **Model:** `specs/current/TlaSpecDevCli.tla` + `specs/current/MC.cfg` @ `e73b7d1`
- **Partition:** `declared`, `specs/tickets/AC-03/results/architecture_components.yaml`
  — `decomposes: false`, `consumable_as_architecture: true`, `Q = -0.018441`

---

## 1. The work

Implement `tla-spec-dev open ticket <ID>`: scaffold the ticket's `current/`,
`desired/`, `tests/` and `results/` directories from the accepted baseline and
record the ticket as open.

---

## 2. Where it lives — MEASURED

| | |
|---|---|
| Component | `C1` (`workflow`) |
| Variables in it | `lastCommand`, `result`, `setup_phase`, `spec_root`, `ticket_state` |
| It **owns** (writes confined here) | `setup_phase`, `spec_root` |
| This action's reads | `setup_phase`, `spec_root`, `ticket_state` — all in `workflow` |
| This action's writes | `lastCommand`, `result`, `ticket_state` — all in `workflow` |
| Internal to the component? | **yes** — `OpenTicket` is in `C1.internal_actions` and appears in no port |

---

## 3. The constraints

These are not preferences. Each one is a fact about the model, and code that
breaks it makes the model wrong about the program.

1. **Write only these variables:** `ticket_state`, `lastCommand`, `result`.
   Notably **not** `setup_phase` and **not** `spec_root` — this action reads
   both and writes neither. Any other program state you write is state the
   model does not have.
2. **Reach only these components, only through these actions:** *none.*
   `OpenTicket` is **internal to `workflow`**. It appears in no port and in no
   component's `reaches[]`. It must not touch `complexity_gate`, `corpus_gate`,
   `effect_conformance`, `kill_test`, or `architecture_scan` — the whole
   `scanners` component — in any way, including reading one "just to report it".
3. **Effects at the boundary.** The declared port for this action is
   `spec_tree: filesystem.write **/specs/**`. That is the **only** effect it
   may perform. This row is present and non-empty, so it claims *these are the
   effects*, not *unmapped*. Keep the transition pure — decide the whole new
   `ticket_state` first, then write the tree once at the boundary. A spawn, a
   network call, a write under `**/results/**` or `**/.venv/**`, or a delete
   anywhere is a conformance gap the effect oracle will report.
4. **One externally visible commitment.** `OpenTicket` does not appear in
   `spanning_actions`: it commits in `workflow` only. Keep it that way — one
   commit point, and nothing externally visible before it. A half-scaffolded
   ticket directory left behind by a failure is a second, unmodeled commitment.
5. **Coordination is explicit, and it is these variables.** `OpenTicket`
   coordinates with nothing: it has no far side. Its only channel to the rest
   of the program is `ticket_state`, which `CloseTicket`, `RunSpecUnitTests`,
   `UpdateTicketCurrent` and `UpdateTicketDesired` also write. If your
   implementation needs another channel — a lock file, a marker the next
   command polls for, a retry that re-reads someone else's state — that is
   protocol state the model does not represent. Add it to the model or do not
   add it to the code.
6. **The component's own state stays single-writer.** `workflow` owns
   `setup_phase` and `spec_root`; you write neither, so nothing you do can
   break that. **MEASURED VIOLATION on what you *do* write:** `ticket_state`,
   `lastCommand` and `result` are each written from `workflow` **and**
   `scanners` (by `RunSpecUnitTests`, and by every command respectively). They
   are not private to this action — do not cache them, do not assume you are
   the last writer, and do not derive anything from their previous value beyond
   what §2 says you read.

---

## 4. What you may NOT do

- Do not write a variable outside §3.1, or introduce program state that is not
  a modeled variable.
- Do not call into a component §3.2 does not list — for `OpenTicket` that is
  *any* other component — even transitively, even "just to read".
- Do not emit an effect on a port §3.3 does not list.
- Do not split `OpenTicket` into two externally visible commitments, or merge
  it with another modeled action.
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
| `modularity_q` | -0.018441 | `> 0` | **N** |
| `crossing_action_fraction` | 0.375 | `<= 0.5` | Y |

**DEGRADED** — `modularity_q` fails. This partition is **declared**, so the
descriptor is consumable, but the boundary is an assertion the project made and
the interaction graph does not confirm. Q < 0 means `workflow` and `scanners`
share *more* interaction than chance would produce: `lastCommand` and `result`
are written by all fifteen commands, so the graph is nearly complete and no cut
through it scores well. Read §3.2 accordingly — "internal to `workflow`" is
true of a boundary nobody has validated.

Vacuity tests: `V1` no (2 components). `V2` no (`workflow` owns 2 variables and
has 9 internal actions). `V3` no (0.375 ≤ 0.5 — 6 of 16 actions cross).

Constraints §3.1, §3.3 and §3.4 are unaffected — they are measured per action,
not per partition, and hold whatever the partition scores.

---

## 7. Reproduce this brief

```bash
python3 scripts/tla_spec_dev.py --spec-root specs analyze architecture \
  specs/current/TlaSpecDevCli.tla specs/current/MC.cfg \
  --components specs/tickets/AC-03/results/architecture_components.yaml \
  --format json > descriptor.json

jq '.measured.partition.components[] | select(.name=="workflow")' descriptor.json
jq '.measured.actions[]          | select(.name=="OpenTicket")'   descriptor.json
jq '.measured.crossing_actions[] | select(.action=="OpenTicket")' descriptor.json   # empty: internal
jq '.measured.spanning_actions[] | select(.action=="OpenTicket")' descriptor.json   # empty: one commitment
jq '.measured.ownership.single_writer_violations' descriptor.json
jq '.measured.partition.criteria, .measured.partition.consumable_as_architecture' descriptor.json
#   specs/current/spec_manifest.yaml: effects.actions.OpenTicket -> [spec_tree]
#                                     effects.components.TlaSpecDevCliPort.ports.spec_tree
```

Rendered by `prompts/implementation_brief.md` on 2026-07-27.
