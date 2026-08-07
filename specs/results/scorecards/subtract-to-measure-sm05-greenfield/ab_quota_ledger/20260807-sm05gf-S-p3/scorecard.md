# Scorecard — ab_quota_ledger, artifact `S`, judge pass 3

`run_id`: `20260807-sm05gf-S-p3` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `S`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. How to read it against your judgement is one of the numbered scoring rules below.

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

- Copied `quota_ledger.py`, `test_quota_ledger.py` (both from the artifact directory) and `examples/validation/ab/tests/test_behavior.py` into a scratch directory outside the repository; ran both suites unmodified against the artifact (60 passed: 28 shared + 32 own).
- Seeded one fault of my own in `commit()`: changed `total_after = self._committed[reservation.tenant] + reservation.amount` to `total_after = reservation.amount`, so the running total written to the durable ledger and tracked in memory drops everything committed before the current call (a wrong-value / durable-content fault, not one I read off the artifact's own kill table before choosing it).
- Reran both suites against the faulted copy. Both caught it: the shared suite failed `test_commit_running_total_accumulates` and `test_r2_the_durable_ledger_agrees_with_memory`; the artifact's own suite failed `test_commit_lines_reach_the_file_itself` and `test_close_total_matches_committed_after_commits_and_releases`.
- Did **not** run the model-derived corpus (`corpus-whole`, `corpus-neg`, etc.) myself — the generator, manifest and seeded-fault catalogue (`check_catalogue.py`, `seeded_faults.toml`, `reference/`, `reference_ports/`) are on the must-not-read list, so I have no tooling to reproduce those cells. My own run only demonstrates the hand-written checks (shared + own suite) are capable of failing, not the corpus.

## Your scores

### D1 — bug detection

**Score:** 3

**Citations** (`file:line` — the bar is in the scoring rules above):

- `.../ports-as-adapters/blind/artifact_U/EVIDENCE.md:71-73` — `M01-guard-zero-amount`, `M02-guard-over-quota`, `M03-guard-close-with-outstanding` (all guard-relaxation / refusal faults) are `SURVIVED` by `corpus-whole` but `KILLED` by `corpus-neg`.
- `.../ports-as-adapters/blind/artifact_U/EVIDENCE.md:111-120` — the per-class block confirms it structurally: `guard_relaxation`: `corpus-whole` "0 of 3", `corpus-neg` "3 of 3", `corpus-port` "3 of 3".
- `.../ports-as-adapters/blind/artifact_U/EVIDENCE.md:74` and `:101-110` — `M04-durable-stale-total` (a wrong-content fault on the durable ledger) is `SURVIVED` by `map-silent` (shape-only) and `KILLED` by `map-checking` (content-asserting); class block `durable_content`: `map-checking` "2 of 2" vs `map-silent` "1 of 2".
- `.../ports-as-adapters/blind/artifact_U/EVIDENCE.md:35-46` — instrument definitions: `corpus-whole` is "every enabled edge of the model's state graph, replayed" (so it cannot, by construction, reach a disabled/refused edge); `corpus-neg` is exactly "the DISABLED edges... each asserting a refusal plus inertness", i.e. model-derived, not the hand-written suite.

**Refuses to claim** (required and non-null for a score of 4): n/a (score is 3, not 4)

**Rationale:** Anchor 2 is met: `map-checking` (a content-asserting adapter) kills a durable-content fault (`M04`) that a shape-only adapter (`map-silent`) and the structural corpus (`corpus-whole`) both miss — this is a content assertion doing real work, not shape-checking dressed up. Anchor 3 is also met, and by a model-derived instrument rather than only the hand-written suite: `corpus-neg` — generated from the model, not hand-written — kills all three guard-relaxation/refusal faults (`M01`–`M03`) in a class `corpus-whole` structurally cannot reach (0 of 3), which is exactly anchor 3's example ("a refusal"). I looked for anchor 4's second requirement — the record naming a fault class it *still* cannot reach — and did not find one for D1 specifically; every class in the per-class block reaches full coverage via at least one instrument once `NOT_DECIDABLE` cells (a declared, verified limitation, not a gap) are set aside. The closest thing to an unreached-class admission in the packet (the missing `corpus-port-swap:fake`) is a D3 fact, not a D1 one. Without an explicit "we cannot reach X" statement for bug detection, I capped at 3 rather than infer one that isn't written down.

### D2 — complexity

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `.../ports-as-adapters/blind/artifact_U/quota_ledger.py:103-110` — five state containers (`_quotas`, `_available`, `_committed`, `_closed`, `_reservations`, `_next_seq`), each with a single clear owner.
- `.../ports-as-adapters/blind/artifact_U/quota_ledger.py:138-152` (`reserve`), `:154-172` (`commit`), `:174-182` (`release`), `:184-195` (`close_tenant`) — each state field is mutated only inside the one command method the feature assigns it to; the guard chain in each command matches FEATURE.md's declared rejection order one-for-one, no extra branching beyond what the four rejection rules and one accept path require.
- `.../ports-as-adapters/blind/artifact_U/EVIDENCE.md:310-327` — mechanical block for artifact U: `instance_state` 8, `module_state` 0, `branch_points` 10, `max_branch_points_in_callable` 4, `max_depth` 1.

**Refuses to claim** (required and non-null for a score of 4): n/a (score is 2, not 4)

**Rationale:** No god-state: `module_state` is 0, and each of the 8 instance fields is written from exactly one or two command methods that correspond directly to FEATURE.md's four commands, not from scattered call sites. `branch_points` (10) sits close to the minimum the four commands' declared rejection ladders require (4+2+1+3 guard checks, roughly), and `max_branch_points_in_callable` (4) matches `reserve`'s four declared rejection reasons exactly — the branching is essential, not accidental. That satisfies anchor 2. I did not find a before/after simplification recorded for *this* artifact's own design (the mechanical block's T/U/W comparison is a cross-artifact table, not a record of this artifact being simplified from an earlier version of itself with both figures kept), so anchor 3 is not met. Note: `instance_state_in_effectful_modules` is 8 of 8 (100%) — all state lives in the one module that also does I/O — but I read that as a D3 (modularity/effect-isolation) signal, not a D2 (complexity-magnitude) one, and did not let it pull this score down.

### D3 — modularity

**Score:** 1

**Citations** (`file:line` — the bar is in the scoring rules above):

- `.../ports-as-adapters/blind/artifact_U/quota_ledger.py:110` — `self._ledger = _LedgerFile(ledger_path)`: the domain object constructs its concrete durable-I/O collaborator directly, inline, in its own constructor. No interface, no injection point, no seam a caller can use to substitute a different durable side.
- `.../ports-as-adapters/blind/artifact_U/quota_ledger.py:72-93` — `_LedgerFile` is a plain concrete class (no `Protocol`/ABC), defined in the same module as the domain class that uses it.
- `.../ports-as-adapters/blind/artifact_U/EVIDENCE.md:322` — mechanical block: `declared_interfaces` = 0, `declared_interface_methods` = 0, `internal_import_edges` = 0 for this artifact (vs. 1 / 2 / 3 for artifact T).
- `.../ports-as-adapters/blind/artifact_U/EVIDENCE.md:49-51` — "`corpus-port-swap:fake` on an artifact that ships no second implementation runs its REAL one" — measured confirmation that no fake/alternate adapter exists to swap in.

**Refuses to claim** (required and non-null for a score of 4): n/a (score is 1, not 4)

**Rationale:** I want to flag that the ladder does not fit this artifact cleanly, per the dispatch's instruction to say so rather than smooth it over. Anchor 0 ("no boundary is discernible; state is written from everywhere") is too harsh — every durable write goes through exactly one class (`_LedgerFile`), called from exactly two sites (`commit`, `close_tenant`); that is a real, followed, internal separation. But anchor 1 ("boundaries named... and the code does not follow them") doesn't fit either, because the code *does* follow the one separation it has — nothing bypasses `_LedgerFile`. And anchor 2 ("cross-boundary calls go through something identifiable as a port") is where I think it genuinely fails: `_LedgerFile` is a concrete class the domain constructs and owns outright, not an abstraction the domain depends on and something else supplies — there is no `Protocol`/ABC, no constructor injection, and the measured `declared_interfaces: 0` / `corpus-port-swap:fake`-runs-the-real-one facts both confirm there is nothing to swap. FEATURE.md itself leaves "whether the durable side is reached through an interface, a callable, or directly" explicitly unspecified, so this artifact isn't violating a stated requirement — it simply never attempted ports-and-adapters. Given the choice between a rung that's too generous (2, "identifiable as a port") and one that's an awkward fit but closer to the truth (1, a declared-but-non-abstracted separation that isn't functioning as a replaceable boundary), the scoring rule says take the lower when torn. I scored 1.

### D4 — behavior preservation

**Score:** 3

**Citations** (`file:line` — the bar is in the scoring rules above):

- `examples/validation/ab/FEATURE.md:91-104` (R1–R5) cross-checked against `.../ports-as-adapters/blind/artifact_U/test_quota_ledger.py:197-202` (R1, `test_release_after_commit_rejects...`), `:85-104` (R2, durability tests), `:220-238` (R3, close-line tests), `:114-131` (R4, `test_a_rejected_command_writes_nothing_durably`), `:133-139` (R5, `test_the_ledger_is_append_only_across_many_writes`) — each declared rule is separately enumerated and exercised, not just implied by a passing suite.
- `.../ports-as-adapters/blind/artifact_U/EVIDENCE.md:172-187` — executability table: every corpus instrument (`corpus-whole`, `corpus-neg`, `corpus-slice-res`, `corpus-slice-led`, `corpus-port`, `map-silent`, `map-checking`) shows `failed on unmutated code: 0`, i.e. the model-derived corpus (per `:37`, "every enabled edge of the model's state graph, replayed") passes cleanly on the correct implementation, not just the hand-written suite.
- My own run (scratch tree, not part of the repository, not otherwise cited as evidence): a seeded fault dropping the running-committed-total in `commit()` was caught by both `test_behavior.py::test_commit_running_total_accumulates` / `test_r2_the_durable_ledger_agrees_with_memory` and `test_quota_ledger.py::test_commit_lines_reach_the_file_itself` / `test_close_total_matches_committed_after_commits_and_releases`.

**Refuses to claim** (required and non-null for a score of 4): n/a (score is 3, not 4)

**Rationale:** Anchor 2 is met (R1–R5 individually enumerated and each shown to hold, both in the shared suite and the artifact's own). Anchor 3 is met: the check is not only hand-written — the EVIDENCE.md executability table shows the model-derived corpus (generated by replaying the state graph of `model/QuotaLedger.tla`, per the instrument's own description) also passes cleanly on this artifact with zero failures on unmutated code. I *did* run my own fault (see judging practice) and it was caught, which is the behavior anchor 4 asks for — but only for the hand-written checks. I do not have tooling access to the corpus generator (`check_catalogue.py`, `seeded_faults.toml` are on the must-not-read list), so I could not personally run my own fault through the model-derived corpus that anchor 3 was built on, and reading the packet's own kill table for that would be "repeating the artifact's claim rather than checking it" (rule 8). I am capping this at 3 rather than 4 for that reason and naming it explicitly, per the dispatch's ask that a low answer here is the preferred one: I verified the check can fail, but only for the half of it (hand-written) I could actually run myself.

### D5 — honesty

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `.../ports-as-adapters/blind/artifact_U/NOTES.md:87-94` — "Queries with an unknown tenant. `available("nobody")` raises `KeyError`... This is the one place I am aware of where a reasonable implementer could differ from me without either of us contradicting the text."
- `.../ports-as-adapters/blind/artifact_U/NOTES.md:96-103` — non-integer `amount` and `bool`-as-`int` named explicitly as unenforced edge cases, with the reasoning for not enforcing them stated plainly rather than hidden.
- `.../ports-as-adapters/blind/artifact_U/NOTES.md:24` and `:32` — pass counts ("28 passed", "32 passed") reported as plain measured facts, with no broader claim of correctness attached to them.

**Refuses to claim** (required and non-null for a score of 4): n/a (score is 2, not 4)

**Anchor reading** (required at 3 or 4; `disclosure` or `measured`): n/a (score is 2)

**Rationale:** Anchor 2 is clearly met: `NOTES.md`'s "What I was unsure about" section names concrete blind spots (the `KeyError` on an unknown-tenant query, non-integer/`bool` amounts) unprompted, inside the artifact itself, not only in a separate report. I looked for anchor 3 — an explicit refusal to emit a positive verdict where the basis doesn't support one (`unobservable`/`unmappable` language) — and did not find one in `NOTES.md`. The notes disclose ambiguity and design choices but never withhold a certification they were in a position to make; they simply don't make sweeping certification claims to begin with, so there is nothing on the record that reads as a refused verdict rather than a stated limitation. (`EVIDENCE.md`'s control-status block does use exactly this kind of refusal language — `NOT_DECIDABLE` cells and a non-green positive control rather than a smoothed-over claim — but I read that as the eval harness's own honesty about its instruments, not the artifact's, since `EVIDENCE.md` is generated by the shared measurement infrastructure rather than authored by whoever produced `quota_ledger.py`/`NOTES.md`. I considered scoring D5 on the packet as a whole and rejected it for that reason — see Disclosures.)

