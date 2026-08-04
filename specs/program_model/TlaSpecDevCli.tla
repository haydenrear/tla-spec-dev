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
\*
\* Read active_tickets as ActiveTickets, closed_tickets as ClosedTickets, and
\* the old ticket_phase[t] as ticket_state[t] - 1 while the ticket is active.

\* MF-020: ticket lifecycle phase as a single ordinal rather than three
\* parallel booleans, now absorbed into ticket_state by MF-025. The old
\* booleans were pinned to a strict total order by CurrentRequiresDesired /
\* SpecUnitTestsRequireCurrent, so only 4 of their 8 combinations were ever
\* reachable. Read desired_ready as >= TicketDesiredReady, current_ready as
\* >= TicketCurrentReady, and spec_unit_tests_passed as
\* >= TicketSpecUnitTestsPassed.
\* MF-013: effect_conformance is the effect conformance verdict -- whether the
\* adapters' observed side effects match the ports the model declares. Like
\* complexity_gate and corpus_gate this is a fact about the whole program
\* rather than about one ticket, so it is a single global variable.
\*
\* Five values, and the four non-"unknown" ones are NOT interchangeable:
\*   "clean"        -- every observed effect landed on a declared port, and
\*                     every declared port was exercised by some case.
\*   "gaps"         -- an effect crossed a boundary with no declared port.
\*                     The model is blind to real behavior.
\*   "dead_surface" -- a declared port no case ever exercised.
\*   "unobservable" -- MF-027: the sandbox could not see the target at all.
\*                     The oracle observes the in-process CPython runtime only,
\*                     so a JVM adapter, a JBang/uv Test Graph node, or an
\*                     adapter that delegates to a child process produces NO
\*                     observations. Before MF-027 that empty observation set
\*                     was indistinguishable from a clean one and the command
\*                     returned success. It is now its own verdict, and it
\*                     DOMINATES the others: a diff computed over a target that
\*                     was never seen carries no information, so reporting it
\*                     as "clean" -- or even as "gaps" -- would assert
\*                     something the run has no evidence for.
\*
\* "gaps", "dead_surface" and "unobservable" are kept apart rather than
\* collapsed into one "fail" because they are not the same finding and do not
\* have the same remedy: a gap is fixed by declaring the port or removing the
\* emission, dead surface by removing the port or adding a case, and an
\* unobservable target by running it in-process or checking that boundary with
\* a different mechanism. The distinction is externally visible in
\* `result.next`, which is why it is represented here instead of being
\* flattened.
\*
\* MF-027 is modeled rather than left to the implementation because the
\* verdict is externally-visible CLI behavior: it selects a distinct exit path
\* and a distinct `result.next`. Leaving it out would make the model blind to
\* a real outcome of a modeled command, which is the same defect the verdict
\* itself exists to report.
\*
\* Note what is deliberately ABSENT, exactly as for corpus_gate: there is no
\* override input, no justification input, and no transition from "gaps" to
\* "clean" that is not a re-measurement. Out-of-contract justifications were
\* WITHDRAWN on 2026-07-18 as degeneracy. Nothing suppresses a gap report --
\* not a manifest entry, not an annotation, not a recorded rationale. The only
\* ways to reach "clean" are to DECLARE the port or to CHANGE THE PROGRAM so it
\* no longer emits the effect. There is no third option.
\*
\* MF-016: kill_test is the mutation kill-test verdict -- oracle 4, and the
\* only one of the four that validates the representation against the PROGRAM
\* rather than against itself. TLC proves self-consistency, analyze corpus
\* proves tractability, effect conformance proves the boundaries are declared;
\* none of them can tell a faithful model from a vacuous one. This can.
\*
\* The experiment it records: seed one fault per declared port and one per
\* invariant, run the distilled corpus, and require the kill rate to meet
\* kill_rate_floor. Like the three gate variables above it is a fact about the
\* whole program, so it is a single global variable.
\*
\* Four values, and the three non-"unknown" ones are NOT interchangeable:
\*   "pass"               -- a COMPLETE catalog ran and the kill rate met the
\*                           floor. The representation caught the seeded bugs.
\*   "below_floor"        -- a complete catalog ran and the rate fell short.
\*                           Some mutant survived: the corpus executed a
\*                           deliberately broken program and could not tell it
\*                           from the correct one, so the representation is too
\*                           abstract at that mutant's boundary. Each survivor
\*                           names the variable and action to refine.
\*   "incomplete_catalog" -- a declared port or an invariant has NO seeded
\*                           fault. No rate is computed. This is deliberately
\*                           NOT "below_floor" and deliberately not a rate of
\*                           0.0 or 1.0: a number derived from a surface that
\*                           was never covered asserts something the run has no
\*                           evidence for, which is exactly the defect MF-027
\*                           removed from the effect oracle when it stopped
\*                           reporting unobserved targets as clean.
\*
\* The remedies differ, which is why the values are kept apart rather than
\* collapsed into one "fail": below_floor is fixed by REFINING THE MODEL at the
\* named variable or action, incomplete_catalog by SEEDING A FAULT for the
\* uncovered boundary. Both are externally visible in `result.next`, which is
\* the same criterion MF-027 used to keep "gaps" apart from "unobservable".
\*
\* Why this gate has no override, stated here because it is the one that keeps
\* the others honest: every other budget in this toolchain is a COST CAP
\* (max_distinct_states, the case caps, the component heuristics). Cost caps
\* alone are gameable in a single obvious direction -- shrink the model toward
\* nothing and every cap passes. kill_rate_floor is the matching VALUE FLOOR,
\* and a trivial model stops killing mutants. Cost cap plus value floor is a
\* real optimization target; either alone invites gaming. So there is no
\* override input, no waiver, no expected-to-survive annotation, and no
\* transition from "below_floor" to "pass" that is not a genuine re-measurement
\* after the model was actually refined. Weakening this one weakens all of them.
\*
\* Note also what is ABSENT by construction: there is no path from
\* "incomplete_catalog" to "pass" that does not go through seeding the missing
\* fault, because the implementation recomputes the required boundary set from
\* the port declarations and the INVARIANTS block on every run. Adding a port
\* to the model breaks the kill test until somebody seeds a fault for it. The
\* obligation cannot drift behind the model, which is the failure mode a
\* documented "remember to add a mutant" rule would have had.
\*
\* NOTE ON PLACEMENT: this comment sits ABOVE the VARIABLES block on purpose.
\* Comments interleaved between names inside the block are not parsed by
\* scripts/analyze_complexity.py, which silently dropped this variable from the
\* dimension table and the bound when it was written that way -- the declared
\* bound stayed at the pre-MF-013 34,992 while TLC measured 38,241 distinct
\* states, a bound below the measured reality. Keep declarations contiguous.
VARIABLES
  setup_phase,
  spec_root,
  ticket_state,
  lastCommand,
  result,
  complexity_gate,
  corpus_gate,
  effect_conformance,
  kill_test,
  architecture_scan,
  architecture_delta

