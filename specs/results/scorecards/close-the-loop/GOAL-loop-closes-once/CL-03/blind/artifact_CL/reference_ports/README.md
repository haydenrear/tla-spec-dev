# `reference_ports/` — the second anchor tree, and why there is one

**THIS IS NOT AN ARM.** Neither is `../reference/`. Nothing here is dispatched
to an agent, judged, scored, or placed in a table beside arm A's, arm B's or
arm C's numbers.

## Why a second reference exists

`../reference/quota_ledger.py` is one flat module. The PA catalogue has to seed
faults **inside an adapter implementation**, and that tree contains no adapter,
so there is nowhere in it for such a fault to be. A catalogue that cannot
express a fault class produces a zero that says nothing — the same argument
that made `available` a stored field rather than a derived one in the flat
reference.

The predecessor measured what happens in the region this tree exists to
represent, and it is the reason this epic exists:

> `BA-B14`, a fault in arm B's in-memory journal adapter, **survives every
> instrument including the hand-written suite.** … **The port removes places for
> some faults to live and creates a region no shared oracle reaches** — the fake
> that earned arm B its D3 = 4 is verified by nothing outside arm B's own tests.
>
> — `specs/results/scorecards/hexagonal-prompting/FINDINGS.md`

## What is carried forward, and what is new

**Carried forward, unchanged:** the feature (`../FEATURE.md`), the model
(`../model/`), the behavioural suite (`../tests/test_behavior.py`), the
catalogue and its harness (`../seeded_faults.toml`, `../check_catalogue.py`),
and both existing arm prompts, byte for byte. The point of a baseline is that
it is the same subject.

**New here:** one more anchor tree for the same feature, with the durable side
behind a port the domain declares. The behaviour is
`../reference/quota_ledger.py`'s behaviour statement for statement. The claim
that it is the same subject is not a claim — the identical shared suite passes
against all three wirings, and `check_catalogue.py --verify-suite` runs it
against each of them with a green control before any mutant is applied:

```
uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q          # flat reference
QUOTA_LEDGER_DIR=examples/validation/ab/reference_ports QUOTA_LEDGER_IMPL=quota_ledger      ... # real adapter
QUOTA_LEDGER_DIR=examples/validation/ab/reference_ports QUOTA_LEDGER_IMPL=quota_ledger_fake ... # fake adapter
```

## The files

| file | what it is |
|---|---|
| `domain.py` | the rules, and the `LedgerJournal` port. Imports no adapter. |
| `journal_file.py` | the **real** adapter: a file on disk. |
| `journal_memory.py` | the **fake** adapter: the record in memory. |
| `quota_ledger.py` | composition point, real wiring. `QUOTA_LEDGER_IMPL=quota_ledger` |
| `quota_ledger_fake.py` | composition point, fake wiring. `QUOTA_LEDGER_IMPL=quota_ledger_fake` |

## The instrument this tree makes possible, stated plainly

Two composition points over one domain, and one suite that asserts **expected
values** rather than agreement between wirings. Running the identical suite
through both wirings is what gives a fault in either adapter somewhere to be
seen. A test that only compares the two wirings passes when the domain is
wrong, because both wirings are wrong together — which is why the shared suite,
not a parity test, is the instrument.

Nothing here gates, refuses, or reports a verdict. It is a fixture.

## What this tree does NOT settle

* It does not show that an **arm** will produce this shape. It shows what a
  seeded fault does once the shape exists. PA-06 re-anchors onto the arms.
* It is one feature, `n = 1`, and the tree was written by the same author as
  the catalogue that seeds into it. That is the same declared bias the flat
  reference carries and it is not reduced by there being two trees.
* `quota_ledger_fake.py` being four lines is evidence that the blind region was
  cheap to reach, **not** evidence that anybody would have reached it. Nobody
  did, for a whole epic, and that is the measured fact.
