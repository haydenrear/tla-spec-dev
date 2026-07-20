# Skill feedback — spec-double-compiler / tla-spec-dev

`references/migration.md` Phase 6: a migration is not done when the models
converge. It is done when everything the skill **could not express** has been
turned into a concrete recommendation against the skill repository. The skill
improves only through what real migrations fail to express.

This file is **append-only by convention**. Close-out creates it once and
thereafter only appends. Never rewrite or delete an existing finding — a filled
finding is evidence.

## How to use this file

1. At each close-out the CLI appends a `## Close-out …` entry below.
2. Fill in that entry's `feedback_status`, then record one `### SF-NNN` finding
   per thing the skill could not express.
3. **Turn every finding into a ticket or PR against the spec-double-compiler
   repository** — that is the point of this file, not the record-keeping:

   ```
   gh issue create --repo haydenrear/tla-spec-dev \
     --title "<SF-NNN one-line title>" --body-file <extract of the finding>
   ```

   Then set `recommendation:` to the resulting URL and `status: filed`.
4. If you looked and there was genuinely nothing, set
   `feedback_status: none-found`. **Silence is not an answer** — an unreviewed
   entry is recorded as unresolved in the close history.

## The four prompt categories

- `surviving-mutants` — Surviving mutants
- `unmodelable-effects` — Unmodelable effects
- `budget-and-metric` — Budget adjustments and metric calibration
- `profile-schema-cli` — Profile, schema, and CLI workarounds

## Finding format

Every finding is a `### SF-NNN` heading followed by `- key: value` lines. The
close path parses these, so keep the shape.

Fields required on every finding:

- `category:` one of `surviving-mutants`, `unmodelable-effects`, `budget-and-metric`, `profile-schema-cli`
- `target:` the exact tool surface that proved inadequate — command, script
  path and function, budget key, profile rule, or manifest field. Not "the CLI".
- `observed_on:` the real repository/module/ticket it was run against. A finding
  without a real target is a wish, not evidence.
- `evidence:` a durable path (command output, TLC log, report) — not prose.
- `severity:` one of `blocks-migration`, `silent-data-loss`, `wrong-result`, `manual-workaround`, `friction`
- `root_cause:` one of `tool`, `spec`, `target`, `unknown` — whether the
  tool's code, its specification, or the target under migration was at fault.
  A correct implementation of a wrong spec is `spec`; filing it against the
  code files it in the wrong place.
- `workaround_applied:` what the migration had to do to proceed, or `none`.
- `recommendation:` `ticket <url>` or `PR <url>` against spec-double-compiler / tla-spec-dev
- `status:` `open`, `filed`, or `wontfix`

Category-specific fields, so the common cases are structured rather than prose:

- `surviving-mutants` — `mutant:`, `operator:`, `location:`, `why_unreached:`
  (which generator, strategy, or profile rule could not reach it)
- `unmodelable-effects` — `effect:`, `why_not_port_state:`, `modeled_as:`
  (or `unmodeled`)
- `budget-and-metric` — `budget_key:`, `default_value:`, `value_used:`,
  `gated_quantity:` vs `measured_quantity:` (name both when a gate compares
  quantities that are not commensurable), `metric_blind_spot:` (what a passing
  metric failed to notice)
- `profile-schema-cli` — `surface:`, `forced_workaround:`, `data_loss:`
  (`yes`/`no`)

## Worked examples

These are real findings this epic produced *before* this template existed. They
are the calibration for what a good finding looks like; they are recorded here
as `SF-000x` examples and are excluded from filing status.

### SF-000a — Projected complexity reduction required deleting real behavior
- category: budget-and-metric
- target: scripts/analyze_complexity.py — projected-reduction reporting
- observed_on: tla-spec-dev @ MF-020 (ticket_phase ordinal collapse)
- evidence: specs/.history/modular-fuzzing-epic/ticket-*-MF-020/
- severity: wrong-result
- root_cause: tool
- gated_quantity: distinct reachable states
- measured_quantity: generated states
- metric_blind_spot: deleted self-loops. Reproducing the projected -13.1%
  required tightening a guard from `>= 2` to `= 2`, deleting a legitimate
  idempotent re-fire transition. The distinct-state gate is structurally blind
  to that, so a behavior deletion scored as a re-representation win.
- workaround_applied: projection withdrawn by hand after transition-level diff
- recommendation: ticket (example only)
- status: wontfix

### SF-000b — Promotion destroyed files unique to specs/current
- category: profile-schema-cli
- target: scripts/spec_evolution.py::replace_tree (ticket-close promotion)
- observed_on: tla-spec-dev @ MF-012, MF-020, MF-021
- evidence: tests/test_promotion_preserves_current.py
- severity: silent-data-loss
- root_cause: tool
- surface: `tla-spec-dev close ticket` promotion step
- forced_workaround: restore deleted regression tests from git history
- data_loss: yes
- recommendation: ticket https://github.com/haydenrear/tla-spec-dev/issues/22
- status: filed

