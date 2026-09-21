# SI-18 handoff — skill-manager adopts the unified plugin

**For an agent running in the `skill-manager` repository, in its own session.**
Issue: https://github.com/haydenrear/tla-spec-dev/issues/367 (issues live in
`tla-spec-dev`; all code work is in the plugin repo or in skill-manager).

## The one rule that is not negotiable

**PRs in the skill-manager repository target that repository's
`epic/self-improvement-substrate` branch, NEVER `main`.** Do not merge to main
and do not sync `SKILL_MANAGER_HOME` without the owner's explicit say-so.

## What changed under you

`tla-spec-dev` is now a single plugin containing **11 skills**: discovery,
git-epic-workflow, git-integration-repo, git-issue, git-issue-workflow,
plugin-repository, skill-manager, skt, spec-double-2, test-graph,
unit-authoring. **skt is no longer a plugin** — it is a contained skill of
that plugin, at `plugins/tla-spec-dev/skills/skt/`. Its hooks lifted UP to the
carrier plugin root; its `src/` moved DOWN into the skill.

The root home has been rebuilt from a recorded manifest and verified: 11 units,
plugins `andrej-karpathy-skills` and `tla-spec-dev`, and **no standalone skt**.
`github:haydenrear/tla-spec-dev` is the coord to use; the old `skt` plugin coord
and the `tla-spec-dev` *repository* are being retired.

## Your scope

1. **Delete the vendored skt copy.** `skill-publisher-skill/src/skt` and
   `skill-publisher-skill/skills/skt` were last touched by `chore: vendored skt
   0.3.0` and a bulk refresh. Canonical skt is contained in the plugin now.
   **Confirm that before deleting, then delete.**
2. **Teach the resolver the plugin rung.** `ProjectVendoredResolver` resolves
   ONE rung, and that is the same defect the front door had. A unit's bytes can
   be at `<home>/skills/<unit>/` OR `<home>/plugins/<plugin>/skills/<unit>/`.
   skt already does this correctly in two places you can copy:
   `skt/wt.py` (globs `plugins/*/skills/skt/scripts/wt`) and
   `skt/ticket.py::_bootstrap_script`, whose docstring explains exactly why the
   second rung is not optional.
3. **Stop `onboard` re-installing skt.** Onboarding installs skt today; after
   the migration that would reinstall the standalone duplicate the whole epic
   removed. This is the delicate part — take it carefully.
4. **Install the plugin and re-run skill-manager's test graphs**, which include
   skt coverage. **Re-measured against `epic/self-improvement-substrate` at
   `d2760141` (2026-09-20):** `test_graph/build.gradle.kts` registers exactly
   **30 graphs** — artifact-dag, browser-auth, checkout-home, doc-smoke,
   git-latest-source-tracking, harness-smoke, home-clone, home-integrity,
   home-sync, home-tripwire, home-verdicts, hyper-experiments, onboard,
   onboarding, password-reset, plugin-smoke, project-child-home, project-env,
   project-libs, project-manifest, project-profiles, project-resolve,
   project-smoke, refresh-flow, smoke, source-tracking, spec-conformance,
   sponsored, sync-settles, ticket-lifecycle — and **NOT ONE names skt**.
   `skt` appears twice in that file and both are COMMENTS (lines 591 and 1474).
   **0 of 299** files under `test_graph/sources/` have skt in their path. So
   "skill-manager's graphs already cover skt" is FALSE. Adding skt to its
   `skill-project.toml` is part of this work.

   Do not confuse `test_graph/` (skill-manager's own 30 graphs) with
   `skills/test_graph/` (the vendored test-graph skill, ~1,500 files). I did,
   briefly, and it inverted the conclusion.

## Seven findings already filed against skill-manager

Read these first; they are in `specs/results/deferred_findings_final.yaml`.

| id | severity | what |
|---|---|---|
| `SI-02-DF-04` | major | `skill-manager install file://<checkout>` stages the ENTIRE directory |
| `SI-11-DF-01` | major | resolves a `skill-script:` CLI installer by the INSTALLED UNIT's name, not the declaring skill's — this is what broke `tlc2` |
| `SI-06-DF-01` | minor | `GOAL-blockers-propose`'s declared local_signal was never rerun |
| `SI-13-DF-02` | minor | two parser defects in `.github/scripts/select-graph-set.py` |
| `SI-13-DF-03` | minor | the two products carry DIFFERENT versions of the test-graph skill |
| `SI-13-DF-04` | minor | `test_graph/docs/` has rendered DAGs for graphs that no longer exist |
| `SI-14-DF-02` | minor | `[plugins.<name>]` accepts `source` and nothing else |

## What is already proven working, so you can tell a regression from a known red

- All five plugin test graphs reach stated verdicts; four PASS.
  `sktSurface` is ERRORED on ONE node, `skt.ticket-roundtrip`, with two named
  causes: `SI-25-DF-06` (its `_resolve_giw` misses the contained rung and
  silently clones upstream main) and `SI-25-DF-07` (`_giw_remedy` is dead code
  because `skt.wt` now imports). **Neither is a skill-manager defect** — but
  DF-06 is the same single-rung bug you are fixing in the resolver.
- The repository suite has **ten standing failures, by name**, unchanged across
  SI-02, SI-03, SI-05, SI-11 and this wave. Compare NAMES, never counts.
  Three of the ten are one citation defect triplicated across three
  `spec_manifest.yaml` files (`SI-25-DF-04`); two more protect a corpus deleted
  in `76ef2758` (`SI-25-DF-05`).
- Both CLIs were driven by hand verb by verb against the rebuilt root home —
  transcripts in `specs/results/epic-self-improvement-substrate/manual/`.

## Traps measured in this epic, which will cost you hours

- **`skt check` exit 10 is `NOTIFY_EXIT` (`check.py:145`), not an error.**
- **`$?` after a pipe is the pipe's last command.** Capture exit codes directly.
- **Build output poisons repo-wide scans.** `test_graph/build` reached 328,508
  entries and 733 MB here; it has now taken suite tests red once and distorted
  `verify.sh` (`SI-25-DF-08`). Clear it before any scan, and never let a sweep
  enumerate anything but `git ls-files`.
- **A fixture created inside a repo that carries `integration.toml` can never
  be `standalone`** — `checkout_kind` walks ancestors. Put fixtures in a system
  temp dir.
- **An empty result is not a passing result.** Every zero in this epic that was
  read as good news was a broken search.

## When you are done

Report back here. The epic then validates that the rebuilt root home still
works, runs the eval ladder, and closes. `tla-spec-dev` the repository is
archived last, after the post-skill-manager work.
