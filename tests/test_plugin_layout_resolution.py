"""Every executable and every binding must find the toolchain under the plugin layout.

SI-02 nested five workflow skills plus test-graph into this repository as
CONTAINED SKILLS of the `tla-spec-dev` plugin. A contained skill's bytes land at
``<home>/plugins/<plugin>/skills/<skill>/`` — never at ``<home>/skills/<skill>/``,
which is where a standalone install used to put them and where most of this
repository's executables were written to look.

The reason this needs a test rather than a one-time sweep is that **every failure
in this class is silent**. A stale path does not raise: it resolves to nothing, a
loop finds no candidate, a `-d` test is false, and the caller takes its fallback
and reports success. SI-11 found three of them — `github-action.py` pinning
`TEST_GRAPH_SKILL_HOME` to the standalone rung, `provider-bindings.json` naming a
provider inside the gitignored home, and a `[[vendored]]` block whose declared
source could not exist — and not one of them had ever failed anything.

So the assertions here are about the SHAPE of resolution, not about whether a
particular run happened to work on the machine it ran on:

1. An executable that names the standalone rung for a skill this bundle contains
   must also name the plugin rung for that same skill. Two-rung resolution is the
   fix; a file carrying only rung one is the defect, whatever it resolves to
   today on a home that still has the retired standalone copy installed.
2. The Test Graph provider binding must name a provider inside this bundle, not
   one inside a Skill Manager home.

Both read tracked files only. Neither needs a home, a network, or an install, and
neither refuses: they are pytest assertions, so a violation is a reported failure
with the offending path quoted — there is no `sys.exit`, no non-zero process exit
of our own, and nothing here can block a promotion (GOAL-no-new-gates).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"

# Directories inside an executable tree whose contents are deliberately wrong.
# Test fixtures plant malformed paths on purpose — `test_provider_bindings.py`
# carries a misspelled `../.skill-manger/skills/test-graph` precisely so the
# loader's rejection can be observed — and scanning them would make this test
# fail on data whose whole job is to be invalid.
EXCLUDED_DIR_NAMES = {"tests", "__pycache__", ".pytest_cache"}

EXECUTABLE_SUFFIXES = {".py", ".sh", ".bash"}


def _contained_skills() -> list[str]:
    """The skills this repository ships as contained skills of the plugin."""
    return sorted(
        path.name
        for path in SKILLS_DIR.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def _executables() -> list[Path]:
    """Tracked executables in the bundle's script trees, fixtures excluded."""
    out: list[Path] = []
    roots = [SKILLS_DIR.glob("*/scripts"), SKILLS_DIR.glob("*/skill-scripts")]
    roots.append(iter([ROOT / "skill-scripts"]))
    for group in roots:
        for scripts_dir in group:
            if not scripts_dir.is_dir():
                continue
            for path in scripts_dir.rglob("*"):
                if not path.is_file() or path.suffix not in EXECUTABLE_SUFFIXES:
                    continue
                if EXCLUDED_DIR_NAMES & set(path.relative_to(scripts_dir).parts):
                    continue
                out.append(path)
    return sorted(out)


# A rung is only a rung when it is anchored on a HOME. `/skills/<skill>` on its
# own is not enough, and getting that wrong is not hypothetical: the first draft
# of this test flagged
#
#     ENTRYPOINT="$SKILL_DIR/skills/spec-double-2/scripts/tla_spec_dev.py"
#
# in skill-scripts/install-tla-spec-dev.sh, which is CORRECT — on the plugin rung
# skill-manager sets SKILL_DIR to the plugin root, so that path is inside the
# bundle and never touches a home at all. Requiring a home anchor is what
# separates "resolving a unit out of a home" from "walking the bundle's own tree".
_HOME_ANCHOR = r"(?:SKILL_MANAGER_HOME|ACTIVE_HOME|\.skill-manager|<home>)"


def _rung_patterns(skill: str) -> tuple[re.Pattern[str], re.Pattern[str]]:
    """Standalone and plugin rung spellings for one contained skill.

    Both are matched from a home anchor, with anything non-whitespace allowed in
    between so the many legitimate spellings all count: a closing quote
    (``"$ACTIVE_HOME"/plugins/*/skills/x``), a glob segment, or a literal plugin
    name (``.skill-manager/plugins/tla-spec-dev/skills/x``). The standalone
    pattern deliberately also matches a plugin rung — the assertion is only ever
    "if a standalone rung is present, a plugin rung must be too", so over-matching
    there costs nothing and under-matching the PLUGIN rung would raise a false
    alarm, which is the expensive direction.
    """
    name = re.escape(skill)
    standalone = re.compile(rf"{_HOME_ANCHOR}\S*?/skills/{name}(?![-\w])")
    plugin = re.compile(rf"{_HOME_ANCHOR}\S*?/plugins/[^/\s]*/skills/{name}(?![-\w])")
    return standalone, plugin


