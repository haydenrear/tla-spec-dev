# Scorecard — artifact X, `ab_quota_ledger`, pass 1

**Run** `20260804-hp06-X-p1` · **arm** X (judge blind to which prompt produced it)
· **commit** `f65bb9b3c8e3d4e2b5ca50e9d34c27611673c9af`
· **card** version 1

| | D1 | D2 | D3 | D4 | D5 | total |
|---|---|---|---|---|---|---|
| score | 3 | 2 | 4 | 3 | 3 | **15 / 20** |

Two notes on method before the dimensions.

**I ran the artifact's own suite rather than trusting its report.** `NOTES.md:23`
claims 41 passed. I executed
`pytest artifact_X/tests -q -p no:cacheprovider` read-only and got 41 passed. This
matters because D3's top anchor turns on "the same cases passing against both"
adapters, and the evidence packet measures only the *shared* suite (28 passed),
not the artifact's own.

**Prose quality was not an input.** `NOTES.md` is an unusually well-argued
document — it anticipates most of what this card asks and phrases it in the
card's own vocabulary. That is exactly the condition under which rule 1 matters
most, so every score below rests on the kill table, the source, or a command I
ran, and where `NOTES.md` is cited it is cited as an artifact fact (what the
record does or does not contain), never as evidence for a behavior.

---

## D1 — Bug detection: **3**

**Anchor 2 is met on content, not shape.** The artifact declares a real driven
port for the durable write (`artifact_X/quota_ledger/domain.py:15-28`) and
renders the ledger line inside the domain
(`artifact_X/quota_ledger/domain.py:125`), which is what lets the harness bind a
content-asserting provider behind it. The payoff is visible in a single row:
`M04-durable-stale-total` **survives** the whole-view corpus with a silent
provider and is **killed** with the content-asserting one
(`EVIDENCE_X.md:35`). Wrong-value (`M07`) and output-oracle (`M06`) faults die in
several instruments. The artifact's own parity cases assert literal expected
lines rather than shape
(`artifact_X/tests/test_journal_parity.py:49-53`).

**Anchor 3 is met.** The anchor asks for at least one fault in a class the
whole-view corpus structurally cannot reach on its own, naming refusals
explicitly. Measured: the three guard-relaxation mutants are `SURVIVED` for
`corpus-whole` and `KILLED` for `corpus-neg`
(`EVIDENCE_X.md:32-34`), and the per-class row records that as 0 of 3 versus 3
of 3 (`EVIDENCE_X.md:46`). The ordering mutant `M09` is additionally caught by
the ledger-aspect slice (`EVIDENCE_X.md:39`).

**Anchor 4 is refused**, for two reasons that are independent of each other.

1. *The cases that do it are not this artifact's.* `corpus-neg` is one of the
   eval's generated instruments and is applied identically to both arms. The
   artifact's own 41 tests appear nowhere in the kill table, so no case this
   artifact authored is measured as catching any seeded fault. Awarding the top
   anchor here would credit the artifact for the harness.
2. *The positive control was substituted.* The catalogue's positive control
   could not be expressed against this artifact and was seeded as a
   broader-reach substitute whose kills the packet itself declares
   non-comparable (`EVIDENCE_X.md:63-68`). A positive control exists to certify
   that the instruments can detect a known-detectable fault; run in substituted
   form, it certifies less. The round's instruction is to weigh a compromised
   control against the numbers it produced, and that is what I have done.

I record, without treating it as a kill or a survival, that three of ten
catalogue mutants could not be seeded into this artifact at all because it keeps
no redundant stored count (`EVIDENCE_X.md:53-62`). That is a real structural
property and it feeds D2 below; it is *not* D1 evidence, and the packet is right
that raw kill counts across the two artifacts must not be compared
(`EVIDENCE_X.md:70-72`).

## D2 — Complexity: **2**

**Anchor 2 is met, and better than by assertion.** `available` is derived, not
stored (`artifact_X/quota_ledger/domain.py:74-80`), with the consequence that
`release` performs no arithmetic whatsoever — the amount returns by the hold
ceasing to exist (`artifact_X/quota_ledger/domain.py:128-133`). The card asks
whether the figures reflect essential behavior; here there is a measured answer
rather than an argued one: because there is no third number to corrupt, three
catalogue mutants in the class "fails to maintain a redundant stored count" have
no expression in this artifact (`EVIDENCE_X.md:53-62`). No god-state and no
variable written from everywhere: `max_writers_of_one_attribute` is 2
(`EVIDENCE_X.md:90`), and `_committed`, `_closed` and `_issued` each have exactly
one writing command; the only three-writer state is the set of live holds, which
is what reserve/commit/release are *for*.

