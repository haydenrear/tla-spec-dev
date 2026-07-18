----------------------------- MODULE TlaSpecDevCli -----------------------------
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
  result,
  complexity_gate,
  corpus_gate

vars ==
  << setup_phase,
     spec_root,
     active_tickets,
     ticket_phase,
     closed_tickets,
     lastCommand,
     result,
     complexity_gate,
     corpus_gate >>

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
  /\ complexity_gate = "unknown"
  /\ corpus_gate = "unknown"

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
                  closed_tickets,
                  complexity_gate,
                  corpus_gate >>

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
                  closed_tickets,
                  complexity_gate,
                  corpus_gate >>

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
                  closed_tickets,
                  complexity_gate,
                  corpus_gate >>

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
                  closed_tickets,
                  complexity_gate,
                  corpus_gate >>

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
                  closed_tickets,
                  complexity_gate,
                  corpus_gate >>

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
                  closed_tickets,
                  complexity_gate,
                  corpus_gate >>

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
                  closed_tickets,
                  complexity_gate,
                  corpus_gate >>

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
                  closed_tickets,
                  complexity_gate,
                  corpus_gate >>

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
  /\ setup_phase >= 4
  /\ root = spec_root
  /\ complexity_gate' \in {"pass", "fail"}
  /\ lastCommand' = "tla-spec-dev analyze complexity"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev run spec-unit-tests")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  active_tickets,
                  ticket_phase,
                  closed_tickets,
                  corpus_gate >>

\* CLI: `tla-spec-dev --spec-root <root> analyze corpus <cases-dir>`
\* MF-014: measures the GENERATED CORPUS against the manifest case caps
\* (max_internal_cases_per_component, max_external_cases_per_action). Like
\* complexity_gate this is a fact about the whole program rather than about one
\* ticket, so it is a single global variable.
\*
\* Note what is deliberately ABSENT: there is no override input, and there is
\* no transition that reduces a case count. Cases are never dropped, filtered,
\* sampled, or truncated to satisfy a budget -- not silently and not with a
\* recorded drop rule. Over cap the command reports the distribution per
\* (action, label class), which strata dominate, which are starved, and what
\* varies across the redundant group, then exits nonzero. The only two ways to
\* reach "pass" are to FIX THE DIAGRAM so the redundant cases are never
\* generated, or to RAISE THE CAP in the manifest with a recorded one-line
\* rationale. Both are re-measurements, which is why this action simply
\* records a fresh verdict.
\* @command AnalyzeCorpus
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.analyze_corpus
AnalyzeCorpus(root) ==
  /\ setup_phase >= 4
  /\ root = spec_root
  /\ corpus_gate' \in {"pass", "fail"}
  /\ lastCommand' = "tla-spec-dev analyze corpus"
  /\ result' = CommandResult(TRUE, NoReason, "Fix the diagram, or raise the cap with a rationale")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  active_tickets,
                  ticket_phase,
                  closed_tickets,
                  complexity_gate >>

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
  /\ setup_phase >= 2
  /\ root = spec_root
  /\ ticket \in active_tickets
  /\ ticket_phase[ticket] >= 2
  /\ \/ complexity_gate = "pass"
     \/ /\ complexity_gate = "fail"
        /\ override
  \* MF-014: generation produces the corpus, then the case caps are measured
  \* over it. The corpus is complete either way -- the gate refuses, it never
  \* trims -- so a failing verdict advances nothing and reports instead.
  \* `override` is deliberately NOT consulted here: the complexity gate has an
  \* explicit --allow-over-budget escape, and the case caps have none. Raising
  \* the cap with a recorded rationale is the accept path, and that is a
  \* different verdict rather than a bypassed one.
  /\ corpus_gate' \in {"pass", "fail"}
  /\ ticket_phase' = IF corpus_gate' = "pass"
                       THEN [ticket_phase EXCEPT ![ticket] = 3]
                       ELSE ticket_phase
  /\ lastCommand' = "tla-spec-dev run spec-unit-tests"
  /\ result' = IF corpus_gate' = "pass"
                 THEN CommandResult(TRUE, NoReason, "tla-spec-dev close ticket <ticket>")
                 ELSE CommandResult(FALSE, NoReason, "Fix the diagram, or raise the cap with a rationale")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  active_tickets,
                  closed_tickets,
                  complexity_gate >>

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
                  ticket_phase,
                  complexity_gate,
                  corpus_gate >>

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
  \/ \E root \in SpecRoots:
      AnalyzeCorpus(root)
  \/ \E root \in SpecRoots, ticket \in Tickets, override \in BOOLEAN:
      RunSpecUnitTests(root, ticket, override)
  \/ \E root \in SpecRoots, ticket \in Tickets:
      CloseTicket(root, ticket)
  \/ Stutter

TypeInvariant ==
  /\ setup_phase \in 0..5
  /\ spec_root \in SpecRoots \cup {NoRoot}
  /\ active_tickets \subseteq Tickets
  /\ closed_tickets \subseteq Tickets
  /\ ticket_phase \in [Tickets -> 0..3]
  /\ complexity_gate \in {"unknown", "pass", "fail"}
  /\ corpus_gate \in {"unknown", "pass", "fail"}

\* MF-022: the four bootstrap ordering invariants below are retained by name
\* even though the setup_phase ordinal now enforces them structurally, so each
\* is a tautology. This follows the precedent MF-020 set for ticket_phase:
\* deleting a named safety property is indistinguishable at review from losing
\* it, and retaining it documents that the ordering is still required and is
\* now guaranteed by construction rather than by checking.
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

\* Not a tautology: this relates setup_phase to the separate spec_root
\* variable and still does real work.
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

\* MF-011: no case generation ever runs against an unanalyzed model. Reaching
\* phase 3 means spec-unit cases were generated and run, which is only possible
\* once analyze complexity has recorded a verdict -- pass, or fail plus the
\* explicit override. The gate is never silently skipped.
SpecUnitTestsRequireAnalyzedGate ==
  (\E ticket \in Tickets: ticket_phase[ticket] >= 3)
    => complexity_gate /= "unknown"

\* MF-014: no ticket ever passes spec-unit tests without its generated corpus
\* having been measured against the case caps. Reaching phase 3 means cases
\* were generated and run, and RunSpecUnitTests records a cap verdict on every
\* such transition -- so a corpus that was never measured cannot be behind a
\* passing ticket. The companion property, that a case is never removed to make
\* the verdict "pass", is structural rather than checkable here: no action in
\* this module reduces a case count, and no override input reaches the cap.
SpecUnitTestsRequireMeasuredCorpus ==
  (\E ticket \in Tickets: ticket_phase[ticket] >= 3)
    => corpus_gate /= "unknown"

ClosedTicketsPassedSpecUnitTests ==
  \A ticket \in closed_tickets:
    ticket_phase[ticket] >= 3

Spec ==
  Init /\ [][Next]_vars

=============================================================================
