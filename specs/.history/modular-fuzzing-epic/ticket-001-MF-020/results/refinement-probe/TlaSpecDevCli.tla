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
  setup_phase,
  spec_root,
  active_tickets,
  ticket_phase,
  closed_tickets,
  lastCommand,
  result

vars ==
  << setup_phase,
     spec_root,
     active_tickets,
     ticket_phase,
     closed_tickets,
     lastCommand,
     result >>

CommandResult(ok, reason, nextStep) ==
  [accepted |-> ok, reason |-> reason, next |-> nextStep]

Init ==
  /\ setup_phase = 0
  /\ spec_root = NoRoot
  /\ active_tickets = {}
  /\ ticket_phase = [t \in Tickets |-> 0]
  /\ closed_tickets = {}
  /\ lastCommand = "Init"
  /\ result = CommandResult(TRUE, NoReason, "BuildSkillCli")

\* The skill ships one local command built from Python entrypoint code.
\* @command BuildSkillCli
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.build_skill_cli
BuildSkillCli ==
  /\ setup_phase = 0
  /\ setup_phase' = 1
  /\ lastCommand' = "BuildSkillCli"
  /\ result' = CommandResult(TRUE, NoReason, "InstallLocalCli")
  /\ UNCHANGED << spec_root,
                  active_tickets,
                  ticket_phase,
                  closed_tickets >>

\* The local environment can invoke `tla-spec-dev ...` after install.
\* @command InstallLocalCli
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.install_local_cli
InstallLocalCli ==
  /\ setup_phase = 1
  /\ setup_phase' = 2
  /\ lastCommand' = "InstallLocalCli"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev scaffold project")
  /\ UNCHANGED << spec_root,
                  active_tickets,
                  ticket_phase,
                  closed_tickets >>

\* CLI: `tla-spec-dev --spec-root <root> scaffold project`
\* Creates the accepted `program_model` baseline only.
\* @command ScaffoldProject
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.scaffold_project
ScaffoldProject(root) ==
  /\ setup_phase = 2
  /\ root \in SpecRoots
  /\ spec_root' = root
  /\ setup_phase' = 3
  /\ lastCommand' = "tla-spec-dev scaffold project"
  /\ result' = CommandResult(TRUE, NoReason, "RecordBudgets")
  /\ UNCHANGED << active_tickets,
                  ticket_phase,
                  closed_tickets >>

\* CLI: scaffold emits a `budgets:` block into spec_manifest.yaml and
\* instructs the agent to propose the documented defaults to the user, ask
\* which to adjust for this program, and record a one-line rationale per
\* changed value. Budgets are established before any generation action, so
\* every downstream gate reads them from the manifest.
\* @command RecordBudgets
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.record_budgets
RecordBudgets(root) ==
  /\ setup_phase = 3
  /\ root = spec_root
  /\ setup_phase' = 4
  /\ lastCommand' = "RecordBudgets"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev scaffold workflow")
  /\ UNCHANGED << spec_root,
                  active_tickets,
                  ticket_phase,
                  closed_tickets >>

\* CLI: `tla-spec-dev --spec-root <root> scaffold workflow`
\* Creates project `current/`, `desired_program_model/`, and ticket plan.
\* @command ScaffoldWorkflow
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.scaffold_workflow
ScaffoldWorkflow(root) ==
  /\ setup_phase = 4
  /\ root = spec_root
  /\ setup_phase' = 5
  /\ lastCommand' = "tla-spec-dev scaffold workflow"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev open ticket <ticket>")
  /\ UNCHANGED << spec_root,
                  active_tickets,
                  ticket_phase,
                  closed_tickets >>

