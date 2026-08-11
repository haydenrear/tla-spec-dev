# Running this scorecard on your own project

`references/portable_scorecard.md` says **what** transfers and what does not.
This says **how** — the file layout, the four commands, and the one rule that
changes the card. It is deliberately short; everything it does not say is in the
card itself, `references/eval_scorecard.md`.

**Read the portability page first if you have not.** It is the reason some of
what you are about to run will not mean for you what it means here.

---

## 1. What to copy, and what is optional

Three files, all under `examples/validation/scorecards/`:

| file | needed for | optional? |
|---|---|---|
| `score_tools.py` | everything below | **no** |
| `architecture_tags.py` | the architecture axis that annotates a comparison | yes |
| `subjects.toml` | the same axis: it declares what a scope *is* | yes |

Plus the card: `references/eval_scorecard.md`. Copy it and edit it — it is meant
to be edited, and §4 is how.

**Optional means optional.** `serve`, `scaffold`, `check`, `index`, `seal`,
`history`, `contested`, `scope` and `audit` all run with `score_tools.py` alone.
Without the other two, `audit` reports the architecture axis `UNVERIFIED` by
name and checks the rest; `tags` refuses and says why. Neither crashes, and
neither wants an empty file created to appease it.

## 2. Where the tool thinks your tree is

The tool finds the tree root by walking up from itself for the first ancestor
carrying `references/eval_scorecard.md`, then for the first carrying `.git`. So
put the card at `<root>/references/eval_scorecard.md` and put the tool anywhere
you like — depth is not counted.

If your layout fits neither rule, set `SCORECARD_REPO_ROOT`. Rounds live wherever
you point `scaffold`, `check` and `index`; the commands that read the whole
record — `seal`, `audit`, `history`, `contested`, `tags` — default to
`<root>/specs/results/scorecards/` and each takes `--root`.

## 3. The four commands you will actually use

```bash
T=examples/validation/scorecards/score_tools.py

python3 $T serve                       # the exact bytes a judge is handed
python3 $T scaffold results/round-1 \
    --example my_subject --arms A,B --judges 2
python3 $T check results/round-1 --require-filled
python3 $T index results/round-1
```

`scaffold` blinds by default: arms are emitted under opaque labels and the
mapping goes to an `UNBLINDING.md` the judges are not given. `serve` is the
whole of what a judge reads — nothing else in the card file reaches one, by
construction, because `serve` renders parsed structure and never file text.

Then `seal` the round, and `audit` reads the sealed record back.

## 4. Changing the card, which is the part that has rules

The rule is in the card, under `Changing this card`. Mechanically it is **two
edits to your copy of `references/eval_scorecard.md` and no edit to any Python**:

1. change `**Scorecard version N.**` at the top to your new number;
2. add a row for it to `### Version history`, **keeping every older row**.

That row carries two digests and they answer different questions:

- **anchors digest** — did the *bar for a score* move? Keep the old anchors and
  it does not.
- **served digest** — did anything a *judge reads* move? A rewritten caveat, a
  rewritten preamble, an edited scoring rule or an edited note all move this one
  while leaving the anchors digest alone.

You do not have to compute either by hand. Put a placeholder that still looks
like a digest — `` `sha256:0` `` — in both cells, run `check`, and the refusal
prints the value it wanted:

```
$ python3 $T check results/round-1
INVALID references/eval_scorecard.md: version 5 declares no served digest. …
        Add `sha256:…` to the row for 5.
```

**A version your card does not declare is refused, never stamped.** Asking for
one before you have bumped the card prints the two edits above rather than
emitting a card with a neighbouring number on it. And once the card declares it,
`scaffold` needs no flag: the default version is the one the card declares.

**Re-score one prior subject under both versions.** That is the half of the rule
no tool can do for you, and it is the only thing that makes a number from before
the bump comparable to one from after. Freeze a copy of the card file before you
edit it and point the old arm at it with `--rubric <frozen copy> --card-version
N`; `examples/validation/scorecards/rubric_v3_frozen.md` is this project's own.

## 5. What will not travel

Nothing here stops you scoring your project on this card. Several things stop
the *numbers* meaning what they mean in this repository, and they are measured
rather than guessed: `references/portable_scorecard.md` §2, §6 and §7. Read them
before comparing your score to one of ours.
