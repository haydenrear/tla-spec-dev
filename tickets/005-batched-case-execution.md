# Batched Case Execution

The current runner writes one Python program per case and spawns one process per
case. This is simple and isolated, but slow for thousands of cases.

Add a batched execution mode while preserving per-case program generation for
debuggable isolation.

Acceptance criteria:

- `--batch` mode executes many cases in one process.
- Failures still report case names and adapter labels.
- Existing one-program-per-case mode remains available.
