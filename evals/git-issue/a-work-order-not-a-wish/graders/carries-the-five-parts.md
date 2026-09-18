---
type: file_exists
path: ".eval/work-order"
weight: 2
---

Written by the `Stop` hook only after `checks/work_order.py` finds all five
properties in `ISSUE.md`: references the implementer starts from, a measurable
goal, the instrument that decides it, a worktree or branch to work in, and what
closes it out -- plus a mention of something that is actually in this program,
so an issue written without opening the repository cannot earn it.

Each property accepts several spellings, deliberately. Pinning one wording
would grade phrasing rather than structure.

The agent cannot write this path: `verify.sh` clears `.eval/` before it looks,
and the check runs write-denied and signals through its exit status.

**What it does not decide.** Whether the references are the right ones, or the
metric a good metric. It reads structure. An issue with five well-formed parts
aimed at the wrong problem earns this verdict, and the response grader beside it
is the only thing here that looks at the substance -- which is why its weight is
half of this one's.
