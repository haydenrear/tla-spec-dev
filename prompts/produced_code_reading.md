# Reading the produced-code descriptor — sub-agent prompt (FI-05)

**Dispatch the "The ask" block below verbatim**, with the report from
`scripts/code_complexity.py` pasted underneath it, to the agent that wrote the
tree. Everything outside that block is for the caller.

## Why this prompt exists

The stated intent for this project's complexity work was **general statistics
that block nothing, and that prompt the model about what the statistics mean.**
The predecessor epic shipped the statistics (`scripts/code_complexity.py`) and
the human-readable intuition (`references/complexity_intuition.md` §"The Other
Descriptor"), and did not ship the prompting. Until this file existed,
`grep -rn code_complexity prompts/` was **empty**: the figures reached a human
reading a reference page and a scorecard's mechanical block, and **no agent was
ever handed them and asked what they meant about its own design.**

The figures are worth asking about. One partition in particular measures the
*port* rather than the *bulk*:

| `totals_code_only` | reference (flat) | reference_ports | arm A | arm B |
|---|---|---|---|---|
| `branch_points_in_effectful_modules` | **10** | **1** | **10** | **1** |
| `instance_state_in_effectful_modules` | **7** | **1** | **8** | **1** |
| `effectful_calls` | 3 | 3 | 5 | 3 |

Both anchor trees implement one feature and make **the same three calls to the
outside world.** Only their location differs. A total cannot see that; the
partition can. (Those cells are asserted against a live run by
`tests/test_code_complexity.py::test_recorded_figures_match_a_live_run` — this
table is a copy of the record, not a second measurement of it.)

## How to produce the report the ask reads

```bash
python3 scripts/code_complexity.py <tree>            # the table
python3 scripts/code_complexity.py <tree> --json     # goes in mechanical.json
```

**Run it yourself and paste the output.** There is deliberately no script in
this repository that runs the instrument and renders this prompt, and that is
not an oversight: `tests/test_code_complexity.py::test_nothing_executable_reads_this_instrument`
asserts that **nothing in the toolchain reads this instrument's output**, and a
renderer would be the first consumer. The instrument stays a thermometer that
nothing is wired to.

The instrument exits 0 on every input, including a tree that does not exist and
a file it cannot parse. If it could not measure something it says so in the
completeness block, with the path and the reason, and that block is part of what
the ask below is asked to read.

## When to dispatch it, and when not to

- **After the tree exists.** These are figures about produced code; there is
  nothing to read before there is code.
- **Never as part of the implementation ask.** It is a separate dispatch on
  purpose. `prompts/hexagonal_implementation.md` states that not one number
  appears in its ask, and folding figures into it would make that false — and
  would put numbers in front of an author who could then build toward them.
- **Never with a second tree's figures beside the first**, unless the reading
  is explicitly about two different programs. See "Two tables" in the ask.

---

## The ask

<!-- PRODUCED-CODE-READING:BEGIN -->

Below is a report from an instrument that counted things in the code you wrote.
You are being asked to **read it** — to say what these figures say about the
program you built, in your own words.

You are not being asked for a score, a grade, a verdict, or a number to move.
Nothing you write here is compared against a threshold, because the instrument
has none and neither does this ask.

### What the instrument counted, in one paragraph

Per module and as a tree total: physical size (`code_lines`), units
(`callables`, `classes`), the names other code can reach (`public_surface`),
mutable object state (`instance_state`), decision points (`branch_points`, plus
the worst single callable and the deepest nesting), declared abstractions
(`declared_interfaces`), who imports whom (`internal_import_edges`), and where
the program touches the outside world (`effectful_calls`, `effect_sinks`,
`modules_with_effectful_calls`). Two figures are **partitions** rather than
counts: `branch_points_in_effectful_modules` and
`instance_state_in_effectful_modules` say how much of the branching and how much
of the mutable state sit in a module that *also* touches the outside world.

### Four questions. Answer them in prose

1. **Where is the outside world in what you wrote?** Name the modules with a
   nonzero `effectful_calls` and say which sinks they reach. Then say whether
   that is where you meant it to be. If it is somewhere you did not intend,
   that is the most useful sentence you can write today.

2. **What sits beside it?** Compare `branch_points_in_effectful_modules` against
   `branch_points`, and `instance_state_in_effectful_modules` against
   `instance_state`. Those two ratios say how much of your program's
   decision-making and mutable state lives next to its I/O. Say what they say
   about *your* tree, naming the modules — not whether the numbers are good.

3. **What did the instrument fail to notice?** `effectful_calls` undercounts by
   construction: it matches names syntactically, so a sink reached through an
   alias, a local variable or `getattr` is invisible, and eighteen names that
   collide with ordinary in-memory operations are left out of its vocabulary
   entirely (they are printed with every report). Point at a place in your tree
   where it undercounts, or say you looked and found none. Do the same for the
   completeness block: anything it could not parse is a hole in every figure
   above it.

4. **Which figure is not what you expected, and what does the surprise mean?**
   A figure you did not predict is one of two things: a fact about your design
   you had not noticed, or a fact about what this instrument counts (its
   `branch_points` rule and its `role`-by-name rule are both printed with the
   report, and both are narrower than they sound). Say which one it is, and say
   how you can tell the difference.

### Three things that will mislead you if nobody says them

- **Totals hide location, and location is usually the question.** The two
  anchor trees in this repository implement one feature and report the
  *identical* `effectful_calls`. In the flat one, the module holding all its
  branch points also holds all of its I/O; in the ported one the module holding
  the branching holds none of it. The totals are the same. Read the per-module
  table and the two `*_in_effectful_modules` partitions.

- **A tree with a boundary in it measures LARGER on most totals, and that is
  not a defect.** An interface, an implementation and a composition point are
  three things where there was one. In this repository's own pair, the ported
  tree reports 5 modules, 26 public surface and 255 code lines against the flat
  tree's 1, 15 and 122 — for the same feature and the same behavior. Whether
  that purchase was worth it is a judgement. It is *your* judgement; the
  instrument does not make it and this ask does not make it for you.

- **One table, one denominator.** The report prints two totals blocks: `totals`
  counts every module including tests, `totals_code_only` excludes them. A table
  that takes one figure from one block and the next from the other manufactures
  a direction out of nothing. This is not hypothetical — it happened in this
  repository, and three figures reversed or flattened when the denominator was
  made uniform, because one subject shipped a bigger test file. Say which block
  every number you quote came from.

### Two tables

If you have been given figures for more than one tree, they are two readings,
not a comparison. **Do not subtract them, do not compute a delta, and do not
report a direction.** The instrument has no `--compare` mode for exactly this
reason. Two trees are comparable only when they implement the same behavior and
were measured from the same block, and even then the difference is a thing to
*explain*, never a thing to score.

### What this ask is NOT

- **Not a score.** No figure here has a good value. There is no threshold in
  the instrument, none in this ask, and nothing in the toolchain reads your
  answer or the figures as a condition on anything.

- **Not a request for a smaller number.** Every count falls when something is
  deleted, and no count can tell you whether what you deleted was carrying
  behavior. **A metric falling is not evidence a design improved.** If reading
  this makes you want to change the tree, the thing to produce first is the
  sentence explaining what you would change and why the *behavior* justifies
  it — and if you do make the change, say plainly that you made it after
  reading a figure, so a later reader can tell a design decision from a number
  chased.

- **Not a before-and-after.** You are not asked whether anything went up or
  down. If you are holding two reports, see "Two tables".

- **Not a question about where your boundary should be.** These figures
  describe where your boundary *is*. They cannot tell you where to put one, and
  an instrument that picked the cut would make every boundary correct by
  construction — including a bad one. Where the seam goes is yours to argue
  for.

- **Not a test of agreement.** "The figures show my design is right" is not an
  answer this ask wants and not one it can check. If you think the figures are
  measuring the wrong thing about this program, **say that** — with which figure
  and what it misses. That is a better reading than a flattering one.

<!-- PRODUCED-CODE-READING:END -->

---

## What this prompt deliberately does not say

Recorded so a later reader can tell an omission from an oversight.

- **No threshold, budget, target or acceptable range.** Not one figure in the
  ask carries a value it should be near. The four numbers that do appear
  (`5/26/255` and `1/15/122`) are there to establish that a boundary makes
  totals go **up**, which is the opposite of a target.
- **No verdict vocabulary, and no direction.** No "improve", "reduce", "keep
  under", "simplify". The ask never requests a delta and explicitly refuses one.
- **No proposed cut, move or refactor** (`CD-01`). The ask says where the
  boundary *is* and states that the instrument cannot tell you where to put one.
- **No consumer.** Nothing runs the instrument on the agent's behalf, nothing
  parses the answer, and nothing gates on either. Asserted by
  `tests/test_code_complexity.py::test_nothing_executable_reads_this_instrument`
  and `tests/test_produced_code_prompt.py`.
- **No claim that asking works.** Whether handing an agent these figures
  produces a better reading — or any change at all — is unmeasured. This prompt
  is a hypothesis with a stated design.

## Validation status of this prompt — read before trusting it

**Unmeasured, n = 0.** No agent has been dispatched this ask, no reading has
been scored, and no A/B separates a tree whose author read its figures from one
whose author did not. What *is* asserted executably today is the narrower
claim that it is not a thermostat: every figure name it uses is emitted by the
shipped instrument, the ask contains no threshold and no verdict vocabulary,
and nothing in the toolchain consumes the figures
(`tests/test_produced_code_prompt.py`). Replace this section with a result when
one exists.
