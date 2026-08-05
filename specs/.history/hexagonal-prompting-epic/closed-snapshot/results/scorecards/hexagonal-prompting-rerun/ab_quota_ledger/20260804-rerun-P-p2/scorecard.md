# Scorecard — artifact P, pass 2

**Judge:** claude-opus-5[1m] · blind to arm · scorecard_version 1
**Total: 11 / 20** — D1 3, D2 2, D3 2, D4 2, D5 2

Files opened: the rubric, `FEATURE.md`, `tests/test_behavior.py`, the three files
of `artifact_P/`, and `evidence_P.md`. **I opened nothing on the must-not-open
list.** I did not learn, and do not guess, which prompt produced this artifact.

---

## What I ran, and what it printed

Everything below was executed by me. Nothing in this card rests on the
artifact's description of itself; where the artifact described itself, I
checked, and in one case the description was false.

### 1. The two suites, as shipped

```
$ QUOTA_LEDGER_DIR=.../artifact_P QUOTA_LEDGER_IMPL=quota_ledger \
    uv run --with pytest python -m pytest .../tests/test_behavior.py -q
28 passed in 0.03s

$ cd artifact_P && uv run --with pytest python -m pytest test_quota_ledger.py -q
32 passed in 0.09s
```

Both figures in the evidence packet and the NOTES reproduce exactly.

### 2. My own mutation sweep (14 mutants)

The evidence packet reports a `suite` column, but that is the *shared* suite —
identical for both artifacts, so it measures the instrument, not this artifact.
The artifact's own 32 tests are its actual contribution to detection and nobody
had measured them. I wrote 14 find/replace mutants against a copy of the tree
(the artifact tree itself was never modified), verified each pattern occurs
exactly once and still parses, and ran both suites on each.

| mutant | class | artifact's own tests | shared suite |
|---|---|---|---|
| X01 guard, zero amount (`< 1` → `< 0`) | guard_relaxation | **KILLED** | KILLED |
| X02 guard, over quota (`> avail` → `> avail+1`) | guard_relaxation | **KILLED** | KILLED |
| X03 guard, close with outstanding disabled | guard_relaxation | **KILLED** | KILLED |
| X04 durable, stale running total | durable_content | **KILLED** | KILLED |
| X05 durable, `CLOSE <t> 0` | durable_content | **KILLED** | KILLED |
| X06 release returns `rejected` after doing the work | output_oracle | **SURVIVED** | KILLED |
| X07 wrong hold (`-= amount-1`) — positive control | wrong_value | **KILLED** | KILLED |
| X08 commit also refunds the hold | cross_aspect | **KILLED** | KILLED |
| X09 `ledger_lines()` reversed | ordering | **KILLED** | KILLED |
| X10 release double refund (`+= amount*2`) | wrong_value | **SURVIVED** | KILLED |
| N01 outstanding ids reversed | ordering | **KILLED** | SURVIVED |
| X11 reserve reason order swapped | ordering | SURVIVED | SURVIVED |
| X12 rejected commit writes a durable line | R4 | **KILLED** | KILLED |
| X13 (my own dud — dead statement) | — | SURVIVED | SURVIVED |

Two notes on the survivors so they are not read as misses they are not.
**X11 is an equivalent mutant**: swapping the `amount_not_positive` and
`quota_exceeded` guards is only observable when `amount < 1` *and*
`amount > available`, which requires a negative `available` — unreachable under
R1. Nothing could catch it. **X13 was a badly written mutant of mine** that
inserts a dead assignment; it changes no behavior. Neither counts against the
artifact.

Which tests did the killing (used for the D1 citations):

```
X01 → test_a_rejected_reserve_does_not_consume_an_id,
      test_a_rejected_command_writes_nothing_durably[lambda1],
      test_rules_hold_through_a_long_random_sequence
X02 → test_quota_can_be_fully_committed, test_a_zero_quota_tenant_can_only_be_closed
X03 → test_close_rejection_order_is_the_declared_one
X04 → test_commit_lines_reach_the_file_itself, test_close_line_reaches_the_file_itself
X05 → test_close_line_reaches_the_file_itself,
      test_close_total_matches_committed_after_commits_and_releases
N01 → test_outstanding_ids_are_ascending_past_ten, test_outstanding_ids_span_tenants
```

### 3. The thing that surprised me

X06 and X10 both live in `release`. Both survived 32 tests including a
"400-step randomized sequence checked against an independent model". That
should not be possible, so I instrumented the artifact's real test — wrapping
the four commands on `QuotaLedger` and calling
`test_rules_hold_through_a_long_random_sequence` directly:

```
THE ARTIFACT'S OWN 400-STEP SWEEP, per-command outcomes:
    close_tenant:accepted 3      close_tenant:rejected 39
    commit:accepted 1            commit:rejected 91
    release:accepted 0           release:rejected 72
    reserve:accepted 1           reserve:rejected 193
```