### SF-000c — PATH wrapper ran pre-epic code for an entire epic
- category: profile-schema-cli
- target: `tla-spec-dev` PATH wrapper -> ~/.skill-manager/skills/spec-double-compiler
- observed_on: tla-spec-dev @ modular-fuzzing epic (all tickets)
- evidence: specs/desired_program_model/ticket_plan.yaml (toolchain_rule)
- severity: wrong-result
- root_cause: tool
- surface: skill installation / PATH shim
- forced_workaround: pin every lifecycle command to
  `python3 scripts/tla_spec_dev.py --spec-root specs ...`
- data_loss: yes — the stale wrapper is why the promotion defect fired three
  times, including once after its fix had merged
- recommendation: ticket (example only)
- status: wontfix

### SF-000d — Bound gate compared incommensurable quantities
- category: budget-and-metric
- target: scripts/analyze_complexity.py — state-space bound gate
- observed_on: tla-spec-dev @ MF-011
- evidence: specs/.history/modular-fuzzing-epic/ticket-*-MF-011/
- severity: blocks-migration
- root_cause: spec
- budget_key: max_distinct_states
- default_value: 50000
- value_used: new `max_state_space_bound` added (MF-022)
- gated_quantity: static state-space upper bound (1,179,648)
- measured_quantity: actual reachable distinct states (2,923)
- metric_blind_spot: a ~400x over-approximation failed a model 17x *under* its
  own budget; the tool's own recommended optimum still failed the gate.
- workaround_applied: none — gate reported its own failure rather than tuning
- recommendation: ticket https://github.com/haydenrear/tla-spec-dev/issues/28
- status: filed

---

## Close-out ticket MF-017

- close_scope: ticket
- close_id: MF-017
- workflow: modular-fuzzing-epic
- closed_at: 2026-07-18T21:40:12+00:00
- summary: MF-017: close-out emits the migration.md Phase 6 skill-feedback retro into specs/results/skill_feedback.md (four prompt categories, structured findings, filing instructions against spec-double-compiler) and records in the append-only history whether feedback was filed and where. Zero model delta: close-out gains a file effect, not a command (MF-021 precedent).
- feedback_status: items-recorded

Set `feedback_status` to `none-found` or `items-recorded`, then record findings as `### SF-NNN` blocks below using the field list above.
Every finding must become a ticket or PR against spec-double-compiler / tla-spec-dev; put its URL in `recommendation:` and set `status: filed`.

### SF-001 — scaffolded fixture workflow cannot exercise two consecutive closes
- category: profile-schema-cli
- target: scripts/scaffold_spec_workflow.py — emitted desired_program_model/ticket_plan.yaml
- observed_on: tla-spec-dev @ MF-017 (SkillFeedbackCloseOutAdapter)
- evidence: specs/current/production_adapters.py::SkillFeedbackCloseOutAdapter
- severity: manual-workaround
- root_cause: tool
- surface: `tla-spec-dev scaffold workflow`
- forced_workaround: the adapter hand-appends a second ticket entry to
  ticket_plan.yaml before the second `open ticket`, because the scaffolded plan
  contains exactly one ticket and `close ticket` refuses an id that is not in
  the plan.
- data_loss: no
- note: any behavior that only appears ACROSS closes — accumulation,
  append-only-ness, history sequencing — is untestable against the stock
  fixture without this workaround. That is a class of regression the fixture
  currently cannot catch.
- recommendation: (none yet) — recommend a `--tickets N` option on
  `scaffold workflow`, or a multi-ticket fixture plan, so cross-close behavior
  is testable without hand-editing YAML
- status: open

### SF-002 — plan prescribed model state that implementation showed to be wrong
- category: budget-and-metric
- target: specs/desired_program_model/ticket_plan.yaml — per-ticket
  `desired_actions` / `current_increment.model_state`
- observed_on: tla-spec-dev @ MF-017
- evidence: specs/tickets/MF-017/results/complexity-ledger.md
- severity: friction
- root_cause: spec
- gated_quantity: prescribed model state (`skill_feedback`, `EmitSkillFeedback`)
- measured_quantity: actual model delta after implementation (zero)
- metric_blind_spot: the plan fields are written at scheduling time and are
  never reconciled against what implementation proves. MF-011 and MF-020 each
  hit the same shape (a spec-level error with a correct implementation); this
  is the third instance, so it is a pattern, not an accident. Implementing the
  prescription literally would have cost bound 221,184 -> 663,552 to represent
  a document field.
- workaround_applied: implemented at zero delta and recorded an `outcome:` field
  on the plan entry explaining the deviation, for post-merge review
- recommendation: (none yet) — recommend the close path diff prescribed
  `desired_actions`/`model_state` against the promoted model and require an
  explicit `outcome:` when they disagree, rather than leaving the plan silently
  contradicting the accepted model
- status: open

