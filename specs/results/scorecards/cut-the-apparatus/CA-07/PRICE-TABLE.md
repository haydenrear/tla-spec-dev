# `CA-07` price table

**`GOAL-apparatus-cut`'s `expected_effect` for this ticket:** *"A SMALL
INCREASE IS EXPECTED AND ACCEPTED — one action or one conformance case. Price
it; it is counted against the goal like everything else."*

**This is one conformance case and one generator function.**

---

## 1. Additions, per surface, never combined

| surface | `14fbb10` (epic tip) | this branch | delta |
|---|---:|---:|---:|
| `scripts/` | 26,756 | 26,837 | **+81** |
| `examples/validation/` | 14,854 | 14,854 | **0** |
| `scripts/` + `examples/validation/` (the goal's command) | 41,610 | 41,691 | **+81** |
| `tests/` | 30,738 | 30,993 | **+255** |
| **card**, `serve \| wc -c` | 6,281 | **6,281** | **0** |
| **card digest** | `sha256:2d7d4a0506d9b259` | `sha256:2d7d4a0506d9b259` | unchanged |

Command, verbatim from the goal:

```bash
find scripts examples/validation -name '*.py' -not -path '*/__pycache__/*' | xargs wc -l | tail -1
```

**The card and the apparatus are never reported as one number**, and neither
figure is quoted without its surface.

## 2. What each addition bought, and the finding that justifies it

Clause (b) of `GOAL-apparatus-cut` requires every change to name the finding
behind it. **These are additions rather than deletions, so clause (b) is
applied in the same spirit: nothing here is justified by taste.**

| lines | where | what | finding |
|---:|---|---|---|
| **62** | `scripts/generate_cases_from_tlc_dump.py` | `declared_param_names` — reads an action's declared argument names out of its own marker record, and a docstring that now matches its code | `CA-06-DF-02`, `CA-07-DF-07` |
| **11** | same, cross-check block | remap declared → formal before comparing key sets, plus the comment naming why the check was vacuous | `CA-06-DF-02`, second face — **and these 11 are protected by nothing, `CA-07-DF-05`** |
| **7** | same, emission block | emit the declared names, plus its comment | `CA-06-DF-02` |
| **1** | same, line 3200 | a line-number citation repointed, twice — `1078-1079` → `1129-1130` → `1139-1140` | `CA-07-DF-04` |
| **255** | `tests/test_negative_corpus_adapter_conformance.py` | the regression: 5 cases, 3 red without the **emission** fix, **0 red without the cross-check fix** | `CA-06-DF-02`, `CA-07-DF-05` |

**No deletions.** Nothing was removed, so nothing has to be priced for what the
tree can no longer do.

## 3. What the tree can now do that it could not

Stated as an addition's mirror image, because a price table that only counts
lines is half a table.

- **`--negative-cases` produces executable cases on a model that declares an
  action marker.** Before: 0 of 11 executed on `examples/distributed_history`.
  After: 11 of 11 executed. *(They still fail — `CA-07-DF-02`. The gain is
  execution, not a green run, and §3 of `RESULTS.md` says so at length.)*
- **The negative pass's soundness cross-check runs.** Before: 0 of 141 enabled
  edges re-evaluated on that subject. After: 141, of which 0 disagreed with
  TLC. On `QuotaLedger` it was always 4,028 and still is. **This gain is
  evidenced by a transcript and by no test — `CA-07-DF-05`, and it is why 11
  of the 71 added lines in `scripts/` are ROUTED rather than consumed.**
- **A `KeyError` in this class now fails a named test** instead of an operator's
  ad-hoc run. **This one is genuinely protected**: back the emission fix out and
  the shipped case goes red.

## 4. What did not move, checked rather than assumed

| | |
|---|---|
| the card | 6,281 bytes, `sha256:2d7d4a0506d9b259` — identical |
| `QuotaLedger`'s negative corpus | 118 cases both keyings, `diff -r` clean apart from the scratch path in `case_coverage.json` |
| `examples/validation/` | 0 lines |
| TLA+, `.cfg`, `spec_manifest.yaml`, `case_adapters.toml` | untouched — `direction=zero`, TLC not required |
| the 15 stale manifest citations behind three baseline reds | identical before and after this branch's edit, checked by re-running the test on both trees |
