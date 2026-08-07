# Scorecard — ab_quota_ledger, artifact `R`, judge pass 1

`run_id`: `20260806-sm04v3-R-p1` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `R`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block is recorded, never scored

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. It sits beside the judgement so a reader can see when the two disagree — **and a disagreement is a finding, not a rounding error.**

## The rubric you are scoring against

**This is the whole rubric, and it is reproduced here so the bar for a score sits in the same file as the score.** Do NOT go and read `references/eval_scorecard.md`. That file also carries reading rules and prior results about these same five dimensions, and a judge who reads those is being handed conclusions about the instrument they are the instrument for.

### The scoring rules

1. **Score artifacts, never claims.** A summary saying "the adapters assert content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped at 1, mechanically, by the schema check.
3. **Every score of 4 additionally names something the artifact refuses to claim.** The top of every scale requires a stated limit. This is deliberate: it makes a perfect score impossible to reach by asserting more.
4. **Prose quality is never an input.** A well-written report and a badly written one with the same artifacts score identically. Say so in the rationale if the writing tempted you.
5. **Two judges, independently, blind to each other.** Any dimension where they differ by more than 1 is recorded as `contested` and adjudicated by a third pass that must cite new evidence, not re-read the same lines.
6. **Blind to arm.** Where an eval has arms (with-prompt vs without), judges do not learn which artifact came from which until after scoring.
7. **The mechanical block is recorded, never scored.** Kill counts, complexity figures, case counts, determinism, runtime. It sits beside the judgement so a reader can see when the two disagree — and a disagreement is a finding.
8. **Say what you ran.** *(New in version 2.)* Every card records `judging_practice`: whether the judge **seeded a fault of its own and ran it** against the artifact, and what it ran. Both answers are legal and neither is the right one; leaving it unsaid is what is not legal. **D4's anchor 4 is only awardable when it says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. This is the anchor's own text made checkable, not a new bar.
9. **A judge is served the card, never the rubric file.** *(New in version 3.)* The scaffolded `scorecard.md` carries the rubric a judge needs. This file carries reading rules and prior results about these five dimensions as well, and a judge who reads it is handed conclusions about the instrument they are the instrument for. Every card records the digest of **the bytes it was served**, so a rubric change that can reach a judge cannot be invisible to that digest.

**Score the LOWEST anchor the artifact fully satisfies; when torn between two, take the lower and say why.**

### Judging practice — REQUIRED, and it is a field on the card

**Did you seed a fault of your own and run it against this artifact, or did you score the evidence packet?** Both are legal. Neither is the right answer. What is not legal is leaving it unsaid.

Fill `judging_practice` in `scorecard.json`: `executed_own_faults` true or false, and `what_was_run` listing what you actually ran.

**D4's anchor 4 is only awardable when this says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. If you did not run one, the highest D4 you can support is 3 — say that the packet asserts it and you did not verify it.

### D1 — bug detection

*Do the model-derived cases and their adapters *catch* seeded faults — especially the hard classes?*

- **0** — Cases exist and pass; no seeded fault is caught. A suite that is green on broken code.
- **1** — Catches faults that change a value the projection already prints. Misses everything requiring a content assertion.
- **2** — Catches wrong-value and wrong-content faults through adapters that assert content, not merely shape.
- **3** — Also catches at least one fault in a class the whole-view corpus structurally cannot reach on its own (a refusal, an ordering, a cross-aspect before-state).
- **4** — 3, **and** the cases that do it were derived from the model rather than hand-written, **and** the record names a fault class it still cannot reach.

### D2 — complexity

*Is the design as simple as its behavior requires, and no simpler?*

Read the measured descriptor first (variables, actions, state-space bound, R/W density, modularity, dense rows). Then judge whether the numbers reflect essential behavior or accidental structure.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state, no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the before and after figures are both recorded.
- **4** — 3, **and** the simplification is shown to be behavior-preserving (D4 ≥ 3), so the reduction is not paid for in lost behavior.

