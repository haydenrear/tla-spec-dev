"""The reflexion check measures production code against the model's architecture.

The properties these tests hold, in order of how much damage their absence
would do:

1. **A refusal beats a false clean (MF-027).** Everything the check cannot see
   makes the verdict ``unmappable``: a model with no architecture, a module the
   map does not place, a component no module realizes, a dynamic edge, an
   unparsed file, and an architecture whose ports permit every pair. Under all
   of them a clean report would be indistinguishable from a real one.
2. **Nothing downgrades ``unmappable``.** No flag, key, annotation, or
   environment variable turns it into ``coherent``. There is deliberately no
   test that an opt-out works, because no opt-out exists -- the
   ``TestNothingDowngradesAnUnobservableVerdict`` shape from
   ``tests/test_effect_conformance.py``.
3. **A positive case exists.** A model that decomposes, with code that matches
   it, reports ``coherent`` and zero divergences -- otherwise the check would
   be validated only for refusing, and "always unmappable" would pass every
   test above.
4. **Divergences carry ``file:line``.** A finding a reader cannot navigate to
   is an opinion.
5. **Advisory, never blocking.** Exit 0 on divergence and on unmappable.
   Nonzero ONLY when the map or the extraction is unusable.
6. **Declared, never inferred (CD-01 and the AC-02 rule).** The tool reads the
   map. It never writes one, and it never says where a module should live.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest  # noqa: E402

from scripts.analyze_architecture import EXIT_PASS, EXIT_USAGE, analyze  # noqa: E402
from scripts.architecture_reflexion import (  # noqa: E402
    SCHEMA,
    SCHEMA_VERSION,
    VERDICT_COHERENT,
    VERDICT_DIVERGENT,
    VERDICT_UNMAPPABLE,
    CodeExtractionError,
    ReflexionMapError,
    extract_python_graph,
    reflexion,
    report_payload,
    run_reflexion,
)

# --------------------------------------------------------------------------
# Fixtures: a model that genuinely decomposes, and code for it
# --------------------------------------------------------------------------

# Three components in a line. `Parse` touches ingest+transform and `Ship`
# touches transform+deliver, so there are ports for those two pairs -- and NO
# action touches raw and shipped, so `ingest <-> deliver` has no port. That
# third pair is what makes a divergence detectable at all: without an unported
# pair, "no divergences" would be a property of the architecture rather than a
# measurement of the code.
PIPELINE_TLA = """----------------------------- MODULE Pipeline -----------------------------
EXTENDS Naturals

VARIABLES raw, parsed, shipped

vars == << raw, parsed, shipped >>

Init ==
  /\\ raw = 0
  /\\ parsed = 0
  /\\ shipped = 0

Ingest ==
  /\\ raw < 2
  /\\ raw' = raw + 1
  /\\ UNCHANGED << parsed, shipped >>

Parse ==
  /\\ raw > 0
  /\\ raw' = raw - 1
  /\\ parsed' = parsed + 1
  /\\ UNCHANGED shipped

Ship ==
  /\\ parsed > 0
  /\\ parsed' = parsed - 1
  /\\ shipped' = shipped + 1
  /\\ UNCHANGED raw

Reset ==
  /\\ shipped > 1
  /\\ shipped' = 0
  /\\ UNCHANGED << raw, parsed >>

Next == Ingest \\/ Parse \\/ Ship \\/ Reset

Spec == Init /\\ [][Next]_vars
===========================================================================
"""

PIPELINE_CFG = """SPECIFICATION Spec
"""

# The declared component partition (AC-01's `--components` shape).
PIPELINE_COMPONENTS = """architecture:
  components:
    - name: ingest
      variables:
        - raw
    - name: transform
      variables:
        - parsed
    - name: deliver
      variables:
        - shipped
"""

COHERENT_MAP = """architecture_map:
  language: python
  components:
    - component: ingest
      modules:
        - ingest.py
    - component: transform
      modules:
        - transform.py
    - component: deliver
      modules:
        - deliver.py
"""

INGEST_PY = """\
\"\"\"Reads raw records.\"\"\"


def read_raw():
    return ["a", "b"]
"""

TRANSFORM_PY = """\
\"\"\"Parses raw records. Reaches ingest, which the model's Parse action ports.\"\"\"
from ingest import read_raw


def parse():
    return [r.upper() for r in read_raw()]
"""

DELIVER_PY = """\
\"\"\"Ships parsed records. Reaches transform, which the model's Ship action ports.\"\"\"
from transform import parse


def ship():
    return list(parse())
"""

# The same tree with one extra edge: deliver reaches ingest directly. No action
# of the model touches raw and shipped, so no port declares that pair.
DELIVER_PY_DIVERGENT = """\
\"\"\"Ships parsed records -- and reaches straight into ingest.\"\"\"
from transform import parse
from ingest import read_raw


def ship():
    return list(parse())


def peek():
    return read_raw()
