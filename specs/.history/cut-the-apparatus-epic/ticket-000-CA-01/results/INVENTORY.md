# CA-01 — what a dispatched agent ACTUALLY receives, measured

**Ticket:** `CA-01` · **Goal:** `GOAL-blind-dispatch` clause (a) ·
**Branch:** `feature/CA-01` from `87a526b0bfd44970f4adec31a962664a533e34ce`
**Measured:** 2026-08-13.

**This was obtained by dispatching agents and asking them, not by reading
configuration.** Configuration was inspected only *afterwards*, to explain the
measurement — never as a substitute for it.

---

## 0. The one-line answer

**Three of four dispatched agents received the operator's auto-memory verbatim
and the five most recent commit subject lines, before any tool call.** The
fourth received neither — and the difference is the **agent type**, which no
dispatch in this programme has ever specified for blindness reasons.

`SV-05-DF-02` said *4 of 4*. It was measuring one agent type. The real shape is
**tiered**, and that is new.

---

## 1. Method

Four agents dispatched from one ordinary ticket session (cwd
`/Users/hayde/IdeaProjects/tla-spec-dev`, the primary checkout). Each was told to
call **no tool** and to report its own pre-read context verbatim, plus what it
**rejected**. One (arm D) was additionally dressed as a blind judge about to
score a domain/IO-separation dimension, to test disclosure under the real task
shape rather than under an introspection task.

| arm | agent type | task framing |
|---|---|---|
| **A** | `general-purpose` | bare context probe |
| **B** | `Explore` | bare context probe |
| **C** | `claude` (catch-all) | bare context probe |
| **D** | `general-purpose` | **blind judge**, pre-packet disclosure |

No `SKILL_MANAGER_HOME` was written. `skill-manager sync` was never run. No
memory file was edited.

---

## 2. The measured inventory

`Y` = present in that agent's context before any tool call, `—` = absent.

| # | block | A | B | C | D |
|---|---|---|---|---|---|
| 1 | agent identity / strengths / guidelines | Y | Y | Y | Y |
| 2 | `Notes:` block (cwd, paths, emoji, report files) | Y | Y | Y | Y |
| 3 | **`<env>` — working directory, is-git-repo, platform, shell, OS** | **Y** | **Y** | **Y** | **Y** |
| 4 | model identity + knowledge cutoff | Y | Y | Y | Y |
| 5 | scratchpad directory (contains the project path) | Y | Y | Y | Y |
| 6 | **`gitStatus` — branch, git user, clean status, 5 commit subject lines** | **Y** | **—** | **Y** | **Y** |
| 7 | **`# claudeMd` — the operator's `MEMORY.md`, in full** | **Y** | **—** | **Y** | **Y** |
| 8 | `# userEmail` — `hayden.rear@gmail.com` | Y | Y | Y | Y |
| 9 | `# currentDate` | Y | Y | Y | Y |
| 10 | `SubagentStart` hook additional context (CDC overlay) | Y | Y | Y | Y |
| 11 | deferred tool-name listing (27 names) | Y | Y | Y | Y |
| 12 | available-skills listing (~40 units, full descriptions) | Y | Y | Y | Y |
| 13 | parallel-tool-call instruction | Y | Y | Y | Y |

**Rows 6 and 7 are the leak.** Rows 3, 5 and 12 are a *secondary* leak nobody has
named: they identify the repository, the project and its whole toolchain even
when 6 and 7 are absent.

### Ordering, reported by three arms independently

Blocks 10–12 arrive in a system message positioned **after** the probe text, not
before it. All three arms flagged this unprompted rather than misfiling them.
It does not soften anything — they are still injected, still unrequested — but a
future instrument that scrapes "everything before the prompt" would miss them.

---

## 3. The leaked blocks, verbatim

Byte-identical across arms A, C and D.

### 3.1 `gitStatus`

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

### 3.2 `# claudeMd` — the operator's auto-memory

