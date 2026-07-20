----------------------------- MODULE Internal -----------------------------
\* MF-023: the INTERNAL view of the tla-spec-dev CLI.
\*
\* Internal is the workflow state machine: the bootstrap phase, the configured
\* spec root, the per-ticket lifecycle, and the four oracle verdicts. It is
\* everything the CLI *knows*.
\*
\* What Internal deliberately does NOT carry is the observable channel --
\* `lastCommand` and `result`. Those are what the CLI *reports*, and they live
\* in External. That division is not a stylistic one; it is the finding this
\* ticket's `analyze complexity` run produced. On the undecomposed module the
\* variable interaction graph scored modularity Q = 0.012, effectively zero,
\* because `lastCommand` and `result` are written by all 14 actions and so
\* connect every variable to every other. They are the hubs that made the model
\* look indecomposable. Moving them to External is what lets the rest of the
\* model separate at all. See results/findings.md, FINDING 2.
\*
\* Note that the tool's own SUGGESTED MOVE for those two variables was ABSTRACT
\* -- project them away, since no configured invariant reads them. That
\* suggestion is REFUSED here and the reason is recorded in findings.md,
\* FINDING 5: `result.next` is externally-visible CLI output, and six separate
\* comments in the pre-split module justify keeping a verdict distinct
\* precisely BECAUSE it is visible in `result.next`. Deleting the variable that
\* carries that visibility would invalidate the justification for keeping the
\* verdicts apart. Relocating it to External preserves the distinction and
\* still removes the hub from Internal. The tool offered "delete" and had no
\* vocabulary for "relocate".
EXTENDS Core

VARIABLES
  setup_phase,
  spec_root,
  ticket_state,
  complexity_gate,
  corpus_gate,
  effect_conformance,
  kill_test

InternalVars ==
  << setup_phase,
     spec_root,
     ticket_state,
     complexity_gate,
     corpus_gate,
     effect_conformance,
     kill_test >>

\* MF-025: every site that meant "the set of active tickets" still says so.
ActiveTickets == {t \in Tickets : ticket_state[t] \in TicketOpened..TicketSpecUnitTestsPassed}
ClosedTickets == {t \in Tickets : ticket_state[t] = TicketClosed}

InternalInit ==
  /\ setup_phase = SetupNothingBuilt
  /\ spec_root = NoRoot
  /\ ticket_state = [t \in Tickets |-> TicketUnopened]
  /\ complexity_gate = "unknown"
  /\ corpus_gate = "unknown"
  /\ effect_conformance = "unknown"
  /\ kill_test = "unknown"

\* The skill ships one local command built from Python entrypoint code.
\* @command BuildSkillCli
\* @port TlaSpecDevCliPort.cli_artifact
BuildSkillCli ==
  /\ setup_phase = SetupNothingBuilt
  /\ setup_phase' = SetupCliBuilt
  /\ UNCHANGED << spec_root, ticket_state, complexity_gate, corpus_gate,
                  effect_conformance, kill_test >>

\* The local environment can invoke `tla-spec-dev ...` after install.
\* @command InstallLocalCli
\* @port TlaSpecDevCliPort.cli_artifact
InstallLocalCli ==
  /\ setup_phase = SetupCliBuilt
  /\ setup_phase' = SetupCliInstalled
  /\ UNCHANGED << spec_root, ticket_state, complexity_gate, corpus_gate,
                  effect_conformance, kill_test >>

\* CLI: `tla-spec-dev --spec-root <root> scaffold project`
\* Creates the accepted `program_model` baseline only.
\* @command ScaffoldProject
\* @port TlaSpecDevCliPort.spec_tree
ScaffoldProject(root) ==
  /\ setup_phase = SetupCliInstalled
  /\ root \in SpecRoots
  /\ spec_root' = root
  /\ setup_phase' = SetupProjectScaffold
  /\ UNCHANGED << ticket_state, complexity_gate, corpus_gate,
                  effect_conformance, kill_test >>

