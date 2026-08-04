#!/usr/bin/env python3
"""Validate release metadata that is not covered by the plugin schema."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


DEFAULT_CLI_EXTENSION_MIN_VERSION = "0.3.7"


def version_tuple(version: str) -> tuple[int, int, int]:
    match = re.match(r"^\s*v?(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise ValueError(f"unsupported semver version: {version!r}")
    return tuple(int(part) for part in match.groups())


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_yzy_release.py <yzy-release.json>", file=sys.stderr)
        return 2

    release_path = Path(sys.argv[1])
    release = json.loads(release_path.read_text(encoding="utf-8"))
    manifest_min = release.get("extension", {}).get("minimumVersion")
    if not manifest_min:
        print("extension.minimumVersion is required", file=sys.stderr)
        return 1

    cli_min = os.environ.get("YZY_CLI_EXTENSION_MIN_VERSION", DEFAULT_CLI_EXTENSION_MIN_VERSION)
    if version_tuple(manifest_min) < version_tuple(cli_min):
        print(
            "extension.minimumVersion "
            f"{manifest_min} is lower than CLI compatibility requirement {cli_min}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
