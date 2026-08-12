# Scorecard — toolchain_removal, artifact `LG`, judge pass 2

`run_id`: `20260812-sv04conf-LG-p2` · scorecard_version 5 · rubric `references/eval_scorecard.md` digest `sha256:24b2c599901d7ae0` · served `sha256:2d7d4a0506d9b259`

**You are scoring artifact `LG`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

- Copied the packet to `…/scratchpad/SV-04/judge-LG-p2/base` and mutated only copies. `git status --porcelain` on the packet is clean afterwards.
- Green control, three repetitions each, identical output every time:
  `QUOTA_LEDGER_DIR=<base>/reference_ports QUOTA_LEDGER_IMPL=quota_ledger uv run --with pytest python -m pytest <base>/tests/test_behavior.py -q -p no:cacheprovider` → **28 passed** (~0.08s)
- Same with `QUOTA_LEDGER_IMPL=quota_ledger_fake` → **28 passed** (~0.07s)
- `QUOTA_LEDGER_PORTS_DIR=<base>/reference_ports … python -m pytest <base>/tests/test_journal_conformance.py -q -p no:cacheprovider` → **14 passed** (~0.07s)
- **14 faults of my own**, one per fresh copy, each run against all three suites (42 suite runs):
  - *fake adapter* — J1 drops `CLOSE` lines; J2 sorts its lines; J3 stops filtering blanks; E2 `lines()` returns its live internal list.
  - *real adapter* — F1 `FileJournal` becomes a pure in-memory buffer with no filesystem call; F2 buffers until two lines are pending; F3 drops `CLOSE` lines; F4 constructor `touch()`es instead of truncating; E1 `append` rewrites the whole file; E3 `lines()` rewrites the file before reading it.
  - *domain* — D1 `release` appends a `RELEASE` line; D2 `commit` credits `available`; D3 the `amount_not_positive` / `quota_exceeded` guard order swapped; D4 `ledger_lines()` returns a shadow list instead of calling the port.
- Kills out of 14 — shared suite / real wiring **5**; shared suite / fake wiring **5**; conformance suite **7**; union **10**. Survivors: D3, E1, E2, E3.
- Proved by exhaustive enumeration (`available` 0..20, `amount` −20..20) that survivor **D3 is an equivalent mutant** and is not counted as a miss; genuine survivors are 3 of 13 non-equivalent faults.
- Reproduced the artifact's own falsifiable claim at `tests/test_journal_conformance.py:14-17` exactly: with `FileJournal`'s body replaced by a list, **28 of 28** shared cases pass through the real wiring and **zero** `ledger.txt` files are created.
- Counted state and write sites in `reference_ports/domain.py` by hand (ast + grep) rather than reading the docstrings' account of them.

## Your scores

