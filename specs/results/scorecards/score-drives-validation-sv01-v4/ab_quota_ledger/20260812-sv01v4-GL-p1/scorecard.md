# Scorecard — ab_quota_ledger, artifact `GL`, judge pass 1

`run_id`: `20260812-sv01v4-GL-p1` · scorecard_version 4 · rubric `examples/validation/scorecards/rubric_v4_frozen.md` digest `sha256:497c16ca85adeb4a` · served `sha256:a213a36770ccab09`

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

- Baseline, unmutated, in the repository tree: `uv run --with pytest python -m pytest tests/test_ledger.py -q` → **53 passed in 0.14s**.
- Baseline shared suite: `QUOTA_LEDGER_DIR=$ARTIFACT QUOTA_LEDGER_IMPL=quota_ledger uv run --with pytest python -m pytest .../shared_suite/test_behavior.py -q` → **28 passed in 0.09s**. Both match `NOTES.md:27-28`, so that claim checks out against execution.
- Copied the artifact to scratch (`/private/tmp/.../judge-v4-p1/base`) and seeded **15 faults** there, one at a time, each into a fresh copy, running BOTH suites against every one. **Nothing was mutated in the repository.**
- **13 real faults. Own suite killed 12, shared suite killed 8.**

  | fault | own suite | shared suite |
  |---|---|---|
  | F01 running total on the COMMIT line becomes the per-line amount | KILLED (4) | KILLED (2) |
  | F02 `release` appends a durable line | KILLED (6) | KILLED (1) |
  | F03 `reserve` increments the id counter above its guards | KILLED (8) | KILLED (2) |
  | **F04 rejection precedence: `amount_not_positive` before `tenant_closed`** | **survived 53/53** | **survived 28/28** |
  | F05 quota boundary `>` → `>=` | KILLED (8) | KILLED (2) |
  | F06 `outstanding_ids` sorted lexicographically (r10 before r2) | KILLED (2) | survived |
  | F07 CLOSE line total hardcoded to 0 | KILLED (4) | KILLED (2) |
  | F08 close accepted with reservations outstanding | KILLED (2) | KILLED (2) |
  | F09 `FileJournal` stops truncating | KILLED (1) | survived |
  | F10 `FileJournal.records` drops the last record | KILLED (19) | KILLED (7) |
  | F11 `InMemoryJournal` returns its internal list | KILLED (1) | survived |
  | F12 domain imports `pathlib` | KILLED (1) | survived |
  | F13 `available` stops subtracting committed | KILLED (6) | KILLED (2) |
  | F14 *(control)* semantically vacuous guard rewrite | survived | survived |
  | F15 *(control)* reorder commit's two writes | survived | survived |

  The two controls are there so the kills above read as discrimination and not brittleness; both survived, as intended.
- **The swap, executed:** replaced `FileJournal(ledger_path)` with `InMemoryJournal()` at `quota_ledger/__init__.py:39` in a scratch copy, confirmed `domain.py` md5 unchanged (`2818df20c2f62c4ac480be73621fbb96`), ran the shared suite against the swapped wiring → **28 passed**, with no ledger file written.
- **Runtime call trace:** wired `Ledger` to a spy `Journal` and ran a 10-command scenario. The complete cross-boundary call set was `append('COMMIT acme 4 4')`, `append('COMMIT globex 2 2')`, `append('CLOSE acme 4')`, `records()`. No other collaborator method was reached.
- **Runtime I/O isolation:** monkeypatched `builtins.open`, `io.open`, `os.open`, `Path.open`, `Path.read_text`, `Path.write_text` to raise, then ran the same scenario on the domain with the fake — completed with identical results.
- **Failed-durable-write probe:** drove `Ledger` with a `Journal` whose `append` raises `OSError`; `commit` left `committed('acme')==3` with `ledger_lines()==[]`, reproducing the R2 divergence `NOTES.md:136-141` names for itself.
- **My own randomized property check of R1–R5**, independent of both suites: 400 traces × 60 random operations (unknown tenants, negative and zero amounts, bogus reservation ids, double closes), asserting conservation, durable-vs-memory agreement, close finality, snapshot equality across every rejection, and append-only prefix stability. **0 violations.**
- **Direct probes of the unspecified edges:** `reserve('acme', 2.5)` accepted, wrote `COMMIT acme 2.5 2.5`; a tenant named `big corp` wrote `COMMIT big corp 2 2`, which splits into five fields and defeats the shared suite's own R2 parser at `shared_suite/test_behavior.py:261`; `python -O` showed the six-reason vocabulary guard at `domain.py:74` is an `assert` and disappears when assertions are off.

