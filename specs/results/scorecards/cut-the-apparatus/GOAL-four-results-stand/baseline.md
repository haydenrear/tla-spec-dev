# `GOAL-four-results-stand` — baseline

**Measured at the epic base `08d1d6a90ad2638cdfceee7cc2e150732daa3438`.**

This is the goal that constrains every other one. **A silently broken result is
the worst outcome available and fails this goal even if the lines fell.**

---

## The four results, each with the evidence that makes it checkable

### 1. Asking for an architecture changes the architecture

D3 went **1 → 4** on the prompt alone, replicated across rounds.

**The confound was killed directly, not argued away:** `arm C` — a *longer*
prompt carrying **no architectural vocabulary** — scored **1/1**. Prompt length
is not the mechanism.

- evidence: `examples/validation/ab/arm_a`, `arm_b`, `arm_c`;
  `specs/results/scorecards/ports-as-adapters/`

### 2. D3 separates architectures on more than one example

`eval_toolchain` — **the first example that is neither the house fixture nor a
hand-built case**:

```
effectful             [0, 1]
ports-and-adapters    [2, 4]
```

**Disjoint, and both judge tiers on both sides** — which `ab_quota_ledger`
cannot say.

- evidence: `specs/results/scorecards/portable-substrate/`

### 3. D3's v5 caveat discriminates

`SV-01`. On an artifact **lacking** the single-observer property, D3 held
**4, 4** at v4 and **4, 4** at v5. On one that **has** it (`CL-03`), D3 fell
**4, 4 → 3, 3**.

**Prediction sealed at a timestamped commit before any judge ran.**

- evidence: `specs/results/scorecards/score-drives-validation-sv01-v4/` and
  `-sv01-v5/`
- **discount, disclosed by the ticket itself:** `SV-01-DF-01` — all four judge
  scratch paths were a prior round's, holding the previous artifact and a prior
  `D3 = 4` one `ls` away. **A contamination that cuts toward the predicted
  answer.** Discounted, not withdrawn.

### 4. A score can produce a test and the re-score sees it

`SV-04`. Control arm **3, 3** vs treatment **4, 4** — **same bytes plus one
file** — with **D2 flat at 2 across all four**. `0 for 7 epics` became
`1 for 8`.

- evidence: `specs/results/scorecards/score-drives-validation-sv04/`

---

## The four disproofs, which are equally load-bearing

| disproof | figure |
|---|---|
| Model-derived cases do not catch bugs hand-written tests miss | **0** unique kills across six trees, **4** the other way, replicated on new subjects |
| Static gates catch nothing | seven epics, **zero** bugs caught by a static check |
| The removal-pricing instrument **is not yet useful** (CORRECTED, `CA-00-DF-05`) | `NEXT-EPIC.md` §5: *"a non-zero was the informative outcome, the instrument would have printed one, and none appeared… the goal is met and the instrument is not yet useful"*. **This row previously read "could only ever return zero — 0 of 9 over the sealed table", which `RM-05-DF-01`, `RM-02` §10.2 and `RD-02` each refute.** |
| Three of the card's five dimensions graded toolchain ownership | **38%** of D1 and **18%** of D4 anchor rationales cited local machinery, against **0%** on D3 and D5 |

**`CA-04` must state explicitly whether disproof 1 is still reproducible from
the sealed record once the instrument that produced it is gone.**

---

## Instruments that must still run at the tip

`RM-02`: *"the substrate's best export, and the epic should be careful not to cut
them for being unglamorous."*

`scope`, `seal`, `contested`, the blinding mechanism, `R-H1`/`R-H2`/`R-H4`/`R3`,
and the version/served double seal. **`CL-01`'s second seal caught a real class
one ticket later.**

## The card at the base

```
serve | wc -c        6281
serve --digest-only  sha256:2d7d4a0506d9b259  (card version 5,
                     rubric file sha256:b7fe75437bf68646)
```

9 rungs, 2 scored dimensions.

---

## The suite at the epic base

Command — **this one, not `README.md:35`, which omits `--with pyyaml` and yields
12 phantom reds**:

```bash
uv run --with pytest --with pyyaml -m pytest tests -q
```

<!-- SUITE-BASELINE-START -->
### At the epic base `08d1d6a`, isolated detached worktree, seven affected files

