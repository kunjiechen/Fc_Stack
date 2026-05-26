from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _module_family(module: str, layer: str) -> str:
    lowered_module = (module or "").lower()
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


def _file_names(payload: dict[str, Any]) -> set[str]:
    return {
        item.get("name", "")
        for item in payload.get("file_items", [])
        if isinstance(item, dict) and item.get("name")
    }


def _dep_names(payload: dict[str, Any]) -> set[str]:
    return {
        item.get("name", "")
        for item in payload.get("dependency_apis", [])
        if isinstance(item, dict) and item.get("name")
    }


def _binding_names(payload: dict[str, Any]) -> set[str]:
    return {
        item.get("name", "")
        for item in payload.get("binding_items", [])
        if isinstance(item, dict) and item.get("name")
    }


def _memmap_names(payload: dict[str, Any]) -> set[str]:
    return {
        item.get("name", "")
        for item in payload.get("memmap_sections", [])
        if isinstance(item, dict) and item.get("name")
    }


def _runtime_names(payload: dict[str, Any]) -> list[str]:
    return [
        item.get("name", "")
        for item in payload.get("runtime_states", [])
        if isinstance(item, dict) and item.get("name")
    ]


def _config_macro_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in payload.get("config_macros", [])
        if isinstance(item, dict)
    ]


def _macro_type(config_macros: list[dict[str, Any]], name: str) -> str:
    for item in config_macros:
        if item.get("name") == name:
            return item.get("macro_type", "")
    return ""


def _calibration_names(payload: dict[str, Any]) -> set[str]:
    return {
        item.get("name", "")
        for item in payload.get("calibration_items", [])
        if isinstance(item, dict) and item.get("name")
    }


def _strategy_names(payload: dict[str, Any]) -> set[str]:
    return {
        item.get("name", "")
        for item in payload.get("strategy_items", [])
        if isinstance(item, dict) and item.get("name")
    }