\* CLI: scaffold emits a `budgets:` block into spec_manifest.yaml and
\* instructs the agent to propose the documented defaults to the user, ask
\* which to adjust for this program, and record a one-line rationale per
\* changed value. Budgets are established before any generation action, so
\* every downstream gate reads them from the manifest.
\* @command RecordBudgets
\* @port TlaSpecDevCliPort.spec_tree
RecordBudgets(root) ==
  /\ setup_phase = SetupProjectScaffold
  /\ root = spec_root
  /\ setup_phase' = SetupBudgetsRecorded
  /\ UNCHANGED << spec_root, ticket_state, complexity_gate, corpus_gate,
                  effect_conformance, kill_test >>

\* CLI: `tla-spec-dev --spec-root <root> scaffold workflow`
\* Creates project `current/`, `desired_program_model/`, and ticket plan.
\* @command ScaffoldWorkflow
\* @port TlaSpecDevCliPort.spec_tree
ScaffoldWorkflow(root) ==
  /\ setup_phase = SetupBudgetsRecorded
  /\ root = spec_root
  /\ setup_phase' = SetupWorkflowScaffold
  /\ UNCHANGED << spec_root, ticket_state, complexity_gate, corpus_gate,
                  effect_conformance, kill_test >>

\* CLI: `tla-spec-dev --spec-root <root> open ticket <ticket-name>`
\* Creates ticket-local current/desired/results/Test Graph workspace.
\* @command OpenTicket
\* @port TlaSpecDevCliPort.spec_tree
OpenTicket(root, ticket) ==
  /\ setup_phase >= SetupWorkflowScaffold
  /\ root = spec_root
  /\ ticket \in Tickets
  \* MF-025: `\notin active_tickets /\ \notin closed_tickets` is exactly
  \* "has not entered the lifecycle yet". Both guards collapse into this one,
  \* and the never-reopened property is now structural.
  /\ ticket_state[ticket] = TicketUnopened
  /\ ticket_state' = [ticket_state EXCEPT ![ticket] = TicketOpened]
  /\ UNCHANGED << setup_phase, spec_root, complexity_gate, corpus_gate,
                  effect_conformance, kill_test >>

\* Agent step: update ticket desired model, adapters, and Test Graph bindings.
\* This is intentionally modeled because the CLI must print this instruction.
\* @command UpdateTicketDesired
\* @port TlaSpecDevCliPort.spec_tree
UpdateTicketDesired(ticket) ==
  /\ ticket \in ActiveTickets
  /\ ticket_state[ticket] = TicketOpened
  /\ ticket_state' = [ticket_state EXCEPT ![ticket] = TicketDesiredReady]
  /\ UNCHANGED << setup_phase, spec_root, complexity_gate, corpus_gate,
                  effect_conformance, kill_test >>

\* Agent step: production implementation has landed and current matches desired.
\* @command UpdateTicketCurrent
\* @port TlaSpecDevCliPort.spec_tree
UpdateTicketCurrent(ticket) ==
  /\ ticket \in ActiveTickets
  /\ ticket_state[ticket] = TicketDesiredReady
  /\ ticket_state' = [ticket_state EXCEPT ![ticket] = TicketCurrentReady]
  /\ UNCHANGED << setup_phase, spec_root, complexity_gate, corpus_gate,
                  effect_conformance, kill_test >>

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
\* @port TlaSpecDevCliPort.evidence_report
\* @port TlaSpecDevCliPort.tlc_process
AnalyzeComplexity(root) ==
  /\ setup_phase >= SetupBudgetsRecorded
  /\ root = spec_root
  /\ complexity_gate' \in {"pass", "fail"}
  /\ UNCHANGED << setup_phase, spec_root, ticket_state, corpus_gate,
                  effect_conformance, kill_test >>

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
\* @port TlaSpecDevCliPort.evidence_report
AnalyzeCorpus(root) ==
  /\ setup_phase >= SetupBudgetsRecorded
  /\ root = spec_root
  /\ corpus_gate' \in {"pass", "fail"}
  /\ UNCHANGED << setup_phase, spec_root, ticket_state, complexity_gate,
                  effect_conformance, kill_test >>

