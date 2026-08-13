# `GOAL-blind-dispatch` — baseline

**Measured at the epic base `08d1d6a90ad2638cdfceee7cc2e150732daa3438`.**

---

## The baseline is a negative

**No round this programme has run was blind in the sense its own dispatches
assert.** `SV-05-DF-02`, and it is the finding that costs the most.

**4 of 4** blind agents in `SV-05`'s 2×2 reported, **unprompted**, that the
operator's persistent auto-memory and the environment block were in their
context **before they read anything**. One quoted `MEMORY.md` verbatim —

> *"up to 2 points per judge move on byte-identical artifacts"*

— and named four prior epics by name.

**The environment block additionally hands every subagent this repository's
path, branch, clean status and the subject lines of its five most recent
commits.** At this epic's base those include:

```
08d1d6a Merge epic/score-drives-validation into main: three goals met, one not, and no round was ever blind
d038afd Merge SV-05: no round was blind, and the diffs buy the timing not the card
4e7a1e6 SV-05: three goals reached, one not, and no round this programme ran was blind
```

**A judge dispatched to score D3 blind has, in context before it opens the
packet, a sentence saying which dimensions this project believes are stable.**

## Why the obvious fix does not work

**It requires no tool call, so no forbidden-reading list reaches it.**
`SV-01-DF-03` filed `git status` as a leak the dispatches never named — and a
dispatch *can* name `git status`. **Nothing a dispatch says removes a block the
harness injects first.**

## Scope of the contamination

Retroactive, and it applies to:

- `CL-04`'s blind adopter probe and its census
- `SV-01`'s four judges
- `SV-04`'s four judges
- `SV-06`'s survey
- `SV-05`'s own four agents

**This does NOT assert that any published number is wrong.** It asserts that
*blind* has meant *blind to the packet and to our source* for eight epics, never
*blind to our conclusions*, and that nobody measured the difference because
nobody noticed it.

## What is owed, and what is not

**Owed immediately, at zero cost:** stop claiming a blindness the round does not
have.

**NOT acceptable:** editing the memory silently and calling the problem gone.
**The record must say what every past round carried.**

## The target

**No numeric target — the instrument does not exist yet.** Four clauses:

1. What a dispatched agent receives is **measured** and written down.
2. A dispatch path exists that demonstrably carries none of the operator's
   conclusions, **proven by fresh agents asked what they received** — not by
   inspecting configuration.
3. The cost is stated. **If blindness cannot be achieved with this harness, that
   is a finding about the whole programme.**
4. No silent memory edit.

## The memory file as it stood at the epic base

Digest recorded so a later round can say whether the leak changed:

```
path: ~/.claude/projects/-Users-hayde-IdeaProjects-tla-spec-dev/memory/MEMORY.md
```

`CA-01` records its digest and contents inventory. **Read it; do not edit it.**
