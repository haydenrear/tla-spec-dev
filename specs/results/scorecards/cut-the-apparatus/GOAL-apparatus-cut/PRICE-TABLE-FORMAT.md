# The epic price-table format

**Established by `CA-02` (issue #256). Every cutting ticket in
`cut-the-apparatus` reports its cut in this shape.**

This is a **plain markdown file with a fixed row shape and no code behind it**,
and that is a deliberate choice rather than a shortcut. The epic is about cutting
apparatus. **A tool for measuring the cutting of apparatus is apparatus** — it
would need its own manifest, its own tests, its own demonstrations and its own
registry row, and `RD-02`'s removal census is the worked example of exactly that
happening: it shipped to measure removals and became one of the things `CA-02`
removed. There is no validator for this file and there is deliberately not going
to be one. It is read by people.

The discipline it replaces is real, though, and it is `RD-02`'s best finding:

> `subtract-to-measure` published **-225 lines from `scripts/`** and the same
> epic added **1,677 net `code_lines`** across the trees it touched, because
> every removal shipped instruments, tests and demonstrations to prove the
> removal safe and **nobody counted that as a cost**.

**So the row shape forces a cut to report what it ADDED.** A price table with an
empty "added" column is making a claim, not omitting a field.

---

## 1. The removal table — one row per deleted file

| column | what goes in it |
|---|---|
| `surface` | `scripts/`, `examples/validation/`, `tests/`, or `specs/`. **Never a combined figure, and never combined with the card.** |
| `path` | The deleted path, exactly. |
| `lines` | Lines in that file at the ticket's base commit. |
| `kind` | `py`, `toml`, `md` — so a Python-line claim can be separated from a total. |
| `finding` | **The finding ID that justifies this deletion.** A row with no finding ID does not ship; `GOAL-apparatus-cut` clause (b) fails on it even if the lines fell. |

## 2. The addition table — one row per file this ticket ADDED or GREW

Same columns, minus `finding`, plus `why`. **This table is mandatory and may not
be omitted when it is empty — write `none` in it explicitly**, because the
failure this whole format exists to catch is an addition that nobody wrote down.

## 3. The net figures, per surface

Every surface reported **separately**, each with the tree it was measured on:

```
surface                 before      after       delta
scripts/                 27,652     27,652          0
examples/validation/     15,901     14,457     -1,444
tests/                   32,162     31,274       -888
```

**The card is reported separately and is never added to any of these**, because
`RM-03-DF-03` makes them incommensurable: the change rule keeps old anchors and
`R-H4` seals the record, so a card removal cannot delete prose or code, and three
epics called themselves simplifications and came out net-additive **because that
outcome is required by construction**.

```
card: `score_tools.py serve | wc -c`   6,281 -> 6,281   (digest sha256:...)
```

## 4. What the tree can no longer do

**Prose, not a table, and not optional.** One paragraph per capability removed,
each stating the capability in the form a future reader would search for, and
**what the record says that capability was worth**. "Nothing, it was unused" is
an acceptable answer only with a measurement behind it.

## 5. Which sealed results depended on it

**Checked, never assumed.** For each: does it still reproduce from the sealed
record, and **does the instrument that produced it still run at the tip?** A cut
that makes a sealed subject underivable, a demonstration stale, or a manifest
unreadable says so **here**, with the numerator/denominator movement named per
`denominator_rule`.

**Distinguish READABLE from RE-DERIVABLE.** A sealed transcript that still opens
is not the same as an instrument that still runs. **Answer both, separately.**

### Run this before answering, because prose did not catch it

`CA-02` — the ticket that wrote this format — answered *"yes, still runs"* for a
result whose producing script its own deletion had already broken, and no amount
of careful writing found it. **The mechanical check is one command per deleted
path, and it is required:**

```bash
# for every path this cut deletes, find anything that LOADS it
git grep -n "$(basename <deleted-path>)" -- specs/ references/ scripts/ examples/ tests/
```

**`specs/results/` is where this bites:** sealed measurement scripts live there,
they are **not exercised by the suite**, and **`R-H4` forbids editing them** to
repair the breakage. So the only moves available are *disclose it* or *do not
make the cut* — pick one and say which in §4.

## 6. Suite movement, under `denominator_rule`

**If the red count moves, say whether the numerator fell or the denominator did.**
Deleting the thing a red tests is a **denominator** move and must never be
reported as a repaired red. State it in this form:

```
baseline:  7 reds  (2 deliberate, 4 inherited-undeclared, 1 CA-00-DF-02)
after:     N reds
movement:  numerator <x>, denominator <y>, because <cause>
```

---

## Worked instance

`specs/results/scorecards/cut-the-apparatus/CA-02/PRICE-TABLE.md` is the first
table in this format and is the reference for anyone filling one in.