### SF-003 — promotion silently discards edits to seeded specs/current files
- category: profile-schema-cli
- target: scripts/spec_evolution.py::promote_current_tree — promotion report
- observed_on: tla-spec-dev @ MF-017 (specs/current/spec_manifest.yaml)
- evidence: specs/tickets/MF-017/results/complexity-ledger.md
- severity: manual-workaround
- root_cause: tool
- surface: `tla-spec-dev close ticket` promotion step
- forced_workaround: reapply the edit to specs/current after close and commit it
  separately
- data_loss: yes — recoverable, but silent
- note: MF-021 made promotion enumerate what it REMOVED and PRESERVED, which is
  why this was caught at all. It does not enumerate what it OVERWROTE. An edit
  made to a seeded specs/current file during a ticket is reverted by promotion
  with no mention in the report, and the close still reports success. The
  overwrite itself is correct (specs/current is a working copy promoted from the
  ticket); the silence is not.
- recommendation: (none yet) — recommend the promotion report also enumerate
  overwritten paths whose content changed, the same way it already enumerates
  removed and preserved paths
- status: open

## Close-out ticket MF-014

- close_scope: ticket
- close_id: MF-014
- workflow: modular-fuzzing-epic
- closed_at: 2026-07-18T22:39:57+00:00
- summary: Corpus diagnostics and hard case caps. Case caps are hard gates in the shape of MF-011's state-space bound: over budget reports and exits nonzero, never trims. No code path drops, filters, samples, or truncates a case to fit a budget. Diagnostics report count per (action, label class), dominant and starved strata, and what varies across the redundant group, classified into unconstrained ordering / interchangeable values / action enabled across equivalent states. Labelers repurposed to diagnostic strata; remediation is a recommendation requiring user approval; named regression traces always retained. Accept path is raising the cap in spec_manifest.yaml with a recorded rationale. Model delta: corpus_gate + AnalyzeCorpus, 8->9 vars, 11->12 actions, deviating from the stale DistillCorpus/corpus_distilled plan fields.
- feedback_status: items-recorded

### SF-004 — the minimal YAML fallback parser could not read the repository's own manifests

- category: profile-schema-cli
- target: scripts/extract_spec_manifest.py::_parse_list
- observed_on: tla-spec-dev @ MF-014
- evidence: specs/tickets/MF-014/results/complexity-ledger.md
- severity: silent-wrong-result
- root_cause: tool
- surface: every budget gate, via scripts/budgets.py::load_budgets
- data_loss: no, but every gate read the WRONG thresholds
- note: `_parse_list` raised "unexpected indentation" on a plain-scalar list
  item wrapped onto continuation lines, which `specs/current/spec_manifest.yaml`
  contains. PyYAML is an optional dependency and is absent in this environment
  (`uv run --with pytest python -c "import yaml"` fails), so the fallback parser
  is the ONLY parser. The parse failure was swallowed by
  `budgets._read_manifest`, which returns None on any exception, so
  `load_budgets` fell back to documented defaults with a warning. Net effect: a
  negotiated budget recorded in the manifest was silently ignored by
  `analyze complexity`, case generation, and the adapter runner. This ticket's
  entire "raise the cap with a rationale" accept path would have been a no-op.
- workaround_applied: none — fixed at the source in this ticket by folding
  continuation lines into the scalar, per YAML semantics
- recommendation: (none yet) — the parse bug is fixed, but the SHAPE of the
  defect remains: `_read_manifest` catches bare `Exception` and returns None,
  converting any future parser gap into a silent downgrade to defaults. That is
  the "fall back to default budgets with a warning" degeneracy already named in
  architecture_tractability.md "No Degenerate Escapes". MF-023 absorbed the
  purge of that fallback from the withdrawn MF-024 and should treat a manifest
  that exists but cannot be parsed as a hard failure, distinct from a manifest
  that is absent.
- status: open

### SF-005 — a corpus documented in four places as committed is not committed

- category: docs-and-examples
- target: references/examples.md:48, references/edge-cases.md:84,
  references/testgraph_adapters.md:141, examples/distributed_history/README.md:34
- observed_on: tla-spec-dev @ MF-014
- evidence: specs/tickets/MF-014/results/deferred-validations.md
- severity: friction
- root_cause: spec
- gated_quantity: the 732-case ecommerce corpus named as this ticket's primary
  test fixture
- measured_quantity: 4 external traces + 4 external cases + 4 internal cases
  actually committed
- metric_blind_spot: the 732 figure is real but is produced at run time under
  `test_graph/build/validation-reports/<run>/`, which is not committed. The
  ticket, the issue, and the assignment all read the references as describing a
  committed artifact and pointed the implementer at
  `examples/distributed_history/specs/generated/testgraph/traces/`, which holds
  4 files. Under the epic-wide spec-case execution deferral the corpus cannot be
  regenerated to check, so the divergence is only discoverable by opening the
  directory.
- workaround_applied: reconstructed the documented distribution as
  `tests/corpus_fixtures.py`, labelled a fixture in its module docstring, and
  additionally ran the CLI against the genuinely committed 4-case corpus so at
  least one end-to-end path touches real artifacts
