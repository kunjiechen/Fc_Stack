"""CLI entry point — single planned SRS path + traceability outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import pickle
from typing import Any

from .bundle import (
    RequirementBundleBuilder,
    render_architecture_seed_yaml,
    render_bundle_json,
    render_bundle_yaml,
    render_test_seed_yaml,
)
from .bundle_validation import build_validation_report
from .builder import EngineeringRequirement, RequirementBuilder
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
        "--source-root",
        type=Path,
        help="Optional project source root used as implemented evidence for bundle export.",
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
            "requirement-bundle",
            "requirement-bundle-json",
            "architecture-seed",
            "test-seed",
            "bundle-validation",
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
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(".cache/fc_requirement_workbench"),
        help="Directory for parser/extraction/planning cache files.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable local cache reuse for parser/extraction/planning stages.",
    )
    args = parser.parse_args()
    cache_dir = args.cache_dir
    use_cache = not args.no_cache

    # ---- Planned SRS pipeline (single path) ----
    parsed = _cached_stage(
        cache_dir,
        "parsed",
        _cache_key(args.input, args.module, "parsed"),
        lambda: MarkdownStructureParser().parse_file(args.input),
        enabled=use_cache,
    )
    features = _cached_stage(
        cache_dir,
        "features",
        _cache_key(args.input, args.module, "features"),
        lambda: FeatureExtractor(module=args.module).extract(parsed),
        enabled=use_cache,
    )
    if args.emit == "features-markdown":
        return _emit_text(
            FeatureExtractionMarkdownRenderer().render(features, args.module),
            args.output,
        )

    candidates = _cached_stage(
        cache_dir,
        "candidates",
        _cache_key(args.input, args.module, "candidates"),
        lambda: RequirementCandidateMapper(module=args.module).map(features),
        enabled=use_cache,
    )
    if args.emit == "candidates-markdown":
        return _emit_text(
            RequirementCandidateMarkdownRenderer().render(candidates, args.module),
            args.output,
        )

    pruning = _cached_stage(
        cache_dir,
        "pruning",
        _cache_key(args.input, args.module, "pruning"),
        lambda: RequirementCandidatePruner().prune(candidates),
        enabled=use_cache,
    )
    if args.emit == "pruning-markdown":
        return _emit_text(
            CandidatePruningMarkdownRenderer().render(pruning, args.module),
            args.output,
        )

    planning = _cached_stage(
        cache_dir,
        "planning",
        _cache_key(args.input, args.module, "planning"),
        lambda: RequirementPlanner(module=args.module).plan(pruning),
        enabled=use_cache,
    )
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

    builder_module = (raw_document.module_name if raw_document and raw_document.module_name else args.module)
    safety_level = raw_document.safety_level if raw_document else "QM"
    engineering = RequirementBuilder(module=builder_module).build(
        planned_requirements, findings
    )
    engineering = _enrich_engineering_requirements(
        engineering,
        module=builder_module,
        raw_document=raw_document,
    )
    srs_document = SrsStructureGenerator().build_document(
        engineering,
        module=builder_module,
        findings=findings,
        overview=_overview_from_features(features, builder_module, safety_level),
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
    requirement_bundle = RequirementBundleBuilder().build(
        module=builder_module,
        input_document=str(args.input),
        engineering_requirements=engineering,
        findings=findings,
        traceability=traceability,
        raw_document=raw_document,
        raw_coverage_detail=raw_coverage_detail,
        source_root=args.source_root,
    )

    payload: dict[str, Any]
    if args.emit == "requirement-bundle":
        return _emit_text(render_bundle_yaml(requirement_bundle), args.output)
    if args.emit == "requirement-bundle-json":
        return _emit_text(render_bundle_json(requirement_bundle), args.output)
    if args.emit == "architecture-seed":
        return _emit_text(render_architecture_seed_yaml(requirement_bundle), args.output)
    if args.emit == "test-seed":
        return _emit_text(render_test_seed_yaml(requirement_bundle), args.output)
    if args.emit == "bundle-validation":
        payload = build_validation_report(requirement_bundle.to_dict())
        return _emit_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", args.output)
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


def _enrich_engineering_requirements(
    requirements: list[EngineeringRequirement],
    *,
    module: str,
    raw_document: Any | None,
) -> list[EngineeringRequirement]:
    enriched = list(requirements)
    text = " ".join(
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
    raw_text = ""
    if raw_document is not None:
        raw_items = (
            list(raw_document.functional_reqs)
            + list(raw_document.interface_reqs)
            + list(raw_document.config_reqs)
            + list(raw_document.nfr_reqs)
        )
        raw_text = " ".join(f"{item.title} {item.description}" for item in raw_items).lower()
    token = _normalize_module_token(module)

    if "det" not in text and "开发错误" not in text and ("det" in raw_text or "参数有效性检查" in raw_text):
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

    has_pwm_signal = any(token_text in raw_text for token_text in ("pwm", "占空比", "周期")) or any(
        token_text in text for token_text in ("pwm", "占空比", "周期", "sethboutsig")
    )
    has_pwm_dependency = ("setduty" in text) or ("getduty" in text)
    if has_pwm_signal and not has_pwm_dependency:
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

    has_spi_signal = ("spi" in raw_text) or ("spi" in text)
    has_spi_dependency = any(token_text in text for token_text in ("spi dependency", "spi communication dependency", "spi服务", "spi 服务依赖"))
    if has_spi_signal and not has_spi_dependency:
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

    if raw_document is not None:
        capability_texts = [
            f"{item.title} {item.description}".lower()
            for item in list(raw_document.functional_reqs) + list(raw_document.config_reqs)
            if getattr(item, "disposition", "") == "capability"
        ]
        if any("极性反转" in text_item for text_item in capability_texts) and "极性反转" not in text:
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
        if any(("故障清除" in text_item) or ("看门狗" in text_item) for text_item in capability_texts) and "故障清除" not in text and "看门狗" not in text:
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

    return enriched


def _normalize_module_token(module: str) -> str:
    return "".join(ch for ch in module.upper() if ch.isalnum()) or "FC"


def _cache_key(input_path: Path, module: str, stage: str) -> str:
    stat = input_path.stat()
    raw = f"{input_path.resolve()}::{module}::{stage}::{stat.st_mtime_ns}::{stat.st_size}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _cached_stage(
    cache_dir: Path,
    stage: str,
    key: str,
    producer: Any,
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


def _overview_from_features(features: list[Any], module: str, safety_level: str = "QM") -> dict[str, Any]:
    if not features:
        return {"safety_level": safety_level}
    groups = [f for f in features if getattr(f, "type", "") == "feature_group"]
    identity = next(
        (f for f in features if getattr(f, "type", "") == "identity"), None
    )
    pins = [f for f in features if getattr(f, "type", "") == "pin"]
    chip_intro = _chip_intro(identity, groups, module)
    pin_rows: list[tuple[str, str, str]] = [_pin_row(pin) for pin in pins[:32]]

    return _generic_overview(module, chip_intro, groups, pin_rows, safety_level)


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
    return any(
        keyword in text
        for keyword in ("state machine", "transition", "mode switch", "operating mode")
    )


def _chip_intro(identity: Any, groups: list[Any], module: str) -> str:
    names = "、".join(
        _feature_name_cn(getattr(g, "name", "")) for g in groups[:8]
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
