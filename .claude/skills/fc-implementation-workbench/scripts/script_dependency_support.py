#!/usr/bin/env python3
"""Shared dependency checks for implementation-workbench scripts."""

from __future__ import annotations

import importlib.util
import sys


def _install_command(modules: list[str]) -> str:
    return f"{sys.executable} -m pip install {' '.join(modules)}"


def require_modules(modules: dict[str, str], *, context: str) -> None:
    missing = [package for package, module_name in modules.items() if importlib.util.find_spec(module_name) is None]
    if not missing:
        return
    names = ", ".join(missing)
    command = _install_command(missing)
    raise SystemExit(
        f"ERROR: missing Python dependencies for {context}: {names}\n"
        f"Install them with: {command}"
    )
