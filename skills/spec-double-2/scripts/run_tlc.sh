#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: $0 SPEC.tla MC.cfg" >&2
  exit 2
fi

SPEC_PATH="$1"
CFG_PATH="$2"
SPEC_DIR="$(cd "$(dirname "$SPEC_PATH")" && pwd)"
SPEC_FILE="$(basename "$SPEC_PATH")"
CFG_FILE="$(basename "$CFG_PATH")"

if [ ! -f "$SPEC_PATH" ]; then
  echo "spec not found: $SPEC_PATH" >&2
  exit 1
fi

if [ ! -f "$CFG_PATH" ]; then
  echo "config not found: $CFG_PATH" >&2
  exit 1
fi

cd "$SPEC_DIR"

# VAL-03: TLC writes its states/ scratch directory under -metadir, which
# defaults to the working directory -- polluting the target spec dir. Point
# it at a temp dir and remove it on exit (the EXIT trap also runs when TLC
# fails or times out).
METADIR="$(mktemp -d "${TMPDIR:-/tmp}/tla-spec-dev-tlc.XXXXXX")"
trap 'rm -rf "$METADIR"' EXIT

if command -v tlc2 >/dev/null 2>&1; then
  tlc2 -metadir "$METADIR" -config "$CFG_FILE" "$SPEC_FILE"
  exit $?
fi

if [ -n "${TLA2TOOLS_JAR:-}" ]; then
  java -cp "$TLA2TOOLS_JAR" tlc2.TLC -metadir "$METADIR" -config "$CFG_FILE" "$SPEC_FILE"
  exit $?
fi

echo "tlc2 was not found. Install this skill with skill-manager or set TLA2TOOLS_JAR." >&2
exit 1
