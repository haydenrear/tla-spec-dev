"""ESC-MO005-03: a run whose inputs moved must not report a program defect.

A ticket close rewrites the spec tree IN PLACE while a case batch imports
adapters out of it, scenario by scenario, over minutes. The measured outcome
was a red record with six failures, followed two minutes later by a green run
of the same cases at the same commit -- byte-identical generated trees,
opposite verdicts, and nothing in either artifact able to tell "the program
disagrees with the model" from "your inputs moved".

The tests below fix both halves of that: the digest is CONTENT-based (an mtime
cannot be trusted, because promotion copies with ``shutil.copy2`` and that
preserves the source mtime), and the named reason WINS over the case failures
it causes, since case failures are the symptom rather than a competing finding.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_cases_from_tlc_dump import ActionMetadata, Edge, render_python_package
from scripts.run_generated_case_adapters import (
    INPUTS_CHANGED_EXIT_CODE,
    INPUTS_CHANGED_SENTINEL,
    SpecInputGuard,
    changed_spec_inputs,
    spec_tree_digest,
)


# --------------------------------------------------------------- digest units


def test_digest_sees_a_rewrite_that_backdates_its_own_mtime(tmp_path: Path) -> None:
    """The forensics trap, encoded.

    ``shutil.copy2`` preserves the SOURCE mtime, so a promoted file can carry
    an mtime from before the run while holding bytes that arrived during it.
    That is why the run start time was compared against a file mtime and the
    rewrite was declared impossible.
    """
    spec = tmp_path / "current"
    spec.mkdir()
    adapters = spec / "adapters.py"
    adapters.write_text("BEFORE\n", encoding="utf-8")
    os.utime(adapters, (1_000_000, 1_000_000))
    before = spec_tree_digest(spec)
    before_mtime = adapters.stat().st_mtime

    adapters.write_text("AFTER\n", encoding="utf-8")
    os.utime(adapters, (1_000_000, 1_000_000))
    after = spec_tree_digest(spec)

    assert adapters.stat().st_mtime == before_mtime, "the mtime is unchanged, as copy2 leaves it"
    assert before["digest"] != after["digest"]
    assert changed_spec_inputs(before, after) == ["adapters.py"]


def test_digest_names_added_and_removed_inputs(tmp_path: Path) -> None:
    spec = tmp_path / "current"
    spec.mkdir()
    (spec / "kept.py").write_text("kept\n", encoding="utf-8")
    (spec / "removed.py").write_text("gone soon\n", encoding="utf-8")
    before = spec_tree_digest(spec)

    (spec / "removed.py").unlink()
    (spec / "added.py").write_text("new\n", encoding="utf-8")
    after = spec_tree_digest(spec)

    assert changed_spec_inputs(before, after) == ["added.py", "removed.py"]


def test_digest_ignores_caches_scratch_output_and_the_runs_own_work_dir(tmp_path: Path) -> None:
    """A guard that fires on its own writes is a guard nobody leaves on.

    Adapters legitimately leave effect logs and scratch next to the spec they
    were loaded from; only the files a run READS are inputs.
    """
    spec = tmp_path / "current"
    work = spec / "work"
    (spec / "__pycache__").mkdir(parents=True)
    work.mkdir(parents=True)
    (spec / "adapters.py").write_text("stable\n", encoding="utf-8")
    before = spec_tree_digest(spec, exclude=(work,))

    (spec / "__pycache__" / "adapters.cpython-313.pyc").write_bytes(b"\x00bytecode")
    (spec / "adapters.pyc").write_bytes(b"\x00bytecode")
    (spec / "events.txt").write_text("setup\nrun\nteardown\n", encoding="utf-8")
    (spec / "adapter.log").write_text("noise\n", encoding="utf-8")
    (work / "case-work").mkdir()
    (work / "case-work" / "program-state.json").write_text("{}", encoding="utf-8")
    after = spec_tree_digest(spec, exclude=(work,))

    assert changed_spec_inputs(before, after) == []


def test_digest_covers_every_file_type_a_run_reads(tmp_path: Path) -> None:
    """The allowlist has to actually contain the inputs, or nothing is watched.

    Named individually rather than asserted as a set so a future narrowing of
    the allowlist fails here with the dropped suffix in the message.
    """
    spec = tmp_path / "current"
    spec.mkdir()
    watched = [
        "adapters.py",
        "External.tla",
        "External.cfg",
        "testgraph_bindings.yml",
        "spec_manifest.yaml",
        "case_adapters.toml",
        "generated/testgraph/traces/manifest.json",
    ]
    for relative in watched:
        path = spec / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("before\n", encoding="utf-8")
    before = spec_tree_digest(spec)

    for relative in watched:
        (spec / relative).write_text("after\n", encoding="utf-8")
    after = spec_tree_digest(spec)

    assert changed_spec_inputs(before, after) == sorted(watched)


def test_guard_without_a_spec_dir_reports_nothing(tmp_path: Path) -> None:
    guard = SpecInputGuard(None)
    guard.start()
    assert guard.finish() == []


# ----------------------------------------------------------- end-to-end (CLI)


ADAPTERS_TEMPLATE = '''\
import os
from pathlib import Path

from spec_double_compiler.runtime import CaseRunResult

SPEC_DIR = Path(__file__).resolve().parent


def _simulate_concurrent_close():
    """What `close ticket` does to specs/current while this batch reads it.

    The utime call is not decoration: promotion copies with shutil.copy2, which
    preserves the source mtime, so the rewritten file legitimately carries a
    timestamp from before the run started.
    """
    target = SPEC_DIR / "adapters.py"
    target.write_text(target.read_text(encoding="utf-8") + "\\n# promoted mid-run\\n", encoding="utf-8")
    os.utime(target, (1000000, 1000000))


class SubmitAdapter:
    def run(self, case, work_dir=None):
        {mutate}
        return CaseRunResult(output=case.output)


class RequestStateProjector:
    def observe(self, ctx):
        return {projection}
'''

BINDINGS = """\
[external]
production_package = "program_under_test"

