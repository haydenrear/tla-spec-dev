"""Does the plan start at the worktree FRONT DOOR? EXIT CODE ONLY.

Run under `checks/nowrite.sb`; the hook writes the verdict from the exit status.

This is the one defect `git-issue-workflow` documents against itself, and it
was measured rather than imagined: four eval runs reached the hand-rolled
`git worktree add` route, for four different reasons, produced a plausible
result each time, and none of them reported a problem. The cost is invisible
because the by-hand route WORKS -- it just leaves the ticket agent writing the
operator's global Skill Manager home, since `git worktree add` alone creates a
checkout with no home of its own.

So the property is narrow and worth checking exactly: the plan's first
worktree move is `wt new` / `skt ticket new`, and if it spells the two halves
out by hand it says so and pairs the worktree with a home bootstrap.

What this CANNOT tell you is whether the agent would actually run what it
wrote. It reads a plan. That bound is in the grader body.

Exit 0  PLAN.md names the front door, or a by-hand pair with the home step
Exit 1  a bare `git worktree add` with no home, or no plan at all
"""

from __future__ import annotations

import pathlib
import re

FRONT_DOOR = [r"\bskt\s+ticket\s+new\b", r"\bwt\s+new\b", r"\bwt\b.*\bnew\b"]
HOME_STEP = [r"bootstrap-home\.sh", r"\bskill[- ]manager home\b", r"\bits own (Skill Manager )?home\b"]


def main() -> int:
    plan = pathlib.Path("PLAN.md")
    if not plan.is_file():
        print("no PLAN.md")
        return 1
    text = plan.read_text(encoding="utf-8", errors="replace")
    if len(text) < 200:
        print(f"PLAN.md is {len(text)} characters; too short to be a plan")
        return 1

    front = any(re.search(p, text, re.I) for p in FRONT_DOOR)
    home = any(re.search(p, text, re.I) for p in HOME_STEP)
    bare_add = re.search(r"git\s+worktree\s+add", text, re.I)

    print(f"front door named: {front}; home step named: {home}; git worktree add present: {bool(bare_add)}")

    if front:
        # The front door does the home step itself, so naming it is enough.
        print("front door ok")
        return 0
    if bare_add and home:
        # The documented by-hand equivalent: acceptable, and the skill says to
        # report having reached it.
        print("by-hand pair ok: worktree and home bootstrap are both named")
        return 0
    if bare_add:
        print(
            "the plan hand-rolls `git worktree add` with no home step: the "
            "ticket agent would write the operator's global home"
        )
        return 1
    print("the plan names no way of creating the worktree at all")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
