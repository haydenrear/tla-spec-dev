# Scorecard — toolchain_removal, artifact `CL`, judge pass 1

`run_id`: `20260811-cl03v5-CL-p1` · scorecard_version 5 · rubric `references/eval_scorecard.md` digest `sha256:24b2c599901d7ae0` · served `sha256:2d7d4a0506d9b259`

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

- Copied the artifact to a scratch tree under scratchpad/judge-v5-p1/ and mutated only the copy; the artifact was never edited in place.
- BASELINE: 28 passed under QUOTA_LEDGER_IMPL=quota_ledger and 28 passed under quota_ledger_fake.
- M1 (the finding behind D3=3): replaced FileJournal's body with an in-memory list, zero filesystem contact, same interface -> 28 passed under BOTH wirings. Re-ran with --basetemp and counted ledger.txt files: 28 at baseline, 0 under M1.
- M2: journal_file.py lines() drops its first entry -> 7 failed / 21 passed under the real wiring, 28 passed under the fake wiring.
- M3: the SAME fault in journal_memory.py lines() -> 28 passed under the real wiring, 7 failed / 21 passed under the fake wiring. M2 and M3 are the mirrored pair that proves each adapter is reachable only through its own composition point.
- M4: domain.py:122 sorted(self._outstanding, reverse=True) -> 28 passed under BOTH wirings. A domain-side fault, invisible to everything.
- M5: domain.py:102 self._quota = {tenant: -999 for tenant in quotas} -> 28 passed under BOTH wirings, proving _quota's values are dead state.
- M6 (control, to show the suite is not inert): domain.py:136 off-by-one in the quota guard -> 3 failed / 25 passed under both wirings.
- Non-mutant probe on the UNMUTATED tree: constructed QuotaLedger({'acme': 100}, path), made 11 reservations, printed outstanding_ids() -> ['r1','r10','r11','r2',...].
- Static: grepped every _available, _quota and import site in domain.py; grepped tests/test_behavior.py for read_text/open/tmp_path (one hit, the fixture) and for every outstanding_ids assertion (four, all of them [] or ['r1']).
- diff -rq of the artifact against examples/validation/ab/ to confirm my file:line citations resolve there. They do, byte for byte, __pycache__ aside. See Disclosures for what that command let me see.

## Your scores

### D2 — complexity