## Verdict

A correct, well-tested, honestly-annotated single-module implementation that catches real faults including a refusal-class one a whole-view corpus alone cannot reach (D1=3, D4=3), but it is not ports-and-adapters in any functional sense — the domain hardcodes its own concrete durable-I/O class with zero abstraction or injection and ships no fake to swap in (D3=1) — so read it as a solid direct implementation, not a hexagonal one.

## Disclosures

**What I saw that I was not meant to see:** Before I knew which files were in scope, I ran `find examples/validation/ab -maxdepth 2 -type f` to see what existed, which printed the *names* (not contents) of every file under that tree, including ones on the must-not-read list: `arm_a/PROMPT.md`, `arm_b/PROMPT.md`, `arm_c/PROMPT.md`, `README.md`, `seeded_faults.toml`, `check_catalogue.py`, `reference/quota_ledger.py`, `reference_ports/*.py`, plus files not explicitly named on the forbidden list either way (`model/QuotaLedger.tla`, `model/QuotaLedger.cfg`, `model/spec_manifest.yaml`, `dispatch_record.py`, `probe_demonstrations.toml`, `eval/*.toml`, `eval/*.py`). I opened none of their contents and did not go back to any of them. This mirrors exactly what the artifact's own author disclosed doing in `NOTES.md:125-129`, which I noticed only after already having done the same thing myself.

