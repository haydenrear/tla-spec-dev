---
type: file_exists
path: ".eval/parses"
weight: 1
---

Written by the `Stop` hook only after SANY parses every `.tla` under
`specs/program_model/`. A module that does not parse is not a model, whatever
the report says about it.

The agent cannot write this path: `verify.sh` deletes `.eval/` before it looks.
Demonstrated -- a workspace with all three verdict files pre-planted, plus a
`placeholder: true` manifest, came out of the hook with none of them.
