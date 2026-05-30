"""AI-powered semantic enrichment — Agent-driven, not API-driven.

This module does NOT make its own API calls.  The FC requirement workbench
skill is invoked by an AI agent that already has reasoning capacity.  Instead
of duplicating that capacity with a separate API key + HTTP call, this module
provides a two-phase protocol:

  Phase 1 ─ build_prompts(features, datasheet_text)
            → returns a list of structured enrichment tasks the agent should
              answer.  Each task has an id, a compact prompt, an input payload,
              and an expected output schema.

  Phase 2 ─ apply_results(features, task_results)
            → patches the agent's answers back into the feature records so
              downstream pipeline stages see enriched data transparently.

The agent (Claude Code or any orchestrator) sits between the two phases and
uses its own reasoning to answer the prompts.  No separate API key, model
selection, or HTTP plumbing is needed inside the pipeline.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Enrichment task definition (Phase 1 output / Phase 2 input)
# ---------------------------------------------------------------------------

@dataclass
class EnrichmentTask:
    """One unit of work for the AI agent."""
    task_id: str
    task_type: str          # "chip_classify" | "fault_enrich" | "mode_normalize"
    instruction: str        # what the agent should do
    input_data: Any         # structured data the agent needs
    output_schema: dict[str, str]  # JSON schema the agent must conform to


# ---------------------------------------------------------------------------
# Phase 2 result types (what the agent returns per task)
# ---------------------------------------------------------------------------

@dataclass
class ChipClassifyResult:
    chip_type: str = ""       # "CAN transceiver" | "motor driver" | "SBC" | ...
    bus_type: str = ""        # "pin-control" | "SPI" | "I2C" | ...
    key_behaviors: list[str] = field(default_factory=list)
    confidence: str = "medium"


@dataclass
class FaultEnrichResult:
    """One enriched fault row returned by the agent."""
    name: str
    trigger: str = ""
    detection: str = ""
    chip_behavior: str = ""
    recovery: str = ""
    software_action: str = ""


@dataclass
class ModeNormalizeResult:
    modes: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Main enricher
# ---------------------------------------------------------------------------

def _safe_setattr(obj: Any, attr: str, value: Any) -> bool:
    """Set attribute on (possibly frozen) dataclass, returning success."""
    try:
        object.__setattr__(obj, attr, value)
        return True
    except (TypeError, AttributeError):
        return False


class AiEnricher:
    """Build enrichment prompts for the agent; apply agent answers to features."""

    # ------------------------------------------------------------------
    # Phase 1 — build prompts
    # ------------------------------------------------------------------

    @staticmethod
    def build_prompts(
        features: list[Any],
        datasheet_text: str,
    ) -> list[EnrichmentTask]:
        """Analyse features and return tasks the agent should answer.

        The returned list may be empty if feature quality is already sufficient
        and no enrichment is needed.
        """
        tasks: list[EnrichmentTask] = []

        # 1. Chip classification — always useful for downstream stages
        chip_task = AiEnricher._build_chip_classify_task(features, datasheet_text)
        if chip_task:
            tasks.append(chip_task)

        # 2. Fault row enrichment — when diagnostic features have shallow data
        fault_task = AiEnricher._build_fault_enrich_task(features, datasheet_text)
        if fault_task:
            tasks.append(fault_task)

        # 3. Mode normalisation — when state names are noisy / duplicated
        mode_task = AiEnricher._build_mode_normalize_task(features, datasheet_text)
        if mode_task:
            tasks.append(mode_task)

        return tasks

    # ------------------------------------------------------------------
    # Phase 2 — apply agent results
    # ------------------------------------------------------------------

    @staticmethod
    def apply_results(
        features: list[Any],
        task_results: dict[str, Any],
    ) -> dict[str, Any]:
        """Patch agent-answered enrichment data back into feature records.

        ``task_results`` is a dict mapping ``task_id`` → parsed result object
        (ChipClassifyResult / list[FaultEnrichResult] / ModeNormalizeResult).

        Returns a summary dict for logging.
        """
        summary: dict[str, Any] = {}

        # --- Fault rows ---
        fault_results: list[FaultEnrichResult] = []
        for v in task_results.values():
            if isinstance(v, list) and v and isinstance(v[0], FaultEnrichResult):
                fault_results = v
                break

        if fault_results:
            summary["fault_rows_patched"] = AiEnricher._patch_fault_rows(
                features, fault_results
            )

        # --- Mode normalisation ---
        for v in task_results.values():
            if isinstance(v, ModeNormalizeResult) and v.modes:
                summary["modes_normalized"] = AiEnricher._patch_modes(features, v)
                break

        # --- Chip classification ---
        for v in task_results.values():
            if isinstance(v, ChipClassifyResult) and v.chip_type:
                summary["chip_classified"] = AiEnricher._patch_chip_class(features, v)
                break

        return summary

    # ==================================================================
    # Task builders (private)
    # ==================================================================

    @staticmethod
    def _build_chip_classify_task(
        features: list[Any], text: str
    ) -> EnrichmentTask | None:
        overview = text[:3500]
        # Collect pin names for context
        pins = [
            f.name for f in features
            if getattr(f, "type", "") == "pin"
        ][:20]
        return EnrichmentTask(
            task_id="chip_classify",
            task_type="chip_classify",
            instruction=(
                "Based on the datasheet excerpt and pin list, classify this chip. "
                "Return JSON with: chip_type (one of: CAN transceiver, motor driver, "
                "SBC/system basis chip, GPIO expander, ADC, other), bus_type (one of: "
                "pin-control, SPI, I2C, SPI+I2C, other), key_behaviors (3-5 Chinese "
                "phrases describing what the driver must do), confidence (high/medium/low)."
            ),
            input_data={
                "excerpt": overview,
                "pins": pins,
            },
            output_schema={
                "chip_type": "string",
                "bus_type": "string",
                "key_behaviors": ["string"],
                "confidence": "string",
            },
        )

    @staticmethod
    def _build_fault_enrich_task(
        features: list[Any], text: str
    ) -> EnrichmentTask | None:
        # Collect raw fault rows from diagnostic features
        raw_faults: list[dict[str, str]] = []
        seen: set[str] = set()
        for f in features:
            for sf in getattr(f, "subfunctions", []):
                for fr in getattr(sf, "fault_rows", []):
                    parts = fr.split("|")
                    if len(parts) >= 4:
                        name = re.sub(r"<br\s*/?>", " ", parts[1].strip(), flags=re.I)
                        name = re.sub(r"<[^>]+>", "", name).strip()
                        if name and name.lower() not in seen and name.strip("-=_") != "":
                            seen.add(name.lower())
                            # parts layout: | name | class | trigger | detect | confirm | behavior | recovery | action |
                            raw_faults.append({
                                "name": name,
                                "current_trigger": parts[3].strip() if len(parts) > 3 else "",
                                "current_detection": parts[4].strip() if len(parts) > 4 else "",
                                "current_behavior": parts[6].strip() if len(parts) > 6 else "",
                                "current_recovery": parts[7].strip() if len(parts) > 7 else "",
                            })

        if not raw_faults:
            return None

        return EnrichmentTask(
            task_id="fault_enrich",
            task_type="fault_enrich",
            instruction=(
                "For each fault/flag/status entry below, read the datasheet excerpt "
                "and fill in missing or incorrect fields.  The 'current_trigger' and "
                "'current_recovery' may be wrong (e.g. showing ERR_N pin availability "
                "instead of the real trigger condition).  Use the datasheet to correct "
                "them.  All free-text fields should be in Chinese except the fault name. "
                "Return a JSON array of objects, one per fault."
            ),
            input_data={
                "excerpt": text[:4500],
                "faults": raw_faults,
            },
            output_schema={
                "name": "string (fault name exactly as given)",
                "trigger": "string (Chinese — what condition sets this)",
                "detection": "string (Chinese — how software detects it)",
                "chip_behavior": "string (Chinese — what the chip does)",
                "recovery": "string (Chinese — how it's cleared: auto / enter Normal mode / write register / reset)",
                "software_action": "string (Chinese — 1 sentence: what the driver should do)",
            },
        )

    @staticmethod
    def _build_mode_normalize_task(
        features: list[Any], text: str
    ) -> EnrichmentTask | None:
        raw_modes: set[str] = set()
        for f in features:
            if getattr(f, "type", "") == "state_machine":
                raw_modes.add(f.name.strip())

        if len(raw_modes) <= 1:
            return None

        return EnrichmentTask(
            task_id="mode_normalize",
            task_type="mode_normalize",
            instruction=(
                "These mode/state names were extracted from a chip datasheet by regex. "
                "Some may be duplicates or false positives (not real device modes). "
                "Normalise them: merge case-insensitive duplicates, remove false positives "
                "(like 'Reset', 'Active', 'POR'), and output clean title-case names. "
                "Return JSON with 'modes' (clean list) and 'removed' (dropped items)."
            ),
            input_data={
                "raw_modes": sorted(raw_modes),
                "excerpt": text[:2000],
            },
            output_schema={
                "modes": ["string"],
                "removed": ["string"],
            },
        )

    # ==================================================================
    # Feature patching helpers (private)
    # ==================================================================

    @staticmethod
    def _patch_fault_rows(
        features: list[Any], enriched: list[FaultEnrichResult]
    ) -> int:
        fault_map = {ef.name.lower(): ef for ef in enriched if ef.name}
        patched = 0
        for f in features:
            if getattr(f, "type", "") != "feature_group":
                continue
            for sf in getattr(f, "subfunctions", []):
                if not getattr(sf, "fault_rows", []):
                    continue
                new_rows: list[str] = []
                for fr in sf.fault_rows:
                    parts = fr.split("|")
                    if len(parts) < 3:
                        new_rows.append(fr)
                        continue
                    # Normalise: replace <br> with space, strip other HTML tags
                    fname = re.sub(r"<br\s*/?>", " ", parts[1].strip(), flags=re.I)
                    fname = re.sub(r"<[^>]+>", "", fname).strip().lower()
                    ai_row = fault_map.get(fname)
                    if ai_row is None:
                        new_rows.append(fr)
                        continue
                    trigger = ai_row.trigger or (parts[2].strip() if len(parts) > 2 else "")
                    detection = ai_row.detection or (parts[4].strip() if len(parts) > 4 else "")
                    behavior = ai_row.chip_behavior or (parts[6].strip() if len(parts) > 6 else "")
                    recovery = ai_row.recovery or (parts[7].strip() if len(parts) > 7 else "")
                    sw_action = ai_row.software_action or (parts[8].strip() if len(parts) > 8 else "")
                    new_rows.append(
                        f"| {ai_row.name or parts[1].strip()} | hardware_chip "
                        f"| {trigger} | {detection or 'MainFunction 中检测对应状态'} "
                        f"| 连续 2 次 MainFunction 周期确认 "
                        f"| {behavior or '详见数据手册'} "
                        f"| {recovery or 'manual_clear'} "
                        f"| {sw_action or '记录故障事件'} |"
                    )
                    patched += 1
                if new_rows:
                    sf.fault_rows[:] = new_rows
        return patched

    @staticmethod
    def _patch_modes(
        features: list[Any], normalized: ModeNormalizeResult
    ) -> int:
        patched = 0
        for f in features:
            if getattr(f, "type", "") != "state_machine":
                continue
            raw_lower = f.name.strip().lower().rstrip(" mode")
            for cm in normalized.modes:
                if cm.lower().rstrip(" mode") == raw_lower:
                    if _safe_setattr(f, "name", cm):
                        patched += 1
                    break
        return patched

    @staticmethod
    def _patch_chip_class(
        features: list[Any], chip: ChipClassifyResult
    ) -> bool:
        for f in features:
            if getattr(f, "type", "") == "identity":
                extra = (
                    f" | AI: {chip.chip_type}, "
                    f"bus={chip.bus_type}, "
                    f"behaviors={'; '.join(chip.key_behaviors[:5])}"
                )
                return _safe_setattr(f, "content", f.content + extra)
        return False


# ---------------------------------------------------------------------------
# Agent helper — parse a result dict into typed objects
# ---------------------------------------------------------------------------

def parse_task_result(task_id: str, raw: Any) -> Any:
    """Convert a raw agent answer (dict or JSON string) into a typed result.

    Usage from the agent side::

        result = parse_task_result(task.task_id, agent_response_json)
        task_results[task_id] = result
    """
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return None

    if task_id == "chip_classify" and isinstance(raw, dict):
        return ChipClassifyResult(
            chip_type=raw.get("chip_type", ""),
            bus_type=raw.get("bus_type", ""),
            key_behaviors=raw.get("key_behaviors", []),
            confidence=raw.get("confidence", "medium"),
        )

    if task_id == "fault_enrich" and isinstance(raw, list):
        return [
            FaultEnrichResult(
                name=item.get("name", ""),
                trigger=item.get("trigger", ""),
                detection=item.get("detection", ""),
                chip_behavior=item.get("chip_behavior", ""),
                recovery=item.get("recovery", ""),
                software_action=item.get("software_action", ""),
            )
            for item in raw
            if isinstance(item, dict) and item.get("name")
        ]

    if task_id == "mode_normalize" and isinstance(raw, dict):
        return ModeNormalizeResult(
            modes=raw.get("modes", []),
            removed=raw.get("removed", []),
        )

    return None