"""


def write_project(root: Path, *, deliver: str = DELIVER_PY, extras: dict[str, str] | None = None) -> Path:
    """Write the fixture spec, declared partition, map, and code tree."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "Pipeline.tla").write_text(PIPELINE_TLA, encoding="utf-8")
    (root / "Pipeline.cfg").write_text(PIPELINE_CFG, encoding="utf-8")
    (root / "components.yaml").write_text(PIPELINE_COMPONENTS, encoding="utf-8")
    (root / "map.yaml").write_text(COHERENT_MAP, encoding="utf-8")
    code = root / "pkg"
    code.mkdir(exist_ok=True)
    (code / "ingest.py").write_text(INGEST_PY, encoding="utf-8")
    (code / "transform.py").write_text(TRANSFORM_PY, encoding="utf-8")
    (code / "deliver.py").write_text(deliver, encoding="utf-8")
    for name, text in (extras or {}).items():
        target = code / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return code


def descriptor_for(root: Path, *, declared: bool = True):
    return analyze(
        root / "Pipeline.tla",
        root / "Pipeline.cfg",
        None,
        components_path=(root / "components.yaml") if declared else None,
    )


def check(root: Path, *, declared: bool = True, map_name: str = "map.yaml"):
    return run_reflexion(
        descriptor_for(root, declared=declared), str(root / "pkg"), str(root / map_name)
    )


@pytest.fixture()
def project(tmp_path: Path) -> Path:
    write_project(tmp_path)
    return tmp_path


def cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "tla_spec_dev.py"),
         "--spec-root", "specs", "analyze", "architecture", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


# --------------------------------------------------------------------------
# 1. The positive case -- without it the check is validated only for refusing
# --------------------------------------------------------------------------


class TestCodeThatMatchesTheArchitecture:
    def test_a_matching_tree_is_coherent(self, project: Path) -> None:
        report = check(project)
        assert report.verdict == VERDICT_COHERENT, report.reasons
        assert report.divergences == []
        assert report.absences == []
        assert report.blind_spots == []

    def test_the_crossing_edges_are_reported_as_convergences_with_their_port(
        self, project: Path
    ) -> None:
        report = check(project)
        pairs = {(row["from_component"], row["to_component"]) for row in report.convergences}
        assert pairs == {("transform", "ingest"), ("deliver", "transform")}
        for row in report.convergences:
            assert row["port"], "a convergence names the port that declares it"
            assert row["port_actions"], "and the model actions that cross it"

    def test_every_declared_port_is_realized_so_there_are_no_absences(
        self, project: Path
    ) -> None:
        report = check(project)
        assert {tuple(p) for p in report.port_pairs} == {
            ("ingest", "transform"),
            ("deliver", "transform"),
        }
        assert report.absences == []

    def test_a_divergence_was_possible_here(self, project: Path) -> None:
        """The positive result means something only because the architecture
        forbids something. ingest <-> deliver has no port; an edge across it
        would have been a divergence, and the next test shows it is."""
        report = check(project)
        assert report.unported_pairs == [("deliver", "ingest")]
        assert report.divergence_detectable is True


# --------------------------------------------------------------------------
# 2. Divergence -- the finding, with file:line
# --------------------------------------------------------------------------


class TestCodeThatViolatesTheArchitecture:
    @pytest.fixture()
    def divergent(self, tmp_path: Path) -> Path:
        write_project(tmp_path, deliver=DELIVER_PY_DIVERGENT)
        return tmp_path

    def test_the_unported_edge_is_a_divergence(self, divergent: Path) -> None:
        report = check(divergent)
        assert report.verdict == VERDICT_DIVERGENT
        pairs = {(row["from_component"], row["to_component"]) for row in report.divergences}
        assert pairs == {("deliver", "ingest")}

    def test_every_divergent_edge_carries_file_and_line(self, divergent: Path) -> None:
        report = check(divergent)
        assert report.divergences
        for row in report.divergences:
            assert row["file"].endswith("deliver.py")
            assert isinstance(row["line"], int) and row["line"] > 0
            assert row["site"] == f"{row['file']}:{row['line']}"
            source = Path(row["file"]).read_text(encoding="utf-8").splitlines()
            # The site is navigable: the named line really carries the dependency.
            assert row["symbol"].rsplit(".", 1)[-1] in source[row["line"] - 1]

    def test_both_the_import_and_the_call_site_are_reported(self, divergent: Path) -> None:
        report = check(divergent)
        kinds = {row["kind"] for row in report.divergences}
        assert kinds == {"import", "call"}, (
            "the import declares the dependency and the call exercises it; a check that "
            "reported only one of them would miss either an unused import or a call "
            "through a re-exported name"
        )

    def test_the_convergent_edges_are_still_convergent(self, divergent: Path) -> None:
        report = check(divergent)
        assert {(r["from_component"], r["to_component"]) for r in report.convergences} == {
            ("transform", "ingest"),
            ("deliver", "transform"),
        }

    def test_divergence_exits_zero(self, tmp_path: Path) -> None:
        """Advisory: a divergent codebase is a FINDING, not a failure."""
        write_project(tmp_path, deliver=DELIVER_PY_DIVERGENT)
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "architecture_reflexion.py"),
             str(tmp_path / "Pipeline.tla"), str(tmp_path / "Pipeline.cfg"),
             "--components", str(tmp_path / "components.yaml"),
             "--code", str(tmp_path / "pkg"), "--map", str(tmp_path / "map.yaml")],
            capture_output=True, text=True,
        )
        assert result.returncode == EXIT_PASS, result.stderr
        assert "architecture_scan = divergent" in result.stdout

    def test_the_report_names_no_move(self, divergent: Path) -> None:
        """CD-01: edges and facts, never 'extract a module'."""
        from scripts.architecture_reflexion import render_report_text

        text = render_report_text(check(divergent)).lower()
        for banned in ("you should", "recommend", "consider moving", "extract a module",
                       "refactor", "suggested", "instead of"):
            assert banned not in text, f"the report suggests a move: {banned!r}"