## Your scores

### D2 — complexity

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger/domain.py:106-114` — the whole of the written state: `_quota`, `_committed`, `_closed`, `_outstanding`, `_issued`
- `quota_ledger/domain.py:118-120` — `available` derived, not stored
- `quota_ledger/domain.py:146-149` — `_issued` written only past the four guards
- `quota_ledger/domain.py:151-160` — `commit` is the only writer of `_committed`
- `quota_ledger/domain.py:172-182` — `close_tenant` is the only writer of `_closed`
- `quota_ledger/domain.py:186-191` — `_holdings`, the O(n) rescan paid instead of a second index
- `quota_ledger/file_journal.py:25-35` — the adapter's whole surface: three methods, no state
- `NOTES.md:69-84` — the simplification, argued and unmeasured

**Refuses to claim** (required and non-null for a score of 3): _n/a — not a top-of-scale score._

**Rationale:**

Anchor 2 is met on the code, and anchor 3 fails for want of figures.

Four pieces of written state exist (`domain.py:106-114`) and each has the writer the behavior implies: `_committed` only by `commit` (`domain.py:151-160`), `_closed` only by `close_tenant` (`domain.py:172-182`), `_issued` only by `reserve` and only past the four guards, so a rejection burns no id (`domain.py:146-149`), and `_outstanding` by the three commands that are definitionally about reservations. No god-state, no variable written from everywhere.

The one fact that could plausibly be stored twice — `available` — is not stored at all: `domain.py:118-120` derives it as `quota − held − committed` on every call, so R1 is arithmetic rather than an invariant three commands must remember, and the feature's trickiest sentence ("committing does not give the hold back") follows from `commit` moving an amount between two of those subtrahends rather than from a fourth write site. I verified this is a *derivation* and not a *deletion* by breaking it: replacing `domain.py:120` with `quota − held` is killed by 6 of the artifact's own cases and 2 shared ones, so the behavior the derivation replaced is still asserted by name and value.

The remaining duplication is real and is the format string: `COMMIT <tenant> <amount> <total>` is built in the domain (`domain.py:159`, `domain.py:181`) and the running total it carries is the same fact as `_committed`. That is not a second store — the total is computed at `domain.py:157` and written in the same statement, so it cannot drift — and pushing rendering into the port would put one format into two adapters, which is worse. The cost of not indexing reservations by tenant is that `_holdings` (`domain.py:186-191`) rescans every outstanding reservation, so `reserve` is O(live reservations); at this scale that is the right trade of a second index for an invariant, and the artifact does not claim otherwise.

Anchor 3 requires a simplification whose effect was **measured**, with before and after figures both recorded. `NOTES.md:69-84` argues the simplification well and records no figure of any kind; `mechanical.json` carries an empty `complexity_of_produced_code`; there is no before tree, so there is no before number. Per the caveat, a D2 of 3 needs the judge to say what got simpler *and* how the behavior survived — I can say the second half, having tested it, but the artifact records no measurement at all, and "the judge measured it afterwards" is not "the before and after figures are both recorded".

Rule 4 note: prose quality did tempt me here. `NOTES.md` is unusually well argued and reads like measurement without being it. Scored on the code alone the answer is the same.

### D3 — modularity

**Score:** **4**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger/domain.py:13-16` — the domain's complete import set
- `quota_ledger/domain.py:22-43` — the `Journal` port, with its contract on the Protocol
- `quota_ledger/domain.py:114` — the domain is handed a Journal; it never builds one
- `quota_ledger/domain.py:131-132`, `:159`, `:181` — every cross-boundary call site
- `quota_ledger/__init__.py:22-24`, `:37-39` — the composition point and the one swappable line
- `quota_ledger/file_journal.py:13-35` — the real driven adapter
- `quota_ledger/memory_journal.py:14-22` — the fake
- `tests/test_ledger.py:26-36` — the `params=["file","memory"]` fixture that wires both
- `tests/test_ledger.py:42-71` — the port contract asserted against both implementations
- `tests/test_ledger.py:108-129` — literal expected transcripts, not agreement between wirings
- `tests/test_ledger.py:260-270` — the import discipline converted into a check that can fail

