# Worktree and home lifecycle

An epic creates a worktree per ticket plus one for itself, and every one of them
carries a `<worktree>/.skill-manager` — a real copy of the project home, not a
symlink (SKILL.md rule 10). Two different things therefore have to be settled
before an epic can close, and they run on **different clocks**:

| | Clock | Owner | Failure if you get it wrong |
| --- | --- | --- | --- |
| The **unit state** in each worktree's home | merge it **early**, at wave close | epic agent | work vanishes silently, and nobody notices for weeks |
| The **worktrees** themselves | remove them **late**, all at once at epic end | epic agent | the machine fills up |

Both belong to the epic agent. The ticket agent cannot own either: it cannot see
its siblings, so it cannot serialize a write into the one shared project home,
and it stops at `pr_open` while its worktree still has to exist for review.

This reference covers why the clocks differ (§1), what the ticket agent owes
(§2), reconciling a wave's homes (§3), the ledger that makes deferred removal
safe (§4), the end-of-epic sweep (§5), bringing the sweep forward under disk
pressure (§6), and what is never allowed (§7).

## 1. Why merge early and delete late

**Merge early**, because a home reconciliation is a *reading* problem. `home
sync` reports a unit the destination also changed as `held-back` (or
`conflicted` under `--merge`) rather than overwriting it, and somebody has to
decide what that means. At wave close there are one or two of those and the
ticket's author is still reachable with a PR body that says what they changed
and why (`epic-ticket.md`, `## Review input`). Deferred to finalization, every
worktree's held-back units arrive at once, in the hour you are also promoting a
model, draining a backlog, and deciding goals — and the authors are long gone.

**Delete late**, because removal is the irreversible step and review is not over
until the epic is. A worktree standing after `pr_open` is the review model
working as designed: the reviewer can check out what the agent actually did, and
the agent can be sent back to reconcile a conflict.

**But deleting late means the disk carries every worktree at once, and the cost
is not the one it looks like.** Get the arithmetic right before you plan around
it, because both of the obvious numbers are wrong in opposite directions.

A home is cloned **copy-on-write**, so a fresh worktree home is nearly free. On
APFS, `home clone` takes the `clonefile(2)` path and the copy shares the
source's blocks. Measured on this skill's own project home: `du` reports
**1.1 GB**, and cloning it moved free space by **33.7 MB — 3.1%**. That agrees
with `git-issue-workflow`'s `references/skill-homes.md`, which measured 3.8% on
a different home and states the trap outright: **do not measure this with `du`**,
which attributes shared blocks to both copies. Ten ticket worktrees are not ten
project homes.

What *does* cost real space is everything that stops sharing:

- **per-home install targets** — `<home>/venvs`, `bin/cli`, `npm/`, `pm/`,
  `cache/` are private by design, and they are where the gigabytes are. The same
  reference measured three skill-script venvs in one home at 48,258 files across
  48,258 distinct inodes, **1.6 GB with zero sharing**;
- **divergence** — every unit a worktree syncs, installs, or edits writes new
  blocks that share nothing with the home it came from. A worktree that ran
  agents for a week is not the cheap clone it started as;
- **the checkout itself** — the repository's tracked files, once per worktree.

So a standing worktree starts nearly free and gets expensive in proportion to
how much work happened in it, which is exactly backwards from "delete the old
ones first" intuition. Two consequences for the sweep:

1. **Measure with free space, not `du`.** `du -sh` over a fleet of per-checkout
   homes reports a number tens of times larger than what removing them returns —
   the same trap, at fleet scale. Report `df` before and after, not a `du` total.
2. **Sweep anyway.** The residue is real even when it is smaller than `du`
   claims, it accrues across epics rather than within one, and a machine that
   runs out of space mid-epic loses the wave it was running, not just the disk.

So: reconcile at every wave close, keep every worktree until the end, then
remove all of them in one deliberate sweep — and never let the removal be the
step that carries the merge. That ordering is the whole design. `git worktree
remove` deletes a home without asking and succeeds exactly as quietly whether it
held a week of skill edits or nothing.

## 2. What the ticket agent owes, and what it must not do

The ticket agent, before it stops at `pr_open`:

- commits and pushes **everything** it wants kept — evidence under the ticket
  evidence root, backlog entries, close history, the lot;
- runs the read-only gate and states the verdict in the PR body:

  ```bash
  skill-manager home close-out --home <worktree>/.skill-manager \
                               --into <main-working-tree>/.skill-manager --json
  ```

- names, in the PR's `## Review input` → *Machinery friction* list, every unit
  it changed inside its own home and why. That list is the epic agent's input
  for §3, and for a unit whose improvement should reach other repositories it is
  the only surviving statement of intent;
- may run `skill-manager unit publish <unit> --ticket <ticket>` for its own
  edits — publishing goes to the unit's own git repository, contends with
  nothing, and the author knows the change best.

