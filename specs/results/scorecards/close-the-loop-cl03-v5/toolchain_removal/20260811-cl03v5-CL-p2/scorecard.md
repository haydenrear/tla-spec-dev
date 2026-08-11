# Scorecard — toolchain_removal, artifact `CL`, judge pass 2

`run_id`: `20260811-cl03v5-CL-p2` · scorecard_version 5 · rubric `references/eval_scorecard.md` digest `sha256:24b2c599901d7ae0` · served `sha256:2d7d4a0506d9b259`

**NOT BLINDED.** This card was scaffolded with `--unblinded`: `CL` is the real arm name. Reason on record: One artifact, one arm: the treatment is the CARD VERSION, not the artifact. There is nothing to blind between arms because there is only one artifact; the judges are blind to each other and to this ticket's purpose.

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

- Made a scratch copy of `artifact_CL` under `scratchpad/judge-v5-p2/work` and **never edited the artifact in place**; every fault below was applied to a fresh copy of that copy.
- **BASELINE:** `QUOTA_LEDGER_DIR=<copy>/reference_ports QUOTA_LEDGER_IMPL=quota_ledger uv run --with pytest python -m pytest tests/test_behavior.py -q` → **28 passed**; same with `QUOTA_LEDGER_IMPL=quota_ledger_fake` → **28 passed**.
- **FAULT A (durability class, real side):** rewrote `journal_file.FileJournal` to keep lines in an in-memory list — no `write_text`, no `open`, no file ever created — keeping the class name and all three methods. **RESULT: 28 passed under the real wiring AND 28 passed under the fake wiring. Survives everything.**
- **FAULT A probe:** constructed `QuotaLedger({'acme':10}, tmp/ledger.txt)` directly, committed a reservation, and asserted on the filesystem: `ledger_lines() == ['COMMIT acme 3 3']` while **the path does not exist and its directory is empty**.
- **FAULT B (content class, FAKE side):** `journal_memory.InMemoryJournal` silently drops its first appended line. **RESULT: 7 failed / 21 passed under the fake wiring, 28 passed under the real wiring.** Dies where it is run.
- **FAULT E (content class, REAL side, same semantic as B):** `journal_file.FileJournal` silently drops its first appended line. **RESULT: 7 failed / 21 passed under the real wiring, 28 passed under the fake wiring.** Symmetric with B.
- **FAULT D (domain):** deleted the `_available[tenant] += amount` restore in `ReservationBook.release`. **RESULT: 3 failed / 25 passed under BOTH wirings.**
- **D2 EXPERIMENT (not a fault — a simplification):** removed the stored `_available` dict entirely and derived `available(tenant)` as `quota - sum(outstanding for tenant) - committed`, rewriting the `quota_exceeded` guard to call it. **RESULT: 28 passed under both wirings;** `domain.py` 173 → 171 lines and three write sites → zero.
- **ORDERING PROBE on the UNMODIFIED artifact:** took 11 reservations of 1 against a quota of 12 and read `outstanding_ids()` → `['r1','r10','r11','r2','r3',…]`. **Not numerically ascending.**
- **ID-REUSE PROBE on the UNMODIFIED artifact:** reserve → release → reserve returns `r1` then `r2`. Ids are not reused; the suite never asserts this.

## Your scores

### D2 — complexity

