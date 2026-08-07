# Evidence packet

The artifact you are scoring is a **toolchain**: a command-line system that
compiles a constrained, annotated TLA+ state-machine specification into Python
spec doubles — generated fakes, ports, validators, Hypothesis strategies, traces
and test-harness integration cases — together with the validation harness that
measures whether those generated artifacts catch faults.

It is presented to you at **two commits**, and the change between them is what
this packet is about.

| | commit | staged at |
|---|---|---|
| **before** | `3f58aca` | `<TREE_ROOT>/before/` |
| **after** | `f49a1c9` | `<TREE_ROOT>/after/` |

Both trees are complete working checkouts. You may read anything in them, copy
either to a scratch directory, seed your own faults and run them.

---

## 1. What the trees are, and what was taken out of them

**The staged trees are REDACTED, and this section is the whole redaction.** The
subject of this round is a repository, so the ordinary blinding — *"here is a
directory, do not read the rest of the repo"* — does not reach it: you have to
read the source, the tests and the harness, and the round's own bookkeeping
lives in the same tree. Rather than forbid paths and trust you not to open them,
the following were **deleted from both trees**:

```
specs/.history/                       specs/desired_program_model/
specs/results/scorecards/             specs/tickets/
specs/results/complexity_ledger.json  specs/results/skill_feedback.md
specs/results/deferred_findings_*.yaml
references/eval_scorecard.md          references/architecture_advice.md
references/hexagonal_prompting.md
examples/validation/PREDICTIONS*.md
*EPIC*.md   NEXT-EPIC.md   EPIC-HANDOFF.md   PORTS-AS-ADAPTERS-STARTER-PROMPT.md
```

**This means parts of the suite cannot pass in these trees.** Nodes that read
those paths will error or fail. The unredacted suite results are given in §6 as
recorded evidence, measured on the real checkouts. **Do not read a redaction
failure as a defect in the artifact** — and if you cannot tell which is which
for some node, say so rather than guessing.

**Four files that state a past evaluation result were NOT removed, because they
are part of the artifact and deleting them would change what you are scoring.**
They are named here so you can recognise them:

- `tests/test_card_has_one_home.py` — carries, twice, a sentence asserting how one
  scored dimension came out across a run of past evaluations. It is **fixture
  data** for a test asserting that a citation of a score is not a statement of a
  rubric.
- `tests/test_score_tools.py` — carries checker messages naming scores.
- `examples/validation/ab/reference_ports/README.md` and `journal_memory.py` —
  each carry one clause asserting a past score on a different artifact.

Those sentences are **about other artifacts in other rounds**, they are not
findings about the trees you are scoring, and they are not the rubric you are
scoring against. **They are named rather than quoted here on purpose: this packet
will not repeat a past result to you in the course of warning you about it.** If
you read them, disclose it and say whether it moved anything. A disclosed leak is
recorded and is never grounds to discard a card.

---

## 2. What changed between the two trees

`git diff --stat 3f58aca f49a1c9 -- scripts tests examples references`:

```
 examples/validation/PREDICTIONS-SM.md              | 260 +++++++    (redacted from your trees)
 examples/validation/gap_mutants/gap_mutants.toml   | 585 +++++++++++++
 examples/validation/gap_mutants/run_gap_mutants.py | 633 +++++++++++++
 examples/validation/instruments/demonstrate.py     | 313 +++++++-
 examples/validation/instruments/instruments.toml   | 832 +++++++++++++++--
 examples/validation/scorecards/score_tools.py      | 460 ++++++++--
 references/case_modules.md                         | 123 ++-
 references/eval_scorecard.md                       | 170 ++++-     (redacted from your trees)
 references/hexagonal_prompting.md                  |   2 +-        (redacted from your trees)
 scripts/effect_conformance.py                      |   2 +-
 scripts/run_generated_case_adapters.py             | 318 +------
 tests/test_card_has_one_home.py                    | 428 ++++++++
 tests/test_gap_mutants.py                          | 486 ++++++++
 tests/test_instrument_demonstrations.py            | 314 +++++++-
 tests/test_port_adapter_binding.py                 | 462 ---------
 tests/test_ports_binding_removed.py                | 220 ++++++
 tests/test_score_tools.py                          | 360 ++++++-
 17 files changed, 4948 insertions(+), 1020 deletions(-)
```

