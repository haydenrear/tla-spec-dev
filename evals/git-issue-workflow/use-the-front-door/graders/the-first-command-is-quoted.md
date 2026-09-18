---
type: regex
pattern: '(skt\s+ticket\s+new|wt\s+new|git\s+worktree\s+add)'
weight: 1
---

The reply ends with a command rather than a description of one. Any of the
three spellings matches, including the wrong one: this grader settles that
something executable was quoted, and the verdict grader beside it settles
whether it was the right thing.

Splitting them is deliberate. Asked both at once -- "is a command quoted" and
"is it the front door" -- a judge on a long report answered neither reliably.
The mechanical half belongs to a regex.
