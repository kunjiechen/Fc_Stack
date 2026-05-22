from __future__ import annotations

from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "templates"
XLSX_PATH = OUT_DIR / "模块原始需求输入模板.xlsx"
TXT_PATH = OUT_DIR / "模块原始需求输入模板.txt"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TXT_PATH.write_text(build_txt_template(), encoding="utf-8")
    write_xlsx(
        XLSX_PATH,
        {
            "说明": instruction_rows(),
            "需求输入": input_rows(),
            "枚举参考": enum_rows(),
        },
    )
    print(XLSX_PATH)
    print(TXT_PATH)


def build_txt_template() -> str:
    return """# 模块原始需求输入模板（TXT）

请直接按下面结构填写。可以删掉示例内容，保留标题。
建议一条需求一行，尽量写明确，不要把多个独立需求塞进同一行。

【基础信息】
模块: TJA1043
模块简称: TJA1043
所属层级: IoExtDrv / BSW
适用项目: FcStack
安全等级: QM

【原始功能需求】
1. 需要支持模式切换。
2. 需要支持当前模式读取。
3. 需要支持初始化后进入 NORMAL 模式。

【原始接口需求】
1. 初始化接口：输入=配置指针；输出=初始化状态；返回值=成功/失败；异常=配置非法、底层依赖不可用。
2. 设置模式接口：输入=实例ID、目标模式；输出=模式切换结果；返回值=成功/失败；异常=非法实例、非法模式、未初始化。
3. 读取模式接口：输入=实例ID；输出=当前模式；返回值=成功/失败；异常=非法实例、空指针、未初始化。

【原始配置需求】
1. 内核数量：默认值=待定；有效范围=1..6；无效配置处理=待定。
2. 实例数量：默认值=1；有效范围=1..256；无效配置处理=待定。
3. 默认模式：默认值=NORMAL；有效范围=NORMAL/STANDBY/SLEEP；无效配置处理=拒绝配置。

【原始非功能与约束需求】
1. 覆盖约束：原始开发需求必须覆盖，优先级高于手册增强内容；验证建议=Review/Trace。
2. 时序约束：模式切换后的状态读取需要满足芯片手册时序；验证建议=Analysis/IT。
3. 安全等级：模块安全等级为 QM；验证建议=Review。

【可选补充】
1. 如果无输入，则按照当前流程执行。
2. 如果有输入，则首先满足覆盖原始开发需求，然后基于手册进行丰富。
3. 输出应包含：正式需求规范文档 + 原始开发需求文档 + 追溯。
"""


def instruction_rows() -> list[list[str]]:
    return [
        ["工作表", "用途", "填写说明"],
        ["说明", "模板说明", "先看本页，再去“需求输入”页填写。"],
        ["需求输入", "主输入页", "一行一条原始需求；类别建议填写 FUNC / INTF / CFG / NFR。"],
        ["枚举参考", "参考值", "提供类别、优先级、状态、验证建议的推荐写法。"],
        [],
        ["字段", "是否建议填写", "说明"],
        ["模块", "建议", "同一文件中建议每行一致；至少填写一次。"],
        ["类别", "强烈建议", "FUNC=功能需求；INTF=接口需求；CFG=配置需求；NFR=非功能与约束需求。"],
        ["标题", "强烈建议", "一句短标题，方便生成原始需求文档。"],
        ["描述", "必填", "尽量写成完整句子，保留原始诉求。"],
        ["输入/输出/返回值/异常", "接口类建议", "仅 INTF 类强烈建议填写。"],
        ["配置时机/默认值/有效范围/无效配置处理", "配置类建议", "仅 CFG 类强烈建议填写。"],
        ["约束分类/约束值/验证建议", "NFR 类建议", "仅 NFR 类强烈建议填写。"],
        ["优先级", "建议", "High / Medium / Low。"],
        ["状态", "建议", "明确 / 待澄清 / Draft。"],
        [],
        ["建议", "", "不要把多个完全不同的需求写在同一行。"],
        ["建议", "", "如果一条需求同时含接口和配置，优先拆成两行。"],
        ["建议", "", "字段能单独填列时，优先填列，不要都堆到描述里。"],
    ]


