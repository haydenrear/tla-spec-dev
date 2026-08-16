# `SS-01` — the ledger moved, and the five decisions that live at that path

**Ticket:** `SS-01`, issue #273. **Branch:** `feature/SS-01`, cut from the
resolved OID `25600fa04ef26eb352cf3e6db5990e7f36a20ea8` (`origin/epic/stabilize-substrate`).
**Epic base for comparison:** `436c78c`, `17 / 1483 / 4 / 1504`.

---

## 1. The blast radius, MEASURED — and the inherited figure is wrong in both directions

Issue #271 section 7.1: *"**10 live files** (only `disposition.LEDGER` is
behaviour) plus **25 archival scorecards** that would cite a dead path."*

Re-derived with `git grep -l` at two named trees, "live" meaning outside
`specs/.history/` and `specs/results/`:

| tree | live files citing the dead path |
|---|---:|
| `436c78c` — the epic base, where the claim was inherited | **9** |
| `25600fa` — this ticket's base | **12** |

**Neither is 10.** The three added between them are this epic's own kickoff
writing — `STABILIZE-SUBSTRATE-EPIC.md`, `specs/desired_program_model/ticket_plan.yaml`,
and the relocated `specs/deferred_findings.yaml` itself — and all three cite the
dead path *as the defect they are describing*, so all three are records and none
is repointed.

**AND THE LITERAL-STRING SWEEP UNDERCOUNTS THE THING THAT MATTERS.** Widening to
any mention of `deferred_findings` at `25600fa` gives **21** live files, and the
nine the full-path grep misses include a **behavioural** one:
`scripts/spec_evolution.py:923` builds the path from parts
(`specs_dir / "desired_program_model" / FINDINGS_LEDGER_NAME`), so no grep for
the path finds it. That is `SS-01-DF-01`, below. **A blast radius measured by
grepping a path string cannot see a path built from parts, and that is the one
that had a consequence.**

The archival figure lands nowhere near 25 either, under four readings at
`436c78c`: **44** files under `specs/results/`, **34** under
`specs/results/scorecards/`, **23** `.md` under `specs/results/`, **19** `.md`
under `specs/results/scorecards/`. **None of the 187 `specs/.history/` files and
none of the `specs/results/` files were rewritten.** `R-H4`.

## 2. Behaviour repointed, and the two exceptions removed

| file | what it was | what it is |
|---|---|---|
| `scripts/disposition.py` | `LEDGER` = the dead path; `ARCHIVE_GLOBS` + `(mtime, size, path)` | `LEDGER` = `specs/deferred_findings.yaml`; archives resolved from entry manifests |
| `examples/validation/scorecards/score_tools.py` | `LEDGER_LIVE` = the dead path; `LEDGER_ARCHIVE_GLOBS` + the same ordering | same, duplicated deliberately (`RM-05` §3) |
| `tests/test_card_has_one_home.py` | an `OUT_OF_SCOPE` key naming one full path | `LEDGER_NAME`, keyed on the file's identity |
| `tests/test_workflow_close_keeps_the_ledger.py` | guarded on the dead path; 4 skips | subject is the sealed snapshot; 0 skips |
| `references/consumption.md` | the rule's stated scope | repointed |
| `examples/validation/instruments/instruments.toml` | the register's `watches` | repointed |

**The two exceptions #271 predicted a third of were the two archive-glob
blocks** — one per instrument, each enumerating `deferred_findings.yaml` at two
historical depths. Both are gone: a close NAMES the archive it wrote, in that
entry's `manifest.json` under `findings_ledger`. **The filename is no longer
enumerated at historical directory depths**, which is what made each new path
need a new exception, so there is no series for a third to join. (`disposition.LEDGER`
and `test_card_has_one_home.LEDGER_NAME` still each name the file once — §11.5.) The third was already being
demanded, red, at `tests/test_card_has_one_home.py:126`, and it was answered with
a rule on the ledger's name rather than a second path.

## 3. `CA-10-DF-10` — decided: the behaviour changes AND the claim is dropped

The claim was *"an archived ledger is FROZEN at that close"*. **It is false on
this repository's own record, and that is measured rather than argued:** the
close of `cut-the-apparatus-epic` wrote **278** rows into
`closed-snapshot/snapshots/desired_program_model/deferred_findings.yaml`; the copy
at the top of the same entry — the one its manifest points at — carries **296**.
Eighteen rows were appended to an "archived" file after its close, in the three
commits after `7d99969 Close the workflow`, because the close had left nowhere
else to write.

