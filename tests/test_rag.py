"""测试 RAG 模块"""

import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock, AsyncMock
from src.llm.rag import format_context, build_prompt, generate_answer, generate_answer_stream


class MockLLM:
    """Mock LLM，用于测试"""

    def __init__(self, response_content="这是一个测试答案"):
        self.response_content = response_content
        self.model = "mock-model"

    def generate(self, messages, temperature=0.7, max_token=2000):
        return {
            "content": self.response_content,
            "finish_reason": "stop",
            "token_used": {
                "total": 100,
                "prompt": 80,
                "completion": 20,
            },
            "model": self.model,
        }

    async def generate_stream(self, messages, temperature=0.7, max_token=2000):
        for chunk in ["这", "是", "一个", "测试", "答案"]:
            yield chunk


def test_format_context_basic():
    """测试基本的上下文格式化"""
    print("=== 测试基本的上下文格式化 ===")

    results = [
        {"content": "人工智能是计算机科学的一个分支"},
        {"content": "机器学习是人工智能的核心技术"},
        {"content": "深度学习使用多层神经网络"},
    ]

    context = format_context(results)

    assert "人工智能是计算机科学的一个分支" in context
    assert "机器学习是人工智能的核心技术" in context
    assert "深度学习使用多层神经网络" in context
    assert context.count("\n\n") == 2

    print("[OK] 基本的上下文格式化测试通过")


def test_format_context_empty_results():
    """测试空结果"""
    print("=== 测试空结果 ===")

    context = format_context([])

    assert context == ""

    print("[OK] 空结果测试通过")


def test_format_context_empty_content():
    """测试空内容"""
    print("=== 测试空内容 ===")

    results = [
        {"content": ""},
        {"content": "   "},
        {"content": "有效内容"},
    ]

    context = format_context(results)

    assert "有效内容" in context
    assert "   " not in context

    print("[OK] 空内容测试通过")


def test_format_context_deduplication():
    """测试内容去重"""
    print("=== 测试内容去重 ===")

    results = [
        {"content": "重复内容"},
        {"content": "重复内容"},
        {"content": "重复内容"},
        {"content": "唯一内容"},
    ]

    context = format_context(results)

    # 重复内容只应出现一次
    assert context.count("重复内容") == 1
    assert "唯一内容" in context

    print("[OK] 内容去重测试通过")


def test_format_context_max_chars():
    """测试最大字符数限制"""
    print("=== 测试最大字符数限制 ===")

    results = [
        {"content": "短文本1"},
        {"content": "短文本2短文本2短文本2短文本2短文本2"},
        {"content": "这段内容应该被跳过，因为它超过了最大字符数限制"},
    ]

    context = format_context(results, max_chars=20)

    assert "短文本1" in context
    # 超过限制的内容不应包含
    assert "这段内容应该被跳过" not in context

    print("[OK] 最大字符数限制测试通过")


def test_format_context_missing_content_key():
    """测试缺少content键"""
    print("=== 测试缺少content键 ===")

    results = [
        {"id": "doc1"},
        {"content": "有效内容"},
    ]

    context = format_context(results)

    assert "有效内容" in context

    print("[OK] 缺少content键测试通过")


def test_build_prompt():
    """测试构建提示词"""
    print("=== 测试构建提示词 ===")

    question = "什么是人工智能？"
    context = "人工智能是计算机科学的一个分支"

    prompt = build_prompt(question, context)

    assert question in prompt
    assert context in prompt
    assert "上下文" in prompt
    assert "问题" in prompt
    assert "答：" in prompt

    print("[OK] 构建提示词测试通过")


def test_build_prompt_empty_context():
    """测试空上下文的提示词"""
    print("=== 测试空上下文的提示词 ===")

    question = "测试问题"
    context = ""

    prompt = build_prompt(question, context)

    assert question in prompt
    assert "[上下文]" in prompt

    print("[OK] 空上下文的提示词测试通过")


