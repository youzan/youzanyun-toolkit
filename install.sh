#!/usr/bin/env bash
set -euo pipefail

# Install the local checkout for Codex plugin development and testing.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MARKETPLACE="${MARKETPLACE:-youzan}"
PLUGIN="${PLUGIN:-youzan-toolkit}"

usage() {
  cat <<'EOF'
Usage:
  ./install.sh

Install youzan-toolkit from this local checkout for development testing.
Use this instead of the Git marketplace install when you want Codex to load
local plugin or skill changes before publishing.

Environment:
  MARKETPLACE  Marketplace name to install from. Defaults to youzan.
  PLUGIN       Plugin name to install. Defaults to youzan-toolkit.
EOF
}

while (($#)); do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if ! command -v codex >/dev/null 2>&1; then
  echo "codex command not found. Install or configure Codex CLI first." >&2
  exit 1
fi

if [[ ! -f "$ROOT_DIR/marketplace.json" ]]; then
  echo "Missing marketplace.json in $ROOT_DIR." >&2
  exit 1
fi

if [[ ! -d "$ROOT_DIR/plugins/$PLUGIN" ]]; then
  echo "Missing plugin directory: $ROOT_DIR/plugins/$PLUGIN." >&2
  exit 1
fi

"$ROOT_DIR/scripts/validate_plugins.sh"

codex plugin marketplace add "$ROOT_DIR"
codex plugin add "$PLUGIN@$MARKETPLACE"

cat <<EOF

Installed local $PLUGIN from $ROOT_DIR.
Open a new Codex task to load the updated skills.
EOF