**Both halves change.** The *behaviour*: the live ledger now sits outside the
directory the close removes, so no writer ever again has cause to append to an
archive. The *claim*: `resolve_ledger` no longer promises a freeze it cannot
keep. It promises what the tree can be checked against — this is the copy that
close **recorded** — and `test_the_recorded_archive_is_not_promised_to_be_frozen`
fails if the freeze sentence comes back.

## 4. `DEFAULT_SWEEP` — decided: `specs/deferred_findings.yaml` added, and NO written decision is overridden

#271 framed this as *"changing it overrides a written decision"*. It does not,
and the record says so in its own words. `CA-10-DF-18`'s `suggested_fix`:
*"Instance 5 waits on `CA-10-DF-10`; **whatever address that decides is the
address `DEFAULT_SWEEP` should name**."* `SS-01` decided the address. The written
decision that instance 5 protected is `specs/.history/**` being out of scope, and
it is untouched — `specs/deferred_findings.yaml` is not under `.history`, and
`sweep_paths` still filters `.history` out of every pattern. The old
`specs/desired_program_model/*.yaml` entry is kept: it still reaches
`ticket_plan.yaml` while a workflow is open.

### 20 / 21 / 18 / 17 — WITHDRAWN AND REPLACED. #271 was right and I was not

**An earlier version of this section said the ledger "cannot account for" the
102 → 82 drop and that #271's *"17 REFUTED figures currently unswept"* was
"wrong twice". Both statements are false, the reviewer of PR #282 refuted them,
the epic owner re-derived it, and I have re-derived it again. `SS-01-DF-03`.**

The cross-tab on `(file × verdict)` over the 23 rows that left the sweep —
**which I never ran, and which decides the whole question**:

| | count | verdict | file |
|---|---:|---|---|
| gone | **17** | REFUTED | `specs/desired_program_model/deferred_findings.yaml` |
| gone | **3** | UNREACHABLE | `specs/desired_program_model/deferred_findings.yaml` |
| gone | 3 | REFUTED | `NEXT-EPIC.md` |
| added | 3 | REFUTED | `NEXT-EPIC.md` (re-anchored) |

**20 of the 23 gone rows are ledger rows. The ledger accounts for the −20
exactly, and it carried precisely 17 REFUTED rows, precisely unswept.**

| figure | what it is |
|---|---|
| **82** | the sweep at `25600fa`: 63 REFUTED, 17 UNREACHABLE, 2 HOLDS |
| **17** | **the ledger's REFUTED contribution at `ea624b9`** — #271's figure, correct as written |
| **20** | the ledger's whole contribution there: 17 REFUTED + 3 UNREACHABLE. **The −20 exactly** |
| **21 / 18** | the ledger at **this** tree, which grew by one counted figure as rows were appended |

**The error is worth more than the figure, and it is the one this ticket
exists to fix, committed by this ticket.** `scope`'s verdict is a joint property
of the **file** and the **tree it is swept in**. I measured the `ea624b9` ledger
under `--root <a bare directory holding only the ledger>` — a root I had built
for the measurement — got `21 / 18 REFUTED / 3 UNREACHABLE`, and reported it as
a property of the file. The same bytes in the full `ea624b9` tree return
`20 / 17 / 3`. **That is `SS-00-DF-01`'s own lesson — quote the tree, not just
the file — broken by the ticket that repaired `SS-00-DF-01`, in the paragraph
where it corrected someone else.** Reproduction in `scope-crosstab.txt`.

**One coincidence made the wrong reading plausible and is worth recording:** the
whole-record UNREACHABLE count at `25600fa` is **also 17**. Two different 17s,
and I matched #271's to the wrong one.

**What does NOT change:** the decision to add `specs/deferred_findings.yaml` to
`DEFAULT_SWEEP`, and the measured cost of it — **`scope` 82 → 103**, +18 REFUTED
and +3 UNREACHABLE. The corrected reading makes that decision *better* supported,
not worse: #271 had already measured what it was worth.

**The false version was also inside `score_tools.py`'s `DEFAULT_SWEEP`
docstring — the file that executes the reading rules — and is corrected there.**

## 5. `SS-00-DF-01` — repaired, and its stated mechanism refuted