# --------------------------------------------------------------------------
# 3. Absence -- a declared port no code edge realizes
# --------------------------------------------------------------------------


class TestDeadArchitecture:
    def test_a_port_no_code_edge_realizes_is_an_absence(self, tmp_path: Path) -> None:
        write_project(tmp_path, deliver='"""Ships nothing yet."""\n\n\ndef ship():\n    return []\n')
        report = check(tmp_path)
        assert [row["between"] for row in report.absences] == [["deliver", "transform"]]
        assert report.divergences == []
        assert report.verdict == VERDICT_DIVERGENT, (
            "an unrealized port is a finding about the pair, not a clean result"
        )

    def test_the_absence_names_the_model_actions_that_cross_the_port(
        self, tmp_path: Path
    ) -> None:
        write_project(tmp_path, deliver='"""Ships nothing yet."""\n')
        report = check(tmp_path)
        assert report.absences[0]["actions"] == ["Ship"]


# --------------------------------------------------------------------------
# 4. The refusal -- everything the check cannot see
# --------------------------------------------------------------------------


class TestARefusalBeatsAFalseClean:
    def test_a_model_with_no_architecture_is_unmappable_not_coherent(
        self, project: Path
    ) -> None:
        """The branch AC-01 published `consumable_as_architecture` for.

        Run without the declared partition the Pipeline model clusters into one
        component. Every code edge is then internal to it, so the diff would
        find zero divergences and zero absences -- a flawless reflexion report
        for a model with no boundary in it.
        """
        descriptor = descriptor_for(project, declared=False)
        assert descriptor.consumable_as_architecture is False
        report = reflexion(descriptor, {}, project / "pkg", "unused")
        assert report.verdict == VERDICT_UNMAPPABLE
        assert [s.kind for s in report.blind_spots] == ["model_has_no_architecture"]
        assert "not about the code" in report.blind_spots[0].detail

    def test_a_module_the_map_does_not_place_is_unmappable(self, tmp_path: Path) -> None:
        """The map cannot cover only the tidy half of a tree."""
        write_project(tmp_path, extras={"stray.py": "from ingest import read_raw\n"})
        report = check(tmp_path)
        assert report.verdict == VERDICT_UNMAPPABLE
        assert report.unmapped_modules == ["stray.py"]
        assert "unmapped_module" in {s.kind for s in report.blind_spots}

    def test_a_component_no_module_realizes_is_unmappable(self, tmp_path: Path) -> None:
        write_project(tmp_path)
        (tmp_path / "partial.yaml").write_text(
            textwrap.dedent(
                """\
                architecture_map:
                  components:
                    - component: ingest
                      modules:
                        - ingest.py
                    - component: transform
                      modules:
                        - transform.py
                        - deliver.py
                """
            ),
            encoding="utf-8",
        )
        report = check(tmp_path, map_name="partial.yaml")
        assert report.verdict == VERDICT_UNMAPPABLE
        assert report.unrealized_components == ["deliver"]

    def test_a_dynamic_import_is_unmappable(self, tmp_path: Path) -> None:
        write_project(
            tmp_path,
            deliver=(
                "import importlib\n"
                "from transform import parse\n\n\n"
                "def ship(name):\n"
                "    return importlib.import_module(name).parse()\n"
            ),
        )
        report = check(tmp_path)
        assert report.verdict == VERDICT_UNMAPPABLE
        assert "dynamic_import" in {s.kind for s in report.blind_spots}

    def test_a_literal_dynamic_import_is_an_edge_not_a_blind_spot(
        self, tmp_path: Path
    ) -> None:
        """Honesty in both directions: what CAN be resolved is resolved."""
        write_project(
            tmp_path,
            deliver=(
                "import importlib\n\n\n"
                "def ship():\n"
                "    return importlib.import_module('ingest').read_raw()\n"
            ),
        )
        report = check(tmp_path)
        assert "dynamic_import" not in {s.kind for s in report.blind_spots}
        assert any(row["kind"] == "dynamic-import" for row in report.divergences)

    def test_a_file_that_will_not_parse_is_unmappable(self, tmp_path: Path) -> None:
        write_project(tmp_path, extras={"broken.py": "def (:\n"})
        (tmp_path / "map.yaml").write_text(
            COHERENT_MAP.replace("        - deliver.py", "        - deliver.py\n        - broken.py"),
            encoding="utf-8",
        )
        report = check(tmp_path)
        assert report.verdict == VERDICT_UNMAPPABLE
        assert "unparsed_file" in {s.kind for s in report.blind_spots}

    def test_a_non_python_file_in_the_tree_is_unmappable(self, tmp_path: Path) -> None:
        """Python-only is a coverage limit, and a limit that is silent is a lie."""
        write_project(tmp_path, extras={"Verify.java": "class Verify {}\n"})
        report = check(tmp_path)
        assert report.verdict == VERDICT_UNMAPPABLE
        assert "non_python_file" in {s.kind for s in report.blind_spots}

    def test_an_architecture_that_permits_every_pair_is_unmappable(
        self, tmp_path: Path
    ) -> None:
        """The structural twin of a clean report from a sandbox that saw nothing.

        With a port between every component pair, no code edge could have been a
        divergence. Zero divergences is then a property of the declared
        architecture rather than a measurement of the code, and this is exactly
        what a model whose actions all touch the same variables produces under
        ANY partition -- including this repository's own.
        """
        write_project(tmp_path)
        (tmp_path / "two.yaml").write_text(
            "architecture:\n"
            "  components:\n"
            "    - name: front\n"
            "      variables:\n"
            "        - raw\n"
            "        - parsed\n"
            "    - name: back\n"
            "      variables:\n"
            "        - shipped\n",
            encoding="utf-8",
        )
        (tmp_path / "two_map.yaml").write_text(
            "architecture_map:\n"
            "  components:\n"
            "    - component: front\n"
            "      modules:\n"
            "        - ingest.py\n"
            "        - transform.py\n"
            "    - component: back\n"
            "      modules:\n"
            "        - deliver.py\n",
            encoding="utf-8",
        )
        report = run_reflexion(
            analyze(
                tmp_path / "Pipeline.tla",
                tmp_path / "Pipeline.cfg",
                None,
                components_path=tmp_path / "two.yaml",
            ),
            str(tmp_path / "pkg"),
            str(tmp_path / "two_map.yaml"),
        )
        assert report.divergences == []
        assert report.divergence_detectable is False
        assert report.verdict == VERDICT_UNMAPPABLE
        assert "unfalsifiable_coherence" in {s.kind for s in report.blind_spots}

    def test_findings_are_still_reported_under_an_unmappable_verdict(
        self, tmp_path: Path
    ) -> None:
        """`unmappable` is not `nothing found`."""
        write_project(
            tmp_path,
            deliver=DELIVER_PY_DIVERGENT,
            extras={"stray.py": "x = 1\n"},
        )
        report = check(tmp_path)
        assert report.verdict == VERDICT_UNMAPPABLE
        assert report.divergences, "the divergence survives the refusal"
        assert any("deliver.py" in row["file"] for row in report.divergences)


