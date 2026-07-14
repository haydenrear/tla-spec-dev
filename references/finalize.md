# Finalize an epic

Finalize only after the user asks to resume/finalize and all scheduled ticket
agents have returned PRs. Work from a clean worktree at the remote epic tip.

## 1. Audit integration

Fetch remote state and verify, for every ticket in
`specs/desired_program_model/ticket_plan.yaml`:

- the mapped GitHub issue and ticket PR exist;
- the ticket PR is merged into `origin/epic/<slug>`;
- merge order respects `depends_on` and `promotion_order`;
- plan status is closed/done;
- exactly one append-only ticket history entry exists;
- the entry records validation evidence;
- no `specs/tickets/<id>` workspace remains.

Also confirm there are no open ticket PRs targeting the epic branch and no
uncommitted changes. An open/green PR or locally closed branch is not integrated.

If the default branch advanced during the epic, integrate it before final
validation. A semantic conflict becomes an explicit reconciliation ticket that
uses the same ticket close path; do not hand-edit accepted state on the epic
branch.

## 2. Validate the integrated epic

Run the union of every ticket matrix plus any epic-level regression graph. Do
not reuse branch-local reports as proof of the integrated state.

At minimum:

1. Run TLC for the integrated Internal and External finite models.
2. Run project-current spec-unit and adapter conformance tests:

   ```bash
   tla-spec-dev --spec-root specs run spec-unit-tests --scope project
   ```

3. Run the repository unit suites named in the plan.
4. Discover and run every affected Test Graph graph from a fresh start.
5. Run the repository's assigned spec-conformance and full-epic graphs. Run
   `specWorkflow` only when validating the tla-spec-dev repository itself.
6. Inspect `summary.json`, `report.md`, node logs, and every evidence envelope.

Confirm project `specs/current` semantically equals the target
`specs/desired_program_model`, including TLA/CFG, YAML, Python adapters, TOML
bindings, JSON artifacts, and graph changes. Do not rely on the cleanup script
as the only comparison.

## 3. Pass the external semantic-review gate

Push the fully integrated, still-open workflow state and open or update a draft
epic PR against the default branch. Include the integrated validation evidence
and request external semantic review while `current` and
`desired_program_model` still exist and can accept review changes normally.

Do not write the irreversible closed snapshot until that review is approved.
If review changes behavior, add/reopen a planned ticket, run its normal
ticket-close path, and repeat integrated validation. Immediately before close,
record the current default-branch SHA. If it differs from the reviewed base,
integrate it, create a reconciliation ticket for semantic conflicts, revalidate,
and refresh approval.

## 4. Promote and close the shared workflow

Promote the converged desired/current semantic model into
`specs/program_model`, regenerate accepted artifacts, and validate the accepted
program model. Then run the spec-double-compiler close script first as a dry
run and then for real, without `--accept-new`:

```bash
python <spec-double-compiler-skill>/scripts/close_tickets.py \
  --repo-root . --dry-run \
  --summary "<epic summary>" \
  --result <integrated-evidence-path>

python <spec-double-compiler-skill>/scripts/close_tickets.py \
  --repo-root . \
  --summary "<epic summary>" \
  --result <integrated-evidence-path>
```

The cleanup script proves every ticket is closed and compares TLA, CFG, and
YAML/YML model files. It does not prove Python adapters, TOML bindings, JSON
artifacts, or Test Graph behavior; the integrated commands and evidence audit
above are the proof for those surfaces. The script writes the workflow
`closed-snapshot` and removes temporary current/desired directories. Inspect the
diff and commit the promoted model, generated artifacts, close snapshot, and
integrated evidence together.

## 5. Update the epic PR

Push the final close commit and update the already-reviewed draft epic PR. Mark
it ready only after confirming its base SHA still matches the reviewed default
tip and the close commit changed workflow artifacts only. Its body includes:

- epic scope and the accepted program-model change;
- every child issue and merged ticket PR;
- the dependency/promotion order actually integrated;
- full validation commands, run IDs, summaries, and report paths;
- the workflow closed-snapshot path;
- issue-closing references for the child issues.

Do not bypass branch protection or merge the epic PR unless the user explicitly
authorizes that final action. A semantic change requested after close requires a
successor workflow; never rewrite the closed snapshot. Keep the epic
worktree/branch until the default-branch merge is verified; clean them up only
afterward.
