from __future__ import annotations

from typing import Any


def build_overview(
    module: str,
    chip_intro: str,
    pin_rows: list[tuple[str, str, str]],
) -> dict[str, Any] | None:
    return None


def build_chip_intro(module: str) -> str | None:
    return None


def build_plan_item_specs(
    module: str,
    by_family: dict[str, list[str]],
) -> list[dict[str, Any]] | None:
    return None


def build_requirement_objects(module: str, source: Any) -> list[Any] | None:
    return None


def get_benchmark(module: str) -> dict[str, Any] | None:
    return None
