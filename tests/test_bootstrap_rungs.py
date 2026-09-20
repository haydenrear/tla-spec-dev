"""`_bootstrap_script` must find the unit CONTAINED in a plugin, not only standalone.

The bug this guards: `ticket new` resolved
`<home>/skills/git-issue-workflow/scripts/bootstrap-home.sh` and nothing else,
so a home carrying that unit inside a plugin rolled its worktree back with
"bootstrap-home.sh not found in this home" -- while the file sat one rung over
the whole time.

The existing suite could not catch it. Every fixture here builds the standalone
rung (`tests/test_epic_mode.py`'s `fake_bootstrap`), so 304 tests passed against
a resolver that only ever looked at the rung they built.
"""
from __future__ import annotations

import stat
from pathlib import Path

from skt import ticket


def _script(at: Path) -> Path:
    at.parent.mkdir(parents=True, exist_ok=True)
    at.write_text("#!/usr/bin/env bash\nexit 0\n")
    at.chmod(at.stat().st_mode | stat.S_IEXEC)
    return at


def _home(tmp_path: Path) -> Path:
    home = tmp_path / ".skill-manager"
    (home / "installed").mkdir(parents=True, exist_ok=True)
    return home


def test_resolves_a_contained_copy_when_no_standalone_exists(tmp_path, monkeypatch):
    home = _home(tmp_path)
    contained = _script(
        home / "plugins" / "some-plugin" / "skills" / ticket.UNIT / "scripts" / "bootstrap-home.sh"
    )
    monkeypatch.setenv("SKILL_MANAGER_HOME", str(home))
    assert not (home / "skills" / ticket.UNIT / "scripts" / "bootstrap-home.sh").exists()
    assert ticket._bootstrap_script() == contained


def test_standalone_still_wins_when_both_exist(tmp_path, monkeypatch):
    home = _home(tmp_path)
    standalone = _script(home / "skills" / ticket.UNIT / "scripts" / "bootstrap-home.sh")
    _script(
        home / "plugins" / "some-plugin" / "skills" / ticket.UNIT / "scripts" / "bootstrap-home.sh"
    )
    monkeypatch.setenv("SKILL_MANAGER_HOME", str(home))
    assert ticket._bootstrap_script() == standalone


def test_none_when_neither_rung_has_it(tmp_path, monkeypatch):
    home = _home(tmp_path)
    monkeypatch.setenv("SKILL_MANAGER_HOME", str(home))
    assert ticket._bootstrap_script() is None
