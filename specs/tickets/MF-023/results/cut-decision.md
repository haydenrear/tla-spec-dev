# MF-023 — the cut: what the tool proposed, what was adopted, and why

## 1. What `analyze complexity` proposed (verbatim)

Command:

```
python3 scripts/tla_spec_dev.py --spec-root specs analyze complexity \
  specs/tickets/MF-023/current/TlaSpecDevCli.tla \
  specs/tickets/MF-023/current/MC.cfg
```

Output (`analyze-complexity-presplit.txt`):

```
[MEASURED] Near-decomposability
  graph modularity Q = 0.012 over the variable interaction graph
  (weight of an edge = number of actions touching both variables)
  C1: kill_test, lastCommand, result, setup_phase, spec_root, ticket_state  (6 variables, 14 actions)
  C2: complexity_gate, corpus_gate, effect_conformance  (3 variables, 4 actions)
  candidate port-crossing actions:
    AnalyzeComplexity crosses C1, C2
    AnalyzeCorpus crosses C1, C2
    RunEffectConformance crosses C1, C2
    RunSpecUnitTests crosses C1, C2

SUGGESTED MOVE: ABSTRACT
  - no configured invariant reads [lastCommand, result]; Move 1 permits
    projecting variables no invariant reads

VERDICT: FAIL -- component C1 is touched by 14 actions, exceeding max_component_actions 8
```

## 2. The proposal was OVERRIDDEN. Two reasons, both measured.

**Reason 1 — it does not fix the failing gate.** The proposed C1 is the failing
component, unchanged: 14 actions against a cap of 8. A decomposition adopting it
verbatim fails the gate identically. Q = 0.012 is the tool saying the partition
is no better than random.

**Reason 2 — the ABSTRACT suggestion contradicts the model's own doctrine.**
The tool suggests projecting away `[lastCommand, result]` because no configured
*invariant* reads them. But `result.next` is externally-visible CLI output, and
**six separate comments in the pre-split module justify keeping a verdict
distinct precisely because that distinction is visible in `result.next`** --
"gaps" vs "dead_surface" vs "unobservable" (MF-013/MF-027), "below_floor" vs
"incomplete_catalog" (MF-016). Deleting the variable that carries the visibility
would invalidate the stated justification for keeping the verdicts apart.

The tool's criterion -- "no invariant reads it" -- is not the criterion the
doctrine uses. It has no notion of external visibility, and it offered only
"delete"; it has no vocabulary for "relocate".

## 3. What was adopted, derived from the tool's own MEASURED evidence

The R/W matrix (MEASURED, not projected) shows:

```
lastCommand         w w w w w w w w w w w w w w    <- all 14 actions
result              w w w w w w w w w w w w w w    <- all 14 actions
```

They are the only two variables written by every action. In a variable
interaction graph weighted by co-touching actions, two universal writers connect
every pair of variables, driving modularity toward zero. **They are the hubs
that made the model look indecomposable.**

Removing them from the internal graph is what lets anything separate -- and the
place they belong is not the bin, it is the External view. That is the split the
doctrine already mandates for every onboarded project:

| View | Variables | Role |
|---|---|---|
| `Core.tla` | none | constants, lifecycle ordinals, verdict domains, `CommandResult` |
| `Internal.tla` | `setup_phase`, `spec_root`, `ticket_state`, `complexity_gate`, `corpus_gate`, `effect_conformance`, `kill_test` | the workflow state machine -- what the CLI *knows* |
| `External.tla` | `lastCommand`, `result` (+ 7 inherited) | the observable channel -- what the CLI *reports* |

So the cut was determined by the tool's measurement and rejected by the tool's
recommendation. Both facts are recorded because the second is the finding.

## 4. Action and invariant mapping (complete)

All 14 actions live in Internal as state transitions; External wraps each with
its channel write as `Invoke<Name>`. No action is dropped or added.