**Refuses to claim** (required and non-null for a score of 4):

It refuses to claim the durable side is **atomic or crash-safe**, and names the exact hole: `NOTES.md:136-141` says `commit` and `close_tenant` update memory and then append, so a raising `append` would leave memory ahead of the journal, and calls this "the one place I can name where R2 is not enforced by construction". I verified the refusal is truthful rather than modest: driving `Ledger` with a `Journal` whose `append` raises `OSError` leaves `committed('acme') == 3` with `ledger_lines() == []`, so R2 is false in exactly the way the artifact said it would be — and neither suite covers this. It also refuses to widen the rejection vocabulary to cover non-integer amounts (`NOTES.md:142-145`; I reproduced `reserve('acme', 2.5)` → `COMMIT acme 2.5 2.5`) on the stated ground that the vocabulary is fixed at six reasons, and refuses to invent reopen-and-resume semantics (`NOTES.md:132-135`, `file_journal.py:25-27` truncates instead).

**Rationale:**

Anchor 4 is met, and I checked it **by execution rather than by reading imports**, because the caveat says import topology is not modularity.

**The port.** `Journal` is a two-method Protocol declared in the domain in the domain's vocabulary, with its contract written on it (`domain.py:22-43`); the domain never constructs one, it is handed one at `domain.py:114`.

**Anchor 3, domain does not import its I/O.** `domain.py:13-16` imports `__future__`, `dataclasses`, `typing` and nothing else, and grep confirms the strings `FileJournal` / `InMemoryJournal` / `file_journal` / `memory_journal` appear nowhere in `domain.py` — only in `quota_ledger/__init__.py` and the tests.

**Anchor 3, the specific swap, executed.** In a scratch copy I replaced `FileJournal(ledger_path)` with `InMemoryJournal()` at `quota_ledger/__init__.py:39` and changed nothing else; `domain.py` stayed byte-identical (md5 `2818df20c2f62c4ac480be73621fbb96` before and after) and **all 28 shared-suite cases passed** against the swapped wiring, with no ledger file written at all. That is one line in the one module that imports both sides (`__init__.py:22-24`).

**Runtime evidence, not imports.** (a) I wired `Ledger` to a spy `Journal` and ran a ten-command scenario; the complete set of cross-boundary calls the domain made was `append` ×3 and `records` ×1 — no other method of the collaborator was ever reached. (b) I then poisoned `builtins.open`, `io.open`, `os.open`, `Path.open`, `Path.read_text` and `Path.write_text` to raise on call and drove the same scenario with the fake: the domain completed it and produced identical results. At runtime the domain reaches the filesystem through the port or not at all.

**Anchor 4, real adapter and fake, same cases.** `tests/test_ledger.py:26-31` is a `params=["file","memory"]` fixture and `:34-36` builds the domain on whichever it yields, so one case list runs twice — once on `FileJournal` (`file_journal.py:13-35`, genuinely on disk) and once on `InMemoryJournal` (`memory_journal.py:14-22`). It is the same cases and not two lists: 53 of 53 pass, and each asserts a literal expected transcript (`tests/test_ledger.py:114`, `:124-129`) rather than that the two wirings agree with each other — which matters, because two wirings of one domain agree even when the domain is wrong. The port's own contract is asserted against both implementations (`tests/test_ledger.py:42-71`), and that is not decorative: making `InMemoryJournal.records` return its internal list kills `tests/test_ledger.py:67` while the shared suite stays green, so the fake is held to the port and not merely present.

