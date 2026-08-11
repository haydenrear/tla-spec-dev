# Scorecard — toolchain_removal, artifact `CL`, judge pass 2

`run_id`: `20260811-cl03v4-CL-p2` · scorecard_version 4 · rubric `examples/validation/scorecards/rubric_v4_frozen.md` digest `sha256:497c16ca85adeb4a` · served `sha256:a213a36770ccab09`

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

- Copied the artifact to a scratch tree (`scratchpad/judge-v4-p2/base` + `/work`); the artifact directory was never edited. Confirmed by `sha256` that all eight packet files are byte-identical to their counterparts under `examples/validation/ab/`, so every citation on this card resolves there.
- Baseline: `QUOTA_LEDGER_DIR=<work>/reference_ports QUOTA_LEDGER_IMPL=quota_ledger uv run --with pytest python -m pytest tests/test_behavior.py -q` → **28 passed** in 0.09s; same with `QUOTA_LEDGER_IMPL=quota_ledger_fake` → **28 passed** in 0.06s.
- **Seeded fault A (mine), fake adapter:** `InMemoryJournal.lines()` returns `reversed(self._lines)`. Result: fake wiring **5 failed / 23 passed**, real wiring **28 passed**. The fake is on the fake wiring's execution path and off the real one's.
- **Seeded fault B (mine), real adapter:** `FileJournal.lines()` returns `sorted(...)`. Result: real wiring **4 failed / 24 passed**, fake wiring **28 passed**. Mirror image of A.
- **Seeded fault C (mine), domain:** `release` decrements `_next_id`, so a released id is handed out again (verified directly: first id `r1`, next id after release `r1`, REUSED). Violates `FEATURE.md:49-50` "never reused". Result: **28 passed in BOTH wirings — 0/56 kills.**
- **Seeded fault D (mine), composition point:** `quota_ledger_fake.py` wired to `FileJournal(ledger_path)` instead of `InMemoryJournal()`. Result: **28 passed** under `QUOTA_LEDGER_IMPL=quota_ledger_fake`. Then re-applied fault A on top: **both wirings 28 passed**, i.e. the fake-adapter fault that fault A proved catchable became invisible again, with no case objecting that the fake wiring never built the fake.
- **Probe 1** (no mutation): drove 11 concurrent reservations against a single tenant and printed `outstanding_ids()` → `['r1','r10','r11','r2',…]`. The suite's `QUOTAS` (`tests/test_behavior.py:38`) cap live reservations at 3, so no case can reach this.
- **Probe 2** (no mutation): constructed `ReservationBook` twice with a tenant name containing a newline, once over `FileJournal` and once over `InMemoryJournal`; the file adapter reported 2 lines including a forged `COMMIT ghost 999 999 2 2`, the memory adapter reported 1. Same domain, same call, divergent observable state.
- **Probe 3** (no mutation): injected a hand-written spy journal directly into `ReservationBook`, drove reserve/commit/close plus two rejected commands, and recorded the append calls and the temp directory contents before and after. Two appends, no file created, no append on a rejection.
- **Probe 4** (no mutation): constructed a second `QuotaLedger` on a path that already held a committed line; `ledger_lines()` came back empty (the constructor truncates, `journal_file.py:28-30`). No case in the suite reconstructs on an existing path.

## Your scores

