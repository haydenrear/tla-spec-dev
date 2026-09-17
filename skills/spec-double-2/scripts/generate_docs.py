#!/usr/bin/env python3
"""Generate docs.md for a spec manifest without regenerating code."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from extract_spec_manifest import load_manifest, validate_manifest  # noqa: E402
from generate_python import render_docs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    errors = validate_manifest(manifest, args.manifest)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_docs(manifest, args.manifest))
    print(f"generated {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
