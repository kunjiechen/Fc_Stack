from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


def _slug_module(module_name: str) -> str:
    return module_name.replace("-", "_").strip()


def _module_family(module_name: str, layer: str) -> str:
    lowered_module = module_name.lower()
    lowered_layer = (layer or "").lower()
    if "bswsys" in lowered_module or "bswsys" in lowered_layer or "wkupsrcp" in lowered_module:
        return "BswSys_Gp"
    if "iomcu" in lowered_module or "iomcu" in lowered_layer:
        return "IoMcu"
    if lowered_module.startswith("gp_06_") or "cdd" in lowered_layer:
        return "Cdd"
    if "ioext" in lowered_module or "ioext" in lowered_layer:
        return "IoExt"
    return layer or "Unknown"


def _external_api_name(item: dict[str, Any]) -> str:
    return item.get("function_name") or item.get("name") or "UnknownExternalApi"


def _first_sentence(text: str) -> str:
    if not text:
        return ""
    for sep in ("。", ". ", "; ", "；"):
        if sep in text:
            return text.split(sep)[0].strip().rstrip(".")
    return text.strip()


def _config_macro_name(module_name: str, display_name: str, requirement_id: str = "") -> str:
    prefix = _slug_module(module_name).upper()
    normalized = (
        display_name.replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
        .replace("（", "_")
        .replace("）", "_")
        .replace("(", "_")
        .replace(")", "_")
    )
    normalized = "".join(ch if ((ch.isascii() and ch.isalnum()) or ch == "_") else "_" for ch in normalized).strip("_")
    if not normalized or not normalized.isascii():
        tail = requirement_id.split("-")[-1] if requirement_id else "ITEM"
        normalized = f"ITEM_{tail.upper()}"
    return f"{prefix}_CFG_{normalized.upper()}"


def _external_api_object(module_name: str, item: dict[str, Any]) -> dict[str, Any]:
    name = _external_api_name(item)
    purpose = item.get("purpose", "")
    status = "Formal" if item.get("status") == "ready" else "Pending Confirmation"
    if name.endswith("Init"):
        prototype = f"void {name}(void)"
        sync_mode = "Synchronous"
        reentrancy = "Non-reentrant"
        return_value = "void"
        constraints = ["Must be called after configuration and dependency initialization."]
    elif name.endswith("MainFunction"):
        prototype = f"void {name}(void)"
        sync_mode = "Synchronous"
        reentrancy = "Non-reentrant"
        return_value = "void"
        constraints = ["Must be called periodically by project scheduling."]
    elif name.startswith(f"{module_name}_Get") and "Fault" in name:
        prototype = f"Std_ReturnType {name}(uint16 Id_u16, uint32* Fault_pu32)"
        sync_mode = "Synchronous"
        reentrancy = "Reentrant"
        return_value = "E_OK / E_NOT_OK"
        constraints = ["Id_u16 must reference a configured object.", "Fault_pu32 must be non-null."]
    elif name.startswith(f"{module_name}_Get"):
        prototype = f"Std_ReturnType {name}(uint16 Id_u16, uint8* Value_pu8)"
        sync_mode = "Synchronous"
        reentrancy = "Reentrant"
        return_value = "E_OK / E_NOT_OK"
        constraints = ["Id_u16 must reference a configured object.", "Output pointer must be non-null."]
    elif name.startswith(f"{module_name}_Set"):
        prototype = f"Std_ReturnType {name}(uint16 Id_u16, uint8 Value_u8)"
        sync_mode = "Synchronous"
        reentrancy = "Reentrant"
        return_value = "E_OK / E_NOT_OK"
        constraints = ["Id_u16 must reference a configured object.", "Input value must satisfy architecture constraints."]
    else:
        prototype = f"Std_ReturnType {name}(void)"
        sync_mode = "Synchronous"
        reentrancy = "Non-reentrant"
        return_value = "E_OK / E_NOT_OK"
        constraints = ["Detailed parameter contract requires architecture review confirmation."]
    return {
        "name": name,
        "prototype": prototype,
        "description": _first_sentence(purpose) or f"{name} frozen from architecture seed.",
        "sync_mode": sync_mode,
        "reentrancy": reentrancy,
        "return_value": return_value,
        "constraints": constraints,
        "evidence": [item.get("requirement_id", "UNKNOWN")],
        "status": status,
        "freeze_status": "formal" if item.get("status") == "ready" else "pending_confirm",
        "decision": "freeze interface",
        "decision_reason": "Architecture seed marks this as an external API candidate.",
    }


def _config_macro_type(display_name: str) -> str:
    lowered = display_name.lower()
    if "det" in lowered or "错误" in display_name:
        return "Development Error Detect"
    if "映射" in display_name or "mapping" in lowered or "signal id" in lowered or "id " in lowered:
        return "Signal Mapping"
    if "策略" in display_name or "strategy" in lowered or "scheme" in lowered or "judge" in lowered or "fill" in lowered:
        return "Strategy Selection"
    if "依赖" in display_name or "dependency" in lowered or "dep_if" in lowered or "binding" in lowered:
        return "Dependency Selection"
    if "端口" in display_name or "port" in lowered or "pin" in lowered or "channel" in lowered or "hardware" in lowered:
        return "Hardware Mapping"
    if "数量" in display_name or "实例" in display_name or "count" in lowered or "num" in lowered:
        return "Count Size"
    if "速率" in display_name or "超时" in display_name or "时间" in display_name or "延时" in display_name or "阈值" in display_name or "delay" in lowered or "retry" in lowered or "threshold" in lowered:
        return "Timing Threshold"
    if "使能" in display_name or "enable" in lowered:
        return "Feature Enable"
    return "Behavior Selection"


def _config_macro_object(module_name: str, item: dict[str, Any]) -> dict[str, Any]:
    macro_name = _config_macro_name(module_name, item.get("name", "CONFIG_ITEM"), item.get("requirement_id", ""))
    return {
        "name": macro_name,
        "purpose": item.get("name", "Configuration item"),
        "macro_type": _config_macro_type(item.get("name", "")),
        "taxonomy_reason": f"Classified from config item wording: {item.get('name', 'Configuration item')}",
        "default_value": "TBD",
        "usage_location": f"{module_name}_Cfg.h",
        "evidence": [item.get("requirement_id", "UNKNOWN")],
        "status": "Formal" if item.get("status") == "ready" else "Pending Confirmation",
        "freeze_status": "formal" if item.get("status") == "ready" else "pending_confirm",
        "decision": "freeze config boundary",
        "decision_reason": item.get("constraint", "Configuration concern from architecture seed."),
    }


def _det_config_macro_object(module_name: str) -> dict[str, Any]:
    upper = _slug_module(module_name).upper()
    return {
        "name": f"{upper}_CFG_DEV_ERROR_DETECT",
        "purpose": "Development error detect switch for public API validation paths.",
        "macro_type": "Development Error Detect",
        "taxonomy_reason": "Live FC pattern uses DET as a dedicated diagnostic macro class.",
        "default_value": "STD_ON",
        "usage_location": f"{module_name}_Cfg.h",
        "evidence": ["source-grounding-aurix2g-live-baseline.md"],
        "status": "Formal",
        "freeze_status": "formal",
        "decision": "freeze DET control macro",
        "decision_reason": "Live AURIX2G FCs commonly expose DET as a Cfg.h macro and may pair it with runtime bookkeeping.",
    }


