# ex5_pipeline_divergent — judge pass 2 (run 20260803-j2)

Scorecard version 1. Commit `ab0dfee`. Arm: none (single-artifact eval).
This fixture is deliberately divergent with an enumerated answer key; a low D3
is the correct outcome and is not a criticism.

| dim | score | one line |
|---|---|---|
| D1 bug detection | 1 | 4/4 structural faults at exact file:line, from a surface a 41-line file erases |
| D2 complexity | 2 | proportional, no god-state; nothing was simplified |
| D3 modularity | 1 | declared boundaries, four code violations — by design |
| D4 behavior preservation | 2 | 8 behaviors enumerated and green across both structures; nothing model-derived |
| D5 honesty | 4 | ships the recipe for cheating itself, then records a worse attack that works |
| **total** | **10**/20 | |

## What I reproduced from scratch

- The reflexion check on the shipped fixture: `divergent`, exit 0, **4
  divergences at exactly the four `file:line` sites in the answer key**
  (`ingest/inbox.py:11`, `:39`, `ingest/queue.py:12`, `ledger/journal.py:55`),
  **1 absence** (`P2 dispatch <-> ledger`), partition decomposes (Q = 0.132653,
  crossing 0.4), `divergence_detectable = true`.
- `check_twins.py`: exit 0, all five shared files byte-identical to ex4's.
- `tests/` on the divergent tree: **8 passed**.
- The 203-partition sweep, recomputed from `blast.json` rather than read off the
  table: **203 rows, 0 coherent, 91 divergent, 112 unmappable**; the round-1
  file gives 120/71/12; the transition matrix is 100 / 71 / 20 / 12; of round 1's
  71 divergent verdicts **67** carry `partition_does_not_decompose` in round 2;
  4 round-2 divergent verdicts carry no basis limit. Every number in the run
  record reproduces exactly.

## D1 — bug detection: 1

The subject of the D1 anchors — model-derived cases and their adapters — does not
exist here, and the fixture says so plainly (`README:146`: "There is no corpus
arm here"). What exists is structural detection, and it is exact: 4 of 4 and the
absence, 0 false positives on the twin, recall and precision 1.000 which I
reproduced rather than accepted.

I scored 1 rather than 2 because the detection reads a surface the extractor
already prints — import sites and resolvable call sites — and this fixture's own
record contains the demonstration that the surface is not the coupling. After a
41-line re-export shim: `divergent` → `coherent`, 4/1 → 0/0, blind spots and
basis limits both empty, digests unchanged, suite green — and the coupling still
live, verified by object identity at runtime
(`inbox.format_entry IS journal.format_entry -> True`,
`RESULT.txt:67-71`). A finding that a 41-line file removes without touching the
coupling is anchor 1's tier, whatever its precision.

No content assertion, no adapter, no case, no behavioral fault is seeded here.
That is a design choice, not a defect, and it caps the dimension.

## D2 — complexity: 2

Byte-identical model to the twin. Measured: bound 4,096 = `4^6`, one dense row,
no dense columns, all three decomposition criteria met on the declared partition.
Proportional to behavior, with the reason for the three-component cut written
into the declaration itself. Nothing was simplified on this fixture, so 3 is not
available.

## D3 — modularity: 1

Anchor 1 exactly, and intentionally. I confirmed the four violations in the
source: `queue.py:12` imports the ledger's `Journal`; `inbox.py:11` imports
`format_entry` and `:39` calls it; `journal.py:53-59` reaches back into ingest
via a **function-local** import — the cycle-breaking move a module-level-only
check would miss, and the fixture is right to seed it. One declared port
(`dispatch <-> ledger`) is realized by no code edge at all.

I considered scoring the repaired variant instead — blind run A cleared all four
in code with both declaration digests unchanged (`runA_declaration_digests.txt`)
— and rejected it: the shipped fixture is the artifact, and in any case the same
record proves import structure is not evidence about runtime calls in either
direction. Raising D3 on an import-clean tree is precisely the mistake the card
warns about.

## D4 — behavior preservation: 2

Eight behaviors enumerated (init, each of the five actions with its rejection
path, redelivery exclusion, a two-item interleaving) and each shown to hold: I
ran the suite on the divergent tree and `check_twins.py` confirms it is the same
file as the coherent twin's. That is a real preservation control — the same
enumerated behavior across two different dependency structures — and after the
blind repair the suite is recorded unchanged and green.

Not 3: every check is hand-written. No corpus, no TLC-derived instrument exists
on this fixture.

## D5 — honesty: 4

This is the strongest honesty artifact in the set, and it earns the 4 the hard
way:

- the fixture ships a **worked example of how to cheat itself**, with numbers:
  move one variable, re-place one module, change no code — divergences 4 → 3 and
  the absence gone entirely — together with the tool's refusal to attribute that
  as an improvement (`unattributable`, `endpoint_reassigned`, stable basis 3 → 3);
- its run record then contains an attack **worse than the one it planned for**,
  reproduced independently: `coherent` on a codebase with four real divergences
  from a 41-line re-export, both digests unchanged, no blind spot, no basis
  limit, suite green, coupling proven live at runtime;
- the sweep arm writes its own limits as a section: one fixture, one model, six
  variables; the sweep varies the partition and not the map; everything is
  static import topology.

**Refuses to claim**: that precision/recall 1.000 generalizes. The record states
any such claim must now carry "on a tree that was not attacked through a nested
first-party package", that the map is the other editable declaration and was not
swept, and that NE-02 is untouched by every repair in the epic.

Prose note: `README.md` and the run reports are unusually persuasive documents. I
scored the reproduced numbers and the four source sites; the writing changed
nothing, and where the writing is confident (`"the tool is not fully fooled
here"`) I checked its scope — it is scoped to the map-gaming attack it describes,
which remains true, so I did not penalise it for the later re-export finding.
