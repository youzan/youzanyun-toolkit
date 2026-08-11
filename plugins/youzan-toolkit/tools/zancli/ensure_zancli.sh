#!/usr/bin/env bash
set -euo pipefail

ZANCLI_INSTALL_URL="${ZANCLI_INSTALL_URL:-https://yzy-static.yzcdn.cn/devtools/release/install.sh}"
ZANCLI_STABLE_VERSION_URL="${ZANCLI_STABLE_VERSION_URL:-https://yzy-static.yzcdn.cn/devtools/release/stable.txt}"
ZANCLI_REQUIRED_VERSION="${ZANCLI_REQUIRED_VERSION:-1.0.18}"
CHECK_ONLY=false
COMMAND_ARGS=()

usage() {
  cat <<'EOF'
Usage: ensure_zancli.sh [--check] [-- command [args...]]

Install or upgrade zancli from the public stable channel when necessary,
verify the current login, and start an OAuth login when needed. Pass a
command after -- to run it only after verification.
EOF
}

find_zancli() {
  if command -v zancli >/dev/null 2>&1; then
    command -v zancli
  elif [[ -x /usr/local/bin/zancli ]]; then
    printf '%s\n' "/usr/local/bin/zancli"
  elif [[ -x "$HOME/.local/bin/zancli" ]]; then
    printf '%s\n' "$HOME/.local/bin/zancli"
  elif [[ -x "$HOME/bin/zancli" ]]; then
    printf '%s\n' "$HOME/bin/zancli"
  fi
}

extract_semver() {
  sed -nE 's/.*v?([0-9]+\.[0-9]+\.[0-9]+).*/\1/p' | head -n 1
}

zancli_version() {
  local binary="$1"
  local output=""

  output="$("$binary" --version 2>/dev/null || true)"
  if [[ -z "$output" ]]; then
    output="$("$binary" version 2>/dev/null || true)"
  fi

  printf '%s\n' "$output" | extract_semver
}

target_version() {
  local stable=""

  if command -v curl >/dev/null 2>&1; then
    stable="$(curl -fsSL "$ZANCLI_STABLE_VERSION_URL" 2>/dev/null | extract_semver || true)"
  fi

  if [[ -n "$stable" ]]; then
    printf '%s\n' "$stable"
  else
    printf '%s\n' "$ZANCLI_REQUIRED_VERSION"
  fi
}

install_zancli() {
  if ! command -v curl >/dev/null 2>&1; then
    echo "curl is required to install or upgrade zancli." >&2
    exit 1
  fi

  echo "Installing zancli from the public stable channel..."
  if [[ "$(id -u)" -eq 0 ]]; then
    curl -fsSL "$ZANCLI_INSTALL_URL" | /bin/bash
  elif command -v sudo >/dev/null 2>&1; then
    curl -fsSL "$ZANCLI_INSTALL_URL" | sudo /bin/bash
  else
    curl -fsSL "$ZANCLI_INSTALL_URL" | /bin/bash
  fi
  export PATH="/usr/local/bin:$HOME/.local/bin:$HOME/bin:${PATH:-}"
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

TARGET_VERSION="$(target_version)"
ZANCLI_PATH="$(find_zancli || true)"

if [[ -n "$ZANCLI_PATH" ]]; then
  CURRENT_VERSION="$(zancli_version "$ZANCLI_PATH")"
  if [[ "$CURRENT_VERSION" != "$TARGET_VERSION" ]]; then
    if [[ -n "$CURRENT_VERSION" ]]; then
      echo "zancli $CURRENT_VERSION does not match stable $TARGET_VERSION; installing stable..." >&2
    else
      echo "zancli version cannot be detected; reinstalling stable $TARGET_VERSION..." >&2
    fi
    install_zancli
    ZANCLI_PATH="$(find_zancli || true)"
  fi
else
  install_zancli
  ZANCLI_PATH="$(find_zancli || true)"
fi

if [[ -z "$ZANCLI_PATH" ]]; then
  echo "zancli installation completed without an executable on PATH." >&2
  exit 1
fi

CURRENT_VERSION="$(zancli_version "$ZANCLI_PATH")"
if [[ "$CURRENT_VERSION" != "$TARGET_VERSION" ]]; then
  if [[ -n "$CURRENT_VERSION" ]]; then
    echo "zancli version is $CURRENT_VERSION after installation, expected $TARGET_VERSION." >&2
  else
    echo "zancli version cannot be detected after installation, expected $TARGET_VERSION." >&2
  fi
  exit 1
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
