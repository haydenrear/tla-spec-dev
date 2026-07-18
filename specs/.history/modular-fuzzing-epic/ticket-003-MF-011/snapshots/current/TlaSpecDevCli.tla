----------------------------- MODULE TlaSpecDevCli -----------------------------
EXTENDS Naturals, FiniteSets, TLC

CONSTANTS
  SpecRoots,
  Tickets,
  NoRoot,
  NoReason

\* MF-020: ticket lifecycle phase as a single ordinal rather than three
\* parallel booleans. 0 = opened, 1 = desired model updated, 2 = current model
\* updated, 3 = spec-unit tests passed. The old booleans were pinned to a strict
\* total order by CurrentRequiresDesired / SpecUnitTestsRequireCurrent, so only
\* 4 of their 8 combinations were ever reachable; the ordinal represents exactly
\* the reachable set. Read desired_ready as >= 1, current_ready as >= 2, and
\* spec_unit_tests_passed as >= 3.
VARIABLES
  cli_built,
  cli_installed,
  spec_root,
  project_scaffolded,
  budgets_recorded,
  workflow_scaffolded,
  active_tickets,
  ticket_phase,
  closed_tickets,
  lastCommand,
  result,
  complexity_gate

vars ==
  << cli_built,
     cli_installed,
     spec_root,
     project_scaffolded,
     budgets_recorded,
     workflow_scaffolded,
     active_tickets,
     ticket_phase,
     closed_tickets,
     lastCommand,
     result,
     complexity_gate >>

CommandResult(ok, reason, nextStep) ==
  [accepted |-> ok, reason |-> reason, next |-> nextStep]

Init ==
  /\ cli_built = FALSE
  /\ cli_installed = FALSE
  /\ spec_root = NoRoot
  /\ project_scaffolded = FALSE
  /\ budgets_recorded = FALSE
  /\ workflow_scaffolded = FALSE
  /\ active_tickets = {}
  /\ ticket_phase = [t \in Tickets |-> 0]
  /\ closed_tickets = {}
  /\ lastCommand = "Init"
  /\ result = CommandResult(TRUE, NoReason, "BuildSkillCli")
  /\ complexity_gate = "unknown"

\* The skill ships one local command built from Python entrypoint code.
\* @command BuildSkillCli
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.build_skill_cli
BuildSkillCli ==
  /\ ~cli_built
  /\ cli_built' = TRUE
  /\ lastCommand' = "BuildSkillCli"
  /\ result' = CommandResult(TRUE, NoReason, "InstallLocalCli")
  /\ UNCHANGED << cli_installed,
                  spec_root,
                  project_scaffolded,
                  budgets_recorded,
                  workflow_scaffolded,
                  active_tickets,
                  ticket_phase,
                  closed_tickets,
                  complexity_gate >>

\* The local environment can invoke `tla-spec-dev ...` after install.
\* @command InstallLocalCli
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.install_local_cli
InstallLocalCli ==
  /\ cli_built
  /\ ~cli_installed
  /\ cli_installed' = TRUE
  /\ lastCommand' = "InstallLocalCli"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev scaffold project")
  /\ UNCHANGED << cli_built,
                  spec_root,
                  project_scaffolded,
                  budgets_recorded,
                  workflow_scaffolded,
                  active_tickets,
                  ticket_phase,
                  closed_tickets,
                  complexity_gate >>

\* CLI: `tla-spec-dev --spec-root <root> scaffold project`
\* Creates the accepted `program_model` baseline only.
\* @command ScaffoldProject
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.scaffold_project
ScaffoldProject(root) ==
  /\ cli_installed
  /\ root \in SpecRoots
  /\ ~project_scaffolded
  /\ spec_root' = root
  /\ project_scaffolded' = TRUE
  /\ lastCommand' = "tla-spec-dev scaffold project"
  /\ result' = CommandResult(TRUE, NoReason, "RecordBudgets")
  /\ UNCHANGED << cli_built,
                  cli_installed,
                  budgets_recorded,
                  workflow_scaffolded,
                  active_tickets,
                  ticket_phase,
                  closed_tickets,
                  complexity_gate >>

\* CLI: scaffold emits a `budgets:` block into spec_manifest.yaml and
\* instructs the agent to propose the documented defaults to the user, ask
\* which to adjust for this program, and record a one-line rationale per
\* changed value. Budgets are established before any generation action, so
\* every downstream gate reads them from the manifest.
\* @command RecordBudgets
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.record_budgets
RecordBudgets(root) ==
  /\ cli_installed
  /\ project_scaffolded
  /\ root = spec_root
  /\ ~budgets_recorded
  /\ budgets_recorded' = TRUE
  /\ lastCommand' = "RecordBudgets"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev scaffold workflow")
  /\ UNCHANGED << cli_built,
                  cli_installed,
                  spec_root,
                  project_scaffolded,
                  workflow_scaffolded,
                  active_tickets,
                  ticket_phase,
                  closed_tickets,
                  complexity_gate >>

