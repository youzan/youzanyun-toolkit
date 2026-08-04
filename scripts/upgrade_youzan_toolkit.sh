#!/usr/bin/env bash
set -euo pipefail

MARKETPLACE="${MARKETPLACE:-youzan}"
PLUGIN="${PLUGIN:-youzanyun-toolkit}"

codex plugin marketplace upgrade "$MARKETPLACE"
codex plugin add "${PLUGIN}@${MARKETPLACE}"