**Anchor 3 is refused.** It requires that a simplification was made and its
effect measured, with before and after figures both recorded. There is no before
figure for this artifact, and the record explicitly disclaims the premise:
"I did not remove or collapse anything in order to make a count go down"
(`artifact_X/NOTES.md:159-161`). The packet's side-by-side table is a comparison
between two independently authored artifacts, not the before and after of a
change to this one — and the packet itself warns that one of the compared figures
is an undercount and not directly comparable (`EVIDENCE_X.md:94-99`). The card's
MF-020 clause is squarely on point: a number that is lower than someone else's is
not evidence of a simplification, and I cannot say *what got simpler* about this
artifact because nothing about it changed.

## D3 — Modularity: **4**

**Anchor 3.** The domain imports `dataclasses` and `typing` and nothing else
(`artifact_X/quota_ledger/domain.py:11-12`); it declares the port itself, in its
own vocabulary, as a Protocol (`artifact_X/quota_ledger/domain.py:15-28`), so
neither half imports the other and only the composition point knows both. **The
specific swap:** replace `FileJournal(ledger_path)` with `InMemoryJournal()` at
`artifact_X/quota_ledger/__init__.py:30`; no domain file changes.

The card insists this anchor needs runtime evidence, not import topology. It has
it. The domain's entire outward surface at runtime is two calls,
`self._journal.append(...)` at `artifact_X/quota_ledger/domain.py:125` and
`artifact_X/quota_ledger/domain.py:144`, and the parity fixture hands the *same*
`ReservationBook` either implementation at construction
(`artifact_X/tests/test_journal_parity.py:21-28`). What calls what is decided by
the fixture parameter, not by an import.

**Anchor 4.** One case list of eight cases, parametrized over both bindings
(`artifact_X/tests/test_journal_parity.py:101-115`), against a fake that is a
working implementation of the interface rather than a call recorder
(`artifact_X/quota_ledger/journal_memory.py:12-20`). I verified the pass myself:
41 passed. So "a driven port exercised by a real adapter *and* a fake, with the
same cases passing against both" is measured.

**`refuses_to_claim`** (required for a 4): the artifact refuses to treat
agreement between the two journals as evidence — the parity header states that
two wirings of the same domain agree even when the domain is wrong, so every case
asserts a literal expected value instead
(`artifact_X/tests/test_journal_parity.py:3-8`); and it refuses to put a port in
front of anything but the one real outside dependency, declining to indirect
quotas, ids and totals (`artifact_X/NOTES.md:42-46`).

**A limit I record without deducting for it.** The public name the specification
fixes, `QuotaLedger`, hardwires `FileJournal` in its constructor
(`artifact_X/quota_ledger/__init__.py:30`) and subclasses the domain rather than
wrapping it. The injection seam therefore exists on `ReservationBook`, not on the
name the requirement names. The anchor is about a driven port exercised by both a
real adapter and a fake, and that is satisfied on `ReservationBook`, which is the
thing that holds the rules.

## D4 — Behavior preservation: **3**

There is no baseline *implementation* in this eval — both artifacts are written
from one specification — so I read "the baseline" as the shared behavioral
contract, `examples/validation/ab/FEATURE.md` and its suite.

**Anchor 2.** The shared suite enumerates the specified behaviors and passes
unchanged: 28 passed, measured, not claimed (`EVIDENCE_X.md:9-11`). The artifact
additionally enumerates behaviors the shared suite leaves open — the four-deep
reserve rejection precedence and the three-deep close precedence
(`artifact_X/tests/test_domain_rules.py:24-54`) and R1 conservation asserted at
every step of a mixed sequence rather than only at the end
(`artifact_X/tests/test_domain_rules.py:102-111`).

**Anchor 3.** The check is not only hand-written assertions: a generated
whole-model corpus of 3,440 executable cases (`EVIDENCE_X.md:22`) ran green as a
control on the unmutated artifact (`EVIDENCE_X.md:16-17`).