### D2 — complexity

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:101-108` — the whole of the stored state
- `reference_ports/domain.py:103`, `:140`, `:161` — the three `_available` write sites
- `reference_ports/domain.py:112`, `:136` — the two `_available` read sites
- `reference_ports/quota_ledger.py:21-36` and `reference_ports/quota_ledger_fake.py:34-49` — two near-identical composition points, each with a hand-maintained seven-entry `__all__`
- `reference_ports/journal_file.py:38` and `reference_ports/journal_memory.py:43` — the "no blanks" rule implemented twice
- `FEATURE.md:91-93` — R1, which makes `_available` derivable
- `reference_ports/README.md:13-16` — the artifact's own disclosure that `available` is stored rather than derived on purpose

**Refuses to claim** (required and non-null for a score of 3): _n/a — not a top-of-scale score._

**Rationale:**

No figure exists to score. `mechanical.json` ships with `complexity_of_produced_code: {}` and there is no descriptor anywhere in the packet, so anchor 1 ("measured and reported") is factually not met; the card's read_first says the absence of a descriptor is not a gap in the evidence, so I did not let anchor 0's "unmeasured" trigger decide a design question, and judged proportionality directly.

I ran the read_first probe — is one fact stored twice, kept in agreement by hand across several write sites and read in one place? Yes, once: `_available` (`reference_ports/domain.py:103`) is fully derivable from quota minus outstanding minus committed, which is exactly what `FEATURE.md:91-93` states as R1, and it is instead maintained by hand at three write sites (`:103` init, `:140` reserve, `:161` release) and read at two (`:112`, `:136`). The artifact discloses this is deliberate (`reference_ports/README.md:13-16` refers to "the same argument that made `available` a stored field rather than a derived one"). Three write sites inside the two commands that own the field, in a 173-line module, is redundancy but not god-state and not a variable written from everywhere — so anchor 2 holds and anchor 0 does not.

Two smaller duplications sit beside it: the two composition points are near-identical including a hand-maintained seven-entry `__all__` re-export each (`quota_ledger.py:21-36`, `quota_ledger_fake.py:34-49`), and the "no blank lines" rule is implemented twice, once per adapter (`journal_file.py:38`, `journal_memory.py:43`) — while the rule that actually distinguishes them, *one line per append*, is implemented in neither (see Disclosures).

3 is unreachable and not by a hair: no simplification is claimed, none is measured, and no before/after figures exist. The structural move here is an **addition** (one flat module becomes five files), not a simplification. I also could not perform the read_first's first instruction — "diff the two trees yourself" — because only one tree is in the packet: the flat `../reference/quota_ledger.py` that `domain.py:8-10` and `README.md:33-35` claim this matches "statement for statement" is not under `artifact_CL/`, so that claim is a claim and I did not score it.

The prose tempted me: the docstrings argue their own design quality fluently and I scored the field write sites instead.

### D3 — modularity

**Score:** **4**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:20-23` — the domain's complete import list: `dataclasses`, `typing`. No pathlib, no os, no adapter.
- `reference_ports/domain.py:38-58` — the `LedgerJournal` port declared in the domain
- `reference_ports/domain.py:101-108` — the journal injected, never constructed
- `reference_ports/domain.py:124-125`, `:150-153`, `:172` — every crossing of the boundary, all three through the port
- `reference_ports/quota_ledger.py:18`, `:25` vs `reference_ports/quota_ledger_fake.py:31`, `:38` — **the named swap**
- `reference_ports/journal_file.py:16-18`, `reference_ports/journal_memory.py:30-43` — adapters import nothing from the domain
- `tests/test_behavior.py:34-36` — the same byte-identical file selects its module by env var
- `tests/test_behavior.py:270-281` — the case that killed both of my adapter faults

**Refuses to claim** (required and non-null for a score of 4):

The artifact refuses to claim that an arm would produce this shape (`reference_ports/README.md:69-71`: "It does not show that an **arm** will produce this shape"), refuses to claim its own generality (`README.md:72-74`: n = 1, and the tree was written by the same author as the catalogue that seeds into it), refuses to read the fake's cheapness as evidence anyone would have built it (`README.md:75-77`), refuses to gate or report a verdict (`README.md:66`), and refuses a parity test between the two wirings with a stated reason — `quota_ledger_fake.py:15-20` says a test that only compares two wirings passes when the domain is wrong because both wirings are wrong together. `domain.py:96-98` also refuses to know its own wiring: "Which one is not this module's business and is not knowable from this file."

**Rationale:**

I took the caveat literally and gathered **call** evidence, not import evidence. Import facts first, as the floor: `domain.py:20-23` imports only `dataclasses` and `typing` — no pathlib, no os, no adapter module — and both adapters import nothing from the domain (`journal_file.py:16-18` takes pathlib only; `journal_memory.py:30-43` imports nothing at all), so the port at `domain.py:38-58` is structural and the dependency runs one way. The named swap: `quota_ledger.py:18`/`:25` constructs `FileJournal(ledger_path)`; `quota_ledger_fake.py:31`/`:38` constructs `InMemoryJournal()` at the same one line, with the same constructor signature, and no file under the domain changes between them — that is anchor 3, executed rather than asserted.

Runtime evidence for anchors 3 and 4, all of it mine:

