#!/usr/bin/env python3
"""Ensure zancli is installed at the public stable version."""

from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


INSTALL_URL = os.environ.get(
    "ZANCLI_INSTALL_URL",
    "https://yzy-static.yzcdn.cn/devtools/release/install.sh",
)
STABLE_VERSION_URL = os.environ.get(
    "ZANCLI_STABLE_VERSION_URL",
    "https://yzy-static.yzcdn.cn/devtools/release/stable.txt",
)
REQUIRED_VERSION = os.environ.get("ZANCLI_REQUIRED_VERSION", "1.0.18")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install or upgrade zancli from the public stable channel."
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--print-path", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    return parser.parse_args()


def extract_semver(text: str) -> str:
    match = re.search(r"v?(\d+\.\d+\.\d+)", text)
    return match.group(1) if match else ""


def fetch_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8").strip()


def target_version() -> str:
    try:
        stable = extract_semver(fetch_text(STABLE_VERSION_URL))
    except (OSError, urllib.error.URLError):
        stable = ""
    return stable or extract_semver(REQUIRED_VERSION) or REQUIRED_VERSION


def find_zancli() -> Path | None:
    for name in ("zancli", "zancli.exe"):
        found = shutil.which(name)
        if found:
            return Path(found)

    home = Path.home()
    candidates = [
        Path("/usr/local/bin/zancli"),
        home / ".local" / "bin" / "zancli",
        home / "bin" / "zancli",
        home / "bin" / "zancli.exe",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def zancli_version(binary: Path) -> str:
    for args in (("--version",), ("version",)):
        try:
            result = subprocess.run(
                [str(binary), *args],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
            )
        except OSError:
            continue
        version = extract_semver(result.stdout)
        if version:
            return version
    return ""


def is_windows() -> bool:
    return os.name == "nt" or platform.system().lower().startswith("windows")


def install_windows(version: str) -> Path:
    machine = platform.machine().lower()
    if machine not in {"amd64", "x86_64"}:
        raise SystemExit(f"unsupported Windows architecture: {platform.machine()}; only AMD64 is available")

    install_dir = Path.home() / "bin"
    install_dir.mkdir(parents=True, exist_ok=True)
    output = install_dir / "zancli.exe"
    url = f"https://yzy-static.yzcdn.cn/devtools/release/v{version}/bin/windows/amd64/zancli.exe"
    print(f"Installing zancli {version} for Windows AMD64...", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=60) as response:
        output.write_bytes(response.read())
    return output


def install_unix() -> Path:
    bash = shutil.which("bash")
    if not bash:
        raise SystemExit("bash is required to install or upgrade zancli on this platform.")

    curl = shutil.which("curl")
    if not curl:
        raise SystemExit("curl is required to install or upgrade zancli.")

    print("Installing zancli from the public stable channel...", file=sys.stderr)
    install_cmd = f'"{curl}" -fsSL "{INSTALL_URL}" | "{bash}"'
    if os.geteuid() != 0 and shutil.which("sudo"):
        install_cmd = f'"{curl}" -fsSL "{INSTALL_URL}" | sudo "{bash}"'
    result = subprocess.run(install_cmd, shell=True, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    path = find_zancli()
    if path is None:
        raise SystemExit("zancli installation completed without an executable on PATH.")
    return path


def ensure_zancli() -> Path:
    version = target_version()
    binary = find_zancli()
    current = zancli_version(binary) if binary else ""

    if binary and current == version:
        return binary

    if binary and current:
        print(f"zancli {current} does not match stable {version}; installing stable...", file=sys.stderr)
    elif binary:
        print(f"zancli version cannot be detected; reinstalling stable {version}...", file=sys.stderr)

    binary = install_windows(version) if is_windows() else install_unix()
    if not is_windows():
        mode = binary.stat().st_mode
        binary.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    current = zancli_version(binary)
    if current != version:
        if current:
            raise SystemExit(f"zancli version is {current} after installation, expected {version}.")
        raise SystemExit(f"zancli version cannot be detected after installation, expected {version}.")
    return binary


def command_after_separator(command: list[str]) -> list[str]:
    if command and command[0] == "--":
        return command[1:]
    return command


def verify_login(binary: Path, check_only: bool) -> int:
    result = subprocess.run([str(binary), "whoami"], check=False)
    if result.returncode == 0:
        print("zancli login verified.", file=sys.stderr)
        return 0

    if check_only:
        print("zancli is not logged in. Run zancli login and try again.", file=sys.stderr)
        return result.returncode or 1

    print("zancli login is required. Complete the browser OAuth flow to continue.", file=sys.stderr)
    login = subprocess.run([str(binary), "login"], check=False)
    if login.returncode != 0:
        return login.returncode

    result = subprocess.run([str(binary), "whoami"], check=False)
    if result.returncode == 0:
        print("zancli login verified.", file=sys.stderr)
        return 0
    return result.returncode or 1


def main() -> int:
    args = parse_args()
    binary = ensure_zancli()
    if args.print_path:
        print(binary)

    if args.check:
        return verify_login(binary, check_only=True)

    command = command_after_separator(args.command)
    if command:
        login_status = verify_login(binary, check_only=False)
        if login_status != 0:
            return login_status
        if Path(command[0]).name.lower() in {"zancli", "zancli.exe"}:
            command[0] = str(binary)
        env = os.environ.copy()
        env["PATH"] = f"{binary.parent}{os.pathsep}{env.get('PATH', '')}"
        return subprocess.run(command, check=False, env=env).returncode

    return verify_login(binary, check_only=False)


if __name__ == "__main__":
    raise SystemExit(main())
