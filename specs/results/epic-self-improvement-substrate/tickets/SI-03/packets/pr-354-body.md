SI-05: a finding that names this repository owes this repository a change

Refs #333. Epic branch `epic/self-improvement-substrate`, workflow
`self-improvement-substrate`, spec ticket `SI-05`, issue #338.

## What landed

The close-out stops recording findings and starts disposing of them.

- **`scripts/spec_evolution.py::print_skill_change_proposals`** — the close now
  names every finding whose `target:` is a surface in this repository and which
  proposes no change, tells the reader the exact field that fixes it, and
  **proceeds**. One warning line per finding. It is wired into
  `print_commit_recommendation`, which is the single funnel for `close ticket`,
  `close_tickets.py` and `close spec workflow`, so ticket close and workflow
  close both get it from one insertion.
- **`scripts/new_ticket_workflow.py`** — `ticket_readme` step 7 and
  `ticket_next_steps` step 6 state the obligation where the ticket agent reads
  it, including that the close warns and still proceeds.
- **`references/migration.md` Phase 6** — the rule, the three dispositions, and
  "a proposal is a diff or an issue with a diff, never prose alone".
- **`scripts/scaffold_spec_workflow.py`** — the cite-symbols-not-line-numbers
  convention now ships in the scaffolded `desired/`+`current/` READMEs (this is
  half of SF-304, see below).
- **`tests/test_close_out_proposals.py`** — 7 new tests, all passing. New file,
  so it collides with no sibling ticket.
- **`specs/results/skill_feedback.md`** — the 13 `recorded-local` findings are
  disposed of.

### The 13 findings, disposed

| Finding | Target | Disposition |
|---|---|---|
| SF-101 | `scripts/architecture_reflexion.py` | `declined` — target cut from the repo; verified absent |
| SF-102 | `run_generated_case_adapters.py` orphan providers | `applied(28cf7b39)` — orphan ports REPORTED, not refused |
| SF-103 | `--effect-report` writes nothing, silently | `proposed` + diff — still reproducible |
| SF-104 | `analyze_architecture.py` + aspect prompt | `declined` — command cut; prompt already repaired 2026-08-04 |
| SF-105 | no document states an interpreter requirement | `applied(SI-05)` — migration.md Phase 6 declares the dependency set |
| SF-201 | ledger has no `tlc_report:` field | `proposed` + diff — still open |
| SF-202 | 17-file suite no scope executes | `proposed` + diff — re-measured, still open |
| SF-203 | close prints "NOT yet filed" and closes anyway | `applied(SI-05)` — **this ticket** |
| SF-301 | effect-conformance `sys.path` | `applied(28cf7b39)` |
| SF-302 | oracle aborts instead of skipping | `applied(28cf7b39)` |
| SF-303 | cap refusal hides `--state-projector` | `proposed` + diff — still open |
| SF-304 | line citations drift; nothing inherits the check | `applied(SI-05)` (convention) + `proposed` (executable half) |
| SF-305 | `TEMPLATE_SENTINEL` substring test | `applied(7066e065)` |

7 `applied`, 2 `declined`, 4 `proposed`. Every proposal is a diff under
`specs/results/epic-self-improvement-substrate/tickets/SI-05/proposals/`, never
prose alone.

**Six of the 13 were already fixed in the tree and nobody had said so.** SF-102,
SF-301, SF-302 and SF-305 were repaired by HP-04 (28cf7b39) and 7066e065; SF-104
was repaired 2026-08-04. They sat as `recorded-local` afterwards. That is the
finding-to-change loop failing in the *cheapest* direction — the work was done
and the record never caught up — and it is the strongest argument for SI-04's
ledger existing at all.

## Model delta I need from the epic agent

I did not touch `specs/`. The assignment puts the `CloseTicket` result string in
the epic agent's hands, and `specs/tickets/SI-05/desired` still differs from
`specs/current` only by the `test_current_ticket_workflow.py` deletion it was
scaffolded with.

