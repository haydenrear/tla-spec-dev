"""`code_complexity` is a THERMOMETER. These tests are what stops it becoming a
thermostat.

The instrument itself is easy; the failure mode is not. Three epics of static
checking in this repository produced a gate that failed every normal program
and was retired to advisory, a check defeated by six lines of YAML, and another
defeated by a 41-line re-export. A complexity tool that grows a threshold is
precisely the thing that was retired. So the properties asserted here are, in
order of how much damage their absence has already caused:

1. **It exits 0 on every input.** A tree that does not exist, an empty tree, a
   tree with no Python, a file that does not parse, a file that is not UTF-8.
   "I could not measure this" is a completeness fact printed with the path and
   the reason -- never a refusal.
2. **There is no threshold in the shipped source.** No `EXIT_` constant other
   than the single zero, no nonzero `sys.exit`, no identifier naming a budget,
   limit or threshold. Asserted against the file's AST, not against prose.
3. **Nothing in the toolchain reads its output as a condition.** Asserted by
   scanning every executable surface in the repository for a reference to it.
4. **The output carries no verdict vocabulary.** MF-020: a figure falling is
   not evidence the design improved, so the instrument prints no direction, no
   delta and no word that supplies one.
5. **It can tell two implementations of one spec apart.** That is the whole
   point of building it -- GOAL-complexity-measurable -- and it is executable
   here against the two committed anchor trees rather than asserted in a
   report.
6. **The documented figure names and the emitted figure names are the same
   set** (the epic's `declaration_executability_rule`): rename a figure and
   forget the table in `references/complexity_intuition.md`, and this fails.
"""

from __future__ import annotations

import ast
import dataclasses
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.code_complexity import (  # noqa: E402
    AMBIGUOUS_SINKS_EXCLUDED,
    EFFECT_SINKS,
    EXIT_OK,
    ModuleFigures,
    _totals,
    analyze_tree,
    classify_role,
    count_branch_points,
    main,
    max_block_depth,
    measure_module,
    render,
)

SCRIPT = REPO_ROOT / "scripts" / "code_complexity.py"
INTUITION_DOC = REPO_ROOT / "references" / "complexity_intuition.md"

FLAT_TREE = REPO_ROOT / "examples" / "validation" / "ab" / "reference"
PORTED_TREE = REPO_ROOT / "examples" / "validation" / "ab" / "reference_ports"
SEALED_ARMS = (
    REPO_ROOT
    / "specs/.history/hexagonal-prompting-epic/closed-snapshot/results/scorecards"
    / "hexagonal-prompting-rerun/arms"
)


# ---------------------------------------------------------------------------
# 1. it refuses nothing
# ---------------------------------------------------------------------------


def _pathological_targets(tmp_path: Path) -> list[Path]:
    missing = tmp_path / "no-such-tree"

    empty = tmp_path / "empty"
    empty.mkdir()

    no_python = tmp_path / "no_python"
    no_python.mkdir()
    (no_python / "README.md").write_text("not python\n", encoding="utf-8")

    broken = tmp_path / "broken"
    broken.mkdir()
    (broken / "fine.py").write_text("def f(x):\n    return x\n", encoding="utf-8")
    (broken / "truncated.py").write_text("def f(:\n", encoding="utf-8")
    (broken / "not_utf8.py").write_bytes(b"x = '\xff\xfe not utf-8'\n")

    single_file = tmp_path / "one.py"
    single_file.write_text("VALUE = 1\n", encoding="utf-8")

    # A deliberately extreme tree: 40 modules, ~100 branch points each, 12 deep,
    # 60 pieces of instance state. The retired complexity gate failed every
    # normal program; this is what it would have refused hardest. Every figure
    # here is far past any plausible budget, so a threshold added later shows up
    # as a nonzero exit HERE, behaviourally, not only as a banned identifier.
    extreme = tmp_path / "extreme"
    extreme.mkdir()
    nested = "".join(
        f"{'    ' * (depth + 2)}if x > {depth} and x < {depth + 9} or x == {depth}:\n"
        for depth in range(12)
    )
    for index in range(40):
        body = [f"GLOBAL_{index} = 0", f"GLOBAL_{index} = 1", f"class Big{index}:"]
        body.append("    def __init__(self):")
        body.extend(f"        self.field_{n} = {n}" for n in range(60))
        for method in range(20):
            body.append(f"    def method_{method}(self, x):")
            body.append(nested.rstrip("\n"))
            body.append(f"{'    ' * 14}return x")
        (extreme / f"mod_{index}.py").write_text("\n".join(body) + "\n", encoding="utf-8")

    return [
        missing,
        empty,
        no_python,
        broken,
        single_file,
        extreme,
        FLAT_TREE,
        PORTED_TREE,
    ]


