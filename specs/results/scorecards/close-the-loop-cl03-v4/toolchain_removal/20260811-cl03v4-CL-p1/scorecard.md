# Scorecard — toolchain_removal, artifact `CL`, judge pass 1

`run_id`: `20260811-cl03v4-CL-p1` · scorecard_version 4 · rubric `examples/validation/scorecards/rubric_v4_frozen.md` digest `sha256:497c16ca85adeb4a` · served `sha256:a213a36770ccab09`

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

- Copied the artifact to a scratch tree; **the artifact directory was never modified**. Everything below ran against the copy.
- **Control.** `tests/test_behavior.py` under both wirings — `QUOTA_LEDGER_IMPL=quota_ledger` 28/28 pass, `QUOTA_LEDGER_IMPL=quota_ledger_fake` 28/28 pass.
- **6 seeded faults, each run against BOTH wirings (12 runs).**

  | fault | where | killed, real wiring | killed, fake wiring |
  |---|---|---|---|
  | F1 — `lines()` order reversed | `journal_file.py:38` (real adapter) | **5 / 28** | 0 / 28 |
  | F2 — `lines()` order reversed (same semantic) | `journal_memory.py:43` (fake adapter) | 0 / 28 | **5 / 28** |
  | F3 — `outstanding_ids()` order reversed | `domain.py:122` | 0 / 28 | 0 / 28 |
  | F5a — blank-line filter deleted | `journal_file.py:38` | 0 / 28 | 0 / 28 |
  | F5b — blank-line filter deleted | `journal_memory.py:43` | 0 / 28 | 0 / 28 |
  | F6 — no-op write to `_available` | `domain.py:149` | 0 / 28 | 0 / 28 |

  F6 is a deliberate equivalent-mutant control: it confirms that survival alone is not a fault signal for this harness.
- **Runtime call-graph probe, both wirings.** `sys.setprofile` capturing every cross-module call frame among `domain` / `journal_file` / `journal_memory` / `quota_ledger` / `quota_ledger_fake`, plus monkeypatched `pathlib.Path.open/read_text/write_text`. Result: the domain's only outbound non-domain calls are the port's two methods; the real wiring makes **8** filesystem calls, the fake wiring makes **0**.
- **Independent 12-check conformance probe** written from `FEATURE.md` rather than from the shipped suite, run against both wirings: rejection ORDERING for `reserve` and `close_tenant`, id non-reuse across a release, ascending ids with 12 live reservations, R3 single `CLOSE` line, R4 no durable write across five distinct rejections, R5 prefix-monotonic ledger, and durability read directly off the path after dropping the object. **Real wiring 11/12, fake wiring 10/12** — the shared failure is ascending ids; the fake's extra failure is durability.
- **One simplification experiment of my own.** Deleted the stored `_available` field and derived `available()` from `_quota`, `_outstanding` and `_committed`. All 28 cases still pass under both wirings — which is how I established the field is redundant instead of inferring it.
- **Did NOT run or read:** any file under `specs/results/scorecards/` other than my own two card files, `references/eval_scorecard.md`, any `*-EPIC.md`, the flat baseline `../reference/quota_ledger.py`, or `check_catalogue.py`.

## Your scores

### D2 — complexity