### D2 — complexity

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:101-108` — the whole of the domain's state, six fields
- `reference_ports/domain.py:140`, `:149`, `:161`, `:171` — every write site outside the constructor
- `reference_ports/domain.py:150-153` — the one fact stored twice: `_committed` and the running total on the line
- `reference_ports/quota_ledger.py:24-25`, `reference_ports/quota_ledger_fake.py:37-38` — each composition point is one constructor line
- `FEATURE.md:61` — the running total is demanded by the feature
- `FEATURE.md:92` — R1, which makes `_available` derivable and therefore redundant

**Refuses to claim** (required and non-null for a score of 3):

It refuses to claim the shape generalises or that the tree is unbiased — `reference_ports/README.md:69-77` says it does not show an arm will produce this shape, that it is `n = 1`, and that the tree and the fault catalogue that seeds into it share an author, "the same declared bias the flat reference carries and it is not reduced by there being two trees."

**Rationale:**

Anchor 2, not 3, and the missing rung is the measurement, not the design. I diffed the state by hand rather than trusting the prose. `ReservationBook` holds six fields (`domain.py:101-108`) and every one is written from at most two command bodies: `_available` at `:140` and `:161`; `_committed` at `:149` only; `_closed` at `:171` only; `_outstanding` at `:141`/`:148`/`:160`; `_next_id` at `:139`; `_journal` never after construction. No field is written from everywhere and there is no god-state: the aggregate is one aggregate because `FEATURE.md:92`'s R1 is a per-tenant invariant across exactly these fields, so the coupling is the behavior's, not the design's. The subject is 339 lines over five files, of which the two composition points are one class and one constructor line each — proportional to a five-query, four-command feature.

One fact **is** stored twice and it belongs on the record. `committed(tenant)` lives both in `_committed` and in the running total rendered onto the COMMIT line (`domain.py:150-153`); and `_available` is fully derivable via R1 yet is stored and hand-maintained across two write sites. Neither is a defect under this anchor — the running total is literally demanded by `FEATURE.md:61`, and stored-vs-derived is a free choice — but it is why I did not reach further, and why this 2 should not be read as "nothing is duplicated".

Anchor 3 fails on its own words: it requires that "a simplification was made and its effect measured — the before and after figures are both recorded". **No figure of any kind is recorded anywhere in the packet**: no complexity descriptor, no line or fan-in count, no before tree. The packet asserts behavioural identity with a flat predecessor (`domain.py:8-10`) but that module is outside the scored scope and outside my read list, so I can neither check it nor extract a "before" from it — and per this dimension's own `read_first`, the absence of a descriptor is not a gap in the evidence, it simply leaves rung 3 unearned. MF-020's warning never gets to apply: there is no number to have dropped.

A note on the literal ladder, because a second judge may read it differently. Read strictly, anchor 0 ("Complexity is unmeasured") is a true sentence about this packet, and "score the LOWEST anchor the artifact fully satisfies" would then force a 0. I reject that reading: the `read_first` says in terms that where no measured descriptor exists "that is not a gap in the evidence" and tells the judge to diff the trees and decide, which is unintelligible if a missing metric caps the score at 0. I read 0/1 as describing artifacts whose only complexity story is a number, and 2/3 as describing the design. Under that reading the design is proportional and the measurement is absent — exactly 2.

Prose quality was not an input, and it did tempt me: every file here carries an unusually persuasive docstring arguing its own design. I scored the field list and the write sites, and where a docstring made a checkable numeric claim I ran it instead of believing it.

### D3 — modularity

**Score:** **4**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:20-23` — the domain's entire import list: `dataclasses`, `typing`
- `reference_ports/domain.py:38-58` — `LedgerJournal`, the driven port, declared as a structural `Protocol`
- `reference_ports/domain.py:125`, `:150-153`, `:172` — the only three call sites that cross the boundary
- `reference_ports/quota_ledger.py:17-25` and `reference_ports/quota_ledger_fake.py:30-38` — the named swap, `FileJournal(ledger_path)` → `InMemoryJournal()`
- `reference_ports/journal_file.py:32-38`, `reference_ports/journal_memory.py:39-43` — the two implementations; neither imports the domain
- `tests/test_journal_conformance.py:117-128` — `record_on_disk()`, the observer that is not the writer
- `tests/test_journal_conformance.py:144-166` — one parametrised source, both implementations
- `tests/test_journal_conformance.py:181-210`, `:216-232` — the durable clauses, and the fake's defining property asserted rather than assumed

**Refuses to claim** (required and non-null for a score of 4):

It refuses to treat agreement between the two wirings as an oracle, and says why — `reference_ports/quota_ledger_fake.py:14-22`: "it does not assert that the two wirings agree. A test that only compares two wirings of one domain passes when the domain is wrong, because both wirings are wrong together." It further refuses to claim the conformance suite sees the domain, concurrency, crash-atomicity, or any record older than one object (`tests/test_journal_conformance.py:39-52`).

**Rationale:**

