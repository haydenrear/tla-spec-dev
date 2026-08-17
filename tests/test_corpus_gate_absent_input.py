"""SS-05. THE CORPUS GATE HAS THREE MORE ENTRANCES THAN `CA-06-DF-05` NAMED.

`CA-10-DF-19`. `CA-06-DF-05` was filed about `passed = not over_cap`, so an empty
corpus always passes. The sweep found three separate ways in, and each is
repaired here with its own demonstrated case:

1. **`load_corpus` accepted an empty GENERATED PACKAGE while refusing an empty
   TRACE DIRECTORY eight lines below it.** `cases.py` carrying `CASES = []`
   returned `[]` and the gate printed `corpus gate PASS: 0 internal case(s)` at
   exit 0, while a trace directory with no JSON in it raised
   `no generated cases or trace JSON files`. That asymmetry is the sink
   `CA-06-DF-01` drained into: the generator emitted `CASES = []` and this
   accepted it. The refusal to copy was already in the same function.

2. **The cap was printed as though it had been measured when it was a default.**
   `analyze_corpus` called `load_budgets(Path("__missing__"), warn=False)` when no
   `spec_manifest.yaml` was found above the corpus, which suppresses
   `budgets.py`'s own *"no readable spec manifest"* warning at exactly the point
   where it decides the verdict, and the report printed
   `cap max_external_cases_per_action = 50` with nothing saying the 50 was a
   documented fallback rather than the project's negotiated 10.

3. **An unattributable corpus was gated at the INTERNAL cap.** `view = args.view
   or package_view or "internal"`, and `infer_view` returns `None` when the
   package declares no `SOURCE_VIEW` and no directory name matches -- so an
   EXTERNAL corpus was capped at 200 instead of 50 and a 120-case external corpus
   PASSED AT FOUR TIMES ITS REAL CAP.

The correct answer to each is a refusal, and in each case the refusal that was
missing was already written somewhere else in the same file or the same package.

NON-VACUITY. A real generated corpus must still be measured and must still pass,
or these three refusals would have replaced a false PASS with a gate that refuses
everything.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import corpus_diagnostics as CD  # noqa: E402


# ---------------------------------------------------------------------------
# Entrance 1: an empty generated package
# ---------------------------------------------------------------------------


def write_package(directory: Path, body: str) -> Path:
    """A generated case package in the shape the toolchain actually emits.

    `load_cases` imports the PACKAGE, so `CASES` and `SOURCE_VIEW` must be
    re-exported from `__init__.py` exactly as a real generated package does --
    see `examples/distributed_history/specs/generated/spec_unit/
    ecommerce_internal_cases/__init__.py`. Writing them into `cases.py` alone
    made the fixture unlike every real subject, which is how the first draft of
    this file failed for a reason that had nothing to do with the repair.
    """
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "cases.py").write_text(body, encoding="utf-8")
    exports = ["CASES"]
    if "SOURCE_VIEW" in body:
        exports.append("SOURCE_VIEW")
    (directory / "__init__.py").write_text(
        f"from .cases import {', '.join(exports)}\n"
        f"__all__ = {exports!r}\n",
        encoding="utf-8",
    )
    return directory


def test_an_empty_generated_package_now_refuses(tmp_path) -> None:
    """`CASES = []`. Before: `corpus gate PASS: 0 internal case(s)`, exit 0."""
    pkg = write_package(tmp_path / "pkg" / "empty_cases",
                        "SOURCE_VIEW = 'internal'\nCASES = []\n")
    with pytest.raises(SystemExit) as excinfo:
        CD.load_corpus(pkg)
    message = str(excinfo.value)
    assert "UNDECIDED [empty]" in message
    assert "CASES = []" in message
    assert "never generated" in message


def test_the_empty_TRACE_directory_still_refuses_in_ITS_OWN_WORDS(tmp_path) -> None:
    """The half that already refused must keep refusing, and the two states must
    not collapse into one message -- an empty package and an empty trace
    directory are different facts about different inputs."""
    empty_dir = tmp_path / "traces"
    empty_dir.mkdir()
    with pytest.raises(SystemExit) as trace_exc:
        CD.load_corpus(empty_dir)

    pkg = write_package(tmp_path / "pkg2" / "empty_cases",
                        "SOURCE_VIEW = 'internal'\nCASES = []\n")
    with pytest.raises(SystemExit) as pkg_exc:
        CD.load_corpus(pkg)

    assert "no generated cases or trace JSON files" in str(trace_exc.value)
    assert str(trace_exc.value) != str(pkg_exc.value)


# ---------------------------------------------------------------------------
# Entrance 2: the cap's provenance
# ---------------------------------------------------------------------------


def test_a_defaulted_cap_is_LABELLED_a_default_on_the_page() -> None:
    """No manifest above the corpus -> the report says the cap is a fallback.

    Before, the same run printed the number with nothing beside it, and a number
    whose provenance is not on the page is read as measured.
    """
    report = CD.analyze_corpus([], view="external", manifest_path=None,
                               source="a corpus with no manifest above it")
    assert report.cap_from_manifest is False
    rendered = CD.render_report(report)
    assert "cap provenance: DOCUMENTED DEFAULT" in rendered
    assert "NOT this project's negotiated cap" in rendered
    assert "CA-10-DF-19" in rendered


def test_a_cap_read_from_a_real_manifest_is_NOT_labelled_a_default() -> None:
    """NON-VACUITY on the label. The subject is this repository's own shipped
    `ex4_pipeline_coherent` manifest, which negotiates its caps explicitly and
    records the rationale."""
    manifest = (ROOT / "examples" / "validation" / "ex4_pipeline_coherent"
                / "specs" / "program_model" / "spec_manifest.yaml")
    assert manifest.is_file()
    report = CD.analyze_corpus([], view="internal", manifest_path=manifest)
    assert report.cap_from_manifest is True
    assert "cap provenance" not in CD.render_report(report)


# ---------------------------------------------------------------------------
# Entrance 3: an unattributable corpus
# ---------------------------------------------------------------------------


class _Args:
    def __init__(self, cases_dir, view=None, manifest=None):
        self.cases_dir = cases_dir
        self.view = view
        self.manifest = manifest


def test_a_corpus_that_declares_no_view_refuses_instead_of_defaulting(tmp_path, capsys) -> None:
    """THE 4x CAP. Before: gated at the internal cap of 200 rather than the
    external 50, so a 120-case external corpus passed.

    The package declares no `SOURCE_VIEW`, its cases carry no `view`/`layer`, and
    no directory on its path is named `spec-unit`/`spec_unit`/`testgraph`.
    """
    pkg = write_package(tmp_path / "nowhere" / "mystery_cases",
                        "CASES = [{'name': 'c1'}, {'name': 'c2'}]\n")
    assert CD.infer_view(pkg, [{"name": "c1"}]) is None, "the fixture is stale"

    code = CD.run(_Args(str(pkg)))
    captured = capsys.readouterr()
    assert code == CD.EXIT_USAGE
    assert "UNDECIDED [empty]" in captured.err
    assert "WHICH CAP APPLIES IS UNKNOWN" in captured.err
    assert "four times their real cap" in captured.err


def test_an_explicit_view_still_decides_the_run(tmp_path, capsys) -> None:
    """NON-VACUITY, and the escape the refusal must leave open: `--view` names the
    cap, so the same corpus is measured rather than refused."""
    pkg = write_package(tmp_path / "nowhere2" / "mystery_cases",
                        "CASES = [{'name': 'c1'}, {'name': 'c2'}]\n")
    code = CD.run(_Args(str(pkg), view="external"))
    captured = capsys.readouterr()
    assert code == CD.EXIT_OK, captured.out + captured.err
    assert "corpus gate PASS: 2 external case(s)" in captured.out


def test_a_declared_view_in_the_package_is_still_honoured(tmp_path, capsys) -> None:
    """The ordinary path, which is the one every shipped corpus takes."""
    pkg = write_package(tmp_path / "declared" / "internal_cases",
                        "SOURCE_VIEW = 'internal'\nCASES = [{'name': 'c1'}]\n")
    code = CD.run(_Args(str(pkg)))
    captured = capsys.readouterr()
    assert code == CD.EXIT_OK, captured.out + captured.err
    assert "1 internal case(s)" in captured.out
