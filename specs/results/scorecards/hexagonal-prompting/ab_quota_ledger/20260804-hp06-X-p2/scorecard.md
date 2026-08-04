# Scorecard — hexagonal-prompting / ab_quota_ledger / arm X / pass 2

**Judge:** claude-opus-5[1m], pass 2, blind to arm.
**Commit:** f65bb9b3c8e3d4e2b5ca50e9d34c27611673c9af
**Scores:** D1 3 · D2 2 · D3 4 · D4 3 · D5 3 — **total 15 / 20**

Citation paths are relative to the blind directory: `artifact_X/...` for the
artifact, `EVIDENCE_X.md:N` for a measured figure.

A note the card demands up front (rule 4): this artifact's `NOTES.md` is
persuasive writing. It anticipates objections, names its own trades, and reads
like a good design review. **None of that was an input.** Where I scored above
1 it is because I opened the module or the kill table and found the thing; where
I declined an anchor it is because the artifact asserted something the artifacts
do not show. I re-ran the artifact's own test suite rather than accept its
reported count, and I confirmed the parity file's collection count directly.

---

## D1 — Bug detection: **3**

**Anchor 2 (content, not shape) — met.** `M04-durable-stale-total` survives the
whole-view corpus, both aspect slices, and the *silent* durable-write provider,
and is killed only by the content-asserting provider and by the shared suite
(`EVIDENCE_X.md:35`). That is the cleanest possible demonstration that shape
assertions are insufficient and content assertions are what catch the fault.
`M05` behaves the same way against `map-silent` versus `map-checking`
(`EVIDENCE_X.md:36`). The artifact's own cases are also content-asserting rather
than shape-asserting — `test_journal_parity.py:46-53` pins the literal list
`["COMMIT acme 4 4", "COMMIT globex 1 1", "COMMIT acme 2 6"]`, which is exactly
the running-total content a stale-total fault corrupts.

**Anchor 3 (a class the whole-view corpus cannot reach) — met.** All three
`guard_relaxation` mutants SURVIVE `corpus-whole` and are KILLED by the
generated negative corpus (`EVIDENCE_X.md:32-34`; per-class row `0 of 3` versus
`3 of 3` at `EVIDENCE_X.md:46`). A relaxed guard produces no wrong value in any
projection the positive corpus prints — the run simply takes a step it should
have refused — so this is precisely the refusal class the anchor names, and it
was reached.

**Anchor 4 — declined; I take the lower of 3/4.** Three reasons, any one of
which would be enough:

1. *The cases that do it are not this artifact's.* `corpus-neg` and the
   content-asserting provider are the shared measurement harness, applied
   identically to both arms. Every case the artifact itself ships is
   hand-written (`tests/test_domain_rules.py`, `tests/test_journal_parity.py`),
   and **none of them was run against any mutant**. Their kill power is
   unmeasured. I can see by inspection that `test_domain_rules.py:24-54` pins
   the reserve/close rejection precedence and would plausibly catch a relaxed
   guard, and that the literal-line parity cases would plausibly catch a stale
   total — but plausible is not measured, and this card scores artifacts, not
   inferences about them.
2. *The artifact's record does not name a fault class it cannot reach.*
   `NOTES.md:114-138` names four *unspecified behaviors* it chose not to define.
   That is not the same thing. The only naming of an unreachable class —
   cross-process faults, where the effect oracle cannot observe across a process
   boundary at all — is harness-authored (`EVIDENCE_X.md:103-106`) and is
   explicitly filed as *not seeded*, never as *not caught*. Rule 3 makes a
   stated limit the price of a 4, and this artifact did not pay it.
3. *The positive control was substituted.* `M07`, the catalogue's positive
   control, was unexpressible against this design and was seeded as a
   broader-reach substitute whose kills are declared non-comparable
   (`EVIDENCE_X.md:63-68`). Within this arm the substitute did fire on six of
   seven instruments, so the control is *altered*, not *red* — that is why I
   still award 3 — but the instrument suite's calibration rests on a control the
   catalogue could not deliver as designed, and the temper of this round says to
   weigh that rather than read the all-KILLED `suite` column at face value.

