---
type: file_exists
path: ".eval/front-door"
weight: 2
---

Written by the `Stop` hook only after `checks/front_door.py` finds that
`PLAN.md` either names the front door (`skt ticket new` / `wt new`), or spells
out the documented by-hand pair -- `git worktree add` **with** the home
bootstrap beside it. A bare `git worktree add` and nothing else fails.

This is the narrowest useful property in the suite, and it is the one with the
best evidence behind it: the by-hand route WORKS, which is exactly why its use
is silent. Four eval runs reached it for four different reasons, produced a
plausible result each time, and left no trace but the cost -- a ticket agent
writing the operator's global Skill Manager home instead of its own.

The agent cannot write this path: `verify.sh` clears `.eval/` first, and the
check runs write-denied.

**What it does not decide.** Whether the agent would run what it wrote, or
whether the rest of the plan is any good. It reads one property of a document.
