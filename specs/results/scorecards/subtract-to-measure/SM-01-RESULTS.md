# SM-01 — the gap mutants, seeded and priced before anything was removed

Nothing has been removed. This ticket seeds, measures and records; `SM-02` and
`SM-03` cut, and `SM-05` re-runs exactly this file's runner on the integrated
tip.

Artifact: `before-state/gap-mutants-before.json`. Runner:
`examples/validation/gap_mutants/run_gap_mutants.py`. Catalogue:
`examples/validation/gap_mutants/gap_mutants.toml`. 26 min 43 s, zero mutants
failed to apply, **both positive controls died on every detector they declare**.

---

## 1. The gap-mutant table

Nine mutants, two positive controls, seven detectors. Every cell carries an
executable count except the two the shipped port-swap driver does not provide
one for — reported as *no count* rather than filled in (`SM-01-DF-01`).

**Baseline, `pytest-full`, on the pristine staged tree: exit 1, 1370 executed,
9 failing** — all nine read git history and fail in a `git archive` tree for
that reason alone (`SM-01-DF-03`). Verdicts compare **failure sets**, never exit
codes.

### Mechanism 1 — the `[ports.*]` binding machinery (`SM-02` cuts it)

| mutant | `corpus-port-swap:fake` | `corpus-port-swap:real` | `corpus-action-bound` (both) | `suite-fake` | `suite-real` | `pytest-full` |
|---|---|---|---|---|---|---|
| **`SM-GM-P1`** the fake journal records newest-first | **DIES** 1543 | SURVIVES 1543 | SURVIVES 1543 | **DIES** 28 | SURVIVES 28 | **DIES** 1370 |
| **`SM-GM-P2`** the manifest renames the port out from under the binding | — | — | — | — | — | **DIES** 1370 |
| **`SM-GM-P3`** the fake is silently a second real adapter | SURVIVES 1543 | SURVIVES 1543 | SURVIVES 1543 | SURVIVES 28 | SURVIVES 28 | **DIES** 1370 |
| **`SM-GM-CTRL-A`** (positive control) | **DIES** 1543 | **DIES** 1543 | **DIES** 1543 | **DIES** 28 | **DIES** 28 | **DIES** 1370 |

`SM-GM-P2` also reports **DIES** on `port-binding-report` — the
`render_port_binding_report` reconciliation, read from its printed text because
it exits 0 regardless (`FI-02-DF-02`).

**Every column the machinery owns is matched by one that outlives it.**

- `SM-GM-P1` dies on `corpus-port-swap:fake` **and** on `suite-fake`, which is
  four lines of `quota_ledger_fake.py` with no binding table, no wiring flag and
  no mapping. Five `test_behavior.py` nodes name it, including
  `test_r5_the_ledger_is_append_only_and_ordered`.
- `SM-GM-P2` dies on the ports report **and** on three pytest nodes:
  `test_port_adapter_binding.py::test_a_bound_port_the_manifest_declares_is_reported_as_declared`,
  and two in `test_port_case_generation.py`. **Two of those three survive `SM-02`**, because
  `test_port_case_generation.py` is about the `--port-cases` corpus, not the binding table.
- `SM-GM-P3` **survives every column the machinery has**, on 1543 executed cases
  each, and dies only to four hand-written nodes in
  `test_ab_three_arms_and_port_faults.py` — among them
  `test_a_fault_seeded_in_the_fake_is_reachable_only_through_the_fake`.

> **THE SWAP CANNOT DETECT THAT ITS OWN FAKE IS NOT A FAKE.** `SM-GM-P3` makes
> `quota_ledger_fake.py` compose the *file* journal, so `--wiring fake` and
> `--wiring real` become the same program under two names. Both columns keep
> reporting, both keep passing, and the run keeps printing *"THIS RUN USED THE
> FAKE SIDE"*. This is the one failure a port-swap mechanism exists to make
> impossible, and it is the one it is blind to. `SM-01-DF-04`.

### Mechanism 2 — the hollow demonstrations and the enumeration check (`SM-03` cuts them)