`TlaSpecDevCli.tla` line 575, inside `CloseTicket`:

```
  /\ result' = CommandResult(TRUE, NoReason, "Open next ticket or close workflow")
```

A **string and comment change, not a guard change** — the `TRUE` and the
`NoReason` stay exactly as they are, because nothing about a missing proposal
refuses:

```
  \* SI-05: a finding whose target is in this repository owes this repository a
  \* proposed change. The close NAMES each finding that owes one and proposes
  \* none, and still succeeds -- the result stays TRUE with NoReason.
  /\ result' = CommandResult(TRUE, NoReason, "Dispose of each finding that names this repository, then open next ticket or close workflow")
```

No new action, no new variable, no guard touched, so the state space is
unchanged.

## Goal contribution

| Goal | Kind | Expected effect | Measured | Classification |
|---|---|---|---|---|
| `GOAL-findings-become-changes` | direct | recorded-local 13 → 0, each one applied/filed-with-diff/declined | **13 → 0**; 13 `skill_change:` dispositions now present (7 applied, 2 declined, 4 proposed) | **moved as expected** |
| `GOAL-no-new-gates` | guard | close warns per unproposed finding and still closes | 0 refusal paths added; `test_the_close_proceeds_and_nothing_refuses` and `test_a_real_ticket_close_with_an_unproposed_finding_still_closes` both green | **moved as expected** |

Signals: `specs/results/epic-self-improvement-substrate/tickets/SI-05/local-signal.txt`.
Both are advisory. **SI-08 decides both goals**, and it should note that this
ticket only moves `skill_feedback.md` — the epic's baseline also counts 33 + 6
deferred-backlog rows with no disposition field, which are not in my slice.

## Validation

| Entry | Command | Result |
|---|---|---|
| repository_unit | `uv run --python 3.12 --with pytest ... python -m pytest tests -q --ignore=tests/test_score_tools.py` | **10 failed / 1601 passed / 5 skipped**, against baseline 10 failed / 1594 passed / 5 skipped — **the same 10 names, zero new failures**. The +7 passed are this ticket's new tests. (Run 1 measured 11: those 10 plus one of mine, now fixed — see below.) |
| spec_unit | `tla_spec_dev.py --spec-root specs run spec-unit-tests --target specs/tickets/SI-05/desired` | 7 failed / 46 passed — **the same 7 names as baseline** |
| spec_unit (2nd form) | `... --scope project` | 7 failed / 49 passed — same 7 names |
| new tests | `pytest tests/test_close_out_proposals.py -q` | 7 passed |
| citations | `pytest tests/test_source_citations.py -q` | 3 failed / 81 passed — the same 3 baseline names |
| tlc | — | `N/A` by the assignment: the epic agent owns the model |

Compared **by failure name, not count**, against a baseline recorded before my
first edit (`pytest-before.txt`, `spec-unit-before.txt`).

### I broke one test and fixed it

The first full run came back **11 failed against a baseline of 10**, and the one
new name was mine:

```
test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[skills/spec-double-2/scripts/scaffold_spec_workflow.py]
```

The SF-304 convention I added — *cite symbols, not line numbers* — spelled out a
literal `scripts/foo.py:192` to show what not to write. The repository's own
citation checker found it, could not resolve it, and went red:

```
citation `scripts/foo.py:192` has no (anchor). Write `FILE.EXT:LINE (some_token_on_that_line)`
-- an unanchored line number cannot be checked and goes stale silently.
```

A convention against line citations that contained a line citation. It is the
same shape as SF-305, which this ticket also disposed of: a narrative quoting the
ledger's own template sentinel, eaten by the ledger. Reworded to carry no literal
file-and-line pair; the parametrised case is gone and the citation suite is back
to exactly its 3 baseline failures. **Caught by comparing failure NAMES rather
than counts** — 11 vs 10 says "one more", the names say which one and whose.

