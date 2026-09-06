"""The reference implementation must carry what the scaffold emits.

`G-12`, found by the round-002 ticket agent. `scaffold_spec.py` substitutes
`SKILL_ROOT_BOOTSTRAP` into every `adapters.py` it writes, because without it
`from spec_double_compiler.runtime import ...` resolves under **no** interpreter
absent a hand-set `PYTHONPATH`. The file
`references/testgraph_adapters.md` calls *"the concrete reference
implementation"* -- and which `scaffold_spec.py` itself names as the worked
example -- carried none of it.

**`G-10`'s shape exactly**: the scaffold is right and the reference teaches
otherwise. Round 2's `T3` established that agents learn the canonical flag set
by reading that example rather than from the tool; they learn adapter shape
there too, and what they were learning could not be imported.

Asserted byte-for-byte against the scaffold's own constant rather than against a
pasted copy. A resolution order written down twice is a resolution order that
will disagree with itself, and this one has an ordering rule that matters --
`Path.home()` is deliberately LAST, so a project or worktree home outranks the
operator's global one.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from scaffold_spec import SKILL_ROOT_BOOTSTRAP  # type: ignore[import-not-found]  # noqa: E402

REFERENCE = REPO_ROOT / "examples/distributed_history/specs/program_model/adapters.py"


def test_the_reference_adapters_carry_the_scaffolds_bootstrap_verbatim() -> None:
    source = REFERENCE.read_text(encoding="utf-8")
    block = SKILL_ROOT_BOOTSTRAP.rstrip("\n")
    assert block in source, (
        "the reference `adapters.py` does not carry the block the scaffold emits "
        "into every adapters.py it writes. An agent copying adapter shape from "
        "this file gets a module that imports under no interpreter without a "
        "hand-set PYTHONPATH. Re-insert it FROM `scaffold_spec.SKILL_ROOT_BOOTSTRAP` "
        "rather than by hand."
    )


def test_the_bootstrap_resolves_before_the_import_it_protects() -> None:
    """Order is the whole point: resolving after the import has already failed
    leaves an inherited PYTHONPATH outranking the bound home.

    The scaffold's own docstring says so -- deciding inside
    `except ModuleNotFoundError` makes the resolution conditional on nothing
    else having answered first. A block placed below the import it protects
    would satisfy the test above and none of its purpose.
    """
    lines = REFERENCE.read_text(encoding="utf-8").splitlines()

    # BY LINE, not by substring. The first version searched the whole text and
    # matched the phrase inside the explanatory COMMENT above the block --
    # prose, describing the import, mistaken for the import. That is the exact
    # coupling `scripts/verdict.py` exists to remove, reproduced in the test
    # written to guard against it, on its first run.
    def first_line_starting(prefix: str) -> int:
        for index, line in enumerate(lines):
            if line.startswith(prefix):
                return index
        raise AssertionError(f"no statement line begins with {prefix!r}")

    bootstrap_at = first_line_starting("_ensure_spec_double_compiler()")
    import_at = first_line_starting("from spec_double_compiler.runtime import")
    assert bootstrap_at < import_at, (
        "the bootstrap runs AFTER the import it exists to make possible, which "
        "is the ordering its own docstring refuses"
    )


def _import_probe(target: Path) -> str:
    return (
        "import sys, importlib.util as u;"
        f"sys.path.insert(0, {str(target.parents[2])!r});"
        f"spec = u.spec_from_file_location('ref_adapters', {str(target)!r});"
        "m = u.module_from_spec(spec); spec.loader.exec_module(m);"
        "import spec_double_compiler as sdc;"
        "print('OK', sdc.__file__)"
    )


def test_it_imports_with_no_skill_manager_home_reachable_at_all(tmp_path) -> None:
    """The CI condition, and the first version of this test never reached it.

    It cleared `PYTHONPATH` only, and passed -- but this checkout lives UNDER
    the operator's home directory, so the resolver's ancestor walk found
    `~/.skill-manager` whatever the environment said. **The test was green for a
    property of this machine, not of this repository**, and would have gone red
    on any runner that checks out elsewhere. Found by the blind review of `#318`.

    So the environment is stripped of every source the resolver consults --
    `SPEC_DOUBLE_COMPILER_HOME`, `SKILL_MANAGER_HOME`, `PYTHONPATH` and `HOME` --
    and the repository is copied somewhere with no home above it.
    """
    import os
    import shutil
    import subprocess

    checkout = tmp_path / "checkout"
    shutil.copytree(
        REPO_ROOT, checkout,
        ignore=shutil.ignore_patterns(
            ".git", "__pycache__", ".skill-manager", "build", ".gradle", "evidence",
        ),
        symlinks=True,
    )
    target = checkout / "examples/distributed_history/specs/program_model/adapters.py"
    assert target.is_file(), "the copy did not include the reference adapters"

    env = {
        k: v for k, v in os.environ.items()
        if k not in ("SPEC_DOUBLE_COMPILER_HOME", "SKILL_MANAGER_HOME", "PYTHONPATH")
    }
    env["HOME"] = str(tmp_path / "no-home")

    proc = subprocess.run(
        [sys.executable, "-c", _import_probe(target)],
        cwd=tmp_path, env=env, text=True, capture_output=True, timeout=180,
    )
    assert proc.returncode == 0, (
        "the reference adapters do not import on a checkout with no Skill "
        "Manager home above it -- i.e. on CI:\n" + proc.stdout + proc.stderr
    )
    assert str(checkout) in proc.stdout, (
        "it imported, but not from the checkout under test:\n" + proc.stdout
    )


def test_the_checkout_outranks_an_installed_skill(tmp_path) -> None:
    """The hazard the block's own docstring names, produced by the block itself.

    `sys.path.insert(0, home)` put an INSTALLED spec-double-compiler ahead of
    the repository whose tests were running, so the reference example inside
    this skill's own repo exercised a different build than the checkout under
    review. Confirmed before the fix: it resolved to
    `~/.skill-manager/skills/spec-double-compiler/`.

    The resolver now tries the enclosing checkout first. A scaffolded downstream
    project has no ancestor holding the package, so nothing changes for it.
    """
    import os
    import subprocess

    target = REPO_ROOT / "examples/distributed_history/specs/program_model/adapters.py"
    env = {k: v for k, v in os.environ.items() if k != "SKILL_MANAGER_HOME"}
    proc = subprocess.run(
        [sys.executable, "-c", _import_probe(target)],
        cwd=tmp_path, env=env, text=True, capture_output=True, timeout=180,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert str(REPO_ROOT) in proc.stdout and ".skill-manager" not in proc.stdout, (
        "the reference adapters resolved spec_double_compiler somewhere other "
        "than this checkout:\n" + proc.stdout
    )
