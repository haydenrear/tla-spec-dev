# CA-01 — addendum: one claim refuted, one instrument defect, and six factual corrections

**Written after `CA-01` closed and after an independent review of PR #263
returned RECOMMEND CHANGES.** The sealed evidence — `RESULT.md`, `INVENTORY.md`,
`R1-demonstration.txt`, `COST.md`, `PROPOSED-DIFFS.md` — is **not edited by this
file**; it is sealed against the close-history snapshot at
`specs/.history/cut-the-apparatus-epic/ticket-000-CA-01/`. Corrections are made
here. `references/blind_dispatch.md` and `examples/validation/instruments/` are
living surfaces and **are** corrected in place, with every change listed in §6.

---

## 1. `CA-01-DF-01` is REFUTED in its original form, by the one flag CA-01 declined to measure

**This is the ticket's own error and it is the important entry in this file.**

`CA-01-DF-01` as filed said blindness to this project's *identity* was **not
reachable with this harness**, and filed it **blocking**. `RESULT.md` §1 and the
PR title carried the same claim unhedged. It is wrong.

**`claude --safe-mode` authenticates normally on OAuth and removes the leak.**
Found by an independent reviewer; filed by the epic owner as `CA-00-DF-03`.
CA-01 then measured it directly, with the same probe text as the original four
arms, and the two agree:

| | auto-memory | gitStatus | SessionStart hook | skills | MCP |
|---|---|---|---|---|---|
| plain, repo cwd (`ARM-O`) | **YES** | **YES** | **YES** | ~40, project units | YES |
| neutral cell (`ARM-N`) | no | no | **YES** | ~40, project units | YES |
| **`--safe-mode`, repo cwd** (`ARM-S1`) | **no** | **YES** | **no** | 11 built-ins | **no** |
| **`--safe-mode` + neutral cell** (`ARM-S2`) | **no** | **no** | **no** | 11 built-ins | **no** |

Transcripts: `probes/ARM-S1-safemode-repo.txt`, `probes/ARM-S2-safemode-cell.txt`.

**Neither half is sufficient alone; the combination is.** `--safe-mode` does not
touch `gitStatus` — at the repository cwd the probe still received the five
commit subject lines, and **reported rejecting an inference from them**:

> I was inclined to infer that *"attribute every red"* and *"210-row findings
> ledger"* imply a scoring rubric with red/amber/green bands and therefore
> answer "yes" to (b). That inference is not in the text […] so I answered (b)
> narrowly.

That is the original leak class still operating under `--safe-mode`, visible
only because the agent declined it. Conversely the neutral cell alone leaves the
hook and the skill listing standing. `ARM-S2` is clean, in the agent's own words:

> no instruction/memory file (`CLAUDE.md`), no repository status listing (the
> environment block states "Is a git repository: false"), no MCP server
> instructions

### What CA-01 established, and what it did not

**Established:** the *effect*, twice, on this harness version, transcripts
recorded. The reviewer measured it twice independently.

**NOT established:** whether `--safe-mode` disables auto-memory **by design or
incidentally**. Its own `--help` names *"CLAUDE.md, skills, plugins, hooks, MCP
servers, custom commands and agents, output styles, workflows, custom themes,
keybindings, and more"* — **auto-memory is not named, and "and more" is carrying
it.** A round depending on this depends on undocumented behaviour, which is
precisely the objection CA-01 raised against the `Explore` tier in
`CA-01-DF-03`, and it applies here with equal force. **Record the memory digest
beside every round rather than trusting the flag.**

### Consequence

`GOAL-blind-dispatch` clause (c)'s *"state the impossibility"* escape hatch was
invoked **prematurely** and is **withdrawn**. The epic **can** run judged rounds
blind to the operator's conclusions. `CA-01-DF-01` is downgraded from
**major/blocking** to **minor/non-blocking** and narrowed to the `<env>` block,
the scratchpad path, and the `--bare` credential gap (`CA-01-DF-02`, unchanged).

**The methodological lesson is the one the reviewer named.** CA-01 explicitly
listed *"Rejected: claiming `--safe-mode` works when I never measured it"* as a
virtue. Refusing to claim it was right. **Refusing to measure it was not**, and
shipping a blocking finding whose own `suggested_fix` (b) pointed straight at
the unmeasured flag is the error. *Unmeasured* is a reason to measure, not a
reason to route around.

