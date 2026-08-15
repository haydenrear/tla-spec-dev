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
entry's `manifest.json` under `findings_ledger`. No filename is enumerated
anywhere, so there is no series for a third to join. The third was already being
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

### 20 / 21 / 18 / 17, reconciled exactly

| figure | what it actually is |
|---|---|
| **82** | counted figures over `DEFAULT_SWEEP` at `25600fa`: 63 REFUTED, 17 UNREACHABLE, 2 HOLDS |
| **17** | the **UNREACHABLE** count in that 82. #271 calls it *"17 REFUTED figures currently **unswept**"* — **wrong twice**: they are UNREACHABLE, not REFUTED, and they are inside the sweep, not outside it |
| **21** | what the ledger carries, and what was genuinely unswept: `scope --path specs/deferred_findings.yaml` |
| **18 / 3** | that 21 split REFUTED / UNREACHABLE |
| **20** | the drop from #271's `102` at `ea624b9` to `82` at `436c78c`. **The ledger cannot account for it**: the same file scoped at three versions — `ea624b9` (259 rows), the closed snapshot (296) and live today (299) — returns **21 / 18 REFUTED / 3 UNREACHABLE every time**. A `−20 REFUTED` attributed entirely to the ledger is off by one figure and misclassifies three; the residue is the `NEXT-EPIC.md` re-anchoring the charter mentions in the same sentence, which I did not re-derive at `ea624b9` and do not claim |

**Measured cost of the decision, at this tip:** `scope` moves **82 → 103**.
REFUTED 63 → 81 (+18), UNREACHABLE 17 → 20 (+3), HOLDS 2 → 2. **+21 denominator,
caused by a file entering the sweep — nothing was checked, refuted or repaired to
produce it.** `GOAL-counted-figures-reach-the-record`'s baseline of 82 is
superseded at the tip and this is the cause.

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

## 9. `GOAL-tree-stabilizes` — four numbers that sum, at both ends, every movement attributed

Both runs are `uv run --with pytest --with pyyaml -m pytest tests -q`, in this
worktree, sealed beside this file as `pytest-base-25600fa.txt` and
`pytest-tip.txt`; collection is `--collect-only`, node lists sealed as
`collection-base-25600fa.txt` and `collection-tip.txt`.

| | failed | passed | skipped | collected |
|---|---:|---:|---:|---:|
| **base** `25600fa` | **17** | **1483** | **4** | **1504** |
| **tip** `61fc43c` | **8** | **1508** | **0** | **1516** |
| movement | **−9** | **+25** | **−4** | **+12** |

`17 + 1483 + 4 = 1504` ✓  `8 + 1508 + 0 = 1516` ✓

**The base reproduces the epic baseline exactly** — `17 / 1483 / 4 / 1504`, the
figure in `GOAL-tree-stabilizes`' baseline evidence, measured on my own worktree
before any edit.

### −9 reds. NUMERATOR, every one of them, and none is a denominator effect

Node-for-node diff of the two FAILED lists: **9 removed, 0 added.**

| red, at the base | cause | why it is green now |
|---|---|---|
| `test_disposition_requirement` × 5 | `SS-00-DF-01`, `assert 88 > 200` | `D.LEDGER` now resolves to the live 301-row ledger instead of an 88-id snapshot |
| `test_score_tools` × 3 (`…passes_its_own_audit`, `…with_rh6`, `…rh5_demonstration_still_goes_red`) | `SS-00-DF-01`, same cause via `_finding_ids` | `audit` 9 violations → 0 |
| `test_card_has_one_home::test_only_the_card_states_…` | issue #271 §7.1's prediction firing — the third carved exception, demanded live | answered with a rule keyed on the ledger's name, not a third path |

**Not repaired, and deliberately so:** `test_architecture_tags::test_the_same_tag_control_holds`
(`RM-06-DF-01`) and `test_instrument_demonstrations` × 2 (`CA-04-DF-04`) are
still red. `test_source_citations` × 3 and `test_goal_baseline_is_a_card` are
`SS-06`'s and `SS-03`'s. `test_ticket_retirement` clears itself as tickets close.
**No red was repaired silently and no new red was introduced.**

### −4 skips. The population is zero, and the second cause is filed

All four were `test_workflow_close_keeps_the_ledger.py:92` (`CA-10-DF-12`). They
run now. **They did not unskip by repointing alone** — §6 above: the subject was
the live spec tree, which refuses its own close while a workflow is open. The
subject is now the sealed `cut-the-apparatus-epic` snapshot. **No skip remains
anywhere in the suite.**

### +12 collected. DENOMINATOR, split two ways, and one half is not mine to claim

Node-for-node diff of the two collection lists:

| nodes | cause |
|---:|---|
| **+8** | `tests/test_ledger_resolution_is_deterministic.py` — the `R1` demonstration this ticket owes for `SS-00-DF-01`, including its absent-input case |
| **+4** | `test_spec_yaml_valid.py::test_spec_yaml_parses` is parametrized over the spec YAML files it discovers, and `open ticket SS-01` scaffolded `specs/tickets/SS-01/`: a second `ticket.yaml`, a second `complexity_ledger.yaml` and two more `spec_manifest.yaml`. **Denominator movement caused by scaffolding a ticket workspace — nothing was written, checked or repaired to produce it**, and every ticket after this one will do the same |
| ±2 | two `test_workflow_close_keeps_the_ledger` tests renamed with their assertions; a wash, listed so the diff reconciles |

### +25 passes, and they reconcile exactly

**9** reds turned green **+ 4** skips that now run and pass **+ 12** newly
collected nodes, all passing **= 25.** ✓ **No pass moved for an unattributed
reason.**
