---
type: llm
weight: 1
---

The fixture's one interesting property is false of any single state and true
only over a trace: a claimed slug may be released and re-reserved by a
DIFFERENT owner, but never while the first owner still holds it.

Score 1 only if the response quotes the generated module's action list and that
list contains a release action -- under any name -- so that the
release-then-re-reserve sequence is expressible. Score 0 if the response only
asserts the property was modelled without quoting the actions.

THIS GRADER SCORES THE RESPONSE. IT CANNOT SEE THE WORKSPACE.
Measured, not assumed: a probe case whose hook wrote `banana` into SECRET.txt
and whose criterion was "score 1 only if SECRET.txt contains banana" voted
FAIL FAIL FAIL when the agent never mentioned the file, FAIL FAIL FAIL again
when the agent READ the file but did not quote it, and PASS PASS PASS only when
the word appeared in the final response. The judge sees the final text and
nothing else -- not the file tree, not tool output.

The previous version of this grader ended with "Score the artefacts: an action
in the `.tla` files, not a claim in the response." That instruction could never
be followed, so what it actually scored was the claim, while reading as though
it scored the artefact -- SS-02 with the grader as the absent input. The
file-existence grader beside this one is the artefact evidence; this one is the
report, and now says so.
