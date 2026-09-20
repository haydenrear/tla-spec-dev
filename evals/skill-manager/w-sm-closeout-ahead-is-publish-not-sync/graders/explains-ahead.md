---
type: llm
weight: 2
---
This grader reads the agent's FINAL RESPONSE ONLY and CANNOT SEE THE WORKSPACE,
the transcript, or which commands actually ran.

THIS GRADER READS THE FINAL RESPONSE ONLY -- not the workspace, not tool output.

Score 1 if the response says the project home is AHEAD of (newer than) the
worktree's copy of spec-double-2, that syncing the worktree copy into it
would move it backwards / off the pinned revision, and that the fix is to
publish what only the worktree holds (then re-run the close). Score 0 if it
recommends a home sync from the worktree, `skt sync spec-double-2`, or
forcing the close.