---

## 2. The instrument had an undeclared false-PASS mode. It is now REFUSED, not declared

`CA-00-DF-04`. Three false-PASS modes were found by review:

| case | shipped behaviour | now |
|---|---|---|
| **empty subject** | `PASS`, exit 0 | **`UNDECIDED`, exit 2** |
| **failed dispatch** (`Error: Invalid API key`) | `PASS`, exit 0 | **`UNDECIDED`, exit 2** |
| judge **paraphrases** the memory | `PASS`, exit 0 | **still `PASS`** — declared |

**The empty / failed-dispatch case was declared nowhere and is the
operationally likely one:** a dispatch that silently did not run reads as a
clean round. `WEAK PASS` never covered it — that fires only when needles cannot
be *derived*, never when the *subject* is empty. **A false PASS in an instrument
whose entire job is refusing is the worst defect it could have had**, and it is
the same shape as the thing CA-01 was built to catch: absence of evidence
reported as evidence of absence.

`check` now applies a precondition before counting any needle — empty, below a
200-byte floor, or carrying a dispatch-failure signature → **exit 2 UNDECIDED**.
Demonstrated on all three reviewer cases, plus proof the two sealed subjects are
unaffected (`ARM-O` still exit 1 REFUSED, `ARM-N` still exit 0 PASS):
`false-pass-demonstration.txt`.

The **paraphrase** mode is not fixable by substring matching and remains
declared in the registry's `blind_spot`.

---

## 3. The `MF-020` claim overstated the instrument. Corrected

**4 of the 27 needles are hand-written literals** in `HARNESS_MARKERS`.

- `RESULT.md` §6 says *"Rejected hand-writing the leak needles"* — **too broad**.
- `references/blind_dispatch.md` §4 called all 27 *"derived from live data"* —
  **wrong**, and corrected in place.
- The PR body's table always showed the 4 as literals; that half was right.

**The sharpest form, from the reviewer:** running `ARM-O` with
`--memory /nonexistent --commits 0` **still REFUSES on those 4 literals alone**,
so **the shipped `R1` failing demonstration is carried entirely by the
hand-written half.** CA-01 had already recorded this property as a *virtue* — it
is why the failing demonstration cannot die from drift (§5) — without noticing
it contradicted the `MF-020` sentence.

**What survives of the original claim, stated precisely:** the four literals are
harness **block labels** — names of injected blocks — not expected *answers*
about any subject, which is why they are not the `MF-020` hazard a hand-written
list of conclusions would be. The two classes that *are* derived (18 memory
entries, 5–12 commit subjects) are the ones that carry project-specific content.
`check` prints the three classes separately, which is what makes the distinction
checkable. The source comment now says all of this.

---

## 4. Re-pricing the lines against `--safe-mode`

The reviewer's point stands: **`--safe-mode` is a zero-apparatus alternative to
much of what CA-01 shipped**, and `--safe-mode` + neutral cell strictly
dominates the shipped path.

Current, measured with the goal's own command at this tree:

| surface | epic base | CA-01 tip | delta |
|---|---|---|---|
| `scripts/` | 27,652 | 27,652 | **0** |
| `examples/validation/` | 15,901 | **16,129** | **+228** |
| combined | 43,553 | **43,781** | **+228** |

**The figure rose from +182 to +228** — the false-PASS fix and the corrected
source comments. Reported because a cost that moves after review must be
re-reported, not left at the flattering number.

### Honestly: which lines does `--safe-mode` make redundant?

| part | lines | does `--safe-mode` replace it? |
|---|---|---|
| `cmd_cell` | **31** | **Largely yes.** Its job is a directory outside any git repo. `--safe-mode` does not do that — `gitStatus` survives it — so the *cell* is still needed, but as a **documented rule** ("dispatch from a directory outside any git repository"), which costs **zero lines**. What the 31 lines add is *refusals*: it declines a path inside a repo, one that already owns a memory slug, one naming the project. That is real but it is a convenience over a one-line rule. |
| `cmd_check` | **80** | **No.** It verifies the round actually was blind. `--safe-mode` is undocumented for auto-memory (§1), so verifying rather than trusting is the whole `R1` argument, and it is the part review found a real defect in — which is evidence the verifier earns its keep. |
| needle derivation, precondition, CLI, docstring | ~117 | **No**, they serve `check`. |

