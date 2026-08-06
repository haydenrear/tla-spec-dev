# FI-06 — the four adversarial channels

Four agents, dispatched in parallel, **blind to each other**, each told that *a
finding making the headline worse is worth more than one confirming it*, and each
**forbidden to write anything inside the repository**. That last constraint is
`FI-03`'s own recorded defect (*"the repository was modified while blind judges
were reading it … a measurement should not have a moving floor and this one
did"*) applied rather than repeated. All four scratch trees are under
`/tmp/fi06/agent{1..4}/`; `git status` was verified clean before and after every
run.

Each channel was pointed at one of the four questions FI-06 must answer, given
the live caveats it had to respect (`FI-01-DF-01`: never run `run_controls.py` on
a ported subject; `FI-02-DF-02`: read `control_red` out of the JSON, never infer
control health from an exit code), and asked for **what it REJECTED** as a
required section.

| channel | question | tool calls | findings kept |
|---|---|---|---|
| **A** | for every instrument: does it go red when the thing it watches is broken? | 88 | 3 (`FI-06-DF-01`, `-02`, `-03`, `-12`) |
| **B** | can the fixture's arms diverge, or does the replacement entail its answer? | 57 | 2 (`FI-06-DF-09`, `-10`) |
| **C** | does anything we generate beat a hand-written suite? | 72 | 2 (`FI-06-DF-07`, `-08`) |
| **D** | is the scorecard stable enough to carry a delta? | 61 | 2 (`FI-06-DF-04`, `-11`) |

**Every claim below was independently reproduced by FI-06 before it was written
into `RESULTS.md`.** Nothing an agent reported was taken on its word.

---

## Verification log — what FI-06 re-ran before believing it

| claim | channel | how FI-06 checked it | result |
|---|---|---|---|
| a second blind-authored catalogue exists, and the suite dominates on it | C | loaded `hexagonal-prompting/GOAL-catch-bugs/kill-table-blind-author-arm-{a,b}.json` and recomputed the sets | **13 rows / gen 8 / suite 9 / gen-only `[]`; 14 rows / gen 8 / suite 9 / gen-only `[]`** — confirmed |
| `ResIds = {r1, r2}` caps behaviours at two `Reserve` | C | `QuotaLedger.cfg:8`; `grep "holder'"` → one line, `:112` | confirmed |
| `BA-A10` is the same fault class as `BA-P11` | C | read `catalogue_blind_arm_a.toml:157-163`, `fault_class = "id_allocation"` | confirmed |
| the oracle's own 266-of-294 split | C | `oracle.py:86-101` | confirmed verbatim |
| `wired_by_default` was added after the seal | B | `git diff 4697687 e074ae5 -- adapter_faults_arm_b.toml` | **two `+` lines, no `-` lines** — confirmed |
| `corpus-action-bound` ≡ `corpus-port-swap:real` | B | evidence-block equality over all 8 rows of all 3 arms | **True on every row** — confirmed |
| all 12 pytest failing slots lack `expect_output` | A | `tomllib` sweep of `instruments.toml` | **12 of 12** — confirmed |
| two rows have `failing.nodes == passing.nodes` | A | same sweep | `complexity-ledger`, `case-modules-validate` — confirmed |
| eight instruments absent from the registry | A | `tomllib` membership test for each path; existence test for each file | all absent, all present on disk — confirmed |
| `extract_spec_manifest.py` is red on the shipped manifest | A | ran it | **exit 1, three `missing required manifest key`** — confirmed |
| the rubric stated the result the judges were measuring | D | `git show 51fe73d:references/eval_scorecard.md` → `:361`, `:376`; `git show 930fa57:… \| grep -c` → **0** | confirmed |
| `architectural-coherence` cards were scored against a rubric not in the tree | D | `git show ab0dfee:references/eval_scorecard.md` → absent; cards have no `rubric` key | confirmed |
| the divergence reproduces at the tip | B + FI-06 | independent corpus regeneration + 3 fresh arm runs (B); re-analysis over the sealed artifacts (FI-06) | **zero cells moved; JSON byte-equal to the sealed `divergence.json`** |