Four changes account for it. **They are described here neutrally; whether any of
them is an improvement is yours to decide, not this packet's to assert.**

### (a) A port-binding mechanism was deleted from the case-adapter runner

`scripts/run_generated_case_adapters.py` lost twelve pieces of a
`[ports."Component.Name"]` binding facility: `AdapterMapping.binds/.port/.fake`,
the `[ports.*]` branch of `load_mappings`, the `[ports.` branch of the fallback
TOML reader, `_port_declaration_type`, `port_case_label`, `load_declared_ports`,
`port_bindings`, `apply_wiring`, `render_port_binding_report`, the
`port-fake-real-swap` half of `render_oracle_statement`, the port-first
precedence in `adapter_for_case`, and the `--wiring` / `--port-manifest` flags.

`tests/test_port_adapter_binding.py` (462 lines, 21 collected nodes) was deleted
whole; `tests/test_ports_binding_removed.py` (220 lines, 14 nodes) was added.

**What the deleted facility claimed to do**, from the documentation at the before
commit: with such a table declaring `adapter` and `fake`, `--wiring fake` swapped
the adapter for the fake, so a fault on either side of the port was on some run's
executed path; without the table *"there is nothing to swap, so `--wiring fake`
runs the real adapter"*.

**A leftover `[ports.*]` table is now ignored rather than rejected** by one of the
two TOML readers and rejected by the other. That asymmetry is in the after tree.

### (b) A hard-coded list in the instrument registry was replaced by a derived walk

`tests/test_instrument_demonstrations.py` asserted `required <= enumerated` over
a literal of **thirteen paths**. The literal is gone. `[registry.enumeration]` in
`examples/validation/instruments/instruments.toml` now declares two roots and two
exclusions, each with a written reason, and the members are **derived** by walking
the tree for a `__main__` guard plus a nonzero exit path.

Separately, 43 registry slots that previously asserted only a process exit code
now also assert an executed-test count (`expect_passed` / `expect_passed_at_least`,
with `expect_skipped` defaulting to 0).

### (c) Statements of a shared rubric were de-duplicated to one home

Twenty statements of a rubric's contents, spread over five documents and one
harness file, were deleted; `tests/test_card_has_one_home.py` (428 lines) was
added to keep them from being written again. Six copies remain, each of which
something executes a comparison of against the source, and twelve remain in files
classified as records of what was true when written.

### (d) A checksum field was removed from a record format

A `total` field was removed from `examples/validation/scorecards/score_tools.py`'s
record schema and from everything that printed it.

---

## 3. The measured produced-code descriptor, before against after

Produced by the artifact's own instrument, `scripts/code_complexity.py`, with the
identical command and interpreter on both trees:

```
python3.14 scripts/code_complexity.py scripts tests examples/validation references --json
```

Raw output for both is in `data/descriptor-before-3f58aca.json` and
`data/descriptor-after-f49a1c9.json`. `totals` (all roles):

| tree | before `3f58aca` | after `f49a1c9` | delta |
|---|---|---|---|
| `scripts/` **code_lines** | 21252 | **21027** | **−225** |
| `scripts/` callables | 803 | 797 | −6 |
| `scripts/` public_surface | 882 | 877 | −5 |
| `scripts/` branch_points | 3272 | 3228 | −44 |
| `scripts/` internal_import_edges | 60 | 59 | −1 |
| `tests/` **code_lines** | 20068 | **21050** | **+982** |
| `tests/` callables | 1261 | 1329 | +68 |
| `tests/` branch_points | 729 | 818 | +89 |
| `examples/validation/` **code_lines** | 8915 | **9835** | **+920** |
| `examples/validation/` callables | 471 | 495 | +24 |
| `examples/validation/` branch_points | 1222 | 1381 | +159 |
| `references/` code_lines | 0 | 0 | 0 |

**Summed over the three trees that carry code: 50235 → 51912, a net of +1677
`code_lines`.** The one tree that fell is `scripts/`, by 225 lines, which is
**1.06 %** of its before figure.