def test_exits_zero_on_every_input(tmp_path: Path) -> None:
    """Including one it cannot parse, and one that is not there at all."""

    for target in _pathological_targets(tmp_path):
        assert main([str(target)]) == EXIT_OK, target
        assert main([str(target), "--json"]) == EXIT_OK, target


def test_subprocess_exits_zero_on_every_input(tmp_path: Path) -> None:
    """The same property through the real command line, not just `main`."""

    for target in _pathological_targets(tmp_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(target)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, (target, result.stderr)
        assert result.stdout.strip(), target


def test_unparseable_file_costs_completeness_and_is_reported(tmp_path: Path) -> None:
    tree = tmp_path / "mixed"
    tree.mkdir()
    (tree / "good.py").write_text(
        "class A:\n    def m(self):\n        if 1:\n            return 2\n",
        encoding="utf-8",
    )
    (tree / "truncated.py").write_text("def f(:\n", encoding="utf-8")
    (tree / "not_utf8.py").write_bytes(b"x = '\xff\xfe'\n")

    record = analyze_tree(tree)
    completeness = record["completeness"]

    assert completeness["files_seen"] == 3
    assert completeness["files_parsed"] == 1
    assert completeness["files_unparsed"] == 2
    assert completeness["parsed_fraction"] == pytest.approx(1 / 3)

    unparsed = {item["path"]: item["reason"] for item in completeness["unparsed"]}
    assert set(unparsed) == {"truncated.py", "not_utf8.py"}
    assert "SyntaxError" in unparsed["truncated.py"]
    assert "UnicodeDecodeError" in unparsed["not_utf8.py"]

    # the sibling that DID parse is still measured -- an unparseable file costs
    # completeness, it does not abandon the tree
    assert record["totals"]["branch_points"] == 1

    text = render(record)
    assert "truncated.py" in text
    assert "not parsed" in text


def test_missing_path_is_reported_not_raised(tmp_path: Path) -> None:
    record = analyze_tree(tmp_path / "absent")
    assert record["completeness"]["path_state"].startswith("not found")
    assert record["modules"] == []
    assert "not found" in render(record)


def test_unresolvable_constructs_are_named(tmp_path: Path) -> None:
    tree = tmp_path / "dynamic"
    tree.mkdir()
    (tree / "d.py").write_text(
        "from os.path import *\n"
        "def f(obj):\n"
        "    setattr(obj, 'x', 1)\n"
        "    return getattr(obj, 'y')\n",
        encoding="utf-8",
    )
    record = analyze_tree(tree)
    unresolved = " ".join(record["completeness"]["unresolved_constructs"])
    assert "import *" in unresolved
    assert "setattr" in unresolved
    assert "getattr" in unresolved


# ---------------------------------------------------------------------------
# 2. there is no threshold in the shipped source
# ---------------------------------------------------------------------------

THERMOSTAT_IDENTIFIER_FRAGMENTS = (
    "threshold",
    "budget",
    "max_allowed",
    "limit",
    "warn",
    "gate",
    "verdict",
    "violation",
    "tolerance",
)


def _shipped_identifiers() -> set[str]:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.arg):
            names.add(node.arg)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.keyword) and node.arg:
            names.add(node.arg)
    return names


def test_shipped_source_declares_no_threshold() -> None:
    """No identifier in the instrument names a budget, limit or threshold.

    Scanned from the AST, so the module docstring may -- and does -- discuss
    thresholds without this passing vacuously on prose.
    """

    offenders = sorted(
        name
        for name in _shipped_identifiers()
        if any(fragment in name.lower() for fragment in THERMOSTAT_IDENTIFIER_FRAGMENTS)
    )
    assert offenders == []


