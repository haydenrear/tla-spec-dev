"""A committed driver whose default `--out` the toolchain refuses is unrunnable.

E-02, round 2 of the agent-ergonomics evaluation. `#301` made
``resolve_spec_tree_out`` refuse any generated-case root outside a ``specs/``
directory, because the ``spec_tree`` effect port declares target ``**/specs/**``
and a write anywhere else is an undeclared effect. That refusal was correct.

What it also did was break
``examples/distributed_history/scripts/regenerate_tlc_cases.py``, whose default
was ``test_graph/build/generated`` -- chosen deliberately, as its own VAL-09
comment records, precisely *because* the corpus lived outside the spec tree.
The example's committed regeneration path could not run as written.

**Nothing went red**, and the reason is the point: the driver is a committed
script with no caller. The suite never invokes it. This is the second finding of
that exact shape -- the ``history-archive-excludes`` defect shipped with two
green tests because both called the helper directly and neither called the path
that used it.

So this test does not run the drivers. It asserts the one property whose absence
made them unrunnable: **a driver's default output root must be a path the
toolchain's own resolver accepts.** Running them needs TLC and minutes; the
contract needs neither, and it is the contract that broke.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# (module path, the attribute holding its default generated-case root)
#
# E-08: this list held ONE driver and the test passed, while THREE more were
# broken the same way and the effectProviderExamples test graph node was red on
# main. A one-element parametrisation is not a guard, it is an example -- so the
# list is now every committed driver that shells out to the generator, and
# `test_every_generator_driver_is_listed` refuses to let a new one be added
# without landing here.
DRIVERS = [
    (
        REPO_ROOT / "examples/distributed_history/scripts/regenerate_tlc_cases.py",
        "DEFAULT_GENERATED_DIR",
    ),
    (
        REPO_ROOT / "examples/effect_providers/atomic_publisher/regenerate.py",
        "GENERATED_DIR",
    ),
    (
        REPO_ROOT / "examples/effect_providers/reminder_worker/regenerate.py",
        "GENERATED_ROOT",
    ),
    (
        REPO_ROOT / "examples/effect_providers/legacy_payment_http/scripts/regenerate.py",
        "GENERATED",
    ),
]

#: Drivers whose generated-case root is KNOWN to sit outside any `specs/` tree,
#: with the issue that decides where it should live. These are xfailed rather
#: than deleted: a skipped row records the defect, a missing row hides it.
KNOWN_OUTSIDE_SPEC_TREE = {
    "reminder_worker": "#314 -- 23 tracked files under generated/; relocating is a decision",
    "legacy_payment_http": "#314 -- 16 tracked files, hardcoded in validate.py and test_project.py",
}


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader, f"cannot load {path}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "driver_path,attr", DRIVERS, ids=lambda v: v.name if isinstance(v, Path) else v
)
def test_driver_default_out_is_accepted_by_the_resolver(driver_path: Path, attr: str) -> None:
    """The refusal that broke this driver is the one that must accept its default."""
    if not driver_path.is_file():
        pytest.skip(f"{driver_path} is not present in this checkout")

    import sys

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        from spec_paths import (  # type: ignore[import-not-found]
            SpecTreePathError,
            resolve_spec_tree_out,
        )
    finally:
        sys.path.pop(0)

    module = _load(driver_path)
    default = getattr(module, attr, None)
    assert default is not None, f"{driver_path.name} has no {attr}"
    # Drivers name their spec directory differently (SPEC_DIR / SPEC_ROOT), and
    # one names it not at all. The resolver only needs a spec directory to
    # resolve RELATIVE paths against; every default checked here is absolute, so
    # a derived fallback is honest rather than a fudge.
    spec_dir = getattr(module, "SPEC_DIR", None) or getattr(module, "SPEC_ROOT", None)
    if spec_dir is None:
        project_root = getattr(module, "PROJECT_ROOT", None) or getattr(
            module, "EXAMPLE_ROOT", None
        )
        assert project_root is not None, (
            f"{driver_path.name} exposes no SPEC_DIR, SPEC_ROOT, PROJECT_ROOT or "
            "EXAMPLE_ROOT, so this test cannot locate its spec tree"
        )
        spec_dir = Path(project_root) / "specs" / "program_model"

    # Catch ONLY SpecTreePathError. The first version of this test caught bare
    # Exception, called the resolver with the wrong arity, and reported the
    # resulting TypeError as though it were the finding -- a green-shaped
    # failure, which is this project's own BLIND class pointed at its own pin.
    # A signature error must crash the test, not masquerade as the defect.
    known = next(
        (why for name, why in KNOWN_OUTSIDE_SPEC_TREE.items() if name in str(driver_path)),
        None,
    )
    try:
        resolve_spec_tree_out(Path(default), Path(spec_dir), flag="--out")
    except SpecTreePathError as exc:  # pragma: no cover - failure path is the point
        if known:
            pytest.xfail(f"{driver_path.name}: {known}\n  {exc}")
        pytest.fail(
            f"{driver_path.name}'s {attr} is {default}, which the toolchain's own "
            f"resolver refuses:\n  {exc}\n"
            "A committed driver whose default output root is refused cannot be run "
            "as written, and no test calls it, so nothing else would report this."
        )


def test_at_least_one_driver_is_checked() -> None:
    """Guard the guard: an empty DRIVERS list would pass vacuously."""
    assert DRIVERS, "no drivers listed -- this test would pass vacuously"


def test_every_generator_driver_is_listed() -> None:
    """A driver that shells out to the generator and is not listed above is unguarded.

    E-08 is exactly this: the list had one entry, three more drivers existed,
    and the parametrisation was green over all of them because they were not in
    it. **A guard that only covers what somebody remembered to add is not a
    guard** -- so discovery is mechanical, and a new driver fails here until it
    is listed.
    """
    found = set()
    for path in (REPO_ROOT / "examples").rglob("*.py"):
        if any(part in {".venv", "build", "evidence", "generated"} for part in path.parts):
            continue
        text = path.read_text(errors="replace")
        # Naming the generator is not invoking it. The first version of this
        # check matched any mention and flagged three files that list the path
        # in a FORBIDDEN_FRAMEWORK_SURFACES constant or a line-range table --
        # a false positive, which is how a guard gets switched off. A driver
        # that actually runs the generator passes it `--out`.
        if "generate_cases_from_tlc_dump.py" in text and '"--out"' in text:
            found.add(path.resolve())
    listed = {p.resolve() for p, _ in DRIVERS}
    unlisted = found - listed
    assert not unlisted, (
        "these drivers invoke the case generator but are not in DRIVERS, so "
        "nothing checks their output roots:\n  "
        + "\n  ".join(sorted(str(p.relative_to(REPO_ROOT)) for p in unlisted))
    )


@pytest.mark.parametrize(
    "driver_path,attr", DRIVERS, ids=lambda v: v.name if isinstance(v, Path) else v
)
def test_driver_does_not_point_dot_at_a_temp_dir(driver_path: Path, attr: str) -> None:
    """`--dot` in a temp dir is a destructive delete, not just a refused write.

    ``run_tlc_dump`` derives the TLC metadir from this path's PARENT and
    ``shutil.rmtree``s it, so an unconstrained ``--dot`` deletes a
    caller-chosen directory that the ``spec_tree_delete`` port does not cover.
    Two of the four drivers did this (E-08) and the refusal is what turned the
    effectProviderExamples node red.

    Checked by reading the source rather than by running it: a real run needs
    TLC and minutes, and the property that broke is textual.
    """
    if not driver_path.is_file():
        pytest.skip(f"{driver_path} is not present in this checkout")
    text = driver_path.read_text(errors="replace")
    if '"--dot"' not in text and "'--dot'" not in text:
        pytest.skip(f"{driver_path.name} does not pass --dot")

    uses_temp = "TemporaryDirectory" in text or "mkdtemp" in text
    if not uses_temp:
        return
    # A driver may still use a temp dir for OTHER things; what it may not do is
    # hand that directory to --dot.
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "--dot" not in line:
            continue
        arg = lines[i + 1] if i + 1 < len(lines) else ""
        assert not any(tok in arg for tok in ("tmp", "temporary", "temp_dir", "mkdtemp")), (
            f"{driver_path.name}:{i + 2} passes a temp-directory path to --dot:\n"
            f"    {arg.strip()}\n"
            "The TLC metadir is derived from that path's PARENT and rmtree'd, so "
            "this is a destructive delete outside the tree `spec_tree_delete` "
            "declares -- and RC-02 refuses it, which is what made the "
            "effectProviderExamples test graph node red on main (E-08)."
        )


def test_no_committed_corpus_sits_at_a_near_miss_of_a_view_root() -> None:
    """A corpus one separator away from what the generator writes is orphaned, not updated.

    E-06 (#313). ``VIEW_OUTPUT_DIRS["internal"]`` is ``spec-unit``; one example's
    committed corpus sat at ``spec_unit`` -- the same word, the other separator.
    The generator clears its output root, so regenerating **deleted the tracked
    tree and wrote an untracked sibling**, while a ``.gitignore`` rule over the
    parent hid the replacement. ``git status`` showed deletions only, at exit 0.

    The precise defect is a NEAR MISS: a directory whose name normalises to a
    view root but is not spelled like one. Checking that is exact. An earlier
    version of this test asserted every directory under a generated tree was a
    view root, and flagged three that are nothing of the kind -- an intermediate
    ``cases/`` level and two contract trees. **False positives are how a guard
    gets switched off**, so this one only claims what it can actually prove.
    """
    import sys

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        from generate_cases_from_tlc_dump import (  # type: ignore[import-not-found]
            VIEW_OUTPUT_DIRS,
        )
    finally:
        sys.path.pop(0)

    def _norm(name: str) -> str:
        return name.replace("-", "").replace("_", "").lower()

    written = set(VIEW_OUTPUT_DIRS.values())
    written_norm = {_norm(n): n for n in written}

    tracked = subprocess.run(
        ["git", "ls-files", "examples"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.splitlines()

    offenders: dict[str, str] = {}
    for rel in tracked:
        parts = pathlib.PurePosixPath(rel).parts
        if "generated" not in parts:
            # Scoped to generated trees on purpose. Unscoped, this flagged
            # `examples/*/test_graph` -- the Gradle validation project, which
            # normalises to the `testgraph` view root and is an entirely
            # different thing. Three false-positive rounds on this guard; each
            # one is a reason somebody would switch it off.
            continue
        after = parts[parts.index("generated") + 1 :]
        base = parts[: parts.index("generated") + 1]
        for i, part in enumerate(after):
            if part in written:
                continue
            canonical = written_norm.get(_norm(part))
            if canonical is not None:
                offenders["/".join(base + after[: i + 1])] = canonical

    assert not offenders, (
        "committed directories one separator away from a view root the generator "
        "writes -- regenerating deletes these and writes a sibling:\n  "
        + "\n  ".join(f"{k}  ->  should be `{v}`" for k, v in sorted(offenders.items()))
    )


def _example_modules_passing_out() -> list[Path]:
    """Every example module that hands `--out` to something. Discovered, not listed.

    Mechanical for the same reason `test_every_generator_driver_is_listed` is:
    a guard that only covers what somebody remembered to add is not a guard.
    """
    found: list[Path] = []
    for path in sorted((REPO_ROOT / "examples").rglob("*.py")):
        if any(
            part in {".venv", "build", "evidence", "generated", "__pycache__"}
            for part in path.parts
        ):
            continue
        if '"--out"' in path.read_text(errors="replace"):
            found.append(path)
    return found


def test_callers_that_override_a_driver_default_are_also_inside_the_spec_tree() -> None:
    """A CALLER that passes `--out` bypasses the default this file already pins.

    ``examples/run_distributed_history_validation.py`` -- the top-level
    validation for the flagship example -- passed
    ``test_graph/build/generated/validation`` on the command line. `#301`'s
    ``spec_tree`` rule refuses that. `#314` moved the driver's DEFAULT under
    ``specs/`` and this caller, which never uses the default, was not moved with
    it. The example's whole validation exited 2 and **nothing was red**, because
    every existing check here asks about defaults.

    That is the third time in this epic that one rule change reached a surface
    nobody enumerated: the driver defaults, then `--dot`, then the remedy text,
    then the docs, then a test's corpus path (E-14), and now a caller's
    override. So this asserts the property one level out: any module-level
    generated-root constant in a file that passes ``--out`` must be a path the
    resolver accepts.

    What it CANNOT see, said rather than implied: a path composed inline at the
    call site. This finds the named constants, which is where all six of those
    surfaces actually lived.
    """
    import sys

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        from spec_paths import (  # type: ignore[import-not-found]
            SpecTreePathError,
            resolve_spec_tree_out,
        )
    finally:
        sys.path.pop(0)

    offenders: list[str] = []
    checked = 0
    for path in _example_modules_passing_out():
        try:
            module = _load(path)
        except Exception:  # pragma: no cover - an unimportable example is not this test's finding
            continue
        for name in dir(module):
            if "GENERATED" not in name.upper():
                continue
            value = getattr(module, name, None)
            if not isinstance(value, pathlib.Path) or not value.is_absolute():
                continue
            checked += 1
            spec_dir = (
                getattr(module, "SPEC_DIR", None)
                or getattr(module, "SPEC_ROOT", None)
                or value.parent
            )
            try:
                resolve_spec_tree_out(value, pathlib.Path(spec_dir), flag="--out")
            except SpecTreePathError as exc:
                offenders.append(
                    f"{path.relative_to(REPO_ROOT)}:{name} = {value}\n    {exc}"
                )

    assert checked, "no generated-root constants were checked -- this test would pass vacuously"
    assert not offenders, (
        "these example modules pass `--out` and name a generated root the "
        "toolchain's own resolver refuses:\n  " + "\n  ".join(offenders)
    )
