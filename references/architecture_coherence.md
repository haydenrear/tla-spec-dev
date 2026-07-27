# Architecture Coherence

*(AC-01 + AC-02. The reference for `tla-spec-dev analyze architecture`: what the
architecture descriptor measures, what the reflexion check adds when production
code is supplied, what neither can see, and the reading order.)*

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
have no architecture worth describing.

**Precisely what that claim is, and is not (AC-03-DF-02, owner-verified).**
The emergent partition comes from *greedy* community detection, so "the model
does not decompose" states **what greedy search found**, not a proof about the
model. Exhaustive enumeration of all 115,975 partitions of
`TlaSpecDevCli.tla`'s 10 variables — scored with this tool's own modularity
function and its own three criteria — finds **two** that meet all three, the
best at `Q = 0.0029`, crossing fraction `0.188`. Hand either back via
`--components` and the shipped CLI agrees: *the partition is a cut*.

Both things are true, and neither cancels the other:

- The doctrine stands. `Q = 0.003` is negligible structure — two orders of
  magnitude under Newman's conventional 0.3 — so refusing to invent a cut is
  still right, and *proposing* one of those partitions would be exactly the
  confidently-wrong automation CD-01 removed. This tool does not adopt
  exhaustive search and does not offer those partitions.
- The wording was overclaiming, and the fix is to report the search method
  with the result: a negative from greedy search reads "greedy community
  detection found no cut", never "no cut exists".

The same distinction applies within one project: `External.tla` does not
decompose under greedy search, while the same example's **`Internal.tla` does**
(2 components, `Q = 0.0069`, crossing fraction exactly `0.50`). A per-model
claim is not a per-project claim.

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
| `coherent` | every crossing code edge has a declared port, and every port is realized |
| `divergent` | a code edge exists that no port declares, or a port exists that no code edge realizes — a finding, not a failure |
| `unmappable` | **the scan ran and could not see the target** |

`unmappable` is deliberately distinct from `unknown` — the same distinction
that made the effect oracle grow `unobservable` in MF-027. "Not run" and "ran
blind" are different facts, and collapsing them to shrink the state space would
delete the verdict this epic exists to report.

`analyze architecture` on its own always reports **`unmappable`**. It measures
the model; with no production code supplied there is nothing for the code to be
coherent *with*, and a clean report on a target that was never observed is
indistinguishable from a clean report on one that was. AC-02 supplies the code
side, below.

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

# The Reflexion Check (AC-02)

*(`analyze architecture <spec> <cfg> --code <tree> --map <map.yaml>`, or
`scripts/architecture_reflexion.py` with the same flags.)*

The reflexion model (Murphy, Notkin & Sullivan): put a **declared** map from
production modules to model components next to the **extracted** dependency
graph of the real code, and report the difference.

| category | what it is |
|---|---|
| **convergence** | a code edge between two components that a port declares |
| **divergence** | a code edge between two components **no port declares** — the block pulled out from under three others |
| **absence** | a **declared port no code edge realizes** — dead architecture |
| *(internal)* | an edge that stays inside one component. Counted, never checked: it crossed no boundary, so no port was needed. **Internal edges are not convergences** — treating them as such is how a one-component map reports a perfect score |

Every divergence carries `file:line` at the **site** of the dependency — the
import statement or the call, not the file it points at. A finding a reader
cannot navigate to is an opinion.

Both `--code` and `--map` are required together. Half a reflexion check is a
usage error (exit 2): scanning code with no map would make the *tool* choose the
boundary, and a map with no code reports every port absent.

## The Declared Map

```yaml
architecture_map:
  language: python
  components:
    - component: lifecycle       # a component NAME the descriptor has
      modules:
        - scripts/start_ticket.py
        - scripts/close_ticket.py
    - component: scanners
      modules:
        - scripts/analyze_complexity.py
```

Module entries resolve relative to the code root or to the working directory,
and must land inside the code root. A directory entry expands to every `*.py`
beneath it. The component names must be names the descriptor's partition
has — declared under `architecture:` or emergent (`C1`, `C2`, …).

