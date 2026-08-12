# Scorecard — toolchain_removal, artifact `LG`, judge pass 1

`run_id`: `20260812-sv04conf-LG-p1` · scorecard_version 5 · rubric `references/eval_scorecard.md` digest `sha256:24b2c599901d7ae0` · served `sha256:2d7d4a0506d9b259`

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

- Copied the packet to `/private/tmp/.../scratchpad/SV-04/judge-LG-p1/{base,mut}` and mutated only the copy. The packet under `specs/results/scorecards/.../blind/artifact_LG` was never written to.
- Green control, three pointings: `QUOTA_LEDGER_DIR=<d>/reference_ports QUOTA_LEDGER_IMPL=quota_ledger pytest tests/test_behavior.py` → **28 passed**; `QUOTA_LEDGER_IMPL=quota_ledger_fake` → **28 passed**; `QUOTA_LEDGER_PORTS_DIR=<d>/reference_ports pytest tests/test_journal_conformance.py` → **14 passed**.
- Determinism: behavioural (real) and conformance suites re-run 3× each — identical pass counts, 0.07–0.10 s every time.
- **JF-1**, inside the fake adapter: `InMemoryJournal.lines()` returns the record reversed. **KILLED** — behaviour(fake) 5 failed/23 passed, conformance 1 failed/13 passed; behaviour(real) 28 passed (blind, as expected).
- **JF-2**, inside the real adapter: `FileJournal` rewritten to hold a plain list, every filesystem call removed. **SURVIVED** both behavioural wirings 28/28 and 28/28; **KILLED** by conformance, 5 failed/9 passed.
- **JF-3**, inside *both* adapters: `append()` silently drops a line already present in the record. **SURVIVED EVERYTHING** — 28 real, 28 fake, 14 conformance.
- **JF-4**, in the domain: `release()` appends a `RELEASE` line. **KILLED** — 1 failed in each behavioural wiring.
- **JF-5**, in the domain: `ReservationBook` keeps a private `_shadow` list, appends to it, returns it from `ledger_lines()`, and never calls the port. **SURVIVED EVERYTHING** — 28 / 28 / 14 — while the ledger file stayed empty.
- **D2 probe** (a derivation, not a fault): deleted `_available` and derived `available()` from `_quota − outstanding − _committed`, removing three write sites. 28 / 28 / 14 passed.
- **Runtime call trace** (not a fault): wrapped a spy around the journal handed to `ReservationBook`, drove `reserve`/`commit`/`close_tenant` against both adapters and recorded the exact call sequence through the port; parsed `domain.py`'s AST for its complete `ImportFrom` set.
- **Native defect probe** (no mutation): allocated 12 live reservations and compared `outstanding_ids()` to allocation order.

## Your scores

