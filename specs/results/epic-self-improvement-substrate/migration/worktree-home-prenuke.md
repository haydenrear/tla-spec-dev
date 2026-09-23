# The worktree home, recorded before the nuke

`/Users/hayde/IdeaProjects/wt-epic-self-improvement-substrate/.skill-manager` — 667 MB, 27 units, tier `worktree`.
Recorded 2026-09-23 at `d4b5e3ca` before rebuilding.

## What it held, and why it is wrong

Eight of the 27 are units the plugin ALSO contains, installed from their
PRE-MIGRATION standalone coords. That is the duplication GOAL-one-unit
clause 1 measures, sitting in the home this worktree resolves from.

| unit | kind | coord it came from | verdict |
|---|---|---|---|
| discovery | SKILL | discovery-skill | **drop** — contained in the plugin |
| git-epic-workflow | SKILL | git-epic-skill | **drop** — contained |
| git-integration-repo | SKILL | git-integration-skill | **drop** — contained |
| git-issue | SKILL | git-issue-skill | **drop** — contained |
| git-issue-workflow | SKILL | git-issue-workflow-skill | **drop** — contained |
| plugin-repository | SKILL | plugin-repository-skill | **drop** — contained |
| test-graph | SKILL | test_graph_skill | **drop** — contained |
| skt | PLUGIN 0.8.2 | haydenrear/skt @ 286a3694 | **drop** — skt is a contained SKILL now |
| spec-double-compiler | SKILL | haydenrear/tla-spec-dev | **drop** — superseded by spec-double-2 in the plugin |

All nine are replaced by ONE coord: `github:haydenrear/tla-spec-dev-plugin`.

## Reinstall from GitHub main

| unit | coord |
|---|---|
| tla-spec-dev | github:haydenrear/tla-spec-dev-plugin |
| andrej-karpathy-skills | github:haydenrear/andrej-karpathy-skills |
| acp-cdc-ai-python | github:haydenrear/acp-cdc-ai-python-skill |
| debugging | github:haydenrear/debugging-skill |
| deploy-helm | github:haydenrear/deploy-cdc |
| doc-repo-devops | github:haydenrear/doc-repo-devops |
| hyper-experiments | github:haydenrear/hyper-experiments-skill |
| hyper-experiments-finance | github:haydenrear/hyper-experiments-finance |
| llm-wiki | github:haydenrear/llm-wiki |
| tracing-observability | github:haydenrear/tracing_skill |
| vision-toolbelt-skill | github:haydenrear/image-ocr-sam-skill |

## Deliberately NOT reinstalled

The same eight the owner excluded from the SI-24 root rebuild: they come
from local paths or deleted worktrees and have no git coord.

`cdc-agent-substrate-plugin` (a DELETED worktree, `wt-108-cdc-mvp-023`),
`code-reviewer`, `live-swarm-agent`, `repo-coder`, `repo-tester`,
`run-tracer` (harness fixtures under meta-orchestrator-202),
`slm-agent`, `tracer-agent` (meta-orchestrator-202 constituents).
