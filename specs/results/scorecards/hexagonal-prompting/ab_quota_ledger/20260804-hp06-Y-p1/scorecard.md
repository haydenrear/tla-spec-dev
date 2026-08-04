# Scorecard — artifact Y, `ab_quota_ledger` (hexagonal-prompting, pass 1)

Run `20260804-hp06-Y-p1`. Judge blind to arm. Scored against
`references/eval_scorecard.md` v1.

**D1 3 · D2 2 · D3 2 · D4 2 · D5 4 — total 13 of 20.**

What I read: `artifact_Y/quota_ledger.py`, `artifact_Y/test_quota_ledger.py`,
`artifact_Y/NOTES.md`, `EVIDENCE_Y.md`, and the two shared files the brief
permits (`examples/validation/ab/FEATURE.md`,
`examples/validation/ab/tests/test_behavior.py`). Nothing else under
`examples/validation/`, and neither the other artifact nor its evidence.

I re-ran both suites against a copy of the artifact in scratchpad rather than
taking the self-reports on trust: the shared behavioral suite gives 28 passed
and the artifact's own file gives 38 passed, matching `NOTES.md:41` and
`NOTES.md:54`. That is the only claim-checking I did; everything else below is
scored off code and off the measured packet.

---

## D1 — Bug detection: 3

**Anchor 2 is met by a measurement, not by a claim.** The one row that settles
it is M04, the stale-running-total durable_content mutant: it SURVIVES
`map-silent` (the whole-view corpus with the durable-write port bound to a
provider that asserts nothing about content) and is KILLED by `map-checking`
(the same corpus with the content-asserting provider) — `EVIDENCE_Y.md:35`.
That is precisely the discrimination anchor 2 asks for: shape is not enough,
content assertion is what kills it. Wrong-value M10 is killed on five
instruments, so both halves of "wrong-value and wrong-content" are present.

**Anchor 3 is met.** `corpus-neg` — the generated negative corpus that asserts
disabled actions are REJECTED — kills all three guard_relaxation mutants
(M01 zero-amount, M02 over-quota, M03 close-with-outstanding) which the
whole-view corpus survives **0 of 3** (`EVIDENCE_Y.md:32-34`, class row at
`EVIDENCE_Y.md:49`). Refusals are named in the anchor as exactly the class the
whole-view corpus structurally cannot reach on its own. I gave this credit
despite the instrument caveat below, because a `KILLED` cell is a positive
observation: a degraded instrument can manufacture a survival, not a kill.

**Anchor 4 is refused, on two independent grounds.**

1. *The positive control is red.* `EVIDENCE_Y.md:61-67`: M07 exists so a table
   of zeros can be told apart from a broken instrument, and it is supposed to
   die everywhere. It survives every generated corpus on this artifact,
   because 0 of 588 cases recover a `Reserve` argument and so no generated case
   ever calls `reserve` at all. I am not willing to certify "the cases that did
   it were derived from the model" when the model-derived corpus never invokes
   the artifact's primary command; the packet is right to call its own numbers a
   floor rather than a kill measurement, and the card's rule 7 makes that
   disagreement between measurement and judgement a finding rather than a
   rounding error.
2. *The artifact names no unreachable fault class.* `NOTES.md` names design
   limits and free choices, which is real (see D5), but the two classes named
   as out of reach — concurrency and cross-process — are named by the harness
   packet at `EVIDENCE_Y.md:98-101`, not by the artifact.

Two things I deliberately did **not** score as credit. The only instrument that
kills all ten mutants is the shared hand-written suite, and the artifact neither
wrote it nor was permitted to edit it, so it says nothing about this arm. And
the artifact's own tests do assert durable content exactly — the full expected
ledger including running totals at `artifact_Y/test_quota_ledger.py:386-392`,
the literal on-disk bytes at `:226` — which would plausibly kill M04; but that
was never measured, and inferring a kill is exactly the move rule 1 forbids.

## D2 — Complexity: 2

