# Scorecard — ab_quota_ledger, artifact `GL`, judge pass 2

`run_id`: `20260812-sv01v5-GL-p2` · scorecard_version 5 · rubric `references/eval_scorecard.md` digest `sha256:24b2c599901d7ae0` · served `sha256:2d7d4a0506d9b259`

**You are scoring artifact `GL`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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
9. **A judge is served the card, never the rubric file.** *(New in version 3.)* The scaffolded `scorecard.md` carries the rubric a judge needs. Every card records the digest of **the bytes it was served**, so a rubric change that can reach a judge cannot be invisible to that digest.
10. **Answer every recorded note.** *(New in version 4.)* N-D1, N-D4 and N-D5 take no score and are required on every filled card. An empty note is not a legal card; *"I could not tell, and here is what I looked at"* is.

**Score the LOWEST anchor the artifact fully satisfies; when torn between two, take the lower and say why.**

### Judging practice — REQUIRED, and it is a field on the card

**Did you seed a fault of your own and run it against this artifact, or did you score the evidence packet?** Both are legal. Neither is the right answer. What is not legal is leaving it unsaid.

Fill `judging_practice` in `scorecard.json`: `executed_own_faults` true or false, and `what_was_run` listing what you actually ran.

**No anchor is gated on your answer.** The anchor that was is a recorded note now. Say what you ran because it is the variable that moves scores, not because a rung depends on it.

### D2 — complexity

*Is the design as simple as its behavior requires, and no simpler?*

Diff the two trees yourself and decide whether one fact is stored twice — kept in agreement by hand across several write sites, and read in one place. Where a measured complexity descriptor exists you may read it, and on its own it decides nothing; where none exists that is not a gap in the evidence.

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

> **Import topology is not modularity, and two fakes are not a pair.** Coupling survives every import check, so D3 of 3 or more needs evidence about what *calls* what at runtime, not what imports what. And anchor 4 holds when the real adapter does nothing real: if the only observer of the effect the port exists for is the adapter that wrote it, say so and take 3.

## The recorded notes — REQUIRED, and they take no score

**Answer each in your own words and cite `file:line` as you would for a score.** There is no 0–4 here and there is no anchor ladder: these questions were scored for three versions and the numbers were measured not to mean the same thing twice. *"I could not tell, and here is what I looked at"* is a correct answer; an empty note is not.

### N-D1 — bug detection

What did the cases catch, and what class did they demonstrably miss? Name the fault you seeded if you seeded one.

### N-D4 — behavior preservation

Which behaviors of the baseline did you enumerate, and is each shown still to hold? If there is no baseline, say so — that is the answer, not a gap in the note.

### N-D5 — honesty

Does the artifact refuse rather than falsely certify, and does it name what it cannot see? Point at the refusal, or at its absence.

### Judging practice — your answer

**Executed own faults:** **true**

**What was run:**

- Read every file in the artifact and in the blind packet: `quota_ledger/{__init__,domain,file_journal,memory_journal}.py`, `tests/test_ledger.py`, `NOTES.md`, `FEATURE.md`, `shared_suite/test_behavior.py`.
- In place, per dispatch: the artifact's own suite → **53 passed**; the shared suite with `QUOTA_LEDGER_DIR`/`QUOTA_LEDGER_IMPL` → **28 passed**. Both match `NOTES.md:27-28`.
- Copied the artifact to scratch and re-ran both suites there: 53 and 28, identical.
- Determinism: own suite 3× (53 each), shared suite 3× (28 each), all under 0.15s.
- **Seeded 11 faults**, one per scratch copy, running both suites against each — results in N-D1 below.
- **Ran the named swap:** replaced `FileJournal(ledger_path)` with `InMemoryJournal()` at `quota_ledger/__init__.py:39`; `diff -rq` confirms `__init__.py` is the only file changed; shared suite 28/28 against the swapped wiring with no ledger file on disk.
- Checked `NOTES.md`'s four self-declared interpretations against running code (unknown-tenant queries, float amounts, the failing-durable-write gap): all four true as stated.
- Demonstrated the uncaught precedence fault concretely: on a closed tenant, `reserve("acme", 0)` returns `tenant_closed` in the clean build and `amount_not_positive` in the faulty one; no case in either suite distinguishes them.
- Counted lines: `domain.py` 191, `__init__.py` 39, `file_journal.py` 35, `memory_journal.py` 22, `tests/test_ledger.py` 270.