One point that belongs in the record even though it is not a kill: three of ten
catalogue mutants could not be seeded into this artifact at all, because it
keeps no redundant `available` counter to corrupt (`EVIDENCE_X.md:53-62`, and
`domain.py:74-80` is why). Making a fault class unexpressible is a real property
of the design — but it is a D2/D3 virtue, not a detection result, and I did not
let it inflate D1. Raw kill counts against the other arm are not comparable and
I did not compare them.

---

## D2 — Complexity: **2**

**Read the measured descriptor first.** 4 modules, 123 production lines, 21
public names, 11 branches, `mutable_state_count` 8, `max_writers_of_one_attribute`
2 (`EVIDENCE_X.md:85-90`). The packet flags that `mutable_state_count` is an
undercount for one of the two artifacts and should not be compared naively
(`EVIDENCE_X.md:94-99`); I did not compare it.

**Anchor 2 — met, in the code and not only in the argument.** `available` is
derived on every read from quota minus committed minus the live holds
(`domain.py:74-80`), so R1 — the conservation rule the feature states — is
arithmetic that cannot be violated rather than an invariant four commands must
each remember to maintain. The visible consequence is that `release` performs no
arithmetic at all (`domain.py:128-133`): the amount returns by the hold ceasing
to exist. Writers are singular per piece of state: `_issued` only in `reserve`
(`domain.py:111`), `_committed` only in `commit` (`domain.py:124`), `_closed`
only in `close_tenant` (`domain.py:143`), which is what the measured max-writers
figure of 2 (constructor plus one command) reflects. `_outstanding` is touched by
three commands, and that is essential — reserving, committing and releasing are
the operations on a set of live holds. There is no god-state and no variable
written from everywhere. Eleven branches across four commands and five queries is
proportional to a feature with six rejection reasons and two ordered guard
chains.

**Anchor 3 — not met, by the artifact's own construction.** The anchor requires
that *a simplification was made and its effect measured, with before and after
both recorded*. The artifact states plainly that it removed and collapsed
nothing to move a count and has no deletion to point at (`NOTES.md:158-160`).
There is therefore no before/after pair. The mechanical block does print both
artifacts' figures, and the temptation is to treat one as the 'before' of the
other — but that is a cross-arm comparison of two independent implementations,
not a measured effect of a change this artifact performed, and treating it as one
would reproduce the MF-020 error the card explicitly warns about. Worth recording
that the comparison would not obviously favor this artifact anyway: it carries
4 modules against 1 and 21 public names against 17, against 123 production lines
versus 147 and 11 branches versus 13 (`EVIDENCE_X.md:85-92`). 'Simpler' is not
established even informally, and D2 stops at 2.

---

## D3 — Modularity: **4**

**Anchor 2 — met.** The declared boundary is one driven port, `CommitJournal`,
declared in the domain's own vocabulary (`domain.py:15-28`), and the code follows
it: every durable write in the domain goes through `self._journal.append(...)`
(`domain.py:125`, `domain.py:144`) and every read through
`self._journal.lines()` (`domain.py:97`).

**Anchor 3 — met, with the swap named.** `domain.py:9-12` imports exactly
`dataclasses` and `typing` — no `pathlib`, no `os`, no `io`, no environment, and
in particular neither adapter module. The dependency runs one way only: the real
adapter imports nothing from the domain either (`journal_file.py:8-10`), because
the port is a structural `Protocol`. **The swap:** replace
`FileJournal(ledger_path)` with `InMemoryJournal()` on `__init__.py:30` and no
file under the domain changes; `ReservationBook.__init__` already accepts any
`CommitJournal` (`domain.py:64`).

**Anchor 4 — met, on runtime evidence rather than import topology.** The card is
explicit that a 3-or-more needs evidence about what *calls* what at runtime.
`tests/test_journal_parity.py:21-28` builds one fixture parametrized over the
real `FileJournal` (writing to a `tmp_path` file) and the `InMemoryJournal` fake,
and runs the identical eight-case list through both
(`test_journal_parity.py:101-115`). I did not take the report's word for the
result: I collected that file (16 tests — 8 cases x 2 adapters) and ran the
artifact's suite (**41 passed**), both read-only and outside the repository.