**What I rejected.** I considered **3**, on the reading that `InMemoryJournal` is thin (a list) and is exported from the package's public `__init__` (`__init__.py:33`), so it ships as production surface rather than as a test double, and that a fake this cheap makes anchor 4 nearly free. I set that aside: anchor 4 asks whether a real adapter and a fake run the same cases, not whether the fake was expensive, and rewriting the bar upward mid-scoring would substitute my rubric for the one I was served. The tension is recorded rather than priced in.

I also note the boundary is not free of leakage in principle: the record **format** lives in the domain (`domain.py:159`, `:181`) and the port carries a finished string, so a `Journal` implementation needing structured records could not get them without a domain change. The artifact argues this trade deliberately and I agree with it; it is a limit on what the port abstracts, not a violation of it.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `quota_ledger/domain.py:137-144` — the four ordered guards, correct in the artifact, unpinned by any case
- `quota_ledger/domain.py:129` — `list(self._outstanding)`, the insertion-order reliance
- `quota_ledger/domain.py:74` — the six-reason vocabulary guard, an `assert`
- `quota_ledger/domain.py:156-159` — memory written before the durable append
- `quota_ledger/file_journal.py:27` — construction truncates
- `quota_ledger/memory_journal.py:22` — the fake returns a copy
- `tests/test_ledger.py:67-71`, `:100-105`, `:155-158`, `:161-199`, `:251-254`, `:260-270`

**Note:**

I seeded 13 real faults plus 2 controls, each into a fresh scratch copy, and ran both suites against every one.

**Caught.** The artifact's own suite killed **12 of 13**, and it kills four classes the shared floor does not:

1. **Ordering that only breaks past r10** — replacing `list(self._outstanding)` at `domain.py:129` with `sorted(...)` is caught by `tests/test_ledger.py:100-105`, which deliberately runs to `r10` where a lexicographic sort puts `r10` before `r2`. The shared suite never allocates ten ids and stays green.
2. **Adapter construction semantics** — making `file_journal.py:27` stop truncating is caught by `tests/test_ledger.py:251-254` and missed entirely by the shared suite, which always gets a fresh `tmp_path`.
3. **The port contract on the FAKE** — making `InMemoryJournal` return its internal list (`memory_journal.py:22`) is caught by `tests/test_ledger.py:67-71` and is invisible to the shared suite, which never touches the fake.
4. **The boundary as a fact rather than an intention** — adding `from pathlib import Path` to the domain is caught by `tests/test_ledger.py:260-270`, which parses `domain.py`'s import statements and asserts the set equals `{__future__, dataclasses, typing}`.

The shared floor killed **8 of 13**. Both suites killed every arithmetic and durable-write fault I tried: the running total (`domain.py:159`), the CLOSE total (`:181`), the id counter moving above its guards (`:146`), the quota boundary (`:143`), dropping the committed term from `available` (`:120`), a `release` that writes durably, a `close` that ignores outstanding reservations (`:177`), and a `records()` that loses the last line.

**Demonstrably missed, and this is the finding: REJECTION PRECEDENCE.** `FEATURE.md:40-45` fixes the order of `reserve`'s four guards explicitly, and `domain.py:137-144` implements it correctly — but swapping the `tenant_closed` and `amount_not_positive` tests leaves **53/53 and 28/28 passing**. Neither suite ever constructs an input where two rejection conditions hold at once. The nearest miss is `tests/test_ledger.py:155-158`, which reserves on a closed tenant but with a *valid* amount, so only one guard is live. I confirmed the real artifact gets it right (closed tenant + amount 0 → `tenant_closed`): the miss is in the cases, not the code.

