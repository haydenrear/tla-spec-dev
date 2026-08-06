# FI-05 — the produced-code statistics reach a PROMPT, and the dispatched prompt is preserved

Measured at `51fe73d` (epic tip when this ticket branched). Nothing here is a
measurement of an arm; this ticket ships instruments and their demonstrations.

## 1. The figures now reach a prompt

`grep -rn code_complexity prompts/` was **empty** at the parent. It is not now:

| file | what it does |
|---|---|
| `prompts/produced_code_reading.md` | the ask. Dispatched AFTER a tree exists, with the report pasted underneath |
| `prompts/hexagonal_implementation.md` | points at it, **outside** `HEXAGONAL-ASK:BEGIN/END` |
| `references/complexity_intuition.md` | §"Where the figures get READ" points back |

The ask asks four questions — where the outside world ended up, what sits beside
it, what the instrument undercounted, which figure was a surprise — and refuses
a score, a delta, a direction and a boundary. Asserted by
`tests/test_produced_code_prompt.py` (43 tests).

**Nothing gates on the figures.** There is deliberately no script that runs the
instrument and renders the prompt, because that script would be the toolchain's
first consumer of a thermometer. The scan that says so is AST-based (import or
invocation), and it ships its own red and green inputs.

## 2. The sealed length match did not move

The produced-code ask is a **separate dispatch**, not a paragraph inside the
hexagonal ask, so PA-01's sealed arm B = 105 unique content lines is untouched.
`test_the_sealed_length_match_is_untouched` and
`test_the_new_section_is_outside_the_sealed_ask_block` assert it.

## 3. The dispatched prompt is preserved — PA-06-DF-10

`examples/validation/ab/dispatch_record.py` records the exact bytes sent, the
digest of the on-disk source at dispatch time, and the size of the delta;
`verify` recomputes all three; `check_catalogue.py --arms --dispatch-dir`
measures the artifact rather than the source.

**The historical demonstration, one harness over two real inputs:**

| | measured ON DISK | measured AS DISPATCHED |
|---|---|---|
| arm C distinct lines | 146 | 160 |
| unique content vs arm A | 109 | **124** |
| ratio to arm B's 105 | 1.038 (+3.8%) | **1.181 (+18.1%)** |
| inside ±10% | yes | **NO** |
| architectural vocabulary | 0 of 109 | **4 of 124** |
| `check_arms` result | **green** | **RED, 2 problems** |

The recorded row is `provenance = "reconstruction"` and is printed as such:
these bytes were rebuilt by PA-06's adversarial channel, not captured at
dispatch. Arms A and B have no dispatch evidence at all — **FI-05-DF-02**.

**Synthetic demonstrations (R1), `dispatch_record.py demonstrate`:** four
mutations of a self-consistent record, each required to go RED with a distinct
reason — artifact edited, source changed after dispatch, declared delta drifted,
artifact missing. All four red; the unmutated record green in each run.

## 4. The sealing procedure — PA-06-DF-03

`examples/validation/check_prediction_seal.py` reads a predictions file before it
is sealed and reports every no-kill prediction whose exact cell already appears
as a KILL in a record that **pre-dates the seal** (its commit is an ancestor of
the sealing commit), plus any `[[retired_control]]` covering the same mutant.

**Demonstrated failing input, on the real record:**

```
$ python3 examples/validation/check_prediction_seal.py examples/validation/PREDICTIONS-PA.md
ALREADY MEASURED:
  N05 (M09 x corpus-neg, corpus-neg-exact, corpus-slice-led, corpus-slice-res,
       corpus-whole): the record ALREADY contained a kill for this cell when the
       file was sealed:
        M09-negative-control-ledger-order / corpus-slice-led = KILLED (16 records)
        M09-negative-control-ledger-order / corpus-whole     = KILLED (18 records)
        M09-negative-control-ledger-order was RETIRED as a negative control ...
UNPARSED:
  N03, N07 -- predict no kill, name no lookupable subject. NOT CHECKED.
NOT SEALABLE AS WRITTEN.                                              exit 1
```

Remove N05's section and the same command is clean, so the red is attributable
to that row and not to the file. `--demonstrate` runs both.

**Coverage is 1 of 3, and is reported as such** — FI-05-DF-03. `PREDICTIONS-PA.md`
is sealed and was not amended.

## 5. Acceptance

Reconciled onto the epic tip `31123dc` (after FI-04 merged) and re-run there:

```
uv run --with pytest --with pyyaml python -m pytest tests -q
1335 passed in 351.46s          # 0 failed
```

**The pre-existing red is gone.** On the branch as first written, acceptance was
`1 failed, 1288 passed`, the failure being
`test_nothing_executable_reads_this_instrument` — PA-06-DF-05, the substring
tripwire that could not tell a prose mention from a gate. **FI-02 replaced it**
with an AST scanner (`executable_references` / `gating_uses`), and the suite is
green.

### What the reconcile changed in this ticket, and why

FI-02's new scanner is repository-wide for gating, and it **flagged this
ticket's own test file** — `test_produced_code_prompt.py` compared figures it
had read from `analyze_tree`. That is a real signal, not noise, and it was
answered twice over:

