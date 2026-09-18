# SI-03: the front door, and why this is corroboration rather than a 59th row

`git-issue-workflow` SKILL.md requires an agent that reached the by-hand
worktree route to say which case it was in. This is that line, with the evidence.

**Case: `skt` resolved and it FAILED.** Not "not found", not "looked in the
wrong place".

```
$ SKT="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/bin/cli/skt"
$ test -x "$SKT" && echo EXECUTABLE
EXECUTABLE
$ "$SKT" ticket new 336-improvement-card --base 21a714486bc1e5e1b6671a65d97a90dab9489db6 \
      --path ../wt-336-improvement-card
  ! reconcile: no skill-manager projection for test-graph on claude at
    /Users/hayde/IdeaProjects/wt-336-improvement-card/.claude/skills/test-graph.
    In order to create all symlinks missing, please run: skill-manager sync
  ! reconcile: no skill-manager projection for test-graph on codex at ...
  ! reconcile: no skill-manager projection for test-graph on gemini at ...
  error: this home holds 15 skill(s) and an agent launched here can reach 12.
    A skill is served through <root>/.<agent>/skills/<unit>, not out of the
    store. These are missing or resolve outside /Users/hayde/IdeaProjects/wt-336-improvement-card:
      .../.claude/skills/git-issue-workflow      (and .codex, .gemini)
      .../.claude/skills/spec-double-compiler    (and .codex, .gemini)
      .../.claude/skills/test-graph              (and .codex, .gemini)
```

**It rolled back completely.** Verified rather than assumed:

```
$ git worktree list | grep 336        -> (no output)
$ ls -d ../wt-336-improvement-card    -> No such file or directory
$ git rev-parse --verify feature/336-improvement-card
fatal: Needed a single revision
```

Worktree gone, branch gone. I fell back to the documented by-hand route in
`git-issue-workflow/references/epic-ticket.md` §2 — `git worktree add` chained
with `bootstrap-home.sh` — which succeeded. `bootstrap-home.sh` then printed the
same projection error; the home exists and is usable, and the three unreachable
units are exactly the three this epic moved into the plugin.

## Why no new backlog row

**This defect is already filed twice, by two different tickets, in the wave
immediately before mine:**

| id | filed by | what it says |
|---|---|---|
| `SI-06-DF-02` | SI-06 | `skt ticket new` refuses on an unprojected home, rolls the worktree back, and still exits 0. The three unreachable units are the three this epic moved into the plugin |
| `SI-11-DF-04` | SI-11 | the unfixed half of the same thing: `new-change.sh` exits 3 correctly and `wt` propagates it; the suspect is `wt.py:main()` returning `proc.returncode` to an entry point that never `sys.exit()`s it |

Both are `pending`. A third row would add no information and would hand the epic
agent another concurrent append to the end of a 58-row cumulative file — which
is the single mechanism that produced **every conflict in wave 3**, and which
the wave-3 review names as its recurring shape. So this is recorded here and
reported in the PR body under `## Skill changes proposed`, citing the two
existing ids.

**What my run adds to theirs, and it is small:** it reproduces on a *fourth*
ticket, at a *later* epic tip (`21a71448`), after SI-11's plugin-layout repairs
merged — so the projection failure is not something SI-11's work fixed. That is
one sentence of corroboration, not a finding.
