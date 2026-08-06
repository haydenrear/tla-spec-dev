# Implementation Brief — `AnalyzeComplexity` in `scanners`

> **Read this instead of the model.** Every constraint below was measured from
> the TLA+ model by `tla-spec-dev analyze architecture`; none was invented for
> you. You do not need to open the spec. You do need to honor the constraints,
> or say why you could not.

- **Confidence:** `DEGRADED` — `modularity_q` fails (Q = -0.018) **and** the
  subject component owns nothing and has no internal action (`V2`). §6.
- **Descriptor:** `specs/tickets/AC-03/results/architecture_descriptor_declared.json`
  (`tla-spec-dev/architecture-descriptor` v1)
- **Model:** `specs/current/TlaSpecDevCli.tla` + `specs/current/MC.cfg` @ `e73b7d1`
- **Partition:** `declared`, `specs/tickets/AC-03/results/architecture_components.yaml`
  — `decomposes: false`, `consumable_as_architecture: true`, `Q = -0.018441`

---

## 1. The work

Implement `tla-spec-dev analyze complexity <tla> <cfg>`: statically parse the
model, compute the dimension table, the state-space bound, the R/W matrix and
the modularity score, write the descriptor, and record the resulting scanner
verdict.

---

## 2. Where it lives — MEASURED

| | |
|---|---|
| Component | `C2` (`scanners`) — **named by the caller**, see §6 |
| Variables in it | `architecture_scan`, `complexity_gate`, `corpus_gate`, `effect_conformance`, `kill_test` |
| It **owns** (writes confined here) | **(none)** — see §6 |
| This action's reads | `workflow`: `setup_phase`, `spec_root` · `scanners`: (none) |
| This action's writes | `workflow`: `lastCommand`, `result` · `scanners`: `complexity_gate` |
| Internal to the component? | **no** — it crosses port `P1` (`workflow <-> scanners`) |

---

## 3. The constraints

These are not preferences. Each one is a fact about the model, and code that
breaks it makes the model wrong about the program.

1. **Write only these variables:** `complexity_gate` in `scanners`;
   `lastCommand` and `result` in `workflow`. Nothing else. In particular **not**
   `setup_phase`, **not** `spec_root` (you read both and write neither), and
   **not** any other scanner verdict — `analyze complexity` does not set
   `corpus_gate`, `effect_conformance`, `kill_test` or `architecture_scan`.
2. **Reach only these components, only through these actions:** `scanners`
   reaches `workflow` (`C1`) via `AnalyzeArchitecture`, `AnalyzeComplexity`,
   `AnalyzeCorpus`, `RunEffectConformance`, `RunKillTest`, `RunSpecUnitTests` —
   port `P1`, the only port in this model. `AnalyzeComplexity` is one of those
   six, so this action *is* the port. What it may touch on the far side is
   exactly §2's read/write rows: read `setup_phase` and `spec_root`, write
   `lastCommand` and `result`. Nothing else in `workflow` is reachable from
   here — `ticket_state` in particular is not.
3. **Effects at the boundary.** The declared port for this action is
   `evidence_report: filesystem.write **/results/**`. That is the **only**
   effect it may perform. The row is present and non-empty: it claims *this is
   the effect*, not *unmapped*. The manifest is explicit that the scan spawns
   nothing — a `tlc_process` (`process.spawn *java*`) port was declared here
   once and **removed** as dead model surface, because the analyze path is a
   static parser. So: no subprocess, no network, no write under `**/specs/**`
   or `**/.venv/**`, no delete. Compute the whole descriptor as a pure function
   of the parsed model, then write the report once.
4. **One externally visible commitment.** **MEASURED SPAN:** this action
   commits in `workflow` (`lastCommand`, `result`) and `scanners`
   (`complexity_gate`) in one step. The model asserts those land atomically.
   Either your implementation makes them atomic — the verdict and the recorded
   command become visible together, or neither does — or the model is wrong
   about your program. Say which. Do not ship a partial commit under an atomic
   name: a run that writes the report and then fails before recording the
   verdict is a state the model says cannot exist.
