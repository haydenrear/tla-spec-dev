#!/usr/bin/env python3
"""Generate Python transition cases from a TLC DOT state graph dump.

This script is intentionally generic: it does not know product domains or
Python fake templates. It treats TLC as the case source of truth:

    TLC states and action-labeled edges -> Python case descriptors.
"""

from __future__ import annotations

import argparse
import ast
import importlib
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


NODE_RE = re.compile(r'^\s*(-?\d+) \[label="(.*)"(?:,style = filled)?\];?$')
EDGE_RE = re.compile(r'^\s*(-?\d+) -> (-?\d+) \[label="([^"]+)"')


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    action: str


def run_tlc_dump(tla_path: Path, cfg_path: Path, dot_path: Path, tlc2: str) -> None:
    dot_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        tlc2,
        "-deadlock",
        "-config",
        str(cfg_path),
        "-dump",
        "dot,actionlabels",
        str(dot_path),
        str(tla_path),
    ]
    subprocess.run(command, check=True)


def load_dot(path: Path) -> tuple[dict[str, dict[str, Any]], list[Edge]]:
    states: dict[str, dict[str, Any]] = {}
    edges: list[Edge] = []
    for line in path.read_text().splitlines():
        node_match = NODE_RE.match(line)
        if node_match:
            node_id, raw_label = node_match.groups()
            states[node_id] = parse_state_label(raw_label)
            continue
        edge_match = EDGE_RE.match(line)
        if edge_match:
            source, target, action = edge_match.groups()
            edges.append(Edge(source=source, target=target, action=action))
    return states, edges


def parse_state_label(raw_label: str) -> dict[str, Any]:
    state: dict[str, Any] = {}
    raw_label = raw_label.replace(r"\"", '"')
    for raw_part in raw_label.split(r"\n"):
        part = raw_part.strip()
        while part.startswith(("/", "\\")):
            part = part[1:].strip()
        if " = " not in part:
            continue
        name, value = part.split(" = ", 1)
        state[name.strip()] = parse_tlc_value(value.strip())
    return state


def parse_tlc_value(value: str) -> Any:
    if value == "{}":
        return frozenset()
    if value.startswith("{") and value.endswith("}"):
        body = value[1:-1].strip()
        if not body:
            return frozenset()
        return frozenset(freeze_set_member(parse_tlc_value(part.strip())) for part in split_top_level(body, ","))
    if value.startswith("(") and value.endswith(")") and ":>" in value:
        return parse_tlc_function(value)
    if value.startswith("<<") and value.endswith(">>"):
        body = value[2:-2].strip()
        if not body:
            return ()
        return tuple(parse_tlc_value(part.strip()) for part in split_top_level(body, ","))
    return parse_atom(value)


def parse_tlc_function(value: str) -> dict[str, Any]:
    body = value[1:-1].strip()
    result: dict[str, Any] = {}
    for part in split_top_level(body, "@@"):
        split = split_top_level_once(part, ":>")
        if split is None:
            continue
        key, raw_value = split
        result[str(parse_atom(key.strip()))] = parse_tlc_value(raw_value.strip())
    return result


