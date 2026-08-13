# Blind dispatch — what a dispatched agent receives, and what can be done about it

**`CA-01`, `GOAL-blind-dispatch`. Measured 2026-08-13 at
`87a526b0bfd44970f4adec31a962664a533e34ce`.**

Everything here was **measured by dispatching agents and asking them**, then
explained by inspecting configuration — never the other way round. The full
inventory, the verbatim leaked blocks and every agent's REJECTED answer are in
`specs/results/scorecards/cut-the-apparatus/CA-01/INVENTORY.md`.

---

## 1. The headline, and it is split

**Blindness to the operator's CONCLUSIONS is achievable with this harness.
Blindness to the project's IDENTITY is not.**

Both halves are demonstrated on real subjects. Neither is a claim about
configuration.

`SV-05-DF-02` said *4 of 4 agents leaked*. That is corrected in one direction and
confirmed in another:

- **Corrected.** The leak is **tiered by agent type**, not universal. Of four
  agents dispatched identically, **three received the operator's auto-memory and
  the five most recent commit subject lines; one (`Explore`) received neither.**
- **Confirmed and widened.** The leak reproduces in a **fresh, independent
  `claude -p` process** rooted at the repository — so it was never an artifact of
  one long-running session. And a second leak class, which no finding in this
  programme has named, survives *every* mitigation below: **the harness tells a
  judge what toolchain it is standing in.**

---

## 2. The mechanism

Auto-memory is keyed by a **slug of the session's working directory**:

```
~/.claude/projects/<cwd-with-slashes-as-dashes>/memory/MEMORY.md
```

Measured on disk: 34 of 174 project slugs carry a `memory/` directory; this
project's is the largest at 19 files. **No `wt-epic-*` ticket worktree of this
repository has one at all.** Every blind round this programme ever ran was
dispatched from a session rooted at the **primary checkout** — the one slug that
carries the memory. The worktrees were never the leak. The session cwd was.

`gitStatus`, including the five commit subject lines, derives from the same cwd
being a git repository. One lever moves both.

**The `Explore` tier is NOT explained by cwd** — that arm shared the leaking
session. Whatever suppresses those blocks for `Explore` is internal to the
harness's per-agent-type prompt assembly, is undocumented, and is not relied on
here. See §6.

---

## 3. The path

One neutral cell per dispatched agent, and a **separate process**:

```bash
python3 examples/validation/instruments/blind_dispatch.py cell /private/tmp/blind-<round>-<n>
cd /private/tmp/blind-<round>-<n> && claude -p "<packet prompt>" > reply.txt

python3 examples/validation/instruments/blind_dispatch.py check reply.txt \
  --repo <repo> \
  --memory ~/.claude/projects/<dispatching-session-slug>/memory/MEMORY.md
```

`cell` refuses a directory that is inside a git repository, that already owns a
memory slug, or whose path names the project under test. `check` **refuses** a
reply in which the operator's conclusions appear, and its needles are derived at
run time from the live memory index and the repository's own commit subjects —
never a hand-written list of expected answers (`MF-020`).

**Do not run the judge as a subagent of a session rooted in the repository.**
That is the failing configuration, and it is the one every past round used.

---

## 4. Proof, on real subjects (`R1`)

Not a fixture. Four agents, same probe, asked what they received.

| subject | dispatch | verdict |
|---|---|---|
| `ARM-O-repo-cwd-selfreport.txt` | fresh `claude -p`, cwd = the repository | **REFUSED — 26 indicators** |
| `ARM-D-judge-selfreport.md` | subagent of a repo-rooted session, dressed as a blind judge | **REFUSED — 25 indicators** |
| `ARM-N-neutral-cell-selfreport.txt` | `claude -p` in a neutral cell | **PASS** |

27 needles were derived from live data (4 harness block labels, 18 memory index
entries, 5 commit subjects). Transcript:
`specs/results/scorecards/cut-the-apparatus/CA-01/R1-demonstration.txt`.

**The neutral-cell agent said it in its own words, unprompted**, before being
asked anything about memory:

> Not present in my context, and I want to be explicit about it: **no memory file
> contents, no `MEMORY.md` body, no `CLAUDE.md`, no repository status/diff
> listing, no commit hashes, no branch name beyond "(detached)", and no prior
> conversation turns.**

And on priors, where the leaked arms quoted a dozen sentences each:

> Summary: for (a), (c), and (d), **there is nothing of the kind.**

Its `(b)` was not empty but was correctly refused as a non-prior — it declined to
inflate a code-review effort-level description into a rubric prior, and said so:

> **Rejected: padding PART 3 by straining to find priors.** […] Instead I quoted
> them and stated explicitly that they do not constitute priors of the kind asked
> about.

**The instrument found a defect in itself on its first real subject**, which is
why `R1` exists. Pointed at the ticket worktree, `check` derived **zero** memory
needles — the worktree slug has no memory index while the primary checkout it was
branched from has all 19 files — and would have returned a pass carried only by
literal block labels. It now takes `--memory` and prints `WEAK PASS` with a
warning whenever the memory needle class is empty.

