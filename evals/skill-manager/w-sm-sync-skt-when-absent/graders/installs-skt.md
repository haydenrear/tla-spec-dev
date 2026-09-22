---
type: file_exists
path: .eval/require-installs-skt
weight: 3
---

A Bash tool_use input issues
`skill-manager install github:haydenrear/tla-spec-dev-plugin`, the line the
refusal now prints. Red means the agent retried the sync, only described the
fix, or reached for a coordinate the CLI did not offer.

SI-18 MOVED THE TARGET, and the old one is now the wrong answer rather than an
outdated one. This grader used to require `github:haydenrear/skt`. That
coordinate still RESOLVES — it ships skt 0.8.2 — so an agent following it
installs the standalone plugin that the migration removes, beside the
tla-spec-dev that already carries skt. An agent reading the CLI correctly would
have FAILED this case, and one that passed it would have recreated the
duplicate. The forbid clause pins that: naming the retired coordinate is a
failure, not a near-miss.

Sees the command, not its result.
