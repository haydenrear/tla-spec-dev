# Scorecard — toolchain_removal, artifact `GL`, judge pass 1

`run_id`: `20260812-sv04conf-GL-p1` · scorecard_version 5 · rubric `references/eval_scorecard.md` digest `sha256:24b2c599901d7ae0` · served `sha256:2d7d4a0506d9b259`

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

- Copied the packet to `/private/tmp/.../SV-04/judge-GL-p1/{base,work}` and mutated only the copy. `diff -r base <packet>` at the end: identical. `git status --porcelain` in the repo: clean of any change of mine.
- Control, both wirings: `QUOTA_LEDGER_DIR=<work>/reference_ports QUOTA_LEDGER_IMPL=quota_ledger uv run --with pytest python -m pytest <work>/tests/test_behavior.py -q -p no:cacheprovider` → **28 passed**; same with `QUOTA_LEDGER_IMPL=quota_ledger_fake` → **28 passed**. Three repeats each, identical.
- **J1** — fault inside the FAKE adapter: `InMemoryJournal.append` → `self._lines.insert(0, line)`. real 28 passed · fake **5 failed** / 23 passed.
- **J2** — same semantic inside the REAL adapter: `FileJournal.lines` → `reversed(...)`. real **5 failed** / 23 passed · fake 28 passed.
- **J3** — round-trip-symmetric corruption in the REAL adapter: `append` writes `"ZZ|" + line`, `lines()` returns `entry[3:]`. **Both wirings 28 passed** while the file on disk holds `ZZ|COMMIT acme 3 3`. This run decided D3 = 3 rather than 4.
- **J4** — DOMAIN: `reserve`'s guard 3 and guard 4 swapped (`quota_exceeded` tested before `amount_not_positive`). **Both wirings 28 passed.**
- **J5** — DOMAIN: the `COMMIT` line's running total replaced by the reservation amount. real **2 failed** / 26 · fake **2 failed** / 26.
- Unseeded probe, no mutation: built `QuotaLedger({"acme": 100}, path)`, made 12 reservations, printed `outstanding_ids()` → `['r1','r10','r11','r12','r2',…]`.

## Your scores

### D2 — complexity

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:101-108` — the whole of the state, six fields, one constructor
- `reference_ports/domain.py:140`, `reference_ports/domain.py:161` — the two hand-kept write sites of `_available`
- `reference_ports/domain.py:144-154` — `_committed` has one write site and renders the ledger line from it in the same statement
- `reference_ports/quota_ledger.py:24-25`, `reference_ports/quota_ledger_fake.py:37-38` — the composition points are one line of behavior each
- `FEATURE.md:91-92` — R1, which is what makes `_available` derivable rather than necessary

**Refuses to claim** (required and non-null for a score of 3):

It claims no complexity figure at all — no descriptor, no before/after, no argument from a number — and `reference_ports/README.md:68-77` refuses the adjacent claims (n = 1, tree and catalogue share an author, "it does not show that an **arm** will produce this shape"). My own limit: the flat tree it says it matches is outside my packet, so I diffed only within the declared scope.

**Rationale:**

Proportional, and there is no third rung's worth of evidence. Six fields for five queries and four commands; each command is a flat guard chain with one effect block (`reference_ports/domain.py:129-173`); no shared mutator, no dispatch table, no god object. On the "one fact stored twice" test the honest answer is *one, bounded*: `_available` is derivable from quota − outstanding − committed — that is literally R1 — and is instead stored and maintained by hand at exactly two write sites (`:140`, `:161`), read at two. Two hand-kept write sites is not a variable written from everywhere. The near-miss is not one: `_committed` has a single write site and the ledger's running total is rendered from it rather than accumulated a second time, so R2's agreement is structural. Anchor 3 is unreachable — nothing in the packet records a simplification with a before figure and an after figure, and there is no complexity descriptor in scope at all (per the read-first that is not a gap, but it also cannot supply the two figures anchor 3 names). Torn between 2 and 3, I take the lower. **Rule 4, stated because it applied:** the docstrings here (`reference_ports/README.md:57-64`, `reference_ports/journal_memory.py:7-27`) argue their own design better than most reports do; I discounted them entirely and this score would be identical with every docstring deleted.

### D3 — modularity

**Score:** **3**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:20-23` — the domain imports `dataclasses` and `typing` and nothing else: no `Path`, no `open`, no `os`
- `reference_ports/domain.py:38-58` — the driven port, declared in the domain in its own vocabulary
- `reference_ports/domain.py:150-153`, `reference_ports/domain.py:172` — every cross-boundary write, both through `self._journal.append`
- `reference_ports/domain.py:124-125` — the read back, through the same object
- `reference_ports/quota_ledger.py:18`,`:25` vs `reference_ports/quota_ledger_fake.py:31`,`:38` — **the specific swap**: `FileJournal(ledger_path)` → `InMemoryJournal()`, one import line and one constructor line, no domain file touched
- `reference_ports/journal_file.py:32-38` — the sole observer of the durable file
- `tests/test_behavior.py:41-54` — `tmp_path` goes in at `:43` and is never read back; `snapshot` observes the durable side only via `book.ledger_lines()`