vars ==
  << setup_phase,
     spec_root,
     ticket_state,
     lastCommand,
     result,
     complexity_gate,
     corpus_gate,
     effect_conformance,
     kill_test,
     architecture_scan,
     architecture_delta >>

\* MF-025: the lifecycle stages by name. Guards and invariants below read as a
\* lifecycle rather than as arithmetic on an integer.
TicketUnopened            == 0
TicketOpened              == 1
TicketDesiredReady        == 2
TicketCurrentReady        == 3
TicketSpecUnitTestsPassed == 4
TicketClosed              == 5
\* RC-01 (MF-026, owner decision 2026-08-01): a close taken under one of the
\* six GUARD-WEAKENING FLAGS -- --accept-new, --allow-open,
\* --no-promote-current, --validate-only, --force, --dry-run -- is a DIFFERENT
\* STATE from a close taken under the guard, and this is the stage that records
\* it. Before this ticket the flags were inventoried as presentation under the
\* per-flag granularity limitation, and the cost of that was specific rather
\* than theoretical: CloseTicket guards on TicketSpecUnitTestsPassed and TLC
\* proves ClosedTicketsPassedSpecUnitTests over 1,292,951 states, while
\* `--accept-new` (tla_spec_dev.py --accept-new) and `--allow-open` exist
\* SPECIFICALLY to bypass that precondition -- so the model proved an invariant
\* the shipped program has two documented flags to violate, no modeled state
\* recorded their use, and NO ORACLE IN THIS TOOLCHAIN COULD SEE THE
\* DIFFERENCE (the kill test seeds faults per declared port and per invariant,
\* i.e. only inside modeled boundaries). Six of the 78 options; the granularity
\* limitation covering the other 72 is untouched.
TicketClosedWeakened      == 6

\* MF-025: every site that meant "the set of active tickets" still says so.
ActiveTickets == {t \in Tickets : ticket_state[t] \in TicketOpened..TicketSpecUnitTestsPassed}
\* RC-01: BOTH closes are closes -- the ticket is out of the active set either
\* way, which is what NoOpenClosedOverlap is about. What differs is whether the
\* close passed through the guard, and that is the distinction
\* GuardedClosedTickets draws below.
ClosedTickets == {t \in Tickets : ticket_state[t] \in {TicketClosed, TicketClosedWeakened}}
\* RC-01: the closes that went through the precondition, and the ONLY ones any
\* invariant here may claim passed spec-unit tests.
GuardedClosedTickets  == {t \in Tickets : ticket_state[t] = TicketClosed}
WeakenedClosedTickets == {t \in Tickets : ticket_state[t] = TicketClosedWeakened}

\* RC-01: READ THE LIFECYCLE, NOT THE INTEGER. Every property below that used
\* to say `ticket_state[t] >= <stage>` meant "this ticket has been through
\* <stage> of the guarded lifecycle". TicketClosedWeakened is an ordinal ABOVE
\* every guarded stage and certifies LESS than any of them, so `>=` silently
\* answers TRUE for it -- and five invariants would have gone on holding, by
\* accident of the encoding, about a ticket that passed nothing. That accident
\* is exactly the class of defect the coverage audit opened this ticket for, so
\* the reader is named once and used everywhere instead of being patched at each
\* site.
TicketReached(t, stage) == ticket_state[t] \in stage..TicketClosed

CommandResult(ok, reason, nextStep) ==
  [accepted |-> ok, reason |-> reason, next |-> nextStep]

Init ==
  /\ setup_phase = 0
  /\ spec_root = NoRoot
  /\ ticket_state = [t \in Tickets |-> TicketUnopened]
  /\ lastCommand = "Init"
  /\ result = CommandResult(TRUE, NoReason, "BuildSkillCli")
  /\ complexity_gate = "unknown"
  /\ corpus_gate = "unknown"
  /\ effect_conformance = "unknown"
  /\ kill_test = "unknown"
  /\ architecture_scan = "unknown"
  /\ architecture_delta = "unknown"

