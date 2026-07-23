#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VALIDATOR="${CODEX_PLUGIN_VALIDATOR:-$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py}"

python3 "$VALIDATOR" "$ROOT_DIR/plugins/youzan-toolkit"