def test_shipped_source_has_exactly_one_exit_code_and_it_is_zero() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(source)

    exit_constants = {
        target.id
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name) and target.id.startswith("EXIT")
    }
    assert exit_constants == {"EXIT_OK"}
    assert EXIT_OK == 0

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
            if name in {"exit", "_exit"} and node.args:
                arg = node.args[0]
                assert not (
                    isinstance(arg, ast.Constant) and arg.value not in (0, None)
                ), ast.dump(node)
        if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
            callee = getattr(node.exc.func, "id", None)
            assert callee != "SystemExit", ast.dump(node)


# ---------------------------------------------------------------------------
# 3. nothing in the toolchain gates on it
# ---------------------------------------------------------------------------

EXECUTABLE_SURFACES = (
    "scripts",
    "skill-scripts",
    "spec_double_compiler",
    "templates",
    "test_graph",
)


def test_nothing_executable_reads_this_instrument() -> None:
    """A thermometer nothing consumes cannot have become a thermostat.

    If a future ticket wires this into a close path, a workflow, a Test Graph
    node or another script, this test names the file that did it.
    """

    consumers: list[str] = []
    for surface in EXECUTABLE_SURFACES:
        root = REPO_ROOT / surface
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.resolve() == SCRIPT.resolve():
                continue
            if any(part in {"__pycache__", ".git", "build", "node_modules"} for part in path.parts):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if "code_complexity" in text:
                consumers.append(str(path.relative_to(REPO_ROOT)))

    for spec_python in (REPO_ROOT / "specs").rglob("*.py"):
        if ".history" in spec_python.parts:
            continue
        try:
            text = spec_python.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if "code_complexity" in text:
            consumers.append(str(spec_python.relative_to(REPO_ROOT)))

    assert sorted(consumers) == []


# ---------------------------------------------------------------------------
# 4. the output carries no verdict
# ---------------------------------------------------------------------------

VERDICT_VOCABULARY = (
    "exceed",
    "too complex",
    "too many",
    "should ",
    "recommend",
    "suggest",
    "refactor",
    "violation",
    "threshold",
    "budget",
    "simpler",
    "better",
    "worse",
    "improve",
    "acceptable",
    "warning",
    "critical",
    "verdict",
    "risky",
    "problem",
    "smell",
    "score",
    "grade",
    "pass",
    "fail",
)


@pytest.mark.parametrize(
    "target",
    [FLAT_TREE, PORTED_TREE, SEALED_ARMS / "arm_a", SEALED_ARMS / "arm_b"],
    ids=["reference", "reference_ports", "arm_a", "arm_b"],
)
def test_output_uses_no_verdict_vocabulary(target: Path) -> None:
    record = analyze_tree(target)
    # The target path is the caller's string, not the instrument's -- one of
    # these trees lives under `results/scorecards/`.
    echoed = str(target).lower()
    blobs = (
        render(record).lower().replace(echoed, "<target>"),
        json.dumps(record).lower().replace(echoed, "<target>"),
    )
    for blob in blobs:
        for word in VERDICT_VOCABULARY:
            assert word not in blob, (word, target.name)


def test_no_comparison_mode_exists() -> None:
    """MF-020, wired into the CLI: there is no delta to misread.

    A `--compare`/`--baseline`/`--diff` flag would print a signed number, and a
    signed number is read as a direction. The best complexity result on this
    project's record was withheld from a top score by both blind judges for
    exactly that reading.
    """

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0
    for flag in ("--compare", "--baseline", "--diff", "--delta", "--against"):
        assert flag not in result.stdout


def test_two_targets_are_reported_side_by_side_never_subtracted() -> None:
    """Measuring two trees at once yields two records and no third thing.

    No combined figure, no derived ratio, no signed difference: each record is
    byte-identical to the one that target produces alone, so the reader does
    the comparing and owns the reading.
    """

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(FLAT_TREE), str(PORTED_TREE), "--json"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    payload = json.loads(result.stdout)
    assert set(payload) == {"reports"}
    assert payload["reports"] == [analyze_tree(FLAT_TREE), analyze_tree(PORTED_TREE)]
    for record in payload["reports"]:
        for key, value in record["totals"].items():
            if isinstance(value, (int, float)):
                assert value >= 0, key


