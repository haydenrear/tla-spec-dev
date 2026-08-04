# Implementation Brief — `<Action>` in `<component>`

> **Read this instead of the model.** Every constraint below was measured from
> the TLA+ model by `tla-spec-dev analyze architecture`; none was invented for
> you. You do not need to open the spec. You do need to honor the constraints,
> or say why you could not.

- **Confidence:** `FULL` | `DEGRADED` | `REFUSED` — `<one line: why>`
- **Descriptor:** `<path to the JSON>` (`tla-spec-dev/architecture-descriptor` v`<n>`)
- **Model:** `<module>.tla` + `<cfg>` @ `<commit>`
- **Partition:** `<declared | emergent>`, `<origin>` — `decomposes: <bool>`,
  `consumable_as_architecture: <bool>`, `Q = <q>`

---

## 1. The work

`<One paragraph, supplied by whoever requested the work. The descriptor does
not know what you are being asked to build — only where it goes.>`

---

## 2. Where it lives — MEASURED

| | |
|---|---|
| Component | `<C_n>` (`<name>`) |
| Variables in it | `<vars>` |
| It **owns** (writes confined here) | `<owns, or "(none) — see §6">` |
| This action's reads | `<per component: C1: a, b; C2: c>` |
| This action's writes | `<per component: C1: x; C2: y>` |
| Internal to the component? | `<yes / no — it crosses <ports>>` |

---

## 3. The constraints

These are not preferences. Each one is a fact about the model, and code that
breaks it makes the model wrong about the program.

1. **Write only these variables:** `<the action's write set, by component>`.
   Any other program state you write is state the model does not have.
2. **Reach only these components, only through these actions:**
   `<C2 (name) via A, B>` — or `<nothing: this action is internal to <component>>`.
   A call into a component not listed here is an edge the model does not
   declare. (`components[].reaches[]`)
3. **Effects at the boundary.** The declared ports for this action are
   `<port: type target>`, `<...>` — or **`(none declared)`**, which this
   manifest distinguishes from *absent*: an empty row claims *performs no
   distinct effect*, an absent row claims *unmapped*. `<state which one>`.
   Keep the transition pure and push every side effect to those ports; an
   effect on any other port is a conformance gap the effect oracle will report.
4. **One externally visible commitment.** `<Either: "This action commits in
   <component> only. Keep it that way — one commit point, and nothing
   externally visible before it." OR: "MEASURED SPAN: this action commits in
   <C1: vars> and <C2: vars> in one step. The model asserts those land
   atomically. Either your implementation makes them atomic, or the model is
   wrong about your program — say which; do not ship a partial commit under an
   atomic name.">`
5. **Coordination is explicit, and it is these variables.** Coordination
   between `<component>` and `<the components it reaches>` happens by writing
   `<the crossing write set>`. If your implementation needs another channel — a
   shared flag, a poll loop, a lock, a retry that reads someone else's row —
   that is protocol state the model does not represent. Add it to the model or
   do not add it to the code.
6. **The component's own state stays single-writer.** `<owns>` is written only
   from `<component>`. `<If single_writer_violations names variables this
   action writes: "MEASURED VIOLATION: <var> is written from <components> by
   <actions>. It is not single-writer today; do not treat it as private.">`

---

## 4. What you may NOT do

- Do not write a variable outside §3.1, or introduce program state that is not
  a modeled variable.
- Do not call into a component §3.2 does not list, even transitively, even
  "just to read".
- Do not emit an effect on a port §3.3 does not list.
- Do not split one modeled action into two externally visible commitments, or
  merge two into one.
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
| `component_count` | `<n>` | `>= 2` | `<Y/N>` |
| `modularity_q` | `<q>` | `> 0` | `<Y/N>` |
| `crossing_action_fraction` | `<f>` | `<= 0.5` | `<Y/N>` |

`<Fill in exactly one:>`

- **FULL** — every criterion met. The boundary this brief names is one the
  model's own interaction graph shows.
- **DEGRADED** — `<the failing criteria>`. This partition is **declared**, so
  the descriptor is consumable, but the boundary is an assertion the project
  made and the interaction graph does not confirm. `<Say what that costs: e.g.
  "Q < 0 means these two components share more interaction than chance — the
  cut is a wish, not a measurement", or "crossing fraction <f> means <n> of
  <m> actions cross the port §3.2 names, so 'reach only through this port' is
  barely a restriction.">` Constraints §3.1, §3.3 and §3.4 are unaffected —
  they are measured per action, not per partition.
- **REFUSED** — see the refusal block below; no constraints were rendered.

**Refusal block** (only when the brief could not be rendered):

> No brief. `<reason>`. There is no component for this work to belong to, so
> every clause above would be true of the whole program and would constrain
> nothing. A vacuous brief is worse than none: it reads like architecture.
> To get a brief here, declare a component partition (`architecture:` in
> `spec_manifest.yaml`, or `--components`) — the tool measures a partition you
> name and never writes one for you.

---

## 7. Reproduce this brief

Every clause above is a field lookup. A reviewer can recount it:

```bash
python3 scripts/tla_spec_dev.py --spec-root specs analyze architecture \
  <tla> <cfg> [--components <partition.yaml>] --format json > descriptor.json

# §2, §3.1, §3.2, §3.6
jq '.measured.partition.components[] | select(.name=="<component>")' descriptor.json
# §3.1, §3.2 (per-component reads/writes of this action)
jq '.measured.crossing_actions[] | select(.action=="<Action>")' descriptor.json
jq '.measured.actions[]          | select(.name=="<Action>")'   descriptor.json
# §3.4
jq '.measured.spanning_actions[] | select(.action=="<Action>")' descriptor.json
# §3.6
jq '.measured.ownership.single_writer_violations' descriptor.json
# §6
jq '.measured.partition.criteria, .measured.partition.consumable_as_architecture' descriptor.json
# §3.3 (the manifest, not the descriptor)
#   effects.actions.<Action>  ->  effects.components.*.ports.<port>
```

Rendered by `prompts/implementation_brief.md` on `<YYYY-MM-DD>`.
