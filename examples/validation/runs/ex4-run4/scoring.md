# ex4 run 4 — the mutant catalogue and the case-module path, re-run (RP-02, RP-03)

Run date 2026-07-30, EV-03. **Mechanical run: no agent.** Scored against the
SAME committed predictions in `../../PREDICTIONS.md`. Two arms in one record:
aim 1 (both fault catalogues, both declared adapter mappings, plus the
hand-written suite) and the case-module path end to end.

Interpreter pinned: `/…/scratchpad/ev03/venv/bin/python` — CPython **3.13.14**
with `pytest`, `pyyaml` and `tomllib` in one place. Round 1 could not do this
(EV-02-DF-05); see "EV-02-DF-05 re-scored" below.

Corpus `gen1`, generated fresh from `Pipeline.tla` in this worktree.
`PYTHONDONTWRITEBYTECODE=1` throughout, and `__pycache__` purged around every
execution, so no run can import a cached mutant.

## The control (MF-016 — without it "killed" means nothing)

| instrument | mapping | cases | exit | verdict |
|---|---|---|---|---|
| **ARM A — corpus alone** | `case_adapters_corpus_only.toml` (`silent_ledger_store_provider`) | 330 | **0** | GREEN |
| **ARM B — corpus + content provider** | `case_adapters.toml` (`ledger_store_provider`) | 330 | **0** | GREEN |
| **pytest** — the hand-written suite | `tests/` | 8 tests | **0** | GREEN |

All three green on the unmutated program before any mutant was applied.
**A1-P1 PASS.** Every kill below is admissible.

## Catalogue 1 — `seeded_faults.toml`, the EV-01 answer key

| id | fault class | ARM A | A points | A detector | ARM B | B points | B detector | round 1 | round 2 |
|---|---|---|---|---|---|---|---|---|---|
| F1 | wrong value | **KILLED** | 44 | `tla_projected_state` | **KILLED** | 88 | `provider_content_assertion` + `tla_projected_state` | killed/killed | **same** |
| F2 | wrong field | **KILLED** | 88 | `tla_output` | **KILLED** | 88 | `tla_output` | killed/killed | **same** |
| F3 | off-by-one (durable) | **SURVIVED** | 0 | — | **KILLED** | 44 | `provider_content_assertion` | survived/killed | **same** |
| F4 | wrong status | **KILLED** | 22 | `tla_output` | **KILLED** | 22 | `tla_output` | killed/killed | **same** |
| F5 | swallowed error | **SURVIVED** | 0 | — | **KILLED** | 44 | `provider_content_assertion` | survived/killed | **same** |
| F6 | off-by-one (in-memory) | **KILLED** | 15 | `tla_output` | **KILLED** | 15 | `tla_output` | killed/killed | **same** |

**ARM A: 4 of 6. ARM B: 6 of 6.** Identical to round 1 — every kill, every
survivor, every detector, and every point count.

- **A1-P2 / A1-P3 / A1-P4 / A1-P5 / A1-P6 PASS**, unchanged.
- **A1-P7 stays SUPERSEDED**, as `seeded_faults.toml`'s RP-02 amendment already
  records: the wrong-item class *was* killable, on the pre-fix instrument as
  well as the post-fix one. This run did not re-seed it; RP-02's measurement
  stands and no answer-key row was edited.

## Catalogue 2 — the reconstructed 12-mutant catalogue (RP-02's `mutants.toml`)

This is the round-1 blind agent's catalogue, reconstructed by RP-02 from the
published class table because the original was applied in place and never
written down (**EV-02-PROTO-02**). Shipping it as a file is what makes this
column re-scorable at all.

| id | class | ARM A | ARM B | pytest |
|---|---|---|---|---|
| M1 | guard relaxation | SURVIVED | SURVIVED | **KILLED** |
| M2 | guard relaxation | SURVIVED | SURVIVED | **KILLED** |
| M3 | guard relaxation | SURVIVED | SURVIVED | **KILLED** |
| M4 | equivalent | SURVIVED | SURVIVED | SURVIVED |
| M5 | wrong write | **KILLED** | **KILLED** | **KILLED** |
| M6 | wrong write | **KILLED** | **KILLED** | **KILLED** |
| M7 | wrong write | **KILLED** | **KILLED** | SURVIVED |
| M8 | wrong write | **KILLED** | **KILLED** | **KILLED** |
| M9 | ordering | SURVIVED | SURVIVED | SURVIVED |
| M10 | wrong write, durable | SURVIVED | **KILLED** | SURVIVED |
| M11 | ordering | SURVIVED | SURVIVED | SURVIVED |
| M12 | ordering | SURVIVED | SURVIVED | SURVIVED |