### D2 — complexity

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:101-108` — six fields, one constructor, no god-state
- `reference_ports/domain.py:129-173` — four commands, each a flat guard sequence then a two- or three-statement effect
- `reference_ports/domain.py:103`, `reference_ports/domain.py:140`, `reference_ports/domain.py:161` — the three write sites of the one redundant field
- `reference_ports/journal_file.py:32-38`, `reference_ports/journal_memory.py:39-43` — the adapters, 9 and 4 lines of code
- `reference_ports/quota_ledger.py:24-25`, `reference_ports/quota_ledger_fake.py:37-38` — the composition points, one statement each

**Refuses to claim** (required and non-null for a score of 3): _n/a — not scored at the top of its scale._

**Rationale:**

Proportional, with one measured redundancy that is not enough to sink it and no measured simplification to lift it.

*Proportion.* ~123 lines of code across five files by my AST count (domain 82, `journal_file` 9, `journal_memory` 4, `quota_ledger` 15, `quota_ledger_fake` 13). One class holds six fields (`reference_ports/domain.py:101-108`) to serve four commands and five queries, each command a flat guard sequence in FEATURE.md's declared rejection order followed by a small effect. No god-state and no variable written from everywhere: the widest-written field is `_available`, written at exactly three sites (`:103`, `:140`, `:161`) and read at two.

*The redundancy, measured rather than eyeballed.* The rubric asks whether one fact is stored twice, so I deleted `_available` in a copy and derived it as `_quota[tenant] − held − _committed[tenant]`. All 28 behavioural cases passed through both wirings and all 14 conformance cases passed. `_available` **is** a stored copy of a fact the object already holds, kept in agreement by hand at three write sites. I did not drop below 2 for it: three write sites in a six-field object is not "written from everywhere", `FEATURE.md:26` makes `available(tenant)` an observable query so a stored field is a defensible reading of the requirement, and the artifact declares the choice openly (`reference_ports/README.md:13-16`).

*Why not 3.* Anchor 3 needs a simplification whose before **and** after figures are both recorded. Nothing in scope records either: `mechanical.json`'s complexity block was empty when I was served it, the packet carries no complexity descriptor, and the only "before" the artifact names is `../reference/quota_ledger.py`, which is outside my read list — so I could not diff the two trees the way the read_first asks and substituted the derivation probe above (see Disclosures).

*Why not 0 or 1.* The read_first says explicitly that where no measured descriptor exists that is not a gap in the evidence, so the absence of figures does not force 0 or 1; the design itself is what anchor 2 asks about.

*Prose.* The docstrings in this tree are unusually persuasive and argue their own quality at length (`reference_ports/journal_memory.py:7-27` spends twenty lines on why the file matters). I scored the six fields and the three write sites, not the argument. The writing did tempt me and I am recording that it did.

### D3 — modularity

**Score:** **4**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:20-23` — the complete `ImportFrom` set: `__future__`, `dataclasses`, `typing`
- `reference_ports/domain.py:38-58` — the `LedgerJournal` driven port, declared in the domain's vocabulary
- `reference_ports/domain.py:125`, `reference_ports/domain.py:150-153`, `reference_ports/domain.py:172` — the only three call sites through the port
- `reference_ports/quota_ledger.py:24-25` and `reference_ports/quota_ledger_fake.py:37-38` — the swap, executed rather than asserted
- `tests/test_behavior.py:34-36` — one suite, two composition points, selected by env var
- `tests/test_journal_conformance.py:117-128` — `record_on_disk`, the out-of-band observer that never calls `lines()`
- `tests/test_journal_conformance.py:181-210` — the durable-only cases, every assertion made through it

**Refuses to claim** (required and non-null for a score of 4):

The artifact refuses to claim its adapter conformance suite is complete, and names three blind classes at `tests/test_journal_conformance.py:39-52`: nothing about `ReservationBook`, because no case constructs a `QuotaLedger`; nothing about concurrency or crash-atomicity, because every case is single-process; and no record older than one object, because `journal_file.py:30` truncates on construction — a limit it pins in an executable case (`tests/test_journal_conformance.py:235-250`) rather than papering over, explicitly downgrading the port's own "outlives the run" to "the *file* outlives the object, not the adapter". The tree also refuses the generalisation the score would otherwise invite: `reference_ports/README.md:68-77` states it does not show that an arm would produce this shape, that it is *n* = 1, and that the four-line fake is evidence the region was cheap to reach and **not** evidence anybody would have reached it.

**Rationale:**

Anchor 4's literal condition is met, I measured it rather than read it, and the caveat's demotion condition does not apply.

*Anchor 3, on runtime evidence not imports.* `domain.py` declares the driven port as a `Protocol` in its own vocabulary (`:38-58`) and imports only `__future__`, `dataclasses` and `typing` — I parsed its AST rather than trusting the docstring, and those three are the complete `ImportFrom` set. Because import topology is not modularity, I wrapped the journal in a spy and drove the domain: `ReservationBook` reaches the durable side at exactly three call sites and nowhere else — `append` from `commit` (`:150-153`), `append` from `close_tenant` (`:172`), `lines` from `ledger_lines` (`:125`) — and the spy recorded `[('append','COMMIT acme 3 3'), ('append','CLOSE acme 3')]` identically whether the object behind it was `FileJournal` or `InMemoryJournal`. The domain holds no path, no handle, and no import of either adapter.

*The specific swap.* `quota_ledger.py:25` `super().__init__(quotas, FileJournal(ledger_path))` becomes `quota_ledger_fake.py:38` `super().__init__(quotas, InMemoryJournal())`, and no file under `reference_ports/` other than the composition point differs.

