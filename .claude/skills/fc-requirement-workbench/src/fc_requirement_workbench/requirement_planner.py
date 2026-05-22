"""Requirement planning layer for author-quality SRS generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .candidate_pruner import CandidatePruningResult, RequiredInputItem
from .schema import (
    ConfigurationRequirementObject,
    FunctionalRequirementObject,
    InterfaceRequirementObject,
    RequirementObject,
    SourceRef,
    StateRequirementObject,
    TimingRequirementObject,
)


@dataclass(frozen=True)
class RequirementPlanItem:
    domain: str
    include_in_srs: str
    planned_requirements: list[str] = field(default_factory=list)
    merge_strategy: str = ""
    authoring_strategy: str = ""
    verification_strategy: str = ""
    missing_inputs: list[str] = field(default_factory=list)
    source_candidates: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RequirementPlanningResult:
    module: str
    plan_items: list[RequirementPlanItem]
    requirements: list[RequirementObject]
    required_inputs: list[RequiredInputItem]

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "plan_items": [item.to_dict() for item in self.plan_items],
            "requirements": [requirement.to_dict() for requirement in self.requirements],
            "required_inputs": [item.to_dict() for item in self.required_inputs],
        }


class RequirementPlanner:
    """Plan a compact set of SRS requirements from pruned candidates."""

    def __init__(self, module: str = "FC") -> None:
        self.module = _module_token(module)

    def plan(self, pruning: CandidatePruningResult | None) -> RequirementPlanningResult:
        required_inputs = pruning.required_inputs if pruning else []
        candidates = pruning.retained_candidates if pruning else []
        by_family = _candidate_index(candidates)

        items = _nca9539_plan_items(by_family) if self.module == "NCA9539" else _generic_plan_items(by_family)
        requirements = _nca9539_requirements(self.module, by_family) if self.module == "NCA9539" else _generic_requirements(self.module, items)
        return RequirementPlanningResult(
            module=self.module,
            plan_items=items,
            requirements=requirements,
            required_inputs=required_inputs,
        )


class RequirementPlanningMarkdownRenderer:
    def render(self, result: RequirementPlanningResult) -> str:
        lines = [
            f"# Requirement Planning - {result.module}",
            "",
            "## Strategy",
            "",
            "- 本阶段从需求制定者角度规划 SRS，不直接照搬候选需求。",
            "- 先定义驱动能力域，再决定每个能力域进入 SRS 的条目数量、合并策略和验证策略。",
            "- SRS 正文不得出现候选、证据等级、映射过程等中间态内容。",
            "- 当项目输入不足时，规划项保留缺失输入，SRS 条目状态保持 Open Issue。",
            "",
            "## Planning Matrix",
            "",
            "| 能力域 | 是否进入 SRS | 规划需求 | 合并策略 | 编写策略 | 验证策略 | 缺失输入 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for item in result.plan_items:
            lines.append(
                "| "
                + " | ".join(
                    _escape(value)
                    for value in (
                        item.domain,
                        item.include_in_srs,
                        "; ".join(item.planned_requirements),
                        item.merge_strategy,
                        item.authoring_strategy,
                        item.verification_strategy,
                        "; ".join(item.missing_inputs),
                    )
                )
                + " |"
            )

        lines.extend(["", "## Planned SRS Requirement Objects", ""])
        lines.extend(["| ID | Type | Name | Description |", "| --- | --- | --- | --- |"])
        for requirement in result.requirements:
            data = requirement.to_dict()
            name = data.get("name") or data.get("interface_name") or data.get("config_name") or data.get("state_name") or data.get("constraint", "")
            description = data.get("description") or data.get("dependency") or data.get("constraint", "")
            lines.append(
                "| "
                + " | ".join(
                    _escape(value)
                    for value in (
                        data.get("id", ""),
                        data.get("type", ""),
                        name,
                        description,
                    )
                )
                + " |"
            )

        lines.extend(["", "## Required Inputs for Ready SRS", ""])
        lines.extend(["| 缺失项 | 影响候选 | 影响类别 | 建议提供方 | 示例 |", "| --- | --- | --- | --- | --- |"])
        for item in result.required_inputs:
            lines.append(
                "| "
                + " | ".join(
                    _escape(value)
                    for value in (
                        item.missing_input,
                        "; ".join(item.affected_candidates),
                        "; ".join(item.affected_types),
                        item.owner_hint,
                        item.example,
                    )
                )
                + " |"
            )
        lines.append("")
        return "\n".join(lines).rstrip() + "\n"


def _nca9539_plan_items(by_family: dict[str, list[str]]) -> list[RequirementPlanItem]:
    return [
        RequirementPlanItem(
            domain="驱动初始化接口",
            include_in_srs="是",
            planned_requirements=["1 条接口需求"],
            merge_strategy="初始化接口为驱动基本入口，独立生成；不与 MainFunction 或运行时读写接口合并。",
            authoring_strategy="描述初始化配置加载、默认寄存器恢复和初始化失败返回。",
            verification_strategy="通过默认配置加载、I2C 初始化失败、重复初始化和非法配置测试验证。",
            missing_inputs=["初始化 API 命名", "配置来源", "默认方向表", "初始化失败返回语义"],
            source_candidates=[*by_family.get("gpio_direction", []), *by_family.get("reset_default", [])],
        ),
        RequirementPlanItem(
            domain="GPIO 输入采样",
            include_in_srs="是",
            planned_requirements=["1 条功能需求", "1 条接口需求"],
            merge_strategy="合并 pin/port 输入读取能力，项目确认接口粒度。",
            authoring_strategy="描述驱动读取输入寄存器、按配置解释极性并返回输入状态。",
            verification_strategy="模拟输入寄存器值，验证 port/pin 读取结果、非法参数返回和极性反转结果。",
            missing_inputs=["输入 pin 使用范围", "读取接口粒度", "极性转换策略", "错误返回语义"],
            source_candidates=by_family.get("gpio_input_read", []),
        ),
        RequirementPlanItem(
            domain="GPIO 输出控制",
            include_in_srs="是",
            planned_requirements=["1 条功能需求", "1 条接口需求"],
            merge_strategy="合并 pin/port 输出写入能力，项目确认是否需要读改写缓存。",
            authoring_strategy="描述驱动写输出寄存器、保持未目标 bit 不被破坏并处理写失败。",
            verification_strategy="写入输出寄存器并读回或观测输出状态，验证 bit mask、非法方向和 I2C 失败路径。",
            missing_inputs=["输出 pin 使用范围", "默认输出电平", "缓存/读改写策略", "写失败处理"],
            source_candidates=by_family.get("gpio_output_write", []),
        ),
        RequirementPlanItem(
            domain="GPIO 方向与极性配置",
            include_in_srs="是",
            planned_requirements=["2 条配置需求", "1 条状态需求"],
            merge_strategy="方向配置和极性配置分别成条，运行时变更作为项目策略。",
            authoring_strategy="描述默认方向、默认极性、运行时变更权限和非法组合处理。",
            verification_strategy="检查初始化配置值，变更方向/极性后验证读写行为和拒绝策略。",
            missing_inputs=["默认方向表", "默认极性", "是否允许运行时方向切换", "是否使用极性反转"],
            source_candidates=[*by_family.get("gpio_direction", []), *by_family.get("gpio_polarity", [])],
        ),
        RequirementPlanItem(
            domain="I2C 寄存器访问",
            include_in_srs="是",
            planned_requirements=["1 条功能约束", "1 条接口/依赖需求"],
            merge_strategy="寄存器读写不直接铺开为大量 SRS 条目，作为底层访问约束统一描述。",
            authoring_strategy="描述驱动通过 I2C 访问寄存器、处理 NACK/timeout/bus error 并保持状态一致。",
            verification_strategy="注入 I2C 正常返回、NACK、timeout、总线错误，验证返回值和内部状态。",
            missing_inputs=["底层 I2C API", "设备地址配置来源", "NACK/timeout 返回语义", "同步/异步策略"],
            source_candidates=by_family.get("register_access", []),
        ),
        RequirementPlanItem(
            domain="中断、复位与异常处理",
            include_in_srs="项目确认后进入",
            planned_requirements=["1 条状态需求", "1 条异常/诊断需求"],
            merge_strategy="INT 与 RESET 不直接生成多个接口，先确认硬件连接和驱动所有权。",
            authoring_strategy="描述中断状态读取/清除、复位后重新初始化和非法输入拒绝。",
            verification_strategy="模拟 INT、RESET、非法参数和通信失败场景，验证状态恢复和错误返回。",
            missing_inputs=["INT 是否连接 MCU", "RESET 所有权", "中断清除条件", "复位后是否自动重新初始化", "是否需要诊断上报"],
            source_candidates=[*by_family.get("interrupt_diagnostic", []), *by_family.get("reset_default", []), *by_family.get("invalid_rejection", [])],
        ),
        RequirementPlanItem(
            domain="周期调度接口",
            include_in_srs="存在异步接口时生成",
            planned_requirements=["存在异步接口时生成 1 条 MainFunction 接口需求"],
            merge_strategy="只要存在异步接口、异步轮询、周期采样、超时推进或诊断轮询，即规划 MainFunction；纯同步/直接读写服务可不生成。",
            authoring_strategy="描述 MainFunction 周期触发、异步状态推进、超时处理、诊断轮询和无阻塞要求。",
            verification_strategy="通过异步请求、周期调度、超时推进和诊断轮询场景验证。",
            missing_inputs=["是否存在异步接口", "MainFunction 调用周期", "异步状态机推进策略", "超时处理策略"],
            source_candidates=[],
        ),
        RequirementPlanItem(
            domain="时序与资源约束",
            include_in_srs="是",
            planned_requirements=["1 条时序需求", "默认安全/编码/资源需求"],
            merge_strategy="时序要求只保留软件需要等待、超时或采样保护的内容。",
            authoring_strategy="描述 I2C 访问、复位恢复和状态采样相关的等待/超时策略。",
            verification_strategy="通过时序分析、超时注入和集成测试验证等待/超时处理。",
            missing_inputs=["软件是否负责等待", "超时值策略", "测试测量点", "资源预算"],
            source_candidates=by_family.get("timing_guard", []),
        ),
    ]


def _nca9539_requirements(module: str, by_family: dict[str, list[str]]) -> list[RequirementObject]:
    source = _source("PLAN-NCA9539")
    return [
        InterfaceRequirementObject(
            id=f"REQ-{module}-IF-0001",
            type="interface",
            interface_name="初始化接口",
            direction="input",
            dependency="接口应加载项目配置、设置 GPIO 默认方向/输出/极性、建立 I2C 访问上下文，并在配置非法或底层访问失败时返回错误。",
            evidence="验证：默认配置加载、非法配置、I2C 初始化失败和重复初始化。",
            source=[source],
        ),
        FunctionalRequirementObject(
            id=f"REQ-{module}-FUNC-0001",
            type="functional",
            name="GPIO 输入采样",
            description="软件应能够读取 NCA9539 输入寄存器，并按照项目配置的 pin/port 范围和极性策略返回 GPIO 输入状态。",
            inputs=["目标 pin 或 port", "输入寄存器值", "极性配置"],
            outputs=["GPIO 输入状态", "错误返回"],
            constraints=["需确认：输入 pin 使用范围；读取接口粒度；极性转换策略；错误返回语义"],
            source=[source],
        ),
        FunctionalRequirementObject(
            id=f"REQ-{module}-FUNC-0002",
            type="functional",
            name="GPIO 输出控制",
            description="软件应能够设置 NCA9539 输出寄存器，并在写入单个 pin 时保持同一 port 内其他 bit 的输出命令值不被改变。",
            inputs=["目标 pin 或 port", "输出电平", "方向配置"],
            outputs=["写入结果", "错误返回"],
            constraints=["需确认：输出 pin 使用范围；默认输出电平；缓存/读改写策略；写失败处理"],
            source=[source],
        ),
        FunctionalRequirementObject(
            id=f"REQ-{module}-FUNC-0003",
            type="functional",
            name="GPIO 极性处理",
            description="软件应在项目启用输入极性反转时，按照极性配置返回逻辑处理后的输入值。",
            inputs=["输入寄存器值", "极性配置"],
            outputs=["逻辑输入状态"],
            constraints=["需确认：项目是否使用极性反转；默认极性；运行时修改策略"],
            source=[source],
        ),
        FunctionalRequirementObject(
            id=f"REQ-{module}-FUNC-0004",
            type="functional",
            name="I2C 寄存器访问",
            description="软件应通过项目指定的 I2C 访问接口读写 NCA9539 寄存器，并在 NACK、timeout 或总线错误时返回失败且保持驱动内部状态一致。",
            inputs=["设备地址", "寄存器地址", "读写数据"],
            outputs=["读写结果", "错误返回"],
            constraints=["需确认：底层 I2C API；设备地址配置来源；NACK/timeout 返回语义；同步/异步策略"],
            source=[source],
        ),
        InterfaceRequirementObject(
            id=f"REQ-{module}-IF-0002",
            type="interface",
            interface_name="GPIO 输入读取接口",
            direction="output",
            dependency="接口应支持项目定义的 pin/port 粒度，并对非法 pin、非法 port 或未配置输入方向返回错误。",
            evidence="验证：模拟输入寄存器、极性配置和非法参数，检查返回状态与错误码。",
            source=[source],
        ),
        InterfaceRequirementObject(
            id=f"REQ-{module}-IF-0003",
            type="interface",
            interface_name="GPIO 输出写入接口",
            direction="input",
            dependency="接口应支持项目定义的 pin/port 粒度，并对非法 pin、非法 port、未配置输出方向或 I2C 写失败返回错误。",
            evidence="验证：写输出寄存器、检查读改写行为、非法方向和 I2C 失败路径。",
            source=[source],
        ),
        InterfaceRequirementObject(
            id=f"REQ-{module}-IF-0004",
            type="interface",
            interface_name="GPIO 配置接口",
            direction="input",
            dependency="接口应支持项目允许的方向配置和极性配置，禁止未授权的运行时方向或极性变更。",
            evidence="验证：初始化配置、运行时配置变更、非法配置组合和错误返回。",
            source=[source],
        ),
        ConfigurationRequirementObject(
            id=f"REQ-{module}-CFG-0001",
            type="configuration",
            config_name="GPIO 默认配置",
            range="pin/port 使用范围、默认方向、默认输出电平、默认极性",
            default="上电后 GPIO 默认为输入；项目默认值需配置确认",
            dependency="需确认：项目 GPIO 使用清单、默认方向表、默认输出值、默认极性。",
            source=[source],
        ),
        ConfigurationRequirementObject(
            id=f"REQ-{module}-CFG-0002",
            type="configuration",
            config_name="I2C 地址与访问配置",
            range="设备地址、I2C 通道、访问超时、错误返回策略",
            default="需项目配置确认",
            dependency="需确认：A0/A1 硬件连接、设备地址来源、底层 I2C 访问接口和超时策略。",
            source=[source],
        ),
        StateRequirementObject(
            id=f"REQ-{module}-STATE-0001",
            type="state",
            state_name="初始化与运行状态",
            transition=["Uninit -> Initialized", "Initialized -> Running", "Running -> Error", "Error -> Reinitialized"],
            dependency=["需确认：初始化顺序、复位后是否自动重新初始化、错误恢复策略。"],
            source=[source],
        ),
        StateRequirementObject(
            id=f"REQ-{module}-STATE-0002",
            type="state",
            state_name="中断与复位处理状态",
            transition=["Running -> InterruptPending", "InterruptPending -> Running", "Running -> ResetDetected", "ResetDetected -> Reinitialized"],
            dependency=["需确认：INT 是否连接 MCU、RESET 所有权、中断清除条件、复位检测方式。"],
            source=[source],
        ),
        TimingRequirementObject(
            id=f"REQ-{module}-TIME-0001",
            type="timing",
            constraint="软件应对 I2C 访问、复位恢复和状态采样设置项目定义的等待、超时或重试策略。",
            minimum="",
            maximum="",
            source=[source],
        ),
    ]


def _generic_plan_items(by_family: dict[str, list[str]]) -> list[RequirementPlanItem]:
    return [
        RequirementPlanItem(
            domain=family,
            include_in_srs="是",
            planned_requirements=["按能力域规划需求"],
            merge_strategy="合并同族候选，保留可验证的软件行为。",
            authoring_strategy="按条件、行为、边界、异常和验证方法编写。",
            verification_strategy="按输入输出和异常路径设计评审/测试验证。",
            source_candidates=candidates,
        )
        for family, candidates in sorted(by_family.items())
    ]


def _generic_requirements(module: str, items: list[RequirementPlanItem]) -> list[RequirementObject]:
    source = _source("PLAN-GENERIC")
    result: list[RequirementObject] = []
    for index, item in enumerate(items, start=1):
        result.append(
            FunctionalRequirementObject(
                id=f"REQ-{module}-FUNC-{index:04d}",
                type="functional",
                name=item.domain,
                description=f"软件应实现 {item.domain} 相关行为，并定义输入、输出、边界条件和异常处理。",
                constraints=["需确认：项目使用范围、接口粒度、错误返回语义和验证方法"],
                source=[source],
            )
        )
    return result


def _candidate_index(candidates: list[Any]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for candidate in candidates:
        family = _family(candidate)
        result.setdefault(family, []).append(candidate.candidate_id)
    return result


def _family(candidate: Any) -> str:
    text = f"{candidate.source_feature} {candidate.source_subfunction}".lower()
    if "polarity" in text or "inversion" in text:
        return "gpio_polarity"
    if "direction" in text or "configuration" in text:
        return "gpio_direction"
    if "output" in text and ("write" in text or "port" in text or "pin" in text):
        return "gpio_output_write"
    if "input" in text and ("read" in text or "port" in text or "pin" in text):
        return "gpio_input_read"
    if "i2c" in text or "register" in text:
        return "register_access"
    if "interrupt" in text or "diagnostic" in text:
        return "interrupt_diagnostic"
    if "reset" in text or "power-on" in text:
        return "reset_default"
    if "timing" in text or "timeout" in text or "wait" in text:
        return "timing_guard"
    if "invalid" in text or "reserved" in text or "unsupported" in text:
        return "invalid_rejection"
    return "other"


def _source(chunk_id: str) -> SourceRef:
    return SourceRef(
        document="RequirementPlan",
        chunk_id=chunk_id,
        heading_path=["Requirement Planning"],
        content_type="planning",
        evidence="Planned from feature and candidate intermediate artifacts.",
    )


def _module_token(value: str) -> str:
    token = "".join(ch for ch in value.upper() if ch.isalnum())
    return token or "FC"


def _escape(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")