\* CLI: `tla-spec-dev --spec-root <root> scaffold workflow`
\* Creates project `current/`, `desired_program_model/`, and ticket plan.
\* @command ScaffoldWorkflow
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.scaffold_workflow
ScaffoldWorkflow(root) ==
  /\ cli_installed
  /\ project_scaffolded
  /\ budgets_recorded
  /\ root = spec_root
  /\ ~workflow_scaffolded
  /\ workflow_scaffolded' = TRUE
  /\ lastCommand' = "tla-spec-dev scaffold workflow"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev open ticket <ticket>")
  /\ UNCHANGED << cli_built,
                  cli_installed,
                  spec_root,
                  project_scaffolded,
                  budgets_recorded,
                  active_tickets,
                  ticket_phase,
                  closed_tickets,
                  complexity_gate >>

\* CLI: `tla-spec-dev --spec-root <root> open ticket <ticket-name>`
\* Creates ticket-local current/desired/results/Test Graph workspace.
\* @command OpenTicket
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.open_ticket
OpenTicket(root, ticket) ==
  /\ cli_installed
  /\ workflow_scaffolded
  /\ root = spec_root
  /\ ticket \in Tickets
  /\ ticket \notin active_tickets
  /\ ticket \notin closed_tickets
  /\ active_tickets' = active_tickets \cup {ticket}
  /\ ticket_phase' = [ticket_phase EXCEPT ![ticket] = 0]
  /\ lastCommand' = "tla-spec-dev open ticket"
  /\ result' = CommandResult(TRUE, NoReason, "Update ticket desired TLA+ first")
  /\ UNCHANGED << cli_built,
                  cli_installed,
                  spec_root,
                  project_scaffolded,
                  budgets_recorded,
                  workflow_scaffolded,
                  closed_tickets,
                  complexity_gate >>

\* Agent step: update ticket desired model, adapters, and Test Graph bindings.
\* This is intentionally modeled because the CLI must print this instruction.
\* @command UpdateTicketDesired
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.update_ticket_desired
UpdateTicketDesired(ticket) ==
  /\ ticket \in active_tickets
  /\ ticket_phase[ticket] = 0
  /\ ticket_phase' = [ticket_phase EXCEPT ![ticket] = 1]
  /\ lastCommand' = "UpdateTicketDesired"
  /\ result' = CommandResult(TRUE, NoReason, "Implement ticket and update current")
  /\ UNCHANGED << cli_built,
                  cli_installed,
                  spec_root,
                  project_scaffolded,
                  budgets_recorded,
                  workflow_scaffolded,
                  active_tickets,
                  closed_tickets,
                  complexity_gate >>

\* Agent step: production implementation has landed and current matches desired.
\* @command UpdateTicketCurrent
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.update_ticket_current
UpdateTicketCurrent(ticket) ==
  /\ ticket \in active_tickets
  /\ ticket_phase[ticket] = 1
  /\ ticket_phase' = [ticket_phase EXCEPT ![ticket] = 2]
  /\ lastCommand' = "UpdateTicketCurrent"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev run spec-unit-tests")
  /\ UNCHANGED << cli_built,
                  cli_installed,
                  spec_root,
                  project_scaffolded,
                  budgets_recorded,
                  workflow_scaffolded,
                  active_tickets,
                  closed_tickets,
                  complexity_gate >>

\* CLI: `tla-spec-dev --spec-root <root> analyze complexity <spec> <cfg>`
\* MF-011: measures the model against the manifest budgets before any
\* generation runs. The gate is a fact about the whole program, not about one
\* ticket, so it is a single global variable rather than a per-ticket map.
\* "unknown" means the model has never been analyzed, and in that state case
\* generation has no enabled transition at all -- an unanalyzed model is
\* exactly the one that exhausts TLC instead of finishing.
\* The outcome is nondeterministic here because it depends on the model being
\* analyzed, which is outside this state machine.
\* @command AnalyzeComplexity
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.analyze_complexity
AnalyzeComplexity(root) ==
  /\ cli_installed
  /\ project_scaffolded
  /\ budgets_recorded
  /\ root = spec_root
  /\ complexity_gate' \in {"pass", "fail"}
  /\ lastCommand' = "tla-spec-dev analyze complexity"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev run spec-unit-tests")
  /\ UNCHANGED << cli_built,
                  cli_installed,
                  spec_root,
                  project_scaffolded,
                  budgets_recorded,
                  workflow_scaffolded,
                  active_tickets,
                  ticket_phase,
                  closed_tickets >>

