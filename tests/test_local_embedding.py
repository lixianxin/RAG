"""测试 LocalEmbedding 本地嵌入模型"""

import sys
import os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from src.embeddings.local_embedding import LocalEmbedding

load_dotenv()


def cosine_similarity(vec1, vec2):
    """计算余弦相似度"""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def print_vector_stats(vector, name="向量"):
    """打印向量统计信息"""
    arr = np.array(vector)
    print(f"  {name}统计:")
    print(f"    维度: {len(vector)}")
    print(f"    最小值: {arr.min():.6f}")
    print(f"    最大值: {arr.max():.6f}")
    print(f"    均值: {arr.mean():.6f}")
    print(f"    标准差: {arr.std():.6f}")


def test_local_embedding():
    """测试本地向量化"""
    print("\n" + "=" * 50)
    print("测试 LocalEmbedding 本地向量化")
    print("=" * 50)

    model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
    device = os.getenv("EMBEDDING_DEVICE", "cpu")

    print(f"\n初始化模型...")
    print(f"  模型: {model_name}")
    print(f"  设备: {device}")

    embedder = LocalEmbedding(
        model_name=model_name,
        device=device,
    )
    print(f"  嵌入名称: {embedder.get_embedding_name()}")
    print(f"  嵌入维度: {embedder.get_embedding_dim()}")

    # 测试1: 单条文本向量化
    print("\n--- 测试1: 单条文本向量化 ---")
    text = "人工智能是计算机科学的一个分支"
    vector = embedder.embed_text(text)
    print(f"  输入文本: {text}")
    print(f"  向量前10个值: {np.array(vector[:10]).round(6)}")
    print_vector_stats(vector)

    assert isinstance(vector, list)
    assert len(vector) == embedder.get_embedding_dim()

    # 测试2: 批量文本向量化
    print("\n--- 测试2: 批量文本向量化 ---")
    texts = ["苹果是一种水果", "香蕉是黄色的水果", "汽车是一种交通工具"]
    vectors = embedder.embed_batch(texts)

    assert len(vectors) == len(texts)
    for i, (text, vec) in enumerate(zip(texts, vectors), 1):
        print(f"\n  文本{i}: {text}")
        print(f"    向量维度: {len(vec)}")
        print(f"    向量前5个值: {np.array(vec[:5]).round(6)}")
        assert len(vec) == embedder.get_embedding_dim()

    # 测试3: 相似度计算
    print("\n--- 测试3: 文本相似度计算 ---")
    sim_fruit = cosine_similarity(vectors[0], vectors[1])
    sim_cross = cosine_similarity(vectors[0], vectors[2])
    sim_self = cosine_similarity(vectors[0], vectors[0])

    print(f"  '苹果' vs '香蕉' (同类):     {sim_fruit:.6f}")
    print(f"  '苹果' vs '汽车' (跨类):     {sim_cross:.6f}")
    print(f"  '苹果' vs '苹果' (自身):     {sim_self:.6f}")

    assert abs(sim_self - 1.0) < 0.0001, "自身相似度应为1.0"
    assert sim_fruit > sim_cross, "同类相似度应大于跨类相似度"

    # 测试4: 不同模型名称
    print("\n--- 测试4: 嵌入名称和维度 ---")
    assert embedder.get_embedding_name() == model_name
    assert isinstance(embedder.get_embedding_dim(), int)
    assert embedder.get_embedding_dim() > 0

    print("\n[OK] 所有测试通过")
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("LocalEmbedding 测试")
    print("=" * 50)

    success = test_local_embedding()

    print("\n" + "=" * 50)
    if success:
        print("[PASS] 测试完成")
    else:
        print("[FAIL] 测试失败")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()