[external.port_bindings]
RequestPort = "real"

[actions.Submit]
view = "external"
channel = "http"
layer = "external"
controllability = "e2e_direct"
adapter = "adapters:SubmitAdapter"
projector = "adapters:RequestStateProjector"
kind = "request-http"
"""


def _spec_tree(tmp_path: Path, *, mutates: bool, cases_pass: bool) -> tuple[Path, Path]:
    spec = tmp_path / "current"
    spec.mkdir(parents=True)
    render_python_package(
        module="Program",
        states={"0": {"status": "pending"}, "1": {"status": "completed"}},
        edges=[Edge("0", "1", "Submit")],
        package_dir=spec / "external_cases",
        view="external",
        action_metadata={"Submit": ActionMetadata("Submit", "external", "e2e_direct", ("testgraph",))},
    )
    (spec / "adapters.py").write_text(
        ADAPTERS_TEMPLATE.format(
            mutate="_simulate_concurrent_close()" if mutates else "pass",
            projection='{"status": "completed"}' if cases_pass else '{"status": "wrong"}',
        ),
        encoding="utf-8",
    )
    mapping = spec / "bindings.toml"
    mapping.write_text(BINDINGS, encoding="utf-8")
    return spec, mapping


def _run(tmp_path: Path, spec: Path, mapping: Path) -> tuple[subprocess.CompletedProcess, Path]:
    digest_out = tmp_path / "reports" / "spec-input-digest.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_generated_case_adapters.py"),
            str(spec / "external_cases"),
            "--mapping",
            str(mapping),
            "--view",
            "external",
            "--batch",
            "--work-dir",
            str(tmp_path / "work"),
            "--import-root",
            str(spec),
            "--input-digest-out",
            str(digest_out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    return completed, digest_out


def test_a_quiescent_spec_tree_runs_clean_and_records_a_stable_digest(tmp_path: Path) -> None:
    """The positive control.

    Without it every assertion below could be satisfied by a guard that fires
    unconditionally, which would be worse than the defect.
    """
    spec, mapping = _spec_tree(tmp_path, mutates=False, cases_pass=True)

    completed, digest_out = _run(tmp_path, spec, mapping)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert INPUTS_CHANGED_SENTINEL not in completed.stdout + completed.stderr
    record = json.loads(digest_out.read_text(encoding="utf-8"))
    assert record["stable"] is True
    assert record["changed"] == []
    assert record["before"] == record["after"]
    assert record["specDir"] == str(spec.resolve())


def test_real_case_failures_are_still_case_failures(tmp_path: Path) -> None:
    """The other half of the control: the guard must not swallow a real defect."""
    spec, mapping = _spec_tree(tmp_path, mutates=False, cases_pass=False)

    completed, digest_out = _run(tmp_path, spec, mapping)
    output = completed.stdout + completed.stderr

    assert completed.returncode != 0
    assert completed.returncode != INPUTS_CHANGED_EXIT_CODE
    assert "projected state mismatch" in output
    assert INPUTS_CHANGED_SENTINEL not in output
    assert json.loads(digest_out.read_text(encoding="utf-8"))["stable"] is True


def test_a_tree_rewritten_mid_run_fails_with_a_named_reason(tmp_path: Path) -> None:
    spec, mapping = _spec_tree(tmp_path, mutates=True, cases_pass=True)

    completed, digest_out = _run(tmp_path, spec, mapping)
    output = completed.stdout + completed.stderr

    assert completed.returncode == INPUTS_CHANGED_EXIT_CODE, output
    assert INPUTS_CHANGED_SENTINEL in output
    assert "adapters.py" in output
    record = json.loads(digest_out.read_text(encoding="utf-8"))
    assert record["stable"] is False
    assert record["changed"] == ["adapters.py"]
    assert record["before"] != record["after"]


def test_the_named_reason_wins_over_the_case_failures_it_caused(tmp_path: Path) -> None:
    """THE FINDING.

    MO-005's record was red with six case failures while its inputs were being
    replaced underneath it. Case failures are what a mid-run rewrite LOOKS
    like, so reporting them as a program/model disagreement is the defect --
    the run must name the input change instead, and it can only do that if the
    digest is re-checked on the failure path before the failure propagates.
    """
    spec, mapping = _spec_tree(tmp_path, mutates=True, cases_pass=False)

    completed, digest_out = _run(tmp_path, spec, mapping)
    output = completed.stdout + completed.stderr

    assert completed.returncode == INPUTS_CHANGED_EXIT_CODE, output
    assert INPUTS_CHANGED_SENTINEL in output
    assert json.loads(digest_out.read_text(encoding="utf-8"))["stable"] is False