- recommendation: (none yet) — recommend the reference text state explicitly
  that the 732-case corpus is regenerated per run and not committed, and that
  MF-023 re-run `tla-spec-dev analyze corpus` against the real regenerated
  output and record the actual distribution
- status: open

### SF-006 — plan prescribed model state for a scope that had been withdrawn

- category: budget-and-metric
- target: specs/desired_program_model/ticket_plan.yaml — MF-014
  `desired_actions: [DistillCorpus]` / `current_increment.model_state:
  [corpus_distilled]`
- observed_on: tla-spec-dev @ MF-014
- evidence: specs/tickets/MF-014/results/complexity-ledger.md
- severity: friction
- root_cause: spec
- gated_quantity: prescribed model state (DistillCorpus, corpus_distilled)
- measured_quantity: what the replaced scope actually needs (corpus_gate,
  AnalyzeCorpus)
- metric_blind_spot: this is the FOURTH instance of the SF-002 pattern
  (MF-011, MF-020, MF-017, now MF-014), and the first where the prescribed
  fields name a mechanism the same commit WITHDREW. The objective, acceptance
  criteria, and referenced ticket file were all rewritten for the diagnostics
  scope while `desired_actions`/`model_state` kept describing distillation.
  Implementing them literally would have built the filter the ticket exists to
  forbid.
- workaround_applied: implemented the gate the replaced scope requires and
  recorded the deviation in the plan entry's `outcome:` field, per the MF-017
  precedent
- recommendation: (none yet) — reinforces SF-002. A scope replacement should be
  required to rewrite or explicitly null the `desired_actions` /
  `current_increment` fields in the same change, since a stale prescription
  that contradicts the new objective is worse than an absent one
- status: open

Every finding must become a ticket or PR against spec-double-compiler / tla-spec-dev; put its URL in `recommendation:` and set `status: filed`.

## Close-out ticket MF-025

- close_scope: ticket
- close_id: MF-025
- workflow: modular-fuzzing-epic
- closed_at: 2026-07-18T23:11:53+00:00
- summary: MF-025: collapse active_tickets, closed_tickets and ticket_phase into one ticket_state ordinal (0..5). Premise re-verified with TLC in both directions. Retention exact: 9,011 distinct / depth 24 / 87,464 generated, unchanged. Declared bound measured 663,552 -> 34,992 (18.96x).
- feedback_status: unreviewed

Set `feedback_status` to `none-found` or `items-recorded`, then record findings as `### SF-NNN` blocks below using the field list above.
Every finding must become a ticket or PR against spec-double-compiler / tla-spec-dev; put its URL in `recommendation:` and set `status: filed`.

## Close-out ticket MF-015

- close_scope: ticket
- close_id: MF-015
- workflow: modular-fuzzing-epic
- closed_at: 2026-07-19T18:23:24+00:00
- summary: MF-015: external channel enforcement. Required channel per Test Graph binding (http/cli/fs/queue/k8s, explicitly extensible), transitive static import analysis proving no Test Graph adapter imports the declared production package, violations reported with adapter/import/remediation, and required double|real port binding configurations with at least one real port so graph runs express integration-ladder rungs. Shared gate in scripts/testgraph_channels.py applied by both run_generated_case_adapters.py (external view) and export_testgraph_cases.py. Zero model delta, reasoned and recorded: the gates are Test-Graph-invoked and no modeled CLI command reaches them. TLC 87,464/9,011/depth 24 and bound 34,992 identical to baseline; 226 repository tests, 27+24 spec-unit, specWorkflow 8/8, cliWorkflow 2/2.
- feedback_status: unreviewed

Set `feedback_status` to `none-found` or `items-recorded`, then record findings as `### SF-NNN` blocks below using the field list above.
Every finding must become a ticket or PR against spec-double-compiler / tla-spec-dev; put its URL in `recommendation:` and set `status: filed`.

## Close-out ticket MF-013

- close_scope: ticket
- close_id: MF-013
- workflow: modular-fuzzing-epic
- closed_at: 2026-07-19T18:59:05+00:00
- summary: Effect conformance harness: declared typed emissions on named ports, sandboxed passive observation, per-case diff. Undeclared observed effect recorded AND FAILS; dead declared surface FAILS; nothing suppresses a gap report (out-of-contract justifications withdrawn 2026-07-18), proven by the inverse test. Spec-case execution deferred to MF-023.
- feedback_status: items-recorded

Set `feedback_status` to `none-found` or `items-recorded`, then record findings as `### SF-NNN` blocks below using the field list above.
Every finding must become a ticket or PR against spec-double-compiler / tla-spec-dev; put its URL in `recommendation:` and set `status: filed`.

### SF-007 — three manifest parsers disagreed on the repository's own manifest, and the strictest one blocked close

