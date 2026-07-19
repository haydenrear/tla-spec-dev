from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_cases_from_tlc_dump import (
    CASE_ENVELOPE_SCHEMA_VERSION,
    CASE_MANIFEST_SCHEMA_VERSION,
    CaseBudgets,
    canonical_json_bytes,
    render_streaming_case_protocol,
    sha256_digest,
)


def write_inputs(
    root: Path,
    edges: list[tuple[int, int, str]],
) -> tuple[Path, Path, Path]:
    tla = root / "Program.tla"
    cfg = root / "MC.cfg"
    dot = root / "Program.dot"
    tla.write_text("---- MODULE Program ----\n====\n", encoding="utf-8")
    cfg.write_text("SPECIFICATION Spec\n", encoding="utf-8")
    states = {
        0: "pending",
        1: "ok",
        2: "missing",
    }
    with dot.open("w", encoding="utf-8") as handle:
        handle.write("digraph DiskGraph {\n")
        for node, status in states.items():
            handle.write(f'{node} [label="/\\\\ status = \\"{status}\\""];\n')
        for source, target, action in edges:
            handle.write(f'{source} -> {target} [label="{action}"];\n')
        handle.write("}\n")
    return tla, cfg, dot


def generate(
    root: Path,
    *,
    edges: list[tuple[int, int, str]],
    package: str,
    budgets: CaseBudgets,
    seed: str = "seed-1",
):
    tla, cfg, dot = write_inputs(root, edges)
    return render_streaming_case_protocol(
        module="Program",
        tla_path=tla,
        cfg_path=cfg,
        dot_path=dot,
        package_dir=root / package,
        budgets=budgets,
        seed=seed,
    )


def test_streaming_protocol_writes_canonical_digest_accounted_records(tmp_path: Path) -> None:
    result = generate(
        tmp_path,
        edges=[
            (0, 1, "Submit"),
            (0, 2, "Submit"),
            (0, 1, "Resolve"),
            (0, 2, "Resolve"),
        ],
        package="stream",
        budgets=CaseBudgets(
            max_cases=20,
            max_output_bytes=2 * 1024 * 1024,
            max_rss_mib=512,
            max_seconds=30,
        ),
    )

    assert result.exit_code == 0
    assert result.cases_path.is_file()
    assert not (result.cases_path.parent / "cases.py").exists()
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == CASE_MANIFEST_SCHEMA_VERSION
    assert manifest["case_schema_version"] == CASE_ENVELOPE_SCHEMA_VERSION
    assert manifest["complete"] is True
    assert manifest["status"] == "complete"
    assert manifest["budget_outcome"] == {"type": "within_budget"}
    assert manifest["observed_transition_count"] == 4
    assert manifest["selected_case_count"] == 4
    assert manifest["emitted_case_count"] == 4
    assert manifest["selection_policy"] == "stable-hash-stratified"
    assert manifest["cases_digest"] == sha256_digest(result.cases_path.read_bytes())

    manifest_digest = manifest.pop("manifest_digest")
    assert manifest_digest == sha256_digest(canonical_json_bytes(manifest))

    records = [
        json.loads(line)
        for line in result.cases_path.read_text(encoding="utf-8").splitlines()
    ]
    assert len(records) == 4
    assert {record["action"] for record in records} == {"Submit", "Resolve"}
    for record in records:
        assert record["schema_version"] == CASE_ENVELOPE_SCHEMA_VERSION
        assert isinstance(record["before"]["status"], str)
        assert isinstance(record["input"], dict)
        assert "expected_output" in record
        assert record["expected_projection"] == record["after"]
        digest = record.pop("record_digest")
        assert digest == sha256_digest(canonical_json_bytes(record))


def test_canonical_json_preserves_integers_sorts_sets_and_encodes_bytes() -> None:
    encoded = canonical_json_bytes(
        {
            "integer": 9_007_199_254_740_993,
            "members": frozenset({3, 1, 2}),
            "path_bytes": b"\xff/a",
        }
    )

    assert json.loads(encoded) == {
        "integer": 9_007_199_254_740_993,
        "members": [1, 2, 3],
        "path_bytes": {"$bytes_base64url": "_y9h"},
    }
    try:
        canonical_json_bytes({"invalid": math.nan})
    except ValueError as exc:
        assert "non-finite" in str(exc)
    else:
        raise AssertionError("non-finite canonical JSON must be rejected")


def test_selection_is_seeded_stable_and_action_outcome_stratified(tmp_path: Path) -> None:
    edges = []
    for _ in range(10):
        edges.extend(
            [
                (0, 1, "Submit"),
                (0, 2, "Submit"),
                (0, 1, "Resolve"),
                (0, 2, "Resolve"),
            ]
        )
    budgets = CaseBudgets(
        max_cases=4,
        max_output_bytes=2 * 1024 * 1024,
        max_rss_mib=512,
        max_seconds=30,
    )
    first = generate(tmp_path, edges=edges, package="first", budgets=budgets)
    second = generate(tmp_path, edges=edges, package="second", budgets=budgets)
    other_seed = generate(
        tmp_path,
        edges=edges,
        package="other",
        budgets=budgets,
        seed="seed-2",
    )

    assert first.cases_path.read_bytes() == second.cases_path.read_bytes()
    first_records = [
        json.loads(line)
        for line in first.cases_path.read_text(encoding="utf-8").splitlines()
    ]
    other_records = [
        json.loads(line)
        for line in other_seed.cases_path.read_text(encoding="utf-8").splitlines()
    ]
    assert len(
        {(record["action"], record["outcome"]) for record in first_records}
    ) == 4
    assert [record["case_id"] for record in first_records] != [
        record["case_id"] for record in other_records
    ]
    assert first.manifest["budget_outcome"]["type"] == "bounded_selection"
    assert first.manifest["candidate_case_count"] == 40
    assert first.manifest["selected_case_count"] == 4


