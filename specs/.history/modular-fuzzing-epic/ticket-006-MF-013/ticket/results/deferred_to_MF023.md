# MF-013 — validations DEFERRED to MF-023 (#30)

Epic-wide policy, owner direction 2026-07-18: build the mechanism, do not run
generated spec cases. This ticket is unusually execution-shaped — an effect
conformance sweep only has meaning over a real corpus — so the split between
what was validated and what was deferred is spelled out precisely.

## Validated HERE (mechanism, not corpus)

| Surface | How |
|---|---|
| Effect declaration schema | 12 unit tests: required `type`/`target`, unobservable types rejected, unknown port in an action rejected, absent block is empty not an error |
| Sandbox observation | 8 unit tests: fs write via `Path` and via `open`, delete, process spawn, fake transport, reads are NOT effects, escape outside the sandbox root still observed, patches restored on exit and on exception |
| Diff — undeclared FAILS | 5 unit tests + 3 runner tests + 1 spec-unit adapter test |
| Diff — nothing suppresses | 7 unit tests + 4 runner tests + 3 spec-unit adapter tests (the inverse test) |
| Dead model surface | 4 unit tests + 1 runner test |
| Report as evidence | 2 unit tests + 3 CLI tests |
| CLI exit-code contract | 7 tests: 0 clean / 1 findings / 2 malformed-or-absent declarations |
| Shipped manifest block | 2 tests asserting it parses and carries no suppression keys |
| Whole-model behavior | TLC, 13 invariants; `specWorkflow`; `cliWorkflow`; 279 repository unit tests |

Validation used unit tests, synthetic adapters (`tests/effect_adapter_fixtures.py`),
fixtures, and the repository test graphs — none of which depend on a generated
case corpus.

## DEFERRED to MF-023 — what it must exercise

1. **Case generation over the reachable state graph.** Not run. The MF-011 gate
   refuses it against this undecomposed module (`C1 has 7 variables` /
   `13 actions`), which is a TRUE finding, not a miscalibration. Not worked
   around: no `--allow-over-budget`, no budget renegotiation.

2. **The effect-conformance sweep over a real corpus.** The per-case diff has
   never run against generated cases. `execute_cases_in_batch` is proven by
   synthetic adapters only.

3. **The distilled-corpus run** and **the mutation kill test.** Neither run;
   MF-016's kill-rate evidence does not exist yet.

4. **REQUIRED: verify or remove the five shipped port declarations.** This is
   the concrete debt this ticket hands over.

   `specs/current/spec_manifest.yaml` declares five ports — `spec_tree`,
   `evidence_report`, `cli_artifact`, `tlc_process`, `test_process`. They
   describe effects the CLI genuinely emits, but **not one has been observed by
   a case**, because no corpus was run. Run today they report as dead model
   surface (see `effect_conformance_declared.json`, verdict `dead_surface`,
   exit 1 — this is the harness working correctly on an empty observation set,
   not a passing check).

   Under the amended doctrine each of the five must be **observed by a case or
   removed**. Prose does not resolve it, and this file is not an exemption —
   it is the handover record. MF-023 must run the corpus and then either
   confirm each port or delete it.

## Fixed here, reported because it was silently degrading a gate

**`specs/current/spec_manifest.yaml` was invalid YAML at the epic tip.**
Pre-existing, inherited from MF-015, verified against
`origin/epic/modular-fuzzing` and not introduced by this ticket. Line 76:

```yaml
  next:
    - MF-023 (...) owns every
      deferred spec-case run for this ticket: case generation over the
```

The unquoted `ticket: case` makes YAML read the line as a mapping key inside a
block sequence, which is a scanner error. Two consequences, both bad:

1. **`analyze complexity` silently fell back to default budgets** on every run,
   emitting `warning: no readable spec manifest ... using documented default
   budgets`. The gate was reading defaults, not the declared manifest. The
   values happen to be identical, so no verdict in this epic was wrong — but
   the gate was not reading what it claimed to read, and would not have noticed
   a deliberately raised budget. This is precisely the "conditional check that
   silently disables itself when its input is absent" that rule 5 forbids, and
   it was firing while the input was present and readable.
2. **`close ticket` could not parse the manifest at all**, which is how it was
   found — MF-013's close was the first to hit the strict parse path.

Repaired by quoting the scalar (`- >-`), wording unchanged. Both ticket-local
manifests now parse, and `analyze complexity` reports
`source: .../spec_manifest.yaml` with no fallback warning.

**For MF-023:** the residue absorbed into it is confirming that overrides are
explicit, visible, and never the default path. A fallback that fires while the
manifest is present and readable is exactly that failure mode. Recommend the
fallback be made to distinguish *absent* from *unparseable*, and to fail loudly
on the latter rather than substituting defaults — a malformed budgets file is
not the same as no budgets file.
