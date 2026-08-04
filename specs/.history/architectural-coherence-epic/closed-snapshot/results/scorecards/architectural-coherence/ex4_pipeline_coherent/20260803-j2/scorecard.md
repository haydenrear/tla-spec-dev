# ex4_pipeline_coherent — judge pass 2 (run 20260803-j2)

Scorecard version 1. Commit `ab0dfee`. Arm: none (single-artifact eval).

| dim | score | one line |
|---|---|---|
| D1 bug detection | 2 | content faults caught in both arms; guard relaxation and ordering measured at zero |
| D2 complexity | 2 | proportional, no god-state; no simplification was made or measured |
| D3 modularity | 3 | a real port swap with runtime evidence; the shipped fake cannot implement it |
| D4 behavior preservation | 4 | model-derived envelope, green control, three mutant catalogues, 38/38 determinism |
| D5 honesty | 3 | exemplary self-correction, one un-amended headline |
| **total** | **14**/20 | |

## What I re-derived rather than read

- Ran `analyze complexity` on `Pipeline.tla` at scoring time: bound **4,096**
  (`COMPLETE`, 6 of 6 variables), emergent **Q = 0.194** over two components,
  one dense row (`delivered` 3/5), **no dense columns**.
- Ran the reflexion check on the byte-identical twin and reproduced its answer
  key exactly (see the ex5 card).
- Re-computed the kill matrices from `kill_matrix.json` and
  `mutant_results.json` instead of the tables: seeded 4/6 ARM A, 6/6 ARM B;
  12-mutant catalogue guard relaxation 0/3 both arms, ordering 0/3 everywhere,
  wrong-write 4/4 ARM A, durable ARM B only; blind 16-mutant catalogue
  view 10/16, pytest 10/16, **union 14/16**, guard_accepts 0/4 on all five
  corpus instruments, ordering 0/2 killed by nothing at all.
- Ran the twin behavioral suite: 8 passed. `check_twins.py` exit 0.

Every figure the run records state, reproduced. That is itself a finding and it
is recorded in `mechanical.json`.

## D1 — bug detection: 2

Anchor 2 is met with unusual clarity, because the two arms are *two declared
mappings* rather than one mapping with assertions switched off
(`providers.py:22-25`, and the two `.toml` files differ by one provider line).
The ARM B assertion is on content — persisted bytes versus the modeled
after-state, plus a separate failure for a write the model did not make
(`providers.py:88-103`). The adapter refuses to execute a case whose argument is
`UNCHECKED` rather than quietly no-op'ing (`adapters.py:104-112`), which is the
vacuous-pass hole closed at the source.

Anchor 3 is not met, and this fixture's own artifacts are the reason:
**guard relaxation 0 of 3** (0 of 4 on the blind catalogue, on all five corpus
instruments) and **ordering 0 of 3 and 0 of 2, killed by nothing including
pytest**.

I considered and rejected the argument that F3/F5/M10 — killed only under ARM B —
constitute "a class the whole-view corpus structurally cannot reach on its own".
They are durable-side *content* faults reached by a content assertion, which is
anchor 2's own wording; treating them as anchor 3 would erase the distinction
between the two anchors, and the classes the rubric names (refusal, ordering,
cross-aspect before-state) are exactly the ones measured at zero here.

## D2 — complexity: 2

The model is proportional to its behavior: `4^6` for six subsets of a two-item
set, one dense row, no dense columns, every variable invariant-read. No god
state, no variable written from everywhere.

It stops at 2 honestly. **No simplification was made.** The fixture deliberately
went the other way — one variable and one action ADDED relative to the owner's
probe model — and argues why (`README:89-98`): a two-component partition has one
component pair, that pair is ported, so no code edge could ever diverge and the
fixture could not be a positive test. That is a well-argued *increase*, not a
measured *reduction*, and D2 ≥ 3 requires the latter.

Recorded, not scored down further: the manifest ships no `justification:` table,
so the descriptor's dead-weight analysis is skipped on the fixture that is
otherwise the most thoroughly measured in the set.

## D3 — modularity: 3

The evidence is about calls, not imports, which is the bar the card sets after
round 2 showed a codebase passing every import check with its coupling intact.

- The domain does not import its I/O: `Journal` receives the store as a
  constructor argument and reaches it through one method (`journal.py:27-49`);
  the only concrete store lives in `specs/`, outside the scanned code root
  (`providers.py:38-54`).
- The specific swap: `silent_ledger_store_provider` ↔ `ledger_store_provider`,
  one line different in each of two declared mappings, zero bytes of
  `pipeline/` changed.
- Runtime proof that the swap is real: on the control both bindings produce
  **byte-identical stdout** (same sha256 in `kill_matrix.json`), and F3/F5/M10
  die under ARM B while surviving ARM A — impossible unless the domain calls the
  bound store during execution.

Not 4. The generated fake's `persist` raises `NotImplementedError`
(`generated/pipeline_contract/fake.py:19-21`), so the driven port has never been
exercised against a double at all. "Real adapter *and* a fake, same cases passing
against both" is not satisfied by two real file-backed stores, and I would rather
name the gap than round up.

## D4 — behavior preservation: 4

Enumerated: 330 model-derived cases over five actions with per-action counts and
`UNCOVERED: none`, plus eight hand-written conformance tests (green, I ran them).
Model-derived: the corpus is generated from the TLC state graph, not authored.
Demonstrated capable of failing: three separate mutant campaigns, each with a
green control recorded first, each with per-detector attribution, plus 38 of 38
byte-identical executions across two independently generated corpora and 6 of 6
replays reproducing the same failing case sets.

The caveat I will not bury: ex4 has no baseline-versus-simplified pair, so this 4
means "the behavioral envelope is enumerated and the check is provably
falsifiable", not "a simplification preserved behavior". A reader comparing this
cell to ex3's 3 should read that difference, not a quality ordering.

**Refuses to claim** (required for a 4): the coverage report refuses to let the
union of the two case modules stand in for the view's corpus
(`case_module_coverage.txt:20`), and the parameter audit refuses to generalize
past the actions its corpus entered (`param_recovery_audit.md:21`).

## D5 — honesty: 3

Anchors 2 and 3 are met inside the fixture, not only in a report:

- it names what it cannot answer before being asked — the composition root has
  nowhere to live, and the fixture says so and explains the workaround
  (`README:126-135`);
- it retracts its own claim in place: "the paragraph above is superseded, and it
  was WRONG on its second half" (`README:183-204`), keeping the superseded
  `param_recovery_audit_pre_rp02.md` beside the corrected one;
- it refuses rather than certifies: the runner exits 1 rather than run a slice
  corpus whose declared port no selected case requires — under **both** shipped
  mappings (`case_modules_worked_example.txt:93-99`). That refusal costs the
  fixture its own cheapest artifact and it is recorded anyway;
- `evidence/df02_nondecomposing_partition/` keeps a round-1 `coherent` printed on
  a partition that does not decompose — an unflattering result preserved.

Held at 3 for one specific, artifact-level reason. **ANSWER KEY 1 still presents
`coherent` as this fixture's ground truth** with no note that round 2 measured
that same verdict flipping to `unmappable` when `generated/pipeline_contract`
moves one directory, with zero bytes of Python changed. This README demonstrably
gets amended when a finding lands (the RP-02 amendment proves the convention
exists); the finding that undercuts its headline did not get one. An artifact
whose positive claim is conditional should say so where the claim is made.
