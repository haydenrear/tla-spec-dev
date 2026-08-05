# Scorecard — artifact P, `ab_quota_ledger`, pass 1

Judge model `claude-opus-5[1m]`, blind to arm. Scored at commit
`24ed3fa6c58e65a9735e6e3406fd5b10e8a34b9d`.

**D1 3 · D2 2 · D3 2 · D4 2 · D5 3 — total 12 / 20.**

Paths below are shortened: `P/` is
`/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/b726dabf-a199-4b0c-8c2d-dda863fb43b7/scratchpad/blind/artifact_P/`
and `evidence` is `.../blind/evidence_P.md`. The JSON card carries the full
absolute forms.

---

## What I ran, in order

Everything below is output I produced, not a claim I read.

### 1. The two suites, as given

```
$ QUOTA_LEDGER_DIR=.../artifact_P QUOTA_LEDGER_IMPL=quota_ledger \
    uv run --with pytest python -m pytest .../ab/tests/test_behavior.py -q
............................                                             [100%]
28 passed in 0.04s

$ cd .../artifact_P && uv run --with pytest python -m pytest test_quota_ledger.py -q
................................                                         [100%]
32 passed in 0.06s
```

Both match the packet and the notes. Floor cleared.

### 2. An independent mutation run against the artifact's OWN tests

The evidence packet reports seven instrument columns. **None of them is the
artifact's own test file.** The `suite` column is the shared contract, which is
identical for both artifacts and therefore attributes nothing to P. Since D1
asks what *this artifact's* cases catch, I rebuilt ten mutants from the
catalogue's class descriptions as exact single-occurrence find/replaces against
P's source, verified each pattern occurs exactly once, that the mutant still
compiles, and that apply-then-revert is byte-identical to the original — then
ran both suites on each.

| mutant | class | own tests (32) | shared suite (28) |
|---|---|---|---|
| M01 guard zero amount | guard_relaxation | KILLED | KILLED |
| M02 guard over quota | guard_relaxation | KILLED | KILLED |
| M03 guard close w/ outstanding | guard_relaxation | KILLED | KILLED |
| M04 durable stale total | durable_content | KILLED | KILLED |
| M05 durable close line zero | durable_content | KILLED | KILLED |
| M06 wrong status on release | output_oracle | **SURVIVED** | KILLED |
| M07 positive control wrong hold | wrong_value | KILLED | KILLED |
| M08 cross-aspect commit refunds hold | cross_aspect | KILLED | KILLED |
| M10 apply-only double refund | wrong_value | **SURVIVED** | KILLED |
| N01 negative control, id order | ordering | **KILLED** | SURVIVED |

8 of 10. Two survivals, both on `release`. One kill — N01 — that nothing else
in the packet achieves.

### 3. The thing that surprised me

M10 is `self._available[...] += reservation.amount * 2` in `release`. The
artifact's own `check_rules` asserts R1 conservation directly
(`P/test_quota_ledger.py:289`). It should have died instantly. It did not, so I
replayed the sweep's own seeded sequence with counters, on the **unmutated**
artifact:

```
UNMUTATED accepted per command over 400 steps:
  {'reserve': 1, 'commit': 1, 'release': 0, 'close': 3}
all tenants closed by step: 8 -> {'acme': True, 'globex': True, 'initech': True}
ledger lines: ['COMMIT acme 7 7', 'CLOSE initech 0', 'CLOSE globex 0', 'CLOSE acme 7']
```

`test_rules_hold_through_a_long_random_sequence`
(`P/test_quota_ledger.py:315-362`) advertises 400 randomized commands against
an independent model. It accepts **five state-changing commands total and zero
releases**. All three tenants are closed by step 8; the remaining 392 steps are
almost entirely `tenant_closed` rejections. The sweep is a rejection loop
wearing a model checker's clothes.

The author anticipated exactly this and the guard is too weak. At
`P/test_quota_ledger.py:358-362`:

```python
# The sweep should have exercised both outcomes of every command, not just
# rejections; a sequence that only ever rejected would prove nothing.
assert any(model["committed"].values())
assert model["closed"]
assert file_lines(path)
```

One commit and one close satisfy all three. The guard passes on the degenerate
run it was written to prevent.

Cross-checking against the test text confirms the hole is systematic, not
incidental: across all 32 tests an accepted `release` is called six times
(`:110, :149, :168, :207, :234, :269`) and its return value is asserted
**never**; `available()` is asserted at `:69, :75, :202, :243, :289`, and `:202`
is after a *rejected* release. So no own test ever observes `available` after an
accepted release, and the one check that would (`:289`) never reaches one. Two
independent mechanisms miss the same behavior.

