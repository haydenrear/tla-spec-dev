# Complexity Minimization Objective

Status: Open

The whole point of the workflow is minimizing program complexity while
retaining every behavior. TLA+ provides the metric; programming becomes an
optimization problem: minimize measured complexity through design, verify
with TLC, subject to the kill-rate floor, clean effect conformance, and full
representation of the program. Doctrine: "The Standing Objective" and "The
Recursive Refinement Loop" in `references/architecture_tractability.md`.

Mechanize the objective so it runs on every ticket, not only at gate
failure, and cannot be gamed.

Acceptance criteria:

- A complexity ledger: `analyze complexity` metrics (state-space bound,
  distinct states, action count, R/W density) are recorded per ticket close
  and workflow close, in the manifest or history entry.
- Ticket close reports the complexity delta against the previous ledger
  entry. An increase requires a recorded justification naming the new
  essential behavior.
- Anti-gaming enforcement: a complexity decrease accompanied by degraded
  retention evidence — kill rate below floor, new unjustified coverage
  gaps or undeclared effects, or reduced external case coverage — is
  rejected at close, not recorded as an improvement. Deltas are only
  reported jointly with retention evidence from the same run.
- The recursive refinement loop is a required close-out step: either an
  approved refinement recommendation (with evidence) or an explicit
  "searched, found none" record. Refinement recommendations are advisory
  and user-approved, never auto-applied.
- Doctrine sections in SKILL.md and
  `references/architecture_tractability.md` are verified present and
  consistent with the shipped mechanization.