Anchor 4, reached on runtime evidence because the caveat says import topology does not count.

Anchor 3 first. The domain imports only `dataclasses` and `typing` (`domain.py:20-23`), declares `LedgerJournal` as a structural `Protocol` (`:38-58`), and reaches the durable side only through it, at three sites: `:125`, `:150-153`, `:172`. The named swap: `quota_ledger.py:25` hands `FileJournal(ledger_path)` to `ReservationBook.__init__`; `quota_ledger_fake.py:38` hands `InMemoryJournal()` to the identical constructor. No file under `reference_ports/` other than the composition point differs between the two. The dependency runs one way at the adapter end too — `journal_file.py` imports only `pathlib`, `journal_memory.py` imports nothing, so neither adapter knows the domain exists.

Anchor 4 needs the same cases passing against both, and needs the pair to be a real one and a fake one rather than two fakes. I ran the identical 28-case shared suite through both composition points: **28 passed** under each, three times, byte-identical output. On top of that, `test_journal_conformance.py:144-166` runs one parametrised source of four port-contract cases against both implementations directly — 8 executions, all green.

The caveat is what decides this dimension, so I attacked it rather than reciting it. *"Anchor 4 holds when the real adapter does nothing real: if the only observer of the effect the port exists for is the adapter that wrote it, say so and take 3."* There **is** an observer outside the writer: `test_journal_conformance.py:117-128`'s `record_on_disk()` opens the declared path with `Path.read_text` and never calls `lines()`, and `:181-210` makes every assertion through it. I did not take that on the docstring's word. I seeded a fault replacing `FileJournal`'s body with a plain in-memory buffer, removing every filesystem call: **28/28 shared cases pass through the REAL wiring with zero `ledger.txt` files created, and 5 conformance cases kill it.** So the out-of-band observer is load-bearing and the real adapter provably does something the fake cannot. `:216-232` closes the other half by asserting the fake writes no file at all, under a `chdir` so an invented path would be caught.

I also checked that the swap swaps what *executes*, not only what imports. A fault seeded in `journal_memory.py:39-43` (drop `CLOSE` lines) leaves the real wiring green at 28/28 and kills 3 cases under the fake wiring; the mirror fault in `journal_file.py:32-38` does the reverse — 3 kills real, 0 kills fake. Two faults with one semantic, one on each side of the port, land on opposite sides of the run. That is a runtime fact about what calls what, which is what the caveat demanded.

One reservation I will not hide, and it did not move me off 4: "durable" here means the file outlives the *object*, not the run — `journal_file.py:30` truncates on construction, so a second `FileJournal` over a written path destroys the record. The artifact pins that itself as an executable case (`test_journal_conformance.py:235-250`), which is why it reads as a scoped port rather than an oversold one.

Prose quality was not an input. Every docstring here argues its own case at length, and that is exactly why I ran mutants instead of reading them.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `reference_ports/journal_file.py:30`, `:32-38` — the real adapter's region
- `reference_ports/journal_memory.py:39-43` — the fake adapter's region
- `reference_ports/quota_ledger_fake.py:37-38` — the second composition point, without which fake-side faults have nowhere to be seen
- `reference_ports/domain.py:134-137` — the equivalent mutant
- `tests/test_journal_conformance.py:117-128` — the only out-of-band observer in the packet
- `tests/test_journal_conformance.py:40-43` — the suite's own statement that it cannot see the domain
- `tests/test_behavior.py:112-119`, `:270-281` — the domain cases that do
- `FEATURE.md:104` — R5, "Nothing is ever rewritten", the clause nothing asserts

**Note:**

I seeded 14 faults of my own and ran all three suites against each.

**Domain faults** are caught by the shared suite through *either* wiring and are invisible to the conformance suite — `release` appending a line, `commit` crediting `available`, and `ledger_lines()` returning a shadow all died (1–7 cases) under both wirings while `test_journal_conformance.py` stayed 14/14 green. That is exactly what that file says about itself at `:40-43`, and it checks out: the two suites are complements, not overlaps.