\* CD-11 (audit run 4, ESC-R4-3): `@port TlaSpecDevCliPort.<name>` names a
\* DECLARED EFFECT PORT -- an entry of
\* effects.components.TlaSpecDevCliPort.ports in spec_manifest.yaml -- and
\* each action's @port lines mirror its row in effects.actions. Before CD-11
\* the tag carried a per-command vocabulary (build_skill_cli, ...) whose
\* intersection with the declared port names was empty; the annotation layer
\* and the effects layer now use one vocabulary. Actions whose effects row is
\* deliberately empty (RecordBudgets, AnalyzeCorpus) carry no @port line and
\* say so. Comments only: nothing parses @port, and the model's states,
\* actions, guards, and invariants are unchanged.
\* The skill ships one local command built from Python entrypoint code.
\* @command BuildSkillCli
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.cli_artifact
BuildSkillCli ==
  /\ setup_phase = 0
  /\ setup_phase' = 1
  /\ lastCommand' = "BuildSkillCli"
  /\ result' = CommandResult(TRUE, NoReason, "InstallLocalCli")
  /\ UNCHANGED << spec_root,
                  ticket_state,
                  complexity_gate,
                  corpus_gate,
                  effect_conformance,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

\* The local environment can invoke `tla-spec-dev ...` after install.
\* RC-02 (MF-026 round-3 N-1): three @port lines ADDED so this action's
\* annotation mirrors its effects.actions row again. RC-01 declared
\* cli_download, cli_artifact_delete and cli_selftest_process in the manifest's
\* ports block and attached them to no action, which broke the mirror rule
\* stated above in the OPPOSITE direction from round-2 G-1: G-1 was an action
\* with @port lines and no row, this was ports that no action's @port lines
\* mirrored. Comments only; the states, guards and invariants are unchanged.
\* @command InstallLocalCli
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.cli_artifact
\* @port TlaSpecDevCliPort.cli_download
\* @port TlaSpecDevCliPort.cli_artifact_delete
\* @port TlaSpecDevCliPort.cli_selftest_process
InstallLocalCli ==
  /\ setup_phase = 1
  /\ setup_phase' = 2
  /\ lastCommand' = "InstallLocalCli"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev scaffold project")
  /\ UNCHANGED << spec_root,
                  ticket_state,
                  complexity_gate,
                  corpus_gate,
                  effect_conformance,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

\* CLI: `tla-spec-dev --spec-root <root> scaffold project`
\* Creates the accepted `program_model` baseline only.
\* @command ScaffoldProject
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.spec_tree
ScaffoldProject(root) ==
  /\ setup_phase = 2
  /\ root \in SpecRoots
  /\ spec_root' = root
  /\ setup_phase' = 3
  /\ lastCommand' = "tla-spec-dev scaffold project"
  /\ result' = CommandResult(TRUE, NoReason, "RecordBudgets")
  /\ UNCHANGED << ticket_state,
                  complexity_gate,
                  corpus_gate,
                  effect_conformance,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

\* CLI: scaffold emits a `budgets:` block into spec_manifest.yaml and
\* instructs the agent to propose the documented defaults to the user, ask
\* which to adjust for this program, and record a one-line rationale per
\* changed value. Budgets are established before any generation action, so
\* every downstream gate reads them from the manifest.
\* @command RecordBudgets
\* @result CliWorkflowResult
\* No @port: the manifest row `RecordBudgets: []` is deliberately empty --
\* the CLI performs no distinct budgets effect (CD-10 DF-2 ruling).
RecordBudgets(root) ==
  /\ setup_phase = 3
  /\ root = spec_root
  /\ setup_phase' = 4
  /\ lastCommand' = "RecordBudgets"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev scaffold workflow")
  /\ UNCHANGED << spec_root,
                  ticket_state,
                  complexity_gate,
                  corpus_gate,
                  effect_conformance,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

\* CLI: `tla-spec-dev --spec-root <root> scaffold workflow`
\* Creates project `current/`, `desired_program_model/`, and ticket plan.
\* @command ScaffoldWorkflow
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.spec_tree
ScaffoldWorkflow(root) ==
  /\ setup_phase = 4
  /\ root = spec_root
  /\ setup_phase' = 5
  /\ lastCommand' = "tla-spec-dev scaffold workflow"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev open ticket <ticket>")
  /\ UNCHANGED << spec_root,
                  ticket_state,
                  complexity_gate,
                  corpus_gate,
                  effect_conformance,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

\* CLI: `tla-spec-dev --spec-root <root> open ticket <ticket-name>`
\* Creates ticket-local current/desired/results/Test Graph workspace.
\* @command OpenTicket
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.spec_tree
OpenTicket(root, ticket) ==
  /\ setup_phase >= 5
  /\ root = spec_root
  /\ ticket \in Tickets
  \* MF-025: `\notin active_tickets /\ \notin closed_tickets` is exactly
  \* "has not entered the lifecycle yet". Both guards collapse into this one,
  \* and the never-reopened property is now structural.
  /\ ticket_state[ticket] = TicketUnopened
  /\ ticket_state' = [ticket_state EXCEPT ![ticket] = TicketOpened]
  /\ lastCommand' = "tla-spec-dev open ticket"
  /\ result' = CommandResult(TRUE, NoReason, "Update ticket desired TLA+ first")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  complexity_gate,
                  corpus_gate,
                  effect_conformance,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

\* Agent step: update ticket desired model, adapters, and Test Graph bindings.
\* This is intentionally modeled because the CLI must print this instruction.
\* @command UpdateTicketDesired
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.spec_tree
UpdateTicketDesired(ticket) ==
  /\ ticket \in ActiveTickets
  /\ ticket_state[ticket] = TicketOpened
  /\ ticket_state' = [ticket_state EXCEPT ![ticket] = TicketDesiredReady]
  /\ lastCommand' = "UpdateTicketDesired"
  /\ result' = CommandResult(TRUE, NoReason, "Implement ticket and update current")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  complexity_gate,
                  corpus_gate,
                  effect_conformance,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

