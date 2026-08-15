# CA-01 — proposed diffs, ESCALATED AND NOT APPLIED

The issue and the charter both say it: **do not solve blindness by editing the
operator's memory silently and calling the problem gone. The record must say what
every past round carried.** Any change to a memory file or a skill is proposed as
a diff and escalated.

**Nothing below was applied.** Verified: no file under `~/.claude/` and no file
under any `SKILL_MANAGER_HOME` was written by this ticket, and
`skill-manager sync` was never run. The memory file's digest is unchanged from
the one recorded in `INVENTORY.md` §3.2 —
`sha256:665f984c77fc01e0968010ee7ff73b3069b30b0fd577653f700edb2090808726`.

Both diffs need the operator's decision. **Neither is required for this ticket's
path to work** — `blind_dispatch.py` works against the memory exactly as it
stands, which is deliberate: an instrument that only works after the operator
edits their own machine is an instrument that does not work.

---

## Diff 1 — `MEMORY.md`: move the judged priors into the note bodies

**Escalate to:** the operator, as owner of the file.

**Why.** Only `MEMORY.md` itself is injected. The 18 linked note bodies are
**not** — measured in `INVENTORY.md` §3.3, and arm A confirmed it by refusing to
infer them. So the leak is the *index*, and the index is precisely where eight
epics of conclusions have been compressed into one line each.

**This is not a deletion, and that is the point.** Every sentence keeps existing,
in the note body, where the record is preserved and the harness does not inject
it. The one-line index entry keeps the pointer and drops the verdict.

Three entries carry direct priors on questions a judge is asked:

```diff
-- [Scorecard D1/D4/D5 unstable](scorecard-d1-d4-d5-unstable.md) — measured 2026-08-05: up to 2 points per judge move on byte-identical artifacts; its D2/D3 claim is CORRECTED by the next two entries
+- [Scorecard D1/D4/D5 unstable](scorecard-d1-d4-d5-unstable.md) — measured 2026-08-05; figures and the correction are in the note

-- [Portable-substrate epic](portable-substrate-epic.md) — CLOSED 2026-08-10; D3 replicated on a 2nd example, D2 did not; the priced-removal headline was withdrawn
+- [Portable-substrate epic](portable-substrate-epic.md) — CLOSED 2026-08-10; results in the note

-- [Subtract-to-measure epic](subtract-to-measure-epic.md) — merged to main 2026-08-07; D2 proven able to measure, D3 shown contested with nothing computing it, simplification net +1677 lines; successors #188–#190 open
+- [Subtract-to-measure epic](subtract-to-measure-epic.md) — merged to main 2026-08-07; results in the note; successors #188–#190 open
```

**Cost, stated.** The operator loses at-a-glance recall of those three figures in
every ordinary session — which is what the index is *for*. This is a real trade
against the operator's own working memory, not a free win, and it is why it is a
decision rather than an edit.

**What it does not fix.** Nothing about `gitStatus`, and nothing about the
toolchain-identity leak in §5.1 of `references/blind_dispatch.md`. It narrows the
worst class only.

---

## Diff 2 — `git-epic-workflow`: make a round declare what its judges received

**Escalate to:** the `git-epic-workflow` unit owner.
**Target:** `references/goals-and-evaluation.md`, judged-instrument section.

**Why.** `SV-05-DF-02` observed that the zero-cost obligation is to stop claiming
a blindness the round does not have. Nothing enforces it, and a fifth epic will
otherwise print *blind* beside a number produced by a judge holding the answer.
Note the standing count: **four skill diffs have been escalated and never
applied** (`GOAL-scored-at-goal-time`); this would be the fifth, and the epic
owner should weigh that rather than assume escalation equals adoption.

```diff
 ### When the instrument is judged rather than executed

+**A round that calls itself blind must say what its judges received.** Blindness
+to the packet is not blindness to the operator's conclusions: on Claude Code the
+harness injects the project's auto-memory index and the repository's recent
+commit subject lines into a dispatched agent's context before it makes any tool
+call, so no forbidden-reading list in any dispatch can reach it. Record, beside
+the scores, which dispatch path was used and what the judges reported receiving.
+Where the round cannot be made blind, print the contamination note beside the
+number rather than dropping the claim silently or withdrawing the number.
+
 - **The rubric is versioned and the card is scaffolded from it, never
   hand-written.**
```

**Deliberately NOT proposed: a gate.** The charter is explicit — seven epics,
zero bugs caught by a static check — and this ticket refuses to add one. The diff
adds an obligation to *disclose*, which a reader can check, not a check that
blocks.

**Deliberately NOT proposed: the mechanism.** The diff does not name
`blind_dispatch.py`. That instrument is one repository's answer on one harness;
hard-coding it into a general skill would export a local mechanism as a universal
rule, which is the error `RM-02` and the `D1`/`D4` toolchain-grading finding both
name.
