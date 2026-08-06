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

```
uv run --with pytest --with pyyaml python -m pytest tests -q
1 failed, 1288 passed in 132.75s     # before `close ticket FI-05`
1 failed, 1284 passed in 128.52s     # after; the 4 are the ticket-local
                                     # workflow tests the close removes
```

The one failure is `tests/test_code_complexity.py::test_nothing_executable_reads_this_instrument`
— **PA-06-DF-05**, carried out of the predecessor epic as issue #147, and **red
on the parent commit `51fe73d` too** (verified by `git archive`). It is the
substring-grep tripwire failing on a prose mention inside a closed round's
evidence generator. It was NOT fixed here: a carried finding is not repaired
inline by a ticket measuring something else. The sharper AST-based discrimination
this ticket needed for its own scan ships beside it, with its own red and green
inputs, as evidence of what the filed fix would look like.

### Parent-commit evidence

`git archive 51fe73d` into a clean tree, with the three new test files copied in:

| module | on parent | here |
|---|---|---|
| `test_produced_code_prompt.py` | **32 failed**, 11 passed | 43 passed |
| `test_dispatch_record.py` | **collection error** — `dispatch_record` does not exist | 16 passed |
| `test_prediction_seal.py` | **collection error** — `check_prediction_seal` does not exist | 14 passed |

The 11 that pass on the parent are the guards on properties that must NOT have
changed: the consumer scan's own red/green inputs, the sealed 105-line length
match, and the instrument's exit-0 behaviour. They are green on both sides
because that is what they assert.

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
