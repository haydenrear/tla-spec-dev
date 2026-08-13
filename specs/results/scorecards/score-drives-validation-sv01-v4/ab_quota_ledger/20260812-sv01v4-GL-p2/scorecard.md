# Scorecard — ab_quota_ledger, artifact `GL`, judge pass 2

`run_id`: `20260812-sv01v4-GL-p2` · scorecard_version 4 · rubric `examples/validation/scorecards/rubric_v4_frozen.md` digest `sha256:497c16ca85adeb4a` · served `sha256:a213a36770ccab09`

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
9. **A judge is served the card, never the rubric file.** *(New in version 3.)* The scaffolded `scorecard.md` carries the rubric a judge needs. This file carries reading rules and prior results about these dimensions as well, and a judge who reads it is handed conclusions about the instrument they are the instrument for. Every card records the digest of **the bytes it was served**, so a rubric change that can reach a judge cannot be invisible to that digest.
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

**Executed own faults:** **true**

**What was run:**

- The artifact's own suite, unmodified, from the artifact directory: `uv run --with pytest python -m pytest tests/test_ledger.py -q` → **53 passed in 0.10s**. Confirms the count claimed at `NOTES.md:14`.
- The shared suite against the artifact: `QUOTA_LEDGER_DIR=<artifact> QUOTA_LEDGER_IMPL=quota_ledger uv run --with pytest python -m pytest <blind>/shared_suite/test_behavior.py -q` → **28 passed in 0.28s**. Confirms the count claimed at `NOTES.md:27`.
- **Twenty-seven seeded faults**, in two batches, each applied to a fresh copy of the artifact under my own scratch directory (`scratchpad/judge-v4-p2/work`, `work2`) and never to the repository. Both suites run against every mutant. Scripts: `scratchpad/judge-v4-p2/mutate.py`, `mutate2.py`.
- Batch 1 (21 mutants; 2 turned out to be no-ops of my own making and 1 — reordering `amount_not_positive` against `quota_exceeded` — is an **equivalent mutant**, since `amount < 1` and `amount > available` are mutually exclusive, so its survival is not a miss and I do not count it): commit returns the hold; rejection reorderings; release writes a durable line; running total off by one; `outstanding_ids` sorted lexicographically; id reuse; a rejected reserve burning an id; the quota boundary flipped to `>=`; close blocked by any tenant's reservation; `CLOSE` writing quota instead of committed; `FileJournal.records` keeping blanks; `FileJournal` not truncating; `InMemoryJournal` leaking its internal list; `committed()` reporting held+committed; `is_closed` always False; the `QuotaLedger` factory rewired to `InMemoryJournal`; the domain importing its adapter; a float amount reaching the ledger line.
- Batch 2 (7 mutants, written specifically against the rejection **precedence** FEATURE.md states and the cross-tenant isolation of `close_tenant`): three genuine reorderings of the four reserve guards; close blocked by another tenant's reservation; `ledger_lines` mutating the journal's returned list; commit not removing the reservation; `FileJournal` writing CRLF.
- A direct runtime probe reading the actual bytes the public `QuotaLedger` entry point puts on disk (`b'COMMIT acme 3 3\n'`), checking the precedence the real artifact produces for a closed tenant asked for amount 0 (`tenant_closed` — correct) and amount 99 (`tenant_closed` — correct), and confirming `available("nobody")` raises `KeyError` and `is_closed("nobody")` returns `False` as `NOTES.md` claims.
- **A third driven adapter of my own** (`SqliteishJournal`, a list of `(index, record)` rows), constructed in scratch and handed to `Ledger` with no artifact file modified, run through a mixed reserve/commit/release/close scenario alongside `FileJournal` and `InMemoryJournal`. All three returned identical observable state.
- A `sys.addaudithook` **I/O audit** over that same scenario, filtering on `open`/`os.`/`io.`/`socket.`/`subprocess.`/`time.`: **zero** events when the domain is driven by the fake journal, exactly `['open']` when driven by the file journal.
- `pytest --collect-only` to confirm the `[file]`/`[memory]` parametrization is symmetric and not degenerate: 16 ids each, plus the 9×2 rejection matrix, plus 3 unparametrized = 53.
- `ls` of the blind packet to establish that **no baseline or reference tree was shipped** (only `artifact_under_score`, `FEATURE.md`, `shared_suite`) — the basis for N-D4.
- **Nothing was written to the repository.** Every mutation and probe ran on copies under `scratchpad/judge-v4-p2/`.