\* CLI: `tla-spec-dev --spec-root <root> run effect-conformance`
\* MF-013: executes component adapters in a sandbox (temp dirs, fake
\* transports, recorded boundaries), collects the side effects that actually
\* crossed a boundary, and diffs them against the ports declared in
\* actions.yml / spec_manifest.yaml. Writes the diff report as ticket evidence.
\*
\* This is the standalone reporting command. It records a fresh verdict and
\* advances no ticket -- reporting is its whole job. The ENFORCING copy of the
\* same measurement lives inside RunSpecUnitTests below, because the shipped
\* runner performs the diff during the spec-unit run rather than waiting to be
\* asked. That is deliberate: a gate you have to remember to invoke is not a
\* gate.
\*
\* Observation is passive in the implementation -- the sandbox patches the
\* real boundaries, so an adapter cannot decline to disclose an effect. The
\* model reflects that by letting the verdict range over all four outcomes
\* rather than making it an input the caller supplies.
\*
\* MF-027: passivity is not the same as reach. The patches live in one CPython
\* interpreter, so passive observation of a target running elsewhere observes
\* nothing. "unobservable" is that case, and it is a failure.
\* @command RunEffectConformance
\* @port TlaSpecDevCliPort.evidence_report
RunEffectConformance(root) ==
  /\ setup_phase >= SetupBudgetsRecorded
  /\ root = spec_root
  /\ effect_conformance' \in {"clean", "gaps", "dead_surface", "unobservable"}
  /\ UNCHANGED << setup_phase, spec_root, ticket_state, complexity_gate,
                  corpus_gate, kill_test >>

\* CLI: `tla-spec-dev --spec-root <root> run kill-test --corpus-command <cmd>`
\* MF-016, oracle 4. Seeds one fault per declared port and one per invariant
\* into real production source, runs the distilled corpus against each, and
\* gates the resulting kill rate against kill_rate_floor from the budgets.
\*
\* Like RunEffectConformance this action advances no ticket -- measuring is its
\* whole job. Unlike RunEffectConformance there is deliberately NO enforcing
\* copy inside RunSpecUnitTests, and that difference is a considered one rather
\* than an omission. The effect oracle is nearly free: it observes a corpus run
\* that was happening anyway. The kill test runs the ENTIRE corpus once per
\* mutant, so at this repository's declared boundaries it costs one full corpus
\* run per mutant. Folding that into every spec-unit invocation would make the
\* inner development loop unusable, and a gate people disable to get work done
\* protects nothing. The doctrine therefore names ONBOARDING and PROMOTION as
\* the required kill-test moments, with per-ticket work reusing the baseline
\* mutants plus one new mutant at the changed boundary.
\*
\* HONEST SCOPE, retained verbatim from the pre-split module because it is
\* still accurate: the promotion INTERLOCK -- CloseTicket requiring kill_test =
\* "pass" -- is NOT modeled, because the shipped `close ticket` does not
\* enforce it. MF-023 ran the kill test (see results/kill-test-*.json) and the
\* measured verdict does not meet the floor, so writing the interlock into the
\* model now would make the model assert a behavior the program does not have
\* AND would block every future close. It remains unmodeled, and the reason is
\* now an evidenced measurement rather than a deferral. See findings.md.
\* @command RunKillTest
\* @port TlaSpecDevCliPort.evidence_report
\* @port TlaSpecDevCliPort.test_process
RunKillTest(root) ==
  /\ setup_phase >= SetupBudgetsRecorded
  /\ root = spec_root
  /\ kill_test' \in {"pass", "below_floor", "incomplete_catalog"}
  /\ UNCHANGED << setup_phase, spec_root, ticket_state, complexity_gate,
                  corpus_gate, effect_conformance >>