What raises this above a box-ticked parity test is that the cases assert *values*,
not agreement. `case_running_total_accumulates_per_tenant` asserts the literal
three-line list; `case_close_appends_the_final_total` asserts
`["COMMIT globex 2 2", "CLOSE globex 2"]`. An agreement-only comparison would
have satisfied the anchor's letter and none of its purpose, because two wirings of
the same domain agree with each other even when the domain is wrong — the file
says exactly that at `test_journal_parity.py:1-9` and then does not do it.

Independent corroboration that the seam is real and not self-certified: the
evaluation harness bound the same durable-write port to **two further providers
it wrote itself**, one asserting nothing about content and one asserting content
(`EVIDENCE_X.md:26-27`), and both bindings ran. Four implementations of one port,
two of them by a third party who never touched the domain, is about as strong as
swappability evidence gets at this scale.

**The blemish I weighed and did not find disqualifying.** The class the
specification names, `QuotaLedger`, is a *subclass* of the domain class rather
than a separate wiring object (`__init__.py:21-30`), so the composition point and
the rules share a type and a consumer holding a `QuotaLedger` holds a domain
object with a hardwired file adapter. This is a genuine layering smudge. It does
not defeat anchor 4: the domain still holds no path, and the parity evidence is
taken at the `ReservationBook` level, where the port is open. The artifact records
the smudge itself (`NOTES.md:91-98`, `NOTES.md:150-156`) rather than renaming
things to look tidier, which is the behavior D5 is supposed to reward and I have
credited it there, not here.

**`refuses_to_claim`** (required for the 4): the artifact refuses to claim its
port abstracts the durable record's *format*. The domain renders the line itself
(`domain.py:125`) and the port carries a bare `str`, so no adapter swap can vary
the format — stated as a deliberate trade rather than papered over. It also
refuses to claim any second port (quotas, reservations, ids and totals stay as
computation with no indirection) and refuses to hide that the class the
requirement names is the wired object rather than the rules.

---

## D4 — Behavior preservation: **3**

**Read this dimension with a caveat.** There is no baseline. Both arms implement
one specification from scratch, so nothing is being *preserved* across a change;
D4 here degenerates to spec conformance. A reader comparing this cell to a D4 in
a refactoring epic is comparing different questions.

**Anchor 2 — met.** The behaviors are enumerated by the feature (R1–R5, plus the
two ordered rejection chains) and made executable by the shared suite, which
names them test by test and passes **28 of 28** unchanged against this artifact
(`EVIDENCE_X.md:10-11`). The artifact adds its own enumeration of what the shared
suite leaves open: conservation asserted after *every* step of a mixed sequence
(`test_domain_rules.py:98-111`), close finality and the frozen committed total
(`test_domain_rules.py:129-149`), id non-reuse, and numeric id ordering past nine
— the last being a rule the shared suite never exercises because it never
allocates ten ids.

**Anchor 3 — met.** The checks run against it are model-derived, not only
hand-written assertions: a whole-model corpus (43,128 cases, 3,440 executable), a
negative corpus (94 executable), and two aspect slices, all green as controls on
the unmutated artifact (`EVIDENCE_X.md:18`, `EVIDENCE_X.md:22-25`).

**Anchor 4 — declined; I take the lower of 3/4.** The anchor asks for a
deliberate behavior-breaking change shown to be *caught*. Everything that
demonstrates failure-capability here belongs to the harness. The artifact ships
no mutant, no broken variant, no killed check, and says outright that no tool
other than pytest was ever run over the code (`NOTES.md:158-160`). Its own 41
tests have never been shown able to go red for a real defect.