# ---------------------------------------------------------------------------
# 5. it can tell two implementations of one spec apart
# ---------------------------------------------------------------------------


def _differing_total_keys(left: Path, right: Path, block: str = "totals_code_only") -> set[str]:
    a = analyze_tree(left)[block]
    b = analyze_tree(right)[block]
    return {key for key in a if a[key] != b[key]}


def test_distinguishes_the_two_anchor_trees() -> None:
    """GOAL-complexity-measurable's local signal, executable.

    `examples/validation/ab/reference/` and `.../reference_ports/` implement the
    SAME feature and pass the SAME behavioural suite. If the instrument reports
    the same figures for both, it cannot do its job.
    """

    differing = _differing_total_keys(FLAT_TREE, PORTED_TREE)
    assert differing, "the instrument cannot tell the two anchor trees apart"
    assert {"modules", "declared_interfaces", "internal_import_edges"} <= differing


def test_distinguishes_the_sealed_arms() -> None:
    differing = _differing_total_keys(SEALED_ARMS / "arm_a", SEALED_ARMS / "arm_b")
    assert differing, "the instrument cannot tell the sealed arms apart"
    assert "declared_interfaces" in differing


def test_location_of_effects_is_reported_not_only_the_total() -> None:
    """The figure that the totals alone would hide.

    Both anchor trees make the same NUMBER of outside-world calls. What differs
    is which module they sit in. A totals-only instrument reports nothing here,
    which is the whole reason the partition is emitted.
    """

    flat = analyze_tree(FLAT_TREE)["totals_code_only"]
    ported = analyze_tree(PORTED_TREE)["totals_code_only"]

    assert flat["effectful_calls"] == ported["effectful_calls"]
    assert flat["branch_points_in_effectful_modules"] != (
        ported["branch_points_in_effectful_modules"]
    )


def test_role_split_is_reported_so_the_filter_is_visible() -> None:
    """Test modules are measured, labelled, and totalled separately.

    An audit that is clean because of its own filter has already cost this
    project a round. The filter is output, not policy.
    """

    record = analyze_tree(SEALED_ARMS / "arm_a")
    roles = {module["path"]: module["role"] for module in record["modules"]}
    assert roles == {"quota_ledger.py": "code", "test_quota_ledger.py": "test"}
    assert record["totals"]["modules"] == 2
    assert record["totals_code_only"]["modules"] == 1
    assert record["totals"]["branch_points"] > record["totals_code_only"]["branch_points"]
    assert "role is assigned by NAME alone" in render(record)


# ---------------------------------------------------------------------------
# 6. the documented figures and the emitted figures are one set
# ---------------------------------------------------------------------------


def _documented_figure_keys() -> set[str]:
    lines = INTUITION_DOC.read_text(encoding="utf-8").splitlines()
    keys: set[str] = set()
    inside = False
    for line in lines:
        if line.strip().startswith("### The figures"):
            inside = True
            continue
        if inside and line.startswith("###"):
            break
        if inside and line.startswith("| `"):
            keys.add(line.split("`")[1])
    return keys


def _shipped_figure_keys() -> set[str]:
    module_keys = {field.name for field in dataclasses.fields(ModuleFigures)}
    return module_keys | set(_totals([]))


def test_documented_figures_match_shipped_output() -> None:
    documented = _documented_figure_keys()
    shipped = _shipped_figure_keys()
    assert documented, "the figure table in complexity_intuition.md is unreadable"
    assert documented == shipped, {
        "documented_only": sorted(documented - shipped),
        "shipped_only": sorted(shipped - documented),
    }


def test_documented_keys_actually_appear_in_a_real_record() -> None:
    """The table is checked against a REAL run, not only against the dataclass."""

    record = analyze_tree(PORTED_TREE)
    emitted = set(record["modules"][0]) | set(record["totals"])
    assert _documented_figure_keys() == emitted


