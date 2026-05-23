# Richer Case Labels

Status: Done

Generated labels are currently action names only. This validates adapter
coverage, but it is too coarse for selecting edge cases.

Add support for stable case labels from TLA comments, state predicates, or
manifest-defined labelers.

Acceptance criteria:

- Generated cases can include labels such as `ready_one_record`,
  `partial_context`, or `already_exported`.
- Adapter mapping can target either coarse action labels or fine-grained labels.
- Missing mapping validation reports all uncovered labels clearly.

Implementation:

- `generate_cases_from_tlc_dump.py --labeler module:function` adds
  repository-local labels from `before/action/after/changed`.
- Adapter mappings are selected in TOML order, so fine-grained mappings can
  override coarse action mappings.
- Coverage validation is per case: every case needs at least one mapped label.
