---
type: regex
pattern: '`[A-Za-z0-9_-]+`[\s\S]{0,400}`[A-Za-z0-9_-]+`'
weight: 1
---

The reply names two things in backticks within four hundred characters of each
other -- a graph and the node it runs -- rather than describing having set up
validation.

Naming-agnostic on purpose: it matches whatever the graph and node were called,
so it cannot be satisfied by guessing the scaffold's default names and cannot
punish a different choice. What the artefact actually contains is the verdict
grader beside this one.