\* CLI: `tla-spec-dev --spec-root <root> run spec-unit-tests`
\* Runs generated/adapted spec-unit validation for ticket current.
\* MF-011: case generation runs only behind the complexity gate. A passing
\* gate enables it outright; a failing gate enables it only under the explicit
\* `--allow-over-budget` override, modeled as the `override` input. When the
\* gate is "unknown" no transition is enabled -- that absence IS the refusal.
\* @command RunSpecUnitTests
\* @port TlaSpecDevCliPort.test_process
\* @port TlaSpecDevCliPort.spec_tree
RunSpecUnitTests(root, ticket, override) ==
  /\ setup_phase >= SetupCliInstalled
  /\ root = spec_root
  /\ ticket \in ActiveTickets
  \* MF-025: was `ticket_phase[ticket] >= 2` on an active ticket. Active caps
  \* the lifecycle at TicketSpecUnitTestsPassed, so the range is 3..4. This
  \* stays a range rather than an equality on purpose: tightening it would
  \* delete the idempotent re-run self-loop on an already-passing ticket.
  /\ ticket_state[ticket] \in TicketCurrentReady..TicketSpecUnitTestsPassed
  /\ \/ complexity_gate = "pass"
     \/ /\ complexity_gate = "fail"
        /\ override
  \* MF-014: generation produces the corpus, then the case caps are measured
  \* over it. The corpus is complete either way -- the gate refuses, it never
  \* trims -- so a failing verdict advances nothing and reports instead.
  \* `override` is deliberately NOT consulted here. The case caps have no
  \* override and never will: raising the cap with a recorded rationale is the
  \* accept path, and that is a different verdict rather than a bypassed one.
  \* `override` survives only for complexity_gate. MF-023 exercised that flag
  \* against this repository (results/override-allow-over-budget.txt): it is
  \* explicit, it is loud, and it is not the default path -- but it IS still
  \* present, and doctrine withdrew it on 2026-07-18. Removing it from the
  \* shipped CLI is recorded as a recommendation for owner approval rather
  \* than performed here, because this ticket declares no production scope.
  /\ corpus_gate' \in {"pass", "fail"}
  \* MF-013: the spec-unit run executes adapters in the effect sandbox, so it
  \* measures effect conformance in the same pass. The verdict is recorded
  \* whatever it is -- the report is written clean or not -- and a ticket
  \* advances only when BOTH gates are satisfied.
  \*
  \* Note the shape of the conjunction below: there is no override input, no
  \* justification input, and no disjunct that lets "gaps" through. An
  \* undeclared observed effect FAILS. Recording the gap is not an alternative
  \* to failing on it -- both happen, which is what the 2026-07-18 audit
  \* required after finding the original criteria made the failure optional.
  \* MF-027: "unobservable" joins the range here too. Note that the ticket
  \* advance below already requires effect_conformance' = "clean", so an
  \* unobservable target blocks a ticket exactly as a gap does -- without a
  \* new clause, because there was never a disjunct to widen.
  /\ effect_conformance' \in {"clean", "gaps", "dead_surface", "unobservable"}
  /\ ticket_state' = IF corpus_gate' = "pass" /\ effect_conformance' = "clean"
                       THEN [ticket_state EXCEPT ![ticket] = TicketSpecUnitTestsPassed]
                       ELSE ticket_state
  /\ UNCHANGED << setup_phase, spec_root, complexity_gate, kill_test >>

\* CLI: `tla-spec-dev --spec-root <root> close ticket <ticket-name>`
\* Closes ticket only after current == desired and spec-unit tests passed.
\* @command CloseTicket
\* @port TlaSpecDevCliPort.spec_tree
CloseTicket(root, ticket) ==
  /\ setup_phase >= SetupCliInstalled
  /\ root = spec_root
  /\ ticket \in ActiveTickets
  \* MF-025: leaving active and entering closed was a single simultaneous
  \* move that left ticket_phase UNCHANGED, so it is exactly this one step.
  /\ ticket_state[ticket] = TicketSpecUnitTestsPassed
  /\ ticket_state' = [ticket_state EXCEPT ![ticket] = TicketClosed]
  /\ UNCHANGED << setup_phase, spec_root, complexity_gate, corpus_gate,
                  effect_conformance, kill_test >>

\* MF-023: the explicit stutter disjunct that the pre-split module carried as
\* `Stutter == UNCHANGED vars` is GONE, and its removal is measured rather than
\* assumed. In TLA+, `[][N]_v` already permits a step that leaves `v`
\* unchanged, so naming stuttering as a disjunct of `N` is redundant. TLC
\* confirms it exactly: with and without the disjunct the Internal view has the
\* SAME 42,861 distinct states at the SAME depth 24, and only the generated
\* count changes (999,636 -> 956,775, a difference of exactly 42,861 -- one
\* self-loop per state).
\*
\* It is removed because case generation emitted every one of those self-loops
\* as a spec case: 42,861 cases, 4.3% of the corpus, labeled `InternalStutter`,
\* for which no adapter can exist because stuttering is not a program behavior.
\* This is a reduction with PROVEN-IDENTICAL reachable behavior, not an
\* abstraction -- no reachable state is dropped.