## Your scores

### D2 — complexity

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger/domain.py:118` — `available` derived (`quota - held - committed`), not stored
- `quota_ledger/domain.py:106` — the four written state slots, and only four
- `quota_ledger/domain.py:151` — commit's running total computed from `_committed` in the assignment itself
- `quota_ledger/domain.py:186` — `_holdings`, the single place that maps tenant → reservations
- `quota_ledger/domain.py:172` — the close guard reading that same helper
- `NOTES.md:69` — the simplification argued
- `NOTES.md:81` — the three written pieces of state, as the author counts them

**Refuses to claim** (required and non-null for a score of 3): _n/a — not scored at the top of the scale._

**Rationale:**

I applied the `read_first` test literally: I went looking for one fact stored twice, kept in agreement by hand across several write sites and read in one place, and I did not find one. There are exactly four written slots (`quota_ledger/domain.py:106`–114): `_outstanding`, `_committed` (written only at `:158`), `_closed` (written only at `:180`), and the `_issued` counter (written only at `:146`, and only after every rejection has returned, so a rejection cannot burn an id). The fact most likely to be duplicated in this feature — `available` — is not stored at all; it is computed per call at `:118`–120, so R1 is arithmetic rather than an invariant three commands must remember. The second candidate, the running total on each `COMMIT` line, is computed from `_committed` in the same expression that assigns it (`:157`–159) rather than maintained beside it, so the durable and in-memory totals cannot disagree by drift — only by a failed write, which the author names. `_holdings` at `:186` is the single place that knows which reservations belong to a tenant, and both the R1 arithmetic and the close guard at `:177` read it. No god-state, no variable written from everywhere.

**I did not give 3.** Anchor 3 wants a simplification whose effect was *measured*, before and after figures both recorded. `NOTES.md:69`–79 argues a simplification — `available` derived rather than stored — and argues it well, and I can independently say what got simpler and that the behavior survived: my seeded fault M01 (commit returns the hold to `available`) is killed by 6 of the artifact's cases and 2 of the shared suite's. But there are no figures, before or after, anywhere in this packet, and there is no second tree to diff: `blind/` contains only `artifact_under_score`, `FEATURE.md` and `shared_suite`. An argued simplification with a surviving behavior is anchor 2 plus a good paragraph. The caveat's MF-020 warning cuts the same way in reverse: if a dropped number is not evidence, a well-argued paragraph with no number is not the measurement anchor 3 names.

**I also did not give 0 or 1.** Nothing here is measured — `mechanical.json` figures are empty and `NOTES.md` reports no complexity descriptor. On a strictly cumulative reading that is anchor 0 ("complexity is unmeasured"). I rejected that reading because this dimension's own `read_first` says that where no measured descriptor exists "that is not a gap in the evidence", which would be self-contradictory if a missing descriptor floored the score at 0. So I read rungs 0–1 as being about what a report *does with figures it has*, and rungs 2–3 as being about the design, and I scored the design. **This is the most contestable judgement on my card and I am flagging it rather than burying it.**

On rule 4: the prose here is unusually good and it did tempt me. `NOTES.md` pre-argues D2's exact case in D2's exact vocabulary — "R1 is true by construction and cannot drift", "this is a *derivation*, not a deletion" — and that is an artifact asking to be scored 3. I checked its two load-bearing claims against the code instead (`available` really is uncomputed at `:118`; `_committed` really has one writer at `:158`) and they hold, so the score reflects the code. The paragraph that would have earned the extra rung is the one thing I refused to count.

### D3 — modularity

**Score:** **4**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger/domain.py:13` — the domain imports `__future__`, `dataclasses`, `typing`, and nothing else
- `quota_ledger/domain.py:22` — the `Journal` port, declared in the domain's own vocabulary with its contract written on it
- `quota_ledger/domain.py:159` — the domain's outward call, through the port
- `quota_ledger/__init__.py:37` — the composition root; the one line the swap changes
- `quota_ledger/file_journal.py:29` — the real driven adapter
- `quota_ledger/memory_journal.py:18` — the fake driven adapter
- `tests/test_ledger.py:26` — the fixture parametrized over `["file", "memory"]` that every behavioral case consumes
- `tests/test_ledger.py:117` — cases asserting literal expected values, not that the two wirings agree
- `tests/test_ledger.py:260` — the AST assertion that the domain imports no adapter

