# Richer Case Labels

Generated labels are currently action names only. This validates adapter
coverage, but it is too coarse for selecting edge cases.

Add support for stable case labels from TLA comments, state predicates, or
manifest-defined labelers.

Acceptance criteria:

- Generated cases can include labels such as `ready_one_record`,
  `partial_context`, or `already_exported`.
- Adapter mapping can target either coarse action labels or fine-grained labels.
- Missing mapping validation reports all uncovered labels clearly.
