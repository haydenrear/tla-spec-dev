# Scorecard — ab_quota_ledger, artifact `GL`, judge pass 1

`run_id`: `20260812-sv01v5-GL-p1` · scorecard_version 5 · rubric `references/eval_scorecard.md` digest `sha256:24b2c599901d7ae0` · served `sha256:2d7d4a0506d9b259`

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

**Executed own faults:** true

**What was run:**

- The artifact's own suite, in place, unmodified: `uv run --with pytest python -m pytest tests/test_ledger.py -q` -> 53 passed in 0.09s. Re-run 3x on a scratch copy: 53 passed each time, 0.40s/0.19s/0.18s.
- The shared suite against the artifact: `QUOTA_LEDGER_DIR=$ARTIFACT QUOTA_LEDGER_IMPL=quota_ledger uv run --with pytest python -m pytest .../shared_suite/test_behavior.py -q` -> 28 passed in 0.19s. Re-run 3x: 28 passed, 0.07s each. (Both counts match NOTES.md:27-28; I ran them rather than take the claim.)
- SEEDED FAULTS: 20 hand-written mutants applied one at a time to a COPY of the artifact under my scratch dir (`p1-mine/mutate.py`), each run against BOTH suites. Nothing was mutated in the repository. Own suite killed 17/20; shared suite killed 13/20; 3 survived both. Full matrix in `mechanical.json` and in N-D1.
- RUNTIME BOUNDARY TRACE (`p1-mine/runtime_trace.py`): a recording proxy wrapped around the Journal handed to `Ledger`, recording every attribute the domain touched over a mixed accept/reject scenario -> exactly {`append`, `records`}. Plus a `sys.addaudithook` on the `open` event over the same scenario driven through the `QuotaLedger` factory -> 12 opens, all with `file_journal.py:27/30/34` as innermost project frame, none from `domain.py`. Plus raw-bytes read of the ledger file independent of the adapter's own `records()`.
- Direct behavioral probes of edges no case covers: rejection-guard precedence (`reserve("nobody", 0)` -> `unknown_tenant`; `reserve("acme", 0)` on a closed tenant -> `tenant_closed`), non-integer amounts (`reserve("acme", 2.5)` -> accepted, writes `COMMIT acme 2.5 2.5`, `available` becomes 7.5), and queries on an unknown tenant (`available` raises KeyError, `is_closed` returns False).
- Executed the swap the artifact names: replaced `FileJournal(ledger_path)` with `InMemoryJournal()` at `__init__.py:39` on a copy and re-ran both suites, to check the claim 'no domain file changes' by doing it rather than reading it.
- My own AST branch count over `quota_ledger/*.py` (23 callables, sum cc=36, max cc=5 at `domain.py:136`) and a `--collect-only` count of the file/memory parametrisation (25 cases per wiring + 3 unparametrised).

## Your scores

