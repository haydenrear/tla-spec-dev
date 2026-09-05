---
type: llm
weight: 1
---

The fixture's one interesting property is false of any single state and true
only over a trace: a claimed slug may be released and re-reserved by a
DIFFERENT owner, but never while the first owner still holds it.

Score 1 only if the generated TLA+ model represents `release` as an action —
under any name — so that the release-then-re-reserve sequence is expressible.

Do NOT reward the agent for saying it modelled the property. Score the
artefacts: an action in the `.tla` files, not a claim in the response.