# --------------------------------------------------------------------------
# 5. Nothing downgrades an unmappable verdict
# --------------------------------------------------------------------------


class TestNothingDowngradesAnUnobservableVerdict:
    """The regression guard, in the shape ``tests/test_effect_conformance.py`` uses.

    Every test asserts the NEGATIVE: some plausible opt-out does NOT turn an
    unmappable verdict into a clean one. There is deliberately no test that an
    opt-out works, because no opt-out exists. The "helpful" instinct here is to
    let a project whose tree the extractor cannot fully resolve declare its way
    to `coherent`; that opt-out is the silence this check exists to remove.
    """

    def _report_with(self, tmp_path: Path, extra_map: str = "") -> object:
        # Baseline: a tree with a module the map does not place, plus a real
        # divergence. Both survive every mutation below.
        write_project(tmp_path, deliver=DELIVER_PY_DIVERGENT, extras={"stray.py": "x = 1\n"})
        (tmp_path / "map.yaml").write_text(COHERENT_MAP + extra_map, encoding="utf-8")
        return check(tmp_path)

    def test_baseline_is_unmappable(self, tmp_path: Path) -> None:
        report = self._report_with(tmp_path)
        assert report.verdict == VERDICT_UNMAPPABLE

    @pytest.mark.parametrize(
        "block",
        [
            "  assume_mapped: true\n",
            "  allow_unmapped: true\n",
            "  assume_coherent: true\n",
            "  allow_divergences: true\n",
            "  accepted_divergences:\n    - deliver.py -> ingest.py\n",
            "  known_divergences:\n    - deliver.py -> ingest.py\n",
            "  expected_divergences:\n    - deliver.py -> ingest.py\n",
            "  waived: true\n",
            "  waiver: reviewed by the architect on 2026-07-27\n",
            "  suppress: true\n",
            "  ignore:\n    - stray.py\n",
            "  exclude:\n    - stray.py\n",
            "  skip:\n    - stray.py\n",
            "  trusted: true\n",
            "  override: coherent\n",
            "  justification: the stray module is a script, not a component\n",
        ],
    )
    def test_no_map_key_downgrades_the_verdict(self, tmp_path: Path, block: str) -> None:
        report = self._report_with(tmp_path, block)
        assert report.verdict == VERDICT_UNMAPPABLE
        assert report.unmapped_modules == ["stray.py"]
        assert report.divergences, "and the divergence is still reported"

    def test_suppression_shaped_keys_are_recorded_loudly(self, tmp_path: Path) -> None:
        """A silently ignored key is nearly as bad as an honored one: the author
        believes the finding was waived."""
        report = self._report_with(tmp_path, "  waived: true\n  justification: reviewed\n")
        assert set(report.ignored_suppression_keys) == {
            "architecture_map.waived",
            "architecture_map.justification",
        }
        from scripts.architecture_reflexion import render_report_text

        text = render_report_text(report)
        assert "IGNORED suppression-shaped keys" in text
        assert "never honored" in text

    def test_the_verdict_is_identical_with_and_without_every_key(
        self, tmp_path: Path
    ) -> None:
        plain = report_payload(self._report_with(tmp_path / "a"))
        loaded = report_payload(
            self._report_with(
                tmp_path / "b",
                "  assume_coherent: true\n  waived: true\n  allow_unmapped: true\n",
            )
        )
        del plain["map"], loaded["map"]
        del plain["code_root"], loaded["code_root"]
        plain_keys = plain.pop("ignored_suppression_keys")
        loaded_keys = loaded.pop("ignored_suppression_keys")
        assert plain_keys == [] and len(loaded_keys) == 3
        assert json.dumps(_strip_paths(plain)) == json.dumps(_strip_paths(loaded))

    @pytest.mark.parametrize(
        "name",
        [
            "TLA_SPEC_DEV_ARCHITECTURE_COHERENT",
            "TLA_SPEC_DEV_ALLOW_UNMAPPED",
            "ARCHITECTURE_SCAN",
            "TLA_SPEC_DEV_SKIP_ARCHITECTURE",
        ],
    )
    def test_no_environment_variable_downgrades_the_verdict(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
    ) -> None:
        monkeypatch.setenv(name, "1")
        report = self._report_with(tmp_path)
        assert report.verdict == VERDICT_UNMAPPABLE

    @pytest.mark.parametrize(
        "flag",
        ["--assume-coherent", "--allow-unmapped", "--force-coherent", "--ignore-unmappable"],
    )
    def test_no_command_line_flag_downgrades_the_verdict(self, flag: str) -> None:
        result = cli("specs/program_model/TlaSpecDevCli.tla", flag)
        assert result.returncode != EXIT_PASS
        assert "unrecognized arguments" in result.stderr or "error:" in result.stderr

    def test_the_verdict_property_reads_nothing_but_the_report(self) -> None:
        """Structural guard: the code that decides the verdict has no input to game."""
        import inspect

        from scripts.architecture_reflexion import ReflexionReport

        source = inspect.getsource(ReflexionReport.verdict.fget)
        for banned in ("os.environ", "getenv", "config", "options", "args", "allow", "assume"):
            assert banned not in source, f"the verdict consults {banned!r}"