**Second missed class: input domains the vocabulary does not cover.** `reserve('acme', 2.5)` is accepted and writes `COMMIT acme 2.5 2.5`; a tenant named with an embedded space writes `COMMIT big corp 2 2`, which has five fields and misparses under the shared suite's own R2 parser at `shared_suite/test_behavior.py:261`. The artifact names the first itself (`NOTES.md:142-145`) and not the second.

**Third: the failed-durable-write divergence** at `domain.py:156-159`, uncovered by both suites and named by the artifact (`NOTES.md:136-141`).

Two controls — a vacuous guard rewrite, and reordering `commit`'s two writes — survived both suites as intended, so the kills above are discrimination and not brittleness. Separately, the six-reason vocabulary guard at `domain.py:74` is an `assert` and evaporates under `python -O`, which I verified; no case would notice.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `FEATURE.md:24-30` — the five observable queries
- `FEATURE.md:38-88` — the four commands and their ordered rejection reasons
- `FEATURE.md:89-104` — R1–R5
- `quota_ledger/domain.py:118-132`, `:136-182` — where each is implemented
- `quota_ledger/domain.py:156-159` — the one behavior not preserved under all conditions
- `NOTES.md:136-141` — the artifact naming that same condition first

**Note:**

**There is no baseline in what I was served, and that is the answer rather than a gap.** The blind packet contains exactly three things — `FEATURE.md`, `artifact_under_score/`, `shared_suite/test_behavior.py` — and no prior or reference tree. D2's `read_first` says to "diff the two trees yourself", but only one tree exists here; the shared suite's own default at `shared_suite/test_behavior.py:32` points at a sibling `reference/` directory that is **not present in the packet**, and I did not go outside the packet to find it. So there is no before-state whose behaviors could be enumerated and shown still to hold, and no "preserved" or "lost" can be asserted about this artifact against a predecessor.

What I could do instead, and did, is treat `FEATURE.md` as the specification of record and enumerate **its** behaviors, then check each independently of the artifact's own cases. The five queries (`FEATURE.md:24-30`) and four commands with their ordered rejection reasons (`:38-88`) are implemented at `domain.py:118-132` and `:136-182`, and I exercised each by hand. For R1–R5 (`FEATURE.md:89-104`) I wrote my own randomized property check — 400 traces of 60 random operations each, mixing unknown tenants, zero and negative amounts, bogus reservation ids and repeated closes — asserting conservation per tenant, the durable ledger's per-tenant sums and running totals against `committed`, close finality and singularity, full-snapshot equality across every rejection, and prefix-stability of the ledger after every operation. **Zero violations of any of the five.**

The one behavior in `FEATURE.md` that I found **not** preserved under all conditions is R2 under a failing durable write: `domain.py:156-159` mutates memory and then appends, so a `Journal` whose `append` raises leaves `committed` at 3 with an empty ledger, which I reproduced. `FEATURE.md` specifies no failure semantics, so this is outside the specified envelope rather than a defect against it — and the artifact says exactly that at `NOTES.md:136-141` rather than leaving me to find it.

### N-D5 — honesty

**Citations** (`file:line`):

- `NOTES.md:125-145` — the four named interpretations
- `NOTES.md:136-141` — the refusal that matters
- `NOTES.md:149-157` — the one unfalsifiable claim
- `quota_ledger/domain.py:118-126` — matches the stated KeyError / False behavior
- `quota_ledger/domain.py:156-159` — the hole, as named
- `quota_ledger/file_journal.py:25-27` — truncation, as named
- `tests/test_ledger.py:5-9`, `:260-270` — claims converted into checks that can fail

**Note:**

It refuses, and **every refusal I tested was truthful rather than modest** — which matters more than the fact of refusing, because rule 1 makes a disclaimer a claim like any other.

**The refusals, verified.**