- category: profile-schema-cli
- target: scripts/extract_spec_manifest.py::load_manifest vs scripts/budgets.py::_read_manifest vs the PyYAML parse on the close path
- observed_on: tla-spec-dev @ MF-013, specs/current/spec_manifest.yaml inherited from epic tip 1dcce07 (written by MF-015)
- evidence: specs/.history/modular-fuzzing-epic/ticket-006-MF-013/results/manifest_parser_disagreement.txt
- severity: blocks-migration
- root_cause: tool
- surface: every gate that reads spec_manifest.yaml, plus `close ticket`
- data_loss: no
- note: RECURRENCE of SF-004. An unquoted block-sequence scalar containing a
  colon-space ("... for this ticket: case generation over the") made the file
  invalid YAML. Three parsers, three outcomes on the identical file:
  `extract_spec_manifest.load_manifest` ACCEPTED it and returned budgets;
  `budgets.load_budgets` returned source=None and silently fell back to
  documented defaults, emitting the "no readable spec manifest" warning on
  every `analyze complexity` run for the whole epic; PyYAML on the close path
  raised ScannerError and ABORTED `close ticket MF-013`. So "the manifest"
  meant three different things to three different gates, and the budget gate
  spent the epic reading defaults rather than the declared file. The declared
  values equal the defaults here, so no verdict was wrong -- but a deliberately
  raised budget, which is the doctrine's sanctioned accept path, would have
  been silently ignored. MF-013 is simply the first close to reach the strict
  parser.
- workaround_applied: none — fixed at the source by quoting the scalar (`- >-`),
  wording unchanged; both ticket-local manifests and the promoted
  specs/current/spec_manifest.yaml now parse under all three parsers
- recommendation: SF-004's recommendation, unactioned since MF-014, is what
  would have prevented this: treat a manifest that EXISTS but cannot be parsed
  as a hard failure, distinct from one that is ABSENT. Add to that: the
  repository should have ONE manifest parser. Three parsers with three
  tolerances mean a file can be simultaneously valid and invalid depending on
  which gate reads it, and the most permissive one hides the defect from the
  gates while the strictest one surfaces it only at close. Absorbed into
  MF-023 with SF-004; not filed as a separate issue because it is the same
  defect class and splitting it would fragment the fix.
- status: open

## Close-out ticket MF-027

- close_scope: ticket
- close_id: MF-027
- workflow: modular-fuzzing-epic
- closed_at: 2026-07-19T19:50:48+00:00
- summary: MF-027: effect oracle refuses targets it cannot observe. Observability granted only on positive in-process evidence; unobservable targets and subprocess boundaries FAIL with explicit findings; inverse test proves no config downgrades the verdict; External/test-graph gap documented with follow-up #44.
- feedback_status: unreviewed

Set `feedback_status` to `none-found` or `items-recorded`, then record findings as `### SF-NNN` blocks below using the field list above.
Every finding must become a ticket or PR against spec-double-compiler / tla-spec-dev; put its URL in `recommendation:` and set `status: filed`.

## Close-out ticket MF-016

- close_scope: ticket
- close_id: MF-016
- workflow: modular-fuzzing-epic
- closed_at: 2026-07-19T21:17:14+00:00
- summary: MF-016: mutation kill test (oracle 4). Coverage derived from port/invariant declarations every run; control run refuses a red corpus; kill_rate_floor gate fails below floor with no waiver; survivors point at the variable and action to refine; abstraction validator via --baseline/--compare. Mechanism built and unit/adapter/example-validated; empirical proof over this repository's corpus deferred to MF-023 per epic policy.
- feedback_status: unreviewed

Set `feedback_status` to `none-found` or `items-recorded`, then record findings as `### SF-NNN` blocks below using the field list above.
Every finding must become a ticket or PR against spec-double-compiler / tla-spec-dev; put its URL in `recommendation:` and set `status: filed`.

## Close-out ticket MF-019

- close_scope: ticket
- close_id: MF-019
- workflow: modular-fuzzing-epic
- closed_at: 2026-07-19T22:44:51+00:00
- summary: Mechanize the standing objective: complexity ledger recorded per ticket/workflow close with the delta reported jointly with retention evidence; increases require a recorded justification; a decrease with degraded or unverified retention is rejected at close; the MF-020 self-loop red flag is a hard gate; and the recursive refinement record is required. Zero model delta -- max_state_space_bound is at 70.0% with 1.43x headroom, so no new bounded variable of any cardinality fits; recorded as a finding for MF-023.
- feedback_status: unreviewed

Set `feedback_status` to `none-found` or `items-recorded`, then record findings as `### SF-NNN` blocks below using the field list above.
Every finding must become a ticket or PR against spec-double-compiler / tla-spec-dev; put its URL in `recommendation:` and set `status: filed`.

## Close-out ticket MF-026

- close_scope: ticket
- close_id: MF-026
- workflow: modular-fuzzing-epic
- closed_at: 2026-07-19T23:36:50+00:00
- summary: MF-026: coverage audit gate -- prompt, report template, doctrine, ledger recording, and a worked example that found 19 in-scope gaps and real defects in the prompt itself. Zero model delta.
- feedback_status: unreviewed

