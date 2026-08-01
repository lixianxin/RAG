"""测试 DocumentStore 文档存储"""

import sys
import os
import tempfile
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.document_store import DocumentStore
from src.embeddings.base import BaseEmbedding
from src.embeddings.chroma_store import ChromaVectorStore
from src.parsers.base import ParseResult


class MockEmbedding(BaseEmbedding):
    """Mock嵌入模型，用于测试"""

    def __init__(self, dim: int = 5):
        self.dim = dim

    def embed_text(self, text: str):
        # 简单的确定性向量化：基于字符的hash
        vector = [0.0] * self.dim
        for i, ch in enumerate(text):
            vector[i % self.dim] += ord(ch) % 10 / 10.0
        # 归一化
        import math

        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def embed_batch(self, texts):
        return [self.embed_text(t) for t in texts]

    def get_embedding_name(self) -> str:
        return "mock-embedding"

    def get_embedding_dim(self) -> int:
        return self.dim


def create_test_store(temp_dir: str) -> DocumentStore:
    """创建测试用的文档存储"""
    embedding = MockEmbedding(dim=5)
    vector_store = ChromaVectorStore(
        collection_name="test_docs",
        persist_directory=temp_dir,
    )
    return DocumentStore(
        embedding_model=embedding,
        vector_store=vector_store,
    )


def create_test_parse_result() -> ParseResult:
    """创建测试用的解析结果"""
    return ParseResult(
        filename="test.txt",
        total_pages=1,
        total_chunks=3,
        table_count=0,
        chunks=[
            {"content": "人工智能是计算机科学的一个分支", "index": 0, "length": 15, "type": "text"},
            {"content": "机器学习是人工智能的核心技术", "index": 1, "length": 14, "type": "text"},
            {"content": "深度学习使用多层神经网络", "index": 2, "length": 12, "type": "text"},
        ],
        raw_text="人工智能是计算机科学的一个分支\n\n机器学习是人工智能的核心技术\n\n深度学习使用多层神经网络",
        tables=[],
        metadata={"parser": "test"},
    )


