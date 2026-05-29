"""Pipeline helpers for orchestration, enrichment, and overview assembly."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .builder import EngineeringRequirement
from .rules import ProjectConstraints


def load_constraints(path: Path | None) -> ProjectConstraints:
    if path is None:
        return ProjectConstraints()
    return ProjectConstraints.from_text(path.read_text(encoding="utf-8"))


def enrich_engineering_requirements(
    requirements: list[EngineeringRequirement],
    *,
    module: str,
    raw_document: Any | None,
) -> list[EngineeringRequirement]:
    enriched = list(requirements)
    token = _normalize_module_token(module)

    if raw_document is None:
        return enriched

    raw_items = (
        list(raw_document.functional_reqs)
        + list(raw_document.interface_reqs)
        + list(raw_document.config_reqs)
        + list(raw_document.nfr_reqs)
    )

    req_text = " ".join(
        " ".join(
            [
                req.title,
                req.description,
                req.constraint,
                req.input,
                req.output,
                req.exception,
                req.function_name,
            ]
        ).lower()
        for req in enriched
    )

    _enrich_det(enriched, raw_items, req_text, token)
    _enrich_pwm_dependency(enriched, raw_items, req_text, token)
    _enrich_spi_dependency(enriched, raw_items, req_text, token)
    _enrich_capability_items(enriched, raw_items, req_text, token)
    return enriched


def overview_from_features(
    features: list[Any],
    module: str,
    safety_level: str = "QM",
) -> dict[str, Any]:
    if not features:
        return {"safety_level": safety_level}
    groups = [f for f in features if getattr(f, "type", "") == "feature_group"]
    identity = next((f for f in features if getattr(f, "type", "") == "identity"), None)
    pins = [f for f in features if getattr(f, "type", "") == "pin"]
    chip_intro = _chip_intro(identity, groups, module)
    pin_rows: list[tuple[str, str, str]] = [_pin_row(pin) for pin in pins[:32]]
    return _generic_overview(module, chip_intro, groups, pin_rows, safety_level)


def _enrich_det(
    enriched: list[EngineeringRequirement],
    raw_items: list[Any],
    req_text: str,
    token: str,
) -> None:
    if "det" in req_text or "开发错误" in req_text:
        return

    has_det_raw = any(
        _item_text(item)
        and (
            "det" in _item_text(item)
            or "开发错误" in _item_text(item)
            or "参数有效性检查" in _item_text(item)
        )
        for item in raw_items
    )
    if not has_det_raw:
        return

    enriched.append(
        EngineeringRequirement(
            requirement_id=f"SRS-{token}-DIAG-9001",
            semantic_id=f"ENRICHED-{token}-DIAG-DET",
            requirement_type="diagnostic",
            title="开发错误检测",
            description="软件应提供开发错误检测能力，对未初始化访问、空指针、非法参数和非法调用顺序进行检测，并按项目约定进行 DET 上报或错误返回。",
            exception="未初始化访问、空指针、非法参数、非法状态调用时，应拒绝继续执行当前请求并保持无关状态不被破坏。",
            constraint="DET 为必备需求；若项目未集成 DET 模块，也应保留等效的开发错误检测和错误返回语义。",
            verification="通过接口测试、边界测试和故障注入验证：触发未初始化访问、空指针、非法参数和非法调用顺序时，应产生定义的 DET 上报或错误返回，且内部状态保持一致。",
            source=[{"document": "Auto Enrichment", "chunk_id": "ENRICHED-DIAG-DET", "evidence": "Derived from raw DET/configuration and interface contract inputs."}],
        )
    )


def _enrich_pwm_dependency(
    enriched: list[EngineeringRequirement],
    raw_items: list[Any],
    req_text: str,
    token: str,
) -> None:
    has_pwm_raw = any(
        token_text in _item_text(item)
        for item in raw_items
        for token_text in ("pwm", "占空比", "周期")
    ) or any(
        token_text in req_text for token_text in ("pwm", "占空比", "周期", "sethboutsig")
    )
    has_pwm_dep = ("setduty" in req_text) or ("getduty" in req_text)
    if not has_pwm_raw or has_pwm_dep:
        return

    enriched.append(
        EngineeringRequirement(
            requirement_id=f"SRS-{token}-FUNC-9001",
            semantic_id=f"ENRICHED-{token}-PWM-DEPENDENCY",
            requirement_type="functional",
            title="PWM依赖集成",
            description="软件应通过项目定义的 PWM 服务完成目标 H 桥输出的周期和占空比控制，并明确 SetDuty 与 GetDuty 或等效能力的依赖边界、错误返回和调用时序。",
            trigger="当上层请求更新 H 桥周期、占空比或方向输出时。",
            input="目标通道标识、周期值、占空比值、方向值。",
            output="PWM 服务调用结果、目标输出刷新结果。",
            exception="PWM 服务未初始化、参数非法或底层调用失败时，应返回定义错误并保持无关输出状态不被破坏。",
            constraint="应明确 SetDuty 与 GetDuty 或等效 PWM 能力的服务归属、单位换算和同步/异步调用策略。",
            verification="通过接口测试和集成测试验证：对有效周期/占空比输入应产生预期 PWM 输出；对非法参数、未初始化和 PWM 服务失败场景，应返回定义错误并保持输出状态一致。",
            source=[{"document": "Auto Enrichment", "chunk_id": "ENRICHED-PWM-DEPENDENCY", "evidence": "Derived from raw PWM/period/duty requirements and interface signatures."}],
        )
    )


def _enrich_spi_dependency(
    enriched: list[EngineeringRequirement],
    raw_items: list[Any],
    req_text: str,
    token: str,
) -> None:
    has_spi_raw = any("spi" in _item_text(item) for item in raw_items)
    has_spi_dep = any(
        token_text in req_text
        for token_text in ("spi dependency", "spi communication dependency", "spi服务", "spi 服务依赖")
    )
    if not has_spi_raw or has_spi_dep:
        return

    enriched.append(
        EngineeringRequirement(
            requirement_id=f"SRS-{token}-FUNC-9002",
            semantic_id=f"ENRICHED-{token}-SPI-DEPENDENCY",
            requirement_type="functional",
            title="SPI通信依赖",
            description="软件应通过项目定义的 SPI 服务完成外部芯片访问，并明确 SPI 通信依赖、调用边界、错误返回和同步调用策略。",
            trigger="当驱动需要访问外部芯片寄存器、模式状态或故障信息时。",
            input="目标芯片标识、寄存器访问请求、发送数据或读写控制参数。",
            output="SPI 服务调用结果、接收数据或通信失败状态。",
            exception="SPI 服务未初始化、参数非法或底层调用失败时，应返回定义错误并保持无关状态不被破坏。",
            constraint="应明确 SPI 服务归属、同步/异步调用策略、超时处理和错误码映射。",
            verification="通过接口测试和集成测试验证：对有效 SPI 访问请求应完成预期通信；对未初始化、非法参数和 SPI 调用失败场景，应返回定义错误并保持运行时状态一致。",
            source=[{"document": "Auto Enrichment", "chunk_id": "ENRICHED-SPI-DEPENDENCY", "evidence": "Derived from raw SPI access requirements and interface signatures."}],
        )
    )


def _enrich_capability_items(
    enriched: list[EngineeringRequirement],
    raw_items: list[Any],
    req_text: str,
    token: str,
) -> None:
    capability_items = [
        item
        for item in raw_items
        if getattr(item, "disposition", "") == "capability"
        and getattr(item, "category", "") in ("FUNC", "CFG")
    ]

    if any("极性反转" in _item_text(item) for item in capability_items) and "极性反转" not in req_text:
        enriched.append(
            EngineeringRequirement(
                requirement_id=f"SRS-{token}-FUNC-9003",
                semantic_id=f"ENRICHED-{token}-POLARITY",
                requirement_type="functional",
                title="极性反转配置",
                description="软件应支持按项目配置对目标输入信号执行极性反转配置，并明确适用对象、默认值和非法配置处理规则。",
                input="目标信号标识、极性配置值。",
                output="极性配置结果或定义错误返回。",
                exception="当目标信号非法、不支持极性反转或底层访问失败时，应返回定义错误并保持原有配置不变。",
                constraint="应明确极性反转的适用范围、运行时修改策略和默认配置来源。",
                verification="通过功能测试和边界测试验证：有效极性配置应产生预期逻辑反转结果；非法输入或底层失败场景应返回定义错误且不破坏既有配置。",
                source=[{"document": "Auto Enrichment", "chunk_id": "ENRICHED-POLARITY-CONFIG", "evidence": "Derived from capability-level polarity configuration statement."}],
            )
        )

    if (
        any(("故障清除" in _item_text(item)) or ("看门狗" in _item_text(item)) for item in capability_items)
        and "故障清除" not in req_text
        and "看门狗" not in req_text
    ):
        enriched.append(
            EngineeringRequirement(
                requirement_id=f"SRS-{token}-FUNC-9004",
                semantic_id=f"ENRICHED-{token}-FAULT-WD",
                requirement_type="functional",
                title="故障清除与看门狗控制",
                description="软件应支持按项目定义执行故障清除和看门狗相关模式控制，并明确触发条件、调用路径、状态影响和错误返回规则。",
                trigger="当上层请求清除故障状态或执行看门狗相关模式控制时。",
                input="目标芯片标识、控制模式值或清故障请求。",
                output="模式控制结果、故障清除结果或定义错误返回。",
                exception="当控制模式非法、驱动未初始化或底层访问失败时，应返回定义错误并保持无关状态不被破坏。",
                constraint="应明确故障清除模式、自动清故障策略、看门狗开关策略及其配置来源。",
                verification="通过接口测试和故障注入验证：有效控制请求应产生预期模式变化或故障清除结果；非法输入和底层失败场景应返回定义错误并保持状态一致。",
                source=[{"document": "Auto Enrichment", "chunk_id": "ENRICHED-FAULT-WD", "evidence": "Derived from capability-level fault-clear and watchdog control statement."}],
            )
        )


def _item_text(item: Any) -> str:
    title = getattr(item, "title", "") or ""
    description = getattr(item, "description", "") or ""
    return f"{title} {description}".lower()


def _normalize_module_token(module: str) -> str:
    return "".join(ch for ch in module.upper() if ch.isalnum()) or "FC"


def _generic_overview(
    module: str,
    chip_intro: str,
    groups: list[Any],
    pin_rows: list[tuple[str, str, str]],
    safety_level: str = "QM",
) -> dict[str, Any]:
    functions = [_feature_summary(g) for g in groups[:12]]
    state_group = next((g for g in groups if _has_state_related_feature(g)), None)
    sm_data = None
    if state_group:
        sm_data = {
            "summary": f"{_feature_summary(state_group)} 驱动需根据项目定义处理状态切换和恢复行为。",
            "diagram": "",
            "states": getattr(state_group, "states", []) if hasattr(state_group, "states") else [],
            "transitions": [],
        }
    return {
        "chip_intro": chip_intro,
        "chip_capabilities": [
            f"{_feature_summary(g)}" for g in groups[:5] if getattr(g, "name", "")
        ] or None,
        "driver_functions": functions[:5] if functions else ["根据项目确认的软件责任生成驱动功能需求。"],
        "driver_boundary_constraints": [
            "驱动不控制芯片硬件复位引脚，复位由外部硬件电路管理。",
            "驱动不控制总线电气特性，由硬件设计保证。",
        ],
        "driver_pending_items": [
            "项目外设使用范围（引脚、功能、模式）。",
            "默认配置参数表。",
            "底层通信接口规范和错误返回策略。",
        ],
        "pin_rows": pin_rows or [("待确认", "待确认", "待提取")],
        "state_machine": sm_data,
        "communication": None,
        "safety_level": safety_level,
    }


def _has_state_related_feature(feature: Any) -> bool:
    text = " ".join(
        [
            getattr(feature, "name", ""),
            getattr(feature, "feature_category", ""),
            getattr(feature, "functional_summary", ""),
        ]
    ).lower()
    return any(keyword in text for keyword in ("state machine", "transition", "mode switch", "operating mode"))


def _chip_intro(identity: Any, groups: list[Any], module: str) -> str:
    names = "、".join(_feature_name_cn(getattr(g, "name", "")) for g in groups[:8])
    if identity:
        return (
            f"`{module}` 外设芯片主要能力包括：{names or '外设访问、配置和状态处理'}。"
            "驱动应根据项目硬件连接和软件接口边界实现对应的软件控制能力。"
        )
    return (
        f"`{module}` 外设芯片用于扩展控制器外部控制和状态采集能力，"
        "驱动负责封装芯片访问、配置和运行时控制行为。"
    )


def _feature_summary(feature: Any) -> str:
    name = _feature_name_cn(getattr(feature, "name", ""))
    summary = getattr(feature, "functional_summary", "") or getattr(feature, "content", "")
    if name:
        return f"{name}：{_summary_cn(summary)}"
    return _summary_cn(summary)


def _feature_name_cn(name: str) -> str:
    # Data-driven: return the name as-is since feature group names are now
    # generated from actual data rather than from a hardcoded template.
    return name


def _summary_cn(summary: str) -> str:
    # Data-driven: return the summary as-is since feature group summaries are
    # now generated from actual extracted data.
    return summary


def _pin_row(pin: Any) -> tuple[str, str, str]:
    name = getattr(pin, "name", "")
    content = getattr(pin, "content", "")
    direction = "待确认"
    function = content
    lowered = content.lower()

    # Try exact prefix match first (e.g. "Input: ..." or "Output — ...").
    for candidate in ("input", "output", "bidirectional"):
        if lowered.startswith(candidate):
            direction = {"input": "输入", "output": "输出", "bidirectional": "双向"}[candidate]
            function = content.split(".", 1)[1].strip() if "." in content else content
            break

    # Fallback: many datasheets embed direction in prose descriptions
    # like "transmit data input" or "receive data output".  Check for
    # direction keywords anywhere in the content, preferring the most
    # specific match.
    if direction == "待确认":
        if re.search(r"\binput\b", lowered):
            direction = "输入"
        elif re.search(r"\boutput\b", lowered):
            direction = "输出"
        elif re.search(r"\b(bidirectional|i/o|input/output)\b", lowered):
            direction = "双向"

    if direction == "待确认":
        direction = _pin_direction(name)
    function = _pin_function_cn(function)
    return (name, direction, function or "待提取")


def _pin_direction(name: str) -> str:
    """Infer pin direction from the pin symbol using common naming conventions.

    This is a best-effort fallback when the datasheet table does not have
    a dedicated direction/type column and the description text does not
    contain explicit direction keywords.
    """
    upper = name.upper().replace("_", "").replace("-", "").replace(" ", "")
    # Input signals: chip receives from MCU
    if re.search(r"(TXD|TX|MOSI|SCK|CS|NCS|SS|EN|STB|IN|SEL|RE|WE)$", upper):
        return "输入"
    # Output signals: chip drives to MCU
    if re.search(r"(RXD|RX|MISO|INT|ERR|FAULT|INH|RDY|SO|DOUT)$", upper):
        return "输出"
    # Bidirectional
    if re.search(r"(SDA|SDI|SDO|IO\d*)$", upper):
        return "双向"
    # Power / ground — these are not MCU-facing signals
    if re.search(r"^(V|VBAT|VCC|VDD|VSS|VIO|GND|BAT)", upper):
        return "供电"
    # Known specific pins
    hardcoded = {
        "A0": "输入", "A1": "输入", "A2": "输入",
        "RESET": "输入", "RESETN": "输入",
        "SCL": "输入", "SCLK": "输入",
        "WAKE": "输入",
        "SPLIT": "输出",
    }
    if upper in hardcoded:
        return hardcoded[upper]
    # Px style GPIO pins: bidirectional
    if re.match(r"^P\d+$", upper):
        return "双向"
    return "项目确认"


def _pin_function_cn(function: str) -> str:
    replacements = {
        "Interrupt open-drain output. Connect to VDD through a pull-up resistor": "中断开漏输出，需通过上拉电阻连接至 VDD",
        "Address input 1. Connect directly to VDD or ground": "地址输入 1，通常直接连接至 VDD 或 GND",
        "Address input 0. Connect directly to VDD or ground": "地址输入 0，通常直接连接至 VDD 或 GND",
        "Active-low reset input. Connect to VDD through a pull-up resistor": "低有效复位输入，需通过上拉电阻连接至 VDD",
        "Port 0 input/output. At power-on": "Port 0 输入/输出引脚，上电后默认配置为输入",
        "Port 1 input/output. At power-on": "Port 1 输入/输出引脚，上电后默认配置为输入",
        "Serial clock bus. Connect to VDD through a pull-up resistor": "I2C 串行时钟总线，需通过上拉电阻连接至 VDD",
        "Serial data bus. Connect to VDD through a pull-up resistor": "I2C 串行数据总线，需通过上拉电阻连接至 VDD",
    }
    for source, target in replacements.items():
        if function.startswith(source):
            return target
    return function
