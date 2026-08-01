from typing import Optional
from pathlib import Path

from src.parsers.base import BaseParser, ParseResult
from src.parsers.cleaner import TextCleaner
from src.parsers.chunker import TextChunker, ChunkStrategy


class MarkdownParser(BaseParser):
    def __init__(
        self,
        cleaner: Optional[TextCleaner] = None,
        chunker: Optional[TextChunker] = None,
    ):
        self.cleaner = cleaner or TextCleaner()
        self.chunker = chunker or TextChunker(
            strategy=ChunkStrategy.PARAGRAPH, max_chunk_size=1000, chunk_overlap=200
        )

    def parse(self, file_path: str) -> ParseResult:
        """
        解析Markdown文件，返回解析结果
        """
        # 读取文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
        # 文本清理
        cleaned_text = self.cleaner.clean(raw_text)
        # 文本分块
        chunks = self.chunker.split(cleaned_text)
        return ParseResult(
            filename=Path(file_path).name,
            total_pages=1,
            total_chunks=len(chunks),
            table_count=0,
            chunks=chunks,
            raw_text=raw_text,
            tables=[],
            metadata={"parser": "markdown"},
        )

    def parse_from_bytes(self, file_bytes: bytes, filename: str):
        """
        从字节流解析Markdown文件，返回解析结果
        """
        raw_text = file_bytes.decode("utf-8")

        cleaned_text = self.cleaner.clean(raw_text)
        chunks = self.chunker.split(cleaned_text)
        return ParseResult(
            filename=filename,
            total_pages=1,
            total_chunks=len(chunks),
            table_count=0,
            chunks=chunks,
            raw_text=raw_text,
            tables=[],
            metadata={"parser": "markdown"},
        )

    def supported_extensions(self) -> list[str]:
        return [".md", ".markdown", ".MD", ".MARKDOWN"]