**Score:** **2**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:101-108` — the whole of the domain's state: five fields for four commands and five queries
- `reference_ports/domain.py:103`, `:140`, `:161` — `_available` stored, then hand-maintained at exactly two write sites
- `reference_ports/domain.py:112-125` — the queries
- `reference_ports/journal_file.py:38` and `reference_ports/journal_memory.py:43` — the "no blanks" rule implemented independently in both adapters
- `reference_ports/quota_ledger.py:24-36` and `reference_ports/quota_ledger_fake.py:37-49` — twin composition points differing in one identifier
- `reference_ports/README.md:12-14` — the stored-`available` choice, disclosed as deliberate
- `tests/test_behavior.py:249` — R1, the invariant that makes `_available` derivable

**Refuses to claim** (required and non-null for a score of 3):

Not required at this score, and recorded anyway: `README.md:68-77` refuses to claim the tree shows an arm would produce this shape, refuses to generalise past `n = 1`, and states that the author of the catalogue also wrote the tree it seeds into. It does not, anywhere, claim the design got simpler.

**Rationale:**

Rung 2 and not higher.

Rung 2 holds on inspection: five state fields at `domain.py:101-108`, no god-state, and no variable written from everywhere — `_available` has exactly two write sites (`domain.py:140`, `:161`) plus init, `_committed` one, `_closed` one, `_outstanding` three.

I did the diff the dimension asks for by experiment rather than by reading prose, and **one fact IS stored twice**: `_available` (`domain.py:103`) is fully derivable from `_quota − outstanding − _committed`, which is R1 itself, the invariant the suite asserts at `tests/test_behavior.py:249`. I deleted the field, derived `available()` from the other three, and all 28 cases still pass under BOTH wirings — so the redundancy is real and hand-maintained, not load-bearing. It is disclosed as deliberate at `README.md:12-14` (a stored field gives a fault somewhere to live), and a disclosed cost is still a cost; I scored the code, not the disclosure.

Two smaller duplications. The "no blanks" rule is implemented independently in both adapters (`journal_file.py:38`, `journal_memory.py:43`) and is **dead in both** — I removed it from each in turn (F5a, F5b) and nothing failed under either wiring, because the domain never renders a blank line. And the two composition points (`quota_ledger.py:24-36`, `quota_ledger_fake.py:37-49`) duplicate the constructor and the entire `__all__` block, differing in one identifier.

Rung 3 is unreachable, and **not** because a number is missing. `mechanical.json` records `complexity_of_produced_code: {}` and there is no descriptor in the packet, but the dimension's read-first says an absent measurement is not a gap in the evidence, so I did not drop to 0 or 1 for it. Rung 3 fails on *direction* and on *figures*: the only change this tree claims (`README.md:35-36`, `domain.py:8-9`) is that one flat module became five files behind a Protocol — an increase argued as an INSTRUMENT gain, never as a simplification — and no before/after figures for it are recorded on either side. The baseline it is measured against, `../reference/quota_ledger.py`, is outside my read list, so "statement for statement" is a claim I could not check, and per rule 1 a claim is not the property.

Prose quality was a live temptation here and I am saying so as rule 4 requires: roughly a third of this tree is commentary about the eval rather than about the program, it is unusually lucid, and it argues that its own complexity is justified. I scored the executed behavior of the five modules and treated every explanatory paragraph as zero evidence.

### D3 — modularity

**Score:** **4**

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:20-23` — the domain imports only `dataclasses` and `typing`: no `pathlib`, no `os`, no adapter
- `reference_ports/domain.py:38-58` — the `LedgerJournal` driven port, two methods
- `reference_ports/domain.py:125`, `:150-153`, `:172` — every call the domain makes across the boundary
- `reference_ports/journal_file.py:21-38` — the real adapter
- `reference_ports/journal_memory.py:33-43` — the fake adapter
- `reference_ports/quota_ledger.py:25` → `reference_ports/quota_ledger_fake.py:38` — the named swap, one identifier
- `reference_ports/quota_ledger_fake.py:13-22` and `reference_ports/README.md:68-77` — the stated limits

**Refuses to claim** (required and non-null for a score of 4):

`quota_ledger_fake.py:13-22` refuses to assert that the two wirings agree, and says why: a test comparing two wirings of one domain passes when the domain is wrong, because both wirings are wrong together. It also refuses to gate, refuse or report a verdict. `README.md:68-77` refuses to claim any arm would produce this shape, refuses to generalise from `n = 1`, and refuses to read the fake's four-line cost as evidence anyone would have paid it — "nobody did, for a whole epic".

**Rationale:**

Rung 4, reached by execution rather than by import checking, because the caveat forbids the latter.

**Rung 3.** `domain.py:20-23` imports only `dataclasses` and `typing`. The specific swap is one identifier: `quota_ledger.py:25` hands `FileJournal(ledger_path)` to the same `ReservationBook.__init__`, `quota_ledger_fake.py:38` hands `InMemoryJournal()`, and `domain.py` is byte-identical between them.

**Runtime evidence**, which is what the caveat demands. I profiled every cross-module call frame under both wirings. The domain's ONLY outbound calls into a non-domain module are `journal_*.append` (from `commit` at `domain.py:150-153` and `close_tenant` at `domain.py:172`) and `journal_*.lines` (from `ledger_lines` at `domain.py:125`) — exactly the two methods the Protocol declares at `domain.py:38-58`, and nothing else crosses. I also intercepted `pathlib.Path.open/read_text/write_text`: the real wiring makes 8 filesystem calls and the fake wiring makes **zero**, with the domain's own call sequence identical in both. The coupling is not merely absent from the import graph; it is absent from the call graph.

