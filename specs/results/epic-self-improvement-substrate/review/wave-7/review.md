# Wave 7 review — epic/self-improvement-substrate

Range: `5f7b6595` → `fd26a2b7`. One ticket: SI-13 (#360), PR #373 merged.
**A second PR, skill-manager #395, is OPEN and NOT merged** — it targets that
repository's default branch, which needs the owner's say-so.

Wave 7 is not a gate. Wave 8 (SI-14) may dispatch.

---

## Block 1 — Model delta applied

**None owed.** Files under `specs/` outside `results/` touched by SI-13: **0**.
No TLA+ action, state or invariant change. SI-13 reports `desired/` untouched —
not even a small edit — and ran no `open ticket`, `close ticket` or
`--accept-new`. Verified by file list across the merge range.

## Block 2 — Anchors placed

**None placed.** All five findings are validation-surface and tooling defects,
attributed `UNMODELED/`. None sits inside a `TlaSpecDevCli` action. Matrix
unchanged.

## Block 3 — Improvement-card row

**No round run.** Single implementation ticket; a row here would decide nothing
and spend judge budget SI-23 needs. Recorded for SI-23: PR #373 would score
strongly on I5 — it lists four things it could not verify, including that **25 of
26 skill-manager graphs were not executed by it**, and it volunteers that its own
header rewrite introduced a bug (below). That is the honesty dimension working.

## Block 4 — Skill changes applied or declined

| proposal | disposition |
|---|---|
| document the runner-vs-bare-gradle distinction (`test_graph/README.md`, `run-graphs.py`) | **applied** in #373 |
| the two `select-graph-set.py` parser defects | **applied** in skill-manager #395 — *not merged*, see below |
| put the materialiser into the ticket front door | **declined by SI-13, correctly** — `skills/**` is outside its `test_graph/**` keys and wave 7's successors edit those files. Proposed with rationale in its PR instead. **I am carrying it**, below. |
| `SI-12-DF-05`'s "track build-logic" | **declined permanently** — it would reintroduce what `175f5c7c` removed |

## Block 5 — Model corrections owed by merged tickets

**None outstanding.** Fourth consecutive wave clean on this debt.

---

## SI-13 corrected the epic agent, and the correction is mine to own

I told SI-09, in its dispatch, that *"the three test graphs CANNOT run in a
ticket worktree… do not report them as green or as your regression. Report them
unmeasurable."* **That was false.**

Verified by me, two ways:

- `skills/test-graph/scripts/_common.py:674` — `run_gradle()` calls
  `prepare_provider_bindings_or_warn(root)` before invoking Gradle.
  `discover.py:34` calls it too.
- **I ran `specWorkflow` through the skill runner in this worktree myself:
  `BUILD SUCCESSFUL in 1m 5s`, rc=0.**

So the graphs were runnable in a ticket worktree the whole time. What cannot run
is **bare `gradlew`**. My `SI-12-DF-05` diagnosis got the *remedy* right —
"track build-logic" would restore the absolute-home-path symlinks `175f5c7c`
deleted — and the *premise* wrong, by generalising from one failing invocation to
"cannot run at all".

**The cost:** five tickets were told something false, and **wave 6 has no graph
verification because SI-09 obeyed my instruction.** SI-12 reported its graphs
unmeasurable for the same reason. Waves 5 and 6 are weaker than they read.

**Corrected everywhere it propagated:** all eight issue bodies (#365–#372) now
say *run them through the skill runner, never bare gradlew*. Swept afterwards
with a non-vacuity assert over 8 issues: **zero stale phrasings, zero missing
corrections.** `SI-12-DF-05` should be closed as **answered**, not implemented.

This is the fifth consecutive wave in which my own verification was the defect —
and the first in which the false result travelled into other agents' work rather
than stopping at my own report.

## Verified, not accepted

| claim | how checked | result |
|---|---|---|
| 0 new failures | failure **NAMES**, suite run by me on the merged tip | 10 → 10, **same ten names** |
| graphs run via the runner | **I ran `specWorkflow` myself** | **BUILD SUCCESSFUL, rc=0** |
| `run_gradle` materialises bindings | read `_common.py:674` and `discover.py:34` | confirmed |
| territory | file list vs `test_graph/**` | 12 outside, all evidence + backlog; **0 `specs/` outside `results/`** |
| backlog delta | row count both sides | 69 → **74**, five new ids |
| the eight corrections landed | sweep with non-vacuity assert | 8 checked, 0 stale, 0 missing |

## What the wave produced

**tla-spec-dev: 3 registered / 3 run / 0 opt-in / 0 dead**, all passing in a
ticket worktree, each verdict read from its own `summary.json` rather than an
exit code. One command: `test_graph/run-graphs.py`.

**skill-manager: 30 distinct graphs**, not the 32 a naive grep returns — two
occurrences sit in comments and `hyper-experiments` registers a second time under
the same name in an `else` branch. 26 run / 4 opt-in / 0 dead, opt-ins named with
reasons in the command's output. The command **imports** the existing CI selector
rather than restating its exclusions, so there is one list.

## Where the bugs probably are

1. **25 of 26 skill-manager graphs rest on CI, not on SI-13's measurement.** It
   labelled them as such. One-day-old nightly CI is good evidence; it is not the
   same as a run anybody watched.
2. **"0 DEAD" is weaker than it sounds**, by SI-13's own admission: it rests on
   source files existing and 28/30 being green once. **A graph that runs and
   asserts nothing useful looks identical to a healthy one** — which is this
   epic's signature defect, one level up.
3. `SI-13-DF-03` — **the two products carry different versions of the test-graph
   skill.** SI-14 and SI-15 both cross that boundary and will trip on it.
4. `SI-13-DF-05` — four committed `case_coverage.json` files carry a
   **worktree-absolute path** (`wt-334-plugin-migration`), so any graph run
   dirties them. Reverted by hand, not committed. That is the same
   absolute-path-in-a-committed-file class as `175f5c7c`.
5. `fresh_report()` decides green vs UNDECIDED from an **mtime window** — a fudge
   that could misread a very fast graph on a coarse-mtime filesystem.

## What the owner is being asked to decide

**skill-manager PR #395 is open and unmerged.** It targets that repository's
`main`, and the standing instruction is that I never merge to a default branch
without explicit say-so. 5 files, +313/−12: the two `select-graph-set.py` parser
fixes, `run-graphs.py`, `README.md`, `build.gradle.kts` header, `CLAUDE.md`.

## Suggested next steps

**Wave 8 is SI-14 (#361)** — pin the eval toolchain, curate the plugin home.

**I am carrying the front-door change SI-13 correctly declined**: the ticket
front door should run the materialiser, or name the runner, so no future agent
repeats what I told five of them. That is epic-agent work in `skills/**`, and it
lands before wave 8 dispatches.

**Deferred findings: 74 rows.** `per_ticket_backlog` still unadopted. Waves 5–7
were single tickets so it cost nothing again — but SI-23 files against **six**
goals into this one file, and that is the run it collides on. I deliberately did
not adopt it mid-wave, because SI-13's live assignment named the shared file.
