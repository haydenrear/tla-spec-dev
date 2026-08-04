# HP-04 — the narrative ledger

The ticket in one line: **the effect oracle now runs, and running it says the
oracle's reach was never what limited detection.**

## What changed, and what it cost

Four defects in the oracle's execution loop, three of them filed by RC-02 and
MF-026 round 4 and one found here.

| | before | after |
|---|---|---|
| loads a scaffolded project's adapters | `ModuleNotFoundError` | yes, with no `PYTHONPATH` |
| an `apply()`-only adapter | `TypeError`, no report at all | `SKIPPED [not-runnable]`, named, run continues |
| an adapter that raises | traceback on case 1 of 148 | collected per case, run FAILS as `adapter_error` |
| the same corpus twice | 20 / 19 / 19 gaps, 9 / 10 / 10 dead ports | 20 / 20 / 20, whole report identical |
| a slice narrower than its view | refused under **every** shipped mapping | executes 50 cases, no third file |
| `path.open("a")` | invisible | observed, same crossing as `open(path, "a")` |

**The complexity delta is `zero` and the model delta is one row.**
`spec_tree_delete` is attached to `RunEffectConformance` because resetting the
per-case work directory is a real `filesystem.delete` under `**/specs/**`, and
this manifest's own rule says an undeclared effect on a modeled action path is a
gap. That rule is the whole point of the ticket, so exempting the ticket from it
would have been the wrong kind of convenient. Cost per `surface_cost_rule`: no
new port (already declared, already exercised by three other actions), no new
action, no new variable, and TLC enumerates 118,573 distinct states before and
after. The refinement search (in the ledger) rejected three alternatives on
measurement; none removed the edit and two bought less.

## The result, which is a zero

`kill-table.txt`, per class per arm, over HP-01's sealed 10-mutant catalogue,
with `Release` bound to an `apply()`-only adapter — the seeded condition M10
targets.

| class | n | oracle-before | oracle-after | corpus |
|---|---|---|---|---|
| cross_aspect | 1 | no-report | 0 of 1 | 1 of 1 |
| durable_content | 2 | no-report | 0 of 2 | 0 of 2 |
| guard_relaxation | 3 | no-report | 0 of 3 | 0 of 3 |
| ordering | 1 | no-report | 0 of 1 | 0 of 1 |
| output_oracle | 1 | no-report | 0 of 1 | 0 of 1 |
| wrong_value | 2 | no-report | 0 of 2 | 1 of 2 |

`no-report` is not zero kills. The pre-HP-04 oracle produced **no report at all**
— on the control and on all ten mutants — so it could not have distinguished
anything from anything. That is worse than a zero and is recorded as its own
outcome rather than folded into one.

`oracle-after` is a genuine zero. **HP-01 sealed a negative prediction that this
ticket would move the mutant matrix by zero cells. It is confirmed.** The RP-02
shape, predicted this time rather than discovered.

M10 SURVIVES on the after arm — prediction N05, "visible without being killable",
confirmed.

## The counterfactual, which is the useful part

A survivor on its own reads as "HP-04 did not help". So the same action was bound
to an adapter whose only difference is that it has a `run(case, work_dir)`,
nothing else changed, and **M10 dies on 8 of 8 cases**.

The remaining distance between the oracle and the fault is one method per
adapter, nine times, in `production_adapters.py` — which this ticket may not
edit. Filed as HP-04-DF-01 with the measurement attached.

## Two corrections to things that were already believed

**Seven of nine "dead ports" were never dead.** RC-02 reported 9 for this model.
Only `cli_download` and `cli_artifact_delete` are proven dead; for the other
seven, every action declaring them was skipped, so the run carries no evidence
either way. A manifest edit made on the strength of that column would have
removed live surface. The report now says `UNEXERCISED PORT (NOT proven dead)`
and names the actions responsible.

**The sandbox never watched `Path.open`.** Found because the oracle "killed" the
ordering NEGATIVE CONTROL: M09 replaces a `path.open("a")` append with a
`Path.write_text`, so the oracle detected a change of *API*, not of behavior — 
and, worse, the more common of the two idioms was the silent one. Patched. M09
now survives, as its own prediction says it should, and observed-effect counts
rose from 67 to 84 because the oracle sees writes it used to miss.

## Measured and unflattering

The first version of this ticket's own kill-table harness reported **10 of 10
KILLED on every class, including the negative control**. It was comparing reports
that carried differently-named temp directories. The flattering number was the
bug, and it is recorded here rather than quietly corrected because a harness that
can produce a 10-of-10 by accident is exactly what a reader of the real table
should know existed.

The second version reported M09 killed for the `Path.open` reason above — also
an artifact, also corrected, also recorded.

## Findings filed, none fixed

- **HP-04-DF-01** — the nine missing `run(case, work_dir)` implementations, with
  the counterfactual attached.
- **HP-04-DF-02** — one boundary, two incompatible `effects:` schemas. HP-01's
  A/B model declares its durable port in the semantic-provider shape, which the
  effect oracle cannot parse, so the M10 instrument needed a manifest of its own.
  This lands on HP-05, which is about to make the semantic shape the default.
- **HP-04-DF-03** — a generated corpus recovers **no arguments at all** for a
  refusal: all seven `Refuse*` actions on HP-01's model carry `{}`. HP-03's
  territory, replicated here on a second model.
- **HP-04-DF-04** — `open ticket` snapshots the oracle's scratch tree into the
  ticket and `close ticket` would promote it into the model. Measured at **706 of
  801 tracked files** on this ticket's own first workspace, which had to be
  deleted and re-opened.

## What this ticket does not claim

It does not claim D1 will move; the matrix says it will not, from this change.
It does not claim an arm scores D3 anchor 4 — only that anchor 4 is now
*runnable*, demonstrated on ex4's `LedgerStorePort` with a real file-backed
adapter and an in-memory fake passing the same six cases. HP-06 decides both.
