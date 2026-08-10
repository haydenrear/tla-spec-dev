# `revision/` — the pass that has a before

Built by **RD-06**. Like everything else under `examples/validation/ab/`, this
directory is *experiment*, not mechanism: nothing here refuses anything, gates
anything, or blocks a promotion.

## Why it exists

`references/eval_scorecard.md`, D2:

> **3** — 2, **and** a simplification was made and its effect measured — the
> before and after figures are both recorded.
> **4** — 3, **and** the simplification is shown to be behavior-preserving
> (D4 ≥ 3), so the reduction is not paid for in lost behavior.

Every artifact this project has ever put in front of a judge was built from
nothing. **A greenfield artifact has no before**, so anchors 3 and 4 were
structurally out of reach for it — not scored down, unreachable. D2 has read 2
on every greenfield card ever written, and one epic was opened on the belief
that this said something about the *card* rather than about the *subjects*.

The `ports-as-adapters` evidence packet tried to reach it sideways: its
mechanical block covered all three arms at once "because the scorecard's D2
anchor 3 reads a before/after and one column cannot reach it". Three arms are
three artifacts, not one artifact twice. **Arm B is not arm A simplified.**

This prompt produces the missing shape: **one implementation, then the same
implementation revised.** Two trees, one lineage.

## What it is not

- **Not a fourth arm.** The arms are compared with each other and share a
  delivery envelope precisely so that the only difference between them is the
  treatment. This prompt is dispatched at a *different kind of input* — an
  existing tree — and no arm-to-arm number is measured on it.
- **Not a repair pass.** It forbids correcting behavior, and says so twice: a
  revision that also fixes bugs cannot be read as behavior-preserving, and the
  before/after stops meaning anything.
- **Not an instruction to make a number go down.** Section 1 carries `MF-020`
  in the same words arm B carries it, and Section 1 explicitly licenses
  *changing nothing*. A prompt that cannot come back empty-handed is a prompt
  that will always report a simplification.

## The one outcome this fixture must be able to produce

**"There was nothing worth simplifying, so nothing was changed."** If the
revision prompt could not return that, every before/after it produced would be
an artifact of the ask rather than of the code — and the round would have built
an instrument that can only agree with itself.

## Running it

```bash
# the shared contract, against a revised tree
QUOTA_LEDGER_DIR=<tree> QUOTA_LEDGER_IMPL=<module> \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q

# the figures, before and after -- two tables, never a delta (MF-020)
python3 scripts/code_complexity.py <before-tree>
python3 scripts/code_complexity.py <after-tree>
```

`scripts/code_complexity.py` has no `--compare` mode on purpose. Read two
tables. A printed `-12` is the shape that invites a reader to treat a fall as a
finding, and this project has a card withheld from a top score by both blind
judges for exactly that.

## What was dispatched

The bytes an agent actually received are in
`examples/validation/ab/dispatch/<round>/`, recorded by `dispatch_record.py`.
`PA-06-DF-10`: a round once measured a length claim against a file that was not
what the arm received and could not tell afterwards. **Measure the artifact,
not this file.**