InternalNext ==
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
  \/ \E root \in SpecRoots:
      RunEffectConformance(root)
  \/ \E root \in SpecRoots:
      RunKillTest(root)
  \/ \E root \in SpecRoots, ticket \in Tickets, override \in BOOLEAN:
      RunSpecUnitTests(root, ticket, override)
  \/ \E root \in SpecRoots, ticket \in Tickets:
      CloseTicket(root, ticket)

\* NOTE ON THE NAME: this operator MUST be called `TypeInvariant`.
\* scripts/analyze_complexity.py looks the name up literally (line 746) and,
\* when it is absent, reports EVERY variable as "unconstrained by
\* TypeInvariant -- excluded from the bound" and computes
\* `bound = 1 (product of 0 bounded dimensions)`. The static
\* `max_state_space_bound` gate then passes vacuously. The shipped example's
\* own Internal.tla names its invariant `InternalInvariant` and is scored
\* exactly that way -- bound 1, PASS. Decomposition therefore silently
\* disables the toolchain's own bound gate unless the view happens to use this
\* name. Recorded as results/findings.md FINDING 1; the name is used here to
\* keep the gate live, NOT because the vacuous pass was acceptable.
TypeInvariant ==
  /\ setup_phase \in SetupPhases
  /\ spec_root \in SpecRoots \cup {NoRoot}
  /\ ticket_state \in [Tickets -> TicketStates]
  \* MF-025: retained by name. Both are now structurally true, since
  \* ActiveTickets and ClosedTickets are defined by comprehension over
  \* Tickets, but a named safety property that is deleted is
  \* indistinguishable at review from one that was lost.
  /\ ActiveTickets \subseteq Tickets
  /\ ClosedTickets \subseteq Tickets
  /\ complexity_gate \in ComplexityVerdicts
  /\ corpus_gate \in CorpusVerdicts
  /\ effect_conformance \in EffectVerdicts
  /\ kill_test \in KillTestVerdicts

\* MF-022: the four bootstrap ordering invariants below are retained by name
\* even though the setup_phase ordinal now enforces them structurally, so each
\* is a tautology. This follows the precedent MF-020 set for ticket_phase:
\* deleting a named safety property is indistinguishable at review from losing
\* it, and retaining it documents that the ordering is still required and is
\* now guaranteed by construction rather than by checking.
CliInstalledRequiresBuilt ==
  setup_phase >= SetupCliInstalled => setup_phase >= SetupCliBuilt

WorkflowRequiresProject ==
  setup_phase >= SetupWorkflowScaffold => setup_phase >= SetupProjectScaffold

\* Budgets are per-program state established during scaffolding.
BudgetsRequireProject ==
  setup_phase >= SetupBudgetsRecorded => setup_phase >= SetupProjectScaffold

\* Every generation action runs behind recorded budgets: the workflow (and
\* therefore every ticket, spec-unit run, and close) cannot be scaffolded
\* until the budgets block exists in the manifest.
WorkflowRequiresBudgets ==
  setup_phase >= SetupWorkflowScaffold => setup_phase >= SetupBudgetsRecorded

\* Not a tautology: this relates setup_phase to the separate spec_root
\* variable and still does real work.
ProjectChoosesKnownSpecRoot ==
  setup_phase >= SetupProjectScaffold => spec_root \in SpecRoots

\* MF-025: retained by name. The ordinal makes this a tautology -- a ticket
\* has one state, and TicketClosed is not in TicketOpened..TicketSpecUnitTestsPassed
\* -- but the property is still required and is now guaranteed by construction
\* rather than by checking.
NoOpenClosedOverlap ==
  ActiveTickets \cap ClosedTickets = {}

CurrentRequiresDesired ==
  \A ticket \in Tickets:
    ticket_state[ticket] >= TicketCurrentReady
      => ticket_state[ticket] >= TicketDesiredReady

