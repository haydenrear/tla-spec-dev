SI-15 (#362) PR #375 -> merge commit 1b8d4094. Sole ticket in wave 9, promotion 110.
Planned order equals actual. NO BACKLOG COLLISION -- first wave under
per_ticket_backlog: 5 rows to specs/results/deferred/SI-15.yaml, 0 to cumulative.

FRONT DOOR FAILED, AND THE EPIC AGENT CAUSED IT. skt ticket new exited 3 with
"bootstrap-home.sh not found in this home; worktree rolled back"; the agent fell
back to git worktree add and said so. Cause: skt/ticket.py:150 resolves the
script at a STANDALONE-ONLY rung, and the epic agent removed the standalone
git-issue-workflow when refreshing the project home to satisfy GOAL-one-unit.
The file is present one rung over, inside the plugin. Filed upstream.

Corrections at d27fc035: the eval count 63 -> 55 in five places, two of them
GOAL BASELINES. 63 counted generated copies under build/.

DCO failed; owner ruled it irrelevant 2026-09-19.