\* CLI: `tla-spec-dev --spec-root <root> open ticket <ticket-name>`
\* Creates ticket-local current/desired/results/Test Graph workspace.
\* @command OpenTicket
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.open_ticket
OpenTicket(root, ticket) ==
  /\ setup_phase >= 5
  /\ root = spec_root
  /\ ticket \in Tickets
  /\ ticket \notin active_tickets
  /\ ticket \notin closed_tickets
  /\ active_tickets' = active_tickets \cup {ticket}
  /\ ticket_phase' = [ticket_phase EXCEPT ![ticket] = 0]
  /\ lastCommand' = "tla-spec-dev open ticket"
  /\ result' = CommandResult(TRUE, NoReason, "Update ticket desired TLA+ first")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  closed_tickets >>

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
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  active_tickets,
                  closed_tickets >>

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
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  active_tickets,
                  closed_tickets >>

\* CLI: `tla-spec-dev --spec-root <root> run spec-unit-tests`
\* Runs generated/adapted spec-unit validation for ticket current.
\* @command RunSpecUnitTests
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.run_spec_unit_tests
RunSpecUnitTests(root, ticket) ==
  /\ setup_phase >= 2
  /\ root = spec_root
  /\ ticket \in active_tickets
  /\ ticket_phase[ticket] >= 2
  /\ ticket_phase' = [ticket_phase EXCEPT ![ticket] = 3]
  /\ lastCommand' = "tla-spec-dev run spec-unit-tests"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev close ticket <ticket>")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  active_tickets,
                  closed_tickets >>

\* CLI: `tla-spec-dev --spec-root <root> close ticket <ticket-name>`
\* Closes ticket only after current == desired and spec-unit tests passed.
\* @command CloseTicket
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.close_ticket
CloseTicket(root, ticket) ==
  /\ setup_phase >= 2
  /\ root = spec_root
  /\ ticket \in active_tickets
  /\ ticket_phase[ticket] = 3
  /\ active_tickets' = active_tickets \ {ticket}
  /\ closed_tickets' = closed_tickets \cup {ticket}
  /\ lastCommand' = "tla-spec-dev close ticket"
  /\ result' = CommandResult(TRUE, NoReason, "Open next ticket or close workflow")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  ticket_phase >>

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
  \/ \E root \in SpecRoots, ticket \in Tickets:
      RunSpecUnitTests(root, ticket)
  \/ \E root \in SpecRoots, ticket \in Tickets:
      CloseTicket(root, ticket)
  \/ Stutter

TypeInvariant ==
  /\ setup_phase \in 0..5
  /\ spec_root \in SpecRoots \cup {NoRoot}
  /\ active_tickets \subseteq Tickets
  /\ closed_tickets \subseteq Tickets
  /\ ticket_phase \in [Tickets -> 0..3]

CliInstalledRequiresBuilt ==
  setup_phase >= 2 => setup_phase >= 1

WorkflowRequiresProject ==
  setup_phase >= 5 => setup_phase >= 3

\* Budgets are per-program state established during scaffolding.
BudgetsRequireProject ==
  setup_phase >= 4 => setup_phase >= 3

\* Every generation action runs behind recorded budgets: the workflow (and
\* therefore every ticket, spec-unit run, and close) cannot be scaffolded
\* until the budgets block exists in the manifest.
WorkflowRequiresBudgets ==
  setup_phase >= 5 => setup_phase >= 4

ProjectChoosesKnownSpecRoot ==
  setup_phase >= 3 => spec_root \in SpecRoots

NoOpenClosedOverlap ==
  active_tickets \cap closed_tickets = {}

CurrentRequiresDesired ==
  \A ticket \in Tickets:
    ticket_phase[ticket] >= 2 => ticket_phase[ticket] >= 1

SpecUnitTestsRequireCurrent ==
  \A ticket \in Tickets:
    ticket_phase[ticket] >= 3 => ticket_phase[ticket] >= 2

ClosedTicketsPassedSpecUnitTests ==
  \A ticket \in closed_tickets:
    ticket_phase[ticket] >= 3

Spec ==
  Init /\ [][Next]_vars

=============================================================================
