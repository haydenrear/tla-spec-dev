---
type: file_exists
path: ".eval/manifest"
weight: 1
---

Written by the `Stop` hook only after `spec_manifest.yaml` parses as a YAML
mapping with at least three keys, one of them a manifest key -- `module`,
`modules`, `ports`, `invariants`, `finite_model` or `codegen`.

ITS PREDECESSOR ASKED ONLY WHETHER THE PATH EXISTED, and a probe scored it
green on a manifest whose entire contents were `placeholder: true`. Worse, in
the run that scored 1.00 the manifest was typed by the agent's `Write` tool
while `tla-spec-dev scaffold project` failed with exit 1 on all three attempts
-- so the grader offered as evidence that the pipeline had run was evidence of
nothing but typing.