| # | Internal action | External wrapper | Ports |
|---|---|---|---|
| 1 | `BuildSkillCli` | `InvokeBuildSkillCli` | `cli_artifact` |
| 2 | `InstallLocalCli` | `InvokeInstallLocalCli` | `cli_artifact` |
| 3 | `ScaffoldProject(root)` | `InvokeScaffoldProject` | `spec_tree` |
| 4 | `RecordBudgets(root)` | `InvokeRecordBudgets` | `spec_tree` |
| 5 | `ScaffoldWorkflow(root)` | `InvokeScaffoldWorkflow` | `spec_tree` |
| 6 | `OpenTicket(root,t)` | `InvokeOpenTicket` | `spec_tree` |
| 7 | `UpdateTicketDesired(t)` | `InvokeUpdateTicketDesired` | `spec_tree` |
| 8 | `UpdateTicketCurrent(t)` | `InvokeUpdateTicketCurrent` | `spec_tree` |
| 9 | `AnalyzeComplexity(root)` | `InvokeAnalyzeComplexity` | `evidence_report`, `tlc_process` |
| 10 | `AnalyzeCorpus(root)` | `InvokeAnalyzeCorpus` | `evidence_report` |
| 11 | `RunEffectConformance(root)` | `InvokeRunEffectConformance` | `evidence_report` |
| 12 | `RunKillTest(root)` | `InvokeRunKillTest` | `evidence_report`, `test_process` |
| 13 | `RunSpecUnitTests(root,t,o)` | `InvokeRunSpecUnitTests` | `test_process`, `spec_tree` |
| 14 | `CloseTicket(root,t)` | `InvokeCloseTicket` | `spec_tree` |

Removed: the explicit `Stutter` disjunct (FINDING 7) -- redundant under
`[][N]_v`, and the only source of uncoverable spec cases.

### Invariants

All 14 pre-split invariants live in **Internal** and are checked by
`Internal.cfg`. They constrain only Internal variables, so this is placement by
free variables rather than by preference.

| Invariant | View | Note |
|---|---|---|
| `TypeInvariant` | Internal | must keep this exact name -- FINDING 1 |
| `CliInstalledRequiresBuilt` | Internal | tautology under the ordinal, retained by name |
| `WorkflowRequiresProject` | Internal | tautology, retained |
| `BudgetsRequireProject` | Internal | tautology, retained |
| `WorkflowRequiresBudgets` | Internal | tautology, retained |
| `ProjectChoosesKnownSpecRoot` | Internal | not a tautology |
| `NoOpenClosedOverlap` | Internal | tautology under MF-025, retained |
| `CurrentRequiresDesired` | Internal | |
| `SpecUnitTestsRequireCurrent` | Internal | |
| `SpecUnitTestsRequireAnalyzedGate` | Internal | MF-011 |
| `SpecUnitTestsRequireMeasuredCorpus` | Internal | MF-014 |
| `SpecUnitTestsRequireMeasuredEffects` | Internal | MF-013/MF-027 |
| `ClosedTicketsPassedSpecUnitTests` | Internal | |
| `KillTestVerdictRequiresBudgets` | Internal | MF-016 |
| `InternalInvariant` | Internal | conjunction of all 14 |
| `ExternalInvariant` | **External** | `InternalInvariant` + channel well-formedness (`result.accepted \in BOOLEAN`, `result.next /= NoReason`) -- **new**, the only added property |

`External.cfg` checks all 14 inherited invariants **plus** `ExternalInvariant`,
so nothing is checked in fewer places after the split than before.

## 5. Per-view component-heuristic results — reported, not tuned

| View | Component | Vars | Actions | `max_component_variables` 6 | `max_component_actions` 8 | Verdict |
|---|---|---|---|---|---|---|
| Internal | C1 | 7 | 14 | **FAIL** | **FAIL** | **FAIL** |
| External | C1 | 2 | 4 | pass | pass | PASS (**vacuous** -- sees 2 of 9 variables, FINDING 1) |

**Neither budget was renegotiated.** The Internal failure is reported as a
finding about the metric (FINDING 3): the cap is unsatisfiable by any partition
of this model, because the singleton `{setup_phase}` alone is touched by 12 of
14 actions. External's pass is reported as vacuous rather than banked as a win.