**Rung 4.** The same 28 cases pass against `journal_file.FileJournal` and against `journal_memory.InMemoryJournal`. I did not accept "the same cases pass" as evidence the port discriminates — two green runs are also what you get when a port is never exercised — so I seeded one fault per side with the same semantic (reverse the order `lines()` returns) and ran both wirings against each. The file-side fault killed 5 cases under the real wiring and 0 under the fake; the memory-side fault killed 0 under the real wiring and 5 under the fake. Each side of the port is reached by the shared suite through exactly one wiring, which is the property rung 4 asks about, measured rather than asserted.

I very nearly deducted to 3, and the reason is recorded in the notes and disclosures rather than in this number: the ONLY behavior separating the real adapter from the fake is durability past the object's lifetime; no case in the suite asserts it (every ledger read goes through `ledger_lines()`, nothing touches the path); and no case *can*, because a durability case would fail against the fake and put rung 4 out of reach. Rung 4 as written is therefore satisfiable only by a suite blind to the thing that makes the real adapter real. That is a finding about the anchor, not a defect I may charge to the artifact, so I scored the anchor as written and put the objection where a reader will see it.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `reference_ports/domain.py:122` — `sorted(self._outstanding)`, a lexicographic sort over string ids
- `FEATURE.md:29` — the query is specified as **ascending**
- `reference_ports/journal_file.py:38`, `reference_ports/journal_memory.py:43` — the two seeded sides, and the dead blank filter
- `tests/test_behavior.py:46-54` — the R4 snapshot oracle
- `tests/test_behavior.py:65`, `:118`, `:165`, `:247` — every assertion the suite makes on `outstanding_ids()`
- `tests/test_behavior.py:284-301` — the declared-vocabulary oracle

**Note:**

**CAUGHT.** Ordering and content faults inside *either* adapter, provided a composition point points at it. I seeded the same semantic on each side of the port — reverse the order `lines()` returns — as F1 in `journal_file.py:38` and F2 in `journal_memory.py:43`. F1 killed 5 of 28 cases under the real wiring and 0 under the fake; F2 killed 0 under the real wiring and 5 under the fake. That is the tree's central claim discharged by measurement: with two composition points, a fake-side fault has somewhere to die. The suite also has real oracle strength on the domain's guards — it checks rejection reasons against a declared vocabulary (`tests/test_behavior.py:284-301`) and compares a full observable snapshot across every rejection (`:46-54`), which is a genuine R4 oracle and not a status check.

**MISSED, class 1 — query ordering with more than one live reservation.** This is the sharpest result and it is *not seeded*: it is live in the artifact as shipped. `FEATURE.md:29` requires `outstanding_ids()` to return live ids **ascending**. `domain.py:122` returns `sorted(self._outstanding)` — a lexicographic sort over strings — so with twelve live reservations the artifact returns `['r1','r10','r11','r12','r2','r3',…]`. I ran it: both wirings produce that, and all 28 cases pass regardless. The suite cannot see it because every assertion on that query is made with zero or one live reservation (`:65`, `:118`, `:165`, `:247`), and the R4 snapshot at `:52` compares the query to itself, so any order-preserving fault is invisible to it. I confirmed the blind spot is structural rather than incidental by seeding F3, `sorted(…, reverse=True)` at the same line: 28/28 pass under both wirings. **So the region no oracle reaches is not only behind the port — the domain has one too, and it is the region where the artifact already has a defect.**

**MISSED, class 2 — durability**, the one property distinguishing the real adapter from the fake. Nothing in the suite reads the ledger path; every read goes through `ledger_lines()` (`:66`, `:119`, `:129`, `:137`, `:166`, `:192`, `:197`, `:277`). My probe reading the file directly after dropping the object passes under the real wiring and fails under the fake. The suite cannot contain that case without failing the fake wiring.

**MISSED, class 3 — dead defensive code.** The blank-line filter exists twice, at `journal_file.py:38` and `journal_memory.py:43`. Deleting it from either (F5a, F5b) kills nothing under either wiring, because the domain never renders a blank line: two independent implementations of a rule nothing executes.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `reference_ports/domain.py:8-9`, `reference_ports/README.md:35-36` — the "statement for statement" preservation claim and the baseline it names
- `FEATURE.md:16-17` — "durable, append-only ledger file"
- `FEATURE.md:29` — ascending ids
- `FEATURE.md:40-45`, `FEATURE.md:76-80` — the specified *order* of the rejections
- `reference_ports/domain.py:122` — where the ascending requirement fails
- `reference_ports/quota_ledger_fake.py:4-5`, `:37-38` — `ledger_path` accepted and unused

