import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.parsers.table_parser import TableProcessor


def test_markdown_to_dataframe_normal():
    """测试markdown_to_dataframe正常情况"""
    print("=== 测试 markdown_to_dataframe 正常情况 ===")

    processor = TableProcessor()
    markdown_table = """| 姓名 | 年龄 | 城市 |
|------|------|------|
| 张三 | 25 | 北京 |
| 李四 | 30 | 上海 |"""

    df = processor.markdown_to_dataframe(markdown_table)

    assert df is not None
    assert list(df.columns) == ["姓名", "年龄", "城市"]
    assert len(df) == 2
    assert df.iloc[0]["姓名"] == "张三"
    assert df.iloc[1]["城市"] == "上海"

    print("[OK] markdown_to_dataframe 正常情况测试通过")


def test_markdown_to_dataframe_empty():
    """测试markdown_to_dataframe空输入"""
    print("=== 测试 markdown_to_dataframe 空输入 ===")

    processor = TableProcessor()

    df = processor.markdown_to_dataframe("")
    assert df is None

    df = processor.markdown_to_dataframe("   ")
    assert df is None

    df = processor.markdown_to_dataframe("| 姓名 | 年龄 |")
    assert df is None

    print("[OK] markdown_to_dataframe 空输入测试通过")


def test_markdown_to_dataframe_single_row():
    """测试markdown_to_dataframe单行数据"""
    print("=== 测试 markdown_to_dataframe 单行数据 ===")

    processor = TableProcessor()
    markdown_table = """| 姓名 | 年龄 |
|------|------|
| 张三 | 25 |"""

    df = processor.markdown_to_dataframe(markdown_table)

    assert df is not None
    assert len(df) == 1
    assert df.iloc[0]["姓名"] == "张三"

    print("[OK] markdown_to_dataframe 单行数据测试通过")


def test_dataframe_to_text_normal():
    """测试dataframe_to_text正常情况"""
    print("=== 测试 dataframe_to_text 正常情况 ===")

    processor = TableProcessor()
    data = {"姓名": ["张三", "李四"], "年龄": ["25", "30"]}
    df = pd.DataFrame(data)

    result = processor.dataframe_to_text(df)

    assert "表格内存" in result
    assert "姓名|年龄" in result
    assert "张三|25" in result
    assert "李四|30" in result

    print("[OK] dataframe_to_text 正常情况测试通过")


def test_dataframe_to_text_empty():
    """测试dataframe_to_text空DataFrame"""
    print("=== 测试 dataframe_to_text 空DataFrame ===")

    processor = TableProcessor()
    df = pd.DataFrame()

    result = processor.dataframe_to_text(df)

    assert result == ""

    print("[OK] dataframe_to_text 空DataFrame测试通过")


def test_table_to_text_normal():
    """测试table_to_text正常情况"""
    print("=== 测试 table_to_text 正常情况 ===")

    processor = TableProcessor()
    markdown_table = """| 姓名 | 年龄 |
|------|------|
| 张三 | 25 |"""

    result = processor.table_to_text(markdown_table)

    assert "表格内存" in result
    assert "姓名|年龄" in result
    assert "张三|25" in result

    print("[OK] table_to_text 正常情况测试通过")


def test_table_to_text_empty():
    """测试table_to_text空输入"""
    print("=== 测试 table_to_text 空输入 ===")

    processor = TableProcessor()

    result = processor.table_to_text("")
    assert result == ""

    result = processor.table_to_text("   ")
    assert result == ""

    print("[OK] table_to_text 空输入测试通过")


def test_merge_table_normal():
    """测试merge_table正常合并"""
    print("=== 测试 merge_table 正常合并 ===")

    processor = TableProcessor()
    tables = [
        {"cols": 2, "page": 1, "markdown": "| a | b |", "rows": 5},
        {"cols": 2, "page": 2, "markdown": "| c | d |", "rows": 5},
        {"cols": 3, "page": 3, "markdown": "| x | y | z |", "rows": 3},
    ]

    result = processor.merge_table(tables)

    assert len(result) == 2
    assert result[0]["cols"] == 2
    assert result[1]["cols"] == 3

    print("[OK] merge_table 正常合并测试通过")


def test_merge_table_single():
    """测试merge_table单表格"""
    print("=== 测试 merge_table 单表格 ===")

    processor = TableProcessor()
    tables = [{"cols": 2, "page": 1, "markdown": "| a | b |"}]

    result = processor.merge_table(tables)

    assert len(result) == 1
    assert result[0]["cols"] == 2

    print("[OK] merge_table 单表格测试通过")


def test_merge_table_empty():
    """测试merge_table空列表"""
    print("=== 测试 merge_table 空列表 ===")

    processor = TableProcessor()

    result = processor.merge_table([])
    assert result == []

    print("[OK] merge_table 空列表测试通过")


def test_extract_key_value_normal():
    """测试extract_key_valule正常情况"""
    print("=== 测试 extract_key_valule 正常情况 ===")

    processor = TableProcessor()
    markdown_table = """| 键 | 值 |
|------|------|
| 姓名 | 张三 |
| 年龄 | 25 |"""

    result = processor.extract_key_valule(markdown_table)

    assert result["姓名"] == "张三"
    assert result["年龄"] == "25"

    print("[OK] extract_key_valule 正常情况测试通过")


def test_extract_key_value_empty():
    """测试extract_key_valule空输入"""
    print("=== 测试 extract_key_valule 空输入 ===")

    processor = TableProcessor()

    result = processor.extract_key_valule("")
    assert result == {}

    result = processor.extract_key_valule("| 姓名 |")
    assert result == {}

    print("[OK] extract_key_valule 空输入测试通过")


def test_extract_key_value_single_column():
    """测试extract_key_valule单列表格"""
    print("=== 测试 extract_key_valule 单列表格 ===")

    processor = TableProcessor()
    markdown_table = """| 姓名 |
|------|
| 张三 |"""

    result = processor.extract_key_valule(markdown_table)

    assert result == {}

    print("[OK] extract_key_valule 单列表格测试通过")


if __name__ == "__main__":
    test_markdown_to_dataframe_normal()
    test_markdown_to_dataframe_empty()
    test_markdown_to_dataframe_single_row()
    test_dataframe_to_text_normal()
    test_dataframe_to_text_empty()
    test_table_to_text_normal()
    test_table_to_text_empty()
    test_merge_table_normal()
    test_merge_table_single()
    test_merge_table_empty()
    test_extract_key_value_normal()
    test_extract_key_value_empty()
    test_extract_key_value_single_column()
    print("\n=== 所有测试通过 ===")