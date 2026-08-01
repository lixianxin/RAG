from pathlib import Path
import trace
from typing import List, Dict, Optional
import tempfile

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

from src.parsers.base import BaseParser, ParseResult
from src.parsers.chunker import TextChunker
from src.parsers.cleaner import TextCleaner
from src.parsers.table_parser import TableProcessor


class PDFParser:
    """基于docling的pdf解析器"""

    def __init__(
        self,
        chunker: Optional[TextChunker] = None,
        cleaner: Optional[TextCleaner] = None,
        table_processor: Optional[TableProcessor] = None,
    ) -> None:
        # 初始化组件
        self.chunker = chunker if chunker else TextChunker()
        self.cleaner = cleaner if cleaner else TextCleaner()
        self.table_processor = table_processor if table_processor else TableProcessor()
        # 初始化docling转换器
        pipeline_opts = PdfPipelineOptions()
        pipeline_opts.do_ocr = False  # 可选：禁用 OCR（节省资源）
        pipeline_opts.do_table_structure = True  # 禁用表格结构识别，避免下载模型
        self.converter = DocumentConverter(pipeline_options=pipeline_opts)

    def parse(self, file_path: str) -> ParseResult:
        """
        解析文档文件
        Args:
            file_path: 文件路径
        Returns:
            ParseResult: 解析结果
        """
        # 关键修复2：使用 convert() 并指定 source 参数
        doc = self.converter.convert(source=file_path)

        # 提取内容
        raw_text = doc.document.export_to_markdown()

        # 提取表格
        tables = self._extract_tables(doc)

        # 处理数据流程
        cleaned_text = self.cleaner.clean(raw_text)
        merged_text = self.table_processor.merge_table(tables)
        chunks = self.chunker.split(cleaned_text, merged_text)

        return ParseResult(
            filename=Path(file_path).name,
            total_pages=len(doc.pages),
            total_chunks=len(chunks),  # 此处的 chunk 数可另作处理，此处保留原意
            table_count=len(merged_text),
            chunks=chunks,
            raw_text=raw_text,
            tables=merged_text,
            metadata={"parser": "docling", "file_path": file_path},
        )

    def parse_from_bytes(self, file_bytes: bytes, filename: str) -> ParseResult:
        """
        从字节流解析文档
        Args:
            file_bytes: 文件字节流
            filename: 文件名
        Returns:
            ParseResult: 解析结果
        """
        # 关键修复3：对应的方法可能是 convert_from_bytes，需确认是否存在
        # 若不存在，可先用临时文件或改用其他方式，这里假设方法名为 convert_from_bytes
        doc = self.converter.convert_from_bytes(file_bytes)

        raw_text = doc.document.export_to_markdown()
        tables = self._extract_tables(doc)

        # 处理数据流程
        cleaned_text = self.cleaner.clean(raw_text)
        merged_text = self.table_processor.merge_table(tables)
        chunks = self.chunker.split(cleaned_text, merged_text)

        return ParseResult(
            filename=filename,
            total_pages=len(doc.pages),
            total_chunks=len(chunks),  # 此处的 chunk 数可另作处理，此处保留原意
            table_count=len(merged_text),
            chunks=chunks,
            raw_text=raw_text,
            tables=merged_text,
            metadata={"parser": "docling", "file_path": filename},
        )

    def supported_extensions(self) -> list[str]:
        """
        返回支持的文件扩展名
        Returns:
            支持的扩展名列表，如 ['.pdf', '.PDF']
        """
        return [".pdf", ".PDF"]

    def _extract_tables(self, doc):
        """提取表格（修正方法名拼写：extract 而非 exstract）"""
        tables = []
        # 检查是否有 tables 属性
        if not hasattr(doc.document, "tables") or not doc.document.tables:
            return tables

        for i, table in enumerate(doc.document.tables, 1):
            try:
                # 获取表格所在页码（通过 prov 属性）
                prov = getattr(table, "prov", [])
                page_no = prov[0].page_no if prov else None
                # 关键修复4：使用 doc.document 作为参数
                table_data = {
                    "table_num": i,
                    "page": page_no,
                    "markdown": table.export_to_markdown(doc=doc.document),
                }
                tables.append(table_data)
            except Exception as e:
                print(f"警告：无法处理表格 {i}，异常信息：{e}")
                continue

        return tables
