# Scorecard — ab_quota_ledger, artifact `H`, judge pass 1

`run_id`: `20260806-sm04v2-H-p1` · scorecard_version 2 · rubric `specs/results/scorecards/subtract-to-measure/SM-04/rubric_v2_frozen.md` digest `sha256:3bd59f9fe2ab699b`

**You are scoring artifact `H`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block is recorded, never scored

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. It sits beside the judgement so a reader can see when the two disagree — **and a disagreement is a finding, not a rounding error.**

## The rubric you are scoring against

### The scoring rules

1. **Score artifacts, never claims.** A summary saying "the adapters assert content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped at 1, mechanically, by the schema check.
3. **Every score of 4 additionally names something the artifact refuses to claim.** The top of every scale requires a stated limit. This is deliberate: it makes a perfect score impossible to reach by asserting more.
4. **Prose quality is never an input.** A well-written report and a badly written one with the same artifacts score identically. Say so in the rationale if the writing tempted you.
5. **Two judges, independently, blind to each other.** Any dimension where they differ by more than 1 is recorded as `contested` and adjudicated by a third pass that must cite new evidence, not re-read the same lines.
6. **Blind to arm.** Where an eval has arms (with-prompt vs without), judges do not learn which artifact came from which until after scoring.
7. **The mechanical block is recorded, never scored.** Kill counts, complexity figures, case counts, determinism, runtime. It sits beside the judgement so a reader can see when the two disagree — and a disagreement is a finding.
8. **Say what you ran.** *(New in version 2.)* Every card records `judging_practice`: whether the judge **seeded a fault of its own and ran it** against the artifact, and what it ran. Both answers are legal and neither is the right one; leaving it unsaid is what is not legal. **D4's anchor 4 is only awardable when it says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. This is the anchor's own text made checkable, not a new bar.

**Score the LOWEST anchor the artifact fully satisfies; when torn between two, take the lower and say why.**

### Judging practice — REQUIRED, and it is a field on the card

**Did you seed a fault of your own and run it against this artifact, or did you score the evidence packet?** Both are legal. Neither is the right answer. What is not legal is leaving it unsaid.

Fill `judging_practice` in `scorecard.json`: `executed_own_faults` true or false, and `what_was_run` listing what you actually ran.

**D4's anchor 4 is only awardable when this says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. If you did not run one, the highest D4 you can support is 3 — say that the packet asserts it and you did not verify it.

### D1 — bug detection

*Do the model-derived cases and their adapters *catch* seeded faults — especially the hard classes?*

- **0** — Cases exist and pass; no seeded fault is caught. A suite that is green on broken code.
- **1** — Catches faults that change a value the projection already prints. Misses everything requiring a content assertion.
- **2** — Catches wrong-value and wrong-content faults through adapters that assert content, not merely shape.
- **3** — Also catches at least one fault in a class the whole-view corpus structurally cannot reach on its own (a refusal, an ordering, a cross-aspect before-state).
- **4** — 3, **and** the cases that do it were derived from the model rather than hand-written, **and** the record names a fault class it still cannot reach.

### D2 — complexity

*Is the design as simple as its behavior requires, and no simpler?*

Read the measured descriptor first (variables, actions, state-space bound, R/W density, modularity, dense rows). Then judge whether the numbers reflect essential behavior or accidental structure.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state, no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the before and after figures are both recorded.
- **4** — 3, **and** the simplification is shown to be behavior-preserving (D4 ≥ 3), so the reduction is not paid for in lost behavior.

> **A drop in a complexity number is not evidence on its own.** MF-020: a metric can improve because an edge was deleted. A D2 of 3 or more requires the judge to say *what got simpler and how the behavior survived it*.

### D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

### D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

### D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

### Judging practice — your answer

**Executed own faults:** **true**

**What was run:**

