----------------------------- MODULE External -----------------------------
\* MF-023: the EXTERNAL view of the tla-spec-dev CLI.
\*
\* External is the observable channel: what a caller invoking `tla-spec-dev`
\* actually sees. It adds exactly two variables to Internal -- `lastCommand`
\* (which command was invoked) and `result` (the accepted/reason/next record
\* printed back) -- and wraps each internal transition with the channel write
\* that the CLI performs when that command runs.
\*
\* WHY THESE TWO AND NOTHING ELSE. `analyze complexity` on the pre-split
\* module reported modularity Q = 0.012 over the variable interaction graph,
\* i.e. no better than a random partition, and proposed
\*   C1: kill_test, lastCommand, result, setup_phase, spec_root, ticket_state
\*   C2: complexity_gate, corpus_gate, effect_conformance
\* which leaves C1 at 14 actions -- exactly the component that was already
\* failing max_component_actions 8. The tool's proposed cut does not fix the
\* budget the same tool reports as failing. That proposal is therefore
\* OVERRIDDEN, with the justification recorded in results/findings.md
\* (FINDING 2) and in results/cut-decision.md. The override uses the tool's own
\* MEASURED evidence rather than intuition: its R/W matrix is the thing that
\* shows `lastCommand` and `result` are the only two variables written by all
\* 14 actions, which is precisely why Q collapsed toward zero.
\*
\* NO HiddenInternalProgress. The shipped example's External.tla carries a
\* `HiddenInternalProgress` disjunct so that internal state can advance without
\* a client request -- correct there, because a background fulfillment worker
\* exists. It is deliberately ABSENT here, and its absence is what makes the
\* retention proof exact. In a CLI there is no such thing as internal progress
\* without an invocation: every state change is caused by a command, and every
\* command writes the channel. Adding the disjunct would introduce reachable
\* states the pre-split model does not have, which would show up as a larger
\* distinct-state count than the 231,621 baseline. See results/retention.md.
EXTENDS Internal

VARIABLES
  lastCommand,
  result

ExternalVars ==
  << setup_phase,
     spec_root,
     ticket_state,
     lastCommand,
     result,
     complexity_gate,
     corpus_gate,
     effect_conformance,
     kill_test >>

ChannelVars == << lastCommand, result >>

\* The channel write every command performs.
Emit(command, ok, reason, nextStep) ==
  /\ lastCommand' = command
  /\ result' = CommandResult(ok, reason, nextStep)

ExternalInit ==
  /\ InternalInit
  /\ lastCommand = "Init"
  /\ result = CommandResult(TRUE, NoReason, "BuildSkillCli")

\* @command BuildSkillCli
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.cli_artifact
InvokeBuildSkillCli ==
  /\ BuildSkillCli
  /\ Emit("BuildSkillCli", TRUE, NoReason, "InstallLocalCli")

\* @command InstallLocalCli
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.cli_artifact
InvokeInstallLocalCli ==
  /\ InstallLocalCli
  /\ Emit("InstallLocalCli", TRUE, NoReason, "tla-spec-dev scaffold project")

\* @command ScaffoldProject
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.spec_tree
InvokeScaffoldProject(root) ==
  /\ ScaffoldProject(root)
  /\ Emit("tla-spec-dev scaffold project", TRUE, NoReason, "RecordBudgets")

\* @command RecordBudgets
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.spec_tree
InvokeRecordBudgets(root) ==
  /\ RecordBudgets(root)
  /\ Emit("RecordBudgets", TRUE, NoReason, "tla-spec-dev scaffold workflow")

\* @command ScaffoldWorkflow
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.spec_tree
InvokeScaffoldWorkflow(root) ==
  /\ ScaffoldWorkflow(root)
  /\ Emit("tla-spec-dev scaffold workflow", TRUE, NoReason, "tla-spec-dev open ticket <ticket>")

\* @command OpenTicket
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.spec_tree
InvokeOpenTicket(root, ticket) ==
  /\ OpenTicket(root, ticket)
  /\ Emit("tla-spec-dev open ticket", TRUE, NoReason, "Update ticket desired TLA+ first")

\* @command UpdateTicketDesired
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.spec_tree
InvokeUpdateTicketDesired(ticket) ==
  /\ UpdateTicketDesired(ticket)
  /\ Emit("UpdateTicketDesired", TRUE, NoReason, "Implement ticket and update current")

\* @command UpdateTicketCurrent
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.spec_tree
InvokeUpdateTicketCurrent(ticket) ==
  /\ UpdateTicketCurrent(ticket)
  /\ Emit("UpdateTicketCurrent", TRUE, NoReason, "tla-spec-dev run spec-unit-tests")

\* @command AnalyzeComplexity
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.evidence_report
\* @port TlaSpecDevCliPort.tlc_process
InvokeAnalyzeComplexity(root) ==
  /\ AnalyzeComplexity(root)
  /\ Emit("tla-spec-dev analyze complexity", TRUE, NoReason, "tla-spec-dev run spec-unit-tests")

\* @command AnalyzeCorpus
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.evidence_report
InvokeAnalyzeCorpus(root) ==
  /\ AnalyzeCorpus(root)
  /\ Emit("tla-spec-dev analyze corpus", TRUE, NoReason, "Fix the diagram, or raise the cap with a rationale")