`totals_code_only` (excluding test-role files) for `scripts/`: 20140 → 19915,
also −225.

A caveat the instrument states about itself, carried here so it is not lost: it
reports `unresolved_constructs` — ten `getattr()` / `setattr()` sites it cannot
resolve — on both trees.

---

## 4. Faults seeded in the gaps, before and after

Before **any** of the deletions in §2, nine faults were seeded, each in the gap
that one of the mechanisms about to be deleted claimed to cover, plus two
positive controls. Each was run against every detector that existed at that time.
After the deletions the same faults were re-run.

- `data/gap-mutants-before.json` — the before run, at the before commit.
- `data/gap-mutants-after-SM-02.json` — re-run after change (a).
- `data/gap-mutants-after-SM-03.json` — re-run after change (b).
- `data/dup-mutants-before.json`, `data/dup-mutants-after.json` — four faults
  seeded for change (c), before and after.

Read the JSON, not this summary, for anything you cite. The runner is
`examples/validation/gap_mutants/run_gap_mutants.py` in either tree and the
catalogue is `examples/validation/gap_mutants/gap_mutants.toml`.

Three properties of the runner that bear on how a cell should be read, taken from
its own docstring:

- verdicts compare **failure sets** against a pristine staged tree, never exit
  codes, because a staged tree has pre-existing failures;
- a detector whose unmutated control run fails is reported `CONTROL_RED` —
  *undecided* — and never as a survival;
- a detector whose entry point no longer exists is reported `REMOVED`, and one
  that executed nothing is `INERT`.

Two things the before-run recorded about itself, in the JSON:

- one seeded fault (`SM-GM-I2`) perturbs a **reported field** rather than the
  refusal path it was aimed at, and is recorded by its own author as a defect in
  the mutant;
- an assertion inside the runner's own test file was firing on the mutated tree
  during measurement, was excluded from the verdict, and is reported per cell as
  `self_detected_nodes`.

For change (d), the before and after were measured in one run; the test that
records it is `test_the_price_of_removing_total_measured_on_both_sides` in
`tests/test_score_tools.py` in the after tree.

**Four mechanisms have no seeded fault at all**, and the reason for each is in
`[[not_seedable]]` in the catalogue.

---

## 5. Instrument registry counts, before and after

Raw: `data/instruments-before.json`, `data/instruments-after.json`. Produced by
`examples/validation/instruments/demonstrate.py`.

| figure | before | after |
|---|---|---|
| enumerated rows | 40 | 57 |
| instruments | 35 | 47 |
| with a demonstrated failing input | 26 | 33 |
| without one | 9 | 14 |
| ratio | 74.3 % | 70.2 % |
| slots asserting only a process exit code | 12 | 0 |
| rows whose failing and passing slots ran the same command | 2 | 0 |

Zero rows were deleted. Twelve of the new denominator are executables the old
hard-coded list could not see; the derived walk found **eighteen** unregistered
executables where a hand enumeration had found eight.

The derived walk's declared blind spot, from the after tree: its predicate is a
`__main__` guard plus a nonzero exit path, so a repository tripwire that is a
**pytest file** has neither and is invisible to it. Six such files exist.

---

## 6. Suite results on the UNREDACTED trees

Measured on real checkouts, not on your staged copies:

```
after  f49a1c9   uv run --with pytest --with pyyaml python -m pytest tests -q
                 1386 passed in 471.39s
before 3f58aca   (the same command, recorded at the time)
                 1177 passed, 1 failed
```

The single failure at the before commit was a deliberately-left-red node from a
prior round, not a regression.

---

## 7. What this packet does not contain, stated so you do not go looking

- **No result of any prior evaluation of this or any other artifact.** The
  redaction in §1 is what removes them, and §1 names the four files it could not
  remove.
- **No claim that the change in §2 was an improvement, or that it was not.**
- **No fault class inventory.** The nine seeded faults are the nine that were
  seeded; nobody claims they are the only faults these regions admit, and the
  runner's own docstring says so.
- **No measurement of the redaction's cost.** How many suite nodes fail in your
  staged trees purely because of §1 was not counted.
