# Refusals observed during the gamut, and why each is CORRECT
# SI-26 requires refusals recorded WITH their refusal, not retried until quiet.

| command | rc | refusal | verdict |
|---|---|---|---|
| skt check | 10 | 2 notifications, tier root | NOT an error — NOTIFY_EXIT (check.py:145) |
| skt ticket list (from /tmp) | 1 | not inside a git repository | correct; names the fix |
| skt ticket new GAM-2 | 1 | working tree is not clean | correct — bootstrap-home.sh WARNED TWICE this would happen |
| skt ticket info GAM-2 | 1 | no worktree for GAM-2 | correct; follows from the refusal above |
| skt ticket close GAM-2 | 1 | no worktree for ticket GAM-2 | correct; also noted edited units needing skt publish |
| tla-spec-dev analyze complexity | 2 | required argument: tla | MY invocation was wrong, not a defect |
| tla-spec-dev retire ticket --reason | 2 | unrecognized arguments | MY invocation was wrong; --reason is not an argument |
| tla-spec-dev close ticket GAM-1 | 1 | status=next; mark done/delivered or --force | correct precondition |
| tla-spec-dev run spec-unit-tests --ticket GAM-1 | 2 | no spec-unit tests or case packages found | correct for a freshly scaffolded ticket; it DID resolve the ticket target |
| wt / new-change.sh / close-change.sh (no args) | 1 | usage | correct |

Every refusal named its own next command. None was retried to make it quiet.

NOTE on SIS-KICKOFF-F-04: 'run spec-unit-tests --ticket' resolved the
TICKET target here and reported about it, so this path did not reproduce
the silent-skip. The finding concerns a repo whose specs/current carries
failures ordered first; this disposable repo has none, so the loop never
returned early. The finding is NOT contradicted — it was not exercised.

## Second pass — the remaining verbs and the by-hand front door

| command | rc | refusal | verdict |
|---|---|---|---|
| `skt build --list` | 2 | unrecognized arguments: --list | MY invocation error; `--list` is not a `build` flag |
| `skt ticket sweep` (from /tmp) | 1 | not inside a git repository | correct; same refusal as `ticket list` |
| `skt ticket sweep --epic ...` | 0 | — | dry run by default; excluded the primary checkout AND the epic worktree, both with stated reasons |
| `skt ticket list --json` | 0 | — | schema 1, resolved the primary checkout and the current worktree |
| `git worktree add` (by hand) | 0 | — | the other front door creates the worktree fine |
| `bootstrap-home.sh --root <by-hand worktree>` | 1 | "that checkout has no Skill Manager home" | **CORRECT, and the best refusal in the gamut** — see below |
| `close-change.sh BH-1 --dry-run` | 0 | gate skipped — no home in this worktree | correct; nothing to reconcile |

### The by-hand route refuses for a reason worth reading

`bootstrap-home.sh` would not clone a worktree home from the global home:

> A worktree home is a copy of its PROJECT home, and close-change.sh reconciles
> it back into that same path. Cloning from anywhere else — the global home
> included — makes this worktree unclosable from birth (issue #50).

It then named the exact command to fix it and offered `--source` for a
deliberate override. This is the guard reasoning one step ahead of the
operator: the failure it prevents would not appear at `new`, it would appear at
`close`, long after the cause was forgettable.

**Both front doors therefore behave consistently**: `skt ticket new` refuses a
dirty parent tree (overridable with `WT_DIRTY_OK=1`), and the by-hand route
refuses a parent with no project home (overridable with `--source`). Neither
silently produces a worktree that cannot be closed.