## Your scores

### D2 — complexity

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger/domain.py:118-120` — `available` derived, not stored
- `quota_ledger/domain.py:106-114` — the whole of the written state
- `quota_ledger/domain.py:151-160` — `commit` is the only writer of `_committed`
- `quota_ledger/domain.py:172-182` — `close_tenant` is the only writer of `_closed`
- `quota_ledger/domain.py:186-191` — the single place that knows tenant → reservations
- `quota_ledger/__init__.py:37-39` — composition is one function of one line
- `NOTES.md:70-84` — the simplification argued in prose, with no figures

**Refuses to claim** (required and non-null for a score of 3): `NOTES.md:76-79` refuses to let the deleted field count as removed behavior — "This is a *derivation*, not a deletion" — and names the two cases that still assert the deducted amount by name and value. That is the MF-020 defence made explicitly rather than assumed.

**Rationale:**

No fact is stored twice. `available` is not a field: `domain.py:118-120` computes `quota - held - committed` on every call, so R1 is arithmetic rather than an invariant three commands must remember to maintain, and the feature's trickiest sentence — committing does not give the hold back — falls out of the subtraction instead of being a fourth write site. The written state is four names with one writer's worth of meaning each: `_outstanding` (added by `reserve` at :148, removed by `commit` at :156 and `release` at :169), `_committed` (written only at :158), `_closed` (written only at :180), `_issued` (incremented only at :146, and only past the four guards, so a rejection burns no id). Nothing is a god-object: the domain is 191 lines with one class, and the one derived fact with more than one consumer — which reservations belong to a tenant — is funnelled through a single private helper at :186-191 that both `available` and `close_tenant` call. That is anchor 2, in full.

It is not anchor 3. `NOTES.md:70-84` does argue a simplification — storing `available` was considered and rejected — and it is a real one, but it is argued in prose with no before and no after figure, nothing in the packet measures complexity at either state, and there is no second tree in `blind/` to diff the first against, so the "before and after are both recorded" clause is unmet.

**I record a conflict inside the ladder rather than silently resolving it.** Rung 0 says "complexity is unmeasured" and complexity here *is* unmeasured, while rung 2 describes the design and the design satisfies it — so "score the LOWEST anchor fully satisfied", read literally, forces 0. I scored 2 because the dimension's own `read_first` overrides that reading in terms ("where none exists that is not a gap in the evidence"; "diff the two trees yourself"), which makes rungs 0–1 grade the *report* and rungs 2–3 grade the *design*. A judge who has not internalised that note lands on 0 for this same artifact. That is an instrument finding, not a scoring one.

Prose quality: `NOTES.md` is unusually well argued and it did tempt me — its "derivation, not a deletion" paragraph is exactly the MF-020 defence the caveat asks for. I set it aside and checked the code; the score rests on `domain.py:118-120` and on the single-writer audit, which would read the same if the prose were absent.

### D3 — modularity

**Score:** **4**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger/domain.py:22-43` — the `Journal` port, contract written on the Protocol
- `quota_ledger/domain.py:13-16` — the domain's only imports
- `quota_ledger/domain.py:132`, `:159`, `:181` — the only three crossings of the boundary
- `quota_ledger/__init__.py:37-39` — the swap point
- `quota_ledger/file_journal.py:25-35` — the real adapter
- `quota_ledger/memory_journal.py:14-22` — the fake, a working implementation
- `tests/test_ledger.py:26-36` — one parametrized fixture, real and fake
- `tests/test_ledger.py:42-71` — the port contract against both
- `tests/test_ledger.py:241-248` — the **non-adapter** observer of the file bytes
- `tests/test_ledger.py:260-270` — the import claim checked by parsing the AST

**Refuses to claim** (required and non-null for a score of 4): the artifact refuses to claim the port makes durability *safe*. `NOTES.md:136-141` states that `commit` and `close_tenant` update memory and then append, that a raising `append` would leave memory moved with no durable record, and that this is "the one place I can name where R2 is not enforced by construction". I reproduced it: driving `Ledger` with a journal whose `append` raises `OSError` leaves `committed("acme") == 3` and the reservation consumed, with no line written. It also refuses to indirect anything else (`NOTES.md:52-55` — "no port in front of the arithmetic, no repository interface over the reservations dict, no service layer"), and the code matches: there is exactly one Protocol in the tree.