The map is **read, never computed**, for the reason AC-01 gives for the
component partition: a tool that picks its own boundary picks the one the code
already has, and every edge is then legal by construction.

Five map shapes are **refused** (exit 2 — unusable input, not a finding about
the code): a component the model does not have; an entry naming no file; a
module placed in two components; a `language:` with no extractor in this build;
and a code root with no Python in it.

## What Makes The Verdict `unmappable`

Each of these means part of the target was not observed, so a clean report on
it would be indistinguishable from a clean report on a target that was:

| blind spot | what it means |
|---|---|
| `model_has_no_architecture` | `partition.consumable_as_architecture` is false. **The reason names the model, not the code.** With one component every code edge is internal, so the diff would otherwise report a flawless codebase for a model with no boundary in it |
| `unmapped_module` | a module in the scanned tree the map places nowhere. A map cannot cover the tidy half of a tree and report it clean |
| `unrealized_component` | a declared component the map places no module in. Whether the code respects a boundary whose other side does not exist is not observable |
| `unfalsifiable_coherence` | **every component pair has a port**, so no code edge *could* have diverged. "No divergences" is then a property of the declared architecture, not a measurement of the code. Note the limit: this catches the fully degenerate case only. A partition that is merely *coarse* — one where the specific pair a bad edge would cross happens to be ported — still reports a real-looking clean |
| `dynamic_import` / `dynamic_attribute` / `star_import` | an edge reached through a computed name. Not an absence — an unknown |
| `unparsed_file` | a `.py` file the parser could not read |
| `non_python_file` | a file in the tree with no extractor in this build |
| `first_party_outside_code_root` | the tree imports a package that sits **beside** the code root in the same project. Its edges are not in the graph, and narrowing `--code` would otherwise delete real dependencies with nothing recorded |

**`unmappable` is not "clean with caveats" and not "nothing found."** Findings
are still reported under it: a divergence discovered next to a blind spot is a
real divergence. The verdict says only that the check will not certify what it
did not observe.

**Nothing downgrades it.** There is no flag, key, annotation, or environment
variable that turns `unmappable` into `coherent`. Suppression-shaped keys in the
map (`assume_coherent`, `allow_unmapped`, `waived`, `justification`,
`accepted_divergences`, `ignore`, `exclude`, …) are **scanned, reported under
`ignored_suppression_keys`, and never honored** — the shape
`scripts/effect_conformance.py` uses, for the reason stated there: a silently
ignored key is nearly as bad as an honored one, because the author believes the
finding was waived. The verdict property reads nothing but the report itself,
and `tests/test_architecture_reflexion.py::TestNothingDowngradesAnUnobservableVerdict`
holds that shut from four directions (map keys, environment variables,
command-line flags, and the source of the verdict property).

## What The Map Cannot Stop

Stated plainly because the dogfood proved it, and because a reader who does not
know this will over-trust a `coherent`:

1. **The map is where the lying would happen.** Placement is the author's
   judgment. Any divergence can be made to disappear by moving the offending
   module into the component it reaches — no code changes, the verdict flips.
   The tool measures the map the project declares and cannot audit the
   declaration. What it *can* do, and does, is refuse a map that covers only
   part of the tree, and publish the placements so the argument is about a
   written-down claim rather than an impression.
2. **A model whose actions all touch the same variables has no architecture to
   violate.** Under *any* partition of such a model, every component pair gets a
   port, and `unfalsifiable_coherence` fires. This is not a corner case: it is
   what this repository's own model does (see below).
3. **Only in-tree edges are edges.** A component that reaches a database, a
   socket, or a subprocess directly is invisible here. The external import
   targets are listed in the report, but they are not measured against
   anything. (`scripts/effect_conformance.py` is the tool that watches *that*
   axis.)
4. **Python only.** Any other language reports refused-or-blind, never clean.

## Measured On This Repository (AC-02, 2026-07-27)

The dogfood is the acceptance test, and it produced a finding rather than a
score. Three runs, none of them `coherent`, all exit 0. Full report:
`specs/.history/architectural-coherence-epic/ticket-002-AC-02/results/dogfood-findings.txt`.

