from pathlib import Path
import shutil
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.onboard_program_model import (
    REQUIRED_BASELINE_FILES,
    has_test_graph,
    missing_baseline_files,
    scaffold,
)


def test_onboard_program_model_creates_only_program_model(tmp_path: Path) -> None:
    scaffold(tmp_path, "SkillManager", force=False, dry_run=False)

    assert not (tmp_path / "specs/current").exists()
    assert not (tmp_path / "specs/desired_program_model").exists()

    manifest = (tmp_path / "specs/program_model/spec_manifest.yaml").read_text(encoding="utf-8")
    assert "workflow: project_onboarding" in manifest
    assert "model_role: accepted_program_model" in manifest


@pytest.mark.parametrize("name", REQUIRED_BASELINE_FILES)
def test_scaffold_emits_every_required_baseline_file(tmp_path: Path, name: str) -> None:
    """A scaffold that omits any of these produces an unusable baseline.

    Internal.tla/External.tla and the two adapter mappings are the whole point of
    the workflow: without them the project has no generative integration testing.
    """
    scaffold(tmp_path, "SkillManager", force=False, dry_run=False)

    assert (tmp_path / "specs/program_model" / name).exists()
    assert missing_baseline_files(tmp_path / "specs/program_model") == []


def test_scaffold_emits_both_views_and_both_adapter_mappings(tmp_path: Path) -> None:
    scaffold(tmp_path, "SkillManager", force=False, dry_run=False)
    program_model = tmp_path / "specs/program_model"

    assert "EXTENDS Core" in (program_model / "Internal.tla").read_text(encoding="utf-8")
    assert "EXTENDS Internal" in (program_model / "External.tla").read_text(encoding="utf-8")

    # Spec-unit adapters map internal actions; Test Graph adapters map external ones.
    case_adapters = (program_model / "case_adapters.toml").read_text(encoding="utf-8")
    assert "InternalAdapter" in case_adapters
    assert "[effect_providers.ExampleEffectPort]" in case_adapters
    assert "specs.program_model.providers:effect_provider" in case_adapters

    actions = (program_model / "actions.yml").read_text(encoding="utf-8")
    assert actions.count("effect_ports: []") == 11

    providers = (program_model / "providers.py").read_text(encoding="utf-8")
    assert "class ProjectEffectProvider" in providers
    assert "def bind(" in providers
    assert "temporary_root_provider" not in providers
    assert "context_provider" not in providers
    assert "SCAFFOLD:" in providers

    usage = (program_model / "effect_provider_usage.yaml").read_text(encoding="utf-8")
    assert "version: 1" in usage
    assert "providers: []" in usage
    assert "bypass_limits:" in usage

    bindings = (program_model / "testgraph_bindings.yml").read_text(encoding="utf-8")
    for hook in ("adapter:", "projector:", "expected_projection:", "assertion:"):
        assert hook in bindings

    adapters = (program_model / "adapters.py").read_text(encoding="utf-8")
    for symbol in (
        "class RegisterActorInternalAdapter",
        "class RegisterActorExternalAdapter",
        "class ProgramStateProjector",
        "class ExpectedProgramProjection",
        "class ProjectedStateAssertion",
    ):
        assert symbol in adapters


def test_scaffold_emits_example_spec_unit_adapter_test(tmp_path: Path) -> None:
    scaffold(tmp_path, "SkillManager", force=False, dry_run=False)
    tests_dir = tmp_path / "specs/program_model/tests"

    assert (tests_dir / "test_spec_unit_adapters.py").exists()
    assert (tests_dir / "test_program_model_onboarding.py").exists()


def test_scaffold_warns_when_repo_has_no_test_graph(tmp_path: Path, capsys) -> None:
    scaffold(tmp_path, "SkillManager", force=False, dry_run=False)

    output = capsys.readouterr().out
    assert "NO test_graph PROJECT FOUND" in output
    assert "will NOT be validated" in output


def test_scaffold_is_quiet_when_test_graph_exists(tmp_path: Path, capsys) -> None:
    test_graph = tmp_path / "test_graph"
    test_graph.mkdir()
    (test_graph / "build.gradle.kts").write_text("", encoding="utf-8")

    assert has_test_graph(tmp_path)

    scaffold(tmp_path, "SkillManager", force=False, dry_run=False)
    assert "NO test_graph PROJECT FOUND" not in capsys.readouterr().out


@pytest.mark.skipif(shutil.which("tlc2") is None, reason="tlc2 is not installed")
@pytest.mark.parametrize(
    ("module", "config"),
    [("Internal.tla", "Internal.cfg"), ("External.tla", "External.cfg")],
)
def test_scaffolded_views_model_check_cleanly(tmp_path: Path, module: str, config: str) -> None:
    """Both scaffolded views must pass TLC as emitted.

    A new user is told to run TLC on both views immediately after onboarding. If
    the scaffold ships a spec that errors, the first thing they see is a failure
    they did not cause.
    """
    scaffold(tmp_path, "SkillManager", force=False, dry_run=False)
    program_model = tmp_path / "specs" / "program_model"

    result = subprocess.run(
        ["tlc2", "-config", config, module],
        cwd=program_model,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout
    assert "No error has been found" in result.stdout


@pytest.mark.parametrize("script", ["onboard_program_model.py", "new_ticket_workflow.py"])
def test_scripts_run_as_direct_invocations(tmp_path: Path, script: str) -> None:
    """These are runnable as plain scripts, where sys.path[0] is scripts/, not the repo root."""
    scaffold(tmp_path, "SkillManager", force=False, dry_run=False)
    args = ["T-1", "title"] if script == "new_ticket_workflow.py" else []

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *args, "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "ModuleNotFoundError" not in result.stderr


def test_onboard_program_model_uses_custom_spec_root(tmp_path: Path) -> None:
    written = scaffold(
        tmp_path,
        "SkillManager",
        force=False,
        dry_run=False,
        spec_root=Path("project/specs"),
    )

    assert tmp_path / "project/specs/program_model/spec_manifest.yaml" in written
    assert (tmp_path / "project/specs/program_model/Internal.tla").exists()
    assert (tmp_path / "project/specs/program_model/External.tla").exists()
    generated_test = (
        tmp_path / "project/specs/program_model/tests/test_program_model_onboarding.py"
    ).read_text(encoding="utf-8")
    assert 'SPEC_ROOT = Path(__file__).resolve().parents[1]' in generated_test


def test_onboard_program_model_preserves_existing_program_model_files(tmp_path: Path) -> None:
    existing = tmp_path / "specs" / "program_model" / "spec_manifest.yaml"
    existing.parent.mkdir(parents=True)
    existing.write_text("keep: true\n", encoding="utf-8")

    scaffold(tmp_path, "SkillManager", force=False, dry_run=False)

    assert existing.read_text(encoding="utf-8") == "keep: true\n"