def _strip_paths(payload: dict) -> dict:
    """Remove absolute-path noise so two runs in different tmp dirs compare."""
    text = json.dumps(payload)
    return json.loads(text.replace("/a/", "/X/").replace("/b/", "/X/"))


# --------------------------------------------------------------------------
# 6. Declared, never inferred -- and an unusable map is refused
# --------------------------------------------------------------------------


class TestTheMapIsDeclaredAndNeverInvented:
    def test_a_map_naming_a_component_the_model_lacks_is_refused(
        self, tmp_path: Path
    ) -> None:
        write_project(tmp_path)
        (tmp_path / "map.yaml").write_text(
            COHERENT_MAP.replace("component: deliver", "component: shipping"), encoding="utf-8"
        )
        with pytest.raises(ReflexionMapError) as excinfo:
            check(tmp_path)
        assert "the model does not have" in str(excinfo.value)

    def test_a_map_entry_naming_no_file_is_refused(self, tmp_path: Path) -> None:
        write_project(tmp_path)
        (tmp_path / "map.yaml").write_text(
            COHERENT_MAP.replace("- deliver.py", "- deliver.py\n        - gone.py"),
            encoding="utf-8",
        )
        with pytest.raises(ReflexionMapError) as excinfo:
            check(tmp_path)
        assert "does not exist" in str(excinfo.value)

    def test_a_module_mapped_to_two_components_is_refused(self, tmp_path: Path) -> None:
        write_project(tmp_path)
        (tmp_path / "map.yaml").write_text(
            COHERENT_MAP.replace("- deliver.py", "- deliver.py\n        - ingest.py"),
            encoding="utf-8",
        )
        with pytest.raises(ReflexionMapError) as excinfo:
            check(tmp_path)
        assert "must not overlap" in str(excinfo.value)

    def test_a_non_python_language_is_refused_not_reported_clean(
        self, tmp_path: Path
    ) -> None:
        """MF-027 at the language edge: no extractor means no measurement."""
        write_project(tmp_path)
        (tmp_path / "map.yaml").write_text(
            COHERENT_MAP.replace("language: python", "language: java"), encoding="utf-8"
        )
        with pytest.raises(ReflexionMapError) as excinfo:
            check(tmp_path)
        assert "no extractor in this build" in str(excinfo.value)

    def test_an_empty_code_tree_is_refused(self, tmp_path: Path) -> None:
        write_project(tmp_path)
        (tmp_path / "empty").mkdir()
        with pytest.raises(CodeExtractionError):
            run_reflexion(
                descriptor_for(tmp_path), str(tmp_path / "empty"), str(tmp_path / "map.yaml")
            )

    def test_the_map_reads_without_pyyaml(self, tmp_path: Path) -> None:
        """The CLI's interpreter frequently has no PyYAML (AC-01 hit this).

        The map must parse through ``scripts/extract_spec_manifest.py``'s
        dependency-free parser as well, or the check silently becomes
        unrunnable on the interpreter the CLI actually uses.
        """
        from scripts.extract_spec_manifest import parse_simple_yaml

        write_project(tmp_path)
        source = parse_simple_yaml(COHERENT_MAP)
        report = reflexion(descriptor_for(tmp_path), source, tmp_path / "pkg", "m.yaml")
        assert report.verdict == VERDICT_COHERENT

    def test_the_shipped_map_reads_without_pyyaml(self) -> None:
        from scripts.extract_spec_manifest import parse_simple_yaml

        text = (REPO_ROOT / "specs" / "program_model" / "architecture_map.yaml").read_text(
            encoding="utf-8"
        )
        parsed = parse_simple_yaml(text)["architecture_map"]
        assert {entry["component"] for entry in parsed["components"]} == {
            "surface",
            "tickets",
            "corpus",
            "kill",
        }


