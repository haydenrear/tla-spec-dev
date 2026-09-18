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

**A red here is not always the model's.** `file_exists` has no UNDECIDED state,
so a verifier whose java or `tla2tools.jar` did not resolve produces the same
absent path as a genuine failure. `.eval/UNDECIDED-toolchain` is written in that
case; check for it before reading a 0 as the run's.
