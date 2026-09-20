# Waves 11-12 — merges

Range `308d2732` (wave-10 close) -> `7e180ea2`.

## Pull requests merged

| PR | ticket | head | merge | files |
|---|---|---|---|---|
| #378 | SI-16 demote skt plugin->skill | 4caab479..fbe8bb9a | `d7a450f3` | 110 |
| #379 | SI-17 move wt into skt | `569a472c` | `d692d6a1` | 44 |

Both merged with `--admin`: DCO red, which the owner declared irrelevant
for this epic on 2026-09-19. GitGuardian green on both.

## Epic-agent commits in the range

- `7e180ea2` record the root home as it stood immediately before the delete
- `769b723d` findings: attribute the seven that skill-manager actually owns
- `f322f7dc` plan: SI-17 is done — wave 12 merged, and the plugin repo now has both waves
- `d692d6a1` Merge pull request #379 from haydenrear/feature/366-wt-into-skt
- `a9e3c0da` parse_simple_yaml learns `|`, and skt gets its [project] table back
- `569a472c` SI-17: move wt into skt, so the worktree tool lives with the lifecycle CLI
- `d4c91275` run-graphs: --only can reach an OPT-IN graph, which is what opting in means
- `afa4addd` plan: the sixteen merged tickets say done, because they are
- `d7a450f3` Merge pull request #378 from haydenrear/feature/365-nest-skt
- `fbe8bb9a` SI-16: the fresh-home evidence, including the install that failed first
- `f3343b3b` SI-16: classify the merged graphs, and the hook path the grep could not see
- `4caab479` SI-16: demote skt from plugin to contained skill
- `b249fae5` record the front-door state at SI-16 dispatch, before the agent hits it
- `802ed52f` plan status: name the ticket actually in flight

## Subtree history

`a317aeb5` brought skt's own history in via `git subtree add`, full history,
no --squash, from `b7ea313a` (the PR haydenrear/skt#54 head, NOT main -- main
lacks the front-door fix). That accounts for the ~90 SKT-* commits in the raw
range; they are skt's, not this epic's.
