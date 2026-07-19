"""MF-013: effect conformance through the real adapter runner.

The unit tests in ``test_effect_conformance.py`` exercise the schema, the
sandbox, and the diff in isolation. These drive the whole path --
``execute_cases_in_batch`` loading an adapter, running it inside the sandbox,
diffing, and exiting nonzero -- so the gate is proven where it actually runs,
not only where it is defined.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from effect_conformance import load_effect_declarations  # noqa: E402
from scripts.run_generated_case_adapters import (  # noqa: E402
    AdapterMapping,
    execute_cases_in_batch,
)

FIXTURES = "tests.effect_adapter_fixtures"


@dataclass(frozen=True)
class Output:
    changed: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Case:
    name: str
    labels: frozenset[str]
    before: dict = field(default_factory=dict)
    input: Any = None
    output: Any = None
    after: Any = None


def effects_block(**extra: Any) -> dict[str, Any]:
    """Declares one port: writes under a case's own sandbox directory."""
    block: dict[str, Any] = {
        "effects": {
            "components": {
                "Fixture": {
                    "ports": {
                        "case_sandbox": {
                            "type": "filesystem.write",
                            "target": "**/sandbox/**",
                        }
                    }
                }
            },
            "actions": {"Act": ["case_sandbox"]},
        }
    }
    block["effects"].update(extra)
    return block


def run_batch(adapter: str, tmp_path: Path, *, effects: dict[str, Any] | None = None, report: Path | None = None):
    case = Case(name="case_1", labels=frozenset({"Act"}))
    mappings = {"Act": AdapterMapping("Act", f"{FIXTURES}:{adapter}", order=0)}
    execute_cases_in_batch(
        cases=[case],
        mappings=mappings,
        work_dir=tmp_path / "work",
        import_roots=[ROOT],
        declarations=load_effect_declarations(effects if effects is not None else effects_block()),
        effect_report_path=report,
    )


class TestRunnerEnforcesEffectConformance:
    def test_declared_only_adapter_passes(self, tmp_path):
        run_batch("DeclaredEffectAdapter", tmp_path)  # no SystemExit

    def test_undeclared_effect_fails_the_run(self, tmp_path):
        """THE rule: the run FAILS. Not warns, not records-and-continues."""
        with pytest.raises(SystemExit) as excinfo:
            run_batch("UndeclaredEffectAdapter", tmp_path)
        message = str(excinfo.value)
        assert "effect conformance gaps" in message
        assert "UNDECLARED EFFECT" in message
        assert "leaked.txt" in message

    def test_gap_is_recorded_AND_the_run_fails(self, tmp_path):
        """Recording is not an alternative to failing: assert both together."""
        report_path = tmp_path / "report.json"
        with pytest.raises(SystemExit):
            run_batch("UndeclaredEffectAdapter", tmp_path, report=report_path)
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        assert payload["ok"] is False
        assert payload["verdict"] == "gaps"
        assert any("leaked.txt" in gap["target"] for gap in payload["gaps"])

    def test_report_is_written_as_evidence_even_when_clean(self, tmp_path):
        report_path = tmp_path / "clean.json"
        run_batch("DeclaredEffectAdapter", tmp_path, report=report_path)
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        assert payload["ok"] is True and payload["verdict"] == "clean"

    def test_dead_declared_port_fails_the_run(self, tmp_path):
        """A port no case exercises fails; it is removed or exercised."""
        block = effects_block()
        block["effects"]["components"]["Fixture"]["ports"]["never_used"] = {
            "type": "network.http",
            "target": "https://example.invalid/**",
        }
        block["effects"]["actions"]["Act"].append("never_used")
        with pytest.raises(SystemExit) as excinfo:
            run_batch("DeclaredEffectAdapter", tmp_path, effects=block)
        assert "DEAD MODEL SURFACE" in str(excinfo.value)
        assert "never_used" in str(excinfo.value)


class TestJustificationDoesNotSuppressInTheRunner:
    """The inverse test, at the runner level.

    ``JustifiedUndeclaredEffectAdapter`` behaves identically to
    ``UndeclaredEffectAdapter`` but carries an ``out_of_contract`` flag, a
    ``justification`` string, an ``effect_waiver`` pattern list and an
    ``allow_undeclared`` flag. The run must fail exactly as if none of them
    were there.
    """

    def test_adapter_carrying_a_justification_still_fails(self, tmp_path):
        with pytest.raises(SystemExit) as excinfo:
            run_batch("JustifiedUndeclaredEffectAdapter", tmp_path)
        assert "UNDECLARED EFFECT" in str(excinfo.value)

    def test_manifest_justification_entry_still_fails(self, tmp_path):
        block = effects_block(
            justifications=[
                {"port": "case_sandbox", "target": "**/undeclared-store/**", "reason": "accepted"}
            ]
        )
        with pytest.raises(SystemExit) as excinfo:
            run_batch("UndeclaredEffectAdapter", tmp_path, effects=block)
        assert "UNDECLARED EFFECT" in str(excinfo.value)

    def test_manifest_allow_undeclared_still_fails(self, tmp_path):
        block = effects_block(allow_undeclared=True)
        with pytest.raises(SystemExit) as excinfo:
            run_batch("UndeclaredEffectAdapter", tmp_path, effects=block)
        assert "UNDECLARED EFFECT" in str(excinfo.value)

    def test_justified_and_unjustified_runs_produce_the_same_verdict(self, tmp_path):
        """The strongest form: byte-comparable outcomes."""
        plain = tmp_path / "plain.json"
        justified = tmp_path / "justified.json"
        with pytest.raises(SystemExit):
            run_batch("UndeclaredEffectAdapter", tmp_path / "a", report=plain)
        with pytest.raises(SystemExit):
            run_batch(
                "JustifiedUndeclaredEffectAdapter",
                tmp_path / "b",
                effects=effects_block(justification="accepted risk"),
                report=justified,
            )
        left = json.loads(plain.read_text(encoding="utf-8"))
        right = json.loads(justified.read_text(encoding="utf-8"))
        assert left["ok"] == right["ok"] is False
        assert left["verdict"] == right["verdict"] == "gaps"
        assert len(left["gaps"]) == len(right["gaps"])
        # ...and the ignored key is surfaced rather than silently dropped.
        assert right["ignored_suppression_keys"] == ["effects.justification"]