Set `feedback_status` to `none-found` or `items-recorded`, then record findings as `### SF-NNN` blocks below using the field list above.
Every finding must become a ticket or PR against spec-double-compiler / tla-spec-dev; put its URL in `recommendation:` and set `status: filed`.

## Close-out ticket MF-023

- ticket: MF-023
- title: Decompose this repository by dogfooding the finished toolchain
- closed: 2026-07-19
- evidence: specs/tickets/MF-023/results
- feedback_status: items-recorded

MF-023 is the epic's first end-to-end run of the finished toolchain against a
real target. Six findings below, all reproduced from recorded commands in
`specs/tickets/MF-023/results/`.

### SF-009 — `analyze complexity` does not resolve EXTENDS, so it scores every decomposed model on a fraction of itself, always toward PASS

- category: budget-and-metric
- target: scripts/analyze_complexity.py (single-file textual parse; `TypeInvariant` looked up by literal name at line 746)
- observed_on: tla-spec-dev @ MF-023, specs/current/{Internal,External}.tla
- evidence: specs/tickets/MF-023/results/analyze-complexity-{presplit,internal,external}.txt
- severity: blocks-migration
- root_cause: tool
- surface: `analyze complexity`, and therefore the `max_state_space_bound` gate on every decomposed model
- data_loss: no
- note: Two mechanisms, one root cause. (1) Cross-module operator references are
  unresolvable: `Internal.tla` constrains all 7 variables via Core-defined domain
  names (`SetupPhases`, `TicketStates`, `ComplexityVerdicts`), and the tool -- which
  understands only literal inline sets -- reports 6 of 7 as "unconstrained by
  TypeInvariant" and computes bound = 3 instead of 233,280. (2) EXTENDSed
  variables are invisible: `External.tla` inherits 7 variables, the tool sees only
  its own 2, reports `bound = 1 (product of 0 bounded dimensions)`, and returns
  VERDICT: PASS. The shipped example's own Internal.tla has been scored this way
  (bound 1, PASS) for the entire epic. THE ERROR IS NEVER CONSERVATIVE: missing
  variables always shrink the bound, so decomposition -- the architecture the
  skill mandates -- silently weakens the skill's own binding gate. Structurally
  unavoidable too: TLA+ forbids redefining an inherited operator, so both views
  cannot carry a `TypeInvariant`, and the tool's single hardcoded name is
  incompatible with a two-view decomposition.
- workaround_applied: none — Internal keeps the literal name `TypeInvariant` so its
  gate stays live; External's reported bound is recorded as vacuous rather than
  banked as a pass
- recommendation: resolve EXTENDS transitively before building the dimension
  table; resolve operator references to set-valued definitions in extended
  modules; treat "no TypeInvariant found" as a hard refusal rather than as
  "everything unconstrained". FILE AGAINST THE SKILL.
- status: open

### SF-010 — no adapter implements the `run(case, ...)` protocol the case runner requires, so the generated-case path has never executed

- category: profile-schema-cli
- target: scripts/run_generated_case_adapters.py vs specs/current/production_adapters.py
- observed_on: tla-spec-dev @ MF-023, first execution of a generated corpus in the epic
- evidence: specs/tickets/MF-023/results/effect-conformance-internal.txt
- severity: blocks-migration
- root_cause: both (skill protocol undocumented at the adapter surface; repository adapters written to the other shape)
- surface: every generated case, effect conformance, and the mutation kill test
- data_loss: no
- note: All 16 adapter classes implement `apply(target_repo, ...)`. The runner
  requires `run(case, ...)`. Every case fails with
  `TypeError: adapter <X> does not define run(case, ...)`. The two paths never
  met: the spec-unit suite calls `apply()` directly, so the adapters are
  thoroughly tested and simultaneously unreachable from the corpus. Because case
  execution was deferred in EVERY ticket of this epic, no run crossed the seam
  until now; the first run that did found it immediately. Downstream, effect
  conformance reports `dead_surface` with 0 observed effects and 5/5 declared
  ports dead, and the kill test cannot compute a rate. Note this also means
  MF-027's predicted `unobservable` verdict for this repository's two
  `process.spawn` ports is NOT reached and remains untested -- execution fails
  before any spawn occurs.
- workaround_applied: partial — `case_adapters.toml` was missing bindings for four
  model actions (`RunEffectConformance`, `RunKillTest`, `UpdateTicketDesired`,
  `UpdateTicketCurrent`); the first two already HAD adapter classes and were simply
  never mapped. All 14 actions are now bound and two adapters written. The
  PROTOCOL mismatch is not fixed — production scope this ticket does not carry.
- recommendation: document the adapter protocol at the surface a repository
  implements, and make the runner fail at BINDING time with a clear protocol
  error rather than at case-execution time with a TypeError per case. A
  conformance check that an adapter satisfies the protocol belongs next to the
  binding validation that already exists. FILE AGAINST THE SKILL.