def _risk_item(index: int, title: str, risk: str) -> dict[str, Any]:
    gate_level, impact_scope, close_condition = _pending_gate_profile("", title)
    return {
        "index": f"R{index}",
        "title": title,
        "risk": risk,
        "impact": "Architecture assumptions may drift if implementation treats this as confirmed.",
        "recommended_action": "Keep item explicit and confirm during architecture review.",
        "gate_level": gate_level,
        "impact_scope": impact_scope,
        "close_condition": close_condition,
        "source_requirement_id": "",
        "remark": "",
        "status": "待评审",
        "freeze_status": "pending_confirm",
    }


def _pending_gate_profile(requirement_id: str, title: str) -> tuple[str, str, str]:
    lowered_title = (title or "").lower()
    req = requirement_id or ""
    if req.endswith("SAFE-0001") or "安全" in title:
        return (
            "release_blocker",
            "safety_compliance",
            "安全等级、诊断或安全约束需完成明确化并经架构评审确认。",
        )
    if req.endswith("CODE-0001") or "编码规范" in title:
        return (
            "release_blocker",
            "project_compliance",
            "编码规范落实方式、边界与约束需完成架构级确认。",
        )
    if req.endswith("RES-0001") or "资源" in title:
        return (
            "incremental_followup",
            "nonfunctional_budget",
            "资源预算和度量记录可在实现深化阶段补齐，但需保留显式跟踪。",
        )
    if any(token in lowered_title for token in ("初始化", "异常", "诊断", "中断", "时序")):
        return (
            "release_blocker",
            "core_behavior",
            "核心行为、异常或时序边界需在架构发布前完成确认。",
        )
    if any(token in lowered_title for token in ("配置", "状态", "i2c", "gpio", "读取", "写入")):
        return (
            "implementation_blocker",
            "implementation_behavior",
            "实现相关行为边界需在详细设计展开前完成确认。",
        )
    return (
        "implementation_blocker",
        "architecture_followup",
        "该项需在实现展开前完成进一步架构确认。",
    )


def _reserved_gate_profile(title: str, description: str) -> tuple[str, str, str]:
    lowered = f"{title} {description}".lower()
    if any(token in lowered for token in ("安全", "safety", "诊断", "diagnostic", "中断", "interrupt")):
        return (
            "release_blocker",
            "core_behavior",
            "该保留能力涉及核心行为或诊断机制，需在 released 架构前收敛为正式对象或明确约束。",
        )
    if any(token in lowered for token in ("i2c", "配置", "config", "采样", "修正", "判定", "trigger", "访问")):
        return (
            "implementation_blocker",
            "implementation_behavior",
            "该保留能力会直接影响实现展开，需在详细设计前收敛为正式对象或明确边界。",
        )
    return (
        "incremental_followup",
        "architecture_followup",
        "该保留能力可继续保留跟踪，但需避免在实现中被隐式落地。",
    )


