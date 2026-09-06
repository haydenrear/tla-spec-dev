---
type: file_exists
path: ".eval/parses"
weight: 1
---

Written by the `Stop` hook only after SANY parses every `.tla` in the workspace.
Here it is a guard rather than an achievement: the model arrives already
parsing, so this can only go red if the session broke it.
