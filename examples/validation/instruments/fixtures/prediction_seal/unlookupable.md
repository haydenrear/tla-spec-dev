# PREDICTIONS — fixture: a no-kill prediction with no lookupable subject

Not a real predictions file. It is `check_prediction_seal.py`'s **blind spot**
demonstration in `instruments.toml`.

The row below predicts that nothing will be killed, and names its instrument as
a *table* rather than as a mutant and a column — which is how `N03` and `N07`
are written in the sealed `PREDICTIONS-PA.md`. There is no cell to look up, so
the checker reports `UNPARSED` **and exits 0**.

That is the failure direction that matters: a reader who watches the exit code
sees green on a prediction that was never checked at all. The `UNPARSED` block
is printed for exactly this reason, and `FI-05-DF-03` records that the checker
reaches 1 of the 3 no-kill rows in the only real file it has run against.

### N91 — nothing will move, stated in a way nothing can check
**Instrument:** the per-mutant per-arm per-instrument table, every row, before
and after.
**Direction:** FLAT — zero cells, on every row.
No mutant id and no instrument column appear in the instrument field, so no cell
can be looked up and no record can contradict this at seal time.