### D2 — complexity

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger/domain.py:106`
- `quota_ledger/domain.py:118`
- `quota_ledger/domain.py:146`
- `quota_ledger/domain.py:158`
- `quota_ledger/domain.py:159`
- `quota_ledger/domain.py:180`
- `quota_ledger/domain.py:186`
- `quota_ledger/__init__.py:39`

**Refuses to claim** (required and non-null for a score of 3): n/a — not the top of this scale. The limit I would have named is recorded under D3 and N-D5.

**Rationale:**

Anchor 2 is fully met and anchor 3 is not, so 2. On anchor 2, I did the read_first exercise and looked for one fact stored twice. The candidate is `available`, and it is NOT stored: `domain.py:118` computes `quota - held - committed` on every call, so R1 is true by construction and there is no write site to keep in agreement. The four fields that ARE written (`domain.py:106-114`) each have a single writer that I checked by reading every assignment: `_committed` only at `:158` (commit), `_closed` only at `:180` (close_tenant), `_issued` only at `:146` (reserve, and only past the rejection guards). `_outstanding` has three write sites (`:148`, `:156`, `:169`) but they are add/remove on a reservation's own lifecycle, not three copies of one fact held in agreement by hand. No god-state: the largest object is `Ledger` with five fields and no field is written from outside its own command. The one genuine cross-boundary duplication -- `_committed` in memory versus the running total on the COMMIT lines -- is emitted from exactly one expression at `:157-159`, so R2 cannot drift between write sites (it can only drift on a failed write, which the artifact names as a limit; see N-D5). Complexity is proportional: my own AST branch count gives max cc=5, in `reserve` (`:136`), whose five branches are precisely the four specified rejections plus the accept path; every other callable is cc<=4, and the two adapters total 57 lines. `_holdings` at `:186` is an O(n) scan reused by both `_held` and the close guard rather than a maintained per-tenant index -- slower, and one fewer thing to keep true.

What blocks 3: anchor 3 wants "a simplification was made and its effect measured -- the before and after figures are both recorded", and there are no figures. `mechanical.json` was delivered to me empty; nothing in the tree records a complexity number before or after anything. The artifact argues one simplification well in prose (deriving `available` instead of storing it) but never measures it, and the caveat's demand -- say what got simpler and how the behavior survived -- can be met on the deletion but not on the measurement, because the before state does not exist as a figure anywhere. I nearly took 3 on the strength of that argument plus my own reconstruction (I could compute the before myself), and did not, because a figure the judge invents is not a figure the artifact recorded. Prose quality tempted me here and I am saying so: NOTES.md is the most persuasive writing I have scored and every clause of it that mattered I re-derived from `domain.py` before using it.

### D3 — modularity

**Score:** 4

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger/domain.py:13`
- `quota_ledger/domain.py:22`
- `quota_ledger/domain.py:132`
- `quota_ledger/domain.py:159`
- `quota_ledger/domain.py:181`
- `quota_ledger/__init__.py:39`
- `quota_ledger/file_journal.py:30`
- `quota_ledger/memory_journal.py:18`
- `tests/test_ledger.py:26`
- `tests/test_ledger.py:241`
- `tests/test_ledger.py:247`
- `tests/test_ledger.py:260`

**Refuses to claim** (required and non-null for a score of 4): That R2 survives a failed durable write. NOTES.md:136-141 names it in as many words -- "this is the one place I can name where R2 is not enforced by construction" -- and the code agrees rather than merely being described: `domain.py:156-158` mutates `_outstanding` and `_committed` and only then calls `_journal.append` at `:159`, with no rollback, no write-ahead ordering and no try/except, so an append that raised would leave memory ahead of the durable record. It also declines to claim the port covers concurrency or process boundaries, and declines to add a seventh rejection reason for non-integer amounts (NOTES.md:142-145), a refusal I confirmed by executing: `reserve("acme", 2.5)` is accepted and writes the line `COMMIT acme 2.5 2.5`.

**Rationale:**

The caveat says import topology is not modularity and D3>=3 needs evidence about what CALLS what at runtime, so I did not score this off the import list. I ran a scripted scenario (reserve/release/commit/close, both accepted and rejected) three ways. (a) With a recording proxy wrapped around the port: over the whole scenario the domain touched exactly two attributes on its Journal, `append` and `records` -- no adapter-specific API leaks across the boundary at runtime. (b) Under a `sys.addaudithook` on `open`: every one of the 12 filesystem opens in the scenario had `file_journal.py` (`:27`, `:30`, `:34`) as its innermost project frame and zero were attributable to `domain.py`. (c) The same scenario wired to the real adapter and to the fake produced byte-identical observables.

Anchor 3: `domain.py:13-16` imports only `__future__`, `dataclasses`, `typing`; the port is declared in the domain's own vocabulary at `:22-43`; the domain's only three outward calls are `:132` (`records`), `:159` and `:181` (`append`). The specific swap: change `FileJournal(ledger_path)` to `InMemoryJournal()` at `__init__.py:39` -- one line, in the only module that imports both sides -- and no domain file changes. I confirmed by executing that swap on a scratch copy: it runs, and both suites still pass (which is itself the survivor M18 in N-D1, and belongs there, not here).

Anchor 4: `tests/test_ledger.py:26-31` is a two-param fixture that wires the same `Ledger` to `FileJournal` and to `InMemoryJournal`. I counted the collection: 50 of the 53 cases are the SAME case list run twice, 25 per wiring, and each asserts a literal expected transcript (`:124-129`, `:215-220`) rather than asserting that the two wirings agree with each other -- agreement between two wirings of one domain is not evidence and this suite deliberately does not rely on it. All 53 pass, three runs, identical.

