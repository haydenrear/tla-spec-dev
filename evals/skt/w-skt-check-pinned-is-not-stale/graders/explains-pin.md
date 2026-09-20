---
type: llm
weight: 2
---
This grader reads the agent's FINAL RESPONSE ONLY and CANNOT SEE THE WORKSPACE,
the transcript, or which commands actually ran.

THIS GRADER READS THE FINAL RESPONSE ONLY -- not the workspace, not tool output.

Score 1 if the response says deploy-helm was (or should be) synced and that
spec-double-2 was left alone because the project's skill-project.toml
pins it at dd2d5176 (so it is not out of date for this project). Score 0 if it
syncs or recommends syncing spec-double-2 to its latest version.
