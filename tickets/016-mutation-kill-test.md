# Mutation Kill Test

Status: Open

Nothing today validates a representation against the program; TLC passing
only proves self-consistency. The existing negative projected-state check
validates harness plumbing, not the model's bug-finding power.

Add kill-test support as the representation's falsifiable experiment.

Acceptance criteria:

- A documented (and eventually CLI-assisted) procedure: seed at minimum one
  fault per port and one per invariant into production code, run the
  distilled corpus, and require the kill rate to meet `kill_rate_floor`
  from the manifest budgets.
- Mutants, the kill matrix, and surviving-mutant analysis are stored as
  ticket evidence; surviving mutants at modeled boundaries point at the
  variable or action to refine.
- Onboarding and promotion are the required kill-test moments; per-ticket
  work reuses baseline mutants plus one new mutant at the changed boundary.
- The distributed_history example gains a worked kill test.