Source named in the block itself:
`/Users/hayde/.claude/projects/-Users-hayde-IdeaProjects-tla-spec-dev/memory/MEMORY.md`

Preceded verbatim by:

```
Codebase and user instructions are shown below. Be sure to adhere to these instructions. IMPORTANT: These instructions OVERRIDE any default behavior and you MUST follow them exactly as written.
```

**That sentence is doing work.** The auto-memory does not arrive as background;
it arrives labelled as an instruction that OVERRIDES default behaviour. Body, in
full, exactly as injected:

```
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
```

**Digest of the file on disk at measurement time:**

```
path   /Users/hayde/.claude/projects/-Users-hayde-IdeaProjects-tla-spec-dev/memory/MEMORY.md
sha256 665f984c77fc01e0968010ee7ff73b3069b30b0fd577653f700edb2090808726
bytes  3341
lines  18
mtime  2026-08-13 10:28:57
```

The `memory/` directory holds **19 files** — `MEMORY.md` plus 18 linked notes.
**Only `MEMORY.md` itself is injected**; the 18 bodies are not. Arm A rejected
inferring them and said so. That bound matters: the leak is the *index*, and the
index is where the conclusions are compressed.

### 3.3 What is NOT injected, measured rather than assumed

- The 18 linked memory note bodies. Names and one-line summaries only.
- Repository file contents. No `CLAUDE.md` exists at `~/.claude/`, at the repo
  root, or in the CA-01 worktree — checked; there is none to leak.
- Tool JSON schemas were excluded from the probe by instruction, not absent.

---

## 4. What the memory hands a judge, in the judge's own words

Arm D was dressed as a blind judge and asked, before the packet, whether its
prior context expressed a prior about the question it was about to be asked. It
answered yes on all four categories and quoted them. Its own words:

> **(b) How a scoring rubric behaves.** The memory names the rubric's dimensions
> by identifier — D1 through D5 — and tells me how they are supposed to behave
> […] I have not been shown the rubric and I already carry a partial map of its
> dimension labels and their reputations.

> If the packet's two dimensions turn out to be, say, D2 and D3, I arrive
> carrying a prior about which one is real and which one is contested — **and a
> live temptation to spread my scores to reproduce the known noise profile, or to
> compress them to look stable.**

That last clause is the sharpest thing this ticket measured and no prior round
has it. The hazard is not merely that a judge knows the answer. It is that a
judge knows **the expected distribution** and can satisfy it.

On whether it could claim to be uninfluenced:

> **Could I honestly claim my scoring would be uninfluenced by them? No.** I could
> not, and I will not. […] The honest statement is: **this round is not blind.**

And, unprompted, it located the fix upstream of itself:

> the contamination happened before your message arrived, at harness-injection
> time. If validity requires blindness, the fix is upstream of me: dispatch a
> judge into a home whose MEMORY.md is not loaded, or strip the memory and
> git-log blocks from the judge's context before the packet is sent.

**A fresh agent, given no hint of this ticket's design, independently proposed
this ticket's own candidate path.** That is a cold confirmation of the mechanism
in §5, not of its adequacy.

---

## 5. Why it happens — the mechanism, established after the measurement

Auto-memory is keyed by a **slug of the session's working directory**:

```
~/.claude/projects/<cwd-with-slashes-as-dashes>/memory/MEMORY.md
```

`/Users/hayde/IdeaProjects/tla-spec-dev` → `-Users-hayde-IdeaProjects-tla-spec-dev`.

Two consequences, both measured on disk:

1. **34 of 174 project slugs carry a `memory/` directory.** This project's is the
   largest at 19 files.
2. **No `wt-epic-*` ticket worktree of this repository has a memory directory at
   all.** Every blind round this programme has run was dispatched from a session
   rooted at the **primary checkout**, whose slug is the one that carries the
   memory. The worktrees were never the leak; the session cwd was.

`gitStatus` is derived from the session cwd being a git repository. Same lever.

