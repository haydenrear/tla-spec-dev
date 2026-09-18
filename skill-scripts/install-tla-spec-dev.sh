#!/usr/bin/env bash
set -euo pipefail

: "${SKILL_MANAGER_BIN_DIR:?SKILL_MANAGER_BIN_DIR is required}"
: "${SKILL_MANAGER_CACHE_DIR:?SKILL_MANAGER_CACHE_DIR is required}"
: "${SKILL_DIR:?SKILL_DIR is required}"
: "${SKILL_NAME:=tla-spec-dev}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "tla-spec-dev install requires python3" >&2
  exit 127
fi

# SI-11: this dep is declared on the PLUGIN, so skill-manager sets SKILL_DIR to
# the plugin root and SKILL_NAME to the plugin's name. The entrypoint is inside
# the contained skill, one `skills/spec-double-2/` rung down. It used to be
# "$SKILL_DIR/scripts/tla_spec_dev.py", which was right while the dep sat on the
# contained skill — and which would now silently resolve against the plugin
# root's OWN scripts/ directory, a different tree that really exists.
ENTRYPOINT="$SKILL_DIR/skills/spec-double-2/scripts/tla_spec_dev.py"
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
