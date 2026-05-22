"""Markdown structure parser and chunk engine for Phase-1."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
import hashlib
import re
from typing import Any


class BlockType(StrEnum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    CODE_BLOCK = "code_block"
    NOTE = "note"
    WARNING = "warning"
    IMAGE = "image"
    HTML_BLOCK = "html_block"


@dataclass(frozen=True)
class MarkdownBlock:
    type: BlockType
    text: str
    line_start: int
    line_end: int
    heading_level: int | None = None
    heading_text: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["type"] = str(self.type)
        return data


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    document: str
    content_type: str
    heading_path: list[str]
    text: str
    line_start: int
    line_end: int
    blocks: list[MarkdownBlock] = field(default_factory=list)
    semantic_tags: list[str] = field(default_factory=list)

    @property
    def chapter(self) -> str:
        return self.heading_path[0] if self.heading_path else ""

    @property
    def sub_chapter(self) -> str:
        return " > ".join(self.heading_path[1:]) if len(self.heading_path) > 1 else ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["blocks"] = [block.to_dict() for block in self.blocks]
        return data


@dataclass(frozen=True)
class ParsedDocument:
    document: str
    blocks: list[MarkdownBlock]
    chunks: list[DocumentChunk]
    semantic_index: dict[str, list[str]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "document": self.document,
            "blocks": [block.to_dict() for block in self.blocks],
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "semantic_index": self.semantic_index,
        }


SEMANTIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "mode": ("mode", "sleep", "standby", "normal", "listen-only", "listen only"),
    "timing": ("wait", "delay", "minimum", "maximum", "timeout", "before", "after", "us", "ms"),
    "diagnostic": ("diagnostic", "fault", "error", "err_n", "fail", "failure", "status"),
    "interface": ("txd", "rxd", "en", "stb", "wake", "inh", "pin", "spi", "lin"),
    "configuration": ("enable", "disable", "configuration", "instance", "mapping", "parameter"),
    "state": ("state", "transition", "enter", "exit", "wake", "sleep", "standby", "normal"),
}


class MarkdownStructureParser:
    """Parse Markdown into blocks, chunks, and a simple semantic index."""

    def parse_file(self, path: str | Path) -> ParsedDocument:
        path = Path(path)
        return self.parse(path.read_text(encoding="utf-8"), document=str(path))

    def parse(self, text: str, document: str = "<memory>") -> ParsedDocument:
        blocks = self._parse_blocks(text)
        chunks = self._build_chunks(document, blocks)
        indexed_chunks = [self._with_semantic_tags(chunk) for chunk in chunks]
        semantic_index = self._build_semantic_index(indexed_chunks)
        return ParsedDocument(
            document=document,
            blocks=blocks,
            chunks=indexed_chunks,
            semantic_index=semantic_index,
        )

    def _parse_blocks(self, text: str) -> list[MarkdownBlock]:
        lines = text.splitlines()
        blocks: list[MarkdownBlock] = []
        index = 0
        while index < len(lines):
            line = lines[index]
            line_no = index + 1

            if not line.strip():
                index += 1
                continue

            heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
            if heading:
                blocks.append(
                    MarkdownBlock(
                        type=BlockType.HEADING,
                        text=line.strip(),
                        line_start=line_no,
                        line_end=line_no,
                        heading_level=len(heading.group(1)),
                        heading_text=heading.group(2).strip(),
                    )
                )
                index += 1
                continue

            if line.lstrip().startswith("```"):
                start = index
                fence = line.lstrip()[:3]
                index += 1
                while index < len(lines) and not lines[index].lstrip().startswith(fence):
                    index += 1
                if index < len(lines):
                    index += 1
                blocks.append(
                    MarkdownBlock(
                        type=BlockType.CODE_BLOCK,
                        text="\n".join(lines[start:index]),
                        line_start=start + 1,
                        line_end=index,
                    )
                )
                continue

            if self._is_table_start(lines, index):
                start = index
                index += 1
                while index < len(lines) and self._is_table_row(lines[index]):
                    index += 1
                blocks.append(
                    MarkdownBlock(
                        type=BlockType.TABLE,
                        text="\n".join(lines[start:index]),
                        line_start=start + 1,
                        line_end=index,
                        metadata={"rows": self._parse_table(lines[start:index])},
                    )
                )
                continue

            if re.match(r"^\s*!\[.*?\]\(.*?\)", line):
                blocks.append(
                    MarkdownBlock(
                        type=BlockType.IMAGE,
                        text=line.strip(),
                        line_start=line_no,
                        line_end=line_no,
                    )
                )
                index += 1
                continue

            if self._is_html_line(line):
                start = index
                index += 1
                while index < len(lines) and lines[index].strip() and self._is_html_line(lines[index]):
                    index += 1
                blocks.append(
                    MarkdownBlock(
                        type=BlockType.HTML_BLOCK,
                        text="\n".join(lines[start:index]),
                        line_start=start + 1,
                        line_end=index,
                    )
                )
                continue

            start = index
            paragraph_lines = [line]
            index += 1
            while index < len(lines) and self._continues_paragraph(lines, index):
                paragraph_lines.append(lines[index])
                index += 1
            paragraph = "\n".join(paragraph_lines).strip()
            block_type = self._paragraph_type(paragraph)
            blocks.append(
                MarkdownBlock(
                    type=block_type,
                    text=paragraph,
                    line_start=start + 1,
                    line_end=index,
                )
            )

        return blocks

    def _build_chunks(self, document: str, blocks: list[MarkdownBlock]) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        heading_stack: list[tuple[int, str]] = []
        section_blocks: list[MarkdownBlock] = []

        def flush_section() -> None:
            nonlocal section_blocks
            if not section_blocks:
                return
            text = "\n\n".join(block.text for block in section_blocks)
            chunks.append(
                self._make_chunk(
                    document=document,
                    content_type="section",
                    heading_path=[item[1] for item in heading_stack],
                    blocks=section_blocks,
                    text=text,
                )
            )
            section_blocks = []

        for block in blocks:
            if block.type == BlockType.HEADING:
                flush_section()
                level = block.heading_level or 1
                heading_stack = [item for item in heading_stack if item[0] < level]
                heading_stack.append((level, block.heading_text or block.text))
                continue

            if block.type == BlockType.TABLE:
                flush_section()
                chunks.append(
                    self._make_chunk(
                        document=document,
                        content_type="table",
                        heading_path=[item[1] for item in heading_stack],
                        blocks=[block],
                        text=block.text,
                    )
                )
                continue

            section_blocks.append(block)

        flush_section()
        return chunks

    def _make_chunk(
        self,
        document: str,
        content_type: str,
        heading_path: list[str],
        blocks: list[MarkdownBlock],
        text: str,
    ) -> DocumentChunk:
        line_start = min(block.line_start for block in blocks)
        line_end = max(block.line_end for block in blocks)
        digest = hashlib.sha1(
            f"{document}:{line_start}:{line_end}:{content_type}:{text}".encode("utf-8")
        ).hexdigest()[:10]
        return DocumentChunk(
            id=f"chunk-{digest}",
            document=document,
            content_type=content_type,
            heading_path=heading_path,
            text=text,
            line_start=line_start,
            line_end=line_end,
            blocks=blocks,
        )

    def _with_semantic_tags(self, chunk: DocumentChunk) -> DocumentChunk:
        haystack = " ".join([*chunk.heading_path, chunk.text]).lower()
        tags = [
            tag
            for tag, keywords in SEMANTIC_KEYWORDS.items()
            if any(self._contains_keyword(haystack, keyword) for keyword in keywords)
        ]
        return DocumentChunk(
            id=chunk.id,
            document=chunk.document,
            content_type=chunk.content_type,
            heading_path=chunk.heading_path,
            text=chunk.text,
            line_start=chunk.line_start,
            line_end=chunk.line_end,
            blocks=chunk.blocks,
            semantic_tags=tags,
        )

    def _build_semantic_index(self, chunks: list[DocumentChunk]) -> dict[str, list[str]]:
        index: dict[str, list[str]] = {tag: [] for tag in SEMANTIC_KEYWORDS}
        for chunk in chunks:
            for tag in chunk.semantic_tags:
                index[tag].append(chunk.id)
        return {tag: ids for tag, ids in index.items() if ids}

    def _continues_paragraph(self, lines: list[str], index: int) -> bool:
        line = lines[index]
        if not line.strip():
            return False
        if re.match(r"^(#{1,6})\s+", line):
            return False
        if line.lstrip().startswith("```"):
            return False
        if self._is_table_start(lines, index):
            return False
        if re.match(r"^\s*!\[.*?\]\(.*?\)", line):
            return False
        return True

    def _paragraph_type(self, paragraph: str) -> BlockType:
        lowered = paragraph.lower()
        if lowered.startswith(("> note", "note:", "**note")):
            return BlockType.NOTE
        if lowered.startswith(("> warning", "warning:", "**warning", "caution:")):
            return BlockType.WARNING
        return BlockType.PARAGRAPH

    def _is_table_start(self, lines: list[str], index: int) -> bool:
        if index + 1 >= len(lines):
            return False
        return self._is_table_row(lines[index]) and bool(
            re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", lines[index + 1])
        )

    def _is_table_row(self, line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2

    def _parse_table(self, rows: list[str]) -> list[list[str]]:
        parsed: list[list[str]] = []
        for row in rows:
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
            parsed.append(cells)
        return parsed

    def _is_html_line(self, line: str) -> bool:
        return bool(re.match(r"^\s*</?[a-zA-Z][^>]*>\s*$", line.strip()))

    def _contains_keyword(self, text: str, keyword: str) -> bool:
        if " " in keyword:
            return keyword in text
        return bool(re.search(rf"\b{re.escape(keyword)}\b", text, flags=re.IGNORECASE))
