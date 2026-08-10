# Scorecard — ab_quota_ledger, artifact `T`, judge pass 2

`run_id`: `20260810-v4-T-p2` · scorecard_version 4 · rubric `references/eval_scorecard.md` digest `sha256:1c5f60dab75f9a79` · served `sha256:9157db7edd640c79`

**You are scoring artifact `T`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. How to read it against your judgement is one of the numbered scoring rules below.

## The rubric you are scoring against

**This is the whole rubric, and it is reproduced here so the bar for a score sits in the same file as the score.** Do NOT go and read `references/eval_scorecard.md`. That file also carries reading rules and prior results about these same dimensions, and a judge who reads those is being handed conclusions about the instrument they are the instrument for.

### The scoring rules

1. **Score artifacts, never claims.** A summary saying "the adapters assert content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped at 1, mechanically, by the schema check.
3. **A score at the top of its scale additionally names something the artifact refuses to claim.** The top of every scale requires a stated limit. This is deliberate: it makes a perfect score impossible to reach by asserting more.
4. **Prose quality is never an input.** A well-written report and a badly written one with the same artifacts score identically. Say so in the rationale if the writing tempted you.
5. **Two judges, independently, blind to each other.** Any dimension where they differ by more than 1 is recorded as `contested` and adjudicated by a third pass that must cite new evidence, not re-read the same lines.
6. **Blind to arm.** Where an eval has arms (with-prompt vs without), judges do not learn which artifact came from which until after scoring.
7. **The mechanical block is recorded, never scored.** Kill counts, complexity figures, case counts, determinism, runtime. It sits beside the judgement so a reader can see when the two disagree — and a disagreement is a finding.
8. **Say what you ran.** *(New in version 2.)* Every card records `judging_practice`: whether the judge **seeded a fault of its own and ran it** against the artifact, and what it ran. Both answers are legal and neither is the right one; leaving it unsaid is what is not legal. From version 4 no anchor is gated on it and it is still required, because what a judge did is a variable in what a judge reports and a variable nothing records is a variable nobody can subtract.
9. **A judge is served the card, never the rubric file.** *(New in version 3.)* The scaffolded `scorecard.md` carries the rubric a judge needs. This file carries reading rules and prior results about these dimensions as well, and a judge who reads it is handed conclusions about the instrument they are the instrument for. Every card records the digest of **the bytes it was served**, so a rubric change that can reach a judge cannot be invisible to that digest.
10. **Answer every recorded note.** *(New in version 4.)* N-D1, N-D4 and N-D5 take no score and are required on every filled card. An empty note is not a legal card; *"I could not tell, and here is what I looked at"* is.

**Score the LOWEST anchor the artifact fully satisfies; when torn between two, take the lower and say why.**

### Judging practice — REQUIRED, and it is a field on the card

**Did you seed a fault of your own and run it against this artifact, or did you score the evidence packet?** Both are legal. Neither is the right answer. What is not legal is leaving it unsaid.

Fill `judging_practice` in `scorecard.json`: `executed_own_faults` true or false, and `what_was_run` listing what you actually ran.

**No anchor is gated on your answer.** The anchor that was is a recorded note now. Say what you ran because it is the variable that moves scores, not because a rung depends on it.

### D2 — complexity

*Is the design as simple as its behavior requires, and no simpler?*

Diff the two trees yourself and decide whether one fact is stored twice. A measured complexity descriptor may be read where one exists and it decides nothing: on the only simplification this project has ever measured, 19 of 21 axes were byte-identical and one moved the wrong way while eight judges found the removal independently.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state, no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the before and after figures are both recorded.

> **A drop in a complexity number is not evidence on its own.** MF-020: a metric can improve because an edge was deleted. A D2 of 3 requires the judge to say *what got simpler and how the behavior survived it*.

### D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

## The recorded notes — REQUIRED, and they take no score

**Answer each in your own words and cite `file:line` as you would for a score.** There is no 0–4 here and there is no anchor ladder: these questions were scored for three versions and the numbers were measured not to mean the same thing twice. *"I could not tell, and here is what I looked at"* is a correct answer; an empty note is not.

### N-D1 — bug detection

What did the cases catch, and what class did they demonstrably miss? Name the fault you seeded if you seeded one.

### N-D4 — behavior preservation

Which behaviors of the baseline did you enumerate, and is each shown still to hold? If there is no baseline, say so — that is the answer, not a gap in the note.

### N-D5 — honesty

Does the artifact refuse rather than falsely certify, and does it name what it cannot see? Point at the refusal, or at its absence.

