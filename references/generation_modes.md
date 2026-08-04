# Generation Modes

Spec Double Compiler has two related generation paths. Keep them distinct.

## Manifest-Driven Spec Doubles

Use `scripts/generate_python.py` when a reviewed `spec_manifest.yaml` defines
the Python API shape:

```bash
python scripts/generate_python.py path/to/spec_manifest.yaml --out path/to/generated
```

This mode generates:

- Python dataclasses for states, commands, results, and events.
- Protocols for ports.
- A deterministic fake/spec double from explicit manifest templates.
- Validators, strategies, traces, contract tests, and generated docs.

This is best when the boundary API is known and the manifest is the reviewed
bridge from TLA+ names to Python names.

## TLC State-Graph Cases

Use `scripts/generate_cases_from_tlc_dump.py` when TLC's reachable state graph
is the case source of truth:

```bash
python scripts/generate_cases_from_tlc_dump.py path/to/Model.tla path/to/MC.cfg --out path/to/generated --package model_cases
```

This mode generates:

- One `StateGraphCase` per action-labeled TLC edge.
- Generic before/input/output/after case descriptors.
- Recovered action `params` on each case input (on by default; MF-029).
  Unrecoverable arguments are the `UNCHECKED` sentinel, provenance is recorded
  in `params:*` labels and `param_recovery_audit.md`, and `--no-infer-params`
  reverts to `params={}`.
- A scripted transition double that accepts exactly the generated case input.
- Validators for structural replay.

`--view internal|external` with `--actions-metadata` generates view-aware
packages (`spec-unit/` and `testgraph/` output subdirectories); optional
`--state-projector`, `--output-projector`, `--dedupe projected`, and
`--labeler` hooks shape the emitted corpus.

## The Negative Corpus: Disabled Edges, Asserted Rejected

A state-graph corpus replays only ENABLED edges, so it contains no rejected
inputs, so **a service that accepts what the model forbids passes every case.**
Guard relaxation measured 0 of 3, then 0 of 3 on both arms, then 0 of 4 on an
independent blind catalogue. Parameter recovery was blamed and fixed — 0 of 5
to 5 of 5 — and not one cell of the mutant matrix moved, because all 330
recovered arguments were arguments the guard ACCEPTS.

```bash
python scripts/generate_cases_from_tlc_dump.py Model.tla MC.cfg --out generated \
    --negative-cases only            # or with-positive
```

At every reachable state, for every action, over every argument tuple its
quantifier domains admit, the action's own body is evaluated against that
state. Where it is definitely FALSE the corpus emits one case: the program must
REJECT this call, and no modeled variable may change. The case's `output` is a
`StateGraphRejection` whose `reason` is **the violated conjunct, verbatim from
the module** — an adapter comparing reasons compares against the specification,
not against this generator.

### Why it cannot produce a false rejection

Evaluation is three-valued. Anything the evaluator does not implement — a
primed variable, `EXCEPT`, `CASE`, `LET`, an unresolvable operator, a domain it
cannot enumerate — is UNKNOWN, never a default. A conjunction is FALSE only
when some conjunct is FALSE, a disjunction only when every disjunct is. So an
unsupported construct costs COMPLETENESS (a refusable input nobody tests) and
can never cost SOUNDNESS. Every action the generator declines is named in the
run output with the reason it was declined.

Two further guards, both reported per run:

- **The disabled set is computed by evaluating the model, never by subtracting
  the dump's edges.** A DOT dump carries one edge per `(source, target, action)`
  and collapses arguments that agree on the successor, so the subtraction would
  report enabled-but-collapsed inputs as refusable. Measured on one 2,649-state
  fixture: 4,028 edges against 7,716 argument tuples that are not disabled.
- **Enabled edges are re-evaluated at their own source state.** A transition TLC
  took must not evaluate FALSE. An action where it does is dropped from the
  negated set rather than trusted.

### What is never negated

An action that WRITES no variable any guard READS. A model may spell its
refusals out as their own actions — and should — but the complement of "this
call is refused" is "this call is accepted", so negating one would assert the
rejection of an input the model enables. Override the selection with
`--negative-action NAME` when the heuristic is wrong for your model; the chosen
and rejected sets are both printed.

The write set of those same refusal actions tells the generator which variables
record an OUTCOME rather than STATE. They arrive on the case as
`StateGraphRejection.outcome_fields`, and an adapter reports them unobservable
(`semantic_output["unobservable"]`) — a real refusal legitimately writes them.
Every other variable is asserted unchanged. A model with no refusal actions gets
an empty tuple and the stronger assertion.

