#!/usr/bin/env sh
set -eu
if [ -z "${TLA2TOOLS_JAR:-}" ]; then
  echo "Set TLA2TOOLS_JAR to a locally obtained tla2tools.jar."
  exit 1
fi
test -f "$TLA2TOOLS_JAR"
echo "Using TLC jar: $TLA2TOOLS_JAR"
