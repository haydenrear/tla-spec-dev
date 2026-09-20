# SI-16 — what was run, and what each run establishes

Every number below was read from the run's own output. No claim here rests on
an exit code taken through a pipe, and no claim rests on an eval score.

## Repository unit suite — compared by NAME against the base

The assignment's `repository_unit` command, run twice: once in this worktree,
once in a throwaway worktree at the ticket's base `571aad99`.

| | failed | passed | skipped |
|---|---|---|---|
| base `571aad99` | 10 | 1704 | 7 |
| this branch | 10 | 1707 | 7 |

**The ten failure NAMES are identical in both runs** — architecture_tags,
corpus_diagnostics, example_drivers_write_inside_spec_tree,
instrument_demonstrations, negative_corpus_adapter_conformance,
source_citations (x3 parameterised), ticket_retirement, verdict_schema. So this
ticket introduces no failure; all ten are pre-existing and none touches the
migration.

The **+3 passed** is not noise and is worth naming: `test_plugin_layout_resolution`
parameterises over the contained skills it discovers, and this ticket takes that
population from 8 to 11 (`skt`, `skill-manager`, `unit-authoring`). Those three
new cases PASS, which is the evidence that no executable resolves the three new
contained skills at the standalone rung only — the regression class SI-11 left
that test behind to catch.

## skt's own suite

`uv run --python 3.12 --with pytest python -m pytest skills/skt/tests -q`
→ **307 passed, 3 skipped**, process exit 0 captured directly (not through a pipe).

One genuine breakage was found and fixed here: `tests/test_artifact_notify.py:491`
resolved `parents[1]/"hooks"/"skt-post-tool.sh"`. It is a hook path that never
spells `CLAUDE_PLUGIN_ROOT`, so the issue's "exactly 10 references" could not
see it (SI-16-DF-01).

## Unit manifests

`skills/skt/.github/scripts/check_units.py` → **47 unit declarations checked,
all valid**, including the three newly contained skills and the plugin identity
(`.claude-plugin/plugin.json` and `skill-manager-plugin.toml` agree on
`tla-spec-dev` / `0.1.0`; skt's own 0.8.2 plugin manifests were deleted).

Two markdown skill-import violations are reported by `install` and both are
**pre-existing eval fixtures that are malformed on purpose** — neither appears
in this ticket's diff. `w-giw-exit6-is-unreadable-frontmatter` is a case whose
whole subject is unreadable frontmatter.

## Spec unit tests

`... run spec-unit-tests --ticket SI-16` exits 1 with 7 failed / 49 passed in
`specs/current`. At base the same tests fail **9**, and this branch's 7 are a
strict SUBSET of those 9. No new spec-unit failure. `specs/` was not modified by
this ticket.

## Test graphs

`sktSurface` and `sktHooks` merged into the carrier's one `test_graph` project
(5 skt sources + 2 support modules; path overlap with the carrier's 12 sources
is zero, as the issue stated, re-measured here). All 20 node references in
`build.gradle.kts` resolve to files on disk.

Both are classified **OPT-IN**, not RUN, and `run-graphs.py --list` prints the
reason: they provision a pinned CPython 3.11/3.13 matrix through uv, and
`skt.wrapper-installed` declares `side_effects("fs:tmp", "net:external")`.
Making them RUN would put a network fetch on this repository's default graph
front door. They were **not executed here**, so they are UNDECIDED rather than
green — stated rather than implied.

## Hooks

See `hook-evidence.md` and `hook.log` beside this file. Verified by the log, as
the ticket requires; an eval run does **not** exercise the shipped hooks
(SI-16-DF-02).

## Boundaries

- Root home `/Users/hayde/.skill-manager` NOT modified: `plugins/` listing and
  `plugins/skt` mtime identical before and after every step, including two
  fresh-home installs.
- `skills/git-issue-workflow/scripts/wt` NOT modified (SI-17 owns it) — empty
  diff against base.
- The `skill-manager` REPOSITORY was not touched (SI-18 owns it). The ten files
  under `skills/skill-manager/` in this diff are the CONTAINED SKILL that skt
  carried in and that this ticket re-homed; that is a different thing from the
  skill-manager repository.
- Home close-out: this worktree has **no** `.skill-manager`. It was created with
  `git worktree add` by hand, because the front door was broken at dispatch
  (SI-16-DF-00), so no ticket-local home was ever bootstrapped and there is
  nothing to close out.

## Fresh-home install, and the front door

Installed from `git archive HEAD` into a home created empty for the purpose.
Logs: `fresh-home-install.log`, `front-door.log`.

| criterion | result |
|---|---|
| no standalone skt unit | `plugins/` = `tla-spec-dev` only; `skill-manager list` has no skt row |
| wrapper resolves the contained skill | `rel="plugins/tla-spec-dev/skills/skt/src/skt/cli.py"`, entrypoint exists |
| wrapper carries no absolute home path | absent |
| no `skill-script not found` for install-skt.sh | installer ran as `plugins/tla-spec-dev/skill-scripts/install-skt.sh` → `✓ cli: skt [skill-script] installed for tla-spec-dev` |
| front door works | `skt ticket new` exit **0**: worktree + branch + its own `.skill-manager` |

`skill-manager list` also shows `deploy-helm` and `tracing-observability`. Those
are NOT substrate units: they come from test-graph's legitimate external
`skill_references = ["github:haydenrear/deploy-cdc"]`, and they are unchanged by
this ticket.

`install` exits **11**, and that is not this ticket's doing: it reports two
markdown skill-import violations in eval FIXTURES that are malformed on purpose
(`w-skt-migration-no-import-edits` omits a `reason`;
`w-giw-exit6-is-unreadable-frontmatter` has invalid YAML, which is the entire
subject of that case). Neither file appears in this ticket's diff; both came in
with SI-15 at `9ba955b7`.

### What this took, and why it is worth recording

The first fresh-home install FAILED acceptance, and it is the only place the
defect could have shown. `skills/git-epic-workflow/skill-manager.toml` still
carried a hard `skill_references = ["github:haydenrear/skt"]`; install unions
every contained skill's references, so it cloned a SECOND standalone skt
(`skt plugin 0.8.2 git 0f38078`) beside the bundled one. Its installer ran
SECOND and overwrote `bin/cli/skt` with `rel="plugins/skt/src/skt/cli.py"` — the
pre-demotion path — after the carrier's own installer had already written the
correct one. The front door then failed on the bootstrap-rung defect that
standalone skt at `0f38078` still has.

So the unit suites, the hook log and the manifest checks were all green while
the shipped artifact was wrong. Fixed in `fd784cad`.