- **(a)** I injected a spy journal straight into `ReservationBook` and drove reserve/commit/close plus two rejected commands; the only writes observed were `append('COMMIT acme 3 3')` and `append('CLOSE acme 3')` (the two sites at `domain.py:150-153` and `:172`), the domain created no file in the temp directory, and no rejected command produced an append.
- **(b)** Seeded fault A in the fake adapter: fake wiring 5 failed / 23 passed, real wiring 28/28 green.
- **(c)** The mirror fault B in the real adapter: real wiring 4 failed / 24 passed, fake wiring green.

Each adapter is provably on its own wiring's execution path and provably off the other's — that is what *calls* what at runtime, and it is exactly the evidence the caveat asks for and that import topology cannot supply. The identical 28 cases (`tests/test_behavior.py:34-36` selects the module by env var, so the file is byte-identical across wirings) pass against both, which is anchor 4's literal requirement, and `test_behavior.py:270-281` is the case that killed both of my adapter faults.

**I nearly scored 3 and I want the reason on the record rather than in the score.** `InMemoryJournal` is not shown to satisfy the same contract as `FileJournal`. I found a legal input where they observably diverge — a tenant name containing a newline makes the file adapter report two ledger lines, one of them forged, where the memory adapter reports one (see Disclosures) — so "the same cases pass against both" is a statement about the region where the two agree and nothing more. I did not downgrade, because that is a limit on what the 4 *means* and not a failure of the anchor as written, and rule 3's top-of-scale gate is the place the rubric puts such limits.

The prose tempted me hard here and I will say so plainly: `domain.py:38-52` and `journal_memory.py:7-27` pre-argue anchors 3 and 4 in their own docstrings, naming the port, naming the swap and naming the significance of the fake. I scored the seeded-fault runs, not those paragraphs; had the runs come out otherwise the docstrings would have earned nothing.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `reference_ports/domain.py:122` — `sorted(self._outstanding)`, lexicographic
- `reference_ports/domain.py:138-139`, `:156-162` — the id counter and `release`
- `reference_ports/domain.py:54-55` — the port's "add one line" contract
- `reference_ports/journal_file.py:32-34`, `reference_ports/journal_memory.py:39-40` — the two `append` implementations
- `tests/test_behavior.py:38`, `:177-180`, `:270-281`
- `FEATURE.md:29`, `FEATURE.md:49-50`

**Note:**

**Caught:** order and content faults in whichever adapter the wiring under test actually builds. My seeded fault A (fake adapter `lines()` reversed) died 5/28 in the fake wiring; my seeded fault B (real adapter `lines()` sorted) died 4/28 in the real wiring; `tests/test_behavior.py:270-281` is the case that killed both, and the R4 snapshot comparisons (`tests/test_behavior.py:85-91`, `:140-145`) plus my spy probe show a rejected command performs no durable write.

**Missed, demonstrably, three classes:**

1. **Reservation-id identity.** My seeded fault C decrements `_next_id` in `release` (`reference_ports/domain.py:156-162`, counter at `:138-139`), so a released id is reissued — directly contrary to `FEATURE.md:49-50` "never reused" — and 28 cases passed in **both** wirings, 0/56. `tests/test_behavior.py:177-180` releases and reserves again but asserts only `status`, never the id.
2. **Ordering of `outstanding_ids()`.** `reference_ports/domain.py:122` returns `sorted(self._outstanding)`, which is lexicographic over strings: with 11 live reservations I measured `['r1','r10','r11','r2','r3',…]`, which is neither allocation order nor the "ascending" `FEATURE.md:29` asks for. **This is a live defect in the shipped artifact, not a mutant**, and it is unreachable by construction — `QUOTAS` at `tests/test_behavior.py:38` totals 14 units across two tenants and no case holds more than three reservations at once, so no case can ever see a two-digit id.
3. **The adapter contract itself.** The port's `append` is documented as "add one line" (`reference_ports/domain.py:54-55`) and neither implementation enforces it: `FileJournal.append` writes `line + '\n'` verbatim (`journal_file.py:32-34`) while `InMemoryJournal.append` stores the string whole (`journal_memory.py:39-40`), so a tenant name containing a newline forges a ledger line in one adapter and not the other. Nothing in the suite constructs a hostile tenant name.