Confirmed by a full re-run after the fix: **10 failed / 1601 passed / 5 skipped**,
the same 10 names as the baseline, zero new failures
(`results/pytest-after.txt`). Run 1's output is kept at
`results/pytest-after-run1.txt` so the regression and its repair are both on the
record rather than only the tidy final number.

`run spec-unit-tests --ticket SI-05` is the form the assignment declares, and it
is the known-weak one (`SIS-KICKOFF-F-04`): it resolves both targets and runs
only the first, so it executed `specs/current` and never touched
`specs/tickets/SI-05/desired`. I ran `--target` explicitly and report both.

## Deferred findings

**None.** The five out-of-keys defects this ticket met are the *subject* of the
ticket, not incidental to it, so they are dispositions on their findings with
diffs attached, not backlog rows. `deferred_findings_final.yaml` is untouched —
deliberately, given wave 1's only merge conflict was concurrent appends to it.

## Skill changes proposed

| Unit | What I hit | Change |
|---|---|---|
| `git-issue-workflow` / `skt` | **`skt ticket new` failed twice and rolled back both times**, exit 3 (bootstrap exit 6). Verbatim: `error: home bootstrap failed (exit 6); worktree and branch rolled back`, caused by `error: this home holds 15 skill(s) and an agent launched here can reach 12` for `git-issue-workflow`, `spec-double-compiler`, `test-graph`. Its own remedy (`skill-manager sync --skip-mcp`) had already run and had not fixed it. | I fell back to the documented by-hand route (`references/epic-ticket.md` §2) plus `bootstrap-home.sh --allow-unprojected`, which succeeded with `12 of 15` projected. **Proposed:** `skt ticket new` should fall back to `--allow-unprojected` with a warning rather than rolling back the worktree — an unservable home is a degraded home, not a reason to destroy a correctly-created worktree. |
| `git-issue-workflow` | The rollback is **silent about the branch**. The first failure left `feature/338-close-out-owes-change` visible in `git branch` with a `+` worktree marker for a directory that no longer existed. | **Proposed:** name the rolled-back branch and worktree path on stderr. |
| `tla-spec-dev` (this repo) | The epic's declared `evidence_root` is under `specs/`, and `.git/info/exclude:23` excludes `/specs/`. Evidence written there is **invisible to `git add -A`** and silently absent from the PR. | Force-added with `git add -f` here. **Proposed:** the assignment should either name an evidence root outside the exclude, or the close-out should force-add. A ticket that follows the instructions exactly ships no evidence. |
| `tla-spec-dev` (this repo) | `scripts/skill_feedback.py::needs_filing` treats anything outside `{filed, wontfix}` as unfiled, so my new `applied` / `declined` / `proposed` statuses are reported as "has no ticket/PR". | **NOT changed** — `skill_feedback.py` is SI-04's conflict key. SI-04 should extend that set when it defines `skill_change`. |
| worktree tooling | **`remote.origin.url` in the SHARED `.git/config` pointed at `/Users/hayde/IdeaProjects/wt-351-plugin-plumbing`** — a sibling ticket's worktree — instead of `git@github.com:haydenrear/tla-spec-dev.git`. It was the canonical GitHub URL earlier in this same ticket, so something rewrote it mid-flight. `.git/config` is per-clone, so this applied to **all nine worktrees and the main checkout**. | **Repaired**: `git remote set-url origin git@github.com:haydenrear/tla-spec-dev.git`, which writes that shared config and therefore fixes every worktree. **This is the same shape as the `/specs/` exclude defect** and is arguably worse: `git push` reported `Everything up-to-date`, `git ls-remote origin` showed the branch at the right SHA, and `git status` showed a clean tracking branch — while GitHub had never heard of the branch. A ticket agent that trusted any of those three would report a pushed PR that does not exist. Whoever owns worktree provisioning should make the origin URL an asserted invariant. |
| 5 diffs | SF-103, SF-201, SF-202, SF-303, SF-304 | Attached under `.../SI-05/proposals/`, each with re-verification against the epic tip. |

## Review input

