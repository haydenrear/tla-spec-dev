# next epic — starter for the next epic owner

> **SUPERSEDED IN PART, 2026-08-04.** The static architecture scanners this
> charter plans repairs for — `scripts/analyze_architecture.py` and
> `scripts/architecture_reflexion.py`, `tla-spec-dev analyze architecture`, and
> the `architecture_scan` / `architecture_delta` model surface — were REMOVED by
> owner direction. Every finding below is still true; what changed is that the
> answer is not a repair. Read `references/architecture_advice.md` first: it
> carries the nine measured facts from this page forward as instructions to
> follow now and as the acceptance criteria any replacement must satisfy. The
> sections here remain the primary record of HOW each was measured — run
> directories, numbers, reproduction steps — which is why nothing below is
> edited.

You are starting a new epic. The previous one (`architectural-coherence`) was
**measured, not asserted**: EV-01 committed predictions before any dispatch,
EV-02 scored against them, two blind agents who had never seen the predictions
worked on sanitized fixtures, and the answer keys were enumerated by the owner
in advance. Read this before anything.

The rule that produced everything below: **a low or unflattering result is the
preferred outcome.** This epic exists in the shape it does because the
complexity-descriptor epic existed, and that one existed because a validation
agent was told exactly that and then found the suggested moves were confidently
wrong. Keep the standard.

---

## 0-A. READ FIRST — AMENDED AGAIN AFTER THE `hexagonal-prompting` EPIC (2026-08-04)

**Everything below §0 was written by the `architectural-coherence` epic. A newer
epic has since run and has OVERTURNED four of its conclusions.** Every one is
marked in place with a `HEXAGONAL-PROMPTING —` note; do not read a §1 or §3 claim
without checking whether it carries one. The four:

1. **"A generated corpus cannot see guard relaxation, ever" is FALSE** (§1). A
   generator mode that emits, per reachable state, the actions whose guards are
   DISABLED, asserted REJECTED, took the class **0 of 3 → 3 of 3** on the seeded
   catalogue, **5 of 5** on one fresh catalogue and **1 of 1** on another, on two
   real implementations. It was never a property of corpora; it was a property of
   *positive* corpora.
2. **"Ordering is invisible at every layer" is FALSE as stated** (§1). It is
   invisible when the modelled thing is a **set**. On a model whose ledger is a
   **sequence**, the ordering mutant dies on the whole-view corpus, on an aspect
   slice and under both provider mappings. Any citation now needs the
   set/sequence clause.
3. **"The mapping choice is worth 30% of that instrument's yield" MUST NOT BE
   QUOTED** (§1, §3). The *direction* has replicated five times on five fixtures
   and is solid. The *magnitude* has failed to reproduce four times: 1 of 6 on
   one fixture, **exactly one mutant** on each of two implementations here.
4. **D3 = 4 has been reached** — the first 4 on any dimension but D5 in this
   project's history — by asking for ports and adapters **in a prompt**, with no
   check, no schema and no gate. §2's NE-02 should be read knowing that.

**And the four sentences from the new round that matter most:**

1. **The prompt worked and the structure caught nothing.** D3 went 2/2 → 4/4
   between the control and the treatment arm. Every per-mutant kill verdict is
   **identical on 49 of 49 comparable cells**. A port did not detect one
   additional fault, and the treatment arm's own 41 tests appear in no kill
   table. If you are tempted to build architecture tooling because "modularity
   catches bugs", this round is the counter-evidence.
2. **The hand-written suite still beats the generator, and a catalogue nobody
   tuned beats them both down.** Seeded catalogue: suite 10 of 10, corpora 9 of
   10. **Fresh independently-authored catalogue: corpora 8 of 13, suite 9 of 13,
   and four whole classes invisible to every instrument including the suite.**
   A catalogue written by the author of the mechanisms flatters both instruments
   by roughly a quarter.
3. **The positive control is red and has been for two tickets.** The corpus
   recovers no `Reserve` argument, so no case that calls the primary command
   executes, so a fault seeded in it survives everything. **Fix this before
   anything else** — and know that fixing it turns a *second* control red
   (HP-06-DF-11), because the oracle re-derives a reservation id the model does
   not allocate that way.
4. **Findings by channel: 0 from the suite, 17 from an adversarial pass, 13 from
   a blind author.** Third round running. **The suite has stopped being
   informative** — 1,329 green assertions produced nothing anybody did not
   already know — and for the third time the most valuable single section of the
   record was an agent's answer to *"what did you reject?"*.

### The best finding of the new round is about a SPECIFICATION, not a tool

A blind author, given only the two implementations and the model, found that
**the model's COMMIT record has three fields where the feature's has four**. R2's
running-total clause is absent from the state machine entirely, and the
manifest's own port description describes a line the model never constructs. The
one mechanism with a measured, replicated edge — the content-asserting provider —
is a hand-written sentence patching a model that does not refine its own
specification.

The same agent found that the two arms **differ in unmutated code on crash
consistency** and that nothing in the fixture can see it; that the fixture
**leaks its own answer key** in files blind roles are permitted to read; and that
two whole fault classes are each held by exactly one assertion.

That is the fourth epic in a row in which the most valuable result came from an
agent READING something and noticing a specification was false of itself. No
metric contains it and no gate reaches it. **Budget for that channel explicitly.**

### What the next epic should probably do first

- **Repair `Reserve` argument recovery, then expect HP-06-DF-11 to fire.** Until
  the positive control is green, no kill number from a whole-view corpus on this
  fixture is a measurement.
- **Make a kill table auditable.** `KILLED` currently means "any exception", the
  failure text for every mutant run is computed and discarded, and 92% of a
  corpus is skipped with the per-case reason dropped. Every kill table this
  project has published shares that driver's ancestry.
- **Do NOT build an architecture checker.** The prompt reached D3 = 4 with no
  tool, and the epic before it proved every static check it shipped was defeated
  cheaply. But do not conclude the prompt "worked" either: 105 unique prompt
  lines against 16 means **this round cannot distinguish hexagonal guidance from
  a longer, more specific ask.** If that distinction matters, run the third arm.
- **Fix `eval_scorecard.md`'s D2, or say it is unreachable for an A/B.** Anchor 3
  needs a before and an after of the same artifact; two arms of one specification
  have neither, all four judges said so, and a goal was `missed` on a target no
  A/B could have hit.
- **Seed the class the blind author was least confident about rejecting**:
  durability across a failing write. It said, in the shape of the predecessor's
  wrong rejection, *"I am declining a class because the harness cannot currently
  reach it, not because the fault is unreal"* — and then proved the arms already
  diverge on it.

Full record: `specs/results/scorecards/hexagonal-prompting/RESULTS.md`,
`PREDICTIONS-SCORED.md` (7 PASS, 4 FAIL, and three of the four failures are
negative predictions), `FINDINGS.md`, `UNBLINDING.md`.

---

## 0. READ FIRST — this document was written after round 1 and amended after round 2

EV-02 (round 1) found 14 defects. The owner directed that they be **repaired
inside the epic** rather than deferred here, and six repair tickets landed
(RP-01..RP-05, RP-07). **EV-03 (round 2) then re-ran the whole eval suite against
the repaired tree and re-scored it against the SAME committed predictions**, with
two fresh blind runs on fresh scratch copies. The full comparison is
`examples/validation/runs/ROUND-2-DELTA.md`; the per-arm records are
`runs/ex4-run4..6`, `runs/ex5-run3..4`, `runs/ex6-run2`.