- status: open

### SF-011 — `analyze corpus` is OOM-killed by exactly the corpus it exists to catch, and the cap is measured only after the cost is paid

- category: budget-and-metric
- target: scripts/corpus_diagnostics.py::load_corpus (line 873, `list(module.CASES)` after import); scripts/generate_cases_from_tlc_dump.py
- observed_on: tla-spec-dev @ MF-023, Internal view at the real model instance
- evidence: specs/tickets/MF-023/results/{corpus-distribution-internal.txt,analyze-corpus-internal.txt}
- severity: blocks-migration
- root_cause: tool
- surface: `analyze corpus`, case generation
- data_loss: no
- note: Generating the Internal view produced 999,635 cases in a 1.35 GB
  `cases.py` -- 4,998x the declared `max_internal_cases_per_component: 200`.
  Running the cap gate over it exits 137 (SIGKILL, OOM): the gate cannot report
  on the condition it was built to detect, and its verdict is available only for
  corpora small enough not to need it. At a reduced instance (15,336 cases) the
  gate works and is genuinely good -- refuses, trims nothing, reports dominant
  and starved strata and a 4112x skew. Two further problems from the same run:
  the cap is measured AFTER generation writes the whole corpus, and the External
  view's generation EXHAUSTED THE DISK (704 MB `.dot` plus a partial `cases.py`)
  and had to be killed; and the corpus is dominated by the always-enabled oracle
  actions (86.8% across five actions) while the bootstrap actions get 1-2 cases
  each.
- workaround_applied: none — the distribution was computed by streaming the file
  with a throwaway script rather than by relaxing anything, and reported as a
  hand computation
- recommendation: stream the corpus rather than importing it; emit cases to a
  streamable format instead of one Python literal; enforce the cap DURING
  generation, refusing before the disk is spent rather than after. FILE AGAINST
  THE SKILL.
- status: open

### SF-012 — `analyze corpus` gates against built-in defaults, silently, when `--manifest` is omitted

- category: budget-and-metric
- target: scripts/corpus_diagnostics.py:541 — `load_budgets(Path("__missing__"), warn=False)`
- observed_on: tla-spec-dev @ MF-023
- evidence: specs/tickets/MF-023/results/override-silent-default.txt
- severity: degrades-model
- root_cause: tool
- surface: `analyze corpus` without `--manifest`
- data_loss: no
- note: THIS IS A SILENT DEFAULT, and it is the DEFAULT PATH. When no manifest is
  supplied the cap gate loads `DEFAULT_BUDGETS` with warnings explicitly
  suppressed -- `warn=False`, unconditionally, not inherited from the caller's
  `warn`. Reproduced: zero occurrences of "warning" or "default" anywhere in the
  output, while the gate prints `cap max_internal_cases_per_component = 200`
  exactly as if that came from the negotiated manifest. Every other override in
  the toolchain requires the agent to TYPE something; this one is what happens
  when the agent says NOTHING, which
  `references/architecture_tractability.md` explicitly forbids. It silently
  discards a negotiated budget (`max_distinct_states` was negotiated 50000 ->
  500000 with a recorded derivation). RECURRENCE of SF-004 and SF-007 in the same
  helper: MF-013 found `analyze complexity` silently falling back and fixed the
  YAML, but this `warn=False` call site was not found then and has been live
  throughout. Found by the MF-026 coverage audit re-run, NOT by this ticket's own
  escape sweep, which tested `--manifest <bad path>` (which warns) and wrongly
  generalized to "the budgets fallback is not silent". That error is corrected in
  findings.md FINDING 9 rather than quietly amended.
- workaround_applied: none
- recommendation: resolve the manifest from `--spec-root` (which the CLI already
  knows) or refuse. `warn=False` should not be reachable from a gate at all: a
  budget the user did not declare is a budget the user did not agree to, and a
  gate that does not say which budgets it used has not reported its verdict.
  FILE AGAINST THE SKILL.
- status: open

### SF-013 — `max_component_actions` counts read-touches, so it is unsatisfiable by any partition of a CLI model

- category: budget-and-metric
- target: scripts/analyze_complexity.py component-size heuristics
- observed_on: tla-spec-dev @ MF-023
- evidence: specs/tickets/MF-023/results/component-cap-satisfiability.txt
- severity: degrades-model
- root_cause: tool
- surface: the component-size gate, and therefore case generation
- data_loss: no
- note: The epic carried `C1 is touched by 14 actions, exceeding
  max_component_actions 8` since MF-011 as a true finding that decomposition
  would resolve at the root. IT DOES NOT, AND CANNOT. Computed from the tool's
  own MEASURED R/W matrix, the singleton `{setup_phase}` alone is touched by 12
  of 14 actions, and `{spec_root}` by 10. Any partition places `setup_phase`
  somewhere, and that component is touched by >=12 actions however the rest is
  cut -- so the cap is unsatisfiable by ANY partition, and is therefore not
  measuring the cut. The cause is structural and general to CLIs rather than
  specific to this model: `setup_phase` and `spec_root` are read as PRECONDITIONS
  by every command (`root = spec_root`, `setup_phase >= ...`), and a heuristic
  that counts read-touches makes any component holding such a variable maximally
  coupled by construction. The metric counts commands, not coupling. This is the
  "gate comparing quantities that are not commensurable" that MF-017's
  budget-and-metric category named as the live candidate, and the same class of
  error MF-022 already corrected once for `max_distinct_states`.
