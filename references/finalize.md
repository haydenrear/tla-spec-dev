# Finalize an epic

Finalize only after the user asks to resume/finalize, all delivered tickets have
returned PRs, and all retired tickets have canonical receipts. Work from a
clean worktree at the remote epic tip.

## 1. Audit integration

Fetch remote state and verify, for every ticket in
`specs/desired_program_model/ticket_plan.yaml`:

- its ID and original plan ordinal are unchanged;
- when delivered, the mapped GitHub issue and ticket PR exist, the PR is merged
  into `origin/epic/<slug>`, merge order respects `depends_on` and
  `promotion_order`, plan status is closed/done, and exactly one append-only
  ticket close-history entry records validation evidence;
- when retired, plan status is exactly `retired`, its retirement schedule
  revision is positive and no newer than the current root revision, its
  canonical `ticket-retirement` receipt exists at the ordinal/ID-derived path,
  and the receipt contains the complete decision-time `retirement` mapping
  exactly — including field set, values, and affected-goal order;
- no undelivered non-retired dependency, reverse-block edge, promotion
  predecessor, or active evaluation ticket refers to a retired ticket;
- delivered tickets may retain sealed historical edges to later-retired IDs;
  those edges are evidence of the old schedule, not active readiness links;
- no `specs/tickets/<id>` workspace remains (an archived retired workspace is
  explicitly unaccepted, never promoted);
- every delivered evaluation ticket merged **after** all delivered contributors
  to the goals it owns, so its measurement describes the integrated epic.

Audit delivery histories and retirement receipts as two different ledgers. A
retirement manifest must say both `kind: ticket-retirement` and
`entry_kind: ticket-retirement`,
`semantic_promotion.performed: false`, and `validation.claimed: false`; it has no
accepted model snapshots, result claim, or complexity ledger. A merged PR or
ordinary close history does not excuse a missing retirement receipt. Conversely,
a retirement receipt proves only that the owner removed scope; never count it
as a delivered PR or passed validation.

Within an epic, the receipt path is always rooted at repository-relative
`specs/.history`; lower-level custom history roots supported by `tla-spec-dev`
are outside this workflow's contract.

Also confirm there are no open ticket PRs targeting the epic branch and no
uncommitted changes. An open/green PR or locally closed branch is not integrated.

## 1a. Drain the deferred-findings backlog

Read `specs/desired_program_model/deferred_findings.yaml`. No entry may remain
`pending` at close. Present every pending finding to the user and settle each
one as:

- **`ticketed`** — worth fixing inside this epic. Add the ticket to the plan,
  revalidate the schedule, bump `schedule_revision`, dispatch it, and wait for
  its PR to merge into the epic branch before finalizing. Finalization restarts
  from step 1.
- **`wontfix`** — record the reason in the entry.
- **carried out of the epic** — file a GitHub issue on the default branch, link
  it from the entry, and list it in the epic PR body.

Batching is a scheduling decision, not a way to lose defects: an epic must not
close with an unexplained finding. Do not fix a deferred finding by hand on the
epic branch; deferred work re-enters through the normal ticket close path.

If the default branch advanced during the epic, integrate it before final
validation. A semantic conflict becomes an explicit reconciliation ticket that
uses the same ticket close path; do not hand-edit accepted state on the epic
branch.

## 1b. Audit every ticket worktree's Skill Manager home

Ticket agents stop at `pr_open` and **leave their worktrees standing** — that is
the review model working as designed. It also means you are the one who will
delete them, and each one holds a `<worktree>/.skill-manager`: a real copy of the
project home, gitignored, so nothing inside it is in the ticket PR, the epic
branch, or the epic PR you are about to open. `git worktree remove` deletes it
without asking and succeeds exactly as quietly whether it held a week of skill
edits or nothing.

Step 1's audit proves the *repository* state is integrated. This proves the *unit*
state is. Do it now, while the tickets' authors are still reachable — not in §5
when you are cleaning up.

