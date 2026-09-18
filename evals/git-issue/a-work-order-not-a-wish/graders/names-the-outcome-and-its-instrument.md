---
type: llm
weight: 1
---

ONE QUESTION ONLY: does the response name something that will be measurably
different once the issue is implemented, AND name the thing that would decide
it -- a test, a suite, a check, a command, a number?

Score 1 only if both are present. "The bug will be fixed" is neither. "A
release-then-resolve test in `test_shortlink.py` passes, and it fails today" is
both.

Do not judge whether the issue is well written, whether the metric is the best
available one, or whether the plan is sound. One question, one answer.

THIS GRADER SCORES THE RESPONSE. IT CANNOT SEE THE WORKSPACE.
Measured, not assumed: a probe case whose hook wrote `banana` into a file and
whose criterion was "score 1 only if that file contains banana" voted
FAIL FAIL FAIL when the agent never mentioned it, FAIL FAIL FAIL again when the
agent had opened it but did not quote it, and PASS PASS PASS only when the word
appeared in the final response. The judge sees the final text and nothing else
-- not the tree, not tool output. The artefact is carried by the verdict grader
beside this one.