A fourth miss worth recording is not a fault class but an **instrument gap**: my seeded fault D repoints `quota_ledger_fake.py` at `FileJournal` and 28 cases pass while calling themselves the fake wiring, so the suite cannot detect that the arrangement it is supposed to be exercising has been dismantled.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `reference_ports/domain.py:8-10`, `reference_ports/README.md:33-35` — the named-but-absent baseline
- `reference_ports/domain.py:112-125`, `:130-137`, `:144-154`, `:164-173` — the queries and the four commands
- `reference_ports/domain.py:39`, `reference_ports/journal_file.py:28-30` — "durable", and the truncating constructor
- `tests/test_behavior.py:239-281` — R1, R2, R5 end to end
- `FEATURE.md:21`, `FEATURE.md:50`, `FEATURE.md:89-104`

**Note:**

**There is no baseline in the packet, and that is the answer.** The artifact names one — `reference_ports/domain.py:8-10` and `README.md:33-35` say the behaviour is `../reference/quota_ledger.py`'s "statement for statement" — but that tree is not under `artifact_CL/` and my read list is the packet, so the preservation claim is a claim and I did not score it. I therefore enumerated the **specification's** behaviours instead and checked each against code plus execution.

**Shown to hold**, on both wirings, 28/28: the five queries (`FEATURE.md:23-30` against `domain.py:112-125`); reserve's four rejections in the specified precedence order (`FEATURE.md:40-45` against `domain.py:130-137`, exercised at `tests/test_behavior.py:75-101`); reserve's accept effects and ascending id allocation for small ids (`FEATURE.md:47-50`, `tests/test_behavior.py:60-73`); commit moving the hold into committed, writing exactly one line and **not** restoring `available` (`FEATURE.md:52-67`, `domain.py:144-154`, `tests/test_behavior.py:112-119`); release restoring the hold and writing nothing (`FEATURE.md:69-72`, `domain.py:156-162`, `tests/test_behavior.py:159-166`); close's three rejections and its single CLOSE line (`FEATURE.md:74-87`, `domain.py:164-173`, `tests/test_behavior.py:186-233`); R1 (`:239-255`); R2 (`:258-267`); R3 (`:186-197` with `:218-233`); R4 — and my spy probe adds that a rejected command produces no `append` **call** at all, which the snapshot comparisons cannot distinguish from a write that happens to be invisible; R5 (`:270-281`).

**Not shown to hold, and I looked:** "ids are never reused" (`FEATURE.md:50`) is asserted by nothing and my mutant survived both wirings; `outstanding_ids()` ascending is false beyond nine live reservations (`domain.py:122`) and unreachable by any case; **durability**, the adjective the port is named for (`domain.py:39`), is verified by no case that outlives one object — I constructed a second ledger on a populated path and got an empty ledger back, which matches `FEATURE.md:21` ("The ledger file starts empty") and is therefore **not** a defect, but it does mean the only "durable" the suite ever tests is a read-back inside one object's lifetime, and under the fake wiring not even that.

### N-D5 — honesty

**Citations** (`file:line`):

- `reference_ports/README.md:66`, `:68-77` — the refusals
- `reference_ports/README.md:36-39` — the one certification
- `reference_ports/quota_ledger_fake.py:15-20`, `reference_ports/domain.py:96-98`, `:8-10`
- `reference_ports/journal_file.py:32-34`, `reference_ports/journal_memory.py:39-40`

**Note:**

It refuses more than most artifacts I have scored, and it refuses in the load-bearing places. `reference_ports/README.md:68-77` is a titled section of things the tree does not settle: it does not show an arm would produce this shape, it is n = 1, the tree and the catalogue that seeds into it share an author, and — the sharpest one — the fake being four lines is evidence the blind region was *cheap to reach* and explicitly **not** evidence anybody would have reached it: "Nobody did, for a whole epic, and that is the measured fact." `README.md:66` refuses a verdict outright ("Nothing here gates, refuses, or reports a verdict. It is a fixture"). `quota_ledger_fake.py:15-20` refuses a parity test between the two wirings and gives the correct reason, that two wirings of one domain agree when the domain is wrong. `domain.py:96-98` refuses to know its own wiring.

