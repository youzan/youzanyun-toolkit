#!/usr/bin/env bash
set -euo pipefail

ZANCLI_INSTALL_URL="${ZANCLI_INSTALL_URL:-https://download.qima-inc.com/files/ops-assets/zancli/install.sh}"
ZANCLI_VERSION="${ZANCLI_VERSION:-v1.0.14-internal.69-gc4f27051}"
CHECK_ONLY=false
COMMAND_ARGS=()

usage() {
  cat <<'EOF'
Usage: ensure_zancli.sh [--check] [-- command [args...]]

Install zancli when necessary, verify the current login, and start an OAuth
login when needed. Pass a command after -- to run it only after verification.
EOF
}

while (($#)); do
  case "$1" in
    --check)
      CHECK_ONLY=true
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --)
      shift
      COMMAND_ARGS=("$@")
      break
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if command -v zancli >/dev/null 2>&1; then
  ZANCLI_PATH="$(command -v zancli)"
elif [[ -x "$HOME/.local/bin/zancli" ]]; then
  ZANCLI_PATH="$HOME/.local/bin/zancli"
else
  if ! command -v curl >/dev/null 2>&1; then
    echo "zancli is not installed and curl is required to install it." >&2
    exit 1
  fi

  echo "Installing zancli ${ZANCLI_VERSION} from the internal channel..."
  curl -fsSL "$ZANCLI_INSTALL_URL" | bash -s -- --version "$ZANCLI_VERSION"
  export PATH="$HOME/.local/bin:${PATH:-}"

  if command -v zancli >/dev/null 2>&1; then
    ZANCLI_PATH="$(command -v zancli)"
  elif [[ -x "$HOME/.local/bin/zancli" ]]; then
    ZANCLI_PATH="$HOME/.local/bin/zancli"
  else
    echo "zancli installation completed without an executable at $HOME/.local/bin/zancli." >&2
    exit 1
  fi
fi

if "$ZANCLI_PATH" whoami >/dev/null 2>&1; then
  echo "zancli login verified." >&2
elif "$CHECK_ONLY"; then
  echo "zancli is not logged in. Run zancli login and try again." >&2
  exit 1
else
  echo "zancli login is required. Complete the browser OAuth flow to continue." >&2
  if [[ -r /dev/tty ]]; then
    "$ZANCLI_PATH" login </dev/tty >&2
  else
    "$ZANCLI_PATH" login >&2
  fi
  "$ZANCLI_PATH" whoami >/dev/null
  echo "zancli login verified." >&2
fi

if ((${#COMMAND_ARGS[@]})); then
  export PATH="$(dirname "$ZANCLI_PATH"):${PATH:-}"
  exec "${COMMAND_ARGS[@]}"
fi
