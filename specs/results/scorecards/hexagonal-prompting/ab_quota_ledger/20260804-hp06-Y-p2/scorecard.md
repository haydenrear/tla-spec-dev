# Scorecard — artifact Y, `ab_quota_ledger`, run `20260804-hp06-Y-p2`

Judge pass 2, blind to arm. Scorecard version 1. Commit
`f65bb9b3c8e3d4e2b5ca50e9d34c27611673c9af`.

**D1 2 · D2 2 · D3 2 · D4 2 · D5 3 — total 11 / 20.**

What I read: `artifact_Y/quota_ledger.py`, `artifact_Y/test_quota_ledger.py`,
`artifact_Y/NOTES.md`, `EVIDENCE_Y.md`, and the two shared files the prompt
permits — `examples/validation/ab/FEATURE.md` and
`examples/validation/ab/tests/test_behavior.py`. Nothing else under
`examples/validation/`, no other artifact, no other judge's output.

I also re-ran both suites myself rather than take the artifact's word for
them: the shared behavioral suite gives **28 passed** against this artifact
unmodified, and the artifact's own file gives **38 passed**. Both claims in
`NOTES.md:41` and `NOTES.md:55` are verified rather than accepted.

**On prose (card rule 4).** `NOTES.md` is the most persuasive document in this
bundle — it argues its own design, discloses a directory listing nobody would
have caught, and pre-empts several objections. It tempted me on D1 and D4 in
particular, where it reads as though a great deal was measured. It was not an
input. Every score below rests on code lines, test lines, or measured cells,
and where the notes assert something I could not see in an artifact I dropped
it.

---

## D1 — Bug detection: **2**

**Anchor 2 is fully satisfied, on a differential the broken control cannot
explain away.** `M04-durable-stale-total` SURVIVES `map-silent` and is KILLED
by `map-checking` (`EVIDENCE_Y.md:35`). The only thing that changes between
those two instruments is that one provider asserts the *content* of the
durable write and the other asserts nothing (`EVIDENCE_Y.md:26-27`), and the
`durable_content` class moves 1 of 2 → 2 of 2 across exactly that swap
(`EVIDENCE_Y.md:48`). That is the anchor's sentence, and it is a within-family
comparison — both sides run the same corpus, so whatever is broken about the
corpus is held constant and the difference is attributable to the content
assertion. Wrong-value is also represented: `M10-apply-only-double-refund` is
killed by `corpus-whole` and `corpus-slice-res` (`EVIDENCE_Y.md:39`).

**Anchor 3 is refused, and this was the closest call on the card.** On its
face the table satisfies it outright: `corpus-neg` kills all three
`guard_relaxation` mutants (`EVIDENCE_Y.md:32-34`) where the whole-view corpus
goes 0 of 3 (`EVIDENCE_Y.md:49`). That is precisely "a class the whole-view
corpus structurally cannot reach on its own — a refusal". I did not award it,
for two compounding reasons:

1. **The positive control is red on every corpus instrument for this
   artifact** (`EVIDENCE_Y.md:60-68`). `M07` exists so a row of zeros can be
   told apart from a broken instrument, and it survives everywhere in the
   corpus family. The packet says so itself and calls its own kill counts "a
   FLOOR reported under a broken instrument, not a clean kill measurement".
2. **The stated cause of that redness contradicts the cells I would be relying
   on.** The packet says the corpus recovers no argument for `Reserve`, so *no
   case that calls `reserve` ever executes* — yet `corpus-neg` is credited
   with killing `M03-guard-close-with-outstanding`, a mutant that is only
   reachable once a tenant *holds a live reservation*, which requires an
   accepting `reserve`. The same tension sits under `corpus-whole`'s kills of
   `M08` (commit refunds the hold) and `M06` (wrong status on release), both
   of which need a reservation to exist. Two parts of this packet cannot both
   be true.

Point 2 is a finding in its own right and I am recording it rather than
scoring around it. When a table and its control narrative disagree, the card's
tie-break says take the lower anchor, and the round's temper says a red
control is weighed against the numbers it produced rather than read at face
value. Both point the same way.

Two further things kept D1 off 4 independently of the above: the artifact
ships **no model-derived cases at all** — its 38 tests are hand-written, and
the corpora are harness-supplied and shared between arms — and **its own
record names no fault class it cannot reach**. The "not measured" section that
names concurrency and cross-process faults (`EVIDENCE_Y.md:96-101`) is the
harness's honesty, not the artifact's.

Citations: `EVIDENCE_Y.md:26-27`, `EVIDENCE_Y.md:35`, `EVIDENCE_Y.md:48`,
`EVIDENCE_Y.md:32-34`, `EVIDENCE_Y.md:60-68`.

---

## D2 — Complexity: **2**