Set against that, **one sentence does certify, and it is the one I could falsify**: `README.md:36-39`, "The claim that it is the same subject is not a claim — the identical shared suite passes against all three wirings." A green shared suite establishes agreement on the 28 cases it contains and nothing outside them, and my probe 2 exhibits a legal input on which two of those wirings observably disagree — a tenant name with a newline yields two ledger lines through the file adapter and one through the memory adapter. So the one place the artifact upgrades evidence into proof is the place the evidence does not reach. The "statement for statement" equivalence at `domain.py:8-10` is the same shape of claim and is unverifiable inside the packet. Both are overreach in kind rather than dishonesty: the artifact names the instrument it is relying on in the same breath, which is what let me go and check it.

## Verdict

The port is real at runtime and not merely in the import graph — I proved it by killing a fault on each side of it independently — but the shared suite is the only oracle over both adapters and it is thinner than it looks: an id-reuse fault, the lexicographic `outstanding_ids()` ordering, and a one-line edit that silently points the fake wiring at the real adapter all survive 28/28 cases in both wirings.

## Disclosures

**What I saw that I was not meant to see:** nothing. I did not open `references/eval_scorecard.md`, `NEXT-EPIC.md`, any `*-EPIC.md`, `specs/desired_program_model/`, or any other scorecard. Two exceptions I am declaring rather than hiding: (1) the artifact's own prose quotes the predecessor's `FINDINGS.md` at `reference_ports/README.md:20-24` and `journal_memory.py:9-15`, including the `BA-B14` result and the sentence "the fake that earned arm B its D3 = 4" — so the packet handed me a prior D3 score on a related artifact before I had formed my own. I read it inside the artifact I was told to read in full and could not unsee it; I mitigated by gathering my own runtime evidence before settling D3, and I note that the number I reached matches the one the packet named, which is exactly the contamination a reader should discount. (2) I ran `shasum` against the eight files under `examples/validation/ab/` purely to confirm my citations resolve there; I compared digests, not contents.

**What I ran that changed a tree:** only my scratch copy at `scratchpad/judge-v4-p2/work`, reset from `base` between every fault. The artifact directory was not written to. My four seeded faults and four probes are itemised under Judging practice.

**What I REJECTED:**

- **I rejected D3 = 3, twice, and nearly took it.** First on the contract-divergence ground (probe 2: the two adapters are not interchangeable on a legal input, so "the same cases pass against both" proves less than the anchor's phrasing suggests). Second on the ground that fault D shows the anchor-4 arrangement is defeatable by a one-line edit no case detects. I rejected both because they are limits on what the 4 means, not evidence the anchor is unmet, and because taking the tie-break rule as cover would have been scoring my own disclosure instead of the artifact. A third judge with new evidence should feel free to overturn me on exactly this.
- **I rejected reading anchor 0 mechanically for D2.** "Complexity is unmeasured" is literally true — `mechanical.json` figures are all empty — and a literalist would have scored 0 and been done. The read_first says absence of a descriptor is not a gap in the evidence, which makes anchors 0 and 1 unreachable for any artifact that ships no descriptor and pushes the whole D2 ladder onto anchor 2 vs 3. **That is a structural observation about the instrument, not about this artifact:** for a subject with no complexity descriptor, D2 has exactly two live rungs and 3 requires a recorded before/after, so D2 is a near-deterministic 2. It cost me no judgement to reach the score, which is a bad sign for a scored dimension.
- **I rejected the claim I could not test.** `domain.py:8-10` and `README.md:33-35` say this tree matches the flat reference "statement for statement". The flat tree is not in the packet, so I did not score it as evidence for anything — including D2, where the read_first explicitly instructs "diff the two trees yourself". **The card asks for a two-tree diff and the packet contains one tree.** That mismatch is worth fixing in the scaffold, not in the score.
- **I tried to break a claim and could not:** the artifact says the domain does not import its I/O and holds "no path, no file handle, no clock, no environment and no global" (`domain.py:14-18`). I attacked it at runtime rather than by reading imports — spy journal injected directly, temp directory diffed before and after — and it held: two `append` calls, zero files created, zero appends on rejected commands. `quota_ledger_fake.py:15-20`'s refusal to write a parity test also survived scrutiny; its stated reason is correct, and my probe 2 is in fact an instance of the failure mode it names in reverse (the wirings disagreeing where nothing looks).
- **I rejected re-running the suite as a finding.** The 28/28 green on both wirings is the floor `FEATURE.md:108-111` names, and on its own it told me nothing. Every result above came from a fault or a probe, not from the suite as shipped.