**So: roughly 31 of 228 lines are replaceable by a sentence, and the epic could
legitimately cut them.** The blunter answer the epic owner invited is also true
in a different sense: **most of the *blindness* is bought by the flag, not by my
lines.** The flag removes four of five leak sources for free; my 228 lines
remove the fifth (`gitStatus`, via the cell) and verify the result. **The
apparatus is not what made the round blind. It is what proves it was.**

`CA-01-DF-04`'s route to giving lines back is unchanged and now cheaper: if a
successor establishes that `--safe-mode` + a worktree-rooted or neutral cwd is
reliable, `cmd_cell` goes and only the verifier remains.

---

## 5. The `Explore` row has NO verbatim backing in this repository. Said plainly

**`INVENTORY.md`'s arm-A/B/C transcripts were never committed.** They were agent
messages in the ticket session; `INVENTORY.md` §7 discloses the abridgement and
`RESULT.md` §7 hedges the claim, but **the disclosure is in a later section than
the claim**, and the reviewer could not check the single observation that
corrects a published figure *downward*.

**Stated here at full strength: the `3 of 4` figure, and specifically the
`Explore` row of `INVENTORY.md` §2, is not backed by a transcript in this
repository or in `specs/.history/`.** Arms `ARM-N`, `ARM-O`, `ARM-S1` and
`ARM-S2` are committed in full; arms A, B and C are not, and cannot be
reconstructed.

**What raises confidence anyway, and it is not CA-01's own word:** the reviewer
**independently replicated the `Explore` behaviour at n=2 while trying to refute
it.** A correction that survives a party attempting to overturn it is stronger
evidence than the original single observation, and that replication — not
CA-01's report — is what the `3 of 4` should now rest on.

**Nothing about `CA-01-DF-03`'s refusal changes.** `Explore` still must not be
used as a blinding mechanism; it is undocumented, and §1 shows how that
reasoning applies to `--safe-mode` too.

---

## 6. Factual corrections, each one line

All found by the reviewer. Sealed files are corrected **here**; living files are
corrected **in place** and marked ✎.

1. **`references/blind_dispatch.md` §4** said *"Four agents, same probe"* above a
   **three-row** table. The four-agent measurement is `INVENTORY.md`; §4's table
   is the three `check` subjects. ✎ corrected.
2. **`references/blind_dispatch.md` §4** called all 27 needles *"derived from
   live data"*. ✎ corrected — 4 are literals (§3).
3. **`references/blind_dispatch.md` §7 vs §4** said **17** and **18** memory
   index entries, unreconciled. ✎ both now say **17 injected**, and explain the
   18th.
4. **`INVENTORY.md` §3.2** quotes **17** bullets as *"in full, exactly as
   injected"* directly above a digest of the **18**-bullet disk file. **Both are
   accurate and they are not the same object:** the injected copy carried 17; the
   file on disk had 18, the extra being the epic owner's `Cut-the-apparatus epic`
   entry added at kickoff. **The injected copy lagged disk.** The adjacency reads
   as if one thing — corrected here, since `INVENTORY.md` is sealed.
5. **`COST.md`** says *"five of this ticket's five filed findings"*. **Six were
   filed** (`CA-01-DF-06` at the epic owner's instruction). The channel claim —
   none from the suite — is unaffected. Corrected here.
6. **The PR's validation table** cites
   `pytest specs/tickets/CA-01/current/tests specs/tickets/CA-01/tests` for the
   67-passed spec-unit figure. **That path no longer exists at the head**: the
   close archived it. The runnable path is
   `specs/.history/cut-the-apparatus-epic/ticket-000-CA-01/ticket/`, which is
   where the reviewer reproduced it. ✎ corrected in the PR body.

---

## 7. The drift CA-01 predicted has already hit its own sealed figures

`R1-demonstration.txt` records **26** and **25** indicators for `ARM-O` and
`ARM-D`. At today's `--commits 5` the same subjects give **22** and **21**: the
epic's commits have moved, so five of the commit-subject needles that matched
when the figure was sealed no longer do.

**This is exactly the coupling CA-01 documented one section after shipping it**
— needles read live from `git log` — **and it has already changed a recorded
number.** The verdicts are unchanged and cannot change: both still REFUSE on the
four literals alone (§3). **The counts are not stable and should never be quoted
as properties of the subjects.** Said outright, because a sealed file with a
number in it invites exactly that.
