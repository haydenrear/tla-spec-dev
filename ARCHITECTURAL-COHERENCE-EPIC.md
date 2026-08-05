# architectural-coherence epic — starter for the ticket agents and the next owner

> **CLOSED, AND ITS SHIPPED SURFACE REMOVED 2026-08-04.** AC-01's architecture
> descriptor, AC-02's reflexion check and AC-04's structure delta are gone by
> owner direction, with the model surface and the ledger member that recorded
> them. This page is the record of what the epic set out to do and what it
> measured. What survives as guidance is `references/architecture_advice.md`.

Read this before touching anything. The canonical schedule is
`specs/desired_program_model/ticket_plan.yaml`; this file is the *why*.

---

## 1. The problem, in the owner's words

AI-generated code is a game of Jenga. Not *wrong* — it passes tests — but
incoherent: every command reaches every module, state has no owner, and the
next change pulls a block out from under three others. The question this epic
takes seriously is why the generator cannot produce reusable modules that
compose, and whether the diagram can be made to force the shape.

## 2. The two levers, and why they are the same lever

This epic ships two things that look unrelated and are not:

- **Case modules (BDD slices).** A module that `EXTENDS` a view, declares no
  state and no actions, and either restricts the next-state relation to one
  aspect's entry points or replaces `Init` with an asserted Given. It cuts the
  program's **behavior surface**, from the user's side, by aspect.
- **Architecture coherence.** A descriptor derived from the model —
  components as variable clusters, the single writer of each variable, the
  crossing actions that are the ports — plus a reflexion check that measures
  the production code against it. It cuts the **implementation**, from the
  inside, by state ownership.

Both are projections of the same object: the variables × actions read/write
matrix that `analyze complexity` already computes. An aspect is a set of
actions; a component is a set of variables; the matrix relates them. That is
the epic's central bet, and it is falsifiable: **if aspects and components line
up, the program decomposes; if every aspect touches every component, the
architecture is the Jenga tower and the matrix already says so.**

The reason this matters for code generation is the third piece:

- **The ask (AC-03).** The descriptor is only advice until it constrains the
  request. An implementation brief that says *this action belongs to component
  C, which owns variables V; it may reach D only through port P; effects live
  at the boundary; one externally visible commitment per action* is a different
  prompt from "implement checkout", and it is derivable — mechanically — from
  a model the project already has.

Enforcement is at generation time. The check is a scanner.

## 3. What is measured already, before any ticket

The case-module half is not a proposal; it was probed against
`examples/distributed_history` and the numbers are in
`examples/case_modules/MEASUREMENTS.md`:

- whole External view: 49,386 distinct states, 732 cases, 1m 23s;
- three aspect modules: 190 cases, 4.3s, **zero** adapter/binding/actions.yml
  changes, channel enforcement passing;
- the slice form reproduces the view's corpus exactly for three of four
  actions; the Given form collapses 504 duplicate-command cases to 12 — which
  is a *claim about the program*, recorded and reviewable, not a filter.

The probe also found **CM-F1**, which is why CM-01 is first: the complexity
ledger locates its model as the alphabetically first `*.tla`, so on every
Core/Internal/External baseline it measures `Core.tla` against `External.cfg`
and reports `bound = None, modularity = 0.0`. The standing-objective ledger has
been measuring a module with no variables and no actions. It survived because
this repository's own baseline is still legacy single-module.

## 4. What this epic ships

| Ticket | Ships |
|---|---|
| CM-01 | Case modules mechanized: declared model discovery (CM-F1 fix), `case_modules:` manifest block, per-module action scope (CM-F2), coverage aggregation report |
| AC-01 | `analyze architecture` — the model-implied structure: components, single-writer ownership and its violations, ports, span-crossing actions |
| AC-02 | The reflexion check — declared code↔component map, extracted dependency graph, convergence / divergence / absence |
| AC-03 | The ask — `prompts/implementation_brief.md` and `prompts/aspect_decomposition.md` |
| AC-04 | Refactor capability — before/after divergence delta, recorded in the complexity ledger, non-gating |
| EV-01 | Eval fixtures, including a deliberately incoherent "Jenga" example with a known answer key, and committed predictions |
| EV-02 | Run the evals as a fact-finding mission; write `NEXT-EPIC.md` |

## 5. Standing constraints (unchanged, non-negotiable)

- **Advisory, not blocking.** No gate. Nothing in this epic may refuse a close,
  a promotion, or a case generation. `references/architecture_tractability.md`,
  "Advisory, Not Blocking", governs; issue #62 is why.
- **No suggested moves.** CD-01 removed the abstract/decompose/refactor chooser
  after validation showed it confidently wrong on standard TLA+. Do not rebuild
  it in a new costume. Descriptors state facts; people (and the prompts in
  AC-03, from measured facts) make the calls.
- **A refusal beats a false clean.** An unmappable target reports `unmappable`,
  never `coherent` — the MF-027 rule, and for the same reason.
- **Never merge to `main`** and never run `skill-manager sync` without explicit
  owner say-so.
- **Never invoke `tla-spec-dev` from PATH** (it execs a stale installed clone).
  Use `python3 scripts/tla_spec_dev.py --spec-root specs …`.
- **Run pytest with `--with pyyaml`**, or the YAML-validity guard skips
  silently.
- **Validate `ticket_plan.yaml` after every edit** with the git-epic-workflow
  validator. It has been broken twice in past epics.
- Evidence integrity is untouched: never drop, filter, sample, or truncate
  cases; never suppress a finding; never doctor a measurement. A metric may not
  block you, and you may not falsify it.

## 6. Known live defect at dispatch (do not fix inside a ticket)

`tests/test_new_ticket_workflow.py::test_skill_requires_two_minute_case_generation_budget`
is RED on `main`: it asserts doc phrases the c72d03a refresh removed. It is
pre-existing and belongs to no ticket in this epic. File it; do not repair it
inside a ticket's scope.

## 7. Epic-owner discipline that paid off twice

Every substantive finding in the last two epics came from an agent measuring,
not from review. So: **tell every agent the brief may be wrong and the issue is
authoritative**, verify claims against the code yourself, and treat the
self-critical result as more valuable than the tidy one. EV-02 exists because
that is how the complexity-descriptor epic was born — a validation agent was
told a low, honest result was a valid outcome, and it found the suggestions
were wrong.
