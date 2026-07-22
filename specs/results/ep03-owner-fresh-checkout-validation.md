# EP-03 epic-owner fresh-checkout validation

External review validated PR #82 at exact candidate
`a455769348a85a9fa8f93e02fdeb6969f0294e95` from a new local clone at
`/private/tmp/tla-spec-dev-ep03-owner-final.GDk8Bv/repo`. The clone had no
pre-existing Test Graph build directory or HTTP project virtualenv. Its tracked
tree was clean before and after validation; only ignored caches and reports were
created.

## Review corrections

- User-facing legacy HTTP commands now use the repository's ignored `.cache/`
  directory and a portable `TLC2_BIN` override instead of machine-specific
  paths. The focused HTTP suite passed 9/9 before this clone was made.
- PR #82 uses the required `Refs #79` marker and records `DEF-001` through
  `DEF-003` under `## Deferred findings`.
- DCO and GitGuardian passed at the corrected candidate.

## Fresh-clone results

- Repository tests: `611 passed in 12.06s`.
- Current spec units: `63 passed in 14.29s`; one current target validated.
- Host TLC: no error; 5,619,356 generated states, 231,621 distinct states,
  depth 25, 0 queued states at completion, 11 seconds.
- `effectProviderExamples-20260722-071146-6fc0a18b`: one node passed, 22/22
  assertions passed, 36/36 fixed mutants reconciled, 2,079 control points per
  accepted repetition, and 70 External cases. Summary SHA-256:
  `5bca795b322b12dd847db28babc7319f9287255ba7eadaba4037078fa7ebddda`.
- `specWorkflow-20260722-071240-f42c31ab`: 8/8 nodes and 64/64 assertions
  passed. Summary SHA-256:
  `895cb725df4369a0367638e33e00984b06628c5f6fc654c04fb7090509f817dd`.
- `cliWorkflow-20260722-071323-7a5f3592`: 2/2 nodes and 41/41 assertions
  passed. Summary SHA-256:
  `28026d25b9ffb63290a02c554f790a76cdbbdefb16165c5cb1c725c52ed3645d`.

The sandbox initially refused UV's home cache/network and TLC's local RMI
socket. The same commands passed with a clone-local UV cache and the required
network/local-socket permissions. Those refusals were execution-environment
limits, not product failures.

This closes the two external-review evidence gaps: the aggregate graph now ran
against the exact corrected PR head, and the aggregate graph, host graphs,
repository tests, spec units, and TLC all ran from one clean clone rather than
only from the ticket worktree.
