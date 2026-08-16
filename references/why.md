# Why bundle skills into a plugin repository

This page is the argument, and it is the part of this skill that is not
mechanical. The mechanics are `git-integration-repo`'s; the decision — *which
skills belong in one bundle, and what that buys* — is here.

## The problem: one repo per skill makes change management N-shaped

`skill-manager` is happiest with **one unit per git repo root**. That is a good
rule for distribution and a bad one for *change*, because change does not
respect unit boundaries. A single real improvement routinely spans several
skills: a vocabulary rename, a script moving from one skill to another, a new
convention every sibling has to honour, a fix in a shared library plus the three
callers of it.

With one repo per skill, that one improvement costs:

- **N branches, N PRs, N reviews** — and reviewers see slices, never the change.
- **N pushes and N syncs**, each of which can fail or be forgotten separately.
- **A window where the store is incoherent.** Sync is per unit. Skill A lands at
  09:00 with the new convention and skill B lands at 14:00 still expecting the
  old one; every agent that starts a session in between runs a home that is
  internally inconsistent, and nothing in the model detects it.
- **N version notifications.** `skt check` tells the consuming agent five
  separate times that something is stale, with no statement anywhere of which
  five go together.
- **Per-agent judgment about ordering**, which is the worst cost, because it is
  paid by every consumer independently and each one can get it wrong.

None of these are bugs. They are what "N independently versioned units" means.

## The move: make the *bundle* the unit of change

A plugin repository keeps one-repo-per-skill for **authorship** and replaces it
with one-repo-per-bundle for **change**:

| | one repo per skill | plugin repository |
|---|---|---|
| Unit of review | one skill's slice | the whole change |
| PRs for a cross-skill change | N | 1 |
| Consumer pulls | N syncs, ordered by hand | 1 `sync <plugin>` |
| Atomicity | none — partial states are reachable | the merge commit is the boundary |
| Version notifications | N | 1 |
| Skill still has its own repo/history | yes | yes |
| Skill installable standalone elsewhere | yes | not from this bundle (see below) |

The parent's merge commit is the coherence boundary. Consumers never observe
half a change, because there is no version of the plugin in which half of it
exists.

## The substrate framing

Say it the way it actually gets used. An agent that carries a plugin repo has:

- **One artifact to reason about.** "What can I do here" is one unit's contents,
  not a set of independently drifting installs.
- **One artifact to change.** Self-improvement — the agent noticing its own
  instructions are wrong and fixing them — is a branch, a commit, and a PR
  against one repo. Not a coordination problem across five.
- **One artifact to pull.** The improvement arrives whole or not at all.

That is what makes it a *substrate* rather than a bundle: the skills stop being
things the agent has to assemble and start being a surface it stands on and can
edit in place.

And it makes a role possible that could not exist before: an **integrating
agent** that watches several plugin repos and their upstream skill repos, sees
the whole cross-bundle picture, and decides *when* a set of upstream skill
changes is coherent enough to be pulled into a bundle and cut as a version.
Under one-repo-per-skill that agent has nothing to act on — every skill is
already published, timing is whatever each consumer's sync happens to do. With
plugin repos, "when does this reach consumers" becomes an explicit, reviewable
decision that someone owns. `references/lifecycle.md` § *The integrating agent*
gives it a concrete loop.

### It has already happened once here

`skt` is the precedent, and worth looking at before designing a bundle. The
repo is still `github:haydenrear/skill-publisher-skill`; the installed unit is
now the **`skt` plugin**, carrying two contained skills — `skt` (orientation,
home tiers, publish, ticket lifecycle) and `unit-authoring` (formerly the
standalone `skill-publisher` skill) — plus `hooks/`, which is what pushes the
`SessionStart` status into every session and which no bare skill could ship.
Agents invoke them as `skt:skt` and `skt:unit-authoring`; nothing named
`unit-authoring` exists under `skills/` any more.

That bundle was assembled by hand. This skill is that move made repeatable, and
adds the half `skt` does not have: the contained skills keeping their own repos
and receiving the parent's changes back.

## What it costs

Be honest about these before bundling; two of them are irreversible-ish.

1. **Contained skills stop being separately addressable.** After the plugin is
   installed, `skill-manager install <contained-skill>` refuses, the skill is
   invoked as `plugin:skill`, and its bytes live at
   `plugins/<plugin>/skills/<skill>/`. Any consumer that wanted just one skill
   from the bundle now takes all of them.
2. **Store paths move**, so sibling skills that resolve each other as
   `$SKILL_MANAGER_HOME/skills/<unit>/…` break. See `layout.md` § *Store paths*.
3. **Two directions of git flow to keep straight**, and one of them
   (`refresh.sh`) is destructive. `lifecycle.md` exists because of this.
4. **The bundle's granularity becomes the consumer's granularity.** A consumer
   that needs one skill pays for all of them: install size, MCP/CLI dependency
   union, and every future change to any of them.

Cost 4 is the one that decides membership, which is the next section.

## Which skills belong in one plugin repo

Bundle when the answer is yes to most of these:

- **Do they change together?** Look at the last ten commits across the
  candidates. If cross-skill changes are frequent, the bundle is already how you
  work and the repos are just making you pay for it.
- **Do they share vocabulary or a library?** A skill that sources another's
  `lib.sh`, or that only makes sense once you have read a sibling, is a bundle
  member — the plugin makes the version skew impossible rather than merely
  documented.
- **Do consumers want all of them?** If every home that installs one installs
  the rest, the separate units are ceremony.
- **Would a broken pairing hurt?** Two units that must agree on an ABI (the
  `WORKTREE_LIB_ABI` check between `git-integration-repo` and
  `git-issue-workflow` is a live example) are describing a version-skew problem
  a shared version would delete outright.

Keep separate when a skill is genuinely general — many unrelated consumers,
changes rarely correlated with any bundle. A widely-used general skill dragged
into a bundle forces every unrelated consumer to take the bundle's other
members and its whole release cadence.

Rules of thumb: prefer **few, cohesive bundles** over one mega-bundle; a bundle
whose members never appear in the same PR is not a bundle, it is a folder. And
a skill can be a constituent of more than one plugin repo — it is just a repo —
though every bundle carrying it must fan its changes back to it, or they drift.

## Plugin repo or harness

They are not competitors along their whole length; the overlap is only the
"several units travel together" part.

| Need | Shape |
|---|---|
| Several skills version, install, sync and change as one thing | **plugin repo** |
| Ship hooks, slash commands, or agent definitions to the harness runtime | **plugin repo** (a bare skill cannot) |
| Bind doc-repo sources into a project's `CLAUDE.md` / `AGENTS.md` | **harness** |
| Named, listable, removable per-project instances | **harness** |
| Select which MCP tools an agent role exposes | **harness** |

So: when a harness's `units = [...]` is really "these five always go together",
that list wants to become a plugin repo, and the harness keeps only the
project-binding and instance parts — often shrinking to `units =
["github:owner/the-plugin-repo"]` plus its docs. When the harness has no docs
and no instances, it disappears into the plugin repo entirely, which can also
carry the `hooks/`, `commands/` and `agents/` a harness never could.

The migration is `migration.md`.