### Judging practice — your answer

**Executed own faults:** true

**What was run:**

- Control run on an unmutated scratch copy of artifact_T: `uv run --with pytest python -m pytest tests/test_ledger.py -q` -> 53 passed, confirming NOTES.md's own count before seeding anything.
- Seeded fault 1 (domain, quota-guard off-by-one): changed `quota_ledger/domain.py`'s `if amount > self.available(tenant):` to `if amount >= self.available(tenant):`, reran the same suite -> 8 of 53 failed, in symmetric file/memory pairs (used for the D3 runtime-swap evidence and for N-D1).
- Reverted fault 1 and diffed against the original to confirm a byte-identical revert.
- Seeded fault 2 (file adapter, blank-line filter removed): changed `quota_ledger/file_journal.py`'s `records()` from `[line for line in text.splitlines() if line]` to `text.splitlines()`, reran the same suite -> 53 of 53 passed (fault survived; used for N-D1).
- Reverted fault 2 and diffed against the original to confirm a byte-identical revert.

## Your scores

### D2 — complexity

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger/domain.py:90-104`
- `quota_ledger/domain.py:118-120`
- `quota_ledger/domain.py:159`
- `quota_ledger/domain.py:181`
- `NOTES.md:70-84`
- `NOTES.md:57-66`
- `EVIDENCE.md:325-343`

**Refuses to claim** (required and non-null for a score of 3): n/a — not a top-of-scale score.

**Rationale:** State is small and each piece has a named, bounded set of writers, not a god-state written from everywhere: `domain.py:90-104`'s docstring enumerates `_outstanding` (written by reserve/commit/release), `_committed` (commit only) and `_closed` (close_tenant only), and the actual write sites in reserve/commit/release/close_tenant match that claim exactly — I traced every one. `available` is derived rather than stored (`domain.py:118-120`), and `NOTES.md:70-84` argues the relationship between that choice and behavior directly: deriving it makes R1 (conservation) true by construction instead of needing three commands to remember to maintain it, and it is why "commit does not give the hold back" falls out rather than being coded as a special case. `NOTES.md:57-66` makes a second explicit complexity-vs-behavior argument: the COMMIT/CLOSE line format stays as two f-strings inside `domain.py:159` and `domain.py:181` rather than being pushed into a `CommitRecord` type each adapter would render, because the latter would duplicate the same format across both adapters — an argued reason not to add an abstraction. That satisfies anchor 2: proportional complexity, no god-state, and the design's shape is argued rather than merely asserted. It does not reach anchor 3. Anchor 3 asks for a simplification made TO THIS ARTIFACT with its own before/after figures recorded; nothing in this packet is a diff of T against an earlier version of T. `EVIDENCE.md:325-343`'s mechanical block is a snapshot across three sibling artifacts (T/U/W), not a before/after of one design's history, and per this rubric's own caveat ("a drop in a complexity number is not evidence on its own") and rule 7 ("recorded, never scored") I am not reading it as one. If anything, on every raw figure in that block T is the *largest* of the three (4 modules vs 1, 202 code_lines vs 151/78, 6 classes vs 4/2), which cuts against treating T as a simplification story at all — the extra size is the second (fake) adapter and the port declaration the ports-and-adapters brief asked for, not a reduction.

### D3 — modularity

**Score:** 4

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger/domain.py:1-11`
- `quota_ledger/domain.py:13-16`
- `quota_ledger/domain.py:22-43`
- `quota_ledger/file_journal.py:1-31`
- `quota_ledger/memory_journal.py:1-23`
- `quota_ledger/__init__.py:13-14`
- `quota_ledger/__init__.py:37-38`
- `tests/test_ledger.py:260-270`
- `tests/test_ledger.py:26-36`
- `tests/test_ledger.py:77-83`
- `tests/test_ledger.py:108-114`
- `NOTES.md:46-51`
- `NOTES.md:93-97`

**Refuses to claim** (required and non-null for a score of 4): `NOTES.md:53-55`: "Nothing else is indirected. There is no port in front of the arithmetic, no repository interface over the reservations dict, no service layer. The reservations live in a dict inside the domain because they are not outside it." The artifact explicitly declines to claim broader modularity than the one boundary it built and names why the rest is not ported.