def test_generate_answer_basic():
    """测试基本的答案生成"""
    print("=== 测试基本的答案生成 ===")

    llm = MockLLM(response_content="人工智能是计算机科学的一个分支")
    question = "什么是人工智能？"
    results = [
        {"content": "人工智能是计算机科学的一个分支", "score": 0.95},
        {"content": "机器学习是人工智能的核心技术", "score": 0.85},
    ]

    answer = generate_answer(llm, question, results)

    assert answer["answer"] == "人工智能是计算机科学的一个分支"
    assert answer["question"] == question
    assert "人工智能是计算机科学的一个分支" in answer["context"]
    assert "token_used" in answer
    assert answer["token_used"]["total"] == 100
    assert answer["model"] == "mock-model"

    print("[OK] 基本的答案生成测试通过")


def test_generate_answer_empty_results():
    """测试空结果的答案生成"""
    print("=== 测试空结果的答案生成 ===")

    llm = MockLLM()
    question = "测试问题"
    results = []

    answer = generate_answer(llm, question, results)

    assert answer["answer"] == "我不知道"
    assert answer["question"] == question
    assert answer["context"] == ""
    assert answer["token_used"]["total"] == 0
    assert answer["model"] == ""

    print("[OK] 空结果的答案生成测试通过")


def test_generate_answer_with_temperature():
    """测试带温度参数的答案生成"""
    print("=== 测试带温度参数的答案生成 ===")

    llm = MockLLM()
    question = "测试问题"
    results = [{"content": "测试内容"}]

    answer = generate_answer(llm, question, results, temperature=0.3, max_token=500)

    assert answer["answer"] == "这是一个测试答案"
    assert answer["token_used"]["total"] == 100

    print("[OK] 带温度参数的答案生成测试通过")


def test_generate_answer_stream_basic():
    """测试流式答案生成"""
    print("=== 测试流式答案生成 ===")

    llm = MockLLM()
    question = "什么是人工智能？"
    results = [{"content": "人工智能是计算机科学的一个分支"}]

    async def collect_stream():
        chunks = []
        async for chunk in generate_answer_stream(llm, question, results):
            chunks.append(chunk)
        return chunks

    chunks = asyncio.run(collect_stream())

    assert len(chunks) == 5
    assert "".join(chunks) == "这是一个测试答案"

    print(f"  流式输出: {''.join(chunks)}")
    print("[OK] 流式答案生成测试通过")


def test_generate_answer_stream_empty_results():
    """测试空结果的流式答案生成"""
    print("=== 测试空结果的流式答案生成 ===")

    llm = MockLLM()
    question = "测试问题"
    results = []

    async def collect_stream():
        chunks = []
        async for chunk in generate_answer_stream(llm, question, results):
            chunks.append(chunk)
        return chunks

    chunks = asyncio.run(collect_stream())

    assert len(chunks) == 1
    assert chunks[0] == "我不知道"

    print("[OK] 空结果的流式答案生成测试通过")


def test_generate_answer_stream_with_params():
    """测试带参数的流式答案生成"""
    print("=== 测试带参数的流式答案生成 ===")

    llm = MockLLM()
    question = "测试问题"
    results = [{"content": "测试内容"}]

    async def collect_stream():
        chunks = []
        async for chunk in generate_answer_stream(
            llm, question, results, temperature=0.5, max_token=1000
        ):
            chunks.append(chunk)
        return chunks

    chunks = asyncio.run(collect_stream())

    assert len(chunks) > 0

    print("[OK] 带参数的流式答案生成测试通过")


if __name__ == "__main__":
    test_format_context_basic()
    test_format_context_empty_results()
    test_format_context_empty_content()
    test_format_context_deduplication()
    test_format_context_max_chars()
    test_format_context_missing_content_key()
    test_build_prompt()
    test_build_prompt_empty_context()
    test_generate_answer_basic()
    test_generate_answer_empty_results()
    test_generate_answer_with_temperature()
    test_generate_answer_stream_basic()
    test_generate_answer_stream_empty_results()
    test_generate_answer_stream_with_params()
    print("\n=== 所有测试通过 ===")