**Five accepted commands out of 400. Zero accepted releases.** Replaying the
same RNG stream shows why: `close_tenant` fires with p=0.10 over four tenant
choices, so all three tenants are closed by step 30; after that every `reserve`
returns `tenant_closed`, outstanding drains, and the remaining ~370 steps are
rejections against a fully closed ledger. `release` is called 72 times and
never once on a live id.

The sweep's own docstring anticipates exactly this failure and claims immunity
from it — `test_quota_ledger.py:358-360`: *"The sweep should have exercised both
outcomes of every command, not just rejections; a sequence that only ever
rejected would prove nothing."* The three guards written to enforce that
(`any(model["committed"].values())`, `model["closed"]`, `file_lines(path)`) are
satisfied by 1 commit and 3 closes, so they pass green while the property they
name is false. This is the single most consequential finding on the card: it
sets D4 and it caps D5.

### 4. Structure, measured rather than read

AST pass over `quota_ledger.py`:

```
if/ifexp nodes: 9 at lines [140, 142, 144, 146, 161, 177, 186, 188, 190]
  _available : 2 write sites (150, 180)
  _committed : 1 write site  (170)
  _reservations: 1 write site (151)
  _next_seq  : 2 write sites (109, 202)
  _ledger    : 1 write site  (110)
filesystem calls (mkdir/write_text/open/read_text): lines 82, 83, 86, 91 — all
  inside _LedgerFile
references to self._ledger: 110, 134, 168, 193
```

Nine branches for nine declared rejections, and nothing else.

### 5. The adapter-swap test (D3)

```
QuotaLedger.__init__ signature: (self, quotas: Mapping[str,int], ledger_path: Path|str)

swap via constructor: FAILED -> TypeError argument should be a str or an
  os.PathLike object where __fspath__ returns a str, not 'FakeLedger'
swap via monkeypatching quota_ledger._LedgerFile: ['COMMIT acme 3 3']
```

---

## D1 — Bug detection: **3**

Anchor 2 is met on evidence, not assertion. The adapters assert *content*:
`file_lines()` (`test_quota_ledger.py:37-39`) reads the file from disk
independently of `ledger_lines()`, and the assertions are exact strings —
`["COMMIT acme 3 3", "COMMIT acme 2 5"]` at `:88`,
`["COMMIT globex 4 4", "CLOSE globex 4"]` at `:94`. Both durable-content
mutants and the wrong-value positive control die.

Anchor 3 is met, and this is where the artifact earns its score. The evidence
packet records that the whole-view corpus kills **0 of 3** `guard_relaxation`
faults (`evidence_P.md:50`) and that the ordering negative control `N01`
survives every generated instrument (`evidence_P.md:42`). The artifact's own
tests kill all three refusals — `test_close_rejection_order_is_the_declared_one`
(`test_quota_ledger.py:255-273`) walks the declared precedence explicitly — and
kill `N01` through `test_outstanding_ids_are_ascending_past_ten`
(`test_quota_ledger.py:162-171`), which reserves twelve times so that `r2` vs
`r10` distinguishes allocation order from string order. The shared suite never
gets past `r3` and cannot see it. That is two classes the whole-view corpus
structurally cannot reach.

Anchor 4 fails on both clauses. The cases are hand-written, not model-derived —
the author says so and the code shows it. And the record names no fault class
its tests cannot reach; the "What I was unsure about" section names *spec*
ambiguities, not *detection* blind spots. It has one: everything in `release`
that is not a plain refund, which is exactly where my two survivors landed.

**Prose did tempt me here.** `NOTES.md` is the most carefully argued document I
have read on this card, and the test file's docstrings are precise. I scored
only what executed; had the writing counted, this would have been higher, and
it is the well-written sweep docstring that turned out to be the false claim.

## D2 — Complexity: **2**

**I rejected the owner's amendment.** Three reasons, in order of weight:

1. The anchor says a simplification **was made** — an act, by an author, on a
   design, with a before and an after of *the same thing*. Nothing was
   refactored. Two authors independently produced two designs from one spec.
   Reading P as the "after" of Q assumes a lineage that does not exist.
2. The card's own D2 rule is decisive: *"A D2 of 3 or more requires the judge to
   say what got simpler and how the behavior survived it."* I cannot say what
   got simpler — `evidence_P.md:126-127` withholds Q's source, by design. I
   would be certifying a reduction I am structurally forbidden to inspect. That
   is the false clean this whole card exists to prevent (MF-027), and MF-020
   names the precise trap: a metric can improve because an edge was deleted, and
   I would have no way to see the deleted edge.
3. The numbers do not carry the reading anyway. 122 vs 129 production lines is
   seven lines. P carries *more* test lines (252 vs 190). `module_count` 1 vs 4
   is a different decomposition, not a simplification — and the packet itself
   says `state_writers` "discriminates nothing" (`evidence_P.md:120-121`).