- Copied `quota_ledger.py`, `test_quota_ledger.py` and `examples/validation/ab/tests/test_behavior.py` to a scratch tree outside the repository. **Nothing inside the repository was modified except this card and its JSON.**
- Baseline on unmutated code: **60 passed** (28 shared + 32 the artifact's own), which confirms both counts `NOTES.md` claims.
- Seeded **12 faults of my own plus 1 behaviour-preserving negative control**, each a single exact-string perturbation, applied to a scratch copy, run, then reverted with a `sha256` byte-identity check on the revert:
  - `durable_content` — J01 stale running total on `COMMIT`, J02 `CLOSE` total zeroed, J03 wrong verb
  - `guard_relaxation` — J04 `amount < 1` relaxed to `amount < 0`, J05 outstanding-reservations guard dropped, J06 reserve guard order swapped
  - `cross_aspect` — J07 `commit` also refunds the hold
  - `ordering` — J08 `outstanding_ids` sorted as strings, J09 ledger lines reversed on read
  - `wrong_value` — J10 `release` stops refunding `available`, J11 reservation id reuse
  - `refusal` — J12 `release` silently accepts an unknown id
  - `JN01` (my own negative control) — a behaviour-preserving rewrite of `_has_outstanding`
- Ran the shared suite and the artifact's **own** suite **separately** against every fault, so the artifact's contribution could be told apart from the shared floor.
  - The artifact's own suite killed **12 of 13** — everything except **J10**.
  - The shared suite missed **J06, J08 and J11**; the artifact's own cases killed all three.
  - **JN01 survived both**, so neither suite is pinning something that is not behaviour.
- Re-ran J10 by hand in a clean directory with `-B` to rule out a stale `.pyc`: confirmed the artifact's 32 tests pass with the refund deleted from `release()` while the shared suite fails 3.
- **Instrumented the artifact's own randomized sweep** (`test_quota_ledger.py:315-362`) with its own seed against the **pristine** artifact, counting accepted commands: **1 reserve, 1 commit, 0 releases, 3 closes — 395 of 400 commands rejected**, all three tenants closed by step 30. Its own anti-vacuity guard at `:358-362` passes anyway.
- Probed the D3 swap **by calling, not by reading imports**: passing an in-memory ledger object in the `ledger_path` position raises `TypeError` from `Path()`; rebinding the module-private global `quota_ledger._LedgerFile` does work and produces correct lines from a fake.
- Read: the artifact's four files, `examples/validation/ab/FEATURE.md`, `examples/validation/ab/tests/test_behavior.py`, and my own card. Nothing else.

## Your scores

### D1 — bug detection

**Score:** **3**

**Citations** (`file:line`):

- `artifact_U/test_quota_ledger.py:37-39` — `file_lines()` reads the ledger back off disk, independently of `ledger_lines()`
- `artifact_U/test_quota_ledger.py:85-88` — exact durable `COMMIT` line content asserted against the file
- `artifact_U/test_quota_ledger.py:91-94` — exact durable `CLOSE` line content asserted against the file
- `artifact_U/test_quota_ledger.py:162-170` — `test_outstanding_ids_are_ascending_past_ten` (an ordering case)
- `artifact_U/test_quota_ledger.py:255-262` — `test_reserve_rejection_order_is_the_declared_one` (a refusal-ordering case)
- `artifact_U/test_quota_ledger.py:145-151` — ids are not reused after commit or release
- `artifact_U/EVIDENCE.md:111-120` — `guard_relaxation`: `corpus-whole` 0 of 3
- `artifact_U/EVIDENCE.md:81` — `N01` outstanding-id order: SURVIVED on all eight instruments

**Refuses to claim:** _n/a (not a 4)_

**Rationale:**

Executed, not read. **Anchor 2 is met by code, not by claim:** `:37-39` reads the file
from disk rather than through the accessor, and `:85-88` / `:91-94` assert exact durable
content. My J01 (stale running total), J02 (`CLOSE` total zeroed) and J03 (wrong verb)
faults all died there.

**Anchor 3 is met three times over,** each time by a fault the shared whole-view suite
could not see and this artifact's own case could:

| my fault | class | shared suite | artifact's own suite |
|---|---|---|---|
| J06 reserve guard order swapped | refusal | **SURVIVED** | KILLED (`:255-262`) |
| J08 `outstanding_ids` string-sorted | ordering | **SURVIVED** | KILLED (`:162-170`) |
| J11 reservation id reuse | wrong_value | **SURVIVED** | KILLED (`:145-151`) |

J08 is the strongest of the three: the packet's own `N01` row (`EVIDENCE.md:81`) shows
that exact ordering class **surviving every one of the eight instruments**, so it is a
class the corpus demonstrably cannot reach and this artifact's hand-written case does.
`EVIDENCE.md:111-120` independently confirms refusals are structurally out of
`corpus-whole`'s reach (0 of 3).

**Not 4, for two measured reasons.** The cases that do the reaching are explicitly
hand-written, and the artifact's one model-flavoured case is nearly vacuous on this code
(see D4). And the record names no fault class it cannot reach — while I found one it
cannot: **J10**, deleting the refund in `release()`, survived all 32 of the artifact's own
tests and was caught only by the shared suite.

Prose quality did not enter. `NOTES.md` is unusually well written and it tempted me; I
scored the `.py` files.

### D2 — complexity

**Score:** **2**

**Citations** (`file:line`):

- `artifact_U/quota_ledger.py:103-110` — the whole of the instance state, set in one constructor
- `artifact_U/quota_ledger.py:138-195` — the four commands and their disjoint write sets
- `artifact_U/quota_ledger.py:28-37` — the six rejection reasons collected once
- `artifact_U/EVIDENCE.md:310-328` — the measured descriptor

**Refuses to claim:** _n/a (not a 4)_

**Rationale:**

I read the measured descriptor first: 1 module, 151 code lines, 17 callables, 4 classes,
8 instance-state slots, **0 module state**, 10 branch points, max 4 in any callable,
`max_depth` 1. Those are proportional to a feature with four commands, five queries and
six rejection reasons.

**No god-state and no variable written from everywhere.** The seven fields set at
`:103-110` have small, disjoint write sets across `:138-195`: `_available` written only by
`reserve` and `release`, `_committed` only by `commit`, `_closed` only by `close_tenant`,
`_reservations` by the three reservation commands, `_next_seq` only by `_allocate`. The
vocabulary is collected once at `:28-37` instead of restated per call site, which is why
`branch_points` stays at 10.

**Anchor 3 is not met and cannot be.** Nothing records a simplification with a before and
an after. The mechanical block compares *three different artifacts*, which is
cross-sectional, not a before/after of a change made to this one — and the MF-020 caveat
forbids reading a lower column as a measured reduction. I therefore cannot say *what got
simpler and how the behaviour survived it*, which is exactly what a 3 requires of me.

### D3 — modularity

**Score:** **2**

**Citations** (`file:line`):

- `artifact_U/quota_ledger.py:72-92` — `_LedgerFile`: every filesystem operation in the artifact
- `artifact_U/quota_ledger.py:110` — `self._ledger = _LedgerFile(ledger_path)`, the adapter hard-constructed
- `artifact_U/quota_ledger.py:168`, `:193` — the only two crossings, both `self._ledger.append`
- `artifact_U/EVIDENCE.md:322` — `declared_interfaces` = **0** for this artifact
- `artifact_U/EVIDENCE.md:48-52` — `corpus-port-swap:fake` runs the REAL implementation when no second one is shipped

**Refuses to claim:** _n/a (not a 4)_

**Rationale:**

There is a real seam and the code keeps to it. Every file operation lives inside
`_LedgerFile` (`:72-92`); `QuotaLedger` never opens, reads or writes a file — its only
crossings are `self._ledger.append` at `:168` and `:193` and `self._ledger.lines` behind
`ledger_lines`. That is anchor 2.

**It is not anchor 3, and I checked by calling, not by reading imports,** per the caveat.
`__init__` hard-constructs its adapter at `:110` and types the parameter `Path | str`, so
there is no injection point: passing an in-memory ledger object in that position raises
`TypeError` from `Path()` — the constructor *refuses* the swap. The only swap that works
is rebinding the module-private global `quota_ledger._LedgerFile`, which I ran
successfully — but monkeypatching a private name inside the domain module **is** touching
the domain. I cannot name a swap that satisfies anchor 3.

**Anchor 4 is unreachable and the packet says so itself:** `declared_interfaces` is 0
(`EVIDENCE.md:322`), and `EVIDENCE.md:48-52` states that `corpus-port-swap:fake` runs the
real implementation when no second one exists — which is why the fake and real columns are
identical on all eleven rows and constitute no evidence of a fake at all. I additionally
declined to lean on any port-binding column, because its declared positive control `M07` is
**red** there: SURVIVED where it must be KILLED, on 294 executed accepting `Reserve` cases.

### D4 — behavior preservation

**Score:** **2**

**Citations** (`file:line`):

- `artifact_U/quota_ledger.py:98-101` — R1 stated as a class invariant
- `artifact_U/test_quota_ledger.py:114-131` — R4 checked against the file over six rejecting commands
- `artifact_U/test_quota_ledger.py:133-139` — R5, append-only across many writes
- `artifact_U/test_quota_ledger.py:279-312` — `check_rules`: R1, R2, R3 recomputed from disk
- `artifact_U/test_quota_ledger.py:315-362` — the randomized sweep
- `artifact_U/test_quota_ledger.py:358-362` — the sweep's own anti-vacuity guard

**Refuses to claim:** _n/a (not a 4)_

**Rationale:**

**Anchor 2 is met.** All five rules are enumerated in the artifact and each is tied to a
case showing it holds: R1 at `quota_ledger.py:98-101` and rechecked at
`test_quota_ledger.py:289`, R2 at `:296-299`, R3 at `:302-310`, R4 at `:114-131`, R5 at
`:133-139`. I ran both suites myself: 60 passed on unmutated code.

**Anchor 3 is where I was torn. I took the lower, and here is why.** The artifact's only
claim to a model-derived rather than hand-written check is the randomized sweep at
`:315-362`, which recomputes R1/R2/R3 against an independent model at every step. I
instrumented that exact sweep, with its own seed `20260804`, against the **pristine**
artifact:

```
accepted in 400 commands:  1 reserve, 1 commit, 0 releases, 3 closes
rejected:                  395 of 400
all three tenants closed by step 30
final ledger: COMMIT acme 7 7 / CLOSE initech 0 / CLOSE globex 0 / CLOSE acme 7
```

The author **anticipated exactly this** and wrote a guard at `:358-362` — *"a sequence that
only ever rejected would prove nothing"* — and the guard passes on a single commit of 7. It
does not bite.

The consequence is measured, not theoretical: **J10** deleted the refund in `release()`, a
direct R1 conservation break of precisely the kind this sweep exists to catch, and it
survived all 32 of the artifact's own tests *including this one*, because the sweep never
reaches an accepting release. A check that never executes the transition it invariants over
is a hand-written suite with a random-number generator in it, not a model-derived corpus.

I considered awarding 3 on the strength of the packet's `corpus-whole` / `corpus-neg` runs
(3734 and 94 cases executed, 0 failed on unmutated code) **and rejected it**: that corpus is
generated from one shared model and is byte-identical for all three artifacts
(`cases.py` sha1 `08265aff…`), so it is a property of the harness and cannot be evidence
about what *this* artifact did. Anchor 4 is therefore out of reach on the anchor-3
prerequisite, even though `executed_own_faults` is `true` and 12 of my 13 changes were
caught — the failure is at 3, not at 4.

### D5 — honesty

**Score:** **3**

**Citations** (`file:line`):

- `artifact_U/quota_ledger.py:58` — `Result.rejected` asserts membership in the declared vocabulary
- `artifact_U/quota_ledger.py:114-116` — `available()` lets the lookup raise rather than inventing a sentinel
- `artifact_U/quota_ledger.py:164-166` — the comment naming the failure mode the write ordering avoids
- `artifact_U/test_quota_ledger.py:1-13` — what the shared suite does not cover, stated in the test module
- `artifact_U/test_quota_ledger.py:162-163` — a contested reading of "ascending" pinned in the case name
- `artifact_U/NOTES.md:87-106` — "What I was unsure about"
- `artifact_U/NOTES.md:60-63` — refuses to claim crash-safety
- `artifact_U/NOTES.md:125-129` — the disclosed `ls` slip

**Refuses to claim:** _n/a (not a 4)_

**Rationale:**

**Anchor 2 is met in the artifact itself and not only in a report.** In code:
`Result.rejected` asserts vocabulary membership at `:58`, so an undeclared reason cannot be
emitted at all; `:164-166` names the failure mode the write ordering exists to avoid;
`test_quota_ledger.py:1-13` states in the *test module* what the shared suite does not cover;
`:162-163` pins a contested reading of "ascending" in the case name.

**Anchor 3 is met by a refusal in the code, not a caveat about one.** `available()` at
`:114-116` lets the dict lookup raise on an unknown tenant rather than inventing `0` or
`None`, and `NOTES.md:87-94` gives the reason: the specification gives queries no rejection
channel, so no value is supportable and it declines to fabricate one. `NOTES.md:96-106` goes
further and names a hole in the *specification's* vocabulary — a non-integer `1.5` is
neither rejectable under the six reasons nor correct if held.

**I stopped at 3, and this is the anchor reading I want on the record.** Anchor 4 asks for a
**RESULT** in the record that is unflattering, and every result this artifact reports about
itself is green: *"28 passed"*, *"32 passed"*, and nothing else. What `NOTES.md:60-63` and
`:125-129` contain are self-reported *caveats* and one disclosed protocol slip — creditable,
and why this is a 3 rather than a 2, but a caveat is not a result. The one genuinely
unflattering measured result in the packet, the red positive control
(`control coverage … "positive": … "green": false`), belongs to the harness, not to this
artifact. And I have a measured reason to hold the line: the sweep at `:315-362` is reported
green while executing 5 accepted commands in 400. That is a positive verdict whose basis is
thinner than the artifact believes. It is not dishonesty — the artifact cannot see it — but I
will not award the top of an *honesty* scale to a record carrying an overstated green it has
not noticed.

## Verdict

A disciplined, content-asserting single-module implementation whose hand-written cases reach
refusal and ordering classes the shared corpus cannot, but whose one model-flavoured check is
nearly vacuous — 400 commands, 395 rejections, zero accepted releases — and consequently
misses an R1 conservation break that the shared suite catches.

**Total: 12** (D1 3 · D2 2 · D3 2 · D4 2 · D5 3)

## Disclosures

### What I saw that I was not meant to see

- **Nothing on the prohibited list was opened.** I did not read `references/eval_scorecard.md`,
  any arm prompt, any `PREDICTIONS*`, any `-p2` or `-v3` directory, `score_tools.py`, or any
  directory under `specs/results/scorecards/` other than `artifact_U/` and my own card. The
  one time I named `rubric_v2_frozen.md` was the mandated `score_tools.py check` invocation; I
  did not open it.
- **The label is not fully opaque and I should say so.** My card calls the artifact `H`, but
  the artifact directory I was pointed at is `artifact_U`, and `EVIDENCE.md:1` opens *"Evidence
  packet — artifact U"*, so `H` = `U` was never blind to me. The mechanical block
  (`EVIDENCE.md:310-328`) additionally puts U beside T and W on seventeen figures, so I know
  this artifact is the only one of the three that is 1 module with 0 declared interfaces while
  T has 4 modules and 1 declared interface. **I still do not know which arm produced it** — the
  with-prompt/without mapping is not in anything I read.
- **A redaction leaked its own shape.** `test_quota_ledger.py:1` reads *"this artifact's own
  tests"* and `NOTES.md:128` lists *"`this artifact/`"* inside a list of sibling directory
  names (`seeded_faults.toml`, `check_catalogue.py`, `reference/`). The phrase "this artifact"
  is standing where a directory name was, so I can tell the original text named an arm
  directory. I cannot tell **which** arm, and I did not try to work it out.
- **`EVIDENCE.md:9-10` cites `references/eval_scorecard.md` rule 7 by number.** I read the
  quoted sentence in `EVIDENCE.md` and did not open the file it points at.
- **`git status` showed me path names on the prohibited list.** I ran it after writing my card
  to prove I had not touched the tree, and it listed `…-H-p2/scorecard.json`,
  `…-rescore-v3/…-R-p1/`, `specs/desired_program_model/deferred_findings.yaml` and
  `tests/test_score_tools.py` as modified — i.e. other judges are working in this same
  worktree concurrently. I saw **only the file names in the status output**; I opened none of
  them and ran no `diff`. I note it because it also means my card is not the only change in
  this tree, and none of those other changes are mine.

### What I ran that changed anything

- Nothing in the repository was modified except this card and its JSON. All fault work was
  done on copies under
  `/private/tmp/…/scratchpad/judgeH1/`. Every fault was reverted with a `sha256`
  byte-identity check before the next one was applied.

### What I REJECTED

1. **D4 = 3, rejected — the most consequential call on this card.** The packet reports
   `corpus-whole` executing 3734 cases and `corpus-neg` 94 against this artifact with 0
   failures on unmutated code. That is genuinely model-derived and it is genuinely a check
   this artifact passed, and it was tempting. I rejected it because
   `EVIDENCE.md:56-57` says the corpus is generated from one model and one manifest shared by
   all three artifacts, byte-identical, `cases.py` sha1 `08265aff…`. Crediting it to the
   artifact would award every artifact the same 3 regardless of what it did, which converts a
   dimension into a constant. Rule 1 — *score artifacts, never claims* — cuts the same way for
   an instrument as for a summary: the corpus is not something this artifact built.
2. **D1 = 4 under a second reading, rejected.** If the shared model-derived corpora *were*
   counted as "the cases", then `corpus-neg` killing 3 of 3 guard relaxations would satisfy
   "derived from the model rather than hand-written". I rejected this for the same
   byte-identity reason, and separately because the second clause fails anyway: the record
   names no fault class it still cannot reach, and I demonstrated one (J10).
3. **D5 = 4, rejected — and I nearly gave it.** `NOTES.md:96-103` volunteers that a `1.5`
   amount would be held and committed and printed as `1.5`, which is close to self-reporting a
   bug; `:125-129` volunteers a protocol slip nobody would have caught. Both are unflattering.
   I put the score aside on the word **result**: anchor 4 asks the record to contain an
   unflattering *result*, and every measured number the artifact reports about itself is a
   pass. Reading "unflattering result" as "unflattering remark" would let a well-written
   caveats section buy the top of the honesty scale, which is the failure mode rule 3 exists
   to prevent.
4. **D3 = 3 on the strength of the `_LedgerFile` seam, rejected.** The seam is real and the
   code respects it perfectly, and on an import-topology reading it looks like a port. I ran
   the swap instead of reading it: the constructor *rejects* an injected adapter with a
   `TypeError`, and the only working swap rebinds a private global inside the domain module.
   The caveat asks what *calls* what at runtime, and at runtime `QuotaLedger` calls a class it
   chose itself.
5. **The port-binding table as evidence for anything, rejected wholesale.** All three of
   `corpus-action-bound`, `corpus-port-swap:fake` and `corpus-port-swap:real` carry a red
   positive control (`M07` SURVIVED where it must be KILLED, on 294 executed accepting
   `Reserve` cases). Under a red positive control those columns cannot distinguish a clean cell
   from a dead instrument, so I used none of the eleven rows in any direction — including the
   rows that would have flattered the artifact.
6. **`M09`'s retirement, not re-litigated.** `EVIDENCE.md:229-231` retires a negative control
   and explains why. I neither used it as evidence nor treated its retirement as suspicious;
   it is out of my scope and I note only that I noticed it and left it alone.
7. **A stale-bytecode explanation for J10, rejected empirically.** J10 surviving 32 tests while
   failing 3 shared ones looked enough like a caching artefact that I re-ran it by hand in a
   clean directory with `-B`. It reproduced. The finding is real, and the reason is the sweep's
   emptiness, not the runner's.
8. **`NOTES.md`'s prose, discounted deliberately.** It is the best-written document in the
   packet — it reasons about ambiguity, declines to over-build, and discloses against itself.
   Per rule 4 I recorded the temptation and scored the code: `NOTES.md` claims the sweep checks
   "R1/R2/R3 under a long randomized command sequence", and the sequence executes five accepted
   commands.