def freeze_set_member(value: Any) -> Any:
    if isinstance(value, dict):
        return frozenset((key, freeze_set_member(inner)) for key, inner in value.items())
    if isinstance(value, list):
        return tuple(freeze_set_member(inner) for inner in value)
    if isinstance(value, tuple):
        return tuple(freeze_set_member(inner) for inner in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(freeze_set_member(inner) for inner in value)
    return value


def split_top_level_once(value: str, separator: str) -> tuple[str, str] | None:
    parts = split_top_level(value, separator, maxsplit=1)
    if len(parts) != 2:
        return None
    return parts[0], parts[1]


def split_top_level(value: str, separator: str, maxsplit: int = -1) -> list[str]:
    parts: list[str] = []
    start = 0
    index = 0
    splits = 0
    stack: list[str] = []
    in_string = False
    while index < len(value):
        if in_string:
            if value[index] == '"' and not is_escaped(value, index):
                in_string = False
            index += 1
            continue

        if value[index] == '"':
            in_string = True
            index += 1
            continue

        if value.startswith("<<", index):
            stack.append(">>")
            index += 2
            continue

        if stack and value.startswith(stack[-1], index):
            index += len(stack.pop())
            continue

        if value[index] in "({[":
            stack.append({"(": ")", "{": "}", "[": "]"}[value[index]])
            index += 1
            continue

        if stack and value[index] == stack[-1]:
            stack.pop()
            index += 1
            continue

        if not stack and value.startswith(separator, index) and (maxsplit < 0 or splits < maxsplit):
            parts.append(value[start:index].strip())
            index += len(separator)
            start = index
            splits += 1
            continue

        index += 1

    parts.append(value[start:].strip())
    return parts


def is_escaped(value: str, index: int) -> bool:
    slash_count = 0
    cursor = index - 1
    while cursor >= 0 and value[cursor] == "\\":
        slash_count += 1
        cursor -= 1
    return slash_count % 2 == 1


def parse_atom(value: str) -> Any:
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def changed_fields(before: dict[str, Any], after: dict[str, Any]) -> dict[str, dict[str, Any]]:
    fields = sorted(set(before) | set(after))
    return {
        field: {"before": before.get(field), "after": after.get(field)}
        for field in fields
        if before.get(field) != after.get(field)
    }


def case_name(index: int, action: str) -> str:
    snake = re.sub(r"(?<!^)([A-Z])", r"_\1", action).lower()
    snake = re.sub(r"[^a-z0-9_]+", "_", snake).strip("_")
    return f"case_{index:04d}_{snake}"


def py_repr(value: Any) -> str:
    if isinstance(value, frozenset):
        if not value:
            return "frozenset()"
        items = ", ".join(py_repr(item) for item in sorted(value, key=repr))
        return f"frozenset([{items}])"
    if isinstance(value, tuple):
        items = ", ".join(py_repr(item) for item in value)
        if len(value) == 1:
            items += ","
        return f"({items})"
    if isinstance(value, dict):
        items = ", ".join(f"{key!r}: {py_repr(inner)}" for key, inner in sorted(value.items()))
        return "{" + items + "}"
    return repr(value)


def load_object(path: str) -> Any:
    module_name, sep, object_name = path.partition(":")
    if not sep:
        raise ValueError(f"object path must be module:object, got {path!r}")
    module = importlib.import_module(module_name)
    obj: Any = module
    for part in object_name.split("."):
        obj = getattr(obj, part)
    return obj


def labels_for_case(
    *,
    before: dict[str, Any],
    action: str,
    after: dict[str, Any],
    changes: dict[str, dict[str, Any]],
    labelers: list[Any],
) -> list[str]:
    labels = [action]
    for labeler in labelers:
        try:
            produced = labeler(before=before, action=action, after=after, changed=changes)
        except TypeError as exc:
            if "keyword" not in str(exc) and "argument" not in str(exc):
                raise
            produced = labeler(before, action, after, changes)
        if isinstance(produced, str):
            produced = [produced]
        if produced is None:
            continue
        for label in produced:
            rendered = str(label)
            if rendered and rendered not in labels:
                labels.append(rendered)
    return labels


def render_python_package(
    *,
    module: str,
    states: dict[str, dict[str, Any]],
    edges: list[Edge],
    package_dir: Path,
    labelers: list[Any] | None = None,
) -> None:
    package_dir.mkdir(parents=True, exist_ok=True)
    write(package_dir / "__init__.py", render_init())
    write(package_dir / "types.py", render_types())
    write(package_dir / "cases.py", render_cases(module, states, edges, labelers or []))
    write(package_dir / "doubles.py", render_doubles())
    write(package_dir / "validators.py", render_validators())
    write(package_dir / "docs.md", render_docs(module, len(states), len(edges)))


def render_init() -> str:
    return (
        "from .cases import CASES, CASES_BY_NAME\n"
        "from .doubles import ScriptedTransitionDouble\n"
        "from .types import StateGraphCase, StateGraphInput, StateGraphOutput\n"
        "from .validators import assert_case_replays\n\n"
        "__all__ = [\n"
        "    \"CASES\",\n"
        "    \"CASES_BY_NAME\",\n"
        "    \"ScriptedTransitionDouble\",\n"
        "    \"StateGraphCase\",\n"
        "    \"StateGraphInput\",\n"
        "    \"StateGraphOutput\",\n"
        "    \"assert_case_replays\",\n"
        "]\n"
    )


def render_types() -> str:
    return (
        "from __future__ import annotations\n\n"
        "from dataclasses import dataclass\n"
        "from typing import Any\n\n\n"
        "@dataclass(frozen=True)\n"
        "class StateGraphInput:\n"
        "    action: str\n"
        "    source_node: str\n"
        "    target_node: str\n\n\n"
        "@dataclass(frozen=True)\n"
        "class StateGraphOutput:\n"
        "    changed: dict[str, dict[str, Any]]\n\n\n"
        "@dataclass(frozen=True)\n"
        "class StateGraphCase:\n"
        "    name: str\n"
        "    before: dict[str, Any]\n"
        "    input: StateGraphInput\n"
        "    output: StateGraphOutput\n"
        "    after: dict[str, Any]\n"
        "    labels: frozenset[str]\n"
    )


def render_cases(module: str, states: dict[str, dict[str, Any]], edges: list[Edge], labelers: list[Any]) -> str:
    lines = [
        "from __future__ import annotations\n\n",
        "from .types import StateGraphCase, StateGraphInput, StateGraphOutput\n\n\n",
        f'SOURCE_MODULE = {module!r}\n',
        f"STATE_COUNT = {len(states)}\n",
        f"TRANSITION_COUNT = {len(edges)}\n\n",
        "CASES = [\n",
    ]
    for index, edge in enumerate(edges, start=1):
        before = states[edge.source]
        after = states[edge.target]
        changes = changed_fields(before, after)
        labels = labels_for_case(before=before, action=edge.action, after=after, changes=changes, labelers=labelers)
        lines.extend(
            [
                "    StateGraphCase(\n",
                f"        name={case_name(index, edge.action)!r},\n",
                f"        before={py_repr(before)},\n",
                "        input=StateGraphInput(\n",
                f"            action={edge.action!r},\n",
                f"            source_node={edge.source!r},\n",
                f"            target_node={edge.target!r},\n",
                "        ),\n",
                f"        output=StateGraphOutput(changed={py_repr(changes)}),\n",
                f"        after={py_repr(after)},\n",
                f"        labels=frozenset({py_repr(tuple(labels))}),\n",
                "    ),\n",
            ]
        )
    lines.extend(["]\n\n", "CASES_BY_NAME = {case.name: case for case in CASES}\n"])
    return "".join(lines)


def render_doubles() -> str:
    return (
        "from __future__ import annotations\n\n"
        "from .types import StateGraphCase, StateGraphInput, StateGraphOutput\n\n\n"
        "class ScriptedTransitionDouble:\n"
        "    def __init__(self, case: StateGraphCase):\n"
        "        self.case = case\n"
        "        self._state = case.before\n"
        "        self._called = False\n\n"
        "    def snapshot(self):\n"
        "        return self._state\n\n"
        "    def input(self) -> StateGraphInput:\n"
        "        return self.case.input\n\n"
        "    def call(self, value: StateGraphInput) -> StateGraphOutput:\n"
        "        if value != self.case.input:\n"
        "            raise AssertionError(f\"unexpected input for {self.case.name}: {value!r}\")\n"
        "        if self._called:\n"
        "            raise AssertionError(f\"case already consumed: {self.case.name}\")\n"
        "        self._called = True\n"
        "        self._state = self.case.after\n"
        "        return self.case.output\n"
    )


def render_validators() -> str:
    return (
        "from __future__ import annotations\n\n"
        "from .types import StateGraphCase\n\n\n"
        "def assert_case_replays(case: StateGraphCase) -> None:\n"
        "    changed = {\n"
        "        field: {\"before\": case.before.get(field), \"after\": case.after.get(field)}\n"
        "        for field in sorted(set(case.before) | set(case.after))\n"
        "        if case.before.get(field) != case.after.get(field)\n"
        "    }\n"
        "    assert case.output.changed == changed\n"
    )


def render_docs(module: str, state_count: int, transition_count: int) -> str:
    return (
        f"# {module} TLC Cases\n\n"
        "Generated from a TLC DOT state graph dump.\n\n"
        f"- States: `{state_count}`\n"
        f"- Transitions: `{transition_count}`\n\n"
        "Each case is one action-labeled edge in the reachable state graph.\n"
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tla", type=Path)
    parser.add_argument("cfg", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--package", default="tlc_state_graph_cases")
    parser.add_argument("--tlc2", default="tlc2")
    parser.add_argument("--dot", type=Path)
    parser.add_argument(
        "--labeler",
        action="append",
        default=[],
        help="Optional module:function returning extra labels for before/action/after/changed",
    )
    args = parser.parse_args()

    for root in [Path.cwd(), Path(__file__).resolve().parents[1]]:
        resolved = str(root.resolve())
        if resolved not in sys.path:
            sys.path.insert(0, resolved)
    dot_path = args.dot or args.out / f"{args.tla.stem}.dot"
    run_tlc_dump(args.tla, args.cfg, dot_path, args.tlc2)
    states, edges = load_dot(dot_path)
    if not states:
        raise SystemExit(f"ERROR: no states parsed from {dot_path}")
    render_python_package(
        module=args.tla.stem,
        states=states,
        edges=edges,
        package_dir=args.out / args.package,
        labelers=[load_object(path) for path in args.labeler],
    )
    print(f"generated {len(edges)} transition cases from {len(states)} states into {args.out / args.package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