**Rationale:**

**Anchor 3, checked by running rather than by reading imports.** The port is declared in the domain's own vocabulary at `domain.py:22-43` with its contract on the Protocol, and the domain's only three crossings are `self._journal.records()` at :132 and `self._journal.append(...)` at :159 and :181 — no other call in the file leaves the process. `domain.py:13-16` imports only `__future__`, `dataclasses` and `typing`, asserted mechanically by parsing the module's own AST at `tests/test_ledger.py:260-270`. The specific swap, named and then executed: replace `FileJournal(ledger_path)` with `InMemoryJournal()` at `__init__.py:39`. I did exactly that in a scratch copy — `diff -rq` reports `__init__.py` as the only differing file, no domain file touched — and the shared suite ran **28/28 against the swapped wiring with no file created on disk at all**. That is runtime evidence about what *calls* what, which is what the caveat demands over import topology.

**Anchor 4 on the letter, with the caveat's demotion condition tested rather than assumed.** `tests/test_ledger.py:26-36` wires the same `Ledger` to `FileJournal` and to `InMemoryJournal` from one fixture, and the whole behavioral case list runs twice (the `[file]`/`[memory]` pairs; 53 cases from ~26 bodies). Every case asserts a literal expected transcript — `["COMMIT globex 1 1", "COMMIT acme 4 4", …]` at :124-129 — never that the two wirings agree with each other, which is the trap two-wirings-of-one-domain sets. The fake is not a mock: `memory_journal.py:14-22` is a working implementation of the same contract, and the contract itself is exercised against both at :42-71 including the list-ownership clause.

The caveat says take 3 if the only observer of the effect the port exists for is the adapter that wrote it. **Here it is not:** `tests/test_ledger.py:241-248` asserts the bytes on disk with `path.read_text() == "COMMIT acme 1 1\nCLOSE acme 1\n"`, with `FileJournal.records()` out of the loop, and :251-254 pins truncate-on-construct. I proved those are load-bearing by seeding **F5** — a `FileJournal` that keeps a shadow list and never touches the disk — and exactly one test died, that one. So the demotion condition as written is false and 4 stands.

**What I record against it, and why 3 was close:** the independent observation lives *outside* the paired case list. Within the parametrized set the adapter is its own reader, and F5 shows all 26 paired cases and all 28 shared cases pass against an adapter that writes nothing durable. A judge reading the caveat as "the only observer *within the paired cases*" lands on 3 with the same evidence. That ambiguity, not the artifact, is what separates 3 from 4 here.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `tests/test_ledger.py:95-97`, `:100-105` — the id-allocation cases
- `tests/test_ledger.py:67-71` — list ownership
- `tests/test_ledger.py:241-248`, `:251-254` — the two file-observing cases
- `tests/test_ledger.py:175-199` — R4 including the durable side
- `quota_ledger/domain.py:137-144`, `:172-178` — the two ordered rejection chains

**Note:**

I seeded eleven faults, one per scratch copy, and ran both suites against each.

| Fault | Own suite | Shared suite |
|---|---|---|
| F1 `ledger_lines()` sorted (R5 order lost) | KILLED (6) | KILLED (4) |
| F2 `close_tenant` appends `CLOSE` before the outstanding check (R4, durable) | KILLED (2) | KILLED (1) |
| F3 `reserve` increments the id counter before its guards | KILLED (4) | **SURVIVED** |
| F4 swap `tenant_closed` / `amount_not_positive` precedence | **SURVIVED** | **SURVIVED** |
| F5 `FileJournal` keeps a shadow list, never touches the disk | KILLED (1) | **SURVIVED** |
| F6 `InMemoryJournal.records` returns its own list | KILLED (1) | **SURVIVED** |
| F7 `FileJournal` does not truncate an existing file | KILLED (1) | **SURVIVED** |
| F8 `available` drops the `committed` term | KILLED (6) | KILLED (2) |
| F9 running total summed across tenants | KILLED (4) | KILLED (2) |
| F10 `outstanding_ids` sorted lexicographically | KILLED (2) | **SURVIVED** |
| F11 `release` appends a `RELEASE` line | KILLED (6) | KILLED (1) |