**Repaired.** `audit` goes **9 violations → 0** at this tree. All nine were
`filed_as = CL-03-DF-04`, which is a real row in all three of the live ledger
(299), the recorded archive (296) and the ledger at `ea624b9` (259).

**Proof, per the acceptance clause: two independent fresh worktrees of the same
commit, same count.** See `two-checkouts-tip.txt`.

**And two claims in the finding and in charter §0 do not survive re-derivation
(`SS-01-DF-02`).** They say all 85 candidates share one mtime, so the ordering
*"degenerates to SIZE"* and *"THE LARGEST FILE WINS"*. Measured on a fresh clone:
**85 distinct mtimes** spanning 3.6 s, so size never breaks a tie — **mtime alone
decides**, landing on whatever git wrote last (`specs/.history` is checked out in
name order; `subtract-to-measure-epic` sorts last). And the **largest** candidate
is `cut-the-apparatus-epic/closed-snapshot/deferred_findings.yaml` at 1,152,237
bytes — **the correct one**. *Had it really degenerated to size the instrument
would have been right,* which matters because "sort by size instead" reads like a
fix and is not one.

Likewise *"9 on this worktree and 0 on another, at the same commit"*: **both
fresh clones report 9**, deterministically. The divergence is not between two
fresh checkouts — it is between a fresh checkout and one whose files have been
touched. Demonstrated, with not a byte of the tree changed:

```
$ python3 examples/validation/scorecards/score_tools.py audit    # 9 violation(s)
$ touch specs/.history/cut-the-apparatus-epic/closed-snapshot/deferred_findings.yaml
$ python3 examples/validation/scorecards/score_tools.py audit    # 0 violation(s)
```

**The claim that survives all of it, and it is the one that mattered: the
instrument's answer was a property of the checkout rather than of the tree.**

## 6. The four skips, and the second reason they were skipping

All four were `test_workflow_close_keeps_the_ledger.py:92`, guarded on the live
ledger existing at the dead path. **Repointing that guard is not sufficient, and
the baseline's expectation that they "unskip when `SS-01` repoints" does not
hold.** Their subject was the LIVE spec tree, and a live spec tree is only
closeable in the minutes between an epic's last ticket closing and its successor
being scaffolded. Run against this epic's tree the close refuses:

```
cannot close ticket workflow:
- ticket SS-01 is not closed: status=planned          (and SS-02 .. SS-08)
```

**So the skip was covering two independent reasons and only one of them was
filed.** The subject is now the sealed `cut-the-apparatus-epic` closed-snapshot —
still this repository's real record, still not a fixture, and closeable because
its tickets really are closed. `specs/.history` is read, never written; `R-H4` is
a rule about editing the record.

The assertions changed with the mechanism, and one INVERTED: the disposition test
used to require the words *"archived ledger"* on stderr, proving the fallback had
fired. It now requires their **absence** — the live ledger survived the close, so
nothing fell back.

## 7. What could not be done, and what is filed

- **`scripts/spec_evolution.py:923`** still sources the archive from
  `desired_program_model/`, so every close from here on records
  `findings_ledger: {exists: false}` and archives nothing. Outside `SS-01`'s
  conflict keys, **not blocking** — the property that mattered is now held by the
  address rather than by the archive. Filed as **`SS-01-DF-01`**, carried to
  `SS-07`. It is also the consumer a path-string grep cannot see.
- **`references/portable_scorecard.md:221`** still names the old path. Left
  alone: it is `RM-02`'s narrative record of what it found when it audited item
  6, not a live declaration. Same for `NEXT-EPIC.md`, `PORTS-AS-ADAPTERS-EPIC.md`,
  `STABILIZE-SUBSTRATE-EPIC.md` and `ticket_plan.yaml`, whose mentions are
  *about* the defect and are correct as written.
- **`ea624b9`'s 102-figure sweep was not re-derived.** I re-derived the ledger's
  own contribution at that commit (21 / 18 / 3, unchanged) and the 82 at this
  tree, which is enough to show the `−20 REFUTED` attribution is wrong; it is not
  enough to say what the residue is, and I do not claim it.