It must **not** run `home sync` into the project home. That is a write to one
shared destination from a process that cannot see the other tickets; two of them
racing is exactly the case the epic agent serializes in §3. It must also not
remove its own worktree, its branch, or anything under another worktree.

## 3. Reconcile the wave's homes into the project home

Do this at wave close, immediately after merging the wave's ticket PRs and
before the review artifact is written — the reconciliation result is one of the
things the review reports.

`close-out` writes nothing, so audit every worktree in any order, concurrently
if you like:

```bash
git -C <repo-root> worktree list --porcelain | awk '/^worktree /{print $2}'

skill-manager home close-out --home <worktree>/.skill-manager \
                             --into <main-working-tree>/.skill-manager --json
```

Two details that decide whether the verdict is about the right two homes:

- **`--into` is the *main working tree's* home**, the one the worktree's home was
  cloned from — not `$PWD`'s nearest git toplevel, which from inside the epic
  worktree names that worktree's own home instead. `close-change.sh` resolves it
  with the same `project_home` helper `bootstrap-home.sh` uses, for exactly this
  reason (`git-issue-workflow`'s `references/skill-homes.md`).
- **Run the home's own CLI, not a bare `skill-manager`.** An older release first
  on `PATH` exits 2, which reads as a failure of your worktree rather than of
  your `PATH`. The pin is `<home>/bin/cli/skill-manager`; the remedies
  `close-out` prints already name a resolved path — use the one it printed.

Read the verdict rather than the exit code alone. `complete.md` §6a in
`git-issue-workflow` documents the full set, and two are easy to misread: **exit
2** means the path you passed `--home` is not a home at all (usually the
worktree directory instead of its `.skill-manager` — the same path
`git worktree remove` takes, so this exit is all that stands between a typo and
a "safe" verdict about the wrong directory), and **exit 9** means the
destination's policy is `frozen`, so nothing was assessed. Neither is "this
worktree is clean".

Then, **one worktree at a time**, reconcile the ones that reported work. The
sync writes the project home; several of them at once do not merge, they race:

```bash
skill-manager home sync --from <worktree>/.skill-manager \
                        --to <main-working-tree>/.skill-manager --merge
```

Read the result rather than the exit code alone:

- **`safe: true` / nothing to sync** — record it and move on.
- **synced** — record the units that moved up a tier.
- **`held-back`** (or `conflicted` under `--merge`) — the project home has its
  own version of that unit, usually because an earlier worktree in this same
  wave already reconciled it. This is the designed outcome, not a failure, and
  it is **a decision, not a retry**: read both versions, take the merge that
  keeps both improvements, and say in the wave review which ticket's edit won
  and why. Serialization prevents overwriting; it does not choose for you.
- **a `close-out` blocker** — the entry names the unit, its status, and the
  literal remedy. Do not guess between the two remedies:

  ```bash
  # up a tier: survives teardown, stays on this machine
  skill-manager home sync --from <worktree>/.skill-manager \
                          --to <main-working-tree>/.skill-manager --merge

  # to the unit's own git repo: the only route that reaches another project
  skill-manager unit publish <unit> --ticket <ticket>
  ```

  A blocker cleared by the wrong remedy is an improvement that reaches this one
  project home and nowhere else, forever. When the PR's *Machinery friction*
  list does not say which was intended, ask the ticket's author or the user
  before clearing it — the epic agent owns that the change is *managed*, not
  that it is guessed.

Then confirm nothing else is stranded in the worktree. `.skill-manager` is
gitignored, which is why the gate above exists; these four checks cover
everything git *can* see:

```bash
git -C <worktree> status --porcelain                       # uncommitted
git -C <worktree> stash list                               # stashed
git -C <worktree> log --oneline @{u}..                     # unpushed
git -C <worktree> log --oneline origin/epic/<slug>..HEAD   # not in the epic branch
```

A non-empty result on any of them is work the sweep in §5 would destroy. Return
it to the ticket's author; do not commit another agent's uncommitted tree
yourself, and do not merge from a ticket branch by hand — that path is
`epic-ticket.md` §5 and it belongs to the ticket.

Record every verdict in the ledger (§4) as you go. A worktree reconciled at wave
2 and used again at wave 4 has to be reconciled again, which is why §5 re-runs
the gate immediately before each removal rather than trusting this pass.

## 4. The worktree ledger

Deferred removal is only safe if the epic knows, at any moment, what is standing
and what is still holding unmerged work. Keep that in one committed file under
the review artifact root, updated at every wave close:

```
results/epic-<slug>/review/worktrees.md
```

One row per worktree, including the epic's own and including tickets that were
retired or never delivered — those still hold a home and still occupy disk:

| Worktree | Ticket | Branch | PR | Merged into epic | Home reconciled | Unmerged work | Size | State |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

- **Home reconciled** — `nothing to sync`, `synced <units>`, `held-back <units> (resolved: ...)`, or `published <units>`, with the wave it happened in.
- **Unmerged work** — the §3 checks, or `none`.
- **Size** — `du -sh <worktree>` is fine as a *relative* ranking of which
  worktrees diverged most, and is the reason to sweep them in that order. It is
  not the space you will get back (§1); record the free-space delta from the
  sweep itself for that.
- **State** — `standing`, `reconciled`, `removed`, or `retained: <reason>`.

Check the headroom the schedule assumes while you are there, and say so in the
wave review when it is thin:

```bash
df -k <repo-root>          # the only honest headroom number
```

## 5. The end-of-epic sweep

Run the sweep **after** the epic PR has merged and the default-branch merge is
verified (`finalize.md` §5) — not before. Until then a worktree may still be
needed to answer a review question.

Sweep from the primary checkout, never from inside a worktree you are removing,
and take the epic's own worktree last.

For each row in the ledger:

1. **Re-run the gate immediately before the removal.** The §3 pass may be waves
   old and the worktree may have been used since. This is not belt-and-braces;
   it is the only check that runs against the state that is about to be deleted.
2. **Re-run the four git checks** from §3. Uncommitted, stashed, unpushed, or
   epic-unmerged work stops that removal and only that removal — carry on with
   the rest and report the one you left standing.
3. **Remove through the door that runs the gate for you**, which refuses (exit
   4) rather than removing on a dirty verdict:

   ```bash
   skt ticket close <ticket>

   # where skt is not installed, the same door by its resolved path
   "${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/git-issue-workflow/scripts/wt" \
     close <ticket>
   ```

   Which one: `test -x "${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/bin/cli/skt"`.
   skt is a PLUGIN — it is never under `skills/`, so listing that directory
   answers wrongly. Falling to the second line because the first was not
   *found* is a front-door defect to report (`SKILL.md` rule 10, *Reaching that
   by-hand pair is itself a finding*); falling to it because skt is genuinely
   absent is not.

   Both resolve a ticket by searching, so a hand-made `../wt-<issue>-<slug>` is
   found. If you need a flag they do not forward, the two steps they wrap keep
   the `&&` — on separate lines the removal runs whatever the gate returned,
   which is the exact loss the gate exists to prevent:

   ```bash
   skill-manager home close-out --home <worktree>/.skill-manager \
                                --into <main-working-tree>/.skill-manager \
     && git -C <repo-root> worktree remove <worktree>
   ```

4. **Update the ledger row to `removed`** with the reclaimed size.

Then finish the sweep:

```bash
git -C <repo-root> worktree prune          # drop stale administrative entries
git -C <repo-root> worktree list           # expect the primary checkout alone
git -C <repo-root> branch --merged epic/<slug>
df -h <repo-root>
```

Delete a local ticket branch only after its worktree is gone — git refuses while
a branch is checked out in one — and only when it is merged. Leave remote
branches to the repository's own policy; the merged PRs hold that history either
way.

**Report the sweep**: worktrees removed, space reclaimed (before and after),
anything retained and why. An epic is not finished while a worktree it created
is still standing without a recorded reason. That is the whole point of doing
this at the end and in one pass — the sweep is the moment the epic's disk cost
goes back to zero, and an epic that skips it has simply moved its cost onto the
next epic, which will be the one that runs out of space.

## 6. When disk pressure will not wait

The default is to keep every worktree to the end. Disk pressure is the one
reason to bring a removal forward, and it does not license a shortcut around any
gate. A delivered ticket's worktree may be swept early when **all** of these
hold:

- its PR is merged into the epic branch;
- its home has been reconciled per §3, and re-checked immediately before removal;
- the four git checks are clean;
- the ledger row records the early removal and why.

Sweep in the order that buys the most space for the least review risk: the
oldest fully delivered tickets first, the epic worktree never.

If the pressure is severe enough that the *next wave* cannot be scheduled, say
so to the user with the numbers (`df -h`, the per-worktree cost, the count of
standing worktrees) instead of quietly removing more than the rule above allows.
Reducing the wave width is also an answer, and it is the user's call.

## 7. Never

- Never `rm -rf` a worktree. It skips the home gate and every other check; the
  gate exists because the home is invisible to `git status`.
- Never use `wt close --force` (or `close-change.sh --force`) to finish an epic
  faster. It still runs the gate and still prints every blocker — it only
  declines to stop, and it states that the work is being discarded. It is for a
  deliberate, named discard, not for a sweep in a hurry.
- Never let a ticket agent sync into the project home, and never run two syncs
  into it at once.
- Never treat `held-back` as success, a merged PR as proof the home was
  reconciled, or a clean verdict recorded in a PR body as a substitute for
  re-running the gate before removal.
- Never remove a worktree holding uncommitted, stashed, unpushed, or
  epic-unmerged work without the user's explicit decision to discard it.
