#!/usr/bin/env python3
"""Resolve and validate the application context for zancli operations."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve the target application context through zancli."
    )
    selector_group = parser.add_mutually_exclusive_group()
    selector_group.add_argument("--app-id")
    selector_group.add_argument("--app-name")
    parser.add_argument("--env", choices=("dev", "prod", "open"))
    parser.add_argument("--zone")
    parser.add_argument("--expected-app-id")
    parser.add_argument("--expected-env", choices=("dev", "prod", "open"))
    return parser.parse_args()


def context_value(context: dict[str, Any], *names: str) -> Any:
    for name in names:
        value = context.get(name)
        if value not in (None, ""):
            return value
    return None


def unwrap_context_response(response: dict[str, Any]) -> dict[str, Any]:
    data = response.get("data")
    if response.get("success") is True and isinstance(data, dict):
        return data
    return response


def main() -> None:
    args = parse_args()
    skill_dir = Path(__file__).resolve().parent.parent
    bootstrap_script = skill_dir.parent / "zancli-bootstrap" / "scripts" / "ensure_zancli.sh"
    if not bootstrap_script.is_file():
        raise SystemExit(f"Missing zancli bootstrap script: {bootstrap_script}")

    zancli_command = ["zancli", "app", "context"]
    for option, value in (
        ("--app-id", args.app_id),
        ("--app-name", args.app_name),
        ("--env", args.env),
        ("--zone", args.zone),
    ):
        if value:
            zancli_command.extend((option, value))
    zancli_command.extend(("--output", "json"))

    result = subprocess.run(
        ["bash", str(bootstrap_script), "--", *zancli_command],
        check=False,
        stdout=subprocess.PIPE,
        stderr=None,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    try:
        context = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"zancli app context did not return valid JSON: {exc}") from exc
    if not isinstance(context, dict):
        raise SystemExit("zancli app context must return a JSON object.")

    resolved_context = unwrap_context_response(context)

    app_id = context_value(resolved_context, "appId")
    app_name = context_value(resolved_context, "appName")
    environment = context_value(resolved_context, "env", "environment")
    if app_id is None or app_name is None or environment is None:
        raise SystemExit("Application context is incomplete: appId, appName, and environment are required.")
    if args.expected_app_id and str(app_id) != args.expected_app_id:
        raise SystemExit(
            f"Resolved appId {app_id} does not match expected appId {args.expected_app_id}."
        )
    if args.expected_env and environment != args.expected_env:
        raise SystemExit(
            f"Resolved environment {environment} does not match expected environment {args.expected_env}."
        )

    json.dump(resolved_context, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