# ---------------------------------------------------------------------------
# 7. one table, one denominator
# ---------------------------------------------------------------------------
#
# PA-02's first report tabled `totals` for the two sealed arms beside what was
# effectively `totals_code_only` for the two anchor trees -- the anchor trees
# ship no test modules, so their two blocks coincide and the mixture was
# invisible by eye. Three figures reversed direction or flattened when the
# denominator was made uniform: branch_points 37->19 became 10->11 (the ported
# tree HIGHER), max_depth 5->3 became 1->1, public_surface 52->48 became 20->25.
# The apparent improvement was arm_a's bigger TEST FILE, which carries 27 of its
# 37 all-modules branch points. Nothing about either implementation moved.
#
# MF-020 wearing a new hat: a figure that improves because of what got counted.
# Worse than the usual case, because these figures land in the scorecard's
# MECHANICAL BLOCK, which is recorded and never scored -- so no judge challenges
# them and nothing else in the protocol catches a wrong one. Hence a test.

#: Column label -> the tree that column reports on. A renamed or reordered
#: column fails, because each table's header row is asserted against these keys
#: in order.
RECORDED_TREES: dict[str, Path] = {
    "reference": FLAT_TREE,
    "reference_ports": PORTED_TREE,
    "arm_a": SEALED_ARMS / "arm_a",
    "arm_b": SEALED_ARMS / "arm_b",
}

#: The record blocks a recorded table may draw from. Each table's own `####`
#: heading names exactly one of these, so renaming a shipped key fails here too.
RECORDED_BLOCKS = ("totals_code_only", "totals")


def _recorded_tables() -> dict[str, dict[str, list[str]]]:
    """The figure tables in complexity_intuition.md, keyed by their block.

    A table is claimed by a block when its own `####` heading names that block.
    A heading naming neither, or both, claims nothing, and the callers below
    fail on the missing block rather than guessing which was meant.
    """

    tables: dict[str, dict[str, list[str]]] = {}
    block: str | None = None
    header_seen = False
    for line in INTUITION_DOC.read_text(encoding="utf-8").splitlines():
        if line.startswith("####"):
            named = [key for key in RECORDED_BLOCKS if f"`{key}`" in line]
            block = named[0] if len(named) == 1 else None
            header_seen = False
            continue
        if block is None or not line.startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if set("".join(cells)) <= {"-", ":"}:
            continue
        if not header_seen:
            header_seen = True
            tables.setdefault(block, {})["__header__"] = cells
            continue
        tables[block][cells[0]] = cells[1:]
    return tables


def test_recorded_figures_match_a_live_run() -> None:
    """Every cell of both recorded tables, against a live run, per block.

    The executable form of the denominator rule. A cell taken from the wrong
    totals block fails here for any tree whose two blocks differ -- which is
    exactly the trees that ship tests, which is exactly where the mistake is
    invisible by eye.
    """

    tables = _recorded_tables()
    assert set(tables) == set(RECORDED_BLOCKS), sorted(tables)

    live = {label: analyze_tree(path) for label, path in RECORDED_TREES.items()}
    labels = list(RECORDED_TREES)

    for block, rows in tables.items():
        assert rows["__header__"] == ["figure"] + labels, (block, rows["__header__"])
        assert len(rows) > 5, block
        for figure, cells in rows.items():
            if figure == "__header__":
                continue
            recorded = [int(cell) for cell in cells]
            actual = [live[label][block][figure] for label in labels]
            assert recorded == actual, (block, figure, recorded, actual)


def test_the_two_denominators_differ_so_a_mixed_table_is_catchable() -> None:
    """A guard on the guard: the test above is only sharp where the blocks differ.

    If every tree reported the same figures under both blocks, mixing them would
    be undetectable and `test_recorded_figures_match_a_live_run` would pass on a
    mixed table. It is sharp precisely for the trees that ship tests, and the
    two anchor trees are named here as the ones where it is NOT sharp -- stated,
    not assumed.
    """

    sharp: list[str] = []
    flat: list[str] = []
    for label, path in RECORDED_TREES.items():
        record = analyze_tree(path)
        (sharp if record["totals"] != record["totals_code_only"] else flat).append(label)

    assert sharp == ["arm_a", "arm_b"], sharp
    assert flat == ["reference", "reference_ports"], flat

    # and the specific mixture that was shipped is caught: an arm figure lifted
    # from `totals` never equals its `totals_code_only` counterpart
    for label in sharp:
        record = analyze_tree(RECORDED_TREES[label])
        for figure in ("branch_points", "code_lines", "public_surface"):
            assert record["totals"][figure] != record["totals_code_only"][figure], (
                label,
                figure,
            )


