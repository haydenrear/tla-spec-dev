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
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# (module path, the attribute holding its default generated-case root)
DRIVERS = [
    (
        REPO_ROOT / "examples/distributed_history/scripts/regenerate_tlc_cases.py",
        "DEFAULT_GENERATED_DIR",
    ),
]


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
    spec_dir = getattr(module, "SPEC_DIR", None)
    assert spec_dir is not None, f"{driver_path.name} has no SPEC_DIR"

    # Catch ONLY SpecTreePathError. The first version of this test caught bare
    # Exception, called the resolver with the wrong arity, and reported the
    # resulting TypeError as though it were the finding -- a green-shaped
    # failure, which is this project's own BLIND class pointed at its own pin.
    # A signature error must crash the test, not masquerade as the defect.
    try:
        resolve_spec_tree_out(Path(default), Path(spec_dir), flag="--out")
    except SpecTreePathError as exc:  # pragma: no cover - failure path is the point
        pytest.fail(
            f"{driver_path.name}'s {attr} is {default}, which the toolchain's own "
            f"resolver refuses:\n  {exc}\n"
            "A committed driver whose default output root is refused cannot be run "
            "as written, and no test calls it, so nothing else would report this."
        )


def test_at_least_one_driver_is_checked() -> None:
    """Guard the guard: an empty DRIVERS list would pass vacuously."""
    assert DRIVERS, "no drivers listed -- this test would pass vacuously"
