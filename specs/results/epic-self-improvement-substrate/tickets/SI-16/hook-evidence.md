# SI-16 — the hooks, verified by their LOG

The ticket forbids accepting an eval score here: a case declaring `plugins:`
silently disables the target plugin's hooks while both arms still score 1.00
(SI-14-DF-01), and `skt-session-start.sh` never exits non-zero by contract.
So this is the hook's own evidence.

## The discriminating condition

The hook resolves skt in three steps: `$SKILL_MANAGER_HOME/bin/cli/skt`, then
`skt` on PATH, then `$CLAUDE_PLUGIN_ROOT/skills/skt/src/skt/cli.py`. The run
below removes the first two, so ONLY the rewritten plugin-root path can answer:

- the home was built fresh with no `bin/` at all
- `PATH=/usr/bin:/bin`, and `command -v skt` on that PATH finds nothing

Had the `skills/skt/` segment been wrong, `resolve_skt` would have returned 1
and the log line would read `skt-unresolvable`. It does not.

## Command

    env -i PATH=/usr/bin:/bin SKT_PYTHON=/opt/homebrew/bin/python3.14 \
        SKILL_MANAGER_HOME=<fresh home> \
        CLAUDE_PLUGIN_ROOT=<repo root> \
        CLAUDE_SESSION_ID=si16-v2 \
        bash hooks/skt-session-start.sh

## Result

    exit 0
    <home>/logs/skt/hook.log EXISTS
    2026-09-20T20:10:47Z session-start session=si16-v2 status-injected

`status-injected`, not `status-failed` and not `skt-unresolvable`: the hook
resolved skt through the carrier plugin root and put the report on stdout.

A second invocation appended a SECOND line (2 lines for 2 runs), which is the
"one line per invocation" half of the contract.

## What this does NOT establish

That an eval run exercises these hooks. It does not — `evals/run.sh` copies
`evals/hooks/hooks.json` over `<view>/hooks/hooks.json`, which is now a
committed file. See SI-16-DF-02.