**6 failed, 314 passed.** Two are the declared deliberate reds. **Four are
inherited and were never declared:**

```
test_architecture_tags.py::test_the_same_tag_control_holds                      DELIBERATE (RM-06-DF-01)
test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer        DELIBERATE (pricer grep)
test_source_citations.py::...[specs/current/spec_manifest.yaml]                 INHERITED, UNDECLARED
test_source_citations.py::...[specs/desired_program_model/spec_manifest.yaml]   INHERITED, UNDECLARED
test_source_citations.py::...[specs/program_model/spec_manifest.yaml]           INHERITED, UNDECLARED
test_ticket_retirement.py::...delivered_plan_has_matching_close_receipts        INHERITED, UNDECLARED
```

**The record says "two deliberate reds, plus a third undeclared one found last
epic." That understates it: there are at least four undeclared inherited reds**,
and `SV-01` and `SV-02` each found only one of them. **None of these is any
ticket's regression.**

### At the epic tip `87a526b`, the same seven files

**12 failed** on the full suite. The six above, plus six the kickoff commit
introduced. **Attributed, because attribution is the whole point:**

| red | cause | verdict |
|---|---|---|
| `test_a_refuted_finding_stays_on_the_record_with_its_filing` | `CA-00-DF-01` | **epic owner's damage** |
| `test_the_repo_ledger_passes_its_own_audit` | `CA-00-DF-01` | **epic owner's damage** |
| `test_the_repo_ledger_passes_its_own_audit_with_rh6` | `CA-00-DF-01` | **epic owner's damage** |
| `test_the_shipped_rh5_demonstration_still_goes_red` | `CA-00-DF-01` | **epic owner's damage** |
| `test_every_fast_demonstration_reproduces` | `CA-00-DF-01` (`scorecard-audit`, `scorecard-contested-drift`) | **epic owner's damage** |
| `test_a_real_epic_plans_judged_baseline_cannot_be_re_opened` | `CA-00-DF-02` | **a finding, not damage** |

**Restoring the ledger cleared five of the six**: those three files went from
**6 failed / 152 passed** to **1 failed / 157 passed** on the same tree. The
survivor is `CA-00-DF-02` — an `R1` instrument whose "real subject" is read out
of the live plan and therefore dies at every epic kickoff.

### So the figure every ticket compares against

**7 reds at the epic branch after the restore**: the 2 deliberate, the 4
inherited-undeclared, and `CA-00-DF-02`. **Anything beyond that list is yours and
must be declared with its cause.**

#### That 7 was DERIVED, and has since been MEASURED

**Stated honestly when written:** the `6 failed / 314 passed` above is a
**seven-file subset**, not a full suite, and the 7th red was added **by
reasoning** rather than by a run. CA-01's independent reviewer caught that the
figure had never been measured end to end, and measured it:

```
full suite at PR #263 head (CA-01, on the restored tree)
  7 failed, 1555 passed in 1192.05s (0:19:52)
```

**Exact match, item for item, no more and no less** — the 2 deliberate, the 3
`test_source_citations`, `test_ticket_retirement`, and `CA-00-DF-02`. **Nothing
attributable to CA-01.**

The derived figure and the measured figure agree. **They did not have to**, and
recording that they were arrived at separately is the point.

### Two runs that are NOT the baseline, and why

Both are recorded rather than deleted, because a discarded run is evidence about
method.

1. **First full-suite run, 9 failed / 1553 passed.** Started at kickoff and
   **contaminated by the epic owner editing `ticket_plan.yaml` and the manifests
   while it was in flight** — several of those tests read those files at test
   time. Unusable, and the same class as the shared-`baseline.txt` corruption in
   this project's own operational rules.
2. **Second full-suite run, 12 failed / 1550 passed.** Clean tree, but a ticket
   agent created a worktree and branch mid-run. **Three tests flipped between the
   two runs on the same tree**, which is why neither was published as the
   baseline and why the attribution above was done per-file in isolation instead.
<!-- SUITE-BASELINE-END -->

**Compare against this figure, not against a recollection.** Two reds are
inherited and deliberate — `RM-06-DF-01` (the same-tag control cannot tell
treatment from architecture) and the pricer grep tripped by narrative documents
— and `SV-02` and `SV-01` independently found a **third undeclared** red last
epic. **Do not repair any of them silently**, and **declare** any red beyond
this baseline with its cause.
