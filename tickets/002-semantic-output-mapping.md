# Semantic Output Mapping

Status: Done

Generated `StateGraphOutput.changed` is structural. Production adapters often
need semantic expectations such as emitted Kafka records, written JSONL rows, or
HTTP responses.

Add a generic mapping layer that can derive named expected outputs from
before/action/after state, without embedding product-specific behavior in the
skill.

Acceptance criteria:

- Manifest/TOML support for output projection functions.
- Generated case programs can compare adapter output against projected semantic
  output.
- Structural state-delta comparison remains available.

Implementation:

- TOML adapter mappings may define `output_projection = "module:function"`.
- Generated per-case programs and batch mode load the projection through the
  shared runtime.
- Adapters can return `semantic_output`; structural `output` and `after`
  checks remain independent.