I checked the caveat's escape hatch and it does not bite here. `InMemoryJournal` is a working second implementation, not a mock, so this is not "two fakes". And the real adapter is not doing nothing real: the effect the port exists for is observed by something that is NOT the adapter that wrote it, at `tests/test_ledger.py:244` and `:247`, which read the raw file with `path.read_text()` and assert the exact bytes `"COMMIT acme 1 1\nCLOSE acme 1\n"` -- framing that `records()` strips and therefore cannot vouch for. I reproduced that independently in my own trace. I was genuinely torn to 3 and say why in the disclosures; what nearly moved me is that the SHIPPED wiring at `__init__.py:39` is exercised by no case in the artifact's own suite (which never imports `QuotaLedger` at all), so nothing observes that the default composition is the durable one. I set that aside for D3 because anchor 4 asks whether a driven port is exercised by a real adapter and a fake with the same cases -- which it demonstrably is -- and the gap is one of case coverage of the composition root, which is what N-D1 records.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `quota_ledger/domain.py:137`
- `quota_ledger/domain.py:141`
- `quota_ledger/__init__.py:39`
- `tests/test_ledger.py:21`
- `tests/test_ledger.py:95`
- `tests/test_ledger.py:100`
- `tests/test_ledger.py:124`
- `tests/test_ledger.py:161`
- `tests/test_ledger.py:247`
- `tests/test_ledger.py:251`
- `tests/test_ledger.py:67`
- `shared_suite/test_behavior.py:75`
- `shared_suite/test_behavior.py:43`

**Note:**

I seeded 20 faults into a scratch copy and ran both suites against each. The artifact's own suite killed 17/20, the shared suite 13/20.

CAUGHT, and worth naming because they are the cases a suite usually lacks: the running total on a COMMIT line being the amount rather than the accumulation (M01, both suites); the two numeric fields on the line swapped (M02, both) -- caught only because cases assert literal transcripts like `tests/test_ledger.py:124-129` rather than parsing their own output; a durable write added to `release` (M03, both) -- `tests/test_ledger.py:139` and `:235` assert `ledger_lines() == []`, so 'writes nothing' is a positive assertion and not an omission; `FileJournal.append` dropping the newline (M13) and `records()` reversing or keeping blanks (M15, M16), all killed by the raw-bytes case at `tests/test_ledger.py:247`.

CAUGHT ONLY BY THE ARTIFACT'S OWN SUITE -- four classes the shared floor misses entirely: id monotonicity past r10, where a lexicographic sort puts r10 before r2 (M07, killed by `tests/test_ledger.py:100-105`); a rejected reserve burning an id (M05b, killed by `:95-98`); `FileJournal` not truncating an existing file at construction (M14, killed by `:251-254`); and `InMemoryJournal.records()` returning its internal list so a caller can mutate the journal (M17, killed by `:67-71`). Each of those is a case the author wrote against a hazard the author named, and each is a real bug the floor would have shipped.

DEMONSTRABLY MISSED, all three surviving BOTH suites:
1. **Rejection-guard PRECEDENCE (M04).** I reordered `domain.py:137-144` to test `amount < 1` before `tenant not in self._quota`, so `reserve("nobody", 0)` returns `amount_not_positive`. FEATURE.md:40-45 specifies the order explicitly. Both suites pass. Neither has a single case in which two guards are true at once -- shared `test_behavior.py:75-83` and own `test_ledger.py:161-173` vary one condition at a time. The artifact's actual behavior is correct here (I probed it: `unknown_tenant`), which is exactly what makes this the interesting miss -- correct-and-unpinned, free to regress silently.
2. **The composition root (M18).** Replacing `FileJournal(ledger_path)` with `InMemoryJournal()` at `__init__.py:39` -- deleting durability outright from the shipped entry point -- passes both suites. The artifact's own suite never imports `QuotaLedger` (`test_ledger.py:21` imports only `FileJournal`, `InMemoryJournal`, `Ledger`), and the shared suite hands in `tmp_path / "ledger.txt"` and then never looks at that path, reading the ledger only through `ledger_lines()`. The single line where the wiring decision lives is the one line no case observes.
3. **The path is ignored (M19).** Same line, made to write `elsewhere.txt` in the same directory. Both suites pass. A user-visible defect -- the ledger is not where you asked for it -- with zero coverage.