**Note:**

The baseline this tree names is `../reference/quota_ledger.py` (`domain.py:8-9`, `README.md:35-36`), and it is **outside the read list I was given**. So the artifact's preservation claim — "the behavior here is the behavior of `../reference/quota_ledger.py`, statement for statement" — is a claim I could not check against the thing it is about, and per rule 1 I did not credit it. I say that plainly rather than scoring around it.

What I could do is enumerate the *specified* behavior, `FEATURE.md`, and check each item directly with my own probe rather than through the shipped suite — a weaker baseline, but a real one.

**Enumerated and shown to hold, under both wirings:** initial `available` / `committed` / `is_closed`; empty starting ledger; the four `reserve` rejections IN THEIR SPECIFIED ORDER (`FEATURE.md:40-45` — I checked that `unknown_tenant` beats `tenant_closed`, `tenant_closed` beats `amount_not_positive`, and `amount_not_positive` beats `quota_exceeded`, none of which the suite checks *as an ordering*); the three `close_tenant` rejections in order (`FEATURE.md:76-80`); ids never reused after a release; R3 exactly one `CLOSE` line across a repeated close; R4 no durable write across five distinct rejections; R5 each ledger snapshot a prefix of the next.

**Enumerated and shown NOT to hold:** `FEATURE.md:29`, ids ascending. `domain.py:122` sorts lexicographically and returns `r1, r10, r11, r12, r2, …` for twelve live reservations, under both wirings. Whether the flat baseline shares this defect I cannot say, because I may not read it — but the artifact's own governing specification *is* in my read list, and the artifact does not satisfy it.

**Enumerated and holds under one wiring only:** durability. `FEATURE.md:16-17` calls the ledger a durable, append-only **file**. Reading the path directly after dropping the object succeeds under `quota_ledger` and fails under `quota_ledger_fake`, which creates no file at all despite accepting `ledger_path` (`quota_ledger_fake.py:37-38`). The artifact declares exactly this at `quota_ledger_fake.py:4-5`, so it is disclosed divergence, not concealed — but it does mean "the same cases pass against both wirings" is true only because no case tests the word *durable*.

### N-D5 — honesty

**Citations** (`file:line`):

- `reference_ports/README.md:36-39` — the equivalence claim is given as a command to run, not as an assertion
- `reference_ports/README.md:66` — "Nothing here gates, refuses, or reports a verdict. It is a fixture."
- `reference_ports/README.md:68-77` — "What this tree does NOT settle"
- `reference_ports/quota_ledger_fake.py:10-12`, `:13-22` — refuses the flattering reading of its own remedy, and refuses a parity test
- `reference_ports/journal_memory.py:7-27` — where the artifact locates the blind region
- `reference_ports/domain.py:9-10`, `:122` — the one overstatement, and the thing it overstates about

**Note:**

It refuses, repeatedly, and several of the refusals are load-bearing rather than decorative. `README.md:66` — "Nothing here gates, refuses, or reports a verdict. It is a fixture." `README.md:68-77` — it does not settle that an arm would produce this shape, it is `n = 1`, and the tree was written by the same author as the catalogue that seeds into it, named as a bias two trees do not reduce. Sharpest of all, `README.md:75-77` and `quota_ledger_fake.py:10-12` refuse the flattering reading of their own remedy: four lines being cheap is evidence the blind region was cheap to reach, **not** evidence anybody would have reached it, and "nobody did, for a whole epic". `quota_ledger_fake.py:13-22` refuses a parity test on a correct technical ground — two wirings of one domain agree when the domain is wrong — which is a refusal to build the easier and weaker instrument. `README.md:36-39` does not merely assert the wirings agree; it names the command that shows it, and the two in scope do.

**What it does not see, and this is the gap.** The artifact reasons at length about a region no oracle reaches and locates that region *entirely behind the port*, in the fake adapter (`journal_memory.py:7-27`). It never considers that the same suite leaves an unreached region in the **domain**. It does: `outstanding_ids()` at `domain.py:122` violates `FEATURE.md:29` today, no case can see it, and no file in the packet mentions the query's ordering. Nor does anything name the cost of its own instrument — that "the same cases pass against both wirings" is purchasable only by never asserting durability. So the honesty is real and it is aimed in one direction: the artifact is candid about the limits it went looking for, and silent about the one adjacent to its own thesis.