| mutant | `instrument-registry` | `pytest-full` | other |
|---|---|---|---|
| **`SM-GM-I1`** the cited node is collected and **skipped** (`pytestmark`, exit 0) | **SURVIVES** | **SURVIVES** 1297 | |
| **`SM-GM-I6`** the cited node is **not collected** (`allow_module_level`, exit 5) | **DIES** | SURVIVES 1297 | |
| **`SM-GM-I2`** the demonstrated instrument stops refusing | **SURVIVES** | **SURVIVES** 1370 | |
| **`SM-GM-I3`** an instrument that was never added to the registry | — | **SURVIVES** 1372 | `registry-enumeration` **SURVIVES** |
| **`SM-GM-I4`** a shipped spec YAML committed unparseable | **DIES** | **DIES** 1370 | `spec-yaml-tripwire` **DIES** 23 |
| **`SM-GM-I5`** the enumerator itself stops reporting a failure | **SURVIVES** | **DIES** 1370 | |
| **`SM-GM-CTRL-B`** (positive control) | **DIES** | — | |

Read `SM-GM-I1` and `SM-GM-I6` as a **difference, never a total.** A table
saying "1 of 2 skip mutants caught" destroys the only comparison they exist to
make:

> **`FI-06` IS RIGHT ABOUT THE MECHANISM AND WRONG ABOUT ITS REACH.** The
> finding says the twelve `expect_exit = 0` slots are satisfied by *"a fully
> skipped run"*. Measured: a module-level skip collects nothing, pytest exits
> **5**, and the demonstration **goes red** — the registry catches it. A
> `pytestmark` skip collects the items and skips them, pytest exits **0**, and
> the demonstration reports `ok`. **The blind spot is a demonstration that goes
> VACUOUS, not one that disappears**, and `SM-03` has to repair the first
> because deleting on the second reads the finding backwards. `SM-01-DF-05`.

Also measured, and it changes what `SM-03` should do:

- **`SM-GM-I3` survives everything, as `FI-04-DF-04` says it must.** A new
  executable under `scripts/` with argparse, a `__main__` and a nonzero exit
  path, and no registry row: `registry-enumeration` green, the full suite green.
  This row is the demonstrated failing input `SM-03`'s repair must flip to
  `DIES`.
- **`SM-GM-I5` dies to `pytest-full` and not to the registry.** The enumerator's
  only verdict surface *is* watched, by
  `test_instrument_demonstrations.py::test_the_runner_REPORTS_a_demonstration_that_stops_reproducing`
  and `::test_the_runner_refuses_a_mutation_that_seeds_nothing`. **`N06` is
  refuted**, and the counts `SM-03` is about to report do not need the caveat I
  predicted they would.
- **`SM-GM-I4` dies on all three detectors.** `spec-yaml-tripwire` is classified
  `no-demonstration-constructible` — *"not without breaking a shipped file"* — and
  breaking one in a throwaway tree turns it red in 23 executed tests. The
  demonstration is constructible; what is not constructible is a demonstration
  that `demonstrate.py` can run, because it shells pytest at `REPO_ROOT`. **The
  classification is about the runner, not about the instrument**, and three
  further rows carry the identical reason. `SM-03` must not delete them on it.

### No seedable gap — four mechanisms, named rather than skipped (R2)

| mechanism | why not |
|---|---|
| `scripts/code_complexity.py` | **Correctly cannot fail.** A thermometer: reports, refuses nothing, `EXIT_OK = 0` is its only exit constant. No claim to catch anything means no gap to seed. **Not a removal target**, named so `SM-03` does not cut it with the other eight. |
| registry row `test-graph-nodes` | Needs gradle, a JVM and JBang. A mutant would report `INERT` on every detector, and `INERT` is indistinguishable from a survival to a reader skimming. **Declared unmeasured rather than measured as nothing.** |
| the `fake =` key of a `[ports.*]` table | The fault would live in the mechanism's own declaration, which is deleted with it — no post-removal tree to re-apply it to. `SM-GM-P2` seeds the equivalent drift in the **manifest**, which outlives `SM-02`. |
| registry row `ticket-state-agreement` | The gap is already total: `ticket.yaml`'s `status` is read by nothing (`PA-02-DF-02`), and every `ticket.yaml` in the tree is under append-only `specs/.history`. The removal's cost is already paid in full. |

---

## 2. Predictions scored — the seven decidable now

Sealed at `b2b8e9c`, **before** the runner was ever pointed at a real mutant.
Five more (`N01`–`N05`) are `SM-05`'s.