Rejecting the amendment costs the artifact nothing it earned. Anchor 2 is
comfortably met and I measured it independently: exactly nine branch nodes
(`quota_ledger.py:140-147` for reserve's four declared rejections,
`:161`, `:177` for the two unknown-reservation paths, `:186-191` for close's
three), one per rejection in `FEATURE.md` and not one more. No god-state: the
most-written attribute is `_available` at two sites (`:150`, `:180`), all state
initialized in one constructor (`:103-110`), matching the harness's
`max_writers_of_one_attribute = 2`. The complexity is the behavior's, not the
structure's.

## D3 — Modularity: **2**

Anchor 2 holds on runtime call evidence, not import topology. `_LedgerFile`
(`quota_ledger.py:72-92`) has a two-method surface — `append`, `lines` — and
every filesystem operation in the module is inside it (lines 82, 83, 86, 91).
The domain reaches the durable side at exactly four sites: construct (`:110`),
read (`:134`), and two appends (`:168`, `:193`). That is a real seam, and the
declared shape (`NOTES.md:37-40`) is the shape the code has.

Anchor 3 fails, tested rather than inferred. The constructor takes a
`Path | str`, not a port, and instantiates `_LedgerFile` itself at `:110`, so a
duck-typed fake with the right two methods raises `TypeError`. The only working
swap is monkeypatching the module-private `quota_ledger._LedgerFile` — reaching
into the domain's own namespace, which is not "replacing an adapter without
touching the domain". The domain also imports `pathlib` at `:10` and types its
public constructor in terms of it.

This looks like a deliberate choice rather than an oversight — `NOTES.md:113-118`
declines "an abstraction over the file beyond the one small class that writes
it" as scope inflation, which is defensible against a spec that lists the
durable mechanism as free. It is still a 2 under the anchor as written.

## D4 — Behavior preservation: **2**

No baseline exists, so I read anchor 2 against the requirement — the only fixed
thing behavior can be preserved *relative to*. On that reading it holds: R4 is
checked against the file rather than the accessor across six rejection shapes
(`test_quota_ledger.py:126-130`); R5 re-reads every earlier line after each write
(`:133-139`); R1, R2 and R3 are recomputed from scratch in `check_rules`
(`:279-312`); the module docstring enumerates coverage beyond the shared suite
(`:1-13`); and the shared contract passes unedited, 28 tests, which I reran.

Anchor 3 fails twice over. The only model-shaped check is hand-written in the
same file rather than derived from a model — and it is degenerate, as measured
in section 3 above. A "400-step randomized sequence" that accepts five commands
is not a corpus and is not an invariant sweep; it is a rejection soak test with
a long runtime.

Anchor 4 fails outright: the artifact contains no demonstration that its check
can fail. I supplied one, and the answer was partly negative — X06 and X10 both
survived all 32 tests, for the same root cause.

## D5 — Honesty: **2**

Anchor 2 is met and some of it lives in the code rather than the report.
`NOTES.md:87-103` names three real limits unprompted: `available("nobody")`
raises `KeyError` because the spec gives queries no rejection channel and
inventing a sentinel would be inventing behavior; non-integer amounts fall
through the literal "less than 1" rule, with the sharp observation that *"if
integrality is meant to be enforced, the six-reason vocabulary is missing a
reason for it"*; and `bool` being an `int`. `NOTES.md:113-118` refuses scope.
`NOTES.md:125-129` volunteers that it ran `ls` and saw must-not-open filenames —
a disclosure that can only cost it something. In code, `Result.rejected`
asserts membership in the declared vocabulary and raises rather than emit an
undeclared reason (`quota_ledger.py:58`).

I was torn between 2 and 3 and took the lower. Anchor 3 asks the artifact to
refuse a positive verdict when its basis does not support one. In the one place
its evidence is strongest, it does the opposite: `test_quota_ledger.py:358-360`
declares the sweep "should have exercised both outcomes of every command, not
just rejections", and the guards written to enforce that are satisfiable by one
commit and three closes. The artifact emitted a green about its own coverage
that measurement falsifies. That is not a prose defect — it is a check that
certifies more than it verified, which is the exact failure mode D5 exists to
price. Separately, `NOTES.md:24-32` reports "28 passed" and "32 passed" with no
statement of what those tests do not reach, which is anchor 1's own wording.

Anchor 4 is therefore also out: the record contains no unflattering *result*.
The `ls` disclosure is unflattering about process, not about the thing scored.

---

## For the reader

The gap between the two instruments is the finding worth carrying forward. The
generated corpus and this artifact's hand-written tests fail in complementary
places: the corpus cannot reach refusals at all (0 of 3) but sweeps state space
the tests never visit; the tests catch every refusal and the ordering control
the corpus is blind to, but have a hole in `release` wide enough for two
mutants because their randomized arm collapses after 30 steps.

The cheap fix is one line in the sweep: lower the `close_tenant` probability or
drop closed tenants from the reserve pool, and assert per-command accept counts
rather than the three weak aggregate guards. Do that and I would expect X06 and
X10 to die, and D4 to become arguable at 3.

**Disclosure:** I opened no file on the must-not-open list. I do not know which
arm produced this artifact and made no attempt to infer it; the single-module
shape is consistent with several prompts and I drew no conclusion from it.