The measured descriptor first (`EVIDENCE_Y.md:80-86`): 1 module, 147
production lines, 17 public names, 13 branches, 5 `self.<name>` assignments,
max 2 writers of any one attribute. The packet warns that one artifact's
`mutable_state_count` is an undercount because it mutates a dataclass through
a local name (`EVIDENCE_Y.md:88-94`), and that is true of this one:
`_Tenant.held` is written at `quota_ledger.py:195`, `:216` and `:230` — three
sites, none of which is a `self.` assignment, so none of which the figure
counts. **The 5 is not the real number.** Corrected, the picture still holds:
the widest-written field is confined to a single class, there is no god-state,
and the counts are proportional to four commands, five queries and one file
collaborator.

The genuine economy is real and load-bearing. `available` is a derived
property, `quota - held - committed` (`quota_ledger.py:86-90`), not a fourth
stored counter — so R1 conservation is true *by construction* rather than
maintained by three separate mutations, and `commit` is correspondingly one
subtraction and one addition (`quota_ledger.py:216-217`) with `available`
unmoved, which is what FEATURE.md:64-65 demands.

**Anchor 3 is refused.** The artifact records no complexity figures of its own
and no before/after pair for the derived-`available` decision or anything
else. The mechanical block's two columns are two independent implementations
of one specification, not a measured before and after of a change — nothing
was simplified *from* anything here. MF-020 is explicit that a number with no
measured predecessor is not a simplification result, and the card requires the
judge to say what got simpler and how behaviour survived it. I cannot, because
nothing was recorded as having been made simpler.

Citations: `artifact_Y/quota_ledger.py:86-90`, `artifact_Y/quota_ledger.py:195`,
`artifact_Y/quota_ledger.py:216-217`, `EVIDENCE_Y.md:80-86`,
`EVIDENCE_Y.md:88-94`.

---

## D3 — Modularity: **2**

A boundary is declared — `_LedgerFile`, "the durable side ... the only write
operation is an append" (`quota_ledger.py:93-118`) — and, unlike the round-2
failures this anchor was written against, **the code actually honours it at
runtime**. Every durable interaction in `QuotaLedger` goes through
`self._ledger`: the two appends at `quota_ledger.py:213` and `:243` and the
read-back at `:161`. No command opens, writes or stats a path itself; even
`ledger_path` delegates (`:163-166`). That single respected chokepoint is what
anchor 2 asks for, and it is a call-topology fact, not an import fact.

**Anchor 3 is refused on the code.** The domain and its I/O are the *same
module*; `os` and `pathlib` are imported at the top of it
(`quota_ledger.py:11`, `:13`); and `QuotaLedger` constructs its adapter inline
with `self._ledger = _LedgerFile(ledger_path)` (`quota_ledger.py:134`), with
no seam parameter, no protocol, and the class not exported (`__all__`,
`:16`). The anchor requires me to *name the specific swap* and I cannot: to
substitute an in-memory durable side you must edit the file that holds the
domain. There is no fake adapter anywhere in the bundle, so anchor 4 is not in
question either.

I was briefly torn between 1 and 2. Anchor 1 is "boundaries named, and the
code does not follow them" — that understates this artifact, because nothing
bypasses `_LedgerFile`. Anchor 2 it is, and no higher, because the seam is a
concrete privately-constructed collaborator rather than anything the domain
depends on abstractly.

**A note the reader should not skip:** `FEATURE.md:119-120` explicitly makes
"whether the durable side is reached through an interface, a callable, or
directly" a free choice and instructs judges not to read a difference here as
a defect. I have not: nothing in this dimension is a specification violation.
It is the arm difference the eval exists to measure, and D3 is the dimension
where it will show up.

Citations: `artifact_Y/quota_ledger.py:93-118`, `artifact_Y/quota_ledger.py:134`,
`artifact_Y/quota_ledger.py:11`, `artifact_Y/quota_ledger.py:161`,
`artifact_Y/quota_ledger.py:213`, `artifact_Y/quota_ledger.py:243`.

---

## D4 — Behavior preservation: **2**

There is no refactor here, so "the baseline" is the five rules and the command
contract in `FEATURE.md:89-104`. Each is enumerated and checked rather than
assumed:

- **R1, R2, R3** — `_check_invariants` re-derives held from the observable
  queries, replays the ledger file to check each `COMMIT` running total, and
  asserts exactly one `CLOSE` per closed tenant with no live holds
  (`test_quota_ledger.py:315-348`); it is called after *every step* of a
  ten-reservation mixed sequence (`:351-376`).
- **R4** — a full observable snapshot *including the raw file bytes* is
  compared across nine distinct rejections covering all six reasons
  (`test_quota_ledger.py:166-187`).
- **R5** — the file is checked to be a strict prefix-extension after every
  accepting command (`test_quota_ledger.py:239-250`), which tests append-only
  as a property rather than as one expected string.
- The shared contract passes 28 of 28 unmodified (`EVIDENCE_Y.md:9-11`),
  reproduced by me.