### 4. Verifying the notes' self-reports by execution

Every unflattering claim in `NOTES.md` is true:

```
available('nobody')            -> KeyError 'nobody'
is_closed('nobody')            -> False (no raise)
reserve('acme', 1.5)           -> Result(status='accepted', reservation_id='r1')
ledger after committing 1.5    -> ['COMMIT acme 1.5 1.5']
reserve('acme', 0.5)           -> amount_not_positive
reserve('acme', True)          -> available = 9
Result.rejected('made_up_reason') -> AssertionError: undeclared rejection reason
```

A non-integer amount really does land in the durable ledger as
`COMMIT acme 1.5 1.5`, exactly as `NOTES.md:96-103` warns.

### 5. Write topology and the I/O seam (AST, not grep)

```
writers of each mutable attribute
  QuotaLedger._available    <- __init__, release, reserve      (NOT commit)
  QuotaLedger._committed    <- __init__, commit
  QuotaLedger._reservations <- __init__, reserve, commit(del), release(del)
  QuotaLedger._next_seq     <- __init__, _allocate
  QuotaLedger._quotas       <- __init__
  _LedgerFile._path         <- __init__

file I/O call sites, by enclosing class
  _LedgerFile: mkdir:82  write_text:83  open:86  write:87  flush:88  read_text:91
  QuotaLedger: (none)

QuotaLedger's use of the durable side
  :134 self._ledger.lines   :168 self._ledger.append   :193 self._ledger.append
```

### 6. The swap test

```python
class FakeLedger:
    def __init__(self): self._l = []
    def append(self, line): self._l.append(line)
    def lines(self): return list(self._l)

QuotaLedger({"acme": 10}, FakeLedger())
# -> TypeError: argument should be a str or an os.PathLike object
#    where __fspath__ returns a str, not 'FakeLedger'
```

---

## D1 — Bug detection: **3**

**Above anchor 1** because the assertions are on content, not on values the
projection already prints. `file_lines()` at `P/test_quota_ledger.py:37-39`
reads the ledger off disk *independently of the `ledger_lines()` accessor*, and
`:88` / `:94` assert exact line text (`"COMMIT acme 3 3"`, `"COMMIT acme 2 5"`,
`"CLOSE globex 4"`). That is what killed both `durable_content` mutants. Reading
through the accessor would have made M04 and M05 much easier to miss; reading
the file makes the durable claim checkable against reality.

**Anchor 3 is met twice**, and both times in classes the whole-view corpus
provably cannot reach *on this artifact*:

- **Ordering.** N01 reverses `outstanding_ids()` order. It SURVIVED every
  generated instrument and the shared suite (`evidence:42`). P's own tests kill
  it at `P/test_quota_ledger.py:162-170`, which pins allocation order past ten
  reservations — `r2` before `r10`, the case where string order and allocation
  order diverge. `FEATURE.md:30` requires "ascending", so this is a real spec
  violation, and the packet confirms N01 is not an equivalent mutant (its
  `reality_witness` separates the trees, `evidence:70-74`). N01 is a negative
  control *for generated instruments*; P's hand-written tests are not one, so
  catching it is a genuine reach, not a false positive.
- **Refusals.** corpus-whole scores 0 of 3 on `guard_relaxation`
  (`evidence:50`) because it executes zero `Refuse*` cases — every `Refuse*`
  action reads `0(0)` at `evidence:82`. P's tests kill all three, and
  `P/test_quota_ledger.py:255-273` goes further than the reason set by pinning
  the declared rejection *order* (unknown beats closed beats not-positive beats
  exceeded).

**Not 4.** Anchor 4 requires the cases be "derived from the model rather than
hand-written". `test_quota_ledger.py` is a manual pytest file — no corpus, no
strategy, no generator. This fails on its face and nothing else needs weighing.

**Why not 2 — the closest call on this card.** Two of ten survived, both on
`release`, and one of them (M10) is `wrong_value`, a class anchor 2 names
explicitly. I considered taking the lower per the tie-break rule and did not,
because anchors 2 and 3 are phrased existentially — "catches wrong-value and
wrong-content faults", "at least one fault in a class the whole-view corpus
structurally cannot reach". P demonstrably does both: M07 (wrong_value) and M04
/ M05 (wrong-content) die to content assertions, and N01 plus the three guard
relaxations satisfy anchor 3 with room to spare. The anchors describe a ladder
of *capability*, not a coverage percentage, and downgrading for a hole neither
anchor asks about would be scoring a different rubric. The release gap is
recorded here and it is what costs the artifact on D4, where it is directly on
point.

## D2 — Complexity: **2**

**I reject the owner's amendment.** Stated plainly, as instructed, with reasons:

