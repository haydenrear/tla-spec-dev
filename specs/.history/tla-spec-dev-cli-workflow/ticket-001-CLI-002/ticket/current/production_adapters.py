"""Ticket-local adapters for the shipped tla-spec-dev CLI entrypoint."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "skill-manager.toml").is_file() and (parent / "scripts" / "tla_spec_dev.py").is_file():
            return parent
    raise RuntimeError("could not locate tla-spec-dev repository root")


class BuildSkillCliAdapter:
    action_name = "BuildSkillCli"

    def apply(self) -> dict[str, object]:
        root = repo_root()
        entrypoint = root / "scripts" / "tla_spec_dev.py"
        installer = root / "skill-scripts" / "install-tla-spec-dev.sh"
        return {
            "accepted": entrypoint.is_file() and installer.is_file(),
            "entrypoint": str(entrypoint),
            "installer": str(installer),
        }


class InstallLocalCliAdapter:
    action_name = "InstallLocalCli"

    def apply(self, bin_dir: Path, cache_dir: Path) -> dict[str, object]:
        root = repo_root()
        env = {
            **os.environ,
            "SKILL_MANAGER_BIN_DIR": str(bin_dir),
            "SKILL_MANAGER_CACHE_DIR": str(cache_dir),
            "SKILL_DIR": str(root),
            "SKILL_NAME": "spec-double-compiler",
        }
        install = subprocess.run(
            ["bash", str(root / "skill-scripts" / "install-tla-spec-dev.sh")],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        wrapper = bin_dir / "tla-spec-dev"
        version = subprocess.run(
            [str(wrapper), "--version"],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        ) if wrapper.exists() else None
        return {
            "accepted": install.returncode == 0 and version is not None and version.returncode == 0,
            "install_exit_code": install.returncode,
            "version_exit_code": None if version is None else version.returncode,
            "version": "" if version is None else version.stdout.strip(),
            "wrapper": str(wrapper),
        }