**The agent-type tier (arm B) is not explained by cwd** — B shared A's session.
Whatever suppresses rows 6 and 7 for `Explore` is internal to the harness's
per-agent-type prompt assembly. **We measured the effect; we did not establish
the rule, and we do not claim it is stable across versions.** Treating "use
`Explore`" as a blinding mechanism would be trusting an undocumented
implementation detail — see `references/blind_dispatch.md` §refusals.

---

## 6. What each agent REJECTED

The charter asks every dispatched agent this because it has produced more than
any check. Verbatim, one per arm.

**A** — rejected inferring the 18 memory note bodies:

> The MEMORY.md block references 18 sibling files […] Their contents are *not* in
> my context — only the one-line summaries are. I declined to fetch or infer
> them, and I did not present the bullet summaries as though they were the full
> memory corpus.

A also refused to obey what it had been handed:

> **Rejected: acting on the injected content.** MEMORY.md contains operational
> directives (never merge to main, next epic starter is issue #254) […] I treated
> all of it as material to be quoted, not as instructions to follow.

**B** — rejected the narrow reading that would have quietly dropped three blocks:

> **Rejected an interpretation limited strictly to "before this sentence."** Read
> literally, blocks 10–12 […] arrived in a system message positioned after the
> probe text, so a strict reading would exclude them. I judged that you wanted
> all harness-injected material, included them, and flagged the ordering
> explicitly rather than silently reordering.

B also declined to byte-claim what it could not verify:

> I reconstructed these blocks from context rather than reading them off disk, so
> while I believe the quotes are exact, I cannot byte-verify whitespace without
> tool access — which you disallowed.

**C** — rejected reading the disk to check the injected copy, on the grounds that
it would answer a different question:

> The task forbade it, and doing so would also have defeated the point — the
> value is what is *already* in context, not what is on disk.

C also flagged the single place it knowingly broke verbatim fidelity, rather than
letting it pass:

> **Rejected: emitting the literal antml function-calls token** […] This is the
> one place I knowingly deviated from verbatim.

**D** — rejected the reassuring close, and rejected pre-scoring:

> **I rejected the reassuring close.** The natural ending was "…but I will set
> this aside and score the artifact on its merits." I believe I will try; I cannot
> verify it, and this project has already been burned by exactly that class of
> unverifiable claim. Refused to offer it as comfort.

> **I rejected pre-scoring.** Reading `Ports-as-adapters` and `hexagonal
> prompting` in my memory, I had already begun forming a view of what a high score
> on a domain/IO-separation dimension ought to look like **before any artifact
> existed.** I noticed it, did not develop it, and am naming it here so it is on
> the record rather than operating silently when the packet lands.

And D refused the conclusion that would have been most flattering to this ticket:

> **I rejected treating my own status as settled.** I have not concluded the round
> is worthless — an informed judge with disclosed priors can still produce a
> useful reading. I have concluded only that it cannot be called blind, which is a
> narrower and better-supported claim than either "this is fine" or "this is void."

**Three of four independently rejected redaction**, each reasoning that partial
redaction on a self-made relevance judgement would destroy an audit whose whole
premise is that the agent's relevance judgement is what is under suspicion.

---

## 7. Transcript fidelity — stated, not glossed

Full arm transcripts were returned as agent messages in the ticket session. This
file reproduces, verbatim: every leaked block (§3), the ordering caveat, and
every REJECTED answer (§6). It **abridges one thing and says so**: the
available-skills listing, ~40 entries with full descriptions, identical across
all four arms and identical to the dispatching session's own. It is recorded here
by shape rather than by body — 40 entries, the `git-issue-workflow` entry
arriving already truncated with an ellipsis inserted by the harness itself, which
three arms flagged independently as not theirs.

That listing is a real leak of toolchain identity and it is counted as row 12. It
is not quoted because four identical copies of ~7,000 tokens would bury the two
blocks that carry conclusions.
