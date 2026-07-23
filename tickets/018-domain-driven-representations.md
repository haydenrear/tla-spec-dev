# Domain-Driven Representations

Status: Deferred (research)

Not scheduled in the modular-fuzzing epic. Keep it in mind while working the
epic tickets: choices made in MF-011 (diagnostics), MF-013 (effect
declarations), and MF-016 (kill tests) should avoid foreclosing this
direction, and observations that support or complicate it belong in the
skill feedback loop (MF-017).

## Idea

The abstractions we implement encode the allowable cases. Instead of "any
value," introduce a domain abstraction that exists **in the code as well as
the spec**, and that interacts with other abstractions in a discrete number
of ways. Both are domain-driven model artifacts. The TLA+ spec represents
the allowable states of the abstraction and the cases the program logic
handles; the code's types make the disallowed states unrepresentable.

## Why this lowers complexity

The state-space bound is the product of variable domain cardinalities.
Today the model shrinks domains by optimistic abstraction — the spec
pretends only a few values matter, and the refinement mapping carries the
burden of that pretense. Moving the quotient into the code (value objects,
enums, smart constructors — "make illegal states unrepresentable" / "parse,
don't validate") makes the spec's small domain the actual domain:

- the complexity gate is passed honestly, at the source;
- spurious states become structurally impossible — spec and code share one
  state lattice, killing the over-generalization failure mode;
- kill tests sharpen: illegal-value mutants cannot construct, so surviving
  mutants concentrate on genuine logic errors;
- aggregate boundaries with fixed command/event protocols make interaction
  cardinality the number of message types, not the product of internal
  states — narrow R/W-matrix cuts designed forward from the domain instead
  of discovered backward from diagnostics.

## DDD mapping to existing concepts

- bounded context -> component (modular_fuzzing.md)
- aggregate -> single-writer state cluster with an invariant boundary
- domain event -> declared effect / commit point (atomicity fidelity)
- value object -> bounded domain in TLA+ constants, enforced in code
- ubiquitous language -> the facts-not-mechanisms naming rule
- saga / process manager -> interface model between components

## Research questions

- Shared-artifact ownership: spec and code must agree on the abstraction's
  cases. Is a generated, types-only "domain kernel" package a legitimate
  production dependency (currently forbidden for generated spec artifacts),
  or should the kernel be hand-written and conformance-checked against the
  spec's constants? What detects drift?
- Ossification: type-encoded cases make new cases breaking changes. When is
  forced exhaustiveness worth it, and when do open-ended values (money,
  timestamps, text) need equivalence classes with smart constructors — and
  how do class boundaries stay synced between code and spec?
- Migration order: design bounded contexts domain-first and reconcile with
  the R/W matrix, or discover cuts from diagnostics and name them
  domain-ward? Likely both; define the reconciliation step.
- Codegen scope: should manifest-driven generation emit domain value types,
  and how does that interact with the adapter rule and the anti-pattern
  list?

## Acceptance criteria (for the eventual research ticket)

- A reference document defining the domain-kernel pattern, its ownership
  and drift-detection rules, and its interaction with the anti-patterns.
- A worked example: one bounded context in distributed_history remodeled
  with code-level domain abstractions, with before/after complexity-gate
  and kill-rate measurements demonstrating (or refuting) the claimed gains.
- Amendments to references/architecture_tractability.md and
  references/modular_fuzzing.md if the pattern holds.
