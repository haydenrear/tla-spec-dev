#!/usr/bin/env python3
"""Render one GitHub issue body per planned ticket, FROM the canonical plan.

    uv run --with pyyaml python3 \
      specs/results/scorecards/stabilize-substrate/kickoff/render_assignments.py <outdir>

Every scheduling field in the rendered assignment is read out of
`specs/desired_program_model/ticket_plan.yaml` rather than typed a second time,
because `plan-and-schedule.md` requires the assignment and the canonical entry to
match EXACTLY on ticket id, schedule revision, dependencies, blocks, wave,
promotion order/predecessor, conflict keys, goal relations, validation matrix and
evidence root -- and a hand-copied assignment is how that drifts.

Writes nothing outside <outdir>. Reads the plan on disk. Refuses rather than
guesses: an unknown goal id, a missing ticket field or an empty ticket list is a
hard error, not a default. Run with `--check` to re-render and diff against
existing bodies without writing.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import yaml

PLAN = pathlib.Path("specs/desired_program_model/ticket_plan.yaml")


def die(msg: str) -> None:
    print(f"REFUSED: {msg}", file=sys.stderr)
    raise SystemExit(2)


def load_plan() -> dict:
    if not PLAN.exists():
        die(f"{PLAN} does not exist -- run from the epic worktree root")
    plan = yaml.safe_load(PLAN.read_text())
    if not plan:
        die(f"{PLAN} parsed to nothing")
    if not plan.get("tickets"):
        die("the plan declares no tickets; an empty plan is UNDECIDED, not satisfied")
    if not plan.get("epic_goals"):
        die("the plan declares no goals and no goals_waived reason")
    return plan


def block(text: str, indent: str) -> str:
    return "\n".join(indent + line for line in str(text).strip().splitlines())


def yaml_list(items) -> str:
    return "[" + ", ".join(f'"{i}"' for i in (items or [])) + "]"


def render(plan: dict, t: dict, goals_by_id: dict) -> str:
    epic = plan["epic"]
    dp = plan["deferment_policy"]
    tid = t["id"]
    slug = t["title"].lower().replace(" ", "-")[:40].strip("-")
    is_eval = t.get("role") == "evaluation"

    goal_lines = []
    for g in t["goals"]:
        gid = g["goal"]
        if gid not in goals_by_id:
            die(f"{tid} names unknown goal {gid}")
        G = goals_by_id[gid]
        goal_lines.append(f'''  - goal: "{gid}"
    kind: "{G['kind']}"
    statement: |-
{block(G['statement'], "      ")}
    metric: |-
{block(G['metric'], "      ")}
    baseline: |-
{block(G['baseline']['value'], "      ")}
    baseline_measured_at: "{G['baseline']['measured_at']}"
    baseline_evidence: "{G['baseline']['evidence']}"
    target: |-
{block(G['target'], "      ")}
    decided_by:
      ticket: "{G['evaluation_ticket']}"
      harness: |-
{block(G['harness'], "        ")}
    evidence_root: "{G['evidence_root']}"
    contribution: "{g['contribution']}"
    expected_effect: |-
{block(g['expected_effect'], "      ")}
    local_signal: "{g['local_signal']}"''')

    ck = t["conflict_keys"]
    owns = f'\n  owns_goals: {yaml_list(t.get("owns_goals"))}' if is_eval else ""

    assignment = f'''<!-- git-epic-workflow:assignment:start -->
## Epic execution — REQUIRED

```yaml
version: 1
epic:
  id: "{epic['id']}"
  workflow: "{plan['name']}"
  branch: "{epic['branch']}"
  base_sha: "{epic['base_sha']}"
  plan_commit: "PLAN_COMMIT"
  schedule_revision: {plan['schedule_revision']}
  default_branch: "{epic['default_branch']}"
ticket:
  spec_id: "{tid}"
  feature_branch: "feature/{tid}"
  worktree: "/Users/hayde/IdeaProjects/wt-epic-stabilize-substrate-{tid}"
  pr_base: "{epic['branch']}"
  depends_on: {yaml_list(t['depends_on'])}
  blocks: {yaml_list(t['blocks'])}
  wave: {t['wave']}
  promotion_order: {t['promotion_order']}
  promotion_predecessor: {f'"{t["promotion_predecessor"]}"' if t['promotion_predecessor'] else 'null'}
  role: {t.get('role', 'implementation')}{owns}
  conflict_keys:
    production: {yaml_list(ck['production'])}
    tla: {yaml_list(ck['tla'])}
    adapters: {yaml_list(ck['adapters'])}
    test_graph: {yaml_list(ck['test_graph'])}
    workflow: {yaml_list(ck['workflow'])}
goals:
{chr(10).join(goal_lines)}
validation:
  tlc: "N/A: no TLC target exists at this tree. `run` accepts only `spec-unit-tests` and `effect-conformance` — verified. Earlier assignments declared `run tlc`; that was an owner error, and SS-01 and SS-03 correctly reported it rather than substituting something else."
  spec_unit: "python3 scripts/tla_spec_dev.py --spec-root specs run spec-unit-tests"
  repository_unit: "uv run --with pytest --with pyyaml -m pytest tests -q"
  graphs: []
  spec_graph: "N/A: this epic changes measurement instruments and the ledger path, not External.tla surfaces. State the no-op model result and its evidence rather than skipping ticket closeout."
  toolchain_spec_workflow: "REQUIRED — this repository IS tla-spec-dev"
  evidence_root: "specs/results/scorecards/stabilize-substrate/{tid}"
review:
  mode: "external"
  ticket_agent_stops_after: "pr_open"
deferment:
  mode: "{dp['mode']}"
  blocking: "{dp['blocking']}"
  budget: {dp['budget']}
  backlog: "{dp['backlog']}"
```

This issue belongs to an existing shared spec workflow. **The epic assignment
overrides ordinary instructions to branch from or target the default branch.**

- **Read `goals` before implementing.** The `expected_effect` is the result this
  change is aiming at; `{t['goals'][0]['goal']}`'s named evaluation ticket decides
  it on the integrated epic. Run `local_signal` before close, record the number
  under the evidence root, and report it against `expected_effect` — **including
  "no measurable movement"**.
- **Verify your branch point.** `wt new` branches from the **local** ref, and a
  ref is a symbolic name, not an identity. Resolve
  `origin/{epic['branch']}` to an OID once and branch from the OID.
- Start the worktree only after every `depends_on` PR is **merged into**
  `origin/{epic['branch']}`. An open or green PR is not a satisfied dependency.
- Run `python3 scripts/tla_spec_dev.py --spec-root specs open ticket {tid}`.
  **Never invoke `tla-spec-dev` from PATH** — it execs a separate installed clone.
  Never scaffold another workflow.
- Before close, wait for `promotion_predecessor`, reconcile the latest epic tip,
  and rerun the validation matrix. `close ticket` **refuses while the plan says
  `planned`** — flip your entry first.
- Mark and close **only this spec ticket**, with every evidence path. Never run
  the whole-workflow close script and never use `--accept-new`.
- **A local signal is a signal, not a gate.** A missed one is reported, never
  hidden, and never justifies weakening the REQUIRED matrix or chasing a metric
  outside this ticket's conflict keys.
- Defects outside your conflict keys are **deferred, not fixed**: append to
  `{dp['backlog']}` and keep working your slice. **Append; never rewrite,
  truncate, reorder or reset it.** An entry with no reproduction is not a
  finding, it is a hunch — do not file it. Expect a tail conflict with any
  sibling ticket and resolve it by **keeping both sets in promotion order**;
  confirm the row count only ever rises.
- **Skills are READ from this repository and NEVER edited.** Anything that must
  change in a Skill Manager home is **proposed as a diff and escalated** in your
  PR body. **All units were synced in both tiers on 2026-08-15 by owner
  decision** and are current as of that date; `spec-double-compiler` now ships at
  `436c78c`, which means the installed unit carries every charter and
  `NEXT-EPIC.md` on disk — **an open contamination channel for any agent you
  dispatch** (`#271` §7.5). Say so if you dispatch one.
- **DO NOT RUN `skill-manager home close-out`, `home sync`, `skt sync` or
  `skt publish`.** Your worktree has its own Skill Manager home
  (`<worktree>/.skill-manager`, gitignored) and **nothing you change inside it is
  in this PR**. **Change management is the epic owner's job, in one place:** the
  owner merges your PR, then merges your worktree home's changes into the project
  home, and only then removes the worktree. Your obligation is **disclosure** —
  state in the PR body whether anything inside your home changed, naming the unit
  and the change, or state plainly that nothing did. **Leave the worktree
  standing.**
- **Write scratch output to a ticket-specific path.** Two concurrent tickets
  corrupted a shared `baseline.txt`. Never hand-roll a wait loop; never kill a
  process by name alone.
- Push the sealed ticket branch and open its PR with base `{epic['branch']}` and
  `Refs #ISSUE_NUMBER`. **Stop for external review**; do not merge to the default
  branch and do not close the GitHub issue.
<!-- git-epic-workflow:assignment:end -->'''

    header = f'''# {tid} — {t['title']}

**Epic:** `{epic['id']}` on `{epic['branch']}`, base `{epic['base_sha'][:7]}`.
**Charter:** `STABILIZE-SUBSTRATE-EPIC.md` — **read it before you touch git.**
**Canonical plan:** `specs/desired_program_model/ticket_plan.yaml` (this issue
mirrors it; the plan is canonical). **Prior record:** `NEXT-EPIC.md`
§0-AAAAAAAAAA. **Owner's starter:** issue #271.

## Summary

{t['objective'].strip()}

## References — your discovery starting point

- `STABILIZE-SUBSTRATE-EPIC.md` — §0 (three figures in the work order that
  already moved), §1 (the tree is the finish condition), §6 (what the
  static-gates doctrine permits), §7 (doctrine), §8 (operational rules paid for)
- `specs/desired_program_model/ticket_plan.yaml` — your canonical entry `{tid}`
  and `planning_rules`
- `specs/deferred_findings.yaml` — **297 rows**, the cumulative ledger, live at
  this path for this epic
- `specs/results/scorecards/stabilize-substrate/` — the goal baselines, each with
  its sealed raw command output beside it
- `specs/results/scorecards/cut-the-apparatus/CA-10-absent-input/RESULT.md` — the
  48-instance sweep, with the seven sub-shapes in §3.2
- `NEXT-EPIC.md` §0-AAAAAAAAAA §8 — *what the next owner must not repeat*

## Discovery notes

**Verify every claim in this issue before acting on it, INCLUDING THE
CORRECTIONS.** Issue #271 handed this epic five figures and five moved. **Then
the owner's own corrections were themselves corrected, twice, by tickets and
reviewers — and one of those corrections was wrong in the opposite direction.**
The chain is the point:

- **`scope` 102 → 82.** The owner attributed the −20 as *"20 REFUTED, all from
  the ledger, plus 3 UNREACHABLE from `NEXT-EPIC.md`"* — **read off two marginal
  totals that were never cross-tabulated.** `SS-01` then argued the ledger could
  not account for it and that #271 was *"wrong twice"*. The cross-tab settles it:
  **17 REFUTED + 3 UNREACHABLE from the ledger, 3 REFUTED from `NEXT-EPIC.md`.**
  The ledger accounts for the −20 exactly, and **#271's "17 REFUTED figures
  currently unswept" was right all along.** `scope` is **103** at `50046b2` after
  `SS-01` added `DEFAULT_SWEEP`, superseding the sealed baseline of 82.
- **`SS-00-DF-01`'s filed mechanism was wrong.** The owner's probe printed mtimes
  with `:.0f`, collapsing four distinct seconds into one, and *"all 85 candidates
  tie, so the largest file wins"* became a filed finding. **There are 85 distinct
  mtimes.** The defect was real and is repaired; the stated cause was an artifact
  of the diagnostic. `SS-01-DF-02`.
- **`0 of 18` → `0 of 20` → `0 of 24` → `0 of 17`.** The charter's correction was
  right at `436c78c` and stale at the tree you branch from; the census then
  changed again when `SS-03` repaired its recogniser. Read
  `GOAL-judged-goals-compliant`'s baseline for the current figure and its tree.
- **The four skips did NOT unskip by repointing**, as the plan and the charter
  both claimed. Repointing alone converts them to four reds on
  `status=planned`. They are gone at `50046b2` for a different reason.

**`scope` cannot do this checking for you:** it returns **zero** counted figures
on charters, plans, baselines and price tables (`CA-08-DF-01`), and it records
nothing about the root it swept (`SS-01-DF-03`). **Until `SS-04` lands, you are
the recogniser — and so far the record shows every party in this epic getting a
figure wrong at least once, including both reviewers' subjects and the owner
three times.**

## Regression & close-out

Run the full REQUIRED matrix above. Report **failed, passed, skipped, xfailed and
collection as numbers THAT SUM**, at the base and at your tip, with **every
movement attributed** and its numerator/denominator direction named. Test command:
`uv run --with pytest --with pyyaml -m pytest tests -q` — **without
`--with pyyaml`, 12 tests go phantom red.**

**Compare against the tree you actually branch from, not against the charter.**
Wave 1 moved it, and four artifacts of this epic's own machinery are now known.
**Do not rediscover them; do not attribute them to your own slice.**

1. **There are FIVE buckets, not four.** `SS-01` added an `xfail(strict=True)`
   pinning `SS-01-DF-01`, so `failed + passed + skipped + xfailed = collection`.
   At `50046b2`, verified independently by the owner in a fresh worktree:
   **8 / 1509 / 0 / 1 / 1518**. A four-number report silently stops summing.
2. **`open ticket` inflates collection by +4 and `close ticket` removes it
   again**, by widening parametrized `test_spec_yaml_valid` over the scaffolded
   `specs/tickets/<id>/` tree. **Every ticket on this epic sees this.** Say which
   side of the close your figure was taken on.
3. **`close ticket` seals the history entry and deletes the workspace in ONE
   operation, so the sealed entry can never describe the tree it produces.**
   `SS-01`'s sealed summary says `8/1508/0/1516` and its live `RESULT.md` says
   `8/1504/0/1512`; `R-H4` forbids editing the entry. **Expect the divergence,
   disclose it in your live `RESULT.md` and PR body, and say which is
   authoritative** — do not leave `SS-08` two numbers and no explanation.
4. **A figure is a joint property of the artifact AND the tree it was measured
   in.** `SS-01-DF-03`: the same ledger bytes score `21/18/3` under a bare
   `--root` and `20/17/3` inside the repository, and `scope`'s output records
   nothing about which root it swept. **Name the tree on every figure you
   publish.** The owner has already been caught by this once and so has `SS-01`.

Close **only** spec ticket `{tid}` with evidence, push, and open a PR with base
`{epic['branch']}`. Report goal contribution in a `## Goal contribution` section.

'''

    if is_eval:
        header += '''**This is a `role: evaluation` ticket.** Run each owned harness from a fresh
start on the reconciled epic tip, after every contributing ticket has merged, and
write results to each goal's `evidence_root`. Report **baseline → measured →
target and a verdict per CLAUSE**, never one token for a multi-clause goal.
**Never edit a target to match a result and never re-run selectively until a
number passes — report the run that happened.** File regressions as deferred
findings; **fix nothing**.

'''

    return header + assignment + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    plan = load_plan()
    goals_by_id = {g["id"]: g for g in plan["epic_goals"]}
    out = pathlib.Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)

    drift = 0
    for t in plan["tickets"]:
        for field in ("id", "title", "objective", "depends_on", "blocks", "wave",
                      "promotion_order", "conflict_keys", "goals"):
            if field not in t:
                die(f"ticket {t.get('id', '?')} has no {field}")
        body = render(plan, t, goals_by_id)
        p = out / f"{t['id']}.md"
        if a.check:
            if not p.exists():
                print(f"MISSING {p}")
                drift += 1
            elif p.read_text() != body:
                print(f"DRIFTED {p}")
                drift += 1
        else:
            p.write_text(body)
            print(f"wrote {p}  ({len(body)} bytes)")

    if a.check:
        print(f"{drift} rendered bodies differ from the plan")
        return 1 if drift else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
