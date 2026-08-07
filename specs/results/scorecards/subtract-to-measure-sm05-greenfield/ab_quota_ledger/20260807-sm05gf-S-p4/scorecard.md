# Scorecard — ab_quota_ledger, artifact `S`, judge pass 4

`run_id`: `20260807-sm05gf-S-p4` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `S`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. How to read it against your judgement is one of the numbered scoring rules below.

**Note:** this run's `mechanical.json` was scaffolded with empty `figures`. The mechanical block reproduced in the shared `EVIDENCE.md` packet (a cross-artifact table covering artifacts T/U/W) was used instead, since that is where the actual figures for this artifact live.

## The rubric you are scoring against

**This is the whole rubric, and it is reproduced here so the bar for a score sits in the same file as the score.** Do NOT go and read `references/eval_scorecard.md`. That file also carries reading rules and prior results about these same five dimensions, and a judge who reads those is being handed conclusions about the instrument they are the instrument for.

### The scoring rules

1. **Score artifacts, never claims.** A summary saying "the adapters assert content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped at 1, mechanically, by the schema check.
3. **Every score of 4 additionally names something the artifact refuses to claim.** The top of every scale requires a stated limit. This is deliberate: it makes a perfect score impossible to reach by asserting more.
4. **Prose quality is never an input.** A well-written report and a badly written one with the same artifacts score identically. Say so in the rationale if the writing tempted you.
5. **Two judges, independently, blind to each other.** Any dimension where they differ by more than 1 is recorded as `contested` and adjudicated by a third pass that must cite new evidence, not re-read the same lines.
6. **Blind to arm.** Where an eval has arms (with-prompt vs without), judges do not learn which artifact came from which until after scoring.
7. **The mechanical block is recorded, never scored.** Kill counts, complexity figures, case counts, determinism, runtime. It sits beside the judgement so a reader can see when the two disagree — and a disagreement is a finding.
8. **Say what you ran.** *(New in version 2.)* Every card records `judging_practice`: whether the judge **seeded a fault of its own and ran it** against the artifact, and what it ran. Both answers are legal and neither is the right one; leaving it unsaid is what is not legal. **D4's anchor 4 is only awardable when it says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. This is the anchor's own text made checkable, not a new bar.
9. **A judge is served the card, never the rubric file.** *(New in version 3.)* The scaffolded `scorecard.md` carries the rubric a judge needs. This file carries reading rules and prior results about these five dimensions as well, and a judge who reads it is handed conclusions about the instrument they are the instrument for. Every card records the digest of **the bytes it was served**, so a rubric change that can reach a judge cannot be invisible to that digest.

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

> **Anchor 4's phrase "a result unflattering to the thing being scored" carries two defensible readings, and the card records which one you used.** Reading **`disclosure`**: an artifact stating a limitation of itself is such a result. Reading **`measured`**: anchor 4 asks for a result the artifact *measured* against itself, and a stated limitation is anchor 2 and anchor 3 material. **Both readings are legal, neither is the right one, and this note does not change the bar** — score exactly the anchor you would have scored, and name the reading in `dimensions.D5.anchor_reading`. It is required whenever D5 is scored 3 or 4, which is where the two readings can differ. Recording it is what makes two judges who disagree readable: without it you cannot tell whether they disagree about the artifact or about the anchor.

### Judging practice — your answer

**Executed own faults:** true

**What was run:**

- Copied `quota_ledger.py` and `test_quota_ledger.py` to a scratch tree outside the repo. First ran both suites unmutated to confirm baseline: shared suite (`examples/validation/ab/tests/test_behavior.py`) — 28 passed; own suite (`test_quota_ledger.py`) — 32 passed. Matches the counts claimed in `NOTES.md:24,32`.
- Seeded my own fault, not one of the 11 in the packet: swapped the order of the `tenant_closed` and `amount_not_positive` guards in `reserve()` (`quota_ledger.py:142-145`), so a closed tenant reserving a non-positive amount would report `amount_not_positive` instead of the spec-mandated `tenant_closed` (`FEATURE.md:40-45` names the order explicitly).
- Ran the shared suite against the mutated code: **28 passed — fault NOT caught.**
- Ran the artifact's own suite against the mutated code: **31 passed, 1 failed** (`test_reserve_rejection_order_is_the_declared_one`, `test_quota_ledger.py:255-263`) — **fault caught**, by the artifact's own hand-written test, not by the shared suite.
- Reverted the mutation and deleted the scratch tree; nothing inside the repository was modified.
- Did **not** run the model-derived corpus (`corpus-whole`/`corpus-neg`/`corpus-port`) against this fault myself — I have no access to the case generator without reading files on the must-not-read list (`check_catalogue.py`, `seeded_faults.toml`), so I cannot say whether those instruments would catch it. This is a real gap in my own verification, named here rather than smoothed over.