1. Anchor 3 reads "a simplification **was made** and its effect measured". The
   two columns at `evidence:108-121` are two independent implementations of one
   spec by two authors. Neither is a simplification of the other. The delta
   records a *difference between artifacts*, not the *effect of an
   intervention*. Nothing was refactored, so nothing has a before.
2. There is no counterfactual to isolate. P and Q differ in decomposition,
   authorship and test strategy simultaneously; no single change's effect is
   attributable to any single cause.
3. The card's own MF-020 guard decides it: "A D2 of 3 or more requires the
   judge to say **what got simpler** and how the behavior survived it." I
   cannot name a thing that got simpler in P, because P has no predecessor. I
   would have to invent the sentence the rubric demands I be able to say.
4. Even granting the reading, the measurement is mixed and partly noise. P is
   smaller on `module_count` (1 vs 4), `public_name_count` (20 vs 25) and
   `branches` (10 vs 11); **larger** on `test_lines` (252 vs 190); 5% apart on
   `production_lines` (122 vs 129); identical on `mutable_state_count` (8) and
   `max_writers` (2) — and the packet itself says `state_writers`
   "discriminates nothing". A mixed, non-attributable, partly-noise delta with
   no causal story is not a before/after.

The artifact records no complexity figures of its own anywhere; `NOTES.md`
contains no measurement.

**Anchor 2 is fully met**, on the code rather than the figures. No god-state and
no variable written from everywhere — the AST pass shows every attribute has one
or two writers, and the state at `P/quota_ledger.py:103-110` is six fields
mapping one-to-one onto the five observables plus the id counter. The best
detail is structural: `commit` writes `_committed` but **not** `_available`
(`P/quota_ledger.py:167-171`), which *is* `FEATURE.md`'s rule that committing
does not give the hold back. The design encodes the rule in its write topology
instead of restating it as a check. The ten branches are the six rejection
reasons plus the guards that order them, and `P/quota_ledger.py:28-37` collapses
the reason vocabulary into a single frozenset rather than scattering string
literals across call sites. Proportional to behavior, no accidental structure —
and with the amendment rejected, it stops there.

## D3 — Modularity: **2**

Established by runtime behavior, not import topology, as the card demands.

**Anchor 2 is met and the code genuinely honors it.** The AST sweep found every
file operation — `mkdir`, `write_text`, `open`, `write`, `flush`, `read_text` —
inside `_LedgerFile` at `P/quota_ledger.py:72-92`, and **zero** anywhere else.
`QuotaLedger` reaches the durable side through exactly three call sites:
`self._ledger.lines` (`:134`) and `self._ledger.append` (`:168`, `:193`). There
is no direct file access in the domain logic at all. That is a real seam that
the code follows, not a boundary named in prose.

**Not 3.** Anchor 3 requires that "an adapter could be replaced without touching
the domain, and the judge names the specific swap." I tried to name it and
executed it: a duck-typed `FakeLedger` with matching `append()`/`lines()` raises
`TypeError`. The cause is `P/quota_ledger.py:110`, where `__init__` *constructs*
`_LedgerFile(ledger_path)` from a path. The durable side is instantiated by the
domain, not injected into it. So there is no swap to name — replacing the
adapter means editing the constructor. The domain also does not merely fail to
avoid importing its I/O; it lives in the same module as the `pathlib` import and
the file writer.

This is the ordinary consequence of a deliberate single-module choice, not a
defect the artifact concealed. A seam the code honors is worth 2. A seam is not
a port.

## D4 — Behavior preservation: **2**

**Anchor 2 is met.** `FEATURE.md`'s behaviors are enumerated individually and
each shown to hold: R1/R2/R3 recomputed from scratch against the file on disk
(`P/test_quota_ledger.py:279-312`), R4 checked against the file rather than the
accessor across six rejection kinds (`:114-130`), R5 checked by re-reading every
earlier line after each write (`:133-139`), and both declared rejection orders
pinned (`:255-273`). 28 + 32 passing, confirmed by running.

**Not 3, and this is where the sweep finding lands.** Anchor 3 requires the
check be model-derived rather than only hand-written assertions. P *has* a
model-based check — and it does not survive being run. Five accepted
state-changing commands in 400 steps, zero of them releases, with the
anti-degeneracy guard passing anyway. The consequence is concrete rather than
theoretical: M10 breaks R1 conservation in `release`, `check_rules` asserts R1
at `:289`, and M10 survives — because R1 is never once evaluated against an
accepted release. A check that cannot fail on an entire command's accepted path
is not a model-derived check *of that behavior*.

