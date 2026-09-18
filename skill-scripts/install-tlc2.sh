#!/usr/bin/env bash
set -euo pipefail

: "${SKILL_MANAGER_BIN_DIR:?}"
: "${SKILL_MANAGER_CACHE_DIR:?}"

if ! command -v java >/dev/null 2>&1; then
  echo "java is required to run tlc2. Install a JRE or JDK, then reinstall or sync this skill." >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required to download tla2tools from the TLA+ GitHub releases." >&2
  exit 1
fi

JAR_DIR="$SKILL_MANAGER_BIN_DIR/.spec-double-compiler"
mkdir -p "$JAR_DIR"

VERSION_LABEL="${TLA2TOOLS_VERSION:-latest}"
if [ -n "${TLA2TOOLS_URL:-}" ]; then
  JAR_URL="$TLA2TOOLS_URL"
elif [ "$VERSION_LABEL" = "latest" ]; then
  JAR_URL="https://github.com/tlaplus/tlaplus/releases/latest/download/tla2tools.jar"
else
  TAG="$VERSION_LABEL"
  case "$TAG" in
    v*) ;;
    *) TAG="v$TAG" ;;
  esac
  JAR_URL="https://github.com/tlaplus/tlaplus/releases/download/$TAG/tla2tools.jar"
fi

JAR_TMP="$SKILL_MANAGER_CACHE_DIR/tla2tools-$VERSION_LABEL.jar.tmp"
JAR_PATH="$JAR_DIR/tla2tools.jar"

curl -fL --retry 3 --retry-delay 1 "$JAR_URL" -o "$JAR_TMP"
mv "$JAR_TMP" "$JAR_PATH"

WRAPPER="$SKILL_MANAGER_BIN_DIR/tlc2"
cat > "$WRAPPER" <<'SH'
#!/usr/bin/env bash
set -euo pipefail

BIN_DIR="$(cd "$(dirname "$0")" && pwd)"
JAR="${TLA2TOOLS_JAR:-$BIN_DIR/.spec-double-compiler/tla2tools.jar}"

if [ ! -f "$JAR" ]; then
  echo "tla2tools jar not found at $JAR" >&2
  echo "Set TLA2TOOLS_JAR or reinstall/sync the spec-double-compiler skill." >&2
  exit 1
fi

exec java -cp "$JAR" tlc2.TLC "$@"
SH
chmod 0755 "$WRAPPER"

echo "installed tlc2 wrapper for tla2tools $VERSION_LABEL"