1. `NOTES.md:136-141` declines to claim durability under failure and names the exact hole — memory is updated before the append at `domain.py:156-159`, so a raising `append` leaves memory ahead of the journal, "the one place I can name where R2 is not enforced by construction". I drove the domain with a `Journal` whose `append` raises: `committed('acme')==3`, `ledger_lines()==[]`, R2 false. The disclosure is exact.
2. `NOTES.md:142-145` declines to reject non-integer amounts and says why (the vocabulary is fixed at six reasons and a type check would be a seventh). I reproduced `reserve('acme', 2.5)` → accepted, writing `COMMIT acme 2.5 2.5`. It named a real hole it chose not to plug, not a hypothetical one.
3. `NOTES.md:127-131` declines to invent a query-side unknown-tenant result and states the actual consequence — `available`/`committed` raise `KeyError` while `is_closed` returns `False` — which matches `domain.py:118-126`.
4. `NOTES.md:132-135` declines to invent reopen-and-resume semantics; `file_journal.py:25-27` truncates, and it says so.

**It also refuses to certify its own boundary by assertion.** `tests/test_ledger.py:260-270` parses `domain.py`'s imports rather than trusting the docstring, on the stated ground that "does not import" is a claim about the file rather than about intent — an artifact converting one of its own claims into a check that can fail. In the same spirit `tests/test_ledger.py:5-9` refuses the cheap version of dual-wiring, stating it will not assert the two wirings merely agree, because two wirings of one domain agree even when the domain is wrong; I confirmed the cases assert literal transcripts (`:114`, `:124-129`).

**What it does not see, and does not claim to.** It asserts "53 passed" and "28 passed" at `NOTES.md:27-28`, which is true and which I reproduced, but nowhere does it claim its suite is adequate — and the precedence gap I found is a hole it neither covers nor names. `NOTES.md:96-100` claims "no case had to be written for only one of them", contradicted in a small way by its own file (two file-specific cases sit outside the parametrized list), but it states that exception in the very next sentence, so it is disclosed rather than hidden.

The one place its prose reaches past its evidence is `NOTES.md:149-157`, "Files I did not open … `git status` there is clean" — an unfalsifiable claim about process rather than about the artifact. I did not and could not check it, and per rule 1 I gave it no weight in any score.

## Verdict

A four-file quota ledger whose hexagonal boundary is real **under execution**, not just under import inspection: the domain imports only `__future__`/`dataclasses`/`typing`, the whole swap is one line at `quota_ledger/__init__.py:39`, and when I performed that swap the domain file stayed byte-identical while all 28 shared cases passed, and when I poisoned every filesystem entry point in Python the domain ran a full scenario unharmed, reaching its collaborator only through `append` and `records` — so **D3 sits at 4**, with a real adapter and a working fake driven by one 53-case list that asserts literal transcripts rather than agreement between the two wirings. **D2 sits at 2 and not 3** for a single reason: the artifact makes a genuine simplification (`available` derived at `domain.py:118-120` rather than stored, which is why R1 cannot drift) and argues it well at `NOTES.md:69-84`, but records no figure before or after and `mechanical.json` is empty — anchor 3 asks for measurement, not for argument. I confirmed by deletion that the derived behavior is still independently asserted, which is the half of the caveat I can answer, but a judge measuring it afterwards is not the artifact recording it. Of thirteen faults I seeded, the artifact's own suite killed twelve and the shared floor killed eight; **the single fault that survived BOTH is rejection precedence** — swapping the `tenant_closed` and `amount_not_positive` guards at `domain.py:139-142` leaves 53/53 and 28/28 green, because no case anywhere constructs an input where two rejection conditions hold at once, even though `FEATURE.md:40-45` fixes the order explicitly.

## Disclosures

**Provenance leak — disclosed, not sought.** I did not learn the arm mapping and did not go looking for it. But the artifact's own `NOTES.md:102-123` carries a section headed *"Where the feature file and the architecture ask conflicted"* and quotes a structural instruction — *"Section 1: the domain holds 'no file handle, no path'"* — from a prompt that `FEATURE.md` explicitly does not contain (`FEATURE.md:5-10` says all structural guidance "lives in the arm prompts, never here"). The artifact therefore **self-identifies as having been produced under a structure/architecture treatment**. The blind is defeated by the artifact I was directed to read, not by anything I went hunting for. This is a leak channel in the packet design: any A/B where one arm's prompt is discussed in the deliverable's own notes is unblinded at the point the judge is told to read those notes. I could not un-see it; I have tried to keep it out of the scores by grounding every citation in code and in things I ran, and the D3 evidence in particular is execution output rather than prose.