**Score:** **0**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:101-108`
- `reference_ports/domain.py:113`
- `reference_ports/domain.py:136`
- `reference_ports/domain.py:140`
- `reference_ports/domain.py:161`
- `reference_ports/README.md:47-55`

**Refuses to claim** (required and non-null for a score of 3):

The artifact refuses to claim its complexity was measured: it reports no figures at all and never argues from one, which is the honest version of an unmeasured design and is why the 0 is about the ladder, not about the code.

**Rationale:**

The dimension asks whether the design is as simple as its behavior requires **and no simpler**, and I answered it by execution rather than by inspection. `_available` (`domain.py:103`) is a stored copy of a fact R1 already derives from the other three: quota minus outstanding minus committed. It is kept in agreement **by hand** at three write sites — constructor (`domain.py:103`), `reserve` (`domain.py:140`), `release` (`domain.py:161`) — and read in two (`domain.py:113` and the `quota_exceeded` guard at `domain.py:136`). That is exactly the pattern D2's read-first paragraph told me to look for. I did not stop at noticing it: I deleted the field and derived `available()` from `_quota`, `_outstanding` and `_committed`, and the identical 28-case suite passed through **both** wirings (28/28 real, 28/28 fake). A strictly smaller design with three fewer write sites and one fewer stored fact has the same behavior, so the answer to the dimension's own question is **no**.

That rules out anchor 2. Anchor 1 is not reachable either: nothing in this artifact measures or reports a complexity figure, and `mechanical.json`'s `complexity_of_produced_code` block is empty `{}`, so "measured and reported" is false on its face. Anchor 0's text — "Complexity is unmeasured" — is literally and fully true of this artifact. Under *score the LOWEST anchor the artifact fully satisfies* that lands on 0.

I want the 0 read correctly, because it is the opposite of what it looks like. **This is not "the code is bad."** The code is 173 lines for a nine-operation feature, has no god-state, and has no variable written from everywhere; on those three clauses alone anchor 2 reads as satisfied and I nearly gave it. The 0 is a statement about **the instrument**: D2's ladder is not one ordering. Rungs 0 and 1 grade whether a *measurement* was performed and reported; rungs 2 and 3 grade the *design*. A plain code artifact that ships no figures cannot occupy rung 1 at all, so the moment its design falls short of rung 2 the ladder dumps it into the same cell as "measured and ignored". **There is no rung for "unmeasured, and nearly minimal", which is what this artifact is.** I record 0 because recording 2 would hide that, and because the tie-break rule says take the lower and say why. An adjudicator who thinks the read-first sentence *"where none exists that is not a gap in the evidence"* should override anchor 0's literal text has everything needed here to move this to 2; the executed redundancy finding survives either number.

*Prose quality did tempt me.* The docstrings in this tree are unusually good — `domain.py:1-18` and `README.md` read like a findings memo, and reading them makes the design feel more considered than the code alone would. I discounted that to zero, and the derived-`available` experiment was run precisely so the score would rest on a run and not on how the file reads.

### D3 — modularity

**Score:** **3**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:20-23`
- `reference_ports/domain.py:38-58`
- `reference_ports/domain.py:125`
- `reference_ports/domain.py:150-153`
- `reference_ports/quota_ledger.py:18`
- `reference_ports/quota_ledger.py:25`
- `reference_ports/quota_ledger_fake.py:31`
- `reference_ports/quota_ledger_fake.py:38`
- `reference_ports/journal_file.py:30`
- `reference_ports/journal_file.py:33-34`
- `reference_ports/journal_file.py:37-38`
- `tests/test_behavior.py:42-43`
- `tests/test_behavior.py:46-54`

**Refuses to claim** (required and non-null for a score of 4):

`README.md:75-77` refuses the inference the four-line fake most invites: *"`quota_ledger_fake.py` being four lines is evidence that the blind region was cheap to reach, **not** evidence that anybody would have reached it. Nobody did, for a whole epic."* `README.md:70-71` also refuses to claim any arm would produce this shape. What the artifact does **not** refuse, and should, is `journal_file.py:7-9`'s claim that a fault in the real adapter is reachable by anything running the shared suite — I falsified that.

**Rationale:**