@pytest.mark.parametrize("skill", _contained_skills())
def test_no_executable_carries_a_standalone_only_rung(skill: str) -> None:
    """A file naming ``<home>/skills/<skill>`` must also name the plugin rung.

    This is the regression guard SI-11 exists to leave behind. It fails when an
    executable GAINS a standalone-only rung — the exact edit that produced
    `github-action.py:320`, which sat there through a 413-executable audit
    because nothing it broke was loud.
    """
    standalone, plugin = _rung_patterns(skill)
    offenders: list[str] = []

    for path in _executables():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if not standalone.search(text):
            continue
        if plugin.search(text):
            continue
        hits = [
            f"    {path.relative_to(ROOT)}:{n}: {line.strip()}"
            for n, line in enumerate(text.splitlines(), 1)
            if standalone.search(line)
        ]
        offenders.append(
            f"  {path.relative_to(ROOT)} names /skills/{skill} with no "
            f"plugins/*/skills/{skill} rung:\n" + "\n".join(hits)
        )

    assert not offenders, (
        f"{len(offenders)} executable(s) resolve the contained skill {skill!r} at "
        "the standalone rung only.\n"
        "A contained skill's bytes are at <home>/plugins/<plugin>/skills/"
        f"{skill}/, so this resolves to nothing in any home that installed the\n"
        "bundle as a plugin — and resolves to a RETIRED standalone copy in a home\n"
        "that predates the migration, which is why it can look fine locally.\n"
        "Add the plugin rung beside the standalone one. Two idioms that do not\n"
        "work, both measured in wave 2: brace expansion does not happen inside\n"
        'double quotes ("$HOME"/{skills,plugins/*/skills}/x matches nothing), and\n'
        "`ls -d ... | head -1` sorts, putting plugins/ first and inverting the\n"
        "intended standalone-first precedence. Use an explicit loop with `break`,\n"
        "the form skills/git-issue-workflow/scripts/agent-home.sh already uses.\n\n"
        + "\n".join(offenders)
    )


def test_test_graph_provider_binding_names_an_in_bundle_provider() -> None:
    """``provider-bindings.json`` must resolve to a provider inside this repo.

    The manifest is TRACKED (only the three directories it generates are
    gitignored), so this is a committed statement about where the Gradle SDK
    comes from, and it is checked here rather than by `project resolve`: the
    `[[vendored]]` block that used to make this claim was deleted by SI-11
    because `from_unit` has no spelling for a contained skill (see
    skill-project.toml).

    The stale value named ``../.skill-manager/skills/test-graph`` — inside the
    checkout's own gitignored home, at the retired standalone copy. That is not
    an inert path: the candidate list is tried in order and the first COMPLETE
    provider wins, so on a home carrying the old standalone install it won, and
    the three graphs ran their entire build against a copy of the SDK that the
    bundle no longer versions.
    """
    manifest_path = ROOT / "test_graph" / "provider-bindings.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    test_graph_root = manifest_path.parent

    workspace = [
        candidate
        for candidate in manifest["provider_candidates"]
        if candidate.get("kind") == "workspace-relative"
    ]
    assert workspace, (
        "provider-bindings.json declares no workspace-relative provider, so the "
        "only candidate left is `skill-root` — whichever copy of the test-graph "
        "scripts happens to be executing. Name the in-bundle provider explicitly."
    )

    for candidate in workspace:
        resolved = (test_graph_root / candidate["path"]).resolve()
        assert ROOT in resolved.parents or resolved == ROOT, (
            f"provider-bindings.json names a provider outside this repository:\n"
            f"  declared: {candidate['path']}\n"
            f"  resolves: {resolved}\n"
            "The provider must be the bundle's own skills/test-graph, not a copy "
            "inside a Skill Manager home."
        )
        assert ".skill-manager" not in resolved.parts, (
            f"provider-bindings.json names a provider inside a Skill Manager home:\n"
            f"  declared: {candidate['path']}\n"
            f"  resolves: {resolved}\n"
            "SI-02 retired the standalone test-graph install; a binding that "
            "points into a home reads the retired copy wherever one still exists, "
            "and silently falls through to `skill-root` wherever one does not."
        )
        for relative in manifest["bindings"].values():
            assert (resolved / relative).is_dir(), (
                f"declared provider {resolved} does not carry {relative}, so this "
                "candidate can never be selected and the manifest is decorative."
            )