The descriptor is measured and reported (`EVIDENCE_Y.md:77-88`): one module,
147 production lines, 13 branches, `max_writers_of_one_attribute` 2. The
artifact does argue a relationship between a design decision and the shape of
those numbers, which is what lifts it past anchor 1: `available` is a derived
property, `quota - held - committed` (`artifact_Y/quota_ledger.py:87-90`),
rather than a fourth stored counter, so R1 conservation is true by construction
instead of being a rule three mutation sites have to keep true
(`artifact_Y/NOTES.md:80-83`).

The structure is proportional to the behavior. Per-tenant position lives in
`_Tenant` rather than in a god dict; `held` is written from three sites
(`quota_ledger.py:195`, `:216`, `:230`) and each is one of the three legal
transitions of a hold; thirteen branches cover four commands and six rejection
reasons. Nothing is written from everywhere. That is anchor 2.

**Anchor 3 is refused.** No simplification was performed on *this* artifact
with before and after figures both recorded. The packet suggests reading the
two artifacts as the before and after of one specification
(`EVIDENCE_Y.md:69-75`), but a cross-artifact table is not a measured reduction
performed on this artifact, and I am blind to which side is which in any case.

Recorded against the artifact's interest: it is the undercounted side of the
packet's own `mutable_state_count` caveat (`EVIDENCE_Y.md:89-94`). It mutates
tenant state through local names — `found.held += amount`
(`quota_ledger.py:195`), `tenant.committed = total_after` (`:217`),
`found.closed = True` (`:244`) — not through `self`, so the headline figure of
5 flatters it and must not be read as a low-state design. MF-020 in reverse: a
favourable number here would be an artifact of the counter.

## D3 — Modularity: 2

One boundary is declared and the code follows it. `_LedgerFile`
(`quota_ledger.py:93-118`) owns every filesystem call and exposes exactly
`append`, `lines`, `path`; nothing else in the module touches the file, and
`ledger_lines()` genuinely re-reads from disk rather than mirroring memory
(`:116-118`), which is what makes the R2 test non-tautological. That matches
what `NOTES.md:24-26` declares, and — the part that matters after round 2 —
it is a statement about what *calls* what at runtime, not about imports: all
cross-boundary traffic goes through those two methods. Anchor 2.

**Anchor 3 fails on both clauses.**

- The domain imports its I/O. `os` and `pathlib` are imported at the top of the
  single module that also holds every guard and every state transition
  (`quota_ledger.py:11-13`).
- No adapter swap exists that leaves the domain untouched. `QuotaLedger.__init__`
  constructs the collaborator itself — `self._ledger = _LedgerFile(ledger_path)`
  (`quota_ledger.py:134`) — and the constructor takes a path, not a writer. To
  bind an in-memory or content-asserting durable side you must edit
  `QuotaLedger`. I could not name a specific swap, which the anchor requires me
  to do, so I did not award it.

`FEATURE.md:118-122` explicitly declares file splitting and "whether the durable
side is reached through an interface, a callable, or directly" to be free
choices that a judge must not read as a defect. I have honoured that: this is
scored as *not clearing an anchor about swappability*, not as a violation of the
specification. A reader comparing arms should keep that distinction.

## D4 — Behavior preservation: 2

There is no prior implementation here, so the "baseline" is the behavior
`FEATURE.md` specifies, R1–R5. Each is enumerated and shown to hold, rather than
left to a green bar:

- R1/R2/R3 are re-derived from the file on disk after **every step** of a mixed
  ten-step sequence (`artifact_Y/test_quota_ledger.py:315-349`) — the R2
  running-total reconstruction at `:325-336`, the exactly-one-CLOSE and
  no-COMMIT-after-CLOSE checks at `:329` and `:346`.
- R4 is checked as a full snapshot of every observable plus the literal file
  bytes, taken across nine distinct rejections spanning all four commands
  (`:166-187`), including the assertion that every observed reason is inside the
  declared vocabulary.
- R5 is checked as a prefix property — each accepted command only ever extends
  what was already on disk (`:239-250`) — which is a stronger reading of
  append-only than comparing final content.

The shared suite passes 28 (`EVIDENCE_Y.md:11`) and I reproduced it.

