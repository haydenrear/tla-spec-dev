#!/usr/bin/env bash
set -euo pipefail

: "${SKILL_MANAGER_BIN_DIR:?SKILL_MANAGER_BIN_DIR is required}"
: "${SKILL_MANAGER_CACHE_DIR:?SKILL_MANAGER_CACHE_DIR is required}"
: "${SKILL_DIR:?SKILL_DIR is required}"
: "${SKILL_NAME:=spec-double-compiler}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "tla-spec-dev install requires python3" >&2
  exit 127
fi

ENTRYPOINT="$SKILL_DIR/scripts/tla_spec_dev.py"
if [[ ! -f "$ENTRYPOINT" ]]; then
  echo "tla-spec-dev entrypoint not found at $ENTRYPOINT" >&2
  exit 1
fi

mkdir -p "$SKILL_MANAGER_BIN_DIR" "$SKILL_MANAGER_CACHE_DIR"

WRAPPER="$SKILL_MANAGER_BIN_DIR/tla-spec-dev"
cat > "$WRAPPER" <<SH
#!/usr/bin/env bash
set -euo pipefail

exec python3 "$ENTRYPOINT" "\$@"
SH
chmod 0755 "$WRAPPER"

"$WRAPPER" --help >/dev/null
echo "installed tla-spec-dev for $SKILL_NAME at $WRAPPER"
