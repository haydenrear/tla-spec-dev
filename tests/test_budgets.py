"""Budgets are per-program manifest state with documented-default fallback."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.budgets import (  # noqa: E402
    BUDGET_KEYS,
    DEFAULT_BUDGETS,
    budget_prompt,
    budgets_block,
    load_budgets,
)

DOCUMENTED = {
    "tlc_seconds": 120,
    "max_distinct_states": 50000,
    "max_state_space_bound": 1000000,
    "max_internal_cases_per_component": 200,
    "max_external_cases_per_action": 50,
    "kill_rate_floor": 0.8,
    "max_component_variables": 6,
    "max_component_actions": 8,
    "max_symmetric_instances": 2,
}


def test_defaults_match_the_documented_reference() -> None:
    assert DEFAULT_BUDGETS == DOCUMENTED


def test_reference_doc_and_defaults_stay_in_sync() -> None:
    """references/modular_fuzzing.md is the prose source for these values."""
    text = (REPO_ROOT / "references" / "modular_fuzzing.md").read_text()
    for key, value in DOCUMENTED.items():
        assert f"{key}: {value}" in text, f"{key} drifted from references/modular_fuzzing.md"


def test_budgets_block_emits_every_key(tmp_path: Path) -> None:
    manifest = tmp_path / "spec_manifest.yaml"
    manifest.write_text("module: Demo\n\n" + budgets_block())
    loaded = load_budgets(manifest, warn=False)
    assert loaded == DEFAULT_BUDGETS
    for key in BUDGET_KEYS:
        assert key in manifest.read_text()


def test_missing_manifest_falls_back_with_warning(tmp_path: Path, capsys) -> None:
    loaded = load_budgets(tmp_path / "absent.yaml")
    assert loaded == DEFAULT_BUDGETS
    assert "no readable spec manifest" in capsys.readouterr().err


def test_missing_block_falls_back_with_warning(tmp_path: Path, capsys) -> None:
    manifest = tmp_path / "spec_manifest.yaml"
    manifest.write_text("module: Demo\n")
    loaded = load_budgets(manifest)
    assert loaded == DEFAULT_BUDGETS
    assert "no budgets block" in capsys.readouterr().err


def test_partial_block_fills_missing_keys_with_warning(tmp_path: Path, capsys) -> None:
    manifest = tmp_path / "spec_manifest.yaml"
    manifest.write_text("module: Demo\nbudgets:\n  tlc_seconds: 45\n")
    loaded = load_budgets(manifest)
    warning = capsys.readouterr().err

    assert loaded["tlc_seconds"] == 45
    assert loaded["max_distinct_states"] == DEFAULT_BUDGETS["max_distinct_states"]
    assert "is missing" in warning


def test_kill_rate_floor_is_numeric_under_the_fallback_parser(tmp_path: Path) -> None:
    """The minimal YAML fallback parser yields strings for floats; gates compare numerically."""
    manifest = tmp_path / "spec_manifest.yaml"
    manifest.write_text("module: Demo\nbudgets:\n  kill_rate_floor: 0.8\n")
    loaded = load_budgets(manifest, warn=False)
    assert isinstance(loaded["kill_rate_floor"], float)
    assert loaded["kill_rate_floor"] == 0.8


def test_non_numeric_budget_falls_back_with_warning(tmp_path: Path, capsys) -> None:
    manifest = tmp_path / "spec_manifest.yaml"
    manifest.write_text("module: Demo\nbudgets:\n  tlc_seconds: soon\n")
    loaded = load_budgets(manifest)
    assert loaded["tlc_seconds"] == DEFAULT_BUDGETS["tlc_seconds"]
    assert "not a valid int" in capsys.readouterr().err


def test_budget_prompt_instructs_negotiation_and_rationale() -> None:
    prompt = budget_prompt("specs/program_model/spec_manifest.yaml")
    assert "Propose these defaults to the user" in prompt
    assert "Ask which to adjust for this program" in prompt
    assert "one-line rationale" in prompt
    for key in BUDGET_KEYS:
        assert key in prompt


def _scaffold(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "tla_spec_dev.py"), *args],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )


def test_scaffold_project_emits_budgets_and_prompt(tmp_path: Path) -> None:
    result = _scaffold(tmp_path, "--spec-root", "specs", "scaffold", "project", "--name", "Prog")
    assert result.returncode == 0, result.stderr

    manifest = tmp_path / "specs/program_model/spec_manifest.yaml"
    assert "budgets:" in manifest.read_text()
    assert load_budgets(manifest, warn=False) == DEFAULT_BUDGETS
    assert "Propose these defaults to the user" in result.stdout
    assert "one-line rationale" in result.stdout


def test_scaffold_workflow_emits_budgets_and_prompt(tmp_path: Path) -> None:
    assert _scaffold(tmp_path, "--spec-root", "specs", "scaffold", "project", "--name", "Prog").returncode == 0
    result = _scaffold(tmp_path, "--spec-root", "specs", "scaffold", "workflow", "T-1", "Title")
    assert result.returncode == 0, result.stderr

    for manifest in (
        tmp_path / "specs/current/spec_manifest.yaml",
        tmp_path / "specs/desired_program_model/spec_manifest.yaml",
    ):
        assert "budgets:" in manifest.read_text(), manifest
        assert load_budgets(manifest, warn=False) == DEFAULT_BUDGETS
    assert "Propose these defaults to the user" in result.stdout