## Your scores

### D1 — bug detection

**Score:** 3

**Citations** (`file:line` — the bar is in the scoring rules above):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:74` — mutant `M04-durable-stale-total`: `map-silent` (asserts nothing about content) SURVIVED, `map-checking` (asserts durable content) KILLED. Satisfies anchor 2: a content-asserting adapter catches what a shape-only one does not.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:111-119` — per-class block, `guard_relaxation`: `corpus-whole` 0 of 3, `corpus-neg` (model-derived, generated from the disabled edges of the model's state graph) 3 of 3. A class the whole-view corpus structurally cannot reach, caught by a different model-derived instrument — anchor 3's own example ("a refusal").
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:71-73` — mutant table rows `M01`-`M03`: SURVIVED under `corpus-whole`, KILLED under `corpus-neg`, confirming the class-level claim at the per-mutant level.
- My own independently-run fault (see `judging_practice`): a guard-**ordering** fault (which rejection reason wins when two guards fire), distinct from any of the 11 packaged mutants and from the packet's own "ordering" class (which is about ledger/id sequence, not guard priority — see `EVIDENCE.md:121-130`, whose two members are plausibly `M06` and the retired `M09`/`N01` pair, not a guard-priority swap). Caught by `test_quota_ledger.py:255-263`, not by `examples/validation/ab/tests/test_behavior.py`. This is additional, self-verified evidence of a class anchor 3 describes ("an ordering") that the whole-view/shared-suite combination does not structurally reach on its own.

**Refuses to claim** (required and non-null for a score of 4): n/a — not scored at 4.

**Rationale:** Anchor 2 is clearly met (content-asserting adapter beats shape-only). Anchor 3 is met twice over: once by the packet's own `guard_relaxation` class data, and once by a fault I seeded and ran myself that the shared hand-written suite missed entirely (28/28 passed on mutated code) and only the artifact's own test caught. I considered anchor 4 and rejected it: the main kill table's `class` column (`EVIDENCE.md:69`) is blank for every one of the 11 mutants, so which mutant belongs to which named class in the per-class JSON block is not stated, only inferable by cross-referencing SURVIVED/KILLED patterns across instruments — too shaky a basis to cite as "the record names a fault class it still cannot reach." Where the per-class data *is* legible (e.g. `wrong_value`), some model-derived instrument (`corpus-whole`, `corpus-slice-res`) always reaches it in full, so I could not find a class the model-derived apparatus as a whole misses. Score capped at 3.

### D2 — complexity

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:150` — `_available[tenant] -= amount`, written only in `reserve`.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:180` — `_available[reservation.tenant] += reservation.amount`, written only in `release`.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:170` — `_committed[reservation.tenant] = total_after`, written only in `commit`.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:194` — `_closed.add(tenant)`, written only in `close_tenant`. No state field is written by more than the commands whose behavior it exists to express.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:312-328` — mechanical block, artifact U column: 1 module, 151 code lines, 10 branch points (all of them in the single effectful module, `EVIDENCE.md:327`), 8 instance-state fields, for 4 commands + 5 queries and 6 declared rejection reasons.

**Refuses to claim** (required and non-null for a score of 4): n/a — not scored at 4.

**Rationale:** Each instance field is written by exactly the command(s) whose behavior needs it; there is no field mutated from every method (no god-state). Complexity is proportional to the six-rule, four-command feature it implements. I considered anchor 3 and rejected it: the mechanical block's T/U/W columns compare three *different* artifacts to each other, not this artifact before and after a simplification of its own design — `NOTES.md` records design decisions but no before/after figures for a simplification made to this artifact. Per the caveat, a cross-artifact comparison is not the before/after anchor 3 asks for, so score capped at 2.

### D3 — modularity

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:72-93` — `_LedgerFile` is the only code that touches the filesystem (`open`, `write_text`, `read_text`); `QuotaLedger` itself never does file I/O directly.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:168` and `:193` — `commit` and `close_tenant` route every durable write through `self._ledger.append(...)`, an identifiable single call rather than inline file operations scattered through the command methods.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:134` — `ledger_lines()` routes reads through `self._ledger.lines()` the same way.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:110` — `self._ledger = _LedgerFile(ledger_path)`: the domain class constructs the concrete I/O class directly, in its own `__init__`, in the same module. No parameter exists to inject an alternate implementation.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:322-324` — mechanical block: `declared_interfaces`=0, `declared_interface_methods`=0, `internal_import_edges`=0 for artifact U (single module; no cross-module boundary exists to import across).

**Refuses to claim** (required and non-null for a score of 4): n/a — not scored at 4.

**Rationale:** There is a real, followed internal separation — `QuotaLedger` never opens the file itself, all durable I/O goes through `_LedgerFile` via two narrow calls — which is more than anchor 1's "declared and not followed." But it stops short of anchor 3: `_LedgerFile` is a concrete class, not a declared port/interface, and `QuotaLedger` builds it directly inside its own constructor with no injection seam, so "an adapter could be replaced without touching the domain" fails on its face — replacing the ledger implementation means editing `quota_ledger.py` itself. I flag this as a place where the rubric's ladder is written for a ports-and-adapters target this artifact never attempted: `examples/validation/ab/FEATURE.md:118-120` explicitly lists "whether the durable side is reached through an interface, a callable, or directly" as **deliberately unspecified**, a free choice either arm may make. This artifact chose "directly." A low D3 here measures "did not build hexagonal architecture," which is spec-compliant, not "failed to build one it attempted." I scored the anchor as written rather than adjusting for that, per the instruction not to smooth a poor fit into a friendlier number, but the mismatch is worth naming.

### D4 — behavior preservation

**Score:** 3

**Citations** (`file:line` — the bar is in the scoring rules above):

- `examples/validation/ab/FEATURE.md:89-105` — R1 through R5, the enumerated behaviors the baseline (the feature spec) requires.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:27-52` — "What each instrument is": the corpus instruments (`corpus-whole`, `corpus-neg`, `corpus-slice-res`, `corpus-slice-led`, `corpus-port`) are generated from the model's state graph, not hand-written.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:71-81` — kill table: model-derived instruments (`corpus-neg`, `corpus-whole`, `corpus-slice-res`) kill several of `M01`-`M10` on this artifact, i.e. the model-derived check is exercised and capable of failing on this codebase, not merely present.
- My own run (see `judging_practice`): shared suite (28) and own suite (32) both reproduced clean on unmutated code, matching `NOTES.md:24,32`.

**Refuses to claim** (required and non-null for a score of 4): n/a — not scored at 4. See rationale for why 4 was withheld despite `executed_own_faults: true`.

**Rationale:** R1-R5 are enumerated in the feature spec and are covered by a model-derived corpus that the evidence packet shows actually killing mutants on this specific artifact — anchors 2 and 3 both hold. I *did* run my own fault (`judging_practice.executed_own_faults: true`), which is the precondition for anchor 4, but the fault I seeded was caught only by the artifact's own hand-written tests (`test_quota_ledger.py:255-263`), not demonstrated caught by the model-derived check itself — I did not run the actual corpus generator against my mutation, and the shared hand-written suite (which sits alongside the model-derived instruments) did not catch it either. Rule 8 is explicit that a judge reading the packet's own table of catches is "repeating the artifact's claim rather than checking it"; my own check did not confirm a model-derived catch, so I am not extending that credit. Anchor 4 withheld; score capped at 3.

### D5 — honesty

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:88-94` — unprompted: `available("nobody")` raises `KeyError`; the author names this as "the one place I am aware of where a reasonable implementer could differ from me without either of us contradicting the text," rather than asserting it is obviously correct.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:96-103` — unprompted: names a possible gap in the spec itself ("If integrality is meant to be enforced, the six-reason vocabulary is missing a reason for it") rather than silently picking a behavior and calling it done.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:113-118` — a `Scope` section naming, unprompted, everything deliberately not built.
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:125-129` — discloses, unprompted, that it saw filenames on the must-not-open list via `ls` and states plainly it opened none of them and saw no contents.

**Refuses to claim** (required and non-null for a score of 4): n/a — not scored at 4.

**Anchor reading** (required at 3 or 4; `disclosure` or `measured`): n/a — not scored at 3 or 4.

**Rationale:** `NOTES.md` names blind spots and open judgment calls unprompted, clearing anchor 2 comfortably. I looked for anchor 3's specific shape — an actual refusal to emit a positive verdict, an `unobservable`/`unmappable` result rather than a stated limitation — and did not find one: every place `NOTES.md` flags uncertainty, it still picks a behavior and defends the pick, rather than declining to certify that behavior. The two are adjacent but not the same thing, and I did not want to convert "documents its judgment calls well" into "refuses to certify," so I held at 2 rather than stretch to 3.

## Verdict

A competent, honest, single-module implementation that satisfies the spec and is caught out by real content- and refusal-sensitive checks (including one I built myself), but it never attempts a ports-and-adapters split, and my own independently-seeded ordering fault exposed a real detection gap between the shared suite and the artifact's own tests that the evidence packet's tables alone would not have surfaced.

## Disclosures

**What I saw that I was not meant to see:** Nothing beyond what the dispatch permits. `NOTES.md:125-129` itself discloses that the artifact's author saw some forbidden filenames via `ls` before knowing the rules; I did not follow up by looking at any of those files myself, and I did not go looking for the arm-to-label mapping.

**What I ran, in full:** Copied `quota_ledger.py` and `test_quota_ledger.py` to a scratch directory outside the repo (not inside it — nothing in the repository was modified). Confirmed the unmutated baseline (28 shared-suite passes, 32 own-suite passes). Seeded a single deliberate fault — swapped the guard order of `tenant_closed` and `amount_not_positive` in `reserve()` — ran both suites against it, reverted, and deleted the scratch tree. Full detail is in `judging_practice.what_was_run` above.

**What I rejected:**

- **D1 at 4**: rejected because the main kill table's `class` column is blank for every mutant (`EVIDENCE.md:69-81`), so I cannot cite which mutant is in which named class without guessing; the one class I could check cleanly (`wrong_value`) is fully reached by some model-derived instrument, so I found no class the model-derived apparatus as a whole cannot reach.
- **D4 at 4**: rejected even though I have `executed_own_faults: true` — the precondition — because the fault I actually ran was caught only by the artifact's own hand-written test, not by anything model-derived, and I did not run the real corpus generator against it. Extending credit from the packet's own table of catches would have been "repeating the artifact's claim," which rule 8 specifically rules out.
- **D3 at 3**: I nearly gave this a 3 on the strength of `_LedgerFile`'s clean internal separation, then read `quota_ledger.py:110` again and saw the domain constructs the concrete I/O class directly with no injectable seam — that fails anchor 3's swap test on its face, so I stepped back to 2.
- **D5 at 3**: I nearly gave this a 3 because `NOTES.md`'s "What I was unsure about" section reads like a refusal in tone; on a closer read every instance still commits to a behavior and defends it, rather than declining to certify one, so I held at 2.
- **A stretch I flagged rather than smoothed**: D3's ladder assumes a ports-and-adapters target. `FEATURE.md:118-120` tells both arms that the durable side being reached "through an interface, a callable, or directly" is deliberately unspecified and free. This artifact chose directly, which is spec-compliant. Scoring it a 2 on D3 is accurate to the rubric as written, but a reader should not read that 2 as "this artifact failed at modularity" — it never attempted the thing D3 measures, and the spec explicitly permitted that.
