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
    in_single = False
    in_double = False
    for index, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:index].rstrip()
    return line.rstrip()


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
        # YAML escapes a single quote inside a single-quoted scalar by
        # doubling it. Returning the raw slice leaves `the epic''s goal`
        # doubled, which then fails an exact comparison against the same text
        # read by any real YAML parser.
        return value[1:-1].replace("''", "'")
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        if not body:
            return []
        return [_parse_scalar(part.strip()) for part in _split_inline_items(body)]
    if value.startswith("{") and value.endswith("}"):
        # Single-line inline mappings with scalar values are part of the
        # supported dependency-invariant profile (the manifest fitness-rule
        # leaf syntax, e.g. `{fact: bound, op: "<", value: 100}`). Nested
        # inline mappings remain unsupported.
        return _parse_inline_mapping(value)
    if value.startswith("{") or value.endswith("}"):
        raise ValueError(
            "unterminated inline mapping in spec manifest; inline mappings "
            "must open and close on one line, with scalar values only"
        )
    return value


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
        if ":" not in item:
            raise ValueError(
                f"inline mapping entry {item!r} has no key; expected `key: value`"
            )
        key, _, raw = item.partition(":")
        key = key.strip().strip("\"'")
        raw = raw.strip()
        if raw.startswith("{"):
            raise ValueError(
                "nested inline mappings are not supported in spec manifests; "
                "use an indented mapping so parsing is dependency-invariant"
            )
        result[key] = _parse_scalar(raw) if raw else None
    return result


def _key_split_pos(content: str) -> int | None:
    """Index of the `:` that separates a key from its value, or None.

    In YAML a colon only ends a key when it is followed by whitespace or by
    the end of the line. Splitting on the first colon regardless turns the
    plain scalar `crates/mh-session::execution` into the mapping
    `{'crates/mh-session': ':execution'}` -- which is exactly how a list of
    conflict keys and implementation scopes silently became a list of
    single-entry dicts that no consumer could match against.
    """
    quote: str | None = None
    i = 0
    while i < len(content):
        ch = content[i]
        if quote is not None:
            if quote == "'" and ch == "'":
                if i + 1 < len(content) and content[i + 1] == "'":
                    i += 2
                    continue
                quote = None
            elif quote == '"':
                if ch == "\\":
                    i += 2
                    continue
                if ch == '"':
                    quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == ":" and (i + 1 == len(content) or content[i + 1] in " \t"):
            return i
        i += 1
    return None


def _split_key_value(content: str) -> tuple[str, str]:
    pos = _key_split_pos(content)
    if pos is None:
        raise ValueError(f"expected key/value entry, got: {content!r}")
    return content[:pos].strip(), content[pos + 1 :].strip()


def _value_text(content: str) -> str:
    """The scalar-value part of a row, for open-quote tracking."""
    if content.startswith("- "):
        content = content[2:].strip()
    pos = _key_split_pos(content)
    return content[pos + 1 :].strip() if pos is not None else content


#: Block-scalar indicators. Everything indented under one of these is content.
_BLOCK_INDICATORS = {">", ">-", ">+", "|", "|-", "|+"}


def _preprocess(text: str) -> list[tuple[int, str]]:
    """Rows as `(indent, content)`, with comments stripped only where they are
    comments.

    A `#` is a comment only outside a scalar, and a scalar can span lines two
    different ways. Both are tracked here:

    * `pending` — the quote char of a FLOW scalar that opened on an earlier
      line and has not closed yet.
    * `block_indent` — the indent of the key that opened a BLOCK scalar
      (`>`, `|`, and their chomping variants). Everything more indented is its
      content.

    Missing either one deletes the rest of a sentence from the middle of a
    prose field, and does it silently: the parse still succeeds. Measured on
    this repository's own deferred-findings backlog, where the text describing
    this very defect -- `sgl-project/sglang#9594 and #23814` -- was itself
    truncated at the `#`.
    """
    rows: list[tuple[int, str]] = []
    pending: str | None = None
    block_indent: int | None = None
    for raw in text.splitlines():
        raw_rstripped = raw.rstrip()
        raw_indent = len(raw_rstripped) - len(raw_rstripped.lstrip(" "))
        in_block = block_indent is not None and (not raw_rstripped.strip() or raw_indent > block_indent)

        stripped = raw_rstripped if (pending is not None or in_block) else _strip_comment(raw)
        if not stripped.strip():
            continue
        if stripped.startswith("\t"):
            raise ValueError("tabs are not supported in spec manifests")
        indent = len(stripped) - len(stripped.lstrip(" "))
        content = stripped.strip()
        rows.append((indent, content))

        if in_block:
            # Block content is opaque: it opens no quotes and closes none.
            continue
        block_indent = None
        value = _value_text(content)
        if pending is None and value in _BLOCK_INDICATORS:
            block_indent = indent
            continue
        pending = _open_quote(value) if pending is None else _open_quote(pending + content)
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
    if indicator != ">-" and lines:
        value += "\n"
    return value, index