A fourth class is missed by construction rather than by omission: non-integer amounts. `reserve("acme", 2.5)` is accepted and writes `COMMIT acme 2.5 2.5`. NOTES.md:142-145 names this as a deliberate choice, so it is a declared gap and not a hidden one, but nothing asserts the resulting behavior either way.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `tests/test_ledger.py:112`
- `tests/test_ledger.py:142`
- `tests/test_ledger.py:175`
- `tests/test_ledger.py:202`
- `tests/test_ledger.py:224`
- `shared_suite/test_behavior.py:117`
- `shared_suite/test_behavior.py:239`
- `shared_suite/test_behavior.py:258`
- `shared_suite/test_behavior.py:270`

**Note:**

THERE IS NO BASELINE, and per the question that is the answer rather than a gap. This artifact is a from-scratch implementation of FEATURE.md; there is no prior version of it in the packet I may read, no before-tree to diff against, and nothing was refactored, so 'preservation' has no referent. The nearest thing to a baseline is the shared suite, which FEATURE.md:106-111 itself calls a floor and not a result.

So I enumerated the specified behaviors instead and checked each holds, which is the question I can actually answer. From FEATURE.md I took: the five queries; the four commands with their reject-orders and six reasons; ids allocated r1,r2,... never reused; commit appending exactly one line and NOT restoring `available`; release writing nothing; close appending exactly one CLOSE line; and R1-R5. Each holds under execution: R1 is checked at `tests/test_ledger.py:224-225` and shared `test_behavior.py:239-255`; R2 at shared `:258-267` and by literal transcript at own `:117-131`; R3 at own `:142-152`; R4 at own `:175-199`, which snapshots all five observables plus the ledger across nine distinct rejections; R5 at shared `:270-281` and own `:202-220`. The commit-does-not-restore rule, the trickiest sentence in the feature, is asserted by name and value at own `:112` and shared `:117`. All 53 + 28 pass, three runs each, no flake.

Two behaviors are specified and NOT pinned by any case, which I only found by seeding faults: the ORDER of the reject guards (FEATURE.md:40-45, 76-80) and the durability of the shipped `QuotaLedger` factory. Both are correct in the artifact today and neither is protected; see N-D1. And three behaviors are unspecified and answered by fiat -- `available`/`committed` raise KeyError on an unknown tenant while `is_closed` returns False (NOTES.md:127-131, which I verified by executing all three).

### N-D5 — honesty

**Citations** (`file:line`):

- `quota_ledger/domain.py:74`
- `quota_ledger/domain.py:156`
- `quota_ledger/domain.py:159`
- `quota_ledger/__init__.py:13`
- `tests/test_ledger.py:260`
- `NOTES.md:136`
- `NOTES.md:142`
- `NOTES.md:127`
- `NOTES.md:149`

**Note:**

It refuses in prose and, in the places that count, the code backs the prose -- which is the only version of this that survives scoring rule 1. Four refusals I checked rather than accepted:

1. NOTES.md:136-141 refuses to claim R2 holds across a failed durable write: 'the one place I can name where R2 is not enforced by construction'. The code agrees: `domain.py:156-158` mutates memory, `:159` appends after, no rollback and no try/except. This is a genuine limit, correctly located, and named without being dressed up as handled.
2. NOTES.md:142-145 refuses to add a type check for non-integer amounts because the reason vocabulary is fixed at six. Executed: `reserve("acme", 2.5)` is accepted and writes `COMMIT acme 2.5 2.5`. The stated consequence is the actual consequence.
3. NOTES.md:127-131 names the three unspecified query behaviors it chose. Executed: KeyError, KeyError, False, as described.
4. `tests/test_ledger.py:260-270` is a refusal to certify by assertion: the file parses `domain.py`'s import statements and asserts the set is exactly `{__future__, dataclasses, typing}`, with the docstring "'does not import' is the claim, so read the imports". The artifact treats its own architectural claim as something to be checked, which is the behavior the rule about claims exists to reward. `domain.py:74` does the same at runtime, asserting a rejection reason is in the declared vocabulary before a Result can carry it.