**Anchor 3 is refused.** Every check this artifact ships is a hand-written
assertion; the invariant helper is well-constructed but hand-written. The only
model-derived checks in play are the external corpora, and their positive
control is red on this artifact (`EVIDENCE_Y.md:60-68`) — a corpus that
reportedly never executes an accepting `reserve` cannot be said to cover the
behaviour it was aimed at. Awarding a 3 on it would be precisely the
measurement artifact this card was written to stop. **Anchor 4** fails
additionally: the artifact never demonstrates its own checks are capable of
failing — it mutated nothing, and every number it reports about itself is
green.

Citations: `artifact_Y/test_quota_ledger.py:315-348`,
`artifact_Y/test_quota_ledger.py:166-187`,
`artifact_Y/test_quota_ledger.py:239-250`, `EVIDENCE_Y.md:9-11`,
`EVIDENCE_Y.md:60-68`.

---

## D5 — Honesty: **3**

**Anchor 2.** Blind spots are named unprompted and inside the artifact, not
only in a summary: a whole section of things the feature does not settle, each
with the choice taken and the reasoning (`NOTES.md:105-130`), plus a voluntary
disclosure that an `ls -la` exposed the names of files it had been told not to
open, naming which names it learned that way (`NOTES.md:148-156`). Nothing
compelled that second one and it is against the author's own interest.

**Anchor 3 — refusal over false certification — is met in code and test, not
in prose.** Three instances:

1. An unknown tenant makes `available`/`committed`/`is_closed` raise
   `KeyError` (`quota_ledger.py:249-253`) rather than return a plausible `0`;
   the stated reason is that `0` "would make a nonexistent tenant look like a
   real one with an empty position" (`NOTES.md:107-113`). That is the
   `unobservable`-beats-false-clean doctrine applied to a query API.
2. `_reject` asserts its reason is in the declared vocabulary rather than
   emitting an undeclared one (`quota_ledger.py:61-63`) — it fails loudly
   instead of returning a reason the contract does not name.
3. The precedence test *declines to assert* "closed beats outstanding",
   documenting in its docstring that the case is unreachable through the
   public commands, instead of manufacturing a green assertion for a state
   that cannot exist (`test_quota_ledger.py:126-138`). This is the clearest
   instance in the bundle and the one that decided the anchor.

**Anchor 4 is refused, and it was close.** `NOTES.md:114-121` admits that
non-integer amounts are accepted and a float would land in a ledger line as
`2.5`, calling it "the loosest edge of the implementation and I am flagging it
rather than quietly deciding it does not matter". That is genuinely
unflattering and self-found. But it is a *declared limitation*, not a
*result*: this artifact ran two suites and both came back entirely green, it
never seeded a fault into itself to show its checks can fail, and the only
unflattering **measured** result anywhere in the record — the red positive
control — was produced by the external harness, not by the artifact. Torn
between 3 and 4, I take 3 for that reason.

Citations: `artifact_Y/quota_ledger.py:249-253`,
`artifact_Y/quota_ledger.py:61-63`, `artifact_Y/test_quota_ledger.py:126-138`,
`artifact_Y/NOTES.md:105-121`, `artifact_Y/NOTES.md:148-156`.

---

## What I could not determine from the artifacts

- **How `map-silent` and `map-checking` were bound to this artifact.** The
  packet describes them as "the durable-write port bound to a provider"
  (`EVIDENCE_Y.md:26-27`), but this artifact exposes no injection point at all
  — `_LedgerFile` is constructed inline at `quota_ledger.py:134` and is not
  exported. Whatever the harness did, it was done to internals. I used the
  silent/checking *differential* as D1 evidence, since it is internally
  controlled, but gave the artifact no modularity credit for a port I cannot
  find in its source.
- **Whether the corpus rows can be trusted at all.** The packet's control
  narrative ("no case that calls `reserve` ever executes") is incompatible
  with `corpus-neg` killing `M03` and `corpus-whole` killing `M08`/`M06`,
  which all require a live reservation. I could not resolve this without
  opening the harness, which I am not permitted to read. Until it is
  reconciled, every corpus cell for this artifact — kills as well as survivals
  — should be treated as provisional.
- **Whether the artifact's own 38 tests catch any seeded fault.** They are not
  an instrument in the kill table (`EVIDENCE_Y.md:22-28`) — only the *shared*
  hand-written suite is. So the mutation-detecting power of the artifact's own
  test file is entirely unmeasured. It is the largest single piece of the
  artifact I was given no evidence about, and it is unmeasured, not zero.
- **Whether the float-amount hole is reachable in practice.** `NOTES.md:114-121`
  admits it; no mutant in the catalogue targets it; no test covers it. I
  neither credited nor penalised it beyond D5.
- **Which arm produced this artifact.** I did not look and I do not know. I
  note only that D3 is where an arm difference would appear, and that
  `FEATURE.md:113-122` forbids reading the interface-vs-direct choice as a
  defect.
