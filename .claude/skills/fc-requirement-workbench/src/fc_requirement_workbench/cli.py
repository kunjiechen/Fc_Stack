"""CLI entry point — single planned SRS path + traceability outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .builder import RequirementBuilder
from .candidate_mapping import RequirementCandidateMapper, RequirementCandidateMarkdownRenderer
from .candidate_pruner import CandidatePruningMarkdownRenderer, RequirementCandidatePruner
from .feature_extraction import FeatureExtractionMarkdownRenderer, FeatureExtractor
from .parser import MarkdownStructureParser
from .raw_requirements import (
    RawInputLoader,
    RawRequirementCoverageAnalyzer,
    RawRequirementExtractor,
    RawRequirementMarkdownRenderer,
    RawRequirementSemanticConverter,
    merge_requirements,
    render_coverage_markdown,
    render_raw_coverage_matrix_markdown,
)
from .requirement_planner import RequirementPlanner, RequirementPlanningMarkdownRenderer
from .rules import ProjectConstraints, RequirementRuleEngine
from .schema import CoverageReport
from .srs import (
    DocxSrsRenderer,
    HtmlSrsRenderer,
    MarkdownSrsRenderer,
    SrsStructureGenerator,
)
from .traceability import (
    ChangeImpactAnalyzer,
    TraceabilityMarkdownRenderer,
    TraceabilityPipeline,
    load_trace_mapping,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate SRS requirements from datasheet markdown via planned SRS path."
    )
    parser.add_argument("input", type=Path, help="Markdown datasheet file")
    parser.add_argument("--module", default="FC", help="Module name used in requirement IDs")
    parser.add_argument(
        "--constraints",
        type=Path,
        help="Optional project constraint Markdown file for rule validation",
    )
    parser.add_argument(
        "--tests", type=Path, help="Optional verification/test trace mapping file"
    )
    parser.add_argument(
        "--raw-input",
        type=Path,
        help="Optional user raw requirement input file (dialog/txt for now).",
    )
    parser.add_argument(
        "--raw-input-type",
        choices=("auto", "dialog", "txt", "excel"),
        default="auto",
        help="Source type for --raw-input (default: auto).",
    )
    parser.add_argument(
        "--changed",
        default="",
        help="Comma-separated SRS requirement IDs for change impact analysis",
    )
    parser.add_argument(
        "--emit",
        choices=(
            "srs-markdown",
            "srs-html",
            "srs-docx",
            "features-markdown",
            "candidates-markdown",
            "pruning-markdown",
            "planning-markdown",
            "rawreq-markdown",
            "rawreq-json",
            "traceability-markdown",
            "traceability",
            "coverage",
            "raw-coverage",
            "verification",
            "aspice",
            "impact",
        ),
        default="srs-markdown",
        help="Output type (default: srs-markdown)",
    )
    parser.add_argument("--output", type=Path, help="Output file path")
    parser.add_argument(
        "--with-intermediates",
        action="store_true",
        help="Write intermediate Markdown artifacts. Disabled by default for faster SRS generation.",
    )
    parser.add_argument(
        "--intermediate-dir",
        type=Path,
        default=Path("artifacts/intermediate"),
        help="Directory for --with-intermediates outputs (default: artifacts/intermediate)",
    )
    args = parser.parse_args()

    # ---- Planned SRS pipeline (single path) ----
    parsed = MarkdownStructureParser().parse_file(args.input)
    features = FeatureExtractor(module=args.module).extract(parsed)
    if args.emit == "features-markdown":
        return _emit_text(
            FeatureExtractionMarkdownRenderer().render(features, args.module),
            args.output,
        )

    candidates = RequirementCandidateMapper(module=args.module).map(features)
    if args.emit == "candidates-markdown":
        return _emit_text(
            RequirementCandidateMarkdownRenderer().render(candidates, args.module),
            args.output,
        )

    pruning = RequirementCandidatePruner().prune(candidates)
    if args.emit == "pruning-markdown":
        return _emit_text(
            CandidatePruningMarkdownRenderer().render(pruning, args.module),
            args.output,
        )

    planning = RequirementPlanner(module=args.module).plan(pruning)
    if args.emit == "planning-markdown":
        return _emit_text(
            RequirementPlanningMarkdownRenderer().render(planning),
            args.output,
        )

    if args.with_intermediates:
        _write_intermediates(
            module=args.module,
            output_dir=args.intermediate_dir,
            features=features,
            candidates=candidates,
            pruning=pruning,
            planning=planning,
        )

    constraints = _load_constraints(args.constraints)
    raw_document = None
    raw_semantic_requirements = []
    if args.raw_input:
        raw_input = RawInputLoader().load(
            args.raw_input,
            source_type=args.raw_input_type,
        )
        raw_document = RawRequirementExtractor().extract(raw_input, module=args.module)
        raw_semantic_requirements = RawRequirementSemanticConverter().convert(raw_document)
        if args.emit == "rawreq-markdown":
            return _emit_text(
                RawRequirementMarkdownRenderer().render(raw_document),
                args.output,
            )
        if args.emit == "rawreq-json":
            payload = json.dumps(raw_document.to_dict(), ensure_ascii=False, indent=2)
            return _emit_text(payload + "\n", args.output)

    planned_requirements = merge_requirements(planning.requirements, raw_semantic_requirements)
    findings = RequirementRuleEngine().validate(planned_requirements, constraints)
    engineering = RequirementBuilder(module=args.module).build(
        planned_requirements, findings
    )
    srs_document = SrsStructureGenerator().build_document(
        engineering,
        module=args.module,
        findings=findings,
        overview=_overview_from_features(features, args.module),
    )

    # ---- SRS outputs ----
    if args.emit == "srs-markdown":
        return _emit_text(MarkdownSrsRenderer().render(srs_document), args.output)
    elif args.emit == "srs-html":
        return _emit_text(HtmlSrsRenderer().render(srs_document), args.output)
    elif args.emit == "srs-docx":
        out = args.output or Path("artifacts/doc/srs.docx")
        DocxSrsRenderer().render_to_file(srs_document, out)
        print(json.dumps({"output": str(out)}, ensure_ascii=False, indent=2))
        return 0

    # ---- Traceability (Phase 4) ----
    traceability = TraceabilityPipeline().build(
        engineering, tests=load_trace_mapping(args.tests)
    )
    raw_coverage_detail = (
        RawRequirementCoverageAnalyzer().build_detail(raw_document, engineering)
        if raw_document is not None
        else None
    )

    payload: dict[str, Any]
    if args.emit == "traceability-markdown":
        content = TraceabilityMarkdownRenderer().render(
            traceability,
            module=args.module,
            raw_document=raw_document,
            raw_coverage=raw_coverage_detail,
        )
        return _emit_text(content, args.output)
    if args.emit == "traceability":
        payload = {"trace_links": [item.to_dict() for item in traceability.trace_links]}
    elif args.emit == "coverage":
        payload = {"coverage": [item.to_dict() for item in traceability.coverage]}
    elif args.emit == "raw-coverage":
        report = raw_document and RawRequirementCoverageAnalyzer().analyze(
            raw_document, planned_requirements
        )
        if report is None:
            report = CoverageReport(
                total_user_reqs=0,
                covered=0,
                uncovered=[],
                coverage_rate=1.0,
                is_satisfied=True,
                gaps_detail="",
            )
        content = render_coverage_markdown(report, args.module)
        return _emit_text(content, args.output)
    elif args.emit == "verification":
        payload = {"verification": [item.to_dict() for item in traceability.verification]}
    elif args.emit == "aspice":
        payload = traceability.evidence.to_dict()
    elif args.emit == "impact":
        changed = [item.strip() for item in args.changed.split(",") if item.strip()]
        payload = {
            "impact": [
                item.to_dict()
                for item in ChangeImpactAnalyzer().analyze(
                    traceability.trace_links, changed
                )
            ]
        }
    else:
        payload = {}

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _load_constraints(path: Path | None) -> ProjectConstraints:
    if path is None:
        return ProjectConstraints()
    return ProjectConstraints.from_text(path.read_text(encoding="utf-8"))


def _emit_text(content: str, output: Path | None) -> int:
    if output is None:
        print(content, end="")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(json.dumps({"output": str(output)}, ensure_ascii=False, indent=2))
    return 0


def _write_intermediates(
    *,
    module: str,
    output_dir: Path,
    features: list[Any],
    candidates: list[Any],
    pruning: Any,
    planning: Any,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        f"{module} 特征提取中间文件.md": FeatureExtractionMarkdownRenderer().render(
            features, module
        ),
        f"{module} 需求候选映射中间文件.md": RequirementCandidateMarkdownRenderer().render(
            candidates, module
        ),
        f"{module} 候选需求压缩中间文件.md": CandidatePruningMarkdownRenderer().render(
            pruning, module
        ),
        f"{module} 需求规划中间文件.md": RequirementPlanningMarkdownRenderer().render(
            planning
        ),
    }
    for filename, content in artifacts.items():
        (output_dir / filename).write_text(content, encoding="utf-8")


def _overview_from_features(features: list[Any], module: str) -> dict[str, Any]:
    if not features:
        return {}
    groups = [f for f in features if getattr(f, "type", "") == "feature_group"]
    identity = next(
        (f for f in features if getattr(f, "type", "") == "identity"), None
    )
    pins = [f for f in features if getattr(f, "type", "") == "pin"]
    chip_intro = _chip_intro(identity, groups, module)
    pin_rows: list[tuple[str, str, str]] = [_pin_row(pin) for pin in pins[:32]]

    if module.upper() == "NCA9539":
        return _nca9539_overview(chip_intro, pin_rows)
    return _generic_overview(module, chip_intro, groups, pin_rows)


def _nca9539_overview(chip_intro: str, pin_rows: list[tuple[str, str, str]]) -> dict[str, Any]:
    return {
        "chip_intro": chip_intro,
        "chip_capabilities": [
            "支持 16 路 GPIO 扩展，每路可独立配置为输入或输出。",
            "支持输入状态读取、输出控制和输入极性反转。",
            "支持 GPIO 方向配置和寄存器访问。",
            "支持 INT 中断指示、RESET 复位和上电默认状态恢复。",
            "支持通过 A0/A1 配置器件地址，同一总线最多挂载 4 片器件。",
        ],
        "driver_functions": [
            "通过 I2C 总线读写芯片内部寄存器（Input、Output、Polarity Inversion、Configuration），实现对 16 路 GPIO 的软件控制。",
            "在初始化阶段加载项目配置表，设置每路 GPIO 的方向（输入/输出）、默认输出电平及极性反转策略。",
            "提供 GPIO 输入状态读取接口，按项目配置的 pin 或 port 粒度返回逻辑电平，支持极性反转后的逻辑值输出。",
            "提供 GPIO 输出控制接口，在写单路 pin 时通过读-改-写操作保持同 port 内其余 pin 的输出值不变。",
            "在 I2C 通信出现 NACK、timeout 或总线错误时，向上层返回明确的错误码，并支持故障状态读取。",
            "若项目使用 INT 引脚且接入 MCU，支持中断状态检测与清除。",
        ],
        "pin_rows": pin_rows or [("待确认", "待确认", "待提取")],
        "state_machine": None,
        "communication": {
            "bus_type": "I2C",
            "summary": (
                "NCA9539-Q1 通过 I2C 总线与主控制器通信，主控制器通过器件地址和命令字节访问内部寄存器。"
            ),
            "speed_modes": [
                "Standard-mode：最高 100 kHz",
                "Fast-mode：最高 400 kHz",
            ],
            "device_addressing": (
                "7-bit 从机地址高 5 位固定，低 2 位由 A1/A0 决定，可形成 4 种器件地址。"
            ),
            "timing_params": [
                {"name": "SCL 时钟频率", "symbol": "f_SCL", "condition": "Standard/Fast", "min": "0", "max": "400", "unit": "kHz"},
                {"name": "RESET 脉宽", "symbol": "t_w(rst)", "condition": "RESET", "min": "6", "max": "—", "unit": "ns"},
                {"name": "复位时长", "symbol": "t_rst", "condition": "RESET", "min": "400", "max": "—", "unit": "ns"},
            ],
        },
    }


def _generic_overview(
    module: str,
    chip_intro: str,
    groups: list[Any],
    pin_rows: list[tuple[str, str, str]],
) -> dict[str, Any]:
    functions = [_feature_summary(g) for g in groups[:12]]
    state_group = next((g for g in groups if _has_state_related_feature(g)), None)
    sm_data = None
    if state_group:
        sm_data = {
            "summary": (
                f"{_feature_summary(state_group)} 驱动需根据项目定义处理状态切换和恢复行为。"
            ),
            "diagram": "",
            "states": getattr(state_group, "states", []) if hasattr(state_group, "states") else [],
            "transitions": [],
        }
    return {
        "chip_intro": chip_intro,
        "chip_capabilities": [
            f"{_feature_summary(g)}" for g in groups[:5] if getattr(g, "name", "")
        ] or None,
        "driver_functions": (functions[:5] if functions else ["根据项目确认的软件责任生成驱动功能需求。"]),
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
    }


def _has_state_related_feature(feature: Any) -> bool:
    text = " ".join(
        [
            getattr(feature, "name", ""),
            getattr(feature, "feature_category", ""),
            getattr(feature, "functional_summary", ""),
        ]
    ).lower()
    return any(
        keyword in text
        for keyword in ("state machine", "transition", "mode switch", "operating mode")
    )


def _chip_intro(identity: Any, groups: list[Any], module: str) -> str:
    names = "、".join(
        _feature_name_cn(getattr(g, "name", "")) for g in groups[:8]
    )
    if module.upper() == "NCA9539":
        return (
            "NCA9539-Q1 是通过 I2C 总线访问的 16-bit GPIO 扩展器，适用于控制器 I/O 资源不足、"
            "需要扩展输入采样、输出控制或外部状态检测的应用场景。芯片提供 GPIO 输入读取、输出控制、"
            "输入极性反转、方向配置、中断指示、复位/上电默认状态以及寄存器访问能力。"
        )
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
    summary = getattr(feature, "functional_summary", "") or getattr(
        feature, "content", ""
    )
    if name:
        return f"{name}：{_summary_cn(summary)}"
    return _summary_cn(summary)


def _feature_name_cn(name: str) -> str:
    mapping = {
        "16-bit GPIO Port Capability": "16-bit GPIO 端口能力",
        "Input Port Function": "输入端口读取功能",
        "Output Port Function": "输出端口写入功能",
        "Polarity Inversion Function": "输入极性反转配置功能",
        "Direction Configuration Function": "GPIO 方向配置功能",
        "I2C Control Interface": "I2C 控制接口",
        "Register Map": "寄存器映射",
        "Interrupt and Diagnostic Signaling": "中断与诊断指示",
        "Reset and Default State": "复位与默认状态",
        "Timing Constraints": "时序约束",
        "Prohibited and Boundary Behavior": "禁止项与边界行为",
    }
    return mapping.get(name, name)


def _summary_cn(summary: str) -> str:
    replacements = {
        "The device exposes GPIO pins that can be organized into port-level input, output, polarity, and direction behaviors through the register map.": "芯片通过寄存器映射提供端口级输入、输出、极性和方向控制能力。",
        "Input port registers provide the software-visible state of GPIO pins configured or used as inputs.": "输入端口寄存器提供 GPIO 输入状态的软件可见视图。",
        "Output port registers define the commanded output level for GPIO pins used as outputs.": "输出端口寄存器定义作为输出使用的 GPIO 输出命令值。",
        "Polarity inversion registers define whether input values are logically inverted before software interpretation.": "极性反转寄存器定义输入值在软件解释前是否进行逻辑反转。",
        "Configuration registers define whether each GPIO bit behaves as input or output.": "配置寄存器定义每个 GPIO bit 的输入/输出方向。",
        "The device is accessed through an I2C control interface using bus pins, address selection, and register read/write transactions.": "芯片通过 I2C 总线、地址选择和寄存器读写事务进行访问。",
        "The register map provides the data model for input sampling, output control, polarity inversion, and direction configuration.": "寄存器映射为输入采样、输出控制、极性反转和方向配置提供数据模型。",
        "Diagnostic or interrupt-related signals provide software-observable status only when the project connects and uses the relevant pins or flags.": "只有项目连接并使用相关引脚或标志时，中断/诊断信号才形成软件可观测状态。",
        "Power-on or reset behavior defines default register and pin state that the driver may need to account for during initialization.": "上电或复位行为定义驱动初始化时需要考虑的默认寄存器和引脚状态。",
        "Timing values constrain bus access, reset handling, signal stabilization, or verification timing.": "时序值约束总线访问、复位处理、信号稳定或验证时机。",
        "Reserved, invalid, unsupported, or cautionary statements define boundaries that may require rejection behavior or project exclusions.": "保留、非法、不支持或警示类描述定义边界行为；只有存在软件输入路径时才生成拒绝或异常处理需求。",
    }
    return replacements.get(summary, summary)


def _pin_row(pin: Any) -> tuple[str, str, str]:
    name = getattr(pin, "name", "")
    content = getattr(pin, "content", "")
    direction = "待确认"
    function = content
    lowered = content.lower()
    for candidate in ("input", "output", "bidirectional"):
        if lowered.startswith(candidate):
            direction = {"input": "输入", "output": "输出", "bidirectional": "双向"}[candidate]
            function = content.split(".", 1)[1].strip() if "." in content else content
            break
    if direction == "待确认":
        direction = _pin_direction(name)
    function = _pin_function_cn(function)
    return (name, direction, function or "待提取")


def _pin_direction(name: str) -> str:
    upper = name.upper()
    if upper == "INT":
        return "输出"
    if upper in {"A0", "A1", "RESET"}:
        return "输入"
    if upper == "SCL":
        return "输入"
    if upper == "SDA" or upper.startswith("P"):
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


if __name__ == "__main__":
    raise SystemExit(main())
