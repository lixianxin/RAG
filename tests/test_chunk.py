import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.parsers.chunker import TextChunker, ChunkStrategy


def test_split_by_paragraph_normal():
    """测试按段落分块正常情况"""
    print("=== 测试按段落分块正常情况 ===")

    chunker = TextChunker(strategy=ChunkStrategy.PARAGRAPH, max_chunk_size=200, min_chunk_size=50, chunk_overlap=50)
    
    text = """这是第一个段落。它包含一些内容，用来测试分块功能。

这是第二个段落。它也有一些文字，用于验证分块逻辑是否正确。

这是第三个段落。这个段落比较短。"""

    chunks = chunker.split(text)

    assert len(chunks) > 0
    for chunk in chunks:
        assert "content" in chunk
        assert "index" in chunk
        assert "length" in chunk
        assert chunk["type"] == "text"
        assert len(chunk["content"]) <= chunker.max_chunk_size

    print(f"[OK] 按段落分块生成 {len(chunks)} 个块")


def test_split_by_paragraph_empty():
    """测试按段落分块空输入"""
    print("=== 测试按段落分块空输入 ===")

    chunker = TextChunker(strategy=ChunkStrategy.PARAGRAPH)

    chunks = chunker.split("")
    assert chunks == []

    chunks = chunker.split("   ")
    assert chunks == []

    print("[OK] 按段落分块空输入测试通过")


def test_split_by_paragraph_short_text():
    """测试按段落分块短文本"""
    print("=== 测试按段落分块短文本 ===")

    chunker = TextChunker(strategy=ChunkStrategy.PARAGRAPH, max_chunk_size=1000, min_chunk_size=100)

    text = "这是一段很短的文本，长度不足以形成一个块。"

    chunks = chunker.split(text)

    assert chunks == []

    print("[OK] 按段落分块短文本测试通过")


def test_split_by_sentence_normal():
    """测试按句子分块正常情况"""
    print("=== 测试按句子分块正常情况 ===")

    chunker = TextChunker(strategy=ChunkStrategy.SENTENCE, max_chunk_size=100, min_chunk_size=30, chunk_overlap=20)

    text = "这是第一句话。这是第二句话，稍微长一点。这是第三句话。这是第四句话，用来测试句子分块功能是否正常工作。"

    chunks = chunker.split(text)

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk["type"] == "text"
        assert len(chunk["content"]) <= chunker.max_chunk_size

    print(f"[OK] 按句子分块生成 {len(chunks)} 个块")


def test_split_by_sentence_empty():
    """测试按句子分块空输入"""
    print("=== 测试按句子分块空输入 ===")

    chunker = TextChunker(strategy=ChunkStrategy.SENTENCE)

    chunks = chunker.split("")
    assert chunks == []

    print("[OK] 按句子分块空输入测试通过")


def test_split_by_character_normal():
    """测试按字符分块正常情况"""
    print("=== 测试按字符分块正常情况 ===")

    chunker = TextChunker(strategy=ChunkStrategy.CHARACTER, max_chunk_size=50, min_chunk_size=20, chunk_overlap=10)

    text = "这是一段较长的文本，用于测试按字符数进行分块的功能。" * 5

    chunks = chunker.split(text)

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk["type"] == "text"
        assert len(chunk["content"]) <= chunker.max_chunk_size

    print(f"[OK] 按字符分块生成 {len(chunks)} 个块")


def test_split_by_character_empty():
    """测试按字符分块空输入"""
    print("=== 测试按字符分块空输入 ===")

    chunker = TextChunker(strategy=ChunkStrategy.CHARACTER)

    chunks = chunker.split("")
    assert chunks == []

    print("[OK] 按字符分块空输入测试通过")


def test_split_long_paragraph():
    """测试超长段落分割"""
    print("=== 测试超长段落分割 ===")

    chunker = TextChunker(strategy=ChunkStrategy.PARAGRAPH, max_chunk_size=100, min_chunk_size=50, chunk_overlap=20)

    long_text = "这是一个非常长的段落，包含很多内容，用来测试超长段落的分割功能。" * 10

    chunks = chunker.split(long_text)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk["content"]) <= chunker.max_chunk_size

    print(f"[OK] 超长段落分割成 {len(chunks)} 个块")


def test_split_with_tables():
    """测试分块时附加表格"""
    print("=== 测试分块时附加表格 ===")

    chunker = TextChunker(strategy=ChunkStrategy.PARAGRAPH)

    text = "这是一段文本内容。"

    tables = [
        {
            "page": 1,
            "markdown": "| 姓名 | 年龄 |\n|------|------|\n| 张三 | 25 |",
            "cols": 2,
            "rows": 2
        }
    ]

    chunks = chunker.split(text, tables)

    assert len(chunks) >= 1
    table_chunks = [c for c in chunks if c["type"] == "table"]
    assert len(table_chunks) == 1
    assert table_chunks[0]["page"] == 1
    assert "表格" in table_chunks[0]["content"]

    print("[OK] 分块时附加表格测试通过")


def test_chunk_overlap():
    """测试块间重叠"""
    print("=== 测试块间重叠 ===")

    chunker = TextChunker(strategy=ChunkStrategy.CHARACTER, max_chunk_size=30, min_chunk_size=10, chunk_overlap=10)

    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ"

    chunks = chunker.split(text)

    assert len(chunks) >= 2, f"期望至少2个块，实际生成 {len(chunks)} 个"
    
    first_chunk = chunks[0]["content"]
    second_chunk = chunks[1]["content"]
    
    expected_overlap = chunker.chunk_overlap
    
    max_possible_overlap = min(len(first_chunk), len(second_chunk), expected_overlap)
    actual_overlap = 0
    
    for i in range(max_possible_overlap, 0, -1):
        if first_chunk.endswith(second_chunk[:i]):
            actual_overlap = i
            break
    
    assert actual_overlap > 0, f"块间应有重叠，实际重叠长度: {actual_overlap}"

    print("[OK] 块间重叠测试通过")


def test_chunk_indexes():
    """测试块索引连续性"""
    print("=== 测试块索引连续性 ===")

    chunker = TextChunker(strategy=ChunkStrategy.PARAGRAPH, max_chunk_size=50, min_chunk_size=10)

    text = """段落一。

段落二。

段落三。

段落四。"""

    chunks = chunker.split(text)

    indexes = [chunk["index"] for chunk in chunks]
    expected_indexes = list(range(len(chunks)))
    assert indexes == expected_indexes, f"索引不连续: {indexes}"

    print("[OK] 块索引连续性测试通过")


def test_default_strategy():
    """测试默认策略"""
    print("=== 测试默认策略 ===")

    chunker = TextChunker()

    assert chunker.strategy == ChunkStrategy.PARAGRAPH
    assert chunker.max_chunk_size == 1000
    assert chunker.min_chunk_size == 100
    assert chunker.chunk_overlap == 200

    text = "这是一个足够长的段落，用来验证默认参数下的分块行为。" * 10

    chunks = chunker.split(text)

    assert len(chunks) > 0

    print("[OK] 默认策略测试通过")


if __name__ == "__main__":
    test_split_by_paragraph_normal()
    test_split_by_paragraph_empty()
    test_split_by_paragraph_short_text()
    test_split_by_sentence_normal()
    test_split_by_sentence_empty()
    test_split_by_character_normal()
    test_split_by_character_empty()
    test_split_long_paragraph()
    test_split_with_tables()
    test_chunk_overlap()
    test_chunk_indexes()
    test_default_strategy()
    print("\n=== 所有测试通过 ===")