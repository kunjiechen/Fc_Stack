from __future__ import annotations

from typing import Any

from ..schema import (
    ConfigurationRequirementObject,
    FunctionalRequirementObject,
    InterfaceRequirementObject,
    SourceRef,
    TimingRequirementObject,
)


def build_chip_intro() -> str:
    return (
        "NCA9539-Q1 是通过 I2C 总线访问的 16-bit GPIO 扩展器，适用于控制器 I/O 资源不足、"
        "需要扩展输入采样、输出控制或外部状态检测的应用场景。芯片提供 GPIO 输入读取、输出控制、"
        "输入极性反转、方向配置、中断指示、复位/上电默认状态以及寄存器访问能力。"
    )


def build_overview(
    chip_intro: str,
    pin_rows: list[tuple[str, str, str]],
) -> dict[str, Any]:
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
            "summary": "NCA9539-Q1 通过 I2C 总线与主控制器通信，主控制器通过器件地址和命令字节访问内部寄存器。",
            "speed_modes": [
                "Standard-mode：最高 100 kHz",
                "Fast-mode：最高 400 kHz",
            ],
            "device_addressing": "7-bit 从机地址高 5 位固定，低 2 位由 A1/A0 决定，可形成 4 种器件地址。",
            "timing_params": [
                {"name": "SCL 时钟频率", "symbol": "f_SCL", "condition": "Standard/Fast", "min": "0", "max": "400", "unit": "kHz"},
                {"name": "RESET 脉宽", "symbol": "t_w(rst)", "condition": "RESET", "min": "6", "max": "—", "unit": "ns"},
                {"name": "复位时长", "symbol": "t_rst", "condition": "RESET", "min": "400", "max": "—", "unit": "ns"},
            ],
        },
    }


