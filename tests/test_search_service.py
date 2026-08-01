"""测试 SearchService 检索服务"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock, patch
from src.retrieval.search_service import (
    SearchService,
    CachedSearchService,
    RetrievalConfig,
    SearchResponse,
)


def create_mock_document_store():
    """创建Mock的文档存储"""
    mock_store = MagicMock()
    mock_store.search.return_value = [
        {"id": "doc1", "content": "人工智能是计算机科学的一个分支", "metadata": {}, "score": 0.95},
        {"id": "doc2", "content": "机器学习是人工智能的核心技术", "metadata": {}, "score": 0.85},
        {"id": "doc3", "content": "深度学习使用多层神经网络", "metadata": {}, "score": 0.75},
        {"id": "doc4", "content": "自然语言处理是人工智能的应用", "metadata": {}, "score": 0.65},
        {"id": "doc5", "content": "计算机视觉是人工智能的应用", "metadata": {}, "score": 0.55},
        {"id": "doc6", "content": "强化学习是机器学习的一种", "metadata": {}, "score": 0.45},
    ]
    mock_store.get_stats.return_value = {
        "count": 100,
        "name": "test_collection",
        "distance": "cosine",
        "embedding_dim": 5,
        "embedding_model": "mock-embedding",
    }
    return mock_store


def test_retrieval_config():
    """测试检索配置"""
    print("=== 测试检索配置 ===")

    config = RetrievalConfig()
    assert config.top_k == 5
    assert config.min_score == 0.0
    assert config.namespace is None
    assert config.metadata_filter is None

    config = RetrievalConfig(top_k=10, min_score=0.5, namespace="test")
    assert config.top_k == 10
    assert config.min_score == 0.5
    assert config.namespace == "test"

    print("[OK] 检索配置测试通过")


def test_search_response():
    """测试检索结果"""
    print("=== 测试检索结果 ===")

    results = [{"id": "doc1", "content": "测试", "score": 0.9}]
    response = SearchResponse(
        query="测试查询",
        total_results=1,
        results=results,
        retrieval_time_ms=100,
    )

    assert response.query == "测试查询"
    assert response.total_results == 1
    assert response.results == results
    assert response.retrieval_time_ms == 100

    print("[OK] 检索结果测试通过")


def test_search_service_init():
    """测试SearchService初始化"""
    print("=== 测试SearchService初始化 ===")

    mock_store = create_mock_document_store()
    service = SearchService(document_store=mock_store)

    assert service.document_store is not None

    print("[OK] SearchService初始化测试通过")


def test_search_service_search_default_config():
    """测试默认配置搜索"""
    print("=== 测试默认配置搜索 ===")

    mock_store = create_mock_document_store()
    service = SearchService(document_store=mock_store)

    response = service.search("人工智能")

    assert isinstance(response, SearchResponse)
    assert response.query == "人工智能"
    assert response.total_results == 5
    assert len(response.results) == 5
    assert response.retrieval_time_ms >= 0

    mock_store.search.assert_called_once_with(
        query="人工智能",
        top_k=5,
        namespace=None,
    )

    print(f"  搜索结果数: {response.total_results}")
    print(f"  检索时间: {response.retrieval_time_ms}ms")
    print("[OK] 默认配置搜索测试通过")


def test_search_service_search_with_config():
    """测试带配置的搜索"""
    print("=== 测试带配置的搜索 ===")

    mock_store = create_mock_document_store()
    service = SearchService(document_store=mock_store)

    config = RetrievalConfig(top_k=3, namespace="test_ns")
    response = service.search("人工智能", config)

    assert response.total_results == 3
    assert len(response.results) == 3

    mock_store.search.assert_called_once_with(
        query="人工智能",
        top_k=3,
        namespace="test_ns",
    )

    print("[OK] 带配置的搜索测试通过")


def test_search_service_min_score_filter():
    """测试最低分数过滤"""
    print("=== 测试最低分数过滤 ===")

    mock_store = create_mock_document_store()
    service = SearchService(document_store=mock_store)

    # 设置较高的最低分数，应该过滤掉低分结果
    config = RetrievalConfig(min_score=0.7)
    response = service.search("人工智能", config)

    # 只有 score >= 0.7 的结果应该被保留
    for result in response.results:
        assert result["score"] >= 0.7

    print(f"  过滤后结果数: {response.total_results}")
    print("[OK] 最低分数过滤测试通过")


def test_search_service_top_k_filter():
    """测试top_k截断"""
    print("=== 测试top_k截断 ===")

    mock_store = create_mock_document_store()
    service = SearchService(document_store=mock_store)

    # 虽然mock返回6条，但top_k=2时应该只返回2条
    config = RetrievalConfig(top_k=2)
    response = service.search("人工智能", config)

    assert response.total_results == 2
    assert len(response.results) == 2

    print("[OK] top_k截断测试通过")


def test_search_service_get_stats():
    """测试获取统计信息"""
    print("=== 测试获取统计信息 ===")

    mock_store = create_mock_document_store()
    service = SearchService(document_store=mock_store)

    stats = service.get_stats()

    assert "count" in stats
    assert "name" in stats
    assert stats["count"] == 100

    mock_store.get_stats.assert_called_once()

    print(f"  统计信息: count={stats['count']}, name={stats['name']}")
    print("[OK] 获取统计信息测试通过")


def test_cached_search_service_init():
    """测试CachedSearchService初始化"""
    print("=== 测试CachedSearchService初始化 ===")

    mock_store = create_mock_document_store()
    service = SearchService(document_store=mock_store)
    cached_service = CachedSearchService(search_service=service)

    assert cached_service.service is service
    assert cached_service.cache is not None
    assert cached_service.cache_hits == 0
    assert cached_service.cache_misses == 0

    print("[OK] CachedSearchService初始化测试通过")


def test_cached_search_service_custom_ttl():
    """测试自定义TTL缓存"""
    print("=== 测试自定义TTL缓存 ===")

    mock_store = create_mock_document_store()
    service = SearchService(document_store=mock_store)
    cached_service = CachedSearchService(
        search_service=service, ttl=60, maxsize=50
    )

    assert cached_service.cache.maxsize == 50

    print("[OK] 自定义TTL缓存测试通过")


def test_cached_search_service_cache_hit():
    """测试缓存命中"""
    print("=== 测试缓存命中 ===")

    mock_store = create_mock_document_store()
    service = SearchService(document_store=mock_store)
    cached_service = CachedSearchService(search_service=service)

    # 第一次搜索 - 缓存未命中
    response1 = cached_service.search("人工智能")
    assert response1.total_results == 5
    assert cached_service.cache_misses == 1

    # 重置mock调用计数
    mock_store.search.reset_mock()

    # 第二次相同搜索 - 应该缓存命中
    response2 = cached_service.search("人工智能")
    assert response2.total_results == 5
    assert cached_service.cache_hits == 1

    # 底层服务不应被调用
    mock_store.search.assert_not_called()

    print(f"  缓存命中次数: {cached_service.cache_hits}")
    print("[OK] 缓存命中测试通过")


def test_cached_search_service_cache_miss():
    """测试缓存未命中"""
    print("=== 测试缓存未命中 ===")

    mock_store = create_mock_document_store()
    service = SearchService(document_store=mock_store)
    cached_service = CachedSearchService(search_service=service)

    # 搜索不同的查询
    response1 = cached_service.search("人工智能")
    response2 = cached_service.search("机器学习")
    response3 = cached_service.search("深度学习")

    assert cached_service.cache_misses == 3
    assert cached_service.cache_hits == 0

    print(f"  缓存未命中次数: {cached_service.cache_misses}")
    print("[OK] 缓存未命中测试通过")


def test_cached_search_service_different_config():
    """测试不同配置的缓存"""
    print("=== 测试不同配置的缓存 ===")

    mock_store = create_mock_document_store()
    service = SearchService(document_store=mock_store)
    cached_service = CachedSearchService(search_service=service)

    # 相同查询，不同配置应使用不同缓存键
    config1 = RetrievalConfig(top_k=3)
    config2 = RetrievalConfig(top_k=5)

    response1 = cached_service.search("人工智能", config1)
    response2 = cached_service.search("人工智能", config2)

    # 应该有2次缓存未命中
    assert cached_service.cache_misses == 2

    print("[OK] 不同配置的缓存测试通过")


def test_cached_search_service_get_stats():
    """测试缓存服务的统计信息"""
    print("=== 测试缓存服务的统计信息 ===")

    mock_store = create_mock_document_store()
    service = SearchService(document_store=mock_store)
    cached_service = CachedSearchService(search_service=service)

    # 执行一些搜索
    cached_service.search("查询1")
    cached_service.search("查询1")  # 应该缓存命中
    cached_service.search("查询2")

    stats = cached_service.get_stats()

    assert "cache_hits" in stats
    assert "cache_misses" in stats
    assert "cache_hit_rate" in stats
    assert stats["cache_hits"] == 1
    assert stats["cache_misses"] == 2
    assert stats["cache_hit_rate"] == 33.33  # 1/3 * 100

    print(f"  缓存命中: {stats['cache_hits']}")
    print(f"  缓存未命中: {stats['cache_misses']}")
    print(f"  缓存命中率: {stats['cache_hit_rate']}%")
    print("[OK] 缓存服务的统计信息测试通过")


def test_cached_search_service_clear_cache():
    """测试清除缓存"""
    print("=== 测试清除缓存 ===")

    mock_store = create_mock_document_store()
    service = SearchService(document_store=mock_store)
    cached_service = CachedSearchService(search_service=service)

    # 填充缓存
    cached_service.search("查询1")
    cached_service.search("查询2")

    assert cached_service.cache_misses == 2

    # 清除缓存
    result = cached_service.clear_cache()
    assert result is True
    assert cached_service.cache_hits == 0
    assert cached_service.cache_misses == 0

    # 再次搜索应该缓存未命中
    cached_service.search("查询1")
    assert cached_service.cache_misses == 1

    print("[OK] 清除缓存测试通过")


def test_cached_search_service_custom_config():
    """测试带配置的缓存搜索"""
    print("=== 测试带配置的缓存搜索 ===")

    mock_store = create_mock_document_store()
    service = SearchService(document_store=mock_store)
    cached_service = CachedSearchService(search_service=service)

    config = RetrievalConfig(top_k=3, namespace="test")

    response1 = cached_service.search("测试", config)
    response2 = cached_service.search("测试", config)

    assert cached_service.cache_hits == 1
    assert response1.total_results == response2.total_results

    print("[OK] 带配置的缓存搜索测试通过")


if __name__ == "__main__":
    test_retrieval_config()
    test_search_response()
    test_search_service_init()
    test_search_service_search_default_config()
    test_search_service_search_with_config()
    test_search_service_min_score_filter()
    test_search_service_top_k_filter()
    test_search_service_get_stats()
    test_cached_search_service_init()
    test_cached_search_service_custom_ttl()
    test_cached_search_service_cache_hit()
    test_cached_search_service_cache_miss()
    test_cached_search_service_different_config()
    test_cached_search_service_get_stats()
    test_cached_search_service_clear_cache()
    test_cached_search_service_custom_config()
    print("\n=== 所有测试通过 ===")