**Several conclusions below were written by round 1 and OVERTURNED by round 2.**
Every one is marked in place with a `ROUND 2:` note. Do not read a §1 or §3 claim
without checking whether it carries one.

The four sentences that matter most:

1. **The false `coherent` is fixed on the declaration path, exhaustively.** All
   203 partitions of the divergent fixture: **12 false cleans → 0**, with **zero
   divergence verdicts lost** and **20 previously-suppressed findings released**.
   The one-component partition that was round 1's headline now reports
   `unmappable` with both basis limits named.
2. **The bug-catching numbers did not move by a single cell.** ARM A 4 of 6, ARM
   B 6 of 6, guard relaxation 0 of 3, ordering 0 of 3 — identical to round 1,
   after a repair that took parameter recovery from 0 of 5 to **5 of 5**. The
   repair worked; the kill rate did not change. **That falsifies round 1's own
   explanation of why guard relaxation is unkillable** (see §1's corrected
   bullet).
3. **Case modules went from "generate" to "generate and run", and that is the one
   place a new detection capability actually appeared.** A blind agent's two
   authored aspects — 89 lines, 74 cases — killed **9 of 16** mutants against the
   330-case whole view's 10 of 16. It is a cost result, not a reach result: the
   bugs are ones the view already caught.
4. **A blind agent found a NEW major defect cheaper than anything round 1 knew
   about**, and the scorer reproduced it independently: `coherent` on a codebase
   with four real divergences, for a 41-line re-export file, with both digests
   unchanged, `blind_spots: []`, `basis_limits: []` and the behavioural suite
   green. **EV-03-DF-03.** It is the strongest argument that NE-02 is the next
   epic's real work, and it is a false clean the epic's own DP-1 scoring rule
   cannot see.

---

## 1. What the last epic learned (do not re-litigate)

`architectural-coherence` shipped four levers: an architecture **descriptor**
(AC-01), a **reflexion check** of code against the model's architecture
(AC-02), an **implementation brief** (AC-03), and an attributable **refactor
delta** (AC-04) — plus case modules (CM-01) and the eval fixtures (EV-01/EV-02).
Every claim below is a measurement with a run record behind it in
`examples/validation/runs/`.

### Survived, and is reliable

- **The divergence check is accurate when its basis is honest.** On the
  enumerated answer key: **precision 1.000, recall 1.000** — all four seeded
  divergences at the exact `file:line`, plus the one absence, plus **zero false
  positives on the coherent twin**. A check that finds divergence everywhere is
  as useless as one that finds it nowhere; this one does neither.
  (`runs/ex5-run1/`)
  **ROUND 2: reproduces exactly — same four `file:line`, same absence, zero false
  positives on the twin (`runs/ex5-run3/`). AND it is now known to be accuracy
  ON AN UNATTACKED TREE ONLY.** A 41-line re-export file through a nested
  first-party package takes the same fixture from `divergent` to `coherent` with
  both digests unchanged and no blind spot (EV-03-DF-03, `runs/ex5-run4/`).
  Never quote 1.000 without that clause again.
- **The refusals hold on real targets.** This repository's own model reports one
  component, Q = 0.000, `unmappable`, and single-writer ownership **NOT
  MEASURABLE** rather than "zero violations". The synthetic Jenga reports
  `unmappable` via `unfalsifiable_coherence`. Both exit 0. (`runs/ex6-run1/`)
  **ROUND 2: holds, and both refusals now name the decomposition basis too
  (`runs/ex6-run2/`). Newly measured: this repository's own DECLARED
  four-component partition does NOT decompose its own model (Q = −0.025,
  crossing 0.6), so `coherent` is not a verdict this repository could earn today
  even with a perfect extractor. The AC-02 note in `ticket_plan.yaml` still says
  otherwise — EV-03-DF-01.**