**Adapter faults** are caught asymmetrically, and this is the packet's real instrument. A fault in `journal_memory.py:39-43` is invisible to the real wiring and killed by the fake wiring; the mirror fault in `journal_file.py:32-38` is the reverse. Without the second composition point (`quota_ledger_fake.py:37-38`) the fake-side faults would have had nowhere to be seen at all. Three adapter faults were killed **only** by the conformance suite: the fake keeping blanks, the constructor `touch()`ing instead of truncating (`journal_file.py:30`), and above all `FileJournal` reduced to an in-memory buffer — 28/28 shared cases pass through the real wiring with zero files written, and `test_journal_conformance.py:117-128` kills it in 5 cases. So the conformance file is not decoration; it is the only thing in the packet that observes the effect the port exists for.

**The class they demonstrably miss is the write discipline itself** — `FEATURE.md:104`'s "Nothing is ever rewritten". I seeded E1 (`append` reads the whole file and rewrites it with the new line appended) and E3 (`lines()` rewrites the file before reading it). Both are content- and order-identical, and both pass all three suites: 28 real, 28 fake, 14 conformance, **zero kills out of 70 case-executions**. Every case in the packet observes the *content* of the record; none observes how the bytes got there. So "append-only as an outcome" is asserted well and "append-only as a mechanism" is unasserted. A second missed class is encapsulation: E2 — `InMemoryJournal.lines()` returning its live internal list so a caller can mutate the record through the accessor — survives all three suites; `journal_memory.py:43` happens to return a fresh list and nothing holds it to that.

One survivor is **not** a miss, and I checked rather than reported it: swapping the `amount_not_positive` and `quota_exceeded` guards at `domain.py:134-137` survives everything, but with `available >= 0` and integer amounts there is no input on which the orderings differ (enumerated exhaustively). It is an equivalent mutant, and counting it would have inflated the miss rate by a third.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `reference_ports/domain.py:8-10`, `reference_ports/README.md:36-45` — the equivalence claim, and the commands that would decide it
- `FEATURE.md:25-31`, `:40-45`, `:72`, `:104` — the clauses I enumerated
- `reference_ports/domain.py:112-125`, `:144-154` — the queries and commit
- `tests/test_behavior.py:46-54`, `:85-91`, `:258-267`, `:270-281` — the snapshot, R4, R2 and R5-order

**Note:**

**There is no baseline tree in the packet, and that is the answer.** `domain.py:8-10` and `README.md:36-38` assert this tree's behavior is `../reference/quota_ledger.py`'s "statement for statement", but that module is outside the scored scope and outside my read list, so the equivalence claim is unverifiable from here and I did not chase it. Note that the claim is stated as *checkable* rather than as a conclusion — `README.md:39-45` names the exact commands that would decide it — so its unverifiability is a property of my packet, not of the artifact.

What the packet does give me is a **specification** baseline, `FEATURE.md`, and I enumerated it clause by clause against runs rather than docstrings:

1. the five observable queries (`FEATURE.md:25-31`) — implemented at `domain.py:112-125`, all five read in `test_behavior.py:46-54`'s snapshot. **Holds.**
2. `reserve`'s four rejections in order (`FEATURE.md:40-45`) — `domain.py:130-137`, covered by `test_behavior.py:75-101`. **Holds**; and the `amount_not_positive`/`quota_exceeded` ordering turns out to be unobservable, so "in order" is untestable for that pair rather than untested.
3. `commit`'s effects incl. `available` **not** returned (`FEATURE.md:52-66`) — `domain.py:144-154`, asserted at `test_behavior.py:112-119`. **Holds**; my seeded D2 dies there.
4. `release` writes nothing to the ledger (`FEATURE.md:72`) — `domain.py:156-162` has no journal call; `test_behavior.py:159-166`. **Holds**; my seeded D1 dies there.
5. `close`'s three rejections and its single CLOSE line (`FEATURE.md:76-88`) — `domain.py:164-173`, `test_behavior.py:186-233`. **Holds.**
6. R1 conservation — `test_behavior.py:239-255`, both with reservations live and after they resolve. **Holds.**
7. R2 ledger agrees with memory — `test_behavior.py:258-267` recomputes the running total from the parsed lines. **Holds.**
8. R3 close is final and singular — covered in part (`test_behavior.py:209-226`); "exactly one CLOSE line" follows from the already-closed rejection rather than being asserted as a count.
9. R4 a rejection changes nothing — the strongest thing in the suite: every rejection case snapshots all five observables and compares (`test_behavior.py:85-91`). **Holds.**
10. R5 append-only and ordered (`FEATURE.md:104`) — *order* holds (`test_behavior.py:270-281` pins the exact interleaved sequence). *"Nothing is ever rewritten"* does **not** hold as an assertion; see N-D1.

All ten were checked through **both** composition points, three repetitions, 28/28 each time — so whatever preservation the shared suite establishes, it establishes on both sides of the port and not only on the wired one.

### N-D5 — honesty

**Citations** (`file:line`):

- `tests/test_journal_conformance.py:14-17` — a falsifiable numeric claim, which I falsified against and it held
- `tests/test_journal_conformance.py:39-52` — "WHAT THIS SUITE STILL CANNOT SEE"
- `tests/test_journal_conformance.py:235-250` — a limit pinned as an executable case
- `reference_ports/quota_ledger_fake.py:14-22` — refusing the cheapest available oracle
- `reference_ports/README.md:66`, `:69-77` — "It is a fixture"; the three refused generalisations
- `reference_ports/journal_file.py:30` — the truncation the limit is about
- `FEATURE.md:104` — the clause the artifact does *not* list among its blind spots

**Note:**

It refuses, in four distinct places, and — the part that actually persuaded me — its refusals are falsifiable and survived falsification.

The refusals. (a) `test_journal_conformance.py:39-52` names three blind spots by name: anything about `ReservationBook`, concurrency and crash-atomicity, and any record older than one object. All three are true; I confirmed the first by seeding domain faults that leave the conformance suite 14/14 green. (b) `quota_ledger_fake.py:14-22` refuses the cheapest available oracle — comparing the two wirings to each other — and gives the correct reason, that both wirings are wrong together when the domain is wrong. An artifact reaching for a score would have taken the parity test and called it a differential oracle. (c) `README.md:69-77` refuses three generalisations at once: that an arm would produce this shape, that `n > 1`, and that author bias is reduced by there being two trees. (d) `README.md:66`: "Nothing here gates, refuses, or reports a verdict. It is a fixture."

It also converts a limit into an executable case instead of a caveat, which is the strongest form of this. `test_journal_conformance.py:235-250` asserts that constructing a second `FileJournal` over a written path **destroys** the record (`journal_file.py:30` truncates), so "outlives the run" is true of the file and not of the adapter. Naming a weakness in prose is cheap; pinning it so that a later tree which fixes it must come and change the case is not.

What I checked rather than accepted: `test_journal_conformance.py:14-17` stakes a hard number — "28 of 28 shared cases still pass through the real wiring while zero `ledger.txt` files are created" if `FileJournal` is replaced by a plain list. I built exactly that mutant. 28 passed; no file created. **The claim is exactly true.** A docstring that stakes a falsifiable number and is right is the honesty evidence here; the eloquence around it is not, and I ignored it.

Two debits, neither large. `README.md:76` calls `quota_ledger_fake.py` "four lines"; the file is 49 lines and the wiring within it is five (`quota_ledger_fake.py:34-38`), and the figure is repeated at `quota_ledger_fake.py:11`. It is a small overstatement in the direction of the artifact's own argument, and the only claim in the packet I found inaccurate. Second: the honesty is concentrated in docstrings whose authority a reader cannot check without doing what I did — the artifact ships no machine-readable record of what it ran, so every number in it is a claim until a judge re-runs it. It happens to be a claim that held.