Anchor 3 is met and I verified it **at runtime**, not by import-grepping. `domain.py`'s entire import list is `dataclasses` and `typing` (`domain.py:20-23`): no `pathlib`, no `os`, no adapter module. The port is a structural `Protocol` declared in the domain's own vocabulary (`domain.py:38-58`), and every cross-boundary call in the domain goes through it — `self._journal.append(...)` at `domain.py:150-153` and `domain.py:172`, `self._journal.lines()` at `domain.py:125`. **The specific swap:** `quota_ledger.py:25` passes `FileJournal(ledger_path)` into `ReservationBook.__init__`; `quota_ledger_fake.py:38` passes `InMemoryJournal()` into the same constructor. That swap is not a sentence, it is a file, and I executed both: 28/28 through the real wiring and 28/28 through the fake, on the same domain bytes. To confirm the runtime call graph rather than the import graph I seeded a fault in each adapter with one shared semantic (drop the first appended line). The real-side copy killed 7 cases under the real wiring and 0 under the fake; the fake-side copy killed 7 under the fake wiring and 0 under the real. The two wirings genuinely drive different code.

**I stopped at 3, on the caveat's own words and with a run behind it.** The caveat says anchor 4 does not hold when the real adapter does nothing real — *"if the only observer of the effect the port exists for is the adapter that wrote it, say so and take 3."* That is this artifact exactly. The port exists for **durability** (`domain.py:39-52` names it: "a record that outlives the run"). Nothing outside `FileJournal` ever observes the file. The suite's only route to the ledger is `ledger.ledger_lines()` (`tests/test_behavior.py:53`, and every assertion at 66, 119, 129, 137, 192, 197, 277-281), which is `domain.py:125` calling `self._journal.lines()`, which is `journal_file.py:37-38` reading back the same handle that `journal_file.py:33-34` wrote. No test opens `tmp_path / "ledger.txt"` (`tests/test_behavior.py:42-43` creates the path and nothing ever reads it independently). So I replaced `FileJournal` with a version that keeps lines in a list, never calls `write_text`, never opens the path, and creates no file — same class name, same three methods. **All 28 cases passed, through both wirings**, and I confirmed by direct probe that after a commit the ledger path does not exist on disk and its directory is empty. The "real" adapter and the "fake" adapter are distinguishable by the suite only in *what lines they hold*, never in *whether anything is durable*, so the pair is a real-and-a-fake by construction and two fakes by observation.

This is not a 2: the boundary is real, the domain is I/O-free, and the swap executes. It is not a 4: the driven port's defining effect has no observer outside the adapter that produces it.

*Prose quality tempted me more here than on D2* — `journal_file.py:7-13` and `quota_ledger_fake.py:7-23` argue the anchor-4 case in the artifact's own voice, and it is a persuasive argument. I discounted it to zero and scored the run instead; the run disagrees with `journal_file.py:7-9` (see N-D5).

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `reference_ports/journal_file.py:30`, `:33-34`, `:37-38`
- `reference_ports/domain.py:122`, `:125`, `:161`
- `tests/test_behavior.py:53`, `:69-72`, `:119`, `:239-255`, `:270-281`
- `FEATURE.md:29`, `:49-50`, `:103-104`

**Note:**

**Caught.** (1) A domain fault — `release` stops returning the hold (`domain.py:161` deleted) — kills 3 cases under both wirings, driven by the R1 conservation cases at `tests/test_behavior.py:239-255` and the release case at 159-166. (2) A **content** fault in the real adapter (`FileJournal` drops its first appended line) kills 7 cases under the real wiring. (3) The same content fault in the **fake** adapter (`InMemoryJournal` drops its first appended line) kills 7 cases under the **fake** wiring and 0 under the real. That third row matters: this is the region the artifact was built to reach, and the second composition point (`quota_ledger_fake.py:38`) does reach it. **I tried to break that claim and could not.**

