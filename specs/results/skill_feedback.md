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