**1. `--code scripts --map specs/program_model/architecture_map.yaml`** —
`unmappable`, and the comparison **does not run at all**. The model has one
component (Q = 0.000; `lastCommand` and `result` are written by all fifteen
commands), so `consumable_as_architecture` is false. The report prints "NOT
RUN" instead of three zeroes, because "zero divergences" for a comparison that
never happened is the false clean in its purest form. Had the diff run anyway,
all 258 code edges would have been internal to the single component: 0
divergences, 0 absences, `coherent`. **This is the recorded acceptance result.**

**2. the same, plus the declared four-component partition**
(`--components specs/program_model/architecture_components.yaml`: `surface`
{`lastCommand`, `result`, `setup_phase`, `spec_root`} / `tickets`
{`ticket_state`} / `corpus` {`complexity_gate`, `corpus_gate`,
`effect_conformance`} / `kill` {`kill_test`}) — the check runs:

```
34 modules, all mapped, 4 components, all realized
258 edges: 140 internal, 118 convergences, 0 divergences, 0 absences
ports:     corpus<->surface, corpus<->tickets, kill<->surface, surface<->tickets
NO port:   corpus<->kill, kill<->tickets
```

The two unported pairs are real — no action touches `kill_test` together with
`ticket_state` or with a corpus verdict — so an edge across either **would**
have been a divergence. There is none: the two kill-test scripts reach only
`budgets.py`, which is in `surface` and ported. That is a genuine falsifiable
negative result about this codebase. The verdict is nevertheless `unmappable`,
for five extraction blind spots: three computed-name
`importlib.import_module` calls, `scripts/run_tlc.sh` (no extractor), and
`spec_double_compiler/` (first-party, beside the code root, outside the scan).

The honest sentence: *over the edges the extractor can resolve, the code
respects both boundaries the model draws — and it cannot resolve all of them,
so the check will not certify it.*

**3. the coarser partition this ticket wrote first** (fold `kill_test` in with
the other scanner verdicts: `surface` / `tickets` / `scanners`) — **every** one
of the three pairs then has a port, because `RunSpecUnitTests` touches
`ticket_state` and two corpus verdicts while every command writes `lastCommand`
and `result`. No code edge could diverge; `unfalsifiable_coherence` fires.

**The reading.** The tool works, and the thing it measures is fragile. Without
a declared partition this repository cannot be measured at all, and the
obstacle is the *model*. With one, whether the check can falsify anything
depends on how fine the partition is — and runs 2 and 3 are both defensible
readings of the same model, separated by one variable's placement. The tool
reports which partition it was handed and whether that one *could* have failed.
It does not tell you the finer cut is the better one, and does not try (CD-01).
Expect `unmappable` far more often than `coherent` on any real Python tree;
that is the design working. All three results are pinned by tests so they
cannot be quietly lost.

## The Reflexion Machine-Readable Contract

`--format json` adds a `reflexion` block to the descriptor payload and moves
`verdict.architecture_scan` off `unmappable` **only because a code side was
actually observed**. Standalone,
`scripts/architecture_reflexion.py --format json` emits the same block as the
document root, with `schema: "tla-spec-dev/architecture-reflexion"`,
`schema_version: 2` (AC-04 bumped it additively to add `basis`; every v1 field
is unchanged).

```
measured.modules_scanned          int
measured.modules_mapped           int
measured.edges_extracted          int
measured.ported_pairs             [[componentA, componentB]]
measured.unported_pairs           [[componentA, componentB]]
measured.divergence_detectable    bool   <-- false means a clean result is vacuous
measured.internal_edges           int
measured.external_imports         {top_level_name: ["file:line"]}
convergences[]                    {from, to, from_component, to_component, pair[2],
                                   kind, symbol, file, line, site, port, port_actions[]}
divergences[]                     {... same, port: null, why}
absences[]                        {port, between[2], actions[], why}
unmapped_modules                  [str]
unrealized_components             [str]
blind_spots[]                     {kind, detail, where}
ignored_suppression_keys          [str]
verdict.architecture_scan         "coherent" | "divergent" | "unmappable"
verdict.reasons                   [str]
verdict.blocks_promotion          false
advisory.suggests_moves           false
basis.map_digest                  sha256 over language + module->component placements
basis.placements                  {module: component}   <-- the declared map, verbatim
basis.scanned_modules             [str]
basis.architecture_digest         sha256 over component names + port pairs + port actions
basis.architecture_ports          [[componentA, componentB]]
basis.comparison_ran              bool   <-- false means this scan holds no findings at all
```

