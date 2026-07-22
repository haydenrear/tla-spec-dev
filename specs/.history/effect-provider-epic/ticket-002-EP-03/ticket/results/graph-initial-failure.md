# Effect-provider Test Graph diagnostic

The first aggregate graph run was deliberately retained as a failed diagnostic:

- Run: `effectProviderExamples-20260722-055525-b28aa642`
- Failed assertion: `atomic kills and exact replays are complete`
- Every live project test and all 56 HTTP external cases passed.
- Root cause: the aggregate node incorrectly required exact replay fields in
  both atomic repetitions. The preregistered atomic runner intentionally uses
  `replay_failures=repetition_index == 0`: repetition one proves nonzero,
  structured, transcript-exact replay for all 12 first discoveries; repetition
  two reruns all 12 mutants and proves equal transcript/verdict digests without
  duplicating replay work, so its replay fields are `null`.
- Correction: the graph now requires 12/12 kills in both repetitions, exact
  replay for every mutant in repetition one, explicit null replay fields in
  repetition two, and equal transcript/verdict digests.
- Passing rerun: `effectProviderExamples-20260722-055736-b0a9ce79`.

This changed only the central evidence adapter. It did not change a project,
model, mutant catalog, threshold, or accepted score.