def input_rows() -> list[list[str]]:
    return [
        [
            "模块",
            "类别",
            "标题",
            "描述",
            "输入",
            "输出",
            "返回值",
            "异常",
            "配置时机",
            "默认值",
            "有效范围",
            "无效配置处理",
            "约束分类",
            "约束值",
            "验证建议",
            "优先级",
            "状态",
        ],
        [
            "TJA1043",
            "FUNC",
            "模式控制",
            "需要支持外设模式切换。",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "High",
            "明确",
        ],
        [
            "TJA1043",
            "INTF",
            "初始化接口",
            "需要提供初始化接口，初始化后进入 NORMAL 模式。",
            "配置指针",
            "初始化状态",
            "成功/失败",
            "配置非法、底层依赖不可用",
            "",
            "",
            "",
            "",
            "",
            "",
            "UT/IT",
            "High",
            "明确",
        ],
        [
            "TJA1043",
            "CFG",
            "实例数量",
            "需要支持多实例配置。",
            "",
            "",
            "",
            "",
            "编译期/配置生成期",
            "1",
            "1..256",
            "拒绝非法配置并报告错误",
            "",
            "",
            "Review/UT",
            "Medium",
            "明确",
        ],
        [
            "TJA1043",
            "NFR",
            "覆盖检查",
            "原始开发需求必须覆盖，优先级高于手册增强内容。",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "覆盖约束",
            "必须100%覆盖原始输入",
            "Review/Trace",
            "High",
            "明确",
        ],
        ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
        ["<请从这一行开始继续填写>", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
    ]


def enum_rows() -> list[list[str]]:
    return [
        ["字段", "推荐值", "说明"],
        ["类别", "FUNC", "功能需求"],
        ["类别", "INTF", "接口需求"],
        ["类别", "CFG", "配置需求"],
        ["类别", "NFR", "非功能与约束需求"],
        ["优先级", "High", "必须优先覆盖"],
        ["优先级", "Medium", "重要但可后续补充细化"],
        ["优先级", "Low", "可选增强项"],
        ["状态", "明确", "输入已经比较清楚"],
        ["状态", "待澄清", "有意图但信息不完整"],
        ["状态", "Draft", "仅初步想法"],
        ["验证建议", "Review", "评审验证"],
        ["验证建议", "UT", "单元测试"],
        ["验证建议", "IT", "集成测试"],
        ["验证建议", "Review/Trace", "评审 + 追溯检查"],
        ["验证建议", "Analysis/IT", "分析 + 集成测试"],
        ["约束分类", "覆盖约束", "例如必须覆盖原始输入"],
        ["约束分类", "安全等级", "例如 QM / ASIL"],
        ["约束分类", "时序", "例如等待时间、超时、采样时序"],
        ["约束分类", "性能", "例如响应时间、CPU占用"],
        ["约束分类", "资源", "例如 RAM/ROM/实例数量/内核数量"],
    ]


def write_xlsx(path: Path, sheets: dict[str, list[list[str]]]) -> None:
    shared_strings: list[str] = []
    string_index: dict[str, int] = {}
    sheet_files: list[tuple[str, str]] = []

    for idx, (sheet_name, rows) in enumerate(sheets.items(), start=1):
        xml_rows: list[str] = []
        for row_idx, row in enumerate(rows, start=1):
            cells: list[str] = []
            for col_idx, value in enumerate(row, start=1):
                text = "" if value is None else str(value)
                if text == "":
                    continue
                if text not in string_index:
                    string_index[text] = len(shared_strings)
                    shared_strings.append(text)
                ref = f"{column_name(col_idx)}{row_idx}"
                cells.append(f'<c r="{ref}" t="s"><v>{string_index[text]}</v></c>')
            xml_rows.append(f'<row r="{row_idx}">{"".join(cells)}</row>')
        sheet_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f'<sheetData>{"".join(xml_rows)}</sheetData>'
            "</worksheet>"
        )
        sheet_files.append((sheet_name, sheet_xml))

    workbook_sheets = []
    workbook_rels = []
    content_types = [
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/xl/sharedStrings.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>',
    ]
    for idx, (sheet_name, _) in enumerate(sheet_files, start=1):
        workbook_sheets.append(f'<sheet name="{xml_escape(sheet_name)}" sheetId="{idx}" r:id="rId{idx}"/>')
        workbook_rels.append(
            '<Relationship '
            f'Id="rId{idx}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{idx}.xml"/>'
        )
        content_types.append(
            f'<Override PartName="/xl/worksheets/sheet{idx}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    workbook_rels.append(
        '<Relationship Id="rId999" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" '
        'Target="sharedStrings.xml"/>'
    )

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<sheets>{"".join(workbook_sheets)}</sheets>'
        "</workbook>"
    )
    workbook_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'{"".join(workbook_rels)}'
        "</Relationships>"
    )
    root_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )
    shared_strings_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        f'count="{len(shared_strings)}" uniqueCount="{len(shared_strings)}">'
        + "".join(f"<si><t>{xml_escape(item)}</t></si>" for item in shared_strings)
        + "</sst>"
    )
    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        + "".join(content_types)
        + "</Types>"
    )

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml)
        archive.writestr("_rels/.rels", root_rels_xml)
        archive.writestr("xl/workbook.xml", workbook_xml)
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        archive.writestr("xl/sharedStrings.xml", shared_strings_xml)
        for idx, (_, sheet_xml) in enumerate(sheet_files, start=1):
            archive.writestr(f"xl/worksheets/sheet{idx}.xml", sheet_xml)


def column_name(index: int) -> str:
    result = ""
    value = index
    while value:
        value, remainder = divmod(value - 1, 26)
        result = chr(ord("A") + remainder) + result
    return result


def xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


if __name__ == "__main__":
    main()