# --------------------------------------------------------------------------
# 7. Exit codes: advisory, never blocking
# --------------------------------------------------------------------------


class TestExitCodes:
    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "architecture_reflexion.py"), *args],
            capture_output=True,
            text=True,
        )

    def test_coherent_exits_zero(self, project: Path) -> None:
        result = self._run(
            str(project / "Pipeline.tla"), str(project / "Pipeline.cfg"),
            "--components", str(project / "components.yaml"),
            "--code", str(project / "pkg"), "--map", str(project / "map.yaml"),
        )
        assert result.returncode == EXIT_PASS, result.stderr
        assert "architecture_scan = coherent" in result.stdout

    def test_unmappable_exits_zero(self, tmp_path: Path) -> None:
        write_project(tmp_path, extras={"stray.py": "x = 1\n"})
        result = self._run(
            str(tmp_path / "Pipeline.tla"), str(tmp_path / "Pipeline.cfg"),
            "--components", str(tmp_path / "components.yaml"),
            "--code", str(tmp_path / "pkg"), "--map", str(tmp_path / "map.yaml"),
        )
        assert result.returncode == EXIT_PASS, result.stderr
        assert "architecture_scan = unmappable" in result.stdout

    def test_an_unusable_map_exits_nonzero(self, tmp_path: Path) -> None:
        write_project(tmp_path)
        result = self._run(
            str(tmp_path / "Pipeline.tla"), str(tmp_path / "Pipeline.cfg"),
            "--components", str(tmp_path / "components.yaml"),
            "--code", str(tmp_path / "pkg"), "--map", str(tmp_path / "missing.yaml"),
        )
        assert result.returncode == EXIT_USAGE
        assert "could not be run" in result.stderr

    def test_a_missing_code_root_exits_nonzero(self, tmp_path: Path) -> None:
        write_project(tmp_path)
        result = self._run(
            str(tmp_path / "Pipeline.tla"), str(tmp_path / "Pipeline.cfg"),
            "--components", str(tmp_path / "components.yaml"),
            "--code", str(tmp_path / "nope"), "--map", str(tmp_path / "map.yaml"),
        )
        assert result.returncode == EXIT_USAGE


# --------------------------------------------------------------------------
# 8. The extractor's own contract
# --------------------------------------------------------------------------