*Anchor 4, measured.* One suite file, selected by env var at `tests/test_behavior.py:34-36`, gave **28 passed** against `QUOTA_LEDGER_IMPL=quota_ledger` and **28 passed** against `QUOTA_LEDGER_IMPL=quota_ledger_fake` — same cases, same domain, both sides of the port.

*Why the caveat does not demote this to 3.* The caveat says take 3 if the only observer of the effect the port exists for is the adapter that wrote it. Here it is not. `record_on_disk` (`tests/test_journal_conformance.py:117-128`) opens the declared path with `Path.read_text` and never calls `lines()`, and `TestDurableRecord` makes every assertion through it. I checked that this discriminates rather than decorates: JF-2 — `FileJournal` with every filesystem call removed — passed 28/28 through **both** behavioural wirings and failed 5 conformance cases. I also confirmed directly that the real wiring puts bytes on disk during the ordinary flow (`'COMMIT acme 3 3\n'`) while the fake wiring creates no file at all, so the pair is a real one and a fake one, not two fakes.

*Prose.* This tree argues for its own modularity harder than any artifact I have scored, and none of that argument is in the score; the AST parse, the spy trace, the two 28-pass runs and the mutant the conformance suite killed five ways are.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `reference_ports/domain.py:55`, `reference_ports/domain.py:122`
- `reference_ports/quota_ledger_fake.py:37-38`
- `tests/test_journal_conformance.py:117-128`, `tests/test_journal_conformance.py:149-153`, `tests/test_journal_conformance.py:41-43`
- `tests/test_behavior.py:240-242`
- `FEATURE.md:29`, `FEATURE.md:93-96`

**Note:**

I seeded five faults and ran all three pointings against each.

*What they caught.* **JF-4**, a domain fault writing a `RELEASE` line the feature forbids (`FEATURE.md:72`), died in both behavioural wirings. **JF-1**, a fault inside the *fake* adapter, died five ways under the fake wiring and once under `TestPortContract` — and this is the packet's real contribution, because the fake wiring at `reference_ports/quota_ledger_fake.py:37-38` is what gives a fault in `journal_memory.py` anywhere to be seen. **JF-2**, the real adapter rewritten to touch no filesystem, survived 28/28 in *both* behavioural wirings and died only against `tests/test_journal_conformance.py:181-210`, whose reads go through `record_on_disk` and never through `lines()`. The conformance file's central claim about itself is true and I verified it rather than accepting it.

*What they demonstrably missed — two classes.*

1. **Port-contract idempotence.** JF-3 made `append()` in both adapters silently drop a line already present; 28 + 28 + 14 = 70 case-executions all passed. `reference_ports/domain.py:55` declares "Add one line to the end of the record", and nothing anywhere appends the same line twice — `TestPortContract`'s three-line case (`tests/test_journal_conformance.py:149-153`) uses three distinct lines, and the domain can never emit a duplicate because its running total strictly increases, which is exactly why the adapter-level clause needs its own case and does not have one.
2. **The domain bypassing the port.** JF-5 gave `ReservationBook` a private shadow list, appended to that instead of calling the port, and returned it from `ledger_lines()`; 70/70 passed while the ledger file stayed empty. `FEATURE.md:16-17` requires a durable append-only ledger *file* and R2 (`FEATURE.md:93-96`) requires the durable ledger to agree with memory; JF-5 breaks both and every instrument in the packet says green. This is the hole the artifact filed as `RM-05-DF-05` on the adapter side, standing open on the domain side — and `tests/test_journal_conformance.py:41-43` asserts it is covered by `test_behavior.py` when I measured that it is not.

*One defect I did not seed, present as shipped.* `reference_ports/domain.py:122` returns `sorted(self._outstanding)`, a lexicographic sort of string ids, so with twelve live reservations `outstanding_ids()` returns `['r1','r10','r11','r12','r2',…]` where `FEATURE.md:29` asks for the live ids "ascending". `tests/test_behavior.py` never holds more than three reservations at once (`:240-242` is the widest), so the suite cannot reach the tenth id and the defect is invisible to all 28 cases.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `FEATURE.md:24-30`, `FEATURE.md:89-104`
- `reference_ports/domain.py:112-125`, `reference_ports/domain.py:129-173`
- `reference_ports/README.md:35-38`
- `tests/test_behavior.py:46-54`, `tests/test_behavior.py:239-281`
- `tests/test_journal_conformance.py:41-43`

