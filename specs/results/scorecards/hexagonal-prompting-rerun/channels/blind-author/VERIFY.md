# VERIFY — proof for every shipped mutant

**No forbidden file was opened.** Disclosure, in the same spirit as both
artifacts' NOTES: I ran `ls -la examples/validation/ab/` before I knew what was
in it, so I saw the *names* `seeded_faults.toml`, `check_catalogue.py`,
`README.md`, `reference/`, `eval/`, `scorecard_shape/`, `arm_a/`, `arm_b/`.
I opened none of them. I read exactly these files in the repository:
`examples/validation/ab/FEATURE.md`, `model/QuotaLedger.tla`,
`model/QuotaLedger.cfg`, `model/spec_manifest.yaml`,
`tests/test_behavior.py` — plus everything inside the two implementation
directories. When running the shared suite I always set `QUOTA_LEDGER_DIR` to a
throwaway copy of an artifact, so the suite never fell back to its default
`reference/`.

## How this was checked

`./verify.py` is the harness; `./observations.py` holds the drivers;
`./report.json` is its raw output. It does, for all 30 mutants:

1. counts `find` in the target file **on raw bytes** and requires exactly 1;
2. applies the replacement once, then applies the inverse replacement once, and
   requires the result to be **byte-identical** to the original;
3. `ast.parse`s the mutated bytes;
4. runs the mutant's named driver against a **clean copy** and a **mutated
   copy** of the tree, in separate subprocesses with `PYTHONDONTWRITEBYTECODE`,
   and requires the two JSON blobs to **differ**;
5. re-hashes the clean throwaway copy against the artifact.

Both implementation directories are SHA-256 hashed before and after the whole
run. Every apply happens inside `./work/`, never in the artifacts.

```
$ python verify.py
... 32 rows ...
failures: 0   artifacts untouched: True
```

`artifacts_untouched: true` in `report.json` is the statement that
`/…/blind/artifact_P` and `/…/blind/artifact_Q` are byte-for-byte what they
were before I started.

## Result table

`occ` = occurrences of `find`. `rev` = apply-then-revert byte-identical.
`parse` = mutated file parses. `sep` = a driver separated clean from mutated.
`shared suite` = what the hand-written `tests/test_behavior.py` says about the
mutated tree (informational — it is not part of the pass criteria).

| mutant | class | occ | rev | parse | sep | shared suite |
|---|---|---|---|---|---|---|
| BA-P01 | guard_order_inversion | 1 | ok | ok | ok | **28 passed (survives)** |
| BA-P02 | guard_boundary_shift | 1 | ok | ok | ok | 2 failed |
| BA-P03 | guard_relaxation | 1 | ok | ok | ok | 2 failed |
| BA-P04 | guard_basis_confusion | 1 | ok | ok | ok | 1 failed |
| BA-P05 | reason_substitution | 1 | ok | ok | ok | 1 failed |
| BA-P06 | effect_misrouted_conservation_preserving | 1 | ok | ok | ok | 2 failed |
| BA-P07 | cross_aspect_write | 1 | ok | ok | ok | 2 failed |
| BA-P08 | durable_content_running_total | 1 | ok | ok | ok | 2 failed |
| BA-P09 | durable_content_close_total | 1 | ok | ok | ok | 3 failed |
| BA-P10 | accumulator_overwrite | 1 | ok | ok | ok | 2 failed |
| BA-P11 | identity_reuse | 1 | ok | ok | ok | **28 passed (survives)** |
| BA-P12 | rejection_not_inert | 1 | ok | ok | ok | 2 failed |
| BA-P13 | append_only_violation | 1 | ok | ok | ok | 5 failed |
| BA-P14 | observation_order_violation | 1 | ok | ok | ok | **28 passed (survives)** |
| BA-P15 | construction_not_empty | 1 | ok | ok | ok | **28 passed (survives)** |
| BA-Q01 | guard_order_inversion | 1 | ok | ok | ok | **28 passed (survives)** |
| BA-Q02 | guard_boundary_shift | 1 | ok | ok | ok | 2 failed |
| BA-Q03 | guard_relaxation | 1 | ok | ok | ok | 2 failed |
| BA-Q04 | guard_basis_confusion | 1 | ok | ok | ok | 1 failed |
| BA-Q05 | reason_substitution | 1 | ok | ok | ok | 1 failed |
| BA-Q06 | effect_misrouted_conservation_preserving | 1 | ok | ok | ok | 2 failed |
| BA-Q07 | cross_aspect_write | 1 | ok | ok | ok | 2 failed |
| BA-Q08 | durable_content_running_total | 1 | ok | ok | ok | 2 failed |
| BA-Q09 | durable_content_close_total | 1 | ok | ok | ok | 3 failed |
| BA-Q10 | accumulator_overwrite | 1 | ok | ok | ok | 2 failed |
| BA-Q11 | identity_reuse | 1 | ok | ok | ok | **28 passed (survives)** |
| BA-Q12 | rejection_not_inert | 1 | ok | ok | ok | **28 passed (survives)** |
| BA-Q13 | append_only_violation | 1 | ok | ok | ok | 5 failed |
| BA-Q14 | observation_order_violation | 1 | ok | ok | ok | **28 passed (survives)** |
| BA-Q15 | construction_not_empty | 1 | ok | ok | ok | **28 passed (survives)** |

Both clean copies: `28 passed`.

**The catalogue is not trivially killed.** 4 of 15 survive the shared
hand-written suite in ONE and 5 of 15 survive it in TWO. Any instrument that
scores above that is doing work the normal suite does not.

## The separating observation, per mutant