def test_the_test_modules_carry_the_difference_and_it_is_recorded() -> None:
    """The fact that explains the mis-tabling, measured rather than narrated."""

    record = analyze_tree(RECORDED_TREES["arm_a"])
    by_role = {"code": 0, "test": 0}
    for module in record["modules"]:
        by_role[module["role"]] += module["branch_points"]

    assert record["totals"]["branch_points"] == 37
    assert record["totals_code_only"]["branch_points"] == 10
    assert by_role["test"] == 27

    assert "27 of its 37" in INTUITION_DOC.read_text(encoding="utf-8")


def test_excluded_sink_vocabulary_is_printed_with_every_report() -> None:
    """The undercount is stated in the output, not only in the docstring."""

    text = render(analyze_tree(FLAT_TREE))
    assert "undercounts by construction" in text
    for name in ("get", "copy", "walk"):
        assert name in AMBIGUOUS_SINKS_EXCLUDED
        assert f"{name} ~ " in text
    assert not (set(AMBIGUOUS_SINKS_EXCLUDED) & {n for names in EFFECT_SINKS.values() for n in names})


# ---------------------------------------------------------------------------
# the counting rules themselves
# ---------------------------------------------------------------------------


def _figures(tmp_path: Path, source: str) -> ModuleFigures:
    path = tmp_path / "m.py"
    path.write_text(source, encoding="utf-8")
    return measure_module(path, tmp_path)


def test_branch_points_count_exactly_the_documented_constructs(tmp_path: Path) -> None:
    counted = (
        "if a:\n    pass\nelif b:\n    pass\n",  # 2 (elif is a nested if)
        "x = 1 if a else 2\n",  # 1
        "for i in r:\n    pass\n",  # 1
        "while a:\n    break\n",  # 1
        "try:\n    pass\nexcept A:\n    pass\nexcept B:\n    pass\n",  # 2
        "x = [i for i in r if i if i]\n",  # 2
        "x = a and b and c\n",  # 2
    )
    expected = (2, 1, 1, 1, 2, 2, 2)
    for source, count in zip(counted, expected):
        assert count_branch_points(ast.parse(source)) == count, source

    not_counted = (
        "assert a\n",
        "with open('f') as h:\n    pass\n",
        "try:\n    pass\nfinally:\n    pass\n",
        "x = {k: v for k, v in items}\n",
    )
    for source in not_counted:
        assert count_branch_points(ast.parse(source)) == 0, source


def test_max_depth_counts_block_nesting_and_zero_is_flat(tmp_path: Path) -> None:
    flat = ast.parse("def f():\n    return 1\n").body[0]
    assert max_block_depth(flat) == 0

    nested = ast.parse(
        "def f():\n"
        "    if a:\n"
        "        for i in r:\n"
        "            with x:\n"
        "                return 1\n"
    ).body[0]
    assert max_block_depth(nested) == 3

    # a nested def's own depth belongs to that def, not the enclosing one
    inner = ast.parse(
        "def outer():\n"
        "    def inner():\n"
        "        if a:\n"
        "            if b:\n"
        "                return 1\n"
        "    return inner\n"
    ).body[0]
    assert max_block_depth(inner) == 0


def test_instance_state_counts_distinct_self_attributes(tmp_path: Path) -> None:
    figures = _figures(
        tmp_path,
        "class C:\n"
        "    def __init__(self):\n"
        "        self.a = 1\n"
        "        self.b = 2\n"
        "        self.a = 3\n"
        "    def later(self):\n"
        "        self.c, self.d = 1, 2\n"
        "        self.a += 1\n"
        "        local = 9\n",
    )
    assert figures.instance_state == 4