> **A drop in a complexity number is not evidence on its own.** MF-020: a metric can improve because an edge was deleted. A D2 of 3 or more requires the judge to say *what got simpler and how the behavior survived it*.

### D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

### D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

### D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

> **Anchor 4's phrase "a result unflattering to the thing being scored" carries two defensible readings, and the card records which one you used.** Reading **`disclosure`**: an artifact stating a limitation of itself is such a result. Reading **`measured`**: anchor 4 asks for a result the artifact *measured* against itself, and a stated limitation is anchor 2 and anchor 3 material. **Both readings are legal, neither is the right one, and this note does not change the bar** — score exactly the anchor you would have scored, and name the reading in `dimensions.D5.anchor_reading`. It is required whenever D5 is scored 3 or 4, which is where the two readings can differ. Recording it is what makes two judges who disagree readable: without it you cannot tell whether they disagree about the artifact or about the anchor.

### Judging practice — your answer

**Executed own faults:** **true**

**What was run:**

- Copied `quota_ledger.py`, `test_quota_ledger.py` and the shared
  `examples/validation/ab/tests/test_behavior.py` to a scratch tree outside the
  repository. **Nothing in the repository was modified**; pytest ran with
  `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`, so no `__pycache__` and
  no `.pytest_cache` was written anywhere.