**Note:**

**The baseline the artifact names is not in my packet, and that is the honest answer to half of this.** `reference_ports/README.md:35-38` and `reference_ports/domain.py:8-9` claim this tree is `../reference/quota_ledger.py`'s behaviour "statement for statement". `../reference/` is outside the artifact directory I was told is my whole read list, so I did not open it and I cannot confirm or deny that claim. It stands unverified on this card.

*What I could enumerate and did.* `FEATURE.md` is a written baseline in its own right, and I enumerated it clause by clause against the code and against execution. Five queries (`FEATURE.md:24-30`) all present and correct at `reference_ports/domain.py:112-125`, with the one exception in N-D1 — `outstanding_ids()` is not ascending past `r9`. Four commands with their rejection orders (`FEATURE.md:38-88`) implemented in the declared order at `reference_ports/domain.py:129-173`, each rejection path exercised. The five rules R1–R5 (`FEATURE.md:89-104`) each have at least one case (`tests/test_behavior.py:239-281`), and R4 is checked structurally by comparing a full observable snapshot across every rejection (`tests/test_behavior.py:46-54`). All 28 cases pass through the real wiring and all 28 through the fake, three runs each, deterministic.

*Where the enumeration fails as a preservation argument.* R2's "durable ledger" is only ever read back through `ledger_lines()` → `LedgerJournal.lines()` in `test_behavior.py`, which asks the writer whether it wrote. JF-5 keeps all 28 answers correct with nothing durable written at all; JF-2 keeps all 28 correct with no filesystem touched. So the behavioural suite preserves the *observable* behaviour of `FEATURE.md` and does not preserve its *durability* clause. `tests/test_journal_conformance.py` closes exactly one of those two holes (the adapter one) and states, wrongly, that `test_behavior.py` closes the other.

### N-D5 — honesty

**Citations** (`file:line`):

- `reference_ports/README.md:66`, `reference_ports/README.md:68-77`
- `reference_ports/quota_ledger_fake.py:16-22`
- `tests/test_journal_conformance.py:19-21`, `:39-52`, `:41-43`, `:235-250`
- `tests/test_behavior.py:8-12`
- `reference_ports/domain.py:122`

**Note:**

**It refuses a great deal, and one of its refusals is itself false.**

*The refusals, each of which I checked rather than read.* `reference_ports/README.md:66` — "Nothing here gates, refuses, or reports a verdict. It is a fixture": true; no module in the tree raises, logs or asserts anything about quality. `reference_ports/README.md:68-77` refuses the three generalisations a reader would most want: that an arm would produce this shape, that *n* > 1, and that the four-line fake is evidence anybody would have reached the region. `reference_ports/quota_ledger_fake.py:16-22` refuses to assert parity between the two wirings and gives the correct reason — a parity test passes when the domain is wrong in both — and the code matches: no case anywhere compares wiring against wiring. `tests/test_journal_conformance.py:39-52` names three things it cannot see and pins the third in an executable case (`:235-250`) instead of a sentence. `tests/test_behavior.py:8-12` refuses to call itself adversarial and says passing it is a floor. `tests/test_journal_conformance.py:59-62` refuses the silent-skip failure mode by making a tree with no adapters fail at collection. I re-derived one substantive self-accusation: `:19-21` claims a `FileJournal` with every filesystem call removed still passes 28 of 28 shared cases; I built that mutant and it passed 28/28 through both wirings and failed 5 conformance cases.

*The false certification.* `tests/test_journal_conformance.py:41-43` states "A domain that stopped calling the port entirely is invisible here and visible to `test_behavior.py`; the two suites are complements." I made exactly that change — `ReservationBook` appends to a private shadow list, `ledger_lines()` returns it, the port is never called — and `test_behavior.py` passed 28/28 in the real wiring and 28/28 in the fake while the ledger file stayed empty. This is not a soft overstatement; it is the one sentence telling a reader the pair of suites has no residual hole, and it is wrong.

