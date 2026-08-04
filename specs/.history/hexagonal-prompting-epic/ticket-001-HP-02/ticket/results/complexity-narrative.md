# HP-02 — complexity narrative

**Measured delta: direction = zero.** HP-02's `implementation_scope` is
`["prompts/", "references/"]` and its `conflict_keys.tla` is empty. It adds no
variable, no action, and no configuration to any modeled surface, and its
declared `model_delta_expectation` is `none`. Per `surface_cost_rule` — the plan
calls that the most important rule it has — a ticket that adds no modeled
surface pays no state-space cost, and that is the intended outcome here, not an
omission.

The two files it ships (`prompts/hexagonal_implementation.md`,
`references/hexagonal_prompting.md`) fall under the plan's
`representation_scope.out_of_model` entry *"prompts/**, references/**, *.md --
documentation and sub-agent prompts"*. The standing proviso — an out-of-model
FILE does not make an out-of-model EFFECT — is satisfied trivially: nothing
executes these files. No script reads them, no test enumerates them
(`tests/test_source_citations.py` scopes `references/` out deliberately), and
they perform no effect on any modeled action path.

## The refinement search, and why it found nothing to apply

There is no modeled representation in HP-02's scope to reduce. The one reduction
the ticket could have made is the one it deliberately refused.

**Refused: a checker for the two copies of the ask.** The ask exists twice —
canonically in `prompts/hexagonal_implementation.md`, and inlined as arm B's
Section 1 because HP-01 requires each arm to be a complete standalone prompt
dispatched verbatim. The obvious tidy-up is a test asserting the two stay in
sync. It was not written, and not because it would be hard: the epic's
`no_new_gates_rule` says a ticket that finds itself adding a rule that refuses
something has left scope, and this reference page's own central argument is that
a check which rewards duplication gets duplication. Shipping a duplication
*enforcer* inside the document explaining why enforcement backfires would be a
particularly poor joke. The duplication is declared in a table with the
canonical side named, and if the drift ever matters the fix is to delete a copy,
not to add an enforcer.

## The complexity result this ticket actually produced, and it is negative

HP-02 carries `contribution: direct` on `GOAL-simpler-same-behavior`, whose
`expected_effect` is *"Arm B's descriptor shows lower complexity at equal
behavior."* The local pilot went **the other way**.

- **The declared instrument could not run.** `analyze complexity` measures a
  TLA+ model; both A/B arms produce Python; and the A/B holds ONE model for both
  arms by design, so the only artifact the scanner can read is byte-identical
  across arms. There is also no "before" — both arms wrote new code from one
  feature file, and "before and after" presupposes a refactor. Filed as
  **HP-02-DF-01**. No proxy metric was substituted, because a line count wearing
  the declared harness's name is how a number acquires authority it never had.
- **On the only substitute available**, arm B is larger: 5 production files
  against 1, 274 production lines against 120, a `Protocol` and two
  implementations where the control has a method.
- **Two real representation reductions did land in arm B**, and both are the
  kind the prompt asked for: it does not store `available` (computes
  `quota - held - committed`), and it keeps no in-memory mirror of the ledger
  where the control carries `self._lines` alongside the file. So arm B holds
  **fewer pieces of state that can drift** and **more modules**. Whether that
  nets out as simpler is exactly the judgement D2 exists to make, and this
  ticket does not get to make it.

This reproduces HP-01's sealed **N01** — *"ports, adapters, and an inversion
boundary are more parts, more indirection, and a larger descriptor, not fewer"*
— and HP-02 claims no credit for it and tuned nothing toward it.

## MF-020 read forward, since this ticket is the one that wrote MF-020 into a prompt

The prompt's own anti-MF-020 clause ("a smaller number is never, on its own, a
better design; whenever you remove something, point at what still holds the
behavior or say the behavior is gone") is applied to this ticket's own record:
**nothing was removed anywhere.** The zero delta is a zero, not a reduction
dressed as one, and there is no deleted edge to account for.

Full evidence and the four-way classification of each declared local signal:
`specs/tickets/HP-02/results/goal-signal.md`.