Per class, per arm:

| class | seeded | ARM A | ARM B | pytest | round 1 (view corpus) |
|---|---|---|---|---|---|
| guard relaxation | 3 | **0/3** | **0/3** | **3/3** | 0/3 corpus, 3/3 pytest |
| ordering | 3 | **0/3** | **0/3** | **0/3** | 0/3 everywhere |
| wrong write (in-memory) | 4 | **4/4** | **4/4** | 3/4 | 4/4 (M7 missed by pytest) |
| wrong write (durable) | 1 | **0/1** | **1/1** | 0/1 | corpus killed, pytest missed |
| equivalent | 1 | n/a | n/a | n/a | n/a |

## THE HONEST NEGATIVE, and it is the headline of this arm

**The mutant matrix did not move a single cell between round 1 and round 2**,
on either catalogue, on either arm, on the pytest column.

RP-02 was a real repair and it is measurable elsewhere: parameter recovery went
0 of 5 → **5 of 5**, all 330 cases now carry `params={'i': 'i1'}` or `'i2'`
where every one previously carried `UNCHECKED`, the adapter no longer touches
`case.after`, and the audit is rendered from the corpus it audits. The corpus
fingerprint moved from `33e07e0de…` to `944189052623960aea…` — a legitimate,
recorded content change and **not** a determinism failure (see run 5).

**None of that killed one additional bug.** Guard relaxation is still 0 of 3 on
both arms. Ordering is still 0 of 3 everywhere.

Attribute it per mechanism, because "the toolchain catches more bugs now" would
be false here:

- **What RP-02 removed** was oracle leakage — the adapter reading its argument
  out of the answer key. That was real, it is gone, and it makes the corpus
  auditable.
- **What RP-02 did not remove**, because it cannot, is the structural half: a
  TLC state graph has **no edge for a transition that did not fire**, so a
  generated corpus contains no rejected inputs. RP-02 counted it: 330 of 330
  recovered arguments are arguments the guard ACCEPTS, 0 are rejected inputs,
  and 220 refusable argument/before-state pairs exist in the state space that
  the generator can never emit.
- EV-02 named two compounding causes for the unkillable guard class. **Cause 2
  is gone and the class did not move, so the whole of the remaining failure is
  attributable to cause 1.** Round 1's own write-up ("compounded by the adapter
  recovering the action argument from the after-state") named parameter recovery
  as part of the reason guard relaxation is unkillable. **That conclusion is now
  falsified**, and `NEXT-EPIC.md` is corrected accordingly.

## The case-module path, end to end (RP-03)

`artifacts/case_modules_worked_example.sh` runs `references/case_modules.md`,
"Worked example: an internal-only project", **verbatim**. Output:
`artifacts/case_modules_worked_example.txt`.

