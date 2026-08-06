# AC-04 — the refactor loop, demonstrated

Three runs, all against this repository or its own fixtures, all exit 0. The
first is the loop on a real change. The second is the gaming move, attempted and
refused. The third is where the drop/deletion/unmapping cases live, because this
repository does not contain a divergence to remove.

Commands are reproducible from the repository root. The baseline in run 1 was
produced by scanning the pre-change tree (`git archive HEAD` of `e610b98`
extracted to a temp directory) **with the post-change tool** — which is exactly
what a user does: install the new build, then scan the old checkout.

---

## Run 1 — the loop on a real change (`code_only`)

**Scan.** The tree at `e610b98` (the epic tip, before this ticket):

```
$ python3 scripts/architecture_reflexion.py specs/program_model/TlaSpecDevCli.tla \
    specs/program_model/MC.cfg \
    --components specs/program_model/architecture_components.yaml \
    --code scripts --map specs/program_model/architecture_map.yaml --format json
```

→ `results/architecture-baseline.json`: 34 modules, 258 edges, 140 internal,
**118 convergence sites (93 distinct dependencies), 0 divergences, 0 absences**,
verdict `unmappable` for the same five extraction blind spots AC-02 recorded.

**Change.** This ticket, landed: the delta in
`scripts/architecture_reflexion.py`, the `--baseline` flag on
`analyze architecture`, the `architecture_delta` member in
`scripts/complexity_ledger.py`, and the `input_dir` wiring in
`scripts/spec_evolution.py`.

**Rescan + record.**

```
$ python3 scripts/tla_spec_dev.py --spec-root specs analyze architecture \
    specs/program_model/TlaSpecDevCli.tla specs/program_model/MC.cfg \
    --components specs/program_model/architecture_components.yaml \
    --code scripts --map specs/program_model/architecture_map.yaml \
    --baseline specs/tickets/AC-04/results/architecture-baseline.json \
    --format json --out specs/tickets/AC-04/results/architecture-delta.json
```

Recorded result (`results/architecture-delta.txt`):

```
  map digest:  sha256:a9523e7d…  ->  sha256:a9523e7d…   (IDENTICAL)
  model digest sha256:a550b702…  ->  sha256:a550b702…   (UNCHANGED)
  attribution: code_only

  DIVERGENCES: 0 -> 0 (+0 distinct dependencies; 0 -> 0 sites)
    no dependency appeared or disappeared.

  CONVERGENCES: 93 -> 95 (+2 distinct dependencies; 118 -> 120 sites)
    GAINED (2):
      + complexity_ledger.py -call-> spec_paths.py
          [spec_paths.resolve_existing_spec_input]  at scripts/complexity_ledger.py:709
      + complexity_ledger.py -import-> spec_paths.py
          [spec_paths]  at scripts/complexity_ledger.py:100
    LOST (0)

  ABSENCES: 0 -> 0 (+0)
  direction = unchanged
```

**Read it honestly.** The two gained dependencies are real and are exactly what
the change did: the ledger now resolves the delta report path through
`scripts/spec_paths.py`, which the map places in `surface` while
`complexity_ledger.py` is in `corpus`. That pair has a port (`surface <-> corpus`,
crossed by `AnalyzeComplexity`, `AnalyzeCorpus`, `RunEffectConformance`,
`RunSpecUnitTests`), so both are convergences: **the change added coupling, and
the coupling it added is coupling the model already declares.**

The divergence half did not move, and it could not have: this repository has no
divergences under the declared four-component partition (AC-02's measured
result), so there was none to remove. A demonstration that produced a divergence
drop here would have had to manufacture the divergence first. That limit is the
finding, not a gap in the evidence — see "What this run does not show" below.

The map digest is byte-for-byte identical across the two scans even though the
two map *files* sat at different paths (a temp checkout and the worktree). The
digest is over the declared placements, not over the file, on purpose: otherwise
a comment edit would read as a boundary change and the refusal below would fire
so often it would be turned off.

---

## Run 2 — the gaming move, on the real repository, refused

AC-02's own warning: *any divergence disappears if the map moves the offending
module into the component it reaches — no code change, verdict flips.* This run
does it, on this repository, and checks what the delta says.

The probe map (`results/probe-map-budgets-in-kill.yaml`) is the repository's real
map with **one edit**: `scripts/budgets.py` moves from `surface` to `kill`.
Nothing else changes and no source file is touched. Scanned with it
(`results/probe-baseline-scan.json`) the repository has **8 divergence sites / 6
distinct divergent dependencies** — `analyze_complexity.py`,
`corpus_diagnostics.py` and `new_ticket_workflow.py` all reach `budgets.py`, and
`corpus <-> kill` and `kill <-> tickets` have no port.

Now "fix" it by putting the map back:

```
$ python3 scripts/tla_spec_dev.py --spec-root specs analyze architecture \
    … --map specs/program_model/architecture_map.yaml \
    --baseline specs/tickets/AC-04/results/probe-baseline-scan.json \
    --out specs/tickets/AC-04/results/gaming-probe.txt
```