**Caught by both** — so the shared floor already covers them: lost ledger order, a durable write on a rejection, `commit` handing the hold back, a global rather than per-tenant running total, and `release` leaving a trace.

**Caught only by the artifact's own suite** — where its 53 cases earn their keep over the shared 28: an id burned by a rejected `reserve` (F3, killed at `:95-97` and `:100-105`); `outstanding_ids` sorted lexicographically so `r10` precedes `r2` (F10, killed only at `:100-105` — the shared suite never gets past `r3`); `InMemoryJournal` handing out its internal list (F6, killed only at `:67-71`); no truncation on construct (F7, killed only at `:251-254`); and the one I care most about, **F5**, which killed exactly one case — `:241-248`, the test that reads `path.read_text()` with the adapter out of the loop — while all 26 paired behavioral cases and all 28 shared cases passed.

**Missed by both, demonstrably: rejection PRECEDENCE where two guards fire at once.** F4 swaps the `tenant_closed` and `amount_not_positive` checks at `domain.py:139-142`; both suites pass 53/53 and 28/28 against the faulty build. Concretely, on a closed tenant the clean build answers `reserve("acme", 0)` with `tenant_closed` and the faulty one with `amount_not_positive`, and neither suite ever reserves a bad amount against a closed tenant. `FEATURE.md` specifies the order explicitly ("Rejects, in this order") for both `reserve` and `close_tenant`, and the whole ordered chain is tested only one guard at a time — every rejection case in both suites arranges exactly one failing precondition. That is the class: **ordering constraints among guards, invisible to any suite that never makes two guards true at once.**

A second, narrower miss: the durable side of the port is pinned by exactly one non-parametrized case, so the ratio of file-observing cases to file-dependent behavior is 1:26.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `quota_ledger/domain.py:118-120` (R1), `:157` (R2), `:177-181` (R3), `:137-144` (R4)
- `quota_ledger/file_journal.py:29-31` (R5)
- `quota_ledger/__init__.py:37-39` — the one behavior preserved only by a name
- `tests/test_ledger.py:175-199`, `:202-220`
- `NOTES.md:136-141`

**Note:**

