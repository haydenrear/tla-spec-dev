# Waves 13–15 review — the substrate is measured, not asserted

Range: `b75672bf` → `0f2dc004`. Three tickets: SI-24 (#377, root-home rebuild,
done in the previous wave), SI-25 (#380) and SI-26 (#381, in progress). All
performed by the epic agent; no ticket agents were dispatched.

**This is the wave where the substrate stopped being described and started
being measured.** Five graphs have verdicts. Both CLIs were driven by hand.
Eight findings were filed, and one of them is a number I got wrong and caught.

---

## Block 1 — Model delta applied

**None owed.** No TLA+ changed. `specs/` changes are confined to
`specs/results/`, the manual transcripts, and `ticket_plan.yaml` status and
issue fields. No action, state or invariant moved, so no TLC re-check is owed.

## Block 2 — Anchors placed

**None placed.** All eight findings are harness, manifest or instrument
defects, attributable `UNMODELED/`.

## Block 3 — Improvement-card row

**No round run.** Neither ticket is an evaluation. The card next runs at SI-23.

## Block 4 — Skill changes applied or declined

| proposal | disposition |
|---|---|
| `run-graphs.py` printed every OPT_IN graph as NOT RUN unconditionally | **applied** (`ab99d575`) |
| `skt.status-tiers` fixture could never be `standalone` | **applied** (`ab99d575`) — fixture moved to a system temp dir |
| `case_coverage.json` carried an absolute worktree path | **applied** (`ab99d575`) — one writer, six records regenerated |
| `tlc-generation.json`'s `package` was stale | **applied** (`ab99d575`) |
| unanchored citation in my own comment | **applied** (`ab99d575`) — caught by the tripwire, not by me |
| `_resolve_giw` misses the contained rung (`SI-25-DF-06`) | **filed, not applied** — it is the graph node's, and the fix belongs with whoever owns the two-rung rule |
| `_giw_remedy` is unreachable (`SI-25-DF-07`) | **filed** — needs a decision about which refusal serves the reader |
| `verify.sh` scans build output (`SI-25-DF-08`) | **filed** — two other units own the two halves |

## Block 5 — Model corrections owed by merged tickets

**None outstanding.** Ninth consecutive wave clean.

---

## What actually landed

**All five graphs reach a stated verdict.** specWorkflow 9/9, cliWorkflow 2/2,
effectProviderExamples 1/1 and sktHooks 3/3 nodes (167 assertions, zero
failures) PASS. sktSurface is ERRORED on one node.

**Each graph appears exactly once**, and a run from a clean tree left
`dirty_count=0` — the runner's own check, not mine afterwards. Acceptance 1 and
3, measured.

**`skt.status-tiers` was fixture locality, and the ticket demanded that be
established BEFORE either side was changed.** It was: a fresh git repo inside
this worktree reports `kind=constituent`, the same repo in a system temp dir
reports `standalone`, because `checkout_kind` walks ancestors for
`integration.toml` and this repository carries one at its root. The assertion
was reporting correct behaviour against a fixture that could not produce the
answer it asked for. The neighbouring `orphan` fixture already documents this
hazard and avoids it with `tempfile.mkdtemp`; this one had never been given the
same treatment.

**The manual gamut found no product defects.** Every nonzero exit was either a
correct refusal that named its own next command, or my own invocation error.
Two of them were mine and are recorded as mine.

## The best thing the gamut found is a refusal

`bootstrap-home.sh` will not clone a worktree home from the global home:
*"A worktree home is a copy of its PROJECT home, and close-change.sh reconciles
it back into that same path. Cloning from anywhere else — the global home
included — makes this worktree unclosable from birth."* The failure it prevents
would not surface at `new`; it would surface at `close`, long after the cause
was forgettable. Both front doors refuse consistently and both offer a named
override.

## Five of the known ten are two defects that have nothing to do with the code

`SI-25-DF-04`: ONE citation defect set, triplicated across `specs/current`,
`specs/desired_program_model` and `specs/program_model` — 10 problems each, 30
total, accounting for three standing failures. One of the ten cites an anchor
that appears on **zero** lines, so `--fix` can never repair it.

`SI-25-DF-05`: two more guards protect
`examples/distributed_history/specs/generated`, deleted in `76ef2758` with a
`.gitignore` line added. Zero tracked files remain. The guards' own text says
*"the protection is now vacuous"*.

A baseline where half the entries are bookkeeping trains readers to ignore the
baseline.

## Verified, not accepted

| claim | how checked | result |
|---|---|---|
| no new suite failures | failure **NAMES** vs the recorded baseline | 10 → 10, unchanged |
| the baseline itself | four independently recorded artifacts | SI-02, SI-03, SI-05, SI-11 agree exactly |
| `_relative_source` works | ran the three real generators | 6 files, 1 line each, source only |
| status-tiers fixed | the graph, not a probe | node PASSES; no temp dir leaked |
| temp-dir cleanup | `find` with a **working** control | 0 leaked against 11 control dirs |
| root home intact | `skt status` from a NEUTRAL cwd | tier root, 11 units, no standalone skt |
| graph leaves tree clean | the run's own `git status` | `dirty_count=0` |
| `skt.wt` imports | imported it from the installed plugin | OK — so `_giw_remedy` is dead code |
| the 297 frontmatter imports | scoped to the section, resolved each path | **zero tracked** — the finding was wrong |

## My verification failed six times this wave, and the controls caught all six

- A `ps` on an already-exited PID read as "blocked on the network" — it had
  simply exited. I declared the suite hung; it was not.
- Two adjacent parent-CPU samples read as "no movement"; the work was in
  short-lived children flickering in and out.
- `grep --include=*.py` unquoted — zsh ate the glob and the shell error read as
  "nothing generates this file".
- `-maxdepth 3` too shallow to reach any temp dir, so "0 leaked" meant nothing.
  The non-vacuity control reported 0 control dirs too, which is what exposed it.
- An assertion dump printed `FAIL None` 39 times because I guessed the keys;
  the real ones are `name`/`status`. I nearly reported 4 failures when there
  were 13.
- **"193 tracked files" for the frontmatter finding.** The grep swept the whole
  report instead of the section. Correctly scoped: 115 files, **zero tracked**.
  Filing it would have sent someone hunting 297 imports in a tree with none.

Every one was caught by a control or a second look. **None was caught by
reading the output.** That is the ninth consecutive wave where that sentence is
true, and it is the reason the controls are non-negotiable.

## Suggested next steps

**SI-26 is substantially complete** — both CLIs, both ticket systems, both
worktree front doors, the workflow scripts, and the dirty-tree guard in both
directions, all with transcripts. What remains is `skt publish` against a real
edited unit, which mutates a home and should be done deliberately.

**SI-18 is ready to dispatch.** The handoff is at
`specs/results/epic-self-improvement-substrate/handoff/SI-18-skill-manager.md`.
It carries the seven `target: skill-manager` findings, the two-rung resolver
fix with two working examples to copy, the correction that skill-manager's 30
graphs name skt **zero** times, and the traps that cost this epic hours.

**Two eval defects still block any scored run**: `SI-16-DF-02` (the runner
overwrites the plugin's now-real `hooks.json`) and `SI-16-DF-03` (nesting
retired the skt pin). The staging ceiling — 28,603 entries against a 20,000
limit — is also unresolved.