| step | round 1 | round 2 |
|---|---|---|
| generate from `specs/case_modules/` **in place**, no copying | **exit 150**, 30-line TLC `AbortException` (EV-02-DF-02) | **exit 0** |
| view corpus | 330 cases / 121 states | **330 / 121** |
| slice `Scenario_DeliveryPath` | 50 cases / 25 states (via copy-and-delete) | **50 / 25**, in place |
| Given `Scenario_RecordAfterDelivery` | 6 cases / 8 states (via copy-and-delete) | **6 / 8**, in place |
| `case_modules.py validate` | exit 0 | **exit 0** |
| `case_modules.py coverage` | `UNCOVERED: none` | **`UNCOVERED: none`** |
| recovered arguments, view corpus | 330/330 (post-RP-02) | **330/330** |
| recovered arguments, slice | **0/50** (RP-03's adjacent finding) | **50/50** |
| recovered arguments, Given | **0/6** | **6/6** |
| **execute the Given's corpus** against unchanged adapters | not possible | **`executed 6 cases in batch`, exit 0** |

**EV-02-DF-02 is CLOSED and measured.** The checked-in modules are reproducible
where they live; `cp`/`rm` is gone from the fixture README. The counts
reproduce round 1's exactly, so the fix changed the mechanism and not the
corpus.

**A2-P1 PASS** (14 lines → 50 cases; 22 lines → 6 cases; view 330 — reproduced).
**A2-P3 PASS, and now it is complete**: round 1 could show the corpora
*generate*; round 2 shows a case-module corpus **executes** against the
project's own adapters with no adapter change. That is the half round 1 could
not reach, and the cause was RP-03's adjacent find — recipes were built from a
case module's own text, which declares no actions, so its corpus carried no
arguments and the adapters refused it case by case.

**DP-3 PASS (tool side), unchanged.** `coverage` still prints, unprompted, that
cross-aspect interleaving is not in the table. Union of the two aspects = 56;
the view = 330; this record does not report 56 as coverage of 330.

### CM-F5 — status: **STILL OPEN, and worse than RP-03 filed it**

Step 6 of the worked example, run verbatim:

```
$ run_generated_case_adapters.py <slice corpus> --mapping specs/program_model/case_adapters.toml …
ERROR: invalid semantic effect provider configuration: provider configured for
       semantic effect port(s) not required by any selected case: LedgerStorePort
exit 1
```

**CM-F5 holds exactly as RP-03 published it.** The `Scenario_DeliveryPath`
slice excludes `Record`, the only action touching `LedgerStorePort`, so the
project's own mapping refuses its corpus. The cheapest outside-in artifact — a
slice, the one form writable from action names alone — is the one that cannot
run end to end. The Given, which cannot be written from outside, runs fine.

**New measurement this run (step 6b), which RP-03's write-up does not contain.**
RP-03 says "the only workaround today is a second mapping file with the provider
removed". This fixture *ships* a second mapping — `case_adapters_corpus_only.toml`,
ARM A — and it **also refuses**, with the identical error, because it also binds
a `LedgerStorePort` provider (a silent one). So on the shipped fixture there is
**no mapping under which the slice's corpus can execute at all**; the workaround
requires authoring a third mapping that exists nowhere. Filed as **EV-03-DF-02**,
a sharpening of CM-F5, not a new defect.

## EV-02-DF-05 (interpreter ambiguity) — re-scored: **STILL OPEN**

Measured again on this machine: `/usr/bin/python3` (3.9.6) has `yaml`, no
`pytest`, no `tomllib`; `/opt/homebrew/bin/python3` (3.14.6) has `tomllib`, no
`yaml`, no `pytest`; `/Library/Frameworks/…/3.10/bin/python3` has `yaml` and
`pytest` but no `tomllib`. **No `python3` on PATH carries all three.** This
ticket solved it by building a pinned venv, which is exactly the step no
document tells anyone to take. RP-03 fixed the `--out` and `--import-root`
frictions and the internal-view worked example; it did not pin an interpreter,
and neither README states a requirement. Still open.

Not a determinism problem: the toolchain's YAML fallback parser and PyYAML were
checked to produce byte-identical JSON on this fixture before any measurement.

## Fixture integrity (X-P4)

`check_twins.py` exit 0 before and after; all five hashes match.
`git status --porcelain examples/validation/ex4_pipeline_coherent` empty after
the whole 38-execution matrix and after the worked example. No answer key,
`PREDICTIONS.md`, or `seeded_faults.toml` was edited. **X-P4 PASS.**

Repository suite: **954 passed, 0 failed** (`uv run --with pytest --with pyyaml
-m pytest tests -q`), matching the pin at the epic tip.

## Evidence-integrity note (EV-03-DF-06)

`.gitignore` line 40 is `*.log`, so an eval artifact written with that extension
is silently dropped from the repository while its scoring record cites it.
**Round 1 lost 15 named artifacts this way** — `../ex4-run1/scoring.md` lists
"14 mutant/control logs (both arms)" and `artifacts/inplace.log` (the EV-02-DF-02
reproduction) under Artifacts, and `git ls-tree -r 3af9e59` shows nine committed
files in that directory, none of them a log. The numbers survive because
`kill_matrix.json` and the harness were committed; the primary outputs did not.
This run writes every execution artifact as `.txt` and verified with
`git ls-files` that no path it names is missing. **Filed as EV-03-DF-06, not
fixed** — `.gitignore` is outside this ticket's keys, and round 1's sealed record
must not be edited by a later ticket.

## Artifacts

`artifacts/kill_matrix_round2.py` (the harness — both catalogues, both arms,
the pytest column, green control first),
`artifacts/kill_matrix.json` (every cell, with detectors, point counts,
failing-case sets and normalized stdout digests),
`artifacts/logs/` (the three control runs, saved as `.txt` -- see the note below),
`artifacts/case_modules_worked_example.sh` / `.txt`,
`artifacts/ex4_reflexion.txt` / `.json` / `ex4_descriptor.txt` (the coherent
control for AC-P1).