**Refuses to claim** (required and non-null for a score of 4):

The artifact refuses to claim that **R2 is enforced by construction**. `NOTES.md:136`–141 states that `commit` and `close_tenant` update memory and *then* append, that a raised append would leave memory ahead of the durable record, and that since the feature specifies no failure or atomicity semantics the author built no rollback and no write-ahead ordering — ending with "this is the one place I can name where R2 is not enforced by construction." I confirmed the ordering it admits to at `quota_ledger/domain.py:156`–159 and `:180`–181. It likewise declines to invent behavior it was not given: `NOTES.md:126`–145 records four unspecified points as *interpretations picked* rather than requirements met — queries on an unknown tenant (`available` raises `KeyError`, confirmed), an existing file at the path (`file_journal.py:27` truncates), no reopen-and-resume, and non-integer amounts, where it explicitly says a type check was **not** added because the rejection vocabulary is fixed at six and a seventh reason would be scope it was not given.

**Rationale:**

The caveat says import topology is not modularity and that 3-or-more needs evidence about what *calls* what at runtime, so I did not score this off the import graph. I ran three things.

**(1) The named swap, executed.** The one-line swap the author names — `FileJournal(ledger_path)` → `InMemoryJournal()` at `quota_ledger/__init__.py:39` — is real, but a swap between the artifact's own two adapters is a weak test because both came from the same hand. So I wrote a **third** adapter of my own (a row-list `SqliteishJournal` the artifact has never seen), handed it to `Ledger` directly, and ran a mixed reserve/commit/release/close scenario against all three. All three returned identical `ledger_lines`, `available`, `committed`, `is_closed` and `outstanding_ids`. No file in `quota_ledger/` was edited to make that work. That is the specific swap, *performed* rather than asserted.

**(2) Runtime call evidence, not import evidence.** I installed a `sys.addaudithook` filtering on `open`/`os.`/`io.`/`socket.`/`subprocess.`/`time.` and ran the same scenario twice. Driven by the fake journal the domain produced **zero** I/O audit events; driven by `FileJournal` it produced exactly one, `open`. That is a runtime demonstration that every byte of I/O in this program is reached through `Journal.append`/`Journal.records` (`domain.py:22`–43) and that the rules themselves touch nothing.

**(3) Anchor 4's specific bar.** `tests/test_ledger.py:26`–36 parametrizes a fixture over `["file", "memory"]` that every behavioral case consumes, so one case list runs against the real adapter and the fake. I confirmed this is not degenerate by collecting ids: 16 `[file]` and 16 `[memory]` variants plus the 9×2 rejection matrix, 53 total, all passing. Crucially the cases assert **literal expected values** (`:117`, `:124`–129: `["COMMIT globex 1 1", "COMMIT acme 4 4", …]`) rather than asserting that the two wirings agree with each other — the failure mode where a fake and a real adapter agree perfectly about a domain that is wrong. That is the difference between anchor 4 and a tautology, and this artifact is on the right side of it.

**Why 4 and not 3, given the tie-break rule.** I was genuinely torn, and the thing that nearly held me at 3 is this: **the composition root is untested.** I seeded a fault (M17) rewiring the public `QuotaLedger` factory at `__init__.py:39` to `InMemoryJournal()` — so the shipped program has no durable side at all and never creates the ledger file — and *both* suites pass, 53 and 28. The artifact's file cases construct `FileJournal` directly (`tests/test_ledger.py:241`, `:251`) and never go through the factory; the shared suite reads `ledger_lines()` and never looks at the path it passed in. I set that aside for D3 because anchor 4 asks whether a driven port is exercised by a real adapter *and* a fake with the same cases passing against both, and it demonstrably is; M17 is a hole in the **cases**, not in the boundary, and it is recorded under N-D1 where it belongs. A reader who thinks the top modularity rung should require the production wiring to be pinned should read this as a 3, and the evidence for that reading is written here rather than left out.