### Keeping it tractable

`--negative-dedupe guard-reads` (the default) keeps one case per
`(action, arguments, violated conjunct, and every state variable that conjunct
reads)`. Cases agreeing on all four are the same test. `--negative-dedupe none`
keeps one per reachable state, which is exact and very large. This is a DEDUPE,
never a trim — no case is dropped to fit a budget, and both counts are printed.

Measured on the same fixture: 39,966 exact against 118 collapsed, and the two
killed **identically** on both a seeded and an independently authored
guard-relaxation catalogue.

### What it does and does not catch

Per class, per instrument, on a 2,649-state fixture and its reference
implementation (`specs/tickets/HP-03/results/`):

| class | whole-view corpus | negative corpus | hand-written suite |
| --- | --- | --- | --- |
| guard relaxation (seeded) | 0 of 3 | **3 of 3** | 3 of 3 |
| guard relaxation (fresh) | 0 of 5 | **5 of 5** | 5 of 5 |
| durable content | 1 of 2 | 0 of 2 | 2 of 2 |
| wrong value | 1 of 2 | 0 of 2 | 2 of 2 |

The negative corpus asserts refusal and inertness and nothing else, so it kills
nothing outside the guard classes and is not a replacement for the positive
corpus. It is the half the positive corpus structurally cannot reach.

It cannot reach a refusal branch the MODEL does not contain: a guard on a
value outside a `CONSTANTS` domain has no reachable state to be refused from.
Nor can it reach a guard on an argument the implementation ALLOCATES rather
than accepts — the model states a caller argument the API has none of. Both
were measured as survivors rather than assumed away.

The run prints the advisory complexity scan before TLC — findings to read,
never a refused build — and, after the complete package is written, checks the
corpus against the manifest case caps (`max_internal_cases_per_component`,
`max_external_cases_per_action`). Over cap it reports the distribution, asks a
redesign question, and exits nonzero without trimming a single case.

Every run states **which state projection and which dedupe mode produced its
counts**, unprompted, in the output and in the package's `docs.md`. A case count
whose projection is unnamed cannot be compared with the next one, and a corpus
that fits its cap only because something was silently dropped is worse than one
that does not fit.

### Write a `tlc_projection.py`

A model with no state projection generates one case per raw TLC edge, and that
is very often a corpus nobody can import. This repository's own model produced
**3,678,217 cases and a 7.4 GB `cases.py`** from the config that exists to make
a corpus tractable — 18,391x its own cap. The projection at
`specs/current/tlc_projection.py` takes the same model to **541 cases and
667 KB**, a 6,800x reduction, by moving two kinds of variable out of the state
and into the OUTPUT, where they are still asserted:

- **pure outputs** every action writes and no guard reads; and
- **recorded verdicts** that form an independent product every action carries
  through unchanged, so the corpus otherwise enumerates each command once per
  combination of verdicts it never reads.

Neither is deleted — a projection that shrinks a count by dropping an oracle has
made the corpus worse and the number better. Say in the module's docstring what
the projection costs; the one in `specs/current/` does.

Repository-local adapters then map real production boundaries to these generic
case descriptors through `case_adapters.toml` and
`scripts/run_generated_case_adapters.py`.

Every TLC run used to produce this state graph has a hard wall-time budget:
`budgets.tlc_seconds` in `spec_manifest.yaml`, default 120 seconds. Wrap the
model-check command in an external timeout of that many seconds and stop it
when the budget expires. A timeout means the diagram is not a viable case-generation
abstraction. First inspect domain cardinalities, variable combinations, action
branching, interleavings, symmetry, and TLC progress output to identify what
multiplies the state count. Distinguish compressible modeling detail from
essential program complexity. Then introduce another diagram/refinement with
smaller bounded domains, less irrelevant state, or separated independent
lifecycles. Do not increase the timeout or wait for the same state space. When
essential complexity remains, give the user concrete options for lowering
program complexity, with the semantic and coverage tradeoff of each option,
before choosing what to omit.

## Relationship To Program Workflow

`program_model`, `current`, and `desired_program_model` are workflow roles, not
generation modes.

- `program_model` is the accepted baseline.
- `current` is the whole-program model implemented right now during active
  ticket work.
- `desired_program_model` is the target model plus ticket plan.

Either generation mode can be used from the appropriate workflow directory, but
for whole-program behavior changes the TLC state-graph case path is usually the
better fit because it keeps cases tied directly to the reachable model.
