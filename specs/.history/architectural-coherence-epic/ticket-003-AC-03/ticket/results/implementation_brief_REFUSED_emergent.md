# Implementation Brief — `OpenTicket` — REFUSED

> **Read this instead of the model.** Every constraint below was measured from
> the TLA+ model by `tla-spec-dev analyze architecture`; none was invented for
> you.

- **Confidence:** `REFUSED` — the partition has one component. See §6.
- **Descriptor:** `specs/tickets/AC-03/results/architecture_descriptor_emergent.json`
  (`tla-spec-dev/architecture-descriptor` v1)
- **Model:** `specs/current/TlaSpecDevCli.tla` + `specs/current/MC.cfg` @ `e73b7d1`
- **Partition:** `emergent` — `decomposes: false`,
  `consumable_as_architecture: false`, `Q = 0.000`

---

## 1. The work

Implement `tla-spec-dev open ticket <ID>` — the same request that
`implementation_brief_OpenTicket.md` renders from a declared partition. This
file is the *same ask against the same model*, rendered from the descriptor as
the tool emits it with no partition declared.

---

## 2.–5. Not rendered.

Gate A of `prompts/implementation_brief.md` failed:
`measured.partition.consumable_as_architecture == false`, and vacuity test
`V1` fires (`components` has length 1). No constraints were rendered.

---

## 6. Provenance — how much this brief is worth

| criterion | measured | rule | met |
|---|---|---|---|
| `component_count` | 1 | `>= 2` | **N** |
| `modularity_q` | 0.0 | `> 0` | **N** |
| `crossing_action_fraction` | 0.0 | `<= 0.5` | Y |

**Refusal block:**

> No brief. This model's emergent partition has one component: `lastCommand`
> and `result` are written by all fifteen commands, so the variable interaction
> graph is effectively complete and greedy modularity maximization terminates
> at the trivial partition, Q = 0.000. There is no component for this work to
> belong to, so every clause of a brief would be true of the whole program and
> would constrain nothing. A vacuous brief is worse than none: it reads like
> architecture.
> To get a brief here, declare a component partition (`architecture:` in
> `spec_manifest.yaml`, or `--components`) — the tool measures a partition you
> name and never writes one for you.

### What the vacuous brief would have said

Recorded so the failure mode is legible rather than theoretical. Every line
below is *true*, and every line is worthless:

> **Where it lives.** Component `C1`. Variables in it: `architecture_scan`,
> `complexity_gate`, `corpus_gate`, `effect_conformance`, `kill_test`,
> `lastCommand`, `result`, `setup_phase`, `spec_root`, `ticket_state`.
> Internal to the component? Yes.
> **Reach only these components:** none — `C1` reaches nothing.
> **One externally visible commitment:** `OpenTicket` does not span. Keep it
> that way.
> **Single-writer:** zero violations.

Ten of ten variables in scope, every action internal, every port absent, zero
violations — a flawless architecture report for a model with no architecture,
in the same template and the same confident voice as a real one.

The descriptor already declines to say most of this: the text renderer prints
`owns: NOT MEASURABLE with one component -- every variable would be trivially
owned`, and `ownership.single_writer_violations` is **`null`**, with
`single_writer_basis` carrying the reason. But the JSON's
`components[0].owns` is the empty list `[]`, and a renderer that reads it as
"owns nothing" rather than "not measurable" gets a plausible clause out of a
field that means the opposite. That is precisely why Gate A is a gate and not a
caveat: the last line of defence is the consumer refusing to render, not the
producer hedging its fields.

---

## 7. Reproduce this refusal

```bash
python3 scripts/tla_spec_dev.py --spec-root specs analyze architecture \
  specs/current/TlaSpecDevCli.tla specs/current/MC.cfg --format json > descriptor.json

jq '.measured.partition.consumable_as_architecture' descriptor.json   # false  -> Gate A
jq '.measured.partition.components | length'        descriptor.json   # 1      -> V1
jq '.measured.partition.criteria'                   descriptor.json
jq '.measured.ownership.single_writer_violations'   descriptor.json   # null, with a reason
```

Rendered by `prompts/implementation_brief.md` on 2026-07-27.
