# Corpus Distillation

Status: Open

TLC edge lists are raw output, not a corpus. The ecommerce example emits 732
external cases with no principled selection, and case caps exist nowhere.

Add stratified case selection to `generate_cases_from_tlc_dump.py`.

Acceptance criteria:

- Selection guarantees at least one case per (action, label class), then
  fills remaining budget by state-predicate novelty.
- Respects `max_internal_cases_per_component` and
  `max_external_cases_per_action` from the manifest budgets.
- The generated manifest records every dropped case and the rule that
  dropped it — no silent truncation.
- Named regression traces (promoted counterexamples and production bugs) are
  always retained regardless of caps.