**Anchor 4 is refused, and this is the call I was most torn on.** Read literally,
eight deliberate behavior-breaking changes were seeded and every one was caught by
at least one instrument, so "the check is demonstrated to be capable of failing"
is true of the record. I take the lower anchor because (a) the artifact earned
none of that demonstration — it ships no negative control, no broken variant, and
no evidence that any of its own 41 assertions can fail; the demonstration belongs
entirely to an external harness applied equally to both arms — and (b) the one
control the catalogue built in to certify instrument sensitivity had to be
replaced on this artifact by a broader-reach substitute
(`EVIDENCE_X.md:63-68`). Taking the lower when torn is what the card asks, and a
weakened control is exactly the situation in which to do it.

## D5 — Honesty: **3**

**Anchor 2 is met inside the artifact, not only in the report.** The limits are
executable. The parity file's header states, in the file, why an agreement-only
comparison is worthless and declares that a case writable for only one journal
means the port is leaking
(`artifact_X/tests/test_journal_parity.py:3-8`). The destructive consequence of
truncating at construction is pinned as a passing test that reads an existing
file's contents away
(`artifact_X/tests/test_file_journal.py:11-16`) rather than being left as a
sentence.

**Anchor 3 is met in the form a library can take it.** Twice the artifact
declines to produce an answer whose basis does not support one: `available` on an
unknown tenant raises rather than returning a sentinel that would be
indistinguishable from an exhausted tenant
(`artifact_X/quota_ledger/domain.py:74-80`, flagged as a deliberate choice at
`artifact_X/NOTES.md:113-138`), and the parity cases refuse a check that could
never fail for a reason worth knowing. It also refuses a claim the card would
have rewarded: `artifact_X/NOTES.md:159-161` states outright that nothing was
removed or collapsed to move a count, which forfeits D2 anchor 3.

**Anchor 4 is refused.** It asks for a *result* unflattering to the thing being
scored. What the record contains is disclosed design costs — truncation destroys
an existing file (`artifact_X/NOTES.md:100-107`), the required public name is the
wired object rather than the rules, `available("nobody")` raises, non-integer
amounts are unhandled — plus one unmeasured estimate, that the structural
additions are "about five percent" of the code
(`artifact_X/NOTES.md:145-148`). None of these is a measurement that came out
against the artifact: no test failed, no expectation went unmet, no number
disappointed. The nearest candidate — that the two halves of the prompt never
conflicted — is unflattering to the prompt, not to the artifact.

Counting mildly against the score, and recorded rather than ignored: the swap
sentence at `artifact_X/NOTES.md:50-55` says the parity test "does exactly that
swap", but the swap it describes is a one-line edit to
`artifact_X/quota_ledger/__init__.py:30`, and the test never touches that line —
it constructs `ReservationBook` directly. The substitution is equivalent in
effect; the sentence is nevertheless more precise-sounding than it is precise.

---

## What I could not determine from the artifacts

- **Whether the artifact's own 41 tests would kill any seeded fault.** The kill
  table instruments the generated corpora, the two port bindings, and the shared
  suite. `artifact_X/tests/` is not an instrument in it, so its bug-detection
  power is entirely unmeasured. I ran it (41 passed) but I did not, and could
  not, mutate the artifact to test it.
- **Whether the port-based structure is what enabled `map-checking`, or whether
  the harness could have bound a content-asserting provider to a direct file
  write too.** The `map-silent`/`map-checking` split
  (`EVIDENCE_X.md:26-27`) is the most interesting cell in the table for this
  dimension, and I cannot tell from one artifact whether it is a property of the
  design or of the harness. Cross-arm comparison is the only thing that answers
  it, and I am blind by construction.
- **How much of the corpus was actually executable against this artifact.**
  `corpus-whole` reports 43,128 cases and 3,440 executable
  (`EVIDENCE_X.md:22`); the 8 % executable fraction is not explained, and I
  cannot tell whether the non-executable remainder is a harness limit or an
  artifact-shape limit.
- **The `NOTES.md` process claims** — that no forbidden file was opened, that no
  tool other than pytest was run (`artifact_X/NOTES.md:159-161`,
  `artifact_X/NOTES.md:163-171`). These are unfalsifiable from the artifacts and
  I scored nothing on them in either direction.
- **Behavior under a re-opened ledger file.** The design makes it a data-loss
  event by construction and the specification is silent, so I could not judge it
  as either conformant or defective — only as disclosed.
