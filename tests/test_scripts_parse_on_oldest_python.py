"""Every CLI source parses on the oldest Python the shim can reach.

The `tla-spec-dev` shim runs `python3` from PATH, which is 3.9 on stock
macOS. Two PEP 701 nested f-strings (3.12+) in one imported module made
the whole CLI fail there with "f-string: expecting '}'", while the suite,
running on 3.12+, stayed green.

`ast.parse(feature_version=...)` cannot catch this — f-string nesting is
decided by the running interpreter's tokenizer — so the check compiles
with a real pre-3.12 interpreter when one can be found.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCES = sorted(
    str(p)
    for d in ("scripts", "spec_double_compiler")
    for p in (ROOT / d).rglob("*.py")
    if "__pycache__" not in p.parts
)
CHECK = (
    "import ast, sys\n"
    "bad = []\n"
    "for f in sys.argv[1:]:\n"
    "    try:\n"
    "        ast.parse(open(f, encoding='utf-8').read(), filename=f)\n"
    "    except SyntaxError as e:\n"
    "        bad.append(f'{f}:{e.lineno}: {e.msg}')\n"
    "print('\\n'.join(bad))\n"
    "sys.exit(1 if bad else 0)\n"
)


def _old_interpreter() -> str | None:
    if sys.version_info < (3, 12):
        return sys.executable
    for name in ("python3.9", "python3.10", "python3.11"):
        found = shutil.which(name)
        if found:
            return found
    uv = shutil.which("uv")
    if uv:
        proc = subprocess.run(
            [uv, "python", "find", "3.9"], capture_output=True, text=True
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    return None


def test_sources_parse_before_pep_701():
    python = _old_interpreter()
    if python is None:
        pytest.skip("no pre-3.12 interpreter available to check against")
    proc = subprocess.run(
        [python, "-c", CHECK, *SOURCES], capture_output=True, text=True
    )
    assert proc.returncode == 0, f"{python} cannot parse:\n{proc.stdout}{proc.stderr}"
