#!/usr/bin/env bash
set -euo pipefail

: "${SKILL_MANAGER_BIN_DIR:?}"
: "${SKILL_MANAGER_CACHE_DIR:?}"

if ! command -v java >/dev/null 2>&1; then
  echo "java is required to run tlc2. Install a JRE or JDK, then reinstall or sync this skill." >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required to download tla2tools from Maven Central." >&2
  exit 1
fi

JAR_DIR="$SKILL_MANAGER_BIN_DIR/.spec-double-compiler"
mkdir -p "$JAR_DIR"

VERSION="${TLA2TOOLS_VERSION:-}"
if [ -z "$VERSION" ]; then
  METADATA_URL="https://repo1.maven.org/maven2/org/lamport/tla2tools/maven-metadata.xml"
  METADATA="$(curl -fsSL "$METADATA_URL")"
  VERSION="$(printf '%s\n' "$METADATA" | sed -n 's:.*<release>\(.*\)</release>.*:\1:p' | head -n 1)"
  if [ -z "$VERSION" ]; then
    VERSION="$(printf '%s\n' "$METADATA" | sed -n 's:.*<latest>\(.*\)</latest>.*:\1:p' | head -n 1)"
  fi
fi

if [ -z "$VERSION" ]; then
  echo "could not determine tla2tools version from Maven metadata" >&2
  exit 1
fi

JAR_TMP="$SKILL_MANAGER_CACHE_DIR/tla2tools-$VERSION.jar.tmp"
JAR_PATH="$JAR_DIR/tla2tools.jar"
JAR_URL="https://repo1.maven.org/maven2/org/lamport/tla2tools/$VERSION/tla2tools-$VERSION.jar"

curl -fsSL "$JAR_URL" -o "$JAR_TMP"
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

echo "installed tlc2 wrapper for tla2tools $VERSION"