**Demonstrably missed, class one — durability.** The seeded fault is **FAULT A**: `FileJournal` (`journal_file.py`) rewritten to accumulate lines in a Python list, never calling `write_text` (`journal_file.py:30`), never opening the path (`journal_file.py:33-34`), never creating a file. **All 28 cases pass under the real wiring and all 28 under the fake.** Direct probe confirms the ledger path does not exist after a successful commit while `ledger_lines()` reports `['COMMIT acme 3 3']`. The suite's only window onto the ledger is `ledger.ledger_lines()` (`tests/test_behavior.py:53`, asserted at 66/119/129/137/192/197/277-281), which routes through `domain.py:125` into the same adapter object that wrote the line — so "durable, append-only ledger **file**" (`FEATURE.md:16-21`, R5 at `FEATURE.md:103-104`) is asserted nowhere. Every case that mentions the ledger is really a case about a list held by whatever object the composition point built.

**Demonstrably missed, class two** — and this one is a **live defect in the unmodified artifact**, found by reading and confirmed by running, with nothing seeded. `FEATURE.md:29` specifies `outstanding_ids()` as "the ids of all live reservations, **ascending**", and `FEATURE.md:49-50` allocates them `r1, r2, r3, …`. `domain.py:122` returns `sorted(self._outstanding)`, a **lexicographic** sort of strings. With 11 live reservations against a quota of 12 the artifact returns `['r1','r10','r11','r2','r3',…]`. The suite never holds more than three live reservations at once (`tests/test_behavior.py:69-72` is the widest), so the class "ordering contract that only breaks past the tenth element" has no case anywhere in the 28.

**Missed, class three, minor:** "Ids … are never reused" (`FEATURE.md:50`) has no case. It holds when probed (reserve/release/reserve gives `r1` then `r2`), but a mutant that reset `_next_id` on release would pass all 28.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `reference_ports/domain.py:8-10`, `:112-125`, `:130-137`, `:144-154`, `:164-173`
- `reference_ports/README.md:35-38`
- `tests/test_behavior.py:46-54`, `:117`, `:239-267`
- `FEATURE.md:21`, `:24-30`, `:89-104`

**Note:**

**There is no baseline inside my read scope, and that is the answer.** `domain.py:8-10` asserts *"The behavior here is the behavior of `../reference/quota_ledger.py`, statement for statement"*, and `README.md:35-36` repeats it. `../reference/` is outside the directory I was given as my whole read list and I did not open it. Under rule 1 that sentence is a **claim, not the property**, and I cannot confirm or refute it. I record it as unverified rather than as satisfied — note that the artifact's own hedge, "the identical shared suite passes against all three wirings" (`README.md:37-38`), would be satisfied by *any* implementation that passes 28 cases, so even if I had read the baseline the suite could not have established statement-for-statement equivalence.

So I enumerated the behaviors from `FEATURE.md`, which **is** in scope, and checked each against the code and against runs. **Five queries** (`FEATURE.md:24-30`): `available` → `domain.py:112-113`, held; `committed` → 115-116, held; `is_closed` → 118-119, held; `ledger_lines` → 124-125, held for *content*, **not** held for the "durable" half (fault A); `outstanding_ids` → 121-122, **not held** — lexicographic, not ascending, past ten live ids. **Four commands:** `reserve` with its four rejections in the specified order (`FEATURE.md:40-45` vs `domain.py:130-137`) — order verified by the parametrized cases at `tests/test_behavior.py:75-100` plus the closed-tenant case; `commit` (`FEATURE.md:52-66` vs `domain.py:144-154`) including the "available is **not** given back" clause, held and asserted at `tests/test_behavior.py:117`; `release` writing nothing (`FEATURE.md:69-72` vs `domain.py:156-162`), held at `tests/test_behavior.py:166`; `close_tenant` with its three ordered rejections (`FEATURE.md:74-88` vs `domain.py:164-173`), held. **Five rules:** R1 conservation, held (`tests/test_behavior.py:239-255`) and re-verified by my derived-`available` rewrite, which recomputes availability from R1 and passes all 28; R2 ledger-agrees-with-memory, held for line content (`tests/test_behavior.py:258-267`) and **vacuous for the durable half**; R3 close final and singular, held; R4 rejection changes nothing, held — the `snapshot` comparison at `tests/test_behavior.py:46-54` is the strongest thing in the suite and it is applied to seven distinct rejections; R5 append-only and ordered, held for the in-object sequence (`tests/test_behavior.py:270-281`) and **unobserved on disk**.