## Claims DROPPED for failing that check

Recorded rather than discarded, because a rejected adversarial claim is evidence
about the artifact.

1. **Channel D's "the `60 judge-scores` arithmetic does not hold."** The claim is
   that *"D2 and D3 moved zero on every one of the 60 judge-scores"* is wrong
   because D2 and D3 are only 24 of the 60. **Dropped.** The sentence reads
   naturally as *"across the 60 judge-scores this ticket measured, D2 and D3
   moved zero"*, which is true. It is loose phrasing, not a false number, and
   filing it would put a prose quibble beside eleven substantive findings.
2. **Channel D's "`15 of 15` is really `6 of 6`."** The claim is that nine of the
   fifteen cells in FI-03's exact-reproduction result could not have differed —
   D2 (constant), D3 (deterministic) and **D1**. **Dropped on D1.** D1 takes four
   distinct values on `ab_quota_ledger` (`{3: 23, 4: 2, 2: 1, 0: 1}`) and moved
   between rounds on this very artifact — PA-06's pass-1 judge gave a 4 where
   every other judge gave 3. The reframing is right about D2 and arguable about
   D3, and the "9 of 15" figure it rests on is wrong. The underlying caution —
   that an exact reproduction across a constant dimension is weaker evidence than
   it reads — is carried in `RESULTS.md` §2 without the number.

Channel A additionally **parked** five `scripts/*.py` rather than filing them
(`tla_spec_dev.py`, `generate_docs.py`, `scaffold_spec.py`, `close_tickets.py`,
`generate_cases_from_tlc_dump.py`), on the boundary between a verdict about a
subject and a precondition failure — *"so the epic owner gets twelve unarguable
omissions rather than seventeen with five to litigate."* Recorded here so the
judgement is visible rather than silent, which is the registry's own standard.

---

## What each channel REJECTED

The highest-yield question this project has, asked of each agent about its own
work.

### Channel A — the enumeration

- **The `R-H5` lead itself.** Already fixed: `instruments.toml` carries a comment
  recording the FI-02 → FI-03 collision and moves the id to `R-H9`. Confirmed
  `R-H9` is free and the demonstration fires on it. **Not a finding.**
- **`scorecard-audit` reporting 7 violations instead of 1.** *"I saw this and
  nearly filed it. It is an artifact of my own scratch copy — I rsync'd without
  `.git`, and `audit` resolves claims against commit history."* Re-run against
  the real tree: green. **Withdrawn.** (Real downstream note: `audit`'s verdict is
  git-dependent and degrades to **red** rather than to "unverifiable".)
- **`corpus-diagnostics` having no `expect_output`.** Reproduced; the red names
  the stated cause exactly. Weak pinning, correct verdict. Not filed.
- **`tla-complexity-descriptor` firing on a missing file.** Disproved — it
  refuses on the `INSTANCE` construct, not on the absent module.
- **`dispatch-record`'s two-string expectation being partly incidental.**
  Disproved by removing the mutation and keeping the staging: both strings vanish.
- **`catalogue-integrity`, `blinding-sanitiser`, `kill-test-boundary-coverage`.**
  All three reproduced and the red names the seeded break. Clean.
- **The nine cli rows whose `passing` argv mirrors the `failing` argv.**
  Initially flagged; *"on inspection the mirror is the point — same argv,
  mutation present vs absent — which is a stronger attribution than most rows
  have."* Rejected as a finding. **This is what makes `FI-06-DF-03` sharp: the
  two rows it does file are the ones with no mutation at all.**
- **`run_tlc.sh`, `skill-scripts/install-*.sh`.** Usage and prerequisite errors,
  which the registry's preamble explicitly excludes. Correctly out.

### Channel B — the divergence