def validate_architecture_source_alignment(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    issues: list[str] = []

    if not isinstance(payload, dict):
        return [f"{path}: top-level payload must be a JSON object"]

    module = payload.get("module", "")
    layer = (payload.get("layer", "") or "").lower()
    family = _module_family(module, layer)
    grounding = payload.get("grounding_summary", {}) or {}
    file_names = _file_names(payload)
    dep_names = _dep_names(payload)
    binding_names = _binding_names(payload)
    memmap_names = _memmap_names(payload)
    runtime_names = _runtime_names(payload)
    config_macros = _config_macro_items(payload)
    calibration_names = _calibration_names(payload)
    strategy_names = _strategy_names(payload)

    config_split_style = grounding.get("config_split_style", "")
    if config_split_style == "Source/config/integration split":
        required_files = {
            f"{module}.c",
            f"{module}.h",
            f"{module}_Types.h",
            f"{module}_Cfg.h",
            f"{module}_Cfg.c",
            f"{module}_CfgData.h",
            f"{module}_MemMap.h",
        }
        missing = sorted(name for name in required_files if name not in file_names)
        if missing:
            issues.append(f"{path}: source/config/integration split grounding expects file_items: {', '.join(missing)}")

    has_callout_files = f"{module}_Callout.h" in file_names and f"{module}_Callout.c" in file_names
    has_callout_dep = any("Callout" in name for name in dep_names)
    if has_callout_dep and not has_callout_files:
        issues.append(f"{path}: callout dependency exists but file_items do not include both {module}_Callout.h and {module}_Callout.c")
    if family == "IoExt" and not has_callout_dep:
        issues.append(f"{path}: IoExt-style module should normally expose callout dependency interfaces based on live-source grounding")

    needs_reg_h = family == "IoExt"
    if needs_reg_h and f"{module}_Reg.h" not in file_names:
        issues.append(f"{path}: IoExt-style module should include {module}_Reg.h according to live-source grounding")
    if family in {"IoMcu", "Cdd"} and f"{module}_Reg.h" in file_names:
        issues.append(f"{path}: {family}-style module should not default to {module}_Reg.h unless the architecture explicitly owns device-register constants")

    if "MainFunction" in {name.split("_")[-1] for name in [item.get("name", "") for item in payload.get("external_apis", []) if isinstance(item, dict)]}:
        if not any(name.endswith("CalloutReadDio") for name in dep_names):
            issues.append(f"{path}: module with MainFunction should normally expose a status/interrupt sampling callout dependency")

    required_memmap = {"CODE", "CONST PER-CORE", "RUNTIME RAM"} if family != "BswSys_Gp" else {"CODE", "CONST GLOBAL", "RUNTIME RAM", "CALIB"}
    missing_memmap = sorted(name for name in required_memmap if name not in memmap_names)
    if missing_memmap:
        issues.append(f"{path}: live-source grounding expects MemMap sections: {', '.join(missing_memmap)}")

    if any("多核" in str(row.get("target_name", "")) for row in payload.get("freeze_matrix", []) if isinstance(row, dict)):
        if not any("Per-core" in name for name in runtime_names):
            issues.append(f"{path}: multi-core architecture constraint exists but runtime_states do not show per-core ownership")
        if "CONST PER-CORE" not in memmap_names or "RUNTIME RAM" not in memmap_names:
            issues.append(f"{path}: multi-core architecture constraint exists but per-core MemMap sections are incomplete")

    if any("Fault" in item.get("name", "") for item in payload.get("external_apis", []) if isinstance(item, dict)):
        if not any("fault" in name.lower() or "det" in name.lower() for name in runtime_names):
            issues.append(f"{path}: diagnostic/fault external API exists but runtime_states do not show fault/DET bookkeeping")

    if config_split_style == "Source/config/integration split":
        if f"{module}_CfgData.h" in file_names:
            expected_const_section = "CONST GLOBAL" if family == "BswSys_Gp" else "CONST PER-CORE"
            if expected_const_section not in memmap_names:
                issues.append(f"{path}: {module}_CfgData.h exists but architecture does not freeze the expected configuration const section {expected_const_section}")
        for index, item in enumerate(config_macros):
            usage_location = item.get("usage_location", "")
            if usage_location and usage_location != f"{module}_Cfg.h":
                issues.append(f"{path}: config_macros[{index}] should normally use {module}_Cfg.h as usage_location under current source split")
            if item.get("macro_type") == "Development Error Detect":
                if not any("det" in name.lower() for name in runtime_names):
                    issues.append(f"{path}: DET-related config macro exists but runtime_states do not show DET/fault bookkeeping")

    actual_suffixes = {name.split(f"{module}_", 1)[-1] for name in dep_names if name.startswith(f"{module}_")}

    if family == "IoExt":
        expected_dep_suffixes = {"CalloutGetCoreId", "CalloutI2cRead", "CalloutI2cWrite"}
        missing_dep = sorted(suffix for suffix in expected_dep_suffixes if suffix not in actual_suffixes)
        if missing_dep:
            issues.append(f"{path}: IoExt-style module is missing expected dependency APIs: {', '.join(missing_dep)}")
        if any("MainFunction" in item.get("name", "") for item in payload.get("external_apis", []) if isinstance(item, dict)):
            if "CalloutReadDio" not in actual_suffixes:
                issues.append(f"{path}: IoExt-style module with MainFunction should normally expose CalloutReadDio")
        expected_binding = {
            f"{module}_CoreSelectionBinding",
            f"{module}_DeviceRegisterAccessBinding",
        }
        if any("MainFunction" in item.get("name", "") for item in payload.get("external_apis", []) if isinstance(item, dict)):
            expected_binding.add(f"{module}_StatusSamplingBinding")
        missing_binding = sorted(name for name in expected_binding if name not in binding_names)
        if missing_binding:
            issues.append(f"{path}: IoExt-style module should normally expose binding items: {', '.join(missing_binding)}")
    elif family == "IoMcu":
        expected_dep_suffixes = {
            "CalloutGetCoreId",
            "CalloutInit",
            "CalloutSetDioSigDir",
            "CalloutGetDioSigLvlIn",
            "CalloutSetDioSigLvlOut",
        }
        missing_dep = sorted(suffix for suffix in expected_dep_suffixes if suffix not in actual_suffixes)
        if missing_dep:
            issues.append(f"{path}: IoMcu-style module is missing expected dependency APIs: {', '.join(missing_dep)}")
        if any("MainFunction" in item.get("name", "") for item in payload.get("external_apis", []) if isinstance(item, dict)):
            issues.append(f"{path}: IoMcu-style module should not default to MainFunction when grounding shows synchronous API style")
        if not any(item.get("name") == f"{module.upper()}_SPEC_DEP_IF" for item in config_macros):
            issues.append(f"{path}: IoMcu-style module should normally freeze a dependency-selection macro such as {module.upper()}_SPEC_DEP_IF")
        elif _macro_type(config_macros, f"{module.upper()}_SPEC_DEP_IF") != "Dependency Selection":
            issues.append(f"{path}: IoMcu-style dependency-selection macro should use macro_type Dependency Selection")
        if not any("route cache" in name.lower() for name in runtime_names):
            issues.append(f"{path}: IoMcu-style module should normally expose a per-core DIO route cache runtime state")
        expected_binding = {
            f"{module}_CoreSelectionBinding",
            f"{module}_DependencySelectionBinding",
            f"{module}_DioAccessBinding",
        }
        missing_binding = sorted(name for name in expected_binding if name not in binding_names)
        if missing_binding:
            issues.append(f"{path}: IoMcu-style module should normally expose binding items: {', '.join(missing_binding)}")
    elif family == "Cdd":
        expected_dep_suffixes = {"CalloutGetCoreId", "CalloutDelayUs", "CalloutTrigEnable"}
        missing_dep = sorted(suffix for suffix in expected_dep_suffixes if suffix not in actual_suffixes)
        if missing_dep:
            issues.append(f"{path}: Cdd-style module is missing expected dependency APIs: {', '.join(missing_dep)}")
        if "CODE RAM COPY" not in memmap_names:
            issues.append(f"{path}: Cdd-style module should normally freeze a CODE RAM COPY MemMap section when following live-source grounding")
        if not any(item.get("name") == f"{module.upper()}_CFG_SAMPLE_STRATEGY" for item in config_macros):
            issues.append(f"{path}: Cdd-style module should normally freeze a sample-strategy configuration macro")
        elif _macro_type(config_macros, f"{module.upper()}_CFG_SAMPLE_STRATEGY") != "Strategy Selection":
            issues.append(f"{path}: Cdd-style sample-strategy macro should use macro_type Strategy Selection")
        if not any("conversion cache" in name.lower() for name in runtime_names):
            issues.append(f"{path}: Cdd-style module should normally expose a per-core ADC conversion cache runtime state")
        expected_calibration = {
            f"{module}_SampleValidityThreshold",
            f"{module}_InvalidFillBehavior",
        }
        missing_calibration = sorted(name for name in expected_calibration if name not in calibration_names)
        if missing_calibration:
            issues.append(f"{path}: Cdd-style module should normally expose calibration items: {', '.join(missing_calibration)}")
        expected_strategy = {
            f"{module}_SampleStrategy",
            f"{module}_ValidityJudgeStrategy",
            f"{module}_InvalidFillStrategy",
        }
        missing_strategy = sorted(name for name in expected_strategy if name not in strategy_names)
        if missing_strategy:
            issues.append(f"{path}: Cdd-style module should normally expose strategy items: {', '.join(missing_strategy)}")
        if _macro_type(config_macros, f"{module.upper()}_CFG_VALIDITY_JUDGE") != "Strategy Selection":
            issues.append(f"{path}: Cdd-style validity-judge macro should use macro_type Strategy Selection")
        if _macro_type(config_macros, f"{module.upper()}_CFG_INVALID_FILL") != "Strategy Selection":
            issues.append(f"{path}: Cdd-style invalid-fill macro should use macro_type Strategy Selection")
        expected_binding = {
            f"{module}_CoreSelectionBinding",
            f"{module}_SamplingDelayBinding",
            f"{module}_TriggerControlBinding",
        }
        missing_binding = sorted(name for name in expected_binding if name not in binding_names)
        if missing_binding:
            issues.append(f"{path}: Cdd-style module should normally expose binding items: {', '.join(missing_binding)}")
    elif family == "BswSys_Gp":
        expected_dep_suffixes = {"CalloutWkSrcDataRevise"}
        missing_dep = sorted(suffix for suffix in expected_dep_suffixes if suffix not in actual_suffixes)
        if missing_dep:
            issues.append(f"{path}: BswSys_Gp-style module is missing expected dependency APIs: {', '.join(missing_dep)}")
        if not any(item.get("name") == f"{module.upper()}_CFG_DATA_REVISE" for item in config_macros):
            issues.append(f"{path}: BswSys_Gp-style module should normally freeze a data-revise configuration macro")
        if not any(item.get("name") == f"{module.upper()}_CFG_SIG_NUM" for item in config_macros):
            issues.append(f"{path}: BswSys_Gp-style module should normally freeze a wakeup-signal count macro")
        elif _macro_type(config_macros, f"{module.upper()}_CFG_SIG_NUM") != "Count Size":
            issues.append(f"{path}: BswSys_Gp-style signal-count macro should use macro_type Count Size")
        if f"{module}_Cali.c" not in file_names:
            issues.append(f"{path}: BswSys_Gp-style wakeup-source module should include {module}_Cali.c based on live-source grounding")
        if not any("wakeup" in name.lower() for name in runtime_names):
            issues.append(f"{path}: BswSys_Gp-style module should normally expose wakeup-related runtime caches")
        expected_calibration = {
            f"{module}_GearLimitThreshold",
            f"{module}_ReviseParameterSet",
        }
        missing_calibration = sorted(name for name in expected_calibration if name not in calibration_names)
        if missing_calibration:
            issues.append(f"{path}: BswSys_Gp-style module should normally expose calibration items: {', '.join(missing_calibration)}")
        expected_strategy = {
            f"{module}_WakeParserStrategy",
            f"{module}_WakeReviseStrategy",
            f"{module}_WakeJudgeStrategy",
        }
        missing_strategy = sorted(name for name in expected_strategy if name not in strategy_names)
        if missing_strategy:
            issues.append(f"{path}: BswSys_Gp-style module should normally expose strategy items: {', '.join(missing_strategy)}")
        expected_binding = {
            f"{module}_WakeSourceDependencyBinding",
            f"{module}_WakeReviseBinding",
        }
        missing_binding = sorted(name for name in expected_binding if name not in binding_names)
        if missing_binding:
            issues.append(f"{path}: BswSys_Gp-style module should normally expose binding items: {', '.join(missing_binding)}")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate architecture bundle alignment against live-source grounding rules.")
    parser.add_argument("paths", nargs="+", help="JSON file(s) to validate")
    args = parser.parse_args()

    issues: list[str] = []
    for raw_path in args.paths:
        path = Path(raw_path)
        if path.is_dir():
            for child in sorted(path.rglob("*.json")):
                issues.extend(validate_architecture_source_alignment(child))
        else:
            issues.extend(validate_architecture_source_alignment(path))

    if issues:
        for issue in issues:
            print(issue)
        return 1

    print("Architecture source-alignment validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
