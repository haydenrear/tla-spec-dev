# PA-02 — the instrument that was missing, and what it says

> **CORRECTED — read `CORRECTION-01.md` in this directory first.** The
> "All modules" table in §1 below was used as this ticket's HEADLINE
> cross-tree comparison, and the four trees do not carry comparable
> denominators: the two anchor trees ship no test modules, the two arms do.
> Like for like on `role=code`, `branch_points` is 10 → 11 (not 37 → 19),
> `max_depth` is 1 → 1 (not 5 → 3) and `public_surface` is 20 → 25 (not
> 52 → 48) — the ported tree is slightly LARGER, not simpler. §2a below was
> already correct and is what the table should have led with. **Nothing here
> is edited**: every figure was measured and reproduces, and the superseded
> presentation stands on the record as it was reported.

`scripts/code_complexity.py`. Figures over produced Python. Recorded, never
scored; nothing in this toolchain reads its output as a condition.

Raw runs: `code_complexity_runs.txt` (four trees, human table, exit code after
each) and `code_complexity.json` (the machine record, four reports in one
payload — which is what belongs in a scorecard's `mechanical.json`).

---

## 1. The figures

Four trees. Two of them — `examples/validation/ab/reference/` and
`.../reference_ports/` — are the **same feature**, passing the **same
behavioural suite**, deliberately different in structure (PA-01). Two of them
are the previous epic's **sealed arms**, which are what the ticket declares as
its local signal.

### All modules (implementation + the tree's own tests)

| figure | `reference` | `reference_ports` | sealed `arm_a` | sealed `arm_b` |
|---|---|---|---|---|
| `modules` | 1 | **5** | 2 | **5** |
| `code_lines` | 122 | 255 | 422 | 407 |
| `callables` | 13 | 22 | 50 | 45 |
| `classes` | 3 | 8 | 4 | 6 |
| `public_surface` | 15 | 26 | 52 | 48 |
| `instance_state` | 7 | 9 | 8 | 8 |
| `module_state` | 0 | 0 | 0 | 0 |
| `branch_points` | 10 | 11 | 37 | 19 |
| `max_branch_points_in_callable` | 4 | 4 | 10 | 4 |
| `max_depth` | 1 | 1 | 5 | 3 |
| `declared_interfaces` | 0 | **1** | 0 | **1** |
| `declared_interface_methods` | 0 | 2 | 0 | 2 |
| `internal_import_edges` | 0 | **4** | 1 | **4** |
| `effectful_calls` | 3 | 3 | 20 | 6 |
| `modules_with_effectful_calls` | 1 | 1 | 2 | 2 |
| `branch_points_in_effectful_modules` | **10** | **1** | **37** | **9** |
| `instance_state_in_effectful_modules` | **7** | **1** | **8** | **1** |

### Implementation only (`role=code`, the filter printed with every report)

| figure | `reference` | `reference_ports` | sealed `arm_a` | sealed `arm_b` |
|---|---|---|---|---|
| `modules` | 1 | 5 | 1 | 4 |
| `code_lines` | 122 | 255 | 151 | 202 |
| `callables` | 13 | 22 | 17 | 23 |
| `public_surface` | 15 | 26 | 20 | 25 |
| `instance_state` | 7 | 9 | 8 | 8 |
| `branch_points` | 10 | 11 | 10 | 11 |
| `max_branch_points_in_callable` | 4 | 4 | 4 | 4 |
| `max_depth` | 1 | 1 | 1 | 1 |
| `declared_interfaces` | 0 | 1 | 0 | 1 |
| `internal_import_edges` | 0 | 4 | 0 | 3 |
| `effectful_calls` | 3 | 3 | 5 | 3 |
| `branch_points_in_effectful_modules` | 10 | 1 | 10 | 1 |
| `instance_state_in_effectful_modules` | 7 | 1 | 8 | 1 |

**It can tell them apart.** Both pairs, on both blocks, on many figures at
once. `test_distinguishes_the_two_anchor_trees` and
`test_distinguishes_the_sealed_arms` assert exactly that, so the claim is
executable and not a sentence in a report.

---

## 2. The unflattering half, which is the part worth reading

### 2a. The figures the ticket names could barely tell them apart

The ticket asks for "modules, public surface, pieces of mutable state, branch
count, depth". Take only those, implementation-only, and this is what a judge
would get:

| | `reference` | `reference_ports` | `arm_a` | `arm_b` |
|---|---|---|---|---|
| branch count | 10 | 11 | 10 | 11 |
| depth | 1 | 1 | 1 | 1 |
| worst callable | 4 | 4 | 4 | 4 |
| mutable state | 7 | 9 | 8 | 8 |
| public surface | 15 | 26 | 20 | 25 |
| modules | 1 | 5 | 1 | 4 |

Branching, depth and the worst single callable are **the same**. Mutable state
moves by ±1. The only classical figures that separate the pairs are the two
that measure *how the code is cut up*, and on those the ported tree is
**bigger** — more modules, more public surface, more code lines, more classes.

**So a produced-code complexity instrument built only from the named figures
would report that the hexagonal arm is larger and otherwise identical.** That
is a real result about the arms and it is the one the epic says it prefers to a
flattering one. It does not say the port was not worth it; it says the classical
figures do not contain the answer, and the D2 rubric's question — "as simple as
its behavior requires, and no simpler" — is not settled by them.

### 2b. Total effects are identical; only their *location* moves

Both anchor trees make **exactly 3** outside-world calls. The total says
nothing. What differs is which module they sit in:

* `reference/`: the module holding **all 10** branch points and **all 7** pieces
  of instance state also holds **all 3** filesystem calls.
* `reference_ports/`: the domain holds **9** branch points and **0** effectful
  calls; the 3 calls live in a 28-line adapter with 1 branch point.

`branch_points_in_effectful_modules` goes 10 → 1 and
`instance_state_in_effectful_modules` goes 7 → 1, with the same pattern on the
sealed arms (10 → 1, 8 → 1). That partition is the one figure in the report
that measures the port rather than the size, and it is the code analogue of the
model descriptor's dense rows. Without it the instrument is a size-counter.

`test_location_of_effects_is_reported_not_only_the_total` pins this: it asserts
`effectful_calls` is *equal* across the two anchor trees and that the location
partition is *not*, so if a future edit collapses the partition back into the
total, the test names it.

### 2c. The instrument confirms the arms, it does not explain them

Implementation-only, `arm_a` ≈ `reference` and `arm_b` ≈ `reference_ports` on
nearly every figure. That is consistent, and it is also a warning: `arm_b`'s
figures separate from `arm_a`'s along exactly the axis its prompt named. It
does not distinguish "hexagonal helped" from "a 6.6×-longer prompt helped" —
the caveat already standing against the D3 = 4 result. This instrument adds no
evidence on that question. `arm_c` exists to settle it and has not been run.

---

## 3. How it is kept from becoming a thermostat

Not by prose. By four tests over the shipped artifact.

1. **It exits 0 on every input** — a missing tree, an empty tree, a tree with no
   Python, an unparseable file, a non-UTF-8 file, and a synthetic 40-module tree
   with ~100 branch points and depth 12 per module. That last one is in the
   fixture list precisely so a threshold added later fails *behaviourally*, not
   only as a banned identifier. Verified: adding `if branch_points > CAP:
   return 1` with an innocuously named constant fails
   `test_exits_zero_on_every_input` and its subprocess twin.
2. **No threshold exists in the source** — the AST is scanned for any identifier
   containing threshold/budget/limit/max_allowed/warn/gate/verdict/violation/
   tolerance, and for any `EXIT_*` constant other than the single `EXIT_OK = 0`,
   and for any nonzero `sys.exit`/`SystemExit`. Scanned from the AST, so the
   docstring may discuss thresholds without the test passing vacuously on prose.
3. **Nothing in the toolchain reads it** — every file under `scripts/`,
   `skill-scripts/`, `spec_double_compiler/`, `templates/`, `test_graph/` and
   every non-history `specs/**/*.py` is scanned for a reference to it. Verified:
   adding one import in `scripts/close_ticket.py` fails the test and names the
   file.
4. **The output carries no verdict vocabulary** — 25 banned words checked against
   both the text and the JSON of all four subject trees.

And structurally: **there is no comparison mode.** No `--compare`, no
`--baseline`, no `--diff`. Two targets in one invocation produce two records
byte-identical to the records those targets produce alone, asserted by test.
MF-020 is the reason: a printed signed number is read as a direction, and a
figure can fall because an edge was deleted.

---

## 4. What was rejected

The question the epic says produces its best material. Answered about design
choices, not about the run.

**Rejected: a `--compare` / delta mode.** The single most useful thing I could
have shipped for PA-06, and the single most dangerous. A table of `-12`/`+4`
converts a set of figures into a direction, and a direction is a verdict with
the word removed. MF-020 says the best complexity result in this project's
record was withheld from a top score by both blind judges for exactly that
reading. Rejected, and a test holds the rejection in place.

**Rejected: cyclomatic complexity as a headline number.** One number per
callable, summed. It is the standard, and it is what a threshold attaches to
five minutes after it ships — every complexity gate ever built is a comparison
against a cyclomatic number. The underlying decision points are reported
instead, unsummed and unranked, which carries the same information and does not
present a scalar begging for a limit.

**Rejected: a maintainability index / composite score.** Any weighted
combination of the figures. A composite is a *judgement expressed as
arithmetic*: the weights are the opinion. The scorecard's whole architecture is
that measurement sits beside judgement and disagreement is a finding — a
composite resolves that disagreement inside the instrument, which is the one
thing the mechanical block exists to prevent.

**Rejected: a coupling/cohesion metric (LCOM, instability, modularity Q).**
Tempting because the model descriptor computes graph modularity and it would
have looked symmetrical. Rejected for a measured reason: the architectural-
coherence epic's static checker *flipped its verdict on this repository because
one variable was added, with nothing tuned*, clearing `modularity_q > 0` — a
criterion that cannot fail. A number that unstable, over a 5-module tree, would
be noise wearing a number's clothes. The import edges are listed instead, so a
reader can see the actual graph and compute nothing.

**Rejected: "the domain imports no I/O" as a boolean.** This is the property
`reference_ports/` was built to have, it is exactly what D3 ≥ 3 asks for, and it
would have been one line. Rejected under CD-01: deciding which module *is* the
domain is picking the boundary, and a tool that picks the boundary makes every
edge legal by construction. Whichever module the tool named as the domain would
pass, always. The partition in §2b reports the same underlying fact — where the
effects sit relative to the decisions — without nominating anybody.

**Rejected: import-graph reachability as an "architecture" figure.** Round 2 of
the predecessor already proved a codebase can pass every import check with its
coupling entirely intact. Import edges are reported as a *list*, labelled as
imports and nothing more, and the report does not call them modularity.

**Rejected: excluding test modules.** The obvious move — test code inflates
every count (arm_a: 37 branch points all-in, 10 implementation-only) — and it is
how an audit becomes clean because of its own filter, which cost this project a
round. Everything is measured, `role` is assigned by *name alone* and printed
with the report, and totals are given twice. The filter is output, not policy.

**Rejected: an ambitious effect-sink vocabulary.** The first draft counted
`get`, `run`, `send`, `copy`, `replace`, `remove`, `walk` and eleven others, and
scored `self._outstanding.get(...)` in the flat reference as a *network call*.
A `dict.get` reported as network is a figure that says something false. All 18
ambiguous names are excluded, listed in the source, and **printed with every
report** as a declared undercount — one-sided the same way the negative corpus
is one-sided, and for the same reason.

**Rejected: parsing with anything but `ast`.** No import resolution against the
environment, no type inference, no execution. Anything that runs the tree under
measurement can fail on a tree it is supposed to measure, and this instrument's
first obligation is that it never refuses.

---

## 5. What this instrument cannot do

Named because a score of 4 requires naming what the artifact refuses to claim,
and because the limits are load-bearing for whoever reads its output next.

* **It does not say which tree is simpler.** It has no opinion and no ordering.
* **`effectful_calls` undercounts, by construction.** Syntactic matching only:
  an aliased sink, a sink through a local variable or `getattr`, and 18
  deliberately excluded names are all invisible. The exclusions are printed;
  the aliasing limit is in the completeness block.
* **It cannot see runtime coupling.** Only what the source says syntactically.
  What *calls* what at runtime — which D3 ≥ 3 explicitly demands — is out of its
  reach.
* **It cannot tell a boundary that pays from a boundary that does not.**
  `reference_ports/` is larger on every size figure. Whether the port was worth
  its cost is a judgement, and the instrument makes none.
* **It has no memory.** No baseline, no history, no trend. Each run is one
  target at one moment; the sealed record is what carries time.
* **n = 1 on the anchor pair.** One feature, and both anchor trees have the same
  author. The instrument distinguishing them is not evidence it distinguishes
  arbitrary designs.
