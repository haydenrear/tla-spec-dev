from scripts.extract_spec_manifest import parse_simple_yaml


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