## The Delta: Comparing Two Scans (AC-04)

`--baseline <a previous --format json scan>` adds a `delta` block. It answers
one question — *did this change move the code toward or away from the
boundaries the model draws* — and it answers it in edges, not in a score.

The unit is a **distinct dependency**, `(from, to, kind, symbol)`. The line
number is deliberately excluded from that identity: a refactor that shifts every
line in a file would otherwise report the whole graph as lost and regained, and
the one edge that actually moved would be buried. Every site is still listed on
its row.

```
basis.attribution        "code_only" | "partial" | "unattributable"
basis.map_unchanged      bool          <-- both digests, before and after
basis.map_changes        {reassigned[{module,from_component,to_component}], added[], removed[]}
basis.architecture_changes {ports_added[], ports_removed[], ...}
divergences.before/after/delta        int
divergences.lost[]       {from,to,kind,symbol,sites[],classification{reason,detail,verifies_drop}}
divergences.gained[]     {from,to,kind,symbol,sites[]}
divergences.stable_basis {before,after,delta,...}  <-- modules in BOTH scans, same component
convergences / absences  the same shape
verdict.direction        "improved" | "worsened" | "unchanged" | "unverified" | "unattributable"
verdict.red_flags        [str]
verdict.blocks_promotion false
```

Three refusals, and each exists because the alternative is a printed improvement
that nothing supports:

1. **`unattributable`** — the two scans did not share a declared map (a module
   present in both was re-placed, or the component set changed) or did not share
   a model (a port was added or removed). "What The Map Cannot Stop" above is not
   a caveat here; it is the mechanism. A one-line re-placement of
   `scripts/budgets.py` from `surface` to `kill` in this repository's own map
   moves the divergence count from 0 to 6 with no code change, and the delta
   across that pair reports `unattributable` with the re-placement named, rather
   than a 6-edge improvement.
2. **`unverified`** — the count fell and the disappeared edges do not explain it.
   Each lost edge is classified: `dependency_removed` (both endpoints still
   scanned and still placed the same way — the disappearance a refactor
   produces), `endpoint_left_tree` (the file is gone: a deletion, red-flagged),
   `endpoint_unmapped` (the file is still there and the map stopped placing it —
   the edge left the *measurement*, not the code), `endpoint_reassigned`. This is
   MF-020 applied to structure.
3. **A baseline that cannot be one** is the only nonzero exit: a text report (it
   does not enumerate the edges), a scan whose comparison never ran (it holds no
   findings — not zero findings), or a payload with no `basis` (the map it was
   measured against is unrecoverable).

The delta is **recorded in the complexity ledger and gates nothing**. A rise is
recorded, not refused. See `references/architecture_tractability.md`, "The
Validated-Refactor Basis Has A Structure Half".

## Exit Codes

| code | when |
|---|---|
| `0` | the check ran — **including `divergent` and `unmappable`**. A divergent codebase is a finding |
| `2` | the map or the code tree is unusable: "I could not measure this" |

No close, promotion, or case-generation path reads `architecture_scan`. A gate
is *earned*, per check, only once real-app validation shows it is trustworthy
enough to block on — and the dogfood above is the argument for why this one has
not earned it yet.

## What This Is Not

- Not a gate. Nothing here refuses anything.
- Not a suggestion engine. No proposed cut, no refactor, no target shape, no
  next step, and no "this module belongs over there". CD-01 binds on both
  halves.
- Not a source of an architecture. The tool measures the partition the project
  declares, or the one the matrix admits, and the module map the project writes.
  It never writes either one.
- Not a semantic check. The reflexion half compares *dependency structure*. It
  says nothing about whether a component does what the model's actions say it
  does.
