from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "examples" / "effect_providers" / "run_validations.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("effect_provider_example_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_fixture(tmp_path: Path, *, described_port: str = "DemoPort") -> Path:
    project = tmp_path / "demo"
    manifest = project / "specs" / "program_model" / "spec_manifest.yaml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        "ports:\n  DemoPort:\n    role: effect\n",
        encoding="utf-8",
    )
    usage = project / "effect_provider_usage.yaml"
    usage.write_text(
        "\n".join(
            (
                "version: 1",
                "providers:",
                f"  - port: {described_port}",
                "    provider: demo:effect_provider",
                "    binding_style: explicit_injection",
                "    state_scope: execution_point",
                "    fuzz_dimensions: [representative]",
                "    assertions: [modeled_result]",
                "    cleanup: context_manager",
                "    bypass_limits: []",
                "",
            )
        ),
        encoding="utf-8",
    )
    run_id = "run-1"
    result_path = project / "evidence" / "validation-runs" / run_id / "result.json"
    result_path.parent.mkdir(parents=True)
    result = {
        "schema_version": 1,
        "project": "demo",
        "run_id": run_id,
        "status": "pass",
        "command": ["/usr/bin/python3", "validate.py", "--run-id", run_id],
        "commit": "0123456789abcdef",
        "provider_contract": {"name": "EffectProvider.bind", "version": 1},
        "seed": 7,
        "cases": {"generated": 1, "control_points": 1, "external": 1},
        "controls": {"passed": 1, "total": 1},
        "mutants": {"killed": 1, "total": 1},
        "replay": {"attempted": 1, "exact": 1, "interpreter": "/usr/bin/python3"},
        "cleanup": {"checked": 1, "clean": 1},
        "duration_seconds": 0.1,
        "usage_descriptor": {
            "path": "effect_provider_usage.yaml",
            "sha256": hashlib.sha256(usage.read_bytes()).hexdigest(),
        },
        "oracle_findings": {
            "tla_owned": ["result"],
            "provider_owned": ["payload"],
            "passive_external": ["boundary"],
        },
        "limitations": ["representative, not exhaustive"],
        "artifacts": ["result.json"],
    }
    result_path.write_text(json.dumps(result), encoding="utf-8")
    return result_path


def test_common_result_and_usage_descriptor_are_accepted(tmp_path: Path, monkeypatch) -> None:
    runner = load_runner()
    monkeypatch.setattr(runner, "EXAMPLES_ROOT", tmp_path)
    result_path = write_fixture(tmp_path)

    result = runner._validate_result("demo", "run-1", result_path)

    assert result["status"] == "pass"


def test_usage_descriptor_must_cover_generated_effect_ports(tmp_path: Path, monkeypatch) -> None:
    runner = load_runner()
    monkeypatch.setattr(runner, "EXAMPLES_ROOT", tmp_path)
    result_path = write_fixture(tmp_path, described_port="WrongPort")

    with pytest.raises(ValueError, match="do not match generated effect ports"):
        runner._validate_result("demo", "run-1", result_path)
