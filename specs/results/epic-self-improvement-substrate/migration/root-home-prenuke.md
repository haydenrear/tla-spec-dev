# Root home: final state immediately before the delete

Captured 2026-09-20T23:51:24Z. Supersedes root-home-inventory.md,
whose source paths had gone stale (meta-orchestrator-202, wt-108-cdc-mvp-023).

Size 5.3G, 139231 entries; cache/ 3.0G and tools/ 1.3G are disposable by design.

## Reinstalled (11, all from main)

| unit | coord | main at capture |
|---|---|---|
| acp-cdc-ai-python | github:haydenrear/acp-cdc-ai-python-skill | 3c02dc52 |
| andrej-karpathy-skills | github:haydenrear/andrej-karpathy-skills | 43442d0f |
| debugging | github:haydenrear/debugging-skill | 3520c531 |
| deploy-helm | github:haydenrear/deploy-cdc | 5d48d0e6 |
| doc-repo-devops | github:haydenrear/doc-repo-devops | 3bf44536 |
| hyper-experiments-finance | github:haydenrear/hyper-experiments-finance | 5b3c8d2b |
| hyper-experiments | github:haydenrear/hyper-experiments-skill | 41b8f560 |
| llm-wiki | github:haydenrear/llm-wiki | d4d6b11a |
| tracing-observability | github:haydenrear/tracing_skill | 9c302067 |
| vision-toolbelt-skill | github:haydenrear/image-ocr-sam-skill | bbd61111 |
| tla-spec-dev-plugin | github:haydenrear/tla-spec-dev-plugin | 769b723d |

## Deliberately NOT reinstalled (10, owner decision 2026-09-20)

Archived first to `/Users/hayde/skill-manager-preNuke-20260920T234941Z.tar.gz` (208K, 89 files),
and all eight are independently recoverable from real sources:

| unit | why out | recoverable from |
|---|---|---|
| cdc-agent-substrate-plugin | file install | commit-diff-context-parent/ |
| code-reviewer | harness fixture | meta-orchestrator/test_graph/fixtures/harness/ |
| live-swarm-agent | harness fixture | meta-orchestrator/test_graph/fixtures/harness/ |
| repo-coder | harness fixture | meta-orchestrator/test_graph/fixtures/harness/ |
| repo-tester | harness fixture | meta-orchestrator/test_graph/fixtures/harness/ |
| run-tracer | harness fixture | meta-orchestrator/test_graph/fixtures/harness/ |
| slm-agent | file install | meta-orchestrator/constituents/ |
| tracer-agent | file install | meta-orchestrator/constituents/ |
| skt | COLLAPSED into the plugin | n/a — contained |
| tla-spec-dev | COLLAPSED into the plugin | n/a — contained |
| test-graph | COLLAPSED into the plugin | n/a — contained |

## Known consequences

- 30 of 77 manifests vendor their Gradle SDK through standalone `test-graph`.
  Those projects are FROZEN for the migration; SI-18 adds the resolver rung.
- The rebuild rewrites agent MCP configs and gateway registration.
  Expect `ACTION_REQUIRED: restart Claude / Codex`.
- `which skill-manager` currently resolves to the HOME SHIM and dies with
  the home. The rebuild is driven from the brew binary directly.