SpecUnitTestsRequireCurrent ==
  \A ticket \in Tickets:
    ticket_state[ticket] >= TicketSpecUnitTestsPassed
      => ticket_state[ticket] >= TicketCurrentReady

\* MF-011: no case generation ever runs against an unanalyzed model. Reaching
\* the passed stage means spec-unit cases were generated and run, which is only
\* possible once analyze complexity has recorded a verdict -- pass, or fail plus
\* the explicit override. The gate is never silently skipped.
\* MF-025: the old guard `ticket_phase[ticket] >= 3` was satisfied by closed
\* tickets too, because CloseTicket left the phase at 3. The faithful ordinal
\* equivalent is therefore `>= TicketSpecUnitTestsPassed`, which covers both
\* the passed-and-still-active state and the closed state -- not an equality.
SpecUnitTestsRequireAnalyzedGate ==
  (\E ticket \in Tickets: ticket_state[ticket] >= TicketSpecUnitTestsPassed)
    => complexity_gate /= "unknown"

\* MF-014: no ticket ever passes spec-unit tests without its generated corpus
\* having been measured against the case caps. RunSpecUnitTests records a cap
\* verdict on every such transition, so a corpus that was never measured cannot
\* be behind a passing ticket. The companion property, that a case is never
\* removed to make the verdict "pass", is structural rather than checkable
\* here: no action in this module reduces a case count, and no override input
\* reaches the cap.
SpecUnitTestsRequireMeasuredCorpus ==
  (\E ticket \in Tickets: ticket_state[ticket] >= TicketSpecUnitTestsPassed)
    => corpus_gate /= "unknown"

\* MF-013: no ticket ever passes spec-unit tests while the representation is
\* blind to a real effect, or while it carries a port no case exercises.
\* MF-027 added the third disqualifying verdict: a ticket must not pass on a
\* target the oracle could not see.
\*
\* Why "/= unknown" and not "= clean": RunEffectConformance is a standalone
\* re-measurement enabled at any point after setup, so a later run can legally
\* find gaps in a program whose ticket passed earlier -- that is a real
\* sequence, and TLC finds it. Asserting "= clean" here would therefore be a
\* false invariant, and weakening the ACTION to make it true would delete the
\* re-measurement rather than describe the program. The gate itself lives where
\* it belongs, in RunSpecUnitTests: ticket_state advances only when
\* effect_conformance' = "clean", with no override and no justification input
\* anywhere in the conjunction.
SpecUnitTestsRequireMeasuredEffects ==
  (\E ticket \in Tickets: ticket_state[ticket] >= TicketSpecUnitTestsPassed)
    => effect_conformance /= "unknown"

\* MF-025: retained by name; now structurally true, since TicketClosed (5)
\* is itself >= TicketSpecUnitTestsPassed (4) and the only way into it is
\* through that stage.
ClosedTicketsPassedSpecUnitTests ==
  \A ticket \in ClosedTickets:
    ticket_state[ticket] >= TicketSpecUnitTestsPassed

\* MF-016: a kill-test verdict exists only after the workflow it measures.
\* RunKillTest guards on budgets recorded, because the floor it gates against
\* IS a budget -- reading kill_rate_floor before budgets are recorded would
\* silently measure against a default nobody negotiated, which is the "falls
\* back to" degeneracy the doctrine forbids.
KillTestVerdictRequiresBudgets ==
  kill_test /= "unknown" => setup_phase >= SetupBudgetsRecorded

InternalInvariant ==
  /\ TypeInvariant
  /\ CliInstalledRequiresBuilt
  /\ WorkflowRequiresProject
  /\ BudgetsRequireProject
  /\ WorkflowRequiresBudgets
  /\ ProjectChoosesKnownSpecRoot
  /\ NoOpenClosedOverlap
  /\ CurrentRequiresDesired
  /\ SpecUnitTestsRequireCurrent
  /\ SpecUnitTestsRequireAnalyzedGate
  /\ SpecUnitTestsRequireMeasuredCorpus
  /\ SpecUnitTestsRequireMeasuredEffects
  /\ ClosedTicketsPassedSpecUnitTests
  /\ KillTestVerdictRequiresBudgets

InternalSpec ==
  InternalInit /\ [][InternalNext]_InternalVars

=============================================================================
