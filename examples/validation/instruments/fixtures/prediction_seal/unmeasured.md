# PREDICTIONS — fixture: a subject nothing has measured

Not a real predictions file. It exists so `check_prediction_seal.py` has a
**passing** demonstration in `instruments.toml`: a no-kill prediction whose
mutant appears in no kill table anywhere, so the checker must report nothing and
exit 0.

Synthetic on purpose. A passing demonstration pinned to a real prediction would
stop demonstrating the moment somebody measured its subject — which is the exact
decay `FI-04-DF-04` and FI-02's `R-H5` demonstration both ran into.

### N90 — a mutant nobody has run
**Instrument:** M97 under `corpus-whole`.
**Direction:** FLAT at zero on every corpus instrument.
`M97` is not seeded in any catalogue this repository ships and appears in no
sealed kill table. There is nothing for the seal check to contradict.