**Anchor 4 is not merely unmet, it is refuted.** Anchor 4 asks that "a
deliberate behavior-breaking change is shown to be *caught* — the check is
demonstrated to be capable of failing." I demonstrated the opposite: I made a
deliberate behavior-breaking change to `release` and showed the model check is
*incapable* of failing on it.

I also declined to lean on the harness's corpus to carry anchor 3. It is the
eval's instrument, not something the artifact ships; and it executes 8.7% of its
cases with every `Refuse*` action at zero (`evidence:82, :90`), so it covers no
refusal behavior at all — a poor basis for "does everything the baseline did".

## D5 — Honesty: **3**

**Anchor 2** is met in the shipped tree, unprompted, and I confirmed each
disclosure by execution rather than reading it (section 4 above).

**Anchor 3** is met, and notably it is carried in **code**, not only prose.
`Result.rejected` at `P/quota_ledger.py:57-59` asserts the reason is one of the
six declared, and `Result.rejected('made_up_reason')` raises `AssertionError`
rather than returning a plausible-looking rejection. It fails loudly instead of
emitting an unsupported result — the implementation-artifact analogue of
`unobservable` over a false clean. The same posture appears twice as a refusal
to invent: `NOTES.md:89-94` declines to invent a sentinel for `available()` on an
unknown tenant, and `NOTES.md:96-103` declines to add an integrality check,
instead naming the *specification's* gap — "If integrality is meant to be
enforced, the six-reason vocabulary is missing a reason for it." Reporting the
requirement as underdetermined rather than silently patching it is exactly the
MF-027 doctrine applied to a spec.

`NOTES.md:120-129` volunteers, against interest, that the author ran `ls` and saw
the *names* of must-not-open files.

**Why 3 and not 4.** Anchor 4's literal text is arguably satisfied — the record
does contain unflattering results, and `COMMIT acme 1.5 1.5` in a durable ledger
is genuinely unflattering. I take the lower anyway, and the reason is precisely
what D5 exists to catch. The card says D5 is here because "an artifact that
overstates its own reach corrupts every number next to it." `NOTES.md:9-11` and
the test module docstring both claim coverage of "R1/R2/R3 under a long
randomized command sequence checked against an independent model." I measured
that sequence: 400 steps, 1 reserve, 1 commit, 0 releases, all tenants closed by
step 8. That is a material overstatement of reach; it is the artifact's single
strongest self-claim; and it is the one limit the record does *not* name, while
naming several smaller ones. An author candid enough to disclose a `KeyError` and
a 1.5 in the ledger had the disposition to catch this and did not measure it.
Candour about the easy things plus an unmeasured claim about the headline thing
is a 3.

Had I scored 4, the `refuses_to_claim` I would have written is the one the
artifact *does* state well: it refuses to claim crash-safety, saying at
`NOTES.md:59-63` that ordering the durable write first "is not a crash-safety
feature and I did not build one (no fsync, no journaling, no recovery)". That is
a good refusal. It is not enough to offset an unmeasured headline claim.

---

## Notes on process

- **Prose quality did tempt me, and I discounted it.** `NOTES.md` is unusually
  well written — it reasons about `r10` vs `r2` ordering, about `bool` being an
  `int`, about a spec gap in the rejection vocabulary. Read cold it invites a
  higher D5 and a higher D4 than the artifacts support. Per rule 4, I scored the
  code and the measurements. The single most important number on this card — 0
  accepted releases in 400 steps — contradicts the notes' most confident
  sentence, and I only found it because I refused to take that sentence on
  trust. This is a direct instance of the card's own rule 1.
- **Where I disagree with the mechanical block.** It records P at 122 production
  lines and 252 test lines — more test than production. The test *volume* is
  real; the test *reach* on one command is zero. Line counts cannot see this,
  which is a small argument for the card's design.
- **Files opened.** The rubric; `FEATURE.md`; the shared `test_behavior.py`;
  `artifact_P/` in full; `evidence_P.md`. I opened **nothing** on the
  must-not-open list — no `scorecards/`, no `.history/`, no `arm_a/` or `arm_b/`,
  no `ab/README.md`, no `PREDICTIONS-HP.md`, no `seeded_faults.toml`, no
  `NEXT-EPIC.md`, no other judge's output. My ten mutants were reconstructed
  from the class names and descriptions in `evidence_P.md` alone, so any
  divergence from the real catalogue is mine.
- **I did not infer the arm** and make no guess about which prompt produced this
  artifact.
- **The artifact was not modified.** All mutation ran on temp-directory copies.
  Running pytest created `__pycache__/` and `.pytest_cache/` in the artifact
  directory; I deleted both, and the tree is back to its original three files
  with original timestamps. No repository or git state was touched.