**What I ran that could have changed a tree:** Nothing inside the repository. All execution (both suites on unmutated code, then again after seeding my own fault) happened against copies in a scratch directory outside the repo (`/private/tmp/.../scratchpad/judge-p3/`), which I created and can be discarded; the repository was never written to.

**What I REJECTED:**

1. I nearly scored D3 at 2 by reading `_LedgerFile.append()` as "something identifiable as a port" — a single, consistently-used write path is genuinely a form of encapsulation. I put that down once I checked whether it was actually *swappable* (per D3's own question, "adapters swappable?") and found it is not: `declared_interfaces: 0`, no `Protocol`/ABC, hardcoded construction inline in `QuotaLedger.__init__`, and the measured fact that `corpus-port-swap:fake` silently runs the real implementation because no fake exists. A boundary that cannot be swapped is not the boundary D3 is asking about, however cleanly it's followed internally.
2. I nearly scored D4 at 4 on the strength of my own seeded-fault run, since I did personally verify a behavior-breaking change is caught (satisfying the literal words of anchor 4 and the `judging_practice: true` gate). I put that down because anchor 4 reads as "3, and..." — built on top of anchor 3's specifically *model-derived* check — and my own run only exercised the hand-written suites; I have no access to the corpus generator to check whether the model-derived corpus catches the same fault, and taking the packet's word for that would be exactly the thing rule 8 says not to do (reading a table instead of checking it).
3. I considered scoring D5 against the whole evidence packet (which does show real refusal-to-certify behavior — `NOT_DECIDABLE` cells, a non-green positive control recorded rather than smoothed over) rather than against `NOTES.md` alone, which would likely have supported a 3. I rejected this because `EVIDENCE.md` reads as generated by the shared measurement harness across all three artifacts, not authored by whoever wrote `quota_ledger.py`; D5 asks whether *the artifact* refuses to falsely certify, and I don't think an externally-generated evidence packet's honesty is evidence about this artifact's own honesty.
4. On D3 specifically, the anchor ladder does not fit this artifact well (see the D3 rationale in full) — FEATURE.md explicitly leaves the durable-side abstraction unspecified, so this artifact isn't failing a requirement, it simply never attempted the shape the ladder assumes. I scored what the evidence supports (1) rather than either forcing a higher score to be charitable about intent, or a 0 that ignores the real internal separation that does exist.