def build_plan_item_specs(by_family: dict[str, list[str]]) -> list[dict[str, Any]]:
    return [
        {
            "domain": "驱动初始化接口",
            "include_in_srs": "是",
            "planned_requirements": ["1 条接口需求"],
            "merge_strategy": "初始化接口为驱动基本入口，独立生成；不与 MainFunction 或运行时读写接口合并。",
            "authoring_strategy": "描述初始化配置加载、默认寄存器恢复和初始化失败返回。",
            "verification_strategy": "通过默认配置加载、I2C 初始化失败、重复初始化和非法配置测试验证。",
            "missing_inputs": ["初始化 API 命名", "配置来源", "默认方向表", "初始化失败返回语义"],
            "source_candidates": [*by_family.get("gpio_direction", []), *by_family.get("reset_default", [])],
        },
        {
            "domain": "GPIO 输入采样",
            "include_in_srs": "是",
            "planned_requirements": ["1 条功能需求", "1 条接口需求"],
            "merge_strategy": "合并 pin/port 输入读取能力，项目确认接口粒度。",
            "authoring_strategy": "描述驱动读取输入寄存器、按配置解释极性并返回输入状态。",
            "verification_strategy": "模拟输入寄存器值，验证 port/pin 读取结果、非法参数返回和极性反转结果。",
            "missing_inputs": ["输入 pin 使用范围", "读取接口粒度", "极性转换策略", "错误返回语义"],
            "source_candidates": by_family.get("gpio_input_read", []),
        },
        {
            "domain": "GPIO 输出控制",
            "include_in_srs": "是",
            "planned_requirements": ["1 条功能需求", "1 条接口需求"],
            "merge_strategy": "合并 pin/port 输出写入能力，项目确认是否需要读改写缓存。",
            "authoring_strategy": "描述驱动写输出寄存器、保持未目标 bit 不被破坏并处理写失败。",
            "verification_strategy": "写入输出寄存器并读回或观测输出状态，验证 bit mask、非法方向和 I2C 失败路径。",
            "missing_inputs": ["输出 pin 使用范围", "默认输出电平", "缓存/读改写策略", "写失败处理"],
            "source_candidates": by_family.get("gpio_output_write", []),
        },
        {
            "domain": "GPIO 方向与极性配置",
            "include_in_srs": "是",
            "planned_requirements": ["2 条配置需求"],
            "merge_strategy": "方向配置和极性配置分别成条；无复杂模式切换时不单独生成状态章节。",
            "authoring_strategy": "描述默认方向、默认极性、运行时变更权限和非法组合处理。",
            "verification_strategy": "检查初始化配置值，变更方向/极性后验证读写行为和拒绝策略。",
            "missing_inputs": ["默认方向表", "默认极性", "是否允许运行时方向切换", "是否使用极性反转"],
            "source_candidates": [*by_family.get("gpio_direction", []), *by_family.get("gpio_polarity", [])],
        },
        {
            "domain": "I2C 寄存器访问",
            "include_in_srs": "是",
            "planned_requirements": ["1 条功能约束", "1 条接口/依赖需求"],
            "merge_strategy": "寄存器读写不直接铺开为大量 SRS 条目，作为底层访问约束统一描述。",
            "authoring_strategy": "描述驱动通过 I2C 访问寄存器、处理 NACK/timeout/bus error 并保持状态一致。",
            "verification_strategy": "注入 I2C 正常返回、NACK、timeout、总线错误，验证返回值和内部状态。",
            "missing_inputs": ["底层 I2C API", "设备地址配置来源", "NACK/timeout 返回语义", "同步/异步策略"],
            "source_candidates": by_family.get("register_access", []),
        },
        {
            "domain": "中断、复位与异常处理",
            "include_in_srs": "项目确认后进入",
            "planned_requirements": ["1 条中断状态接口需求", "1 条故障诊断读取接口需求", "1 条异常/诊断需求", "1 条复位接口需求"],
            "merge_strategy": "INT、故障读取和 RESET 按外部可见能力拆分；无复杂状态跳转时不单独生成状态机需求。",
            "authoring_strategy": "描述中断状态读取/清除、故障诊断状态读取、复位后重新初始化和非法输入拒绝。",
            "verification_strategy": "模拟 INT、RESET、非法参数、通信失败和故障恢复场景，验证状态读取与错误返回。",
            "missing_inputs": ["INT 是否连接 MCU", "RESET 所有权", "中断清除条件", "复位后是否自动重新初始化", "是否需要诊断上报"],
            "source_candidates": [*by_family.get("interrupt_diagnostic", []), *by_family.get("reset_default", []), *by_family.get("invalid_rejection", [])],
        },
        {
            "domain": "周期调度接口",
            "include_in_srs": "存在异步接口时生成",
            "planned_requirements": ["存在异步接口时生成 1 条 MainFunction 接口需求"],
            "merge_strategy": "只要存在异步接口、异步轮询、周期采样、超时推进或诊断轮询，即规划 MainFunction；纯同步/直接读写服务可不生成。",
            "authoring_strategy": "描述 MainFunction 周期触发、异步状态推进、超时处理、诊断轮询和无阻塞要求。",
            "verification_strategy": "通过异步请求、周期调度、超时推进和诊断轮询场景验证。",
            "missing_inputs": ["是否存在异步接口", "MainFunction 调用周期", "异步状态机推进策略", "超时处理策略"],
            "source_candidates": [],
        },
        {
            "domain": "时序与资源约束",
            "include_in_srs": "是",
            "planned_requirements": ["1 条时序需求", "默认安全/编码/资源需求"],
            "merge_strategy": "时序要求只保留软件需要等待、超时或采样保护的内容。",
            "authoring_strategy": "描述 I2C 访问、复位恢复和状态采样相关的等待/超时策略。",
            "verification_strategy": "通过时序分析、超时注入和集成测试验证等待/超时处理。",
            "missing_inputs": ["软件是否负责等待", "超时值策略", "测试测量点", "资源预算"],
            "source_candidates": by_family.get("timing_guard", []),
        },
    ]


def build_requirement_objects(module: str, source: SourceRef) -> list[Any]:
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
        InterfaceRequirementObject(
            id=f"REQ-{module}-IF-0005",
            type="interface",
            interface_name="中断状态获取接口",
            direction="output",
            dependency="接口应返回自上次读取以来发生输入变化的 Port/Pin 状态，并在读取后按芯片行为或驱动策略清除对应中断状态。",
            evidence="验证：模拟输入变化、中断触发和清除流程，检查返回状态与清除结果。",
            source=[source],
        ),
        InterfaceRequirementObject(
            id=f"REQ-{module}-IF-0006",
            type="interface",
            interface_name="故障诊断信息读取接口",
            direction="output",
            dependency="接口应返回通信故障、寄存器回读校验故障、中断异常和未初始化访问等诊断状态，并在状态不可获取时返回定义错误。",
            evidence="验证：模拟通信故障、回读不一致、中断异常和未初始化访问，检查故障状态字与错误返回。",
            source=[source],
        ),
        InterfaceRequirementObject(
            id=f"REQ-{module}-IF-0007",
            type="interface",
            interface_name="驱动复位接口",
            direction="input",
            dependency="接口应支持对指定实例执行硬件复位或软件重新初始化，并在复位失败时返回定义错误。",
            evidence="验证：模拟硬件复位、软件重新初始化、RESET 不可控和复位失败场景。",
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
        TimingRequirementObject(
            id=f"REQ-{module}-TIME-0001",
            type="timing",
            constraint="软件应对 I2C 访问、复位恢复和状态采样设置项目定义的等待、超时或重试策略。",
            minimum="",
            maximum="",
            source=[source],
        ),
    ]
