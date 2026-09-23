# Re-verification after the pull and the home rebuild

SI-26's fifteen transcripts predate both skill-manager's 13 commits and the
worktree home rebuild. These re-run the paths most likely to have moved.
HEAD `2c21e609`, 2026-09-23. Every exit code captured directly, never through a
pipe.

## Result: every path green

| surface | result |
|---|---|
| `skt` — version, status, check, ticket list, ticket sweep | **all rc=0** |
| `tla-spec-dev` — version, help, all 7 verb helps | **all rc=0** |
| lifecycle — bootstrap-home → ticket new → info → list → close | **all rc=0** |
| dirty-tree guard — refusal, then `WT_DIRTY_OK=1` override, then close | **rc=1, rc=0, rc=0** |

`skt check` now returns **rc=0, "all current (11 change-managed units)"**. Before
the rebuild it was rc=10 with four stale units — git-issue, skt,
spec-double-compiler, test-graph.

## Their `skt status` fix, verified in situ

`65ebfdec` rewrote the migration advice. The old advice is visible in THIS
session's own startup hook, which fired before the rebuild:

> `migrate skill-manager now ships inside the skt plugin; skill-dev-skill is
> gone … declare [plugins.skt] source = "github:haydenrear/skt"`

That names `github:haydenrear/skt` — the coordinate the migration removes. An
operator following it reinstalls the exact standalone the epic deleted. After
the fix and the rebuild, `skt status` emits **no migrate line at all**, because
the home no longer carries the shape that triggers it. It also correctly reports
`checkout integration repo`, the active spec workflow, and
`19 installed (11 change-managed)`.

## A regression the graphs caught, and half of it was mine

Nuking `.skill-manager` left the agent projection directories beside it. 24
symlinks across `.claude/skills`, `.codex/skills` and `.gemini/skills` still
pointed at `<home>/skills/<unit>` — the standalone rung the nuke removed. `ls`
lists a dangling symlink's name, so the directories looked populated while every
`open()` failed with ENOENT.

`sktHooks` went **PASSED → ERRORED**: `skt.wrapper-installed` errored with zero
assertions run and the two downstream nodes were skipped. Clearing the 24
dangling links restored it to PASSED. 30 resolvable, 0 broken afterwards. The
contained skills reach agents through `.claude/plugins/`, not `.claude/skills/`,
so nothing was lost.

**The half that is not mine is BLIND-shaped.** `bootstrap-home.sh` printed

    projected: 10 of 10 into each of .claude .codex .gemini
    verified:  10 skill(s) servable

into directories holding 24 unusable entries. It verifies what it just wrote and
never inspects what is already there. Its own comment (~line 1500) records the
same counter lying once before, differently: `verified: 20 skill(s) servable` on
a worktree whose `.claude` had no `skills/` directory at all — *"Every agent
launched in that worktree saw zero skills."* That fix taught it about the empty
case, not the dangling case. `skt check` also reported `all current` throughout.

Handed to SI-27 (#382) to file, since that ticket owns the findings files this
wave.

## Graphs, same run

specWorkflow 9/9, cliWorkflow 2/2, effectProviderExamples 1/1, sktHooks 3/3 —
**PASSED**. sktSurface **ERRORED** on `skt.ticket-roundtrip` only, 13 of 39
assertions, the same thirteen by name as SI-25 — `SI-25-DF-06` and `-DF-07`,
unchanged. Tree clean after every run.