def _open_quote(text: str) -> str | None:
    """The quote char `text` opens and does not close, or None.

    A YAML flow scalar may wrap onto continuation lines, so `objective: 'one`
    is a legal start whose value is not complete until the closing quote is
    seen -- possibly several lines later.
    """
    if not text or text[0] not in "\"'":
        return None
    quote, body, i = text[0], text[1:], 0
    while i < len(body):
        ch = body[i]
        if quote == "'":
            if ch == "'":
                if i + 1 < len(body) and body[i + 1] == "'":
                    i += 2  # an escaped quote, not the terminator
                    continue
                return None
        else:
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                return None
        i += 1
    return quote


def _looks_like_mapping_entry(text: str) -> bool:
    pos = _key_split_pos(text)
    return pos is not None and bool(text[:pos].strip()) and " " not in text[:pos].strip()


def _fold_continuation(
    rows: list[tuple[int, str]], index: int, row_indent: int, value: str
) -> tuple[str, int]:
    """Fold more-indented continuation lines into a wrapped scalar.

    Any YAML dumper writing to a width limit -- which is how the epic ticket
    plans in this repository are produced -- wraps a long scalar onto
    continuation lines. Without this the parser raised "unexpected
    indentation" on the whole file, and because the ticket plan is what
    `open ticket` reads, that made every ticket in such an epic unopenable.

    Folding is applied only where YAML is unambiguous about it: an
    unterminated quoted scalar, or a plain scalar whose continuation cannot
    be read as a mapping entry. Anything else keeps raising, so a genuinely
    misindented mapping is still a loud error rather than a silent string.
    """
    quote = _open_quote(value)
    parts = [value]
    while index < len(rows) and rows[index][0] > row_indent and not rows[index][1].startswith("- "):
        if quote is None and _looks_like_mapping_entry(rows[index][1]):
            break
        parts.append(rows[index][1])
        index += 1
        if quote is not None and _open_quote(" ".join(parts)) is None:
            break
    return (" ".join(parts) if len(parts) > 1 else value), index


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
        if value in {">", ">-", ">+"}:
            result[key], index = _parse_folded_scalar(rows, index, row_indent, value)
            continue
        if value:
            value, index = _fold_continuation(rows, index, row_indent, value)
            result[key] = _parse_scalar(value)
            continue

        if index < len(rows) and rows[index][0] > row_indent:
            result[key], index = _parse_block(rows, index, rows[index][0])
        elif index < len(rows) and rows[index][0] == row_indent and rows[index][1].startswith("- "):
            # A block sequence may sit at the SAME indent as the key that owns
            # it. That is ordinary YAML and it is what every dumper emits, so
            # requiring the sequence to be further indented made the parser
            # stop at the first such key and declare the entire remainder of
            # the file "unparsed manifest content" -- which is how a ticket
            # plan produced by a YAML dumper became unreadable.
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
        if _key_split_pos(item) is not None and not item.startswith(("'", '"')):
            key, value_text = _split_key_value(item)
            if value_text in {">", ">-", ">+"}:
                folded, index = _parse_folded_scalar(rows, index, row_indent, value_text)
                value = {key: folded}
                if index < len(rows) and rows[index][0] > row_indent:
                    child, index = _parse_block(rows, index, rows[index][0])
                    if isinstance(child, dict):
                        value.update(child)
                result.append(value)
                continue
            if value_text:
                value_text, index = _fold_continuation(rows, index, row_indent, value_text)
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
            #
            # A QUOTED item wraps the same way, and must additionally have its
            # quotes stripped once folded: joining the lines and appending the
            # raw string leaves the value carrying its own delimiters, so an
            # exact comparison against the same entry read by a real YAML
            # parser fails on every wrapped quoted entry.
            folded, index = _fold_continuation(rows, index, row_indent, item)
            if folded != item:
                result.append(_parse_scalar(folded))
            else:
                result.append(_parse_scalar(item))
    return result, index


def parse_simple_yaml(text: str) -> dict[str, Any]:
    rows = _preprocess(text)
    if not rows:
        return {}
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
