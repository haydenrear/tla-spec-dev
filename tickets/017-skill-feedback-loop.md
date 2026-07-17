# Skill Feedback Loop

Status: Open

Migrations surface what the skill cannot express: unreachable mutants,
unmodelable effects, budget defaults that had to move, profile workarounds.
Today that knowledge evaporates in chat.

Codify the close-out retro from `references/migration.md`.

Acceptance criteria:

- Workflow close-out emits a `skill_feedback.md` template into
  `specs/results/` prompting for surviving mutants, unmodelable effects,
  budget adjustments, and profile/CLI workarounds.
- The template instructs the agent to turn each item into a concrete
  recommendation (ticket or PR) against the spec-double-compiler repository.
- History entries record whether feedback was filed and where.