| ID | claim | verdict | why |
|---|---|---|---|
| **P01** | fake-side fault dies to the suite, not the binding | **PASS** | as labelled, **ENTAILED** |
| **P02** | manifest drift is the machinery's unique catch | **FAIL** | predicted `SURVIVES` on `pytest-full`; it **DIES** on three nodes, two of which outlive `SM-02` |
| **P03** | `complexity-ledger` is redundant with the suite | **FAIL** | predicted `DIES` on both; it **SURVIVES** both. The row does not catch this instrument going soft either |
| **P04** | the enumeration check cannot see an omission | **PASS** | as labelled, **ENTAILED** |
| **P05** | "not constructible" is about the runner | **FAIL** on its second half | the tripwire dies as predicted, but `instrument-registry` **also** dies — staging the whole repo makes `REPO_ROOT` the staged tree, so the runner's limitation is reachable after all |
| **P06** | the hollow slots are blind to VACUOUS, not to MISSING | **PASS** | the split is exactly as predicted, and it is the sharpest result here |
| **N06** | nothing watches the enumerator's exit code | **FAIL** | two nodes in `test_instrument_demonstrations.py` watch it |

**3 PASS, 4 FAIL, and both passes that were not entailed are `P06`.** The
predecessor's alarm — 8 of 8 with four structurally unfalsifiable negatives — is
not triggered here: four rows were refuted by a run, including the one negative
that was decidable at this ticket.

**What the failures bought.** `P02` and `P05` failed because I predicted a
uniqueness the measurement did not find; `P03` failed because my mutant was
weaker than I thought — `"verdict": "rejected" if errors else "recorded"` is a
*reported field*, not the refusal path, so `SM-GM-I2` perturbs what the ledger
says about itself rather than whether it refuses. **That is a defect in my
mutant and it is recorded as one, not reinterpreted into a finding about the
registry.** `SM-05` should read `SM-GM-I2` as `UNDER-POWERED`, not as evidence
the row is hollow.

---

## 3. The instrument found two defects in itself before it found any in the repo

Both came from the dominant channel the predecessor named — *build the
instrument, then ask what it cannot report* — applied to the first run's **raw
`new_failing_nodes`** rather than to its verdicts.

1. **The instrument was detecting itself.**
   `tests/test_gap_mutants.py::test_every_mutant_anchor_occurs_exactly_once_in_the_shipped_tree`
   reads the catalogue's anchors out of whatever tree it runs in — which during
   a measurement is the **mutated** one. It fired on every mutant, and on
   **`SM-GM-I2` and `SM-GM-I3` it was the only new failure**, so the first run
   scored both as `DIES` when the repository catches neither. Excluded from the
   verdict, reported per cell as `self_detected_nodes`, and covered by two tests
   — one that the exclusion changes nothing about a genuine node, one that it
   cannot grow.

2. **A shipped tripwire caught this ticket.**
   `tests/test_code_complexity.py::test_no_reader_of_this_instrument_gates_on_its_output`
   went red on my own new test file, which named the descriptor module and
   compared a figure two lines later — the thermometer-into-thermostat shape it
   exists to catch. **Fixed by not naming the module, not by adding the file to
   the tripwire's exemption list**; lengthening a list was rejected at
   `EVAL-RERUN-DF-01` and again at `ARM_MODULE_PREFIXES`, and it would be worse
   here because that scan is one of the nine instruments this epic is judging.

Neither is flattering and both are the point: a gap-mutant runner that could not
be shown to misreport would be the fifth unfalsifiable instrument in this
repository.

---

## 4. Findings filed, none fixed

`SM-01-DF-01` … `SM-01-DF-05` in `specs/desired_program_model/deferred_findings.yaml`.
Budget 5, batch mode, spent exactly. The measurement-relevant one:

> **`SM-01-DF-01`, MAJOR.** The two columns `SM-02`'s case rests on —
> `suite-real` / `suite-fake`, where `suite-fake` strictly dominates
> `corpus-port-swap:fake` — carry **no executable count** and are **structurally
> exempt from control checking**. `run_suite` returns `total_failed` derived
> from an exit code and nothing else; `control_verdict` decides through
> `witness_count`, which reads `per_action`, which those columns do not have, so
> `witness_count` returns `None` and *nothing is decided against them*. That
> machinery was written because `PA-04`'s first run printed `control_red: []`
> while a control had survived four columns. The repair covered the corpus
> columns and left the suite columns in exactly the state it was written to end.

`SM-01`'s own runner re-measures the same subject **with** counts (28 executed
per suite run) and agrees with the driver on every cell — so no sealed number is
shown to be wrong, only undecidable from its own artifact. Both readings are
kept side by side (`suite-*` counted, `portswap-suite-*` uncounted) so a future
disagreement is visible rather than overwritten.