- **`sweep_paths` still reports nothing when a declared pattern matches zero
  files** (`CA-10-DF-18`'s other half). Not shipped here: this ticket adds no new
  report surface.

## 8. Instruments still running at the tip (`GOAL-four-results-still-stand`)

`audit` 0 violations; `scope` runs; `scope --path NEXT-EPIC.md` → **3 counted
figures, 3 REFUTED**, unchanged; `contested` → **9 contested dimensions over 39
judge groups, 0 unrecorded**, unchanged; `seal` runs; `serve | wc -c` = **6,281**,
card version **5**, served digest **`sha256:2d7d4a0506d9b259`**, anchors digest
**`sha256:f73b4d82638f09df`** — all unchanged, and `test_score_tools`'s
served-digest and frozen-bar fixtures pass.

---

## 9. `GOAL-tree-stabilizes` — the numbers that sum, and there are now FIVE

Runs are `uv run --with pytest --with pyyaml -m pytest tests -q`; collection is
`--collect-only`. Sealed here: `pytest-base-25600fa.txt`, `pytest-tip-final.txt`
(pre-review tip) and `pytest-tip-review.txt` (this tip), with the matching node
lists.

| | failed | passed | skipped | **xfailed** | collected |
|---|---:|---:|---:|---:|---:|
| **base** `25600fa` | **17** | **1483** | **4** | 0 | **1504** |
| pre-review tip `587d46c` | 8 | 1504 | 0 | 0 | 1512 |
| **tip** `<this commit>` | **8** | **1509** | **0** | **1** | **1518** |

`17 + 1483 + 4 + 0 = 1504` ✓  `8 + 1509 + 0 + 1 = 1518` ✓

**I INTRODUCED THE FIFTH CATEGORY AND IT HAS TO BE DECLARED.** The goal says
"four numbers that sum". After this ticket they do not: the `xfail(strict=True)`
pinning `SS-01-DF-01` is a fifth bucket, and a reader adding only four will be
one short. It is one node, it is deliberate, and `strict=True` means **it becomes
a FAILURE the moment `SS-01-DF-01` is fixed** — which is the point, and why an
`xfail` was the right answer to "the finding is untested in both directions".
**`SS-08` should report five numbers, or three tickets from now the sum will
quietly stop working.**

### Against the base: −9 failed, +26 passed, −4 skipped, +1 xfailed, +14 collected

- **−9 failed, numerator, 9 removed and 0 added** — 5 `test_disposition_requirement`
  + 3 `test_score_tools` (`SS-00-DF-01`), 1 `test_card_has_one_home` (the third
  exception, predicted by #271 §7.1). **The same 8 survive at every measurement
  point and none was touched**: the deliberate reds (`RM-06-DF-01`,
  `CA-04-DF-04`) and `SS-03`/`SS-06`'s rows. `test_ticket_retirement` now names
  **seven** planned tickets rather than eight, which is `SS-01` closing.
- **−4 skipped**, the entire population; §6 for the second cause.
- **+14 collected, denominator**: **+8** the original `R1` demonstration file,
  **+6** the review round — 4 parametrized empty/zero-byte/malformed/no-key
  ledger bodies (`SS-01-DF-04`), 1 three-entry archive-ordering case
  (`SS-01-DF-06`), 1 `xfail` (`SS-01-DF-01`).
- **+26 passed** = 9 reds repaired + 4 skips now running + 13 new passing nodes.
  ✓ (the 14th new node is the `xfail`).

**No pass, red, skip or collected node moved for an unattributed reason, at
either measurement point.**

## 10. The REQUIRED TLC entry does not exist, and it was not worked around

`python3 scripts/tla_spec_dev.py --spec-root specs run tlc` — **`run` accepts
only `spec-unit-tests` and `effect-conformance`.** Recorded as
**`N/A: no TLC target exists at this tree`**, per the epic owner's correction
(the assignment template carries it on all eight issues; `SS-03` hit the same
thing). Refusal output and the no-op model determination:
`tlc-and-model-delta.txt`.

---

## 11. Disclosures. Each of these was raised in review, not by me

**11.1 — The sealed history entry carries a superseded figure, and `R-H4` says
leave it.** `specs/.history/stabilize-substrate-epic/ticket-000-SS-01/summary.md`
and that entry's `results/RESULT.md` record **`8 / 1508 / 0 / 1516`**. That was
true of `61fc43c`, the tree at the moment of `close ticket`, when the ticket
workspace `open ticket` had scaffolded was still present and contributed 4
parametrized nodes. `close ticket` removed the workspace *as part of the same
operation that sealed the entry*, so the entry cannot describe the tree it
produced. **The authoritative figure is `8 / 1504 / 0 / 1512`** — this document
§9, `pytest-tip-final.txt`, measured on the committed tip. **The entry is not
edited**; both runs are sealed here and the difference is 4 parametrized nodes,
in the denominator, in the passing column. **`SS-08` should read §9, not the
entry.** `specs/results/skill_feedback.md` is live rather than sealed and has
been corrected in place.

**And this is a property of the close, not a mistake I made — it will recur on
all eight tickets.** `close ticket` removes the ticket workspace and seals the
history entry **in one operation**, so *the entry can never describe the tree it
produces*. Any ticket whose figures are measured before its close records a
number its own close then invalidates, and **`SS-08` will meet eight of them**.
The general repair is for the close to record the figure's tree, or for every
ticket to publish the pre-close/post-close pair as this one does; the narrow
fact is that the ticket-workspace delta is **+4 parametrized nodes, every time**.
Raised with the owner rather than filed — this ticket has already spent its
deferment budget of 5 (seven rows, `SS-01-DF-01` … `-07`).

**11.2 — Five files were edited outside my declared `implementation_scope`.**
`references/consumption.md` (`SS-02`'s), `examples/validation/instruments/instruments.toml`
(`SS-05`/`06`/`07`'s), `specs/desired_program_model/ticket_plan.yaml` (**`SS-03`'s,
in flight** — my edit is the single-word status flip `close ticket` requires),
and `specs/results/complexity_ledger.json` + `specs/results/skill_feedback.md`
(both written by the close itself). The first two are one-string repoints of
statements *about the instrument this ticket changed*; leaving them would have
left the rule and the register naming a file that does not exist. **They are
small and I believe correct, and they were undisclosed, which is the defect.**

**11.3 — I ran a stray `git checkout 25600fa -- .` in the worktree.** While
diffing collection I chained `git stash -q -u; git checkout 25600fa -- .;
git stash pop` into one command. The tree was clean and fully committed at
`61fc43c`, so the stash was empty; the `checkout` staged `25600fa`'s content over
my working tree, and the `pop` collided with a pre-existing unrelated stash from
another branch. **`git reset --hard HEAD` restored the tree, and every figure in
this document was re-derived from the committed tree afterwards** — the reviewer
independently re-derived them from the commits and confirmed nothing moved.
**It affected no measurement: the suite run had already completed and the
collect-only had already been written before the chain ran.** It is disclosed
here because it was disclosed nowhere in the record, and a disclosure that lives
only in a chat transcript is not a disclosure. **The rule it breaks is the one
this epic's §8 already pays for** — do not chain a destructive git command behind
a `;`.

**11.4 — `two-checkouts-tip.txt` is measured at `61fc43c`, not at the tip.** The
two-clone proof was run before the ticket close and the file says so. The
reviewer re-ran it at `587d46c` on two fresh clones and got **0 / 0**, so the
claim holds at the tip; the artifact is labelled rather than re-run.

**11.5 — "No filename is enumerated anywhere" overstated it.** `disposition.LEDGER`
names `specs/deferred_findings.yaml` and `test_card_has_one_home.LEDGER_NAME`
names `deferred_findings.yaml`. What was removed is the *enumeration of that
filename at historical directory depths* — the two archive-glob tuples — which is
what made each new path need a new exception. **The substantive claim holds; the
sentence was wider than the fact.**

## 12. What the review changed in the code

| finding | change |
|---|---|
| `SS-01-DF-03` | `RESULT.md` §4 and the `DEFAULT_SWEEP` docstring corrected |
| `SS-01-DF-04` | `_finding_ids` returns `None` when the ledger names no findings; the UNVERIFIED line says which state it hit; 4 parametrized cases |
| `SS-01-DF-05` | the UNVERIFIED refusal exits **2**, not 1; the docstring states both non-zero outcomes |
| `SS-01-DF-06` | `created_at_utc` is parsed, not string-compared; unparseable sorts oldest; a three-entry ordering test |
| `SS-01-DF-01` | re-routed to the **owner** — no ticket on this epic carries `scripts/spec_evolution.py`; and now an `xfail(strict=True)` that flips when it is fixed |
| `SS-01-DF-07` | `SS-01-DF-02`'s broken evidence citation corrected before merge |