def test_init():
    """测试初始化"""
    print("=== 测试初始化 ===")

    temp_dir = tempfile.mkdtemp()
    try:
        store = create_test_store(temp_dir)

        assert store.embedding is not None
        assert store.vector_store is not None

        print("[OK] 初始化测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_add_parse_result():
    """测试添加解析结果"""
    print("=== 测试添加解析结果 ===")

    temp_dir = tempfile.mkdtemp()
    try:
        store = create_test_store(temp_dir)
        parse_result = create_test_parse_result()

        doc_ids = store.add_parse_result(parse_result, namespace="test")

        assert len(doc_ids) == 3
        for doc_id in doc_ids:
            assert doc_id.startswith("test_test.txt_")

        stats = store.get_stats()
        assert stats["count"] == 3

        print(f"  添加文档数: {len(doc_ids)}")
        print(f"  存储统计: count={stats['count']}")
        print("[OK] 添加解析结果测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_add_parse_result_with_table():
    """测试添加包含表格的解析结果"""
    print("=== 测试添加包含表格的解析结果 ===")

    temp_dir = tempfile.mkdtemp()
    try:
        store = create_test_store(temp_dir)

        parse_result = ParseResult(
            filename="table_doc.txt",
            total_pages=2,
            total_chunks=2,
            table_count=1,
            chunks=[
                {"content": "这是文本内容", "index": 0, "length": 6, "type": "text"},
                {"content": "|列1|列2|\n|---|---|\n|值1|值2|", "index": 1, "length": 30, "type": "table", "page": 1},
            ],
            raw_text="这是文本内容",
            tables=[{"page": 1, "markdown": "|列1|列2|\n|---|---|\n|值1|值2|"}],
            metadata={"parser": "test"},
        )

        doc_ids = store.add_parse_result(parse_result, namespace="table_test")

        assert len(doc_ids) == 2

        # 验证可以通过搜索找到表格内容
        results = store.search("列1", top_k=5)
        assert len(results) > 0

        print(f"  添加文档数: {len(doc_ids)}")
        print("[OK] 添加包含表格的解析结果测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_search():
    """测试搜索"""
    print("=== 测试搜索 ===")

    temp_dir = tempfile.mkdtemp()
    try:
        store = create_test_store(temp_dir)
        parse_result = create_test_parse_result()

        store.add_parse_result(parse_result, namespace="test")

        results = store.search("人工智能", top_k=2)

        assert len(results) <= 2
        for result in results:
            assert "id" in result
            assert "content" in result
            assert "metadata" in result
            assert "score" in result

        print(f"  搜索结果数: {len(results)}")
        for i, result in enumerate(results):
            print(f"  结果{i+1}: score={result['score']:.4f}, content={result['content'][:20]}")
        print("[OK] 搜索测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_search_with_namespace():
    """测试带命名空间的搜索"""
    print("=== 测试带命名空间的搜索 ===")

    temp_dir = tempfile.mkdtemp()
    try:
        store = create_test_store(temp_dir)

        # 添加两个命名空间的文档
        parse_result1 = create_test_parse_result()
        parse_result1.filename = "doc1.txt"
        store.add_parse_result(parse_result1, namespace="ns1")

        parse_result2 = create_test_parse_result()
        parse_result2.filename = "doc2.txt"
        store.add_parse_result(parse_result2, namespace="ns2")

        # 搜索特定命名空间
        results_ns1 = store.search("人工智能", top_k=5, namespace="ns1")
        results_ns2 = store.search("人工智能", top_k=5, namespace="ns2")
        results_all = store.search("人工智能", top_k=5)

        # 验证命名空间过滤
        for result in results_ns1:
            assert result["metadata"]["namespace"] == "ns1"
        for result in results_ns2:
            assert result["metadata"]["namespace"] == "ns2"

        print(f"  ns1结果数: {len(results_ns1)}")
        print(f"  ns2结果数: {len(results_ns2)}")
        print(f"  全部结果数: {len(results_all)}")
        print("[OK] 带命名空间的搜索测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_add_documents():
    """测试直接添加文档"""
    print("=== 测试直接添加文档 ===")

    temp_dir = tempfile.mkdtemp()
    try:
        store = create_test_store(temp_dir)

        texts = ["测试文本1", "测试文本2", "测试文本3"]
        metadatas = [
            {"source": "manual", "category": "test"},
            {"source": "manual", "category": "test"},
            {"source": "manual", "category": "test"},
        ]

        doc_ids = store.add_documents(texts, metadatas, namespace="manual")

        assert len(doc_ids) == 3
        for doc_id in doc_ids:
            assert doc_id.startswith("manual_")

        stats = store.get_stats()
        assert stats["count"] == 3

        print(f"  添加文档数: {len(doc_ids)}")
        print("[OK] 直接添加文档测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_add_documents_empty_metadata():
    """测试添加文档时元数据不足"""
    print("=== 测试添加文档时元数据不足 ===")

    temp_dir = tempfile.mkdtemp()
    try:
        store = create_test_store(temp_dir)

        texts = ["文本1", "文本2", "文本3"]
        metadatas = [{"source": "test"}]  # 只有1个元数据

        doc_ids = store.add_documents(texts, metadatas, namespace="test")

        assert len(doc_ids) == 3

        print("[OK] 元数据不足时添加文档测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_get_stats():
    """测试获取统计信息"""
    print("=== 测试获取统计信息 ===")

    temp_dir = tempfile.mkdtemp()
    try:
        store = create_test_store(temp_dir)
        parse_result = create_test_parse_result()

        store.add_parse_result(parse_result)

        stats = store.get_stats()

        assert "count" in stats
        assert "name" in stats
        assert "distance" in stats
        assert "embedding_dim" in stats
        assert "embedding_model" in stats
        assert stats["count"] == 3
        assert stats["embedding_dim"] == 5
        assert stats["embedding_model"] == "mock-embedding"

        print(f"  统计信息: {stats}")
        print("[OK] 获取统计信息测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_search_empty_store():
    """测试在空存储中搜索"""
    print("=== 测试在空存储中搜索 ===")

    temp_dir = tempfile.mkdtemp()
    try:
        store = create_test_store(temp_dir)

        results = store.search("测试查询", top_k=5)

        assert len(results) == 0

        print("[OK] 空存储搜索测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_multiple_additions():
    """测试多次添加文档"""
    print("=== 测试多次添加文档 ===")

    temp_dir = tempfile.mkdtemp()
    try:
        store = create_test_store(temp_dir)

        for i in range(3):
            parse_result = ParseResult(
                filename=f"doc{i}.txt",
                total_pages=1,
                total_chunks=1,
                table_count=0,
                chunks=[
                    {"content": f"这是第{i}个文档的内容", "index": 0, "length": 15, "type": "text"},
                ],
                raw_text=f"这是第{i}个文档的内容",
                tables=[],
                metadata={"parser": "test"},
            )
            store.add_parse_result(parse_result, namespace=f"batch{i}")

        stats = store.get_stats()
        assert stats["count"] == 3

        print(f"  总文档数: {stats['count']}")
        print("[OK] 多次添加文档测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_init()
    test_add_parse_result()
    test_add_parse_result_with_table()
    test_search()
    test_search_with_namespace()
    test_add_documents()
    test_add_documents_empty_metadata()
    test_get_stats()
    test_search_empty_store()
    test_multiple_additions()
    print("\n=== 所有测试通过 ===")