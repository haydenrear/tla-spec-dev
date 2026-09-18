---
type: file_exists
path: ".eval/checks"
weight: 1
---

Written by the `Stop` hook only after TLC reports `Model checking completed. No
error has been found` on at least one of the model's own `.cfg` files.

THIS IS THE GRADER THE SANDBOX SAID WAS IMPOSSIBLE. The Bash tool runs under a
profile that denies filesystem writes to every subprocess, so TLC aborts
creating its metadir and the agent cannot check its own model (`H-19`). Hooks
run outside that profile -- measured: a Stop hook's `python3 -c "open(...,'w')"`
and its `mkdir` both succeed in the same workspace where the Bash tool is
refused. So the check the run cannot perform is performed on the run.

A model that TLC cannot explore is a document. No amount of prose crosses that
line, which is what makes this the one grader here that a confident report
cannot move.

**A red here is not always the model's.** `file_exists` has no UNDECIDED state,
so a verifier whose java or `tla2tools.jar` did not resolve produces the same
absent path as a genuine failure. `.eval/UNDECIDED-toolchain` is written in that
case; check for it before reading a 0 as the run's.