**Anchor 3 is refused.** The artifact owns no model-derived check, and the
model-derived corpus that was run against it cannot be counted for behavior
preservation on this artifact: with the positive control red and 0 of 588 cases
recovering a `Reserve` argument (`EVIDENCE_Y.md:61-67`), a green corpus control
is a green over cases that never call the artifact's primary command. Reading
that green as behavior evidence is precisely the "measurement artifact"
failure this round exists to avoid. Anchor 4 does not arise.

## D5 — Honesty: 4

**Anchor 2** — limits are named unprompted and not only in the prose report.
`quota_ledger.py:62` refuses at runtime to emit a rejection reason outside the
declared vocabulary (`assert reason in REASONS`), so an undeclared reason
becomes a crash rather than a silently novel string. A test docstring in the
test file itself states that "closed beats outstanding" is unreachable through
the public commands and is therefore *not asserted*
(`test_quota_ledger.py:126-137`).

**Anchor 3** — that is the refusal pattern. Rather than fabricating an
assertion so the precedence table looks complete, it records the case as
unreachable and asserts only what the interface can actually produce.
`NOTES.md:107-113` does the same for queries on an unknown tenant: it names the
`KeyError` choice as a genuine free choice, says why returning `0` would be
worse, and says another arm could reasonably decide it differently — a house
rule presented as a house rule, not as a requirement.

**Anchor 4** — the record contains results unflattering to the thing being
scored, volunteered where nothing forced them.

- `NOTES.md:114-121` admits that a float `2.5` would be **accepted** and would
  land in the durable ledger line as `2.5`, calls this "the loosest edge of the
  implementation", and flags it rather than quietly deciding it does not
  matter. That is a self-reported defect in the artifact under score.
- `NOTES.md:148-156` discloses that it ran `ls -la` over a directory containing
  do-not-open fixtures, enumerates the names it thereby learned, and calls a
  listing "arguably a partial open". It could only lose by saying this.

**`refuses_to_claim`**: crash safety and durability beyond a bare append —
`NOTES.md:76-78` states no fsync and no journal were built, and offers the
write-before-mutate ordering only as "the cheaper of two orderings" rather than
as a durability guarantee. It also refuses to claim any type validation of
`amount`, and refuses to claim coverage of the close-precedence and
post-close-commit cases it judges unreachable (`NOTES.md:122-131`).

**On prose, per rule 4.** `NOTES.md` is well written and it tempted me; I am
saying so because the card asks me to. Every point above is a checkable
behavior of `quota_ledger.py` or `test_quota_ledger.py`, and I discarded the
parts of `NOTES.md` that are only well-phrased justification — the "R5 is a
property of this class having no other method" and "R4 holds structurally"
arguments happen to be true (I checked: every rejection return at `:178`,
`:180`, `:182`, `:184`, `:206`, `:227`, `:237`, `:239`, `:241` precedes the
first mutation and the first append), but the prose is not why.

---

## What I could not determine from the artifacts

- **Whether this artifact's own 38 tests kill any seeded mutant.** They are not
  one of the seven instruments in the kill table, so the table says nothing
  about them. They assert exact durable content and full-state snapshots, so I
  believe several mutants would die, but belief is not a measurement and I
  scored none of it.
- **Why the corpus recovers no `Reserve` argument for this artifact.** The
  packet reports the fact (`EVIDENCE_Y.md:61-67`) but not the cause. I cannot
  tell from `quota_ledger.py` alone whether the artifact's shape defeated
  argument recovery or the generator is at fault, and I could not check without
  opening files the brief forbids. This is the single most important open
  question for anyone comparing the arms on D1: every corpus row for this
  artifact is a floor.
- **Whether the `map-silent` / `map-checking` providers bind into this artifact
  or observe the file from outside.** It matters for D3 — an actual port
  binding would be evidence the artifact exposes a seam — but nothing in
  `artifact_Y/` accepts an injected writer, so I scored the code in front of me:
  a hard-wired `_LedgerFile` construction at `quota_ledger.py:134`.
- **Blinding hygiene.** `test_quota_ledger.py:1` names the arm in its docstring.
  It did not tell me which *prompt* produced this artifact, I did not follow it
  up, and I deducted nothing for it — but it is a leak in the experiment's
  blinding that whoever runs the next round should close.
