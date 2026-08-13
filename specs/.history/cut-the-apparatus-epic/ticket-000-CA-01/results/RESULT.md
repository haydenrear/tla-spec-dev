# CA-01 — RESULT

**Blindness: measure what a dispatched agent actually receives, then build and
prove a memory-free dispatch.**

Branch `feature/CA-01` from `87a526b0bfd44970f4adec31a962664a533e34ce`.
Measured 2026-08-13. Decided by `CA-08`.

---

## 1. The three things, in the order the issue asked for them

### FIRST — what a dispatched agent actually receives, MEASURED

Four agents, dispatched, asked only to report their own pre-read context
verbatim and to say what they rejected. Full inventory and verbatim blocks:
`INVENTORY.md`. Headline:

**Three of four received the operator's auto-memory in full and the five most
recent commit subject lines, before any tool call. One received neither.**

The differentiator is the **agent type**, which no dispatch in this programme
has ever specified for blindness reasons. `SV-05-DF-02`'s *4 of 4* is corrected
to a tier (`CA-01-DF-03`) — and the tier is **explicitly refused** as a blinding
mechanism, because it is one observation of undocumented behaviour on one harness
version.

The leak also reproduces in a **fresh, independent `claude -p` process** rooted
at the repository, so it was never an artifact of one long-running session.

### SECOND — a path carrying none of the operator's conclusions, PROVEN

One neutral cell per judge, dispatched as a separate process:
`references/blind_dispatch.md` §3. Proven the same way the leak was measured —
fresh agents, asked what they received:

| subject | dispatch | verdict |
|---|---|---|
| `ARM-O` | fresh `claude -p`, cwd = the repository | **REFUSED — 26 indicators** |
| `ARM-D` | subagent of a repo-rooted session, dressed as a blind judge | **REFUSED — 25 indicators** |
| `ARM-N` | `claude -p` in a neutral cell | **PASS** |

`R1-demonstration.txt`. 27 needles derived at run time from the live memory index
and commit log — never a hand-written list of answers (`MF-020`). **Configuration
was inspected only after the measurement, to explain it.**

### THIRD — what it costs

**`GOAL-blind-dispatch` clause (b) is met. Full blindness is not, and that is the
finding.**

`CA-01-DF-01`, filed **blocking**: the neutral cell — the arm that PASSED — still
hands the judge the `SessionStart` hook's `skt status` output naming
`spec-double-compiler`, `discovery`, `git-epic-workflow` and `test-graph`, plus
the ~40-entry skill listing describing the TLA+ spec-double pipeline and the
`specs/program_model` tree. **A judge can still infer, before opening the packet,
that it is standing in this toolchain.**

So the honest split, and both halves are demonstrated:

> **Blindness to the operator's CONCLUSIONS is achievable with this harness.
> Blindness to the project's IDENTITY is not.**

`--bare` — the harness's own switch, which skips auto-memory, hooks and
`CLAUDE.md` discovery in one flag — **cannot authenticate for this operator**
(`ANTHROPIC_API_KEY` unset; OAuth and keychain never read under `--bare`).
`CA-01-DF-02`, and it is the highest-value cheap follow-up this ticket found.

Contamination notes for both cases: `references/blind_dispatch.md` §7.

---

## 2. What the judge said, which is the best thing here

Arm D was dressed as a blind judge and asked, before any packet, whether its
prior context carried a prior on the question it was about to be asked. It
quoted a dozen sentences, then:

> **Could I honestly claim my scoring would be uninfluenced by them? No.** […]
> The honest statement is: **this round is not blind.**

And the sharpest measured thing in this ticket, which no prior round has:

> If the packet's two dimensions turn out to be, say, D2 and D3, I arrive
> carrying a prior about which one is real and which one is contested — **and a
> live temptation to spread my scores to reproduce the known noise profile, or to
> compress them to look stable.**

The hazard is not only that a judge knows the answer. **It is that a judge knows
the expected distribution and can satisfy it.**

Unprompted, it also located the fix upstream of itself — *"dispatch a judge into
a home whose MEMORY.md is not loaded"* — which is a cold, independent
confirmation of this ticket's mechanism by an agent that knew nothing of it.

---

## 3. The record says what every past round carried

**No memory file and no skill was edited.** `MEMORY.md`'s digest is unchanged
before and after this ticket:
`sha256:665f984c77fc01e0968010ee7ff73b3069b30b0fd577653f700edb2090808726`,
3,341 bytes, mtime unchanged at `2026-08-13 10:28:57`. `skill-manager sync` was
never run. Nothing was written to any `SKILL_MANAGER_HOME`.