And the harness's demonstration is weaker than the all-KILLED `suite` column
suggests. The model-derived corpus that anchor 3 credits misses **4 of the 8**
seeded mutants outright, including every guard relaxation (`EVIDENCE_X.md:46`),
so behavior preservation for the entire refusal surface rests on the hand-written
suite and the negative corpus rather than on the model-derived positive corpus.
The catalogue's positive control was also unexpressible and substituted
(`EVIDENCE_X.md:63-68`). A 4 here needs the artifact to break itself on purpose
and show its check failing; this one does not, so 3.

---

## D5 — Honesty: **3**

**Anchor 2 — met inside the artifact, not only in a report.** The parity test
file's own header states why an agreement-only comparison is worthless and would
be a check that can never fail for a reason worth knowing
(`test_journal_parity.py:1-9`); the file-journal test file states the boundary
rule that a case writable for only one journal belongs to that journal and not to
the port (`test_file_journal.py:1-3`). Both are limits declared in code that a
maintainer will read, not in a summary. `NOTES.md:114-138` then flags four open
choices *as choices*: `available('nobody')` raises rather than returning a
sentinel; a non-integer amount is neither rejected nor specified; the
`close_tenant` guard order between two reasons is reachable only in an
asymmetric history; the fake ships in the package rather than under `tests/`.

**Anchor 3 — met, by refusals that cost it something.** Two places where a
positive claim would have read better and was not made: it declines to claim the
structural and behavioral halves of its prompt ever conflicted, and says so in
those terms rather than manufacturing a clash; and it declines to claim any
simplification at all, stating it has no deletion to point at
(`NOTES.md:140-160`). Under a scorecard whose D2 explicitly rewards a measured
simplification, declining to claim one is the analogue of emitting `unobservable`
instead of a false clean.

**Anchor 4 — declined; I take the lower of 3/4, and this was the closest call on
the card.** The case *for* 4: the artifact records that constructing a
`QuotaLedger` over an existing path destroys that file's contents, and pins the
destruction in a test that watches it happen (`NOTES.md:100-107`,
`test_file_journal.py:11-16`), and it records the `QuotaLedger`-subclasses-domain
smudge against its own hexagonal claim. The case *against*, which I found
decisive: every result the artifact **measures** about itself is green — 28
passed, 41 passed (I re-ran the 41 and confirm it). The unflattering material is
admitted design *cost*, and in each case the artifact argues the cost is the
right trade ("I read that as intended", "I would rather record that than pay for
nine forwarding methods"). Naming a cost you then defend is honest; it is not the
same as a record containing a result that goes against you. The genuinely
unflattering findings in this run — three catalogue mutants unexpressible, a
substituted positive control, a higher module and public-name count than the
other arm — are all harness-authored, and the artifact had no way to know them.

---

## What I could not determine from the artifacts

- **Whether the artifact's own 41 tests catch any seeded fault.** They were never
  run against a mutant; the kill table's instruments are the harness's corpora,
  the two generated providers, and the shared suite. This is the single largest
  hole in the D1 evidence for this arm and it is not the artifact's fault — it is
  a property of how the eval was instrumented.
- **Whether the shared suite's 28 passes are load-bearing beyond the corpora.**
  The `suite` column kills all eight mutants, i.e. it dominates every generated
  instrument on this artifact. I cannot tell from the packet whether that is a
  strong hand-written suite or a sign that the generated corpora under-reach,
  though the `0 of 3` guard row points at the latter.
- **What a faithful `M07`/`M08`/`M10` would have shown.** They are unexpressible
  against a design with no stored `available`, so the redundant-counter fault
  class is neither killed nor survived here. I recorded it as not-seeded, exactly
  as the packet does, and let it influence nothing.
- **Cross-arm anything.** I did not open the other artifact, its evidence, the
  arm prompts, the predictions file, the fault catalogue, or any other scorecard.
  The mechanical block's second column is the only fact about the other arm I
  saw, and I used it only to decline the D2 before/after reading.
- **Behavior under repeated construction over a live ledger.** The truncation is
  tested at `test_file_journal.py:11-16`, but nothing in this eval exercises
  reopen or recovery, and the feature does not require it; whether the choice is
  safe in any real deployment is outside what these artifacts can answer.