I also checked the boundary is not merely declared. `domain.py:13`–16 imports three stdlib names and nothing else, and the artifact tests that claim by parsing its own imports (`tests/test_ledger.py:260`–270) — an assertion about the file rather than about intent. I verified that test does work by seeding M18 (add `from .file_journal import FileJournal` to the domain, behavior otherwise untouched): the artifact's suite kills it, the shared suite does not notice.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `tests/test_ledger.py:175` — R4 across every observable including the durable one
- `tests/test_ledger.py:100` — ids ascending past `r10`
- `tests/test_ledger.py:241`, `tests/test_ledger.py:251` — the two file-specific cases, which bypass the factory
- `tests/test_ledger.py:260` — the AST import assertion
- `quota_ledger/__init__.py:39` — the untested composition root
- `quota_ledger/domain.py:139` — the precedence guard nothing exercises
- `quota_ledger/domain.py:177`, `quota_ledger/domain.py:186` — per-tenant close isolation, unproven
- `quota_ledger/file_journal.py:31` — the newline the disk assertion cannot see
- `NOTES.md:98` — the claim that outruns that assertion

**Note:**

I seeded **27 faults**; after discarding 2 no-ops of my own making and 1 equivalent mutant, **24 were live**. The artifact's own 53 cases killed **20 of 24**; the shared suite killed **14 of 24**. The gap between them is the artifact's contribution and it is real: id reuse, lexicographic ordering of `outstanding_ids` past `r10` (`tests/test_ledger.py:100`), a second `FileJournal` at the same path not starting empty (`:251`), `InMemoryJournal` leaking its internal list to the caller (`:67`), and the domain importing an adapter (`:260`) are all killed by the artifact's suite and all survive the shared floor. `tests/test_ledger.py:175`–199 is the strongest single case: it snapshots every observable **including `ledger_lines`** across nine rejections, so R4's durable half is actually checked rather than assumed.

**Four classes were demonstrably missed**, and I confirmed each by seeding it and watching both suites pass.

**(1) The composition root is untested (fault M17).** Rewrite `quota_ledger/__init__.py:39` from `Ledger(quotas, FileJournal(ledger_path))` to `Ledger(quotas, InMemoryJournal())` — the shipped program now has no durable side, creates no file, and loses everything on exit — and 53/53 and 28/28 still pass. The artifact's file cases construct `FileJournal` directly (`tests/test_ledger.py:241`, `:251`) and never go through the factory; the shared suite reads `ledger_lines()` and never looks at the path it passed in. **Nothing in either suite asserts that the file at the constructed path exists or has content.** This is the most valuable thing I found and it is a hole in the highest-value line of the program.

**(2) Rejection precedence is untested (faults M21, M22).** `FEATURE.md` states reserve's rejections "in this order": `unknown_tenant`, `tenant_closed`, `amount_not_positive`, `quota_exceeded`. Move the `amount < 1` guard at `quota_ledger/domain.py:141` above the `tenant in self._closed` guard at `:139` and a closed tenant asked to reserve 0 answers `amount_not_positive` where the spec requires `tenant_closed`. Both suites pass. Neither suite ever constructs an input that violates two guards at once, so the **order** — an explicit, numbered requirement — has no coverage at all. (For the record, reordering `amount_not_positive` against `quota_exceeded` is an *equivalent* mutant, since `amount < 1` and `amount > available` cannot both hold; only the closed-tenant precedence is genuinely uncovered.) The real code gets this right: I confirmed by probe that the shipped artifact answers `tenant_closed` for both amount 0 and amount 99 on a closed tenant.

**(3) Cross-tenant isolation of `close_tenant` is untested (fault M24).** Change the guard at `quota_ledger/domain.py:177` from `self._holdings(tenant)` to also reject when **any other** tenant holds a live reservation, and both suites pass. Every close in both suites happens either with nothing outstanding anywhere or with a reservation belonging to the tenant being closed; no case closes tenant A while tenant B holds one. `_holdings` at `:186` exists precisely to make close per-tenant, and nothing proves it does.

**(4) The one case that reads the disk does not read bytes (fault M27).** `tests/test_ledger.py:247` asserts `path.read_text() == "COMMIT acme 1 1\nCLOSE acme 1\n"`, and `NOTES.md:98`–100 presents it as checking "that the bytes on disk are one record per line". `Path.read_text()` opens in text mode and performs universal-newline translation, so changing `file_journal.py:31` to write `record + "\r\n"` passes that assertion untouched. I verified the translation directly: a file written as `b'…\r\n…\r\n'` compares equal to the LF literal. The fix is `read_bytes()`; the claim is one word stronger than the assertion supports.