def test_output_budget_writes_only_typed_incomplete_manifest(tmp_path: Path) -> None:
    result = generate(
        tmp_path,
        edges=[(0, 1, "Submit")],
        package="limited",
        budgets=CaseBudgets(
            max_cases=10,
            max_output_bytes=128,
            max_rss_mib=512,
            max_seconds=30,
        ),
    )

    assert result.exit_code == 2
    assert result.manifest["complete"] is False
    assert result.manifest["status"] == "incomplete"
    assert result.manifest["budget_outcome"]["type"] == "budget_exceeded"
    assert result.manifest["budget_outcome"]["budget"] == "max_output_bytes"
    assert result.manifest["emitted_case_count"] == 0
    assert result.manifest["cases_digest"] is None
    assert result.manifest_path.is_file()
    assert not result.cases_path.exists()
    assert not (result.cases_path.parent / ".cases.jsonl.partial").exists()
    assert not (result.cases_path.parent / "cases.py").exists()


def test_time_budget_writes_typed_incomplete_manifest(tmp_path: Path) -> None:
    result = generate(
        tmp_path,
        edges=[(0, 1, "Submit")],
        package="timeout",
        budgets=CaseBudgets(
            max_cases=10,
            max_output_bytes=1024 * 1024,
            max_rss_mib=512,
            max_seconds=0.000001,
        ),
    )

    assert result.exit_code == 2
    assert result.manifest["budget_outcome"]["budget"] == "max_seconds"
    assert not result.cases_path.exists()


def test_rss_budget_writes_typed_incomplete_manifest(tmp_path: Path) -> None:
    result = generate(
        tmp_path,
        edges=[(0, 1, "Submit")],
        package="rss-limit",
        budgets=CaseBudgets(
            max_cases=10,
            max_output_bytes=1024 * 1024,
            max_rss_mib=0.001,
            max_seconds=30,
        ),
    )

    assert result.exit_code == 2
    assert result.manifest["budget_outcome"]["budget"] == "max_rss_mib"
    assert not result.cases_path.exists()


def test_cli_returns_nonzero_for_typed_budget_failure(tmp_path: Path) -> None:
    tla, cfg, dot = write_inputs(tmp_path, [(0, 1, "Submit")])
    command = [
        sys.executable,
        str(ROOT / "scripts/generate_cases_from_tlc_dump.py"),
        str(tla),
        str(cfg),
        "--out",
        str(tmp_path / "cli-output"),
        "--input-dot",
        str(dot),
        "--format",
        "streaming-jsonl",
        "--max-output-bytes",
        "128",
    ]
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        command,
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 2
    manifest_path = (
        tmp_path / "cli-output" / "tlc_state_graph_cases" / "case-manifest.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["budget_outcome"]["budget"] == "max_output_bytes"
    assert not manifest_path.with_name("cases.jsonl").exists()


def test_75701_transition_fixture_stays_bounded_and_exact(tmp_path: Path) -> None:
    transition_count = 75_701
    tla = tmp_path / "Program.tla"
    cfg = tmp_path / "MC.cfg"
    dot = tmp_path / "Program.dot"
    tla.write_text("---- MODULE Program ----\n====\n", encoding="utf-8")
    cfg.write_text("SPECIFICATION Spec\n", encoding="utf-8")
    with dot.open("w", encoding="utf-8") as handle:
        handle.write("digraph DiskGraph {\n")
        handle.write('0 [label="/\\\\ status = \\"pending\\""];\n')
        handle.write('1 [label="/\\\\ status = \\"ok\\""];\n')
        for _ in range(transition_count):
            handle.write('0 -> 1 [label="Submit"];\n')
        handle.write("}\n")

    result = render_streaming_case_protocol(
        module="Program",
        tla_path=tla,
        cfg_path=cfg,
        dot_path=dot,
        package_dir=tmp_path / "stress",
        budgets=CaseBudgets(
            max_cases=64,
            max_output_bytes=4 * 1024 * 1024,
            max_rss_mib=512,
            max_seconds=120,
        ),
        seed="stress-seed",
    )

    assert result.exit_code == 0
    assert result.manifest["observed_transition_count"] == transition_count
    assert result.manifest["candidate_case_count"] == transition_count
    assert result.manifest["selected_case_count"] == 64
    assert result.manifest["emitted_case_count"] == 64
    assert result.manifest["resource_usage"]["peak_rss_mib"] <= 512
    assert result.manifest["cases_digest"] == sha256_digest(
        result.cases_path.read_bytes()
    )
    assert len(result.cases_path.read_text(encoding="utf-8").splitlines()) == 64
    assert not (result.cases_path.parent / "cases.py").exists()
    assert not list(result.cases_path.parent.glob(".case-selection-*.sqlite3"))