def test_module_state_counts_only_rebound_names(tmp_path: Path) -> None:
    figures = _figures(
        tmp_path,
        "CONSTANT = 1\n"
        "COUNTER = 0\n"
        "COUNTER += 1\n"
        "TWICE = 1\n"
        "TWICE = 2\n"
        "def bump():\n"
        "    global VIA_GLOBAL\n"
        "    VIA_GLOBAL = 1\n",
    )
    assert figures.module_state == 3  # COUNTER, TWICE, VIA_GLOBAL -- not CONSTANT


def test_public_surface_excludes_underscored_and_dunder(tmp_path: Path) -> None:
    figures = _figures(
        tmp_path,
        "PUBLIC = 1\n"
        "_private = 2\n"
        "def visible():\n    pass\n"
        "def _hidden():\n    pass\n"
        "class Shown:\n"
        "    def __init__(self):\n        pass\n"
        "    def method(self):\n        pass\n"
        "    def _helper(self):\n        pass\n"
        "class _Hidden:\n"
        "    def method(self):\n        pass\n",
    )
    assert figures.public_top_level == 3  # PUBLIC, visible, Shown
    assert figures.public_methods == 1  # Shown.method only
    assert figures.public_surface == 4


def test_declared_exports_read_only_from_a_literal(tmp_path: Path) -> None:
    assert _figures(tmp_path, "__all__ = ['a', 'b']\n").declared_exports == 2
    assert _figures(tmp_path, "__all__ = sorted(names)\n").declared_exports is None
    assert _figures(tmp_path, "x = 1\n").declared_exports is None


def test_declared_interfaces_recognise_protocol_abc_and_abstractmethod(
    tmp_path: Path,
) -> None:
    figures = _figures(
        tmp_path,
        "from abc import ABC, abstractmethod\n"
        "from typing import Protocol\n"
        "class P(Protocol):\n"
        "    def a(self): ...\n"
        "    def b(self): ...\n"
        "class A(ABC):\n"
        "    def c(self): ...\n"
        "class D:\n"
        "    @abstractmethod\n"
        "    def e(self): ...\n"
        "class Plain:\n"
        "    def f(self): ...\n",
    )
    assert figures.declared_interfaces == 3
    assert figures.declared_interface_methods == 4


def test_role_is_assigned_by_name_alone(tmp_path: Path) -> None:
    root = tmp_path
    assert classify_role(root / "test_x.py", root) == "test"
    assert classify_role(root / "x_test.py", root) == "test"
    assert classify_role(root / "conftest.py", root) == "test"
    assert classify_role(root / "tests" / "x.py", root) == "test"
    assert classify_role(root / "pkg" / "test" / "x.py", root) == "test"
    assert classify_role(root / "pkg" / "domain.py", root) == "code"
    # a module full of assertions but not named like a test is still `code`
    assert classify_role(root / "pkg" / "contested.py", root) == "code"


def test_internal_import_edges_resolve_within_the_tree_only(tmp_path: Path) -> None:
    tree = tmp_path / "pkg_tree"
    (tree / "pkg").mkdir(parents=True)
    (tree / "pkg" / "__init__.py").write_text("from .domain import D\n", encoding="utf-8")
    (tree / "pkg" / "domain.py").write_text("import json\n", encoding="utf-8")
    (tree / "main.py").write_text("from pkg import D\nimport os\n", encoding="utf-8")

    record = analyze_tree(tree)
    edges = {tuple(edge) for edge in record["internal_import_edges"]}
    assert ("pkg/__init__.py", "pkg/domain.py") in edges
    assert ("main.py", "pkg/__init__.py") in edges
    by_path = {module["path"]: module for module in record["modules"]}
    assert by_path["pkg/domain.py"]["imports_external"] == 1
    assert by_path["main.py"]["imports_external"] == 1


def test_json_record_is_machine_readable_and_carries_its_limits(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(PORTED_TREE), "--json"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0
    record = json.loads(result.stdout)
    assert record["report_version"] >= 1
    assert record["completeness"]["files_parsed"] == 5
    assert record["definitions"]["branch_points"]
    assert record["effect_sinks_excluded"]["get"] == "dict.get"
    assert "MF-020" in record["note"]


def test_two_targets_in_one_invocation_are_two_records() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(FLAT_TREE), str(PORTED_TREE), "--json"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert len(payload["reports"]) == 2
    assert payload["reports"][0]["target"] != payload["reports"][1]["target"]