**Refuses to claim** (required and non-null for a score of 4):

`reference_ports/quota_ledger_fake.py:14-22` refuses, in its own file, the false certificate this design invites — a parity assertion between the two wirings — and gives the right reason (two wirings of one domain agree when the domain is wrong). `reference_ports/README.md:66` refuses to gate or report a verdict; `:70-77` refuses to claim any arm would produce this shape. What it does **not** refuse, and what I had to establish myself, is that no case observes the ledger file independently of the adapter that wrote it.

**Rationale:**

Anchor 3 is fully satisfied and anchor 4's caveat is exactly what this tree trips. Because import topology is not modularity, I checked what *calls* what by mutation: a fault inside the fake fails 5/28 under `quota_ledger_fake` and 0/28 under `quota_ledger`; the mirror fault inside the real adapter fails 5/28 under `quota_ledger` and 0/28 under `quota_ledger_fake`. That is runtime evidence that the domain's `append` lands in whichever adapter the composition point supplied, and that these are two genuinely different execution paths — not two fakes wearing one name. Anchor 4's literal words are met (28 identical cases green through a real adapter and a fake). I take 3 anyway, on the caveat's own condition: **the only observer of the effect the port exists for is the adapter that wrote it.** `ledger_lines()` returns through the same journal object (`domain.py:124-125` → `journal_file.py:36-38`) and no case anywhere opens the ledger path. That is not a technicality — I made `FileJournal` write `ZZ|COMMIT acme 3 3` to disk and strip the prefix back off on read, and all 28 cases pass through both wirings. The real adapter's realness — that there is a file, in that format, outliving the object — is asserted by the adapter and checked by nobody. Rule 4: the tree argues for its own 4 in prose (`README.md:57-64`); the J3 run is the reason I did not give it one.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `tests/test_behavior.py:41-54`, `:75-84`, `:239-249`
- `reference_ports/domain.py:122`, `:124-125`, `:134-137`
- `reference_ports/journal_file.py:32-38`, `reference_ports/journal_memory.py:39-43`
- `FEATURE.md:40-45`, `FEATURE.md:49-50`

**Note:**

**Caught:** an ordering fault inside the in-memory adapter (J1) dies 5/28 — but only under the fake composition point, 0/28 under the real one; the mirror fault inside the file adapter (J2) dies 5/28 under the real wiring and 0/28 under the fake; a domain fault in the running total (J5) dies 2/28 under both. So the cases catch value, order and cross-tenant accounting faults on whichever side of the port is wired in, and the pair of composition points is load-bearing rather than decorative: without `quota_ledger_fake.py:37-38` the whole of J1 is invisible.

**Missed, three classes.** (1) **Round-trip-symmetric adapter faults.** J3: `append` writes `"ZZ|" + line`, `lines()` strips it; 28/28 green through *both* wirings while the durable file holds a format `FEATURE.md:57-63` does not describe. No test opens the ledger path — `tmp_path` goes in at `tests/test_behavior.py:43` and every durable assertion returns through `book.ledger_lines()`. Any adapter defect that is its own inverse is unreachable through any wiring. (2) **Guard order.** J4 swaps `reserve`'s `amount_not_positive` and `quota_exceeded` guards (`domain.py:134-137`); 28/28 green both wirings, because the suite's rejection inputs (`tests/test_behavior.py:75-84`) never make two guards fire at once — amounts 0 and −2 are below every balance and 11 is positive. `FEATURE.md:40-45` states an **order**; the cases test a mapping. (3) **An unseeded defect**, found by probing rather than mutating: `domain.py:122` returns `sorted(self._outstanding)`, a *string* sort, so with twelve live reservations `outstanding_ids()` is `['r1','r10','r11','r12','r2',…]` and `FEATURE.md:29`/`:49-50`'s "ascending" is violated from the tenth reservation onward. The suite's largest quota is 10 and its longest sequence holds three, so the case that would show this is not in the file.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `FEATURE.md:24-30`, `:38-50`, `:52-72`, `:76-104`
- `reference_ports/domain.py:8-11`, `:112-125`, `:122`
- `reference_ports/README.md:39-45`
- `tests/test_behavior.py:46-54`, `:239-281`

**Note:**

