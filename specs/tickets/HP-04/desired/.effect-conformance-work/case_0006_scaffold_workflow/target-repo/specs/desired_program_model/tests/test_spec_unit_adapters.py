"""Example spec-unit adapter test for the CliProject program model.

Runs the generated internal cases through the spec-unit adapters in
`adapters.py`, mapped by `case_adapters.toml`.

The external counterpart is NOT a pytest test: External-view cases run as Test
Graph nodes. See `testgraph_bindings.yml` and
`references/testgraph_adapters.md`.

Reference implementation:
examples/distributed_history/specs/program_model/tests/test_ecommerce_adapters.py

SCAFFOLD: this is skipped until the adapters in adapters.py are implemented and
generated cases exist. Remove the skip once both are real.
"""

import subprocess
import sys
from pathlib import Path

import pytest


SPEC_DIR = Path(__file__).resolve().parents[1]
SPEC_ROOT = SPEC_DIR.parent
REPO_ROOT = SPEC_ROOT.parent

CASES_DIR = SPEC_ROOT / "generated" / "spec-unit" / "cliproject_internal_cases"


def _runner_script() -> Path | None:
    # The runner must be invoked as a script by absolute path, not as
    # `-m scripts.run_generated_case_adapters`: the module name resolves only
    # inside the toolchain repository, and once [effect_providers.*] is
    # configured the runner's import layout requires direct-script mode.
    try:
        import spec_double_compiler
    except ImportError:
        return None
    candidate = (
        Path(spec_double_compiler.__file__).resolve().parents[1]
        / "scripts"
        / "run_generated_case_adapters.py"
    )
    return candidate if candidate.is_file() else None


@pytest.mark.skipif(
    not CASES_DIR.exists(),
    reason="no generated spec-unit cases yet; generate them from Internal.tla first",
)
def test_internal_adapters_run_in_batch(tmp_path: Path) -> None:
    runner = _runner_script()
    if runner is None:
        pytest.skip("spec_double_compiler runtime not importable; set PYTHONPATH to the tla-spec-dev checkout")
    command = [
        sys.executable,
        str(runner),
        str(CASES_DIR),
        "--mapping",
        str(SPEC_DIR / "case_adapters.toml"),
        "--spec-dir",
        str(SPEC_DIR),
        "--view",
        "internal",
        "--batch",
        "--work-dir",
        str(tmp_path / "internal-work"),
        "--import-root",
        str(REPO_ROOT),
    ]
    subprocess.run(command, check=True, cwd=REPO_ROOT)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
