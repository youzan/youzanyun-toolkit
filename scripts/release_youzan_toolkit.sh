#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHEBUSTER="${CACHEBUSTER:-release-$(date -u +%Y%m%d%H%M%S)}"
UPDATER="${CODEX_PLUGIN_CACHEBUSTER_UPDATER:-$HOME/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py}"

python3 "$UPDATER" "$ROOT_DIR/plugins/youzan-toolkit" --cachebuster "$CACHEBUSTER"
"$ROOT_DIR/scripts/validate_plugins.sh"
