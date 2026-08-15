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
  tlc: "python3 scripts/tla_spec_dev.py --spec-root specs run tlc"
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
- **Verify your branch point.** `wt new` branches from the **local** ref, and
  `main` in the primary checkout is stale at `08d1d6a`. Resolve
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
  `{dp['backlog']}` and keep working your slice. **Until `SS-01` merges, the
  instruments still name the dead per-epic path**, so invoke
  `python3 scripts/disposition.py --ledger {dp['backlog']}` explicitly. **Append;
  never rewrite, truncate, reorder or reset it.** An entry with no reproduction
  is not a finding, it is a hunch — do not file it.
- **Skills are READ from this repository and NEVER edited.** Anything that must
  change in a Skill Manager home is **proposed as a diff and escalated**.
  `spec-double-compiler` is **deliberately unsynced** for this epic's duration.
- Your worktree has its own Skill Manager home (`<worktree>/.skill-manager`,
  gitignored), and **nothing you change inside it is in this PR**. Before
  stopping, run `skill-manager home close-out --home <worktree>/.skill-manager
  --into /Users/hayde/IdeaProjects/tla-spec-dev/.skill-manager` and state the
  verdict in the PR body. Leave the worktree standing; the finalizer removes it.
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

**Verify every claim in this issue before acting on it.** Issue #271 handed this
epic four figures and **four of them moved** — 41,691 py lines was measured at a
different tree, `0 of 18` judged goals is `0 of 20` here, the "live" ledger path
does not exist, and the `scope` sweep is 82 figures rather than 102. The
predecessor's cut list had **three of four items that did not exist as
described**. `scope` cannot do this checking for you: it returns **zero** counted
figures on charters, plans, baselines and price tables (`CA-08-DF-01`).

**And one live defect was found at kickoff and is already filed:**
`SS-00-DF-01` — `score_tools.py audit` reports **9 violations on a fresh worktree
and 0 on another**, at the same commit, because the archived-ledger fallback
orders by filesystem mtime and git does not preserve mtimes. **Every `audit`
figure you quote is a joint property of the tree AND the checkout.**

## Regression & close-out

Run the full REQUIRED matrix above. Report **reds, passes, skips and collection
as four numbers that sum**, at the base and at your tip, with **every movement
attributed** and its numerator/denominator direction named. The epic-base figure
is in `GOAL-tree-stabilizes`' baseline evidence — compare against **that**, not
against a recollection. Test command:
`uv run --with pytest --with pyyaml -m pytest tests -q` — **without
`--with pyyaml`, 12 tests go phantom red.**

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