- **That the mutant fails to apply to arm B.** Disproved: `applied_exactly_once:
  true`, `occurrences_of_find: 1` on every row of every arm, in the sealed
  artifacts and in the re-run.
- **That it is a mapping or re-anchoring miss.** Disproved: every `find` string
  occurs exactly once in its own arm.
- **That the cells were fudged, or the sealed results are not reproducible.**
  *"Disproved emphatically. Independent corpus regeneration, independent runs,
  zero cells moved across all 13 column-slots. FI-04's measurement discipline is
  genuinely good; the problem is what the cells mean, not whether they are
  real."*
- **That `arm_b_fake.py` is an epic-authored artefact, making `:fake` a harness
  difference rather than a design difference.** *"Tried hard, rejected."* It calls
  only names in arm B's own `__all__` and follows arm B's own docstring verbatim;
  an arm-A equivalent is genuinely not constructible from arm A's public surface.
  **The asymmetry is real.**
- **That arm B's `:fake` column is broken or dead, so `SURVIVED` is an instrument
  failure.** Disproved: `FI-M15` and `FI-M17` both die on it, so the column
  executes both the domain and `InMemoryJournal`. **Arm B's `SURVIVED` is a true
  "not on the executed path", which is precisely why it is entailed rather than
  measured.**
- **That the predictions were amended after the runs.** Disproved for every
  `predicted_*` string. `FI-06-DF-09` is filed narrowly about the *selector* for
  that reason, and is not an accusation of prediction-editing.
- **That `FI-M15` is mislabelled "in-region" because it lives in `domain.py`.**
  Declined — "in-region" means the port's region variables, defined explicitly in
  the catalogue header. Consistent usage.

### Channel C — generator versus suite

- **That the shipped script's arithmetic is wrong.** *"Attacked hardest, held
  completely."* All five tables recomputed per column and per mutant id,
  including both sealed row shapes, `NOT_DECIDABLE` handling and proper-subset
  dominance. **Zero disagreements.**
- **That the correction's arithmetic is wrong at the mutant-id level.**
  `BA-P11`/`BA-P05`/`BA-Q11`/`BA-Q05`, 11-11 and 10-10, the four-instrument
  attribution of `BA-P11`, and "neither the negative corpus nor the port corpus"
  — **all correct. The epic's §2 table is right in every cell.**
- **That `suite-fake` does not strictly dominate `corpus-port-swap:fake`.**
  Verified from three independent raw tables. It dominates, strictly, plus
  exactly two.
- **That the epoch-1 blind catalogue's mis-keyed `refine_variable` /
  `refine_action` suppressed its kills.** A good hypothesis, **disproved**:
  `kill_test.py` uses those fields only to compose the survivor-pointer message;
  they never enter the verdict. **The epoch-1 result is not a harness artifact.**
- **That `BA-A10` survived because the epoch-1 corpus was weaker.** Disproved:
  both epochs generate 43,128 cases from a byte-identical `.tla`; the 294-case
  execution difference is arm bindability, not corpus strength.
- **That `BA-P11` is a toy fault.** Rejected. *"Reusing a live reservation id so a
  later commit overwrites another tenant's hold is a genuine production-class
  defect."* The criticism filed is different: **the suite already runs the
  separating trace** (`tests/test_behavior.py:177`) and merely omits the
  assertion.
- **That the blind catalogue is a fraud.** Rejected as overreach. *"The channel is
  careful, self-reports its own leaks, documents rejected candidates. The problem
  is a design problem — the brief hands the author both instruments and asks for
  `gap_targeted` — not dishonesty."*

### Channel D — the scorecard

- **That the reported table is wrong.** *"It is not."* Every cell and every summed
  |movement| (9, 5, 7, 10, 13, 4) reproduced from the raw JSON without using
  `derive_movements.py`.
- **That the label mapping `T=Q, U=P` was fitted to the scores.** Rejected —
  documented independently in two `UNBLINDING.md` files that predate the scores,
  and the 38 `[[movement]]` entries pair the correct card paths. **No
  circularity.** (Standing note: it is a hand-typed CLI flag with no default and
  nothing validates it.)
