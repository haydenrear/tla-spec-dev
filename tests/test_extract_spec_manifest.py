from pathlib import Path
import subprocess
import sys

import pytest

from scripts.extract_spec_manifest import load_manifest, parse_simple_yaml


ROOT = Path(__file__).resolve().parents[1]


def test_parse_simple_yaml_supports_folded_block_scalar_with_strip_chomping() -> None:
    manifest = parse_simple_yaml(
        """\
module: StreamLite
planning:
  summary: >-
    Close the seven open tickets after
    the accepted model is promoted.
status: ready
"""
    )

    assert manifest == {
        "module": "StreamLite",
        "planning": {
            "summary": "Close the seven open tickets after the accepted model is promoted."
        },
        "status": "ready",
    }


def test_parse_simple_yaml_supports_folded_scalar_in_list_mapping() -> None:
    manifest = parse_simple_yaml(
        """\
tickets:
  - summary: >-
      Preserve nested folded
      planning text.
    status: open
  - summary: single line
"""
    )

    assert manifest == {
        "tickets": [
            {"summary": "Preserve nested folded planning text.", "status": "open"},
            {"summary": "single line"},
        ]
    }


def test_load_manifest_ignores_optional_yaml_package(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class TrapYaml:
        @staticmethod
        def safe_load(_text: str) -> object:
            raise AssertionError("optional YAML parser must not select the contract")

    monkeypatch.setitem(sys.modules, "yaml", TrapYaml())
    path = tmp_path / "spec_manifest.yaml"
    path.write_text(
        """module: Stable
package: stable_contract
state: {}
commands: {}
results: {}
ports: {}
""",
        encoding="utf-8",
    )

    assert load_manifest(path)["module"] == "Stable"


def test_nested_inline_mappings_parse_and_agree_with_pyyaml(tmp_path: Path) -> None:
    """A NESTED flow mapping is read, not refused. This REPLACES a refusal.

    This test previously asserted the opposite -- that `state: {value: {type:
    str}}` raised "nested inline mappings are not supported; use an indented
    mapping so parsing is dependency-invariant". That refusal was the right
    call FOR AS LONG AS THE PARSER COULD NOT DO IT: failing closed beat parsing
    differently from PyYAML.

    It is the wrong call now, for a reason the differential (#298) made
    visible. YAML IS A SUPERSET OF JSON, and `specs/tickets/*/ticket.yaml` is
    written as pretty-printed JSON -- so PyYAML read those files and this
    parser raised on them. The refusal did not deliver dependency invariance;
    it delivered a parser that could not read the repository's own tickets when
    PyYAML was absent, which is exactly the condition this parser exists for.

    Dependency invariance is now established BY MEASUREMENT rather than by
    refusal: `tests/test_parse_simple_yaml_differential.py` parses every YAML
    under `specs/` through both implementations and compares values. That is a
    stronger guarantee than this test ever gave, because it covers the two
    defect classes a refusal cannot see -- the ones that parse successfully and
    return wrong data.
    """
    path = tmp_path / "spec_manifest.yaml"
    text = """module: Unstable
package: unstable_contract
state: {value: {type: str}}
commands: {}
results: {}
ports: {}
"""
    path.write_text(text, encoding="utf-8")

    parsed = load_manifest(path)
    assert parsed["state"] == {"value": {"type": "str"}}

    yaml = pytest.importorskip("yaml")
    assert parsed == yaml.safe_load(text)


def test_complete_generated_tree_is_identical_with_and_without_site_packages(
    tmp_path: Path,
) -> None:
    manifest = (
        ROOT
        / "examples"
        / "effect_providers"
        / "reminder_worker"
        / "specs"
        / "program_model"
        / "spec_manifest.yaml"
    )
    trees: list[dict[str, bytes]] = []
    for label, python_flags in (("normal", []), ("no-site", ["-S"])):
        out = tmp_path / label
        completed = subprocess.run(
            [
                sys.executable,
                *python_flags,
                str(ROOT / "scripts" / "generate_python.py"),
                str(manifest),
                "--out",
                str(out),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr
        package = out / "reminder_contract"
        trees.append(
            {
                path.name: path.read_bytes()
                for path in sorted(package.iterdir())
                if path.is_file()
            }
        )

    assert trees[0] == trees[1]


def test_inline_mapping_sequence_items_parse_whole() -> None:
    """ex3-run4 finding 1: `- {fact: ...}` sequence items are rule leaves.

    Splitting them at the first colon as block-mapping entries mangled them
    into a `{fact` key plus an unterminated-inline-mapping error, which made
    the ENTIRE manifest unreadable — budgets, justification, and fitness all
    silently degraded to defaults behind one stderr warning.
    """
    from scripts.extract_spec_manifest import parse_simple_yaml

    text = (
        "module: X\n"
        "budgets:\n"
        "  max_internal_cases_per_component: 716\n"
        "fitness_functions:\n"
        "  - name: composed\n"
        "    rule:\n"
        "      all:\n"
        "        - {fact: bound_known, op: ==, value: true}\n"
        "        - {fact: bound, op: '<=', value: 624}\n"
    )
    parsed = parse_simple_yaml(text)
    leaves = parsed["fitness_functions"][0]["rule"]["all"]
    assert leaves == [
        {"fact": "bound_known", "op": "==", "value": True},
        {"fact": "bound", "op": "<=", "value": 624},
    ]
    assert parsed["budgets"]["max_internal_cases_per_component"] == 716