```bash
git -C <repo-root> worktree list --porcelain | awk '/^worktree /{print $2}'

# per worktree, including ../wt-epic-<slug>
skill-manager home close-out --home <worktree>/.skill-manager \
                             --into <repo-root>/.skill-manager --json
```

`--into` is the project home every one of them was cloned from. Reading the
verdict:

- **`safe: true`** — record it. A ticket PR body that already states a clean
  verdict (see `git-issue-workflow`'s `references/epic-ticket.md`) is corroborating
  evidence, not a substitute: re-run the gate, because the worktree may have been
  used since.
- **`blockers[]`** — each entry names the unit, its status, and the literal remedy.
  Do not clear them yourself by guessing which of the two remedies applies:

  ```bash
  # up a tier: survives the teardown, stays on this machine
  skill-manager home sync --from <worktree>/.skill-manager \
                          --to <repo-root>/.skill-manager --merge

  # to the unit's own git repo: the only route that reaches another project
  skill-manager unit publish <unit> --ticket <ticket>
  ```

  A skill improvement made during a ticket is `unit publish` work and belongs to
  that ticket's author, exactly like a deferred finding belongs to the backlog.
  Return the worktree to them, or settle it with the user; a blocker cleared by
  the wrong remedy is an improvement that reaches the project home and nowhere
  else, forever.

An epic must not close with an unexplained blocker, for the same reason §1a will
not let it close with a pending finding.

You can audit every worktree in any order, including concurrently: `close-out`
**writes nothing**, so there is nothing for two of them to corrupt and no
exclusion needed. What is serialized is the *remedy* — the `home sync` calls that
follow — because several worktrees reconciling into one project home do write it.
And serialization is not merging: when two worktrees have edited the same unit,
the second sync reports that unit `held-back` (or `conflicted` under `--merge`)
rather than overwriting the first. That is a result to read, not a step that
succeeded. `held-back` is a `home sync` status; `close-out` never reports it.

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

## 2a. Decide the epic goals

Read `epic_goals` from `specs/desired_program_model/ticket_plan.yaml` and settle
every goal before the review gate. A goal is decided by running its `harness` on
the integrated epic tip, not by trusting a ticket-branch number.

- Reuse the owning evaluation ticket's run only when it ran on a tip identical
  to the current integrated one; otherwise re-run the harness here.
- Compare against the recorded baseline, not against intuition. A baseline that
  was never measured makes the goal `unmeasured` — say so; do not backfill it
  from the post-epic branch and call it a comparison.
- Store results under each goal's `evidence_root` and cite them in the epic PR.

Report every goal, and every clause of a goal whose target has more than one, as
its own row (`—` in the Clause column when there is only one):

| Goal | Clause | Kind | Baseline | Measured | Target | Verdict |
| --- | --- | --- | --- | --- | --- | --- |

Verdicts are `met`, `missed`, or `unmeasured` with a reason. **A goal verdict is
not always one word**: a multi-clause target can settle as met on one clause and
missed on another, and one token per goal forces a choice that will fall the
flattering way (`references/goals-and-evaluation.md`). A missed goal is a
decision for the user, presented with the measured shortfall and the options:
add a ticket inside this epic (finalization restarts from step 1), accept the
shortfall with a recorded reason, or carry it out of the epic as a new issue.
Never edit a target to match the measurement, and never close an epic with a
silently unmeasured goal. A regression a goal harness uncovers is a finding: it
enters the backlog and the normal ticket path, not a hand fix on the epic branch.

For a goal named in a verified retirement receipt, do not fabricate a harness
result. Report the explicit disposition instead:

- `accepted_missed` → `missed (accepted via retirement)` plus reason and receipt;
- `accepted_unmeasured` → `unmeasured (accepted via retirement)` plus reason and
  receipt;
- `carried` → `carried` plus successor issue, workflow, reason, and receipt.

Every retired ticket affecting the same goal must agree. These dispositions are
the user's decision record, not evidence that the target was met.

## 3. Pass the external semantic-review gate

Push the fully integrated, still-open workflow state and open or update a draft
epic PR against the default branch. Include the integrated validation evidence
and request external semantic review while `current` and
`desired_program_model` still exist and can accept review changes normally.

Do not write the irreversible closed snapshot until that review is approved.
The review must include every schedule-revision amendment and retirement
receipt, not only delivered code. If review changes behavior, add/reopen a
planned ticket, run its normal ticket-close path, and repeat integrated
validation. Immediately before close, record the current default-branch SHA.
If it differs from the reviewed base, integrate it, create a reconciliation
ticket for semantic conflicts, revalidate, and refresh approval.

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

The cleanup script proves every delivered ticket has its accepted close history
and every retired ticket has the exact canonical no-claim receipt, then compares
TLA, CFG, and YAML/YML model files. Direct statuses such as `carried`,
`superseded`, or `abandoned` do not satisfy it; those are
`retirement.resolution` values under `status: retired`. The script does not prove
Python adapters, TOML bindings, JSON artifacts, or Test Graph behavior; the
integrated commands and evidence audit above are the proof for those surfaces.
The script writes the workflow
`closed-snapshot` and removes temporary current/desired directories. Inspect the
diff and commit the promoted model, generated artifacts, close snapshot, and
integrated evidence together.

## 5. Update the epic PR

Push the final close commit and update the already-reviewed draft epic PR. Mark
it ready only after confirming its base SHA still matches the reviewed default
tip and the close commit changed workflow artifacts only. Its body includes:

- epic scope and the accepted program-model change;
- a delivered-work table with every child issue, merged ticket PR, and
  close-history path;
- a separate retired-scope table with original ordinal/ID, resolution, reason,
  decision identity/time, receipt, affected-goal disposition, and successor;
- the dependency/promotion order actually integrated;
- full validation commands, run IDs, summaries, and report paths;
- the goal table from step 2a — baseline, measured, target, and verdict per
  goal, with the user's recorded acceptance for any missed goal;
- the workflow closed-snapshot path;
- the deferred-findings disposition: tickets opened, `wontfix` reasons, and
  issues carried to the default branch;
- issue-closing references for delivered child issues and explicit not-planned
  or carried dispositions for retired child issues.

Do not bypass branch protection or merge the epic PR unless the user explicitly
authorizes that final action. A semantic change requested after close requires a
successor workflow; never rewrite the closed snapshot. Keep the epic
worktree/branch until the default-branch merge is verified; clean them up only
afterward.

### Teardown: the gate runs before every removal

When you do clean up, each worktree removal is the irreversible step for its home,
so re-run §1b's gate immediately before it rather than trusting the earlier pass —
a worktree can be used again between the audit and the teardown.

```bash
# One command, every repo shape, and for a declared epic/ticket worktree too:
# it runs the gate and, only on a clean verdict, removes the worktree
# (refusing with exit 4 otherwise). It resolves <ticket> by searching where
# ticket worktrees live, so the declared ../wt-<issue>-<slug> path is found.
skt ticket close <ticket>

# Where skt is not installed, the same door by its resolved path:
WT="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/git-issue-workflow/scripts/wt"
"$WT" close <ticket>

# The two steps it wraps, if you need a flag it does not forward. Keep the `&&`:
# on separate lines the removal runs whatever the gate returned, which is the
# exact loss the gate exists to prevent.
skill-manager home close-out --home <worktree>/.skill-manager \
                             --into <repo-root>/.skill-manager \
  && git -C <repo-root> worktree remove <worktree>
```

`wt close --force` (which forwards to `close-change.sh --force`) still runs the
gate and still prints every blocker; it
only declines to stop, and it states that the work is being discarded. It exists so
a deliberate discard is named and loud instead of an improvised `rm -rf` that skips
this check and every other one. `skill-manager home close-out` itself has no
`--force`: the CLI owns the verdict, the script owns whether to obey it. Do not use
it to finish an epic faster — a blocker at this point is an improvement somebody
made and nobody published.