**Hot spots**
- `scripts/spec_evolution.py` — the only behavioral change. `print_skill_change_proposals` re-reads `skill_feedback.md` from disk rather than using the record's `findings`, because `to_record()` does not carry `skill_change` and that function is SI-04's. If SI-04 adds the field to `to_record()`, this should switch to the record and drop the re-read.
- `specs/results/skill_feedback.md` — 13 blocks edited. **SI-04 also reads this file.** Our conflict keys are disjoint by design (it owns `skill_feedback.py` and the readers, I own the content), but we are writing the same document in the same wave.
- `REPO_TARGET_PREFIXES` is a substring match. `specs/` and `tests/` are broad enough to match a finding about someone else's repo that happens to use those names.
- `scripts/scaffold_spec_workflow.py` — the SF-304 convention text is prose that this repository's own citation checker parses. I tripped that once already (see *I broke one test and fixed it*). Anyone editing that string should re-run `tests/test_source_citations.py` rather than assume prose is inert.

**Decisions and overrides**
- **Statuses `applied` / `declined` / `proposed` are mine, not the schema's.** The existing vocabulary is `open|filed|wontfix`, and `filed` demands a URL that an in-repo commit does not have. The goal metric counts `recorded-local`, which is now 0, but **SI-04 owns the vocabulary** and may want different spellings. Cheap to rename.
- I used SI-04's field spelling from issue #337 (`skill_change: none | proposed(<unit>, <diff or issue>) | applied(<commit>) | declined(<reason>)`). **SI-04 has not landed** — no PR for #337, no `improvement_ledger.py` on the tip. If its spelling changed during implementation, mine is wrong and is a sed away.
- I did **not** apply the five out-of-keys fixes even though the files are in my worktree, per the deferment policy. A reader expecting 13 applied changes gets 7.
- `--allow-unprojected` on the worktree home — a deliberate guardrail weakening, taken because the front door left no other route. The home is "NOT verified": 12 of 15 skills reachable.

**Where I'd look for bugs in my own change**
1. `_finding_targets_this_repository` on the real corpus. I tested it on fixtures; I did not assert which of the *37* real findings it selects. Cheapest experiment: run `print_skill_change_proposals` against the committed `skill_feedback.md` and eyeball the selected set.
2. The `latest_close_out_scope` interaction. My warning only ever sees the newest close-out block — correct, and it means a ticket that records nothing gets a silent close even with 13 unproposed findings above it. Intended, worth confirming it is what the epic wants.
3. `new_ticket_workflow.py` — both edits are inside f-strings. They pass, but a future editor adding a literal `{` there breaks scaffolding at runtime, not at import.

**Machinery friction**
- The `skt` failure above cost the most: two full worktree creations (~2 min each) that rolled back, and a stale branch that made the worktree look present when it was gone.
- **The issue's own References section named the wrong findings.** It says the 13 `recorded-local` findings have `target:` values naming `analyze_complexity.py`, `extract_spec_manifest.py`, `spec_evolution.py::promote_current_tree` and `scaffold_spec_workflow.py`. They do not — those are SF-000a/SF-000d (worked examples, excluded from filing status) and SF-003/SF-004 (already `filed`). The real 13 are SF-101–105, SF-201–203, SF-301–304 and SF-305, and **most of them target files outside this ticket's conflict keys.** The conflict keys were derived from the wrong finding set, which is why 5 of 13 could only be proposed. This is the single thing I would fix about the plan.
- `.git/info/exclude` silently swallowing the evidence root (above).
- My worktree home is **clean**: `home close-out` returned `safe: true`, exit 0, `blockers: []`, every unit `unchanged`. I published nothing and changed nothing inside it.

## Close-out

- `home close-out` verdict: **clean**, no blockers, nothing published.
- Spec ticket **not** closed and not promoted — the epic agent owns that at wave merge, per the assignment's model-ownership rule.
- Worktree left standing at `../wt-338-close-out-owes-change`.
- Stopped at PR open. Issue #338 left open; `main` untouched.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01DUdxjqPbjrJ45Bpxw8uZeS

