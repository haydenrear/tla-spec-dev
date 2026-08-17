# `stranded-loaders` demonstration fixtures — SS-05

Two one-file record roots, staged by `demonstrate.py` for the
`stranded-loaders` row in `instruments.toml`.

`demonstrate.py` supports `stage` and `mutate` only; the `write` primitive
belongs to `score_tools.py absent-input`'s staging and is silently ignored
here. That cost this ticket two `MISS` rows before it was noticed, and it is
recorded so the next author does not spend the same minutes.

- `stranded/` names `scripts/no_such_file_this_repository_has.py`, which this
  repository does not have and must not acquire. If a file ever appears at that
  path the failing demonstration stops reproducing, and `demonstrate.py`
  REPORTS a demonstration that stopped reproducing rather than skipping it.
- `resolves/` names `scripts/disposition.py`, which this repository ships.

Both are FIXTURES OF THE INSTRUMENT, not subjects of the toolchain: the sweep
reads string literals out of `*.py`, so one literal each is the whole input.
