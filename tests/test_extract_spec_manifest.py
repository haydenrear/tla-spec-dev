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


def test_a_manifest_the_constrained_parser_cannot_represent_still_fails_closed(
    tmp_path: Path,
) -> None:
    """The registered failing demonstration for `manifest-validator`.

    IT REPLACES ONE THIS CHANGE REMOVED, and the substitution is the point. The
    register previously cited the nested-inline-mapping refusal, whose stated
    purpose was that the parser must not "silently parse differently with and
    without PyYAML installed". Nested flow mappings are now SUPPORTED, because
    refusing them meant the parser could not read a JSON document while PyYAML
    could -- the refusal was causing the divergence it existed to prevent.

    The purpose is now served two ways, and both are stronger than the old
    demonstration:

      - `tests/test_parse_simple_yaml_differential.py` compares VALUES against
        PyYAML across every manifest in the repository, which covers the defect
        classes a refusal cannot see: the ones that parse successfully and
        return wrong data;
      - and the constrained parser still FAILS CLOSED on input it genuinely
        cannot represent, which is what this test demonstrates.

    A demonstration that cannot fail is not a demonstration, so this asserts a
    real refusal on a real input rather than asserting the absence of one.
    """
    unterminated = tmp_path / "unterminated.yaml"
    unterminated.write_text(
        "module: Unstable\nstate: {value: str\ncommands: {}\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="unterminated inline mapping"):
        load_manifest(unterminated)

    tabbed = tmp_path / "tabbed.yaml"
    tabbed.write_text("module: Unstable\n\tstate: {}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="tabs are not supported"):
        load_manifest(tabbed)

#: Double-quoted scalars, paired with the value a real YAML reader returns.
#:
#: A double-quoted scalar is the one YAML style that interprets backslash
#: escapes, and `parse_simple_yaml` returned the raw slice between the quotes
#: — silently wrong data, never an exception. It stayed invisible until
#: `yaml.safe_dump` first emitted this style, which it does as soon as a value
#: carries a newline: long epic ticket objectives.
#:
#: The expectations below are NOT hand-derived. Every one is checked against
#: PyYAML by `test_double_quoted_scalars_agree_with_pyyaml`, so the table
#: cannot drift into encoding this parser's own assumption twice — and the
#: cases still run, as ordinary expectations, in the environments without
#: PyYAML that are the entire reason this parser exists.
DOUBLE_QUOTED_CASES = [
    pytest.param(
        'k: "alpha beta\\\n  \\ gamma\\ndelta"\n',
        "alpha beta gamma\ndelta",
        id="escaped-line-break-then-escaped-space",
    ),
    pytest.param(
        'k: "tab\\there and a \\"quote\\" and a back\\\\slash"\n',
        'tab\there and a "quote" and a back\\slash',
        id="tab-quote-backslash",
    ),
    pytest.param(
        'k: "ends in an escaped backslash\\\\\n  and folds to a space"\n',
        "ends in an escaped backslash\\ and folds to a space",
        id="even-backslashes-are-not-a-continuation",
    ),
    pytest.param(
        'k: "plain wrap\n  folds to one space"\n',
        "plain wrap folds to one space",
        id="plain-fold",
    ),
    pytest.param(
        'k: "\\u00e9 \\x41 \\_"\n',
        "\u00e9 A \xa0",
        id="numeric-and-named-escapes",
    ),
    pytest.param(
        "k: 'a continuation line may start with\n  - a dash, which is prose here'\n",
        "a continuation line may start with - a dash, which is prose here",
        id="dash-continuation-inside-open-quote",
    ),
]


@pytest.mark.parametrize("text,expected", DOUBLE_QUOTED_CASES)

def test_quoted_scalar_escapes_and_continuations(text: str, expected: str) -> None:
    """The fifth `parse_simple_yaml` defect, found after the fix for the first four.

    Two things had to be decided, and only one of them could be decided here.

    The escapes themselves are local: `\\n`, `\\t`, `\\"`, `\\\\`, `\\ ` and the
    numeric forms resolve inside the scalar. But a YAML line continuation — a
    trailing backslash whose line break and following indent both vanish —
    could not be resolved after the parser folded wrapped lines together,
    because by then it is character-for-character identical to an escaped
    space. It is resolved at FOLD time instead, where the line boundary is
    still visible: an odd number of trailing backslashes means the break was
    escaped, so the lines join with no space at all.
    """
    assert parse_simple_yaml(text)["k"] == expected


@pytest.mark.parametrize("text,expected", DOUBLE_QUOTED_CASES)
def test_double_quoted_scalars_agree_with_pyyaml(text: str, expected: str) -> None:
    """Differential: the table above is PyYAML's answer, not this parser's.

    `parse_simple_yaml` is a REIMPLEMENTATION of a YAML subset, so the only
    instrument that can judge it is the thing it reimplements. This is the
    check that keeps the expectations honest; it skips where PyYAML is absent,
    which is exactly the situation the reimplementation exists for.
    """
    yaml = pytest.importorskip("yaml")

    assert yaml.safe_load(text)["k"] == expected
    assert parse_simple_yaml(text) == yaml.safe_load(text)


def test_unsupported_double_quoted_escape_fails_loudly() -> None:
    """An escape this parser does not know must RAISE, not pass through.

    Passing it through is the defect's own failure mode wearing a smaller hat:
    a value that is quietly wrong and flows on into generated contracts. Real
    YAML readers reject it, so this parser does too.
    """
    with pytest.raises(ValueError, match="unsupported escape"):
        parse_simple_yaml('k: "a \\q b"\n')
