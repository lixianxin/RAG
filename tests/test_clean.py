import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.parsers.cleaner import TextCleaner

"""测试 TextCleaner 文本清洗器"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parsers.cleaner import TextCleaner


def test_cleaner():
    """测试文本清洗功能"""
    print("=== 测试 TextCleaner ===")

    cleaner = TextCleaner()

    # 测试文本
    test_text = """第1页

这是一段测试文本。

第2页

这是另一段内容。"""

    cleaned = cleaner.clean(test_text)
    print("清洗后文本:")
    print(cleaned)

    assert "第1页" not in cleaned
    assert "第2页" not in cleaned
    assert "测试文本" not in cleaned

    print("[OK] 文本清洗测试通过")

def test_normalize_whitespace():
    """测试规范化空白字符功能"""
    print("=== 测试 TextCleaner 规范化空白字符 ===")

    cleaner = TextCleaner()

    # 测试文本
    test_text = """  这  是  一  段  测试  文本  。  """

    normalized = cleaner.normalize_whitespace(test_text)
    print("规范化后文本:")
    print(normalized)

    assert normalized == "这是是一段测试文本。"

    print("[OK] 规范化空白字符测试通过")
    
def test_remove_exstract_chars():
    """测试移除特殊字符功能"""
    print("=== 测试 TextCleaner 移除特殊字符 ===")

    cleaner = TextCleaner()

    # 测试文本
    test_text = """这是是一段测试文本。"""

    cleaned = cleaner.remove_exstract_chars(test_text)
    print("移除后文本:")
    print(cleaned)

    assert cleaned == "这是是一段测试文本。"

    print("[OK] 移除特殊字符测试通过")
    
if __name__ == "__main__":
    test_cleaner()
    test_normalize_whitespace()
    test_remove_exstract_chars()
