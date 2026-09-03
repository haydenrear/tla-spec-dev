"""A committed generated artifact that nobody compares is a stale artifact.

`G-01`: running the shipped effect-provider validations modified **24 tracked
files** before doing anything else. `HP-03` added the negative corpus and
`generate_python.py` began emitting `effect_providers.py` for any manifest that
declares effect ports; no committed contract followed either change.

**One of the three examples asserted `committed == regenerated`. That one was
red on `main`. The other two had no assertion at all**, so they went green while
rewriting the tree underneath them, and the visible half of the defect was a
third of it.

Regenerating the corpora cleared the symptom. This is the missing guard, and it
is written as one test over every example rather than as a third copy of
reminder_worker's: a per-example assertion is what produced a defect that
existed in three places and was reported in one.

Cheap on purpose -- `generate_python.py` reads a manifest and writes Python. No
TLC, no network, ~2s for all three.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EFFECT_PROVIDERS = REPO_ROOT / "examples" / "effect_providers"
GENERATOR = REPO_ROOT / "scripts" / "generate_python.py"


def _manifests() -> list[Path]:
    """Every example manifest, discovered. A hand-list is what `G-01` was."""
    return sorted(
        m
        for m in EFFECT_PROVIDERS.glob("*/specs/program_model/spec_manifest.yaml")
        if "generated" not in m.parts
    )


def _source_tree(root: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(root)): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts
    }


def test_at_least_one_example_is_checked() -> None:
    assert _manifests(), "no example manifests discovered -- this file is vacuous"


@pytest.mark.parametrize("manifest", _manifests(), ids=lambda m: m.parents[2].name)
def test_the_committed_contract_is_what_the_generator_emits_today(manifest: Path) -> None:
    example = manifest.parents[2]
    with tempfile.TemporaryDirectory(prefix="contract-drift-") as tmp:
        out = Path(tmp)
        completed = subprocess.run(
            [sys.executable, str(GENERATOR), str(manifest), "--out", str(out)],
            cwd=example, text=True, capture_output=True, timeout=120,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr

        produced = [p for p in out.iterdir() if p.is_dir()]
        assert len(produced) == 1, f"expected one generated package, got {produced}"
        package = produced[0]

        # The committed copy is found BY NAME rather than by a per-example path,
        # because the three examples put it in three different places and a
        # table of those paths is the thing that goes stale.
        #
        # "Committed" means IN GIT, asked rather than inferred from the layout.
        # On disk, `reminder_worker` also carries an untracked leftover
        # `generated/reminder_contract` from an older run; a directory that git
        # does not know about cannot have drifted from anything.
        #
        # `evidence/` is excluded on purpose: those are FROZEN records of past
        # runs. They are supposed to differ from today's generator, and
        # comparing them to it would turn the project's own evidence discipline
        # into a permanent red.
        tracked = subprocess.run(
            ["git", "ls-files", str(example.relative_to(REPO_ROOT))],
            cwd=REPO_ROOT, text=True, capture_output=True, check=False,
        ).stdout.splitlines()
        committed_dirs = {
            (REPO_ROOT / rel).parent for rel in tracked
            if rel and "evidence/" not in rel
        }
        candidates = [d for d in committed_dirs if d.name == package.name]
        assert candidates, (
            f"{example.name} generates a package `{package.name}` that is not "
            "committed anywhere under the example. Either commit it or say in "
            "the example's README that its contract is generated on demand -- an "
            "artifact that is neither is the state `G-01` was."
        )
        assert len(candidates) == 1, f"ambiguous committed contract: {candidates}"
        committed = candidates[0]

        produced_tree, committed_tree = _source_tree(package), _source_tree(committed)
        missing = sorted(set(produced_tree) - set(committed_tree))
        extra = sorted(set(committed_tree) - set(produced_tree))
        assert not missing and not extra, (
            f"{example.name}'s committed contract has drifted from the generator.\n"
            f"  the generator emits, and the tree lacks: {missing}\n"
            f"  the tree carries, and the generator does not emit: {extra}\n"
            f"Regenerate with the example's own driver. This is `G-01`: the file "
            "set drifting is exactly how 24 tracked files came to be rewritten by "
            "a validation run."
        )
        differing = sorted(k for k in produced_tree if produced_tree[k] != committed_tree[k])
        assert not differing, (
            f"{example.name}'s committed contract differs in content from what "
            f"the generator emits today: {differing}"
        )
