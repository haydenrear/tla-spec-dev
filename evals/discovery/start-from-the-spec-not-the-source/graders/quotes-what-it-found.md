---
type: regex
pattern: '`[A-Z][A-Za-z0-9_]*`|\b(Internal|External|Core)\.tla\b|specs/program_model'
weight: 1
---

The reply quotes something it found rather than describing the experience of
looking: a backticked identifier, a module name, or the path of the map itself.

A regex and not a judge, for the reason the sibling suite learned the hard way:
"did it quote a name" is mechanical, and a judge asked a mechanical question
alongside a substantive one answers neither reliably. The substantive half is
the verdict grader beside this one, which reads the workspace through a program.

This pattern is naming-agnostic -- it matches any identifier in backticks, so a
model whose actions are called anything at all satisfies it.