def _calibration_items(module_name: str, family: str, seed: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if family == "Cdd":
        items.extend(
            [
                {
                    "name": f"{module_name}_SampleValidityThreshold",
                    "type": "uint32",
                    "initial_value": "TBD",
                    "description": "Calibration threshold set used when the sampling-validity strategy requires calibrated boundary values.",
                    "status": "Conditional",
                    "freeze_status": "conditional",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                },
                {
                    "name": f"{module_name}_InvalidFillBehavior",
                    "type": "enum",
                    "initial_value": "TBD",
                    "description": "Calibration-controlled invalid-fill behavior used when invalid samples need project-tuned fallback handling.",
                    "status": "Conditional",
                    "freeze_status": "conditional",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                },
            ]
        )
    elif family == "BswSys_Gp":
        items.extend(
            [
                {
                    "name": f"{module_name}_GearLimitThreshold",
                    "type": "uint32 range table",
                    "initial_value": "TBD",
                    "description": "Calibration thresholds for wakeup-source gear-limit evaluation and derived status judgment.",
                    "status": "Formal",
                    "freeze_status": "formal",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                },
                {
                    "name": f"{module_name}_ReviseParameterSet",
                    "type": "uint32 table",
                    "initial_value": "TBD",
                    "description": "Calibration parameter set used by wakeup-source revise logic before final status evaluation.",
                    "status": "Conditional",
                    "freeze_status": "conditional",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                },
            ]
        )
    return items


def _strategy_items(module_name: str, family: str) -> list[dict[str, Any]]:
    if family == "Cdd":
        return [
            {
                "name": f"{module_name}_SampleStrategy",
                "strategy_type": "Sampling Scheme",
                "selection_scope": "Module-level compile-time strategy",
                "backing_reference": f"{_slug_module(module_name).upper()}_CFG_SAMPLE_STRATEGY",
                "description": "Defines which ADC sampling scheme the module uses for raw signal acquisition.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
            {
                "name": f"{module_name}_ValidityJudgeStrategy",
                "strategy_type": "Validity Judge",
                "selection_scope": "Module-level compile-time strategy",
                "backing_reference": f"{_slug_module(module_name).upper()}_CFG_VALIDITY_JUDGE",
                "description": "Defines how sampled data validity is judged before the module exposes raw values.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
            {
                "name": f"{module_name}_InvalidFillStrategy",
                "strategy_type": "Invalid Fill",
                "selection_scope": "Module-level compile-time strategy",
                "backing_reference": f"{_slug_module(module_name).upper()}_CFG_INVALID_FILL",
                "description": "Defines how invalid samples are filled or retained when validity judgment rejects raw data.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
        ]
    if family == "BswSys_Gp":
        return [
            {
                "name": f"{module_name}_WakeParserStrategy",
                "strategy_type": "Wake Parser",
                "selection_scope": "Per-signal configuration strategy",
                "backing_reference": f"{module_name}_CfgType.WkSrcParser_b",
                "description": "Defines whether wakeup-source inputs require parser handling before wake-type and status judgment.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
            {
                "name": f"{module_name}_WakeReviseStrategy",
                "strategy_type": "Wake Revise",
                "selection_scope": "Per-signal configuration strategy with callout adaptation",
                "backing_reference": f"{module_name}_CfgType.WkSrcRevise_b / {module_name}_CalloutWkSrcDataRevise",
                "description": "Defines whether wakeup-source inputs require revise processing before final status evaluation.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
            {
                "name": f"{module_name}_WakeJudgeStrategy",
                "strategy_type": "Wake Judge",
                "selection_scope": "Per-signal wake-type-specific strategy",
                "backing_reference": f"{module_name}_CfgType.WkSrcType_u8 / internal WkSrcJudge_* family",
                "description": "Defines which wakeup-status judge path is selected for AI/DI and special wakeup-source types.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
        ]
    return []


def _binding_items(module_name: str, family: str, seed: dict[str, Any]) -> list[dict[str, Any]]:
    if family == "IoExt":
        items = [
            {
                "name": f"{module_name}_CoreSelectionBinding",
                "binding_type": "Core Selection",
                "source_side": f"{module_name}.c runtime ownership",
                "target_side": f"{module_name}_CalloutGetCoreId",
                "binding_mechanism": "Callout",
                "description": "Binds module runtime/config selection to the current-core query boundary.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
            {
                "name": f"{module_name}_DeviceRegisterAccessBinding",
                "binding_type": "Device Register Access",
                "source_side": f"{module_name} external API and internal register access paths",
                "target_side": f"{module_name}_CalloutI2cRead / {module_name}_CalloutI2cWrite",
                "binding_mechanism": "Callout",
                "description": "Binds register read/write behavior to project adaptation instead of direct platform access.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
        ]
        if _needs_mainfunction(seed):
            items.append(
                {
                    "name": f"{module_name}_StatusSamplingBinding",
                    "binding_type": "Status Sampling",
                    "source_side": f"{module_name}_MainFunction periodic handling",
                    "target_side": f"{module_name}_CalloutReadDio",
                    "binding_mechanism": "Callout",
                    "description": "Binds periodic interrupt/status sampling to adaptation-side DIO access.",
                    "status": "Formal",
                    "freeze_status": "formal",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                }
            )
        return items
    if family == "IoMcu":
        return [
            {
                "name": f"{module_name}_CoreSelectionBinding",
                "binding_type": "Core Selection",
                "source_side": f"{module_name}.c synchronous signal routing",
                "target_side": f"{module_name}_CalloutGetCoreId",
                "binding_mechanism": "Callout",
                "description": "Binds signal routing and per-core ownership to the current-core query boundary.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
            {
                "name": f"{module_name}_DependencySelectionBinding",
                "binding_type": "Dependency Selection",
                "source_side": f"{module_name}_Cfg.h compile-time dependency selection",
                "target_side": f"{_slug_module(module_name).upper()}_SPEC_DEP_IF",
                "binding_mechanism": "Config Macro",
                "description": "Binds the module to one selected MCU/DIO dependency implementation path.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
            {
                "name": f"{module_name}_DioAccessBinding",
                "binding_type": "DIO Access",
                "source_side": f"{module_name} direction/read/write APIs",
                "target_side": f"{module_name}_CalloutInit / {module_name}_CalloutSetDioSigDir / {module_name}_CalloutGetDioSigLvlIn / {module_name}_CalloutSetDioSigLvlOut",
                "binding_mechanism": "Callout",
                "description": "Binds synchronous DIO signal operations to project-selected low-level dependency access.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
        ]
    if family == "Cdd":
        return [
            {
                "name": f"{module_name}_CoreSelectionBinding",
                "binding_type": "Core Selection",
                "source_side": f"{module_name}.c conversion/runtime ownership",
                "target_side": f"{module_name}_CalloutGetCoreId",
                "binding_mechanism": "Callout",
                "description": "Binds conversion buffers and configuration ownership to the current-core selection boundary.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
            {
                "name": f"{module_name}_SamplingDelayBinding",
                "binding_type": "Sampling Delay",
                "source_side": "Sampling control logic",
                "target_side": f"{module_name}_CalloutDelayUs",
                "binding_mechanism": "Callout",
                "description": "Binds ADC timing-sensitive delay behavior to adaptation-side delay service.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
            {
                "name": f"{module_name}_TriggerControlBinding",
                "binding_type": "Trigger Control",
                "source_side": "ADC group trigger control logic",
                "target_side": f"{module_name}_CalloutTrigEnable",
                "binding_mechanism": "Callout",
                "description": "Binds trigger enable behavior to the selected project-specific trigger implementation.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
        ]
    if family == "BswSys_Gp":
        return [
            {
                "name": f"{module_name}_WakeSourceDependencyBinding",
                "binding_type": "Wake Source Access",
                "source_side": f"{module_name}_CfgType dependency function pointers",
                "target_side": "DepGetWkUpStsU8 / DepGetWkUpStsU16 / DepGetWkUpStsU32 / DepGetWkUpStsB",
                "binding_mechanism": "Config-bound function pointer",
                "description": "Binds wakeup-source status acquisition to configured dependency providers instead of a fixed module implementation.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
            {
                "name": f"{module_name}_WakeReviseBinding",
                "binding_type": "Wake Revise",
                "source_side": f"{module_name}_CfgType.WkSrcRevise_b",
                "target_side": f"{module_name}_CalloutWkSrcDataRevise",
                "binding_mechanism": "Config-gated callout",
                "description": "Binds wakeup-source revise policy to a callout adaptation boundary under configuration control.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
        ]
    return []


def _needs_mainfunction(seed: dict[str, Any]) -> bool:
    for item in seed.get("external_interface_candidates", []):
        if _external_api_name(item).endswith("MainFunction"):
            return True
    return False


def _dependency_apis(module_name: str, family: str, seed: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if family == "IoExt":
        items.extend(
            [
                {
                    "name": f"{module_name}_CalloutGetCoreId",
                    "prototype": f"uint32 {module_name}_CalloutGetCoreId(void)",
                    "description": "Returns the current core ID used to select per-core configuration and runtime objects.",
                    "implemented_by": "Project Adaptation / Platform",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "sync_mode": "Synchronous",
                    "reentrancy": "Reentrant",
                    "return_value": "Current core ID",
                    "constraints": ["Returned core ID must be valid for configured cores."],
                    "call_scenario": "Per-core object selection",
                },
                {
                    "name": f"{module_name}_CalloutI2cRead",
                    "prototype": f"Std_ReturnType {module_name}_CalloutI2cRead(uint8 Addr_u8, uint8 Reg_u8, uint8* Data_pu8, uint16 Size_u16)",
                    "description": "Reads register data from the external device through project adaptation.",
                    "implemented_by": "Project Adaptation / IoExtDev",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "sync_mode": "Synchronous",
                    "reentrancy": "Reentrant",
                    "return_value": "E_OK / E_NOT_OK",
                    "constraints": ["Output pointer must be non-null.", "Address/register arguments must be valid."],
                    "call_scenario": "External device register read",
                },
                {
                    "name": f"{module_name}_CalloutI2cWrite",
                    "prototype": f"Std_ReturnType {module_name}_CalloutI2cWrite(uint8 Addr_u8, uint8 Reg_u8, const uint8* Data_pcu8, uint16 Size_u16)",
                    "description": "Writes register data to the external device through project adaptation.",
                    "implemented_by": "Project Adaptation / IoExtDev",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "sync_mode": "Synchronous",
                    "reentrancy": "Reentrant",
                    "return_value": "E_OK / E_NOT_OK",
                    "constraints": ["Input pointer must be non-null when size is non-zero."],
                    "call_scenario": "External device register write",
                },
            ]
        )
        if _needs_mainfunction(seed):
            items.append(
                {
                    "name": f"{module_name}_CalloutReadDio",
                    "prototype": f"Std_ReturnType {module_name}_CalloutReadDio(uint16 Id_u16, uint8* State_pu8)",
                    "description": "Reads adaptation-side interrupt or status pin state for periodic handling.",
                    "implemented_by": "IoMcu / Project Adaptation",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "sync_mode": "Synchronous",
                    "reentrancy": "Reentrant",
                    "return_value": "E_OK / E_NOT_OK",
                    "constraints": ["State pointer must be non-null.", "Id must map to a configured object."],
                    "call_scenario": "Periodic status or interrupt sampling",
                }
            )
    elif family == "IoMcu":
        items.extend(
            [
                {
                    "name": f"{module_name}_CalloutGetCoreId",
                    "prototype": f"uint32 {module_name}_CalloutGetCoreId(void)",
                    "description": "Returns the current core ID used to select core-local DIO configuration and runtime objects.",
                    "implemented_by": "Project Adaptation / Platform",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "sync_mode": "Synchronous",
                    "reentrancy": "Reentrant",
                    "return_value": "Current core ID",
                    "constraints": ["Returned core ID must be valid for configured cores."],
                    "call_scenario": "Per-core signal mapping and runtime routing",
                },
                {
                    "name": f"{module_name}_CalloutInit",
                    "prototype": f"Std_ReturnType {module_name}_CalloutInit(void)",
                    "description": "Initializes the project-selected MCU/DIO dependency binding used by this module.",
                    "implemented_by": "Project Adaptation / IoMcu",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "sync_mode": "Synchronous",
                    "reentrancy": "Non-reentrant",
                    "return_value": "E_OK / E_NOT_OK",
                    "constraints": ["Must be called before DIO read/write dependency access."],
                    "call_scenario": "Dependency initialization",
                },
                {
                    "name": f"{module_name}_CalloutSetDioSigDir",
                    "prototype": f"Std_ReturnType {module_name}_CalloutSetDioSigDir(uint16 Id_u16, uint8 Dir_u8)",
                    "description": "Sets physical DIO direction through the project-selected low-level dependency.",
                    "implemented_by": "Project Adaptation / IoMcu",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "sync_mode": "Synchronous",
                    "reentrancy": "Reentrant",
                    "return_value": "E_OK / E_NOT_OK",
                    "constraints": ["Id_u16 must map to a configured DIO signal.", "Dir_u8 must be a supported direction value."],
                    "call_scenario": "Signal direction adaptation",
                },
                {
                    "name": f"{module_name}_CalloutGetDioSigLvlIn",
                    "prototype": f"Std_ReturnType {module_name}_CalloutGetDioSigLvlIn(uint16 Id_u16, uint8* Level_pu8)",
                    "description": "Reads physical DIO input level through the project-selected low-level dependency.",
                    "implemented_by": "Project Adaptation / IoMcu",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "sync_mode": "Synchronous",
                    "reentrancy": "Reentrant",
                    "return_value": "E_OK / E_NOT_OK",
                    "constraints": ["Id_u16 must map to a configured DIO signal.", "Level_pu8 must be non-null."],
                    "call_scenario": "Signal input read adaptation",
                },
                {
                    "name": f"{module_name}_CalloutSetDioSigLvlOut",
                    "prototype": f"Std_ReturnType {module_name}_CalloutSetDioSigLvlOut(uint16 Id_u16, uint8 Level_u8)",
                    "description": "Writes physical DIO output level through the project-selected low-level dependency.",
                    "implemented_by": "Project Adaptation / IoMcu",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "sync_mode": "Synchronous",
                    "reentrancy": "Reentrant",
                    "return_value": "E_OK / E_NOT_OK",
                    "constraints": ["Id_u16 must map to a configured DIO signal."],
                    "call_scenario": "Signal output write adaptation",
                },
            ]
        )
    elif family == "Cdd":
        items.extend(
            [
                {
                    "name": f"{module_name}_CalloutGetCoreId",
                    "prototype": f"uint32 {module_name}_CalloutGetCoreId(void)",
                    "description": "Returns the current core ID used to select core-local ADC runtime and configuration objects.",
                    "implemented_by": "Project Adaptation / Platform",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "sync_mode": "Synchronous",
                    "reentrancy": "Reentrant",
                    "return_value": "Current core ID",
                    "constraints": ["Returned core ID must be valid for configured cores."],
                    "call_scenario": "Per-core conversion and configuration routing",
                },
                {
                    "name": f"{module_name}_CalloutDelayUs",
                    "prototype": f"void {module_name}_CalloutDelayUs(uint16 Delay_u16)",
                    "description": "Provides the microsecond-level delay adaptation used by ADC sampling control paths.",
                    "implemented_by": "Project Adaptation / Cdd",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "sync_mode": "Synchronous",
                    "reentrancy": "Reentrant",
                    "return_value": "void",
                    "constraints": ["Delay_u16 must remain within architecture-approved timing bounds."],
                    "call_scenario": "Sampling timing adaptation",
                },
                {
                    "name": f"{module_name}_CalloutTrigEnable",
                    "prototype": f"Std_ReturnType {module_name}_CalloutTrigEnable(uint8 Group_u8, uint8 Enable_u8)",
                    "description": "Bridges trigger enable control to the project-selected ADC trigger implementation.",
                    "implemented_by": "Project Adaptation / Cdd",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "sync_mode": "Synchronous",
                    "reentrancy": "Reentrant",
                    "return_value": "E_OK / E_NOT_OK",
                    "constraints": ["Group_u8 must reference a configured ADC trigger group."],
                    "call_scenario": "Trigger path adaptation",
                },
            ]
        )
    elif family == "BswSys_Gp":
        items.extend(
            [
                {
                    "name": f"{module_name}_CalloutWkSrcDataRevise",
                    "prototype": f"void {module_name}_CalloutWkSrcDataRevise(uint16 WkId_u16, uint32* DataIn_pu32)",
                    "description": "Revises wakeup-source raw data through project-specific correction logic before status judgment.",
                    "implemented_by": "Project Adaptation / BswSys_Gp",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "sync_mode": "Synchronous",
                    "reentrancy": "Non-reentrant",
                    "return_value": "void",
                    "constraints": ["DataIn_pu32 must be non-null.", "Revision logic must preserve architecture-defined wake-source semantics."],
                    "call_scenario": "Wakeup-source preprocessing and data revise",
                }
            ]
        )
    return items


def _runtime_states(module_name: str, family: str, seed: dict[str, Any]) -> list[dict[str, Any]]:
    items = [
        {
            "name": "Per-core init state",
            "owner": f"{module_name}.c",
            "read_write_side": "Written by Init; read by public APIs.",
            "lifecycle": "Created after initialization and reset on re-init/fault recovery.",
            "memory_section": f"{module_name.upper()}_CLEAR_FAR_DATA_ALIGN4_COREx",
            "concurrency_strategy": "Per-core ownership with no cross-core sharing.",
            "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            "status": "Formal",
            "freeze_status": "formal",
        }
    ]
    if _needs_mainfunction(seed):
        items.append(
            {
                "name": "Per-core status/event cache",
                "owner": f"{module_name}.c",
                "read_write_side": "Written by MainFunction; read by getter or control APIs.",
                "lifecycle": "Updated during periodic handling and fault/state changes.",
                "memory_section": f"{module_name.upper()}_CLEAR_FAR_DATA_ALIGN4_COREx",
                "concurrency_strategy": "Per-core runtime buffer governed by current-core access.",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                "status": "Formal",
                "freeze_status": "formal",
            }
        )
    items.append(
        {
            "name": "Per-core fault/DET state",
            "owner": f"{module_name}.c",
            "read_write_side": "Written by validation and dependency-failure paths; read by diagnostic getters.",
            "lifecycle": "Updated whenever architecture-defined error paths are triggered.",
            "memory_section": f"{module_name.upper()}_CLEAR_FAR_DATA_ALIGN4_COREx",
            "concurrency_strategy": "Per-core ownership; no implicit cross-core merge.",
            "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            "status": "Formal",
            "freeze_status": "formal",
        }
    )
    if family == "IoMcu":
        items.insert(
            1,
            {
                "name": "Per-core DIO route cache",
                "owner": f"{module_name}.c",
                "read_write_side": "Written by Init or configuration reload; read by direction/read/write APIs.",
                "lifecycle": "Updated when configuration is loaded and reused by synchronous signal access APIs.",
                "memory_section": f"{module_name.upper()}_CLEAR_FAR_DATA_ALIGN4_COREx",
                "concurrency_strategy": "Per-core route ownership with no cross-core sharing.",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                "status": "Formal",
                "freeze_status": "formal",
            },
        )
    if family == "Cdd":
        items.insert(
            1,
            {
                "name": "Per-core ADC conversion cache",
                "owner": f"{module_name}.c",
                "read_write_side": "Written by init/trigger-driven acquisition paths; read by raw-signal getter APIs.",
                "lifecycle": "Updated when conversion results are captured and cleared on re-init.",
                "memory_section": f"{module_name.upper()}_CLEAR_FAR_DATA_ALIGN4_COREx",
                "concurrency_strategy": "Per-core result ownership with explicit core-local access.",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                "status": "Formal",
                "freeze_status": "formal",
            },
        )
    if family == "BswSys_Gp":
        items = [
            {
                "name": "Wakeup-source runtime cache",
                "owner": f"{module_name}.c",
                "read_write_side": "Written by Init and internal wake-source handling paths; read by GetWkUpSts.",
                "lifecycle": "Initialized during startup and updated when wake-source status is revised or judged.",
                "memory_section": f"{module_name.upper()}_CLEAR_FAR_DATA_ALIGN4_GLOBAL",
                "concurrency_strategy": "Global runtime ownership with architecture-controlled asynchronous updates.",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                "status": "Formal",
                "freeze_status": "formal",
            },
            {
                "name": "Wakeup gear/status derived cache",
                "owner": f"{module_name}.c",
                "read_write_side": "Written by wake-source pre/post handling and gear calculation logic; read by status APIs.",
                "lifecycle": "Updated when wakeup-source inputs are normalized and wake type is interpreted.",
                "memory_section": f"{module_name.upper()}_CLEAR_FAR_DATA_ALIGN4_GLOBAL",
                "concurrency_strategy": "Global runtime ownership with no per-core split by default.",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                "status": "Formal",
                "freeze_status": "formal",
            },
            {
                "name": "Wakeup DET/fault state",
                "owner": f"{module_name}.c",
                "read_write_side": "Written by parameter validation and dependency revise/error paths; read by diagnostic reporting paths.",
                "lifecycle": "Updated whenever DET-enabled validation or revise logic detects an invalid condition.",
                "memory_section": f"{module_name.upper()}_CLEAR_FAR_DATA_ALIGN4_GLOBAL",
                "concurrency_strategy": "Global runtime ownership.",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                "status": "Formal",
                "freeze_status": "formal",
            },
        ]
    return items


def _memmap_sections(module_name: str, family: str) -> list[dict[str, Any]]:
    upper = module_name.upper()
    items = [
        {
            "name": "CODE",
            "target_content": "External API implementation and internal helper code.",
            "start_macro": f"{upper}_CODE_START",
            "stop_macro": f"{upper}_CODE_STOP",
            "used_files": [f"{module_name}.c", f"{module_name}.h", f"{module_name}_Callout.c"],
            "notes": "Module-specific code section.",
            "status": "Formal",
            "freeze_status": "formal",
            "evidence": ["source-grounding-aurix2g-live-baseline.md"],
        },
        {
            "name": "CONST PER-CORE",
            "target_content": "Per-core configuration constants and mapping tables.",
            "start_macro": f"{upper}_CONST_FAR_DATA_ALIGN4_COREx_START",
            "stop_macro": f"{upper}_CONST_FAR_DATA_ALIGN4_COREx_STOP",
            "used_files": [f"{module_name}_Cfg.c", f"{module_name}_CfgData.h"],
            "notes": "Preferred when configuration ownership is core-local.",
            "status": "Formal",
            "freeze_status": "formal",
            "evidence": ["source-grounding-aurix2g-live-baseline.md"],
        },
        {
            "name": "RUNTIME RAM",
            "target_content": "Per-core runtime states, caches, and DET/fault bookkeeping.",
            "start_macro": f"{upper}_CLEAR_FAR_DATA_ALIGN4_COREx_START",
            "stop_macro": f"{upper}_CLEAR_FAR_DATA_ALIGN4_COREx_STOP",
            "used_files": [f"{module_name}.c"],
            "notes": "Per-core clear-data runtime section.",
            "status": "Formal",
            "freeze_status": "formal",
            "evidence": ["source-grounding-aurix2g-live-baseline.md"],
        },
        {
            "name": "CALIB",
            "target_content": "Optional calibration constants if project later confirms calibration objects.",
            "start_macro": f"{upper}_CONST_FAR_DATA_ALIGN4_CALI_COREx_START",
            "stop_macro": f"{upper}_CONST_FAR_DATA_ALIGN4_CALI_COREx_STOP",
            "used_files": [f"{module_name}_Cali.c"],
            "notes": "Reserved unless calibration is explicitly required.",
            "status": "Conditional",
            "freeze_status": "conditional",
            "evidence": ["source-grounding-aurix2g-live-baseline.md"],
        },
    ]
    if family == "Cdd":
        items.insert(
            1,
            {
                "name": "CODE RAM COPY",
                "target_content": "Latency-sensitive code copied to RAM for ADC trigger or acquisition control.",
                "start_macro": f"{upper}_CODE_RAM_COPY_START",
                "stop_macro": f"{upper}_CODE_RAM_COPY_STOP",
                "used_files": [f"{module_name}.c", f"{module_name}.h"],
                "notes": "Observed in live Cdd family and should stay explicit when required.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
        )
    if family == "BswSys_Gp":
        items = [
            {
                "name": "CODE",
                "target_content": "Wakeup-source external APIs and internal status-handling helpers.",
                "start_macro": f"{upper}_CODE_START",
                "stop_macro": f"{upper}_CODE_STOP",
                "used_files": [f"{module_name}.c", f"{module_name}.h", f"{module_name}_Callout.c"],
                "notes": "Module-specific code section.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
            {
                "name": "CONST GLOBAL",
                "target_content": "Wakeup-source configuration containers and mapping tables.",
                "start_macro": f"{upper}_CONST_FAR_DATA_ALIGN4_GLOBAL_START",
                "stop_macro": f"{upper}_CONST_FAR_DATA_ALIGN4_GLOBAL_STOP",
                "used_files": [f"{module_name}_Cfg.c", f"{module_name}_CfgData.h"],
                "notes": "Global const section used by current wakeup-source configuration style.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
            {
                "name": "RUNTIME RAM",
                "target_content": "Wakeup-source runtime caches and DET state.",
                "start_macro": f"{upper}_CLEAR_FAR_DATA_ALIGN4_GLOBAL_START",
                "stop_macro": f"{upper}_CLEAR_FAR_DATA_ALIGN4_GLOBAL_STOP",
                "used_files": [f"{module_name}.c"],
                "notes": "Global runtime section for asynchronous wakeup-state handling.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
            {
                "name": "CALIB",
                "target_content": "Calibration data for wakeup-source thresholds or revise parameters.",
                "start_macro": f"{upper}_CONST_FAR_DATA_ALIGN4_CALI_GLOBAL_START",
                "stop_macro": f"{upper}_CONST_FAR_DATA_ALIGN4_CALI_GLOBAL_STOP",
                "used_files": [f"{module_name}_Cali.c"],
                "notes": "Observed as a real file carrier in the live BswSys_Gp wakeup-source module.",
                "status": "Formal",
                "freeze_status": "formal",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
            },
        ]
    return items


def _needs_reg_h(family: str, seed: dict[str, Any]) -> bool:
    if family == "IoExt":
        return True
    for item in seed.get("capability_notes", []):
        text = f"{item.get('title', '')} {item.get('description', '')}".lower()
        if "register" in text or "寄存器" in text or "i2c" in text or "spi" in text:
            return True
    return False


def _file_items(module_name: str, family: str, seed: dict[str, Any]) -> list[dict[str, Any]]:
    items = [
        {
            "name": f"{module_name}.c",
            "required_level": "Required",
            "responsibility": "Module implementation file.",
            "key_content": "External API implementation and internal helpers.",
            "status": "Formal",
            "freeze_status": "formal",
        },
        {
            "name": f"{module_name}.h",
            "required_level": "Required",
            "responsibility": "External interface header file.",
            "key_content": "Public API prototypes and header-level contract.",
            "status": "Formal",
            "freeze_status": "formal",
        },
        {
            "name": f"{module_name}_Types.h",
            "required_level": "Required",
            "responsibility": "Type definition header file.",
            "key_content": "Architecture-owned type and enum definitions.",
            "status": "Formal",
            "freeze_status": "formal",
        },
        {
            "name": f"{module_name}_Cfg.h",
            "required_level": "Required",
            "responsibility": "Configuration macro header file.",
            "key_content": "Compile-time switches, counts, and mapping macros.",
            "status": "Formal",
            "freeze_status": "formal",
        },
        {
            "name": f"{module_name}_Cfg.c",
            "required_level": "Required",
            "responsibility": "Configuration data implementation file.",
            "key_content": "Concrete configuration tables and project-specific constants.",
            "status": "Formal",
            "freeze_status": "formal",
        },
        {
            "name": f"{module_name}_CfgData.h",
            "required_level": "Required",
            "responsibility": "Configuration data declaration header file.",
            "key_content": "Extern declarations for configuration containers.",
            "status": "Formal",
            "freeze_status": "formal",
        },
        {
            "name": f"{module_name}_Callout.h",
            "required_level": "Required",
            "responsibility": "Project adaptation interface header file.",
            "key_content": "Dependency interface prototypes and adaptation boundary.",
            "status": "Formal",
            "freeze_status": "formal",
        },
        {
            "name": f"{module_name}_Callout.c",
            "required_level": "Required",
            "responsibility": "Project adaptation implementation file.",
            "key_content": "Project/platform binding for callout dependency interfaces.",
            "status": "Formal",
            "freeze_status": "formal",
        },
        {
            "name": f"{module_name}_MemMap.h",
            "required_level": "Required",
            "responsibility": "Memory-section carrier file.",
            "key_content": "Module-specific section start/stop macros.",
            "status": "Formal",
            "freeze_status": "formal",
        },
    ]
    if _needs_reg_h(family, seed):
        items.append(
            {
                "name": f"{module_name}_Reg.h",
                "required_level": "Required",
                "responsibility": "Register definition header file.",
                "key_content": "Register constants, masks, protocol or command definitions.",
                "status": "Formal",
                "freeze_status": "formal",
            }
        )
    if family == "BswSys_Gp":
        items.append(
            {
                "name": f"{module_name}_Cali.c",
                "required_level": "Required",
                "responsibility": "Calibration source file.",
                "key_content": "Calibration values and thresholds used by wakeup-source logic.",
                "status": "Formal",
                "freeze_status": "formal",
            }
        )
    return items


def build_freeze_bundle(seed_path: Path) -> dict[str, Any]:
    seed = yaml.safe_load(seed_path.read_text(encoding="utf-8")) or {}
    module_name = seed.get("module_name", "UnknownModule")
    layer = seed.get("layer", "Unknown")
    family = _module_family(module_name, layer)

    freeze_matrix: list[dict[str, Any]] = []
    coverage_result: list[dict[str, Any]] = []
    rule_evidence: list[dict[str, Any]] = []
    grounding_evidence: list[dict[str, Any]] = []

    frozen_external_interfaces: list[str] = []
    frozen_config_items: list[str] = []
    reserved_capabilities: list[str] = []
    pending_confirm_items: list[str] = []
    implementation_prohibitions = [
        "Do not add new external APIs outside the frozen architecture set.",
        "Do not bypass frozen dependency boundaries with direct platform binding.",
        "Do not treat reserved or pending-confirm items as formal implemented behavior.",
    ]
    implementation_required_areas = [
        "External interface set",
        "Configuration boundary",
        "Risk and pending-confirm handling",
    ]
    external_apis: list[dict[str, Any]] = []
    dependency_apis: list[dict[str, Any]] = _dependency_apis(module_name, family, seed)
    binding_items: list[dict[str, Any]] = _binding_items(module_name, family, seed)
    config_macros: list[dict[str, Any]] = []
    calibration_items: list[dict[str, Any]] = _calibration_items(module_name, family, seed)
    strategy_items: list[dict[str, Any]] = _strategy_items(module_name, family)
    risk_items: list[dict[str, Any]] = []
    file_items: list[dict[str, Any]] = _file_items(module_name, family, seed)
    runtime_states: list[dict[str, Any]] = _runtime_states(module_name, family, seed)
    memmap_sections: list[dict[str, Any]] = _memmap_sections(module_name, family)

    for item in seed.get("external_interface_candidates", []):
        requirement_id = item.get("requirement_id", "UNKNOWN")
        target_name = _external_api_name(item)
        external_apis.append(_external_api_object(module_name, item))
        freeze_matrix.append(
            {
                "source_id": requirement_id,
                "source_type": "architecture_seed",
                "architecture_target": "external_api",
                "target_name": target_name,
                "freeze_action": "freeze_external_api",
                "freeze_status": "formal" if item.get("status") == "ready" else "pending_confirm",
                "reason": item.get("purpose", "Architecture seed proposes this external interface."),
                "decision": "freeze interface",
                "decision_reason": "Seed already identifies this as an external interface candidate.",
                "implementation_impact": "Implementation must preserve this interface boundary once architecture is accepted.",
            }
        )
        coverage_result.append(
            {
                "requirement_id": requirement_id,
                "coverage_status": "covered" if item.get("status") == "ready" else "pending_confirm",
                "coverage_object": target_name,
                "reason": "Architecture seed already maps this requirement to an external interface candidate.",
                "notes": item.get("purpose", ""),
            }
        )
        frozen_external_interfaces.append(target_name)

    for item in seed.get("config_item_candidates", []):
        requirement_id = item.get("requirement_id", "UNKNOWN")
        macro_name = _config_macro_name(module_name, item.get("name", "CONFIG_ITEM"), requirement_id)
        config_macros.append(_config_macro_object(module_name, item))
        freeze_matrix.append(
            {
                "source_id": requirement_id,
                "source_type": "architecture_seed",
                "architecture_target": "config_macro",
                "target_name": macro_name,
                "freeze_action": "freeze_config_macro",
                "freeze_status": "formal" if item.get("status") == "ready" else "pending_confirm",
                "reason": item.get("constraint", "Architecture seed identifies this as a configuration concern."),
                "decision": "freeze config boundary",
                "decision_reason": "Seed already classifies this as a configuration candidate.",
                "implementation_impact": "Implementation must keep this capability within the configuration boundary.",
            }
        )
        coverage_result.append(
            {
                "requirement_id": requirement_id,
                "coverage_status": "covered_with_constraint" if item.get("status") == "ready" else "pending_confirm",
                "coverage_object": macro_name,
                "reason": "Architecture freezes this requirement as a configuration-side object rather than a runtime interface.",
                "notes": item.get("constraint", ""),
            }
        )
        frozen_config_items.append(macro_name)

    config_macros.append(_det_config_macro_object(module_name))
    frozen_config_items.append(f"{_slug_module(module_name).upper()}_CFG_DEV_ERROR_DETECT")
    if family == "IoMcu":
        config_macros.append(
            {
                "name": f"{_slug_module(module_name).upper()}_SPEC_DEP_IF",
                "purpose": "Selects the concrete MCU/DIO dependency binding variant.",
                "macro_type": "Dependency Selection",
                "taxonomy_reason": "IoMcu family exposes explicit dependency interface selection in Cfg.h.",
                "default_value": "TBD",
                "usage_location": f"{module_name}_Cfg.h",
                "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                "status": "Formal",
                "freeze_status": "formal",
                "decision": "freeze dependency selection macro",
                "decision_reason": "Live IoMcu family uses explicit dependency selection in Cfg.h.",
            }
        )
        frozen_config_items.append(f"{_slug_module(module_name).upper()}_SPEC_DEP_IF")
    if family == "Cdd":
        config_macros.extend(
            [
                {
                    "name": f"{_slug_module(module_name).upper()}_CFG_OSP_ENABLE",
                    "purpose": "Controls oversampling-path availability in the Cdd ADC strategy set.",
                    "macro_type": "Feature Enable",
                    "taxonomy_reason": "OSP is an on/off feature gate in live Cdd configuration.",
                    "default_value": "TBD",
                    "usage_location": f"{module_name}_Cfg.h",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "decision": "freeze Cdd strategy switch",
                    "decision_reason": "Live Cdd family exposes strategy-heavy configuration switches in Cfg.h.",
                },
                {
                    "name": f"{_slug_module(module_name).upper()}_CFG_SAMPLE_STRATEGY",
                    "purpose": "Selects ADC sampling strategy for the module family.",
                    "macro_type": "Strategy Selection",
                    "taxonomy_reason": "Live Cdd family keeps sampling strategy as an explicit strategy selector.",
                    "default_value": "TBD",
                    "usage_location": f"{module_name}_Cfg.h",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "decision": "freeze sampling strategy selector",
                    "decision_reason": "Live Cdd family keeps sampling and validity strategy choices in Cfg.h.",
                },
                {
                    "name": f"{_slug_module(module_name).upper()}_CFG_VALIDITY_JUDGE",
                    "purpose": "Selects the sampled-data validity judgment strategy for the module family.",
                    "macro_type": "Strategy Selection",
                    "taxonomy_reason": "Live Cdd family keeps validity-judge logic as an explicit strategy selector.",
                    "default_value": "TBD",
                    "usage_location": f"{module_name}_Cfg.h",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "decision": "freeze validity-judge strategy selector",
                    "decision_reason": "Live Cdd family exposes validity strategy in Cfg.h.",
                },
                {
                    "name": f"{_slug_module(module_name).upper()}_CFG_INVALID_FILL",
                    "purpose": "Selects the invalid-sample fill behavior for the module family.",
                    "macro_type": "Strategy Selection",
                    "taxonomy_reason": "Live Cdd family keeps invalid-fill behavior as an explicit strategy selector.",
                    "default_value": "TBD",
                    "usage_location": f"{module_name}_Cfg.h",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "decision": "freeze invalid-fill strategy selector",
                    "decision_reason": "Live Cdd family exposes invalid-fill strategy in Cfg.h.",
                },
            ]
        )
        frozen_config_items.extend(
            [
                f"{_slug_module(module_name).upper()}_CFG_OSP_ENABLE",
                f"{_slug_module(module_name).upper()}_CFG_SAMPLE_STRATEGY",
                f"{_slug_module(module_name).upper()}_CFG_VALIDITY_JUDGE",
                f"{_slug_module(module_name).upper()}_CFG_INVALID_FILL",
            ]
        )
    if family == "BswSys_Gp":
        config_macros.extend(
            [
                {
                    "name": f"{_slug_module(module_name).upper()}_CFG_DATA_REVISE",
                    "purpose": "Enables wakeup-source data revise logic before final status judgment.",
                    "macro_type": "Feature Enable",
                    "taxonomy_reason": "Data revise is modeled as an enable/disable switch in live BswSys_Gp config.",
                    "default_value": "STD_ON",
                    "usage_location": f"{module_name}_Cfg.h",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "decision": "freeze revise switch",
                    "decision_reason": "Live BswSys_Gp wakeup-source module exposes a data-revise configuration switch.",
                },
                {
                    "name": f"{_slug_module(module_name).upper()}_CFG_SIG_NUM",
                    "purpose": "Defines the configured wakeup-source signal count.",
                    "macro_type": "Count Size",
                    "taxonomy_reason": "Signal count is a classic count/size configuration object.",
                    "default_value": "TBD",
                    "usage_location": f"{module_name}_Cfg.h",
                    "evidence": ["source-grounding-aurix2g-live-baseline.md"],
                    "status": "Formal",
                    "freeze_status": "formal",
                    "decision": "freeze signal-count macro",
                    "decision_reason": "Live BswSys_Gp wakeup-source module publishes wakeup signal count in Cfg.h.",
                },
            ]
        )
        frozen_config_items.extend(
            [
                f"{_slug_module(module_name).upper()}_CFG_DATA_REVISE",
                f"{_slug_module(module_name).upper()}_CFG_SIG_NUM",
            ]
        )

    for idx, item in enumerate(seed.get("pending_confirm_items", []), start=1):
        requirement_id = item.get("requirement_id", "UNKNOWN")
        title = item.get("title", "PendingConfirm")
        gate_level, impact_scope, close_condition = _pending_gate_profile(requirement_id, title)
        risk_item = _risk_item(idx, title, item.get("reason", "Pending confirmation required."))
        risk_item["gate_level"] = gate_level
        risk_item["impact_scope"] = impact_scope
        risk_item["close_condition"] = close_condition
        risk_item["source_requirement_id"] = requirement_id
        risk_items.append(risk_item)
        freeze_matrix.append(
            {
                "source_id": requirement_id,
                "source_type": "architecture_seed",
                "architecture_target": "risk_item",
                "target_name": title,
                "freeze_action": "mark_pending_confirm",
                "freeze_status": "pending_confirm",
                "reason": item.get("reason", "Seed marks this item as pending confirmation."),
                "decision": "isolate pending item",
                "decision_reason": "Pending items must stay explicit in architecture rather than silently frozen as formal facts.",
                "implementation_impact": "Implementation must not assume this item is confirmed.",
            }
        )
        coverage_result.append(
            {
                "requirement_id": requirement_id,
                "coverage_status": "pending_confirm",
                "coverage_object": title,
                "reason": item.get("reason", "Pending confirmation required."),
                "gate_level": gate_level,
                "impact_scope": impact_scope,
                "close_condition": close_condition,
                "notes": "",
            }
        )
        pending_confirm_items.append(title)

    for item in seed.get("architecture_only_items", []):
        title = item.get("title", "ArchitectureConstraint")
        freeze_matrix.append(
            {
                "source_id": item.get("raw_id", "UNKNOWN"),
                "source_type": "architecture_seed",
                "architecture_target": "architecture_constraint",
                "target_name": title,
                "freeze_action": "architecture_only_constraint",
                "freeze_status": "formal",
                "reason": item.get("gate_reason", item.get("description", "Architecture-only constraint.")),
                "decision": "freeze architecture constraint",
                "decision_reason": "This item affects architecture boundary even if it is not a formal external interface.",
                "implementation_impact": "Implementation must preserve this architecture-only constraint.",
            }
        )

    for item in seed.get("capability_notes", []):
        title = item.get("title", "ReservedCapability")
        gate_level, impact_scope, close_condition = _reserved_gate_profile(title, item.get("description", ""))
        freeze_matrix.append(
            {
                "source_id": item.get("raw_id", "UNKNOWN"),
                "source_type": "architecture_seed",
                "architecture_target": "capability_note",
                "target_name": title,
                "freeze_action": "reserve",
                "freeze_status": "reserved",
                "reason": item.get("promotion_reason", item.get("gate_reason", "Capability note is not yet a formal architecture object.")),
                "decision": "reserve capability",
                "decision_reason": "Capability summary exists but is not frozen as a formal architecture object in V1.",
                "implementation_impact": "Implementation must not silently realize this capability beyond frozen formal objects.",
                "gate_level": gate_level,
                "impact_scope": impact_scope,
                "close_condition": close_condition,
                "source_requirement_ids": item.get("linked_formal_requirements", []),
            }
        )
        reserved_capabilities.append(title)

    rule_evidence.append(
        {
            "object_group": "file_items",
            "object_name": module_name,
            "rule_source": "project-style-rules.md",
            "rule_reason": "Architecture follows the established FC file-family and adaptation split rules.",
            "rule_type": "project_style",
        }
    )
    for file_item in file_items:
        rule_evidence.append(
            {
                "object_group": "file_items",
                "object_name": file_item["name"],
                "rule_source": "source-grounding-aurix2g-live-baseline.md",
                "rule_reason": "Live AURIX2G source shows module/config/integration file-family split and callout/MemMap carriers.",
                "rule_type": "live_source_pattern",
            }
        )
    for dep_item in dependency_apis:
        rule_evidence.append(
            {
                "object_group": "dependency_apis",
                "object_name": dep_item["name"],
                "rule_source": "source-grounding-aurix2g-live-baseline.md",
                "rule_reason": "Live AURIX2G module families use family-specific callout adaptation as a first-class dependency mechanism.",
                "rule_type": "live_source_pattern",
            }
        )
    for ext_item in external_apis:
        rule_evidence.append(
            {
                "object_group": "external_apis",
                "object_name": ext_item["name"],
                "rule_source": "fc-architecture-rules.md",
                "rule_reason": "Architecture must freeze module-owned external interfaces explicitly instead of leaving implementation entry points implicit.",
                "rule_type": "architecture_rule",
            }
        )
    for macro_item in config_macros:
        rule_evidence.append(
            {
                "object_group": "config_macros",
                "object_name": macro_item["name"],
                "rule_source": "project-style-rules.md",
                "rule_reason": "Project style requires compile-time feature, mapping, strategy, and timing decisions to stay in explicit configuration carriers.",
                "rule_type": "project_style",
            }
        )
    for binding_item in binding_items:
        rule_evidence.append(
            {
                "object_group": "binding_items",
                "object_name": binding_item["name"],
                "rule_source": "source-grounding-aurix2g-live-baseline.md",
                "rule_reason": "Live AURIX2G families freeze not only dependency APIs but also the binding boundary between FC logic and dependency provider.",
                "rule_type": "live_source_pattern",
            }
        )
        freeze_matrix.append(
            {
                "source_id": binding_item["target_side"],
                "source_type": "grounding_rule",
                "architecture_target": "binding_item",
                "target_name": binding_item["name"],
                "freeze_action": "freeze_binding_item",
                "freeze_status": binding_item["freeze_status"],
                "reason": binding_item["description"],
                "decision": "freeze binding boundary",
                "decision_reason": "Binding semantics should stay explicit architecture objects instead of being inferred only from APIs or macros.",
                "implementation_impact": "Implementation must preserve this binding boundary and must not bypass it silently.",
            }
        )
    for cal_item in calibration_items:
        rule_evidence.append(
            {
                "object_group": "calibration_items",
                "object_name": cal_item["name"],
                "rule_source": "source-grounding-aurix2g-live-baseline.md",
                "rule_reason": "Live AURIX2G families use explicit calibration carriers when thresholds, revise parameters, or fill behaviors need project tuning.",
                "rule_type": "live_source_pattern",
            }
        )
    for strategy_item in strategy_items:
        rule_evidence.append(
            {
                "object_group": "strategy_items",
                "object_name": strategy_item["name"],
                "rule_source": "source-grounding-aurix2g-live-baseline.md",
                "rule_reason": "Live AURIX2G Cdd family uses explicit compile-time strategy selection for sampling, validity, and invalid-fill behavior.",
                "rule_type": "live_source_pattern",
            }
        )
        freeze_matrix.append(
            {
                "source_id": strategy_item["backing_reference"],
                "source_type": "grounding_rule",
                "architecture_target": "strategy_item",
                "target_name": strategy_item["name"],
                "freeze_action": "freeze_strategy_item",
                "freeze_status": strategy_item["freeze_status"],
                "reason": strategy_item["description"],
                "decision": "freeze strategy object",
                "decision_reason": "Strategy semantics should remain explicit architecture objects instead of hiding only in macro names.",
                "implementation_impact": "Implementation must preserve the selected strategy boundary and not silently replace it with unrelated behavior.",
            }
        )
    for runtime_item in runtime_states:
        rule_evidence.append(
            {
                "object_group": "runtime_states",
                "object_name": runtime_item["name"],
                "rule_source": "static-vs-dynamic.md",
                "rule_reason": "Runtime state areas must remain explicitly classified so initialization, concurrency, and lifecycle boundaries stay stable across implementation.",
                "rule_type": "lifecycle_rule",
            }
        )
    for memmap_item in memmap_sections:
        rule_evidence.append(
            {
                "object_group": "memmap_sections",
                "object_name": memmap_item["name"],
                "rule_source": "project-style-rules.md",
                "rule_reason": "Project style requires code, const, and runtime areas to be frozen through explicit MemMap sections rather than inferred ad hoc by implementation.",
                "rule_type": "memmap_rule",
            }
        )
    grounding_evidence.append(
        {
            "object_group": "module_family",
            "object_name": module_name,
            "grounding_source": "source-grounding-aurix2g-live-baseline.md",
            "grounding_reason": "Freeze decisions should follow live AURIX2G source/config/integration split and adaptation style.",
            "pattern_name": layer,
        }
    )

    bundle = {
        "module": module_name,
        "architecture_version": "V1",
        "architecture_status": "Draft",
        "output_mode": "Formal Draft",
        "layer": layer,
        "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "grounding_summary": {
            "module_family": family,
            "closest_live_patterns": ["Gp_TLE92104"] if family == "IoExt" else (["Gp_IoMcuDio"] if family == "IoMcu" else (["Gp_06_Adc3ph"] if family == "Cdd" else (["Gp_WkUpSrcP"] if family == "BswSys_Gp" else [layer]))),
            "config_split_style": "Source/config/integration split",
            "notes": "Initial freeze bundle generated from architecture seed only.",
        },
        "input_contract": {
            "requirement_input": "",
            "architecture_seed": str(seed_path),
            "grounding_sources": ["references/source-grounding-aurix2g-live-baseline.md"],
            "project_constraints": ["Architecture skill optimized independently without cross-skill bridge assumptions."],
        },
        "freeze_matrix": freeze_matrix,
        "coverage_result": coverage_result,
        "rule_evidence": rule_evidence,
        "grounding_evidence": grounding_evidence,
        "external_apis": external_apis,
        "dependency_apis": dependency_apis,
        "binding_items": binding_items,
        "config_macros": config_macros,
        "strategy_items": strategy_items,
        "calibration_items": calibration_items,
        "runtime_states": runtime_states,
        "memmap_sections": memmap_sections,
        "file_items": file_items,
        "risk_items": risk_items,
        "implementation_constraints": {
            "frozen_external_interfaces": frozen_external_interfaces,
            "frozen_dependency_interfaces": [item["name"] for item in dependency_apis],
            "frozen_binding_items": [item["name"] for item in binding_items if item.get("freeze_status") == "formal"],
            "frozen_config_items": frozen_config_items,
            "frozen_strategy_items": [item["name"] for item in strategy_items if item.get("freeze_status") == "formal"],
            "frozen_calibration_items": [item["name"] for item in calibration_items if item.get("freeze_status") in {"formal", "conditional"}],
            "reserved_capabilities": reserved_capabilities,
            "pending_confirm_items": pending_confirm_items,
            "implementation_prohibitions": implementation_prohibitions,
            "implementation_required_areas": implementation_required_areas,
        },
        "change_summary": ["Initial freeze bundle generated from architecture seed."],
    }
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Build FC architecture freeze bundle JSON from architecture seed YAML.")
    parser.add_argument("seed", help="Architecture seed YAML path")
    parser.add_argument("-o", "--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    seed_path = Path(args.seed)
    out_path = Path(args.output)
    bundle = build_freeze_bundle(seed_path)
    out_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote freeze bundle: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
