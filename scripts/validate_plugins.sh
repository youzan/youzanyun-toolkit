#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VALIDATOR="${CODEX_PLUGIN_VALIDATOR:-$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py}"
SKILL_VALIDATOR="${CODEX_SKILL_VALIDATOR:-$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py}"
PLUGIN_DIR="$ROOT_DIR/plugins/youzan-toolkit"

python3 "$VALIDATOR" "$PLUGIN_DIR"

for skill_dir in "$PLUGIN_DIR"/skills/*; do
  [[ -d "$skill_dir" ]] || continue
  python3 "$SKILL_VALIDATOR" "$skill_dir"
done