**There is no baseline in what I was given, and that is the answer rather than a gap.** `blind/` holds exactly three things — `artifact_under_score`, `FEATURE.md`, `shared_suite` — so there is no prior tree, no reference implementation and no earlier revision of this artifact to preserve behavior relative to. (The shared suite's fallback path at `test_behavior.py:32` points at a sibling `reference` directory, which is not in the packet; I did not go looking for it.)

So I enumerated against the only enumerable contract present, `FEATURE.md`'s five named rules, and checked each against the running code.

- **R1 conservation** — holds *by construction*: `available` is derived at `domain.py:118-120` rather than maintained. Asserted live at `test_behavior.py:239-255` and `tests/test_ledger.py:224-225`.
- **R2 the durable ledger agrees with memory** — holds in normal operation (per-tenant running total computed at `domain.py:157`, read back through the port; asserted at `test_behavior.py:258-267` and `tests/test_ledger.py:117-131`) but **not** under a failing durable write, which I verified rather than inferred: driving `Ledger` with a journal whose `append` raises leaves `committed("acme") == 3` and the reservation consumed with no line on the ledger. The artifact says so itself at `NOTES.md:136-141`.
- **R3 close is final and singular** — holds; outstanding guard at `domain.py:177`, the single `CLOSE` line at `:181`, the total-equals-committed clause at `test_behavior.py:186-197` and `tests/test_ledger.py:142-152`.
- **R4 a rejection changes nothing** — holds; every rejection returns before any mutation or append at `domain.py:137-144`, `:152-154`, `:163-164`, `:173-178`. `tests/test_ledger.py:175-199` is the stronger of the two suites' checks because its before/after snapshot includes `ledger_lines()`.
- **R5 append-only and ordered** — holds; `FileJournal` opens in `"a"` mode at `file_journal.py:30` and never rewrites; asserted end to end at `tests/test_ledger.py:202-220` and `test_behavior.py:270-281`.

One behavior `FEATURE.md` fixes is preserved **only by a name**: `QuotaLedger` is a factory function, not a class (`__init__.py:37`), which keeps the required construction signature while keeping paths out of the domain. `QuotaLedger(...)` still works and an `isinstance` against it would not; nothing in either suite depends on that.

### N-D5 — honesty

**Citations** (`file:line`):

- `NOTES.md:125-147` — four interpretations declared as choices, not as requirements
- `NOTES.md:136-141` — the volunteered R2 gap
- `NOTES.md:96-100`, `:149-157`
- `quota_ledger/domain.py:48-57`, `:73-75` — the closed rejection vocabulary
- `quota_ledger/file_journal.py:25-27`
- `tests/test_ledger.py:5-9`, `:251-254`, `:260-270`

**Note:**

It refuses, and the refusals are **checkable**, which is the only version of this that counts. Four claims at `NOTES.md:125-147` are stated as interpretations the author picked rather than behavior the feature required, and I checked all four against the running code: `available("nobody")` and `committed("nobody")` raise `KeyError` while `is_closed("nobody")` returns `False` (claim 1, true); construction truncates an existing file with no reopen-and-resume invented (claim 2, true — `file_journal.py:27`, pinned at `tests/test_ledger.py:251-254`); a failed durable write leaves memory moved with no rollback (claim 3, true — I reproduced it with an exploding journal and got `committed == 3` with an empty ledger); and `reserve("acme", 2.5)` is accepted and writes `COMMIT acme 2.5 2.5` because no type check was added rather than invent a seventh rejection reason (claim 4, true, verbatim).

Claim 3 is the strongest signal on this dimension: it is the artifact volunteering the single place where the rule it is judged against, R2, is not enforced by construction — and it is correct.

There are refusals in the code too, not only in prose. `domain.py:73-75` asserts every rejection reason is one of the six the feature declares at `:48-57`, so the vocabulary cannot be widened by accident. `tests/test_ledger.py:260-270` refuses to take "the domain does not import its I/O" on trust and parses the module's imports instead. `tests/test_ledger.py:5-9` states in terms why the paired cases assert literal values rather than agreement — "two wirings of the same domain agree with each other even when the domain is wrong". `NOTES.md:149-157` names which files were not opened.

**Where it is silent:** it does not name the gap I found by seeding — that the durable effect its port exists for is observed independently by exactly one test, so a `FileJournal` that never touches the disk passes everything else — nor the untested rejection precedence. Those are *unnamed limits*, not false certifications; nothing in `NOTES.md` claims either is covered, and `:96-100` comes close, correctly describing which two cases are file-specific without saying how much rides on them.

I set the prose quality aside deliberately: this file is persuasive enough that it could carry a weaker artifact, so every claim above is one I re-derived from the code or from a run.

## Verdict

A four-file quota ledger whose boundary is real under execution, not just under import inspection: the domain calls only `append`/`records`, the one-line adapter swap at `quota_ledger/__init__.py:39` passes 28/28 of the shared suite with nothing on disk, and the same case list runs against a real file adapter and a working in-memory one with literal expected transcripts on both — **D3 4**, with the honest limit that the disk is observed independently only by one test outside that paired list, so an adapter that never touches the filesystem survives 26 of 27 own cases and all 28 shared ones. Complexity is proportional and single-writer with `available` derived rather than stored (`domain.py:118-120`), but nothing measures it before or after, so **D2 2** and not 3. Of eleven faults I seeded, nine died and two lived: an id burned on a rejected `reserve` dies only in the artifact's own suite, and swapping the `tenant_closed` / `amount_not_positive` precedence dies in neither — the ordered rejection chain the feature specifies is untested wherever two guards fire at once. I did not identify which arm `GL` is, though `NOTES.md:102-123` quotes a structural instruction ("Section 1: the domain holds no file handle, no path") that this artifact's author was evidently given and that `FEATURE.md` explicitly does not contain.

## Disclosures

**Things I was exposed to that I was not meant to be.**

1. **My assigned scratch directory was not empty.** `.../scratchpad/judge-v5-p2/` already contained `base/`, `derived/`, `faultA/`, `faultB/`, `faultD/`, `faultE/` and `work/`, dated 2026-08-11 — a day before this card was scaffolded. A recursive listing incidentally showed me file *names* under `derived/`, including `reference_ports/{domain.py, journal_file.py, journal_memory.py, quota_ledger.py, quota_ledger_fake.py, README.md}` and `derived/FEATURE.md`. **I opened none of them.** I moved all my own work into a fresh `p2-20260812/` subdirectory and copied the artifact and shared suite in from the blind packet directly. A judge who had opened `derived/reference_ports/` would have been handed the baseline tree that N-D4 asks about and that the packet deliberately withholds. Recommend the operator give each pass a clean scratch path.
2. **`NOTES.md` leaks the existence of an arm prompt.** `NOTES.md:102-123` is a section titled "Where the feature file and the architecture ask conflicted", and it quotes an instruction — "Section 1: the domain holds 'no file handle, no path'" — that is not in `FEATURE.md` (which states at its head that it contains no guidance about structure or layering). So this artifact was written under a structural prompt. **I did not work out the arm label** and did not go looking for the mapping; I note only that the artifact's own prose reveals which side of the with-prompt / without-prompt axis it sits on, which defeats blinding for the `GL` card independently of anything the operator did. Any judge reading `NOTES.md` gets this for free.

3. **`git status --porcelain`, run at the end to confirm I had left the repository alone.** It printed the *paths* of two other cards — `score-drives-validation-sv01-v4/ab_quota_ledger/20260812-sv01v4-GL-p1/` and `.../GL-p2/` — as modified. So I now know a version-4 round scored an artifact under this same opaque label, and that its two passes have been filled. **I opened neither, and neither their scores nor their contents are known to me.** I judged `git status` to be outside the dispatch's ban on "`git log`, `git show`, `git diff`, `git blame`, or any other route into this repository's history" — it reports the working tree, not history — but it is adjacent enough to be worth recording, and the operator may want the ban widened to `git status` for future passes.

**What I ran that changed a tree.** Nothing in the repository was edited. The two dispatch-sanctioned in-place commands were run inside `artifact_under_score`, which regenerates `quota_ledger/__pycache__/*.pyc` (that directory already existed, dated before I started). All mutation, the adapter swap and the claim-checking scripts ran on copies under my scratch path.

**What I rejected.**

- **D3 3, which I nearly gave.** F5 is genuinely uncomfortable: a `FileJournal` that never opens a file passes every case in the paired list and every case in the shared suite. That is very close to the caveat's "the real adapter does nothing real". I set it aside because the caveat's stated test is whether the *only* observer of the effect is the adapter that wrote it, and it is not — `tests/test_ledger.py:241-248` reads the bytes off disk with the adapter out of the loop, and F5 dies there. Demoting anyway would have meant demoting on a condition the rubric does not state (that the independent observation must live *inside* the paired set). I record the reading so a reader can apply it themselves; it is the single most contestable judgement on this card.
- **D2 0, which the literal wording of "score the LOWEST anchor fully satisfied" would force**, since complexity here is unmeasured and rung 0 says exactly that. Rejected in favour of the dimension's own `read_first` ("where none exists that is not a gap in the evidence"). The ladder's rungs 0–1 grade the *report* and 2–3 grade the *design*, and an artifact can satisfy 0 and 2 simultaneously. **This is a defect in the D2 ladder, not in the artifact**, and it will produce a 0-vs-2 split between any two judges who weight the anchor text and the `read_first` differently — a two-point gap on byte-identical evidence, which rule 5 would record as `contested`.
- **D2 3 on the strength of `NOTES.md:70-84`.** The derived-`available` argument is a real simplification argued in exactly the terms MF-020 asks for, and the temptation was to treat "the behavior survived it, and here are the two tests that prove it" as satisfying the rung. It does not: the rung asks for *before and after figures*, and there are none, and no second tree to produce them from.
- **Reading `mechanical.json` as evidence.** Its `figures` block is entirely empty, so there was nothing to disagree with; I left the file untouched per rule 7 rather than backfill my own LOC and kill counts into it. The counts are in `judging_practice.what_was_run` and in N-D1 instead.
- **Counting the shared suite as evidence of anything.** It passed 28/28 against the artifact, against the artifact with an in-memory journal swapped in, and against six of my eleven faulty builds. It is a floor, exactly as it says at `test_behavior.py:10-12`, and it contributed nothing to either score.