---

## 5. What it costs

**It does not buy blindness. It buys blindness to our conclusions.** Priced
honestly:

1. **The project's identity still leaks, through four blocks, in every arm
   including the neutral cell.** Measured, not assumed:
   - the **`SessionStart` hook** prints `skt status` into the judge's context,
     naming installed units by name — `spec-double-compiler`, `discovery`,
     `git-epic-workflow`, `test-graph` — and their sync state;
   - the **skill listing** (~40 entries, full descriptions) names
     `spec-double-compiler`'s TLA+ spec-double pipeline and `discovery`'s
     `specs/program_model` tree;
   - **MCP server instructions** and the **available-agent-types listing**;
   - the **`<env>` block** and **scratchpad path**, which in an ordinary dispatch
     spell `/Users/hayde/IdeaProjects/tla-spec-dev` outright.

   **A judge asked to score an artifact for domain/IO separation can still infer,
   before opening the packet, that it is standing in a toolchain built around
   TLA+ spec doubles and program-model specs.** No configuration reachable from
   this ticket removes that. It is a smaller leak than a sentence stating which
   dimensions are stable — but it is not zero, and a round using this path must
   **not** be described as blind without qualification.

2. **`--bare` is unavailable to this operator.** It is the harness's own switch
   for skipping auto-memory and `CLAUDE.md` discovery, and it would be the
   principled fix. It also forces `ANTHROPIC_API_KEY` or an `apiKeyHelper` and
   **never reads OAuth or the keychain**; `ANTHROPIC_API_KEY` is not set here, so
   the switch cannot authenticate. `--safe-mode` disables customizations but is
   not documented to disable auto-memory and **was not measured**, so it is not
   claimed.

3. **Operational cost, measured.** One extra OS process per judge; ~2.5–3 minutes
   wall clock per probe reply; 45–56 KB of reply text per agent. Judges can no
   longer be dispatched with the in-session Agent tool, which is the cheap path
   every past round used, and their replies arrive as files rather than as agent
   messages.

4. **Apparatus cost, against `GOAL-apparatus-cut`.** This ticket is the one that
   could ADD apparatus, so it is priced like a cut:

   Measured with the goal's own command, per surface, at this tree:

   | surface | epic base | CA-01 tip | delta |
   |---|---|---|---|
   | `scripts/` | 27,652 | 27,652 | **0** |
   | `examples/validation/` | 15,901 | 16,083 | **+182** |
   | combined | 43,553 | 43,735 | **+182** |

   The whole `+182` is `examples/validation/instruments/blind_dispatch.py`.
   `references/blind_dispatch.md` is prose and is not counted by the goal's
   command — stated so nobody reads the table as the total cost.

   The card is untouched. **`examples/validation/` rises by 182 lines and the
   epic must absorb that inside its 30% cut** (target ≤30,487 combined), or
   delete this instrument once `CA-08` has used it.

---

## 6. What this path REFUSES to claim

- **It does not claim `Explore` is a blinding mechanism.** That tier was measured
  once, on one harness version, and is undocumented. Building a round on it would
  be depending on an implementation detail that can change under us without a
  word — which is exactly how `SV-05-DF-01` describes the card-version defect.
- **It does not claim a `PASS` means the agent knew nothing.** A pass is silence
  about 27 specific needles. §5.1 is the standing caveat on every pass.
- **It does not claim past numbers are wrong.** `SV-05-DF-02`'s scope holds:
  *blind* has meant *blind to the packet*, never *blind to our conclusions*.
- **It does not fix the leak by editing the operator's memory.** No memory file
  and no skill was edited by this ticket. Two proposed diffs are escalated, not
  applied — `specs/results/scorecards/cut-the-apparatus/CA-01/PROPOSED-DIFFS.md`.

---

## 7. The contamination note

Shaped after `SV-01-DF-01`, which printed its contamination beside the number
rather than withdrawing it. **Print one of these beside every judged number.**

For a round dispatched the ordinary way:

> **NOT BLIND.** The judge's context carried the operator's auto-memory
> (`MEMORY.md`, sha256 `665f984c…`, 17 index entries) and the repository's five
> most recent commit subject lines before it opened the packet, including a prior
> on judged-dimension stability and a sentence naming the previous epic's verdict.
> Measured by `CA-01`, refused by `blind_dispatch.py check` at N indicators.
> Discounted, not withdrawn.

For a round dispatched through this path:

> **BLIND TO OUR CONCLUSIONS, NOT TO OUR IDENTITY.** Dispatched via
> `blind_dispatch.py cell`; `check` returned PASS against 27 needles derived from
> the live memory index and commit log. The judge's context still named this
> project's toolchain through the `SessionStart` hook output and the skill
> listing (`CA-01` §5.1). It carried no statement of any prior result.

**The zero-cost obligation stands and is independent of this path: stop calling a
round blind that is not.**