The count improves 6 → 0. The verdict (`results/gaming-probe.txt`):

```
  attribution:   unattributable
    - 1 module(s) present in both scans were RE-PLACED by the map:
      budgets.py (kill -> surface). Re-placing a module moves the boundary, not
      the code -- it is the one edit that makes any divergence disappear for free.

  DIVERGENCES: 6 -> 0 (-6 distinct dependencies; 8 -> 0 sites)
    LOST (6): … each classified
      endpoint_reassigned: `budgets.py` was re-placed by the map (kill -> surface).
      The edge did not go away; the boundary it crossed did.
    stable-basis only (modules in both scans, same component): 0 -> 0 (+0)

  direction = unattributable
```

**This is the load-bearing property of the ticket.** A six-edge improvement, on
the real repository, with zero lines of code changed, and the tool prints
`unattributable` with the re-placement named rather than a number anyone could
put in a report. The same refusal fires from the model end: adding a port to the
spec turns a divergence into a convergence, so the component/port structure is
digested too (test:
`TestTheMapCannotBeMovedBetweenTheScans::test_a_changed_model_side_is_unattributable`).

The probe map is kept as evidence and is **not** the repository's map. It is
labelled at the top of the file.

---

## Run 3 — the drop, the deletion, and the unmapping (fixtures)

`tests/test_architecture_reflexion.py`, classes `TestARealRefactorIsMeasured`,
`TestADropTheEdgesDoNotExplain`, `TestABaselineThatCannotBeOne`,
`TestTheDeltaAdvisesAndNothingElse`. The fixture is AC-02's three-component
Pipeline model, where `ingest <-> deliver` has no port, so a divergence exists to
remove:

| scenario | measured | direction |
|---|---|---|
| the divergent edge is genuinely removed | 2 → 0, both dependencies enumerated with their sites, classified `dependency_removed` | `improved` |
| the divergent edge is added | 0 → 2, both enumerated | `worsened`, exit 0 |
| the module is deleted from the tree | 2 → 0, classified `endpoint_left_tree` | `improved` **+ RED FLAG** — the coupling is gone because the file is gone |
| the module is dropped from the map, code untouched | 2 → 0, classified `endpoint_unmapped` | `unverified` |
| the module is re-placed in the map, code untouched | 2 → 0, classified `endpoint_reassigned` | `unattributable` |
| a port is added to the model, code and map untouched | 2 → 0 | `unattributable` |
| every line in a file shifts | no dependency gained or lost | `unchanged` |

The last row is why the edge identity is `(from, to, kind, symbol)` and excludes
the line number: an identity keyed by line would report the whole graph as lost
and regained on any reformatting, burying the one edge that moved.

---

## What this run does not show, stated plainly

1. **No real divergence was removed on a real tree.** This repository has none
   under the declared partition, so the `improved` path is exercised only on
   fixtures. The delta's behaviour on a genuinely divergent production tree is
   therefore untested at scale.
2. **The divergence number on this repository is 0 and stays 0.** Under the
   declared four-component partition, only `corpus <-> kill` and
   `kill <-> tickets` can diverge at all, and only two scripts sit in `kill`.
   Most changes to this repository cannot move the headline number in either
   direction. The delta's useful output here is the convergence enumeration, not
   the divergence count.
3. **The verdict stays `unmappable` throughout**, for AC-02's five extraction
   blind spots. The delta is computed and reported under an unmappable verdict on
   purpose — "I could not see all of it" and "nothing changed" are different
   facts — but it inherits every one of those blind spots.

## Behavior preservation: which oracle is load-bearing

For the claim that run 1's change preserved behavior:

- **Load-bearing.** TLC green on the model before and after
  (`results/tlc-current.txt`, 32,122,220 generated / 1,292,951 distinct / depth
  26 / 59s, identical to AC-01's and AC-03's runs), the repository behavior tests
  (`results/pytest-full.txt`, 864 passed and the one pre-existing failure already
  deferred as CM-01-DF-01 / AC-DF-01), and the spec-unit adapter conformance run
  (`results/spec-unit-tests.txt`, 2 targets). Where a generated case corpus is
  replayed against effect providers with **content** assertions, that is the
  oracle validated for this bug class — the effect-provider work measured 45
  mutation points killed on exactly the class MF-038 missed, with a deterministic
  replay command per failure (the `ex1-run4` property).
- **NOT load-bearing.** The mutation kill rate. MF-038 measured 0 of 9 content
  bugs caught at kill rate 0.31 against a floor of 0.8. It is recorded as
  `not_run` in this ticket's ledger entry and it certifies nothing.
- **NOT load-bearing either.** The architecture delta itself. It is a fact about
  dependency structure. It says nothing about whether the program still behaves
  the same, and it belongs beside the behavior evidence, never in place of it.
