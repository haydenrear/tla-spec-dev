# Scorecard — toolchain_removal, artifact `GL`, judge pass 2

`run_id`: `20260812-sv04conf-GL-p2` · scorecard_version 5 · rubric `references/eval_scorecard.md` digest `sha256:24b2c599901d7ae0` · served `sha256:2d7d4a0506d9b259`

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

- Copied the packet to scratch (never edited in place) and ran the green control both ways: QUOTA_LEDGER_DIR=<copy>/reference_ports QUOTA_LEDGER_IMPL=quota_ledger|quota_ledger_fake uv run --with pytest python -m pytest tests/test_behavior.py -q -p no:cacheprovider -- 28 collected, 28 passed under each.
- Seeded 12 faults of my own, one per mutant copy, and ran the shared suite through BOTH composition points for each. 9 in the first batch: J1 journal_memory.append drops CLOSE lines; J2 the same semantic in journal_file.append; J3 journal_memory.lines() reversed; J4 the same in journal_file.lines(); J5 FileJournal.__init__ touch() instead of write_text('') (the 'file starts empty' rule); J6 domain.commit also refunds _available; J7 domain.release decrements _next_id (id reuse); J8/J9 duplicate-line suppression in each adapter.
- Results, first batch: KILLED J1 (fake wiring only, 3/28), J2 (real wiring only, 3/28), J3 (fake only, 5/28), J4 (real only, 5/28), J6 (both wirings, 2/28). SURVIVED both wirings: J5, J7, J8, J9.
- 3 more faults aimed at whether anything outside FileJournal observes the file: K1 append writes reversed and prefixed, lines() un-prefixes (round-trip clean, file content garbage); K2 __init__ redirects to <path>.elsewhere so nothing is written at the caller's path; K3 FileJournal drops the filesystem entirely for an in-memory list. ALL THREE SURVIVED the real wiring, 28 passed each.
- A direct probe script (no pytest) to check that the two most interesting survivors are real bugs and not equivalent mutants: constructing over a pre-existing stale ledger file returns [] on the baseline and ['COMMIT stale 99 99'] under J5; ids go r1 -> release -> r2 on the baseline and r1 -> release -> r1 under J7.
- Determinism: the suite run 3x per wiring, 28 passed every time, identical counts. Runtime 1.41s on the first (cold) real-wiring run and 0.07-0.09s warm, per wiring.
- Static counting in domain.py: imports, every `self._<field>` write site, and every `self._journal.` call site.
- NOT run: `check_catalogue.py`, the PA catalogue, and anything under `../reference/` -- all outside the read list I was given.

## Your scores

### D2 — complexity

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:101-108`
- `reference_ports/domain.py:129-173`
- `reference_ports/domain.py:140`
- `reference_ports/domain.py:161`
- `reference_ports/README.md:14-15`
- `reference_ports/quota_ledger_fake.py:34-38`

**Refuses to claim** (required and non-null for a score of 3):

README.md:70-77 refuses to claim the tree shows an arm would produce this shape, refuses n>1 ('it is one feature, n = 1'), and refuses to read the four-line fake wiring as evidence anyone would have written it -- 'evidence that the blind region was cheap to reach, NOT evidence that anybody would have reached it'. What it does not refuse anywhere, and what I could not find, is any complexity figure at all.

**Rationale:**

Scored on the design, because this dimension's read_first says a missing complexity descriptor 'is not a gap in the evidence' and tells the judge to diff the trees themselves. I note the tension openly: taken literally, anchor 0 ('complexity is unmeasured') is the anchor this packet satisfies -- no descriptor ships with it, mechanical.json arrived empty, and I found no before/after figures anywhere in the read list. I do not score 0 or 1 because anchor 1 requires figures to have been 'measured and reported' and there are none, and because the dimension's own instruction forecloses reading their absence as a defect. What I diffed: I could only diff the two COMPOSITION POINTS, since the flat `../reference/` tree the README compares against is outside my read list -- I did not open it. quota_ledger.py:24-25 and quota_ledger_fake.py:37-38 are the same four lines with one class name changed, over one shared `ReservationBook`; there is no second copy of the rules. The state is six fields (domain.py:102-108) and each is written from the constructor plus only the commands whose semantics own it: `_committed` from commit alone (:149), `_closed` from close_tenant alone (:171), `_next_id` from reserve alone (:139), `_journal` never rewritten after :108. No god-state and no variable written from everywhere. One fact IS stored twice: `_available` is derivable from R1 (quota minus outstanding minus committed) and is instead maintained by hand at reserve (:140) and release (:161). That is the strongest argument against anchor 2, and it is why I considered the lower rung. Two things hold me at 2 rather than below: it is read in two places (the query at :113 and the quota_exceeded guard at :136), not one, so it is not the 'kept in agreement by hand and read in one place' shape the read_first names; and the artifact discloses the redundancy as deliberate (README.md:14-15). I also probed it -- a seeded fault that refunds `_available` at commit died under both wirings (2 of 28 cases), so the two copies are not silently divergent. Not 3: no simplification is claimed here and no before/after figures exist to record, so the MF-020 bar -- say what got simpler and how the behavior survived it -- has nothing to attach to. If anything this tree is a COMPLICATION of a flat module (a port plus two adapters plus two composition points for one file write), and it is measured in neither direction. Prose quality was a real temptation on this artifact and I am recording that it was excluded: every module carries a long, well-argued docstring, and none of them is evidence. The score comes from domain.py's field/write-site topology, which I counted, and from mutants I ran.

### D3 — modularity

**Score:** 3

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:20-23`
- `reference_ports/domain.py:38-58`
- `reference_ports/domain.py:125`
- `reference_ports/domain.py:150`
- `reference_ports/domain.py:172`
- `reference_ports/quota_ledger.py:25`
- `reference_ports/quota_ledger_fake.py:38`
- `reference_ports/journal_file.py:28-38`
- `tests/test_behavior.py:34-36`
- `tests/test_behavior.py:43`