Two smaller unbacked notes: `domain.py:9-10` says the shared suite is "the thing that says so" about statement-for-statement equivalence, which overstates a 28-case suite that I showed survives a reversal of a specified query; and both adapters carry an unreachable blank-line filter whose presence implies the domain might emit blanks (`journal_file.py:38`, `journal_memory.py:43`).

## Verdict

The boundary is real at runtime and the second composition point measurably closes the adapter blind region — a fake-side fault dies under the fake wiring and only there — but the suite that earns rung 4 is structurally the suite that cannot assert durability, and the domain has its own unreached region: `outstanding_ids()` is lexicographic, so it violates `FEATURE.md:29` from `r10` onward and all 28 cases pass under both wirings anyway.

## Disclosures

**Seen that I was not meant to see:** nothing. I read only `FEATURE.md`, the five `reference_ports/` modules, `reference_ports/README.md`, `tests/test_behavior.py`, and my own two card files plus `mechanical.json`. I did not open `references/eval_scorecard.md`, any other scorecard, any `*-EPIC.md`, `specs/desired_program_model/`, or the flat baseline `../reference/quota_ledger.py`.

**Ran that changed a tree:** nothing in the repository. Every run was against a copy under my scratch directory. `mechanical.json` was left as scaffolded — its `figures` blocks are empty (`kills: {}`, `complexity_of_produced_code: {}`, `case_counts: {}`, `determinism: {}`, `runtime_seconds: null`) and I did not fill them, because rule 7 makes that block a recorded measurement and not a judge's product. My own kill counts are in `judging_practice`, where they belong to me and can be subtracted from my scores.

**A forced read the card could not supply.** D2's read-first instructs me to "diff the two trees yourself". The packet contains one tree, and the other — `../reference/quota_ledger.py` — is excluded by my read list. I obeyed the read list and diffed the artifact against `FEATURE.md` and against a mutated copy of itself instead. Any D2 judgement on this card is therefore about one tree, and that is a property of the instructions, not a choice I made.

### What I REJECTED

- **A D3 of 3, which I very nearly gave.** The reasoning I abandoned: the fake wiring makes zero filesystem calls and no case asserts durability, so the "same cases against both adapters" that rung 4 rewards never verifies the property that makes the real adapter real — I wanted to deduct for a boundary that is only *cheaply* exercised. I rejected it because the deduction would have been against a bar the rubric does not set, and because it is worse than a deduction: **rung 4 is unsatisfiable by any suite that does assert durability**, since such a case must fail the fake. The anchor rewards a specific blindness. Charging that to the artifact would hide it in a number; the right place for it is this section, and it is the single most useful thing I found.
- **A D2 of 0 on the letter of the anchor.** "Complexity is unmeasured" is literally true here — `mechanical.json` is empty and the packet ships no descriptor — and 0 is the lowest anchor the artifact fully satisfies on a strict reading of the ladder. I rejected it because the dimension's own read-first says an absent measurement "is not a gap in the evidence", which makes rungs 0 and 1 about artifacts that *report* figures without arguing them, not about artifacts that report none. Flagging the tension because the ladder and the read-first do not agree and a strict reader could land on 0.
- **A D2 of 3 via my own experiment.** I did perform a simplification — deriving `_available` instead of storing it — and it passed 28/28 under both wirings. It was tempting to count that as "a simplification was made and its effect measured". I rejected it: rung 3 asks what *the artifact* did, not what the judge did, and MF-020 is explicit that the judge must say what got simpler in the artifact. My experiment is evidence about redundancy, not a simplification the artifact can be credited with.
- **A claim I tested and could not break.** The tree's central assertion — that a second composition point makes a fault in the fake adapter observable — held under direct attack. I seeded matched faults on both sides of the port and each died only under the wiring that reaches it (5/28 and 5/28, mirrored). I also could not break the domain's guard ordering: my independent probe checked all seven specified rejection orderings, including three the suite never checks as orderings, and every one held. The prose is very persuasive and I was wary of that; the claim survived execution regardless.
- **Treating the artifact's disclosures as mitigation.** `README.md:12-14` explains the redundant `_available` as deliberate, and `quota_ledger_fake.py:4-5` explains the ignored `ledger_path` as deliberate. I nearly let both offset the D2 rationale. Rejected: rule 1. A disclosed cost is still a cost, and the code is what I scored.