Two candidate baselines; only one is in my packet. The baseline the artifact names — `../reference/quota_ledger.py`, which `domain.py:8-11` and `README.md:39-45` say this tree matches "statement for statement" — is **not** in my read scope, so I could not diff it and I record that claim as **unverified**, neither confirmed nor refuted. The baseline I could enumerate is `FEATURE.md`'s observable contract, checked item by item by running the shared suite through both wirings (28/28 each, three repeats, identical): the five queries (`FEATURE.md:24-30` vs `domain.py:112-125`); `reserve`'s four reasons and accept effects (`:38-50` vs `domain.py:129-142`); `commit`'s single line, its committed increase and its deliberate non-return of availability (`:52-66` vs `domain.py:144-154`, asserted at `tests/test_behavior.py:112-119`); `release` writing nothing (`:69-72` vs `domain.py:156-162`); `close`'s three-guard order and single `CLOSE` line (`:76-88` vs `domain.py:164-173`); R1 (`tests/test_behavior.py:239-255`), R2 (`:258-267`), R3 (`:186-233`), R4 via full-snapshot comparison (`:46-54`, `:85-91`), R5 (`:270-281`). **One item does not hold as written:** the ids-ascending clause (`FEATURE.md:29`, `:49-50`) fails from ten live reservations onward at `domain.py:122` — demonstrated, not inferred. Everything else holds under both wirings alike.

### N-D5 — honesty

**Citations** (`file:line`):

- `reference_ports/README.md:57-64`, `:66`, `:70-77`
- `reference_ports/quota_ledger_fake.py:14-22`
- `reference_ports/journal_file.py:8-13`, `:36-38`
- `reference_ports/domain.py:96-99`, `:124-125`
- `tests/test_behavior.py:41-54`

**Note:**

It refuses in several places and they are real refusals, not hedges. `README.md:66` — "Nothing here gates, refuses, or reports a verdict. It is a fixture." `README.md:70-77` gives up three claims it would have been easy to make: that an arm would produce this shape, that n = 1 with tree and catalogue sharing an author is anything but the bias already declared, and — sharpest — that a four-line fake being *cheap* is evidence anybody would have written it ("Nobody did, for a whole epic, and that is the measured fact"). `quota_ledger_fake.py:14-22` refuses the specific false certificate this design invites, a parity assertion between the wirings, with the correct reason. `domain.py:96-99` declines to know which journal it holds.

**Where it is not honest enough is one sentence.** `README.md:57-64` says running the identical suite through both wirings "is what gives a fault in either adapter somewhere to be seen", and `journal_file.py:8-13` says a fault there "is reachable by anything that runs the shared suite through the real wiring". Both are true only of faults visible through the adapter's own read path. J3 is a fault in the real adapter that both wirings pass, because nothing but `journal_file.py:36-38` ever observes the file. The tree names the blind region the port created on the **fake** side precisely, and does not name the residual blind region on the **real** side. That is an unnamed limit, not a false certificate — it never claims exhaustiveness — but it is the thing a reader of this README would not know to look for.

## Verdict

A real port with a real swap — D2 **2**, D3 **3** — and the finding worth carrying is that the durable file is never read by anything except the adapter that wrote it: I corrupted the on-disk format to `ZZ|COMMIT acme 3 3` and all 28 cases stayed green through both wirings, so the second composition point genuinely closes the fake's blind region (an in-memory-adapter fault kills 5/28 under the fake wiring and 0/28 under the real one) while leaving a round-trip-symmetric blind region on the real side that no wiring reaches.

## Disclosures

**Leak, disclosed, and it came from inside the artifact.** The packet's own prose carries prior results about the dimension I am the instrument for. `reference_ports/README.md:14-24` quotes `specs/results/scorecards/hexagonal-prompting/FINDINGS.md` on `BA-B14`, including the sentence "the fake that earned **arm B its D3 = 4** is verified by nothing outside arm B's own tests", and `reference_ports/journal_memory.py:7-27` repeats it. So I know a prior round's D3 score for some other artifact, that a fault class in exactly this file survived every instrument there, and that this tree declares itself **not an arm** (`README.md:3`). I read those lines before I could know what they were; I did not go looking further. Effect on my scoring: the leak points *toward* 4 on D3, and I scored 3 on the strength of my own J3 run. Nothing in it moved D2.

**Second, smaller leak.** Running the required checker meant reading `examples/validation/scorecards/score_tools.py`; a source comment near its total-check states that "D2 has taken one value on every card ever written about `ab_quota_ledger`". I saw that after both scores were fixed and written to disk, and my D2 rationale is argued from `domain.py`'s field list and write sites, not from it.

**What I ran that changed a tree:** nothing in the repository. All five mutants and the probe ran against a copy under my scratch directory; `diff -r` against the packet is empty and `git status --porcelain` shows no change of mine.

**Rejected.** (a) D3 = 4, whose literal words are satisfied — rejected on the caveat, with J3 as the evidence rather than as an argument. (b) D2 = 3 on the grounds that the tree is visibly simple — rejected because anchor 3 asks for two figures and this packet records none. (c) D2 = 1 on the grounds that no complexity was measured — rejected because the read-first says an absent descriptor is not a gap, and the anchor 2 text is about the design, not about the reporting. (d) Reading `../reference/` to check the "statement for statement" claim — refused as outside the packet, and recorded as unverified in N-D4 instead.
