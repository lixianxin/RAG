import os
import sys
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parsers.markdown_parse import MarkdownParser
from src.parsers.chunker import TextChunker, ChunkStrategy
from src.parsers.cleaner import TextCleaner


def create_test_markdown(content: str) -> str:
    """创建测试用的markdown文件"""
    temp_file = tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8")
    temp_file.write(content)
    temp_file.close()
    return temp_file.name


def test_supported_extensions():
    """测试支持的文件扩展名"""
    print("=== 测试支持的文件扩展名 ===")

    parser = MarkdownParser()
    extensions = parser.supported_extensions()

    assert isinstance(extensions, list)
    assert ".md" in extensions
    assert ".markdown" in extensions
    assert ".MD" in extensions
    assert ".MARKDOWN" in extensions

    print("[OK] 支持的文件扩展名测试通过")


def test_parse_simple_markdown():
    """测试解析简单markdown"""
    print("=== 测试解析简单markdown ===")

    parser = MarkdownParser()

    content = """# 标题

这是第一段正文。

这是第二段正文，包含**加粗**和*斜体*文本。"""

    temp_file = create_test_markdown(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert result.total_pages == 1
        assert result.table_count == 0
        assert "标题" in result.raw_text
        assert "这是第一段正文" in result.raw_text
        assert "这是第二段正文" in result.raw_text

        print(f"[OK] 解析简单markdown成功，生成 {result.total_chunks} 个块")
    finally:
        os.unlink(temp_file)


def test_parse_markdown_with_headers():
    """测试解析带标题的markdown"""
    print("=== 测试解析带标题的markdown ===")

    parser = MarkdownParser()

    content = """# 一级标题

## 二级标题

### 三级标题

这是正文内容。"""

    temp_file = create_test_markdown(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert "一级标题" in result.raw_text
        assert "二级标题" in result.raw_text
        assert "三级标题" in result.raw_text

        print(f"[OK] 解析带标题的markdown成功，生成 {result.total_chunks} 个块")
    finally:
        os.unlink(temp_file)


def test_parse_markdown_with_lists():
    """测试解析带列表的markdown"""
    print("=== 测试解析带列表的markdown ===")

    parser = MarkdownParser()

    content = """这是一个无序列表：

- 第一项
- 第二项
- 第三项

这是一个有序列表：

1. 第一点
2. 第二点
3. 第三点"""

    temp_file = create_test_markdown(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert "第一项" in result.raw_text
        assert "第二点" in result.raw_text

        print(f"[OK] 解析带列表的markdown成功，生成 {result.total_chunks} 个块")
    finally:
        os.unlink(temp_file)


def test_parse_markdown_with_code_block():
    """测试解析带代码块的markdown"""
    print("=== 测试解析带代码块的markdown ===")

    parser = MarkdownParser()

    content = """这是一段代码：

```python
def hello():
    print("Hello, World!")
```

这是代码后面的文本。"""

    temp_file = create_test_markdown(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert "def hello" in result.raw_text
        assert "print" in result.raw_text

        print(f"[OK] 解析带代码块的markdown成功，生成 {result.total_chunks} 个块")
    finally:
        os.unlink(temp_file)


def test_parse_markdown_with_links():
    """测试解析带链接的markdown"""
    print("=== 测试解析带链接的markdown ===")

    parser = MarkdownParser()

    content = """请访问[百度](https://www.baidu.com)搜索信息。

也可以查看[GitHub](https://github.com)上的代码。"""

    temp_file = create_test_markdown(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert "百度" in result.raw_text
        assert "github" in result.raw_text.lower()

        print(f"[OK] 解析带链接的markdown成功，生成 {result.total_chunks} 个块")
    finally:
        os.unlink(temp_file)


def test_parse_from_bytes():
    """测试从字节流解析markdown"""
    print("=== 测试从字节流解析markdown ===")

    parser = MarkdownParser()

    content = "# 字节流测试\n\n这是通过字节流解析的内容。"
    content_bytes = content.encode("utf-8")

    result = parser.parse_from_bytes(content_bytes, "test.md")

    assert result.filename == "test.md"
    assert result.total_pages == 1
    assert "字节流测试" in result.raw_text
    assert "通过字节流解析" in result.raw_text

    print(f"[OK] 从字节流解析markdown成功，生成 {result.total_chunks} 个块")


def test_parse_empty_markdown():
    """测试解析空markdown"""
    print("=== 测试解析空markdown ===")

    parser = MarkdownParser()

    temp_file = create_test_markdown("")

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert result.raw_text == ""
        assert result.table_count == 0

        print("[OK] 解析空markdown测试通过")
    finally:
        os.unlink(temp_file)


def test_parse_short_markdown():
    """测试解析短markdown（低于最小块大小）"""
    print("=== 测试解析短markdown ===")

    parser = MarkdownParser(chunker=TextChunker(max_chunk_size=1000, min_chunk_size=100))

    content = "这是一段很短的文本。"

    temp_file = create_test_markdown(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert result.total_chunks == 0

        print("[OK] 解析短markdown测试通过")
    finally:
        os.unlink(temp_file)


def test_parse_markdown_with_custom_components():
    """测试使用自定义组件解析markdown"""
    print("=== 测试使用自定义组件解析markdown ===")

    chunker = TextChunker(strategy=ChunkStrategy.SENTENCE, max_chunk_size=500, min_chunk_size=10, chunk_overlap=50)
    cleaner = TextCleaner()

    parser = MarkdownParser(cleaner=cleaner, chunker=chunker)

    content = """这是第一个句子。这是第二个句子，稍微长一点。这是第三个句子。这是第四个句子。这是第五个句子。"""

    temp_file = create_test_markdown(content)

    try:
        result = parser.parse(temp_file)

        assert result.filename is not None
        assert len(result.chunks) > 0

        print(f"[OK] 使用自定义组件解析成功，生成 {result.total_chunks} 个块")
    finally:
        os.unlink(temp_file)


def test_parse_markdown_with_metadata():
    """测试解析结果的元数据"""
    print("=== 测试解析结果的元数据 ===")

    parser = MarkdownParser()

    content = "# 测试元数据\n\n内容。"

    temp_file = create_test_markdown(content)

    try:
        result = parser.parse(temp_file)

        assert result.metadata is not None
        assert result.metadata["parser"] == "markdown"

        print("[OK] 解析结果的元数据测试通过")
    finally:
        os.unlink(temp_file)


if __name__ == "__main__":
    test_supported_extensions()
    test_parse_simple_markdown()
    test_parse_markdown_with_headers()
    test_parse_markdown_with_lists()
    test_parse_markdown_with_code_block()
    test_parse_markdown_with_links()
    test_parse_from_bytes()
    test_parse_empty_markdown()
    test_parse_short_markdown()
    test_parse_markdown_with_custom_components()
    test_parse_markdown_with_metadata()
    print("\n=== 所有测试通过 ===")