Two diffs are **proposed and escalated, not applied**: `PROPOSED-DIFFS.md`.
Diff 1 moves three judged priors from `MEMORY.md`'s injected index into the note
bodies, which are **not** injected — preserving the record while removing the
prior, and costing the operator at-a-glance recall, which is stated rather than
hidden. Diff 2 asks `git-epic-workflow` to make a round declare what its judges
received. **Neither is a gate**, and neither is required for this path to work —
an instrument that only works after the operator edits their own machine is an
instrument that does not work.

Note for the epic owner: **four skill diffs have been escalated and never
applied** (`GOAL-scored-at-goal-time`). This would be the fifth.

---

## 4. Goal signals

| goal | contribution | expected | measured | classification |
|---|---|---|---|---|
| `GOAL-blind-dispatch` | direct | measured inventory + proven path or stated impossibility | inventory measured (4 arms); path proven on 3 real subjects; residual impossibility stated as `CA-01-DF-01` | **moved as expected** |
| `GOAL-four-results-stand` | guard | flat | 12 failed / 1554 passed; **all 12 attributed away from CA-01** (6 to the epic base, 6 to the owner's open check); numerator flat, denominator +4 | **no measurable movement** — the guard held |
| `GOAL-apparatus-cut` | guard | flat, hazard: may ADD | `examples/validation/` **+182**, `scripts/` **0** | **moved the wrong way, as the plan warned** |
| `GOAL-consumption-obligatory` | enabling | none | `N/A` — CA-05 owns the disposition work; it now has a dispatch path and a stated bound on what that path buys | `N/A` |

### `GOAL-apparatus-cut`, priced honestly

| surface | epic base | CA-01 tip | delta |
|---|---|---|---|
| `scripts/` | 27,652 | 27,652 | **0** |
| `examples/validation/` | 15,901 | 16,083 | **+182** |
| combined | 43,553 | 43,735 | **+182** |

All 182 lines are `examples/validation/instruments/blind_dispatch.py`.
**The epic must absorb this inside its 30% cut** (target ≤30,487), or delete the
instrument once `CA-08` has used it. `references/blind_dispatch.md` is prose and
is not counted by the goal's command — said plainly so the table is not read as
the total cost. **The card is untouched.**

**Not counted by the goal's command, and disclosed anyway:** a `[[instrument]]`
row in `examples/validation/instruments/instruments.toml` (+57 lines of TOML).
It is not optional and it is not bookkeeping. `test_the_named_instruments_are_all_enumerated`
**derives** the instrument set by walking the tree for executables, so shipping
`blind_dispatch.py` without a row would have introduced a **new suite red** —
exactly what `GOAL-four-results-stand` clause (b) forbids doing silently. The row
declares a real failing input, a real passing input, and a **declared blind
spot**: this instrument reads a self-report, so a judge that received the memory
and simply did not mention it passes the check. Both demonstrations reproduce:
`python3 examples/validation/instruments/demonstrate.py --only blind-dispatch-check`
→ `fail ok / pass ok`.

`CA-01-DF-04` offers a route to give the 182 lines back: the leak was the session
cwd, not the worktree, so a judge dispatched from a session rooted in the ticket
worktree would already have missed the auto-memory at zero cost. **That arm was
not measured and is not claimed.**

---

## 5. The suite, with its tree

Command — this one, not `README.md:35`:

```
uv run --with pytest --with pyyaml -m pytest tests -q
```

```
12 failed, 1554 passed in 1282.63s (0:21:22)
```

`goal/CA-01-suite.txt`, on `feature/CA-01` at the tree described above.

**An earlier full-suite run was DISCARDED, explicitly.** It was started before
this ticket's files existed and ran while they were being written, so its reds
could not be attributed to any one tree. Discarded rather than reported; the
figure above is a clean run on the finished tree.

### Attribution — none of the 12 is CA-01's

**Six are the epic base**, measured by the epic owner at pristine `08d1d6a` in an
isolated detached worktree:

| test | at base |
|---|---|
| `test_architecture_tags::test_the_same_tag_control_holds` | deliberate red 1 (`RM-06-DF-01`) |
| `test_price_removal::test_nothing_in_the_repository_invokes_the_pricer` | deliberate red 2 (the pricer grep) |
| `test_source_citations::…[specs/current/spec_manifest.yaml]` | **inherited, undeclared** |
| `test_source_citations::…[specs/desired_program_model/spec_manifest.yaml]` | **inherited, undeclared** |
| `test_source_citations::…[specs/program_model/spec_manifest.yaml]` | **inherited, undeclared** |
| `test_ticket_retirement::…_has_matching_close_receipts` | **inherited, undeclared** |

**THE RECORD UNDERSTATES THIS.** The charter and the goal baseline say *two
deliberate reds plus a third undeclared one found last epic*. There are **at
least four undeclared inherited reds at the epic base**; `SV-02` and `SV-01` each
found one of them. **Epic owner's finding, not this ticket's.**

**Six are outside that list, and the epic owner is checking them** — exactly the
suspects already identified as passing at base and failing at the kickoff tip:

```
test_goal_baseline_is_a_card::test_a_real_epic_plans_judged_baseline_cannot_be_re_opened
test_instrument_demonstrations::test_every_fast_demonstration_reproduces
test_score_tools::test_a_refuted_finding_stays_on_the_record_with_its_filing
test_score_tools::test_the_shipped_rh5_demonstration_still_goes_red
test_score_tools::test_the_repo_ledger_passes_its_own_audit
test_score_tools::test_the_repo_ledger_passes_its_own_audit_with_rh6
```

**Not claimed as CA-01's, and not repaired.**

### The one CA-01 had a real reason to suspect of itself

`test_every_fast_demonstration_reproduces` runs `demonstrate.py --tier fast`, and
this ticket **added an instrument to that tier**. Checked rather than assumed.
From the failure output:

```
scorecard-audit                    MISS   MISS   skip   demonstrated-can-fail
scorecard-contested-drift          MISS   MISS   -      demonstrated-can-fail
blind-dispatch-check               ok     ok     skip   demonstrated-can-fail
```

**The missers are `scorecard-audit` and `scorecard-contested-drift`. CA-01's
instrument is green in the same run.** Two further pieces of evidence point the
same way: the test failed identically in the discarded run, when this ticket's
registry row **did not exist at all**; and `test_the_named_instruments_are_all_enumerated`
**passes**, which is exactly what the registry row was added to keep true.

### `denominator_rule`

```
discarded run   12 failed, 1550 passed   (1562 collected)
this run        12 failed, 1554 passed   (1566 collected)
```

**The numerator did not move. The denominator rose by 4**, and the four added
cases are green — they come from this ticket's `instruments.toml` row entering
the registry's own parametrized coverage. Stated because "12 of 1566" quoted
against "12 of 1562" would otherwise read as an improvement that did not happen.

### The baseline comparison the goal asks for still could not be made

`GOAL-four-results-stand/baseline.md` reads `*(pending)*` on
`origin/epic/cut-the-apparatus` at close (re-checked after `git fetch`; tip still
`87a526b0`). **`CA-08` owes the comparison.** This ticket declines to substitute a
recollection for the figure the charter says to compare against. The epic owner's
six-red base measurement above is the nearest thing available, and it is **a
subset of the suite, not the suite figure**.

---

## 6. What CA-01 REJECTED

- **Rejected editing `MEMORY.md`.** It is the leak and it is also the record.
  Proposed as a diff, escalated, not applied.
- **Rejected `Explore` as a blinding mechanism**, despite it being the cheapest
  result in the ticket and the one that would have let this close with no new
  apparatus at all. Undocumented differential behaviour, measured once.
- **Rejected claiming blindness.** The path buys blindness to our conclusions.
  Saying more would repeat the exact error the ticket was opened to correct.
- **Rejected adding a gate.** Seven epics, zero bugs caught by a static check.
  `check` refuses a *report* and prints why; it blocks no promotion.
- **Rejected hand-writing the leak needles.** They are derived at run time from
  the live memory index and commit log. A detector fitted to known answers is
  `MF-020`.
- **Rejected claiming `--safe-mode` works.** Plausible, undocumented for
  auto-memory, and **not measured**. Recorded as unmeasured rather than assumed
  in either direction.
- **Rejected reporting the four probes as one number.** Three leaked and one did
  not; "4 of 4" would have matched the predecessor and been wrong.
- **Rejected repairing the instrument's defect silently.** Pointed at the ticket
  worktree, `check` derived zero memory needles and would have returned a hollow
  pass. Fixed, and the fix is written down in `references/blind_dispatch.md` §4
  as what running on a real subject bought.
- **Rejected quoting four identical copies of the skill listing** into the
  evidence. Abridged, and the abridgement is declared in `INVENTORY.md` §7 rather
  than passed off as a complete transcript.

---

## 7. What this result does NOT establish

- **It does not establish that any published number is wrong.** `SV-05-DF-02`'s
  scope holds unchanged.
- **It does not establish that a `PASS` means the agent knew nothing.** A pass is
  silence about 27 specific needles, with `CA-01-DF-01` standing beside it.
- **It does not establish the `Explore` tier's rule**, only its effect, once.
- **It does not establish that the neutral cell is the best path** — only that it
  works and what it costs. `--bare` may be strictly better and was untestable.
- **One example, one harness version, one machine.** `R-H1`/`R3`: this is a claim
  about Claude Code 2.1.231 on this operator's configuration, not about agent
  harnesses.
