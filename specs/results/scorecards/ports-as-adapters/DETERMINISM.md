# Determinism — PA-06

**A nondeterministic instrument is a finding however good its first run.**

## The 8-instrument table

Arm C's table was produced twice, end to end, from the same corpora against the
same tree, and the two JSON artifacts were compared after normalisation (sort
keys; drop the `out` path, which is the invocation's own output filename and not
evidence about a mutant).

| subject | run 1 vs run 2 |
|---|---|
| `arm_c` | **identical** — `kill-table-arm-c.json` vs `determinism-arm-c-run-2.json`, zero keys differ, INCLUDING the `evidence` block that carries the failure text of every failing execution |

Arms A and B are not re-run here for determinism, because a stronger check is
available for them and was run instead: their tables are compared **cell for cell
against the predecessor's sealed tables at `f052d3c`** and reproduce them
exactly. Two runs a minute apart agreeing is weaker evidence than one run
agreeing with a run made by a different ticket, on a different day, across two
declared instrument changes.

## The port-binding table

Not run twice at PA-06 either, for the same reason and with a better check:
every subject PA-04 measured was re-measured on this tip and diffed against
PA-04's sealed output.

| subject | cells moved vs PA-04's sealed run |
|---|---|
| `reference_ports` | **0** |
| `arm_a` | **0** |
| `arm_b` | **0** |
| `arm_c` | n/a — first run |

Each cell of that table runs in a **fresh interpreter**. `EVAL-RERUN-DF-01` is
why: a purge keyed on a fixed list of binding-module names left a module holding
a handle on the pristine tree, every mutant executed against unmutated code, and
the run reported 11 of 11 SURVIVED with green controls. A subprocess cannot hold
a stale handle, so that class of bug is unreachable here by construction rather
than by a list being correct.

## The corpus

The port corpus regenerated at this tip has `cases.py` sha1
`08265aff0d81f27f4dfc9694d2a69c3c5b6e695c`, **byte-identical to the value PA-03
sealed and PA-04 quoted**. Same corpus, three tickets, two instrument changes
between them.
