# Coverage Audit Gate

Status: Open

An end-of-epic sub-agent procedure that finds what the model **does not
represent**, and gates promotion on closing the in-scope gaps.

## The hole this fills

The doctrine defines four oracles, and every one of them is bounded to what is
already modeled:

| Oracle | Bounded to |
|---|---|
| Output conformance | cases that exist |
| Projected-state conformance | cases that exist |
| Effect conformance | the corpus — which is generated *from the model* |
| Mutation kill test | faults seeded "one per port and one per invariant" — **modeled boundaries only** |

Unmodeled program surface is never generated into a case, never adapted, never
mutated. **A subsystem with no representation is invisible to all four gates,
and all four report green.** The model can be perfectly faithful about
everything it covers and blind to half the program.

"Coverage" appears in `modular_fuzzing.md` and `architecture_tractability.md`
only as an assertion — "a new unjustified coverage gap", "external coverage is
rejected, not celebrated", "a harness that reaches 2% coverage is rejected".
Nothing measures it.

The four oracles check **fidelity of what is modeled**. This checks
**completeness of what is modeled**. Neither implies the other.

## Deliverable

A checked-in sub-agent prompt and report template — **prompt only, no tooling**
by owner decision. It runs at the end of an epic, after the mechanism tickets
land and **before** final end-to-end integration, as a promotion gate.

Because there is no mechanical inventory backing it, **the prompt itself must
impose the completeness discipline.** A prompt that says "look for uncovered
behavior" finds whatever the agent happens to notice. This one must require
systematic enumeration, in tables, with every row explicitly dispositioned. If
the agent can produce a plausible report without having walked the whole
surface, the prompt has failed.

Required sweeps, each producing a table where **every row carries a verdict**
(represented / unrepresented / partial) with file:line evidence:

1. **Program surface** — every module and package in the declared scope,
   mapped to the spec action(s) representing it, or marked unrepresented.
2. **Effects** — every real side-effect site (filesystem, network, subprocess,
   environment, clock, randomness, persistent store) mapped to a declared port,
   or marked undeclared. Enumerate by category so the sweep is checkable rather
   than impressionistic.
3. **Behaviors** — error paths, retries, timeouts, fallbacks, concurrency and
   interleaving, and config-driven branches. These are the ones a
   happy-path-shaped model reliably misses.
4. **Both views** — Internal (component detail) and External (public input
   surface and the observable projection). A behavior may be covered in one and
   absent from the other; report per view, not once.

The report ends with a verdict and, for each gap, a proposed model update.

## Gate semantics

**In-scope gaps are hard.** An uncovered behavior or effect inside the epic's
declared scope fails promotion. Per the fourth governing rule: model it, or
change the program. There is no third option.

**Out-of-scope surface is inventoried and reported, and does not gate.** An
epic scoped to one subsystem is not blocked by surface elsewhere.

**The scope is declared once, in the plan, and reviewed once** — it is not a
per-finding waiver. That distinction is the whole design. A gate whose findings
can each be closed by a recorded justification is the out-of-contract
suppression mechanism that was purged from MF-013, rebuilt one level up. One
reviewable boundary decision is a boundary; N per-finding justifications are an
escape hatch. See "No Degenerate Escapes" in
`references/architecture_tractability.md`.

**Remediation is advisory; the gap is not.** The agent proposes *how* to close
a gap and the owner approves, adjusts or vetoes the approach — consistent with
"Recommendations, Never Verdicts". The *existence* of an in-scope gap is not
negotiable, and the report must not offer a "accept as-is" disposition for one.

## Acceptance criteria

- A checked-in sub-agent prompt and report template, with the four sweeps
  above, each requiring a complete enumeration table with per-row verdicts and
  file:line evidence.
- The prompt explicitly forbids a "justified / accept as-is" disposition for an
  in-scope gap. The only dispositions are: model it, change the program, or
  (out of scope) inventory it.
- The prompt requires the epic's declared scope to be **read from the plan**,
  not decided by the auditing agent — an agent that chooses its own scope can
  define every gap out of existence.
- Report is emitted as ticket evidence and recorded in the complexity ledger
  MF-019 defines, so an epic that skipped the audit is visible.
- Both views are reported separately; a single merged verdict is not
  acceptable.
- Worked example: run the procedure against this repository and include the
  resulting report as evidence. A prompt nobody has executed is unvalidated.
- Documented in `SKILL.md` and the epic doctrine as a required end-of-epic
  step, with the ordering stated — after mechanisms land, before final
  end-to-end integration.

## Note on the prompt-only choice

The tradeoff was accepted deliberately: no tooling means no completeness
guarantee from the inventory side, so the discipline lives entirely in the
prompt's structure. If the worked example shows the agent skipping surface or
producing impressionistic findings, that is a finding about the prompt, and it
should be reported rather than smoothed over — a follow-up ticket for the
mechanical inventory is the honest outcome in that case.
