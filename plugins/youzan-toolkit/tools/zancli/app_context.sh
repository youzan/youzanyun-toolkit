#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONTEXT_SCRIPT="$PLUGIN_ROOT/skills/yzy-app-context/scripts/resolve_app_context.py"

if [[ ! -f "$CONTEXT_SCRIPT" ]]; then
  echo "Missing app context resolver: $CONTEXT_SCRIPT" >&2
  exit 1
fi

exec python3 "$CONTEXT_SCRIPT" "$@"