class TestTheExtractor:
    def test_imports_and_calls_are_separate_edge_kinds(self, project: Path) -> None:
        graph = extract_python_graph(project / "pkg")
        kinds = {(e.src, e.dst, e.kind) for e in graph.edges}
        assert ("transform.py", "ingest.py", "import") in kinds
        assert ("transform.py", "ingest.py", "call") in kinds

    def test_external_imports_are_not_edges_and_are_named(self, tmp_path: Path) -> None:
        write_project(tmp_path, extras={"ingest.py": "import json\nimport os\n\n\ndef read_raw():\n    return json.loads('[]')\n"})
        graph = extract_python_graph(tmp_path / "pkg")
        assert "json" in graph.external_imports and "os" in graph.external_imports
        assert not any(e.dst.startswith("json") for e in graph.edges)

    def test_relative_imports_resolve(self, tmp_path: Path) -> None:
        code = tmp_path / "tree"
        (code / "sub").mkdir(parents=True)
        (code / "a.py").write_text("VALUE = 1\n", encoding="utf-8")
        (code / "sub" / "__init__.py").write_text("", encoding="utf-8")
        (code / "sub" / "b.py").write_text("from ..a import VALUE\n", encoding="utf-8")
        graph = extract_python_graph(code)
        assert ("sub/b.py", "a.py") in {(e.src, e.dst) for e in graph.edges}

    def test_a_star_import_is_an_edge_and_a_blind_spot(self, tmp_path: Path) -> None:
        write_project(tmp_path, deliver="from transform import *\n")
        graph = extract_python_graph(tmp_path / "pkg")
        assert ("deliver.py", "transform.py") in {(e.src, e.dst) for e in graph.edges}
        assert "star_import" in {s.kind for s in graph.blind_spots}

    def test_getattr_into_an_in_tree_module_is_a_blind_spot(self, tmp_path: Path) -> None:
        write_project(
            tmp_path,
            deliver="import transform\n\n\ndef ship(name):\n    return getattr(transform, name)()\n",
        )
        graph = extract_python_graph(tmp_path / "pkg")
        assert "dynamic_attribute" in {s.kind for s in graph.blind_spots}

    def test_pycache_is_not_scanned(self, tmp_path: Path) -> None:
        code = write_project(tmp_path)
        (code / "__pycache__").mkdir()
        (code / "__pycache__" / "ingest.cpython-311.pyc").write_bytes(b"\x00")
        graph = extract_python_graph(code)
        assert graph.non_python_files == []
        assert sorted(graph.modules) == ["deliver.py", "ingest.py", "transform.py"]


# --------------------------------------------------------------------------
# 9. The machine-readable contract, and the CLI wiring
# --------------------------------------------------------------------------


class TestTheMachineReadableContract:
    def test_the_payload_is_versioned_and_separates_the_three_categories(
        self, tmp_path: Path
    ) -> None:
        write_project(tmp_path, deliver=DELIVER_PY_DIVERGENT)
        payload = report_payload(check(tmp_path))
        assert payload["schema"] == SCHEMA
        assert payload["schema_version"] == SCHEMA_VERSION
        assert set(payload) >= {"convergences", "divergences", "absences", "blind_spots"}
        assert payload["verdict"]["architecture_scan"] == VERDICT_DIVERGENT
        assert payload["verdict"]["blocks_promotion"] is False
        assert payload["advisory"]["suggests_moves"] is False

    def test_analyze_architecture_carries_the_reflexion_block(self, tmp_path: Path) -> None:
        write_project(tmp_path, deliver=DELIVER_PY_DIVERGENT)
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "analyze_architecture.py"),
             str(tmp_path / "Pipeline.tla"), str(tmp_path / "Pipeline.cfg"),
             "--components", str(tmp_path / "components.yaml"),
             "--code", str(tmp_path / "pkg"), "--map", str(tmp_path / "map.yaml"),
             "--format", "json"],
            capture_output=True, text=True,
        )
        assert result.returncode == EXIT_PASS, result.stderr
        payload = json.loads(result.stdout)
        assert payload["reflexion"]["schema"] == SCHEMA
        assert payload["verdict"]["architecture_scan"] == VERDICT_DIVERGENT
        # AC-01's descriptor fields are unchanged by the code side.
        assert payload["measured"]["partition"]["consumable_as_architecture"] is True

    def test_the_descriptor_is_unchanged_when_no_code_side_is_given(
        self, project: Path
    ) -> None:
        from scripts.analyze_architecture import descriptor_payload

        descriptor = descriptor_for(project)
        assert "reflexion" not in descriptor_payload(descriptor)
        assert descriptor_payload(descriptor)["verdict"]["architecture_scan"] == "unmappable"

    def test_half_a_reflexion_check_is_a_usage_error(self) -> None:
        result = cli("specs/program_model/TlaSpecDevCli.tla", "--code", "scripts")
        assert result.returncode == EXIT_USAGE
        assert "needs both --code and --map" in result.stderr


# --------------------------------------------------------------------------
# 10. The dogfood: this repository's own model and scripts/ tree
# --------------------------------------------------------------------------


def test_this_repository_reports_unmappable_for_a_model_reason() -> None:
    """The acceptance run, pinned as a test.

    `specs/program_model/TlaSpecDevCli.tla` has ONE component (Q = 0.000):
    `lastCommand` and `result` are written by every command. There is no
    architecture for `scripts/` to be coherent with, so the verdict is
    `unmappable` and the reason names the MODEL, not the code. Reporting
    `coherent` here -- which the diff would produce, because with one component
    every edge is internal -- is the exact failure the check exists to prevent.
    """
    base = REPO_ROOT / "specs" / "program_model"
    descriptor = analyze(base / "TlaSpecDevCli.tla", base / "MC.cfg")
    assert descriptor.consumable_as_architecture is False
    report = run_reflexion(
        descriptor, str(REPO_ROOT / "scripts"), str(base / "architecture_map.yaml")
    )
    assert report.verdict == VERDICT_UNMAPPABLE
    assert [s.kind for s in report.blind_spots] == ["model_has_no_architecture"]


