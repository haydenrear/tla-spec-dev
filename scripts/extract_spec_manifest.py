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
            # A `#` starts a comment ONLY at line start or after whitespace.
            # Without this, `report.md#def-001--replay-provenance` truncated to
            # `report.md` -- silent wrong data, and it is the same class as the
            # multi-line quote case above seen from the other side. Measured on
            # specs/results/finalization/deferred_findings_final.yaml, where it
            # cost three evidence anchors.
            if index == 0 or line[index - 1] in " \t":
                return line[:index].rstrip()
    return line.rstrip()


#: Single-character escapes YAML defines inside a double-quoted scalar.
_DOUBLE_ESCAPES = {
    "0": "\0",
    "a": "\a",
    "b": "\b",
    "t": "\t",
    "\t": "\t",
    "n": "\n",
    "v": "\v",
    "f": "\f",
    "r": "\r",
    "e": "\x1b",
    " ": " ",
    '"': '"',
    "/": "/",
    "\\": "\\",
    "N": "\x85",
    "_": "\xa0",
    "L": "\u2028",
    "P": "\u2029",
}

#: Numeric escapes, mapped to the count of hex digits that follow.
_HEX_ESCAPES = {"x": 2, "u": 4, "U": 8}

_HEX_DIGITS = set("0123456789abcdefABCDEF")


def _trailing_backslashes(text: str) -> int:
    """How many backslashes `text` ends with.

    An ODD count means the last one is itself an escape character, still
    waiting for the thing it escapes. That is the whole test for `is this
    double-quoted line continuing onto the next one`.
    """
    count = 0
    for char in reversed(text):
        if char != "\\":
            break
        count += 1
    return count


def _unescape_double_quoted(body: str) -> str:
    """Resolve the escape sequences in a double-quoted scalar's body.

    Returning the raw slice instead -- which is what this parser did -- is the
    silent-wrong-data class again, not a crash: `"a\\nb"` came back as the six
    characters `a`, `\\`, `n`, `b` rather than the four a YAML reader sees. It
    stayed invisible until `yaml.safe_dump` first emitted double-quoted scalars,
    which it does as soon as a value carries a newline -- long ticket objectives.

    Unknown escapes RAISE rather than passing through, matching the real
    parsers. A wrong manifest that stops the toolchain is recoverable; a wrong
    manifest that flows into generated contracts is not.
    """
    out: list[str] = []
    index = 0
    while index < len(body):
        char = body[index]
        if char != "\\":
            out.append(char)
            index += 1
            continue
        if index + 1 >= len(body):
            raise ValueError(
                "double-quoted scalar ends in a lone backslash; a trailing `\\` "
                "escapes a line break, so the continuation line is missing"
            )
        code = body[index + 1]
        width = _HEX_ESCAPES.get(code)
        if width is not None:
            digits = body[index + 2 : index + 2 + width]
            if len(digits) != width or any(d not in _HEX_DIGITS for d in digits):
                raise ValueError(
                    f"malformed numeric escape `\\{code}{digits}` in a double-quoted "
                    f"scalar; `\\{code}` takes exactly {width} hex digits"
                )
            out.append(chr(int(digits, 16)))
            index += 2 + width
            continue
        replacement = _DOUBLE_ESCAPES.get(code)
        if replacement is None:
            raise ValueError(
                f"unsupported escape `\\{code}` in double-quoted spec-manifest "
                "scalar; quote the value with ' instead, where no escape but '' "
                "is interpreted"
            )
        out.append(replacement)
        index += 2
    return "".join(out)


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
        # A double-quoted scalar is the ONE YAML scalar style that interprets
        # backslash escapes. Slicing the quotes off and stopping there returns
        # the escapes as literal text. See _unescape_double_quoted.
        return _unescape_double_quoted(value[1:-1])
    if re.fullmatch(r"-?\d+", value) and not re.fullmatch(r"-?0\d+", value):
        # A leading zero is not a decimal integer in YAML, and the values this
        # protects are COMMIT SHAS: `found_at_commit: 0806272` came back as the
        # int 806272 while PyYAML kept the string. Silent, and it corrupts
        # exactly the field a reader uses to go look at the tree. Measured on
        # specs/results/epic-close/deferred_findings_final.yaml.
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


