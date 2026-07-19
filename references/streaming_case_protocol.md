# Streaming TLC Case Protocol

Use the streaming protocol when a TLC state graph can contain more transitions
than are safe to render into one Python module. It is the scalable interchange
for cross-language brokers and adapters:

```text
case-manifest.json
cases.jsonl
```

The generator never writes `cases.py` in this mode. It retains parsed TLC
states, scans transitions as an iterator, spools only minimal candidate
metadata to a temporary SQLite database, and materializes only the selected
case records. The temporary database is removed on success and failure.

## Command

```bash
python3 scripts/generate_cases_from_tlc_dump.py \
  path/to/Internal.tla \
  path/to/Internal.cfg \
  --out generated \
  --package internal_cases \
  --format streaming-jsonl \
  --view internal \
  --actions-metadata path/to/actions.yml \
  --max-cases 10000 \
  --max-output-bytes 134217728 \
  --max-rss-mib 512 \
  --max-seconds 120 \
  --per-case-timeout-ms 30000 \
  --seed ticket-seed \
  --tier model
```

Use `--input-dot path/to/Internal.dot` to consume an existing
action-labeled TLC DOT file without starting TLC. `--dot` retains its legacy
meaning: it selects the path where the generator asks TLC to write its dump.

The defaults shown above are active in streaming mode. Legacy Python generation
remains the default output format for bounded existing callers.

## Versioned records

`case-manifest.json` uses `schema_version: cdc.case-manifest.v1` and declares
`case_schema_version: cdc.case-envelope.v1`. Every JSONL record uses
`schema_version: cdc.case-envelope.v1`.

The authoritative Draft 2020-12 schemas ship with the skill:

- `schemas/cdc/case-envelope-v1.schema.json`
- `schemas/cdc/case-manifest-v1.schema.json`

Consumers should use these files directly instead of maintaining a looser
repository-local copy.

The manifest records:

- completion status and a typed budget outcome;
- observed, eligible, candidate, selected, staged, and emitted counts;
- exact counts by action/outcome stratum;
- selection policy, seed, tier, four generation budgets, and the downstream
  per-case timeout;
- spec, configuration, projection, and DOT digests;
- the digest and byte size of the exact `cases.jsonl` stream;
- exact-integer elapsed milliseconds and process peak RSS bytes.

Each case envelope records:

- a stable case ID and per-record digest;
- top-level spec, module, configuration, and projection digests;
- required provenance (`tlc-generated` or `reviewed`);
- view, action, outcome, labels, and TLC source/target IDs;
- canonical before/input/expected-output/after/expected-projection values;
- tier, selection stratum/rank/hash, seed, and budgets;
- the source digests needed to reproduce its semantic identity.

TLC-generated records always carry string source/target node IDs. Reviewed
cases may use `null` for those IDs. Adapter IDs and campaign routing are not
producer data and are deliberately absent from `CaseEnvelope`; brokers keep
that mapping in their campaign configuration.

`cases_digest` is SHA-256 over the exact JSONL bytes, including one newline per
record. `record_digest` is SHA-256 over the canonical record with
`record_digest` omitted. `manifest_digest` is computed the same way over the
manifest with `manifest_digest` omitted.

`module_digest` hashes the TLA+ module bytes, `config_digest` hashes the
configuration bytes, and `projection_digest` commits the view, dedupe policy,
and projector implementations. `spec_digest` hashes that three-digest semantic
bundle. The optional nested `source_digests` repeats those values and, when a
DOT graph exists, adds its exact file digest.

## Canonical JSON

Canonical JSON has sorted object keys and no insignificant whitespace.
Mathematical sets become arrays sorted by each member's canonical JSON bytes;
sequences retain their order. Protocol numerics are exact JSON integers;
floats, including integer-valued floats, are rejected. Resource telemetry uses
integer milliseconds and bytes. Raw bytes and filesystem paths use explicit
unpadded base64url wrappers:

```json
{"$bytes_base64url":"..."}
{"$path_bytes_base64url":"..."}
```

## Deterministic bounded selection

Selection policy `stable-hash-stratified` first groups candidates by
`(action, outcome)`. Within each stratum it orders cases by a SHA-256 hash over
the fixed seed, semantic digest, and transition ordinal. It then interleaves
strata by rank, using a stable seeded stratum hash for ties. This gives each
available action/outcome stratum one case before taking a second case from a
stratum, subject to `max_cases`.

The generic outcome classifier uses common `outcome`, `status`, `result`,
`kind`, or `code` fields and otherwise classifies the changed-field shape.
Pass `--outcome-projector module:function` when a program has a stronger
semantic outcome vocabulary.

If candidates exceed `max_cases`, the run is complete and reports
`budget_outcome.type: bounded_selection`; the manifest accounts for both the
full candidate count and the selected count. This is intentional deterministic
selection, not silent truncation.

## Hard failure budgets

`max_output_bytes`, `max_rss_mib`, and `max_seconds` are hard failure budgets.
A breach:

1. removes the partial JSONL stream and any stale `cases.jsonl` or `cases.py`;
2. writes `complete: false`, `status: incomplete`, and
   `budget_outcome.type: budget_exceeded`;
3. identifies the budget, limit, observed value, and stage;
4. exits the CLI with status 2.

An incomplete manifest never carries a `cases_digest`, and no case stream
survives that could be mistaken for conformance evidence. Output-byte
accounting includes the complete manifest plus JSONL stream. The small typed
incomplete manifest is always retained so a byte-budget failure remains
diagnosable.

`max_cases` is enforced before emission by deterministic selection. Invalid
non-positive budget values are rejected rather than reinterpreted.

## Legacy compatibility

`--format legacy-python` preserves the existing generated package containing
`cases.py`, types, doubles, and validators. Use it only for deliberately
bounded graphs. The legacy parser now reads the DOT file line by line, but its
in-memory edge/case package behavior is otherwise unchanged.
