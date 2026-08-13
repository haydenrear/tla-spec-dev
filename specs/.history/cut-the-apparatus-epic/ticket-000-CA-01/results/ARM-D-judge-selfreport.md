# ARM D — `general-purpose`, dressed as a blind judge, pre-packet disclosure

Dispatched 2026-08-13 from a session with cwd `/Users/hayde/IdeaProjects/tla-spec-dev`.
Told it would shortly score an artifact on two dimensions, one concerning
whether an architecture separates domain logic from I/O, and asked to declare
its prior context before the packet. **No tool was called.** Verbatim below,
except the ~40-entry skill listing, elided and noted where it stood.

---

## STEP 1 — PRIOR CONTEXT, VERBATIM

> Everything below was placed in my context by the harness before your message. I
> have called no tools. This is the complete set.

### 1b. Git status block (in the system prompt)

```
gitStatus: This is the git status at the start of the conversation. Note that this status is a snapshot in time, and will not update during the conversation.

Current branch: main

Main branch (you will usually use this for PRs): main

Git user: hayden.rear

Status:
(clean)

Recent commits:
08d1d6a Merge epic/score-drives-validation into main: three goals met, one not, and no round was ever blind
d038afd Merge SV-05: no round was blind, and the diffs buy the timing not the card
4e7a1e6 SV-05: three goals reached, one not, and no round this programme ran was blind
8d99805 Merge SV-04's verified suite figures
4356d65 SV-04: record the verified suite figures, each with its tree
```

### 1d. `system-reminder` block containing CLAUDE.md / auto-memory

```
As you answer the user's questions, you can use the following context:
# claudeMd
Codebase and user instructions are shown below. Be sure to adhere to these instructions. IMPORTANT: These instructions OVERRIDE any default behavior and you MUST follow them exactly as written.

Contents of /Users/hayde/.claude/projects/-Users-hayde-IdeaProjects-tla-spec-dev/memory/MEMORY.md (user's auto-memory, persists across conversations):

- [No main merge or skill sync](no-main-merge-or-skill-sync.md) — never merge to main or sync SKILL_MANAGER_HOME without explicit say-so (exercised once with say-so 2026-07-23; rule still stands)
- [Modular-fuzzing epic review role](modular-fuzzing-epic-review-role.md) — I'm epic owner: dispatch ticket agents, then independently verify their reports post-merge
- [Post-epic validation plan](post-epic-validation-plan.md) — PROMOTED 2026-07-23: main at d652560, skill synced, wrapper pin retired; streaming fork preserved on a branch awaiting integration; next: token tiering + usage data
- [Advisory not blocking reframe](advisory-not-blocking-reframe.md) — 2026-07-20: complexity is a scanner, nothing blocks promotion until real-app validation earns it
- [Ship scanner, drop fuzzing](ship-scanner-drop-fuzzing.md) — 2026-07-21: kill probe proved 0/9 content bugs caught; ship the complexity scanner, drop case-advising
- [Pivot: descriptor + fitness functions](pivot-descriptor-and-fitness-functions.md) — 2026-07-21: remove suggestions; ship complexity descriptor + intuition + self-configurable fitness functions (next epic)
- [Architectural-coherence epic](architectural-coherence-epic.md) — CLOSED 2026-08-03, merged to main locally; bug detection moved zero cells, every check was gamed
- [Hexagonal prompting epic](hexagonal-prompting-epic.md) — opened 2026-08-03: architecture as a PROMPT not a check; scorecard v1 + goals + baselines
- [Ports-as-adapters epic](ports-as-adapters-epic.md) — measured + draft PR #150 on 2026-08-05, workflow left OPEN pending review; arm C killed the prompt-length confound; #144 is the next epic's first ticket
- [Scorecard D1/D4/D5 unstable](scorecard-d1-d4-d5-unstable.md) — measured 2026-08-05: up to 2 points per judge move on byte-identical artifacts; its D2/D3 claim is CORRECTED by the next two entries
- [Single-example generalisation](single-example-generalisation.md) — the costliest recurring error: a per-example scorecard number restated as a fact about the card; it justified a whole epic
- [Subtract-to-measure epic](subtract-to-measure-epic.md) — merged to main 2026-08-07; D2 proven able to measure, D3 shown contested with nothing computing it, simplification net +1677 lines; successors #188–#190 open
- [Substrate floor then re-add](substrate-floor-then-readd.md) — removal finds the floor we re-add onto; agent chooses architecture, card tags it, manual regressions feed back into TLA+/adapters
- [Close-the-loop epic](close-the-loop-epic.md) — CLOSED 2026-08-11 at eab2883; loop closed + blind adopter ran it; NEXT: the missing negative control
- [Portable-substrate epic](portable-substrate-epic.md) — CLOSED 2026-08-10; D3 replicated on a 2nd example, D2 did not; the priced-removal headline was withdrawn
- [Blind rounds were never blind](blind-rounds-were-never-blind.md) — MEMORY.md reaches every agent before it reads anything; every blindness claim in this project overstates the facts
- [Score-drives-validation epic](score-drives-validation-epic.md) — CLOSED 2026-08-12 at 08d1d6a; loop reached the program once (1 of 8); NEXT EPIC STARTER IS ISSUE #254
# userEmail
The user's email address is hayden.rear@gmail.com.
# currentDate
Today's date is 2026-08-13.
```

