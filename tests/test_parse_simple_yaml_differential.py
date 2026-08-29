"""Differential: `parse_simple_yaml` against PyYAML, over this repository.

WHY A DIFFERENTIAL AND NOT A UNIT TEST. `parse_simple_yaml` exists so the
toolchain need not depend on PyYAML, which makes it a REIMPLEMENTATION of a
subset of YAML, and the only way to know a reimplementation is right is to run
it against the thing it reimplements. Nobody had.

WHY IT MATTERS MORE THAN AN ORDINARY PARSER BUG. PyYAML is an OPTIONAL
dependency and is frequently absent. When it is, this parser is not a fallback,
it is the only one there is.

WHY EXCEPTION-BASED CHECKS COULD NOT HAVE FOUND IT (#298). Of the four defects
this test was written for, TWO PARSED SUCCESSFULLY AND RETURNED WRONG DATA:

  - `crates/mh-substrate::deploy` came back as `{'crates/...': ':deploy'}`,
    and in `git-epic-workflow` that string is a `conflict_key` -- the mechanism
    keeping two concurrent tickets off the same files;
  - `#` truncated inside quoted AND block scalars, and `'image''s'` kept its
    doubled quote.

Nothing raised on either. A check that only asserts "it did not throw" is
blind to both, which is the entire argument for comparing VALUES.

THE MEASUREMENT THAT ARGUES FOR SHIPPING THIS RATHER THAN JUST THE PATCH. On
the reporting repository, three independently-derived patches were run against
this differential: two of them fixed the two RAISING defects, were
indistinguishable from each other, and both still produced 147 diffs. Only the
patch fixing all four reached zero. TWO PATCHES THAT BOTH "FIXED THE CRASH"
WERE BOTH STILL WRONG, and only a value comparison could say so.

NORMALISATION, AND ITS LIMIT. Whitespace INSIDE a scalar is normalised, because
the two implementations fold long lines differently and that difference is not
meaningful. Everything else is compared exactly -- structure, types, keys, and
the characters of every scalar.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import pytest

yaml = pytest.importorskip(
    "yaml",
    reason="the differential needs the implementation it differentials against",
)

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from extract_spec_manifest import parse_simple_yaml  # noqa: E402


def _manifests() -> list[Path]:
    """Every YAML this parser could actually be pointed at, minus sealed history.

    `specs/.history` is excluded for the same reason `test_spec_yaml_valid.py`
    excludes it: it is an append-only archive of past trees, R-H4 seals it, and
    a defect frozen into a receipt is not a defect in today's parser.
    """
    return sorted(
        path
        for path in REPO_ROOT.glob("specs/**/*.y*ml")
        if ".history" not in path.parts and path.is_file()
    )


def _normalise(value: Any) -> Any:
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    if isinstance(value, dict):
        return {key: _normalise(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalise(item) for item in value]
    return value


def _diffs(mine: Any, theirs: Any, path: str = "") -> list[str]:
    """Every disagreeing path, not just the first -- the count is the signal."""
    where = path or "<root>"
    if type(mine) is not type(theirs) and not (mine is None and theirs is None):
        return [f"{where}: type {type(mine).__name__} != {type(theirs).__name__}"]
    if isinstance(theirs, dict):
        out: list[str] = []
        for key in sorted(set(mine) | set(theirs)):
            if key not in mine:
                out.append(f"{where}.{key}: MISSING from parse_simple_yaml")
            elif key not in theirs:
                out.append(f"{where}.{key}: EXTRA in parse_simple_yaml")
            else:
                out.extend(_diffs(mine[key], theirs[key], f"{where}.{key}"))
        return out
    if isinstance(theirs, list):
        if len(mine) != len(theirs):
            return [f"{where}: length {len(mine)} != {len(theirs)}"]
        out = []
        for i, (a, b) in enumerate(zip(mine, theirs)):
            out.extend(_diffs(a, b, f"{where}[{i}]"))
        return out
    if mine != theirs:
        return [f"{where}: {mine!r} != {theirs!r}"]
    return []


@pytest.mark.parametrize("path", _manifests(), ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_parse_simple_yaml_agrees_with_pyyaml(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    expected = yaml.safe_load(text)
    if not isinstance(expected, dict):
        pytest.skip("parse_simple_yaml only claims mapping roots")

    actual = parse_simple_yaml(text)
    diffs = _diffs(_normalise(actual), _normalise(expected))
    assert not diffs, (
        f"{path.relative_to(REPO_ROOT)}: {len(diffs)} disagreement(s) with PyYAML.\n"
        + "\n".join(f"  {line}" for line in diffs[:20])
        + ("\n  ..." if len(diffs) > 20 else "")
    )


def test_the_differential_has_something_to_differential() -> None:
    """Guard the guard: an empty parametrisation would pass vacuously."""
    assert _manifests(), "no YAML found under specs/ -- this test would pass vacuously"


@pytest.mark.parametrize(
    "label,text",
    [
        ("d1 mapping value wrapping onto a continuation line",
         "purpose: 'a long single-quoted scalar that wraps\n  onto a continuation line'\n"),
        ("d2 block sequence at its key's indentation",
         "epic_goals:\n- id: GOAL-one\n- id: GOAL-two\n"),
        ("d3 a string containing :: is not a mapping",
         'conflict_keys:\n  production: ["crates/mh-substrate::deploy"]\n  other:\n    - External:deploy\n'),
        ("d4a a doubled single quote is an escape",
         "name: 'image''s'\n"),
        ("d4b # inside a block scalar is literal",
         "note: >-\n  a sentence with a # inside it that must survive\n"),
        ("d4b # not preceded by whitespace is literal",
         "url: http://host/p#frag\n"),
        ("a real trailing comment is still a comment",
         "a: 1  # stripped\nb: 2\n"),
    ],
)
def test_the_four_defects_stay_fixed(label: str, text: str) -> None:
    """The demonstrated failing inputs, kept as inputs rather than as prose.

    Each of these produced a wrong answer or an exception before #298. Two
    raised; two returned wrong data silently. They are pinned here so the
    repository-wide differential above is not the only thing standing between
    this parser and a regression -- the differential can only see defects the
    repository's own manifests happen to contain.
    """
    assert parse_simple_yaml(text) == yaml.safe_load(text), label


# ---------------------------------------------------------------------------
# THE COROLLARY, ADDED AFTER THE DIFFERENTIAL REPORTED CLEAN ON A BROKEN PARSER
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("seed", range(12))
def test_safe_dump_output_round_trips(seed: int) -> None:
    """Parse what a DUMPER writes, not only what this repository happens to hold.

    THIS EXISTS BECAUSE THE DIFFERENTIAL ABOVE PASSED ON A PARSER THAT WAS
    WRONG. Every manifest under `specs/` agreed with PyYAML while
    `parse_simple_yaml` silently joined two paragraphs of a multi-line scalar
    with a space -- because no file in this repository contained that shape.
    The differential reported clean because it could not look, which is a BLIND
    record on the instrument, not a pass.

    The shape it could not see is the one a dumper produces constantly:
    `yaml.safe_dump` writes a `\n` inside a scalar as a BLANK LINE, and YAML
    folds n>1 line breaks to n-1 newlines. Every long ticket objective and
    every multi-paragraph finding summary written by a tool has it. It was
    found by an independent fix (PR #307) whose own corpus did contain it.

    Generating the input removes the dependency on what the corpus happens to
    contain -- the defect class this test is named for.
    """
    import random

    rng = random.Random(seed)
    words = "alpha beta gamma delta epsilon zeta eta theta iota kappa".split()

    def sentence() -> str:
        return " ".join(rng.choice(words) for _ in range(rng.randint(3, 25)))

    payload = {
        "objective": "\n".join(sentence() for _ in range(rng.randint(1, 4))),
        "found_at_commit": f"{rng.randint(0, 9)}{rng.randint(100000, 999999)}",
        "note": f"see report.md#anchor-{seed} and 'quoted {rng.choice(words)}'",
        "nested": {"a": [sentence(), {"b": sentence()}]},
    }
    text = yaml.safe_dump(payload)

    assert parse_simple_yaml(text) == yaml.safe_load(text), (
        "parse_simple_yaml disagrees with PyYAML on output PyYAML itself wrote"
    )