\* Agent step: production implementation has landed and current matches desired.
\* @command UpdateTicketCurrent
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.spec_tree
UpdateTicketCurrent(ticket) ==
  /\ ticket \in ActiveTickets
  /\ ticket_state[ticket] = TicketDesiredReady
  /\ ticket_state' = [ticket_state EXCEPT ![ticket] = TicketCurrentReady]
  /\ lastCommand' = "UpdateTicketCurrent"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev run spec-unit-tests")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  complexity_gate,
                  corpus_gate,
                  effect_conformance,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

\* CLI: `tla-spec-dev --spec-root <root> analyze complexity <spec> <cfg>`
\* MF-011, amended by CD-09 (G2): measures the model against the manifest
\* budgets and records the verdict. The verdict is a fact about the whole
\* program, not about one ticket, so it is a single global variable rather
\* than a per-ticket map -- and it is ADVISORY: recorded as an observable
\* fact, consulted by no guard. Nothing downstream blocks on it; a dense
\* model is a finding the agent reads, not a refused build
\* (references/architecture_tractability.md, "Advisory, Not Blocking").
\* The outcome is nondeterministic here because it depends on the model being
\* analyzed, which is outside this state machine.
\* @command AnalyzeComplexity
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.evidence_report
AnalyzeComplexity(root) ==
  /\ setup_phase >= 4
  /\ root = spec_root
  /\ complexity_gate' \in {"pass", "fail"}
  /\ lastCommand' = "tla-spec-dev analyze complexity"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev run spec-unit-tests")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  ticket_state,
                  corpus_gate,
                  effect_conformance,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

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
\* No @port: `AnalyzeCorpus: []` -- evidence_report removed as a dead
\* declared port (CD-11 R4-3; corpus_diagnostics.py prints only).
AnalyzeCorpus(root) ==
  /\ setup_phase >= 4
  /\ root = spec_root
  /\ corpus_gate' \in {"pass", "fail"}
  /\ lastCommand' = "tla-spec-dev analyze corpus"
  /\ result' = CommandResult(TRUE, NoReason, "Fix the diagram, or raise the cap with a rationale")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  ticket_state,
                  complexity_gate,
                  effect_conformance,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

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
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.evidence_report
\* @port TlaSpecDevCliPort.spec_tree
\* HP-04: the per-case work directory is emptied before each case, so the same
\* corpus on the same tree reports the same gap count. That delete is a real
\* effect under **/specs/** and is declared rather than left silent.
\* @port TlaSpecDevCliPort.spec_tree_delete
RunEffectConformance(root) ==
  /\ setup_phase >= 4
  /\ root = spec_root
  /\ effect_conformance' \in {"clean", "gaps", "dead_surface", "unobservable"}
  /\ lastCommand' = "tla-spec-dev run effect-conformance"
  /\ result' = CASE effect_conformance' = "clean"
                      -> CommandResult(TRUE, NoReason, "tla-spec-dev run spec-unit-tests")
                 [] effect_conformance' = "gaps"
                      -> CommandResult(FALSE, NoReason, "Declare the port, or change the program so it no longer emits the effect")
                 [] effect_conformance' = "unobservable"
                      -> CommandResult(FALSE, NoReason, "Run the target in-process, or check that boundary another way -- this oracle does not cover it")
                 [] OTHER
                      -> CommandResult(FALSE, NoReason, "Remove the dead port, or add a case that exercises it")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  ticket_state,
                  complexity_gate,
                  corpus_gate,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

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
\* mutant, so at this repository's 18 declared boundaries it costs 18 full
\* corpus runs. Folding that into every spec-unit invocation would make the
\* inner development loop unusable, and a gate people disable to get work done
\* protects nothing. The doctrine therefore names ONBOARDING and PROMOTION as
\* the required kill-test moments, with per-ticket work reusing the baseline
\* mutants plus one new mutant at the changed boundary.
\*
\* HONEST SCOPE, recorded here because the model must not claim more than the
\* CLI does: the promotion INTERLOCK -- CloseTicket requiring kill_test =
\* "pass" -- is NOT modeled, because the shipped `close ticket` does not yet
\* enforce it. Kill-test RUNS are deferred epic-wide to MF-023, so gating close
\* on a run that cannot happen yet would block every ticket close including
\* this one. Writing the guard into the model anyway would make the model
\* assert a behavior the program does not have, which is precisely the defect
\* oracle 4 exists to detect. The interlock lands with the runs in MF-023.
\*
\* Note the verdict range below excludes "unknown": running the command always
\* produces a measurement or an explicit refusal to measure. There is no
\* outcome where the kill test runs and learns nothing, and no input by which a
\* caller supplies the verdict -- the same shape as the three gates above.
\* @command RunKillTest
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.evidence_report
\* @port TlaSpecDevCliPort.mutation_write
\* @port TlaSpecDevCliPort.corpus_process
RunKillTest(root) ==
  /\ setup_phase >= 4
  /\ root = spec_root
  /\ kill_test' \in {"pass", "below_floor", "incomplete_catalog"}
  /\ lastCommand' = "tla-spec-dev run kill-test"
  /\ result' = CASE kill_test' = "pass"
                      -> CommandResult(TRUE, NoReason, "tla-spec-dev close ticket <ticket>")
                 [] kill_test' = "below_floor"
                      -> CommandResult(FALSE, NoReason, "Refine the variable or action named by each surviving mutant until it dies -- the floor is not waivable")
                 [] OTHER
                      -> CommandResult(FALSE, NoReason, "Seed a fault for every declared port and invariant that has none")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  ticket_state,
                  complexity_gate,
                  corpus_gate,
                  effect_conformance,
                  architecture_scan,
                  architecture_delta >>

\* CLI: `tla-spec-dev --spec-root <root> run spec-unit-tests`
\* Runs generated/adapted spec-unit validation for ticket current.
\* CD-09 (coverage-audit run 2, gap G2): the complexity gate no longer appears
\* in this guard AT ALL, and the `override` input is gone. The shipped command
\* performs no complexity check -- the descriptor is ADVISORY (MF-036/CD-01):
\* the program proceeds on a failing scan with a warning and has no
\* --allow-over-budget flag (generate_cases_from_tlc_dump.py, the scan-first
\* generation path, proceeds-on-fail; scripts/tla_spec_dev.py
\* run_spec_unit_tests reads no gate). The old guard
\* `complexity_gate = "pass" \/ (complexity_gate = "fail" /\ override)`
\* modeled the withdrawn blocking gate: doctrine withdrew the flag on
\* 2026-07-18 as degeneracy, the removal was deferred to MF-023 and never
\* done, and the model kept asserting a refusal the program does not perform.
\* The recorded verdict itself survives as complexity_gate -- an observable
\* fact AnalyzeComplexity records, read by no transition.
\* @command RunSpecUnitTests
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.test_process
\* @port TlaSpecDevCliPort.runner_process
\* @port TlaSpecDevCliPort.spec_tree
RunSpecUnitTests(root, ticket) ==
  /\ setup_phase >= 2
  /\ root = spec_root
  /\ ticket \in ActiveTickets
  \* MF-025: was `ticket_phase[ticket] >= 2` on an active ticket. Active caps
  \* the lifecycle at TicketSpecUnitTestsPassed, so the range is 3..4. This
  \* stays a range rather than an equality on purpose: tightening it would
  \* delete the idempotent re-run self-loop on an already-passing ticket.
  /\ ticket_state[ticket] \in TicketCurrentReady..TicketSpecUnitTestsPassed
  \* MF-014: generation produces the corpus, then the case caps are measured
  \* over it. The corpus is complete either way -- the gate refuses, it never
  \* trims -- so a failing verdict advances nothing and reports instead.
  \* The case caps have no override and never will: raising the cap with a
  \* recorded rationale is the accept path, and that is a different verdict
  \* rather than a bypassed one.
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
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  complexity_gate,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

\* CLI: `tla-spec-dev --spec-root <root> close ticket <ticket-name>`
\* Closes ticket only after current == desired and spec-unit tests passed.
\* @command CloseTicket
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.spec_tree
\* @port TlaSpecDevCliPort.spec_tree_delete
\* @port TlaSpecDevCliPort.git_metadata
CloseTicket(root, ticket) ==
  /\ setup_phase >= 2
  /\ root = spec_root
  /\ ticket \in ActiveTickets
  \* MF-025: leaving active and entering closed was a single simultaneous
  \* move that left ticket_phase UNCHANGED, so it is exactly this one step.
  /\ ticket_state[ticket] = TicketSpecUnitTestsPassed
  /\ ticket_state' = [ticket_state EXCEPT ![ticket] = TicketClosed]
  /\ lastCommand' = "tla-spec-dev close ticket"
  /\ result' = CommandResult(TRUE, NoReason, "Open next ticket or close workflow")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  complexity_gate,
                  corpus_gate,
                  effect_conformance,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

\* CLI: `tla-spec-dev --spec-root <root> close ticket <ticket-name>` taken under
\* one of the six GUARD-WEAKENING FLAGS.
\* RC-01, owner decision 2026-08-01 (MF-026 round-2 reservation). This is the
\* SAME shipped command as CloseTicket; what differs is that `--accept-new`
\* skips the current == desired check and overwrites current/ from desired/,
\* and `--allow-open` accepts a ticket whose plan status is not closed/done.
\* Both bypass the precondition CloseTicket guards on, so the transition is
\* modeled with the precondition REMOVED rather than with a flag input: a flag
\* the guard ignores would be presentation, and presentation is what this
\* action exists to stop representing.
\*
\* Note what the guard below says and does not say. It requires the ticket to
\* be ACTIVE -- a ticket that was never opened cannot be closed by any flag --
\* and nothing else. TicketOpened is reachable here, which is exactly the
\* claim: a ticket can reach a closed stage having passed no spec-unit run.
\* ClosedTicketsPassedSpecUnitTests is narrowed to GuardedClosedTickets for
\* precisely this reason; see the tombstone on that invariant.
\*
\* Which of the six was used is NOT distinguished, and that is per-flag
\* granularity rather than an omission -- the inventoried limitation covering
\* the other 72 options is untouched. What each of them does, stated so the
\* transition is not read as more uniform than it is:
\*   --accept-new         (close ticket)        skips the current == desired
\*                                              check and overwrites current/
\*                                              from desired/;
\*   --allow-open         (close ticket)        snapshots a ticket whose plan
\*                                              status is not closed/done;
\*   --no-promote-current (close ticket)        closes without promoting ticket
\*                                              desired/ into project current/;
\*   --validate-only      (run spec-unit-tests) reports a passing run that
\*                                              executed no case body;
\*   --force / --dry-run  (scaffold, open)      overwrite, or write nothing at
\*                                              all, under a command whose whole
\*                                              contract is what it wrote.
\*
\* A RECORDED LIMIT OF OBSERVATION, not of this model: the first three reach the
\* close path and are recorded there (scripts/spec_evolution.py writes
\* `guard_weakening` into the append-only history entry, which is what makes
\* this state externally observable at all). The last three weaken an EARLIER
\* step, so a close that follows one of them is in fact one of these closes
\* while the close path cannot see which flag did it. The model represents the
\* fact -- this close did not pass the guarded precondition -- and the record
\* names the flags it can name.
\* @command CloseTicketWeakened
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.spec_tree
\* @port TlaSpecDevCliPort.spec_tree_delete
\* @port TlaSpecDevCliPort.git_metadata
CloseTicketWeakened(root, ticket) ==
  /\ setup_phase >= 2
  /\ root = spec_root
  /\ ticket \in ActiveTickets
  /\ ticket_state' = [ticket_state EXCEPT ![ticket] = TicketClosedWeakened]
  /\ lastCommand' = "tla-spec-dev close ticket --accept-new"
  /\ result' = CommandResult(TRUE, NoReason, "Closed under a guard-weakening flag -- the spec-unit precondition was not checked")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  complexity_gate,
                  corpus_gate,
                  effect_conformance,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

\* CLI: `tla-spec-dev --spec-root <root> analyze architecture`
\* AC-01/AC-02: emits the ARCHITECTURE the diagram implies -- components as
\* variable clusters, the single writer of each variable, and the crossings
\* that are its ports -- and (AC-02) compares it against the production code's
\* real dependency structure. Like complexity, it is a SCANNER: it records a
\* verdict and blocks nothing. "divergent" means the code has edges the model
\* declares no port for; "unmappable" means the reflexion map could not be
\* built at all, which is "I could not measure this" rather than a finding.
\* No guard anywhere reads architecture_scan, deliberately: see
\* references/architecture_tractability.md, "Advisory, Not Blocking".
\*
\* RC-01 (MF-026 G-8): `--baseline` compares this scan against a previous one
\* and reports the DIVERGENCE DELTA. Its outcome is a second externally
\* observable result of the same command and none of its values is derivable
\* from architecture_scan, so it is its own variable rather than a widened scan
\* domain: "the code moved toward the boundaries the model draws" and "this
\* scan is coherent" are different facts, and the ledger records them
\* separately (scripts/complexity_ledger.py ARCHITECTURE_DELTA_DIRECTIONS).
\* The two refusals matter more than the three measurements: `unattributable`
\* is what the tool returns when the two scans did not share a declared map and
\* model -- the gaming move AC-04 demonstrated, where re-placing one module in
\* the map alone moves the divergence count 0 -> 6 with no source change -- and
\* `unverified` is the structural MF-020 rule, a count that fell without the
\* edges that disappeared being enumerated. Modeling only `improved` /
\* `worsened` / `unchanged` would represent exactly the half of this command
\* that can be gamed.
\* @command AnalyzeArchitecture
\* @result CliWorkflowResult
\* RC-01 (MF-026 G-1/G-2/G-4): this action's row in effects.actions was ABSENT
\* in all three manifests -- the only non-stutter action with no row -- and the
\* line that stood here read "No @port: the scan reads the model and the source
\* tree and prints." It does not only print: `--out` writes the descriptor
\* (analyze_architecture.py) and the reflexion report
\* (architecture_reflexion.py). The write is now constrained to the
\* `evidence_report` port's declared `**/results/**` target
\* (scripts/spec_paths.py resolve_evidence_out), so the declaration below is
\* true of every caller rather than of the documented one.
\* @port TlaSpecDevCliPort.evidence_report
AnalyzeArchitecture(root) ==
  /\ setup_phase >= 4
  /\ root = spec_root
  /\ architecture_scan' \in {"coherent", "divergent", "unmappable"}
  \* An unmappable scan cannot yield a MEASURED delta: with no comparable
  \* reflexion report the count that would be compared does not exist, so the
  \* only honest outcomes are "no comparison was asked for" and the two
  \* refusals. This is the same rule as the scan's own -- a refusal beats a
  \* false clean -- applied one level up.
  /\ architecture_delta' \in IF architecture_scan' = "unmappable"
                              THEN {"unknown", "unverified", "unattributable"}
                              ELSE {"unknown", "improved", "worsened", "unchanged",
                                    "unverified", "unattributable"}
  /\ lastCommand' = "tla-spec-dev analyze architecture"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev run spec-unit-tests")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  ticket_state,
                  complexity_gate,
                  corpus_gate,
                  effect_conformance,
                  kill_test >>

\* CLI: `tla-spec-dev --spec-root <root> generate cases <spec.tla> <cfg> --out <dir>`
\* RC-01 (MF-026 G-6), the headline gap: CASE-MODULE GENERATION -- this epic's
\* flagship feature -- was ENTIRELY UNREPRESENTED. scripts/case_modules.py
\* shipped a standalone main() unreachable from build_parser, and
\* scripts/generate_cases_from_tlc_dump.py spawned java/TLC, rmtree'd its
\* metadir and wrote generated packages with no action, no port and no CLI
\* subcommand anywhere in the model. CM-01 and RP-03 BOTH CLOSED "ZERO MODEL
\* DELTA" against surface the model does not contain, and all four oracles
\* reported green -- because every oracle in this toolchain is bounded to what
\* is already modeled, so unmodeled surface is never generated into a case,
\* never adapted and never mutated. That is the whole reason the coverage-audit
\* gate exists.
\*
\* Guarded on setup_phase >= 4 for the same reason AnalyzeCorpus and
\* RunKillTest are: generation measures the corpus against the manifest case
\* caps at the end of the run, and reading a cap before budgets are recorded
\* would silently measure against a default nobody negotiated.
\*
\* Records NO verdict. The command writes a corpus; it does not measure one.
\* corpus_gate deliberately stays UNCHANGED here -- setting it back to
\* "unknown" on every generation would falsify
\* SpecUnitTestsRequireMeasuredCorpus for a ticket that legitimately passed
\* earlier, which is asserting something the program does not do.
\* @command GenerateCases
\* @result CliWorkflowResult
\* @port TlaSpecDevCliPort.corpus_process
\* @port TlaSpecDevCliPort.spec_tree
\* @port TlaSpecDevCliPort.spec_tree_delete
GenerateCases(root) ==
  /\ setup_phase >= 4
  /\ root = spec_root
  /\ lastCommand' = "tla-spec-dev generate cases"
  /\ result' = CommandResult(TRUE, NoReason, "tla-spec-dev analyze corpus <cases-dir>")
  /\ UNCHANGED << setup_phase,
                  spec_root,
                  ticket_state,
                  complexity_gate,
                  corpus_gate,
                  effect_conformance,
                  kill_test,
                  architecture_scan,
                  architecture_delta >>

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
  \/ \E root \in SpecRoots:
      AnalyzeArchitecture(root)
  \/ \E root \in SpecRoots:
      GenerateCases(root)
  \/ \E root \in SpecRoots:
      RunEffectConformance(root)
  \/ \E root \in SpecRoots:
      RunKillTest(root)
  \/ \E root \in SpecRoots, ticket \in Tickets:
      RunSpecUnitTests(root, ticket)
  \/ \E root \in SpecRoots, ticket \in Tickets:
      CloseTicket(root, ticket)
  \/ \E root \in SpecRoots, ticket \in Tickets:
      CloseTicketWeakened(root, ticket)
  \/ Stutter

TypeInvariant ==
  /\ setup_phase \in 0..5
  /\ spec_root \in SpecRoots \cup {NoRoot}
  \* RC-01: 0..6 -- TicketClosedWeakened is the sixth stage.
  /\ ticket_state \in [Tickets -> 0..6]
  \* MF-025: retained by name. Both are now structurally true, since
  \* ActiveTickets and ClosedTickets are defined by comprehension over
  \* Tickets, but a named safety property that is deleted is
  \* indistinguishable at review from one that was lost.
  /\ ActiveTickets \subseteq Tickets
  /\ ClosedTickets \subseteq Tickets
  /\ complexity_gate \in {"unknown", "pass", "fail"}
  /\ corpus_gate \in {"unknown", "pass", "fail"}
  /\ effect_conformance \in {"unknown", "clean", "gaps", "dead_surface", "unobservable"}
  /\ kill_test \in {"unknown", "pass", "below_floor", "incomplete_catalog"}
  \* AC-01: an advisory RECORD, not a gate. No action guards on it and no
  \* value of it refuses anything -- "divergent" is a fact the owner reads.
  /\ architecture_scan \in {"unknown", "coherent", "divergent", "unmappable"}
  \* RC-01 (G-8): the delta's domain is the shipped one -- the five direction
  \* verdicts scripts/complexity_ledger.py records, plus "unknown" for a scan
  \* that was not asked for a comparison. Like architecture_scan it is an
  \* advisory RECORD: no action guards on it and no value of it refuses
  \* anything. "worsened" is recorded, never refused.
  /\ architecture_delta \in {"unknown", "improved", "worsened", "unchanged", "unverified", "unattributable"}

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

\* MF-025: retained by name. The ordinal makes this a tautology -- a ticket
\* has one state, and TicketClosed is not in TicketOpened..TicketSpecUnitTestsPassed
\* -- but the property is still required and is now guaranteed by construction
\* rather than by checking.
NoOpenClosedOverlap ==
  ActiveTickets \cap ClosedTickets = {}

\* RC-01: TicketReached, not >=. See the tombstone on
\* ClosedTicketsPassedSpecUnitTests -- a weakened close reached NEITHER of
\* these stages, and `>=` would have claimed it reached both.
CurrentRequiresDesired ==
  \A ticket \in Tickets:
    TicketReached(ticket, TicketCurrentReady)
      => TicketReached(ticket, TicketDesiredReady)

SpecUnitTestsRequireCurrent ==
  \A ticket \in Tickets:
    TicketReached(ticket, TicketSpecUnitTestsPassed)
      => TicketReached(ticket, TicketCurrentReady)

\* CD-09 (G2): SpecUnitTestsRequireAnalyzedGate REMOVED, deliberately and with
\* this tombstone rather than silently -- a deleted safety property must be
\* distinguishable at review from a lost one (the MF-020/MF-022 retention
\* precedent, applied in reverse). The invariant asserted that no ticket
\* passes spec-unit tests before analyze complexity records a verdict. That
\* was the blocking-gate era's property: it held only because the old
\* RunSpecUnitTests guard refused to fire while complexity_gate = "unknown".
\* The shipped program has no such refusal -- `run spec-unit-tests` performs
\* no complexity check, and the descriptor is advisory (MF-036/CD-01) -- so
\* the invariant claimed an assurance the program does not provide, which is
\* precisely the defect coverage-audit run 2 recorded as gap G2. TLC evidence
\* of the removal being real: states with a ticket at
\* TicketSpecUnitTestsPassed and complexity_gate = "unknown" are now
\* reachable (distinct states grew when the guard came out).

\* MF-014: no ticket ever passes spec-unit tests without its generated corpus
\* having been measured against the case caps. Reaching phase 3 means cases
\* were generated and run, and RunSpecUnitTests records a cap verdict on every
\* such transition -- so a corpus that was never measured cannot be behind a
\* passing ticket. The companion property, that a case is never removed to make
\* the verdict "pass", is structural rather than checkable here: no action in
\* this module reduces a case count, and no override input reaches the cap.
\* RC-01: TicketReached. TLC FOUND THIS ONE -- with `>=` the first weakened
\* close from TicketOpened violated it in 1,094 states, because a ticket sitting
\* at TicketClosedWeakened satisfied `>= TicketSpecUnitTestsPassed` while no
\* corpus had ever been measured. That violation is the property working: the
\* invariant is about corpora behind PASSING tickets, and a weakened close is
\* not a passing ticket.
SpecUnitTestsRequireMeasuredCorpus ==
  (\E ticket \in Tickets: TicketReached(ticket, TicketSpecUnitTestsPassed))
    => corpus_gate /= "unknown"

\* MF-013: no ticket ever passes spec-unit tests while the representation is
\* blind to a real effect, or while it carries a port no case exercises.
\* Reaching TicketSpecUnitTestsPassed means adapters ran in the sandbox and the
\* diff came back clean -- "unknown" is excluded because the run always records
\* a verdict, and "gaps"/"dead_surface"/"unobservable" are excluded because
\* they are failures. MF-027 added the third: a ticket must not pass on a
\* target the oracle could not see, which is a weaker claim than a gap only in
\* the sense that it reports the absence of evidence rather than the evidence
\* of a defect. Both are disqualifying.
\*
\* This is the invariant form of the rule the 2026-07-18 audit restored. The
\* companion property, that no justification can make a gap acceptable, is
\* structural rather than checkable here: no action in this module takes a
\* justification input, and no transition maps "gaps" to a passing ticket.
\* tests/test_effect_conformance.py proves the same thing about the shipped
\* implementation by asserting a recorded justification does NOT prevent the
\* failure.
\*
\* Why "/= unknown" and not "= clean": RunEffectConformance is a standalone
\* re-measurement enabled at any point after setup, so a later run can legally
\* find gaps in a program whose ticket passed earlier -- that is a real
\* sequence, and TLC finds it. Asserting "= clean" here would therefore be a
\* false invariant, and weakening the ACTION to make it true would delete the
\* re-measurement rather than describe the program. The gate itself lives where
\* it belongs, in RunSpecUnitTests: ticket_state advances only when
\* effect_conformance' = "clean", with no override and no justification input
\* anywhere in the conjunction. This invariant states the part that holds
\* globally -- a ticket never passes on an unmeasured effect surface -- and
\* matches SpecUnitTestsRequireMeasuredCorpus, which is weakened for exactly
\* the same reason.
SpecUnitTestsRequireMeasuredEffects ==
  (\E ticket \in Tickets: TicketReached(ticket, TicketSpecUnitTestsPassed))
    => effect_conformance /= "unknown"

\* MF-025: retained by name; now structurally true, since TicketClosed (5)
\* is itself >= TicketSpecUnitTestsPassed (4) and the only way into it is
\* through that stage.
\*
\* RC-01 NARROWING, recorded here rather than done silently -- a weakened
\* safety property must be distinguishable at review from one that was lost
\* (the MF-020/MF-022 retention precedent, applied to a weakening). The
\* quantifier moved from ClosedTickets to GuardedClosedTickets. It had to.
\* TicketClosedWeakened is 6, and 6 >= 4, so leaving the quantifier over
\* ClosedTickets would have kept this invariant TRUE BY ACCIDENT OF THE ORDINAL
\* ENCODING while a weakened close never passed a spec-unit run -- the model
\* would read as an assurance that every closed ticket was validated, which is
\* exactly what `--accept-new` and `--allow-open` exist to make false.
\*
\* What this invariant now claims is the whole of what TLC can prove: a close
\* taken THROUGH THE GUARD passed spec-unit tests. What it deliberately no
\* longer claims is anything about a close taken around the guard, and the
\* absence of that claim is the finding. There is no companion invariant
\* asserting the weakened path is safe, because it is not.
ClosedTicketsPassedSpecUnitTests ==
  \A ticket \in GuardedClosedTickets:
    TicketReached(ticket, TicketSpecUnitTestsPassed)

\* RC-01: the companion, and the only new named property this ticket adds. It
\* states what a weakened close IS, positively, so the narrowing above cannot be
\* read as the model simply having less to say: a ticket closed around the guard
\* never reached the spec-unit stage, and no invariant in this module may be
\* read as evidence that it did.
\*
\* It is deliberately NOT "weakened closes are forbidden". The shipped CLI
\* offers the flags, they have legitimate uses, and an invariant asserting a
\* refusal the program does not perform is precisely the defect CD-09's G2
\* removed. What is asserted is that the record distinguishes the two, which is
\* the thing that was missing: `--accept-new` and `--allow-open` bypassed a
\* precondition TLC proved over 1,292,951 states and no oracle could see it.
WeakenedClosesCertifyNothing ==
  \A ticket \in WeakenedClosedTickets:
    ~TicketReached(ticket, TicketSpecUnitTestsPassed)

\* MF-016: a kill-test verdict exists only after the workflow it measures.
\* RunKillTest guards on setup_phase >= 4 (budgets recorded), because the floor
\* it gates against IS a budget -- reading kill_rate_floor before budgets are
\* recorded would silently measure against a default nobody negotiated, which
\* is the "falls back to" degeneracy the doctrine forbids. This invariant
\* states the consequence globally: a measured verdict implies the budgets it
\* was measured against exist.
\*
\* Deliberately stated as an implication from the verdict rather than as
\* "closing a ticket requires kill_test = pass". That stronger property is the
\* promotion interlock, and it is NOT true of the shipped CLI yet -- see the
\* honest-scope note on RunKillTest. An invariant that TLC proves about a model
\* the program does not implement is worse than no invariant, because it reads
\* as an assurance.
KillTestVerdictRequiresBudgets ==
  kill_test /= "unknown" => setup_phase >= 4

Spec ==
  Init /\ [][Next]_vars

=============================================================================