- **AC-04's delta cannot be gamed, and this was attacked directly.** Against
  the maximal gaming move — collapse the whole partition to one component and
  re-place all eight modules — it reports `direction = unattributable`, names
  every re-placed module, classifies each lost edge `endpoint_reassigned` ("the
  edge did not go away; the boundary it crossed did"), and reports **stable
  basis 0 → 0**. DP-7 predicted the refusal would hold. It holds.
  (`runs/ex5-run2/`)
- **Content-asserting effect providers catch what nothing else catches.**
  Per fault class, per arm, green control both arms:
  **ARM A (corpus alone) 4 of 6; ARM B (corpus + content provider) 6 of 6.**
  The two survivors under ARM A are exactly the two durable-side faults, killed
  under ARM B by `provider_content_assertion` and by nothing else.
  (`runs/ex4-run1/`)
  **ROUND 2: identical, cell for cell, detector for detector, point count for
  point count (`runs/ex4-run4/`). Independently replicated a third time by a
  blind agent on a fresh 16-mutant catalogue: 3 of 3 durable-write mutants killed
  by the checking mapping, 0 of 3 by the silent one — 30% of that instrument's
  entire yield (`runs/ex4-run6/`).**
  **HEXAGONAL-PROMPTING — THE 30% DOES NOT REPRODUCE AS A PROPORTION. DO NOT
  QUOTE IT.** HP-05 measured the mapping worth 1 of 6 under the checking mapping
  and 1 of 10 overall on a second fixture; HP-06 measured it worth **exactly one
  mutant on each of two further implementations** (`map-checking` 2 of 2,
  `map-silent` 1 of 2, plain corpus 1 of 2, identical on both arms). The
  DIRECTION has now replicated five times on five fixtures and is solid. The
  MAGNITUDE is fixture-dependent and is not a property of the mechanism.
- **Determinism, including the half nobody had tested.** Generation is
  byte-identical (the same `cases.py` sha256 EV-01 recorded, across worktrees,
  output paths, and two Python interpreters five minor versions apart).
  Execution is byte-identical across two independently generated corpora over
  **14 executions including twelve FAILING ones** — a corpus deterministic only
  when it passes is not a deterministic corpus. Seeded failures **replay
  exactly** from the command the runner prints: three faults, both arms, each
  replayed twice, all six reproducing the originating error string.
  (`runs/ex4-run2/`)
  **ROUND 2: 38 of 38 executions byte-identical, 24 of them failing ones, plus
  the case-module corpora which round 1 could not even generate in place
  (`runs/ex4-run5/`). The corpus fingerprint MOVED, from `33e07e0de…` to
  `944189052623960aea…` — that is RP-02's recorded content change, not a
  determinism failure, and the fixture's `evidence/corpus_fingerprint.txt`
  carries both with the reason.**
- **Case modules generate, and the tool refuses to oversell them.** 14 authored
  lines → 50 cases; 22 authored lines → 6; the view is 330; and `coverage`
  states unprompted, every run, that the union of aspects is not the view.
  (`runs/ex4-run1/`)
  **ROUND 2: they now also RUN. RP-03 made the checked-in modules generate in
  place (round 1: exit 150) and fixed parameter recovery across `EXTENDS`, which
  round 1 never reached — the slice went 0/50 → 50/50 arguments and the Given
  0/6 → 6/6, and the Given's corpus executes against the project's unchanged
  adapters. A blind agent then used two authored aspects as real instruments and
  measured 9 of 16 mutants from 74 cases (`runs/ex4-run4/`, `runs/ex4-run6/`).**

### Killed, or badly wounded

- **`coherent` can be obtained on a divergent codebase, for about six lines of
  YAML, and nothing flags it.** Enumerating all 203 set partitions of the
  divergent fixture's variables: 12 report `coherent`, and **all 12 fail the
  model's own decomposition criteria while zero of the 12 honest partitions
  produce a clean.** The criteria are a perfect discriminator and the reflexion
  check does not consult them. Worse, the **fully degenerate case is not
  caught**: a declared ONE-component partition on a codebase with four real
  divergences reports `coherent`, exit 0, `blind_spots: []` — because the
  `unfalsifiable_coherence` guard is written `len(names) >= 2` and excludes the
  one blob it exists for. `divergence_detectable` is computed as `false` and no
  consumer reads it. **EV-02-DF-01.** (`runs/ex5-run2/`, `runs/ex6-run1/`)
  **ROUND 2 — FIXED BY RP-01, AND MEASURED ON THE SAME INSTRUMENT. The sweep
  rerun: 12 false cleans → 0, all 203 exit 0, and — the part that had to be
  checked — ZERO divergence verdicts were lost and 20 previously-suppressed
  findings were released (71 → 91 `divergent`).** The mechanism is a
  `basis_limits` list (seen in full, clean withheld) kept SEPARATE from
  `blind_spots` (could not see); verified independently, 67 of round 1's 71
  divergence verdicts carry `partition_does_not_decompose`, so folding the two
  together would have suppressed 67 real findings to remove the same 12 false
  cleans. **DP-2 re-scored MISSED → CAUGHT; DP-2b CONFIRMED → CLOSED on the
  measured path.** (`runs/ex5-run3/`) **This closes the DECLARATION route to a
  false clean. It does not close the CODE route — see EV-03-DF-03 below.**
- **The mitigation already exists and lives in the wrong artifact.** AC-03's
  `prompts/implementation_brief.md` documents this exact defect by name and adds
  Gate B: `V1` refuses a 1-component declared partition, `V3` degrades on
  `crossing_action_fraction > 0.5`. AC-03 is a **prompt**; AC-02 is a
  **program**. The check a human must remember is enforced; the check a program
  could enforce is not. Part of EV-02-DF-01.
  **ROUND 2 — FIXED. The basis now travels with the verdict in both the text and
  the JSON (`basis.partition_decomposes`, `partition_criteria`,
  `partition_failed_criteria`, `clean_result_supportable`,
  `unsupported_clean_reasons`). Round 1 measured that the word "decompose"
  appeared zero times in the reflexion output; it now appears with every
  criterion and its measurement. NE-01(3) was honoured: the declared partition is
  never REFUSED — the comparison runs, findings keep their `file:line`, exit stays
  0, and what is withheld is only the word `coherent`.**
- **The reflexion check measures static import topology, not interaction.**
  Found by the blind agent, verified: the seeded absence proves it from one side
  — `dispatch` and `ledger` interacted the whole time via a parameter, and with
  no import the tool called it dead architecture. In reverse, pass a function as
  an argument or annotate a type as a string and the divergence vanishes while
  the coupling survives. **Nothing in the tool distinguishes a real refactor
  from that dodge.** (`runs/ex5-run1/`)
  **ROUND 2 — NOT FIXED, and now much worse than round 1 understood. This epic
  touched none of it, which was the plan. What round 2 added is the price: a
  blind agent, told only to make the report clean, found that
  `architecture_reflexion.py` decides first-party-outside-`--code` by testing ONE
  path (`code_root.parent / name`), so a first-party package nested at
  `generated/pkg`, `src/pkg` or `vendor/pkg` is silently filed as third-party.
  Consequences, both reproduced independently by the scorer: (a) moving
  `pipeline_contract` up one directory on the COHERENT fixture, changing zero
  bytes of Python, flips `coherent` → `unmappable` — so this epic's only positive
  architecture result is conditional on directory depth; (b) a 41-line re-export
  shim plus one decorative import turns the DIVERGENT fixture into `coherent`,
  0 divergences, 0 absences, `blind_spots: []`, `basis_limits: []`,
  `clean_result_supportable: true`, both digests identical to the answer key,
  8/8 behavioural tests green, runtime coupling fully intact.
  **EV-03-DF-03, major.** DP-1's scoring rule cannot see it: no declaration
  moved. This is NE-02's whole case, made concrete.**
- **Anything outside `--code` is free.** Push cross-component wiring into an
  unscanned composition root and the codebase reads coherent by construction; a
  DI-heavy service passes trivially. The blind run demonstrated this **in its
  own fix** — it edited `tests/driver.py`, outside the scanned root, invisible
  to the check that then scored it clean. The adjacent tricks *are* guarded
  (unmapped modules force `unmappable`; suppression-shaped map keys are reported
  and never honored). Scoping is not.
  **ROUND 2 — NOT FIXED, and the hazard is wider than "scoping". Round 1 recorded
  it as `--code` being POINTED somewhere convenient. EV-03-DF-03 shows the same
  hazard reachable with `--code` unchanged, by ADDING A FILE. Round 2's blind
  agent also edited `tests/driver.py` — outside the scanned root — exactly as
  round 1's did, so that half replicates too.**
- **A generated corpus cannot see guard relaxation, ever.** It replays only
  ENABLED edges, so it contains no rejected inputs: a service that accepts what
  the model forbids passes every case. Compounded by the adapter recovering the
  action argument from the case's after-state — the oracle hands it the
  argument. Found independently by the blind agent (0 of 3 guard mutants) and
  by EV-01 as DF-01. **This is why "4 of 6 beats MF-038's 0 of 9" is an upper
  bound and must never be quoted without it.**
  **ROUND 2 — THE CLAUSE ABOUT THE ADAPTER IS FALSE AND IS RETRACTED.** RP-02
  removed the oracle leakage completely: parameter recovery went **0 of 5 → 5 of
  5**, all 330 cases carry a real argument, and the adapter reads
  `case.input.params` and never touches `case.after`. **Guard relaxation stayed
  at 0 of 3.** Not one cell of the mutant matrix moved, on either arm, on either
  catalogue. RP-02 counted the reason: all 330 recovered arguments are arguments
  the guard ACCEPTS, 0 are rejected inputs, and 220 refusable pairs exist in the
  state space that a TLC state graph can never emit. **So the oracle leak was
  real, is gone, and was NEVER what made guard relaxation unkillable — the whole
  of the remaining failure is the structural half.** Independently replicated a
  third time by a blind agent on a fresh catalogue: **0 of 4 guard-accepts on all
  five corpus instruments, 4 of 4 on the hand-written suite**, with the mechanism
  found from scratch (`330 'status': 'applied'` — the corpus never once asks the
  program to reject a call). (`runs/ex4-run4/`, `runs/ex4-run6/`)
  The "4 of 6 is an upper bound" caveat is now **narrower**: the leak is gone, so
  4 of 6 is a measurement rather than a ceiling. It remains one fixture, six
  faults, and a corpus that cannot see two whole classes.
  **HEXAGONAL-PROMPTING — OVERTURNED. THE HEADLINE OF THIS BULLET IS NOW FALSE.**
  "A generated corpus cannot see guard relaxation, ever" was true of a corpus
  built from ENABLED edges only. HP-03 built a generator mode that emits, at each
  reachable state, the actions whose guards are DISABLED there, asserted
  REJECTED. Guard relaxation went **0 of 3 -> 3 of 3** on HP-01's seeded
  catalogue and **5 of 5** on a fresh independent one, and HP-06 reproduced
  **3 of 3 under `corpus-neg` on two real implementations**, against 0 of 3 for
  every other generated instrument in the same run. The class is not structurally
  unreachable; it was unreachable *from a positive corpus*. The rest of the
  bullet — that recovering the argument does nothing, that the state graph has no
  edge for a transition that did not fire — is still exactly right, and is why
  the fix had to be a new emission mode rather than better recovery.
- **Ordering is invisible at every layer.** `ledger` and `queue` are TLA+ sets;
  the code implements them as ordered lists documented "append-only". The
  projector sorts, the adapter uses `frozenset`, the provider compares
  `sorted()`. A ledger that silently reverses is undetectable by any of the
  three. **Modeling gap, not a tool bug — and no case module can fix it.**
  **ROUND 2 — NOT FIXED, confirmed again, and now confirmed to be invisible to
  the HAND-WRITTEN SUITE as well.** Round 1's blind catalogue: 0 of 3 ordering
  mutants killed by the corpus. Round 2's blind catalogue: **0 of 2 killed by
  ANYTHING — five corpus instruments and the behavioural suite.** The agent
  traced all four layers unprompted and reached round 1's conclusion
  independently: it needs a MODEL change, not a test change. (`runs/ex4-run6/`)
  **HEXAGONAL-PROMPTING — OVERTURNED, AND THE CORRECTED CLAIM IS NARROWER.**
  "Ordering is invisible at every layer" is a property of THIS MODEL, not of
  corpora. It is invisible when the modelled thing is a **set**; `ledger` and
  `queue` here are sets, which is the whole of the reason. On a model that
  represents its ledger as a **sequence**, HP-03's ordering mutant M09 DIED on
  the whole-view corpus, and HP-06 reproduced that on both arms — killed by
  `corpus-whole`, by the ledger aspect slice and by both provider mappings,
  surviving only the negative corpus and the reservations slice, neither of which
  projects the ledger. **Anything citing "ordering is structurally invisible" now
  needs the set/sequence clause.** The second half of round 2's note also stands
  corrected: on a sequence model the hand-written suite kills it easily.
- **X-P3 fails.** Six of eight friction items in the blind aspect run were
  documentation insufficiency, not tool defects, and the root of most of them is
  that **every published command path assumes an external view**. An
  internal-only project has no worked example anywhere in the repo.
  **EV-02-DF-05.** And a checked-in case module **cannot be generated from where
  the convention puts it** (TLC cwd, no module search path, exit 150):
  the shipped convention and the shipped tool disagree. **EV-02-DF-02.**
  **ROUND 2 — EV-02-DF-02 IS CLOSED** (generation resolves the `EXTENDS` closure
  and hands SANY the directories it found; the checked-in modules regenerate in
  place with byte-equal output, and the diagnosis for an unresolvable `EXTENDS`
  is one sentence before the JVM starts). **The internal-view worked example
  exists and runs verbatim end to end. EV-02-DF-05 is PARTLY CLOSED: the
  external-view assumption and the `--out` / `--import-root` frictions are fixed;
  NO INTERPRETER IS PINNED ANYWHERE, and no `python3` on the eval machine's PATH
  carries `yaml`, `pytest` and `tomllib` together — hit again by both round-2
  blind agents. X-P3 still FAILS, with 8 items again — but four of round 1's
  eight are gone and the round-2 items are different ones, including two new
  toolchain defects: `--effect-report PATH` silently writes nothing and exits 0
  (EV-03-DF-04), and `analyze architecture` without `--components` silently
  substitutes an emergent partition for the declared one (EV-03-DF-05).**
- **"A non-author can write an aspect" holds for SLICES and fails for GIVENS.**
  A slice needs action names; a Given must constrain every variable of the view
  and know every guard. The Given is the form with the **best** measured
  result — see below — so the mechanism with the strongest number is precisely
  the one that cannot be written from outside, and no document says so.
  **EV-02-DF-04.**
  **ROUND 2 — DOCUMENTED, not "fixed", because the asymmetry is a FACT and not a
  defect.** `references/case_modules.md` now states it as a table of what each
  form requires and where that knowledge lives, and names the split that makes a
  Given commissionable from outside (the outsider supplies the CLAIM, someone
  with the model writes the predicate). Round 2's blind agent followed exactly
  that split unprompted and said so in its report. Step 0's provenance
  requirement is now LABELLED UNENFORCEABLE with a contract in place of a guard —
  and the round-2 agent opened its report with "No author was in the loop… **This
  decomposition is UNREVIEWED**" before quoting a single number. That is the
  contract working. It is still not a control: `case_modules.py validate` exits 0
  on an authorless decomposition without a murmur. (`runs/ex4-run6/`)
- **CM-F5 — a slice narrower than its view orphans the view's effect providers.
  STILL OPEN, and sharper than RP-03 filed it.** The runner refuses a mapping
  that configures an effect provider no selected case requires. On a whole view
  that is correct; on a slice it is normal, because slicing is what makes an
  aspect narrower. RP-03 said the workaround is "a second mapping file with the
  provider removed" — **but the fixture SHIPS two mappings and both bind the
  port, so the slice has ZERO working configurations and the workaround requires
  a third file that exists nowhere.** Round 2's blind agent hit this without
  knowing it existed, lost 3 of its 15 actions to it, authored the third mapping,
  and made the point nobody else had: **that mapping is a strictly weaker
  instrument** — it has no durable-write oracle, so its slice's kills are a floor
  and a green slice run over-reads unless you read its mapping.
  **So the cheapest outside-in artifact — a slice, the only form writable from
  action names alone — is still the one that cannot run end to end, and the form
  that runs is the one that cannot be written from outside.** EV-03-DF-02.

### Scored against the committed predictions

| prediction | outcome |
|---|---|
| prediction | round 1 | ROUND 2 |
|---|---|---|
| A1-P1..P6 (kill table, per class per arm) | **all PASS**, every per-fault prediction exact | **all PASS, identical numbers** |
| A1-P7 (the wrong-item class is unmeasurable) | stated as a limit | **SUPERSEDED by RP-02** — it was killable all along, before the fix as well as after |
| A2-P1..P3 | PASS | **PASS**, and A2-P3 completed: a module corpus now EXECUTES |
| A2-P4 (aspects not derivable) | PASS, sharpened | **PASS**, and the artifact now carries the caveat |
| A3-P1..P4 (determinism, replay) | **all PASS** | **all PASS**, 38 executions vs 14 |
| AC-P1..P6 (answer keys, refusals, exit 0) | **all PASS** | **all PASS**, unchanged |
| DP-1 (agent redraws the map) | **PASS at n=1** | **PASS at n=1 again** — both digests at answer-key values, 0 deletions — **and the rule is now known not to catch the cheapest attack (EV-03-DF-03)** |
| DP-2 (`unfalsifiable_coherence` catches the degenerate case) | **MISSED** | **CAUGHT** |
| DP-2b (declared partition failing all criteria reports a real-looking clean) | **CONFIRMED**, 12 of 203 | **CLOSED on the measured path**, 0 of 203 |
| DP-3, DP-5, DP-6, DP-7, DP-8 | **PASS** | **PASS** (DP-7 not re-exercised — no `--baseline` delta was taken in round 2) |
| X-P1, X-P2, X-P4 | **PASS** | **PASS** |
| X-P3 (docs suffice) | **FAIL**, 6 of 8 items | **FAIL**, 8 items again — 4 of round 1's 8 are gone, the round-2 items are different ones |

**The DP-1 honesty note.** DP-1 predicted that at least one run would redraw the
map rather than fix the code. One blind run was dispatched; it did not — all
four declarations byte-identical, only production code moved, recall 1.0 on the
answer key, unprompted. That is a real result and it is **n = 1**. DP-1
predicted a rate, and one honest agent is evidence about one agent under one
prompt. Recording it as "DP-1 disproved" would be exactly the overclaim this
epic was built to avoid. Two things must travel with the PASS: **three of the
four divergences were cleared by DELETING dead code, and the metric cannot tell
deletion from refactoring**; and the agent's own report says the cheapest way to
get clean was **editing the model**, which it declined on judgment, not because
anything stopped it.

**ROUND 2's DP-1 note.** A second blind agent, on a differently sanitized copy,
also chose the code. Both declarations byte-identical, both digests at the
answer-key values, `tests/test_behavior.py` untouched, recall 1.0 unprompted,
8/8 green. **Better than round 1 on attribution: zero deletions.** It considered
deleting the three uncalled helpers as the fastest clean and rejected it in
writing ("it makes the check pass by deleting the subject rather than by fixing
it"), then removed each cross-boundary dependency while preserving every
helper's output byte-for-byte. **n = 2, and DP-1 predicted a RATE — still not
falsified.**

And the part that matters more than the PASS: **the agent tested three dishonest
routes and reported them instead of taking one.** One of the three works, is
cheaper than the honest fix, is invisible to the map a reviewer reads, and is
invisible to DP-1's own scoring rule. That is EV-03-DF-03. **The centrepiece
experiment's value in round 2 was not the verdict; it was the report.**

### The finding worth more than any mechanism this epic shipped

Working from the public README alone, the blind aspect author found that
**the public surface is false of the model**:

```
Fail(i)   ==  i \in delivered  /\  delivered' = delivered \ {i}  /\  failed' = failed \cup {i}
Record(i) ==  i \in delivered  /\  i \notin ledger  /\  ledger' = ledger \cup {i}
```

Once an item fails it leaves `delivered`, so it can **never** reach the ledger —
while the README promises "a failed item is recorded as failed" and "the ledger
records each outcome", and the model's own `LedgerIsDownstream` invariant
reserves room for exactly the behavior the model then makes unreachable.

**No case module could ever catch this.** A case module may not add an action,
and there is no action to enter; a corpus can only test behavior the model has.
**The value came from the human-facing act of authoring the aspect, not from the
cases it generated.**

This is the one result in the epic that no prediction contains and no metric
measures. It is the strongest available argument for the manual-test-starter
path **and its strength is not expressible as a kill rate.** Whatever the next
epic builds, it must not optimize the aspect surface for kills and lose this.

**ROUND 2: IT REPLICATES.** A second blind agent, on a differently sanitized
copy, found the same contradiction from the README alone — and added three facts
round 1 did not have: (1) `LedgerIsDownstream` permits a state no action can
reach, so the real invariant is strictly stronger and the written one passes
vacuously on the half that matters; (2) the behavioural suite asserts the same
weak property and therefore cannot fail; (3) `test_two_item_interleaving`
asserts the **negation** of the README sentence, so whoever fixes the promise
must change a passing test. **A result that reproduces across two agents, two
sanitizations and two rounds is not an anecdote.** (`runs/ex4-run6/`)

---

## 2. What the next epic should build

Four pieces, in dependency order. Each one is a fix for something above that was
**measured**, not for something that sounds wrong.

**ROUND 2 STATUS OF NE-01..NE-04, up front:**

| | round-1 charter | status after the repair tickets + EV-03 |
|---|---|---|
| **NE-01** put the basis in the report | the highest-severity finding | **DONE by RP-01**, acceptance met exactly (12 → 0 over 203, 0 findings lost, 20 released). **Remove it from the charter.** |
| **NE-02** measure interaction, not imports | the real work | **UNTOUCHED, and now the top priority** — EV-03-DF-03 gives it the negative fixture it was told to build first, already built |
| **NE-03** the oracle's blind spots | guard relaxation, ordering, parameter recovery | **parameter recovery DONE by RP-02 — and it changed no kill.** Guards and ordering untouched, and both re-confirmed from outside |
| **NE-04** the aspect surface as a design review | docs, an authoring aid, fix DF-02 first | **DF-02 DONE by RP-03**, the asymmetry and Step 0 documented, case-module corpora now EXECUTE. **CM-F5 is the remaining blocker** |

### NE-01 — DONE by RP-01. Do not re-open. *(round-1 text kept for the record)*

~~The highest-severity finding, and the cheapest fix in the epic.~~ **RP-01
landed all three changes and EV-03 measured the acceptance criterion on the
instrument that found the defect: the 203-partition sweep reports 0 `coherent`,
zero divergence verdicts were lost, and 20 previously-suppressed findings were
released. The one thing to carry forward is the design decision RP-01 made and
measured: the refusal is a BASIS LIMIT (withholds a clean, never a finding),
kept separate from a BLIND SPOT (could not see) — filing it as a blind spot
would have suppressed 67 of 71 real divergence verdicts to remove the same 12
false cleans. Keep that distinction; it is load-bearing.** Three changes, all
additive, none of which lets the tool choose a boundary (CD-01 removed
that, permanently):

1. **Delete the `len(names) >= 2` clause** in
   `architecture_reflexion.py:921`. A one-component declared partition is the
   *strongest* case of `unfalsifiable_coherence`, not an exception to it.
   `divergence_detectable == false` must force `unmappable` on its own instead
   of being computed, reported in JSON, and ignored by the verdict.
2. **Move AC-03's Gate B from the prompt into the program.** Carry
   `partition.decomposes`, the failed criteria, and the V1/V3 tests into the
   reflexion text report and into `basis.partition_decomposes` in the JSON.
   `coherent` measured against a partition the model does not support is a
   different claim from `coherent` measured against one it does, and the report
   must say which it is.
3. **Do NOT refuse a declared non-decomposing partition.** Carry the fact, not
   the judgment. A project may have good reasons for a boundary the modularity
   metric dislikes; it may not have them silently.

Acceptance: re-run `runs/ex5-run2/artifacts/df02_blast.py`. The 12 false cleans
must become 0 `coherent` — as `unmappable` or as `coherent (basis: does not
decompose)`, the epic's choice, but never as an unqualified clean.
**MET. The rerun is `runs/ex5-run3/artifacts/df02_blast_round2.py`, and its
output is `runs/ex5-run3/artifacts/blast.json`.**

### NE-02 — measure interaction, not imports. **NOW THE TOP PRIORITY.**

The check's accuracy (precision 1.000, recall 1.000) is real **and is entirely
about static import topology**. **ROUND 2 raised this from "the next epic should
decide" to "the next epic must fix this first", because a fourth evasion was
found, it is cheaper than the other three, and it is invisible to every scoring
rule this epic wrote:**

- **THE ONE TO FIX FIRST — a re-export through a nested first-party package
  (EV-03-DF-03).** `architecture_reflexion.py` decides first-party-outside-
  `--code` by testing exactly one path, `code_root.parent / name`. A package at
  `generated/pkg`, `src/pkg`, `gen/pkg` or `vendor/pkg` is one level too deep and
  is silently filed as third-party. Measured both ways: moving the fixture's
  generated package up one directory, with zero Python changed, flips `coherent`
  → `unmappable`; and a 41-line re-export shim turns the divergent fixture into
  `coherent` with **0 divergences, 0 absences, `blind_spots: []`,
  `basis_limits: []`, both digests identical to the answer key, and 8/8
  behavioural tests green**. The fix is entirely in the DETECTION — resolve
  first-party-ness against the project root and the `sys.path` the project
  itself installs — and **no verdict rule changes**, because
  `first_party_outside_code_root` already forces `unmappable` and is already
  never downgraded. Ship a regression test in the `TestNothingDowngrades…` shape
  that pins the nested case specifically.

The three round-1 evasions, all still confirmed:

- **Parameter-passed collaborators.** The seeded absence in the fixture is a
  worked example of the tool being wrong in the *safe* direction (reporting dead
  architecture where a real interaction existed). The unsafe direction is the
  same blindness.
- **The composition root.** The coherent fixture's own README confesses it has
  nowhere to live: inside `--code` it gives its component an edge to everything;
  outside, it is free. **This has no answer today and the next epic must produce
  one** — a declared `composition_root:` exempt from port checks but *reported*,
  or a rule that a root must be mapped and its edges attributed to the
  components it wires. Pick one and measure it on a DI-heavy real service, not
  on a fixture.
- **Deletion vs refactoring.** The metric cannot tell them apart, and the one
  blind run cleared 3 of 4 divergences by deleting. Whether that matters is a
  judgment the epic should make explicitly rather than by omission.
  **ROUND 2 adds a third remedy nobody had counted: DUPLICATION.** The round-2
  agent cleared two divergences by copying a four-character format string into
  the other component, and observed that for every unported pair the tool's only
  accepted remedies are duplicate, push the dependency into the caller, or move a
  module in the map — so *"make the coherence check clean" is a standing
  instruction to duplicate across component boundaries*, and nothing in the
  report tells a reviewer that the diff which cleared the finding added
  duplication.
- **NEW (round 2) — ports are UNDIRECTED, so a layering violation inside a
  correctly-ported pair is invisible.** `ports[].between` is an unordered pair,
  but the model has a direction: `Record(i)` *reads* `delivered` and *writes*
  `ledger`, and the descriptor already computes `crossing_actions[].reads` /
  `.writes` per component. The reflexion half throws it away. This is a
  *different* gap from the documented "a ported pair hides a bad edge" — it is a
  bad edge hiding inside a **correctly** ported pair, and the data the fix needs
  already exists.
- **NEW (round 2) — a reporting helper weighs the same as the domain path.**
  Three of ex5's four divergences are operator-view helpers nothing calls; the
  fourth is a function-local import written specifically to dodge an import
  cycle. The report ranks them identically. "4 divergences" reads as four times
  as bad as one, and here it was one architectural fact stated four times. This
  re-frames the epic's precision/recall of 1.000: it is a count of **edges**, not
  of architectural facts.

Build the **negative fixture first**: a codebase that is genuinely coupled and
that the current check reports `coherent`. Until that fixture exists, "the check
is accurate" means "accurate on imports."
**ROUND 2 BUILT IT FOR YOU.** `runs/ex5-run4/artifacts/reexport_attack/` is a
codebase with four real, runtime-live cross-boundary dependencies that the
current check reports `coherent` with `blind_spots: []` — 41 lines of diff on
top of the shipped divergent twin, with the behavioural suite green. Start
there.

### NE-03 — the oracle's blind spots, named in the product

Two whole fault classes are invisible **by construction**, and both were found
independently from outside:

- **Guard relaxation.** A generated corpus contains only enabled edges. The fix
  is not more cases; it is a **negative corpus** — the disabled edges at each
  reachable state, asserted to be REJECTED. TLC already knows them. This is the
  single largest available increase in what the corpus can see, and it is a new
  generator mode, not a tuning knob.
- **Ordering.** Sets in the model, lists in the code, `sorted()` at every oracle
  layer. Either the profile grows sequences, or the toolchain **says in the
  descriptor** that a set-typed variable implemented as an ordered collection is
  unobservable. Saying it is cheap and honest; growing the profile is neither.
- ~~**Parameter recovery (EV-01-DF-01).**~~ **DONE by RP-02, and the result is
  the most important negative in this document. Recovery went 0 of 5 → 5 of 5,
  all 330 cases carry a real argument, the adapter no longer reads `case.after`,
  and the audit is rendered from the corpus it audits. THE MUTANT MATRIX DID NOT
  MOVE A SINGLE CELL.** Guard relaxation stayed 0 of 3 on both arms, and RP-02
  counted why: 330 of 330 recovered arguments are arguments the guard ACCEPTS, 0
  are rejected inputs, and 220 refusable pairs exist in the state space a state
  graph can never emit. **Do not budget any of NE-03's guard work against
  parameter recovery — that hypothesis is dead.** The remaining caveat on the
  kill numbers is narrower than round 1's: the leak is gone, so 4 of 6 is a
  measurement rather than a ceiling; it is still one fixture and six faults.

Ship the corpus and the hand-written suite as **complements with a per-class
table**, never as one kill rate. **Measured twice more in round 2, on the
repaired tree.** RP-02's reconstruction: guard relaxation 0/3 corpus, 3/3
pytest. A fresh blind 16-mutant catalogue: view corpus **10/16**, hand-written
suite **10/16**, **union 14/16**, and the two they both miss are both ordering.
Guard-accepts: **0 of 4 on all five corpus instruments, 4 of 4 on pytest.**
Neither instrument dominates and neither is close.

### NE-04 — the aspect surface as a design review, not only a generator

The unplanned results point the same way twice:

- ~~60 authored lines → 38 cases that killed **exactly** what the 330-case
  whole-view corpus killed. An **8.7× reduction at zero measured loss** on a
  12-mutant catalog. The Given divides and holds.~~
  **ROUND 2 RETIRES THIS HEADLINE.** With a mutant deliberately placed in the
  gap, **74 case-module cases reached 9 of the whole view's 10 kills**, not 10.
  The one lost is a `Fail` that misbehaves only when the work queue is still
  non-empty — a before-state the Given asserts away and the slice never reaches.
  Round 1's "zero measured loss" was a property of round 1's catalogue, not of
  the Given. The round-2 agent's warning, verbatim: *"Do not read a 'case
  modules == view' result off a catalogue that has no cross-aspect mutant in
  it."* It also corrected the vocabulary: on this profile every case is ONE
  action against a materialized before-state, so "cross-aspect interleaving" is
  not about call orderings at all — it is about **before-state diversity**, and
  that is exactly where the loss lives. The honest claim is still good and it is
  smaller: **9 of 10 of the view's kills, from 22% of the cases, for 89 authored
  lines.**
- The Given cannot be written from outside (EV-02-DF-04), and the act of trying
  to write one is what surfaced the model/README contradiction. **Round 2: both
  halves replicate** — a second agent split claim-from-outside and
  predicate-from-inside exactly as RP-03's asymmetry table describes, and found
  the same contradiction.
- **NEW (round 2) — on a small model the cost argument does not apply at all.**
  The round-2 agent measured the whole view generating in 0.95 s and executing
  330 cases in 0.23 s, against `references/case_modules.md`'s headline of
  1m 23s → 2.2s, and concluded that on this project a case module is worth
  writing for what it **documents** and for nothing else: *"the `case_modules:`
  block plus the claim comment is genuinely the best-written statement of intent
  in the repository, and it is 34 lines."* **The reference leads with the wrong
  benefit for small models.** That is a docs finding and it is sharper than
  A2-P2.

So: state the precondition per form in the docs ~~; give the Given an authoring
aid~~; make Step 0's provenance checkable or delete it. **ROUND 2 STATUS: RP-03
did the docs half. The asymmetry is a table in the reference and at the point of
authoring; Step 0 is LABELLED UNENFORCEABLE with a contract in place of a guard,
and the round-2 blind agent honoured that contract unprompted — it declared its
decomposition UNREVIEWED before quoting a number. Still not a control:
`case_modules.py validate` exits 0 on an authorless decomposition. The Given
authoring aid was NOT built and is still open.**
~~And **fix EV-02-DF-02 first**~~ — **DONE by RP-03; modules generate in place
and their corpora now carry recovered arguments and EXECUTE.**
**THE REMAINING BLOCKER IS CM-F5 (EV-03-DF-02): a slice narrower than its view
orphans the view's effect providers, and on the shipped fixture NO mapping can
run a slice's corpus — the documented workaround requires a third mapping file
that does not exist, and the one you write has no durable-write oracle.** Fix
that first now: it is the first thing a new author hits after generation
succeeds, and the instrument they end up with is weaker than the one they think
they have.

---

## 3. Do NOT re-litigate

**ROUND 2 HEALTH WARNING ON THIS SECTION.** Round 1 wrote it. Round 2 overturned
two of its entries and had to weaken a third. A "do not re-litigate" list is only
as good as its willingness to retract, so the retractions are first:

- **RETRACTED — "a generated corpus cannot see guard relaxation … *compounded by
  the adapter recovering the action argument from the case's after-state*".**
  The compounding clause was wrong. RP-02 removed the leak entirely (0 of 5 → 5
  of 5 parameters, adapter never touches `case.after`) and **guard relaxation
  stayed at 0 of 3 on both arms, with the whole mutant matrix unchanged.** The
  cause is structural and only structural: a state graph has no edge for a
  transition that did not fire. Do not spend a ticket on parameter recovery
  expecting kills.
- **RETRACTED — "the wrong-item class is a class this instrument cannot
  measure".** `seeded_faults.toml` declined to seed one on that reasoning. RP-02
  seeded two and **both were killed, before the fix as well as after.** The
  refusal to seed was over-cautious; the class belongs in a future catalogue.
- **WEAKENED — "the divergence check is accurate (precision 1.000, recall
  1.000)".** True, and true only of a tree nobody attacked through a nested
  first-party package. EV-03-DF-03 obtains a full `coherent` on the divergent
  fixture for 41 lines, with both digests unchanged and no blind spot. Quote the
  1.000 with that clause or not at all.
- **WEAKENED — "the Given divides and holds, 8.7× at zero measured loss".** See
  NE-04: with a mutant placed in the gap it is **9 of the view's 10 kills**, not
  10. The zero-loss result was a property of the catalogue.

Everything below this line still stands.

- **Advisory, not blocking.** Nothing in this line of work refuses a close, a
  promotion, or a case generation. Every fixture exits 0, including the
  `divergent` one. Do not propose an architecture gate; the complexity gate
  already failed every normal program and the pivot is settled.
- **No suggested moves (CD-01).** The tool does not propose a cut, a refactor,
  or a module move. EV-02-DF-01's fix is to *carry a fact*, not to pick a
  boundary. A tool that picks the boundary makes every edge legal by
  construction. **Round 2: RP-01 shipped exactly that and it worked. Keep the
  discipline for EV-03-DF-05 too — naming a declaration the run did not use is a
  fact, not a suggestion.**
- **The map and the partition are DECLARED, never inferred.** This is not a gap;
  it is the design. The gameability that follows is the price, and AC-04's
  attribution refusal is the mitigation that works. Do not "solve" gaming by
  inferring the map.
- **`unmappable` is never downgraded.** No flag, key, annotation, or environment
  variable turns it into `coherent`. Suppression-shaped map keys are reported
  and never honored. Keep it that way. **Round 2 re-verified this across all 203
  partitions and on both refusal fixtures, and blind run A attacked it directly
  with a partition coarsening and got `unmappable`. It held.**
- **NEW (round 2) — `basis_limits` and `blind_spots` are DIFFERENT LISTS and must
  stay different.** A basis limit withholds a *clean* and never a *finding*
  ("I saw everything; the yardstick does not support the word `coherent`"). A
  blind spot says "I could not see". RP-01 measured the alternative: filing
  `partition_does_not_decompose` as a blind spot removes the same 12 false cleans
  **and suppresses 67 of 71 real divergence verdicts to do it.** Do not merge
  them for tidiness.
- **The single-writer violations on the pipeline fixture are CORRECT OUTPUT.**
  `queue` and `delivered`, both written by `Deliver`: the handoff mutates both
  sides in one step, so it is simultaneously the port and the violation. That is
  the atomicity-fidelity signal. A report that names them scores correct; a
  scorer that counts them as false positives has miscalibrated the key.
- **Emergent partitioning is greedy and mostly vacuous on real models** — and
  "neither real model decomposes" was itself overclaiming: exhaustive
  enumeration of all 115,975 partitions of this repo's model finds 2 that meet
  every criterion, at Q = 0.003. The doctrine survives; the wording was
  corrected on the epic branch. Do not re-derive either half.
- **Generation determinism is settled.** Measured four times now across two
  epics, two interpreters, and three output paths, always byte-identical. Keep
  it as a control precisely because it always passes; do not spend a ticket
  re-proving it. The risk was always **execution**, and that half is now
  measured too. **Round 2 makes it seven measurements, now including the
  case-module corpora and 24 FAILING executions, and it adds the rule that goes
  with it: a fingerprint that changes because a ticket deliberately changed
  generated content is NOT a determinism failure. RP-02 moved the ex4 corpus
  fingerprint from `33e07e0de…` to `944189052623960aea…`; the fixture's
  `evidence/corpus_fingerprint.txt` carries both values with the reason, and
  that is the pattern to copy.**
- **MF-038's 0-of-9 is not superseded.** ARM A reproduces it on exactly the
  faults MF-038 was made of. The improvement to 4 of 6 comes from a
  **content-bearing output projection** (MF-038's own first recommendation), and
  the last two kills come from a **content-asserting provider**. Attribute per
  mechanism or the number is uninterpretable. **Round 2 reproduced the whole
  table cell for cell and a blind agent reproduced the arm split independently on
  a fresh catalogue (3 of 3 durable-write mutants under the checking mapping, 0
  of 3 under the silent one). The mapping choice is worth 30% of that
  instrument's yield. Never report a kill number without naming its mapping.**
  **HEXAGONAL-PROMPTING: the "30% of that instrument's yield" clause is
  withdrawn — see the note at §1. "Never report a kill number without naming its
  mapping" is stronger than ever and HP-05 made the announcement automatic.**

---

## 4. How to run it

- Branch off the current `epic/architectural-coherence` tip. You inherit the
  four levers, the case-module surface, and the six eval fixtures.
- **The open findings are in `specs/desired_program_model/deferred_findings.yaml`.
  Round 1 filed EV-02-DF-01..05; RP-01/RP-02/RP-03 closed DF-01, DF-02, DF-03 and
  documented DF-04, and DF-05 is PARTLY closed. Round 2 filed five more:**
  - **EV-03-DF-03 (major)** — the re-export / nested-first-party false clean.
    **This is NE-02 and it is the top of the list.**
  - **EV-03-DF-02 (minor)** — CM-F5 sharpened: a slice has zero working shipped
    mappings. This is NE-04's remaining blocker.
  - **EV-03-DF-04 (minor)** — `--effect-report PATH` silently writes nothing.
  - **EV-03-DF-05 (minor)** — `analyze architecture` without `--components`
    silently substitutes an emergent partition for the declared one.
  - **EV-03-DF-01 (minor)** — the AC-02 "falsifiable-and-clean under a
    four-component partition" claim in `ticket_plan.yaml` is false on the
    repaired tree and still on record.
- **Re-score against `examples/validation/PREDICTIONS.md`**, and commit new
  predictions **before** any dispatch. The predictions in that file are what
  made "as expected" a usable phrase in this epic; six of them were wrong, and
  knowing which six is the whole value.
- Run each example at least twice. Every mechanical arm in EV-02 was run twice
  and the divergence was zero; that is a result, and it is only a result because
  it was checked.

### Eval protocol, corrected by this run

- **EV-02-PROTO-01 — redaction that announces itself is a weak blind.** The
  sanitizer left `\* --` comment stubs in the model; the agent noticed and said
  so. Ship a purpose-written neutral fixture variant, not a stripped one.
- **EV-02-PROTO-02 — a blind run's mutant catalog must be an artifact.** The
  aspect run's 12 mutants were applied in place and restored; no catalog
  survives, so its numbers cannot be re-scored. Blind runs that measure kills
  must ship a `seeded_faults.toml`-shaped file the way EV-01 did.
- **Compare the ARCHITECTURE digest, not only the map digest.** DP-1's scoring
  rule was written against the map. The blind run's own report names editing the
  model as the cheapest way to get clean; the model digest is the only thing
  that would catch it.
  **ROUND 2 APPLIED THIS AND FOUND ITS LIMIT. Both digests were compared and both
  were unchanged — and the run's own report then described a route to `coherent`
  that moves NEITHER. A digest rule can only catch a lie told in a declared
  artifact. EV-03-DF-03 is told in ordinary Python. The next round's DP-1 scoring
  must also diff the PRODUCTION TREE for new indirection — or, better, re-run the
  check with the extractor fixed and see whether the clean survives.**
- **Pin the interpreter.** No `python3` on PATH carries both `yaml` and
  `pytest`, and `python3` under `timeout(1)` resolved to a different interpreter
  than in an interactive shell. State an absolute path in the validation README.
  **ROUND 2: still not done in the docs, and hit again by both blind agents.
  EV-03 solved it for itself by building a uv venv with `pytest` + `pyyaml` on
  CPython 3.13 (which also has `tomllib`) and pinning it for every measurement —
  that is the step no document tells anyone to take. EV-02-DF-05 stays open.**

### Eval protocol, corrected by ROUND 2

- **A sanitizer must PRESERVE LINE COUNTS when the answer key is `file:line`.**
  Round 2's sanitizers assert it per replacement and refuse the whole run
  otherwise (`runs/ex5-run4/artifacts/sanitize_runA.py`), and the sanitized copy
  was verified before dispatch to reproduce the identical divergence sites and
  the identical digests. Purpose-written neutral text that moves a line is a
  silently corrupted answer key.
- **Make the blind MECHANICAL, not a promise.** Round 2 gave each agent a trimmed
  toolchain copy (`scripts/`, `references/`, `prompts/`, `SKILL.md`) with
  `examples/` and `specs/` removed, so the answer key was unreachable even by
  accident, and ran a token scan over the sanitized tree before dispatch.
  Note the cost, recorded so it is not double-counted: the trimmed copy makes the
  agent report "documented artifact does not exist" for things that DO exist in
  the repository.
- **EV-02-PROTO-02 WORKED — keep it.** Instructing the blind run to ship its
  mutant catalogue as a file produced 16 mutants with exact `find`/`replace`, a
  harness that asserts each pattern occurs exactly once, and a JSON matrix. Every
  number in that run is re-derivable, which round 1's was not.
- **Ask the blind agent to enumerate what it REJECTED, and to test the cheap
  routes.** Round 2's biggest finding came from the "considered and rejected"
  section, not from the work. The prompt asked for "anything you considered and
  rejected, including any approach that would have produced a clean report faster
  than the one you took" — and the agent tested three, one of which works and
  defeats the epic's own scoring rule.
- **Seed a mutant IN THE GAP the mechanism is supposed to lose.** Round 1's "case
  modules kill exactly what the view kills" was an artifact of a catalogue with
  no cross-aspect mutant in it. Round 2's agent seeded one deliberately and the
  claim moved to 9 of 10. A reduction result with no mutant in the gap is not a
  measurement.

---

## 5. Standing constraints (unchanged, non-negotiable)

- **Never merge to `main`** and **never run `skill-manager sync`** without
  explicit owner say-so.
- **Never invoke `tla-spec-dev` from PATH** — it execs a stale installed clone.
  Use `python3 scripts/tla_spec_dev.py --spec-root specs ...`.
- **Run pytest with `--with pyyaml`** or the YAML-validity guard skips silently.
- **Validate `ticket_plan.yaml` after every edit.**
- The tool serves a **constrained v0 TLA+ profile**, not arbitrary TLA+. Both
  invisible fault classes in §2/NE-03 are properties of that profile, and
  widening it is a decision with a cost, not a bug fix.
- **Findings are FILED, never fixed inline, during a measurement.** A fix during
  measurement destroys the measurement. EV-02 filed five and fixed none; **EV-03
  filed five and fixed none, including the major one it found in the very tool it
  was measuring.**

---

## 6. Epic-owner discipline that paid off, again

Predictions committed before dispatch; answer keys enumerated by the owner and
not by the agent under test; agents never shown the predictions; two arms
declared as two mappings rather than one mapping with its assertions switched
off, so a reader of the record can see which instrument produced a number.

That last one is the reusable trick. **DP-8 — "an EV-02 number reported without
naming its arm is uninterpretable" — is the reason this epic has a 4/6 and a 6/6
instead of a single misleading number**, and the reason the blind aspect run
reported a per-class table instead of "5 of 11". Apply the same split to any
future claim: separate the mechanism you are selling from the mechanism that did
the work, in the artifact, before the measurement runs.

And the standing one: **an epic that closes with only good news about itself has
not been measured.** This one closes with an accuracy result of 1.000 and a
six-line YAML file that makes it say `coherent` on a codebase with four
divergences. Both are true. Ship both.

---

## 7. What round 2 changes about how to read all of the above

The repairs were **measured, not assumed**, and the measurement was scored
against the predictions round 1 had already committed. Three things came out of
that discipline that no amount of arguing would have produced:

1. **A repair that worked and changed nothing.** RP-02 closed a real oracle leak
   and the kill matrix did not move a single cell. Nobody predicted that. It
   killed a hypothesis that had been in this document as a fact.
2. **A repair whose second-order effect had to be checked separately.** RP-01
   removed 12 false cleans; the number that mattered was whether it removed any
   TRUE findings to do it. It removed none and released 20. Had that not been
   measured, "12 → 0" would have been indistinguishable from a tool that had
   simply learned to refuse everything.
3. **A defect nobody was looking for**, found because a blind agent was asked what
   it *rejected* and not only what it *did*, and reproduced because the scorer
   did not take its word for it.

**The six-line YAML file in the paragraph above no longer works.** A 41-line
Python file does. Ship that too.

### The one-sentence answer to "does this catch harder bugs now?"

**No — it lies less.** It stopped certifying 12 things it had not measured, it
started running case-module corpora it previously could only generate, and it
kills exactly the same bugs it killed before, cell for cell. The classes it
cannot see are structural, they were re-confirmed three times in round 2 by
instruments that had never heard of them, and none of them moved.
