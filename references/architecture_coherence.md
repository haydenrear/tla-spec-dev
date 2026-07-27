# Architecture Coherence

*(AC-01. The reference for `tla-spec-dev analyze architecture`: what the
architecture descriptor measures, what it cannot see, and the reading order.)*

`analyze complexity` already computed the structure. It printed it. This
reference covers the command that gives that structure a name, a schema, and
consumers.

Read this alongside `references/architecture_tractability.md` — Move 2
("Decompose") is the design doctrine, Move 3's target shapes
(single-writer state, functional core / imperative shell, explicit commit
points, explicit protocol state) are the vocabulary, and "Advisory, Not
Blocking" is the governing stance. This reference is the *measurement* half of
that advice.

## Reading Order

1. **Component partition** — what the components are, and where they came
   from (`DECLARED` by the project, or `EMERGENT` from the interaction graph).
2. **Does this partition decompose the model?** — the criteria table.
   **Read this before anything below it.** If the partition is not a cut,
   every figure underneath is relative to a boundary the model does not have,
   and the descriptor says so in place of a clean number.
3. **State ownership** — per-variable writers, then single-writer violations.
4. **Ports** — the crossings that would become interfaces if the cut were
   taken.
5. **Spanning actions** — the write sets that commit in more than one
   component at once. These are the actions the cut cannot be taken through
   without splitting an atomic commitment.
6. **Verdict** — the value recorded in the model's `architecture_scan`.

## What It Measures

Everything comes from the spec + cfg. No source file is read.

**Components.** Variable clusters. Two sources, and the descriptor always says
which:

- `DECLARED` — the project wrote the partition down, in `spec_manifest.yaml`
  under `architecture:` or in a file passed to `--components`:

  ```yaml
  architecture:
    components:
      - name: lifecycle
        variables: [setup_phase, spec_root, ticket_state]
      - name: scanners
        variables: [complexity_gate, corpus_gate, kill_test]
  ```

  Components must not overlap, and every variable must exist in the model. A
  declaration that cannot be read is **refused** (exit 2) — never silently
  replaced by the emergent clustering, which would report facts about a
  boundary nobody declared under the declaration's name.

- `EMERGENT` — greedy modularity maximization over the variable interaction
  graph, the same computation `analyze complexity` reports. This is a
  measurement of what the R/W matrix admits. **It is not a proposal.** The tool
  never writes a partition file and never recommends one.

**Ownership.** For each variable, the actions that write it. Then the
single-writer violations: variables whose writes are not confined to one
component.

The attribution is over each action's **write set only**. An action that reads
`a` in C1 and writes `b` in C2 writes into one component; counting `b` as
multi-component because the action glanced across the boundary would make every
variable touched by any crossing action a violation, and the finding would
carry no information. An action that *writes* in C1 and C2 does commit state in
both, and every variable it writes is then measurably not confined.

**Ports.** Component pairs that some action crosses, each with the actions that
cross it. Published keyed by the pair (`P1: C1 <-> C2`) as well as per action,
because the reflexion check's question is "does a port exist between these two
components", not "which actions cross".

**Span.** Actions whose write set covers more than one component. Distinct from
a crossing action, which may merely read across. The evidence is file-free by
construction: it names model variables and actions.

## What It Cannot See

- **Nothing about the code.** AC-01 is the model side only. The comparison
  against production modules is the reflexion check (`--code` / `--map`, AC-02).
- **Nothing TLC would find.** This is static parsing, with the same coverage
  contract as the complexity scanner: `EXTENDS` is followed, `INSTANCE` and
  `LOCAL` fail closed, actions are the top-level disjuncts of the next-state
  relation with helper bodies expanded transitively, and when no next-state
  relation can be found the fallback primes heuristic is used **and says so**.
- **Whether a component *should* exist.** The descriptor measures the structure
  that is there. Some components score badly and still need to exist in that
  shape.
- **A better partition.** By design. See below.

## The Refusal: When The Model Does Not Decompose

An emergent partition is a **cut** only if all three hold:

| criterion | rule | why |
|---|---|---|
| `component_count` | `>= 2` | a partition with one component separated nothing |
| `modularity_q` | `> 0` | Q ≤ 0 means the partition groups no more interaction than chance |
| `crossing_action_fraction` | `<= 0.5` | a boundary crossed by more than half the actions is not a boundary |

The last reuses the R/W matrix's own `>half` convention — the same one that
already makes a variable a dense row and an action a dense column — rather than
a threshold invented for this command. Newman's conventional reading (Q above
~0.3 indicates significant community structure) is **reported next to the
score and never applied as a criterion**: picking a Q threshold to pass or fail
models is the tuned judgment CD-01 removed.

When the criteria are not met, the descriptor states that the model does not
decompose, prints the criteria with their measurements, and **stops**. It does
not present a one-component partition in which every variable is trivially
owned, no action is a port, and zero single-writer violations are found. That
would be a flawless architecture report for a model with no architecture, and
it would be indistinguishable from the real thing — the MF-027 rule, applied to
structure. Fields that are not defined are `null` and carry a reason.

It also does not propose a different partition. Naming a boundary the matrix
does not show is exactly the CD-01 failure: the removed suggested-move chooser
was confidently wrong on standard TLA+ (an aliased invariant made it recommend
projecting away every variable), and a clean-looking architecture derived from
an invented cut is worse than no architecture at all. The way to have an
architecture measured on a model that does not decompose is to **declare** one.

**Measured on this repository (AC-01, 2026-07-27).** Neither real target
decomposes:

