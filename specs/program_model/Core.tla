------------------------------- MODULE Core -------------------------------
\* MF-023: shared vocabulary for the decomposed views.
\*
\* Core carries NO variables. It holds the constants, the lifecycle ordinals,
\* and the command-result constructor that Internal and External both need.
\* Keeping it variable-free is what makes the two views composable: External
\* EXTENDS Internal EXTENDS Core, so a name defined here means the same thing
\* in both views by construction rather than by convention.
\*
\* This module exists because `spec_manifest.yaml` has pointed at
\* `../program_model/Core.tla` since the epic began while the file was absent,
\* and nothing failed. See results/findings.md, FINDING 3.
EXTENDS Naturals, FiniteSets, TLC

CONSTANTS
  SpecRoots,
  Tickets,
  NoRoot,
  NoReason

\* MF-022: bootstrap setup phase as a single ordinal rather than five parallel
\* booleans. 0 = nothing built, 1 = cli built, 2 = cli installed,
\* 3 = project scaffolded, 4 = budgets recorded, 5 = workflow scaffolded. The
\* old booleans (cli_built, cli_installed, project_scaffolded,
\* budgets_recorded, workflow_scaffolded) were pinned into a strict total order
\* by their own action guards, so only 6 of their 32 combinations were ever
\* reachable; the ordinal represents exactly the reachable set. Read cli_built
\* as >= 1, cli_installed as >= 2, project_scaffolded as >= 3,
\* budgets_recorded as >= 4, and workflow_scaffolded as >= 5.
SetupNothingBuilt     == 0
SetupCliBuilt         == 1
SetupCliInstalled     == 2
SetupProjectScaffold  == 3
SetupBudgetsRecorded  == 4
SetupWorkflowScaffold == 5

SetupPhases == SetupNothingBuilt..SetupWorkflowScaffold

\* MF-025: the whole per-ticket lifecycle as a single ordinal. This subsumes
\* MF-020's ticket_phase together with the two membership sets it lived
\* alongside. active_tickets (SUBSET Tickets), closed_tickets (SUBSET Tickets)
\* and ticket_phase ([Tickets -> 0..3]) were not three independent facts: they
\* were one lifecycle recorded three ways.
\*
\*   0  not yet opened
\*   1  active, phase 0 (opened)
\*   2  active, phase 1 (desired model updated)
\*   3  active, phase 2 (current model updated)
\*   4  active, phase 3 (spec-unit tests passed)
\*   5  closed
\*
\* Why the collapse is exact rather than a packing trick:
\*   - OpenTicket guarded on the ticket being in NEITHER set, so a ticket is
\*     never reopened and the lifecycle is monotonic.
\*   - CloseTicket left ticket_phase UNCHANGED, so a closed ticket retains
\*     phase 3. There is no closed-with-some-other-phase state to represent.
\*   - NoOpenClosedOverlap already forbade being both active and closed.
\* Of the 8 x 8 x 64 = 4,096 declared combinations, exactly six per-ticket
\* combinations were reachable and they were totally ordered. TLC confirmed
\* both directions before the collapse: no seventh combination occurs in any
\* reachable state, and each of the six is individually reachable. The ordinal
\* therefore represents the reachable set exactly -- it neither drops a
\* reachable state nor admits an unreachable one.
TicketUnopened            == 0
TicketOpened              == 1
TicketDesiredReady        == 2
TicketCurrentReady        == 3
TicketSpecUnitTestsPassed == 4
TicketClosed              == 5

TicketStates == TicketUnopened..TicketClosed

\* The verdict domains of the four oracles. Named here rather than inlined so
\* that Internal's TypeInvariant, External's channel projection, and the
\* manifest's justification table all read the same set.
ComplexityVerdicts == {"unknown", "pass", "fail"}
CorpusVerdicts     == {"unknown", "pass", "fail"}
EffectVerdicts     == {"unknown", "clean", "gaps", "dead_surface", "unobservable"}
KillTestVerdicts   == {"unknown", "pass", "below_floor", "incomplete_catalog"}

\* The observable shape the CLI writes to its caller. Defined in Core because
\* External constructs it and Internal's action comments refer to it, but note
\* that only External carries the VARIABLE that holds one.
CommandResult(ok, reason, nextStep) ==
  [accepted |-> ok, reason |-> reason, next |-> nextStep]

=============================================================================