**Score:** **2** _(0–3)_

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:101`
- `reference_ports/domain.py:102`
- `reference_ports/domain.py:103`
- `reference_ports/domain.py:113`
- `reference_ports/domain.py:130`
- `reference_ports/domain.py:140`
- `reference_ports/domain.py:161`
- `reference_ports/domain.py:165`
- `reference_ports/journal_memory.py:33`
- `reference_ports/quota_ledger.py:21`
- `reference_ports/quota_ledger_fake.py:34`
- `reference_ports/README.md:15`

**Refuses to claim** (required and non-null for a score of 3):

Not required at this rung (top of D2 is 3), recorded anyway: reference_ports/README.md:68-77 refuses to claim the tree shows an arm would produce this shape, refuses to treat n=1 written by the catalogue's own author as reduced bias, and refuses to read quota_ledger_fake.py being four lines as evidence anybody would have written those four lines. What the tree does NOT refuse anywhere is the durability its port is named for -- see D3.

**Rationale:**

ANCHOR 2, and 2 is a ceiling here rather than a compliment. The design is proportional: five files, ~340 lines of code for a spec with four commands, five queries and five rules; one class holds the state (reference_ports/domain.py:101-108); no god-state and no variable written from everywhere -- the most-written field has three write sites, all inside the command that owns them.

3 IS STRUCTURALLY UNREACHABLE FOR THIS ARTIFACT, and that is worth more than the number. Anchor 3 wants a simplification with before AND after figures recorded. Nothing in this tree measures anything: there is no complexity descriptor, and mechanical.json's complexity_of_produced_code is {}. The read_first tells me to diff the two trees myself -- but the 'before' tree, ../reference/quota_ledger.py, is not on my read list, so the diff the rung depends on is a diff I am forbidden to perform. I did not perform it. 3 was never on the table.

I APPLIED THE READ_FIRST'S OWN TEST AND IT DID FIND SOMETHING -- I nearly took 1 on it. Is one fact stored twice, kept in agreement by hand? Yes, twice over. (a) reference_ports/domain.py:102 stores _quota and :103 stores _available from the SAME mapping; _quota's VALUES are then never read again -- :130 and :165 use it only as a membership test. I proved this by execution rather than by reading: mutating :102 to {tenant: -999 for tenant in quotas} leaves all 28 cases passing under both wirings. That is dead duplicated state, demonstrated, not alleged. (b) _available is derivable at every instant -- R1 is exactly the identity quota - outstanding - committed -- and is instead cached and hand-maintained at :103, :140 and :161. reference_ports/README.md:15-16 concedes this was made a stored field ON PURPOSE so that a seeded fault would have somewhere to live, which means the artifact is by its own account less simple than its behavior requires, for the instrument's sake and not the behavior's.

WHY I DID NOT TAKE 1 DESPITE THAT. The tie-break says take the lower when torn, and I was torn for a long time. I took 2 because anchor 1's text is factually FALSE about this artifact -- it describes figures measured and reported with no relationship to the design argued, and there are no figures at all. Scoring 1 would have asserted something untrue in order to look strict. The two duplications I found are real but small: a dead dict and a cached aggregate with three write sites, neither of which is a god-state or a variable written from everywhere. I record the near-miss instead of banking it.

PROSE: rule 4 applied and it cost the artifact nothing and gained it nothing. This tree is written to be persuasive -- reference_ports/quota_ledger.py:9 ('so the claim is not a claim'), reference_ports/quota_ledger_fake.py:7 ('THIS FILE IS AN INSTRUMENT, NOT A CONVENIENCE'), reference_ports/journal_memory.py:7-27 where 21 of 43 lines are advocacy citing a prior epic's finding. It tempted me upward. I scored the five bodies of code, which are 15, 12, 6, 5 and 45 lines, and the score is what those lines support.

### D3 — modularity

**Score:** **3** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

- `reference_ports/domain.py:20`
- `reference_ports/domain.py:38`
- `reference_ports/domain.py:54`
- `reference_ports/domain.py:108`
- `reference_ports/domain.py:125`
- `reference_ports/domain.py:150`
- `reference_ports/domain.py:172`
- `reference_ports/journal_file.py:30`
- `reference_ports/journal_file.py:32`
- `reference_ports/journal_file.py:36`
- `reference_ports/journal_memory.py:39`
- `reference_ports/quota_ledger.py:18`
- `reference_ports/quota_ledger.py:25`
- `reference_ports/quota_ledger_fake.py:31`
- `reference_ports/quota_ledger_fake.py:38`
- `tests/test_behavior.py:34`
- `tests/test_behavior.py:43`
- `tests/test_behavior.py:53`

**Refuses to claim** (required and non-null for a score of 4):

Anchor 4 is what the artifact refuses to earn, and the refusal is mine, not its. The tree DOES claim the fake wiring is 'an instrument, not a convenience' (reference_ports/quota_ledger_fake.py:7) and it is right. What nothing in the tree refuses -- and what I am refusing on its behalf -- is that the file adapter is verified to be a FILE adapter. reference_ports/journal_file.py:22 asserts 'Durable, append-only' and reference_ports/domain.py:39 names the port for durability, and no case anywhere observes a byte on disk. The honest limit the tree does state is reference_ports/README.md:68-77 (does not show an arm would produce this shape; n=1; cheap to reach is not evidence anybody would reach it).

**Rationale:**

ANCHOR 3, taken under the caveat's second sentence verbatim, and I executed the condition rather than reasoning about it.

ANCHOR 3 IS FULLY MET AND THE SWAP IS NAMED. reference_ports/domain.py:20-23 imports dataclasses and typing and nothing else -- no pathlib, no os, no io. The port is declared in the domain's own vocabulary at :38-58 and the domain calls it at :125, :150 and :172 and holds it as an opaque constructor argument at :108. THE SPECIFIC SWAP: reference_ports/quota_ledger.py:25 passes FileJournal(ledger_path); reference_ports/quota_ledger_fake.py:38 passes InMemoryJournal(); reference_ports/domain.py is byte-identical across the two and neither adapter module imports the domain, so the dependency runs one way. This is a RUNTIME claim, not an import claim, and I checked it at runtime: I seeded the same semantic fault (drop the first line from lines()) on each side of the port. In journal_file.py it killed 7 of 28 cases under QUOTA_LEDGER_IMPL=quota_ledger and 0 of 28 under quota_ledger_fake; in journal_memory.py the rows swap exactly. Each adapter is reached only through its own composition point, and running the same suite through both is a real instrument -- it converts two blind regions into two covered ones.

WHY NOT 4. The caveat: 'if the only observer of the effect the port exists for is the adapter that wrote it, say so and take 3.' The port exists for durability (reference_ports/domain.py:39, :56). The only reader of the file is reference_ports/journal_file.py:36, the same class that wrote it at :32. tests/test_behavior.py never opens the path -- tmp_path appears once, at :43, where it is handed to the constructor and never touched again; snapshot() at :53 reads the ledger back through ledger_lines() -> the port. So I replaced FileJournal's body with a plain list and ZERO filesystem contact: all 28 cases pass under the real wiring, and running the suite with --basetemp shows 28 ledger.txt files created at baseline and 0 created by the mutant. The 'real' adapter can stop being real without a single case noticing. It is not a fake-and-a-fake by construction -- journal_file.py:30-34 genuinely writes -- but it is a real adapter whose realness no shared oracle observes, which is the condition the caveat names. Take 3.

TWO THINGS THAT SHARPEN THIS. First, reference_ports/journal_file.py:30 TRUNCATES on construction and nothing ever reopens an existing ledger, so 'durable' here has never meant longer than one object's lifetime -- the same lifetime the fake offers, which is what reference_ports/journal_memory.py:34 calls the thing that makes it a fake. Second, under the fake wiring ledger_path is accepted and discarded (quota_ledger_fake.py:37-38), so FEATURE.md:21's 'the ledger file starts empty' is satisfied by never creating a file, and no case can tell.

PROSE: rule 4 applied. reference_ports/quota_ledger.py:9 says 'so the claim is not a claim' about the swap. On the swap it is correct and I gave it the rung. On durability the same confident register is carrying an unverified property, and the register earned it nothing.

## Your recorded notes — no score

### N-D1 — bug detection

**Citations** (`file:line`):

- `tests/test_behavior.py:65`
- `tests/test_behavior.py:118`
- `tests/test_behavior.py:165`
- `tests/test_behavior.py:247`
- `tests/test_behavior.py:43`
- `tests/test_behavior.py:53`
- `reference_ports/domain.py:122`
- `reference_ports/domain.py:102`
- `reference_ports/journal_file.py:32`
- `reference_ports/journal_file.py:36`
- `FEATURE.md:29`

**Note:**

SEEDED, six faults, all listed in judging_practice.

WHAT THE CASES CAUGHT. Real behavioral faults on the paths the suite walks. M6, an off-by-one in the quota guard at reference_ports/domain.py:136, died 3/28 under both wirings. M2, a dropped ledger line in reference_ports/journal_file.py:36, died 7/28 under the real wiring. M3, the identical fault in reference_ports/journal_memory.py:42, died 7/28 under the fake wiring. The mirrored M2/M3 pair is the artifact's own central claim and it holds: running the same expected-value suite through both composition points gives a fault in EITHER adapter somewhere to be seen, and neither adapter is reachable through the other's wiring.

CLASS ONE THAT IS DEMONSTRABLY MISSED -- ORDERING OF outstanding_ids(). The query is asserted four times in the whole suite (tests/test_behavior.py:65, :118, :165, :247) and three of those expect []; the fourth expects ['r1']. A one-element list has no order, so the 'ascending' half of FEATURE.md:29 is never exercised at all. M4 -- reference_ports/domain.py:122 returning sorted(..., reverse=True) -- passes all 28 cases under both wirings. And this is not only a mutant: the UNMUTATED artifact sorts lexicographically, so with 11 live reservations it returns ['r1','r10','r11','r2','r3',...]. Whether that is a defect turns on whether 'ascending' means numeric for ids the same file allocates as r1, r2, r3 (FEATURE.md:49-50); my point for this note is that the suite cannot form an opinion either way, because it never puts two reservations outstanding at once and looks.

CLASS TWO -- ANYTHING ABOUT THE DURABLE MEDIUM. tests/test_behavior.py:43 hands tmp_path to the constructor and no case ever opens the resulting file; every ledger assertion goes back through ledger_lines() at :53, i.e. through the same port that wrote it. M1 gutted every filesystem call out of reference_ports/journal_file.py:32-38 and all 28 cases passed. Append-only-ness, on-disk line format, and the file existing at all are unobservable to this suite by construction, not by oversight.

CLASS THREE -- DEAD STATE. M5 corrupted every value in _quota at reference_ports/domain.py:102 to -999 and nothing failed, because only the key set is ever read.

THE SHAPE OF THE MISSES IS THE FINDING. The artifact's thesis (reference_ports/journal_memory.py:7-27) is that the port creates a blind region on the FAKE side, and it closes that one. M4 and M5 are blind regions in the DOMAIN, on both wirings at once, which the second composition point does nothing for; M1 is a blind region in the REAL adapter, which it also does nothing for. Two composition points doubled the coverage of one fault class and left the other two exactly where they were.

### N-D4 — behavior preservation

**Citations** (`file:line`):

- `reference_ports/domain.py:8`
- `reference_ports/domain.py:130`
- `reference_ports/domain.py:139`
- `reference_ports/domain.py:156`
- `reference_ports/domain.py:165`
- `FEATURE.md:25`
- `FEATURE.md:40`
- `FEATURE.md:66`
- `FEATURE.md:72`
- `FEATURE.md:91`
- `tests/test_behavior.py:117`
- `tests/test_behavior.py:159`

**Note:**

THE BASELINE THE ARTIFACT NAMES IS NOT ONE I MAY READ, so I could not check its claim and I did not try. reference_ports/domain.py:8-10 asserts the behavior is ../reference/quota_ledger.py's 'statement for statement'. That tree is outside my read list. I enumerated against FEATURE.md instead, which is inside it and is the requirement either way. Recording the substitution rather than papering over it.

ENUMERATED, AND WHERE EACH STANDS.
1. available/committed/is_closed/ledger_lines (FEATURE.md:25-30) -- hold; reference_ports/domain.py:112-125, exercised throughout.
2. outstanding_ids ascending (FEATURE.md:29) -- NOT SHOWN TO HOLD, and at 10+ live reservations the unmutated tree returns r1, r10, r11, r2 (see N-D1). This is the one enumerated behavior I would not sign.
3. reserve's four rejections IN THAT ORDER (FEATURE.md:40-45) -- the guards at reference_ports/domain.py:130-137 are in the stated order by inspection, but the ORDER is untested: no case supplies an input that trips two guards at once (reserve('nobody', 0) would separate unknown_tenant from amount_not_positive and does not appear).
4. close's three rejections in order (FEATURE.md:76-81) -- reference_ports/domain.py:165-170 by inspection; likewise untested for order.
5. ids r1, r2, r3 in acceptance order, never reused (FEATURE.md:49-50) -- holds: _next_id only increments at :139 and neither commit nor release ever returns an id to the pool. Tested at :69-72 for allocation; reuse is covered only indirectly by :148-153.
6. commit appends exactly one COMMIT line with the running total (FEATURE.md:57-62) -- holds, reference_ports/domain.py:150-153, tested at :112-137.
7. commit does NOT return the amount to available (FEATURE.md:66) -- holds, and this one is asserted explicitly with a message at tests/test_behavior.py:117.
8. release writes nothing (FEATURE.md:72) -- holds; reference_ports/domain.py:156-162 has no journal call at all, asserted at tests/test_behavior.py:166.
9. close appends exactly one CLOSE line (FEATURE.md:82-87) -- holds, :172.
10. R1 conservation (FEATURE.md:91) -- holds; and note it holds because available is stored and hand-maintained to make it hold, not because it is derived. See D2.
11. R4, a rejection changes nothing (FEATURE.md:100) -- holds structurally: every guard in all four commands returns before any mutation, and each rejection path is snapshot-compared.
12. R5, append-only and ordered (FEATURE.md:103) -- holds in the domain's call order, but see M1: the append-only-ness OF THE FILE is not observable to this suite, so what is preserved is the order ledger_lines() reports, not the order bytes reached a disk.

So: eleven of twelve enumerated behaviors hold against FEATURE.md; one (ordering of outstanding_ids) does not hold at scale and is invisible to the suite; and the artifact's own preservation claim, against ../reference/, is one I am not permitted to evaluate and therefore did not.

### N-D5 — honesty

**Citations** (`file:line`):

- `reference_ports/README.md:66`
- `reference_ports/README.md:68`
- `reference_ports/README.md:71`
- `reference_ports/README.md:75`
- `reference_ports/quota_ledger_fake.py:14`
- `reference_ports/quota_ledger_fake.py:21`
- `reference_ports/journal_memory.py:22`
- `reference_ports/domain.py:39`
- `reference_ports/journal_file.py:22`
- `reference_ports/quota_ledger.py:9`

**Note:**

IT REFUSES, AND THE REFUSALS ARE THE UNUSUAL KIND -- specific, load-bearing, and against its own interest.

reference_ports/README.md:68-77 is a 'What this tree does NOT settle' section that gives up three things a weaker artifact would have kept: that the shape says nothing about whether an ARM would produce it; that n=1 and the tree shares an author with the catalogue that seeds into it, and that two trees does not reduce that bias; and -- the sharpest one -- that quota_ledger_fake.py being four lines is evidence the blind region was CHEAP to reach and explicitly not evidence anybody would have reached it, 'Nobody did, for a whole epic, and that is the measured fact.' README.md:66 and quota_ledger_fake.py:21-22 both refuse a verdict role outright: 'Nothing here gates, refuses, or reports a verdict. It is a fixture.'

THE BEST REFUSAL IS A NEGATIVE DESIGN DECISION WITH ITS REASON. quota_ledger_fake.py:14-20 declines to write a test asserting the two wirings agree, and says why: 'A test that only compares two wirings of one domain passes when the domain is wrong, because both wirings are wrong together.' That is correct, it is the trap this tree was most likely to fall into, and it is refused in the code rather than apologised for in prose. reference_ports/journal_memory.py:22-27 similarly explains the blind region mechanically instead of asserting it.

WHERE THE REFUSAL IS ABSENT -- AND IT IS ABSENT AT EXACTLY THE POINT I BROKE. Nothing anywhere names the limit M1 exposes. reference_ports/domain.py:39 names the port 'the durable, append-only record'; reference_ports/journal_file.py:22 says 'Durable, append-only, one line per entry'; reference_ports/README.md:53 calls it 'the real adapter: a file on disk'. All three are stated flatly and none is qualified by the fact that no case observes a byte on disk -- and journal_file.py:30 truncates on construction, so nothing here survives a process either. reference_ports/quota_ledger.py:9 goes furthest: 'so the claim is not a claim.' For the swap that sentence is earned. For the adapter being real it is not, and the artifact does not distinguish the two.

SECOND ABSENCE. journal_memory.py:7-27 and README.md:14-24 present the blind region as a property of the FAKE side specifically. M4 and M5 show equally invisible faults in the DOMAIN, reachable by every wiring and killed by none. The artifact never claims to have closed those, so this is under-scope rather than a false certification -- but a tree this careful about naming what it cannot see does not mention that the region it maps has a domain-side half.

Net: it refuses rather than falsely certifies, on everything it looked at, and it did not look at whether its real adapter is real.

## Verdict

Genuine ports and adapters -- the domain imports no I/O, the swap is executed rather than asserted, and two composition points over one suite really do give a fault in either adapter somewhere to die -- but the file adapter can be emptied of every filesystem call and all 28 cases still pass, so the durability the port is named for is observed by nobody outside the adapter that writes it, and the blind region this tree was built to close also has a domain-side half it does not mention: outstanding_ids() can be returned in reverse and the suite is silent.

## Disclosures

**What I ran, and that it changed nothing in the tree.** I copied the artifact to
`scratchpad/judge-v5-p1/` and mutated only the copy. The artifact directory and
`examples/validation/ab/` were never edited. Six seeded faults, one non-mutant probe,
one control; all listed under judging practice above. The scratch tree was restored and
re-run green (28/28 both wirings) after the last mutant.

**What I saw that I was not meant to see.** To confirm my `file:line` citations resolve
in `examples/validation/ab/` I ran `ls` and `diff -rq` there. That printed the NAMES of
sibling paths — `arm_a`, `arm_b`, `arm_c`, `seeded_faults.toml`, `check_catalogue.py`,
`model/`, `eval/`, `revision/`, `scorecard_shape/`, `reference/`. I opened none of them
and I read no line of any of them. Names only, and I am recording it because a judge who
now knows there are three arms and a fault catalogue is not quite the judge who started.
I did not open `references/eval_scorecard.md`, any other scorecard, any `*-EPIC.md`, or
`specs/desired_program_model/`. The one prior result that reached me came from inside the
artifact itself: `reference_ports/journal_memory.py:11-16` and `README.md:19-24` quote
`BA-B14` and the finding that arm B's fake is verified by nothing. I could not avoid that
without refusing to read the artifact, and it plainly primed me to go looking at the
adapter boundary. My M1 result is not that quote — it points the opposite way, at the
REAL adapter — but the direction I was looking came from the artifact's own advocacy.

**REJECTED — the line of reasoning I abandoned.** I spent longer on D2 = 1 than on any
other question and dropped it. The evidence for 1 was real and I proved it by execution:
`reference_ports/domain.py:102` stores `_quota` and `:103` stores `_available` from the
same mapping, and corrupting every value in `_quota` to `-999` leaves all 28 cases green
under both wirings — dead duplicated state, which is precisely the "one fact stored twice"
the D2 read_first sends a judge to look for. I dropped it because anchor 1's text is
*factually false about this artifact*: it describes figures measured and reported without
an argument, and nothing here measures anything at all. Taking the lower rung would have
meant asserting something untrue in order to look strict. I record the near-miss instead
of banking it, and I flag the structural reason 3 was never reachable: **the D2 ladder's
bottom two rungs are about measurement and its top two are about design, so an artifact
that measures nothing has no rung below 2 that describes it.** That is a property of the
instrument, not of this tree.

**REJECTED — "the read list forbids the diff the rung requires."** D2's read_first says
*diff the two trees yourself*. The second tree is `../reference/quota_ledger.py`, which my
instructions place off-limits. I considered treating that as a defect in the artifact
(no before/after figures → cap at 2) and I considered reading the other tree anyway. I did
neither: I scored what was in front of me and am naming the contradiction here instead.
A rung that requires a comparison a judge is forbidden to make is unreachable by
construction, and no artifact can fix that.

**REJECTED — scoring D3 = 4.** The letter of anchor 4 is satisfied and I nearly took it:
one driven port, a real adapter and a fake, and the *same* suite green against both — I
ran it. What stopped me was the caveat's second sentence, and I tested it rather than
argued it. I replaced `FileJournal`'s body with a plain list and zero filesystem calls;
28/28 still passed, and `--basetemp` showed 28 `ledger.txt` files created at baseline
against 0 under the mutant. The only observer of the durability the port exists for is the
adapter that wrote it. Take 3.

**A claim I tested and could NOT break.** The artifact's central claim — that the second
composition point converts an unreachable region into a reachable one — is true, and I
tried to falsify it. The same semantic fault seeded on each side of the port gave exactly
mirrored rows (real wiring 7 failed / fake wiring 28 passed; and the reverse), so neither
adapter leaks into the other's wiring and running both wirings genuinely doubles the
reachable surface for that fault class. `reference_ports/quota_ledger_fake.py:14-20` also
refuses to write a wirings-agree test, on the grounds that such a test passes when the
domain is wrong — I went looking for the lazy parity test and it is genuinely not there.
Both claims survived.

**The finding I did not expect, and the one I would carry forward.** The tree argues the
port's blind region lives on the fake side. It has a domain-side half nobody mentions:
`sorted(self._outstanding, reverse=True)` at `reference_ports/domain.py:122` passes all 28
cases under **both** wirings, because `outstanding_ids()` is asserted four times and three
of those expect `[]`. Two composition points do nothing for that fault — it is blind on
every wiring at once. And the unmutated tree already sorts lexicographically, so at eleven
live reservations it returns `r1, r10, r11, r2, …`. Second composition points buy adapter
coverage; they buy nothing at all in the domain.

**Prose.** Rule 4 was live throughout and I am naming it because it was a real pull. This
tree is written to persuade — `quota_ledger.py:9` "so the claim is not a claim",
`quota_ledger_fake.py:7` "THIS FILE IS AN INSTRUMENT, NOT A CONVENIENCE",
`journal_memory.py` at 21 of 43 lines advocacy. Both scores are what the 83 lines of
executable code support, and one of them is capped by a mutant that ignores every word.