\* The four-way CASE below is the reason `result` was NOT projected away when
\* `analyze complexity` suggested it. Each verdict selects a DIFFERENT
\* `result.next`, and the pre-split module's own comments justify keeping
\* "gaps", "dead_surface" and "unobservable" apart precisely because that
\* distinction is externally visible here. Deleting this variable would have
\* removed the evidence for keeping the verdicts distinct.
\* @command RunEffectConformance
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.evidence_report
InvokeRunEffectConformance(root) ==
  /\ RunEffectConformance(root)
  /\ lastCommand' = "tla-spec-dev run effect-conformance"
  /\ result' = CASE effect_conformance' = "clean"
                      -> CommandResult(TRUE, NoReason, "tla-spec-dev run spec-unit-tests")
                 [] effect_conformance' = "gaps"
                      -> CommandResult(FALSE, NoReason, "Declare the port, or change the program so it no longer emits the effect")
                 [] effect_conformance' = "unobservable"
                      -> CommandResult(FALSE, NoReason, "Run the target in-process, or check that boundary another way -- this oracle does not cover it")
                 [] OTHER
                      -> CommandResult(FALSE, NoReason, "Remove the dead port, or add a case that exercises it")

\* @command RunKillTest
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.evidence_report
\* @port TlaSpecDevCliPort.test_process
InvokeRunKillTest(root) ==
  /\ RunKillTest(root)
  /\ lastCommand' = "tla-spec-dev run kill-test"
  /\ result' = CASE kill_test' = "pass"
                      -> CommandResult(TRUE, NoReason, "tla-spec-dev close ticket <ticket>")
                 [] kill_test' = "below_floor"
                      -> CommandResult(FALSE, NoReason, "Refine the variable or action named by each surviving mutant until it dies -- the floor is not waivable")
                 [] OTHER
                      -> CommandResult(FALSE, NoReason, "Seed a fault for every declared port and invariant that has none")

\* @command RunSpecUnitTests
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.test_process
\* @port TlaSpecDevCliPort.spec_tree
InvokeRunSpecUnitTests(root, ticket, override) ==
  /\ RunSpecUnitTests(root, ticket, override)
  /\ lastCommand' = "tla-spec-dev run spec-unit-tests"
  /\ result' = CASE effect_conformance' = "gaps"
                      -> CommandResult(FALSE, NoReason, "Declare the port, or change the program so it no longer emits the effect")
                 [] effect_conformance' = "unobservable"
                      -> CommandResult(FALSE, NoReason, "Run the target in-process, or check that boundary another way -- this oracle does not cover it")
                 [] effect_conformance' = "dead_surface"
                      -> CommandResult(FALSE, NoReason, "Remove the dead port, or add a case that exercises it")
                 [] corpus_gate' = "fail"
                      -> CommandResult(FALSE, NoReason, "Fix the diagram, or raise the cap with a rationale")
                 [] OTHER
                      -> CommandResult(TRUE, NoReason, "tla-spec-dev close ticket <ticket>")

\* @command CloseTicket
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.spec_tree
InvokeCloseTicket(root, ticket) ==
  /\ CloseTicket(root, ticket)
  /\ Emit("tla-spec-dev close ticket", TRUE, NoReason, "Open next ticket or close workflow")

\* MF-023: removed for the reason recorded in Internal.tla -- `[][N]_v` already
\* permits stuttering, and the explicit disjunct only served to emit one
\* uncoverable spec case per reachable state.

ExternalNext ==
  \/ InvokeBuildSkillCli
  \/ InvokeInstallLocalCli
  \/ \E root \in SpecRoots:
      InvokeScaffoldProject(root)
  \/ \E root \in SpecRoots:
      InvokeRecordBudgets(root)
  \/ \E root \in SpecRoots:
      InvokeScaffoldWorkflow(root)
  \/ \E root \in SpecRoots, ticket \in Tickets:
      InvokeOpenTicket(root, ticket)
  \/ \E ticket \in Tickets:
      InvokeUpdateTicketDesired(ticket)
  \/ \E ticket \in Tickets:
      InvokeUpdateTicketCurrent(ticket)
  \/ \E root \in SpecRoots:
      InvokeAnalyzeComplexity(root)
  \/ \E root \in SpecRoots:
      InvokeAnalyzeCorpus(root)
  \/ \E root \in SpecRoots:
      InvokeRunEffectConformance(root)
  \/ \E root \in SpecRoots:
      InvokeRunKillTest(root)
  \/ \E root \in SpecRoots, ticket \in Tickets, override \in BOOLEAN:
      InvokeRunSpecUnitTests(root, ticket, override)
  \/ \E root \in SpecRoots, ticket \in Tickets:
      InvokeCloseTicket(root, ticket)

\* The channel carries no bounded domain of its own: `lastCommand` ranges over
\* the command strings and `result` over records built from them, exactly as in
\* the pre-split module where both were reported by analyze complexity as
\* "unconstrained by TypeInvariant -- excluded from the bound". External
\* therefore adds ZERO to the declared static bound, and Internal's
\* TypeInvariant (inherited through EXTENDS) is the whole of the bounded
\* constraint. This is stated explicitly because analyze complexity, run on
\* External.tla alone, cannot see it: the tool does not follow EXTENDS, so it
\* reports External's bound as 1 over 0 bounded dimensions. See
\* results/findings.md FINDING 1.
ExternalInvariant ==
  /\ InternalInvariant
  /\ result.accepted \in BOOLEAN
  /\ result.next /= NoReason

Spec == ExternalInit /\ [][ExternalNext]_ExternalVars

=============================================================================
