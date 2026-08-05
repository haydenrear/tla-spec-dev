# Implementation Brief — `<Action>` in `<component>`

> **Read this instead of the model.** Every constraint below was derived from
> the TLA+ model; none was invented for you, and none is a claim about the
> production code. You do not need to open the spec. You do need to honor the
> constraints, or say why you could not.

- **Confidence:** `FULL` | `DEGRADED` | `REFUSED` — `<one line: why>`
- **Model:** `<module>.tla` + `<cfg>` @ `<commit>`
- **Complexity JSON:** `<path>` (`analyze complexity --format json`)
- **Partition:** `<declared by <who>, on <date> | emergent, declared by nobody>`
  — `<n>` components

---

## 1. The work

`<One paragraph, supplied by whoever requested the work. The model does not
know what you are being asked to build — only where it goes.>`

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

**Does the partition this brief cites constrain anything?**

| test | measured | fires when | fired |
|---|---|---|---|
| `V1` one component | `<n>` components | `n == 1` | `<Y/N>` |
| `V2` subject constrains nothing | owns `<k>` variables, `<j>` internal actions | both zero | `<Y/N>` |
| `V3` the port is not a port | `<n>` of `<m>` actions write into >1 component | fraction > 0.5 | `<Y/N>` |
| `V4` nobody declared the partition | `<declared by … | emergent>` | emergent | `<Y/N>` |

`<Optional, and only as an uninterpreted figure: graph modularity Q = <q> from
analyze complexity. NO THRESHOLD IS APPLIED TO IT HERE. The removed architecture
scanner published `Q > 0` as its decomposition rule — ~26x below the threshold
it printed on the same page — and one added variable flipped this repository's
own verdict. See references/architecture_advice.md S2. Delete this line rather
than let a reader think it decided something.>`

`<Fill in exactly one:>`

- **FULL** — the partition was declared, Gate A holds, and no test fired. The
  boundary this brief names is one somebody committed to and the model's write
  sets respect.
- **DEGRADED** — `<the tests that fired>`. `<Say what that costs the reader in
  one sentence.>` Constraints §3.1, §3.3 and §3.4 are unaffected — they are
  derived per action, not per partition.
- **REFUSED** — see the refusal block below; no constraints were rendered.

**Refusal block** (only when the brief could not be rendered):

> No brief. `<reason>`. There is no component for this work to belong to, so
> every clause above would be true of the whole program and would constrain
> nothing. A vacuous brief is worse than none: it reads like architecture.
> To get a brief here, DECLARE a component partition — name the components and
> the variables each owns, in writing, and hand it to the renderer. Nothing in
> this toolchain will pick one for you, deliberately: a tool that picks the
> boundary makes every edge legal by construction
> (`references/architecture_advice.md` S6).

---

## 7. Reproduce this brief

Every clause above is derived arithmetic over one JSON payload, one partition,
and one manifest. A reviewer can redo it:

```bash
python3 scripts/tla_spec_dev.py --spec-root specs analyze complexity \
  <tla> <cfg> --format json > complexity.json

# the read/write set of this action -- §3.1, §3.2, §3.4, §3.6 all derive from it
jq '.measured.actions[] | select(.name=="<Action>")' complexity.json
# every action, to work out which variables are writes-confined -- §2 `owns`
jq '.measured.actions[] | {name, writes}' complexity.json
# the EMERGENT clustering: a measurement of the matrix, NOT the partition
jq '.measured.components, .measured.port_crossing_actions, .measured.modularity' complexity.json
# §3.3 (the manifest, not the model)
#   effects.actions.<Action>  ->  effects.components.*.ports.<port>
```

The partition itself is not in that payload and never will be. It is
`<declared by …>` and is reproduced by reading that declaration.

Rendered by `prompts/implementation_brief.md` on `<YYYY-MM-DD>`.