1. **The hand-rolled AST scanner written here was deleted.** FI-02 shipped the
   same analysis, better: docstrings excluded, whole-token match. Two scanners
   drifting apart is the `declaration_executability_rule`'s own shape, so this
   file now imports FI-02's `executable_references` and keeps only what FI-02
   does not cover — `examples/` and `prompts/`, the two trees FI-05 added files
   to, asserted at **zero executable references**, which is stronger than "does
   not gate". Seven self-tests of the private copy went with it (43 tests → 36).
2. **The figure reads were removed rather than exempted.** The prompt's figure
   names and quoted cells are now bound to `references/complexity_intuition.md`
   — itself pinned to a live run by `test_documented_figures_match_shipped_output`
   and `test_recorded_figures_match_a_live_run` — so the chain instrument →
   reference page → prompt stays executable end to end while **the file
   arranging for nothing to consume the thermometer stopped being a consumer of
   it.**

What remains are 23 comparisons of the instrument's **name**, which every test
about an instrument makes by definition. `tests/test_produced_code_prompt.py` is
therefore added to `GATING_SCAN_EXEMPT` as its third entry — and on a **narrower
ground than the other two, bounded by a test**:
`test_the_third_exemption_never_reads_a_figure` requires every executable
reference in it to be a name token, never an import and never an invocation, and
requires its output never to be read. A figure cannot be reached without one of
those, so a file with neither cannot gate on a figure. Add a figure read and
that test goes red instead of the exemption quietly widening.

### Parent-commit evidence

`git archive 51fe73d` into a clean tree, with the three new test files copied in
(measured before the reconcile, on the branch point):

| module | on parent | here |
|---|---|---|
| `test_produced_code_prompt.py` | **32 failed**, 11 passed | 36 passed |
| `test_dispatch_record.py` | **collection error** — `dispatch_record` does not exist | 16 passed |
| `test_prediction_seal.py` | **collection error** — `check_prediction_seal` does not exist | 14 passed |

The 11 that passed on the parent were guards on properties that must NOT have
changed. Seven of them were the private scanner's self-tests and are now gone;
what is left is the sealed 105-line length match and the instrument's exit-0
behaviour, green on both sides because that is what they assert.

## 5b. Registered in FI-02's instrument registry

`FI-04-DF-04`, confirmed again: `test_the_named_instruments_are_all_enumerated`
asserts `required <= enumerated` against a hardcoded list, so it catches a
rename and **cannot** catch an instrument never added. Both of this ticket's
instruments meet the registry's definition — watches a subject, produces a
verdict, returns nonzero — and both are registered by hand.

| row | failing | passing | blind spot |
|---|---|---|---|
| `dispatch-record` | the shipped ports-as-adapters record, staged and tampered → exit 1, `HAS BEEN EDITED` | the same record untouched → exit 0 | **cannot see a dispatch that was never recorded**: an empty evidence dir verifies GREEN |
| `prediction-seal` | the sealed `PREDICTIONS-PA.md` → exit 1, N05 `ALREADY MEASURED` | a fixture whose mutant is in no kill table → exit 0 | **cannot check a prediction naming no mutant and no column**: reported `UNPARSED`, **exit 0** |

Both blind spots are declared with their failure direction named, and **neither
is the safe direction**:

- `dispatch-record`'s is the live state of arms A and B — no row at all, so the
  checker is green about the very thing it exists for (**FI-05-DF-02**, major).
- `prediction-seal`'s is green-looking silence on 2 of the 3 no-kill rows in the
  only real file it has run against (**FI-05-DF-03**).

Registry totals after these rows: **40 enumerated, 5 not-instruments, 35
instruments, 26 with a demonstrated failing input, 9 without, 12 with a
demonstrated blind spot.** `demonstrate.py --only dispatch-record --only
prediction-seal` reports `ok ok ok` for both.

Three paths were added to the rename guard's `required` set — this ticket's two
and FI-04's `divergence.py`, which was registered but never pinned — with the
guard's limit written into its own docstring rather than left implicit.

**No demonstration here is pinned to an unimplemented identifier.** The failing
one for `prediction-seal` is a **sealed** file, byte-frozen by the rule that
produced the finding; the passing and blind-spot ones are synthetic fixtures
under `examples/validation/instruments/fixtures/prediction_seal/`, written
synthetic precisely so they cannot stop demonstrating when somebody measures a
real subject. `dispatch-record`'s are the shipped record and a temporary copy.

## 6. Findings filed, not fixed

| id | severity | what |
|---|---|---|
| FI-05-DF-01 | minor | prediction ids and mutant ids share a namespace, so a prediction about the mutant `N01` cannot be checked by id |
| FI-05-DF-02 | major | only arm C has any recoverable dispatch, and it is a reconstruction; arms A and B have none |
| FI-05-DF-03 | minor | the seal check reaches 1 of the 3 no-kill predictions in the only file it has been run against |

## 7. Goal contribution

- **GOAL-instruments-can-fail** (enabling) — expected: none on its own. Observed:
  as expected. The produced-code instrument gained a reader and gained no
  consumer; `test_nothing_executable_consumes_the_instrument_after_the_prompt_landed`
  is the local signal, executable.
- **GOAL-scorecard-carries-a-delta** (guard) — expected none. Observed none. The
  figures stay in the mechanical block and nothing scores them.
- **GOAL-fixture-can-diverge** (guard) — expected none. Observed none. No arm,
  corpus, catalogue or kill table was touched.