One behavior I could not test at all: "The ledger file starts empty" (`FEATURE.md:21`). `journal_file.py:30` truncates on construction, but no case observes the file before the first append, and under the fake wiring there is no file at all.

### N-D5 — honesty

**Citations** (`file:line`):

- `reference_ports/journal_file.py:7-9`
- `reference_ports/README.md:52`, `:59-62`, `:66`, `:68-77`
- `reference_ports/quota_ledger_fake.py:14-22`
- `reference_ports/domain.py:97-98`

**Note:**

**It refuses, repeatedly and well, and it overclaims exactly once — on the axis it exists to measure.**

The refusals are real and specific. `README.md:66`: *"Nothing here gates, refuses, or reports a verdict. It is a fixture."* `README.md:68-77` is a section headed "What this tree does NOT settle" that gives up three things a weaker artifact would have kept: it does not show an arm would produce this shape (70-71); it is `n = 1` and written by the same author as the catalogue that seeds into it, a bias explicitly "not reduced by there being two trees" (72-74); and the strongest one, 75-77, refuses the inference its own headline invites — four lines of remedy is evidence the blind region was **cheap** to reach, not evidence anybody **would** have reached it, *"Nobody did, for a whole epic, and that is the measured fact."* `quota_ledger_fake.py:14-22` declines to add a parity assertion and says why a parity test would be worthless (both wirings wrong together). `domain.py:97-98` declines to let the domain know which adapter it has. That is a genuine refusal posture and I could not find self-flattery in it.

**The overclaim:** `journal_file.py:7-9` states that a fault in that file *"is reachable by anything that runs the shared suite through the real wiring, which is every instrument the predecessor had."* **I falsified that by execution.** Fault A is a fault in `journal_file.py` — durability removed entirely, no file ever created — and it is reachable by **nothing**: 28/28 pass under the real wiring and 28/28 under the fake. `README.md:59-62`'s broader form, that running the identical suite through both wirings "is what gives a fault in either adapter somewhere to be seen", has the same shape: **true for the content class** (my faults B and E both die, symmetrically) and **false for the durability class**. The artifact never draws that distinction, and the distinction is the whole subject — this tree exists to size a blind region, and it has measured the blind region on one side of the port while leaving an unmeasured one of its own on the other.

What the artifact cannot see, it mostly names. What it cannot see and does **not** name is that its "real" adapter is only real *by inspection*: nothing in the packet distinguishes `FileJournal` from a second in-memory journal, so `README.md:52`'s table entry "the **real** adapter: a file on disk" is a property of the source text and not of anything the suite establishes.

## Verdict

Real ports and adapters with a genuinely paired fake — content faults on either side of the port die under the wiring that runs them — but the durability the port exists for is observed only by the adapter that writes it, so a `FileJournal` that never touches the disk passes all 28 cases through both wirings: read this suite as an oracle for line content and never for persistence.

## Disclosures

**Nothing was read outside the permitted set.** I did not open `references/eval_scorecard.md`, any other scorecard, `NEXT-EPIC.md`, any `*-EPIC.md`, or `specs/desired_program_model/`. I read only `artifact_CL/**` plus my own two card files and `mechanical.json` beside them.