What it does **not** name and should: `FEATURE.md:104`'s "nothing is ever rewritten" is asserted by no case, and the conformance suite's own list of blind spots (`:39-52`) omits write discipline — even though that file is the one place that would have observed it.

## Verdict

A genuine ports-and-adapters tree whose port is verified from outside the writer — D3 = 4 survived a deliberate attack on the anchor-4 caveat (a `FileJournal` replaced by an in-memory buffer passes 28/28 through the real wiring and is killed only by the out-of-band conformance cases) — but D2 stops at **2** because the packet records no complexity figure of any kind, and the one fault class that survives all three suites is `FEATURE.md:104`'s "nothing is ever rewritten": an adapter that rewrites the whole ledger file on every append, or on every read, is indistinguishable from an appending one to all 70 case-executions in this packet.

## Disclosures

**Leak, disclosed, from inside my own packet.** The artifact's prose tells me what it is and quotes a prior round's result at me. `reference_ports/README.md:3-4` and `reference_ports/domain.py:3-4` both open with "**THIS IS NOT AN ARM**", so I know the subject I hold is a reference/anchor tree rather than an A/B arm's output. Worse for blinding, `reference_ports/README.md:19-23` and `reference_ports/journal_memory.py:9-15` quote `specs/results/scorecards/hexagonal-prompting/FINDINGS.md` verbatim, including finding id `BA-B14` and the sentence "the fake that earned **arm B its D3 = 4** is verified by nothing outside arm B's own tests" — i.e. a prior D3 score, on this same dimension, in the packet I was told to read in full. `tests/test_journal_conformance.py:16-18` adds a second finding id, `RM-05-DF-05`. I did not open any of those files and I did not go looking for the arm mapping. I have no way to un-see the number, so I state plainly how I handled it: I scored D3 by seeding faults and running them, and my anchor-4 decision turns on the `record_on_disk` out-of-band observer at `tests/test_journal_conformance.py:117-128`, which I verified with the F1 mutant — a mechanism `BA-B14` explicitly says did not exist in the prior round, so the quoted 4 is not the evidence my 4 rests on. Flagged rather than concealed, per the round's rule; whether a packet whose subject narrates prior scores at its judge is still a blind packet is a question for whoever assembled it, not for me.

**What I ran, and what it changed.** Everything ran against a copy under `…/scratchpad/SV-04/judge-LG-p2/`. The packet was never edited in place; `git status --porcelain` on `blind/artifact_LG` is clean. Fourteen faults were seeded into throwaway copies, never into the tree.

**What I rejected.**
- I rejected the literal reading of "score the LOWEST anchor the artifact fully satisfies" under D2, which would force a 0 because no complexity metric exists. Reasoning in the D2 rationale; a second judge could legitimately land elsewhere and this is the likeliest place for us to differ.
- I rejected counting the surviving guard-order mutant as a missed fault. It looked like the best finding of the round until I enumerated the inputs and found it unobservable — an equivalent mutant. Had I reported it, this card would have claimed a bug-detection hole that does not exist.
- I rejected the packet's docstrings as evidence for anything, including the ones I ultimately agreed with. Everything cited above as fact was re-derived by running or by counting.
- I rejected `README.md:76`'s "four lines" as accurate; recorded in N-D5 as the packet's one inaccurate claim.
- Not read, per instruction: `references/eval_scorecard.md`, every other directory under `specs/results/scorecards/`, any `artifact_*` directory other than mine, `examples/validation/ab/` outside my packet, `specs/desired_program_model/`, any `*-EPIC.md`, and git history. The `git rev-parse --short HEAD` for the `commit` field was the only git command run.