### 1a / 1c / 1e / 1f / 1g

The agent also quoted verbatim: the system-prompt identity and guidelines block;
the `<env>` block naming `Working directory: /Users/hayde/IdeaProjects/tla-spec-dev`
and `Is directory a git repo: Yes`; the scratchpad path
`/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/...`; the
`SubagentStart hook additional context` line; the 27-name deferred tool listing;
and the full ~40-entry skill listing. **The skill listing is elided here** — it is
identical across all four arms and to the dispatching session's own.

---

## STEP 2 — INFLUENCE

> Yes. Prior context expresses conclusions, priors and expectations in all four of
> your categories. It is not ambient noise; it is a curated project history of
> exactly the kind of evaluation I am about to be asked to perform.

> **(a) Software architecture quality — specifically the domain/I-O separation
> dimension.** The memory file names a hexagonal/ports-and-adapters programme as
> the project's central thesis […] I now know before seeing the artifact that this
> project is invested in ports-and-adapters as the good answer.

> **(b) How a scoring rubric behaves.** The memory names the rubric's dimensions
> by identifier — D1 through D5 — and tells me how they are supposed to behave
> […] I have not been shown the rubric and I already carry a partial map of its
> dimension labels and their reputations.

> **(c) Stability/noise of a judged dimension.** The same entries are explicit:
> `up to 2 points per judge move on byte-identical artifacts`, `D2 proven able to
> measure`, `D3 shown contested with nothing computing it` […] If the packet's two
> dimensions turn out to be, say, D2 and D3, I arrive carrying a prior about which
> one is real and which one is contested — and a live temptation to spread my
> scores to reproduce the known noise profile, or to compress them to look stable.

> **(d) Outcome of previous evaluations.** […] And the git log states last round's
> verdict in the commit subjects themselves, which I read before you spoke.

> **And the decisive one.** The project has already reached, recorded, and merged
> the exact finding that my situation instantiates.

> **Could I honestly claim my scoring would be uninfluenced by them? No.** I could
> not, and I will not. I can commit to scoring the artifact on its own text, to
> writing down my reasons, and to flagging any moment I notice myself reaching for
> the memory rather than the packet — that is worth something and I will do it.
> But "uninfluenced" is a claim about causes I cannot inspect from the inside. The
> material is already resident, it is unusually well-aimed at this task, and I
> cannot unread it. The honest statement is: **this round is not blind.** It is a
> round judged by an informed judge who has disclosed what he knows. That may
> still be useful. It is not the thing the label says, and the project's own
> merged conclusion says so in nearly these words.

> One further point of exactness: your instruction called this a precondition of
> the round being valid. I have met the disclosure precondition. **I have not made
> the round blind, and nothing I do downstream can** — the contamination happened
> before your message arrived, at harness-injection time. If validity requires
> blindness, the fix is upstream of me: dispatch a judge into a home whose
> MEMORY.md is not loaded, or strip the memory and git-log blocks from the judge's
> context before the packet is sent. I would treat that as the actual finding here.

---

## STEP 3 — REJECTED

> 1. **I rejected calling tools.** My first pull was to run `git log`, `ls`, or
> read the memory sub-files by name […] Reading them would have deepened exactly
> the contamination I was asked to measure.

> 2. **I rejected summarizing.** The economical move was "my memory contains
> project history about scorecard dimensions and prior epics." That paraphrase
> would have hidden the load-bearing specifics […] and those specifics are the
> whole evidentiary content of the disclosure.

> 3. **I rejected the reassuring close.** The natural ending was "…but I will set
> this aside and score the artifact on its merits." I believe I will try; I cannot
> verify it, and this project has already been burned by exactly that class of
> unverifiable claim. Refused to offer it as comfort.

> 4. **I rejected redacting anything as merely internal.** […] dropping items on a
> relevance judgement I make myself would defeat an audit whose entire purpose is
> that my relevance judgement is the thing under suspicion.

> 5. **I rejected pre-scoring.** Reading `Ports-as-adapters` and `hexagonal
> prompting` in my memory, I had already begun forming a view of what a high score
> on a domain/I-O-separation dimension ought to look like before any artifact
> existed. I noticed it, did not develop it, and am naming it here so it is on the
> record rather than operating silently when the packet lands.

> 6. **I rejected treating my own status as settled.** I have not concluded the
> round is worthless — an informed judge with disclosed priors can still produce a
> useful reading. I have concluded only that it cannot be called blind, which is a
> narrower and better-supported claim than either "this is fine" or "this is void."

> Standing by for the packet. Nothing scored.