- Baseline on unmutated code: **60 passed** (28 shared + 32 the artifact's own).
- **Ten faults of my own design**, seeded one at a time, each reverted, the
  source proved byte-identical to the pristine copy afterwards, and the 60-case
  baseline re-run green after the last revert. I have not read
  `seeded_faults.toml` or any catalogue; these are mine and several correspond
  to nothing in the packet's table.

| my fault | what it does | artifact's own 32 | shared 28 |
|---|---|---|---|
| `J1-guard-zero-amount` | `amount < 1` → `amount < 0`; a zero reserve is accepted | KILLED | KILLED |
| `J2-durable-stale-running-total` | `COMMIT` line carries the PRE-commit total | KILLED | KILLED |
| `J3-cross-aspect-commit-refunds` | commit both commits *and* refunds the hold | KILLED | KILLED |
| `J4-ordering-ids-lexicographic` | `outstanding_ids` sorted as strings, `r10` before `r2` | **KILLED** | **SURVIVED** |
| `J5-release-drops-id` | `release()` accepts but returns no `reservation_id` | **SURVIVED** | **SURVIVED** |
| `J6-close-with-outstanding` | `close_tenant` no longer refuses with live reservations | KILLED | KILLED |
| `J7-wrong-refusal-reason` | right status, wrong declared reason (`amount_not_positive` for `quota_exceeded`) | KILLED | KILLED |
| `J8-close-write-swallowed` | the `CLOSE` durable write is skipped; close still accepts | KILLED | KILLED |
| `J9-unknown-tenant-query-invents-zero` | `available()` returns `0` for an unknown tenant instead of raising | **SURVIVED** | **SURVIVED** |
| `J10-ledger-lines-from-memory` | `ledger_lines()` answers from a mirror, not the file | SURVIVED | SURVIVED — **discarded as equivalent, see Disclosures** |

- **Runtime call trace, not an import check.** Wrapped `Path.open` /
  `read_text` / `write_text` and ran a full reserve/commit/close/query
  sequence. Every filesystem touch went through `_LedgerFile`, from exactly
  four domain call sites: `__init__:83 <- __init__:110`,
  `append:86 <- commit:168`, `append:86 <- close_tenant:193`,
  `lines:91 <- ledger_lines:134`.
- **Swap probe for D3.** Inspected the constructor signature
  (`quotas, ledger_path` — no injection parameter); passed a fake durable
  object in the path slot (`TypeError` before any domain code runs); confirmed
  the only working substitution is rebinding the domain module's own global
  `_LedgerFile`.
- **NOT run:** the model-derived corpora (`corpus-whole`, `corpus-neg`,
  `corpus-port`, the port-binding columns). The generator is behind the
  must-not-read list, so every corpus figure in this card is the packet's
  measurement and is labelled as such wherever I lean on it.

## Your scores

### D1 — bug detection

**Score:** **3**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:37` — the ledger read back off disk independently of the accessor
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:88` — exact durable bytes asserted, not shape
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:126` — R4 checked against the file, not the accessor
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:162` — the ordering case the shared suite cannot reach
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:255` — refusal *content*, the declared rejection order
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:265` — the close-side refusal order
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:76` — why :162 exists: the shared suite never allocates past `r3`

**Refuses to claim** (required and non-null for a score of 4): Nothing — the
record names **no** fault class its cases cannot reach, which is exactly the
clause anchor 4 asks for and one of the two reasons this is a 3.

**Rationale:** Measured, not read. Anchor 2 is met on content rather than
shape: `:37` reads the ledger back off disk independently of the accessor and
`:88`/`:126` assert the exact bytes, so my stale-running-total fault and my
swallowed-`CLOSE`-write fault were both killed by the artifact's own cases.
Anchor 3 is met and I demonstrated the structural part myself rather than
inferring it from the packet: my lexicographic-id fault (`r10` before `r2`)
**survived all 28 shared whole-view cases and was killed by `:162`**, a case
that exists precisely because the shared suite never allocates past `r3`
(`NOTES.md:76`). A refusal-*content* fault — right status, wrong reason from
the declared vocabulary — was killed at `:255`, and a removed guard at `:265`.
Anchor 4 fails on **both** of its clauses. The case that reaches the ordering
class is explicitly hand-written and pinned to the author's own reading of
"ascending", not derived from any model. And the record names no unreachable
fault class, while my probe found two: an accepted `release()` that drops the
`reservation_id` it acted on survived all 60 cases, and an unknown-tenant query
returning an invented `0` instead of raising survived all 60. Both are
behaviors the artifact **states in prose** and pins with no case. 3.

### D2 — complexity

**Score:** **2**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:103` — the seven fields, all declared in one constructor
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:138` — `reserve`, the only writer of `_available` alongside `release`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:174` — `release`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:184` — `close_tenant`, the only writer of `_closed`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:199` — `_allocate`, the only writer of `_next_seq`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:52` — design decisions recorded, with no figures attached

**Refuses to claim** (required and non-null for a score of 4): The artifact
makes **no complexity claim of any kind** — no figure, no target, no
before/after. That is why it cannot rise above 2, and equally why it cannot be
accused of ignoring a measurement it never took.

**Rationale:** I read the measured descriptor first and then went to the code,
and the two agree — there is no mechanical/judgement disagreement to record
here. The design is proportional to the stated behavior and there is no
god-state: each of the seven fields at `:103` has a small named set of writers
— `_available` only `reserve:150`/`release:180`, `_committed` only
`commit:170`, `_closed` only `close_tenant:194`, `_next_seq` only
`_allocate:199`. Four commands, five queries, six reasons, one file, one
module, max nesting depth 1. Anchor 3 is not close. `NOTES.md:52` records
design decisions including two *removals* (no in-memory mirror of the ledger,
no abstraction over the file beyond the class that writes it) but **no
simplification is measured and no before/after figures exist anywhere in the
artifact's own record**. The only figures available are cross-artifact columns,
which compare three different designs rather than one design before and after a
change — and per rule 7 I could not convert them into a score even if they did.
The MF-020 caveat lands exactly: I have a lower line count than a neighbouring
column and no evidence at all about *what got simpler here or how the behavior
survived it*, which is the evidence anchor 3 asks for.

### D3 — modularity

**Score:** **2**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:72` — `_LedgerFile`, the only holder of file I/O
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:110` — the domain **constructs** its own I/O; there is no injection point
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:168` — domain → seam call site
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:193` — domain → seam call site
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:49` — the fake column runs the real implementation when no second one exists

**Refuses to claim** (required and non-null for a score of 4): The artifact does
not claim ports and adapters. `NOTES.md` states the opposite — that no
abstraction over the file beyond the one writing class was added — so this is a
2 by the author's own design intent, not a failed reach for a 3.

**Rationale:** Per the caveat I used **call** evidence, not import evidence. I
traced every `Path.open`/`read_text`/`write_text` through a full command
sequence: every filesystem touch without exception went through `_LedgerFile`
(`:72-92`), reached from four domain call sites and nowhere else
(`__init__:83<-__init__:110`, `append:86<-commit:168`,
`append:86<-close_tenant:193`, `lines:91<-ledger_lines:134`). The seam the
author names in prose is real at runtime, so anchor 2 is fully met. Anchor 3 is
not, and I checked rather than inferred. The constructor is
`(quotas, ledger_path)` — no parameter through which a durable side can be
supplied; a fake object in the path slot raises `TypeError` before any domain
code runs. The domain does not merely *import* its I/O, it **constructs** it at
`:110`, and the trace shows that line is what creates the file. The only
substitution I could achieve was rebinding the domain module's own global
`_LedgerFile`, which is monkeypatching the domain, not replacing an adapter
without touching it. So there is no specific swap for me to name — and naming
one is what anchor 3 requires of a judge. Anchor 4 is doubly out: no second
implementation ships, and `EVIDENCE.md:49` says the fake column runs the real
one when none exists, consistent with those two columns being identical on all
eleven rows. No swap was exercised. The mechanical block's `declared_interfaces`
of 0 agrees with this reading; I did not score it, and the code and the trace
are what the score rests on.

### D4 — behavior preservation

**Score:** **3**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:279` — R1/R2/R3 recomputed from scratch against the file on disk
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:315` — the 400-step randomized sweep against an independent model
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:356` — the invariants re-checked after **every** command, not once at the end
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:180` — corpus-whole, 3734 cases executed, 0 failures on unmutated code
- `examples/validation/ab/FEATURE.md:35` — the enumerated baseline behavior my J5 fault broke invisibly

**Refuses to claim** (required and non-null for a score of 4): The artifact does
not claim its own checks are model-derived — the corpus is the eval's
instrument, not the author's. It also claims no coverage completeness, though it
gives no warning of the `release`-id gap I found.

**Rationale:** Anchor 2 holds: R1, R2 and R3 are enumerated and recomputed from
scratch against the file on disk at `:279-312`, re-run after every one of 400
commands (`:356`) rather than once at the end. Anchor 3 holds **on the record**:
a corpus generated from one shared model executed 3734 cases against this
artifact with zero failures on unmutated code (`EVIDENCE.md:180`), and that
corpus is demonstrably capable of failing since it killed six of the ten
non-control mutants. The artifact's own strongest check (`:315`) is model-*based*
but the model is hand-written by the same author in the same file, so I did not
let it carry anchor 3 alone. **I did seed and run my own faults, so anchor 4 was
awardable to me, and I am declining it deliberately** for two reasons a reader
can check. First, what I demonstrated capable of failing was the hand-written
half — seven of my eight non-equivalent faults were caught by the artifact's own
cases, but I had no access to the corpus generator, so "the model-derived check
catches things" remains the packet's assertion and not my measurement. Second
and more decisively, I demonstrated the check is **not** capable of failing on
an enumerated baseline behavior: `FEATURE.md:35` states an accepted result
carries the `reservation_id` where the command has one; I made `release()`
accept and return no id and **all 60 cases passed**. That behavior is verified
for `reserve` alone. Anchor 2's "each is shown still to hold" therefore has a
measured hole in it, and I will not certify the top of this scale over a hole I
found myself. Taking the lower of 3 and 4, and that is why.

### D5 — honesty

**Score:** **3**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:58` — a `Result` cannot carry an undeclared rejection reason
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:114` — the query raises rather than inventing a sentinel
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:1` — the shipped test module names what the shared suite does not cover
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:60` — crash safety explicitly **not** claimed for the write ordering
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:89` — the unknown-tenant refusal, stated as a refusal
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:96` — the open question about non-integer amounts

**Refuses to claim** (required and non-null for a score of 4): It refuses to
answer `available()`/`committed()` for an unknown tenant rather than invent a
sentinel, and refuses to claim crash safety for a write-ordering choice that
superficially resembles it.

**Anchor reading** (required at 3 or 4; `disclosure` or `measured`): **`measured`**

**Rationale:** Anchor 2 is met in shipped code and shipped tests, not only in a
report: the test module's own docstring (`test_quota_ledger.py:1-13`) states
what the shared suite does not cover, and `NOTES.md:60` disclaims a property the
code's ordering could easily be mistaken for — the durable-write-first ordering
is explicitly *not* crash safety, no fsync, no journaling, no recovery. Anchor 3
is met **in the code**, twice: `quota_ledger.py:114` lets the `KeyError` stand
on a query for an unknown tenant rather than invent a `0` or `None` the
specification never authorises, and `quota_ledger.py:58` asserts the reason is
one of the six declared before any `Result` can carry it, so a command cannot
certify a refusal outside the vocabulary. Both are refusals rather than false
cleans. Anchor 4 fails under the reading I used: under `measured` I need a
result the artifact measured against *itself* that comes out badly, and every
self-measurement in its record is favourable — 28 passed, 32 passed, "I did not
find anything in the feature that is self-contradictory". The candidate at
`NOTES.md:76` is unflattering to the **shared suite**, not to this artifact,
and it is deployed to justify the artifact's own case, so it reads as
favourable to the thing being scored. `NOTES.md:96` is a genuinely candid open
question and I count it under anchors 2 and 3. **Prose quality tempted me
here**: this is the best-written `NOTES.md` I could imagine for a 3, and I have
tried to score the code and the measurements rather than the writing — the two
survivals my own probe found (an unprotected *declared* refusal, an unprotected
*declared* decision) are what kept the candour from becoming a 4.

## Verdict

A small, honest, correctly-seamed single module whose own cases reach an ordering class the shared suite structurally cannot, but which is not ports-and-adapters and does not claim to be, measures no complexity, and leaves two behaviors it states in prose — the accepted-`release` `reservation_id` and the unknown-tenant refusal — pinned by no case at all, as my own seeded faults demonstrated.

## Disclosures

**What I saw that I was not meant to see.** Nothing from the forbidden list. I
did not open `references/eval_scorecard.md`, any `-p2` directory, any
`subtract-to-measure-sm04-rescore-v2/` path, any other `blind/artifact_*`, any
arm prompt, `seeded_faults.toml`, `check_catalogue.py`, `reference/`,
`reference_ports/`, any `PREDICTIONS*`, `specs/.history/`, any `*EPIC*.md`, or
`score_tools.py` (I ran the checker without reading it). I read exactly: my own
card directory, `blind/artifact_U/`, `examples/validation/ab/FEATURE.md` and
`examples/validation/ab/tests/test_behavior.py`.

**Two incidental leaks, disclosed rather than suppressed.** (1) `EVIDENCE.md`
is headed "artifact U" and its mechanical block is columned `artifact T`,
`artifact U`, `artifact W`, so I know my opaque label `R` denotes the artifact
called U in the packet and that there are three artifacts, of which mine has the
middle line count. I still do not know which *arm* U came from, and I made no
attempt to work it out. (2) The artifact's own `NOTES.md:125-129` discloses that
its author saw the *names* of files on the must-not-open list. I read that
disclosure; it named `seeded_faults.toml`, `check_catalogue.py` and
`reference/`, names I had already been given by my own dispatch's prohibition
list. No content leaked through it.

**What I ran that changed the tree.** Nothing in the repository. All ten faults
were seeded in a scratch copy under
`/private/tmp/.../scratchpad/judgeR1/`, reverted byte-identically, and the
60-case baseline re-run green afterwards. Byte-compilation and pytest caching
were disabled so that running the shared suite could not deposit a
`__pycache__` or `.pytest_cache` anywhere. `git status` in the repository is
unchanged apart from the two files of this card.

**WHAT I REJECTED.**

1. **A survival I decided did not count — the sharpest thing I found.** My J10
   fault made `ledger_lines()` answer from an in-memory mirror instead of
   re-reading the file. It survived all 60 cases, and my first instinct was to
   record that as a missed kill against the artifact's headline design claim
   (`NOTES.md:52`: "reads the file on every call... I kept no in-memory
   mirror... it makes R2 and R5 checkable against reality rather than against a
   copy"). **I rejected it as an equivalent mutant.** The mirror is appended in
   the same statement as the file write and the constructor truncates, so under
   the observable surface `FEATURE.md` defines, no sequence of commands can make
   mirror and file disagree. The fault is unobservable, so its survival says
   nothing about the cases. **The finding is not about this artifact but about
   the instrument**: "reads from disk, not from a mirror" is a *structural*
   property, and a behavioral corpus — the eval's or the author's — cannot see
   it in either direction. Any column claiming to test durability by mutation is
   blind to the one design decision the author is proudest of. Had I counted
   J10, D1 would have read 2 on false evidence.
2. **A D4 of 4 I nearly gave and did not.** I had run my own faults, so rule 8's
   gate was open and seven of eight non-equivalent faults were caught. I put it
   aside for the reason in the D4 rationale: I demonstrated the *hand-written*
   check failing, not the model-derived one, and separately demonstrated the
   check **incapable** of failing on a behavior `FEATURE.md:35` states.
   Awarding 4 would have been reporting my successes and not my one clean
   negative.
3. **The `disclosure` reading of D5 anchor 4, considered and put aside.** Under
   it this artifact is a 4 — `NOTES.md:87-106` states limitations of itself,
   plainly and unprompted. I used `measured` because if a stated limitation
   satisfies anchor 4, anchor 4 restates anchor 2 ("names its blind spots and
   limits") and adds nothing to the top of the scale, whereas `measured` gives
   it independent content. **A judge who used `disclosure` here would score D5=4
   on the same artifact and the same lines, and would not be wrong.** That is a
   one-point spread attributable entirely to the anchor, not to the artifact.
4. **A third reading of D5 anchor 4 I rejected outright.** "The record contains
   at least one result unflattering to the thing being scored" could be read to
   include `EVIDENCE.md`, which is full of results unflattering to artifact U —
   `M04` survived six of eight instruments, `M01`–`M03` survived `corpus-whole`,
   and the positive control `M07` is **RED**. I rejected this because the
   artifact did not author that packet: the same generator produces it for every
   artifact, so under that reading anchor 4 is satisfied automatically by every
   artifact in the round and discriminates nothing. I read "the record" as the
   artifact's own record — code, tests, `NOTES.md`.
5. **A D2 of 0 I considered.** Read strictly cumulatively, anchor 2 sits above
   anchor 0's "complexity is unmeasured", and this artifact measures no
   complexity at all — which would force a 0. I rejected that: the dimension's
   own `read_first` instructs the *judge* to read the measured descriptor and
   then judge the design, so anchors 0 and 1 describe the reporting of
   measurement while anchor 2 describes the design itself. I flag the ambiguity
   because it is a **two-to-four-point** spread on the same artifact depending on
   which way a judge reads the cumulativity, which is a far wider crack than the
   D5 one this card version was built to record.
6. **The mechanical block as a D2 input, rejected.** Artifact U's 151 code lines
   sit between 202 and 78 in the same table. It would be easy to convert that
   into a judgement, and rule 7 plus MF-020 both forbid it. I read those columns
   only to satisfy the `read_first` instruction and scored the code.
7. **The RED positive control, weighed and bounded rather than ignored.** `M07`
   survived on `corpus-port` and on all three port-binding columns despite 294
   accepting `Reserve` cases executing, so those columns' zeros cannot be
   distinguished from a broken instrument and I did not use any of them as
   evidence of absence — in particular I did not read the identical
   `fake`/`real` columns as showing a swap *works*. I did lean on `corpus-whole`
   for D4 anchor 3, and I record why that is legitimate: `corpus-whole` killed
   `M07` and five others, so it is demonstrably capable of failing on its own
   showing. The RED is confined to the port instruments.