\* CLI: `tla-spec-dev --spec-root <root> run spec-unit-tests`
\* Runs generated/adapted spec-unit validation for ticket current.
\* MF-011: case generation runs only behind the complexity gate. A passing
\* gate enables it outright; a failing gate enables it only under the explicit
\* `--allow-over-budget` override, modeled as the `override` input. When the
\* gate is "unknown" no transition is enabled -- that absence IS the refusal.
\* @command RunSpecUnitTests
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.run_spec_unit_tests
RunSpecUnitTests(root, ticket, override) ==
  /\ cli_installed
  /\ root = spec_root
  /\ ticket \in active_tickets
  /\ ticket_phase[ticket] >= 2
  /\ \/ complexity_gate = "pass"
     \/ /\ complexity_gate = "fail"
        /\ override
  /\ ticket_phase' = [ticket_phase EXCEPT ![ticket] = 3]
  /\ lastCommand' = "tla-spec-dev run spec-unit-tests"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev close ticket <ticket>")
  /\ UNCHANGED << cli_built,
                  cli_installed,
                  spec_root,
                  project_scaffolded,
                  budgets_recorded,
                  workflow_scaffolded,
                  active_tickets,
                  closed_tickets,
                  complexity_gate >>

\* CLI: `tla-spec-dev --spec-root <root> close ticket <ticket-name>`
\* Closes ticket only after current == desired and spec-unit tests passed.
\* @command CloseTicket
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.close_ticket
CloseTicket(root, ticket) ==
  /\ cli_installed
  /\ root = spec_root
  /\ ticket \in active_tickets
  /\ ticket_phase[ticket] = 3
  /\ active_tickets' = active_tickets \ {ticket}
  /\ closed_tickets' = closed_tickets \cup {ticket}
  /\ lastCommand' = "tla-spec-dev close ticket"
  /\ result' = CommandResult(TRUE, NoReason, "Open next ticket or close workflow")
  /\ UNCHANGED << cli_built,
                  cli_installed,
                  spec_root,
                  project_scaffolded,
                  budgets_recorded,
                  workflow_scaffolded,
                  ticket_phase,
                  complexity_gate >>

Stutter ==
  UNCHANGED vars

Next ==
  \/ BuildSkillCli
  \/ InstallLocalCli
  \/ \E root \in SpecRoots:
      ScaffoldProject(root)
  \/ \E root \in SpecRoots:
      RecordBudgets(root)
  \/ \E root \in SpecRoots:
      ScaffoldWorkflow(root)
  \/ \E root \in SpecRoots, ticket \in Tickets:
      OpenTicket(root, ticket)
  \/ \E ticket \in Tickets:
      UpdateTicketDesired(ticket)
  \/ \E ticket \in Tickets:
      UpdateTicketCurrent(ticket)
  \/ \E root \in SpecRoots:
      AnalyzeComplexity(root)
  \/ \E root \in SpecRoots, ticket \in Tickets, override \in BOOLEAN:
      RunSpecUnitTests(root, ticket, override)
  \/ \E root \in SpecRoots, ticket \in Tickets:
      CloseTicket(root, ticket)
  \/ Stutter

TypeInvariant ==
  /\ cli_built \in BOOLEAN
  /\ cli_installed \in BOOLEAN
  /\ spec_root \in SpecRoots \cup {NoRoot}
  /\ project_scaffolded \in BOOLEAN
  /\ budgets_recorded \in BOOLEAN
  /\ workflow_scaffolded \in BOOLEAN
  /\ active_tickets \subseteq Tickets
  /\ closed_tickets \subseteq Tickets
  /\ ticket_phase \in [Tickets -> 0..3]
  /\ complexity_gate \in {"unknown", "pass", "fail"}

CliInstalledRequiresBuilt ==
  cli_installed => cli_built

WorkflowRequiresProject ==
  workflow_scaffolded => project_scaffolded

\* Budgets are per-program state established during scaffolding.
BudgetsRequireProject ==
  budgets_recorded => project_scaffolded

\* Every generation action runs behind recorded budgets: the workflow (and
\* therefore every ticket, spec-unit run, and close) cannot be scaffolded
\* until the budgets block exists in the manifest.
WorkflowRequiresBudgets ==
  workflow_scaffolded => budgets_recorded

ProjectChoosesKnownSpecRoot ==
  project_scaffolded => spec_root \in SpecRoots

NoOpenClosedOverlap ==
  active_tickets \cap closed_tickets = {}

CurrentRequiresDesired ==
  \A ticket \in Tickets:
    ticket_phase[ticket] >= 2 => ticket_phase[ticket] >= 1

SpecUnitTestsRequireCurrent ==
  \A ticket \in Tickets:
    ticket_phase[ticket] >= 3 => ticket_phase[ticket] >= 2

\* MF-011: no case generation ever runs against an unanalyzed model. Reaching
\* phase 3 means spec-unit cases were generated and run, which is only possible
\* once analyze complexity has recorded a verdict -- pass, or fail plus the
\* explicit override. The gate is never silently skipped.
SpecUnitTestsRequireAnalyzedGate ==
  (\E ticket \in Tickets: ticket_phase[ticket] >= 3)
    => complexity_gate /= "unknown"

ClosedTicketsPassedSpecUnitTests ==
  \A ticket \in closed_tickets:
    ticket_phase[ticket] >= 3

Spec ==
  Init /\ [][Next]_vars

=============================================================================
