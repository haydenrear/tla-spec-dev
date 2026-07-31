# Runtime Requirements

This reference describes the runtime tools the installed skill expects. It is
not an installation guide; in normal use the skill has already been installed
and these dependencies are provided through its `skill-manager.toml`.

Declared CLI dependencies:

- `jinja2`
- `pytest`
- `tlc2`
- `tla-spec-dev`

The `tlc2` wrapper is installed by `skill-scripts/install-tlc2.sh`. It downloads
the TLA+ tools jar from the TLA+ GitHub releases at install time and requires a
local Java runtime.

The `tla-spec-dev` wrapper is installed by
`skill-scripts/install-tla-spec-dev.sh`. It wraps `scripts/tla_spec_dev.py`
(the spec-workflow CLI: scaffold, open, run, analyze, close) and requires a
local `python3`.

Repository scripts are intentionally plain Python where possible. Some tests
and examples require `pytest`; TLC case generation requires `tlc2`.

## Which Skill Manager home those tools come from

There is no single Skill Manager home. A machine has up to three tiers, and each
one is a **real copy** of the one above it, not a symlink:

```
root       ~/.skill-manager              where the operator installs
   |  copy
project    <repo>/.skill-manager         one per repository, gitignored
   |  copy
worktree   <worktree>/.skill-manager     one per ticket, gitignored
```

The copies are deliberate. A symlink farm makes the child and the parent the
same bytes, so two ticket worktrees editing "their" `tlc2` wrapper, their
`spec-double-compiler`, or their generated cases are editing each other's. This
skill is a heavy user of that: a spec workflow writes generated cases, evidence,
and `specs/.history` entries, and two tickets doing it at once through one shared
home interleave.

So **`tlc2`, `pytest`, `jinja2` and `tla-spec-dev` are not "the ones on PATH"**.
They are the ones in the home this checkout is bound to, and the wrappers are
generated shell scripts with that home's absolute path baked into the body — no
environment variable redirects them after the fact. Launch through the home's
`bin/launch/{claude,codex,gemini}` shims (or `skill-manager exec`) rather than
exporting variables by hand; the shims put this home's `bin/` first on PATH and
remove other homes' `bin/`, which is the part hand-exporting always misses.

Check which home answered before trusting a run:

```bash
skill-manager home describe --json     # the env, the resolved CLI, the unit snapshot
skill-manager home drift               # refuses a launch while a unit moved unread
```

### How a scaffolded module finds this skill

`tla-spec-dev` puts the installed skill on `PYTHONPATH` before it runs anything.
A Test Graph node, a bare `pytest`, or an IDE imports the same
`specs/program_model/adapters.py` with none of that. So the scaffold emits a
resolver into `adapters.py` and `providers.py`, and its order is load-bearing:

1. `SPEC_DOUBLE_COMPILER_HOME` — explicit override, names the skill directory
   itself. Set but wrong **refuses**; it does not fall through.
2. `$SKILL_MANAGER_HOME/skills/spec-double-compiler` — the home this launch is
   bound to.
3. the nearest enclosing `<checkout>/.skill-manager/skills/spec-double-compiler`,
   walking up from the module — so a project or worktree home is still found from
   a bare shell that exported nothing.
4. `~/.skill-manager/skills/spec-double-compiler` — **last**.
5. an inherited `PYTHONPATH` — only when **none** of the four above answered.

That order holds **unconditionally**, including when `spec_double_compiler` is
already importable. This is not a detail: the resolver originally ran only in an
`except ModuleNotFoundError` branch, which made every guarantee above void in the
one environment the paragraph names. Measured with two homes planted and distinct
markers — `PYTHONPATH` naming the operator's home, `SKILL_MANAGER_HOME` naming the
project's, and `SPEC_DOUBLE_COMPILER_HOME` deliberately pointing at nothing — the
operator's global home answered, exit 0, empty stderr, and the invalid override
was never even looked at.

Item 5 being last has one consequence worth stating plainly: when
`SKILL_MANAGER_HOME` and the `tla-spec-dev` you invoked name **different** builds
of this skill, the bound home wins. In the ordinary case they are the same
directory and this is a no-op. When they differ — a CLI wrapper pinned to another
home, an exported `PYTHONPATH` — the home the checkout is bound to is treated as
the authority, and `SPEC_DOUBLE_COMPILER_HOME` is how you override that.

`Path.home()` last is the whole point. A repository that resolves the global home
first reads a different build of this skill than the checkout was resolved
against, and from a ticket worktree it reads a home another agent is editing
right now. Repositories onboarded before this resolver existed hand-wrote
`Path.home() / ".skill-manager"` as their *first* fallback; if you find that
shape in a `specs/program_model/adapters.py`, it is a defect, not a convention.

### An edit you make to this skill inside a home is not in any diff

A home is gitignored. If you improve `spec-double-compiler` while using it —
inside `<worktree>/.skill-manager/skills/spec-double-compiler/` — the edit is
invisible to `git status`, invisible to the repository's diff, and deleted with
the worktree. Two commands move it, and they answer different questions:

```bash
# up a tier, so closing the worktree does not take it with it (local to this machine)
skill-manager home sync --from <worktree>/.skill-manager --to <repo>/.skill-manager --merge

# to this skill's own git repository, which is the only path that reaches another project
skill-manager unit publish spec-double-compiler --ticket <ticket>
```

`skill-manager home close-out --home <worktree>/.skill-manager --into <repo>/.skill-manager`
refuses while such an edit is still only in the worktree, and names the command
to run per unit. Run it before `git worktree remove`, never after.
