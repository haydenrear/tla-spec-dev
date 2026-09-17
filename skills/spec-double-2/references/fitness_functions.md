# Fitness Functions Over the Complexity Descriptor

**Status: EXPERIMENTAL (CD-03).** Self-configured, composable, advisory.

A fitness function is a condition a project's agent declares it **wants to
hold** about the project's complexity descriptor — "the bound stays under X",
"no god-state", "the phase variable's domain stays tiny". The agent who knows
the project writes the rules; they persist with the project; and every later
`analyze complexity` run evaluates them and **surfaces any rule that does not
hold (a FIRING) so future agents are notified**.

Three properties are load-bearing:

- **No built-in rules.** The tool ships empty. Nothing fires unless this
  project's agent configured it. With nothing configured, the scanner prints
  no fitness section at all.
- **Advisory.** A firing is a notification, never a block. It does not change
  the scanner's exit code, does not block promotion, and does not refuse case
  generation. Even a broken rules file only produces an advisory
  `CONFIG ERROR` line. (Same stance as the descriptor's threshold warnings —
  `references/architecture_tractability.md`, "Advisory, Not Blocking".)
- **Composable primitives, not a framework.** Leaves are `{fact, op, value}`
  comparisons over the descriptor's published facts; the only combinators are
  `all` / `any` / `not`. That is the whole language.

## Where rules live (per-project persistence)

Three places, all read on every scan, all allowed at once:

1. **`spec_manifest.yaml`** — a `fitness_functions:` block alongside
   `budgets:`, so the rules travel with the manifest.
2. **`fitness_functions.yaml`** — a sibling file next to the `.tla` spec
   (the same directory the default manifest is resolved from), for projects
   that want the rules in their own file.
3. **`fitness_functions.json`** — same shape as the YAML file, parsed with
   the standard library alone. The manifest block is parsed by the
   repository's constrained dependency-invariant parser and works with or
   without PyYAML (flow-style rule leaves like `{fact: bound, op: "<",
   value: 100}` and floats included; no nested inline mappings). Only the
   sibling `.yaml` file needs PyYAML; under a bare `python3` its presence is
   reported as an advisory `CONFIG ERROR` — use the manifest block or `.json`
   there.

All use the same shape:

```yaml
fitness_functions:
  - name: no-god-state-and-modular
    description: keep state decomposed; no variable touched by most actions
    rule:
      all:
        - {fact: god_state_count, op: ==, value: 0}
        - {fact: modularity, op: '>=', value: 0.1}
  - name: state-space-in-check
    description: bound stays small and the phase domain stays tiny
    rule:
      all:
        - {fact: bound, op: '<', value: 100000}
        - {fact: variable_domain, var: phase, op: '<=', value: 6}
```

`name` and `rule` are required; `description` is optional prose echoed when
the rule fires. Quote `'>='`/`'<='`/`'<'`/`'>'` in flow style so YAML does not
eat them.

## The rule tree

A rule node is exactly one of:

- a **leaf**: `{fact: <name>, op: <op>, value: <number|bool>}` — with
  `var: <variable>` when the fact is `variable_domain`;
- `all: [<node>, ...]` — every child must hold (and);
- `any: [<node>, ...]` — at least one child must hold (or);
- `not: <node>` — the child must not hold.

Ops: `<` `<=` `>` `>=` `==` `!=`.

## Facts a leaf can name

All derived from the descriptor's `[MEASURED]` JSON payload — rules read
published facts, nothing private. (`scripts/fitness_functions.py`,
`FACT_DOCS`, is the authoritative list.)

| fact | meaning |
|---|---|
| `bound` | static state-space upper bound (UNKNOWN when no domain resolves) |
| `bound_known` | True when the static bound could be resolved at all |
| `modularity` | graph-modularity Q over the variable interaction graph |
| `component_count` | number of near-decomposable variable clusters |
| `max_component_variables` | size of the largest component, in variables |
| `max_component_actions` | actions touching the most-touched component |
| `action_count` | number of actions (top-level next-state-relation disjuncts; helpers attributed to their callers) |
| `variable_count` | number of declared variables |
| `god_state_count` | dense rows: variables touched by more than half the actions |
| `dense_column_count` | actions touching more than half the variables |
| `port_crossing_action_count` | actions touching more than one component |
| `unread_by_invariant_count` | variables no configured invariant reads |
| `unjustified_count` | variables with no justification linkage (UNKNOWN without a `justification:` table) |
| `variable_domain` | domain cardinality of one variable; needs `var: <name>` |

## Semantics: holds / FIRED / unknown / invalid

- **holds** — the condition is true on this scan.
- **FIRED** — the condition is false. The report line carries the leaf-level
  trace (`god_state_count=1 == 0 is FALSE`) so the reader sees exactly which
  measured facts drove it.
- **unknown** — a compared fact could not be measured (e.g. the bound is
  UNKNOWN, or `unjustified_count` without a `justification:` table).
  Evaluation is three-valued (Kleene): unknown never silently converts to a
  pass or a fail; it is surfaced as its own status.
- **invalid** — the rule itself is malformed (unknown fact, unknown op,
  missing `value`, unknown variable). Surfaced with the cause; never raised.

## What a firing looks like

Text report (the section exists only when rules are configured):

```
[CONFIGURED] Fitness functions (self-configured; advisory -- report, never block)
  sources: /path/to/fitness_functions.yaml
  FIRED: no-god-state-and-modular -- god_state_count=1 == 0 is FALSE; modularity=0.000 >= 0.100 is FALSE
    (keep state decomposed; no variable touched by most actions)
  holds: state-space-in-check

  A FIRED fitness function is a NOTIFICATION to this project's future
  agents: a condition the project's agent declared it wants to hold does
  not hold on this scan. It does NOT block promotion and does NOT change
  the exit code -- read it, judge it, and decide with the owner.
```

JSON: a `fitness` key with `sources`, `config_errors`, `fired` (names), and
per-rule `results` (`name`/`status`/`detail`/`description`);
`blocks_promotion` is always `false`. `fitness` is `null` when nothing is
configured.

## When to add fitness functions

After reading a descriptor (`references/complexity_intuition.md`), encode the
shape you decided this project should keep as one or two composed rules —
**add fitness functions for this complexity descriptor so future agents are
notified** when a later change breaks the shape. Keep them few and honest:
a fitness function is a remembered design decision, not a linter. The worked
example recorded for CD-03 is
`specs/.history/complexity-descriptor-epic/ticket-002-CD-03/results/fitness_worked_example.txt`.
