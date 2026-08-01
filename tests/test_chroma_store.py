"""测试 ChromaVectorStore 向量存储"""

import sys
import os
import tempfile
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embeddings.chroma_store import ChromaVectorStore
from src.embeddings.vector_store import Document, SearchResult


def create_test_store(temp_dir: str) -> ChromaVectorStore:
    """创建测试用的向量存储"""
    return ChromaVectorStore(
        collection_name="test_collection",
        persist_directory=temp_dir,
    )


def test_init():
    """测试初始化"""
    print("=== 测试初始化 ===")

    temp_dir = tempfile.mkdtemp()

    try:
        store = create_test_store(temp_dir)

        assert store.collection_name == "test_collection"
        assert store.distance == "cosine"
        assert store.client is not None
        assert store.collection is not None

        print("[OK] 初始化测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_add_documents():
    """测试添加文档"""
    print("=== 测试添加文档 ===")

    temp_dir = tempfile.mkdtemp()

    try:
        store = create_test_store(temp_dir)

        documents = [
            Document(id="doc1", content="人工智能是计算机科学的一个分支", metadata={"source": "book1"}),
            Document(id="doc2", content="机器学习是人工智能的核心技术", metadata={"source": "book2"}),
            Document(id="doc3", content="深度学习使用多层神经网络", metadata={"source": "book3"}),
        ]
        embeddings = [
            [0.1, 0.2, 0.3, 0.4, 0.5],
            [0.2, 0.3, 0.4, 0.5, 0.6],
            [0.3, 0.4, 0.5, 0.6, 0.7],
        ]

        ids = store.add_documents(documents, embeddings)

        assert len(ids) == 3
        assert "doc1" in ids
        assert "doc2" in ids
        assert "doc3" in ids

        stats = store.get_collection_stats()
        assert stats["count"] == 3

        print("[OK] 添加文档测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_add_documents_auto_id():
    """测试自动生成ID"""
    print("=== 测试自动生成ID ===")

    temp_dir = tempfile.mkdtemp()

    try:
        store = create_test_store(temp_dir)

        documents = [
            Document(id="", content="测试文档", metadata={}),
        ]
        embeddings = [[0.1, 0.2, 0.3, 0.4, 0.5]]

        ids = store.add_documents(documents, embeddings)

        assert len(ids) == 1
        assert ids[0] != ""
        assert len(ids[0]) > 0

        print("[OK] 自动生成ID测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_search():
    """测试搜索"""
    print("=== 测试搜索 ===")

    temp_dir = tempfile.mkdtemp()

    try:
        store = create_test_store(temp_dir)

        documents = [
            Document(id="doc1", content="苹果是一种水果", metadata={"category": "fruit"}),
            Document(id="doc2", content="香蕉是黄色的水果", metadata={"category": "fruit"}),
            Document(id="doc3", content="汽车是一种交通工具", metadata={"category": "vehicle"}),
        ]
        embeddings = [
            [0.9, 0.1, 0.0, 0.0, 0.0],
            [0.8, 0.2, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.9, 0.1, 0.0],
        ]

        store.add_documents(documents, embeddings)

        results = store.search(query_embedding=[0.85, 0.15, 0.0, 0.0, 0.0], top_k=2)

        assert len(results) == 2
        assert isinstance(results[0], SearchResult)
        assert isinstance(results[0].document, Document)
        assert results[0].score >= 0

        print(f"  搜索结果数量: {len(results)}")
        for i, result in enumerate(results):
            print(f"  结果{i+1}: id={result.document.id}, score={result.score:.4f}")

        print("[OK] 搜索测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_search_with_filter():
    """测试带过滤条件的搜索"""
    print("=== 测试带过滤条件的搜索 ===")

    temp_dir = tempfile.mkdtemp()

    try:
        store = create_test_store(temp_dir)

        documents = [
            Document(id="doc1", content="苹果是一种水果", metadata={"category": "fruit"}),
            Document(id="doc2", content="香蕉是黄色的水果", metadata={"category": "fruit"}),
            Document(id="doc3", content="汽车是一种交通工具", metadata={"category": "vehicle"}),
        ]
        embeddings = [
            [0.9, 0.1, 0.0, 0.0, 0.0],
            [0.8, 0.2, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.9, 0.1, 0.0],
        ]

        store.add_documents(documents, embeddings)

        results = store.search(
            query_embedding=[0.5, 0.5, 0.0, 0.0, 0.0],
            top_k=5,
            filter={"category": "fruit"},
        )

        assert len(results) > 0
        for result in results:
            assert result.document.metadata["category"] == "fruit"

        print(f"  过滤后结果数量: {len(results)}")
        print("[OK] 带过滤条件的搜索测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_clear():
    """测试清空数据"""
    print("=== 测试清空数据 ===")

    temp_dir = tempfile.mkdtemp()

    try:
        store = create_test_store(temp_dir)

        documents = [
            Document(id="doc1", content="测试文档", metadata={}),
        ]
        embeddings = [[0.1, 0.2, 0.3, 0.4, 0.5]]

        store.add_documents(documents, embeddings)

        stats = store.get_collection_stats()
        assert stats["count"] == 1

        result = store.clear()
        assert result is True

        stats = store.get_collection_stats()
        assert stats["count"] == 0

        print("[OK] 清空数据测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_get_collection_stats():
    """测试获取集合统计信息"""
    print("=== 测试获取集合统计信息 ===")

    temp_dir = tempfile.mkdtemp()

    try:
        store = create_test_store(temp_dir)

        stats = store.get_collection_stats()

        assert "count" in stats
        assert "name" in stats
        assert "distance" in stats
        assert stats["name"] == "test_collection"
        assert stats["distance"] == "cosine"

        print(f"  统计信息: {stats}")
        print("[OK] 获取集合统计信息测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_empty_search():
    """测试空搜索"""
    print("=== 测试空搜索 ===")

    temp_dir = tempfile.mkdtemp()

    try:
        store = create_test_store(temp_dir)

        results = store.search(query_embedding=[0.1, 0.2, 0.3, 0.4, 0.5], top_k=5)

        assert len(results) == 0

        print("[OK] 空搜索测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_multiple_additions():
    """测试多次添加文档"""
    print("=== 测试多次添加文档 ===")

    temp_dir = tempfile.mkdtemp()

    try:
        store = create_test_store(temp_dir)

        for batch in range(3):
            documents = [
                Document(
                    id=f"batch{batch}_doc{i}",
                    content=f"第{batch}批文档{i}",
                    metadata={"batch": batch},
                )
                for i in range(2)
            ]
            embeddings = [[float(batch), float(i), 0.0, 0.0, 0.0] for i in range(2)]

            store.add_documents(documents, embeddings)

        stats = store.get_collection_stats()
        assert stats["count"] == 6

        print(f"  总文档数: {stats['count']}")
        print("[OK] 多次添加文档测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_custom_collection_name():
    """测试自定义集合名"""
    print("=== 测试自定义集合名 ===")

    temp_dir = tempfile.mkdtemp()

    try:
        store = ChromaVectorStore(
            collection_name="custom_collection",
            persist_directory=temp_dir,
            distance="euclidean",
        )

        stats = store.get_collection_stats()
        assert stats["name"] == "custom_collection"
        assert stats["distance"] == "euclidean"

        print("[OK] 自定义集合名测试通过")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_init()
    test_add_documents()
    test_add_documents_auto_id()
    test_search()
    test_search_with_filter()
    test_clear()
    test_get_collection_stats()
    test_empty_search()
    test_multiple_additions()
    test_custom_collection_name()
    print("\n=== 所有测试通过 ===")