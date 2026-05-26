"""Cache helpers for the requirement workbench pipeline."""

from __future__ import annotations

import hashlib
from pathlib import Path
import pickle
from typing import Any, Callable


def cache_key(input_path: Path, module: str, stage: str, dependency_fingerprint: str) -> str:
    stat = input_path.stat()
    raw = (
        f"{input_path.resolve()}::{module}::{stage}::{stat.st_mtime_ns}::{stat.st_size}"
        f"::{dependency_fingerprint}"
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def dependency_fingerprint(anchor_file: str) -> str:
    package_root = Path(anchor_file).resolve().parents[2]
    tracked_paths = [
        package_root / "pyproject.toml",
        package_root / "references",
        package_root / "src" / "fc_requirement_workbench",
    ]
    records: list[str] = []
    for path in tracked_paths:
        if not path.exists():
            continue
        if path.is_file():
            stat = path.stat()
            records.append(f"{path.resolve()}::{stat.st_mtime_ns}::{stat.st_size}")
            continue
        for child in sorted(
            file for file in path.rglob("*")
            if file.is_file() and file.suffix in {".py", ".md", ".yaml", ".yml", ".toml"}
        ):
            stat = child.stat()
            records.append(f"{child.resolve()}::{stat.st_mtime_ns}::{stat.st_size}")
    return hashlib.sha256("\n".join(records).encode("utf-8")).hexdigest()[:24]


def cached_stage(
    cache_dir: Path,
    stage: str,
    key: str,
    producer: Callable[[], Any],
    *,
    enabled: bool,
) -> Any:
    if not enabled:
        return producer()
    stage_dir = cache_dir / stage
    stage_dir.mkdir(parents=True, exist_ok=True)
    cache_file = stage_dir / f"{key}.pkl"
    if cache_file.exists():
        with cache_file.open("rb") as handle:
            return pickle.load(handle)
    value = producer()
    with cache_file.open("wb") as handle:
        pickle.dump(value, handle)
    return value