5. **Coordination is explicit, and it is these variables.** Coordination
   between `scanners` and `workflow` happens by writing `lastCommand` and
   `result` — that is the entire far-side write set of every action on `P1`.
   There is no other channel. If your implementation needs one — a flag another
   command polls, a lock, a cached descriptor another action reads, a "did the
   last scan pass" side file — that is protocol state the model does not
   represent. Add it to the model or do not add it to the code.
6. **The component's own state stays single-writer.** `scanners` owns
   **nothing**. **MEASURED VIOLATION on what you write:** `complexity_gate` is
   written from `workflow` and `scanners` (by `AnalyzeComplexity` itself, which
   commits in both); `lastCommand` and `result` likewise, by all fifteen
   commands. Not one variable you touch is private to this component. Treat
   every read of them as a read of shared state.

---

## 4. What you may NOT do

- Do not write a variable outside §3.1, or introduce program state that is not
  a modeled variable.
- Do not call into a component §3.2 does not list, even transitively, even
  "just to read". `ticket_state` is in `workflow` but outside this action's
  read set — it is not yours.
- Do not emit an effect on a port §3.3 does not list. Re-adding a `java` spawn
  here re-adds a port the manifest deliberately deleted.
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
| `modularity_q` | -0.018441 | `> 0` | **N** |
| `crossing_action_fraction` | 0.375 | `<= 0.5` | Y |

**DEGRADED**, on two counts.

- `modularity_q` fails. The partition is **declared**, so the descriptor is
  consumable, but the interaction graph does not confirm the boundary: Q < 0
  means these two components share more interaction than chance. The cut is a
  wish, not a measurement.
- **`V2` fires.** `scanners` has `owns: []` and `internal_actions: []`. Every
  action that touches it also commits in `workflow`. So "this work belongs to
  `scanners`" restricts nothing on its own — the component has no private state
  to protect and no action that stays inside it. §2 and the first clause of
  §3.6 are therefore near-empty, and §3.2's "reach only through this port" is
  weak here because *every* action of this component is on that port.

`V3` does not fire (0.375 ≤ 0.5 — 6 of 16 actions cross).

**Subject component:** named by the caller. `AnalyzeComplexity` appears in
`spanning_actions`, so it commits in both components and there is no derivable
answer to which one the work belongs to.

Constraints §3.1, §3.3 and §3.4 are unaffected by any of this — they are
measured per action, not per partition. §3.4 in particular is the strongest
clause in this brief and does not depend on the partition being good: the
action's write set spans, and that is a fact about the action.

---

## 7. Reproduce this brief

```bash
python3 scripts/tla_spec_dev.py --spec-root specs analyze architecture \
  specs/current/TlaSpecDevCli.tla specs/current/MC.cfg \
  --components specs/tickets/AC-03/results/architecture_components.yaml \
  --format json > descriptor.json

jq '.measured.partition.components[] | select(.name=="scanners")'        descriptor.json
jq '.measured.actions[]          | select(.name=="AnalyzeComplexity")'   descriptor.json
jq '.measured.crossing_actions[] | select(.action=="AnalyzeComplexity")' descriptor.json
jq '.measured.spanning_actions[] | select(.action=="AnalyzeComplexity")' descriptor.json
jq '.measured.ownership.single_writer_violations' descriptor.json
jq '.measured.ports' descriptor.json
jq '.measured.partition.criteria, .measured.partition.consumable_as_architecture' descriptor.json
#   specs/current/spec_manifest.yaml: effects.actions.AnalyzeComplexity -> [evidence_report]
#                                     effects.components.TlaSpecDevCliPort.ports.evidence_report
```

Rendered by `prompts/implementation_brief.md` on 2026-07-27.
