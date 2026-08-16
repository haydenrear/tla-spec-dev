# `SS-07` pointers — read this before the baseline

**Added by `SS-07` (issue #276) on 2026-08-16. It edits nothing beside it;
`baseline.md` is the owner's and is left alone.**

## The disclosure this goal's clause (d) asks for

**`specs/results/scorecards/close-the-loop/GOAL-price-means-something/00-DISCLOSURE-NOT-RE-DERIVABLE-AT-THE-TIP.md`**

Clause (d) — *the stranded disproof instrument is DECIDED* — was decided
**DISCLOSE**, and that file is the disclosure. It also records something the
record did not have: `CA-02-DF-04`'s restore command had never been executed,
and running it reproduces `repriced_history.py` **byte-identical** to its sealed
transcript. **Read the limits stated there before quoting it: it is a pure
replay over inputs frozen at `37ab155`, so byte-identity was guaranteed by
determinism. It authenticates the transcript. It does not re-derive the claim
against today's record, and `CA-08`'s decision stands.**

## What is NOT pointed at it, said plainly

By `SS-07-DF-04`'s own standard — *delivering an instrument is not consumption* —
writing a disclosure into one directory is **routing**. Measured:
`grep -rln "00-DISCLOSURE-NOT-RE-DERIVABLE"` returns `SS-07`'s `RESULT.md`, this
file, and the disclosure itself. **Every other document carrying the claim still
says nothing about it:** `NEXT-EPIC.md` §5,
`cut-the-apparatus/CA-02/PRICE-TABLE.md`, `.../CA-04/PRICE-TABLE.md`,
`.../CA-08/RESULT.md`, `close-the-loop/CL-04/RESULT.md`, `RESULT-CL-02.md` and
`specs/results/skill_feedback.md`. **All of them are outside `SS-07`'s conflict
keys, and four are sealed results of closed tickets, so `SS-07` did not touch
them.** The epic owner decides; the list is in `SS-07/RESULT.md` §4 as a table.

## Three figures in `baseline.md` that moved, so nobody re-quotes them

Re-derived at `48f9c7e` and again at `06cbcce`, in two independent fresh
worktrees:

| `baseline.md` says | at the epic's wave-1 tip | why |
|---|---|---|
| `scope` **82** counted figures (§5) | **103** | `SS-01` added the relocated ledger to `DEFAULT_SWEEP` |
| `audit` reports **9** violations (§5) | **0** | `SS-01` repaired `SS-00-DF-01`; 0 in two independent fresh checkouts |
| *"all 85 candidates share one mtime and the largest file wins"* (§5) | **refuted** | 85 distinct mtimes; size never consulted. The charter withdrew this on 2026-08-16 |

**The owner is correcting `baseline.md` itself.** This page exists so the
correction is discoverable in the meantime.

## What "verified by execution" does and does not cover

`SS-07`'s first draft called all four results *verified by execution*. **Narrowed
after review:** three halves were genuinely **re-executed** —
`test_journal_conformance.py` (`14 passed`), `check_catalogue.py --arms`,
`architecture_tags.py derive`. The rest, including **result 3 entirely**, was
`index`/`history` **re-rendering the sealed `scorecard.json`**: proof the card
opens, parses and still says what the record claims, which is what clause (a)
asks — **not** a recomputation, and **no judge was re-run**. The full table is
`SS-07/RESULT.md` §1.

## Running `index` over this record MUTATES it

`SS-07-DF-01`: **16 of the 18 sealed card trees change on disk** when `index` is
run over them — 13 rewritten, 3 created — and `score_tools.py:1657` has no
read-only mode. **Every score value is preserved**; the staleness is
presentational. **`SS-08` will trigger this, because this goal's own harness
says to check that the sealed cards render.** Run `git status` afterwards and
revert.