def _flow_colon(item: str) -> int | None:
    """The top-level `key:` colon inside ONE flow-mapping entry, or None.

    Quote- and depth-aware, so a colon inside a nested collection or inside a
    quoted key does not split. Unlike `_key_split_pos` this does NOT require
    trailing whitespace: JSON writes `"key":"value"`, which is valid flow
    syntax and is what `specs/tickets/*/ticket.yaml` contains.
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
    return None



def _parse_inline_mapping(value: str) -> dict[str, Any]:
    body = value[1:-1].strip()
    if not body:
        return {}
    result: dict[str, Any] = {}
    for item in _split_inline_items(body):
        colon = _flow_colon(item)
        if colon is None:
            raise ValueError(
                f"inline mapping entry {item!r} has no key; expected `key: value`"
            )
        key = item[:colon].strip().strip("\"'")
        raw = item[colon + 1 :].strip()
        # NESTED FLOW COLLECTIONS ARE SUPPORTED. Refusing them meant this
        # parser could not read a JSON document -- and YAML IS A SUPERSET OF
        # JSON, so PyYAML read specs/tickets/*/ticket.yaml and this raised on
        # it. Recursing through _parse_scalar is what makes the two agree.
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


#: Marks a paragraph break carried from a blank line inside an open scalar.
#: A control character on purpose: it cannot occur in a manifest, so a stray
#: one surviving into a parsed value is a parser bug rather than data.
_PARA = "\x00"


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
    blanks = 0
    for raw in text.splitlines():
        raw_rstripped = raw.rstrip()
        raw_indent = len(raw_rstripped) - len(raw_rstripped.lstrip(" "))
        in_block = block_indent is not None and (not raw_rstripped.strip() or raw_indent > block_indent)

        stripped = raw_rstripped if (pending is not None or in_block) else _strip_comment(raw)
        if not stripped.strip():
            # A blank line inside an OPEN scalar is not nothing: YAML folds one
            # line break to a space, and n>1 consecutive breaks to n-1
            # NEWLINES. So a blank line is how `yaml.safe_dump` writes a `\n`
            # -- which it does for every multi-line string, including every
            # long ticket objective and every multi-paragraph finding summary.
            # Dropping it silently joined two paragraphs with a space.
            if pending is not None:
                blanks += 1
            continue
        if stripped.startswith("\t"):
            raise ValueError("tabs are not supported in spec manifests")
        indent = len(stripped) - len(stripped.lstrip(" "))
        content = stripped.strip()
        if blanks:
            content = _PARA * blanks + content
            blanks = 0
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

    HOW the join is made is itself part of the contract, and there are two
    joins, not one:

    * An ordinary wrap folds to a SPACE -- that is YAML flow folding.
    * A double-quoted line ending in a backslash is an ESCAPED LINE BREAK.
      It folds to NOTHING, and the continuation line's leading whitespace is
      dropped with it.

    The distinction has to be drawn HERE, before the lines are joined, because
    afterwards it cannot be drawn at all: an escaped line break arrives as
    `\\` followed by the folded space, which is character-for-character
    identical to the escaped space `\\ `. Deciding between them downstream
    would be a guess. Deciding here is a fact -- the line boundary is still
    visible, and a trailing backslash on THIS line means the break was
    escaped.

    A continuation line may also begin with `- `. That is a sequence item only
    when no quote is open; inside an open quoted scalar it is prose, and
    breaking out of the fold there left the row to be re-read as a block
    sequence, which raised `unexpected indentation` and made the whole
    manifest unreadable.
    """
    quote = _open_quote(value)
    folded = value
    joined = False
    while index < len(rows) and rows[index][0] > row_indent:
        content = rows[index][1]
        if quote is None and content.startswith("- "):
            break
        if quote is None and _looks_like_mapping_entry(content):
            break
        paragraphs = 0
        while content.startswith(_PARA):
            paragraphs += 1
            content = content[len(_PARA):]
        if paragraphs:
            # n+1 line breaks fold to n newlines; the leading indent goes with
            # them, exactly as YAML does.
            folded = folded + "\n" * paragraphs + content
            joined = True
            index += 1
            if quote is not None and _open_quote(folded) is None:
                break
            continue
        if quote == '"' and _trailing_backslashes(folded) % 2 == 1:
            # Escaped line break: drop the backslash, join with no space. The
            # continuation line was already left-stripped by _preprocess,
            # which is exactly what YAML does to it.
            folded = folded[:-1] + content
        else:
            folded = f"{folded} {content}"
        joined = True
        index += 1
        if quote is not None and _open_quote(folded) is None:
            break
    return (folded if joined else value), index


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
    if rows[0][1].startswith("{"):
        # A JSON document IS a YAML document -- YAML is a superset -- and
        # `specs/tickets/*/ticket.yaml` is written that way, so PyYAML reads
        # those files and a line-oriented parser raises `expected key/value
        # entry, got '{'` at row 1. Joined and handed to the flow parser whole.
        parsed = _parse_scalar(" ".join(content for _, content in rows))
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
