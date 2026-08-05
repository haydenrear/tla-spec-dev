# HP-05 narrative: the mapping stops being a thing an expert remembers

## What this ticket claimed and what it delivered

The claim was that the one mechanism in this project with a measured,
replicated edge — effect providers that assert durable **content** — was not
the default, and that the difference between having it and not having it was
worth about 30% of that instrument's yield.

Three things now hold that were not true at the epic tip:

1. `scripts/generate_python.py` **generates** the content-asserting provider
   from the manifest, for every port declared `role: effect`. It also generates
   the silent one, so that choosing to run without a durable-write oracle is a
   visible edit to a mapping file rather than an assertion somebody simply did
   not write.
2. Codegen **binds** the content-asserting provider in `case_adapters.toml` for
   any effect port that has no binding. Additive only: a table somebody wrote is
   never rewritten, so a deliberate choice survives regeneration.
3. Every degraded configuration **announces itself in the run's output**, in one
   of two shapes, with the same closing sentence: *kills counted under this
   mapping are a FLOOR, not a total, and a green run over-reads.*

## The measurement, and why one column exists only as a control

One corpus, three mappings, differing in exactly one line of TOML.

| class | n | map-none | map-silent | map-checking | suite |
|---|---|---|---|---|---|
| cross_aspect | 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| durable_content | 2 | 1 of 2 | 1 of 2 | **2 of 2** | 2 of 2 |
| guard_relaxation | 3 | 0 of 3 | 0 of 3 | 0 of 3 | 3 of 3 |
| ordering | 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| output_oracle | 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| wrong_value | 2 | 1 of 2 | 1 of 2 | 1 of 2 | 2 of 2 |

`map-none` is a **reproduction control**, not a result. This instrument installs
a seam the reference implementation does not have — it routes `_append_line`
through the bound port while still writing the file — and a seam that changed
the baseline would make the map-checking column unreadable. It did not:
map-none reproduces HP-03's committed `corpus-whole` column in all ten rows.

So the checking/silent difference is one cell, M04, and it is the cell the
ticket was aimed at.

## Three things that are unflattering and are the point

**M05 was already dying.** The dispatch brief said both durable-side mutants
survive both corpora and die only on the hand-written suite. That is true of M04
and false of M05: HP-03's own committed kill table records M05 as KILLED by
corpus-whole. The cause is in the model — the CLOSE element is
`<< "CLOSE", t, committed[t] >>`, so its third slot *is* the total, and the
ordinary projected-state comparison already sees a zeroed one. Only the COMMIT
element drops its total, and only M04 lives there. **One mutant moved, not two.**

**The 30% figure does not reproduce as a proportion.** On the blind agent's
16-mutant catalogue the mapping was worth 3 of 10 kills. Here it is worth 1 of 6
under the checking mapping, and 1 of 10 mutants overall. The *direction* has now
replicated three times out of three attempts on three fixtures. The *magnitude*
is fixture-dependent, and quoting 30% as a property of the mechanism rather than
of ex4 would be the same mistake round 1 made with its guard-relaxation
explanation.

**The generator is still worse than a suite written in an afternoon.** Suite 10
of 10. Whole-view corpus under the checking mapping, 6 of 10. Whole-view
(checking) plus HP-03's negative corpus, **9 of 10** — up from 8 of 10, so the
gap narrows from two mutants to one. The survivor is M07, which the catalogue
declares a **positive control** that must die on every instrument. It does not,
because it is seeded inside `reserve()` and Reserve contributes zero executable
cases. That is a corpus-executability problem, not an oracle problem, and it
means the `wrong_value` row is not citeable as a clean measurement while its
control is red.

## What could not be reached, and where the line is

The honest answer to *"does a scaffolded project assert content without anyone
configuring it?"* is **yes once it declares an effect port, and the scaffold does
not help it get there.** `scaffold project` still emits a `providers.py` whose
body is `raise NotImplementedError` and a commented-out `[effect_providers.*]`
table. Those live in `scaffold_spec.py` and `onboard_program_model.py`, which are
in no ticket's conflict keys and not in HP-05's edit permission. Filed as
HP-05-DF-01, not fixed.

The runner also never names the mapping it loaded. The provider recovers the
name from `TLA_SPEC_DEV_MAPPING` or from `--mapping` on the command line, and
says `<unnamed mapping>` when it cannot. That workaround is visible in the
output as a workaround. `run_generated_case_adapters.py` is HP-04's conflict key
and HP-04 was running concurrently. Filed as HP-05-DF-02, not fixed.

## `no_new_gates_rule`

Nothing added here refuses anything. An unbound port runs. A silent provider
runs. A port with no `content:` block runs. Codegen never fails because a
mapping is weak, and the audit is a `print`, not an exit code. The one thing
that raises is the content assertion itself — which is the oracle firing on a
failing case, i.e. a kill, i.e. the instrument working.