- **That FI-03 buried the MISS.** *"It did not. Both documents open with `GOAL …
  is MISSED`, and the REJECTED section explicitly names reporting the flattering
  half as a move it declined. This is better practice than the framing in my
  brief assumed."*
- **That D3 is degenerate too.** *"It is not."* Attacked on floor/ceiling pinning,
  coarse anchors, judge-family collapse, and whether `4/2/1` is just artifact
  size. **None held. `ports-as-adapters`' headline on D3 survives.**
- **That the anchors moved between rounds and the digest hid it.** They did not —
  `eeccf4576bc6fd85` at all seven sampled commits. The filed defect
  (`FI-06-DF-11`) is the *mechanism* gap, not a substantive anchor change.
- **That the `check` gate rejecting `D4 = 4` with `executed_own_faults: false` is
  retroactive rubber-stamping.** Rejected: a v1 judge really did award D4 = 4 on
  all three artifacts while writing in its own REJECTED section that it had
  seeded nothing. **The gate is demonstrated, not hypothetical.**
- **That byte-identity is asserted rather than checked.** Rejected for the
  PA-06 → FI-03 leg, which is genuinely verified at the git tree-object level.
  The objection survives only for the EVAL-RERUN leg, whose blind copies were
  never committed.

---

## Things the channels noticed that nobody asked about

Carried forward because several are cheap and one is the best lead in the
repository.

- **`ResIds = {r1, r2}` is the single cheapest change here with a chance of
  moving a cell.** Four fault classes were recorded as invisible to *everything
  including the suite* by the HP-06 blind author — `guard_order`,
  `id_allocation`, `query_projection`, `durable_encoding` — and two of them sit
  behind this wall. No epic has proposed enlarging it.
- **`kill-table-arm-a-STALE-BINDING-DF-01.json` is a complete zero row for all
  six generated columns with `suite` at 10 of 11**, sitting in the same directory
  as the live tables with nothing but its filename marking it stale. Any reader
  picking tables by glob reproduces "the generator catches nothing" from it
  alone.
- **`wiring_notes` is written into every artifact and read by nothing.** The one
  sentence in the artifact that says the arm-A `:fake` cell decides nothing is
  invisible to the analysis that reads that cell.
- **Three of the five dimensions have no discriminating power on this example
  family.** D2 is constant at 2, D5 is 4 on 4 of 4 blind judges for arm C and
  `SELF-IMPROVEMENT.md:1071` already flags that *"D5 no longer separates anything
  at all"*, and D1 is 3 on 23 of 27. **That is a bigger finding about the card
  than the delta question is, and nothing in the repository states it in one
  place.** It is stated here.
- **The `NOTES.md` blinding leak is five rounds old with no fix.** `T`'s and
  `W`'s quote numbered sections of their own prompts and `U`'s does not — a
  direct arm signal inside the blind directory, reported independently by every
  judge in HP-06, EVAL-RERUN, PA-06 and both FI-03 passes.
- **The v2 judges' rubric is not recoverable from any commit.**
  `rubric_v1_frozen.md` archives the v1 arm's — good practice — but the v2 arm
  read FI-03's in-progress working-tree edit, pinned only by a digest that is
  blind to prose. `rubric_v2_frozen.md` would close it for one line.
- **`demonstrate.py` shells `uv` with no guard.** `FileNotFoundError` is caught by
  neither handler, so an environment without `uv` crashes the whole enumeration
  with a traceback instead of reporting 12 unrunnable slots.
- **`specs/desired_program_model/deferred_findings.yaml` does not load under
  `scripts/extract_spec_manifest.parse_simple_yaml`** — `unexpected indentation
  at '- examples/validation/PREDICTIONS-PA.md'`. **This predates FI-06**
  (confirmed on the parent commit) and the plan's two-loader rule covers
  `ticket_plan.yaml`, which does load under both. Recorded, not filed.
