"""MF-013: `tla-spec-dev run effect-conformance` exit-code contract.

The command's whole value is that it FAILS. These tests pin the exit codes so
that a future change cannot quietly turn a finding into a warning.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import effect_conformance_report  # noqa: E402


def make_args(**kwargs):
    defaults = dict(
        spec_root="specs", ticket=None, target=None, cases_dir=None,
        mapping=None, work_dir=None, out=None, format="text",
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def write_spec_dir(tmp_path: Path, effects_yaml: str) -> Path:
    spec_dir = tmp_path / "spec"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec_manifest.yaml").write_text(effects_yaml, encoding="utf-8")
    return spec_dir


DECLARED = """
module: Demo
effects:
  components:
    C:
      ports:
        workspace:
          type: filesystem.write
          target: "**/workspace/**"
  actions:
    Act: [workspace]
"""


def test_missing_spec_dir_exits_2(tmp_path):
    assert effect_conformance_report.run(make_args(target=tmp_path / "nope")) == 2


def test_no_declarations_exits_2(tmp_path):
    spec_dir = write_spec_dir(tmp_path, "module: Demo\n")
    assert effect_conformance_report.run(make_args(target=spec_dir)) == 2


def test_malformed_declaration_exits_2(tmp_path):
    spec_dir = write_spec_dir(
        tmp_path,
        "module: Demo\neffects:\n  components:\n    C:\n      ports:\n        p:\n          target: '**'\n",
    )
    assert effect_conformance_report.run(make_args(target=spec_dir)) == 2


def test_unexercised_declaration_exits_1_as_dead_surface(tmp_path):
    """No corpus means nothing observed, so every declared port reads as dead."""
    spec_dir = write_spec_dir(tmp_path, DECLARED)
    assert effect_conformance_report.run(make_args(target=spec_dir)) == 1


def test_report_is_written_as_evidence(tmp_path):
    spec_dir = write_spec_dir(tmp_path, DECLARED)
    out = tmp_path / "results" / "effects.json"
    assert effect_conformance_report.run(make_args(target=spec_dir, out=out)) == 1
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["ok"] is False
    assert payload["verdict"] == "dead_surface"
    assert "withdrawn" in payload["suppression_policy"]


def test_manifest_justification_does_not_change_the_exit_code(tmp_path):
    """The inverse test at the CLI boundary."""
    plain = write_spec_dir(tmp_path / "a", DECLARED)
    justified = write_spec_dir(
        tmp_path / "b",
        DECLARED + "  justification: 'ports are aspirational, accepted by review'\n",
    )
    assert effect_conformance_report.run(make_args(target=plain)) == 1
    assert effect_conformance_report.run(make_args(target=justified)) == 1


def test_shipped_ticket_declarations_load_through_the_cli(tmp_path):
    out = tmp_path / "shipped.json"
    code = effect_conformance_report.run(
        make_args(target=ROOT / "specs" / "tickets" / "MF-013" / "current", out=out)
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert code == 1
    assert payload["declared_ports"], "shipped manifest declares no ports"
    assert payload["ignored_suppression_keys"] == []