Against that, three places where it certifies more than it can see, and the last is the sharpest:
- NOTES.md:1-12 says 'Four files' and 53 cases and 28 shared passes; true, and I checked all three rather than believe them, but they are self-report.
- NOTES.md:149-157 ('Files I did not open', 'git status there is clean') is unverifiable from inside the packet -- I have no route to check it and I am not permitted one. It is a claim, so I neither credited nor penalised it.
- The most load-bearing sentence in the whole document -- `__init__.py:13-14` and NOTES.md:46-51, 'replace FileJournal with InMemoryJournal and no domain file changes' -- is TRUE, and nothing in the artifact would notice if it became false. I performed that exact swap and both suites still pass, because both suites still pass with the durable side deleted (N-D1, M18). The artifact does not name that. Its honesty about what it cannot see is real but it does not extend to the one line where its central claim lives.

No false certification found. Prose quality tempted me hard on this note in particular, and the way I handled it was to execute every refusal before recording it as one.

## Verdict

A genuinely small ports-and-adapters implementation whose boundary I verified by running rather than by reading imports -- the domain touches only `append`/`records` on its port at runtime, every filesystem open in a full scenario comes from `file_journal.py`, and 50 of its 53 cases are one case list run against a real adapter and a working fake with literal expected transcripts on both -- so D3=4; D2=2 because the design is proportional to its behavior (max cc=5, in the one function that has four specified rejections) with `available` derived rather than stored, but no before/after complexity figure is recorded anywhere and anchor 3 asks for measurement, not argument. The finding worth more than either number is what seeded faults showed: I killed 17 of 20 mutants with the artifact's own suite and 13 of 20 with the shared suite, and the three that survived BOTH are the ones that matter -- reordering the rejection guards so `reserve("nobody", 0)` returns `amount_not_positive` instead of `unknown_tenant` (FEATURE.md:40-45 specifies that order and no case ever makes two guards true at once), and swapping the shipped composition root to hand the domain an `InMemoryJournal` or a file at the wrong path, which nothing observes because the artifact's own suite never constructs `QuotaLedger` and the shared suite never looks at the path it passed in. I did not learn which arm this is.

## Disclosures

**Judge model:** `claude-opus-5[1m]`. **Commit:** `5e07dce`. **Arm:** I did not work out which arm `GL` is and did not go looking.

