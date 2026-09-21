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