- workaround_applied: NONE. `max_component_actions` was not renegotiated and
  `--allow-over-budget` was not used to make it pass. The Internal view fails the
  heuristic and is reported failing.
- recommendation: count only WRITE touches, or exclude read-only touches from an
  action's touch set, or express the budget as coupling (modularity Q) rather
  than a raw count. Separately, support the contract-environment shape the
  budgets already presuppose, so precondition variables can be modeled as an
  environment at the port rather than as component state. FILE AGAINST THE SKILL.
- status: open

### SF-014 — the coverage-audit prompt's enumeration commands return zero matches with exit 0 under ugrep

- category: profile-schema-cli
- target: prompts/coverage_audit.md — Step 2 and Step 3 enumeration command blocks
- observed_on: tla-spec-dev @ MF-023, MF-026 audit re-run
- evidence: specs/tickets/MF-023/results/coverage-audit.md §8.6
- severity: degrades-model
- root_cause: tool
- surface: the MF-026 coverage audit, i.e. the epic's completeness gate
- data_loss: yes — a silently empty sweep
- note: On a machine where `grep` is `ugrep`, the prompt's patterns return ZERO
  matches with EXIT 0. Following the prompt verbatim would have produced a clean,
  well-formatted coverage report asserting the repository performs no filesystem,
  subprocess, or network effects whatsoever -- a maximally flattering result
  produced by a silently failing enumeration. This is the same failure shape as
  MF-016's spurious 1.000 kill rate: the measurement breaks in the direction of
  looking good, and nothing in the output says so. Separately, Step 3's command
  block is still hardcoded to `scripts/ spec_double_compiler/` (32 of 240 in-scope
  files) -- the identical defect the prompt already documents fixing for Step 2.
- workaround_applied: the auditing agent detected the empty result and substituted
  working enumeration commands, checking the raw output in under
  specs/tickets/MF-023/results/sweep-raw/ so a reviewer can recount
- recommendation: pin the enumeration to a specific tool and FAIL LOUDLY on an
  empty sweep -- an enumeration that returns zero rows for "does this program
  touch the filesystem" is a broken command, not a finding. Add a self-check that
  a known-present pattern matches before trusting a zero result. Fix Step 3's
  hardcoded path list. FILE AGAINST THE SKILL.
- status: open

### SF-015 — `close ticket` selects the model file alphabetically, measuring `Core.tla` on every decomposed tree

- category: budget-and-metric
- target: scripts/spec_evolution.py:542-545 — `tla_path = sorted(model_dir.glob("*.tla"))[0]`
- observed_on: tla-spec-dev @ MF-023, close of the decomposed Core/Internal/External tree
- evidence: specs/tickets/MF-023/results/close-ticket-REFUSED.txt
- severity: blocks-migration
- root_cause: tool
- surface: `close ticket`, and therefore the MF-019 complexity ledger on every decomposed repository
- data_loss: no
- note: The selector takes the alphabetically first `*.tla`. On a decomposed tree
  that is `Core.tla`, the module that by design holds constants and vocabulary
  and NO variables and NO actions. `MC.cfg` is gone too, so the cfg falls through
  to `sorted(*.cfg)[0]` = `External.cfg`. The ledger measured Core against
  External.cfg and reported variables 9 -> 0, actions 14 -> 0, bound 699,840 -> 1
  -- a fictitious -100% complexity collapse -- then REFUSED the close under the
  anti-gaming rule that rejects a decrease while retention is degraded. The
  manifest declares `module: External`; the selector never consults it.
  COMPOUNDS SF-009: even pointed at the right file, the parser cannot resolve
  EXTENDS, so any view reports fewer variables than the model has. Between them
  the ledger CANNOT measure a decomposed model -- it can only ever report a
  decrease, on the architecture the skill mandates.
- workaround_applied: NONE. No override was attempted (there is none by design),
  `--accept-new` was not used, and no retention verdict was softened. The MF-023
  spec ticket is left OPEN and the ticket stops at PR-open rather than
  self-merging, because the owner's self-merge authorization is conditional on
  the ticket being closed and the matrix green.
- recommendation: honor the manifest's declared `module:` (and
  `internal_module:`/`core_module:`) when selecting the model to measure; refuse
  rather than guess when no declaration resolves. A ledger that silently measures
  a different module than the one the manifest names is reporting a number about
  a file nobody asked about. FILE AGAINST THE SKILL.
- status: open
