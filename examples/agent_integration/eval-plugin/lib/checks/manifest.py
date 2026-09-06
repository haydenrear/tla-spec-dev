"""Is `spec_manifest.yaml` a manifest, or a token? EXIT CODE ONLY.

Run under the same write-denying profile as its sibling. It parses
agent-authored YAML rather than importing agent-authored code, so the risk is
lower -- but a check that writes its own verdict is a check whose verdict can
be written by whatever it just executed, and the rule is worth keeping uniform.

Exit 0  a mapping with >= 3 keys, at least one of them a manifest key
Exit 1  anything else, including a one-key token
"""

from __future__ import annotations

import pathlib
import re
import sys

MANIFEST_KEYS = {"module", "modules", "ports", "invariants", "finite_model", "codegen"}


def main() -> int:
    src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "specs/program_model/spec_manifest.yaml")
    if not src.is_file():
        print("no manifest")
        return 1
    text = src.read_text(encoding="utf-8")

    # PyYAML is not guaranteed: the hook's python3 is whatever is on PATH, and
    # treating ImportError as "the manifest did not parse" once cost a real
    # manifest its verdict.
    try:
        import yaml

        document = yaml.safe_load(text)
        if not isinstance(document, dict):
            print("manifest is not a mapping")
            return 1
        keys = set(document)
    except ImportError:
        keys = {m.group(1) for m in re.finditer(r"^([A-Za-z_][A-Za-z0-9_-]*):", text, re.M)}
        print(f"no PyYAML; scanned top-level keys instead: {sorted(keys)}")
    except Exception as exc:
        print(f"manifest did not parse: {exc}")
        return 1

    hit = sorted(keys & MANIFEST_KEYS)
    if len(keys) < 3 or not hit:
        print(f"manifest is a token, not a manifest: keys={sorted(keys)}")
        return 1
    print(f"manifest ok: {hit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