**Seen that I should not have been.** One, and it is a scratch-hygiene leak rather than a rubric leak. The scratch directory I was assigned, `.../scratchpad/judge-v5-p1/`, was NOT empty: it already held `patch.py`, `run.sh` and a `work/` tree dated 2026-08-11 (a day before this round's packet), left by some earlier session that reused the path. My first command there was `cp -R` followed by `ls -R`, and that listing printed the pre-existing filenames before I could avoid it — so I know a directory named `work/reference_ports/` exists containing `domain.py`, `journal_file.py`, `journal_memory.py`, alongside a `work/FEATURE.md` and a `work/tests/`. **I opened none of them.** I read no byte of any file under `work/`, `patch.py` or `run.sh`. I immediately moved my own work into a fresh `p1-mine/` subdirectory and did not touch the rest again. What the exposure could have biased: seeing that some *other* ports-shaped tree exists could prime a judge toward reading this artifact as "the ports arm". Two things limit it — I had already read all four of this artifact's source files and formed the D3 reading before running that `ls`, and the filenames differ from this artifact's (`journal_file.py` vs `file_journal.py`), so it is a different tree either way. Recording it rather than deciding for myself that it was harmless.

**Read nothing on the forbidden list.** No `references/eval_scorecard.md`, no `rubric_v4_frozen.md`, no other scorecard anywhere under `specs/results/scorecards/` outside this directory, no `PREDICTIONS-SV-01.md` or anything else directly under `SV-01/`, no `subjects.toml` or other `examples/validation/` content, no `*-EPIC.md` / `NEXT-EPIC.md` / `SKILL.md` / root `README.md`, no `specs/desired_program_model/`, and no `git log`/`show`/`diff`/`blame` — I ran no git command at all. I also did not look for the other passes.

**Changed in the tree.** I ran both suites once *in place* in the artifact directory before switching to a copy, which causes CPython to write `quota_ledger/__pycache__/*.pyc` and `tests/__pycache__/`. A `quota_ledger/__pycache__` was already present and timestamped before my session, so I was not the first, but my runs refreshed it. No source file in the repository was edited; **all 20 seeded faults were applied to copies under my scratch directory only**, and I re-ran the pristine artifact afterwards to confirm 53/28 still pass.

**WHAT I REJECTED.**

*The 3 I nearly gave on D3, and did not.* The argument for 3 is real: the shipped composition root at `quota_ledger/__init__.py:39` is the single line where the port/adapter decision actually lives, and no case in the artifact's own suite ever constructs `QuotaLedger` — `tests/test_ledger.py:21` imports `FileJournal`, `InMemoryJournal`, `Ledger` and never the factory. I proved the consequence rather than argued it: swap that line to `InMemoryJournal()` and all 53 + 28 cases still pass with durability deleted. A reasonable judge stops there and says the pairing is demonstrated in the fixture but not in the product. I rejected it because anchor 4 asks a specific question — is a driven port exercised by a real adapter *and* a fake, with the same cases passing against both — and the answer is yes, measurably: 25 identical cases per wiring, literal transcripts on each, never an agreement assertion between them. And the caveat's escape hatch, "the only observer of the effect the port exists for is the adapter that wrote it", is factually false here: `tests/test_ledger.py:244,247` reads the raw file and asserts the trailing-newline framing that `records()` strips and cannot vouch for. So M18 is a coverage finding, and I put it in N-D1 where coverage findings go, instead of laundering it into a modularity score. If pass 2 lands on 3 for exactly this reason, the disagreement is about where the finding belongs, not about what the artifact does.

*The 3 I nearly gave on D2, and did not.* The `available`-is-derived decision is a real simplification, correctly reasoned, and the caveat's demand — say what got simpler and how the behavior survived — I could have met: three commands no longer write a field, R1 holds by construction, and the surviving behavior is pinned by name and value at `tests/test_ledger.py:112` and shared `test_behavior.py:117`. What anchor 3 asks for beyond that is *figures, before and after*, and there are none — `mechanical.json` arrived empty and nothing in the tree records a complexity number at any point in time. I could compute a "before" myself by reconstructing the unsimplified design, and that is precisely the move I rejected: a figure the judge invents is not a figure the artifact recorded, and MF-020's whole point is that an unanchored complexity number proves nothing about behavior.

*The 0 I did not give on D2.* Read literally and in isolation, anchor 0 ("complexity is unmeasured") is satisfied — nothing here measures complexity — and the rule says take the lowest anchor fully satisfied. I rejected that reading because the dimension's own `read_first` says in terms that where no measured descriptor exists "that is not a gap in the evidence", which makes 0/1 a rung about *ignoring* a measurement rather than about lacking one. Flagging it because the ladder is genuinely non-monotone at that seam: a judge who applies the lowest-anchor rule mechanically to D2 scores 0 on any artifact that never ran a complexity tool, which cannot be what the scale means and would make D2 measure tool-use rather than design.

*Evidence I considered and set aside.* (a) The import-set assertion at `tests/test_ledger.py:260-270` is the single most quotable piece of D3 evidence in the artifact, and I refused to let it carry the score — the caveat says coupling survives every import check, so I went and got runtime evidence instead, and the audit-hook trace is what the score actually rests on. (b) NOTES.md is the best-written document I have scored; rule 4 says prose is never an input, so I re-derived every load-bearing claim from source or by executing it, and where I could not — the "Files I did not open" section — I recorded it as an unverifiable claim and neither credited nor penalised it. (c) I set aside the artifact's 53-vs-28 case count as a quality signal; more cases is not better cases, and the mutation matrix is what separated the two suites, not the counts.

*A finding I nearly did not report.* M04 — reordering the rejection guards so `reserve("nobody", 0)` answers `amount_not_positive` instead of `unknown_tenant` — survives BOTH suites, and my first instinct was to drop it as pedantic. It is the opposite. FEATURE.md:40-45 and 76-80 specify the precedence twice, in numbered lists, as the only thing they bother to number; the artifact implements it correctly; and neither suite ever makes two guards true at once, so the one requirement the spec was most emphatic about is the one requirement nothing pins. Correct-and-unpinned is the state a regression walks into unannounced, and it is invisible to every instrument here except a seeded fault.
