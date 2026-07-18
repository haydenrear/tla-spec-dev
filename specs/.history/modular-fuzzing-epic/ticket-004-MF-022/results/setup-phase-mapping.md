# Part 2 — before/after mapping for the `setup_phase` collapse

MF-022 Part 2. Enumerated **before** the model was edited. This is the
deliverable that proves nothing was silently dropped: every guard and every
invariant conjunct expressed over the five removed booleans has a named
equivalent over `setup_phase`.

## The ordinal

```
setup_phase \in 0..5
```

| Value | Meaning | Reached by |
|---|---|---|
| 0 | nothing built | `Init` |
| 1 | CLI built | `BuildSkillCli` |
| 2 | CLI installed | `InstallLocalCli` |
| 3 | project scaffolded | `ScaffoldProject` |
| 4 | budgets recorded | `RecordBudgets` |
| 5 | workflow scaffolded | `ScaffoldWorkflow` |

## Predicate equivalences

The five booleans are pinned into a strict total order by their own action
guards, so each is exactly a threshold on the ordinal:

| Removed boolean | Equivalent | Negation |
|---|---|---|
| `cli_built` | `setup_phase >= 1` | `setup_phase < 1` |
| `cli_installed` | `setup_phase >= 2` | `setup_phase < 2` |
| `project_scaffolded` | `setup_phase >= 3` | `setup_phase < 3` |
| `budgets_recorded` | `setup_phase >= 4` | `setup_phase < 4` |
| `workflow_scaffolded` | `setup_phase >= 5` | `setup_phase < 5` |

**Reachability claim.** 5 booleans admit 32 combinations; the guards admit
only the 6 prefix-closed ones (FFFFF, TFFFF, TTFFF, TTTFF, TTTTF, TTTTT). The
ordinal `0..5` represents exactly those 6 and nothing else. The 26 dropped
combinations were declared state the program could never occupy.

## Action guard mapping

Each conjunction of thresholds collapses to a single equality because the old
guards paired a positive predicate with the negation of the next one.

| Action | Before | After | Note |
|---|---|---|---|
| `Init` | all five `= FALSE` | `setup_phase = 0` | |
| `BuildSkillCli` | `~cli_built` / `cli_built' = TRUE` | `setup_phase = 0` / `setup_phase' = 1` | `<1` collapses to `= 0` |
| `InstallLocalCli` | `cli_built /\ ~cli_installed` / `cli_installed' = TRUE` | `setup_phase = 1` / `setup_phase' = 2` | `>=1 /\ <2` |
| `ScaffoldProject` | `cli_installed /\ ~project_scaffolded` / `project_scaffolded' = TRUE` | `setup_phase = 2` / `setup_phase' = 3` | `>=2 /\ <3`; `spec_root' = root` unchanged |
| `RecordBudgets` | `cli_installed /\ project_scaffolded /\ ~budgets_recorded` / `budgets_recorded' = TRUE` | `setup_phase = 3` / `setup_phase' = 4` | `>=2 /\ >=3 /\ <4` |
| `ScaffoldWorkflow` | `cli_installed /\ project_scaffolded /\ budgets_recorded /\ ~workflow_scaffolded` / `workflow_scaffolded' = TRUE` | `setup_phase = 4` / `setup_phase' = 5` | `>=2 /\ >=3 /\ >=4 /\ <5` |
| `OpenTicket` | `cli_installed /\ workflow_scaffolded` | `setup_phase >= 5` | `>=2 /\ >=5` |
| `UpdateTicketDesired` | (no setup predicate) | unchanged | |
| `UpdateTicketCurrent` | (no setup predicate) | unchanged | |
| `AnalyzeComplexity` | `cli_installed /\ project_scaffolded /\ budgets_recorded` | `setup_phase >= 4` | `>=2 /\ >=3 /\ >=4` |
| `RunSpecUnitTests` | `cli_installed` | `setup_phase >= 2` | |
| `CloseTicket` | `cli_installed` | `setup_phase >= 2` | |

No action gains or loses an enabling condition. Every collapse above is an
equivalence over the reachable set, not a weakening.

## Invariant mapping

| Invariant | Before | After | Status |
|---|---|---|---|
| `TypeInvariant` | five `\in BOOLEAN` conjuncts | `setup_phase \in 0..5` | 5 conjuncts to 1 |
| `CliInstalledRequiresBuilt` | `cli_installed => cli_built` | `setup_phase >= 2 => setup_phase >= 1` | retained, now structurally enforced |
| `WorkflowRequiresProject` | `workflow_scaffolded => project_scaffolded` | `setup_phase >= 5 => setup_phase >= 3` | retained, now structurally enforced |
| `BudgetsRequireProject` | `budgets_recorded => project_scaffolded` | `setup_phase >= 4 => setup_phase >= 3` | retained, now structurally enforced |
| `WorkflowRequiresBudgets` | `workflow_scaffolded => budgets_recorded` | `setup_phase >= 5 => setup_phase >= 4` | retained, now structurally enforced |
| `ProjectChoosesKnownSpecRoot` | `project_scaffolded => spec_root \in SpecRoots` | `setup_phase >= 3 => spec_root \in SpecRoots` | retained, **still load-bearing** |

### On the four ordering invariants becoming tautologies

`CliInstalledRequiresBuilt`, `WorkflowRequiresProject`, `BudgetsRequireProject`
and `WorkflowRequiresBudgets` become tautologies once the ordinal enforces the
ordering structurally — that is the point of the collapse. They are **retained
by name** in the module and in `MC.cfg` rather than deleted, for two reasons:

1. It follows the precedent MF-020 already set in this module, which kept
   `CurrentRequiresDesired` and `SpecUnitTestsRequireCurrent` as retained
   tautologies over `ticket_phase` after the same kind of collapse.
2. Deleting a named safety property is indistinguishable at review from losing
   it. Retaining it documents that the ordering is still required and is now
   guaranteed by construction rather than by checking.

`ProjectChoosesKnownSpecRoot` is **not** a tautology — it relates
`setup_phase` to the separate `spec_root` variable — and must keep doing real
work.

## Variables and bound — predicted

| | Before | After |
|---|---|---|
| state variables | 12 | 8 |
| declared bound | 1,179,648 | 221,184 |

Bound arithmetic: the five booleans contribute `2^5 = 32`; `setup_phase`
contributes `6`. So `1,179,648 / 32 * 6 = 221,184`.

Note this differs from the `393,216 -> 73,728` figures quoted in the issue.
Those were measured on the pre-MF-011 11-variable model, before
`complexity_gate` (cardinality 3) was added: `393,216 * 3 = 1,179,648` and
`73,728 * 3 = 221,184`. The ratio is identical (5.33x); only the baseline
moved. The on-branch baseline measured for this ticket is authoritative, and
`analyze complexity` independently projects 221,184 from the current model.

## Retention proof obligation

Reachable distinct states and search depth must be **unchanged** by this
collapse: 2,923 distinct at depth 23. Generated states must also hold at
18,720 — a drop in generated at constant distinct would be the self-loop
deletion signature, which is a red flag rather than a win.
