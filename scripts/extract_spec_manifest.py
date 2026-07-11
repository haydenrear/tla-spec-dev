#!/usr/bin/env python3
"""Read and validate a Spec Double Compiler manifest.

The parser intentionally supports a small YAML subset so the scripts can
run in a bare Python environment. If PyYAML is installed, it is used.
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
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        if not body:
            return []
        return [_parse_scalar(part.strip()) for part in body.split(",")]
    return value


def _split_key_value(content: str) -> tuple[str, str]:
    if ":" not in content:
        raise ValueError(f"expected key/value entry, got: {content!r}")
    key, value = content.split(":", 1)
    return key.strip(), value.strip()


def _preprocess(text: str) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for raw in text.splitlines():
        stripped = _strip_comment(raw)
        if not stripped.strip():
            continue
        if stripped.startswith("\t"):
            raise ValueError("tabs are not supported in spec manifests")
        indent = len(stripped) - len(stripped.lstrip(" "))
        rows.append((indent, stripped.strip()))
    return rows


def _parse_block(rows: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(rows) or rows[index][0] < indent:
        return {}, index
    if rows[index][1].startswith("- "):
        return _parse_list(rows, index, indent)
    return _parse_dict(rows, index, indent)


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
        if value:
            result[key] = _parse_scalar(value)
            continue

        if index < len(rows) and rows[index][0] > row_indent:
            result[key], index = _parse_block(rows, index, rows[index][0])
        else:
            result[key] = {}
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

        if ":" in item and not item.startswith(("'", '"')):
            key, value_text = _split_key_value(item)
            value: dict[str, Any] = {key: _parse_scalar(value_text) if value_text else {}}
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
    text = path.read_text()
    try:
        import yaml  # type: ignore
    except Exception:
        return parse_simple_yaml(text)
    loaded = yaml.safe_load(text)
    if not isinstance(loaded, dict):
        raise ValueError("manifest root must be a mapping")
    return loaded


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
