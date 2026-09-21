# The manual gamut (SI-26)

Every surface driven by hand against the **rebuilt root home**, because
GOAL-evals-earned forbids writing an eval for behaviour nobody has watched
work. Each exit code was captured directly, never through a pipe — an exit
code read through a pipe is `tail`'s, and this epic has made that error before.

| file | what it records |
|---|---|
| `tla-spec-dev-help.txt` | every verb's `--help`, 9 commands, all rc=0 |
| `tla-spec-dev-lifecycle.txt` | scaffold project → scaffold workflow → open ticket → analyze → run spec-unit-tests |
| `tla-spec-dev-close-retire.txt` | generate / analyze corpus / effect-conformance / retire / close |
| `skt-verbs.txt` | status, check, ticket list, build, publish, sync against the root home |
| `skt-ticket-lifecycle.txt` | bootstrap-home → ticket new → info → list → close |
| `dirty-tree-guard.txt` | the dirty-tree refusal AND the `WT_DIRTY_OK=1` override |
| `workflow-scripts.txt` | `wt`, `new-change.sh`, `close-change.sh`, `bootstrap-home.sh` |
| `plugin-repository-verify.txt` | verify.sh's FAIL, decomposed into its three causes |
| `graph-verdicts.txt` | all five test graphs with stated verdicts |
| `two-ticket-systems.md` | the spec ticket vs the worktree ticket, and where they trap a reader |
| `refusals.md` | every refusal observed, each with why it is correct |

## What the gamut actually established

**The front door works.** `tla-spec-dev` and `skt` both resolve through the
installed plugin's shims; the installed verb surface matches the worktree
source exactly (7 verbs, `analyze` carrying only `complexity` and `corpus`).

**Every refusal named its own next command.** Nine distinct refusals were
observed and none was retried to make it quiet. Two of the nonzero exits were
MY invocation errors, recorded as such rather than filed as defects.

**`skt check` exits 10 and that is not a failure** — `NOTIFY_EXIT` at
`check.py:145`. It reported 2 notifications at tier root.

**The dirty-tree guard was exercised in both directions**: it refused a dirty
parent tree, and `WT_DIRTY_OK=1` let the same command through.
