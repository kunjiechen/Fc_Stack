from __future__ import annotations

from typing import Any

from . import nca9539

_PROFILE_REGISTRY = {
    "NCA9539": nca9539,
}


def get_profile(module: str):
    return _PROFILE_REGISTRY.get(module.upper())


def build_overview(
    module: str,
    chip_intro: str,
    pin_rows: list[tuple[str, str, str]],
) -> dict[str, Any] | None:
    profile = get_profile(module)
    if profile is None:
        return None
    return profile.build_overview(chip_intro=chip_intro, pin_rows=pin_rows)


def build_chip_intro(module: str) -> str | None:
    profile = get_profile(module)
    if profile is None or not hasattr(profile, "build_chip_intro"):
        return None
    return profile.build_chip_intro()


def build_plan_item_specs(
    module: str,
    by_family: dict[str, list[str]],
) -> list[dict[str, Any]] | None:
    profile = get_profile(module)
    if profile is None:
        return None
    return profile.build_plan_item_specs(by_family)


def build_requirement_objects(module: str, source: Any) -> list[Any] | None:
    profile = get_profile(module)
    if profile is None:
        return None
    return profile.build_requirement_objects(module=module, source=source)