def test_a_declared_partition_of_this_repository_is_falsifiable_and_the_code_respects_it() -> None:
    """The second dogfood run, pinned with the numbers it produced.

    The shipped four-component partition (surface / tickets / corpus / kill)
    leaves two pairs unported -- no action of the model touches `kill_test`
    together with `ticket_state` or with a corpus verdict -- so a code edge
    across either pair WOULD have been a divergence. There is none: the two
    kill-test scripts reach only `budgets.py`, which is in `surface` and ported.

    The verdict is still `unmappable`, and for a different reason: three
    computed-name `importlib.import_module` calls, `scripts/run_tlc.sh`, and
    the first-party `spec_double_compiler/` package beside the code root. The
    code side is clean over what the extractor could resolve, and the check
    will not certify what it did not see.
    """
    base = REPO_ROOT / "specs" / "program_model"
    descriptor = analyze(
        base / "TlaSpecDevCli.tla",
        base / "MC.cfg",
        components_path=base / "architecture_components.yaml",
    )
    assert descriptor.consumable_as_architecture is True
    report = run_reflexion(
        descriptor, str(REPO_ROOT / "scripts"), str(base / "architecture_map.yaml")
    )
    assert report.unported_pairs == [("corpus", "kill"), ("kill", "tickets")]
    assert report.divergence_detectable is True
    assert report.divergences == []
    assert report.absences == []
    assert report.unmapped_modules == []
    assert report.unrealized_components == []
    kinds = {s.kind for s in report.blind_spots}
    assert kinds == {"dynamic_import", "first_party_outside_code_root", "non_python_file"}
    assert "unfalsifiable_coherence" not in kinds
    assert report.verdict == VERDICT_UNMAPPABLE


def test_a_coarser_partition_of_the_same_model_could_not_have_falsified_anything(
    tmp_path: Path,
) -> None:
    """Why the shipped partition separates `kill`, and how easily it might not have.

    Fold `kill_test` in with the other scanner verdicts -- an entirely natural
    reading, and the first one this ticket wrote -- and every one of the three
    component pairs has a port, because `RunSpecUnitTests` touches
    `ticket_state` and two corpus verdicts while every command writes
    `lastCommand` and `result`. No code edge could then diverge, and a
    `coherent` verdict would have been true by construction.

    Nothing separates the two files except the judgment of whoever wrote them.
    That is the reflexion model's own blind spot, not this implementation's, and
    it is the single most important thing a reader of a `coherent` verdict has
    to know.
    """
    coarse = tmp_path / "coarse.yaml"
    coarse.write_text(
        "architecture:\n"
        "  components:\n"
        "    - name: surface\n"
        "      variables:\n"
        "        - lastCommand\n"
        "        - result\n"
        "        - setup_phase\n"
        "        - spec_root\n"
        "    - name: tickets\n"
        "      variables:\n"
        "        - ticket_state\n"
        "    - name: scanners\n"
        "      variables:\n"
        "        - complexity_gate\n"
        "        - corpus_gate\n"
        "        - effect_conformance\n"
        "        - kill_test\n",
        encoding="utf-8",
    )
    base = REPO_ROOT / "specs" / "program_model"
    descriptor = analyze(base / "TlaSpecDevCli.tla", base / "MC.cfg", components_path=coarse)
    names = sorted(c.name for c in descriptor.components)
    every_pair = {
        (left, right) for i, left in enumerate(names) for right in names[i + 1 :]
    }
    by_id = {c.cid: c.name for c in descriptor.components}
    ported = {
        tuple(sorted((by_id[p.between[0]], by_id[p.between[1]])))
        for p in descriptor.ports
    }
    assert ported == every_pair


def test_a_first_party_package_beside_the_code_root_is_a_blind_spot(tmp_path: Path) -> None:
    """Narrowing --code must not silently delete edges.

    An import that lands in the standard library is out of scope. An import that
    lands in a sibling package of the scanned tree is out of SCAN -- a property
    of where --code was pointed, not of the program -- and pointing --code at a
    tidy subdirectory would otherwise remove real dependencies from the graph
    with nothing recorded.
    """
    write_project(tmp_path, deliver="from helper import assist\n")
    (tmp_path / "helper").mkdir()
    (tmp_path / "helper" / "__init__.py").write_text("def assist():\n    return 1\n", encoding="utf-8")
    graph = extract_python_graph(tmp_path / "pkg")
    spots = {s.kind for s in graph.blind_spots}
    assert "first_party_outside_code_root" in spots
    report = check(tmp_path)
    assert report.verdict == VERDICT_UNMAPPABLE