- `specs/current/TlaSpecDevCli.tla` — one component, Q = 0.000. `lastCommand`
  and `result` are written by all 15 commands, so the interaction graph is
  effectively complete. There is no cut to name.
- `examples/distributed_history/.../External.tla` — two components, Q = 0.047,
  but 9 of 12 actions cross the boundary. Every variable is written by some
  action that also writes into the other component, so the example has **no
  single-writer state at all**.

That is a finding about the models, not a defect in the tool, and it is the
epic's most load-bearing measurement: the descriptor's first two real targets
have no architecture to describe.

## Advisory, Never Blocking

`analyze architecture` exits `0` whenever it can analyze the model. A model
with no architecture is a **finding**. It exits nonzero only for:

- an unresolvable module hierarchy (exit 1) — the MF-030 fail-closed, "I could
  not measure this";
- an unreadable **declared** partition, or a missing spec/cfg (exit 2).

No action in the TLA+ model guards on `architecture_scan`, and no close,
promotion, or case-generation path may read it. A gate is *earned*, per check,
only once real-app validation shows it is trustworthy enough to block on.

## `architecture_scan`

The model's `architecture_scan` variable ranges over
`unknown | coherent | divergent | unmappable`.

| value | meaning |
|---|---|
| `unknown` | the scan has not run |
| `coherent` | every code edge has a declared port |
| `divergent` | a code edge exists that no port declares — a finding, not a failure |
| `unmappable` | **the scan ran and could not see the target** |

`unmappable` is deliberately distinct from `unknown` — the same distinction
that made the effect oracle grow `unobservable` in MF-027. "Not run" and "ran
blind" are different facts, and collapsing them to shrink the state space would
delete the verdict this epic exists to report.

`analyze architecture` on its own always reports **`unmappable`**. It measures
the model; with no production code supplied there is nothing for the code to be
coherent *with*, and a clean report on a target that was never observed is
indistinguishable from a clean report on one that was. AC-02 supplies the code
side.

## The Machine-Readable Contract

`--format json` emits `schema: "tla-spec-dev/architecture-descriptor"`,
`schema_version: 1`. The consumer-facing fields:

```
measured.variables                              [str]
measured.actions[]                              {name, reads[], writes[]}
measured.action_attribution                     str   (how the action set was determined)
measured.partition.source                       "declared" | "emergent"
measured.partition.origin                       str
measured.partition.modularity_q                 float
measured.partition.decomposes                   bool
measured.partition.consumable_as_architecture   bool   <-- BRANCH ON THIS
measured.partition.criteria[]                   {name, measured, rule, met, why}
measured.partition.unassigned_variables         [str]  (declared partitions only)
measured.partition.components[]                 {id, name, variables[], owns[],
                                                 actions[], internal_actions[],
                                                 crossing_actions[], writer_actions[],
                                                 reaches[{component, name, via_actions[]}]}
measured.ownership.writers                      {variable: [action]}
measured.ownership.single_writer_violations     [{variable, components[], component_names[],
                                                  writers[]}] | null
measured.ownership.single_writer_basis          str    (what the violations are relative to)
measured.ports[]                                {id, between[2], actions[]}
measured.crossing_actions[]                     {action, components[], ports[],
                                                 reads{cid: [var]}, writes{cid: [var]}}
measured.spanning_actions[]                     {action, write_components[],
                                                 writes{cid: [var]}, evidence}
verdict.architecture_scan                       "unmappable" (from this command)
verdict.reasons                                 [str]
verdict.blocks_promotion                        false
advisory.blocks_promotion                       false
advisory.suggests_moves                         false
```

### For AC-02, the reflexion check

- `partition.components[].id` / `.name` are the component identifiers a
  declared `architecture_map.yaml` maps production modules onto.
- `ports[].between` is the **declared port edge set**. A code edge whose
  endpoints map to two different components is a **convergence** iff some port
  lists that pair, and a **divergence** otherwise. A port that no code edge
  realizes is an **absence**.
- **`partition.consumable_as_architecture` is the field that prevents the false
  clean.** When it is `false`, the model side has no architecture, so the
  reflexion verdict is `unmappable` — *not* `coherent`. A single-component
  partition makes every code edge internal and would otherwise report a
  perfectly coherent codebase for a model with no components. Nothing may
  downgrade that to clean.
- `crossing_actions[].reads` / `.writes` give the per-component direction of
  each crossing, for reporting which side of a divergent edge is which.

### For AC-03, the implementation brief

Per component, the brief's clauses map directly:

- *the component this work belongs to, and the variables it owns* —
  `components[].name`, `components[].owns` (note: `owns` is writes-confined,
  not mere membership, and is empty when the partition has one component);
- *which other components it may reach, and through which port only* —
  `components[].reaches[]`, giving the target component and the exact action
  set that is allowed to reach it;
- *the actions that are internal to the component* —
  `components[].internal_actions`;
- *the atomicity-fidelity rule, one externally visible commitment per action* —
  `spanning_actions[]` names every action that currently commits in more than
  one component, which is the violation of that rule the model can see.

A brief must not be rendered from a descriptor whose
`consumable_as_architecture` is `false`: there is no component to belong to.

## What This Is Not

- Not a gate. Nothing here refuses anything.
- Not a suggestion engine. No proposed cut, no refactor, no target shape, no
  next step. CD-01 binds.
- Not a code analysis. That is AC-02.
- Not a source of an architecture. The tool measures the partition the project
  declares, or the one the matrix admits. It never writes one.