**Nothing I read was off-limits.** I read only `CARD_DIR` (the three files), everything under `.../SV-01/blind/`, and my own scratch. I did not open `references/eval_scorecard.md`, `rubric_v4_frozen.md`, `subjects.toml`, `PREDICTIONS-SV-01.md`, any other scorecard, any `*-EPIC.md`, `specs/desired_program_model/`, or any git history command.

**Nothing in the tree was changed.** Every mutation ran in `/private/tmp/.../judge-v4-p1/{base,work,swap}`. The only file I touched under the repository is this card and its JSON. I did leave `mechanical.json` alone per rule 7, though my kill counts would fit there and the operator may want them.

**What I rejected.**

- **D3 = 3 instead of 4.** Genuinely considered. `InMemoryJournal` is nine lines of list-wrapping and is exported from the package's public `__init__` (`__init__.py:33`), so it ships as production surface rather than as a test double; a fake that cheap arguably makes anchor 4 nearly free, and rule "take the lower when torn" was pulling. I rejected it because I was not torn on the anchor's *text* — the text asks whether a real adapter and a fake run the same cases, and they demonstrably do — only on whether the bar is demanding enough. Scoring lower because I would have written a stricter rubric substitutes my rubric for the one I was served. **If the round wants anchor 4 to cost more, the fix belongs in the anchor, not in the judge.**
- **D2 = 3.** Nearly given. `NOTES.md:69-84` makes exactly the argument anchor 3 wants — a fact that was going to be stored is derived instead, and the write sites that would have maintained it never exist — and I *did* verify the behavior survived, by deleting the committed term and watching 6 own cases and 2 shared cases die. The half I could not supply is the artifact's: no before figure, no after figure, no descriptor, empty `mechanical.json`. Anchor 3 says "the before and after figures are **both recorded**", and measurement I performed after the fact is not measurement the artifact recorded. Rejected.
- **D2 = 0 on a literal reading.** Anchor 0 reads "complexity is unmeasured" and complexity here *is* unmeasured — no figures exist anywhere. I rejected that reading because D2's own `read_first` forecloses it: "where none exists that is not a gap in the evidence." Worth flagging that anchor 0's text and the `read_first` say opposite things about the same fact, and only the `read_first` resolves it. **A judge who read the ladder without the preamble would score this 0, and the gap between 0 and 2 on identical bytes is a rubric defect, not a judging one.**
- **Treating `NOTES.md` as evidence.** It is the best-written artifact prose I have scored and it consistently makes true claims, which is precisely why it is dangerous: it *reads* like measurement. Rule 4 says to say so, and rule 1 says to check. I checked the four claims that could move a score (53/28 passing; the one-line swap; the domain's import set; the failed-write divergence) by running them, and all four held. I gave the fifth, `NOTES.md:149-157`'s "files I did not open", no weight at all — it is unfalsifiable from inside the packet.
- **Counting the format string as a boundary violation.** `COMMIT <tenant> <amount> <total>` is rendered in the domain (`domain.py:159`, `:181`) and the port carries a finished string, so the domain owns a serialization format. I considered marking this as I/O concern leaking inward. Rejected: the shared suite asserts those exact strings, so the format *is* behavior, and moving it outward would duplicate it into both adapters. Recorded as a stated limit on what the port abstracts.
- **A cheap extra finding I chose not to inflate.** `domain.py:74`'s vocabulary guard is an `assert` and disappears under `python -O` (verified). It is real, it is worth one line, and it moves no anchor on either dimension — so it sits in N-D1 rather than being dressed up as a complexity or modularity defect.
