#!/usr/bin/env python3
"""Read and validate a Spec Double Compiler manifest.

The parser intentionally supports one constrained YAML subset in every
environment. Optional packages must not change the generated contract.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any


def _strip_comment(line: str) -> str:
    """Strip a trailing comment, quote-aware AND whitespace-aware.

    Two rules, and the second was missing. A `#` inside a quoted scalar is
    literal -- that part was always here. A `#` NOT preceded by whitespace is
    ALSO literal, which is what YAML says and what this did not do: `image#1`
    and `http://host/p#frag` were truncated to `image` and `http://host/p`
    with nothing raised. Silent wrong data, so no exception-based check could
    have seen it.

    Block-scalar CONTENT is not passed through here at all -- see
    `_preprocess`. A block scalar carries no quotes to track, so every `#` in
    prose was a truncation point. That form was found only by running the
    differential as a standing test, when the parser truncated the sentence
    describing this bug at its own `#`.
    """
    text, _ = _strip_comment_stateful(line, None)
    return text


def _strip_comment_stateful(line: str, quote: str | None) -> tuple[str, str | None]:
    """Strip a trailing comment; return the text and any quoted scalar left open.

    THE STATE IS NARROW ON PURPOSE. A quoted scalar may span lines, and
    stripping each line independently truncated continuation lines at their
    first `#` -- `narrative: 'Workflow close ... (CD-04..08, PRs #94-#98) ...'`
    lost most of its sentence with nothing raised.

    But a quote only opens a scalar when it is the FIRST character of a VALUE.
    An apostrophe in prose (`the descriptor's domain`, or any `#` comment
    containing one) opens nothing, and treating it as an open quote suppresses
    comment stripping for the rest of the file. That was a real regression in
    this change, caught by `test_budgets` before it shipped: a full-line `#`
    comment survived into `_parse_dict` and raised `expected key/value entry`.
    So the state is entered ONLY from a value-initial quote.
    """
    if quote is not None:
        index = _closing_quote(line, 0, quote)
        if index is None:
            return line.rstrip(), quote
        head = line[: index + 1]
        tail, _ = _strip_comment_stateful(line[index + 1 :], None)
        return (head + tail).rstrip(), None

    text = _strip_trailing_comment(line)
    return text, _value_quote_left_open(text)


def _strip_trailing_comment(line: str) -> str:
    in_single = False
    in_double = False
    for index, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            if index == 0 or line[index - 1] in " \t":
                return line[:index].rstrip()
    return line.rstrip()


def _value_start(content: str) -> int:
    """Where a value begins on this line, or -1 if the line opens no value."""
    if content.startswith("- "):
        inner = _value_start(content[2:])
        return 2 if inner == -1 else 2 + inner
    colon = _mapping_colon(content)
    if colon == -1:
        return -1
    offset = colon + 1
    while offset < len(content) and content[offset] in " \t":
        offset += 1
    return offset


def _value_quote_left_open(text: str) -> str | None:
    content = text.strip()
    if not content:
        return None
    indent = len(text) - len(text.lstrip(" "))
    start = _value_start(content)
    if start == -1 or start >= len(content):
        return None
    quote = content[start]
    if quote not in "\"'":
        return None
    return None if _closing_quote(text, indent + start + 1, quote) is not None else quote


def _closing_quote(line: str, start: int, quote: str) -> int | None:
    index = start
    while index < len(line):
        if line[index] == quote:
            if _is_doubled_quote(line, index, quote):
                index += 2
                continue
            return index
        index += 1
    return None


def _is_doubled_quote(line: str, index: int, quote: str) -> bool:
    return quote == "'" and index + 1 < len(line) and line[index + 1] == "'"


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "{}"}:
        return {}
    if value == "[]":
        return []
    if value in {"null", "None", "~"}:
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        # YAML escapes a single quote inside a single-quoted scalar by doubling
        # it. Without this, `'image''s'` came back as `image''s`.
        return value[1:-1].replace("''", "'")
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        return _unescape_double_quoted(value[1:-1])
    if re.fullmatch(r"-?\d+", value) and not re.fullmatch(r"-?0\d+", value):
        # A leading zero is not a decimal integer in YAML, and the values this
        # actually protects are COMMIT SHAS: `found_at_commit: 0806272` came
        # back as the int 806272 while PyYAML kept the string. Silent, and it
        # corrupts exactly the field a reader would use to go look at the tree.
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        if not body:
            return []
        return [_parse_scalar(part.strip()) for part in _split_inline_items(body)]
    if value.startswith("{") and value.endswith("}"):
        # Flow mappings, including NESTED ones -- both the fitness-rule leaf
        # syntax (`{fact: bound, op: "<", value: 100}`) and a whole JSON
        # document joined onto one line by `parse_simple_yaml`.
        return _parse_inline_mapping(value)
    if value.startswith("{") or value.endswith("}"):
        raise ValueError(
            "unterminated inline mapping in spec manifest; inline mappings "
            "must open and close on one line, with scalar values only"
        )
    return value


_DQ_SIMPLE = {
    "n": "\n", "t": "\t", "r": "\r", "0": "\0", "a": "\a", "b": "\b",
    "f": "\f", "v": "\v", "e": "\x1b", '"': '"', "\\": "\\", "/": "/",
    " ": " ", "N": "\x85", "_": "\xa0",
}


def _unescape_double_quoted(body: str) -> str:
    """Decode a double-quoted scalar's escapes, including \\uXXXX.

    Before this, `\\u2014` survived as six literal characters where PyYAML
    produced an em dash, and a trailing backslash -- YAML's line continuation --
    survived as a stray `\\` in the middle of a folded sentence. Both are
    silent: the value parses, and it is wrong.
    """
    out: list[str] = []
    index = 0
    while index < len(body):
        char = body[index]
        if char != "\\" or index + 1 >= len(body):
            out.append(char)
            index += 1
            continue
        marker = body[index + 1]
        if marker in {"u", "U", "x"}:
            width = {"x": 2, "u": 4, "U": 8}[marker]
            digits = body[index + 2 : index + 2 + width]
            if len(digits) == width:
                try:
                    out.append(chr(int(digits, 16)))
                    index += 2 + width
                    continue
                except ValueError:
                    pass
        if marker in _DQ_SIMPLE:
            out.append(_DQ_SIMPLE[marker])
            index += 2
            continue
        out.append(marker)
        index += 2
    return "".join(out)


def _split_inline_items(body: str) -> list[str]:
    """Split a flow-collection body on top-level commas (quote-aware)."""
    items: list[str] = []
    depth = 0
    quote: str | None = None
    current = ""
    for ch in body:
        if quote is not None:
            current += ch
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            current += ch
        elif ch in "[{":
            depth += 1
            current += ch
        elif ch in "]}":
            depth -= 1
            current += ch
        elif ch == "," and depth == 0:
            items.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        items.append(current.strip())
    return items


def _parse_inline_mapping(value: str) -> dict[str, Any]:
    body = value[1:-1].strip()
    if not body:
        return {}
    result: dict[str, Any] = {}
    for item in _split_inline_items(body):
        colon = _flow_colon(item)
        if colon == -1:
            raise ValueError(
                f"inline mapping entry {item!r} has no key; expected `key: value`"
            )
        key = item[:colon].strip().strip("\"'")
        raw = item[colon + 1 :].strip()
        # NESTED FLOW COLLECTIONS ARE SUPPORTED. They used to be refused, on the
        # reasoning that an indented mapping keeps parsing dependency-invariant.
        # The refusal did not achieve that -- it made this parser unable to read
        # a JSON document, and YAML IS A SUPERSET OF JSON, so PyYAML read those
        # files and this parser raised on them. `specs/tickets/*/ticket.yaml` is
        # written as pretty-printed JSON. Recursing through `_parse_scalar` is
        # what makes the two agree; found by the differential in this change.
        result[key] = _parse_scalar(raw) if raw else None
    return result


def _flow_colon(item: str) -> int:
    """Index of the top-level `key:` colon inside one flow-mapping entry.

    Quote- and depth-aware, so a colon inside a nested collection or a quoted
    key does not split. Unlike `_mapping_colon` this does NOT require trailing
    whitespace: JSON writes `"key":"value"`, which is valid flow syntax.
    """
    depth = 0
    quote: str | None = None
    for index, char in enumerate(item):
        if quote is not None:
            if char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
        elif char in "[{":
            depth += 1
        elif char in "]}":
            depth -= 1
        elif char == ":" and depth == 0:
            return index
    return -1


def _mapping_colon(content: str) -> int:
    """Index of the colon that separates a block-mapping key, or -1.

    YAML requires a colon to be FOLLOWED BY WHITESPACE (or end the line) before
    it separates a key from a value. `crates/mh-substrate::deploy` and
    `External:deploy` are therefore plain scalars, and splitting them at the
    first colon returned `{'crates/mh-substrate': ':deploy'}` and
    `{'External': 'deploy'}` -- structure where a string was expected, with
    nothing raised.

    That is worth a helper rather than an inline test because of what those
    strings are: in `git-epic-workflow` they are `conflict_keys`, the mechanism
    that keeps two concurrently-running tickets off the same files. A tool
    reading them through this parser got a mapping and no error.

    Quote-aware, so a colon inside a quoted key does not split.
    """
    quote: str | None = None
    for index, char in enumerate(content):
        if quote is not None:
            if char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
        elif char == "[" or char == "{":
            # A flow collection opens the VALUE side; any colon inside it
            # belongs to the flow parser, not to us.
            break
        elif char == ":" and (index + 1 == len(content) or content[index + 1] in " \t"):
            return index
    return -1


def _is_mapping_entry(content: str) -> bool:
    return _mapping_colon(content) != -1


def _split_key_value(content: str) -> tuple[str, str]:
    colon = _mapping_colon(content)
    if colon == -1:
        raise ValueError(f"expected key/value entry, got: {content!r}")
    return content[:colon].strip(), content[colon + 1 :].strip()


BLOCK_SCALAR_INDICATORS = {">", ">-", ">+", "|", "|-", "|+"}


def _preprocess(text: str) -> list[tuple[int, str]]:
    """Rows as (indent, content), with comments stripped OUTSIDE block scalars.

    The block-scalar carve-out is the point. A `>` or `|` scalar's content is
    literal text, and running `_strip_comment` over it truncated every line at
    its first `#`. The content lines carry no quotes, so the quote-awareness
    that protects flow scalars protects nothing here.
    """
    rows: list[tuple[int, str]] = []
    block_indent: int | None = None
    quote: str | None = None
    for raw in text.splitlines():
        if raw.startswith("\t"):
            raise ValueError("tabs are not supported in spec manifests")
        if block_indent is not None:
            if not raw.strip():
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            if indent > block_indent:
                # Inside the block scalar: literal, never comment-stripped.
                rows.append((indent, raw.rstrip()[indent:]))
                continue
            block_indent = None

        stripped, open_quote = _strip_comment_stateful(raw, quote)
        quote = open_quote
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        content = stripped.strip()
        rows.append((indent, content))
        colon = _mapping_colon(content)
        if colon != -1 and content[colon + 1 :].strip() in BLOCK_SCALAR_INDICATORS:
            block_indent = indent
        elif content.startswith("- ") and content[2:].strip() in BLOCK_SCALAR_INDICATORS:
            block_indent = indent
    return rows


def _parse_block(rows: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(rows) or rows[index][0] < indent:
        return {}, index
    if rows[index][1].startswith("- "):
        return _parse_list(rows, index, indent)
    return _parse_dict(rows, index, indent)


def _parse_folded_scalar(
    rows: list[tuple[int, str]], index: int, parent_indent: int, indicator: str
) -> tuple[str, int]:
    if index >= len(rows) or rows[index][0] <= parent_indent:
        return "", index

    content_indent = rows[index][0]
    lines: list[str] = []
    while index < len(rows) and rows[index][0] >= content_indent:
        lines.append(rows[index][1])
        index += 1

    value = " ".join(lines)
    if indicator not in {">-", "|-"} and lines:
        value += "\n"
    return value, index


def _parse_dict(rows: list[tuple[int, str]], index: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(rows):
        row_indent, content = rows[index]
        if row_indent < indent:
            break
        if row_indent > indent:
            raise ValueError(f"unexpected indentation at: {content!r}")
        if content.startswith("- "):
            break

        key, value = _split_key_value(content)
        index += 1
        if value in BLOCK_SCALAR_INDICATORS:
            result[key], index = _parse_folded_scalar(rows, index, row_indent, value)
            continue
        if value:
            # A mapping value may wrap onto more-indented continuation lines,
            # which YAML folds into one scalar. `_parse_list` already folded the
            # sequence-item form of exactly this; `_parse_dict` did not, and
            # raised "unexpected indentation" instead. In valid YAML a
            # more-indented line after `key: value` can only continue that
            # scalar, so folding is the only correct reading.
            continuation: list[str] = []
            while (
                index < len(rows)
                and rows[index][0] > row_indent
                and not rows[index][1].startswith("- ")
            ):
                continuation.append(rows[index][1])
                index += 1
            if continuation:
                result[key] = _parse_scalar(" ".join([value, *continuation]))
            else:
                result[key] = _parse_scalar(value)
            continue

        if index < len(rows) and rows[index][0] > row_indent:
            result[key], index = _parse_block(rows, index, rows[index][0])
        elif (
            index < len(rows)
            and rows[index][0] == row_indent
            and rows[index][1].startswith("- ")
        ):
            # A block sequence may sit at the SAME indentation as its key --
            # the form `epic_goals:` / `- id: GOAL-one` at column 0, which is
            # valid YAML and extremely common in hand-written plans. This read
            # the key as null, broke out of the mapping on the `- ` row, and
            # surfaced much later as "unparsed manifest content at row N": the
            # whole sequence silently fell out of the document.
            result[key], index = _parse_list(rows, index, row_indent)
        else:
            result[key] = None
    return result, index


def _parse_list(rows: list[tuple[int, str]], index: int, indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(rows):
        row_indent, content = rows[index]
        if row_indent < indent:
            break
        if row_indent > indent:
            raise ValueError(f"unexpected indentation at: {content!r}")
        if not content.startswith("- "):
            break

        item = content[2:].strip()
        index += 1
        if not item:
            if index < len(rows) and rows[index][0] > row_indent:
                value, index = _parse_block(rows, index, rows[index][0])
            else:
                value = None
            result.append(value)
            continue

        if item.startswith("{"):
            # A sequence item that IS an inline mapping (`- {fact: bound,
            # op: "<", value: 100}` — the fitness-rule leaf syntax). Route it
            # to the scalar parser whole; splitting it at the first colon as
            # a `key: value` block-mapping entry mangles it into a `{fact`
            # key and an "unterminated inline mapping" error, which makes the
            # ENTIRE manifest unreadable and silently degrades budgets,
            # justification, and fitness to defaults.
            result.append(_parse_scalar(item))
            continue
        if _is_mapping_entry(item):
            key, value_text = _split_key_value(item)
            if value_text in BLOCK_SCALAR_INDICATORS:
                folded, index = _parse_folded_scalar(rows, index, row_indent, value_text)
                value = {key: folded}
                if index < len(rows) and rows[index][0] > row_indent:
                    child, index = _parse_block(rows, index, rows[index][0])
                    if isinstance(child, dict):
                        value.update(child)
                result.append(value)
                continue
            value: dict[str, Any] = {key: _parse_scalar(value_text) if value_text else None}
            if index < len(rows) and rows[index][0] > row_indent:
                child, index = _parse_block(rows, index, rows[index][0])
                if not value_text:
                    value[key] = child
                elif isinstance(child, dict):
                    value.update(child)
                else:
                    value[key] = child
            result.append(value)
        else:
            # A plain-scalar list item may wrap onto more-indented continuation
            # lines, which YAML folds into a single scalar. Without this the
            # parser raised "unexpected indentation" on any manifest carrying a
            # wrapped list entry -- and because PyYAML is an optional
            # dependency that is frequently absent, this parser is usually the
            # only one available. A parse failure there is not loud: every
            # budget gate falls back to the documented defaults, so a
            # negotiated cap recorded in the manifest would be silently
            # ignored. Found while wiring the MF-014 case-cap gate, whose
            # entire "raise the cap with a rationale" accept path depends on
            # the manifest actually being read.
            continuation: list[str] = []
            while (
                index < len(rows)
                and rows[index][0] > row_indent
                and not rows[index][1].startswith("- ")
            ):
                continuation.append(rows[index][1])
                index += 1
            if continuation:
                # Through _parse_scalar, not raw. A wrapped QUOTED scalar
                # otherwise kept its surrounding quotes, because only the
                # unwrapped path ever reached the quote-stripping branch.
                result.append(_parse_scalar(" ".join([item, *continuation])))
            else:
                result.append(_parse_scalar(item))
    return result, index


def parse_simple_yaml(text: str) -> dict[str, Any]:
    rows = _preprocess(text)
    if not rows:
        return {}
    if rows[0][1].startswith("{"):
        # A JSON document IS a YAML document -- YAML is a superset -- and
        # `specs/tickets/*/ticket.yaml` is written that way. The flow parser
        # required an inline mapping to open and close on ONE line, so a
        # pretty-printed JSON file raised `expected key/value entry, got '{'`
        # at row 1. Found by the differential in this same change: PyYAML reads
        # these files and this parser could not.
        joined = " ".join(content for _, content in rows)
        parsed = _parse_scalar(joined)
        if not isinstance(parsed, dict):
            raise ValueError("manifest root must be a mapping")
        return parsed
    parsed, index = _parse_block(rows, 0, rows[0][0])
    if index != len(rows):
        raise ValueError(f"unparsed manifest content at row {index + 1}")
    if not isinstance(parsed, dict):
        raise ValueError("manifest root must be a mapping")
    return parsed


def load_manifest(path: Path) -> dict[str, Any]:
    return parse_simple_yaml(path.read_text(encoding="utf-8"))


# The accepted baseline spreads its semantics across three modules. Actions live
# in Internal.tla and External.tla; there is no single {module}.tla.
BASELINE_MODULES = ("Core.tla", "Internal.tla", "External.tla")


def _module_path(manifest_path: Path, module_name: str) -> Path:
    return manifest_path.with_name(f"{module_name}.tla")


def _baseline_module_paths(manifest_path: Path) -> list[Path]:
    return [
        path
        for path in (manifest_path.with_name(name) for name in BASELINE_MODULES)
        if path.exists()
    ]


def _spec_sources(manifest_path: Path, module_name: str) -> tuple[list[Path], str | None]:
    """Resolve the TLA+ sources a manifest describes.

    Prefers the three-module baseline (Core/Internal/External). Falls back to a
    legacy single {module}.tla so older specs keep validating.
    """
    baseline = _baseline_module_paths(manifest_path)
    if any(path.name == "Internal.tla" for path in baseline):
        return baseline, None

    legacy = _module_path(manifest_path, module_name)
    if legacy.exists():
        return [legacy], module_name
    return [], None


def validate_manifest(manifest: dict[str, Any], manifest_path: Path) -> list[str]:
    errors: list[str] = []
    for key in ["module", "package", "state", "commands", "results", "ports"]:
        if key not in manifest:
            errors.append(f"missing required manifest key: {key}")

    module_name = str(manifest.get("module", ""))
    if not module_name:
        return errors

    paths, declared_module = _spec_sources(manifest_path, module_name)
    if not paths:
        errors.append(
            f"TLA+ module not found: expected {manifest_path.parent / 'Internal.tla'} "
            f"(accepted baseline) or {_module_path(manifest_path, module_name)} (legacy)"
        )
        return errors

    text = "\n".join(path.read_text() for path in paths)

    # Only a legacy single-module spec must declare MODULE <module>. In the
    # three-module baseline `module` is the logical program name, not a filename.
    if declared_module and f"MODULE {declared_module}" not in text:
        errors.append(f"{paths[0].name} does not declare MODULE {declared_module}")

    for command_name, command in dict(manifest.get("commands", {})).items():
        action = command.get("action") if isinstance(command, dict) else None
        if action and not re.search(rf"(?m)^\s*{re.escape(str(action))}\b", text):
            errors.append(f"command {command_name} references missing action {action}")

    for invariant in manifest.get("invariants", []) or []:
        invariant_name = str(invariant)
        if invariant_name and not re.search(rf"(?m)^\s*{re.escape(invariant_name)}\b", text):
            errors.append(f"missing invariant definition {invariant_name}")

    return errors


def summarize(manifest: dict[str, Any]) -> str:
    commands = ", ".join(dict(manifest.get("commands", {})).keys()) or "(none)"
    ports = ", ".join(dict(manifest.get("ports", {})).keys()) or "(none)"
    invariants = ", ".join(str(x) for x in manifest.get("invariants", []) or []) or "(none)"
    return "\n".join(
        [
            f"module: {manifest.get('module')}",
            f"package: {manifest.get('package')}",
            f"commands: {commands}",
            f"ports: {ports}",
            f"invariants: {invariants}",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    errors = validate_manifest(manifest, args.manifest)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(summarize(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
