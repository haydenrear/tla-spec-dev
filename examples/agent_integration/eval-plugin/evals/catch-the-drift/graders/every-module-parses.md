---
type: file_exists
path: ".eval/parses"
weight: 1
---

Written by the `Stop` hook only after SANY parses every `.tla` in the workspace.
Here it is a guard rather than an achievement: the model arrives already
parsing, so a red usually means the session broke it.

**Usually, not only.** It also goes red when the verifier's own java or
`tla2tools.jar` did not resolve, because `file_exists` has no UNDECIDED state
and an unrun check and a failed one are the same absent path. Before reading a
red here as the agent's, check `.eval/` for `UNDECIDED-toolchain`.