**Rationale:** Domain independence is demonstrated at the call-through level, not just import syntax: `domain.py:1-11` and `domain.py:22-43` declare the `Journal` port in the domain's own vocabulary as a Protocol with a stated contract, and `Ledger` only ever calls `self._journal.append(...)`/`.records()` — there is no other path by which domain code reaches storage. `domain.py:13-16` imports only `__future__`, `dataclasses`, `typing`, and I did not take that on the artifact's word: `tests/test_ledger.py:260-270` parses `domain.py`'s own AST and asserts that import set, and I re-ran it myself (see judging practice). `file_journal.py` and `memory_journal.py` each implement the two-method contract with no import of `domain.py` or of each other. The swap is named specifically, not gestured at: `__init__.py:13-14` states it and `__init__.py:37-38` is the one line that would change — `FileJournal(ledger_path)` to `InMemoryJournal()` — with `NOTES.md:46-51` giving the same claim in prose. That clears anchor 3. Anchor 4 asks for the same cases passing against a real adapter and a fake at runtime, not just that a fake exists: `tests/test_ledger.py:26-36` parametrizes one `journal` fixture over `FileJournal`/`InMemoryJournal` and builds `ledger` on top of it, so every behavioral test in the file (e.g. `tests/test_ledger.py:77-83, 108-114`) runs twice, once per adapter, each asserting a literal expected value rather than merely that the two wirings agree with each other (`NOTES.md:93-97` states this design choice explicitly, and it is the right one — two wirings of a wrong domain would still agree with each other). I ran this suite myself rather than reading the claim: 53 passed on a scratch copy. I then seeded my own fault in `domain.py` (the quota guard weakened from `>` to `>=`) and reran: 8 of 53 cases failed, in symmetric file/memory pairs, which is direct runtime evidence that the same cases exercise both adapters through the same domain code. Worth recording as a disagreement per rule 7: `EVIDENCE.md:168`, the harness's own generated `corpus-port-swap` table (not the artifact's own suite), shows `M09-negative-control-ledger-order` KILLED when bound to the real `FileJournal` but SURVIVED when bound to the fake `InMemoryJournal` — an asymmetry I could not resolve, since the code that generates and binds that corpus is outside this card's declared scope and I was told not to read it. `EVIDENCE.md`'s own control-status block marks M09 `"decides_nothing": true` for this run, and my own targeted fault-seeding on the artifact's declared suite (not the harness corpus) showed symmetric, not asymmetric, kill behavior, which is the evidence the D3=4 score actually rests on. I am flagging the discrepancy rather than resolving it.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `tests/test_ledger.py:228-235`
- `quota_ledger/file_journal.py:33-34`
- `EVIDENCE.md:71-81`

**Note:** I seeded two faults myself (see judging practice above). Fault 1, a one-character off-by-one in the quota-exceeded guard (`domain.py`: `>` to `>=`), was caught hard: 8 of the artifact's own 53 cases failed, in symmetric file/memory pairs, including `tests/test_ledger.py:228-235` (`test_the_quota_can_be_exhausted_and_recovered`) and the interleaving/totals tests. That class — a guard boundary condition on the domain's own arithmetic — is well covered. Fault 2, removing the blank-line filter from `FileJournal.records()` (`file_journal.py:34`), SURVIVED all 53 cases: no test ever causes a blank line to reach that filter, so the class this suite demonstrably misses is defensive/framing logic in the file adapter for inputs the domain never actually produces — the guard is present in the code but its necessity is asserted, not exercised. Separately, `EVIDENCE.md`'s own per-mutant table (lines 71-81) is in scope since it ships inside this artifact directory: the declared shared `suite` column killed 10 of the 11 listed mutants and let N01 (a negative control that is supposed to survive) survive, consistent with what I found by hand — strong on the guard/durable-content classes the suite targets, silent on adapter-internal defensive paths the suite never drives.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `EVIDENCE.md:61-62`
- `NOTES.md:102-123`
- `NOTES.md:125-145`

**Note:** There is no baseline for this note in the before/after sense: artifact T is not a revision of a prior version of itself, it is one of three independent implementations built against the same feature brief, so there is no earlier T whose behaviors this T could be checked against. That is the answer, not a gap. If "baseline" is instead read as the feature specification's required behaviors, I could not independently enumerate them against the spec myself: `FEATURE.md` and the shared suite at `examples/validation/ab/tests/test_behavior.py` are both outside this card's declared scope (only `artifact_T` and my own card directory), so I did not open them. What is in scope is `EVIDENCE.md:61-62`, which reports that shared suite unchanged and passing 28/28 on artifact T, and `NOTES.md:102-123`, which names the one place the artifact's author found `FEATURE.md`'s structure and behavior asks in tension (a path-taking constructor versus a domain that must not know paths) and how it was resolved — behavior wins, via a factory function — plus `NOTES.md:125-145`, four explicitly named places the feature was silent, with the interpretation chosen for each. I did not independently verify these resolutions against `FEATURE.md`; I am reporting what the artifact itself discloses and citing it as such.

### N-D5 — honesty

**Citations** (`file:line`):

- `NOTES.md:136-141`
- `NOTES.md:125-145`
- `NOTES.md:149-156`
- `quota_ledger/domain.py:22-43`

**Note:** Yes, in several concrete places rather than one. `NOTES.md:136-141` names a specific correctness gap the author found and did not paper over: "commit and close_tenant update memory and then append. If the append raised, memory would have moved without a durable record ... This is the one place I can name where R2 is not enforced by construction." `NOTES.md:125-145` lists four unspecified-behavior decisions with the reasoning for each rather than silently picking one and asserting it was required. `NOTES.md:149-156` ("Files I did not open") is a direct, checkable disclosure of the boundary of what the author looked at — it names files by name and states "I read exactly two files in the repository: FEATURE.md and tests/test_behavior.py" — the same move this note itself asks for, made by the artifact about itself. The Journal Protocol's contract (`domain.py:22-43`) is written as a small, complete list of guarantees rather than an open-ended one, itself a form of not over-claiming. I found no place where the artifact certifies something my own fault-seeding or reading contradicted — the one place I found daylight (the blank-line filter surviving unmutated, see N-D1) is a coverage gap, not a false certification: the artifact never claims that path is tested.

## Verdict

T earns the top of D3 on runtime evidence I reproduced myself (a seeded quota-guard fault killed symmetrically across both the real `FileJournal` and the fake `InMemoryJournal` wirings of the same 53-case suite) and a named, working swap point at `quota_ledger/__init__.py:37-38`, but only a mid-scale D2: the design's complexity is argued and proportional to its behavior (single-writer state, a derived `available`), yet nothing in this packet is a measured before/after simplification of T itself, so anchor 3 is unreached; a reader should also note the unresolved `EVIDENCE.md:168` real-vs-fake asymmetry on a control the packet itself calls decision-inert.

## Disclosures

I did not read any prohibited file: no `references/eval_scorecard.md`, no `rubric_v3_frozen.md`, no other example's or epic's scorecards, no `NEXT-EPIC.md`/`*-EPIC.md`, no `UNBLINDING.md`, and no other judge's card. I do not know which arm ("with-prompt" vs "without", or any other axis) artifact T actually corresponds to, and I made no attempt to find out.

What I ran that touched a filesystem: I copied `artifact_T` into my scratchpad directory (outside this repo, under `/private/tmp/.../scratchpad/artifact_T_test`) and ran its test suite there, unmodified, then twice more after seeding and reverting a fault each time, diffing each reverted file against the original to confirm a byte-identical restore. Nothing in the repository itself, and nothing under this artifact directory or my card directory, was modified during that process — only the scratch copy.

What I rejected: I was tempted to let `EVIDENCE.md`'s mechanical block (T being the largest of the three artifacts on every raw complexity figure) push D2 toward the bottom anchor, treating "biggest of three" as "least proportional." I rejected that reading because rule 7 and the D2 caveat both say a bare figure — in either direction — is not evidence on its own, and because the size difference has a named, argued cause (the second adapter and the port declaration the ports-and-adapters brief itself asked for), not an unexplained one. I was also tempted to let the `EVIDENCE.md:168` real/fake asymmetry on M09 pull D3 down from 4, since it looks at first glance like exactly the kind of "same cases, different adapters, different result" gap anchor 4 is designed to catch. I rejected using it for that because (a) it comes from the harness's generated corpus, not the artifact's own declared suite, which is the surface anchor 4 asks the judge to evaluate; (b) the evidence packet's own control-status analysis marks that specific cell `"decides_nothing": true`; and (c) I could not investigate the actual cause because the code that generates and binds that corpus is out of this card's declared scope — so I recorded the discrepancy as a disclosed, unresolved finding in the D3 rationale instead of either hiding it or letting an unexplained number move the score. Ambiguity I could not settle on my own: whether "the design's complexity is proportional to its behavior" (D2 anchor 2) should be read against the feature spec alone or against the ports-and-adapters task this artifact was actually asked to do — I read it against the latter, since `subject.declared_effect_boundary` on this very card is "ports-and-adapters," but a different reading of "behavior" could plausibly push T toward anchor 1 for carrying machinery (a fake adapter) the bare feature brief does not itself require. Writing the rationale out in full (rather than just picking a number) is what surfaced the M09 asymmetry as worth naming at all; a number alone would have let it pass silently.
