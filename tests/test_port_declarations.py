"""Every declared port's target must be falsifiable, and must match reality.

MF-026 F-9. Three declaration/behaviour mismatches were shipped in three
consecutive attempts, in both directions:

  - HP-04 declared `spec_tree_delete` (`**/specs/**`) for a delete that runs at
    an unconstrained `--work-dir`. NARROWER than the behaviour.
  - The first repair declared `case_work_dir_delete` with target `**`, which
    `_target_matches` collapses to `*`, which fnmatch crosses separators with --
    so it accepts every string, and no `filesystem.delete` on that action can
    ever be a gap again. WIDER than the behaviour.
  - The same repair declared `case_program_process` as `*programs/case_*`, with
    an underscore, while the shipped path builder emits `case-<hex>`. Matches
    NOTHING, by construction.

Each was caught by a human or an audit reading code, and none by a test: the
closure that introduced two of them added only literal boundary counts
(26 -> 28), which pass whether or not a port is correct. So this file tests the
class rather than the instances.

A declaration that cannot fail is not a declaration.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from effect_conformance import _target_matches  # noqa: E402

MANIFEST_TREES = ("program_model", "current", "desired_program_model")

# Strings no port should accept. If a target matches these it is degenerate:
# it asserts nothing about where the effect may land, so the port can never be
# reported as a gap and the declaration is decoration.
UNRELATED = (
    "/etc/passwd",
    "totally/unrelated/path.txt",
    "",
    "/",
)

# Ports whose target is `*` DELIBERATELY, because the code genuinely enforces no
# constraint on where the effect lands and the manifest says so: "any glob
# narrower than `*` would assert a constraint the code does not enforce". That
# is a legitimate reason to be unfalsifiable and it is on record beside each one.
#
# It is an ALLOWLIST rather than a blanket exemption so that adding a new
# unfalsifiable port takes a deliberate edit to this file and a reason. The
# first repair reached for `**` here, where the code DOES enforce a constraint
# and documents it as designed -- narrower than the behaviour, then wider than
# it, in consecutive attempts.
DELIBERATELY_UNCONSTRAINED = {
    "cli_artifact",
    "cli_artifact_delete",
    "cli_download",
    "corpus_process",
}


def _ports(tree: str) -> dict[str, dict]:
    """Every declared port in one tree, keyed by name.

    The FIRST version of this file read `effects.ports`, which does not exist --
    the real path is `effects.components.<Component>.ports`. It found zero ports
    and every assertion passed vacuously, which made it the FOURTH instance of
    the class it was written to close: a check that cannot fail. Hence the
    non-empty assertion below. A test that silently finds nothing to test is
    worse than no test, because it reports green.
    """
    import yaml

    base = REPO_ROOT / "specs" / tree
    if tree != "program_model" and not base.is_dir():
        pytest.skip(f"specs/{tree} is absent -- no spec workflow is open")
    manifest = yaml.safe_load((base / "spec_manifest.yaml").read_text())
    components = ((manifest.get("effects") or {}).get("components") or {})
    ports: dict[str, dict] = {}
    for component in components.values():
        ports.update((component or {}).get("ports") or {})
    assert ports, (
        f"specs/{tree}/spec_manifest.yaml declares no ports under "
        "effects.components.<Component>.ports -- either the manifest changed "
        "shape or this reader is looking in the wrong place. Refusing to pass "
        "vacuously."
    )
    return ports


def _port_ids(tree: str) -> list[str]:
    try:
        return sorted(_ports(tree))
    except Exception:  # pragma: no cover - collection must not explode
        return []


@pytest.mark.parametrize("tree", MANIFEST_TREES)
def test_no_declared_port_target_is_degenerate(tree: str) -> None:
    """A target that accepts an arbitrary unrelated path constrains nothing.

    This is the check that would have caught `**` on the day it was written.
    """
    degenerate: list[str] = []
    for name, port in sorted(_ports(tree).items()):
        if name in DELIBERATELY_UNCONSTRAINED:
            continue
        target = str(port.get("target", ""))
        if all(_target_matches(target, probe) for probe in UNRELATED):
            degenerate.append(f"{name} (target {target!r})")
    assert not degenerate, (
        "these ports accept every string, so no effect on them can ever be "
        "reported as a gap:\n  " + "\n  ".join(degenerate) + "\n"
        "`_target_matches` collapses `**` to `*`, and fnmatch's `*` crosses "
        "separators. Declare the component the code actually writes under."
    )


@pytest.mark.parametrize("tree", MANIFEST_TREES)
def test_process_and_path_ports_match_a_path_the_code_actually_produces(tree: str) -> None:
    """Every port whose real target this repo can construct must match it.

    The paths below are built with the SHIPPED builders, not written by hand, so
    a rename in the builder fails this test instead of silently orphaning a port.
    """
    from run_generated_case_adapters import _opaque_path_component

    case_component = _opaque_path_component("case", "SomeCase")
    work = Path("/tmp/some-work-dir")

    # These are the exact expressions the runner uses.
    real_paths = {
        "case_program_process": str(work / "programs" / f"{case_component}.py"),
        "case_work_dir_delete": str(work / "case-work" / case_component),
    }

    ports = _ports(tree)
    unmatched: list[str] = []
    for name, probe in real_paths.items():
        if name not in ports:
            continue
        target = str(ports[name].get("target", ""))
        if not _target_matches(target, probe):
            unmatched.append(f"{name}: target {target!r} does not match {probe!r}")
    assert not unmatched, (
        "these ports declare a target the code can never produce:\n  "
        + "\n  ".join(unmatched)
        + "\n(the component is built by _opaque_path_component, which emits "
        "`<role>-<hex>` with a HYPHEN)"
    )