Every pair below is `clean` vs `mutated`, produced by the named driver in
`observations.py`, which talks only to `QuotaLedger(quotas, path)` and the five
queries FEATURE.md declares. Nothing here reads a private attribute.

### BA-P01 / BA-Q01 — `C01_guard_order`
`close_tenant("globex")`, then `reserve("globex", 0)`:
- clean: `rejected / tenant_closed`
- mutated: `rejected / amount_not_positive`

Both arms identical. Note the mutant is still a *rejection*, still names a
declared reason, and still changes nothing.

### BA-P02 / BA-Q02 — `C02_boundary`
`reserve("acme", 10)` against a quota of 10:
- clean: `accepted / r1`, available 0, outstanding `["r1"]`
- mutated: `rejected / quota_exceeded`, available 10, outstanding `[]`

### BA-P03 / BA-Q03 — `C03_relaxation`
`reserve("acme", 0)`:
- clean: `rejected / amount_not_positive`, outstanding `[]`
- mutated: `accepted / r1`, outstanding `["r1"]`, available still 10

The state-only half of that observation is identical (`available` is 10 in
both). Only the id set and the reported outcome move — which is the point.

### BA-P04 / BA-Q04 — `C04_basis`
`reserve("acme", 6)` twice against a quota of 10:
- clean: second is `rejected / quota_exceeded`, available 4
- mutated: second is `accepted / r2`, available **-2**, outstanding `["r1","r2"]`

### BA-P05 / BA-Q05 — `C05_reason`
`reserve("nobody", 1)` and `close_tenant("nobody")`:
- clean: both `rejected / unknown_tenant`
- mutated: reserve says `tenant_closed`, close still says `unknown_tenant`

The two commands now contradict each other about the same tenant.

### BA-P06 / BA-Q06 — `C06_release`
`reserve("acme", 3)` then `release(r1)`:
- clean: available 10, committed 0, ledger `[]`
- mutated: available 7, committed 3, ledger `[]`

**R1 still holds in the mutant** (7 + 0 held + 3 = 10). Only R2 is false:
`committed("acme") == 3` with no `COMMIT` line behind it.

### BA-P07 / BA-Q07 — `C07_commit_refund`
`reserve("acme", 3)` then `commit(r1)`:
- clean: available 7, committed 3, ledger `["COMMIT acme 3 3"]`
- mutated: available **10**, committed 3, ledger `["COMMIT acme 3 3"]`

**The ledger line is byte-identical in both.** The whole difference is on a
variable the ledger side does not project.

### BA-P08 / BA-Q08 — `C08_running_total`
Commit 3 then 2 on acme:
- clean: `["COMMIT acme 3 3", "COMMIT acme 2 5"]`, committed 5
- mutated: `["COMMIT acme 3 3", "COMMIT acme 2 2"]`, committed 5

Memory is untouched; the *first* line is identical; exactly one field of the
second line is wrong.

### BA-P09 / BA-Q09 — `C09_close_total`
Commit 3 on acme (quota 10), then close:
- clean: `[..., "CLOSE acme 3"]`
- mutated: `[..., "CLOSE acme 10"]`

### BA-P10 / BA-Q10 — `C10_accumulator`
Commit 3 then 2 on acme:
- clean: committed 5, `["COMMIT acme 3 3", "COMMIT acme 2 5"]`
- mutated: committed **2**, `["COMMIT acme 3 3", "COMMIT acme 2 2"]`

Distinct from BA-x08: there the ledger lied and memory was right; here they
agree with each other on the wrong number, so any check that only compares the
two sides passes.

### BA-P11 / BA-Q11 — `C11_id_reuse`
`reserve → r1`, `commit(r1)`, `reserve` again:
- clean: second id `r2`, outstanding `["r2"]`
- mutated: second id `r1`, outstanding `["r1"]`

### BA-P12 — `C12_rejection_inert`
`reserve("acme", 99)` (refused), then `reserve("acme", 1)`:
- clean: refused `quota_exceeded`; available 9; next `accepted / r1`
- mutated: refused `quota_exceeded`; available **-90**; next **`rejected / quota_exceeded`**

The refused call is reported correctly and has permanently damaged the tenant.

### BA-Q12 — `C12_rejection_inert`
Same input, different damage (TWO does not store `available`):
- clean: next `accepted / r1`, outstanding `["r1"]`
- mutated: next `accepted / r2`, outstanding `["r2"]`

A refused reserve consumed id `r1`.

### BA-P13 / BA-Q13 — `C13_append_only`
Two commits, then read the file itself:
- clean bytes: `"COMMIT acme 3 3\nCOMMIT acme 2 5\n"`
- mutated bytes: `"COMMIT acme 2 5\n"`

### BA-P14 / BA-Q14 — `C14_outstanding_order`
Twelve live reservations:
- clean: `r1 … r12`
- mutated: `r1, r10, r11, r12, r2, r3, …, r9`

Identical for the first nine allocations, in both arms.

### BA-P15 / BA-Q15 — `C15_construction`
Write `"COMMIT acme 5 5\nCLOSE globex 2\n"` to the path, *then* construct:
- clean: `ledger_lines() == []`, file emptied
- mutated: `ledger_lines() == ["COMMIT acme 5 5", "CLOSE globex 2"]`,
  while `committed("acme") == 0` and `is_closed("globex") is False`

R2 and R3 are false before a single command has run.

## Equivalent mutants

None shipped. Everything I could not separate was dropped and is written up in
`REJECTED.md` with the evidence of the attempt (`./rejects.py`,
`./rejects_report.json`) — including which drivers, a 600-step randomized
sweep, and the shared suite all failed to tell it from correct behavior.