Also missed, and named by the author rather than found by me — so I count it as disclosed rather than as a gap: a float amount is accepted (`NOTES.md:142`–145). That one is in fact killed by both suites once it reaches a ledger line, since `COMMIT acme 3.0 3.0` is not the expected literal — a case of exact-string assertions catching a class their author did not aim them at.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `quota_ledger/domain.py:118`, `:136`, `:157`, `:177` — the derived `available`, the guards in stated order, R2's running total, R3's finality
- `quota_ledger/file_journal.py:29` — append-only mode, R5
- `tests/test_ledger.py:114`, `tests/test_ledger.py:175` — the trickiest sentence, and R4
- `shared_suite/test_behavior.py:32` — the reference directory the packet does not ship
- `shared_suite/test_behavior.py:117` — the same behavior asserted from the floor
- `NOTES.md:69` — the simplification framed as a derivation

**Note:**

**There is no baseline, and I checked rather than assumed.** The blind packet contains exactly three entries — `artifact_under_score/`, `FEATURE.md`, `shared_suite/` — and no `reference/` tree, no prior version of the artifact, and no second implementation to diff against. (The shared suite's own default at `shared_suite/test_behavior.py:32` points at a sibling `reference` directory that was **not** shipped into the blind packet, which is presumably deliberate: a judge who could run the reference could diff the two trees.) The repository's history would be the other route to a baseline and reading it is out of bounds for this card. So there is no before-state whose preservation could be demonstrated, and D2 anchor 3's "before and after figures" is unreachable for this artifact on this packet — part of why D2 is a 2.

What I could do instead is enumerate the behaviors `FEATURE.md` fixes and check each against the code and against an execution, treating the specification as the thing that must be preserved. **All fifteen hold.** Five queries: `available` derived at `quota_ledger/domain.py:118`, `committed` `:122`, `is_closed` `:125`, `outstanding_ids` `:128` (insertion-ordered; verified past `r10` by the artifact's own case at `tests/test_ledger.py:100` and by my lexicographic-sort fault M06 dying there), `ledger_lines` `:131`. Four commands with their guards in `FEATURE.md`'s stated order at `domain.py:136`–182 — and I confirmed by probe that the shipped code answers `tenant_closed`, not `amount_not_positive`, for a closed tenant asked to reserve 0, so the order is right in the code even though nothing tests it. Five rules: **R1** holds by construction because `available` is computed rather than stored (`:118`–120), and fault M01 (commit returns the hold) is killed 6-and-2; **R2**'s running total is computed from `_committed` in the assignment itself (`:157`–159), and M05 (write the pre-commit total) is killed 26-and-6; **R3**'s finality is guarded at `:177` and its single `CLOSE` line written at `:181`, and M11 (write quota instead of committed) is killed 6-and-3; **R4** is asserted across every observable including the durable one at `tests/test_ledger.py:175`–199, and M08b (a rejected reserve burning an id) is killed 8-and-2; **R5**'s append-only ordering follows from `file_journal.py:29`–31 opening in `"a"` mode and never rewriting, and M04 (release writes a line) is killed 6-and-1.

The one behavior the artifact itself frames as at risk from its own design decision is worth naming: `NOTES.md:69`–79 argues that deriving `available` rather than storing it is "a *derivation*, not a deletion" and that the feature's trickiest sentence — committing does not give the hold back — now falls out rather than being maintained. That is exactly the shape MF-020 warns about: a thing looking simpler because something was removed. I tested it rather than accepting it. The behavior is still asserted by name and value at `tests/test_ledger.py:114` and in the shared suite at `test_behavior.py:117`, and my M01 fault, which restores the hold on commit, is killed by both. **The simplification did not take the behavior with it.**

### N-D5 — honesty

**Citations** (`file:line`):

- `NOTES.md:136` — the atomicity refusal
- `NOTES.md:126` — four interpretations recorded as choices
- `NOTES.md:102` — the conflict between the feature and the structural ask, and the alternative rejected
- `NOTES.md:149` — files not opened; nothing written to the repository
- `NOTES.md:96` — the claim about literal assertions (verified true)
- `quota_ledger/domain.py:156` — the memory-then-append ordering it confesses to
- `quota_ledger/__init__.py:37` — the factory the conflict note explains
- `quota_ledger/file_journal.py:19` — the framing the disk assertion fails to pin
- `tests/test_ledger.py:241` — the assertion that does not read bytes
- `tests/test_ledger.py:260` — the import claim it does test

**Note:**

It refuses in four distinct places, and the refusals are load-bearing rather than decorative. **First**, the atomicity refusal at `NOTES.md:136`–141: `commit` and `close_tenant` update memory and then append, a raised append would leave memory ahead of the durable record, and rather than building a rollback the author writes "this is the one place I can name where R2 is not enforced by construction." I verified the ordering it confesses to at `quota_ledger/domain.py:156`–159 and `:180`–181. It is accurate, it is the sharpest limitation in the program, and the artifact volunteered it. **Second**, four interpretations recorded as choices rather than requirements met (`NOTES.md:126`–145): queries on an unknown tenant (I confirmed `available("nobody")` raises `KeyError` and `is_closed("nobody")` returns `False`, exactly as stated), truncation of an existing file, no reopen-and-resume, and non-integer amounts — where it explicitly declines to add a type check because "the vocabulary is fixed at six", a refusal to invent scope. **Third**, `NOTES.md:102`–123 records where `FEATURE.md` and its structural instructions conflicted and how it resolved the conflict, including the alternative it rejected and why — a disclosure that makes the odd factory-named-like-a-class at `quota_ledger/__init__.py:37` legible instead of leaving a reader to guess. **Fourth**, `NOTES.md:149`–157 states which files it did not open and that it wrote nothing to the repository.

Against rule 1 I checked every claim in `NOTES.md` that would move a score, and they hold: 53 own cases and 28 shared (both confirmed by running them); the domain importing only `__future__`/`dataclasses`/`typing` (confirmed by reading `domain.py:13`–16 and by the artifact's own AST assertion at `tests/test_ledger.py:260`); the one-line swap at `__init__.py:39` (confirmed by performing it, and by performing a harder version with an adapter of my own); and the claim at `NOTES.md:96`–100 that every case asserts a literal expected value rather than that the two wirings agree (confirmed by reading the cases — this is the difference between anchor-4 evidence and a tautology, and it is the claim I most expected to fail).

**One overclaim, small but real**, and the only place where the prose outruns the artifact. `NOTES.md:98`–100 says two file-specific tests exist because they are about the file rather than the rules, one of them checking "that the bytes on disk are one record per line". That test, `tests/test_ledger.py:241`–248, does not read bytes: it compares `path.read_text()`, which performs universal-newline translation, so a `FileJournal` writing CRLF at `file_journal.py:31` passes it unchanged — I seeded exactly that fault and both suites passed. The docstring at `file_journal.py:19`–22 likewise says the trailing-newline framing is the adapter's business, which is true and is precisely the framing that assertion fails to pin. This is a claim about a test's *reach* that the test does not support, not a false statement about behavior — and it is the honest answer to "where does this artifact certify more than it can see." The larger unseen thing it does not name at all is that its own suite cannot tell whether the shipped program is wired to the real adapter (fault M17, under N-D1): the notes describe the swap as a feature and never observe that nothing would notice if the swap were made in production by accident.

## Verdict

A four-file quota ledger whose boundary is real under runtime inspection and not merely declared: I wrote a third journal adapter of my own and drove the domain with it unchanged, and an audit hook shows the rules emit zero I/O events behind the fake and exactly one `open` behind the file adapter, so **D3 is a 4** on executed evidence rather than on the import graph (**D2 is a 2**: the design stores no fact twice and `available` is derived rather than maintained, but the simplification the author argues for is argued, not measured, and there is no second tree in the packet to diff or any figure before or after). The finding worth more than either number is that 27 seeded faults located a consistent blind spot rather than a weak suite: the artifact's 53 cases kill 20 of them and out-catch the shared floor on id reuse, lexicographic id ordering, file truncation, list aliasing and the domain's own imports — but rewiring the public `QuotaLedger` factory to the in-memory journal, so the program never writes a durable file at all, passes both suites, as does closing a tenant while a *different* tenant holds a live reservation, as does inverting `FEATURE.md`'s stated rejection precedence so a closed tenant asked for a zero amount answers `amount_not_positive` instead of `tenant_closed`. The code is right on all three; nothing tests any of them, and the one case that presents itself as reading bytes off disk compares through `Path.read_text()`, which silently normalises CRLF, so a line-ending fault survives it too. I remained blind to the arm and worked out nothing about provenance.

## Disclosures

**One out-of-bounds action, disclosed.** After the card was written and both scores were fixed, I ran `git status --short` to confirm I had left the repository clean. The dispatch forbids "`git log`, `git show`, `git diff`, `git blame`, or any other route into this repository's history", and `git status` is fairly read as covered by that clause. Its output listed the *paths* of four other modified scorecards — a sibling `…-GL-p1/` pass-1 card in this same round, and a `score-drives-validation-sv01-v5/…-GL-p2/` card from a round I did not know existed. **I opened none of them and I saw no contents, no scores and no arm mapping — filenames only.** It came after scoring and could not have moved my numbers, but it is recorded here rather than left out, and a reader who wants to treat this card as compromised has the fact to do it with. I ran no other `git` command.

**Nothing else out of bounds was read.** I read only this `CARD_DIR`, everything under `.../SV-01/blind/`, and my own scratch. I did not open `references/eval_scorecard.md`, `rubric_v4_frozen.md`, any other scorecard, `PREDICTIONS-SV-01.md` or anything else directly under `SV-01/`, any of `examples/validation/` beyond the two packet copies, any `*-EPIC.md`/`NEXT-EPIC.md`/`SKILL.md`/`README.md`, or `specs/desired_program_model/`.

**Nothing in the repository was changed.** All 27 mutations and every probe ran on copies under `scratchpad/judge-v4-p2/`. The only repository files I wrote are this card and `scorecard.json` beside it. Note that running the artifact's suite from the artifact directory does create `__pycache__` and `.pytest_cache`; I passed `-p no:cacheprovider` for the mutation runs, but the two baseline runs were made in place with the documented commands.

**Provenance.** I worked out nothing about which arm `GL` is. `NOTES.md:102`–123 refers to "the architecture ask" and "Section 1" of a prompt I was not given, which tells me an arm prompt existed and said something about the domain holding "no file handle, no path" — but that is a fact about this artifact's own instructions, not a mapping from `GL` to an arm name, and I made no attempt to resolve it. I did not read `subjects.toml` or any predictions file.

**What I rejected.**

- **D3 = 3, which I nearly gave.** The argument was M17: the composition root is untested, so nothing proves the shipped program is wired to the real adapter, and a top modularity score for a program whose production wiring could silently be the fake felt like scoring the demo rather than the delivery. I set it aside because anchor 4's bar is about a *driven port exercised by a real adapter and a fake with the same cases passing against both*, which is met and which I verified three ways, and because M17 is a defect in the case list, not in the boundary. It is recorded under N-D1 instead of being laundered into a lower D3, and a reader who weighs it differently has everything needed to read this as a 3.
- **D2 = 0, which the ladder's literal cumulative reading demands.** Nothing in this artifact is measured; `mechanical.json` is empty. I rejected that reading because the dimension's own `read_first` states that a missing complexity descriptor "is not a gap in the evidence", which cannot be reconciled with a 0 floor for unmeasured work. This is the most contestable call on my card.
- **D2 = 3, which the prose argues for.** `NOTES.md:69`–79 makes the simplification case in the rubric's own vocabulary. I confirmed the simplification is real and that the behavior survived it (M01 dies 6-and-2), but "the before and after figures are both recorded" is simply false here — there are no figures and no second tree — so the rung is not reached. Rule 4 in action: the best-written paragraph in the packet is the one I declined to count.
- **Three mutants I discarded rather than reported as findings.** Two batch-1 mutants (M08, M19) turned out to be no-ops of my own construction, and one (M02, swapping `amount_not_positive` against `quota_exceeded`) is an **equivalent mutant** — `amount < 1` and `amount > available` are mutually exclusive over the reachable state space, so no input distinguishes the two orderings. I nearly reported M02 as a fourth precedence miss and it would have been wrong. I wrote batch 2 specifically to replace it with reorderings that a real input *can* distinguish, and two of those (M21, M22) are the genuine finding.
- **The 53-vs-28 case count as evidence of anything.** The artifact's suite is larger than the floor, but 34 of its 53 ids are the same cases run twice through the parametrized fixture, so the count overstates distinct coverage by roughly double. I used kill results, not case counts. `mechanical.json` is left as scaffolded: I did not have a defensible reach figure to print beside my kills, and rule 7 says the block is recorded, never scored, so an unsupported number there would be worse than an empty one.