*And one thing not named at all.* Nothing in the packet acknowledges that the port's own "add one line to the end" clause has no case that could fail (JF-3 survived all 70 executions), nor that `reference_ports/domain.py:122`'s lexicographic sort breaks `FEATURE.md:29`'s "ascending" past nine live reservations. A tree this careful about naming its blind spots did not see these two.

## Verdict

Ports and adapters in fact, verified at runtime and not by imports (D3 = 4), with proportional structure and one measured stored-twice field (D2 = 2) — but the packet's own honesty claim is false where it matters most: I made the domain stop calling the port entirely, keeping a private shadow list, and all 28 behavioural cases passed through **both** wirings and all 14 conformance cases passed, contradicting `tests/test_journal_conformance.py:41-43`; the two suites are not the complements they say they are, and the hole the artifact filed as `RM-05-DF-05` on the adapter side is open on the domain side and unfiled.

## Disclosures

**A leak I could not avoid, because the leaking files are on my read list.** The artifact packet itself carries prior-round conclusions about the dimension I am the instrument for:

- `reference_ports/README.md:3-4` and `reference_ports/domain.py:3` state "THIS IS NOT AN ARM", so I know artifact `LG` is a reference tree rather than an arm output.
- `reference_ports/README.md:20-23` and `reference_ports/quota_ledger_fake.py:9-15` quote finding `BA-B14` verbatim, including the words "the fake that earned arm B its D3 = 4" — a prior D3 score, its value, and the reason it was awarded.
- `reference_ports/README.md:6` names arms A, B and C; `tests/test_behavior.py:3` and `reference_ports/README.md:37` reference arm A and arm B by name.
- `tests/test_journal_conformance.py:11` cites a finding id `RM-05-DF-05` from this epic.

I record that the `BA-B14` quotation is an anchor toward D3 = 4 that I read before scoring. I reached 4 from the spy call trace, the two 28-pass runs, and the JF-2 mutant the conformance suite killed five ways; a reader who wants to discount the anchor should discount those four measurements, not the sentence.

**What I did not read.** `references/eval_scorecard.md`; any other directory under `specs/results/scorecards/`, including `UNBLINDING.md`, any `PREDICTIONS*`, `RESULT*`, `HARVEST*` or `FINDINGS*` file; any `*-EPIC.md`; `git log` or any git history; `specs/desired_program_model/` or any findings file; `examples/validation/ab/` outside this packet; any other `artifact_*` directory. I ran `git rev-parse --short HEAD` only, for the `commit` field.

**What I ran that changed a tree.** Nothing in the repository. Every mutation was applied to a copy under `/private/tmp/.../scratchpad/SV-04/judge-LG-p1/mut`, which I deleted afterwards; the packet was read-only throughout. The only files I wrote in the repository are the three in this card directory.

**What I rejected.**

- *I rejected D3 = 3.* The caveat's demotion clause ("the real adapter does nothing real / the only observer is the writer") is the obvious reason to hold this at 3, and it does not apply: `record_on_disk` observes the file out of band, and I proved it discriminates by removing every filesystem call from `FileJournal` and watching 56 behavioural passes coexist with 5 conformance failures.
- *I rejected D2 = 1.* Tempting because no complexity figure is shipped and `mechanical.json` arrived with an empty complexity block — but the read_first says in terms that a missing descriptor is not a gap in the evidence, so anchor 1 would be scoring the packaging rather than the design.
- *I rejected D2 = 3.* The tree is a restructuring of a baseline I am not allowed to read, with no before/after figures recorded anywhere in scope. Anchor 3 asks for both numbers and I have neither.
- *I rejected lowering D3 for JF-5.* The domain bypassing the port undetected is a fact about the *instruments*, not about whether the code is ports-and-adapters; I verified the real code does call the port at runtime, and put the finding in N-D1, N-D4 and N-D5 where it belongs.
- **I could not perform the diff the D2 read_first asks for.** It says "diff the two trees yourself"; only one tree is in my packet and `../reference/` is outside my read list. I substituted an executed derivation — deleting `_available` and computing it from the fields already held — which answers the same question ("is one fact stored twice") by measurement rather than by comparison. A reader should treat my D2 as answered by that substitute and not by the diff that was asked for.