**Things I saw inside the artifact that are about other work.** The artifact quotes its own predecessor's findings at length — `reference_ports/README.md:20-24` and `journal_memory.py:7-27` reproduce `BA-B14` and the sentence *"the port removes places for some faults to live and creates a region no shared oracle reaches"*, attributed to `specs/results/scorecards/hexagonal-prompting/FINDINGS.md`. **This is a prior result about D3, embedded in the subject.** I did not open the cited file, but I could not un-read the quotation, and it named the exact conclusion my D3 was about to reach before I had run anything. I treated it as a hypothesis to test rather than a finding to inherit, and my faults B and E were designed to *falsify* it (they did not). Worth recording for the instrument's sake: **the card-not-rubric rule keeps prior results out of the judge's hands, and this artifact hands them back through the subject.** A judge cannot be blinded to a conclusion the code's docstrings assert.

**Nothing in the artifact tree was changed.** Every run was against copies under `scratchpad/judge-v5-p2/`; `work/` is the pristine copy and each fault lives in its own sibling directory. `git status` in the worktree is unaffected by my runs.

**What I rejected.**

1. **I nearly scored D3 = 4, and the reason I nearly did is the most useful thing on this card.** Everything anchor 4 asks for is *visibly* present: a driven port, a real adapter, a fake adapter, one suite, both green. I had written "4" before I asked what the suite would notice if `FileJournal` stopped being real. The caveat's condition is not detectable by reading — the file *does* call `write_text` and `open` — so the only way to answer it was to delete the durability and re-run. **28/28, twice.** I reject the reading of anchor 4 that treats "a real adapter and a fake" as a fact about *what the adapters are*; on this evidence it has to be a fact about *what the cases can tell apart*, and here they cannot tell the two apart on the one axis the port exists for.

2. **I rejected the flattering D2 = 2, and I want the alternative on the record because I think it is a close call.** The case for 2: the design has no god-state, `_available` is written from two command sites (not "everywhere"), and the read-first paragraph explicitly says a missing complexity descriptor "is not a gap in the evidence" — so docking for the absence of figures looks like exactly the mistake that sentence forbids. The case for 0, which I took: the dimension's own question is "and no simpler", I answered it by executing a strictly simpler design that passes identically, and rungs 1 and 2 are both false on their own text while rung 0's text is true on its own text. **If a third pass overturns this, the finding to keep is not the number — it is that D2's ladder grades two different things on one axis and has no cell for a code artifact that ships no figures.** A judge scoring the same bytes can land on 0 or 2 depending only on which half of the ladder they read as governing, and that is a property of the instrument, not of the artifact.

3. **I rejected the `outstanding_ids` finding as a D2 or D3 input** and confined it to N-D1/N-D4. It is a genuine defect in the unmodified artifact — `sorted()` over `r1…r11` is not "ascending" (`domain.py:122` vs `FEATURE.md:29`) — and it was tempting to let a real bug pull a score down. It is not evidence about complexity and not evidence about modularity. It goes in the notes, which take no score, and it stays there.

4. **A claim I tested and could not break.** The artifact's central instrument claim — that a second composition point makes a fault in the *fake* adapter observable, closing the region the predecessor recorded as blind — is **true**, and I tried twice to defeat it. The fake-side fault dies (7 of 28) under the fake wiring and the identically-shaped real-side fault dies (7 of 28) under the real wiring; the kill counts are symmetric, which is the strongest possible form of the claim. `quota_ledger_fake.py` earns its four lines.

5. **I rejected re-running the suite as evidence of anything.** The 28-pass baseline appears in `what_was_run` only as a control. Every number on this card that carries weight came from changing something and re-running, and the one that carries the most weight is a run where **nothing failed**.

6. **I rejected writing the fake-adapter parity test I initially wanted.** My first instinct on finding fault A was "add a case that opens the ledger file and reads it". `quota_ledger_fake.py:16-20` argues in advance that a cross-wiring parity assertion is worthless, and it is right — but the fix for fault A is not a parity test, it is a case that reads the *filesystem*, which the fake wiring cannot run at all. That asymmetry is the real shape of the gap and it is why I recorded it rather than proposing a one-line remedy: **any oracle strong enough to catch fault A is an oracle the fake wiring cannot execute.**