**Refuses to claim** (required and non-null for a score of 4):

quota_ledger_fake.py:16-22 refuses to assert parity between the two wirings and says why -- 'a test that only compares two wirings of one domain passes when the domain is wrong' -- and refuses to gate or report a verdict. README.md:70-72 refuses to claim an arm would produce this shape. Nothing in the packet claims the durable file is independently observed, and nothing claims it is not either; that gap is mine to report, not the artifact's refusal.

**Rationale:**

Anchor 3 is met and I name the swap. The domain declares the driven port itself (domain.py:38-58, `LedgerJournal` as a Protocol in the domain's own vocabulary) and imports only `dataclasses` and `typing` (domain.py:20-23) -- I grepped for `open(`, `Path`, `os.`, `journal_file`, `journal_memory` and `FileJournal` in domain.py and the only hits are inside docstrings. Exactly three cross-boundary calls exist, all through the port handle: `_journal.lines()` at :125 and `_journal.append(...)` at :150 and :172. THE SWAP: quota_ledger.py:25 passes `FileJournal(ledger_path)` and quota_ledger_fake.py:38 passes `InMemoryJournal()` into the identical `ReservationBook.__init__`; `domain.py` is byte-identical across both wirings and the adapter modules import nothing from the domain, so the dependency runs one way. Not import topology -- runtime call evidence, which the caveat demands. I seeded a fault in journal_memory.append (drop CLOSE lines) and it died only under QUOTA_LEDGER_IMPL=quota_ledger_fake (3 of 28) while all 28 passed under quota_ledger; I seeded the MIRROR of it in journal_file.append and it died only under quota_ledger (3 of 28) while all 28 passed under the fake. Reversing lines() in each adapter reproduced the same one-sided pattern (5 of 28 each). That asymmetry can only come from which object the domain actually calls at runtime, so the boundary is real and not an import convention. Anchor 4's literal text is also satisfied in fact: the identical 28 cases pass green through both wirings, and I ran them. I take 3 anyway, under the caveat, because the real adapter's realness is observed by nothing outside the real adapter. tests/ contains one file; it constructs through the composition point (test_behavior.py:43) and reads the durable side only via `ledger_lines()` (:54), which is `FileJournal.lines()` reading back what `FileJournal.append()` wrote. I proved the consequence rather than asserting it: (a) making FileJournal write reversed, prefixed garbage and un-prefix it on read -- 28 passed; (b) making FileJournal write to `<path>.elsewhere` so no file ever appears at the caller's path -- 28 passed; (c) deleting the filesystem from FileJournal entirely and backing it with a list, i.e. two fakes and no real adapter -- 28 passed. The caveat's condition ('the only observer of the effect the port exists for is the adapter that wrote it') is therefore met literally and demonstrably, and its instruction is 'say so and take 3'. Prose was again a temptation and again excluded: quota_ledger_fake.py:1-23 argues its own case eloquently. The score rests on the mutant asymmetry and on (c).

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `tests/test_behavior.py:41-54`
- `tests/test_behavior.py:60-107`
- `tests/test_behavior.py:270-281`
- `reference_ports/journal_file.py:28-30`
- `reference_ports/journal_file.py:32-38`
- `reference_ports/domain.py:138-139`
- `reference_ports/domain.py:156-162`

**Note:**

I seeded 12 faults and ran every one; 5 died, 7 lived, and 2 of the 7 are equivalent mutants I am not counting against the suite.

WHAT THE CASES CAUGHT. Both semantic classes I seeded inside an adapter -- a dropped CLOSE line and a reversed read-back -- died, but each died under exactly ONE wiring: the journal_memory faults only under QUOTA_LEDGER_IMPL=quota_ledger_fake and the identical journal_file faults only under quota_ledger. The killing cases are the ones that assert literal ledger content: test_behavior.py:119, :129, :137, :192, :197 and test_r5_the_ledger_is_append_only_and_ordered at :270-281. The R4 `snapshot` comparison (:46-54, used at :87-91 and seven other rejection cases) is the strongest single mechanism in the file: it compares all five observables across a rejection, so a rejection with a side effect has nowhere to hide. A domain fault that refunded `_available` at commit died under both wirings via the explicit assertion at :117.

WHAT IT DEMONSTRABLY MISSED -- three classes, all shown by execution, not argued.
(1) THE REAL ADAPTER'S REALNESS. FileJournal can be replaced wholesale by an in-memory list (journal_file.py:32-38 gutted) and all 28 cases still pass through the REAL wiring. So can writing reversed, prefixed garbage to disk and un-prefixing it on read, and so can writing to `<path>.elsewhere` so that no file ever appears at the path the caller named. The suite reads the durable side only through `ledger_lines()`, which is the same adapter reading itself; nothing in tests/ ever opens the file. This is the same blind-region shape the packet identifies on the fake side, sitting on the real side, and the packet does not name it.
(2) CONSTRUCTION-TIME LEDGER STATE. FEATURE.md:21 says the ledger file starts empty and journal_file.py:30 implements that by truncating. Weakening it to `touch()` survives all 28 cases both ways, because the `ledger` fixture (test_behavior.py:41-43) always hands out a fresh tmp_path and so never observes a pre-existing file. My probe confirms it is a real bug: over a stale file the baseline reports [] and the mutant reports the stale COMMIT line.
(3) ID REUSE AFTER RELEASE. FEATURE.md:49-50 says ids are never reused. Decrementing `_next_id` in release (domain.py:156-162) survives all 28 cases both ways -- test_reservation_ids_are_allocated_in_order (:69-72) only ever reserves, and no case releases and then checks the next id. Probe: baseline r1 -> release -> r2, mutant r1 -> release -> r1.

HONESTY ABOUT TWO SURVIVORS I AM NOT COUNTING: duplicate-line suppression in either adapter survives, but the domain's line format (domain.py:151-152, a strictly increasing per-tenant running total; :172, one CLOSE per tenant) makes two identical lines unreachable. Those are equivalent mutants and a suite gap they are not.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `FEATURE.md:26-104`
- `reference_ports/README.md:24-45`
- `reference_ports/domain.py:8-12`
- `tests/test_behavior.py:1-20`
- `reference_ports/quota_ledger.py:24-25`
- `reference_ports/quota_ledger_fake.py:37-38`

**Note:**

THERE IS NO BASELINE IN MY READ LIST, and that is the answer. The artifact's own claim of preservation is stated against `../reference/quota_ledger.py` -- 'the behavior here is the behavior of ../reference/quota_ledger.py, statement for statement' (domain.py:8-9, repeated at README.md:24-27) -- and that tree is outside the directory I was told to score. I did not open it. So the statement-for-statement claim is a claim I cannot check, and I am recording it as unchecked rather than as met.

WHAT I COULD ENUMERATE is FEATURE.md, which is the requirement and is present. I walked all five observables (FEATURE.md:26-31) and all four commands with their ordered rejection ladders (:38-88) against domain.py:112-173 and found each implemented in the stated order: reserve's four guards at :130-137 in FEATURE's order, commit and release rejecting `unknown_reservation` at :146 and :158, close_tenant's three guards at :165-170 in order, `available` deliberately NOT restored at commit (:149-153, matching FEATURE.md:65-66), release writing nothing durable (:156-162, matching :72). R1-R5 all have cases and all pass. The six-reason vocabulary is declared once (domain.py:28-35) and checked at test_behavior.py:284-301.

WHAT I COULD CHECK BY EXECUTION is the weaker but real form of preservation this tree actually offers: the same 28 cases pass unmodified through both composition points, so the domain's behavior is preserved ACROSS THE PORT SWAP. I ran both, three times each, identical results. That is preservation between two wirings of one domain, not preservation against a prior implementation, and the packet is careful about the difference itself (quota_ledger_fake.py:16-20 refuses to treat wiring agreement as an oracle). One asymmetry worth recording: quota_ledger_fake.py:37-38 accepts `ledger_path` and discards it, so the fake wiring cannot preserve any behavior that depends on the path -- and per N-D1 no case observes one, so nothing detects that.

### N-D5 — honesty

**Citations** (`file:line`):

- `reference_ports/README.md:68-77`
- `reference_ports/README.md:1-6`
- `reference_ports/quota_ledger_fake.py:14-22`
- `reference_ports/journal_memory.py:7-27`
- `tests/test_behavior.py:6-12`
- `reference_ports/journal_file.py:6-13`

**Note:**

The artifact refuses in several specific, checkable places and it does not falsely certify. README.md has a section headed 'What this tree does NOT settle' (:68-77) that gives up three things a flattering version would have kept: that an arm would ever produce this shape (':70-72, PA-06 re-anchors onto the arms'), that n is anything but 1, and -- the sharpest one -- that the four-line fake composition point is evidence anyone would have written it: 'evidence that the blind region was cheap to reach, NOT evidence that anybody would have reached it. Nobody did, for a whole epic, and that is the measured fact' (:75-77). It also declares its own author bias in the same breath (':73-74, the tree was written by the same author as the catalogue that seeds into it'). quota_ledger_fake.py:16-20 refuses the easy oracle and says why a parity test would be circular. The test suite volunteers that it is 'a competent hand-written suite, not an adversarial one' (test_behavior.py:6-8) and that writing it stronger to flatter a prediction would be tuning an instrument to its own metric. README.md:66 and quota_ledger_fake.py:21-22 both refuse to gate or report a verdict. Nothing anywhere claims the suite is complete.

WHERE THE REFUSAL DOES NOT REACH, and this is the honest counterweight: the packet names the blind region precisely on one side of the port and is silent about the same region on the other. journal_file.py:6-13 asserts that a fault there 'is reachable by anything that runs the shared suite through the real wiring' -- true for the two fault shapes I mirrored, and false for the three I ran in N-D1(1), where FileJournal stops touching the filesystem, writes garbage, or writes to another path and all 28 cases stay green. That sentence is the one place in the packet where a claim outruns the evidence, and it is stated as fact rather than as a refusal. It is a gap in self-inspection rather than a false certification -- the sentence is about which instrument reaches the file, and the artifact never claims the file's CONTENT is independently observed -- but a reader would come away believing the real side is covered.

## Verdict

A genuine port with a genuine swap -- the domain imports no I/O, and mutants prove at runtime that each adapter is reached only through its own composition point -- but the second wiring is what makes the fake observable, not what makes the real adapter real: FileJournal can be emptied of the filesystem entirely and all 28 shared cases still pass, so the durable effect the port exists for has no observer outside the adapter that wrote it, and the artifact's one overreaching sentence (journal_file.py:6-13) says the opposite.

## Disclosures

_Anything you saw that you were not meant to see, anything you ran that changed the tree, and anything you REJECTED. For three rounds running the best finding in this project came from the last one, and zero came from re-running the suite._

**LEAKS — disclosed, not concealed. Three of them, and the first is the serious one.**

1. **The artifact told me it is not an arm.** `reference_ports/README.md:1-6` opens with "**THIS IS NOT AN ARM.** Neither is `../reference/`. Nothing here is dispatched to an agent, judged, scored, or placed in a table beside arm A's, arm B's or arm C's numbers," and `reference_ports/domain.py:3` repeats it. So I know artifact `GL` is a hand-written reference/anchor tree written by the eval's own author, not an arm's output. I read this inside my assigned read list, before scoring, and there was no way to score the packet without reading it. I did not go looking for the arm mapping and I still do not know it — but the blinding on this card is materially weakened and a reader should discount it accordingly. I tried to hold the effect off by scoring only what I could execute; whether that worked is not mine to certify.

2. **The artifact carries a prior epic's result about the very dimension I am scoring.** `reference_ports/README.md:19-23` and `reference_ports/journal_memory.py:9-15` quote `specs/results/scorecards/hexagonal-prompting/FINDINGS.md` by name, including finding `BA-B14` and the sentence "the fake that earned arm B its **D3 = 4** is verified by nothing outside arm B's own tests." That is a prior D3 score, with its arm named, embedded in the artifact I was told to read in full. It plainly anchors upward on D3 and I record that I scored 3, below it, on evidence I ran myself (K3) rather than on that sentence.

3. **`score_tools.py` carries prior results in its comments.** I was instructed to run `examples/validation/scorecards/score_tools.py`, and I read its validation logic first so my card would not be refused on a technicality. Its comments state prior scoring outcomes: "`opus` judged D3 2, 2 and `sonnet` 4, 3 on the same artifact while D2 agreed across tiers"; "four judges scored three different subjects of one artifact once already, and D3 came out 2, 2, 3, 4"; and "D2 has taken one value on every card ever written about `ab_quota_ledger`, and D1, D4 and D5 each take a different value from a different judge on the same bytes." I saw those after forming both scores from the code and the mutants, and I did not change either. The tool a judge is told to run should probably not narrate the distribution of prior judges' scores.

**What I did NOT read**, having been told not to: `references/eval_scorecard.md`; any other directory under `specs/results/scorecards/`, including `UNBLINDING.md`, any `PREDICTIONS*`, `RESULT*` or `HARVEST*`; any `*-EPIC.md`; any other `artifact_*`; `examples/validation/ab/` outside my packet — which includes `../reference/`, `../model/`, `../seeded_faults.toml` and `check_catalogue.py`, all named by the artifact and all outside my read list; git history. I ran no `git log`. The one `git` command I ran was `git rev-parse --short HEAD` for the `commit` field.

**What I ran that changed a tree: nothing in the repository.** The packet was copied to `/private/tmp/claude-501/.../scratchpad/SV-04/judge-GL-p2/base` and every one of the 12 mutants is a separate copy under `.../judge-GL-p2/mut/<fault-id>`. The packet was never edited in place. The only files I wrote in the repository are this card, `scorecard.json` and `mechanical.json`.

**What I REJECTED.**

- **I rejected D3 = 4, and this is the card's main content.** Anchor 4's literal text is satisfied — one driven port, a real adapter and a fake, the same 28 cases green through both, and I ran them. The caveat's escape clause is what stopped me, and I did not take it on impression: I gutted `FileJournal` of the filesystem entirely (backed it with a list), and 28/28 passed through the *real* wiring; I redirected it to `<path>.elsewhere` so no file ever appears where the caller asked, 28/28; I made it write reversed prefixed garbage and un-prefix it on read, 28/28. Nothing in `tests/` opens the ledger file. The real adapter's realness is observed by nothing outside the real adapter, so the instruction "say so and take 3" applies exactly.
- **I rejected D2 = 0 and D2 = 1, against the literal anchor text.** Read literally, "complexity is unmeasured" describes this packet: no descriptor, empty `mechanical.json`, no before/after figures. I did not take 0 because the dimension's own `read_first` says a missing descriptor "is not a gap in the evidence" and instructs the judge to diff the trees personally, which only makes sense if the design anchors are reachable without one. I flag the tension rather than resolve it silently, because a different judge reading the same two sentences could legitimately land on 0 and the gap between us would be two points of nothing.
- **I rejected the D2 = 3 route via "the port is a simplification".** It is a complication of a flat module measured in neither direction, and MF-020 is explicit that a number moving is not the argument.
- **I rejected all five modules' docstrings as evidence** (scoring rule 4). They are the most persuasive prose I have read on a scored artifact and they argue the artifact's case better than the artifact demonstrates it — `journal_file.py:6-13` asserts that a fault in the real adapter "is reachable by anything that runs the shared suite through the real wiring", and three of my mutants show that is false as stated. Both scores rest on counts I made and mutants I ran.
- **I rejected two of my own survivors as evidence.** `J8`/`J9` (duplicate-line suppression in either adapter) survive both wirings, but the domain's line format makes two identical lines unreachable, so they are equivalent mutants and not a suite gap. Counting them would have inflated the miss rate from 5/10 to 7/12.

**Scope limit I could not close.** D2's `read_first` says "diff the two trees yourself". The second tree it means is `../reference/`, which is outside my read list, so the only diff I could perform is between the two composition points inside my packet. The artifact's central preservation claim — "the behavior here is the behavior of `../reference/quota_ledger.py`, statement for statement" (`reference_ports/domain.py:8-9`) — is therefore recorded by me as unchecked, not as met.
