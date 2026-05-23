# Batched Case Execution

Status: Done

The current runner writes one Python program per case and spawns one process per
case. This is simple and isolated, but slow for thousands of cases.

Add a batched execution mode while preserving per-case program generation for
debuggable isolation.

Acceptance criteria:

- `--batch` mode executes many cases in one process.
- Failures still report case names and adapter labels.
- Existing one-program-per-case mode remains available.

Implementation:

- Added `--batch` mode to `run_generated_case_adapters.py`.
- Failures include case name and selected mapping label.
- The old generated-program mode is unchanged.
- `--batch --python path/to/python` re-executes the batch under the requested
  interpreter for project venvs.
